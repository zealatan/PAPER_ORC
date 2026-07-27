/**
 * Project export/serialization. Serialization is deterministic: with `canonical` enabled, object
 * keys are sorted so the same project always produces byte-identical output (spec §23, §29).
 */
import type { MotionProject } from "../project/types";

export interface ExportOptions {
  /** Indentation passed to JSON.stringify. Defaults to 2. Use 0 for compact output. */
  space?: number;
  /** Sort object keys recursively for byte-stable output. Defaults to false. */
  canonical?: boolean;
}

function sortKeysDeep(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map(sortKeysDeep);
  }
  if (value !== null && typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>).sort(([a], [b]) =>
      a < b ? -1 : a > b ? 1 : 0,
    );
    const result: Record<string, unknown> = {};
    for (const [key, val] of entries) {
      result[key] = sortKeysDeep(val);
    }
    return result;
  }
  return value;
}

/** Serialize a project to a JSON string. */
export function exportProject(
  project: MotionProject,
  options: ExportOptions = {},
): string {
  const space = options.space ?? 2;
  const data = options.canonical ? sortKeysDeep(project) : project;
  return JSON.stringify(data, null, space);
}

/** Structured-clone a project so callers can mutate without touching the original. */
export function cloneProject(project: MotionProject): MotionProject {
  return JSON.parse(JSON.stringify(project)) as MotionProject;
}
