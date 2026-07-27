/**
 * "table" component (spec §8.1). Renders a simple grid of string cells into scene-graph
 * primitives: a set of interior grid lines plus left-aligned text per cell. Coordinates are
 * element-local: the content box spans `[0, 0] → [width, height]` from the resolved transform.
 */
import type { MotionElement } from "@motion-studio/core";
import { type DrawNode, group } from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

export interface TableProps {
  rows: string[][];
  color: string;
  lineColor: string;
}

const propsSchema = z.object({
  rows: z.array(z.array(z.string())).default([
    ["A", "1"],
    ["B", "2"],
    ["C", "3"],
  ]),
  color: z.string().default("#ffffff"),
  lineColor: z.string().default("#2a2f3a"),
});

const defaultProps: TableProps = {
  rows: [
    ["A", "1"],
    ["B", "2"],
    ["C", "3"],
  ],
  color: "#ffffff",
  lineColor: "#2a2f3a",
};

export const tableComponent: ComponentDefinition<TableProps> = {
  type: "table",
  displayName: "Table",
  category: "chart",
  propsSchema,
  defaultProps,
  defaultTransform: { width: 700, height: 360 },
  render(element: MotionElement): DrawNode | null {
    const p = readProps(tableComponent, element);
    const W = element.transform.width;
    const H = element.transform.height;

    const rows = p.rows.length ? p.rows : [[""]];
    const nR = rows.length;
    const nC = Math.max(...rows.map((r) => r.length), 1);
    const rh = H / nR;
    const cw = W / nC;

    const children: DrawNode[] = [];

    for (let i = 1; i < nR; i += 1) {
      children.push({
        kind: "line",
        x1: 0,
        y1: i * rh,
        x2: W,
        y2: i * rh,
        stroke: { color: p.lineColor, width: 1 },
      });
    }

    for (let j = 1; j < nC; j += 1) {
      children.push({
        kind: "line",
        x1: j * cw,
        y1: 0,
        x2: j * cw,
        y2: H,
        stroke: { color: p.lineColor, width: 1 },
      });
    }

    rows.forEach((row, ri) => {
      row.forEach((cell, ci) => {
        children.push({
          kind: "text",
          x: ci * cw + 12,
          y: ri * rh + rh / 2,
          text: String(cell),
          fontSize: 24,
          fill: { color: p.color },
          align: "left",
          baseline: "middle",
        });
      });
    });

    return group(children);
  },
};
