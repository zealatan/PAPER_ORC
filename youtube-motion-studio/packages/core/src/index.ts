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
  PluginActivationError,
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

// Element operations (immutable)
export {
  findElementById,
  updateElementById,
  removeElementById,
  addElementToScene,
} from "./project/elementOps";

// Commands (spec §20)
export {
  type EditorCommand,
  updateElementTransform,
  updateElementTiming,
  updateElementProps,
  updateElementStyle,
  renameElement,
  setElementVisible,
  addAnimation,
  updateAnimation,
  removeAnimation,
  deleteElement,
  addElement,
  updateScene,
  setVariableValue,
  setTheme,
  addAudioTrack,
  updateAudioTrack,
  removeAudioTrack,
} from "./commands";

// AI draft integration (validated data, reviewable edits)
export {
  type AIGenerationRequest,
  type AIGenerationResponse,
  type AIAdapter,
  type AIReview,
  type AIEdit,
  type AIEditSummary,
  type AIEditReview,
  type AssetRequest,
  reviewAIResponse,
  applyAIEdit,
  applyAIEdits,
  reviewAIEdits,
} from "./ai";

// Subtitles (SRT round-trip, active-cue selection)
export {
  type SubtitleCue,
  parseSrt,
  serializeSrt,
  formatSrtTime,
  parseSrtTime,
  activeCue,
} from "./subtitle";

// Variable bindings, theme engine, templates
export { applyBindings } from "./project/bindings";
export { type Theme, THEMES, DEFAULT_THEME_ID, resolveTheme, applyTheme } from "./theme";
export { type MotionTemplate, instantiateTemplate } from "./template";

// History (undo/redo)
export {
  type HistoryEntry,
  type HistoryState,
  type RunResult,
  type StepResult,
  createHistory,
  runCommand,
  undo,
  redo,
  canUndo,
  canRedo,
} from "./history";

// Samples
export { ronaldReadProject } from "./samples/ronaldRead";
