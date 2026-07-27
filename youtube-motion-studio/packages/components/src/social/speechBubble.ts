/**
 * "speech-bubble" social component. Renders a rounded bubble with a downward tail and centered
 * text. Coordinates are element-local: the content box spans `[0, 0] → [width, height]` from the
 * resolved transform, and a fixed strip at the bottom is reserved for the tail.
 */
import type { MotionElement } from "@motion-studio/core";
import {
  type DrawNode,
  type PolylineNode,
  type RectNode,
  type TextNode,
  group,
} from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

export interface SpeechBubbleProps {
  text: string;
  background: string;
  color: string;
  radius: number;
}

const propsSchema = z.object({
  text: z.string().default("..."),
  background: z.string().default("#ffffff"),
  color: z.string().default("#111111"),
  radius: z.number().default(20),
});

const defaultProps: SpeechBubbleProps = {
  text: "...",
  background: "#ffffff",
  color: "#111111",
  radius: 20,
};

export const speechBubbleComponent: ComponentDefinition<SpeechBubbleProps> = {
  type: "speech-bubble",
  displayName: "Speech Bubble",
  category: "social",
  propsSchema,
  defaultProps,
  defaultTransform: { width: 600, height: 260 },
  render(element: MotionElement): DrawNode | null {
    const p = readProps(speechBubbleComponent, element);
    const W = element.transform.width;
    const H = element.transform.height;
    const tail = 28;

    const bubble: RectNode = {
      kind: "rect",
      x: 0,
      y: 0,
      width: W,
      height: H - tail,
      radius: p.radius,
      fill: { color: p.background },
    };

    const tailNode: PolylineNode = {
      kind: "polyline",
      points: [
        [W * 0.3, H - tail],
        [W * 0.45, H],
        [W * 0.5, H - tail],
      ],
      closed: true,
      fill: { color: p.background },
    };

    const textNode: TextNode = {
      kind: "text",
      x: W / 2,
      y: (H - tail) / 2,
      align: "center",
      baseline: "middle",
      text: p.text,
      fontSize: 36,
      fill: { color: p.color },
      maxWidth: W - 60,
    };

    return group([bubble, tailNode, textNode]);
  },
};
