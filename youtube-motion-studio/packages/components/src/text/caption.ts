/**
 * "caption" component. Renders a single line of caption text centered on a rounded
 * background rect. Coordinates are element-local: the content box spans
 * `[0, 0] → [width, height]` from the resolved transform.
 */
import type { MotionElement } from "@motion-studio/core";
import { type DrawNode, group } from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

export interface CaptionProps {
  text: string;
  fontSize: number;
  color: string;
  background: string;
  radius: number;
}

const propsSchema = z.object({
  text: z.string().default("Caption"),
  fontSize: z.number().default(44),
  color: z.string().default("#ffffff"),
  background: z.string().default("#111111"),
  radius: z.number().default(12),
});

const defaultProps: CaptionProps = {
  text: "Caption",
  fontSize: 44,
  color: "#ffffff",
  background: "#111111",
  radius: 12,
};

export const captionComponent: ComponentDefinition<CaptionProps> = {
  type: "caption",
  displayName: "Caption",
  category: "text",
  propsSchema,
  defaultProps,
  defaultTransform: { width: 900, height: 110 },
  render(element: MotionElement): DrawNode | null {
    const p = readProps(captionComponent, element);
    const W = element.transform.width;
    const H = element.transform.height;

    const textNode: DrawNode = {
      kind: "text",
      x: W / 2,
      y: H / 2,
      text: p.text,
      fontSize: p.fontSize,
      fill: { color: p.color },
      align: "center",
      baseline: "middle",
    };

    // No background pill when the background is empty / "none" / "transparent".
    const hasBackground =
      p.background !== "" && p.background !== "none" && p.background !== "transparent";
    if (!hasBackground) return textNode;

    const background: DrawNode = {
      kind: "rect",
      x: 0,
      y: 0,
      width: W,
      height: H,
      radius: p.radius,
      fill: { color: p.background },
    };
    return group([background, textNode]);
  },
};
