# @motion-studio/editor

The browser editor shell for YouTube Motion Studio (Vite + React).

## Current status (M0/M1)

The shell proves the app is runnable and that it consumes `@motion-studio/core` — it imports,
validates, and normalizes the sample project and renders a summary. It hardcodes **no** content:
everything shown is derived from project data.

Later milestones add the top toolbar, left panel (scenes/hierarchy/components/assets), center
canvas, right inspector, and bottom timeline described in spec §11.

## Commands

```bash
pnpm --filter @motion-studio/editor dev        # start Vite dev server
pnpm --filter @motion-studio/editor build      # production build
pnpm --filter @motion-studio/editor typecheck  # tsc --noEmit
```

## Architecture notes

- UI owns no domain state; the project model lives in `@motion-studio/core` (spec §34.3).
- Editor theme is defined with CSS variables in `src/styles/global.css` (spec §27, §34.4).
