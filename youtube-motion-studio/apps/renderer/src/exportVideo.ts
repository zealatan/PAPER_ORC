/**
 * The default {@link VideoExportStrategy}: deterministic SVG frames → FFmpeg → MP4 (spec §24).
 *
 * Two paths, chosen automatically:
 *  - **flat**: no video backgrounds → rasterize opaque frames and pipe them straight to FFmpeg.
 *  - **composited**: any scene has a video background → build a background track that matches the
 *    timeline (`backgroundTrack.ts`), then overlay transparent element frames on top so the legacy
 *    deck's background videos appear in the final MP4.
 *
 * Both report progress per frame, support cancellation via an AbortSignal (kill FFmpeg + remove the
 * partial file), and return a full render report.
 */
import { spawn } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { unlink } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import type { Writable } from "node:stream";
import {
  createRegistry,
  missingAssetIds,
  projectDuration,
  renderFrameToPng,
  resolveForRender,
  type FontConfig,
} from "./frames";
import { spawnFfmpeg } from "./ffmpeg";
import { buildBackgroundTrack, hasVideoBackground } from "./backgroundTrack";
import type {
  ExportOptions,
  ExportProgressCallback,
  ExportResult,
  RenderReport,
  VideoExportStrategy,
} from "./types";
import type { MotionProject } from "@motion-studio/core";
import type { RenderRegistry } from "@motion-studio/renderer-core";

const APP_VERSION = "0.1.0";

interface PumpConfig {
  frameCount: number;
  fps: number;
  width: number;
  skipBackground: boolean;
  fonts?: FontConfig;
}

async function pumpFrames(
  stdin: Writable,
  project: MotionProject,
  registry: RenderRegistry,
  config: PumpConfig,
  onProgress?: ExportProgressCallback,
  signal?: AbortSignal,
): Promise<void> {
  for (let i = 0; i < config.frameCount; i += 1) {
    if (signal?.aborted) throw new Error("Export cancelled");
    const png = renderFrameToPng(
      project,
      i / config.fps,
      registry,
      config.width,
      config.skipBackground,
      config.fonts,
    );
    if (!stdin.write(png)) {
      await new Promise<void>((resolve) => stdin.once("drain", resolve));
    }
    onProgress?.({
      frame: i + 1,
      totalFrames: config.frameCount,
      ratio: (i + 1) / config.frameCount,
    });
  }
  stdin.end();
}

export async function exportVideo(
  project: MotionProject,
  options: ExportOptions,
  onProgress?: ExportProgressCallback,
  signal?: AbortSignal,
): Promise<ExportResult> {
  const startedAt = Date.now();
  const registry = createRegistry();
  const resolved = resolveForRender(project);

  const width = options.width ?? project.settings.width;
  const height = options.height ?? project.settings.height;
  const fps = options.fps ?? project.settings.fps;
  const crf = options.crf ?? 20;
  const preset = options.preset ?? "medium";
  const ffmpegPath = options.ffmpegPath ?? "ffmpeg";
  const durationSeconds = projectDuration(project);
  const frameCount = Math.max(1, Math.round(durationSeconds * fps));
  const composite = hasVideoBackground(resolved);

  const removePartial = async () => {
    try {
      await unlink(options.outPath);
    } catch {
      /* nothing to remove */
    }
  };

  let ffmpegCommand: string;

  if (composite) {
    const tmpDir = mkdtempSync(join(tmpdir(), "ms-export-"));
    try {
      const bgPath = await buildBackgroundTrack(resolved, {
        width,
        height,
        fps,
        ffmpegPath,
        tmpDir,
      });
      const args = [
        "-y",
        "-i",
        bgPath,
        "-f",
        "image2pipe",
        "-framerate",
        String(fps),
        "-i",
        "-",
        "-filter_complex",
        "[0:v][1:v]overlay=shortest=1",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        String(crf),
        "-preset",
        preset,
        "-movflags",
        "+faststart",
        "-r",
        String(fps),
        options.outPath,
      ];
      ffmpegCommand = [ffmpegPath, ...args].join(" ");
      const child = spawn(ffmpegPath, args, { stdio: ["pipe", "ignore", "pipe"] });
      let stderr = "";
      child.stderr?.on("data", (c: Buffer) => {
        stderr += c.toString();
        if (stderr.length > 8000) stderr = stderr.slice(-8000);
      });
      const done = new Promise<void>((resolve, reject) => {
        child.on("error", reject);
        child.on("close", (code) =>
          code === 0
            ? resolve()
            : reject(new Error(`ffmpeg exited ${code}:\n${stderr.slice(-1000)}`)),
        );
      });
      try {
        await pumpFrames(
          child.stdin as Writable,
          resolved,
          registry,
          { frameCount, fps, width, skipBackground: true, fonts: options.fonts },
          onProgress,
          signal,
        );
        await done;
      } catch (error) {
        void done.catch(() => undefined);
        try {
          child.kill("SIGKILL");
        } catch {
          /* gone */
        }
        await removePartial();
        throw error;
      }
    } finally {
      rmSync(tmpDir, { recursive: true, force: true });
    }
  } else {
    const ffmpeg = spawnFfmpeg({
      fps,
      crf,
      preset,
      outPath: options.outPath,
      ffmpegPath,
    });
    ffmpegCommand = ffmpeg.command;
    try {
      await pumpFrames(
        ffmpeg.child.stdin,
        resolved,
        registry,
        { frameCount, fps, width, skipBackground: false, fonts: options.fonts },
        onProgress,
        signal,
      );
      await ffmpeg.done;
    } catch (error) {
      void ffmpeg.done.catch(() => undefined);
      try {
        ffmpeg.child.kill("SIGKILL");
      } catch {
        /* gone */
      }
      await removePartial();
      throw error;
    }
  }

  const report: RenderReport = {
    projectId: project.id,
    schemaVersion: project.schemaVersion,
    outputPath: options.outPath,
    width,
    height,
    fps,
    durationSeconds,
    frameCount,
    codec: "h264",
    crf,
    preset,
    renderDurationMs: Date.now() - startedAt,
    missingAssets: missingAssetIds(project),
    ffmpegCommand,
    appVersion: APP_VERSION,
  };

  return { report };
}

/** Strategy object form of {@link exportVideo}. */
export const svgFfmpegStrategy: VideoExportStrategy = {
  export: exportVideo,
};
