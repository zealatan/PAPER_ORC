/**
 * Right-hand inspector (spec §11): edits the selected element's name, transform, appearance and
 * (for text) content. A thin view over the store — every field reads from the selected element and
 * writes back through a store action, owning no local domain state (spec §34.3).
 */
import { selectSelectedElement, useEditor } from "../state/store";
import { AnimationSection } from "./AnimationSection";
import { SubtitleSection } from "./SubtitleSection";

export function Inspector() {
  const element = useEditor(selectSelectedElement);
  const renameSelected = useEditor((s) => s.renameSelected);
  const updateSelectedTransform = useEditor((s) => s.updateSelectedTransform);
  const updateSelectedStyle = useEditor((s) => s.updateSelectedStyle);
  const updateSelectedProps = useEditor((s) => s.updateSelectedProps);

  if (!element) {
    return (
      <div className="panel">
        <div className="empty-hint">Select an element to edit its properties.</div>
      </div>
    );
  }

  const { transform, style } = element;
  const backgroundColor =
    typeof style.backgroundColor === "string" ? style.backgroundColor : "#000000";

  return (
    <div className="panel">
      <details className="insp-section" open>
        <summary>General</summary>
        <div className="field">
          <label>Name</label>
          <input value={element.name} onChange={(e) => renameSelected(e.target.value)} />
        </div>
        <div className="field">
          <label>Type</label>
          <input value={element.type} disabled />
        </div>
      </details>

      <details className="insp-section" open>
        <summary>Transform</summary>
        <div className="field-row">
          <div className="field">
            <label>X</label>
            <input
              type="number"
              value={transform.x}
              onChange={(e) => updateSelectedTransform({ x: Number(e.target.value) })}
            />
          </div>
          <div className="field">
            <label>Y</label>
            <input
              type="number"
              value={transform.y}
              onChange={(e) => updateSelectedTransform({ y: Number(e.target.value) })}
            />
          </div>
        </div>
        <div className="field-row">
          <div className="field">
            <label>Width</label>
            <input
              type="number"
              value={transform.width}
              onChange={(e) => updateSelectedTransform({ width: Number(e.target.value) })}
            />
          </div>
          <div className="field">
            <label>Height</label>
            <input
              type="number"
              value={transform.height}
              onChange={(e) =>
                updateSelectedTransform({ height: Number(e.target.value) })
              }
            />
          </div>
        </div>
        <div className="field-row">
          <div className="field">
            <label>Rotation</label>
            <input
              type="number"
              value={transform.rotation}
              onChange={(e) =>
                updateSelectedTransform({ rotation: Number(e.target.value) })
              }
            />
          </div>
          <div className="field">
            <label>Opacity</label>
            <input
              type="number"
              step={0.05}
              min={0}
              max={1}
              value={transform.opacity}
              onChange={(e) =>
                updateSelectedTransform({ opacity: Number(e.target.value) })
              }
            />
          </div>
        </div>
      </details>

      <details className="insp-section" open>
        <summary>Appearance</summary>
        <div className="field">
          <label>Background</label>
          <input
            type="color"
            value={backgroundColor}
            onChange={(e) => updateSelectedStyle({ backgroundColor: e.target.value })}
          />
        </div>
      </details>

      {element.type === "text" ? (
        <details className="insp-section" open>
          <summary>Content</summary>
          <div className="field">
            <label>Text</label>
            <input
              value={String(element.props.text ?? "")}
              onChange={(e) => updateSelectedProps({ text: e.target.value })}
            />
          </div>
          <div className="field">
            <label>Font size</label>
            <input
              type="number"
              value={Number(element.props.fontSize ?? 48)}
              onChange={(e) => updateSelectedProps({ fontSize: Number(e.target.value) })}
            />
          </div>
        </details>
      ) : null}

      <SubtitleSection />
      <AnimationSection />
    </div>
  );
}
