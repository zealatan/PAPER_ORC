/**
 * Timeline (spec §14): a ruler + draggable playhead (scrubbing), a scene band, and one clip per
 * element that can be dragged (move `timing.start`) or trimmed at either edge. Time↔pixel math and
 * edge snapping come from the pure `timelineMath` module; clip edits go through timing commands so
 * they undo/redo. Scrubbing drives arbitrary-timestamp preview.
 */
import { useLayoutEffect, useMemo, useRef, useState } from "react";
import {
  buildClips,
  projectDuration,
  rulerTicks,
  sceneSpans,
  snapTime,
  timeToX,
  xToTime,
} from "../state/timelineMath";
import { useEditor } from "../state/store";

type Drag =
  | { kind: "scrub" }
  | {
      kind: "move" | "trim-start" | "trim-end";
      id: string;
      sceneStart: number;
      startX: number;
      start0: number;
      dur0: number;
    };

let seq = 0;

export function Timeline() {
  const project = useEditor((s) => s.project);
  const time = useEditor((s) => s.time);
  const playing = useEditor((s) => s.playing);
  const selectedId = useEditor((s) => s.selectedElementId);
  const setTime = useEditor((s) => s.setTime);
  const selectElement = useEditor((s) => s.selectElement);
  const setElementTiming = useEditor((s) => s.setElementTiming);

  const trackRef = useRef<HTMLDivElement>(null);
  const dragRef = useRef<Drag | null>(null);
  const mergeRef = useRef("");
  const [width, setWidth] = useState(0);

  useLayoutEffect(() => {
    const node = trackRef.current;
    if (!node) return;
    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) setWidth(entry.contentRect.width);
    });
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  const duration = projectDuration(project);
  const spans = useMemo(() => sceneSpans(project), [project]);
  const clips = useMemo(() => buildClips(project), [project]);
  const ticks = useMemo(() => rulerTicks(duration), [duration]);

  const pxPerSecond = duration > 0 && width > 0 ? width / duration : 0;
  const tolerance = pxPerSecond > 0 ? 7 / pxPerSecond : 0;

  function localX(clientX: number): number {
    const rect = trackRef.current?.getBoundingClientRect();
    return rect ? clientX - rect.left : 0;
  }

  function snapTargets(exceptId: string): number[] {
    const targets = [time];
    for (const span of spans) targets.push(span.start, span.start + span.duration);
    for (const clip of clips) {
      if (clip.elementId === exceptId) continue;
      targets.push(clip.globalStart, clip.globalStart + clip.duration);
    }
    return targets;
  }

  function onMove(event: PointerEvent) {
    const drag = dragRef.current;
    if (!drag || width === 0) return;
    const t = xToTime(localX(event.clientX), duration, width);

    if (drag.kind === "scrub") {
      setTime(Math.min(duration, Math.max(0, t)));
      return;
    }

    const dt = t - xToTime(drag.startX, duration, width);
    if (drag.kind === "move") {
      const globalStart = snapTime(
        drag.sceneStart + drag.start0 + dt,
        snapTargets(drag.id),
        tolerance,
      );
      const start = Math.max(0, globalStart - drag.sceneStart);
      setElementTiming(drag.id, { start }, mergeRef.current);
    } else if (drag.kind === "trim-start") {
      const globalStart = snapTime(
        drag.sceneStart + drag.start0 + dt,
        snapTargets(drag.id),
        tolerance,
      );
      const start = Math.max(0, globalStart - drag.sceneStart);
      const end = drag.start0 + drag.dur0;
      setElementTiming(
        drag.id,
        { start, duration: Math.max(0.1, end - start) },
        mergeRef.current,
      );
    } else {
      const globalEnd = snapTime(
        drag.sceneStart + drag.start0 + drag.dur0 + dt,
        snapTargets(drag.id),
        tolerance,
      );
      const nextDuration = Math.max(0.1, globalEnd - (drag.sceneStart + drag.start0));
      setElementTiming(drag.id, { duration: nextDuration }, mergeRef.current);
    }
  }

  function onUp() {
    dragRef.current = null;
    window.removeEventListener("pointermove", onMove);
    window.removeEventListener("pointerup", onUp);
  }

  function startDrag(drag: Drag) {
    seq += 1;
    mergeRef.current = `timeline:${seq}`;
    dragRef.current = drag;
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
  }

  function onRulerPointerDown(event: React.PointerEvent) {
    setTime(
      Math.min(duration, Math.max(0, xToTime(localX(event.clientX), duration, width))),
    );
    startDrag({ kind: "scrub" });
  }

  function clipDragStart(
    event: React.PointerEvent,
    kind: "move" | "trim-start" | "trim-end",
    clipId: string,
    sceneStart: number,
    start0: number,
    dur0: number,
  ) {
    event.stopPropagation();
    selectElement(clipId);
    startDrag({
      kind,
      id: clipId,
      sceneStart,
      startX: localX(event.clientX),
      start0,
      dur0,
    });
  }

  return (
    <div className="timeline">
      <div className="timeline__head">
        <span>{playing ? "▶ Playing" : "⏸ Paused"}</span>
        <span>
          {time.toFixed(2)}s / {duration.toFixed(2)}s
        </span>
      </div>

      <div className="timeline__track" ref={trackRef} onPointerDown={onRulerPointerDown}>
        <div className="timeline__ruler">
          {width > 0 &&
            ticks.map((tick) => (
              <span
                key={tick.time}
                className="timeline__tick"
                style={{ left: timeToX(tick.time, duration, width) }}
              >
                {tick.label}
              </span>
            ))}
        </div>

        <div className="timeline__scenes">
          {width > 0 &&
            spans.map((span) => (
              <div
                key={span.sceneId}
                className="timeline__scene"
                style={{
                  left: timeToX(span.start, duration, width),
                  width: timeToX(span.duration, duration, width),
                }}
                title={span.name}
              >
                {span.name}
              </div>
            ))}
        </div>

        <div className="timeline__clips">
          {width > 0 &&
            clips.map((clip, i) => {
              const span = spans.find((s) => s.sceneId === clip.sceneId);
              const sceneStart = span ? span.start : 0;
              return (
                <div
                  key={clip.elementId}
                  className={
                    clip.elementId === selectedId
                      ? "timeline__clip timeline__clip--active"
                      : "timeline__clip"
                  }
                  style={{
                    left: timeToX(clip.globalStart, duration, width),
                    width: timeToX(clip.duration, duration, width),
                    top: i * 22,
                  }}
                  onPointerDown={(e) =>
                    clipDragStart(
                      e,
                      "move",
                      clip.elementId,
                      sceneStart,
                      clip.globalStart - sceneStart,
                      clip.duration,
                    )
                  }
                >
                  <span
                    className="timeline__trim timeline__trim--start"
                    onPointerDown={(e) =>
                      clipDragStart(
                        e,
                        "trim-start",
                        clip.elementId,
                        sceneStart,
                        clip.globalStart - sceneStart,
                        clip.duration,
                      )
                    }
                  />
                  <span className="timeline__clip-label">{clip.name}</span>
                  {clip.animations.map((aStart, ai) => (
                    <span
                      key={ai}
                      className="timeline__anim-marker"
                      style={{
                        left:
                          clip.duration > 0 ? `${(aStart / clip.duration) * 100}%` : "0%",
                      }}
                    />
                  ))}
                  <span
                    className="timeline__trim timeline__trim--end"
                    onPointerDown={(e) =>
                      clipDragStart(
                        e,
                        "trim-end",
                        clip.elementId,
                        sceneStart,
                        clip.globalStart - sceneStart,
                        clip.duration,
                      )
                    }
                  />
                </div>
              );
            })}
        </div>

        {width > 0 ? (
          <div
            className="timeline__playhead"
            style={{ left: timeToX(time, duration, width) }}
          />
        ) : null}
      </div>
    </div>
  );
}
