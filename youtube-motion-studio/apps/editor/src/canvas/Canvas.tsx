/**
 * Center canvas: renders the project through the deterministic SVG backend at the current time and
 * supports click selection with a selection overlay. Hit-testing uses each element's base bounding
 * box (rotation-agnostic in M3); precise transform handles arrive in M4.
 */
import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { renderProjectToSvg } from "@motion-studio/renderer-core";
import { createDefaultRenderRegistry } from "@motion-studio/components";
import { elementBox, selectActiveScene, selectDuration, useEditor } from "../state/store";

const registry = createDefaultRenderRegistry();

function usePlaybackClock() {
  const playing = useEditor((s) => s.playing);
  const setTime = useEditor((s) => s.setTime);
  const duration = useEditor(selectDuration);

  useEffect(() => {
    if (!playing) return;
    let raf = 0;
    let last = performance.now();
    const tick = (now: number) => {
      const dt = (now - last) / 1000;
      last = now;
      const next = useEditor.getState().time + dt;
      setTime(duration > 0 ? next % duration : next);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [playing, duration, setTime]);
}

export function Canvas() {
  usePlaybackClock();
  const project = useEditor((s) => s.project);
  const time = useEditor((s) => s.time);
  const scene = useEditor(selectActiveScene);
  const selectedId = useEditor((s) => s.selectedElementId);
  const selectElement = useEditor((s) => s.selectElement);

  const stageRef = useRef<HTMLDivElement>(null);
  const [stageWidth, setStageWidth] = useState(0);

  useLayoutEffect(() => {
    const node = stageRef.current;
    if (!node) return;
    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) setStageWidth(entry.contentRect.width);
    });
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  const svg = useMemo(() => renderProjectToSvg(project, time, registry), [project, time]);

  const scale = stageWidth > 0 ? stageWidth / project.settings.width : 0;
  const selectedBox = useMemo(() => {
    if (!selectedId || !scene) return null;
    const element = scene.elements.find((el) => el.id === selectedId);
    return element ? elementBox(element) : null;
  }, [selectedId, scene]);

  function handleClick(event: React.MouseEvent<HTMLDivElement>) {
    const node = stageRef.current;
    if (!node || !scene || scale === 0) return;
    const rect = node.getBoundingClientRect();
    const px = (event.clientX - rect.left) / scale;
    const py = (event.clientY - rect.top) / scale;

    const ordered = [...scene.elements].sort(
      (a, b) => b.transform.zIndex - a.transform.zIndex,
    );
    const hit = ordered.find((element) => {
      if (!element.visible) return false;
      const box = elementBox(element);
      return (
        px >= box.left &&
        px <= box.left + box.width &&
        py >= box.top &&
        py <= box.top + box.height
      );
    });
    selectElement(hit ? hit.id : null);
  }

  const aspect = project.settings.height / project.settings.width;

  return (
    <div className="canvas">
      <div className="canvas__scroll">
        <div
          ref={stageRef}
          className="canvas__stage"
          style={{
            aspectRatio: `${project.settings.width} / ${project.settings.height}`,
          }}
          onClick={handleClick}
        >
          <div className="canvas__svg" dangerouslySetInnerHTML={{ __html: svg }} />
          {selectedBox && scale > 0 ? (
            <div
              className="canvas__selection"
              style={{
                left: selectedBox.left * scale,
                top: selectedBox.top * scale,
                width: selectedBox.width * scale,
                height: selectedBox.height * scale,
              }}
            />
          ) : null}
        </div>
      </div>
      <div className="canvas__meta">
        {project.settings.width} × {project.settings.height} · {aspect.toFixed(2)}:1 ·{" "}
        {time.toFixed(2)}s
      </div>
    </div>
  );
}
