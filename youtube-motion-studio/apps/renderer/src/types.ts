/**
 * Export pipeline contracts (spec §24). A {@link VideoExportStrategy} turns a project into an MP4;
 * the {@link RenderReport} captures everything about the render for reproducibility.
 */
import type { MotionProject } from "@motion-studio/core";
import type { FontConfig } from "./frames";

export interface ExportOptions {
  /** Absolute output path for the MP4. */
  outPath: string;
  fps?: number;
  /** H.264 CRF (lower = higher quality). Default 20. */
  crf?: number;
  /** x264 preset. Default "medium". */
  preset?: string;
  width?: number;
  height?: number;
  /** ffmpeg executable. Default "ffmpeg". */
  ffmpegPath?: string;
  /** Font loading for the rasterizer (e.g. a deck's heavy display face). */
  fonts?: FontConfig;
}

export interface ExportProgress {
  frame: number;
  totalFrames: number;
  ratio: number;
}

export type ExportProgressCallback = (progress: ExportProgress) => void;

export interface RenderReport {
  projectId: string;
  schemaVersion: string;
  outputPath: string;
  width: number;
  height: number;
  fps: number;
  durationSeconds: number;
  frameCount: number;
  codec: string;
  crf: number;
  preset: string;
  renderDurationMs: number;
  missingAssets: string[];
  ffmpegCommand: string;
  appVersion: string;
}

export interface ExportResult {
  report: RenderReport;
}

export interface VideoExportStrategy {
  export(
    project: MotionProject,
    options: ExportOptions,
    onProgress?: ExportProgressCallback,
    signal?: AbortSignal,
  ): Promise<ExportResult>;
}
