/**
 * Validation bridges Zod parsing to the domain types and to the structured
 * {@link ProjectValidationError} (spec §7). Invalid data is never silently discarded; every
 * problem carries a JSON path, expected type, actual value, and a suggested fix where possible.
 */
import type { ZodIssue } from "zod";
import { MotionProjectSchema } from "./schema";
import type { MotionProject } from "./types";
import { ProjectValidationError, type ValidationIssue } from "../errors";

/** Convert a Zod path array into a readable JSON path such as `scenes[0].transform.x`. */
export function formatPath(path: ReadonlyArray<string | number>): string {
  let out = "";
  for (const segment of path) {
    if (typeof segment === "number") {
      out += `[${segment}]`;
    } else {
      out += out === "" ? segment : `.${segment}`;
    }
  }
  return out;
}

function summarizeValue(value: unknown): unknown {
  if (typeof value === "string" && value.length > 80) {
    return `${value.slice(0, 77)}…`;
  }
  return value;
}

function issueToValidationIssue(issue: ZodIssue): ValidationIssue {
  const path = formatPath(issue.path);
  const result: ValidationIssue = { path, message: issue.message };

  switch (issue.code) {
    case "invalid_type": {
      result.expected = issue.expected;
      result.received = issue.received;
      result.suggestion =
        issue.received === "undefined"
          ? `Add the missing "${path}" field (expected ${issue.expected}).`
          : `Change "${path}" to a ${issue.expected}.`;
      break;
    }
    case "invalid_enum_value": {
      result.expected = issue.options.map((o) => JSON.stringify(o)).join(" | ");
      result.received = summarizeValue(issue.received);
      result.suggestion = `Use one of: ${result.expected}.`;
      break;
    }
    case "unrecognized_keys": {
      result.expected = "no additional properties";
      result.received = issue.keys.join(", ");
      result.suggestion = `Remove unknown key(s): ${issue.keys.join(", ")}.`;
      break;
    }
    case "invalid_union_discriminator": {
      result.expected = issue.options.map((o) => JSON.stringify(o)).join(" | ");
      result.suggestion = `Set the discriminator to one of: ${result.expected}.`;
      break;
    }
    case "too_small":
    case "too_big": {
      result.suggestion = issue.message;
      break;
    }
    default:
      break;
  }
  return result;
}

/** Map a Zod error's issues to structured validation issues. */
export function collectIssues(issues: readonly ZodIssue[]): ValidationIssue[] {
  return issues.map(issueToValidationIssue);
}

export type ValidationResult =
  | { success: true; project: MotionProject }
  | { success: false; issues: ValidationIssue[] };

/** Validate without throwing. */
export function safeValidateProject(data: unknown): ValidationResult {
  const parsed = MotionProjectSchema.safeParse(data);
  if (parsed.success) {
    return { success: true, project: parsed.data as MotionProject };
  }
  return { success: false, issues: collectIssues(parsed.error.issues) };
}

/** Validate and throw a {@link ProjectValidationError} on failure. */
export function validateProject(data: unknown): MotionProject {
  const result = safeValidateProject(data);
  if (!result.success) {
    throw new ProjectValidationError(
      `Project failed validation with ${result.issues.length} issue(s).`,
      result.issues,
    );
  }
  return result.project;
}
