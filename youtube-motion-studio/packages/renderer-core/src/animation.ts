/**
 * Deterministic animation evaluation (spec §15, §23). Given an element's scene-local time, this
 * computes the transform/opacity delta contributed by its animations. It is a pure function of
 * `(element, localTime)` — a frame at time `t` never depends on any previously rendered frame.
 *
 * Milestone 2 implements the common entrance/exit presets and a basic numeric keyframe evaluator;
 * the full preset library and per-property keyframe channels are extended in Milestone 6.
 */
import type {
  AnimationDefinition,
  MotionElement,
  Transform2D,
} from "@motion-studio/core";
import { ease, resolveEasing } from "./easing";

/** Multiplicative/additive delta applied over an element's base transform. */
export interface TransformDelta {
  translateX: number;
  translateY: number;
  scaleMul: number;
  rotateAdd: number;
  opacityMul: number;
}

export interface ResolvedTransform {
  transform: Transform2D;
  opacity: number;
}

const IDENTITY: TransformDelta = {
  translateX: 0,
  translateY: 0,
  scaleMul: 1,
  rotateAdd: 0,
  opacityMul: 1,
};

const clamp01 = (t: number): number => (t < 0 ? 0 : t > 1 ? 1 : t);
const num = (v: unknown, fallback: number): number =>
  typeof v === "number" && Number.isFinite(v) ? v : fallback;

type PresetFn = (p: number, params: Record<string, unknown>) => TransformDelta;

/** Entrance/exit preset registry keyed by presetId. */
const PRESETS: Record<string, PresetFn> = {
  "fade-in": (p) => ({ ...IDENTITY, opacityMul: ease("ease-out", p) }),
  "fade-out": (p) => ({ ...IDENTITY, opacityMul: 1 - ease("ease-in", p) }),
  "pop-in": (p, params) => {
    const overshoot = num(params.overshoot, 1.1);
    // back-eased scale from 0 → 1 with configurable overshoot peak.
    const eased = ease("back", p);
    const scale = eased * (1 + (overshoot - 1) * 4 * p * (1 - p));
    return { ...IDENTITY, scaleMul: p >= 1 ? 1 : scale, opacityMul: ease("ease-out", p) };
  },
  "scale-in": (p) => ({
    ...IDENTITY,
    scaleMul: ease("ease-out", p),
    opacityMul: ease("ease-out", p),
  }),
  "zoom-in": (p) => {
    const s = 0.6 + 0.4 * ease("ease-out", p);
    return { ...IDENTITY, scaleMul: p >= 1 ? 1 : s, opacityMul: ease("ease-out", p) };
  },
  "scale-out": (p) => ({
    ...IDENTITY,
    scaleMul: 1 - ease("ease-in", p),
    opacityMul: 1 - ease("ease-in", p),
  }),
  "slide-left": (p, params) => slide(p, -num(params.distance, 200), 0),
  "slide-right": (p, params) => slide(p, num(params.distance, 200), 0),
  "slide-up": (p, params) => slide(p, 0, num(params.distance, 200)),
  "slide-down": (p, params) => slide(p, 0, -num(params.distance, 200)),
};

function slide(p: number, fromX: number, fromY: number): TransformDelta {
  const e = ease("ease-out", p);
  return {
    ...IDENTITY,
    translateX: fromX * (1 - e),
    translateY: fromY * (1 - e),
    opacityMul: ease("ease-out", p),
  };
}

/** Normalized progress of an animation at a given scene-local time (clamped 0..1). */
export function animationProgress(
  animation: AnimationDefinition,
  localTime: number,
): number {
  const begin = animation.start + (animation.delay ?? 0);
  if (animation.duration <= 0) return localTime >= begin ? 1 : 0;
  return clamp01((localTime - begin) / animation.duration);
}

function evaluatePreset(
  animation: AnimationDefinition,
  localTime: number,
): TransformDelta {
  if (animation.kind !== "preset") return IDENTITY;
  const preset = PRESETS[animation.presetId];
  if (!preset) return IDENTITY;
  return preset(animationProgress(animation, localTime), animation.params ?? {});
}

function evaluateKeyframes(
  animation: AnimationDefinition,
  localTime: number,
): TransformDelta {
  if (animation.kind !== "keyframes" || animation.keyframes.length === 0) return IDENTITY;
  const t = localTime - animation.start - (animation.delay ?? 0);
  const frames = [...animation.keyframes].sort((a, b) => a.time - b.time);

  const first = frames[0]!;
  const last = frames[frames.length - 1]!;
  let value: number;
  if (t <= first.time) {
    value = num(first.value, 0);
  } else if (t >= last.time) {
    value = num(last.value, 0);
  } else {
    let lo = first;
    let hi = last;
    for (let i = 0; i < frames.length - 1; i += 1) {
      if (t >= frames[i]!.time && t <= frames[i + 1]!.time) {
        lo = frames[i]!;
        hi = frames[i + 1]!;
        break;
      }
    }
    const span = hi.time - lo.time || 1;
    const localP = clamp01((t - lo.time) / span);
    const eased = resolveEasing(hi.easing)(localP);
    value = num(lo.value, 0) + (num(hi.value, 0) - num(lo.value, 0)) * eased;
  }

  // Milestone 2 maps a numeric keyframe channel by target name; more channels land in M6.
  switch (animation.target) {
    case "opacity":
      return { ...IDENTITY, opacityMul: clamp01(value) };
    case "scale":
      return { ...IDENTITY, scaleMul: value };
    default:
      return IDENTITY;
  }
}

function compose(a: TransformDelta, b: TransformDelta): TransformDelta {
  return {
    translateX: a.translateX + b.translateX,
    translateY: a.translateY + b.translateY,
    scaleMul: a.scaleMul * b.scaleMul,
    rotateAdd: a.rotateAdd + b.rotateAdd,
    opacityMul: a.opacityMul * b.opacityMul,
  };
}

/** Resolve an element's transform + opacity at a scene-local time, applying all its animations. */
export function resolveElementTransform(
  element: MotionElement,
  localTime: number,
): ResolvedTransform {
  let delta = IDENTITY;
  for (const animation of element.animations) {
    const contribution =
      animation.kind === "preset"
        ? evaluatePreset(animation, localTime)
        : evaluateKeyframes(animation, localTime);
    delta = compose(delta, contribution);
  }

  const base = element.transform;
  const transform: Transform2D = {
    ...base,
    x: base.x + delta.translateX,
    y: base.y + delta.translateY,
    scaleX: base.scaleX * delta.scaleMul,
    scaleY: base.scaleY * delta.scaleMul,
    rotation: base.rotation + delta.rotateAdd,
  };
  const opacity = clamp01(base.opacity * delta.opacityMul);
  return { transform, opacity };
}
