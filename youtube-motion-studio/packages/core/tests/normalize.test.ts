import { describe, expect, it } from "vitest";
import {
  createEmptyProject,
  normalizeProject,
  ronaldReadProject,
  validateProject,
} from "../src";

describe("normalizeProject", () => {
  it("fills optional element collections with empty arrays", () => {
    const normalized = normalizeProject(ronaldReadProject);
    for (const scene of normalized.scenes) {
      for (const element of scene.elements) {
        expect(Array.isArray(element.bindings)).toBe(true);
        expect(Array.isArray(element.effects)).toBe(true);
      }
    }
  });

  it("is idempotent", () => {
    const once = normalizeProject(ronaldReadProject);
    const twice = normalizeProject(once);
    expect(twice).toEqual(once);
  });

  it("does not mutate its input", () => {
    const snapshot = structuredClone(ronaldReadProject);
    normalizeProject(ronaldReadProject);
    expect(ronaldReadProject).toEqual(snapshot);
  });

  it("returns a detached copy", () => {
    const normalized = normalizeProject(ronaldReadProject);
    normalized.scenes[0]!.elements[0]!.name = "mutated";
    expect(ronaldReadProject.scenes[0]?.elements[0]?.name).toBe("Profile Card");
  });

  it("normalizes nested children recursively", () => {
    const project = structuredClone(ronaldReadProject);
    const parent = project.scenes[0]!.elements[0]!;
    parent.children = [
      {
        id: "child-1",
        type: "label",
        name: "Child",
        visible: true,
        locked: false,
        transform: parent.transform,
        style: {},
        props: {},
        timing: { start: 0, duration: 1 },
        animations: [],
      },
    ];
    const normalized = normalizeProject(project);
    const child = normalized.scenes[0]?.elements[0]?.children?.[0];
    expect(child?.bindings).toEqual([]);
    expect(child?.effects).toEqual([]);
  });
});

describe("createEmptyProject", () => {
  it("produces a valid, empty, deterministic project", () => {
    const project = createEmptyProject({
      id: "p1",
      name: "New Project",
      now: "2026-01-01T00:00:00.000Z",
    });
    expect(() => validateProject(project)).not.toThrow();
    expect(project.settings.width).toBe(1080);
    expect(project.settings.height).toBe(1920);
    expect(project.settings.fps).toBe(30);
    expect(project.scenes).toEqual([]);
  });
});
