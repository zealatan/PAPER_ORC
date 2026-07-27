import {
  DEFAULT_TRANSFORM,
  createEmptyProject,
  type AssetReference,
  type MotionElement,
  type MotionProject,
  type Scene,
  type Transform2D,
} from "@motion-studio/core";
import { createRenderContext, type RenderContext } from "@motion-studio/renderer-core";

export function makeTransform(overrides: Partial<Transform2D> = {}): Transform2D {
  return { ...DEFAULT_TRANSFORM, anchorX: 0, anchorY: 0, ...overrides };
}

export interface MakeElementOpts {
  transform?: Partial<Transform2D>;
  style?: Record<string, unknown>;
  props?: Record<string, unknown>;
  timing?: MotionElement["timing"];
  animations?: MotionElement["animations"];
  children?: MotionElement[];
}

export function makeElement(
  id: string,
  type: string,
  opts: MakeElementOpts = {},
): MotionElement {
  return {
    id,
    type,
    name: id,
    visible: true,
    locked: false,
    transform: makeTransform(opts.transform),
    style: opts.style ?? {},
    props: opts.props ?? {},
    timing: opts.timing ?? { start: 0, duration: 10 },
    animations: opts.animations ?? [],
    ...(opts.children ? { children: opts.children } : {}),
  };
}

export function makeScene(id: string, elements: MotionElement[], duration = 5): Scene {
  return {
    id,
    name: id,
    duration,
    background: { type: "solid", color: "#101010" },
    elements,
  };
}

export function makeProject(
  scenes: Scene[],
  assets: AssetReference[] = [],
): MotionProject {
  const project = createEmptyProject({
    id: "test",
    name: "Test",
    now: "2026-01-01T00:00:00.000Z",
  });
  return { ...project, scenes, assets };
}

export function makeContext(project?: MotionProject): RenderContext {
  return createRenderContext(project ?? makeProject([]));
}
