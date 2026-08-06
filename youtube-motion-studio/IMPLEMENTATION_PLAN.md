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

## Milestone 2 — Renderer Foundation ✅ (this pass)

- [x] Backend-agnostic scene-graph IR (`renderer-core/src/scene-graph.ts`) — rect/ellipse/line/
      text/image/group primitives; components emit these so backends never duplicate logic.
- [x] Deterministic timeline (`timeline.ts`) — `evaluateProjectAtTime(project, globalTime)`:
      global→scene→element-local time, visibility windows, zIndex paint order, nested children.
- [x] Transform + easing + animation math (`transform.ts`, `easing.ts`, `animation.ts`) — pure,
      seedless; entrance/exit presets (fade/pop/scale/zoom/slide) + basic numeric keyframes.
- [x] `RenderRegistry` + `RenderContext` (asset resolution); unknown types render as placeholders.
- [x] **SVG backend** (`renderers/svg.ts`) — byte-stable `renderProjectToSvg` + `SvgFrameRenderer`
      (the `FrameRenderer` contract), used for deterministic visual-regression snapshots.
- [x] **Pixi backend** (`renderers/pixi.ts`) — `PixiFrameRenderer`, lazy `import("pixi.js")` so Node
      never loads WebGL; browser preview/export behind the same interface.
- [x] Component pack (`packages/components`): registry + rectangle, circle, text, image, group,
      each with Zod props schema, defaults, and a primitive renderer.
- [x] Editor renders a live demo via the SVG backend with a `renderAtTime` scrubber.

**Acceptance:** same time ⇒ same frame (asserted across timeline/svg/animation tests); sample scene
renders; visual-regression SVG snapshots stored + stable; 74 tests pass across 5 packages. The five
components + Pixi backend were implemented by a 6-agent leaf workflow against fixed contracts.

Deferred within M2 (documented TODOs): full preset/keyframe library and per-property keyframe
channels (M6); Pixi image-asset loading; canvas/WebGPU backends.

---

## Milestone 3 — Editor Shell ✅ (this pass)

- [x] Zustand store (`apps/editor/src/state/store.ts`) — project + transient editor state
      (selection, playback, UI) kept separate from serialized project (spec §21); immutable element
      updates via `projectOps.ts`.
- [x] Shell layout (spec §11): top toolbar, left panel, center canvas, right inspector, bottom
      timeline (`App.tsx` + `styles/global.css` dark token theme).
- [x] Center canvas (`canvas/Canvas.tsx`) — renders the project via the SVG backend at the current
      time, click-selection with a selection overlay, and a preview playback clock (rAF).
- [x] Top toolbar — play/pause/stop, time readout, JSON **Save** (download) and **Load** (file).
- [x] Left panel — Scenes list + Hierarchy tree with visibility toggles and selection.
- [x] Inspector — collapsible General/Transform/Appearance/Content sections editing the selected
      element (name, transform, background, text props).
- [x] Timeline placeholder — scene segments + playhead + click-to-seek.

**Acceptance:** project opens; components render on the canvas; inspector selection + editing works;
JSON save→reload round-trips the project. The four panels were built by a 4-agent workflow against
the store contract, then integrated. (Command/undo architecture arrives in M4, spec §20.)

---

## Milestone 4 — Canvas Interaction ✅ (this pass)

- [x] Command/history architecture in core (spec §20): `EditorCommand` + command creators
      (`commands/`), snapshot-based undo/redo with mergeKey coalescing (`history/`), immutable
      element ops (`project/elementOps.ts`). Unit-tested.
- [x] Store refactor: every mutation runs through `runCommand`; `undo`/`redo` actions; multi-select
      (`selectedElementIds` + primary); drag/nudge via a multi-element transform command.
- [x] Canvas direct manipulation: click + shift-click select, drag-move, corner **resize** handles,
      **rotate** handle, multi-select overlays — all command-driven and coalesced per gesture.
- [x] Snapping engine (pure `computeSnap`) with center/edge guides drawn on the canvas.
- [x] Keyboard shortcuts hook: undo/redo (Ctrl/Cmd+Z / Shift+Z / Y), delete, arrow-nudge
      (1px / 10px with Shift), ignoring text inputs.
- [x] Toolbar Undo/Redo buttons wired to history state.

**Acceptance (smoke-verified):** transforms are command-driven; drag moved an element +100px and
**Undo restored it exactly** (Δx→0); canvas overlay and inspector stay synchronized. 86 tests pass.

Deferred within M4 (documented): rotation-aware selection overlay/handles (overlay is AABB),
marquee selection, align/distribute UI, equal-spacing suggestions.

---

## Milestone 5 — Timeline & Playback ✅ (this pass)

- [x] Pure timeline math (`state/timelineMath.ts`): scene spans, global/scene/element time
      conversions, clip layout, "nice" ruler ticks, edge snapping. Unit-tested.
