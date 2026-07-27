import { useMemo } from "react";
import {
  ProjectValidationError,
  importProject,
  ronaldReadProject,
  type MotionProject,
} from "@motion-studio/core";

interface LoadState {
  ok: boolean;
  project?: MotionProject;
  error?: string;
  issues?: string;
}

/**
 * Milestone 0/1 editor shell: it proves the app is runnable and that it consumes the core
 * project model (import → validate → normalize) rather than hardcoding any content. The full
 * canvas, hierarchy, inspector, and timeline arrive in later milestones.
 */
function loadSample(): LoadState {
  try {
    const { project } = importProject(ronaldReadProject);
    return { ok: true, project };
  } catch (error) {
    if (error instanceof ProjectValidationError) {
      return { ok: false, error: error.message, issues: error.formatIssues() };
    }
    return { ok: false, error: error instanceof Error ? error.message : String(error) };
  }
}

function totalDuration(project: MotionProject): number {
  return project.scenes.reduce((sum, scene) => sum + scene.duration, 0);
}

export function App() {
  const state = useMemo(loadSample, []);
  const project = state.project;

  return (
    <div className="app">
      <header className="app__header">
        <h1>YouTube Motion Studio</h1>
        <p>
          Local-first, JSON-driven motion graphics for vertical Shorts — editor shell
          (M0/M1).
        </p>
      </header>

      <section className="card">
        <h2>Sample project</h2>
        {state.ok && project ? (
          <>
            <p>
              <span className="badge badge--ok">Validated</span>
            </p>
            <dl className="kv">
              <dt>Name</dt>
              <dd>{project.name}</dd>
              <dt>Schema version</dt>
              <dd>{project.schemaVersion}</dd>
              <dt>Composition</dt>
              <dd>
                {project.settings.width} × {project.settings.height} @{" "}
                {project.settings.fps} FPS
              </dd>
              <dt>Theme</dt>
              <dd>{project.theme.themeId}</dd>
              <dt>Scenes</dt>
              <dd>{project.scenes.length}</dd>
              <dt>Total duration</dt>
              <dd>{totalDuration(project)}s</dd>
            </dl>
          </>
        ) : (
          <>
            <p>
              <span className="badge badge--error">Invalid</span> {state.error}
            </p>
            {state.issues ? <pre className="issues">{state.issues}</pre> : null}
          </>
        )}
      </section>

      {state.ok && project ? (
        <section className="card">
          <h2>Scenes</h2>
          <ul className="scene-list">
            {project.scenes.map((scene) => (
              <li key={scene.id}>
                <span>{scene.name}</span>
                <span className="muted">
                  {scene.elements.length} elements · {scene.duration}s
                </span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}
