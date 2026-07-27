/**
 * "bar-chart" component. Renders a simple vertical bar chart from a list of numeric values.
 * Bars are scaled to the tallest value and laid out left-to-right across the content box, which
 * spans `[0, 0] → [width, height]` in element-local coordinates.
 */
import { type MotionElement } from "@motion-studio/core";
import { type DrawNode, type RectNode, group } from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

const num = (v: unknown, d: number): number =>
  typeof v === "number" && Number.isFinite(v) ? v : d;

const propsSchema = z.object({
  values: z.array(z.number()).default([3, 6, 4, 8, 5]),
  color: z.string().default("#ffd000"),
  gap: z.number().default(12),
});

type Props = z.infer<typeof propsSchema>;

export const barChartComponent: ComponentDefinition<Props> = {
  type: "bar-chart",
  displayName: "Bar Chart",
  category: "chart",
  propsSchema,
  defaultProps: {
    values: [3, 6, 4, 8, 5],
    color: "#ffd000",
    gap: 12,
  },
  defaultTransform: { width: 600, height: 360 },
  render(element: MotionElement): DrawNode | null {
    const p = readProps(barChartComponent, element);
    const W = element.transform.width;
    const H = element.transform.height;

    const vals = p.values.length ? p.values : [1];
    const n = vals.length;
    if (n < 1) return null;

    const max = Math.max(...vals.map((v) => num(v, 0)), 1);
    const gap = num(p.gap, 12);
    const bw = (W - gap * (n - 1)) / n;

    const children: RectNode[] = vals.map((raw, i) => {
      const v = num(raw, 0);
      const h = (v / max) * H;
      return {
        kind: "rect",
        x: i * (bw + gap),
        y: H - h,
        width: bw,
        height: h,
        radius: 6,
        fill: { color: p.color },
      };
    });

    return group(children);
  },
};
