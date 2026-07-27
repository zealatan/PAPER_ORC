/**
 * @motion-studio/renderer — Node MP4 export pipeline (deterministic SVG frames → FFmpeg).
 */
export { exportVideo, svgFfmpegStrategy } from "./exportVideo";
export {
  buildFfmpegArgs,
  spawnFfmpeg,
  ffmpegAvailable,
  type FfmpegConfig,
} from "./ffmpeg";
export {
  createRegistry,
  resolveForRender,
  renderFrameToPng,
  missingAssetIds,
} from "./frames";
export type { FontConfig } from "./frames";
export { renderDeckParallel } from "./parallelExport";
export type { ParallelExportOptions, ParallelExportResult } from "./parallelExport";
export type {
  ExportOptions,
  ExportProgress,
  ExportProgressCallback,
  ExportResult,
  RenderReport,
  VideoExportStrategy,
} from "./types";
