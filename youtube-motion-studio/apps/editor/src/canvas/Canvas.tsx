/**
 * Center canvas with direct-manipulation editing (spec §12): renders the project via the SVG
 * backend at the current time and supports click/shift-click selection, drag-move, corner resize,
 * and a rotate handle. All transforms are command-driven (store → core commands) so undo/redo and
 * canvas↔inspector stay in sync. Snapping guides come from the pure `computeSnap` engine.
 */
import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { renderProjectToSvg } from "@motion-studio/renderer-core";
import { createDefaultRenderRegistry } from "@motion-studio/components";
import {
  applyBindings,
  applyTheme,
  resolveTheme,
  type MotionElement,
  type Transform2D,
} from "@motion-studio/core";
import {
  elementBox,
  selectActiveScene,
  selectDuration,
  useEditor,
  type TransformEntry,
} from "../state/store";
import { type ScreenBox } from "../state/projectOps";
import { computeSnap, type Guide } from "./snapping";

const registry = createDefaultRenderRegistry();
const HANDLES = ["nw", "ne", "se", "sw"] as const;
type Handle = (typeof HANDLES)[number];

let gestureSeq = 0;

interface Gesture {
  id: string;
  mode: "move" | "resize" | "rotate";
  handle?: Handle;
  startPx: number;
  startPy: number;
  starts: Map<string, Transform2D>;
  primaryId: string;
}

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

function boxToTransform(base: Transform2D, box: ScreenBox): Partial<Transform2D> {
  const width = box.width / base.scaleX;
  const height = box.height / base.scaleY;
  return {
    width,
    height,
    x: box.left + base.anchorX * box.width,
    y: box.top + base.anchorY * box.height,
  };
}

