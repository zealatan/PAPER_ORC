import { describe, expect, it } from "vitest";
import { toMatrix, toSvgTransform } from "../src/transform";
import { makeTransform } from "./helpers";

describe("toMatrix", () => {
  it("produces identity + translation for a plain transform (anchor at origin)", () => {
    const m = toMatrix(makeTransform({ x: 10, y: 20 }));
    expect(m).toEqual([1, 0, 0, 1, 10, 20]);
  });

  it("applies scale", () => {
    const m = toMatrix(makeTransform({ x: 0, y: 0, scaleX: 2, scaleY: 3 }));
    expect(m).toEqual([2, 0, 0, 3, 0, 0]);
  });

  it("applies a 90-degree rotation", () => {
    const [a, b, c, d] = toMatrix(makeTransform({ rotation: 90 }));
    expect(a).toBeCloseTo(0, 5);
    expect(b).toBeCloseTo(1, 5);
    expect(c).toBeCloseTo(-1, 5);
    expect(d).toBeCloseTo(0, 5);
  });

  it("places the anchor point at (x, y)", () => {
    // width/height 100, anchor centered → anchor offset (50,50) maps to (x,y).
    const t = makeTransform({
      x: 200,
      y: 300,
      width: 100,
      height: 100,
      anchorX: 0.5,
      anchorY: 0.5,
    });
    const [a, b, c, d, e, f] = toMatrix(t);
    // local anchor (50,50) transformed must equal (200,300).
    expect(a * 50 + c * 50 + e).toBeCloseTo(200, 5);
    expect(b * 50 + d * 50 + f).toBeCloseTo(300, 5);
  });

  it("is deterministic", () => {
    const t = makeTransform({ x: 3.3333, rotation: 33, scaleX: 1.5 });
    expect(toMatrix(t)).toEqual(toMatrix(t));
  });
});

describe("toSvgTransform", () => {
  it("emits a matrix(...) string", () => {
    expect(toSvgTransform(makeTransform({ x: 5, y: 6 }))).toBe("matrix(1 0 0 1 5 6)");
  });
});
