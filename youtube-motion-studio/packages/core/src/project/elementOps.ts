/**
 * Immutable element operations on a project (spec §34.1). Pure: they never mutate their input and
 * only rebuild the branches that change. Shared by the command layer and the editor.
 */
import type { MotionElement, MotionProject, Scene } from "./types";

function searchElements(
  elements: MotionElement[],
  elementId: string,
): MotionElement | null {
  for (const element of elements) {
    if (element.id === elementId) return element;
    if (element.children) {
      const nested = searchElements(element.children, elementId);
      if (nested) return nested;
    }
  }
  return null;
}

/** Find an element anywhere in the project with its owning scene. */
export function findElementById(
  project: MotionProject,
  elementId: string | null,
): { scene: Scene; element: MotionElement } | null {
  if (!elementId) return null;
  for (const scene of project.scenes) {
    const element = searchElements(scene.elements, elementId);
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

/** Return a new project with one element replaced by `update(element)`. */
export function updateElementById(
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

function filterElements(elements: MotionElement[], elementId: string): MotionElement[] {
  const result: MotionElement[] = [];
  for (const element of elements) {
    if (element.id === elementId) continue;
    result.push(
      element.children
        ? { ...element, children: filterElements(element.children, elementId) }
        : element,
    );
  }
  return result;
}

/** Return a new project with an element (and its subtree) removed. */
export function removeElementById(
  project: MotionProject,
  elementId: string,
): MotionProject {
  return {
    ...project,
    scenes: project.scenes.map((scene) => ({
      ...scene,
      elements: filterElements(scene.elements, elementId),
    })),
  };
}

/** Return a new project with `element` appended to a scene's top-level elements. */
export function addElementToScene(
  project: MotionProject,
  sceneId: string,
  element: MotionElement,
  index?: number,
): MotionProject {
  return {
    ...project,
    scenes: project.scenes.map((scene) => {
      if (scene.id !== sceneId) return scene;
      const elements = [...scene.elements];
      elements.splice(index ?? elements.length, 0, element);
      return { ...scene, elements };
    }),
  };
}
