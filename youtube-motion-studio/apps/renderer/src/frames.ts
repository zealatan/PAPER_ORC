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

/**
 * Font loading for the rasterizer. Text weight/family only render correctly if resvg can find the
 * face: `files` registers specific font files (e.g. a heavy display face bundled with a deck),
 * `defaultFamily` is used when a text node names no family, and system fonts stay available for
 * broad language coverage (Korean, etc.).
 */
export interface FontConfig {
  files?: string[];
  defaultFamily?: string;
  loadSystemFonts?: boolean;
}

/** Default fonts: keep system fonts (Korean coverage) and default to a CJK-capable family. */
const DEFAULT_FONTS: FontConfig = {
  loadSystemFonts: true,
  defaultFamily: "Noto Sans CJK KR",
};

/** Rasterize one frame to a PNG buffer. `skipBackground` yields a transparent frame for compositing. */
export function renderFrameToPng(
  project: MotionProject,
  timeSeconds: number,
  registry: RenderRegistry,
  width: number,
  skipBackground = false,
  fonts: FontConfig = DEFAULT_FONTS,
): Buffer {
  const svg = renderProjectToSvg(project, timeSeconds, registry, { skipBackground });
  const resvg = new Resvg(svg, {
    fitTo: { mode: "width", value: width },
    font: {
      loadSystemFonts: fonts.loadSystemFonts ?? true,
      fontFiles: fonts.files ?? [],
      defaultFontFamily: fonts.defaultFamily ?? "Noto Sans CJK KR",
    },
  });
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
