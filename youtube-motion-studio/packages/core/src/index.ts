/**
 * @motion-studio/core — the domain model, validation, normalization, migrations and IO for
 * MotionProject documents. This package owns the source of truth for a project; UI and renderer
 * packages consume it and never hold domain truth of their own (spec §21, §34.3).
 */

// Domain types
export type * from "./project/types";

// Zod schemas (runtime validation)
export {
  MotionProjectSchema,
  SceneSchema,
  MotionElementSchema,
  Transform2DSchema,
  AnimationDefinitionSchema,
  ProjectSettingsSchema,
  VariableDefinitionSchema,
  AssetReferenceSchema,
  AssetSourceSchema,
  AudioTrackSchema,
  BackgroundDefinitionSchema,
  TransitionDefinitionSchema,
  KeyframeSchema,
  EasingDefinitionSchema,
} from "./project/schema";

// Validation
export {
  validateProject,
  safeValidateProject,
  collectIssues,
  formatPath,
  type ValidationResult,
} from "./project/validate";

// Normalization + defaults
export { normalizeProject } from "./project/normalize";
export {
  CURRENT_SCHEMA_VERSION,
  DEFAULT_PROJECT_SETTINGS,
  DEFAULT_TRANSFORM,
  createEmptyProject,
  type CreateProjectInput,
} from "./project/defaults";

// Errors
export {
  MotionStudioError,
  ProjectValidationError,
  MigrationError,
  type ValidationIssue,
} from "./errors";

// Migrations
export {
  MigrationRegistry,
  projectMigrations,
  readSchemaVersion,
  type ProjectMigration,
  type MigrationRunResult,
} from "./migrations";

// IO
export { importProject, type ImportOptions, type ImportResult } from "./io/importProject";
export { exportProject, cloneProject, type ExportOptions } from "./io/exportProject";

// Samples
export { ronaldReadProject } from "./samples/ronaldRead";
