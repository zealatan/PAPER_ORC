import { describe, expect, it } from "vitest";
import {
  addElementToScene,
  canRedo,
  canUndo,
  createHistory,
  deleteElement,
  findElementById,
  redo,
  removeElementById,
  renameElement,
  runCommand,
  undo,
  updateElementById,
  updateElementTransform,
  ronaldReadProject,
  type MotionElement,
} from "../src";

const baseElement: MotionElement = {
  id: "new-1",
  type: "rectangle",
  name: "New",
  visible: true,
  locked: false,
  transform: {
    x: 0,
    y: 0,
    width: 10,
    height: 10,
    rotation: 0,
    scaleX: 1,
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
};

describe("elementOps", () => {
  it("finds, updates immutably, removes, and adds elements", () => {
    const found = findElementById(ronaldReadProject, "caption-1");
    expect(found?.element.type).toBe("caption");

    const updated = updateElementById(ronaldReadProject, "caption-1", (el) => ({
      ...el,
      name: "X",
    }));
    expect(findElementById(updated, "caption-1")?.element.name).toBe("X");
    expect(findElementById(ronaldReadProject, "caption-1")?.element.name).toBe(
      "Bottom Caption",
    );

    const removed = removeElementById(ronaldReadProject, "caption-1");
    expect(findElementById(removed, "caption-1")).toBeNull();

    const added = addElementToScene(ronaldReadProject, "scene-1", baseElement);
    expect(findElementById(added, "new-1")?.element.id).toBe("new-1");
  });
});

describe("history", () => {
  it("records a command and undoes/redoes it exactly", () => {
    const h0 = createHistory();
    const run = runCommand(
      ronaldReadProject,
      h0,
      updateElementTransform("caption-1", { x: 999 }),
    );
    expect(run.changed).toBe(true);
    expect(findElementById(run.project, "caption-1")?.element.transform.x).toBe(999);
    expect(canUndo(run.history)).toBe(true);

    const undone = undo(run.project, run.history);
    expect(undone).not.toBeNull();
    expect(findElementById(undone!.project, "caption-1")?.element.transform.x).toBe(540);
    expect(canRedo(undone!.history)).toBe(true);

    const redone = redo(undone!.project, undone!.history);
    expect(findElementById(redone!.project, "caption-1")?.element.transform.x).toBe(999);
  });

  it("coalesces consecutive commands with the same mergeKey", () => {
    let project = ronaldReadProject;
    let history = createHistory();
    for (const x of [10, 20, 30]) {
      const r = runCommand(
        project,
        history,
        updateElementTransform("caption-1", { x }, "drag:caption-1"),
        { coalesce: true },
      );
      project = r.project;
      history = r.history;
    }
    // A single coalesced entry; undo returns to the original in one step.
    expect(history.past).toHaveLength(1);
    const undone = undo(project, history);
    expect(findElementById(undone!.project, "caption-1")?.element.transform.x).toBe(540);
  });

  it("does not record a no-op command", () => {
    const history = createHistory();
    const run = runCommand(ronaldReadProject, history, {
      label: "noop",
      execute: (p) => p,
    });
    expect(run.changed).toBe(false);
    expect(canUndo(run.history)).toBe(false);
  });

  it("clears the redo stack after a new command", () => {
    const h0 = createHistory();
    const a = runCommand(ronaldReadProject, h0, renameElement("caption-1", "A"));
    const undone = undo(a.project, a.history)!;
    expect(canRedo(undone.history)).toBe(true);
    const b = runCommand(undone.project, undone.history, deleteElement("caption-1"));
    expect(canRedo(b.history)).toBe(false);
  });
});
