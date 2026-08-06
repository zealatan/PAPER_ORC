import { describe, expect, it } from "vitest";
import {
  evaluateProjectAtTime,
  projectDuration,
  sceneIndexAtTime,
  sceneStartTimes,
} from "../src/timeline";
import { makeElement, makeProject, makeScene } from "./helpers";

const project = makeProject([
  makeScene("s1", [makeElement("a", "rectangle")], 5),
  makeScene("s2", [makeElement("b", "circle")], 3),
]);

describe("scene time math", () => {
  it("computes scene start times from accumulated durations", () => {
    expect(sceneStartTimes(project)).toEqual([0, 5]);
  });

  it("computes total duration", () => {
    expect(projectDuration(project)).toBe(8);
  });

  it("locates the active scene", () => {
    expect(sceneIndexAtTime(project, 0)).toBe(0);
    expect(sceneIndexAtTime(project, 4.9)).toBe(0);
    expect(sceneIndexAtTime(project, 5)).toBe(1);
    expect(sceneIndexAtTime(project, 100)).toBe(1);
    expect(sceneIndexAtTime(project, -1)).toBe(0);
  });
});

describe("evaluateProjectAtTime", () => {
  it("returns the active scene and scene-local time", () => {
    const frame = evaluateProjectAtTime(project, 6);
    expect(frame.sceneIndex).toBe(1);
    expect(frame.sceneLocalTime).toBe(1);
    expect(frame.scene?.id).toBe("s2");
  });

  it("hides elements outside their timing window", () => {
    const p = makeProject([
      makeScene("s1", [
        makeElement("early", "rectangle", { timing: { start: 0, duration: 2 } }),
        makeElement("late", "rectangle", { timing: { start: 3, duration: 2 } }),
      ]),
    ]);
    const frame = evaluateProjectAtTime(p, 1);
    const early = frame.elements.find((e) => e.element.id === "early");
    const late = frame.elements.find((e) => e.element.id === "late");
    expect(early?.visible).toBe(true);
    expect(late?.visible).toBe(false);
  });

  it("orders elements by zIndex ascending", () => {
    const p = makeProject([
      makeScene("s1", [
        makeElement("top", "rectangle", { transform: { zIndex: 10 } }),
        makeElement("bottom", "rectangle", { transform: { zIndex: 1 } }),
      ]),
    ]);
    const frame = evaluateProjectAtTime(p, 0);
    expect(frame.elements.map((e) => e.element.id)).toEqual(["bottom", "top"]);
  });

  it("is deterministic for the same timestamp", () => {
    expect(evaluateProjectAtTime(project, 2.5)).toEqual(
      evaluateProjectAtTime(project, 2.5),
    );
  });
});
