/**
 * The "group" layout component: a pure container whose children are composited by the frame
 * renderer. Its own visual is empty unless an explicit `backgroundColor` style is set, in which
 * case it paints a single filled rectangle spanning its content box.
 */
import type { MotionElement } from "@motion-studio/core";
import type { DrawNode, RenderContext } from "@motion-studio/renderer-core";
import { z } from "zod";
import type { ComponentDefinition } from "../types";

const num = (v: unknown, d: number): number =>
  typeof v === "number" && Number.isFinite(v) ? v : d;

export const groupComponent: ComponentDefinition = {
  type: "group",
  displayName: "Group",
  category: "layout",
  propsSchema: z.object({}).passthrough(),
  defaultProps: {},
  defaultTransform: { width: 400, height: 400 },
  render(element: MotionElement, _ctx: RenderContext): DrawNode | null {
    const width = element.transform.width;
    const height = element.transform.height;
    const backgroundColor = element.style.backgroundColor;
    if (typeof backgroundColor !== "string") {
      return null;
    }
    return {
      kind: "rect",
      x: 0,
      y: 0,
      width,
      height,
      radius: num(element.style.borderRadius, 0) || undefined,
      fill: { color: backgroundColor },
    };
  },
};
