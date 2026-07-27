/**
 * Deterministic SVG backend. Produces a byte-stable SVG string for a project at a given time,
 * which makes it ideal for visual-regression snapshot tests and headless rendering (spec §23,
 * §33.3). It walks the {@link EvaluatedFrame} and paints {@link DrawNode} primitives; unknown
 * element types become visible placeholders (spec §8.2).
 */
import type { BackgroundDefinition, MotionProject } from "@motion-studio/core";
import type {
  DrawNode,
  EllipseNode,
  Fill,
  ImageNode,
  LineNode,
  PolylineNode,
  RectNode,
  Stroke,
  TextNode,
} from "../scene-graph";
import { evaluateProjectAtTime, type ResolvedElement } from "../timeline";
import { toSvgTransform } from "../transform";
import { createRenderContext } from "../registry";
import type {
  FrameRenderer,
  RenderContext,
  RenderedFrame,
  RenderRegistry,
} from "../types";

export interface SvgRenderOptions {
  includeXmlDeclaration?: boolean;
}

function fmt(n: number): string {
  const r = Math.round(n * 1000) / 1000;
  return String(Object.is(r, -0) ? 0 : r);
}

function esc(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function fillAttrs(fill: Fill | undefined): string {
  if (!fill) return `fill="none"`;
  const opacity =
    fill.opacity != null && fill.opacity !== 1
      ? ` fill-opacity="${fmt(fill.opacity)}"`
      : "";
  return `fill="${esc(fill.color)}"${opacity}`;
}

function strokeAttrs(stroke: Stroke | undefined): string {
  if (!stroke) return "";
  const opacity =
    stroke.opacity != null && stroke.opacity !== 1
      ? ` stroke-opacity="${fmt(stroke.opacity)}"`
      : "";
  return ` stroke="${esc(stroke.color)}" stroke-width="${fmt(stroke.width)}"${opacity}`;
}

function nodeOpacityAttr(opacity: number | undefined): string {
  return opacity != null && opacity !== 1 ? ` opacity="${fmt(opacity)}"` : "";
}

function rectSvg(n: RectNode): string {
  const radius = n.radius ? ` rx="${fmt(n.radius)}" ry="${fmt(n.radius)}"` : "";
  return `<rect x="${fmt(n.x)}" y="${fmt(n.y)}" width="${fmt(n.width)}" height="${fmt(n.height)}"${radius} ${fillAttrs(n.fill)}${strokeAttrs(n.stroke)}${nodeOpacityAttr(n.opacity)}/>`;
}

function ellipseSvg(n: EllipseNode): string {
  return `<ellipse cx="${fmt(n.cx)}" cy="${fmt(n.cy)}" rx="${fmt(n.rx)}" ry="${fmt(n.ry)}" ${fillAttrs(n.fill)}${strokeAttrs(n.stroke)}${nodeOpacityAttr(n.opacity)}/>`;
}

function lineSvg(n: LineNode): string {
  return `<line x1="${fmt(n.x1)}" y1="${fmt(n.y1)}" x2="${fmt(n.x2)}" y2="${fmt(n.y2)}"${strokeAttrs(n.stroke)}${nodeOpacityAttr(n.opacity)}/>`;
}

function polylineSvg(n: PolylineNode): string {
  const pts = n.points.map(([x, y]) => `${fmt(x)},${fmt(y)}`).join(" ");
  const tag = n.closed ? "polygon" : "polyline";
  const fill = n.closed ? fillAttrs(n.fill) : fillAttrs(n.fill ?? undefined);
  return `<${tag} points="${pts}" ${fill}${strokeAttrs(n.stroke)}${nodeOpacityAttr(n.opacity)}/>`;
}

function textSvg(n: TextNode): string {
  const anchor = n.align === "center" ? "middle" : n.align === "right" ? "end" : "start";
  const baseline =
    n.baseline === "top"
      ? "text-before-edge"
      : n.baseline === "middle"
        ? "central"
        : n.baseline === "bottom"
          ? "text-after-edge"
          : "alphabetic";
  const weight = n.fontWeight ? ` font-weight="${fmt(n.fontWeight)}"` : "";
  const family = n.fontFamily ? ` font-family="${esc(n.fontFamily)}"` : "";
  const spacing =
    n.letterSpacing != null ? ` letter-spacing="${fmt(n.letterSpacing)}"` : "";
  return `<text x="${fmt(n.x)}" y="${fmt(n.y)}" font-size="${fmt(n.fontSize)}"${weight}${family}${spacing} text-anchor="${anchor}" dominant-baseline="${baseline}" ${fillAttrs(n.fill)}${nodeOpacityAttr(n.opacity)}>${esc(n.text)}</text>`;
}

function imageSvg(n: ImageNode): string {
  const par =
    n.fit === "contain"
      ? "xMidYMid meet"
      : n.fit === "fill"
        ? "none"
        : n.fit === "none"
          ? "xMinYMin slice"
          : "xMidYMid slice";
  const clip = n.radius ? ` clip-path="inset(0 round ${fmt(n.radius)}px)"` : "";
  return `<image x="${fmt(n.x)}" y="${fmt(n.y)}" width="${fmt(n.width)}" height="${fmt(n.height)}" href="${esc(n.href)}" preserveAspectRatio="${par}"${clip}${nodeOpacityAttr(n.opacity)}/>`;
}

function nodeToSvg(node: DrawNode): string {
  switch (node.kind) {
    case "rect":
      return rectSvg(node);
    case "ellipse":
      return ellipseSvg(node);
    case "line":
      return lineSvg(node);
    case "polyline":
      return polylineSvg(node);
    case "text":
      return textSvg(node);
    case "image":
      return imageSvg(node);
    case "group": {
      const translate =
        (node.x ?? 0) !== 0 || (node.y ?? 0) !== 0
          ? ` transform="translate(${fmt(node.x ?? 0)} ${fmt(node.y ?? 0)})"`
          : "";
      const inner = node.children.map(nodeToSvg).join("");
      return `<g${translate}${nodeOpacityAttr(node.opacity)}>${inner}</g>`;
    }
    default:
      return "";
  }
}

function placeholderNode(type: string, width: number, height: number): DrawNode {
  return {
    kind: "group",
    children: [
      {
        kind: "rect",
        x: 0,
        y: 0,
        width,
        height,
        fill: { color: "#ff00ff", opacity: 0.12 },
        stroke: { color: "#ff00ff", width: 2, opacity: 0.8 },
      },
      {
        kind: "text",
        x: width / 2,
        y: height / 2,
        text: `?${type}`,
        fontSize: Math.max(12, Math.min(width, height) * 0.12),
        fill: { color: "#ff00ff" },
        align: "center",
        baseline: "middle",
      },
    ],
  };
}

function elementToSvg(
  resolved: ResolvedElement,
  registry: RenderRegistry,
  ctx: RenderContext,
): string {
  if (!resolved.visible) return "";
  const { element } = resolved;
  const renderer = registry.get(element.type);
  const own = renderer
    ? renderer.render(element, ctx)
    : placeholderNode(element.type, element.transform.width, element.transform.height);

  const parts: string[] = [];
  if (own) parts.push(nodeToSvg(own));
  for (const child of resolved.children) {
    parts.push(elementToSvg(child, registry, ctx));
  }
  if (parts.length === 0) return "";

  const transform = toSvgTransform(resolved.transform);
  const opacity = nodeOpacityAttr(resolved.opacity);
  return `<g transform="${transform}"${opacity}>${parts.join("")}</g>`;
}

function backgroundToSvg(
  background: BackgroundDefinition | null,
  width: number,
  height: number,
  ctx: RenderContext,
  idPrefix: string,
): string {
  if (!background || background.type === "none") return "";
  switch (background.type) {
    case "solid":
      return `<rect x="0" y="0" width="${fmt(width)}" height="${fmt(height)}" fill="${esc(background.color)}"/>`;
    case "gradient": {
      const id = `${idPrefix}-grad`;
      const angle = background.angle ?? 0;
      const rad = (angle * Math.PI) / 180;
      const x2 = fmt(Math.cos(rad));
      const y2 = fmt(Math.sin(rad));
      const stops = background.stops
        .map(
          (s) =>
            `<stop offset="${fmt(s.position * 100)}%" stop-color="${esc(s.color)}"/>`,
        )
        .join("");
      return `<defs><linearGradient id="${id}" x1="0" y1="0" x2="${x2}" y2="${y2}">${stops}</linearGradient></defs><rect x="0" y="0" width="${fmt(width)}" height="${fmt(height)}" fill="url(#${id})"/>`;
    }
    case "image": {
      const href = ctx.resolveAssetUrl(background.assetId);
      if (!href) return "";
      const par = background.fit === "contain" ? "xMidYMid meet" : "xMidYMid slice";
      return `<image x="0" y="0" width="${fmt(width)}" height="${fmt(height)}" href="${esc(href)}" preserveAspectRatio="${par}"/>`;
    }
    case "video":
      // Video frames are not deterministically renderable in static SVG; paint a neutral fill.
      return `<rect x="0" y="0" width="${fmt(width)}" height="${fmt(height)}" fill="#0a0e16"/>`;
    default:
      return "";
  }
}

/** Render a project to a deterministic SVG string at the given global time. */
export function renderProjectToSvg(
  project: MotionProject,
  timeSeconds: number,
  registry: RenderRegistry,
  options: SvgRenderOptions = {},
): string {
  const { width, height, backgroundColor } = project.settings;
  const ctx = createRenderContext(project);
  const frame = evaluateProjectAtTime(project, timeSeconds);

  const base = `<rect x="0" y="0" width="${fmt(width)}" height="${fmt(height)}" fill="${esc(backgroundColor)}"/>`;
  const bg = backgroundToSvg(
    frame.background,
    width,
    height,
    ctx,
    `s${frame.sceneIndex}`,
  );
  const body = frame.elements.map((el) => elementToSvg(el, registry, ctx)).join("");

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${fmt(width)}" height="${fmt(height)}" viewBox="0 0 ${fmt(width)} ${fmt(height)}">${base}${bg}${body}</svg>`;
  return options.includeXmlDeclaration
    ? `<?xml version="1.0" encoding="UTF-8"?>${svg}`
    : svg;
}

/** {@link FrameRenderer} implementation backed by the deterministic SVG serializer. */
export class SvgFrameRenderer implements FrameRenderer {
  private project: MotionProject | null = null;

  constructor(
    private readonly registry: RenderRegistry,
    private readonly options: SvgRenderOptions = {},
  ) {}

  initialize(project: MotionProject): Promise<void> {
    this.project = project;
    return Promise.resolve();
  }

  renderFrame(timeSeconds: number): Promise<RenderedFrame> {
    if (!this.project) {
      return Promise.reject(
        new Error("SvgFrameRenderer.initialize must be called first."),
      );
    }
    const payload = renderProjectToSvg(
      this.project,
      timeSeconds,
      this.registry,
      this.options,
    );
    return Promise.resolve({
      width: this.project.settings.width,
      height: this.project.settings.height,
      mediaType: "image/svg+xml",
      payload,
    });
  }

  dispose(): Promise<void> {
    this.project = null;
    return Promise.resolve();
  }
}
