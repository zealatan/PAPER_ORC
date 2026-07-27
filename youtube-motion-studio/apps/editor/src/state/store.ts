/**
 * Editor store (Zustand). Holds the project plus transient editor state (selection, playback,
 * history, UI) — separate from the serialized project (spec §21). Every project mutation goes
 * through the command/history layer in `@motion-studio/core` so undo/redo is exact and drags
 * coalesce (spec §20). Panel-facing action names are stable across M3→M4.
 */
import { create } from "zustand";
import {
  addAnimation as addAnimationCommand,
  addAudioTrack as addAudioTrackCommand,
  applyBindings,
  applyTheme,
  parseSrt,
  reviewAIResponse,
  removeAudioTrack as removeAudioTrackCommand,
  updateAudioTrack as updateAudioTrackCommand,
  canRedo as coreCanRedo,
  canUndo as coreCanUndo,
  createHistory,
  deleteElement as deleteElementCommand,
  exportProject,
  findElementById,
  importProject,
  instantiateTemplate,
  removeAnimation as removeAnimationCommand,
  resolveTheme,
  setTheme as setThemeCommand,
  setVariableValue as setVariableValueCommand,
  updateAnimation as updateAnimationCommand,
  redo as coreRedo,
  renameElement as renameElementCommand,
  runCommand as coreRunCommand,
  setElementVisible as setElementVisibleCommand,
  undo as coreUndo,
  updateElementById,
  updateElementProps as updateElementPropsCommand,
  updateElementStyle as updateElementStyleCommand,
  updateElementTiming as updateElementTimingCommand,
  updateElementTransform as updateElementTransformCommand,
  type AIGenerationResponse,
  type AnimationDefinition,
  type AudioTrack,
  type EditorCommand,
  type ElementTiming,
  type HistoryState,
  type MotionElement,
  type MotionProject,
  type MotionTemplate,
  type Transform2D,
} from "@motion-studio/core";
import { projectDuration } from "@motion-studio/renderer-core";
import { pgDeckAdapter } from "@motion-studio/legacy-adapter";
import { demoProject } from "../demoProject";
import { elementBox, findScene } from "./projectOps";

export type LeftTab = "scenes" | "hierarchy" | "variables" | "templates";

export interface TransformEntry {
  id: string;
  patch: Partial<Transform2D>;
}

export interface EditorState {
  // ── project ──
  project: MotionProject;
  history: HistoryState;
  dirty: boolean;
  loadError: string | null;
  loadFromJson(raw: string): boolean;
  replaceProject(project: MotionProject): void;
  toJson(): string;
  markSaved(): void;

  // ── commands / history ──
  apply(command: EditorCommand, coalesce?: boolean): void;
  undo(): void;
  redo(): void;

  // ── selection (multi) ──
  selectedSceneId: string | null;
  selectedElementIds: string[];
  selectedElementId: string | null; // primary (last selected)
  selectScene(sceneId: string | null): void;
  selectElement(elementId: string | null, additive?: boolean): void;
  clearSelection(): void;

  // ── element editing (via commands) ──
  updateSelectedTransform(patch: Partial<Transform2D>): void;
  updateSelectedProps(patch: Record<string, unknown>): void;
  updateSelectedStyle(patch: Record<string, unknown>): void;
  renameSelected(name: string): void;
  toggleElementVisible(elementId: string): void;
  setElementsTransform(entries: TransformEntry[], mergeKey: string): void;
  setElementTiming(
    elementId: string,
    patch: Partial<ElementTiming>,
    mergeKey: string,
  ): void;
  moveSelectedBy(dx: number, dy: number, mergeKey?: string): void;
  deleteSelected(): void;

  // ── animation editing ──
  addAnimationToSelected(presetId: string): void;
  updateSelectedAnimation(animationId: string, patch: Partial<AnimationDefinition>): void;
  removeSelectedAnimation(animationId: string): void;

  // ── variables / themes / templates ──
  setVariable(variableId: string, value: unknown): void;
  setThemeId(themeId: string): void;
  useTemplate(template: MotionTemplate): void;

  // ── ai / legacy import ──
  importAIDraft(response: AIGenerationResponse): boolean;
  importDeck(deckText: string): Promise<void>;

