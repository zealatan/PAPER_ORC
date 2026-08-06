/**
 * Left panel (spec §11): Scenes, Hierarchy, Variables, and Templates tabs. A thin view over the
 * store — selection, variables, theme, and the active tab live in Zustand, not here.
 */
import type { MotionElement, VariableDefinition } from "@motion-studio/core";
import { STARTER_TEMPLATES } from "../templates";
import { selectActiveScene, useEditor, type LeftTab } from "../state/store";

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

function VariableField({ variable }: { variable: VariableDefinition }) {
  const setVariable = useEditor((s) => s.setVariable);
  const value = variable.value;
  if (variable.type === "number") {
    return (
      <div className="field">
        <label>{variable.name}</label>
        <input
          type="number"
          value={typeof value === "number" ? value : 0}
          onChange={(e) => setVariable(variable.id, Number(e.target.value))}
        />
      </div>
    );
  }
  return (
    <div className="field">
      <label>{variable.name}</label>
      <input
        value={typeof value === "string" ? value : String(value ?? "")}
        onChange={(e) => setVariable(variable.id, e.target.value)}
      />
    </div>
  );
}

const TABS: Array<{ id: LeftTab; label: string }> = [
  { id: "scenes", label: "Scenes" },
  { id: "hierarchy", label: "Hierarchy" },
  { id: "variables", label: "Variables" },
  { id: "templates", label: "Templates" },
];

export function LeftPanel() {
  const leftTab = useEditor((s) => s.leftTab);
  const setLeftTab = useEditor((s) => s.setLeftTab);
  const project = useEditor((s) => s.project);
  const selectedSceneId = useEditor((s) => s.selectedSceneId);
  const selectScene = useEditor((s) => s.selectScene);
  const useTemplate = useEditor((s) => s.useTemplate);
  const scene = useEditor(selectActiveScene);

  const variables = Object.values(project.variables);

  return (
    <div className="panel">
      <div className="panel__tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            className={leftTab === tab.id ? "tab tab--active" : "tab"}
            onClick={() => setLeftTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
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
      ) : null}

      {leftTab === "hierarchy" ? (
        <>
          <div className="panel__section-title">Hierarchy</div>
          {scene ? (
            <ul className="tree">
              <ElementTree elements={scene.elements} nested={false} />
            </ul>
          ) : null}
        </>
      ) : null}

      {leftTab === "variables" ? (
        <>
          <div className="panel__section-title">Variables</div>
          {variables.length === 0 ? (
            <div className="empty-hint">This project has no variables.</div>
          ) : (
            variables.map((variable) => (
              <VariableField key={variable.id} variable={variable} />
            ))
          )}
        </>
      ) : null}

      {leftTab === "templates" ? (
        <>
          <div className="panel__section-title">Templates</div>
          <ul className="tree">
            {STARTER_TEMPLATES.map((template) => (
              <li key={template.id} className="template-item">
                <div className="template-item__name">{template.name}</div>
                <div className="template-item__desc">{template.description}</div>
                <button
                  className="tbtn tbtn--primary"
                  onClick={() => useTemplate(template)}
                >
                  Use template
                </button>
              </li>
            ))}
          </ul>
        </>
      ) : null}
    </div>
  );
}
