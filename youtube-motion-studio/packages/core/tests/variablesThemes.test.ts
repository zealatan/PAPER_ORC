import { describe, expect, it } from "vitest";
import {
  applyBindings,
  applyTheme,
  createHistory,
  findElementById,
  instantiateTemplate,
  resolveTheme,
  ronaldReadProject,
  runCommand,
  setVariableValue,
  type MotionTemplate,
} from "../src";

describe("applyBindings", () => {
  it("writes variable values into bound element props", () => {
    const bound = applyBindings(ronaldReadProject);
    expect(findElementById(bound, "profile-card-1")?.element.props.title).toBe(
      "Ronald Read",
    );
    expect(findElementById(bound, "caption-1")?.element.props.text).toBe(
      "아무도 그를 부자라고 생각하지 않았음.",
    );
  });

  it("changing one variable updates every bound element", () => {
    const changed = runCommand(
      ronaldReadProject,
      createHistory(),
      setVariableValue("person_name", "Warren Buffett"),
    ).project;
    const bound = applyBindings(changed);
    expect(findElementById(bound, "profile-card-1")?.element.props.title).toBe(
      "Warren Buffett",
    );
  });

  it("applies a format-number transform", () => {
    const project = structuredClone(ronaldReadProject);
    project.variables.yield = {
      id: "yield",
      name: "Yield",
      type: "number",
      value: 0.0296,
    };
    project.scenes[0]!.elements[1]!.bindings = [
      {
        variableId: "yield",
        targetPath: "props.text",
        transform: { type: "format-number", format: "0.0%" },
      },
    ];
    const bound = applyBindings(project);
    expect(findElementById(bound, "caption-1")?.element.props.text).toBe("3.0%");
  });
});

describe("applyTheme", () => {
  it("resolves token references and preserves literals", () => {
    const project = structuredClone(ronaldReadProject);
    project.scenes[0]!.elements[0]!.style = {
      backgroundColor: "token:accent",
      borderColor: "#123456",
    };
    const themed = applyTheme(project, resolveTheme("finance-yellow"));
    const style = findElementById(themed, "profile-card-1")?.element.style;
    expect(style?.backgroundColor).toBe("#ffd000");
    expect(style?.borderColor).toBe("#123456");
  });

  it("different themes yield different values", () => {
    const project = structuredClone(ronaldReadProject);
    project.scenes[0]!.elements[0]!.style = { backgroundColor: "token:accent" };
    const a = applyTheme(project, resolveTheme("finance-yellow"));
    const b = applyTheme(project, resolveTheme("news-red"));
    expect(findElementById(a, "profile-card-1")?.element.style.backgroundColor).not.toBe(
      findElementById(b, "profile-card-1")?.element.style.backgroundColor,
    );
  });
});

describe("instantiateTemplate", () => {
  it("produces a new independent project", () => {
    const template: MotionTemplate = {
      id: "tpl-1",
      name: "Biography",
      description: "A profile intro",
      category: "story",
      project: ronaldReadProject,
    };
    const created = instantiateTemplate(
      template,
      "project-xyz",
      "2026-01-01T00:00:00.000Z",
    );
    expect(created.id).toBe("project-xyz");
    expect(created.name).toBe("Biography");

    // Independent: mutating the new project must not touch the template's project.
    created.scenes[0]!.name = "changed";
    expect(template.project.scenes[0]?.name).toBe("Profile Introduction");
  });
});
