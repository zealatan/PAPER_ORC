/**
 * @motion-studio/schemas
 *
 * Provides the formal JSON Schema (Draft 2020-12) for a MotionProject document.
 * The schema is the language-agnostic contract; `@motion-studio/core` provides Zod
 * schemas that mirror it for rich runtime validation inside the app.
 */
import projectSchema from "../project.schema.json";

/** The MotionProject JSON Schema as a plain object (Draft 2020-12). */
export const projectJsonSchema: Readonly<Record<string, unknown>> =
  projectSchema as Record<string, unknown>;

/** The `$id` of the project schema. */
export const PROJECT_SCHEMA_ID = "https://motion-studio.dev/schemas/project.schema.json";

export default projectJsonSchema;
