/**
 * @motion-studio/renderer-core — deterministic timeline evaluation, a backend-agnostic
 * scene-graph IR, transform/easing/animation math, and renderer backends (SVG, Pixi).
 */
export * from "./scene-graph";
export * from "./transform";
export * from "./easing";
export * from "./animation";
export * from "./timeline";
export * from "./types";
export { DefaultRenderRegistry, createRenderContext } from "./registry";
export {
  renderProjectToSvg,
  SvgFrameRenderer,
  type SvgRenderOptions,
} from "./renderers/svg";
export { PixiFrameRenderer, type PixiRendererOptions } from "./renderers/pixi";
