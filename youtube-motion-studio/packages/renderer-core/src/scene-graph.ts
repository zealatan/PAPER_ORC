/**
 * Backend-agnostic scene-graph IR.
 *
 * Components map their (props, style, resolved transform) to a tree of {@link DrawNode}
 * primitives. Each renderer backend (SVG, Pixi, …) knows only how to paint these primitives, so
 * component logic is never duplicated per backend (spec §0: "no duplicated rendering logic").
 *
 * All coordinates in a component's returned nodes are in the element's **local** space, where the
 * content box spans `[0, 0] → [width, height]`. Placement, rotation, scale, anchor and element
 * opacity are applied by the enclosing group the renderer creates from the resolved transform.
 */

export type TextAlign = "left" | "center" | "right";
export type TextBaseline = "top" | "middle" | "bottom" | "alphabetic";

export interface Fill {
  color: string;
  opacity?: number;
}

export interface Stroke {
  color: string;
  width: number;
  opacity?: number;
}

interface DrawNodeBase {
  /** Stable id for diffing / debugging. */
  id?: string;
  /** Node-local opacity multiplier, 0..1. */
  opacity?: number;
}

export interface RectNode extends DrawNodeBase {
  kind: "rect";
  x: number;
  y: number;
  width: number;
  height: number;
  radius?: number;
  fill?: Fill;
  stroke?: Stroke;
}

export interface EllipseNode extends DrawNodeBase {
  kind: "ellipse";
  cx: number;
  cy: number;
  rx: number;
  ry: number;
  fill?: Fill;
  stroke?: Stroke;
}

export interface LineNode extends DrawNodeBase {
  kind: "line";
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  stroke: Stroke;
}

export interface TextNode extends DrawNodeBase {
  kind: "text";
  x: number;
  y: number;
  text: string;
  fontSize: number;
  fontWeight?: number;
  fontFamily?: string;
  fill: Fill;
  align?: TextAlign;
  baseline?: TextBaseline;
  /** Optional wrapping width in local px. */
  maxWidth?: number;
  letterSpacing?: number;
  lineHeight?: number;
}

export interface ImageNode extends DrawNodeBase {
  kind: "image";
  x: number;
  y: number;
  width: number;
  height: number;
  /** Resolved asset URL (data/object/remote). */
  href: string;
  radius?: number;
  fit?: "cover" | "contain" | "fill" | "none";
}

export interface GroupNode extends DrawNodeBase {
  kind: "group";
  /** Optional local translation applied to children (in addition to element transform). */
  x?: number;
  y?: number;
  children: DrawNode[];
}

export type DrawNode =
  RectNode | EllipseNode | LineNode | TextNode | ImageNode | GroupNode;

/** Convenience: a group wrapping several nodes. */
export function group(children: DrawNode[], base?: Partial<GroupNode>): GroupNode {
  return { kind: "group", children, ...base };
}
