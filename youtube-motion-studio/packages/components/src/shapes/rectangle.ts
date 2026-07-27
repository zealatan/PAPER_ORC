/**
 * "rectangle" shape component. A rectangle carries no meaningful props of its own; its appearance
 * is driven entirely by `element.style` (background/border), consistent with the CSS-like styling
 * model. Coordinates are element-local: the box spans `[0, 0] → [width, height]`.
 */
import type { MotionElement } from "@motion-studio/core";
import type { DrawNode, RectNode, RenderContext } from "@motion-studio/renderer-core";
import { z } from "zod";
import type { ComponentDefinition } from "../types";

const str = (v: unknown, d: string): string => (typeof v === "string" ? v : d);
const num = (v: unknown, d: number): number =>
  typeof v === "number" && Number.isFinite(v) ? v : d;

export const rectangleComponent: ComponentDefinition = {
  type: "rectangle",
  displayName: "Rectangle",
  category: "shape",
  propsSchema: z.object({}).passthrough(),
  defaultProps: {},
  defaultTransform: { width: 240, height: 140 },
  render(element: MotionElement, _ctx: RenderContext): DrawNode {
    const W = element.transform.width;
    const H = element.transform.height;

    const fillColor = str(element.style.backgroundColor, "#ffffff");
    const borderColor = element.style.borderColor;
    const borderWidth = num(element.style.borderWidth, 0);
    const radius = num(element.style.borderRadius, 0);

    const node: RectNode = {
      kind: "rect",
      x: 0,
      y: 0,
      width: W,
      height: H,
      fill: { color: fillColor },
      stroke:
        borderWidth > 0 && typeof borderColor === "string"
          ? { color: borderColor, width: borderWidth }
          : undefined,
    };
    if (radius > 0) node.radius = radius;
    return node;
  },
};
