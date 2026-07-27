/**
 * "title" component. Renders a single line of title text into a scene-graph text
 * primitive. Coordinates are element-local: the content box spans `[0, 0] → [width,
 * height]` from the resolved transform.
 */
import type { MotionElement } from "@motion-studio/core";
import type { DrawNode } from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

export interface TitleProps {
  text: string;
  fontSize: number;
  color: string;
  align: "left" | "center" | "right";
  fontWeight: number;
  fontFamily?: string;
}

const propsSchema = z.object({
  text: z.string().default("Title"),
  fontSize: z.number().default(88),
  color: z.string().default("#ffffff"),
  align: z.enum(["left", "center", "right"]).default("center"),
  fontWeight: z.number().default(800),
  /** Optional font family (e.g. a heavy display face for hero numbers). */
  fontFamily: z.string().optional(),
});

const defaultProps: TitleProps = {
  text: "Title",
  fontSize: 88,
  color: "#ffffff",
  align: "center",
  fontWeight: 800,
};

export const titleComponent: ComponentDefinition<TitleProps> = {
  type: "title",
  displayName: "Title",
  category: "text",
  propsSchema,
  defaultProps,
  defaultTransform: { width: 900, height: 160 },
  render(element: MotionElement): DrawNode | null {
    const p = readProps(titleComponent, element);
    const W = element.transform.width;
    const H = element.transform.height;

    const x = p.align === "center" ? W / 2 : p.align === "right" ? W : 0;

    const textNode: DrawNode = {
      kind: "text",
      x,
      y: H / 2,
      text: p.text,
      fontSize: p.fontSize,
      fontWeight: p.fontWeight,
      ...(p.fontFamily ? { fontFamily: p.fontFamily } : {}),
      fill: { color: p.color },
      align: p.align,
      baseline: "middle",
    };

    return textNode;
  },
};
