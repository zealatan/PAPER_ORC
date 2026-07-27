/**
 * "notification" component (spec §8.1). Renders a social/system-style notification card: a
 * rounded background, a colored icon square, a title line, and an optional body line.
 * Coordinates are element-local: the content box spans `[0, 0] → [width, height]` from the
 * resolved transform.
 */
import type { MotionElement } from "@motion-studio/core";
import { type DrawNode, group } from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

export interface NotificationProps {
  title: string;
  body: string;
  iconColor: string;
  background: string;
}

const propsSchema = z.object({
  title: z.string().default("Notification"),
  body: z.string().default(""),
  iconColor: z.string().default("#ff3b30"),
  background: z.string().default("#1e222b"),
});

const defaultProps: NotificationProps = {
  title: "Notification",
  body: "",
  iconColor: "#ff3b30",
  background: "#1e222b",
};

export const notificationComponent: ComponentDefinition<NotificationProps> = {
  type: "notification",
  displayName: "Notification",
  category: "social",
  propsSchema,
  defaultProps,
  defaultTransform: { width: 760, height: 150 },
  render(element: MotionElement): DrawNode | null {
    const p = readProps(notificationComponent, element);
    const W = element.transform.width;
    const H = element.transform.height;

    const nodes: DrawNode[] = [
      {
        kind: "rect",
        x: 0,
        y: 0,
        width: W,
        height: H,
        radius: 18,
        fill: { color: p.background },
      },
      {
        kind: "rect",
        x: 24,
        y: H / 2 - 28,
        width: 56,
        height: 56,
        radius: 12,
        fill: { color: p.iconColor },
      },
      {
        kind: "text",
        x: 110,
        y: p.body ? H * 0.36 : H / 2,
        text: p.title,
        fontSize: 30,
        fontWeight: 700,
        fill: { color: "#ffffff" },
        align: "left",
        baseline: "middle",
      },
    ];

    if (p.body) {
      nodes.push({
        kind: "text",
        x: 110,
        y: H * 0.66,
        text: p.body,
        fontSize: 24,
        fill: { color: "#9aa3b2" },
        align: "left",
        baseline: "middle",
        maxWidth: W - 130,
      });
    }

    return group(nodes);
  },
};
