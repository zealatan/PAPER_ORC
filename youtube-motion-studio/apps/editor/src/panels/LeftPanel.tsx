/**
 * Left panel (spec §11): switches between the Scenes list and the Hierarchy tree of the active
 * scene. A thin view over the store — selection and the active tab live in Zustand, not here.
 */
import type { MotionElement } from "@motion-studio/core";
import { selectActiveScene, useEditor } from "../state/store";

function ElementTree({
  elements,
  nested,
}: {
  elements: MotionElement[];
  nested: boolean;
}) {
  const selectedElementId = useEditor((s) => s.selectedElementId);
  const selectElement = useEditor((s) => s.selectElement);
  const toggleElementVisible = useEditor((s) => s.toggleElementVisible);

  return (
    <>
      {elements.map((el) => {
        const base = nested ? "tree-item tree-item--nested" : "tree-item";
        return (
          <li key={el.id}>
            <div
              className={selectedElementId === el.id ? `${base} tree-item--active` : base}
              onClick={() => selectElement(el.id)}
            >
              <button
                className="icon-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleElementVisible(el.id);
                }}
              >
                {el.visible ? "👁" : "🚫"}
              </button>
              {el.name}
              <span className="tree-item__type">{el.type}</span>
            </div>
            {el.children && el.children.length > 0 ? (
              <ul className="tree">
                <ElementTree elements={el.children} nested />
              </ul>
            ) : null}
          </li>
        );
      })}
    </>
  );
}

export function LeftPanel() {
  const leftTab = useEditor((s) => s.leftTab);
  const setLeftTab = useEditor((s) => s.setLeftTab);
  const project = useEditor((s) => s.project);
  const selectedSceneId = useEditor((s) => s.selectedSceneId);
  const selectScene = useEditor((s) => s.selectScene);
  const scene = useEditor(selectActiveScene);

  return (
    <div className="panel">
      <div className="panel__tabs">
        <button
          className={leftTab === "scenes" ? "tab tab--active" : "tab"}
          onClick={() => setLeftTab("scenes")}
        >
          Scenes
        </button>
        <button
          className={leftTab === "hierarchy" ? "tab tab--active" : "tab"}
          onClick={() => setLeftTab("hierarchy")}
        >
          Hierarchy
        </button>
      </div>

      {leftTab === "scenes" ? (
        <>
          <div className="panel__section-title">Scenes</div>
          <ul className="tree">
            {project.scenes.map((s) => (
              <li
                key={s.id}
                className={
                  selectedSceneId === s.id ? "tree-item tree-item--active" : "tree-item"
                }
                onClick={() => selectScene(s.id)}
              >
                {s.name}
                <span className="tree-item__type">{s.duration}s</span>
              </li>
            ))}
          </ul>
        </>
      ) : (
        <>
          <div className="panel__section-title">Hierarchy</div>
          {scene ? (
            <ul className="tree">
              <ElementTree elements={scene.elements} nested={false} />
            </ul>
          ) : null}
        </>
      )}
    </div>
  );
}
