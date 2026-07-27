/**
 * "bar-chart" component. Renders a simple vertical bar chart from a list of numeric values.
 * Bars are scaled to the tallest value and laid out left-to-right across the content box, which
 * spans `[0, 0] → [width, height]` in element-local coordinates.
 */
import { type MotionElement } from "@motion-studio/core";
import {
  type DrawNode,
  type LineNode,
  type TextNode,
  group,
} from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

const num = (v: unknown, d: number): number =>
  typeof v === "number" && Number.isFinite(v) ? v : d;

const propsSchema = z.object({
  values: z.array(z.number()).default([3, 6, 4, 8, 5]),
  color: z.string().default("#ffd000"),
  gap: z.number().default(12),
  /** Optional x-axis labels under each bar. */
  labels: z.array(z.string()).optional(),
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

    const labels = p.labels ?? [];
    const labelH = labels.length ? 34 : 0;
    const plotH = Math.max(1, H - labelH);
    const max = Math.max(...vals.map((v) => num(v, 0)), 1);
    const gap = num(p.gap, 12);
    const bw = (W - gap * (n - 1)) / n;

    const children: DrawNode[] = [];
    // baseline
    children.push({
      kind: "line",
      x1: 0,
      y1: plotH,
      x2: W,
      y2: plotH,
      stroke: { color: "#ffffff", width: 1, opacity: 0.15 },
    } satisfies LineNode);

    vals.forEach((raw, i) => {
      const v = num(raw, 0);
      const h = (v / max) * plotH;
      const x = i * (bw + gap);
      children.push({
        kind: "rect",
        x,
        y: plotH - h,
        width: bw,
        height: h,
        radius: 6,
        fill: { color: p.color },
      });
      const label = labels[i];
      if (label) {
        children.push({
          kind: "text",
          x: x + bw / 2,
          y: plotH + labelH / 2,
          text: label,
          fontSize: 20,
          fill: { color: "#9aa3b2" },
          align: "center",
          baseline: "middle",
        } satisfies TextNode);
      }
    });

    return group(children);
  },
};
