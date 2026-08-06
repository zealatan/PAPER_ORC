/**
 * Pure, immutable helpers for locating and updating elements inside a project. The store uses
 * these so state updates never mutate the previous project object (spec §34.1 immutable updates).
 */
import type { MotionElement, MotionProject, Scene } from "@motion-studio/core";

export function findScene(project: MotionProject, sceneId: string | null): Scene | null {
  if (!sceneId) return null;
  return project.scenes.find((scene) => scene.id === sceneId) ?? null;
}

function findInElements(
  elements: MotionElement[],
  elementId: string,
): MotionElement | null {
  for (const element of elements) {
    if (element.id === elementId) return element;
    if (element.children) {
      const nested = findInElements(element.children, elementId);
      if (nested) return nested;
    }
  }
  return null;
}

/** Find an element anywhere in the project (top-level or nested), with its owning scene. */
export function findElement(
  project: MotionProject,
  elementId: string | null,
): { scene: Scene; element: MotionElement } | null {
  if (!elementId) return null;
  for (const scene of project.scenes) {
    const element = findInElements(scene.elements, elementId);
    if (element) return { scene, element };
  }
  return null;
}

function mapElements(
  elements: MotionElement[],
  elementId: string,
  update: (element: MotionElement) => MotionElement,
): MotionElement[] {
  return elements.map((element) => {
    if (element.id === elementId) return update(element);
    if (element.children) {
      return { ...element, children: mapElements(element.children, elementId, update) };
    }
    return element;
  });
}

/** Return a new project with a single element replaced by `update(element)`. */
export function updateElement(
  project: MotionProject,
  elementId: string,
  update: (element: MotionElement) => MotionElement,
): MotionProject {
  return {
    ...project,
    scenes: project.scenes.map((scene) => ({
      ...scene,
      elements: mapElements(scene.elements, elementId, update),
    })),
  };
}

export interface ScreenBox {
  left: number;
  top: number;
  width: number;
  height: number;
}

/** Axis-aligned bounding box of an element in project pixels (ignores rotation; M3 hit-testing). */
export function elementBox(element: MotionElement): ScreenBox {
  const { x, y, width, height, scaleX, scaleY, anchorX, anchorY } = element.transform;
  const w = width * scaleX;
  const h = height * scaleY;
  return { left: x - anchorX * w, top: y - anchorY * h, width: w, height: h };
}
