/**
 * Typed error hierarchy (spec §30). User-facing errors expose *what failed*, a *probable cause*,
 * and a *suggested action*; raw stack traces are never surfaced by default.
 *
 * Only the errors used by Milestones 0–1 are implemented here. Later milestones add their own
 * (AssetNotFoundError, RenderInitializationError, FrameRenderError, ExportCancelledError, …)
 * following the same base contract.
 */

/** A single structured validation problem (spec §7). */
export interface ValidationIssue {
  /** Dot/bracket JSON path to the offending value, e.g. `scenes[0].elements[1].transform.x`. */
  path: string;
  /** Human-readable message. */
  message: string;
  /** Expected type or shape, when known. */
  expected?: string;
  /** The actual received value (kept small; large values are summarized). */
  received?: unknown;
  /** A suggested fix, when one can be inferred. */
  suggestion?: string;
}

export abstract class MotionStudioError extends Error {
  abstract readonly code: string;
  /** A short, user-facing probable cause. */
  readonly probableCause?: string;
  /** A suggested next action for the user. */
  readonly suggestion?: string;

  constructor(
    message: string,
    options?: { probableCause?: string; suggestion?: string },
  ) {
    super(message);
    this.name = new.target.name;
    this.probableCause = options?.probableCause;
    this.suggestion = options?.suggestion;
  }
}

export class ProjectValidationError extends MotionStudioError {
  readonly code = "PROJECT_VALIDATION_ERROR";
  readonly issues: ValidationIssue[];

  constructor(message: string, issues: ValidationIssue[]) {
    super(message, {
      probableCause: "The project data did not match the expected schema.",
      suggestion:
        issues.length > 0
          ? `Fix ${issues.length} field(s); see the issues list for paths and expected types.`
          : "Check the project JSON against the MotionProject schema.",
    });
    this.issues = issues;
  }

  /** A compact multi-line summary suitable for logs or a details toggle. */
  formatIssues(): string {
    return this.issues
      .map((i) => {
        const parts = [`• ${i.path || "<root>"}: ${i.message}`];
        if (i.expected !== undefined) parts.push(`expected ${i.expected}`);
        if (i.suggestion) parts.push(`fix: ${i.suggestion}`);
        return parts.join(" — ");
      })
      .join("\n");
  }
}

export class PluginActivationError extends MotionStudioError {
  readonly code = "PLUGIN_ACTIVATION_ERROR";
  readonly pluginId: string;

  constructor(pluginId: string, message: string, suggestion?: string) {
    super(message, {
      probableCause: `Plugin "${pluginId}" could not be activated.`,
      suggestion:
        suggestion ?? "Check the plugin's manifest, permissions, and engine version.",
    });
    this.pluginId = pluginId;
  }
}

export class MigrationError extends MotionStudioError {
  readonly code = "MIGRATION_ERROR";
  readonly fromVersion: string;
  readonly toVersion: string;

  constructor(
    message: string,
    fromVersion: string,
    toVersion: string,
    suggestion?: string,
  ) {
    super(message, {
      probableCause: `No migration path from ${fromVersion} to ${toVersion}.`,
      suggestion:
        suggestion ?? "Register the missing ProjectMigration steps and try again.",
    });
    this.fromVersion = fromVersion;
    this.toVersion = toVersion;
  }
}
