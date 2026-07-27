/**
 * Renderer contracts (spec §4.2, §8.4, §23). Element renderers turn a single {@link MotionElement}
 * into backend-agnostic {@link DrawNode} primitives; backends paint those primitives. The
 * deterministic {@link FrameRenderer} contract guarantees a frame at time `t` depends only on the
 * project and `t`.
 */
import type { AssetReference, MotionElement, MotionProject } from "@motion-studio/core";
import type { DrawNode } from "./scene-graph";

/** Context handed to element renderers. Provides asset resolution and project settings. */
export interface RenderContext {
  project: MotionProject;
  /** Resolve an asset id to a usable URL (data/object/remote), or null when unresolved. */
  resolveAssetUrl(assetId: string): string | null;
  /** Look up an asset reference by id. */
  getAsset(assetId: string): AssetReference | undefined;
}

/** Renders one element's own visual (children are handled by the frame renderer). */
export interface ElementRenderer {
  type: string;
  render(element: MotionElement, ctx: RenderContext): DrawNode | null;
}

/** Registry mapping element `type` → renderer (spec §8.2). */
export interface RenderRegistry {
  register(renderer: ElementRenderer): void;
  unregister(type: string): void;
  get(type: string): ElementRenderer | undefined;
  has(type: string): boolean;
  list(): ElementRenderer[];
}

export type FrameMediaType = "image/svg+xml" | "image/png" | "canvas";

/** A rendered frame produced by a {@link FrameRenderer}. */
export interface RenderedFrame {
  width: number;
  height: number;
  mediaType: FrameMediaType;
  /** SVG/markup string, data URL, or opaque handle depending on the backend. */
  payload: string;
}

/**
 * Deterministic frame renderer (spec §23). `renderFrame(t)` must not depend on whether any other
 * time was rendered first.
 */
export interface FrameRenderer {
  initialize(project: MotionProject): Promise<void>;
  renderFrame(timeSeconds: number): Promise<RenderedFrame>;
  dispose(): Promise<void>;
}