  // ── audio / subtitles ──
  importSrtToSelected(srtText: string): void;
  addAudio(track: AudioTrack): void;
  updateAudio(trackId: string, patch: Partial<AudioTrack>): void;
  removeAudio(trackId: string): void;

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

function pruneSelection(project: MotionProject, ids: string[]): string[] {
  return ids.filter((id) => findElementById(project, id) !== null);
}

/** A command that patches several elements' transforms at once (multi-select drag / nudge). */
function transformManyCommand(
  entries: TransformEntry[],
  mergeKey: string,
): EditorCommand {
  return {
    label: "Transform",
    mergeKey,
    execute: (project) =>
      entries.reduce(
        (acc, entry) =>
          updateElementById(acc, entry.id, (element) => ({
            ...element,
            transform: { ...element.transform, ...entry.patch },
          })),
        project,
      ),
  };
}

let animSeq = 0;
let projSeq = 0;

export const useEditor = create<EditorState>((set, get) => ({
  project: demoProject,
  history: createHistory(),
  dirty: false,
  loadError: null,

  loadFromJson(raw) {
    try {
      const { project } = importProject(raw);
      set({
        project,
        history: createHistory(),
        loadError: null,
        dirty: false,
        selectedSceneId: firstSceneId(project),
        selectedElementIds: [],
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
      history: createHistory(),
      dirty: true,
      selectedSceneId: firstSceneId(project),
      selectedElementIds: [],
      selectedElementId: null,
    });
  },

  toJson() {
    return exportProject(get().project, { space: 2 });
  },

  markSaved() {
    set({ dirty: false });
  },

  apply(command, coalesce = false) {
    const state = get();
    const result = coreRunCommand(state.project, state.history, command, { coalesce });
    if (result.changed) {
      set({ project: result.project, history: result.history, dirty: true });
    }
  },

  undo() {
    const state = get();
    const result = coreUndo(state.project, state.history);
    if (result) {
      set({
        project: result.project,
        history: result.history,
        dirty: true,
        selectedElementIds: pruneSelection(result.project, state.selectedElementIds),
        selectedElementId: findElementById(result.project, state.selectedElementId)
          ? state.selectedElementId
          : null,
      });
    }
  },

  redo() {
    const state = get();
    const result = coreRedo(state.project, state.history);
    if (result) {
      set({
        project: result.project,
        history: result.history,
        dirty: true,
        selectedElementIds: pruneSelection(result.project, state.selectedElementIds),
      });
    }
  },

  selectedSceneId: firstSceneId(demoProject),
  selectedElementIds: [],
  selectedElementId: null,

  selectScene(sceneId) {
    set({ selectedSceneId: sceneId, selectedElementIds: [], selectedElementId: null });
  },

  selectElement(elementId, additive = false) {
    if (!elementId) {
      set({ selectedElementIds: [], selectedElementId: null });
      return;
    }
    const found = findElementById(get().project, elementId);
    set((state) => {
      let ids: string[];
      if (additive) {
        ids = state.selectedElementIds.includes(elementId)
          ? state.selectedElementIds.filter((id) => id !== elementId)
          : [...state.selectedElementIds, elementId];
      } else {
        ids = [elementId];
      }
      return {
        selectedElementIds: ids,
        selectedElementId: ids[ids.length - 1] ?? null,
        selectedSceneId: found ? found.scene.id : state.selectedSceneId,
      };
    });
  },

  clearSelection() {
    set({ selectedElementIds: [], selectedElementId: null });
  },

  updateSelectedTransform(patch) {
    const id = get().selectedElementId;
    if (!id) return;
    const key = Object.keys(patch)[0] ?? "t";
    get().apply(updateElementTransformCommand(id, patch, `field:${id}:${key}`), true);
  },

  updateSelectedProps(patch) {
    const id = get().selectedElementId;
    if (!id) return;
    const key = Object.keys(patch)[0] ?? "p";
    get().apply(updateElementPropsCommand(id, patch, `prop:${id}:${key}`), true);
  },

  updateSelectedStyle(patch) {
    const id = get().selectedElementId;
    if (!id) return;
    const key = Object.keys(patch)[0] ?? "s";
    get().apply(updateElementStyleCommand(id, patch, `style:${id}:${key}`), true);
  },

  renameSelected(name) {
    const id = get().selectedElementId;
    if (!id) return;
    get().apply(renameElementCommand(id, name), true);
  },

  toggleElementVisible(elementId) {
    const found = findElementById(get().project, elementId);
    if (!found) return;
    get().apply(setElementVisibleCommand(elementId, !found.element.visible));
  },

  setElementsTransform(entries, mergeKey) {
    if (entries.length === 0) return;
    get().apply(transformManyCommand(entries, mergeKey), true);
  },

  setElementTiming(elementId, patch, mergeKey) {
    get().apply(updateElementTimingCommand(elementId, patch, mergeKey), true);
  },

  moveSelectedBy(dx, dy, mergeKey = "nudge") {
    const { project, selectedElementIds } = get();
    const entries: TransformEntry[] = [];
    for (const id of selectedElementIds) {
      const found = findElementById(project, id);
      if (found) {
        entries.push({
          id,
          patch: { x: found.element.transform.x + dx, y: found.element.transform.y + dy },
        });
      }
    }
    get().setElementsTransform(entries, mergeKey);
  },

  deleteSelected() {
    const ids = get().selectedElementIds;
    for (const id of ids) {
      get().apply(deleteElementCommand(id));
    }
    set({ selectedElementIds: [], selectedElementId: null });
  },

  addAnimationToSelected(presetId) {
    const id = get().selectedElementId;
    if (!id) return;
    animSeq += 1;
    const animation: AnimationDefinition = {
      id: `anim-${animSeq}`,
      kind: "preset",
      target: "transform",
      start: 0,
      duration: 0.5,
      presetId,
    };
    get().apply(addAnimationCommand(id, animation));
  },

  updateSelectedAnimation(animationId, patch) {
    const id = get().selectedElementId;
    if (!id) return;
    get().apply(
      updateAnimationCommand(id, animationId, patch, `anim:${id}:${animationId}`),
      true,
    );
  },

  removeSelectedAnimation(animationId) {
    const id = get().selectedElementId;
    if (!id) return;
    get().apply(removeAnimationCommand(id, animationId));
  },

  setVariable(variableId, value) {
    get().apply(setVariableValueCommand(variableId, value), true);
  },

  setThemeId(themeId) {
    get().apply(setThemeCommand(themeId));
  },

  useTemplate(template) {
    projSeq += 1;
    const now = new Date().toISOString();
    get().replaceProject(instantiateTemplate(template, `project-${projSeq}`, now));
  },

  async importDeck(deckText) {
    try {
      const { project } = await pgDeckAdapter.import(deckText);
      get().replaceProject(project);
      set({ loadError: null });
    } catch (error) {
      set({ loadError: error instanceof Error ? error.message : String(error) });
    }
  },

  importAIDraft(response) {
    const review = reviewAIResponse(response);
    if (review.ok && review.project) {
      get().replaceProject(review.project);
      set({ loadError: null });
      return true;
    }
    set({
      loadError:
        review.issues.map((i) => `${i.path || "<root>"}: ${i.message}`).join("; ") ||
        "AI draft was invalid.",
    });
    return false;
  },

  importSrtToSelected(srtText) {
    const cues = parseSrt(srtText);
    get().updateSelectedProps({ cues });
  },

  addAudio(track) {
    get().apply(addAudioTrackCommand(track));
  },

  updateAudio(trackId, patch) {
    get().apply(updateAudioTrackCommand(trackId, patch, `audio:${trackId}`), true);
  },

  removeAudio(trackId) {
    get().apply(removeAudioTrackCommand(trackId));
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

// ── selectors ──

export function selectSelectedElement(state: EditorState): MotionElement | null {
  return findElementById(state.project, state.selectedElementId)?.element ?? null;
}

export function selectActiveScene(state: EditorState) {
  return (
    findScene(state.project, state.selectedSceneId) ?? state.project.scenes[0] ?? null
  );
}

export function selectDuration(state: EditorState): number {
  return projectDuration(state.project);
}

export function selectCanUndo(state: EditorState): boolean {
  return coreCanUndo(state.history);
}

export function selectCanRedo(state: EditorState): boolean {
  return coreCanRedo(state.history);
}

/** The project with variable bindings + theme tokens resolved, ready to render (spec §9, §10). */
export function selectResolvedProject(state: EditorState): MotionProject {
  return applyTheme(
    applyBindings(state.project),
    resolveTheme(state.project.theme.themeId),
  );
}

export { elementBox };
