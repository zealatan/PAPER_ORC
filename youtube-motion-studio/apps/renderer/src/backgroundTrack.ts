/**
 * Build a background video track that matches the project timeline: each scene contributes a
 * segment — its background video (looped + cover-scaled) or a solid-colour clip — concatenated to a
 * single `bg.mp4`. The export then overlays the transparent element frames on top of this track, so
 * the legacy deck's background videos appear in the final MP4 (spec §26.3 step 8: preserve export
 * compatibility).
 */
import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";
import { join } from "node:path";
import { createRenderContext } from "@motion-studio/renderer-core";
import type { MotionProject } from "@motion-studio/core";

export function hasVideoBackground(project: MotionProject): boolean {
  return project.scenes.some((scene) => scene.background.type === "video");
}

function run(ffmpegPath: string, args: string[]): Promise<void> {
  return new Promise((resolve, reject) => {
    const child = spawn(ffmpegPath, args, { stdio: ["ignore", "ignore", "pipe"] });
    let stderr = "";
    child.stderr?.on("data", (c: Buffer) => {
      stderr += c.toString();
      if (stderr.length > 4000) stderr = stderr.slice(-4000);
    });
    child.on("error", reject);
    child.on("close", (code) =>
      code === 0
        ? resolve()
        : reject(new Error(`ffmpeg failed (${code}): ${stderr.slice(-600)}`)),
    );
  });
}

const toFfColor = (hex: string): string =>
  hex.startsWith("#") ? `0x${hex.slice(1)}` : hex;

export interface BackgroundTrackOptions {
  width: number;
  height: number;
  fps: number;
  ffmpegPath: string;
  tmpDir: string;
}

/** Render the per-scene background segments and concat them into a single track; returns its path. */
export async function buildBackgroundTrack(
  project: MotionProject,
  options: BackgroundTrackOptions,
): Promise<string> {
  const { width, height, fps, ffmpegPath, tmpDir } = options;
  const ctx = createRenderContext(project);
  const segments: string[] = [];

  for (let i = 0; i < project.scenes.length; i += 1) {
    const scene = project.scenes[i]!;
    const seg = join(tmpDir, `seg_${i}.mp4`);
    const dur = scene.duration;
    const bg = scene.background;
    const videoUrl = bg.type === "video" ? ctx.resolveAssetUrl(bg.assetId) : null;

    if (bg.type === "video" && videoUrl) {
      await run(ffmpegPath, [
        "-y",
        "-stream_loop",
        "-1",
        "-t",
        String(dur),
        "-i",
        videoUrl,
        "-vf",
        `scale=${width}:${height}:force_original_aspect_ratio=increase,crop=${width}:${height},fps=${fps}`,
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        seg,
      ]);
    } else {
      const color = bg.type === "solid" ? bg.color : "#0e1726";
      await run(ffmpegPath, [
        "-y",
        "-f",
        "lavfi",
        "-i",
        `color=c=${toFfColor(color)}:s=${width}x${height}:d=${dur}:r=${fps}`,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        seg,
      ]);
    }
    segments.push(seg);
  }

  const listPath = join(tmpDir, "concat.txt");
  writeFileSync(listPath, segments.map((p) => `file '${p}'`).join("\n"));
  const bgPath = join(tmpDir, "bg.mp4");
  await run(ffmpegPath, [
    "-y",
    "-f",
    "concat",
    "-safe",
    "0",
    "-i",
    listPath,
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv420p",
    "-r",
    String(fps),
    bgPath,
  ]);
  return bgPath;
}
