/**
 * Global keyboard shortcuts for the editor (spec §13): undo/redo, delete selection, and arrow-key
 * nudging. The listener reads fresh actions/state via `useEditor.getState()` so the hook never
 * subscribes to store values and never re-renders. Events that originate from editable fields
 * (inputs, textareas, selects, contenteditable) are ignored so typing is never hijacked.
 */
import { useEffect } from "react";
import { useEditor } from "../state/store";

function isEditableTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false;
  const tag = target.tagName;
  return (
    tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || target.isContentEditable
  );
}

export function useKeyboardShortcuts(): void {
  useEffect(() => {
    function onKeyDown(event: KeyboardEvent): void {
      if (isEditableTarget(event.target)) return;

      const mod = event.ctrlKey || event.metaKey;

      if (mod && (event.key === "z" || event.key === "Z")) {
        event.preventDefault();
        if (event.shiftKey) {
          useEditor.getState().redo();
        } else {
          useEditor.getState().undo();
        }
        return;
      }

      if (mod && (event.key === "y" || event.key === "Y")) {
        event.preventDefault();
        useEditor.getState().redo();
        return;
      }

      if (event.key === "Delete" || event.key === "Backspace") {
        if (useEditor.getState().selectedElementIds.length > 0) {
          event.preventDefault();
          useEditor.getState().deleteSelected();
        }
        return;
      }

      if (
        event.key === "ArrowLeft" ||
        event.key === "ArrowRight" ||
        event.key === "ArrowUp" ||
        event.key === "ArrowDown"
      ) {
        if (useEditor.getState().selectedElementIds.length === 0) return;
        event.preventDefault();
        const step = event.shiftKey ? 10 : 1;
        let dx = 0;
        let dy = 0;
        if (event.key === "ArrowLeft") dx = -step;
        else if (event.key === "ArrowRight") dx = step;
        else if (event.key === "ArrowUp") dy = -step;
        else dy = step;
        useEditor.getState().moveSelectedBy(dx, dy, "nudge");
      }
    }

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);
}
