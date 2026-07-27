/**
 * "line-chart" component. Plots one or more numeric series as polylines across the element's content
 * box, with optional area fill, y-axis grid + tick labels, and a legend. Coordinates are
 * element-local (`[0, 0] → [width, height]`); all series share one y-scale so they are comparable.
 */
import type { MotionElement } from "@motion-studio/core";
import {
  type DrawNode,
  type LineNode,
  type PolylineNode,
  type TextNode,
  group,
} from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

export interface LineSeries {
  values: number[];
  color: string;
  label?: string;
}

export interface LineChartProps {
  values: number[];
  color: string;
  strokeWidth: number;
  area: boolean;
  series?: LineSeries[];
  yTicks?: [number, string][];
  legend?: { color: string; label: string }[];
}

const propsSchema = z.object({
  values: z.array(z.number()).default([2, 5, 3, 8, 6, 9]),
  color: z.string().default("#4aa3ff"),
  strokeWidth: z.number().default(4),
  area: z.boolean().default(false),
  series: z
    .array(
      z.object({
        values: z.array(z.number()),
        color: z.string().default("#4aa3ff"),
        label: z.string().optional(),
      }),
    )
    .optional(),
  yTicks: z.array(z.tuple([z.number(), z.string()])).optional(),
  legend: z.array(z.object({ color: z.string(), label: z.string() })).optional(),
});

const defaultProps: LineChartProps = {
  values: [2, 5, 3, 8, 6, 9],
  color: "#4aa3ff",
  strokeWidth: 4,
  area: false,
};

export const lineChartComponent: ComponentDefinition<LineChartProps> = {
  type: "line-chart",
  displayName: "Line Chart",
  category: "chart",
  propsSchema,
  defaultProps,
  defaultTransform: { width: 600, height: 360 },
  render(element: MotionElement): DrawNode | null {
    const p = readProps(lineChartComponent, element);
    const W = element.transform.width;
    const H = element.transform.height;

    const series: LineSeries[] =
      p.series && p.series.length > 0
        ? p.series
        : [{ values: p.values.length ? p.values : [0], color: p.color }];

    const marginL = p.yTicks && p.yTicks.length ? 96 : 0;
    const marginT = p.legend && p.legend.length ? 44 : 0;
    const plotW = Math.max(1, W - marginL);
    const plotH = Math.max(1, H - marginT);

    const all = series.flatMap((s) => s.values);
    const tickVals = (p.yTicks ?? []).map(([v]) => v);
    const max = Math.max(...all, ...tickVals, 1);
    const min = Math.min(...all, ...tickVals, 0);
    const span = max - min || 1;
    const mapY = (v: number): number => marginT + plotH - ((v - min) / span) * plotH;
    const mapX = (i: number, n: number): number =>
      marginL + (n > 1 ? (i * plotW) / (n - 1) : 0);

    const children: DrawNode[] = [];

    // y-axis grid + labels
    for (const [value, label] of p.yTicks ?? []) {
      const y = mapY(value);
      children.push({
        kind: "line",
        x1: marginL,
        y1: y,
        x2: W,
        y2: y,
        stroke: { color: "#ffffff", width: 1, opacity: 0.12 },
      } satisfies LineNode);
      children.push({
        kind: "text",
        x: marginL - 10,
        y,
        text: label,
        fontSize: 22,
        fill: { color: "#9aa3b2" },
        align: "right",
        baseline: "middle",
      } satisfies TextNode);
    }

    // series
    series.forEach((s, si) => {
      const pts: [number, number][] = s.values.map(
        (v, i) => [mapX(i, s.values.length), mapY(v)] as [number, number],
      );
      if (p.area && si === 0) {
        children.push({
          kind: "polyline",
          points: [[marginL, H] as [number, number], ...pts, [W, H] as [number, number]],
          closed: true,
          fill: { color: s.color, opacity: 0.18 },
        } satisfies PolylineNode);
      }
      children.push({
        kind: "polyline",
        points: pts,
        stroke: { color: s.color, width: p.strokeWidth },
      } satisfies PolylineNode);
    });

    // legend (top-left, horizontal)
    let lx = marginL;
    for (const entry of p.legend ?? []) {
      children.push({
        kind: "rect",
        x: lx,
        y: 8,
        width: 26,
        height: 20,
        radius: 4,
        fill: { color: entry.color },
      });
      children.push({
        kind: "text",
        x: lx + 34,
        y: 18,
        text: entry.label,
        fontSize: 22,
        fill: { color: "#c9d3e4" },
        align: "left",
        baseline: "middle",
      } satisfies TextNode);
      lx += 34 + entry.label.length * 13 + 30;
    }

    return group(children);
  },
};
