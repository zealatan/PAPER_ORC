# Architecture Overview

This document summarizes the architecture established in Milestones 0–1. It expands as later
milestones land. The authoritative requirements live in
`../../../blog/architecture_docs/YouTube_Motion_Studio_Master_Spec.md`.

## Layering

The system is deliberately layered so that rendering, state, UI, timeline, serialization, and
export stay independent (spec §0, §21).

```
┌──────────────────────────────────────────────┐
│ apps/editor        UI shell (React)           │  ← consumes core; owns no domain truth
├──────────────────────────────────────────────┤
│ packages/core      Domain model + services    │  ← the source of truth for a project
│   • project/       types, Zod schema, defaults │
│   • migrations/    versioned, ordered runner   │
│   • io/            import/export pipeline       │
│   • errors         typed error hierarchy        │
├──────────────────────────────────────────────┤
│ packages/schemas   JSON Schema (Draft 2020-12) │  ← language-agnostic contract
└──────────────────────────────────────────────┘
```

## The MotionProject document

A `MotionProject` (spec §6) is the top-level serializable document:

- `settings` — composition size, fps, background, pixel ratio.
- `theme` — reference to a theme by id.
- `variables` — template variables (spec §9).
- `assets` — asset references with discriminated `source` unions (spec §6.7).
- `scenes[]` — sequential scenes; global time is accumulated scene duration.
  - `elements[]` — `MotionElement`s with `transform`, `style`, `props`, `timing`,
    `animations`, optional `bindings`, `effects`, and nested `children`.
- `audioTracks` — audio timeline (fleshed out in M9).

Everything is plain data: no functions, no DOM references (spec §21).

## Validation pipeline

Implemented in `packages/core/src/io/importProject.ts`, following spec §7:

```
raw (string | unknown)
  → parse            (JSON.parse when string; typed ProjectValidationError on syntax error)
  → schema validate  (Zod; issues carry JSON path, expected, received, suggestion)
  → migrate          (ordered ProjectMigration chain by schemaVersion)
  → validate         (re-validate migrated data — never trust a migration blindly)
  → normalize        (fill deterministic defaults; spec §6.2 defaults)
  → MotionProject
```

Invalid data is **never silently discarded** — it surfaces as a `ProjectValidationError`
carrying structured issues.

## Determinism

Determinism is a first-class requirement (spec §23). The domain model contains no timing or
randomness; a project rendered at time `t` will depend only on the serialized data and `t`.
The renderer (M2) will consume this model through a `renderAtTime` contract.

## Migrations

`packages/core/src/migrations` holds an ordered registry. `runMigrations(project, target)`:

- finds the current `schemaVersion`,
- applies each `ProjectMigration` in order until the target version is reached,
- throws `MigrationError` when no path exists,
- is idempotent when a project is already at the target version.

Every schema change ships with a migration and tests (spec §29.3).
