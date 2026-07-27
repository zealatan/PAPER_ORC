# YouTube Motion Studio

A local-first, JSON-driven, AI-compatible **motion graphics editor** for vertical YouTube
Shorts (default composition **1080 × 1920 @ 30 FPS**).

This repository implements the product described in
`../blog/architecture_docs/YouTube_Motion_Studio_Master_Spec.md`. It is being built milestone by
milestone; the app stays runnable after every milestone.

## Current status

Implemented: **Milestone 0 (Repository Foundation)** and **Milestone 1 (Core Project Model)**.
See [`IMPLEMENTATION_PLAN.md`](./IMPLEMENTATION_PLAN.md) for the full milestone checklist and the
deferred milestones (renderer, editor shell, timeline, animation, export, plugins, AI).

## Architecture at a glance

The project keeps **rendering / state / UI / timeline / serialization / export** separated
(spec §0). Content is never hardcoded into the renderer — everything is serializable project data.

```
packages/schemas   JSON Schema (Draft 2020-12) for MotionProject
packages/core      Domain types, Zod schema, validation, normalization, migrations, samples
apps/editor        Vite + React shell (loads and validates the sample project)
examples/          Sample .motion.json projects
docs/              Architecture and development notes
```

The validation pipeline (spec §7) is:

```
raw JSON → parse → schema validate → migrate → validate → normalize defaults → editor
```

## Requirements

- Node.js ≥ 20 (developed on v22)
- pnpm 9 (via `corepack`)

## Getting started

```bash
corepack enable            # provides pnpm 9
pnpm install
pnpm dev                   # runs apps/editor on Vite
```

## Quality gates

```bash
pnpm typecheck    # tsc --noEmit across all packages
pnpm lint         # ESLint (flat config) + typescript-eslint
pnpm format:check # Prettier
pnpm test         # Vitest unit + integration tests
pnpm build        # Library tsc emit + editor Vite build
```

CI (`.github/workflows/ci.yml`) runs all of the above on every push.

## Packages

| Package                                        | Purpose                                                  |
| ---------------------------------------------- | -------------------------------------------------------- |
| [`@motion-studio/schemas`](./packages/schemas) | Formal JSON Schema for a `MotionProject`.                |
| [`@motion-studio/core`](./packages/core)       | Domain model, validation, normalization, migrations, IO. |
| [`@motion-studio/editor`](./apps/editor)       | Browser editor shell (grows across later milestones).    |

## License

Private / internal.
