/**
 * Deterministic easing functions (spec §14.7). Each maps a normalized progress `t ∈ [0, 1]` to an
 * eased value. Pure and stateless: no clocks, no randomness (spec §23).
 */
import type { EasingDefinition, EasingType } from "@motion-studio/core";

export type EasingFn = (t: number) => number;

const clamp01 = (t: number): number => (t < 0 ? 0 : t > 1 ? 1 : t);

const c1 = 1.70158;
const c3 = c1 + 1;

export const easingFns: Record<EasingType, EasingFn> = {
  linear: (t) => t,
  ease: (t) => cubicBezier(0.25, 0.1, 0.25, 1)(t),
  "ease-in": (t) => t * t,
  "ease-out": (t) => 1 - (1 - t) * (1 - t),
  "ease-in-out": (t) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2),
  "cubic-bezier": (t) => t, // overridden when bezier control points are supplied
  bounce: (t) => bounceOut(t),
  elastic: (t) => {
    const c4 = (2 * Math.PI) / 3;
    if (t === 0 || t === 1) return t;
    return Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
  },
  back: (t) => c3 * t * t * t - c1 * t * t,
  spring: (t) => {
    // Lightweight critically-damped-ish spring approximation, deterministic.
    return 1 - Math.pow(2, -10 * t) * Math.cos((t * 10 * Math.PI) / 2);
  },
};

function bounceOut(t: number): number {
  const n1 = 7.5625;
  const d1 = 2.75;
  if (t < 1 / d1) return n1 * t * t;
  if (t < 2 / d1) return n1 * (t -= 1.5 / d1) * t + 0.75;
  if (t < 2.5 / d1) return n1 * (t -= 2.25 / d1) * t + 0.9375;
  return n1 * (t -= 2.625 / d1) * t + 0.984375;
}

/** Cubic Bezier easing (De Casteljau sampling), matching CSS `cubic-bezier(x1,y1,x2,y2)`. */
export function cubicBezier(x1: number, y1: number, x2: number, y2: number): EasingFn {
  const sampleCurveX = (t: number): number => {
    const u = 1 - t;
    return 3 * u * u * t * x1 + 3 * u * t * t * x2 + t * t * t;
  };
  const sampleCurveY = (t: number): number => {
    const u = 1 - t;
    return 3 * u * u * t * y1 + 3 * u * t * t * y2 + t * t * t;
  };
  return (x: number): number => {
    if (x <= 0) return 0;
    if (x >= 1) return 1;
    let low = 0;
    let high = 1;
    let t = x;
    for (let i = 0; i < 24; i += 1) {
      const cx = sampleCurveX(t);
      if (Math.abs(cx - x) < 1e-5) break;
      if (cx < x) low = t;
      else high = t;
      t = (low + high) / 2;
    }
    return sampleCurveY(t);
  };
}

/** Resolve an {@link EasingDefinition} to a concrete easing function. */
export function resolveEasing(easing: EasingDefinition | undefined): EasingFn {
  if (!easing) return easingFns.linear;
  if (easing.type === "cubic-bezier" && easing.bezier) {
    const [x1, y1, x2, y2] = easing.bezier;
    return cubicBezier(x1, y1, x2, y2);
  }
  return easingFns[easing.type] ?? easingFns.linear;
}

/** Ease a normalized progress value with a named easing. */
export function ease(type: EasingType, t: number): number {
  return (easingFns[type] ?? easingFns.linear)(clamp01(t));
}
