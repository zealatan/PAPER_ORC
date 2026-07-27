/**
 * Top toolbar (spec §11): project identity, save state, transport controls, and JSON load/save.
 * A thin view over the store — playback and project I/O are store actions (spec §34.3).
 */
import { useRef } from "react";
import { THEMES } from "@motion-studio/core";
import { selectCanRedo, selectCanUndo, selectDuration, useEditor } from "../state/store";

export function TopToolbar() {
  const name = useEditor((s) => s.project.name);
  const dirty = useEditor((s) => s.dirty);
  const playing = useEditor((s) => s.playing);
  const time = useEditor((s) => s.time);
  const duration = useEditor(selectDuration);

  const togglePlay = useEditor((s) => s.togglePlay);
  const setTime = useEditor((s) => s.setTime);
  const pause = useEditor((s) => s.pause);
  const loadFromJson = useEditor((s) => s.loadFromJson);
  const toJson = useEditor((s) => s.toJson);
  const markSaved = useEditor((s) => s.markSaved);
  const undo = useEditor((s) => s.undo);
  const redo = useEditor((s) => s.redo);
  const canUndo = useEditor(selectCanUndo);
  const canRedo = useEditor(selectCanRedo);
  const themeId = useEditor((s) => s.project.theme.themeId);
  const setThemeId = useEditor((s) => s.setThemeId);

  const inputRef = useRef<HTMLInputElement>(null);

  function handleStop() {
    setTime(0);
    pause();
  }

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    loadFromJson(text);
    event.target.value = "";
  }

  function handleSave() {
    const json = toJson();
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${name}.motion.json`;
    anchor.click();
    URL.revokeObjectURL(url);
    markSaved();
  }

  return (
    <div className="toolbar">
      <span className="toolbar__title">{name}</span>
      <span className={dirty ? "status-dot status-dot--dirty" : "status-dot"}>
        {dirty ? "● Unsaved" : "● Saved"}
      </span>
      <button type="button" className="tbtn" onClick={undo} disabled={!canUndo}>
        ↶ Undo
      </button>
      <button type="button" className="tbtn" onClick={redo} disabled={!canRedo}>
        ↷ Redo
      </button>
      <span className="toolbar__spacer" />
      <select
        className="toolbar__theme"
        value={themeId}
        onChange={(e) => setThemeId(e.target.value)}
        title="Theme"
      >
        {THEMES.map((theme) => (
          <option key={theme.id} value={theme.id}>
            {theme.name}
          </option>
        ))}
      </select>
      <button type="button" className="tbtn" onClick={togglePlay}>
        {playing ? "⏸ Pause" : "▶ Play"}
      </button>
      <button type="button" className="tbtn" onClick={handleStop}>
        ⏹ Stop
      </button>
      <span className="status-dot">
        {time.toFixed(2)} / {duration.toFixed(2)}s
      </span>
      <button type="button" className="tbtn" onClick={() => inputRef.current?.click()}>
        Load
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="application/json,.json,.motion.json"
        style={{ display: "none" }}
        onChange={handleFileChange}
      />
      <button type="button" className="tbtn tbtn--primary" onClick={handleSave}>
        Save
      </button>
    </div>
  );
}
