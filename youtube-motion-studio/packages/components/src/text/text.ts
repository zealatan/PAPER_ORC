/**
 * "text" component (spec §8.1). Renders a single line of styled text into scene-graph
 * primitives, optionally on a rounded background rect. Coordinates are element-local: the
 * content box spans `[0, 0] → [width, height]` from the resolved transform.
 */
import type { MotionElement } from "@motion-studio/core";
import { type DrawNode, group } from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

export interface TextProps {
  text: string;
  fontSize: number;
  fontWeight: number;
  textAlign: "left" | "center" | "right";
  color?: string;
  fontFamily?: string;
}

const propsSchema = z.object({
  text: z.string().default(""),
  fontSize: z.number().default(48),
  fontWeight: z.number().default(600),
  textAlign: z.enum(["left", "center", "right"]).default("left"),
  color: z.string().optional(),
  fontFamily: z.string().optional(),
});

const defaultProps: TextProps = {
  text: "",
  fontSize: 48,
  fontWeight: 600,
  textAlign: "left",
};

const str = (v: unknown, d: string): string => (typeof v === "string" ? v : d);
const num = (v: unknown, d: number): number =>
  typeof v === "number" && Number.isFinite(v) ? v : d;

export const textComponent: ComponentDefinition<TextProps> = {
  type: "text",
  displayName: "Text",
  category: "text",
  propsSchema,
  defaultProps,
  defaultTransform: { width: 640, height: 140 },
  render(element: MotionElement): DrawNode | null {
    const p = readProps(textComponent, element);
    const W = element.transform.width;
    const H = element.transform.height;

    const color = p.color ?? str(element.style.color, "#ffffff");
    const x = p.textAlign === "center" ? W / 2 : p.textAlign === "right" ? W : 0;

    const textNode: DrawNode = {
      kind: "text",
      x,
      y: H / 2,
      text: p.text,
      fontSize: p.fontSize,
      fontWeight: p.fontWeight,
      fontFamily: p.fontFamily,
      fill: { color },
      align: p.textAlign,
      baseline: "middle",
    };

    const background = element.style.backgroundColor;
    if (typeof background === "string") {
      const bgRect: DrawNode = {
        kind: "rect",
        x: 0,
        y: 0,
        width: W,
        height: H,
        radius: num(element.style.borderRadius, 0) || undefined,
        fill: { color: background },
      };
      return group([bgRect, textNode]);
    }

    return textNode;
  },
};