- [x] Full timeline panel: time ruler, scene band, one clip per element, a draggable playhead.
- [x] Scrubbing — drag the playhead / click the ruler to preview any timestamp.
- [x] Clip editing — drag to move `timing.start`, trim either edge; snapping to playhead, scene
      bounds, and neighbouring clip edges. All via the `updateElementTiming` command (undoable).
- [x] Playback and scrubbing share the same deterministic `renderProjectToSvg(time)` path, so a
      scrubbed frame matches the played frame.

**Acceptance (smoke-verified):** scrub to 50% → 2.50s preview; trimming a clip shrank it and
**Undo restored it**; playback matches scrubbed frames. 92 tests pass.

---

## Milestone 6 — Animation ✅ (this pass)

- [x] Deterministic animation evaluation (from M2) with easing + entrance/exit presets; preset ids
      exposed via `PRESET_IDS` for the editor.
- [x] Animation commands in core (`addAnimation` / `updateAnimation` / `removeAnimation`) — undoable.
- [x] Animation inspector section: list, add (preset picker), edit start/duration, remove — every
      animation is plain editable `AnimationDefinition` data.
- [x] Timeline animation indicators: a marker per animation on each element clip.
- [x] Store actions for animation editing; visual snapshot tests render presets at multiple
      timestamps (t=0 / 0.25 / 1).

**Acceptance:** animation is deterministic (unit tests); presets are editable data (inspector,
smoke-verified add 1→2); visual tests cover multiple timestamps. 96 tests pass.

Deferred within M6: a keyframe editor UI (keyframes evaluate deterministically already; per-property
channels + graph editor land alongside richer M6 later); more presets.

---

## Milestone 7 — Production Components ✅ (this pass)

- [x] Extended the scene-graph IR with a `polyline` primitive (SVG + Pixi) for charts, tails, arrows.
- [x] 13 production components, each with a Zod props schema, defaults, default transform, and a
      primitive renderer: **title, caption, image-card, profile-card, character, speech-bubble,
      topic-circle, youtube-comment, phone-frame, notification, bar-chart, line-chart, table**.
- [x] All registered in the component registry (18 built-ins total incl. M2 primitives).
- [x] Tests: every built-in renders on default props and on garbage/unknown props **without
      crashing**; registry completeness; unknown element types still show placeholders.

**Acceptance:** each component has schema + renderer + defaults + tests; unknown props do not crash
the editor (verified across all 18). Showcase SVG visually verified. 101 tests pass. The 13
components were built by a 13-agent workflow against the fixed `ComponentDefinition` contract.

Deferred within M7: per-component inspector control schemas (components currently use the generic
inspector + data-editable props); richer chart axes/labels.

---

## Milestone 8 — Variables, Themes & Templates ✅ (this pass)

- [x] Variable bindings (`core/project/bindings.ts`): `applyBindings` writes variable values into
      bound element paths (with `format-number` / `uppercase` transforms). Edit once → all bound
      elements update.
- [x] Theme engine (`core/theme`): a token registry (5 themes) + `applyTheme` resolving
      `token:<name>` references; manual literals preserved.
- [x] Templates (`core/template`): `MotionTemplate` + `instantiateTemplate` → a **new independent**
      deep-cloned project. Two starter templates (Biography Story, Stat Card) as app content.
- [x] Commands: `setVariableValue`, `setTheme`; store actions + a `selectResolvedProject` selector
      (bindings + theme applied at render).
- [x] Editor: Variables tab (edit values), Templates tab (Use template), toolbar theme picker.

