/**
 * Domain model for a MotionProject.
 *
 * These interfaces are the documented, hand-written contract (spec §6). The Zod schemas in
 * `./schema.ts` mirror them for runtime validation, and the recursive element schema is
 * annotated against {@link MotionElement} so the two cannot silently diverge in shape.
 *
 * Everything here is plain, serializable data: no functions, no DOM references (spec §21).
 */

/** Semantic version string, e.g. "1.0.0". */
export type SemVer = string;

export interface ProjectSettings {
  width: number;
  height: number;
  fps: number;
  durationMode: "scenes" | "fixed";
  fixedDuration?: number;
  backgroundColor: string;
  pixelRatio: number;
  safeArea?: SafeAreaSettings;
}

export interface SafeAreaSettings {
  top?: number;
  right?: number;
  bottom?: number;
  left?: number;
}

export interface ThemeReference {
  themeId: string;
  overrides?: Record<string, unknown>;
}

export type VariableType =
  | "string"
  | "number"
  | "boolean"
  | "color"
  | "date"
  | "imageAsset"
  | "videoAsset"
  | "audioAsset"
  | "json";

export interface VariableDefinition {
  id: string;
  name: string;
  type: VariableType;
  value: unknown;
  defaultValue?: unknown;
  description?: string;
  required?: boolean;
  group?: string;
}

export type AssetType = "image" | "video" | "audio" | "svg" | "font" | "json" | "unknown";

export type AssetSource =
  | { kind: "local-path"; path: string }
  | { kind: "object-url"; key: string }
  | { kind: "data-url"; value: string }
  | { kind: "remote-url"; url: string }
  | { kind: "generated"; generatorId: string; params?: unknown };

export interface AssetReference {
  id: string;
  type: AssetType;
  name: string;
  source: AssetSource;
  mimeType?: string;
  width?: number;
  height?: number;
  duration?: number;
  checksum?: string;
  metadata?: Record<string, unknown>;
}

export type AudioTrackKind = "voiceover" | "music" | "sfx" | "video-audio";

export interface AudioTrack {
  id: string;
  kind: AudioTrackKind;
  assetId: string;
  start: number;
  duration: number;
  trimStart?: number;
  trimEnd?: number;
  volume?: number;
  muted?: boolean;
  fadeIn?: number;
  fadeOut?: number;
  playbackRate?: number;
  duckingGroup?: string;
}

export type BackgroundDefinition =
  | { type: "none" }
  | { type: "solid"; color: string }
  | {
      type: "gradient";
      angle?: number;
      stops: Array<{ color: string; position: number }>;
    }
  | { type: "image"; assetId: string; fit?: BackgroundFit }
  | { type: "video"; assetId: string; fit?: BackgroundFit; loop?: boolean };

export type BackgroundFit = "cover" | "contain" | "fill" | "none";

export type TransitionType =
  | "cut"
  | "fade"
  | "slide"
  | "push"
  | "zoom"
  | "wipe"
  | "blur-fade"
  | "dip-to-black"
  | "dip-to-white";

export interface TransitionDefinition {
  type: TransitionType;
  duration: number;
  params?: Record<string, unknown>;
}

export interface Transform2D {
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  scaleX: number;
  scaleY: number;
  /** Normalized 0..1. */
  anchorX: number;
  /** Normalized 0..1. */
  anchorY: number;
  skewX: number;
  skewY: number;
  /** 0..1. */
  opacity: number;
  zIndex: number;
}

export interface ElementTiming {
  start: number;
  duration: number;
  trimStart?: number;
  trimEnd?: number;
  playbackRate?: number;
}

export interface VariableBinding {
  variableId: string;
  targetPath: string;
  transform?: BindingTransform;
}

export interface BindingTransform {
  type: string;
  [key: string]: unknown;
}

export interface EffectDefinition {
  id: string;
  type: string;
  params?: Record<string, unknown>;
  enabled?: boolean;
}

export type EasingType =
  | "linear"
  | "ease"
  | "ease-in"
  | "ease-out"
  | "ease-in-out"
  | "cubic-bezier"
  | "bounce"
  | "elastic"
  | "back"
  | "spring";

export interface SpringSettings {
  mass?: number;
  stiffness?: number;
  damping?: number;
  initialVelocity?: number;
}

export interface EasingDefinition {
  type: EasingType;
  /** Four control points when type is "cubic-bezier". */
  bezier?: [number, number, number, number];
  spring?: SpringSettings;
}

export type KeyframeInterpolation = "linear" | "step" | "bezier" | "spring";

export interface Keyframe<T = unknown> {
  id: string;
  time: number;
  value: T;
  easing: EasingDefinition;
  interpolation: KeyframeInterpolation;
}

export interface AnimationLoop {
  enabled: boolean;
  count?: number;
  direction?: "normal" | "alternate";
}

interface AnimationBase {
  id: string;
  target: string;
  start: number;
  duration: number;
  delay?: number;
  loop?: AnimationLoop;
}

export interface PresetAnimation extends AnimationBase {
  kind: "preset";
  presetId: string;
  params?: Record<string, unknown>;
}

export interface KeyframeAnimation extends AnimationBase {
  kind: "keyframes";
  keyframes: Keyframe[];
}

export type AnimationDefinition = PresetAnimation | KeyframeAnimation;

/**
 * A visual element in a scene. `type` is an open string resolved through the component
 * registry (spec §8); concrete per-component prop schemas are validated by that registry
 * in later milestones. `children` makes the element tree recursive.
 */
export interface MotionElement {
  id: string;
  type: string;
  name: string;
  visible: boolean;
  locked: boolean;
  transform: Transform2D;
  style: Record<string, unknown>;
  props: Record<string, unknown>;
  timing: ElementTiming;
  animations: AnimationDefinition[];
  bindings?: VariableBinding[];
  effects?: EffectDefinition[];
  children?: MotionElement[];
  metadata?: Record<string, unknown>;
}

export interface Scene {
  id: string;
  name: string;
  duration: number;
  background: BackgroundDefinition;
  elements: MotionElement[];
  transitionIn?: TransitionDefinition;
  transitionOut?: TransitionDefinition;
  metadata?: Record<string, unknown>;
}

export interface MotionProject {
  schemaVersion: SemVer;
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
  settings: ProjectSettings;
  theme: ThemeReference;
  variables: Record<string, VariableDefinition>;
  assets: AssetReference[];
  scenes: Scene[];
  audioTracks: AudioTrack[];
  metadata?: Record<string, unknown>;
}
