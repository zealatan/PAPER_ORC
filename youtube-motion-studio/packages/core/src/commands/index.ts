/**
 * Editor commands (spec §20). Every project mutation is expressed as an {@link EditorCommand} so
 * the history layer can record, coalesce, undo, and redo it. Commands are pure `execute` functions
 * (project → project); the inverse for undo is recovered from the pre-execution snapshot by the
 * history layer, which keeps commands simple and deterministic.
 */
import {
  addElementToScene,
  removeElementById,
  updateElementById,
} from "../project/elementOps";
import type {
  AnimationDefinition,
  ElementTiming,
  MotionElement,
  MotionProject,
  Scene,
  Transform2D,
} from "../project/types";

export interface EditorCommand {
  /** Human-readable label for history UI. */
  label: string;
  /**
   * Optional coalescing key: consecutive commands with the same key collapse into one history
   * entry (e.g. a continuous drag or rapid typing).
   */
  mergeKey?: string;
  execute(project: MotionProject): MotionProject;
}

export function updateElementTransform(
  elementId: string,
  patch: Partial<Transform2D>,
  mergeKey?: string,
): EditorCommand {
  return {
    label: "Update transform",
    mergeKey,
    execute: (project) =>
      updateElementById(project, elementId, (element) => ({
        ...element,
        transform: { ...element.transform, ...patch },
      })),
  };
}

export function updateElementTiming(
  elementId: string,
  patch: Partial<ElementTiming>,
  mergeKey?: string,
): EditorCommand {
  return {
    label: "Update timing",
    mergeKey,
    execute: (project) =>
      updateElementById(project, elementId, (element) => ({
        ...element,
        timing: { ...element.timing, ...patch },
      })),
  };
}

export function updateElementProps(
  elementId: string,
  patch: Record<string, unknown>,
  mergeKey?: string,
): EditorCommand {
  return {
    label: "Update properties",
    mergeKey,
    execute: (project) =>
      updateElementById(project, elementId, (element) => ({
        ...element,
        props: { ...element.props, ...patch },
      })),
  };
}

export function updateElementStyle(
  elementId: string,
  patch: Record<string, unknown>,
  mergeKey?: string,
): EditorCommand {
  return {
    label: "Update style",
    mergeKey,
    execute: (project) =>
      updateElementById(project, elementId, (element) => ({
        ...element,
        style: { ...element.style, ...patch },
      })),
  };
}

export function renameElement(elementId: string, name: string): EditorCommand {
  return {
    label: "Rename element",
    mergeKey: `rename:${elementId}`,
    execute: (project) =>
      updateElementById(project, elementId, (element) => ({ ...element, name })),
  };
}

export function setElementVisible(elementId: string, visible: boolean): EditorCommand {
  return {
    label: visible ? "Show element" : "Hide element",
    execute: (project) =>
      updateElementById(project, elementId, (element) => ({ ...element, visible })),
  };
}

export function addAnimation(
  elementId: string,
  animation: AnimationDefinition,
): EditorCommand {
  return {
    label: "Add animation",
    execute: (project) =>
      updateElementById(project, elementId, (element) => ({
        ...element,
        animations: [...element.animations, animation],
      })),
  };
}

export function updateAnimation(
  elementId: string,
  animationId: string,
  patch: Partial<AnimationDefinition>,
  mergeKey?: string,
): EditorCommand {
  return {
    label: "Update animation",
    mergeKey,
    execute: (project) =>
      updateElementById(project, elementId, (element) => ({
        ...element,
        animations: element.animations.map((animation) =>
          animation.id === animationId
            ? ({ ...animation, ...patch } as AnimationDefinition)
            : animation,
        ),
      })),
  };
}

export function removeAnimation(elementId: string, animationId: string): EditorCommand {
  return {
    label: "Remove animation",
    execute: (project) =>
      updateElementById(project, elementId, (element) => ({
        ...element,
        animations: element.animations.filter(
          (animation) => animation.id !== animationId,
        ),
      })),
  };
}

export function deleteElement(elementId: string): EditorCommand {
  return {
    label: "Delete element",
    execute: (project) => removeElementById(project, elementId),
  };
}

export function addElement(
  sceneId: string,
  element: MotionElement,
  index?: number,
): EditorCommand {
  return {
    label: "Add element",
    execute: (project) => addElementToScene(project, sceneId, element, index),
  };
}

export function setVariableValue(variableId: string, value: unknown): EditorCommand {
  return {
    label: "Set variable",
    mergeKey: `var:${variableId}`,
    execute: (project) => {
      const variable = project.variables[variableId];
      if (!variable) return project;
      return {
        ...project,
        variables: {
          ...project.variables,
          [variableId]: { ...variable, value },
        },
      };
    },
  };
}

export function setTheme(themeId: string): EditorCommand {
  return {
    label: "Change theme",
    execute: (project) =>
      project.theme.themeId === themeId
        ? project
        : { ...project, theme: { ...project.theme, themeId } },
  };
}

export function updateScene(
  sceneId: string,
  patch: Partial<Pick<Scene, "name" | "duration" | "background">>,
): EditorCommand {
  return {
    label: "Update scene",
    mergeKey: `scene:${sceneId}`,
    execute: (project) => ({
      ...project,
      scenes: project.scenes.map((scene) =>
        scene.id === sceneId ? { ...scene, ...patch } : scene,
      ),
    }),
  };
}
