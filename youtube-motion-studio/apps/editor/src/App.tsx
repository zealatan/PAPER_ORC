import { useMemo, useState } from "react";
import {
  ProjectValidationError,
  importProject,
  ronaldReadProject,
  type MotionProject,
} from "@motion-studio/core";
import { renderProjectToSvg } from "@motion-studio/renderer-core";
import { createDefaultRenderRegistry } from "@motion-studio/components";
import { demoProject } from "./demoProject";

interface LoadState {
  ok: boolean;
  project?: MotionProject;
  error?: string;
  issues?: string;
}

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

/**
 * Milestone 0–2 editor shell: it proves the app is runnable and that it consumes the core project
 * model AND the deterministic renderer (import → validate → renderAtTime → SVG). The full canvas,
 * hierarchy, inspector, and timeline arrive in later milestones.
 */
export function App() {
  const state = useMemo(loadSample, []);
  const registry = useMemo(() => createDefaultRenderRegistry(), []);
  const [time, setTime] = useState(1);
  const svg = useMemo(
    () => renderProjectToSvg(demoProject, time, registry),
    [registry, time],
  );
  const project = state.project;

  return (
    <div className="app">
      <header className="app__header">
        <h1>YouTube Motion Studio</h1>
        <p>
          Local-first, JSON-driven motion graphics for vertical Shorts — editor shell
          (M0–M2).
        </p>
      </header>

      <section className="card">
        <h2>Renderer preview · deterministic renderAtTime</h2>
        <div className="preview">
          {/* SVG is produced purely from project data at time t (spec §23). */}
          <div className="preview__frame" dangerouslySetInnerHTML={{ __html: svg }} />
          <div className="preview__controls">
            <label htmlFor="time">Time: {time.toFixed(2)}s</label>
            <input
              id="time"
              type="range"
              min={0}
              max={5}
              step={0.05}
              value={time}
              onChange={(event) => setTime(Number(event.target.value))}
            />
            <p className="muted">
              Rendered by <code>@motion-studio/renderer-core</code> (SVG backend) from the
              built-in components. Scrub to see the deterministic pop-in / fade-in.
            </p>
          </div>
        </div>
      </section>

      <section className="card">
        <h2>Sample project validation</h2>
        {state.ok && project ? (
          <>
            <p>
              <span className="badge badge--ok">Validated</span>
            </p>
            <dl className="kv">
              <dt>Name</dt>
              <dd>{project.name}</dd>
              <dt>Composition</dt>
              <dd>
                {project.settings.width} × {project.settings.height} @{" "}
                {project.settings.fps} FPS
              </dd>
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
    </div>
  );
}
