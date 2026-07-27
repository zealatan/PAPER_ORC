/**
 * The default {@link VideoExportStrategy}: deterministic SVG frames → FFmpeg → MP4 (spec §24).
 *
 * Pipeline: resolve project (bindings + theme) → for each frame, rasterize the deterministic SVG to
 * PNG → pipe to FFmpeg (H.264, yuv420p, faststart). Reports progress per frame, supports
 * cancellation via an AbortSignal (kills FFmpeg and removes the partial file), and returns a full
 * render report.
 */
import { unlink } from "node:fs/promises";
import {
  createRegistry,
  missingAssetIds,
  projectDuration,
  renderFrameToPng,
  resolveForRender,
} from "./frames";
import { spawnFfmpeg } from "./ffmpeg";
import type {
  ExportOptions,
  ExportProgressCallback,
  ExportResult,
  RenderReport,
  VideoExportStrategy,
} from "./types";
import type { MotionProject } from "@motion-studio/core";

const APP_VERSION = "0.1.0";

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

  const ffmpeg = spawnFfmpeg({ fps, crf, preset, outPath: options.outPath, ffmpegPath });
  const stdin = ffmpeg.child.stdin;

  const cleanupPartial = async () => {
    // Swallow the ffmpeg exit rejection we're about to cause by killing it.
    void ffmpeg.done.catch(() => undefined);
    try {
      ffmpeg.child.kill("SIGKILL");
    } catch {
      /* already gone */
    }
    try {
      await unlink(options.outPath);
    } catch {
      /* nothing to remove */
    }
  };

  try {
    for (let i = 0; i < frameCount; i += 1) {
      if (signal?.aborted) throw new Error("Export cancelled");
      const time = i / fps;
      const png = renderFrameToPng(resolved, time, registry, width);
      if (!stdin.write(png)) {
        await new Promise<void>((resolve) => stdin.once("drain", resolve));
      }
      onProgress?.({
        frame: i + 1,
        totalFrames: frameCount,
        ratio: (i + 1) / frameCount,
      });
    }
    stdin.end();
    await ffmpeg.done;
  } catch (error) {
    await cleanupPartial();
    throw error;
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
    ffmpegCommand: ffmpeg.command,
    appVersion: APP_VERSION,
  };

  return { report };
}

/** Strategy object form of {@link exportVideo}. */
export const svgFfmpegStrategy: VideoExportStrategy = {
  export: exportVideo,
};
