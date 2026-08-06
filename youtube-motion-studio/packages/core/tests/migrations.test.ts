import { describe, expect, it } from "vitest";
import {
  MigrationError,
  MigrationRegistry,
  importProject,
  readSchemaVersion,
  ronaldReadProject,
  type ProjectMigration,
} from "../src";

const bump = (
  from: string,
  to: string,
  mutate?: (p: Record<string, unknown>) => void,
): ProjectMigration => ({
  from,
  to,
  migrate(project) {
    const next = structuredClone(project) as Record<string, unknown>;
    next.schemaVersion = to;
    mutate?.(next);
    return next;
  },
});

describe("readSchemaVersion", () => {
  it("reads a string schemaVersion", () => {
    expect(readSchemaVersion({ schemaVersion: "1.0.0" })).toBe("1.0.0");
  });

  it("throws MigrationError when schemaVersion is missing", () => {
    expect(() => readSchemaVersion({})).toThrow(MigrationError);
  });
});

describe("MigrationRegistry", () => {
  it("is a no-op when already at the target version", () => {
    const registry = new MigrationRegistry();
    const project = { schemaVersion: "1.0.0" };
    const result = registry.run(project, "1.0.0");
    expect(result.applied).toEqual([]);
    expect(result.project).toBe(project);
  });

  it("applies an ordered chain of migrations", () => {
    const registry = new MigrationRegistry()
      .register(bump("0.8.0", "0.9.0", (p) => (p.a = 1)))
      .register(bump("0.9.0", "1.0.0", (p) => (p.b = 2)));

    const result = registry.run({ schemaVersion: "0.8.0" }, "1.0.0");
    expect(result.applied).toEqual(["0.8.0→0.9.0", "0.9.0→1.0.0"]);
    expect(result.project).toMatchObject({ schemaVersion: "1.0.0", a: 1, b: 2 });
  });

  it("does not mutate the input project", () => {
    const registry = new MigrationRegistry().register(
      bump("0.9.0", "1.0.0", (p) => (p.added = true)),
    );
    const input = { schemaVersion: "0.9.0" };
    registry.run(input, "1.0.0");
    expect(input).toEqual({ schemaVersion: "0.9.0" });
  });

  it("throws MigrationError when no path exists", () => {
    const registry = new MigrationRegistry().register(bump("0.8.0", "0.9.0"));
    try {
      registry.run({ schemaVersion: "0.8.0" }, "1.0.0");
      expect.unreachable("should have thrown");
    } catch (error) {
      expect(error).toBeInstanceOf(MigrationError);
      const migrationError = error as MigrationError;
      expect(migrationError.fromVersion).toBe("0.9.0");
      expect(migrationError.toVersion).toBe("1.0.0");
    }
  });

  it("rejects duplicate registrations for the same source version", () => {
    const registry = new MigrationRegistry().register(bump("0.9.0", "1.0.0"));
    expect(() => registry.register(bump("0.9.0", "1.0.1"))).toThrow(/already registered/);
  });

  it("is idempotent: re-running a migrated project changes nothing", () => {
    const registry = new MigrationRegistry().register(bump("0.9.0", "1.0.0"));
    const once = registry.run({ schemaVersion: "0.9.0" }, "1.0.0");
    const twice = registry.run(once.project, "1.0.0");
    expect(twice.applied).toEqual([]);
    expect(twice.project).toEqual(once.project);
  });
});

describe("importProject with migrations", () => {
  it("migrates an older project before strict validation", () => {
    const older = structuredClone(ronaldReadProject) as unknown as Record<
      string,
      unknown
    >;
    older.schemaVersion = "0.9.0";

    const registry = new MigrationRegistry().register(bump("0.9.0", "1.0.0"));
    const { project, migrationsApplied } = importProject(older, { registry });

    expect(migrationsApplied).toEqual(["0.9.0→1.0.0"]);
    expect(project.schemaVersion).toBe("1.0.0");
  });
});
