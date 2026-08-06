import { describe, expect, it } from "vitest";
import type { PresetAnimation } from "@motion-studio/core";
import { animationProgress, resolveElementTransform } from "../src/animation";
import { makeElement } from "./helpers";

const preset = (over: Partial<PresetAnimation> = {}): PresetAnimation => ({
  id: "anim",
  kind: "preset",
  target: "transform",
  start: 0,
  duration: 1,
  presetId: "fade-in",
  ...over,
});

describe("animationProgress", () => {
  it("clamps to [0, 1] across the window", () => {
    const a = preset({ start: 1, duration: 2 });
    expect(animationProgress(a, 0)).toBe(0);
    expect(animationProgress(a, 2)).toBeCloseTo(0.5, 5);
    expect(animationProgress(a, 3)).toBe(1);
    expect(animationProgress(a, 10)).toBe(1);
  });
});

describe("resolveElementTransform", () => {
  it("fade-in ramps opacity from 0 to base", () => {
    const el = makeElement("a", "rectangle", {
      animations: [preset({ presetId: "fade-in" })],
    });
    expect(resolveElementTransform(el, 0).opacity).toBe(0);
    expect(resolveElementTransform(el, 1).opacity).toBeCloseTo(1, 5);
  });

  it("pop-in scales from ~0 up to exactly 1 at the end", () => {
    const el = makeElement("a", "rectangle", {
      animations: [preset({ presetId: "pop-in", params: { overshoot: 1.1 } })],
    });
    expect(resolveElementTransform(el, 0).transform.scaleX).toBeCloseTo(0, 5);
    expect(resolveElementTransform(el, 1).transform.scaleX).toBeCloseTo(1, 5);
  });

  it("leaves the base transform unchanged with no animations", () => {
    const el = makeElement("a", "rectangle");
    const r = resolveElementTransform(el, 0.5);
    expect(r.transform).toEqual(el.transform);
    expect(r.opacity).toBe(1);
  });

  it("is deterministic", () => {
    const el = makeElement("a", "rectangle", {
      animations: [
        preset({ presetId: "pop-in" }),
        preset({ id: "b", presetId: "fade-in" }),
      ],
    });
    expect(resolveElementTransform(el, 0.37)).toEqual(resolveElementTransform(el, 0.37));
  });

  it("ignores unknown presets (identity)", () => {
    const el = makeElement("a", "rectangle", {
      animations: [preset({ presetId: "does-not-exist" })],
    });
    expect(resolveElementTransform(el, 0.5).opacity).toBe(1);
  });
});
