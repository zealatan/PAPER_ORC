/**
 * The project import pipeline (spec §7 / §29):
 *
 *   raw (string | unknown)
 *     → parse
 *     → envelope check
 *     → migrate            (bring schemaVersion up to current)
 *     → validate           (strict Zod validation of the migrated data)
 *     → normalize defaults
 *     → MotionProject
 *
 * Invalid input never corrupts anything: it throws a typed, structured error.
 */
import { ProjectValidationError } from "../errors";
import { type MigrationRegistry, projectMigrations } from "../migrations/registry";
import { CURRENT_SCHEMA_VERSION } from "../project/defaults";
import { normalizeProject } from "../project/normalize";
import type { MotionProject } from "../project/types";
import { validateProject } from "../project/validate";

export interface ImportOptions {
  /** Target schema version to migrate to. Defaults to the current version. */
  targetVersion?: string;
  /** Migration registry to use. Defaults to the application registry. */
  registry?: MigrationRegistry;
}

export interface ImportResult {
  project: MotionProject;
  /** Ordered `from→to` migration steps applied, if any. */
  migrationsApplied: string[];
}

function parseRaw(raw: string | unknown): unknown {
  if (typeof raw !== "string") return raw;
  try {
    return JSON.parse(raw);
  } catch (error) {
    throw new ProjectValidationError("Project JSON could not be parsed.", [
      {
        path: "",
        message: error instanceof Error ? error.message : "Invalid JSON.",
        expected: "valid JSON text",
        suggestion: "Check for trailing commas, unquoted keys, or truncated content.",
      },
    ]);
  }
}

/** Import raw project data (JSON string or parsed object) into a validated MotionProject. */
export function importProject(
  raw: string | unknown,
  options: ImportOptions = {},
): ImportResult {
  const targetVersion = options.targetVersion ?? CURRENT_SCHEMA_VERSION;
  const registry = options.registry ?? projectMigrations;

  const data = parseRaw(raw);

  if (typeof data !== "object" || data === null || Array.isArray(data)) {
    throw new ProjectValidationError("Project data must be a JSON object.", [
      {
        path: "",
        message: "Expected an object at the project root.",
        expected: "object",
        received: data === null ? "null" : Array.isArray(data) ? "array" : typeof data,
        suggestion: "Provide a MotionProject object with a `schemaVersion` field.",
      },
    ]);
  }

  const { project: migrated, applied } = registry.run(data, targetVersion);
  const validated = validateProject(migrated);
  const project = normalizeProject(validated);

  return { project, migrationsApplied: applied };
}
