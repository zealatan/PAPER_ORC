/**
 * Ordered migration registry and runner. `run` walks the `from → to` chain until it reaches the
 * target version, throwing {@link MigrationError} when no path exists. Running against a project
 * already at the target version is a no-op (idempotent).
 */
import { MigrationError } from "../errors";
import type { MigrationRunResult, ProjectMigration } from "./types";

/** Read the `schemaVersion` field from pre-validation project data. */
export function readSchemaVersion(project: unknown): string {
  if (
    typeof project === "object" &&
    project !== null &&
    "schemaVersion" in project &&
    typeof (project as { schemaVersion: unknown }).schemaVersion === "string"
  ) {
    return (project as { schemaVersion: string }).schemaVersion;
  }
  throw new MigrationError(
    "Project is missing a string `schemaVersion` field.",
    "unknown",
    "unknown",
    'Add a top-level `schemaVersion` (e.g. "1.0.0") to the project JSON.',
  );
}

export class MigrationRegistry {
  private readonly byFrom = new Map<string, ProjectMigration>();

  register(migration: ProjectMigration): this {
    if (this.byFrom.has(migration.from)) {
      throw new Error(
        `A migration from version "${migration.from}" is already registered.`,
      );
    }
    this.byFrom.set(migration.from, migration);
    return this;
  }

  list(): ProjectMigration[] {
    return [...this.byFrom.values()];
  }

  /** Bring `project` from its current `schemaVersion` up to `targetVersion`. */
  run(project: unknown, targetVersion: string): MigrationRunResult {
    let current = readSchemaVersion(project);
    let data = project;
    const applied: string[] = [];
    // Guard against cyclic migrations: the chain can never exceed the registered count.
    const maxSteps = this.byFrom.size + 1;

    let steps = 0;
    while (current !== targetVersion) {
      const migration = this.byFrom.get(current);
      if (!migration) {
        throw new MigrationError(
          `No migration registered from version "${current}" toward "${targetVersion}".`,
          current,
          targetVersion,
        );
      }
      data = migration.migrate(data);
      applied.push(`${migration.from}→${migration.to}`);
      current = migration.to;

      if (++steps > maxSteps) {
        throw new MigrationError(
          "Migration chain did not terminate (possible cycle).",
          current,
          targetVersion,
        );
      }
    }

    return { project: data, applied };
  }
}

/**
 * The application-wide migration registry.
 *
 * There are currently no released schema versions prior to 1.0.0, so no migrations are
 * registered yet. New schema versions must register their upgrade step here together with tests.
 */
export const projectMigrations = new MigrationRegistry();
