/**
 * Authoring toolkit for the verification examples. Thin, strictly-typed builders over the core
 * domain model (spec §6) so each example's project.json is compact yet valid. Everything is
 * deterministic: timestamps are fixed and no clock/random is read.
 */
import {
  type AnimationDefinition,
  type BackgroundDefinition,
  type MotionElement,
  type MotionProject,
  type Scene,
  type Transform2D,
  createEmptyProject,
} from "@motion-studio/core";

export const W = 1080;
export const H = 1920;
export const FPS = 30;

/** Fixed creation timestamp keeps generated project.json byte-stable across runs. */
export const FIXED_NOW = "2026-07-27T00:00:00.000Z";

/** Shared dark palette (spec: 검정 배경 / 흰 텍스트 / 노랑 강조 / 청록·빨강 보조). */
export const C = {
  bg: "#0a0b0d",
  bgCard: "#15181f",
  border: "#2b313c",
  text: "#ffffff",
  dim: "#9aa3b2",
  accent: "#ffd000",
  teal: "#33d6c8",
  red: "#ff5a5a",
} as const;

export const TITLE_FONT = "Black Han Sans";
export const BODY_FONT = "Noto Sans CJK KR";

/** Vertical safe area for Shorts: keep important text away from the bottom UI band. */
export const SAFE_TOP = 260;
export const SAFE_BOTTOM = 1580;

const IDENTITY_TRANSFORM: Omit<Transform2D, "x" | "y" | "width" | "height"> = {
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
  anchorX: 0.5,
  anchorY: 0.5,
  skewX: 0,
  skewY: 0,
  opacity: 1,
  zIndex: 0,
};

/** A box centered at (cx, cy). Element content renders in local [0,0]→[w,h]; anchor 0.5 → (cx,cy) is its center. */
export function box(
  cx: number,
  cy: number,
  w: number,
  h: number,
  extra: Partial<Transform2D> = {},
): Transform2D {
  return { ...IDENTITY_TRANSFORM, x: cx, y: cy, width: w, height: h, ...extra };
}

export interface ElementInput {
  id: string;
  type: string;
  transform: Transform2D;
  props?: Record<string, unknown>;
  style?: Record<string, unknown>;
  /** Element visibility window within the scene (seconds). Defaults to the whole scene. */
  start?: number;
  duration?: number;
  animations?: AnimationDefinition[];
  zIndex?: number;
}

export function el(input: ElementInput): MotionElement {
  const transform =
    input.zIndex !== undefined
      ? { ...input.transform, zIndex: input.zIndex }
      : input.transform;
  return {
    id: input.id,
    type: input.type,
    name: input.id,
    visible: true,
    locked: false,
    transform,
    style: input.style ?? {},
    props: input.props ?? {},
    timing: { start: input.start ?? 0, duration: input.duration ?? 9999 },
    animations: input.animations ?? [],
  };
}

let animSeq = 0;
/** Entrance preset animation. presetId ∈ fade-in|pop-in|scale-in|zoom-in|slide-{left,right,up,down}. */
export function enter(
  presetId: string,
  start: number,
  duration: number,
  params?: Record<string, unknown>,
): AnimationDefinition {
  animSeq += 1;
  return {
    id: `anim-${animSeq}`,
    kind: "preset",
    target: "self",
    start,
    duration,
    presetId,
    ...(params ? { params } : {}),
  };
}

export function scene(
  id: string,
  name: string,
  duration: number,
  elements: MotionElement[],
  background: BackgroundDefinition = { type: "solid", color: C.bg },
): Scene {
  return { id, name, duration, background, elements };
}

export function project(
  id: string,
  name: string,
  scenes: Scene[],
  metadata: Record<string, unknown> = {},
): MotionProject {
  const p = createEmptyProject({
    id,
    name,
    now: FIXED_NOW,
    settings: { width: W, height: H, fps: FPS, backgroundColor: C.bg },
    themeId: "minimal-dark",
  });
  p.scenes = scenes;
  p.metadata = { generator: "examples-toolkit", ...metadata };
  return p;
}

/** Convenience: a heavy title (Black Han Sans), centered horizontally on `cx` (default canvas center). */
export function title(
  id: string,
  text: string,
  cy: number,
  opts: {
    size?: number;
    color?: string;
    start?: number;
    duration?: number;
    anim?: AnimationDefinition[];
    cx?: number;
    width?: number;
  } = {},
): MotionElement {
  return el({
    id,
    type: "title",
    transform: box(opts.cx ?? W / 2, cy, opts.width ?? W - 120, opts.size ?? 130),
    props: {
      text,
      fontSize: opts.size ?? 118,
      color: opts.color ?? C.text,
      align: "center",
      fontWeight: 900,
      fontFamily: TITLE_FONT,
    },
    start: opts.start,
    duration: opts.duration,
    animations: opts.anim,
    zIndex: 5,
  });
}

/** Convenience: a body caption (Noto Sans CJK KR) with optional pill background. */
export function caption(
  id: string,
  text: string,
  cy: number,
  opts: {
    size?: number;
    color?: string;
    background?: string;
    start?: number;
    duration?: number;
    anim?: AnimationDefinition[];
    width?: number;
    cx?: number;
  } = {},
): MotionElement {
  return el({
    id,
    type: "caption",
    transform: box(opts.cx ?? W / 2, cy, opts.width ?? W - 200, (opts.size ?? 48) + 40),
    props: {
      text,
      fontSize: opts.size ?? 46,
      color: opts.color ?? C.dim,
      background: opts.background ?? "",
      radius: 16,
    },
    start: opts.start,
    duration: opts.duration,
    animations: opts.anim,
    zIndex: 6,
  });
}

/** Convenience: a rounded card (rectangle styled through element.style). */
export function card(
  id: string,
  transform: Transform2D,
  opts: {
    fill?: string;
    border?: string;
    borderWidth?: number;
    radius?: number;
    start?: number;
    duration?: number;
    anim?: AnimationDefinition[];
    zIndex?: number;
  } = {},
): MotionElement {
  return el({
    id,
    type: "rectangle",
    transform,
    style: {
      backgroundColor: opts.fill ?? C.bgCard,
      borderColor: opts.border ?? C.border,
      borderWidth: opts.borderWidth ?? 2,
      borderRadius: opts.radius ?? 28,
    },
    start: opts.start,
    duration: opts.duration,
    animations: opts.anim,
    zIndex: opts.zIndex ?? 1,
  });
}
