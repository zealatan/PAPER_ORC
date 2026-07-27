/**
 * Deterministic frame rasterization: resolve a project (bindings + theme), render it to SVG at a
 * timestamp, and rasterize the SVG to PNG with resvg. No browser required — a frame at time `t`
 * depends only on the project and `t` (spec §23).
 */
import { Resvg } from "@resvg/resvg-js";
import {
  applyBindings,
  applyTheme,
  resolveTheme,
  type MotionProject,
} from "@motion-studio/core";
import {
  createRenderContext,
  projectDuration,
  renderProjectToSvg,
  type RenderRegistry,
} from "@motion-studio/renderer-core";
import { createDefaultRenderRegistry } from "@motion-studio/components";

export function createRegistry(): RenderRegistry {
  return createDefaultRenderRegistry();
}

/** Apply variable bindings + theme tokens so the render matches the editor preview. */
export function resolveForRender(project: MotionProject): MotionProject {
  return applyTheme(applyBindings(project), resolveTheme(project.theme.themeId));
}

/** Rasterize one frame to a PNG buffer. */
export function renderFrameToPng(
  project: MotionProject,
  timeSeconds: number,
  registry: RenderRegistry,
  width: number,
): Buffer {
  const svg = renderProjectToSvg(project, timeSeconds, registry);
  const resvg = new Resvg(svg, { fitTo: { mode: "width", value: width } });
  return Buffer.from(resvg.render().asPng());
}

/** Asset ids referenced by the project that do not resolve to a URL. */
export function missingAssetIds(project: MotionProject): string[] {
  const ctx = createRenderContext(project);
  const missing = new Set<string>();
  for (const asset of project.assets) {
    if (ctx.resolveAssetUrl(asset.id) === null) missing.add(asset.id);
  }
  return [...missing];
}

export { projectDuration };
