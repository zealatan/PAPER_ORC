import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import { describe, expect, it } from "vitest";
import { PROJECT_SCHEMA_ID, projectJsonSchema } from "@motion-studio/schemas";
import { ronaldReadProject } from "../src";

function makeValidator() {
  const ajv = new Ajv2020({ allErrors: true, strict: false });
  addFormats(ajv);
  return ajv.compile(projectJsonSchema);
}

describe("project JSON Schema", () => {
  it("exposes the canonical $id", () => {
    expect(PROJECT_SCHEMA_ID).toBe(
      "https://motion-studio.dev/schemas/project.schema.json",
    );
    expect(projectJsonSchema.$id).toBe(PROJECT_SCHEMA_ID);
  });

  it("compiles as a valid Draft 2020-12 schema", () => {
    expect(() => makeValidator()).not.toThrow();
  });

  it("accepts the canonical sample project", () => {
    const validate = makeValidator();
    const valid = validate(ronaldReadProject);
    expect(validate.errors ?? []).toEqual([]);
    expect(valid).toBe(true);
  });

  it("rejects a project with an unknown discriminator", () => {
    const validate = makeValidator();
    const broken = structuredClone(ronaldReadProject) as unknown as {
      scenes: Array<{ background: { type: string } }>;
    };
    broken.scenes[0]!.background = { type: "hologram" };
    expect(validate(broken)).toBe(false);
    expect(validate.errors?.length ?? 0).toBeGreaterThan(0);
  });

  it("rejects a project missing a required field", () => {
    const validate = makeValidator();
    const broken = structuredClone(ronaldReadProject) as unknown as Record<
      string,
      unknown
    >;
    delete broken.settings;
    expect(validate(broken)).toBe(false);
  });
});
