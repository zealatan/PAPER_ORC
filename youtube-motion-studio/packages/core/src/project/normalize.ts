/**
 * Normalization fills deterministic defaults after validation (spec §7 pipeline step
 * "normalize defaults"). It is:
 *
 *  - pure: it never mutates its input,
 *  - idempotent: `normalize(normalize(x))` deep-equals `normalize(x)`,
 *  - lossless: it only *adds* safe defaults, never drops data.
 */
import type { MotionElement, MotionProject } from "./types";

function normalizeElement(element: MotionElement): MotionElement {
  const normalized: MotionElement = {
    ...element,
    // Optional collections become concrete empty arrays so downstream code (inspector,
    // renderer, bindings) can iterate without null checks.
    bindings: element.bindings ?? [],
    effects: element.effects ?? [],
  };
  if (element.children) {
    normalized.children = element.children.map(normalizeElement);
  }
  return normalized;
}

/** Return a fresh, fully-defaulted copy of the project. */
export function normalizeProject(project: MotionProject): MotionProject {
  return {
    ...project,
    variables: { ...project.variables },
    assets: project.assets.map((asset) => ({ ...asset })),
    audioTracks: project.audioTracks.map((track) => ({ ...track })),
    scenes: project.scenes.map((scene) => ({
      ...scene,
      elements: scene.elements.map(normalizeElement),
    })),
  };
}
