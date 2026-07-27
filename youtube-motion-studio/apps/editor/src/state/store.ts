/**
 * Editor store (Zustand). Holds the project plus transient editor state (selection, playback, UI)
 * — kept separate from the serialized project (spec §21). Element edits are immutable updates via
 * `projectOps`. In M3 edits are applied directly through store actions; M4 refactors mutations onto
 * the command/history architecture (spec §20) without changing this public surface much.
 */
import { create } from "zustand";
import {
  exportProject,
  importProject,
  type MotionElement,
  type MotionProject,
  type Transform2D,
} from "@motion-studio/core";
import { projectDuration } from "@motion-studio/renderer-core";
import { demoProject } from "../demoProject";
import { elementBox, findElement, findScene, updateElement } from "./projectOps";

export type LeftTab = "scenes" | "hierarchy";

export interface EditorState {
  // ── project ──
  project: MotionProject;
  dirty: boolean;
  loadError: string | null;
  loadFromJson(raw: string): boolean;
  replaceProject(project: MotionProject): void;
  toJson(): string;
  markSaved(): void;

  // ── selection ──
  selectedSceneId: string | null;
  selectedElementId: string | null;
  selectScene(sceneId: string | null): void;
  selectElement(elementId: string | null): void;

  // ── element editing ──
  updateSelectedTransform(patch: Partial<Transform2D>): void;
  updateSelectedProps(patch: Record<string, unknown>): void;
  updateSelectedStyle(patch: Record<string, unknown>): void;
  renameSelected(name: string): void;
  toggleElementVisible(elementId: string): void;

  // ── playback ──
  time: number;
  playing: boolean;
  setTime(time: number): void;
  play(): void;
  pause(): void;
  togglePlay(): void;

  // ── ui ──
  leftTab: LeftTab;
  setLeftTab(tab: LeftTab): void;
}

function firstSceneId(project: MotionProject): string | null {
  return project.scenes[0]?.id ?? null;
}

export const useEditor = create<EditorState>((set, get) => ({
  project: demoProject,
  dirty: false,
  loadError: null,

  loadFromJson(raw) {
    try {
      const { project } = importProject(raw);
      set({
        project,
        loadError: null,
        dirty: false,
        selectedSceneId: firstSceneId(project),
        selectedElementId: null,
        time: 0,
        playing: false,
      });
      return true;
    } catch (error) {
      set({ loadError: error instanceof Error ? error.message : String(error) });
      return false;
    }
  },

  replaceProject(project) {
    set({
      project,
      dirty: true,
      selectedSceneId: firstSceneId(project),
      selectedElementId: null,
    });
  },

  toJson() {
    return exportProject(get().project, { space: 2 });
  },

  markSaved() {
    set({ dirty: false });
  },

  selectedSceneId: firstSceneId(demoProject),
  selectedElementId: null,

  selectScene(sceneId) {
    set({ selectedSceneId: sceneId, selectedElementId: null });
  },

  selectElement(elementId) {
    if (!elementId) {
      set({ selectedElementId: null });
      return;
    }
    const found = findElement(get().project, elementId);
    set({
      selectedElementId: elementId,
      selectedSceneId: found ? found.scene.id : get().selectedSceneId,
    });
  },

  updateSelectedTransform(patch) {
    const id = get().selectedElementId;
    if (!id) return;
    set((state) => ({
      dirty: true,
      project: updateElement(state.project, id, (element) => ({
        ...element,
        transform: { ...element.transform, ...patch },
      })),
    }));
  },

  updateSelectedProps(patch) {
    const id = get().selectedElementId;
    if (!id) return;
    set((state) => ({
      dirty: true,
      project: updateElement(state.project, id, (element) => ({
        ...element,
        props: { ...element.props, ...patch },
      })),
    }));
  },

  updateSelectedStyle(patch) {
    const id = get().selectedElementId;
    if (!id) return;
    set((state) => ({
      dirty: true,
      project: updateElement(state.project, id, (element) => ({
        ...element,
        style: { ...element.style, ...patch },
      })),
    }));
  },

  renameSelected(name) {
    const id = get().selectedElementId;
    if (!id) return;
    set((state) => ({
      dirty: true,
      project: updateElement(state.project, id, (element) => ({ ...element, name })),
    }));
  },

  toggleElementVisible(elementId) {
    set((state) => ({
      dirty: true,
      project: updateElement(state.project, elementId, (element) => ({
        ...element,
        visible: !element.visible,
      })),
    }));
  },

  time: 0,
  playing: false,
  setTime(time) {
    set({ time: Math.max(0, time) });
  },
  play() {
    set({ playing: true });
  },
  pause() {
    set({ playing: false });
  },
  togglePlay() {
    set((state) => ({ playing: !state.playing }));
  },

  leftTab: "scenes",
  setLeftTab(tab) {
    set({ leftTab: tab });
  },
}));

// ── selectors (kept out of components to reduce rerenders) ──

export function selectSelectedElement(state: EditorState): MotionElement | null {
  return findElement(state.project, state.selectedElementId)?.element ?? null;
}

export function selectActiveScene(state: EditorState) {
  return (
    findScene(state.project, state.selectedSceneId) ?? state.project.scenes[0] ?? null
  );
}

export function selectDuration(state: EditorState): number {
  return projectDuration(state.project);
}

export { elementBox };