export function Canvas() {
  usePlaybackClock();
  const project = useEditor((s) => s.project);
  const time = useEditor((s) => s.time);
  const scene = useEditor(selectActiveScene);
  const selectedIds = useEditor((s) => s.selectedElementIds);
  const primaryId = useEditor((s) => s.selectedElementId);
  const selectElement = useEditor((s) => s.selectElement);
  const setElementsTransform = useEditor((s) => s.setElementsTransform);

  const stageRef = useRef<HTMLDivElement>(null);
  const gestureRef = useRef<Gesture | null>(null);
  const [stageWidth, setStageWidth] = useState(0);
  const [guides, setGuides] = useState<Guide[]>([]);

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

  // Render the project with variable bindings + theme tokens resolved (spec §9, §10).
  const resolved = useMemo(
    () => applyTheme(applyBindings(project), resolveTheme(project.theme.themeId)),
    [project],
  );
  const svg = useMemo(
    () => renderProjectToSvg(resolved, time, registry),
    [resolved, time],
  );
  const scale = stageWidth > 0 ? stageWidth / project.settings.width : 0;

  const elements = scene?.elements ?? [];
  const selectedBoxes = useMemo(
    () =>
      elements
        .filter((el) => selectedIds.includes(el.id))
        .map((el) => ({ id: el.id, box: elementBox(el) })),
    [elements, selectedIds],
  );
  const primaryBox = selectedBoxes.find((b) => b.id === primaryId)?.box ?? null;

  function toProject(event: { clientX: number; clientY: number }) {
    const rect = stageRef.current?.getBoundingClientRect();
    if (!rect || scale === 0) return null;
    return {
      px: (event.clientX - rect.left) / scale,
      py: (event.clientY - rect.top) / scale,
    };
  }

  function hitTest(px: number, py: number): MotionElement | null {
    const ordered = [...elements].sort((a, b) => b.transform.zIndex - a.transform.zIndex);
    return (
      ordered.find((element) => {
        if (!element.visible) return false;
        const box = elementBox(element);
        return (
          px >= box.left &&
          px <= box.left + box.width &&
          py >= box.top &&
          py <= box.top + box.height
        );
      }) ?? null
    );
  }

  function beginGesture(
    mode: Gesture["mode"],
    startPx: number,
    startPy: number,
    handle?: Handle,
  ) {
    const ids = useEditor.getState().selectedElementIds;
    const starts = new Map<string, Transform2D>();
    for (const el of elements) {
      if (ids.includes(el.id)) starts.set(el.id, el.transform);
    }
    const primary = useEditor.getState().selectedElementId;
    if (!primary) return;
    gestureSeq += 1;
    gestureRef.current = {
      id: `${mode}:${gestureSeq}`,
      mode,
      handle,
      startPx,
      startPy,
      starts,
      primaryId: primary,
    };
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onPointerUp);
  }

  function onPointerMove(event: PointerEvent) {
    const gesture = gestureRef.current;
    const point = toProject(event);
    if (!gesture || !point) return;
    let dx = point.px - gesture.startPx;
    let dy = point.py - gesture.startPy;

    if (gesture.mode === "move") {
      const primaryStart = gesture.starts.get(gesture.primaryId);
      if (primaryStart) {
        const proposed = elementBox({
          ...fakeEl,
          transform: { ...primaryStart, x: primaryStart.x + dx, y: primaryStart.y + dy },
        });
        const others = elements
          .filter((el) => !gesture.starts.has(el.id))
          .map((el) => elementBox(el));
        const snap = computeSnap(proposed, others, project.settings, 6);
        dx += snap.dx;
        dy += snap.dy;
        setGuides(snap.guides);
      }
      const entries: TransformEntry[] = [];
      gesture.starts.forEach((start, id) => {
        entries.push({ id, patch: { x: start.x + dx, y: start.y + dy } });
      });
      setElementsTransform(entries, gesture.id);
    } else if (gesture.mode === "resize" && gesture.handle) {
      const start = gesture.starts.get(gesture.primaryId);
      if (!start) return;
      const box = elementBox({ ...fakeEl, transform: start });
      const next = resizeBox(box, gesture.handle, dx, dy);
      setElementsTransform(
        [{ id: gesture.primaryId, patch: boxToTransform(start, next) }],
        gesture.id,
      );
    } else if (gesture.mode === "rotate") {
      const start = gesture.starts.get(gesture.primaryId);
      if (!start) return;
      const box = elementBox({ ...fakeEl, transform: start });
      const cx = box.left + box.width / 2;
      const cy = box.top + box.height / 2;
      const angle = (Math.atan2(point.py - cy, point.px - cx) * 180) / Math.PI + 90;
      setElementsTransform(
        [{ id: gesture.primaryId, patch: { rotation: Math.round(angle) } }],
        gesture.id,
      );
    }
  }

  function onPointerUp() {
    gestureRef.current = null;
    setGuides([]);
    window.removeEventListener("pointermove", onPointerMove);
    window.removeEventListener("pointerup", onPointerUp);
  }

  function onStagePointerDown(event: React.PointerEvent<HTMLDivElement>) {
    if (event.button !== 0) return;
    const point = toProject(event);
    if (!point) return;
    const hit = hitTest(point.px, point.py);
    if (!hit) {
      selectElement(null);
      return;
    }
    if (event.shiftKey) {
      selectElement(hit.id, true);
      return;
    }
    if (!useEditor.getState().selectedElementIds.includes(hit.id)) {
      selectElement(hit.id);
    }
    beginGesture("move", point.px, point.py);
  }

  function onHandlePointerDown(event: React.PointerEvent, handle: Handle) {
    event.stopPropagation();
    const point = toProject(event);
    if (!point) return;
    beginGesture("resize", point.px, point.py, handle);
  }

  function onRotatePointerDown(event: React.PointerEvent) {
    event.stopPropagation();
    const point = toProject(event);
    if (!point) return;
    beginGesture("rotate", point.px, point.py);
  }

  return (
    <div className="canvas">
      <div className="canvas__scroll">
        <div
          ref={stageRef}
          className="canvas__stage"
          style={{
            aspectRatio: `${project.settings.width} / ${project.settings.height}`,
          }}
          onPointerDown={onStagePointerDown}
        >
          <div className="canvas__svg" dangerouslySetInnerHTML={{ __html: svg }} />

          {scale > 0 &&
            guides.map((guide, i) =>
              guide.axis === "x" ? (
                <div
                  key={`gx${i}`}
                  className="canvas__guide canvas__guide--v"
                  style={{ left: guide.position * scale }}
                />
              ) : (
                <div
                  key={`gy${i}`}
                  className="canvas__guide canvas__guide--h"
                  style={{ top: guide.position * scale }}
                />
              ),
            )}

          {scale > 0 &&
            selectedBoxes.map(({ id, box }) => (
              <div
                key={id}
                className={
                  id === primaryId
                    ? "canvas__selection canvas__selection--primary"
                    : "canvas__selection"
                }
                style={{
                  left: box.left * scale,
                  top: box.top * scale,
                  width: box.width * scale,
                  height: box.height * scale,
                }}
              />
            ))}

          {scale > 0 && primaryBox ? (
            <div
              className="canvas__handles"
              style={{
                left: primaryBox.left * scale,
                top: primaryBox.top * scale,
                width: primaryBox.width * scale,
                height: primaryBox.height * scale,
              }}
            >
              <div className="canvas__rotate" onPointerDown={onRotatePointerDown} />
              {HANDLES.map((handle) => (
                <div
                  key={handle}
                  className={`canvas__handle canvas__handle--${handle}`}
                  onPointerDown={(e) => onHandlePointerDown(e, handle)}
                />
              ))}
            </div>
          ) : null}
        </div>
      </div>
      <div className="canvas__meta">
        {project.settings.width} × {project.settings.height} · {time.toFixed(2)}s ·{" "}
        {selectedIds.length} selected
      </div>
    </div>
  );
}

// A throwaway element used only to reuse `elementBox` math for a bare transform.
const fakeEl: MotionElement = {
  id: "_",
  type: "_",
  name: "_",
  visible: true,
  locked: false,
  transform: {
    x: 0,
    y: 0,
    width: 0,
    height: 0,
    rotation: 0,
    scaleX: 1,
    scaleY: 1,
    anchorX: 0,
    anchorY: 0,
    skewX: 0,
    skewY: 0,
    opacity: 1,
    zIndex: 0,
  },
  style: {},
  props: {},
  timing: { start: 0, duration: 0 },
  animations: [],
};

function resizeBox(box: ScreenBox, handle: Handle, dx: number, dy: number): ScreenBox {
  let { left, top, width, height } = box;
  if (handle === "nw") {
    left += dx;
    top += dy;
    width -= dx;
    height -= dy;
  } else if (handle === "ne") {
    top += dy;
    width += dx;
    height -= dy;
  } else if (handle === "se") {
    width += dx;
    height += dy;
  } else {
    left += dx;
    width -= dx;
    height += dy;
  }
  // Keep sizes positive.
  return {
    left,
    top,
    width: Math.max(4, width),
    height: Math.max(4, height),
  };
}
