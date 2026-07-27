/**
 * Pixi.js (v8) browser backend for the {@link FrameRenderer} contract. Unlike the deterministic
 * SVG backend, this composites the {@link EvaluatedFrame} onto a WebGL/WebGPU stage and extracts a
 * PNG data URL, so it is intended for in-browser preview/export and is NOT exercised by the Node
 * test suite (no WebGL). The real `pixi.js` module is loaded lazily inside {@link
 * PixiFrameRenderer.initialize} so that merely importing this file in Node never pulls in WebGL.
 */
import type { MotionProject } from "@motion-studio/core";
import type { Application, Container } from "pixi.js";
import type * as PixiNamespace from "pixi.js";
import type { DrawNode } from "../scene-graph";
import { evaluateProjectAtTime, type ResolvedElement } from "../timeline";
import { toMatrix } from "../transform";
import { createRenderContext } from "../registry";
import type {
  FrameRenderer,
  RenderContext,
  RenderedFrame,
  RenderRegistry,
} from "../types";

/** The lazily-imported `pixi.js` module namespace. */
type PixiModule = typeof PixiNamespace;

export interface PixiRendererOptions {
  background?: string;
}

/** Font weights Pixi's {@link TextStyle} accepts, indexed by hundreds bucket. */
const FONT_WEIGHT_BUCKETS = [
  "100",
  "200",
  "300",
  "400",
  "500",
  "600",
  "700",
  "800",
  "900",
] as const;

function toFontWeight(
  weight: number | undefined,
): (typeof FONT_WEIGHT_BUCKETS)[number] | undefined {
  if (typeof weight !== "number" || !Number.isFinite(weight)) return undefined;
  const index = Math.min(8, Math.max(0, Math.round(weight / 100) - 1));
  return FONT_WEIGHT_BUCKETS[index];
}

/** {@link FrameRenderer} implementation backed by a Pixi.js v8 renderer. */
export class PixiFrameRenderer implements FrameRenderer {
  private project: MotionProject | null = null;
  private app: Application | null = null;
  private pixi: PixiModule | null = null;

  constructor(
    private readonly registry: RenderRegistry,
    private readonly options: PixiRendererOptions = {},
  ) {}

  async initialize(project: MotionProject): Promise<void> {
    this.project = project;
    const PIXI = await import("pixi.js");
    const app = new PIXI.Application();
    await app.init({
      width: project.settings.width,
      height: project.settings.height,
      backgroundColor: this.options.background ?? project.settings.backgroundColor,
      antialias: true,
    });
    this.app = app;
    this.pixi = PIXI;
  }

  async renderFrame(timeSeconds: number): Promise<RenderedFrame> {
    const { app, project, pixi } = this;
    if (!app || !project || !pixi) {
      throw new Error("PixiFrameRenderer.initialize must be called first.");
    }

    const ctx = createRenderContext(project);
    const frame = evaluateProjectAtTime(project, timeSeconds);

    app.stage.removeChildren();
    for (const element of frame.elements) {
      this.renderElement(app.stage, element, ctx, pixi);
    }

    app.renderer.render(app.stage);
    const canvas = app.renderer.extract.canvas(app.stage);
    const payload = canvas.toDataURL ? canvas.toDataURL("image/png") : "";

    return {
      width: project.settings.width,
      height: project.settings.height,
      mediaType: "image/png",
      payload,
    };
  }

  async dispose(): Promise<void> {
    this.app?.destroy(true);
    this.app = null;
    this.pixi = null;
    this.project = null;
  }

  /** Composite one resolved element (and its children) as nested Pixi containers. */
  private renderElement(
    parent: Container,
    resolved: ResolvedElement,
    ctx: RenderContext,
    PIXI: PixiModule,
  ): void {
    if (!resolved.visible) return;

    const container = new PIXI.Container();
    const [a, b, c, d, e, f] = toMatrix(resolved.transform);
    container.setFromMatrix(new PIXI.Matrix(a, b, c, d, e, f));
    container.alpha = resolved.opacity;

    const renderer = this.registry.get(resolved.element.type);
    const node = renderer ? renderer.render(resolved.element, ctx) : null;
    if (node) this.paintNode(container, node, PIXI);

    for (const child of resolved.children) {
      this.renderElement(container, child, ctx, PIXI);
    }

    parent.addChild(container);
  }

  /** Convert a {@link DrawNode} into Pixi display objects appended to `container`. */
  private paintNode(container: Container, node: DrawNode, PIXI: PixiModule): void {
    switch (node.kind) {
      case "rect": {
        const g = new PIXI.Graphics();
        if (node.radius && node.radius > 0) {
          g.roundRect(node.x, node.y, node.width, node.height, node.radius);
        } else {
          g.rect(node.x, node.y, node.width, node.height);
        }
        if (node.fill) g.fill({ color: node.fill.color, alpha: node.fill.opacity ?? 1 });
        if (node.stroke) {
          g.stroke({
            color: node.stroke.color,
            width: node.stroke.width,
            alpha: node.stroke.opacity ?? 1,
          });
        }
        g.alpha = node.opacity ?? 1;
        container.addChild(g);
        break;
      }
      case "ellipse": {
        const g = new PIXI.Graphics();
        g.ellipse(node.cx, node.cy, node.rx, node.ry);
        if (node.fill) g.fill({ color: node.fill.color, alpha: node.fill.opacity ?? 1 });
        if (node.stroke) {
          g.stroke({
            color: node.stroke.color,
            width: node.stroke.width,
            alpha: node.stroke.opacity ?? 1,
          });
        }
        g.alpha = node.opacity ?? 1;
        container.addChild(g);
        break;
      }
      case "line": {
        const g = new PIXI.Graphics();
        g.moveTo(node.x1, node.y1).lineTo(node.x2, node.y2);
        g.stroke({
          color: node.stroke.color,
          width: node.stroke.width,
          alpha: node.stroke.opacity ?? 1,
        });
        g.alpha = node.opacity ?? 1;
        container.addChild(g);
        break;
      }
      case "text": {
        const text = new PIXI.Text({
          text: node.text,
          style: {
            fontSize: node.fontSize,
            fontWeight: toFontWeight(node.fontWeight),
            fontFamily: node.fontFamily,
            fill: { color: node.fill.color, alpha: node.fill.opacity ?? 1 },
          },
        });
        text.x = node.x;
        text.y = node.y;
        text.alpha = node.opacity ?? 1;
        container.addChild(text);
        break;
      }
      case "image": {
        // No image loader in this static path: paint a neutral placeholder box.
        const g = new PIXI.Graphics();
        if (node.radius && node.radius > 0) {
          g.roundRect(node.x, node.y, node.width, node.height, node.radius);
        } else {
          g.rect(node.x, node.y, node.width, node.height);
        }
        g.fill({ color: "#333333", alpha: 0.5 });
        g.alpha = node.opacity ?? 1;
        container.addChild(g);
        break;
      }
      case "group": {
        const g = new PIXI.Container();
        g.x = node.x ?? 0;
        g.y = node.y ?? 0;
        g.alpha = node.opacity ?? 1;
        for (const child of node.children) {
          this.paintNode(g, child, PIXI);
        }
        container.addChild(g);
        break;
      }
      default:
        break;
    }
  }
}
