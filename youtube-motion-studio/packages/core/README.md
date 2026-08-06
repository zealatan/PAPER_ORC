# @motion-studio/core

The domain model and data services for a `MotionProject`: types, Zod schema, validation,
normalization, migrations, and import/export. This package is the **source of truth** for project
data; UI and renderer packages consume it and hold no domain truth of their own.

## Public API

```ts
import {
  // types
  type MotionProject,
  // validation
  validateProject,
  safeValidateProject,
  // pipeline
  importProject,
  exportProject,
  // model helpers
  createEmptyProject,
  normalizeProject,
  CURRENT_SCHEMA_VERSION,
  // migrations
  MigrationRegistry,
  projectMigrations,
  // errors
  ProjectValidationError,
  MigrationError,
  // sample
  ronaldReadProject,
} from "@motion-studio/core";
```

### Import pipeline

```ts
const { project, migrationsApplied } = importProject(jsonStringOrObject);
```

Runs: `parse → envelope check → migrate → validate → normalize` (spec §7). On failure it throws a
typed error (`ProjectValidationError` / `MigrationError`) with structured issues — never a bare
string, never silent data loss.

### Export

```ts
const json = exportProject(project, { space: 2, canonical: true });
```

`canonical: true` sorts keys recursively for byte-stable, deterministic output (spec §23).

## Architecture notes

- **Types** in `src/project/types.ts` are authoritative; **Zod** in `src/project/schema.ts`
  mirrors them for runtime validation. The recursive element schema is annotated against
  `MotionElement` so the two cannot diverge in shape.
- **Determinism**: the model carries no clocks or randomness; factories take timestamps as input.
- **Migrations** are ordered, idempotent, and throw `MigrationError` on a missing path.

## Testing

```bash
pnpm --filter @motion-studio/core test   # or: pnpm test (repo root)
```

Covers schema validation, structured errors, JSON-Schema conformance (Ajv 2020), lossless
round-trips, normalization idempotency, and the migration runner.
