import { describe, expect, it } from "vitest";
import { demoProject } from "../src/demoProject";
import {
  buildClips,
  projectDuration,
  rulerTicks,
  sceneSpans,
  snapTime,
  timeToX,
  xToTime,
} from "../src/state/timelineMath";

describe("sceneSpans / projectDuration", () => {
  it("lays scenes end to end", () => {
    const spans = sceneSpans(demoProject);
    expect(spans).toHaveLength(1);
    expect(spans[0]).toMatchObject({ start: 0, duration: 5 });
    expect(projectDuration(demoProject)).toBe(5);
  });
});

describe("buildClips", () => {
  it("produces one clip per top-level element with global start", () => {
    const clips = buildClips(demoProject);
    const ids = clips.map((c) => c.elementId);
    expect(ids).toContain("card");
    expect(ids).toContain("title");
    expect(ids).toContain("tag");
    // 'dot' is a nested child, not a top-level clip.
    expect(ids).not.toContain("dot");
    const title = clips.find((c) => c.elementId === "title");
    expect(title?.globalStart).toBe(0);
    expect(title?.duration).toBe(5);
  });
});

describe("time <-> x", () => {
  it("round-trips", () => {
    expect(timeToX(2.5, 5, 400)).toBe(200);
    expect(xToTime(200, 5, 400)).toBe(2.5);
  });

  it("guards zero duration/width", () => {
    expect(timeToX(2, 0, 400)).toBe(0);
    expect(xToTime(200, 5, 0)).toBe(0);
  });
});

describe("rulerTicks", () => {
  it("uses a nice step and spans the duration", () => {
    const ticks = rulerTicks(5, 10).map((t) => t.time);
    expect(ticks[0]).toBe(0);
    expect(ticks).toContain(1);
    expect(ticks[ticks.length - 1]).toBeGreaterThanOrEqual(5);
  });
});

describe("snapTime", () => {
  it("snaps to the nearest target within tolerance", () => {
    expect(snapTime(1.04, [1, 2, 3], 0.1)).toBe(1);
    expect(snapTime(1.5, [1, 2, 3], 0.1)).toBe(1.5); // outside tolerance → unchanged
  });
});
