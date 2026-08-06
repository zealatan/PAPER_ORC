# @motion-studio/schemas

Formal **JSON Schema (Draft 2020-12)** for a `MotionProject` document.

## Purpose

This package holds the language-agnostic contract for project data. It is the schema an AI
system, an importer, or an external tool validates against. Inside the app,
`@motion-studio/core` provides Zod schemas that mirror this file for richer runtime messages.

## Public API

```ts
import { projectJsonSchema, PROJECT_SCHEMA_ID } from "@motion-studio/schemas";
```

- `projectJsonSchema` — the schema as a plain object.
- `PROJECT_SCHEMA_ID` — its canonical `$id`.

The raw file is also exported: `@motion-studio/schemas/project.schema.json`.

## Architecture notes

- Draft 2020-12, strict (`additionalProperties: false`) at the top level and on structural defs.
- Discriminated unions (`oneOf` on a `const` discriminator) for `AssetSource`,
  `BackgroundDefinition`, and `AnimationDefinition`.
- Element `type` is an **open string** validated structurally: concrete per-component prop
  schemas live in the component registry (later milestones), matching the extensible
  registry design in the spec.

## Testing

Schema validity and sample-project conformance are covered by tests in `@motion-studio/core`
(using Ajv 2020) so the JSON Schema and the Zod schema are checked against the same fixtures.
