/**
 * Bottom timeline: scene segments sized by their relative duration, with a draggable-in-M4 playhead.
 * Clicking a scene selects it and seeks to its start; clicking empty track space scrubs the playhead
 * (M3 placeholder — richer keyframe lanes and transitions arrive later). Reads playback + selection
 * from the store; owns no local state (spec §34.3).
 */
import type { MouseEvent } from "react";
import { selectDuration, useEditor } from "../state/store";

export function Timeline() {
  const project = useEditor((s) => s.project);
  const time = useEditor((s) => s.time);
  const playing = useEditor((s) => s.playing);
  const selectedSceneId = useEditor((s) => s.selectedSceneId);
  const selectScene = useEditor((s) => s.selectScene);
  const setTime = useEditor((s) => s.setTime);
  const duration = useEditor(selectDuration);

  function seek(event: MouseEvent<HTMLDivElement>) {
    if (duration <= 0) return;
    const rect = event.currentTarget.getBoundingClientRect();
    if (rect.width <= 0) return;
    const ratio = (event.clientX - rect.left) / rect.width;
    const clamped = Math.min(Math.max(ratio, 0), 1);
    setTime(clamped * duration);
  }

  let sceneStart = 0;

  return (
    <div className="timeline">
      <div className="timeline__head">
        <span>{playing ? "Playing" : "Paused"}</span>
        <span>
          {time.toFixed(2)}s / {duration.toFixed(2)}s
        </span>
      </div>
      <div className="timeline__track" onClick={seek}>
        {project.scenes.map((scene) => {
          const start = sceneStart;
          sceneStart += scene.duration;
          const width = duration > 0 ? (scene.duration / duration) * 100 : 0;
          const className =
            selectedSceneId === scene.id
              ? "timeline__scene timeline__scene--active"
              : "timeline__scene";
          return (
            <div
              key={scene.id}
              className={className}
              style={{ width: `${width}%` }}
              onClick={(event) => {
                event.stopPropagation();
                selectScene(scene.id);
                setTime(start);
              }}
            >
              {scene.name}
            </div>
          );
        })}
        <div
          className="timeline__playhead"
          style={{ left: `${duration > 0 ? (time / duration) * 100 : 0}%` }}
        />
      </div>
    </div>
  );
}
