import { describe, expect, it } from "vitest";
import { demoProject } from "../src/demoProject";
import {
  elementBox,
  findElement,
  findScene,
  updateElement,
} from "../src/state/projectOps";

describe("findElement", () => {
  it("finds a top-level element with its scene", () => {
    const found = findElement(demoProject, "title");
    expect(found?.element.id).toBe("title");
    expect(found?.scene.id).toBe("scene-1");
  });

  it("finds a nested child element", () => {
    const found = findElement(demoProject, "dot");
    expect(found?.element.type).toBe("circle");
  });

  it("returns null for unknown ids", () => {
    expect(findElement(demoProject, "nope")).toBeNull();
    expect(findElement(demoProject, null)).toBeNull();
  });
});

describe("findScene", () => {
  it("locates a scene by id", () => {
    expect(findScene(demoProject, "scene-1")?.name).toBe("Demo");
    expect(findScene(demoProject, null)).toBeNull();
  });
});

describe("updateElement", () => {
  it("updates immutably without touching the original", () => {
    const next = updateElement(demoProject, "title", (el) => ({
      ...el,
      name: "Renamed",
    }));
    expect(findElement(next, "title")?.element.name).toBe("Renamed");
    expect(findElement(demoProject, "title")?.element.name).toBe("title");
    expect(next).not.toBe(demoProject);
  });

  it("updates a nested element and preserves siblings", () => {
    const next = updateElement(demoProject, "dot", (el) => ({
      ...el,
      visible: false,
    }));
    expect(findElement(next, "dot")?.element.visible).toBe(false);
    expect(findElement(next, "title")).not.toBeNull();
  });
});

describe("elementBox", () => {
  it("computes the top-left box from anchor + scale", () => {
    const box = elementBox({
      id: "b",
      type: "rectangle",
      name: "b",
      visible: true,
      locked: false,
      transform: {
        x: 200,
        y: 300,
        width: 100,
        height: 80,
        rotation: 0,
        scaleX: 2,
        scaleY: 1,
        anchorX: 0.5,
        anchorY: 0.5,
        skewX: 0,
        skewY: 0,
        opacity: 1,
        zIndex: 0,
      },
      style: {},
      props: {},
      timing: { start: 0, duration: 1 },
      animations: [],
    });
    // width*scaleX = 200; anchor centered → left = 200 - 100 = 100; top = 300 - 40 = 260.
    expect(box).toEqual({ left: 100, top: 260, width: 200, height: 80 });
  });
});
