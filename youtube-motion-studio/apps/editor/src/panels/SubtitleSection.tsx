/**
 * Subtitle inspector section (spec §16.3). Shown for "subtitle" elements: reports the cue count and
 * imports an .srt file into the element's cue data (parsed by core, undoable via the props command).
 */
import { useRef } from "react";
import { selectSelectedElement, useEditor } from "../state/store";

export function SubtitleSection() {
  const element = useEditor(selectSelectedElement);
  const importSrt = useEditor((s) => s.importSrtToSelected);
  const inputRef = useRef<HTMLInputElement>(null);

  if (!element || element.type !== "subtitle") return null;

  const cues = Array.isArray(element.props.cues) ? element.props.cues : [];

  async function handleFile(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    importSrt(text);
    event.target.value = "";
  }

  return (
    <details className="insp-section" open>
      <summary>Subtitles</summary>
      <div className="field">
        <label>Cues</label>
        <input value={`${cues.length} cues`} disabled />
      </div>
      <div className="anim-row__actions">
        <button type="button" className="tbtn" onClick={() => inputRef.current?.click()}>
          Import SRT
        </button>
        <input
          ref={inputRef}
          type="file"
          accept=".srt,text/plain"
          style={{ display: "none" }}
          onChange={handleFile}
        />
      </div>
    </details>
  );
}
