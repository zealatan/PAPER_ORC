/**
 * "circle" shape component. Renders an ellipse filling the element's content box, so a square
 * transform yields a circle. Fill and stroke are read defensively from the untyped element style.
 */
import type { MotionElement } from "@motion-studio/core";
import type { EllipseNode, Stroke } from "@motion-studio/renderer-core";
import { z } from "zod";
import type { ComponentDefinition } from "../types";

const str = (v: unknown, d: string): string => (typeof v === "string" ? v : d);
const num = (v: unknown, d: number): number =>
  typeof v === "number" && Number.isFinite(v) ? v : d;

export const circleComponent: ComponentDefinition = {
  type: "circle",
  displayName: "Circle",
  category: "shape",
  propsSchema: z.object({}).passthrough(),
  defaultProps: {},
  defaultTransform: { width: 160, height: 160 },
  render(element: MotionElement): EllipseNode {
    const w = element.transform.width;
    const h = element.transform.height;
    const borderWidth = num(element.style.borderWidth, 0);
    const stroke: Stroke | undefined =
      borderWidth > 0 && typeof element.style.borderColor === "string"
        ? { color: element.style.borderColor, width: borderWidth }
        : undefined;
    return {
      kind: "ellipse",
      cx: w / 2,
      cy: h / 2,
      rx: w / 2,
      ry: h / 2,
      fill: { color: str(element.style.backgroundColor, "#ffffff") },
      stroke,
    };
  },
};
