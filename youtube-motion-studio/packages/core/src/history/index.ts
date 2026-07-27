/**
 * Undo/redo history (spec §20). Snapshot-based: each entry keeps the project before and after a
 * command so undo/redo are exact. Consecutive commands sharing a `mergeKey` coalesce into one entry
 * (continuous drag, rapid typing). History is transient editor state — never part of saved project
 * JSON (spec §21).
 */
import type { EditorCommand } from "../commands";
import type { MotionProject } from "../project/types";

export interface HistoryEntry {
  label: string;
  mergeKey?: string;
  before: MotionProject;
  after: MotionProject;
}

export interface HistoryState {
  past: HistoryEntry[];
  future: HistoryEntry[];
  limit: number;
}

export function createHistory(limit = 100): HistoryState {
  return { past: [], future: [], limit };
}

export interface RunResult {
  project: MotionProject;
  history: HistoryState;
  changed: boolean;
}

/**
 * Execute a command against the project and record it. Returns the new project + history. If the
 * command is a no-op (project unchanged) nothing is recorded.
 */
export function runCommand(
  project: MotionProject,
  history: HistoryState,
  command: EditorCommand,
  options: { coalesce?: boolean } = {},
): RunResult {
  const after = command.execute(project);
  if (after === project) {
    return { project, history, changed: false };
  }

  const last = history.past[history.past.length - 1];
  const canCoalesce =
    options.coalesce === true &&
    command.mergeKey != null &&
    last != null &&
    last.mergeKey === command.mergeKey &&
    history.future.length === 0;

  let past: HistoryEntry[];
  if (canCoalesce && last) {
    // Keep the original `before`; extend the `after` to the latest state.
    const merged: HistoryEntry = { ...last, after };
    past = [...history.past.slice(0, -1), merged];
  } else {
    const entry: HistoryEntry = {
      label: command.label,
      mergeKey: command.mergeKey,
      before: project,
      after,
    };
    past = [...history.past, entry];
    if (past.length > history.limit) past = past.slice(past.length - history.limit);
  }

  return {
    project: after,
    history: { ...history, past, future: [] },
    changed: true,
  };
}

export interface StepResult {
  project: MotionProject;
  history: HistoryState;
}

/** Undo the most recent entry, returning the restored project. Null when nothing to undo. */
export function undo(_project: MotionProject, history: HistoryState): StepResult | null {
  const entry = history.past[history.past.length - 1];
  if (!entry) return null;
  return {
    project: entry.before,
    history: {
      ...history,
      past: history.past.slice(0, -1),
      future: [...history.future, entry],
    },
  };
}

/** Redo the most recently undone entry. Null when nothing to redo. */
export function redo(_project: MotionProject, history: HistoryState): StepResult | null {
  const entry = history.future[history.future.length - 1];
  if (!entry) return null;
  return {
    project: entry.after,
    history: {
      ...history,
      future: history.future.slice(0, -1),
      past: [...history.past, entry],
    },
  };
}

export const canUndo = (history: HistoryState): boolean => history.past.length > 0;
export const canRedo = (history: HistoryState): boolean => history.future.length > 0;
