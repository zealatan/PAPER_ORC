/**
 * Example build pipeline: generate → preview → render → validate → gallery. Everything runs on the
 * existing engine (renderFrameToPng / renderDeckParallel / exportVideo). Fonts are explicit files
 * (no reliance on system font resolution) so renders are deterministic and reproducible.
 */
import { spawnSync } from "node:child_process";
import {
  cpSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { validateProject, type MotionProject } from "@motion-studio/core";
import {
  createRegistry,
  renderDeckParallel,
  renderFrameToPng,
  resolveForRender,
  exportVideo,
  type FontConfig,
} from "@motion-studio/renderer";
import { EXAMPLES, type ExampleDef } from "./projects/index";

const HERE = dirname(fileURLToPath(import.meta.url));
export const EXAMPLES_DIR = join(HERE, "..");
const FONTS_DIR = join(EXAMPLES_DIR, "fonts");

/** Explicit font files only (spec: do not depend on system font resolution). */
export const FONTS: FontConfig = {
  files: [
    join(FONTS_DIR, "BlackHanSans-Regular.ttf"),
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
  ],
  defaultFamily: "Noto Sans CJK KR",
  loadSystemFonts: false,
};

export interface Validation {
  exampleId: string;
  name: string;
  renderSuccess: boolean;
  hasMoovAtom: boolean;
  durationSeconds: number;
  frameCount: number;
  resolution: { width: number; height: number };
  fps: number;
  scenes: number;
  componentsUsed: string[];
  featuresTested: string[];
  warnings: string[];
  renderTimeMs: number;
  parallelWorkers: number;
  framesPerSecond: number;
  outputSizeBytes: number;
  serialRenderTimeMs?: number;
  dataDisclaimer?: string;
}

function dir(id: string): string {
  return join(EXAMPLES_DIR, id);
}
function ensure(p: string): string {
  mkdirSync(p, { recursive: true });
  return p;
}
function ffprobe(file: string, args: string[]): string {
  const r = spawnSync("ffprobe", ["-v", "error", ...args, file], { encoding: "utf8" });
  return (r.stdout ?? "").trim();
}

function collectComponents(project: MotionProject): string[] {
  const types = new Set<string>();
  const walk = (els: MotionProject["scenes"][number]["elements"]): void => {
    for (const e of els) {
      types.add(e.type);
      if (e.children) walk(e.children);
    }
  };
  for (const s of project.scenes) walk(s.elements);
  return [...types].sort();
}

const sceneStarts = (p: MotionProject): number[] => {
  const out: number[] = [];
  let acc = 0;
  for (const s of p.scenes) {
    out.push(acc);
    acc += s.duration;
  }
  return out;
};
const totalDuration = (p: MotionProject): number =>
  p.scenes.reduce((a, s) => a + s.duration, 0);

// ── generate ──────────────────────────────────────────────────────────────────
export function generate(ex: ExampleDef): { warnings: string[] } {
  const project = ex.build();
  validateProject(project); // throws on schema error
  ensure(dir(ex.id));
  writeFileSync(join(dir(ex.id), "project.json"), JSON.stringify(project, null, 2));
  return { warnings: [] };
}

// ── preview ─────────────────────────────────────────────────────────────────--
export function preview(ex: ExampleDef): void {
  const project = loadProject(ex.id);
  const registry = createRegistry();
  const resolved = resolveForRender(project);
  const starts = sceneStarts(project);
  const previewDir = ensure(join(dir(ex.id), "preview"));
  const frameFiles: string[] = [];

  project.scenes.forEach((scene, i) => {
    const s = starts[i]!;
    const phases: Array<[string, number]> = [
      ["start", s + 0.2],
      ["middle", s + scene.duration / 2],
      ["end", s + scene.duration - 0.2],
    ];
    for (const [phase, t] of phases) {
      const png = renderFrameToPng(resolved, t, registry, 540, false, FONTS);
      const name = `scene-${String(i + 1).padStart(2, "0")}-${phase}.png`;
      writeFileSync(join(previewDir, name), png);
      frameFiles.push(join(previewDir, name));
    }
  });

  // Representative frame: middle of the richest scene, full resolution.
  const richest = project.scenes.reduce(
    (best, s, i) =>
      s.elements.length > project.scenes[best]!.elements.length ? i : best,
    0,
  );
  const repT = starts[richest]! + project.scenes[richest]!.duration / 2;
  writeFileSync(
    join(dir(ex.id), "representative.png"),
    renderFrameToPng(resolved, repT, registry, 1080, false, FONTS),
  );

  buildContactSheet(frameFiles, join(dir(ex.id), "contact-sheet.png"));
}

function buildContactSheet(frames: string[], outPath: string): void {
  if (frames.length === 0) return;
  const tmp = mkdtempSync(join(tmpdir(), "cs-"));
  try {
    frames.forEach((f, i) => cpSync(f, join(tmp, `${String(i).padStart(3, "0")}.png`)));
    const cols = 3;
    const rows = Math.ceil(frames.length / cols);
    spawnSync(
      "ffmpeg",
      [
        "-y",
        "-v",
        "error",
        "-framerate",
        "1",
        "-i",
        join(tmp, "%03d.png"),
        "-frames:v",
        "1",
        "-vf",
        `scale=360:640,tile=${cols}x${rows}:padding=10:margin=10:color=#111318`,
        outPath,
      ],
      { encoding: "utf8" },
    );
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}

// ── render ────────────────────────────────────────────────────────────────────
export async function render(
  ex: ExampleDef,
): Promise<{ renderTimeMs: number; workers: number; serialMs?: number }> {
  const project = loadProject(ex.id);
  ensure(dir(ex.id));
  const outPath = join(dir(ex.id), "output.mp4");
  const t0 = process.hrtime.bigint();
  const res = await renderDeckParallel(project, { outPath, fonts: FONTS });
  const renderTimeMs = Number(process.hrtime.bigint() - t0) / 1e6;

  // Example 10: also render serially to compare (spec §performance).
  let serialMs: number | undefined;
  if (ex.id === "10-full-showcase") {
    const s0 = process.hrtime.bigint();
    await exportVideo(project, {
      outPath: join(dir(ex.id), "output-serial.mp4"),
      fonts: FONTS,
    });
    serialMs = Number(process.hrtime.bigint() - s0) / 1e6;
  }
  return { renderTimeMs, workers: res.concurrency, serialMs };
}

// ── validate ──────────────────────────────────────────────────────────────────
export function validate(
  ex: ExampleDef,
  timing: { renderTimeMs: number; workers: number; serialMs?: number },
): Validation {
  const project = loadProject(ex.id);
  const outPath = join(dir(ex.id), "output.mp4");
  const warnings: string[] = [];

  const meta = (project.metadata ?? {}) as Record<string, unknown>;
  const width = Number(
    ffprobe(outPath, [
      "-select_streams",
      "v:0",
      "-show_entries",
      "stream=width",
      "-of",
      "csv=p=0",
    ]) || 0,
  );
  const height = Number(
    ffprobe(outPath, [
      "-select_streams",
      "v:0",
      "-show_entries",
      "stream=height",
      "-of",
      "csv=p=0",
    ]) || 0,
  );
  const durationSeconds = Number(
    ffprobe(outPath, ["-show_entries", "format=duration", "-of", "csv=p=0"]) || 0,
  );
  const nbFrames = ffprobe(outPath, [
    "-select_streams",
    "v:0",
    "-count_frames",
    "-show_entries",
    "stream=nb_read_frames",
    "-of",
    "csv=p=0",
  ]);
  const frameCount = Number(
    nbFrames || Math.round(totalDuration(project) * project.settings.fps),
  );
  // moov atom: ffprobe succeeds only if the container is finalized.
  const hasMoovAtom = width > 0 && height > 0 && durationSeconds > 0;
  const outputSizeBytes = existsSync(outPath) ? statSync(outPath).size : 0;

  if (width !== 1080 || height !== 1920)
    warnings.push(`resolution ${width}x${height} != 1080x1920`);
  if (durationSeconds < 8 || durationSeconds > 22)
    warnings.push(`duration ${durationSeconds.toFixed(1)}s outside 8–22s`);

  const v: Validation = {
    exampleId: ex.id,
    name: ex.name,
    renderSuccess: hasMoovAtom && outputSizeBytes > 0,
    hasMoovAtom,
    durationSeconds: Number(durationSeconds.toFixed(3)),
    frameCount,
    resolution: { width, height },
    fps: project.settings.fps,
    scenes: project.scenes.length,
    componentsUsed: collectComponents(project),
    featuresTested: ex.featuresTested,
    warnings,
    renderTimeMs: Math.round(timing.renderTimeMs),
    parallelWorkers: timing.workers,
    framesPerSecond: Number((frameCount / (timing.renderTimeMs / 1000)).toFixed(1)),
    outputSizeBytes,
    ...(timing.serialMs !== undefined
      ? { serialRenderTimeMs: Math.round(timing.serialMs) }
      : {}),
    ...(typeof meta.dataDisclaimer === "string"
      ? { dataDisclaimer: meta.dataDisclaimer }
      : {}),
  };
  writeFileSync(join(dir(ex.id), "validation.json"), JSON.stringify(v, null, 2));
  return v;
}

export function loadProject(id: string): MotionProject {
  const p = join(dir(id), "project.json");
  if (existsSync(p)) return JSON.parse(readFileSync(p, "utf8")) as MotionProject;
  return EXAMPLES.find((e) => e.id === id)!.build();
}

export function outputsExist(id: string): boolean {
  return (
    existsSync(join(dir(id), "output.mp4")) &&
    existsSync(join(dir(id), "validation.json"))
  );
}
