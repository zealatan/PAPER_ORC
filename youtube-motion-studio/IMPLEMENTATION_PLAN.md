# YouTube Motion Studio — Implementation Plan

Derived from `blog/architecture_docs/YouTube_Motion_Studio_Master_Spec.md` (v1.0.0).
This plan is the working checklist. The **specification is the source of truth**; where the
spec is silent, reasonable architectural decisions are recorded here.

## Guiding constraints (from spec §0)

- Never hardcode content into the renderer; all content is serializable data.
- Keep rendering / state / UI / timeline / serialization / export separated.
- Monorepo, TypeScript strict, registries + schemas + adapters over hacks.
- Every project deterministic; every migration versioned; every major module tested.
- Keep the app runnable after every milestone.

## Repository placement decision

The spec describes a standalone `youtube-motion-studio/` monorepo. The existing repository
(`/home/messi/PAPER_ORC`) is a shared working tree used concurrently by other sessions
(deck pipeline on branch `fire-inflation`). To avoid disrupting that shared tree we do **not**
switch branches; instead the monorepo lives in an isolated directory
`youtube-motion-studio/` at the repo root, colliding with nothing.

## Toolchain decisions

| Concern            | Choice                                                 | Rationale                         |
| ------------------ | ------------------------------------------------------ | --------------------------------- |
| Package manager    | pnpm 9 (via corepack)                                  | spec §5 mandates pnpm workspaces  |
| Language           | TypeScript 5, `strict`                                 | spec §34.1                        |
| Module system      | ESM, `moduleResolution: bundler`                       | Vite + vitest friendly            |
| Runtime validation | Zod 3                                                  | spec §7 (Zod mirrors JSON Schema) |
| JSON Schema        | Draft 2020-12, validated in tests with Ajv 8           | spec §7                           |
| Editor app         | Vite + React 18                                        | spec §4.1                         |
| Tests              | Vitest 2                                               | spec §4.1                         |
| Lint / format      | ESLint 9 flat config + typescript-eslint 8, Prettier 3 | spec §4.1                         |
| CI                 | GitHub Actions                                         | spec §36 M0                       |

Cross-package imports resolve to **TypeScript source** via each package's `exports` map so the
editor and tests need no pre-build step in dev; library packages still emit `dist` via `tsc`
during `build` to prove they compile standalone.

## Package layout (subset built now)

Only the packages required for Milestones 0–1 are created now. Later milestones (renderer-core,
components, animation-presets, templates, plugin-sdk, asset-manager, shared-ui, renderer app)
are left as explicit TODOs with acceptance criteria below.

```
youtube-motion-studio/
├─ package.json, pnpm-workspace.yaml, tsconfig.base.json, eslint.config.js, prettier.config.js
├─ vitest.config.ts, .npmrc, .gitignore, README.md, IMPLEMENTATION_PLAN.md
├─ .github/workflows/ci.yml
├─ packages/
│  ├─ schemas/   → project.schema.json (Draft 2020-12) + typed accessor
│  └─ core/      → domain types, Zod schema, validation, normalization, migrations, samples, tests
├─ apps/
│  └─ editor/    → minimal Vite+React shell that loads + validates the sample project
├─ examples/
│  └─ ronald-read/project.motion.json
└─ docs/architecture/overview.md
```

---

## Milestone 0 — Repository Foundation ✅ (this pass)

- [x] pnpm monorepo (`pnpm-workspace.yaml`, root `package.json` scripts)
- [x] Vite editor app (`apps/editor`), runnable via `pnpm dev`
- [x] TypeScript strict mode (`tsconfig.base.json`)
- [x] ESLint flat config + Prettier
- [x] Vitest test setup
- [x] GitHub Actions CI (`install → typecheck → lint → test → build`)
- [x] Basic documentation (`README.md`, `docs/architecture/overview.md`, per-package READMEs)
- [x] Sample project (`examples/ronald-read/project.motion.json`)

**Acceptance:** `pnpm install`, `pnpm dev`, `pnpm build`, `pnpm test` all succeed.
Also enforced: `pnpm typecheck`, `pnpm lint`, `pnpm format:check`.

## Milestone 1 — Core Project Model ✅ (this pass)

- [x] Project interfaces (`packages/core/src/project/types.ts`) mirroring spec §6
- [x] Zod schema (`packages/core/src/project/schema.ts`) — discriminated unions for
      element types, animation kinds, asset sources, background/transition types
- [x] JSON Schema (`packages/schemas/project.schema.json`) — Draft 2020-12, strict, `$defs`
- [x] Validation (`packages/core/src/project/validate.ts`) producing errors with
      JSON path, expected type, actual value, suggested fix (spec §7)
- [x] Normalization (`packages/core/src/project/normalize.ts`) — fill defaults deterministically
- [x] Migrations framework (`packages/core/src/migrations/*`) — ordered, tested, idempotent runner
- [x] Import/export flow (`packages/core/src/io/*`) implementing the spec §7 pipeline:
      `parse → schema validate → migrate → validate → normalize`
- [x] Typed errors (`packages/core/src/errors.ts`)
- [x] Sample project files + round-trip fixtures

**Acceptance:**

- Invalid projects produce useful errors (path + expected + actual + suggestion). — tests
- Valid projects round-trip without data loss. — tests
- Migration tests pass (ordering, path-finding, idempotency, `MigrationError` on gaps). — tests

---

## Deferred milestones (explicit TODOs — not implemented this pass)

- **M2 Renderer foundation**: `packages/renderer-core` — `FrameRenderer`, Pixi/DOM renderers,
  `RenderRegistry`, deterministic `renderAtTime`. _Accept:_ same time ⇒ same frame; visual regression.
- **M3 Editor shell**, **M4 Canvas interaction**, **M5 Timeline/playback**, **M6 Animation**,
  **M7 Production components**, **M8 Variables/Themes/Templates**, **M9 Audio/Subtitles**,
  **M10 MP4 export** (`apps/renderer`), **M11 Plugins**, **M12 AI draft integration**.

Each remains defined by its spec §36 acceptance criteria. The domain model and validation
built in M1 are the foundation these consume; no shortcut was taken that blocks them.

## Verification commands

```bash
corepack pnpm install        # or: pnpm install (shim on PATH)
pnpm typecheck
pnpm lint
pnpm format:check
pnpm test
pnpm build
```
