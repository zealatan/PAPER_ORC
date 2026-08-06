/**
 * Cinematic authoring toolkit for the showcase Shorts (720×1280 / 15fps). Same deterministic,
 * strictly-typed builder approach as the examples toolkit, plus helpers for the effects that this
 * engine *does* support natively — gradient backgrounds and keyframe scale (Ken Burns / camera
 * zoom). Blur / drop-shadow / real masks are not rendered by the SVG backend, so "glow" and
 * "vignette" are faked with layered translucent shapes (design, not new engine features).
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
export const FIXED_NOW = "2026-08-01T00:00:00.000Z";

export const TITLE_FONT = "Black Han Sans";
export const BODY_FONT = "Noto Sans CJK KR";

const IDENTITY: Omit<Transform2D, "x" | "y" | "width" | "height"> = {
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

export function box(
  cx: number,
  cy: number,
  w: number,
  h: number,
  extra: Partial<Transform2D> = {},
): Transform2D {
  return { ...IDENTITY, x: cx, y: cy, width: w, height: h, ...extra };
}

export interface ElementInput {
  id: string;
  type: string;
  transform: Transform2D;
  props?: Record<string, unknown>;
  style?: Record<string, unknown>;
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

let seq = 0;
/** Entrance preset (fade-in|pop-in|scale-in|zoom-in|slide-{left,right,up,down}). */
export function enter(
  presetId: string,
  start: number,
  duration: number,
  params?: Record<string, unknown>,
): AnimationDefinition {
  seq += 1;
  return {
    id: `a${seq}`,
    kind: "preset",
    target: "self",
    start,
    duration,
    presetId,
    ...(params ? { params } : {}),
  };
}

/** Ken Burns / camera zoom: animate the element's scale over a window (the one keyframe channel the
 * engine renders besides opacity). `from`→`to` are scale multipliers. */
export function kenBurns(
  start: number,
  duration: number,
  from: number,
  to: number,
): AnimationDefinition {
  seq += 1;
  const easing = { type: "ease-out" as const };
  return {
    id: `kb${seq}`,
    kind: "keyframes",
    target: "scale",
    start,
    duration,
    keyframes: [
      { id: `kb${seq}-0`, time: 0, value: from, easing, interpolation: "linear" },
      { id: `kb${seq}-1`, time: duration, value: to, easing, interpolation: "linear" },
    ],
  };
}

export type Grad = { colors: string[]; angle?: number };
export function gradient(colors: string[], angle = 90): BackgroundDefinition {
  const stops = colors.map((color, i) => ({
    color,
    position: colors.length === 1 ? 0 : i / (colors.length - 1),
  }));
  return { type: "gradient", angle, stops };
}

export function scene(
  id: string,
  name: string,
  duration: number,
  elements: MotionElement[],
  background: BackgroundDefinition = { type: "solid", color: "#000000" },
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
    settings: { width: W, height: H, fps: FPS, backgroundColor: "#000000" },
    themeId: "minimal-dark",
  });
  p.scenes = scenes;
  p.metadata = { generator: "hero-toolkit", ...metadata };
  return p;
}

export interface TextOpts {
  size?: number;
  color?: string;
  cx?: number;
  cy?: number;
  width?: number;
  weight?: number;
  rotation?: number;
  start?: number;
  duration?: number;
  anim?: AnimationDefinition[];
  z?: number;
}

/** Heavy display title (Black Han Sans), optionally tilted (static rotation — animated rotation is
 * unsupported, so kinetic-type tilt is baked into the transform). */
export function bigText(
  id: string,
  text: string,
  cy: number,
  o: TextOpts = {},
): MotionElement {
  return el({
    id,
    type: "title",
    transform: box(
      o.cx ?? W / 2,
      cy,
      o.width ?? W - 80,
      o.size ?? 120,
      o.rotation ? { rotation: o.rotation } : {},
    ),
    props: {
      text,
      fontSize: o.size ?? 96,
      color: o.color ?? "#ffffff",
      align: "center",
      fontWeight: o.weight ?? 900,
      fontFamily: TITLE_FONT,
    },
    start: o.start,
    duration: o.duration,
    animations: o.anim,
    zIndex: o.z ?? 5,
  });
}

/** Body label (Noto Sans CJK KR), optional pill background. */
export function label(
  id: string,
  text: string,
  cy: number,
  o: TextOpts & { background?: string } = {},
): MotionElement {
  return el({
    id,
    type: "caption",
    transform: box(o.cx ?? W / 2, cy, o.width ?? W - 120, (o.size ?? 34) + 28),
    props: {
      text,
      fontSize: o.size ?? 32,
      color: o.color ?? "#c9d3e4",
      background: o.background ?? "",
      radius: 12,
    },
    start: o.start,
    duration: o.duration,
    animations: o.anim,
    zIndex: o.z ?? 6,
  });
}

export interface PanelOpts {
  fill?: string;
  border?: string;
  borderWidth?: number;
  radius?: number;
  opacity?: number;
  start?: number;
  duration?: number;
  anim?: AnimationDefinition[];
  z?: number;
}

/** Rounded rectangle panel/card (styled via element.style). */
export function panel(
  id: string,
  transform: Transform2D,
  o: PanelOpts = {},
): MotionElement {
  const t = o.opacity !== undefined ? { ...transform, opacity: o.opacity } : transform;
  return el({
    id,
    type: "rectangle",
    transform: t,
    style: {
      backgroundColor: o.fill ?? "#12151c",
      borderColor: o.border ?? "#2a2f3a",
      borderWidth: o.borderWidth ?? 0,
      borderRadius: o.radius ?? 20,
    },
    start: o.start,
    duration: o.duration,
    animations: o.anim,
    zIndex: o.z ?? 1,
  });
}

/** Filled circle (via circle component style). */
export function dot(
  id: string,
  cx: number,
  cy: number,
  r: number,
  fill: string,
  o: PanelOpts = {},
): MotionElement {
  return el({
    id,
    type: "circle",
    transform: box(cx, cy, r * 2, r * 2),
    style: {
      backgroundColor: fill,
      borderColor: o.border ?? "",
      borderWidth: o.borderWidth ?? 0,
    },
    start: o.start,
    duration: o.duration,
    animations: o.anim,
    zIndex: o.z ?? 2,
  });
}
