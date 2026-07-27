/**
 * Parallel deck export (spec §24). resvg rasterization is CPU-bound and synchronous — ~256ms/frame
 * on one core — so a serial 4-minute deck takes ~30min. This renders each scene in its own OS
 * process (true multi-core) into an MP4 segment, then concatenates the segments losslessly. Wall
 * time drops to roughly the longest single scene instead of the sum of all scenes.
 *
 * Determinism is preserved: each scene is an independent single-scene sub-project rendered by the
 * same {@link exportVideo} path, and concat is a stream copy.
 */
import { spawn } from "node:child_process";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { availableParallelism } from "node:os";
import type { MotionProject } from "@motion-studio/core";
import type { FontConfig } from "./frames";

export interface ParallelExportOptions {
  outPath: string;
  /** Heavy display font file registered for the rasterizer (shorthand for a single font file). */
  fontFile?: string;
  /** Full font configuration (multiple files, default family, system-font toggle). Wins over fontFile. */
  fonts?: FontConfig;
  /** Max concurrent scene processes. Defaults to cores - 2 (min 1). */
  concurrency?: number;
  ffmpegPath?: string;
  /** Progress callback fired as each scene segment finishes. */
  onSceneDone?: (done: number, total: number, sceneName: string) => void;
}

export interface ParallelExportResult {
  outPath: string;
  scenes: number;
  concurrency: number;
}

const WORKER = fileURLToPath(new URL("./sceneWorker.mts", import.meta.url));

function runWorker(
  jsonPath: string,
  outPath: string,
  fontFile: string | undefined,
  fontsJson: string | undefined,
): Promise<void> {
  return new Promise((resolve, reject) => {
    const args = ["--import", "tsx", WORKER, jsonPath, outPath];
    if (fontFile) args.push(fontFile);
    const child = spawn(process.execPath, args, {
      stdio: ["ignore", "ignore", "pipe"],
      // A full FontConfig is passed out-of-band so the worker can register multiple font files.
      env: fontsJson ? { ...process.env, MS_FONTS: fontsJson } : process.env,
    });
    let stderr = "";
    child.stderr.on("data", (c: Buffer) => {
      stderr += c.toString();
      if (stderr.length > 4000) stderr = stderr.slice(-4000);
    });
    child.on("error", reject);
    child.on("close", (code) =>
      code === 0
        ? resolve()
        : reject(new Error(`scene worker exited ${code}: ${stderr}`)),
    );
  });
}

/** Run `tasks` with at most `limit` in flight, preserving index order of results. */
async function pool<T>(
  items: T[],
  limit: number,
  fn: (item: T, i: number) => Promise<void>,
): Promise<void> {
  let next = 0;
  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    for (;;) {
      const i = next++;
      if (i >= items.length) return;
      await fn(items[i]!, i);
    }
  });
  await Promise.all(workers);
}

function concat(
  segments: string[],
  outPath: string,
  ffmpegPath: string,
  tmpDir: string,
): Promise<void> {
  const listPath = join(tmpDir, "concat.txt");
  writeFileSync(listPath, segments.map((s) => `file '${s}'`).join("\n"));
  return new Promise((resolve, reject) => {
    const args = [
      "-y",
      "-f",
      "concat",
      "-safe",
      "0",
      "-i",
      listPath,
      "-c",
      "copy",
      "-movflags",
      "+faststart",
      outPath,
    ];
    const child = spawn(ffmpegPath, args, { stdio: ["ignore", "ignore", "pipe"] });
    let stderr = "";
    child.stderr.on("data", (c: Buffer) => {
      stderr += c.toString();
      if (stderr.length > 4000) stderr = stderr.slice(-4000);
    });
    child.on("error", reject);
    child.on("close", (code) =>
      code === 0
        ? resolve()
        : reject(new Error(`ffmpeg concat exited ${code}: ${stderr}`)),
    );
  });
}

export async function renderDeckParallel(
  project: MotionProject,
  options: ParallelExportOptions,
): Promise<ParallelExportResult> {
  const total = project.scenes.length;
  if (total === 0) throw new Error("project has no scenes");
  const ffmpegPath = options.ffmpegPath ?? "ffmpeg";
  const concurrency = Math.max(1, options.concurrency ?? availableParallelism() - 2);
  const tmpDir = mkdtempSync(join(tmpdir(), "ms-parallel-"));

  try {
    // One single-scene sub-project per scene (assets/settings/theme travel with it).
    const segments: string[] = project.scenes.map((_, i) =>
      join(tmpDir, `seg_${String(i).padStart(4, "0")}.mp4`),
    );
    const jsonPaths = project.scenes.map((scene, i) => {
      const sub: MotionProject = { ...project, scenes: [scene] };
      const p = join(tmpDir, `scene_${i}.json`);
      writeFileSync(p, JSON.stringify(sub));
      return p;
    });

    const fontsJson = options.fonts ? JSON.stringify(options.fonts) : undefined;
    let done = 0;
    await pool(project.scenes, concurrency, async (scene, i) => {
      await runWorker(jsonPaths[i]!, segments[i]!, options.fontFile, fontsJson);
      done += 1;
      options.onSceneDone?.(done, total, scene.name);
    });

    await concat(segments, options.outPath, ffmpegPath, tmpDir);
    return { outPath: options.outPath, scenes: total, concurrency };
  } finally {
    rmSync(tmpDir, { recursive: true, force: true });
  }
}
