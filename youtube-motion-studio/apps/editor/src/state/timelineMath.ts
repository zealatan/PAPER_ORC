/**
 * Pure timeline math (spec §14): global/scene/element time conversions, clip layout, ruler ticks,
 * and edge snapping. No React, no store — trivially testable and deterministic.
 */
import type { MotionProject } from "@motion-studio/core";

export interface SceneSpan {
  sceneId: string;
  name: string;
  start: number;
  duration: number;
}

export interface ClipLayout {
  elementId: string;
  sceneId: string;
  name: string;
  type: string;
  /** Global start time (scene start + element timing.start), in seconds. */
  globalStart: number;
  duration: number;
}

/** Global start time + duration of each scene, from accumulated durations. */
export function sceneSpans(project: MotionProject): SceneSpan[] {
  const spans: SceneSpan[] = [];
  let acc = 0;
  for (const scene of project.scenes) {
    spans.push({
      sceneId: scene.id,
      name: scene.name,
      start: acc,
      duration: scene.duration,
    });
    acc += scene.duration;
  }
  return spans;
}

export function projectDuration(project: MotionProject): number {
  if (
    project.settings.durationMode === "fixed" &&
    project.settings.fixedDuration != null
  ) {
    return project.settings.fixedDuration;
  }
  return project.scenes.reduce((sum, scene) => sum + scene.duration, 0);
}

/** One clip per top-level element, positioned on the global timeline. */
export function buildClips(project: MotionProject): ClipLayout[] {
  const clips: ClipLayout[] = [];
  for (const span of sceneSpans(project)) {
    const scene = project.scenes.find((s) => s.id === span.sceneId);
    if (!scene) continue;
    for (const element of scene.elements) {
      clips.push({
        elementId: element.id,
        sceneId: scene.id,
        name: element.name,
        type: element.type,
        globalStart: span.start + element.timing.start,
        duration: element.timing.duration,
      });
    }
  }
  return clips;
}

export const timeToX = (time: number, duration: number, width: number): number =>
  duration > 0 ? (time / duration) * width : 0;

export const xToTime = (x: number, duration: number, width: number): number =>
  width > 0 ? (x / width) * duration : 0;

export interface RulerTick {
  time: number;
  label: string;
}

/** Ruler ticks at a "nice" step (1/2/5/10…) targeting roughly `maxTicks` divisions. */
export function rulerTicks(duration: number, maxTicks = 10): RulerTick[] {
  if (duration <= 0) return [{ time: 0, label: "0s" }];
  const rough = duration / maxTicks;
  const pow = Math.pow(10, Math.floor(Math.log10(rough)));
  const candidates = [1, 2, 5, 10].map((m) => m * pow);
  const step = candidates.find((c) => c >= rough) ?? candidates[candidates.length - 1]!;
  const ticks: RulerTick[] = [];
  for (let t = 0; t <= duration + 1e-9; t += step) {
    const rounded = Math.round(t * 1000) / 1000;
    ticks.push({ time: rounded, label: `${rounded}s` });
  }
  return ticks;
}

/** Snap a time value to the nearest target within `tolerance` seconds; else return it unchanged. */
export function snapTime(value: number, targets: number[], tolerance: number): number {
  let best = value;
  let bestDelta = tolerance;
  for (const target of targets) {
    const delta = Math.abs(target - value);
    if (delta <= bestDelta) {
      best = target;
      bestDelta = delta;
    }
  }
  return best;
}
