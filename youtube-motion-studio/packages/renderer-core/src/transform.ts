/**
 * Transform math shared by every backend so SVG and Pixi produce identical placement
 * (spec §0: no duplicated rendering logic). A {@link Transform2D} places the element's anchor
 * point at `(x, y)` and applies rotation/scale/skew about that anchor.
 */
import type { Transform2D } from "@motion-studio/core";

/** 2D affine matrix in the SVG/Canvas convention: [a, b, c, d, e, f]. */
export type Matrix2D = [number, number, number, number, number, number];

const DEG_TO_RAD = Math.PI / 180;

function round(value: number): number {
  // Stabilize tiny floating error for deterministic, byte-stable output.
  const r = Math.round(value * 1e6) / 1e6;
  return Object.is(r, -0) ? 0 : r;
}

/** Anchor offset in element-local pixels. */
export function anchorOffset(t: Transform2D): { ax: number; ay: number } {
  return { ax: t.anchorX * t.width, ay: t.anchorY * t.height };
}

/**
 * Compose the element transform as an ordered op list:
 * `translate(x,y) rotate scale skew translate(-anchor)`.
 * Returned as a single affine matrix.
 */
export function toMatrix(t: Transform2D): Matrix2D {
  const { ax, ay } = anchorOffset(t);
  const cos = Math.cos(t.rotation * DEG_TO_RAD);
  const sin = Math.sin(t.rotation * DEG_TO_RAD);
  const tanX = Math.tan(t.skewX * DEG_TO_RAD);
  const tanY = Math.tan(t.skewY * DEG_TO_RAD);

  // M = T(x,y) * R(rot) * S(sx,sy) * Skew * T(-ax,-ay)
  // rotation * scale
  let a = cos * t.scaleX;
  let b = sin * t.scaleX;
  let c = -sin * t.scaleY;
  let d = cos * t.scaleY;

  // apply skew (multiply RS * Skew where Skew = [1, tanY, tanX, 1, 0, 0])
  const a2 = a + c * tanY;
  const b2 = b + d * tanY;
  const c2 = a * tanX + c;
  const d2 = b * tanX + d;
  a = a2;
  b = b2;
  c = c2;
  d = d2;

  // translate to (x,y) and pre-translate by -anchor
  const e = t.x - (a * ax + c * ay);
  const f = t.y - (b * ax + d * ay);

  return [round(a), round(b), round(c), round(d), round(e), round(f)];
}

/** SVG `transform` attribute value for an element transform. */
export function toSvgTransform(t: Transform2D): string {
  const [a, b, c, d, e, f] = toMatrix(t);
  return `matrix(${a} ${b} ${c} ${d} ${e} ${f})`;
}
