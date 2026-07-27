/**
 * "topic-circle" component (spec §8.1). Renders a filled circle with a centered label,
 * useful for topic bubbles / social badges. Coordinates are element-local: the content box
 * spans `[0, 0] → [width, height]` from the resolved transform.
 */
import type { MotionElement } from "@motion-studio/core";
import { type DrawNode, group } from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

export interface TopicCircleProps {
  label: string;
  fill: string;
  color: string;
  fontSize: number;
}

const propsSchema = z.object({
  label: z.string().default("Topic"),
  fill: z.string().default("#1e88e5"),
  color: z.string().default("#ffffff"),
  fontSize: z.number().default(40),
});

const defaultProps: TopicCircleProps = {
  label: "Topic",
  fill: "#1e88e5",
  color: "#ffffff",
  fontSize: 40,
};

export const topicCircleComponent: ComponentDefinition<TopicCircleProps> = {
  type: "topic-circle",
  displayName: "Topic Circle",
  category: "social",
  propsSchema,
  defaultProps,
  defaultTransform: { width: 320, height: 320 },
  render(element: MotionElement): DrawNode | null {
    const p = readProps(topicCircleComponent, element);
    const W = element.transform.width;
    const H = element.transform.height;

    const circle: DrawNode = {
      kind: "ellipse",
      cx: W / 2,
      cy: H / 2,
      rx: W / 2,
      ry: H / 2,
      fill: { color: p.fill },
    };

    const label: DrawNode = {
      kind: "text",
      x: W / 2,
      y: H / 2,
      text: p.label,
      fontSize: p.fontSize,
      fontWeight: 700,
      fill: { color: p.color },
      align: "center",
      baseline: "middle",
    };

    return group([circle, label]);
  },
};
