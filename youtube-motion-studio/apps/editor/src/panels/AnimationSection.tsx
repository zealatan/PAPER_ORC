/**
 * Animation inspector section (spec §15). Lists the selected element's animations as editable data
 * — preset picker, start, and duration — plus add/remove. Every edit goes through animation
 * commands so it is undoable. Presets are represented as plain `AnimationDefinition` data.
 */
import { PRESET_IDS } from "@motion-studio/renderer-core";
import { selectSelectedElement, useEditor } from "../state/store";

export function AnimationSection() {
  const element = useEditor(selectSelectedElement);
  const addAnimation = useEditor((s) => s.addAnimationToSelected);
  const updateAnimation = useEditor((s) => s.updateSelectedAnimation);
  const removeAnimation = useEditor((s) => s.removeSelectedAnimation);

  if (!element) return null;

  return (
    <details className="insp-section" open>
      <summary>Animation</summary>

      {element.animations.length === 0 ? (
        <div className="empty-hint">No animations.</div>
      ) : (
        element.animations.map((animation) => (
          <div key={animation.id} className="anim-row">
            {animation.kind === "preset" ? (
              <div className="field">
                <label>Preset</label>
                <select
                  value={animation.presetId}
                  onChange={(e) =>
                    updateAnimation(animation.id, { presetId: e.target.value })
                  }
                >
                  {PRESET_IDS.map((id) => (
                    <option key={id} value={id}>
                      {id}
                    </option>
                  ))}
                </select>
              </div>
            ) : (
              <div className="field">
                <label>Keyframes</label>
                <input value={`${animation.keyframes.length} keys`} disabled />
              </div>
            )}
            <div className="field-row">
              <div className="field">
                <label>Start</label>
                <input
                  type="number"
                  step={0.05}
                  min={0}
                  value={animation.start}
                  onChange={(e) =>
                    updateAnimation(animation.id, { start: Number(e.target.value) })
                  }
                />
              </div>
              <div className="field">
                <label>Duration</label>
                <input
                  type="number"
                  step={0.05}
                  min={0}
                  value={animation.duration}
                  onChange={(e) =>
                    updateAnimation(animation.id, { duration: Number(e.target.value) })
                  }
                />
              </div>
            </div>
            <div className="anim-row__actions">
              <button
                type="button"
                className="tbtn"
                onClick={() => removeAnimation(animation.id)}
              >
                Remove
              </button>
            </div>
          </div>
        ))
      )}

      <div className="anim-row__actions">
        <button
          type="button"
          className="tbtn tbtn--primary"
          onClick={() => addAnimation(PRESET_IDS[0] ?? "fade-in")}
        >
          + Add animation
        </button>
      </div>
    </details>
  );
}
