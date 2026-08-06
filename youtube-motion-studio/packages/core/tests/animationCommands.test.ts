import { describe, expect, it } from "vitest";
import {
  addAnimation,
  createHistory,
  findElementById,
  removeAnimation,
  ronaldReadProject,
  runCommand,
  updateAnimation,
  type AnimationDefinition,
} from "../src";

const newAnim: AnimationDefinition = {
  id: "anim-new",
  kind: "preset",
  target: "transform",
  start: 0,
  duration: 0.5,
  presetId: "scale-in",
};

function animsOf(project: typeof ronaldReadProject, id: string) {
  return findElementById(project, id)?.element.animations ?? [];
}

describe("animation commands", () => {
  it("adds an animation to an element", () => {
    const next = addAnimation("profile-card-1", newAnim).execute(ronaldReadProject);
    expect(animsOf(next, "profile-card-1")).toHaveLength(2);
    expect(animsOf(ronaldReadProject, "profile-card-1")).toHaveLength(1);
  });

  it("updates an existing animation by id", () => {
    const next = updateAnimation("caption-1", "animation-2", {
      presetId: "pop-in",
    }).execute(ronaldReadProject);
    const anim = animsOf(next, "caption-1")[0];
    expect(anim?.kind === "preset" ? anim.presetId : "").toBe("pop-in");
  });

  it("removes an animation by id", () => {
    const next = removeAnimation("profile-card-1", "animation-1").execute(
      ronaldReadProject,
    );
    expect(animsOf(next, "profile-card-1")).toHaveLength(0);
  });

  it("is undoable through history", () => {
    const result = runCommand(
      ronaldReadProject,
      createHistory(),
      addAnimation("profile-card-1", newAnim),
    );
    expect(result.changed).toBe(true);
    expect(animsOf(result.project, "profile-card-1")).toHaveLength(2);
  });
});
