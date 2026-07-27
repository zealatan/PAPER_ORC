/**
 * Deterministic timeline evaluation (spec §14, §23). `evaluateProjectAtTime(project, globalTime)`
 * returns the full visual state at any timestamp without depending on real-time playback or any
 * previously rendered frame.
 *
 * Time model (spec §14.2):
 *  - global project time → active scene + scene-local time (accumulated scene durations),
 *  - scene-local time → element visibility window and element-local animation time.
 * Element timing is relative to scene start (spec §6.6), including nested children.
 */
import type {
  BackgroundDefinition,
  MotionElement,
  MotionProject,
  Scene,
  Transform2D,
} from "@motion-studio/core";
import { resolveElementTransform } from "./animation";

export interface ResolvedElement {
  element: MotionElement;
  transform: Transform2D;
  opacity: number;
  visible: boolean;
  children: ResolvedElement[];
}

export interface EvaluatedFrame {
  globalTime: number;
  sceneIndex: number;
  scene: Scene | null;
  sceneLocalTime: number;
  background: BackgroundDefinition | null;
  /** Top-level resolved elements, ordered by paint order (zIndex ascending, then declaration). */
  elements: ResolvedElement[];
}

/** Start time (seconds) of each scene, from accumulated durations. */
export function sceneStartTimes(project: MotionProject): number[] {
  const starts: number[] = [];
  let acc = 0;
  for (const scene of project.scenes) {
    starts.push(acc);
    acc += scene.duration;
  }
  return starts;
}

/** Total project duration in seconds. */
export function projectDuration(project: MotionProject): number {
  if (
    project.settings.durationMode === "fixed" &&
    project.settings.fixedDuration != null
  ) {
    return project.settings.fixedDuration;
  }
  return project.scenes.reduce((sum, scene) => sum + scene.duration, 0);
}

/** Locate the active scene index for a global time. */
export function sceneIndexAtTime(project: MotionProject, globalTime: number): number {
  const starts = sceneStartTimes(project);
  if (starts.length === 0) return -1;
  if (globalTime < 0) return 0;
  for (let i = starts.length - 1; i >= 0; i -= 1) {
    if (globalTime >= starts[i]!) return i;
  }
  return 0;
}

function isWithinTiming(element: MotionElement, sceneLocalTime: number): boolean {
  const { start, duration } = element.timing;
  return sceneLocalTime >= start && sceneLocalTime <= start + duration;
}

function paintOrder(elements: MotionElement[]): MotionElement[] {
  return elements
    .map((element, index) => ({ element, index }))
    .sort((a, b) => {
      const dz = a.element.transform.zIndex - b.element.transform.zIndex;
      return dz !== 0 ? dz : a.index - b.index;
    })
    .map((entry) => entry.element);
}

function resolveElement(element: MotionElement, sceneLocalTime: number): ResolvedElement {
  const localTime = sceneLocalTime - element.timing.start;
  const { transform, opacity } = resolveElementTransform(element, localTime);
  const visible = element.visible && isWithinTiming(element, sceneLocalTime);
  const children = element.children
    ? paintOrder(element.children).map((child) => resolveElement(child, sceneLocalTime))
    : [];
  return { element, transform, opacity, visible, children };
}

/** Evaluate the entire project at a global timestamp. */
export function evaluateProjectAtTime(
  project: MotionProject,
  globalTime: number,
): EvaluatedFrame {
  const sceneIndex = sceneIndexAtTime(project, globalTime);
  if (sceneIndex < 0) {
    return {
      globalTime,
      sceneIndex,
      scene: null,
      sceneLocalTime: 0,
      background: null,
      elements: [],
    };
  }

  const starts = sceneStartTimes(project);
  const scene = project.scenes[sceneIndex]!;
  const sceneLocalTime = globalTime - starts[sceneIndex]!;
  const elements = paintOrder(scene.elements).map((element) =>
    resolveElement(element, sceneLocalTime),
  );

  return {
    globalTime,
    sceneIndex,
    scene,
    sceneLocalTime,
    background: scene.background,
    elements,
  };
}
