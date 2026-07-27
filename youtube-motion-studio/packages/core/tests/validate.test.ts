import { describe, expect, it } from "vitest";
import {
  ProjectValidationError,
  ronaldReadProject,
  safeValidateProject,
  validateProject,
  type MotionProject,
} from "../src";

function clone(): MotionProject {
  return structuredClone(ronaldReadProject);
}

describe("validateProject", () => {
  it("accepts the canonical sample project", () => {
    expect(() => validateProject(ronaldReadProject)).not.toThrow();
    const project = validateProject(ronaldReadProject);
    expect(project.id).toBe("project-example-001");
    expect(project.scenes).toHaveLength(1);
  });

  it("reports a missing required field with path, expected type and a suggestion", () => {
    const broken = clone();
    // @ts-expect-error deliberately remove a required field
    delete broken.settings.width;

    const result = safeValidateProject(broken);
    expect(result.success).toBe(false);
    if (result.success) return;

    const issue = result.issues.find((i) => i.path === "settings.width");
    expect(issue).toBeDefined();
    expect(issue?.expected).toBe("number");
    expect(issue?.received).toBe("undefined");
    expect(issue?.suggestion).toMatch(/Add the missing/);
  });

  it("reports a wrong type at a nested array path", () => {
    const broken = clone();
    // @ts-expect-error wrong type on purpose
    broken.scenes[0].elements[0].transform.x = "not-a-number";

    const result = safeValidateProject(broken);
    expect(result.success).toBe(false);
    if (result.success) return;

    const issue = result.issues.find(
      (i) => i.path === "scenes[0].elements[0].transform.x",
    );
    expect(issue).toBeDefined();
    expect(issue?.expected).toBe("number");
  });

  it("rejects unknown top-level keys", () => {
    const broken = clone() as MotionProject & { rogue?: unknown };
    broken.rogue = true;

    const result = safeValidateProject(broken);
    expect(result.success).toBe(false);
    if (result.success) return;

    const issue = result.issues.find((i) => i.suggestion?.includes("rogue"));
    expect(issue).toBeDefined();
    expect(issue?.expected).toBe("no additional properties");
  });

  it("rejects an invalid enum value with the allowed options", () => {
    const broken = clone();
    // @ts-expect-error invalid enum on purpose
    broken.settings.durationMode = "sometimes";

    const result = safeValidateProject(broken);
    expect(result.success).toBe(false);
    if (result.success) return;

    const issue = result.issues.find((i) => i.path === "settings.durationMode");
    expect(issue).toBeDefined();
    expect(issue?.suggestion).toMatch(/scenes/);
  });

  it("throws a ProjectValidationError with a formatted issue list", () => {
    const broken = clone();
    // @ts-expect-error remove required field
    delete broken.scenes[0].elements[0].transform.opacity;

    try {
      validateProject(broken);
      expect.unreachable("should have thrown");
    } catch (error) {
      expect(error).toBeInstanceOf(ProjectValidationError);
      const validationError = error as ProjectValidationError;
      expect(validationError.code).toBe("PROJECT_VALIDATION_ERROR");
      expect(validationError.issues.length).toBeGreaterThan(0);
      expect(validationError.formatIssues()).toContain("transform.opacity");
    }
  });
});