**Acceptance (smoke-verified in the browser):** editing `person_name` updated the bound
profile-card text; switching to the News-Red theme repainted `token:accent` (#e01e37); using a
template produced a fresh project. 107 tests pass.

Deferred within M8: binding-creation UI (bindings authored in data/templates for now); typography /
spacing theme tokens beyond colors; variable groups/forms.

---

## Milestone 9 — Audio & Subtitles ✅ (this pass)

- [x] Subtitles as data (`core/subtitle`): `SubtitleCue`, `parseSrt`/`serializeSrt` (lossless
      round-trip), `activeCue(cues, time)`. Time-aware **subtitle component** renders the active cue
      via a new `RenderContext.time` / `sceneTime` (threaded through the SVG + Pixi backends).
- [x] Subtitle inspector: cue count + **Import SRT** (file → parsed cues, undoable).
- [x] Audio track commands (`addAudioTrack` / `updateAudioTrack` / `removeAudioTrack`) and a preview
      sync hook (`useAudioPlayback`) that drives one `<audio>` per track from the timeline
      (position + play/pause), so audio stays in sync during playback and scrubbing.

**Acceptance:** SRT round-trip is unit-tested; subtitle timing is correct (smoke: the cue switched
at its boundary as the playhead scrubbed 1s → 3.5s); audio is driven off the same timeline clock as
the preview. 112 tests pass.

Deferred within M9: waveform rendering; audio-clip editing in the timeline lane; WebVTT import;
karaoke/word-level highlighting (data model supports it).

---

## Milestone 10 — MP4 Export ✅ (this pass)

- [x] `apps/renderer` Node export pipeline: deterministic SVG frames → **resvg** rasterization →
      **FFmpeg** (H.264, yuv420p, +faststart). No browser needed; a frame at `t` depends only on the
      project and `t`.
- [x] Applies variable bindings + theme before rendering, so **the export matches the editor
      preview** exactly.
- [x] Per-frame progress callback; **cancellation** via AbortSignal (kills FFmpeg, removes the
      partial file); a full **render report** (resolution, fps, duration, codec, CRF, timing,
      missing assets, exact FFmpeg command).
- [x] `render` CLI (via tsx) + an **integration test that actually encodes an MP4 and verifies it
      with ffprobe** (guarded to skip when ffmpeg is absent).

**Acceptance (verified with a real file):** the sample exported to a valid **1080 × 1920 H.264 MP4**;
ffprobe reported **duration 5.000s** matching the project; **150 frames** (5s × 30fps, none missing);
the decoded frame shows the bound "Ronald Read" name and the Korean caption. 115 tests pass.

Deferred within M10: audio mixing into the MP4 (single-track adelay/amix — arg-building only so far,
no audio asset to exercise); an in-editor Export button (needs a render server/queue); PNG-sequence /
GIF / WebM outputs.

---

## Milestone 11 — Plugins ✅ (this pass)

- [x] `packages/plugin-sdk`: plugin **manifest** (id/version/engine/permissions), a permission-gated
      **PluginAPI** (register components/themes/templates), and a **PluginHost** that loads behind
      three guards — engine-version check, permission check, and error isolation.
- [x] Reversible registration: every capability call returns a disposer, so `unload` exactly
      reverses `activate` (spec §19.4).
- [x] Example plugin (a "sticker" component + a theme) demonstrating a trusted local plugin.
- [x] `PluginActivationError` (typed) surfaced instead of crashes.

**Acceptance (unit-tested):** the example plugin registers a component then removes it on unload; a
plugin requiring a newer engine is rejected; a plugin that throws during activation is isolated and
its partial registrations are rolled back; capabilities without permission are denied. 119 tests.

Deferred within M11: an in-editor Plugins tab wired to a live/dynamic render registry; untrusted
plugin sandboxing (spec §19.3 — only trusted local plugins for now).

## Milestone 12 — AI Draft Integration ✅ (this pass)

- [x] AI request/response models + an `AIAdapter` interface (AI produces **data**, never touches
      rendered nodes — spec §25.1).
- [x] `reviewAIResponse`: validates an AI project draft through the standard import pipeline
      **without side effects** — invalid output is rejected safely and never corrupts the project.
- [x] Structured AI edits (`update-element` / `set-variable` / `add-element` / `remove-element`)
      with `applyAIEdit`/`applyAIEdits`, and `reviewAIEdits` producing a **reviewable diff**
      (per-edit validity + a preview with only the valid edits applied — approve/reject).
- [x] Asset requests surfaced as placeholders; `store.importAIDraft` loads a valid draft or reports
      structured issues.

**Acceptance (unit-tested):** invalid AI output is rejected without throwing; a valid draft loads as
editable data; a batch of edits is reviewed with invalid ones flagged and only valid ones applied.
124 tests.

---

## Status: all milestones M0–M12 implemented ✅

The full spec §36 roadmap is complete: monorepo → domain model → deterministic renderer → editor
shell → canvas interaction → timeline → animation → 18-component pack → variables/themes/templates →
audio/subtitles → **MP4 export** → plugins → AI drafts. 124 tests across 21 files; typecheck, lint,
format, and build all green; a real 1080×1920 MP4 was produced and ffprobe-verified.

Remaining work is the _within-milestone_ deferrals noted in each section above (e.g. audio mixing
into MP4, in-editor Plugins/AI panels, keyframe graph editor, WebVTT, sandboxed plugins) and the
spec's future/non-goal items — none of which block the implemented foundation.

## Legacy deck integration (spec §26) ✅

- [x] `packages/legacy-adapter`: a `LegacyTemplateAdapter` that **detects and imports the existing
      PG deck** (`pg_deck.json`) into a MotionProject. Per spec §26.3 (step 1, "isolate the reusable
      project data"; do not rewrite the original renderer): titles/subtitles/quotes become real text
      elements, per-scene `subLines` become a time-distributed subtitle, background videos become
      **asset requests**, and complex chart/table templates are imported as labelled placeholders and
      listed in a **migration report**.
- [x] Verified on the real deck: **20 scenes → 91 elements**, 14 chart placeholders + 4 background
      asset requests reported; a rendered frame shows the hero scene's Korean eyebrow/title/caption
      and the active subtitle cue. Unit-tested (detect, text translation, subtitle cues, placeholders).

This is the on-ramp for gradually moving the PG deck onto the new engine (spec §26.3 steps 2–8:
wrap renderer → registry → scenes-as-JSON → replace timing → visual editor → replace legacy
components incrementally), while the old pipeline keeps working untouched.

## Verification commands

```bash
corepack pnpm install        # or: pnpm install (shim on PATH)
pnpm typecheck
pnpm lint
pnpm format:check
pnpm test
pnpm build
```
