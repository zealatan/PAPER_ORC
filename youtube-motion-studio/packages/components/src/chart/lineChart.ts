/**
 * "line-chart" component. Plots a series of numeric values as a polyline across the element's
 * content box, optionally filling the area beneath the line. Coordinates are element-local: the
 * box spans `[0, 0] → [width, height]` from the resolved transform. Values are normalized to the
 * box height so the line always fits regardless of scale.
 */
import type { MotionElement } from "@motion-studio/core";
import { type DrawNode, type PolylineNode, group } from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

export interface LineChartProps {
  values: number[];
  color: string;
  strokeWidth: number;
  area: boolean;
}

const propsSchema = z.object({
  values: z.array(z.number()).default([2, 5, 3, 8, 6, 9]),
  color: z.string().default("#4aa3ff"),
  strokeWidth: z.number().default(4),
  area: z.boolean().default(false),
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

    const vals = p.values.length ? p.values : [0];
    const max = Math.max(...vals, 1);
    const min = Math.min(...vals, 0);
    const span = max - min || 1;
    const n = vals.length;
    const step = n > 1 ? W / (n - 1) : W;

    const pts: [number, number][] = vals.map(
      (v, i) => [i * step, H - ((v - min) / span) * H] as [number, number],
    );

    const children: DrawNode[] = [];

    if (p.area) {
      const areaPoints: [number, number][] = [
        [0, H] as [number, number],
        ...pts,
        [W, H] as [number, number],
      ];
      const areaNode: PolylineNode = {
        kind: "polyline",
        points: areaPoints,
        closed: true,
        fill: { color: p.color, opacity: 0.18 },
      };
      children.push(areaNode);
    }

    const lineNode: PolylineNode = {
      kind: "polyline",
      points: pts,
      stroke: { color: p.color, width: p.strokeWidth },
    };
    children.push(lineNode);

    return group(children);
  },
};
