import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { cloneProject, exportProject, importProject, ronaldReadProject } from "../src";

const here = dirname(fileURLToPath(import.meta.url));
const examplePath = resolve(here, "../../../examples/ronald-read/project.motion.json");
const exampleJson = readFileSync(examplePath, "utf8");

describe("project round-trip", () => {
  it("imports the example JSON file without data loss", () => {
    const { project, migrationsApplied } = importProject(exampleJson);
    expect(migrationsApplied).toEqual([]);
    expect(project.id).toBe("project-example-001");
    expect(project.scenes[0]?.elements).toHaveLength(2);
  });

  it("keeps the TS sample and the example JSON file in sync", () => {
    const fromFile = importProject(exampleJson).project;
    const fromTs = importProject(ronaldReadProject).project;
    expect(fromFile).toEqual(fromTs);
  });

  it("is idempotent and lossless through export → import → export", () => {
    const first = importProject(exampleJson).project;
    const serialized = exportProject(first);
    const second = importProject(serialized).project;
    expect(second).toEqual(first);

    // Serializing the re-imported project yields identical bytes (deterministic).
    expect(exportProject(second, { canonical: true })).toBe(
      exportProject(first, { canonical: true }),
    );
  });

  it("preserves original values and only adds safe defaults", () => {
    const original = JSON.parse(exampleJson) as typeof ronaldReadProject;
    const imported = importProject(exampleJson).project;

    // Scalar / non-element sections are byte-for-byte preserved.
    expect(imported.settings).toEqual(original.settings);
    expect(imported.theme).toEqual(original.theme);
    expect(imported.variables).toEqual(original.variables);
    expect(imported.assets).toEqual(original.assets);
    expect(imported.audioTracks).toEqual(original.audioTracks);

    // Element data is preserved; normalization only *adds* empty collections.
    const element = imported.scenes[0]?.elements[0];
    const originalElement = original.scenes[0]?.elements[0];
    expect(element?.props).toEqual(originalElement?.props);
    expect(element?.style).toEqual(originalElement?.style);
    expect(element?.transform).toEqual(originalElement?.transform);
    expect(element?.bindings).toEqual(originalElement?.bindings);
    expect(element?.effects).toEqual([]); // added default, not present in source
  });

  it("clones without sharing references", () => {
    const project = importProject(exampleJson).project;
    const copy = cloneProject(project);
    copy.name = "changed";
    if (copy.scenes[0]) copy.scenes[0].name = "changed scene";
    expect(project.name).toBe("Ronald Read Example");
    expect(project.scenes[0]?.name).toBe("Profile Introduction");
  });
});
