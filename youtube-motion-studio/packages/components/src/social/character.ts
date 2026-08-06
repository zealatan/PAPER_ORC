/**
 * "character" social component. A simple stylized mascot composed of a rounded body rect, an
 * elliptical head, and two eyes. Coordinates are element-local: the content box spans
 * `[0, 0] → [width, height]` from the resolved transform.
 */
import type { MotionElement } from "@motion-studio/core";
import {
  type DrawNode,
  type EllipseNode,
  type RectNode,
  group,
} from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

export interface CharacterProps {
  color: string;
  faceColor: string;
}

const propsSchema = z.object({
  color: z.string().default("#ffd000"),
  faceColor: z.string().default("#111111"),
});

const defaultProps: CharacterProps = {
  color: "#ffd000",
  faceColor: "#111111",
};

export const characterComponent: ComponentDefinition<CharacterProps> = {
  type: "character",
  displayName: "Character",
  category: "social",
  propsSchema,
  defaultProps,
  defaultTransform: { width: 300, height: 420 },
  render(element: MotionElement): DrawNode | null {
    const p = readProps(characterComponent, element);
    const W = element.transform.width;
    const H = element.transform.height;

    const body: RectNode = {
      kind: "rect",
      x: W * 0.2,
      y: H * 0.42,
      width: W * 0.6,
      height: H * 0.5,
      radius: W * 0.15,
      fill: { color: p.color },
    };

    const head: EllipseNode = {
      kind: "ellipse",
      cx: W / 2,
      cy: H * 0.28,
      rx: W * 0.28,
      ry: W * 0.28,
      fill: { color: p.color },
    };

    const eyeL: EllipseNode = {
      kind: "ellipse",
      cx: W * 0.42,
      cy: H * 0.26,
      rx: 8,
      ry: 8,
      fill: { color: p.faceColor },
    };

    const eyeR: EllipseNode = {
      kind: "ellipse",
      cx: W * 0.58,
      cy: H * 0.26,
      rx: 8,
      ry: 8,
      fill: { color: p.faceColor },
    };

    return group([body, head, eyeL, eyeR]);
  },
};
