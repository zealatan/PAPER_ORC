# YouTube Motion Studio
## Master Product Requirements & Software Design Specification

**Document type:** Product Requirements Document (PRD) + Software Design Document (SDD)  
**Primary implementation agent:** Claude Code  
**Primary language:** TypeScript  
**Primary runtime:** Browser + Node.js  
**Primary target:** Local-first browser-based motion graphics editor for YouTube Shorts  
**Default composition:** 1080 × 1920, 30 FPS, 9:16 vertical video  
**Status:** Initial architecture and implementation specification  
**Version:** 1.0.0

---

# 0. Instructions for Claude Code

You are building a long-term, production-grade motion graphics editing application.

Do not interpret this document as a request for a quick prototype.

The application must be designed as a reusable video creation engine that can grow to:

- 100+ component types
- 100+ animation presets
- 1,000+ timeline elements
- tens of thousands of lines of code
- AI-generated projects
- reusable YouTube Shorts templates
- programmatic MP4 rendering
- future desktop packaging
- future plugin marketplace support

## Mandatory implementation principles

1. Never hardcode a specific video, company, person, story, subtitle, scene, or animation into the renderer.
2. All project content must be represented as serializable data.
3. All visual elements must be editable through a GUI.
4. All project data must support JSON import and export.
5. Rendering, state, UI, timeline, serialization, and export must remain separated.
6. Do not place the whole application in one HTML file.
7. Do not use inline JavaScript for application logic.
8. Do not use duplicated rendering logic.
9. Do not implement features as isolated hacks.
10. Prefer extension points, registries, schemas, adapters, and reusable services.
11. Every saved project must be deterministic.
12. Preview playback and exported video must match as closely as technically possible.
13. The AI integration layer must never directly manipulate DOM nodes.
14. AI communicates only through validated project JSON or commands.
15. Every data migration must be versioned.
16. Every major module must have automated tests.
17. Do not ask the user to manually finish boilerplate work that can be completed autonomously.
18. When a requirement is too large for one implementation pass, implement the correct foundational architecture first and leave explicit TODO items with acceptance criteria.
19. Do not replace architecture with temporary shortcuts without documenting the tradeoff.
20. Keep the application runnable after every milestone.

## Required workflow

Before writing large amounts of code:

1. Inspect the existing repository.
2. Create or update `IMPLEMENTATION_PLAN.md`.
3. Create a checklist grouped by milestone.
4. Implement the smallest coherent vertical slice.
5. Run type checks, lint, unit tests, and build.
6. Fix failures before proceeding.
7. Update documentation.
8. Commit logical changes separately when Git is available.

---

# 1. Product Vision

YouTube Motion Studio is a browser-based, local-first motion graphics editor optimized for rapid production of YouTube Shorts, Reels, and vertical informational videos.

It should combine selected strengths of:

- Adobe After Effects: timeline, keyframes, easing, compositing
- Canva: reusable templates and asset-driven creation
- PowerPoint: simple scene composition and presentation logic
- Figma: direct manipulation, alignment, hierarchy, reusable components
- CapCut: video-oriented editing and caption workflows
- Remotion-style rendering: programmatic, deterministic video output

The product is not intended to replicate every feature of those tools.

Its core advantage is:

> A reusable, JSON-driven, AI-compatible motion graphics engine specialized for repeatable content production.

Example target content:

- company stories
- dividend investing stories
- retirement backtests
- historical biographies
- ETF comparisons
- stock analysis explainers
- timeline-based storytelling
- character-based explainers
- comments and social media simulations
- charts, maps, tables, counters, and subtitles
- templated YouTube Shorts

---

# 2. Product Goals

## 2.1 Primary goals

The application must allow the user to:

1. Create and edit vertical video compositions visually.
2. Organize a project into scenes and timeline layers.
3. Add reusable visual components.
4. Animate elements using presets or keyframes.
5. Edit all relevant properties through an inspector.
6. Save and load projects as JSON.
7. reuse templates by replacing variables and assets.
8. preview animations at a target frame rate.
9. export still images, project bundles, HTML previews, and MP4 video.
10. generate valid project JSON from an AI system.
11. maintain compatibility across future schema versions.
12. integrate later with existing HTML-based video templates.

## 2.2 Secondary goals

- local-first usage
- no mandatory account
- offline editing after dependencies are installed
- future desktop packaging using Tauri or Electron
- future collaborative editing
- future cloud rendering
- future asset marketplace
- future template marketplace
- future voice, subtitle, and AI image integrations

## 2.3 Non-goals for the first production version

- full After Effects parity
- complex 3D rendering
- advanced skeletal animation
- professional color grading
- multi-user real-time collaboration
- cloud account management
- advanced audio mixing
- GPU particle simulation
- arbitrary third-party code execution inside projects

---

# 3. Target User and Core Workflows

## 3.1 Primary user

A creator who produces multiple YouTube Shorts with recurring visual styles and wants to replace manual PowerPoint or video-editor assembly with reusable HTML-based templates.

## 3.2 Core workflow A: Create from template

1. Open application.
2. Select template such as `Biography Story`.
3. Enter variables:
   - person name
   - headline
   - dates
   - assets
   - key facts
4. Application updates every bound element.
5. User adjusts timing and styling.
6. User previews.
7. User exports MP4.

## 3.3 Core workflow B: Build manually

1. Create a new 1080 × 1920 project.
2. Add scenes.
3. Drag components from asset panel to canvas.
4. Edit properties.
5. Add animation presets.
6. Adjust timeline clips.
7. Add audio and subtitles.
8. Export.

## 3.4 Core workflow C: AI-generated project

1. User provides a structured prompt or script.
2. AI service returns a validated project JSON draft.
3. Application imports the JSON.
4. Missing assets are shown as unresolved placeholders.
5. User reviews and edits.
6. Application exports final video.

## 3.5 Core workflow D: Import existing project

1. Open JSON or project bundle.
2. Validate schema.
3. Run migrations when required.
4. Show migration report.
5. Load project without data loss.

---

# 4. Recommended Technology Stack

## 4.1 Application

Use:

- TypeScript
- Vite
- React
- Zustand for editor state
- Zod for runtime validation
- Vitest for unit and integration tests
- Playwright for end-to-end tests
- ESLint
- Prettier

React is recommended for the editor UI because the application will include:

- hierarchy trees
- property panels
- timeline editing
- selection state
- context menus
- drag-and-drop
- keyboard shortcuts
- multiple synchronized panels

The rendering engine must remain framework-independent where practical.

## 4.2 Canvas and rendering

Use a renderer abstraction.

Recommended initial implementation:

- PixiJS for high-performance composition rendering
- HTML DOM overlay only where required for text editing or accessible controls
- OffscreenCanvas or standard Canvas for frame capture where supported

Do not tightly couple project data to PixiJS APIs.

Create renderer interfaces so future backends can include:

- DOMRenderer
- PixiRenderer
- Canvas2DRenderer
- future WebGPU renderer

## 4.3 Interaction layer

Use one of the following:

- custom transform handles on top of PixiJS
- or a dedicated interaction layer based on DOM/SVG overlays

Avoid making Fabric.js the core source of truth. It may be used only if isolated behind an adapter.

## 4.4 Timeline and animation

Implement an internal deterministic timeline model.

GSAP may be used for interactive preview only if wrapped behind an adapter.

However, final frame rendering must be based on deterministic evaluation:

```ts
renderFrame(project, timeInSeconds)
```

Do not rely only on browser animation timing or CSS animations for export.

## 4.5 Charts

Use a chart abstraction.

Recommended:

- custom SVG/Canvas charts for core reusable chart types
- optional adapter for ECharts

Charts must support deterministic rendering at arbitrary timestamps.

## 4.6 Export and rendering

Use:

- Node.js render worker
- Playwright or Puppeteer
- FFmpeg
- PNG frame sequence or raw frame pipe
- Web Audio API for preview
- FFmpeg for final audio mixing

Recommended pipeline:

```text
Project JSON
→ render route
→ deterministic frame evaluation
→ browser frame capture
→ FFmpeg encoding
→ MP4 output
```

Support H.264 MP4 first.

## 4.7 File and persistence

Initial implementation:

- JSON file import/export
- IndexedDB autosave
- File System Access API when available
- browser download fallback

Future desktop version may use native filesystem APIs.

---

# 5. Repository Structure

```text
youtube-motion-studio/
├─ apps/
│  ├─ editor/
│  │  ├─ index.html
│  │  ├─ src/
│  │  │  ├─ main.tsx
│  │  │  ├─ app/
│  │  │  ├─ panels/
│  │  │  ├─ canvas/
│  │  │  ├─ timeline/
│  │  │  ├─ inspector/
│  │  │  ├─ hierarchy/
│  │  │  ├─ assets/
│  │  │  └─ styles/
│  │  └─ vite.config.ts
│  └─ renderer/
│     ├─ src/
│     │  ├─ server.ts
│     │  ├─ renderJob.ts
│     │  ├─ frameCapture.ts
│     │  └─ ffmpeg.ts
│     └─ package.json
│
├─ packages/
│  ├─ core/
│  │  ├─ src/
│  │  │  ├─ project/
│  │  │  ├─ scene/
│  │  │  ├─ element/
│  │  │  ├─ timeline/
│  │  │  ├─ animation/
│  │  │  ├─ variables/
│  │  │  ├─ commands/
│  │  │  ├─ history/
│  │  │  ├─ migrations/
│  │  │  └─ validation/
│  │  └─ tests/
│  │
│  ├─ renderer-core/
│  │  ├─ src/
│  │  │  ├─ Renderer.ts
│  │  │  ├─ RenderContext.ts
│  │  │  ├─ PixiRenderer.ts
│  │  │  ├─ DomRenderer.ts
│  │  │  └─ RenderRegistry.ts
│  │  └─ tests/
│  │
│  ├─ components/
│  │  ├─ src/
│  │  │  ├─ registry.ts
│  │  │  ├─ text/
│  │  │  ├─ media/
│  │  │  ├─ social/
│  │  │  ├─ finance/
│  │  │  ├─ charts/
│  │  │  ├─ character/
│  │  │  ├─ shapes/
│  │  │  └─ layout/
│  │  └─ tests/
│  │
│  ├─ animation-presets/
│  ├─ templates/
│  ├─ plugin-sdk/
│  ├─ schemas/
│  ├─ asset-manager/
│  └─ shared-ui/
│
├─ plugins/
│  ├─ stock-charts/
│  ├─ maps/
│  ├─ subtitles/
│  └─ social-cards/
│
├─ examples/
│  ├─ biography-story/
│  ├─ company-story/
│  └─ etf-comparison/
│
├─ docs/
│  ├─ architecture/
│  ├─ component-api/
│  ├─ schema/
│  ├─ plugins/
│  └─ development/
│
├─ scripts/
├─ tests/
├─ package.json
├─ pnpm-workspace.yaml
├─ tsconfig.base.json
├─ eslint.config.js
├─ prettier.config.js
├─ IMPLEMENTATION_PLAN.md
└─ README.md
```

Use a monorepo managed with `pnpm`.

---

# 6. Domain Model

## 6.1 Project

A project is the top-level serializable document.

```ts
interface MotionProject {
  schemaVersion: string;
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;

  settings: ProjectSettings;
  theme: ThemeReference;
  variables: Record<string, VariableDefinition>;
  assets: AssetReference[];
  scenes: Scene[];
  audioTracks: AudioTrack[];
  metadata?: Record<string, unknown>;
}
```

## 6.2 Project settings

```ts
interface ProjectSettings {
  width: number;
  height: number;
  fps: number;
  durationMode: "scenes" | "fixed";
  fixedDuration?: number;
  backgroundColor: string;
  pixelRatio: number;
  safeArea?: SafeAreaSettings;
}
```

Default:

```json
{
  "width": 1080,
  "height": 1920,
  "fps": 30,
  "durationMode": "scenes",
  "backgroundColor": "#000000",
  "pixelRatio": 1
}
```

## 6.3 Scene

```ts
interface Scene {
  id: string;
  name: string;
  duration: number;
  background: BackgroundDefinition;
  elements: MotionElement[];
  transitionIn?: TransitionDefinition;
  transitionOut?: TransitionDefinition;
  metadata?: Record<string, unknown>;
}
```

Scenes are sequential by default.

Global timeline time is calculated from accumulated scene durations.

## 6.4 Motion element

```ts
interface MotionElement {
  id: string;
  type: string;
  name: string;
  visible: boolean;
  locked: boolean;

  transform: Transform2D;
  style: ElementStyle;
  props: Record<string, unknown>;

  timing: ElementTiming;
  animations: AnimationDefinition[];
  bindings?: VariableBinding[];
  effects?: EffectDefinition[];

  children?: MotionElement[];
  metadata?: Record<string, unknown>;
}
```

## 6.5 Transform

```ts
interface Transform2D {
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
  scaleX: number;
  scaleY: number;
  anchorX: number;
  anchorY: number;
  skewX: number;
  skewY: number;
  opacity: number;
  zIndex: number;
}
```

Coordinates use project pixels.

Anchor uses normalized values from 0 to 1.

## 6.6 Element timing

```ts
interface ElementTiming {
  start: number;
  duration: number;
  trimStart?: number;
  trimEnd?: number;
  playbackRate?: number;
}
```

Timing is relative to scene start unless explicitly documented otherwise.

## 6.7 Assets

```ts
type AssetType =
  | "image"
  | "video"
  | "audio"
  | "svg"
  | "font"
  | "json"
  | "unknown";

interface AssetReference {
  id: string;
  type: AssetType;
  name: string;
  source: AssetSource;
  mimeType?: string;
  width?: number;
  height?: number;
  duration?: number;
  checksum?: string;
  metadata?: Record<string, unknown>;
}

type AssetSource =
  | { kind: "local-path"; path: string }
  | { kind: "object-url"; key: string }
  | { kind: "data-url"; value: string }
  | { kind: "remote-url"; url: string }
  | { kind: "generated"; generatorId: string; params: unknown };
```

Remote assets must be resolved and cached before deterministic export.

---

# 7. JSON Schema Requirements

Create a formal JSON Schema file.

Required file:

```text
packages/schemas/project.schema.json
```

Requirements:

- Draft 2020-12
- strict validation
- explicit required fields
- no unknown top-level fields unless metadata is used
- discriminated unions for element types
- discriminated unions for animation types
- version field required
- reusable `$defs`
- human-readable validation messages where possible

Also create Zod schemas that mirror the JSON Schema.

Validation flow:

```text
raw JSON
→ parse
→ schema validate
→ migrate
→ validate migrated data
→ normalize defaults
→ load editor
```

Never silently discard invalid data.

Show validation errors with:

- JSON path
- expected type
- actual value
- suggested fix

---

# 8. Component System

## 8.1 Component definition

Every component type must be registered.

```ts
interface ComponentDefinition<TProps> {
  type: string;
  displayName: string;
  category: string;
  icon?: string;

  propsSchema: ZodSchema<TProps>;
  defaultProps: TProps;
  defaultTransform: Partial<Transform2D>;

  render: ComponentRenderer<TProps>;
  inspector: InspectorDefinition<TProps>;

  migrateProps?: (
    oldProps: unknown,
    fromVersion: string
  ) => TProps;
}
```

## 8.2 Component registry

```ts
interface ComponentRegistry {
  register(definition: ComponentDefinition<unknown>): void;
  unregister(type: string): void;
  get(type: string): ComponentDefinition<unknown>;
  list(): ComponentDefinition<unknown>[];
  listByCategory(category: string): ComponentDefinition<unknown>[];
}
```

Unknown components must render as visible placeholders rather than crash the project.

## 8.3 Required MVP components

### Text

- BigTitle
- Subtitle
- Caption
- Paragraph
- CounterText
- TypewriterText
- Label
- HandwrittenLabel

### Shape and layout

- Rectangle
- RoundedRectangle
- Circle
- Line
- Arrow
- Pointer
- Divider
- Badge
- Panel
- Group
- StackLayout
- GridLayout

### Media

- Image
- Video
- Logo
- SVGIcon
- BackgroundImage
- ImageCard
- ProductCard

### Social and UI

- YouTubeComment
- YouTubeThumbnail
- SubscribeButton
- LikeButton
- Notification
- ChatBubble
- PhoneFrame
- BrowserFrame
- ProfileCard

### Storytelling

- Character
- SpeechBubble
- ThoughtBubble
- TopicCircle
- FactCard
- QuoteCard
- TimelineCard
- NewsCard
- ComparisonCard

### Finance

- CompanyCard
- StockCard
- DividendCard
- PriceBadge
- KPIGrid
- PortfolioAllocation
- ReturnSummary
- RetirementScenarioCard

### Charts

- BarChart
- HorizontalBarChart
- LineChart
- AreaChart
- PieChart
- DonutChart
- Heatmap
- ProgressBar
- Counter
- Table
- ComparisonTable

## 8.4 Component lifecycle

Each rendered component must support:

```ts
interface RenderedComponent {
  mount(context: RenderContext): void;
  update(element: MotionElement, time: number): void;
  unmount(): void;
  getBounds(): Rect;
}
```

Do not store the source of truth inside the rendered component.

---

# 9. Variables and Template Binding

The variable system is a core feature.

## 9.1 Variable definition

```ts
interface VariableDefinition {
  id: string;
  name: string;
  type:
    | "string"
    | "number"
    | "boolean"
    | "color"
    | "date"
    | "imageAsset"
    | "videoAsset"
    | "audioAsset"
    | "json";
  value: unknown;
  defaultValue?: unknown;
  description?: string;
}
```

## 9.2 Binding

```ts
interface VariableBinding {
  variableId: string;
  targetPath: string;
  transform?: BindingTransform;
}
```

Examples:

```json
{
  "variableId": "company_name",
  "targetPath": "props.title"
}
```

```json
{
  "variableId": "dividend_yield",
  "targetPath": "props.value",
  "transform": {
    "type": "format-number",
    "format": "0.0%"
  }
}
```

## 9.3 Binding requirements

- bindings update immediately in the editor
- circular bindings are rejected
- invalid target paths show warnings
- variable changes must be undoable
- templates may mark variables as required
- variables may be grouped into forms
- variables must support preview values
- variables may bind to multiple components

---

# 10. Theme Engine

## 10.1 Theme model

```ts
interface Theme {
  id: string;
  name: string;
  tokens: {
    colors: Record<string, string>;
    typography: Record<string, TypographyToken>;
    spacing: Record<string, number>;
    radii: Record<string, number>;
    shadows: Record<string, ShadowToken>;
    strokes: Record<string, StrokeToken>;
    chartPalette: string[];
  };
  componentOverrides?: Record<string, unknown>;
}
```

## 10.2 Initial themes

- Minimal Light
- Minimal Dark
- Finance Yellow
- Corporate Blue
- News Red
- Retro Vintage
- High Contrast
- Clean White
- Black Background Product
- Documentary Beige

## 10.3 Theme behavior

Changing a theme must:

- update bound theme tokens
- preserve manual overrides
- optionally allow reset to theme defaults
- update charts
- update typography
- update component chrome
- remain undoable

Do not replace literal values that were intentionally customized.

---

# 11. Editor Layout

Default desktop layout:

```text
┌───────────────────────────────────────────────────────────────┐
│ Top toolbar                                                   │
├───────────────┬────────────────────────────┬──────────────────┤
│ Assets /      │                            │ Inspector        │
│ Components /  │        Canvas              │ Properties       │
│ Hierarchy     │                            │                  │
│               │                            │                  │
├───────────────┴────────────────────────────┴──────────────────┤
│ Timeline                                                      │
└───────────────────────────────────────────────────────────────┘
```

## 11.1 Top toolbar

Include:

- project name
- save status
- undo
- redo
- zoom
- play
- pause
- stop
- current time
- FPS selector
- preview quality
- export
- settings

## 11.2 Left panel tabs

- Scenes
- Hierarchy
- Components
- Assets
- Templates
- Variables
- Plugins

## 11.3 Right inspector

Sections:

- General
- Transform
- Layout
- Appearance
- Typography
- Content
- Animation
- Effects
- Timing
- Bindings
- Accessibility
- Advanced

Use collapsible sections.

## 11.4 Bottom timeline

- ruler
- playhead
- scene segments
- tracks
- clips
- keyframes
- zoom
- horizontal scrolling
- snapping
- markers
- audio waveform
- selected element highlighting

---

# 12. Canvas Editor

## 12.1 Canvas requirements

- render project at correct aspect ratio
- scale to viewport
- zoom from 10% to 400%
- pan
- checkerboard transparency option
- safe zones
- center guides
- rule-of-thirds guides
- custom guides
- grid
- snap
- rulers
- current frame indicator
- preview resolution selector

## 12.2 Selection

Support:

- single select
- multi-select
- marquee selection
- hierarchy selection
- alt-click cycling through overlapping elements
- lock state
- hidden state
- select parent
- select child

## 12.3 Transform controls

Support:

- move
- resize
- rotate
- scale
- anchor editing
- aspect ratio lock
- keyboard nudging
- 1 px step
- 10 px step with modifier
- snap to guides
- snap to sibling edges
- snap to centers
- equal spacing suggestions

## 12.4 Smart guides

Show guides for:

- horizontal center
- vertical center
- equal gap
- same width
- same height
- aligned edges
- aligned baselines
- safe area boundary
- canvas boundary

Snapping tolerance must be configurable.

## 12.5 Context menu

Include:

- cut
- copy
- paste
- duplicate
- delete
- group
- ungroup
- lock
- hide
- bring forward
- bring to front
- send backward
- send to back
- align
- distribute
- add animation
- create component preset

---

# 13. Hierarchy and Scene Management

## 13.1 Hierarchy tree

Each scene displays:

- groups
- elements
- nested elements
- visibility
- lock state
- component icon
- animation indicator
- binding indicator
- warning indicator

Support drag-and-drop reordering.

## 13.2 Scene actions

- add
- duplicate
- rename
- delete
- reorder
- split
- merge
- save as template
- change duration
- apply transition

## 13.3 Scene transitions

Initial transition types:

- cut
- fade
- slide
- push
- zoom
- wipe
- blur fade
- dip to black
- dip to white

Transitions must be deterministic and previewable at arbitrary timestamps.

---

# 14. Timeline Model

## 14.1 Core requirements

Timeline evaluation must not depend on real-time playback.

At any timestamp:

```ts
evaluateProjectAtTime(project, globalTime)
```

must return the visual state.

## 14.2 Timeline coordinate systems

Support:

- global project time
- scene-local time
- element-local time
- source media time

All conversions must be explicit and tested.

## 14.3 Tracks

Initial track types:

- visual element
- group
- audio
- subtitle
- camera
- marker
- scene transition

## 14.4 Clip operations

- drag
- trim start
- trim end
- slip source
- stretch duration
- duplicate
- split
- delete
- ripple move
- snap
- move between layers

## 14.5 Keyframes

Keyframeable properties:

- x
- y
- width
- height
- rotation
- scale
- opacity
- color
- blur
- border radius
- text reveal progress
- chart progress
- numeric value
- custom component properties

## 14.6 Keyframe model

```ts
interface Keyframe<T> {
  id: string;
  time: number;
  value: T;
  easing: EasingDefinition;
  interpolation: "linear" | "step" | "bezier" | "spring";
}
```

## 14.7 Easing

Support:

- linear
- ease
- ease-in
- ease-out
- ease-in-out
- cubic bezier
- bounce
- elastic
- back
- spring

Spring settings:

- mass
- stiffness
- damping
- initial velocity

---

# 15. Animation Engine

## 15.1 Animation types

Support both:

1. preset animations
2. property keyframes

## 15.2 Initial entrance presets

- Fade In
- Pop In
- Scale In
- Zoom In
- Slide Left
- Slide Right
- Slide Up
- Slide Down
- Bounce In
- Elastic In
- Rotate In
- Flip In
- Blur In
- Wipe In
- Typewriter
- Counter Up
- Draw Line
- Chart Reveal

## 15.3 Initial exit presets

- Fade Out
- Pop Out
- Scale Out
- Zoom Out
- Slide Left Out
- Slide Right Out
- Slide Up Out
- Slide Down Out
- Blur Out
- Wipe Out

## 15.4 Loop presets

- Float
- Pulse
- Blink
- Shake
- Wiggle
- Breathe
- Rotate
- Glow
- Bounce
- Bob

## 15.5 Animation definition

```ts
interface AnimationDefinition {
  id: string;
  kind: "preset" | "keyframes";
  target: string;
  start: number;
  duration: number;
  delay?: number;
  presetId?: string;
  params?: Record<string, unknown>;
  keyframes?: Keyframe<unknown>[];
  loop?: {
    enabled: boolean;
    count?: number;
    direction?: "normal" | "alternate";
  };
}
```

## 15.6 Animation requirements

- arbitrary time evaluation
- no stateful dependency on previous frames
- deterministic
- composable
- conflict resolution when multiple animations target same property
- preview/export parity
- reusable presets
- user-created presets
- animation preset versioning

---

# 16. Audio and Subtitle System

## 16.1 Audio tracks

Support:

- voiceover
- background music
- sound effects
- imported video audio
- multiple tracks

Properties:

- start
- duration
- trim
- volume
- mute
- fade in
- fade out
- playback rate
- ducking group

## 16.2 Waveforms

Generate and cache waveform summaries.

Do not decode the full audio file repeatedly.

## 16.3 Subtitles

Support:

- manual subtitles
- SRT import
- WebVTT import
- JSON subtitle format
- word-level timestamps
- sentence-level timestamps
- style presets
- karaoke highlight
- emphasized word
- line wrapping rules
- safe-area positioning

Subtitle components must be ordinary project elements backed by subtitle data.

---

# 17. Asset Manager

## 17.1 Asset panel

Categories:

- images
- videos
- audio
- SVG icons
- logos
- characters
- backgrounds
- templates
- generated assets
- recent
- favorites

## 17.2 Asset import

Support:

- drag and drop
- file picker
- paste from clipboard
- remote URL import
- directory import where supported

## 17.3 Asset metadata

Extract:

- dimensions
- duration
- MIME type
- file size
- checksum
- thumbnail
- waveform
- codec information where available

## 17.4 Asset handling

- deduplicate by checksum
- preserve original asset
- generate proxies when necessary
- show missing asset warnings
- allow relinking
- avoid base64 embedding for large files by default
- support portable project bundles

---

# 18. Template System

## 18.1 Template categories

- Biography Story
- Company Story
- Dividend Story
- Retirement Scenario
- ETF Comparison
- Stock Crash
- Historical Timeline
- Product Explainer
- News Summary
- Comment Response
- Social Proof
- Before and After
- Top Five List
- Myth vs Fact

## 18.2 Template package

```ts
interface MotionTemplate {
  id: string;
  name: string;
  description: string;
  thumbnailAssetId?: string;
  category: string;
  project: MotionProject;
  variableForm: VariableFormDefinition;
  requiredPlugins?: string[];
}
```

## 18.3 Template behavior

- templates are immutable originals
- creating from template makes a new project
- variable form is generated automatically
- unresolved required variables block final export
- optional variables use defaults
- asset placeholders are visible
- theme selection can be changed

---

# 19. Plugin System

## 19.1 Goals

Plugins may contribute:

- component types
- inspector controls
- templates
- themes
- animation presets
- importers
- exporters
- asset providers
- validators
- commands

## 19.2 Plugin manifest

```json
{
  "id": "stock-charts",
  "name": "Stock Charts",
  "version": "1.0.0",
  "engine": {
    "minimumVersion": "1.0.0"
  },
  "entry": "./dist/index.js",
  "permissions": [
    "register-components",
    "register-inspector-controls"
  ]
}
```

## 19.3 Security

Initially, only trusted local plugins are supported.

Future untrusted plugins require sandboxing.

Do not allow arbitrary remote scripts by default.

## 19.4 Plugin API

```ts
interface MotionStudioPlugin {
  activate(api: PluginAPI): void | Promise<void>;
  deactivate?(): void | Promise<void>;
}
```

Plugin registration must be reversible.

---

# 20. Command and History Architecture

All editor modifications must use commands.

```ts
interface EditorCommand {
  id: string;
  label: string;
  execute(context: EditorContext): void;
  undo(context: EditorContext): void;
  mergeWith?(next: EditorCommand): EditorCommand | null;
}
```

Required commands:

- AddElementCommand
- DeleteElementCommand
- UpdateElementCommand
- MoveElementCommand
- ResizeElementCommand
- ReorderElementCommand
- AddSceneCommand
- DeleteSceneCommand
- UpdateSceneCommand
- AddKeyframeCommand
- UpdateKeyframeCommand
- RemoveKeyframeCommand
- ChangeVariableCommand
- ChangeThemeCommand

History requirements:

- undo
- redo
- command coalescing for continuous drag
- configurable maximum history
- history reset after project load
- dirty state tracking

---

# 21. State Management

Use separate stores or slices for:

- project data
- editor UI
- selection
- playback
- timeline viewport
- asset library
- history
- export jobs
- notifications
- plugin registry

Do not mix temporary UI state into saved project JSON.

Saved project state must be serializable without functions or DOM references.

---

# 22. Playback Engine

## 22.1 Playback states

- stopped
- playing
- paused
- scrubbing
- rendering

## 22.2 Playback requirements

- use high-resolution timestamps
- support frame stepping
- support loop range
- support scene loop
- support playback rate
- drop preview frames when necessary
- never change logical timeline time based on dropped frames
- display current frame number
- display performance warnings

## 22.3 Preview quality

Options:

- full
- half
- quarter
- auto

Preview quality must not alter project coordinates.

---

# 23. Deterministic Rendering

This is a critical architectural requirement.

The renderer must support:

```ts
interface FrameRenderer {
  initialize(project: MotionProject): Promise<void>;
  renderFrame(timeSeconds: number): Promise<RenderedFrame>;
  dispose(): Promise<void>;
}
```

A frame rendered at time `t` must not depend on whether `t - 1 frame` was rendered first.

Avoid:

- random values without seeds
- stateful CSS animations
- `setTimeout`-driven element state
- mutation-based animation accumulation
- clock-dependent particle states
- network-dependent assets during final rendering

Random effects must use seeded randomness.

---

# 24. MP4 Export Pipeline

## 24.1 Required first implementation

Export H.264 MP4 with:

- 1080 × 1920
- 30 FPS
- configurable CRF
- configurable preset
- AAC audio
- yuv420p
- faststart

## 24.2 Rendering strategies

Implement strategy abstraction:

```ts
interface VideoExportStrategy {
  export(
    project: MotionProject,
    options: ExportOptions,
    progress: ExportProgressCallback
  ): Promise<ExportResult>;
}
```

Initial strategy:

1. launch Playwright Chromium
2. open dedicated render route
3. load project JSON
4. wait for all assets and fonts
5. render each frame deterministically
6. capture PNG or raw bitmap
7. pipe frames to FFmpeg
8. mix audio
9. finalize MP4
10. produce render report

## 24.3 Render report

Include:

- project ID
- schema version
- output path
- resolution
- FPS
- duration
- codec
- bitrate or CRF
- render duration
- missing asset warnings
- font fallback warnings
- dropped or failed frame count
- FFmpeg command
- application version

## 24.4 Export cancellation

Export jobs must support cancellation and cleanup.

Partial files should be removed or clearly marked.

## 24.5 Additional exports

- PNG current frame
- PNG frame sequence
- transparent WebM where supported
- GIF preview
- JSON
- portable project bundle
- standalone HTML preview

---

# 25. AI Integration

## 25.1 Principle

AI does not modify rendered nodes.

AI produces:

- project JSON
- scene plans
- component commands
- variable values
- asset requests

All AI output must be validated.

## 25.2 AI request model

```ts
interface AIGenerationRequest {
  prompt: string;
  targetDuration?: number;
  targetTemplateId?: string;
  themeId?: string;
  script?: string;
  availableAssets?: AssetSummary[];
  constraints?: {
    maxScenes?: number;
    allowedComponentTypes?: string[];
    language?: string;
  };
}
```

## 25.3 AI response model

```ts
interface AIGenerationResponse {
  projectDraft: unknown;
  assetRequests: AssetRequest[];
  warnings: string[];
  explanation?: string;
}
```

## 25.4 Validation

Flow:

```text
AI response
→ JSON parsing
→ schema validation
→ reference validation
→ asset validation
→ normalization
→ preview import
```

Invalid output must not corrupt the current project.

## 25.5 AI edit commands

Future AI editing should use structured commands:

```json
{
  "type": "update-element",
  "elementId": "title-1",
  "patch": {
    "props.text": "새로운 제목"
  }
}
```

Each AI edit should produce a reviewable diff.

## 25.6 Prompting constraints

The AI system should know:

- available component registry
- project schema
- theme tokens
- template variables
- allowed animation presets
- asset IDs
- project duration constraints

Do not send entire binary assets to the LLM.

---

# 26. Existing HTML Template Integration

The application must support gradual integration with an existing HTML-based YouTube video template.

## 26.1 Adapter approach

Create:

```ts
interface LegacyTemplateAdapter {
  detect(input: string): DetectionResult;
  import(input: string): Promise<LegacyImportResult>;
  export?(project: MotionProject): Promise<string>;
}
```

## 26.2 Import expectations

The importer may identify:

- canvas dimensions
- background layers
- static text
- images
- videos
- CSS positioning
- known animation names
- scene containers
- subtitle regions

Unsupported logic must be listed in a migration report.

## 26.3 Integration strategy

Do not rewrite the user's existing template immediately.

Use this sequence:

1. isolate reusable project data
2. wrap existing renderer
3. introduce component registry
4. move scenes into JSON
5. replace timing logic
6. introduce visual editor
7. replace legacy components incrementally
8. preserve export compatibility until migration completes

---

# 27. UI Design System

## 27.1 Editor appearance

Default:

- dark interface
- high contrast
- neutral gray panels
- compact spacing
- clear selected-state accent
- readable typography
- minimal decorative effects

## 27.2 Tokens

Define:

- panel background
- elevated panel
- input background
- border
- primary text
- secondary text
- accent
- warning
- error
- success
- selection
- timeline playhead
- clip colors by type

## 27.3 Accessibility

- keyboard navigation
- focus states
- contrast-compliant text
- tooltips
- accessible labels
- reduced motion setting for editor UI
- screen-reader names for controls

The exported video itself may use intentionally stylized visual designs.

---

# 28. Keyboard Shortcuts

Required:

| Action | Shortcut |
|---|---|
| Undo | Ctrl/Cmd + Z |
| Redo | Ctrl/Cmd + Shift + Z |
| Copy | Ctrl/Cmd + C |
| Paste | Ctrl/Cmd + V |
| Duplicate | Ctrl/Cmd + D |
| Delete | Delete / Backspace |
| Save | Ctrl/Cmd + S |
| Select all | Ctrl/Cmd + A |
| Group | Ctrl/Cmd + G |
| Ungroup | Ctrl/Cmd + Shift + G |
| Play/Pause | Space |
| Stop | Shift + Space |
| Previous frame | Left Arrow |
| Next frame | Right Arrow |
| Move 1 px | Arrow key |
| Move 10 px | Shift + Arrow |
| Zoom in | Ctrl/Cmd + Plus |
| Zoom out | Ctrl/Cmd + Minus |
| Fit canvas | Ctrl/Cmd + 0 |

Keyboard shortcuts must not trigger while typing inside text inputs unless explicitly appropriate.

---

# 29. Persistence and Autosave

## 29.1 Autosave

- debounce changes
- save to IndexedDB
- maintain recovery snapshots
- display saving/saved status
- recover after browser crash
- do not overwrite imported file without explicit user action

## 29.2 Project file

Suggested extension:

```text
.motion.json
```

Portable bundle:

```text
.motionpkg
```

A portable bundle may be a ZIP containing:

```text
project.json
assets/
fonts/
manifest.json
```

## 29.3 Migration

Every project has `schemaVersion`.

Create migrations:

```ts
interface ProjectMigration {
  from: string;
  to: string;
  migrate(project: unknown): unknown;
}
```

Migrations must be:

- ordered
- tested
- non-destructive where possible
- logged
- idempotent when practical

---

# 30. Error Handling

Use typed errors.

Examples:

- ProjectValidationError
- AssetNotFoundError
- UnsupportedComponentError
- RenderInitializationError
- FrameRenderError
- ExportCancelledError
- PluginActivationError
- MigrationError

User-facing errors must include:

- what failed
- probable cause
- suggested action
- technical details toggle

Do not expose raw stack traces by default.

---

# 31. Logging and Diagnostics

Create a diagnostic logger with levels:

- debug
- info
- warn
- error

Include contextual metadata:

- project ID
- scene ID
- element ID
- plugin ID
- export job ID
- frame number

Provide a diagnostics export file.

---

# 32. Performance Requirements

Initial targets on a modern desktop:

- editor UI interaction under 100 ms
- transform feedback under 16 ms where possible
- 60 FPS preview for moderate scenes
- responsive timeline with 1,000 clips
- project load under 3 seconds for ordinary projects
- no full-project rerender for simple inspector changes
- virtualization for large hierarchy and asset lists
- waveform and thumbnails cached
- lazy-load heavy plugins and components

## 32.1 Performance architecture

- dirty-region or dirty-node updates
- memoized component render inputs
- pooled graphics where useful
- texture caching
- asset reference counting
- batched state updates
- avoid unnecessary React rerenders
- worker-based heavy computations
- Web Worker for waveform generation
- optional worker for schema validation on large projects

---

# 33. Testing Strategy

## 33.1 Unit tests

Test:

- schema validation
- migrations
- time conversion
- easing functions
- keyframe interpolation
- scene duration calculation
- variable binding
- command undo/redo
- component registry
- plugin registry
- export option validation

## 33.2 Integration tests

Test:

- create project
- add scene
- add element
- edit inspector
- save JSON
- reload JSON
- preserve output
- apply animation
- scrub timeline
- import asset
- resolve missing asset
- run migration

## 33.3 Visual regression tests

For fixed example projects:

- render specific frames
- compare screenshots
- allow small tolerance
- store golden images
- test text fallback and chart rendering

## 33.4 End-to-end tests

Use Playwright.

Required flows:

- create and save project
- load sample project
- edit title
- move element
- undo
- redo
- add animation
- export PNG
- launch MP4 render job
- cancel export
- recover autosave

---

# 34. Coding Standards

## 34.1 TypeScript

- strict mode
- no implicit `any`
- avoid type assertions
- discriminated unions
- immutable updates for project state
- exhaustive switches for element and command types
- public APIs documented

## 34.2 Functions and classes

- single responsibility
- dependency injection for services
- avoid large god classes
- avoid deep inheritance
- prefer composition
- keep renderer adapters isolated

## 34.3 React

- components should not own domain state
- domain mutations go through commands
- avoid giant context providers
- use selectors to reduce rerenders
- separate presentation and orchestration
- no direct DOM mutation except controlled canvas/editor adapters

## 34.4 Styling

- use CSS variables for editor theme
- use CSS modules or a consistent scoped approach
- no random inline style strings for editor chrome
- project element styles are data-driven and may be applied dynamically

## 34.5 Documentation

Every package must have a README containing:

- purpose
- public API
- architecture notes
- examples
- testing instructions

---

# 35. Security

- sanitize imported HTML and SVG
- reject script tags in SVG
- do not execute project-supplied JavaScript
- validate remote URLs
- display CORS errors clearly
- restrict plugin permissions
- avoid arbitrary shell command construction
- escape FFmpeg arguments
- use temporary directories safely
- do not expose local file paths in shared project exports unless requested

---

# 36. Development Roadmap

## Milestone 0 — Repository Foundation

Deliver:

- pnpm monorepo
- Vite editor app
- TypeScript strict mode
- lint
- format
- test setup
- CI
- basic documentation
- sample project

Acceptance criteria:

- `pnpm install`
- `pnpm dev`
- `pnpm build`
- `pnpm test`
- all succeed

## Milestone 1 — Core Project Model

Deliver:

- project interfaces
- Zod schema
- JSON Schema
- validation
- normalization
- migrations framework
- sample project files

Acceptance criteria:

- invalid projects produce useful errors
- valid projects round-trip without data loss
- migration tests pass

## Milestone 2 — Renderer Foundation

Deliver:

- renderer interface
- Pixi renderer
- render context
- component registry
- basic element transforms
- deterministic `renderAtTime`

Initial components:

- rectangle
- circle
- text
- image
- group

Acceptance criteria:

- same time produces same frame
- sample scene renders correctly
- visual regression tests pass

## Milestone 3 — Editor Shell

Deliver:

- top toolbar
- left panel
- inspector
- center canvas
- timeline placeholder
- dark UI theme
- project load/save

Acceptance criteria:

- project opens
- components render
- inspector selection works
- JSON save and reload preserves project

## Milestone 4 — Canvas Interaction

Deliver:

- selection
- drag
- resize
- rotate
- multi-select
- guides
- snapping
- hierarchy synchronization
- keyboard movement

Acceptance criteria:

- transformations are command-driven
- undo/redo works
- canvas and inspector remain synchronized

## Milestone 5 — Timeline and Playback

Deliver:

- scene timeline
- element clips
- playhead
- playback
- scrubbing
- trimming
- snapping
- global/scene-local time conversion

Acceptance criteria:

- arbitrary timestamp preview works
- clips can be moved and trimmed
- playback matches scrubbed frames

## Milestone 6 — Animation

Deliver:

- keyframes
- easing
- entrance/exit presets
- animation inspector
- animation timeline indicators

Acceptance criteria:

- animation is deterministic
- presets can be converted or represented as editable data
- visual tests cover multiple timestamps

## Milestone 7 — Production Components

Deliver first large component pack:

- profile card
- character
- speech bubble
- title
- caption
- image card
- YouTube comment
- phone frame
- bar chart
- line chart
- table
- topic circle
- notification

Acceptance criteria:

- each component has schema, renderer, inspector, defaults, tests
- unknown props do not crash the editor

## Milestone 8 — Variables, Themes, Templates

Deliver:

- variable manager
- bindings
- theme engine
- template package
- template variable form
- starter templates

Acceptance criteria:

- replacing company name updates all bound elements
- changing theme updates token-bound components
- template produces a new independent project

## Milestone 9 — Audio and Subtitles

Deliver:

- audio tracks
- waveform
- preview playback
- subtitle import
- subtitle styling
- voiceover alignment

Acceptance criteria:

- audio remains synchronized during preview
- subtitle timing is correct
- SRT round-trip is tested

## Milestone 10 — MP4 Export

Deliver:

- renderer app or route
- Playwright frame capture
- FFmpeg encoding
- audio mixing
- progress reporting
- cancellation
- render report

Acceptance criteria:

- sample project exports a valid 1080 × 1920 MP4
- output duration matches project
- audio synchronization is within acceptable tolerance
- no missing frames

## Milestone 11 — Plugins

Deliver:

- plugin manifest
- plugin loader
- plugin SDK
- example plugin
- permission validation

Acceptance criteria:

- example plugin registers and removes a component
- incompatible version is rejected
- plugin error does not crash core editor

## Milestone 12 — AI Draft Integration

Deliver:

- AI adapter interface
- JSON import review
- validation report
- AI command diff
- asset request placeholders

Acceptance criteria:

- invalid AI output is rejected safely
- valid AI project loads as editable data
- user can approve or reject AI edits

---

# 37. First Implementation Slice

Claude Code should not attempt all milestones at once.

Implement this vertical slice first:

1. monorepo foundation
2. project schema
3. Pixi renderer
4. rectangle, text, image, profile card, speech bubble
5. editor shell
6. hierarchy
7. inspector
8. canvas selection, drag, resize
9. simple sequential scenes
10. play/pause/restart
11. JSON import/export
12. undo/redo
13. one sample vertical project
14. unit and visual tests
15. clear README

Do not implement MP4 rendering before deterministic `renderAtTime` is proven.

---

# 38. Sample Project JSON

```json
{
  "schemaVersion": "1.0.0",
  "id": "project-example-001",
  "name": "Ronald Read Example",
  "createdAt": "2026-07-27T00:00:00.000Z",
  "updatedAt": "2026-07-27T00:00:00.000Z",
  "settings": {
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "durationMode": "scenes",
    "backgroundColor": "#000000",
    "pixelRatio": 1
  },
  "theme": {
    "themeId": "finance-yellow"
  },
  "variables": {
    "person_name": {
      "id": "person_name",
      "name": "Person Name",
      "type": "string",
      "value": "Ronald Read"
    },
    "headline": {
      "id": "headline",
      "name": "Headline",
      "type": "string",
      "value": "아무도 그를 부자라고 생각하지 않았음."
    }
  },
  "assets": [],
  "audioTracks": [],
  "scenes": [
    {
      "id": "scene-1",
      "name": "Profile Introduction",
      "duration": 5,
      "background": {
        "type": "solid",
        "color": "#FFD000"
      },
      "elements": [
        {
          "id": "profile-card-1",
          "type": "profile-card",
          "name": "Profile Card",
          "visible": true,
          "locked": false,
          "transform": {
            "x": 140,
            "y": 600,
            "width": 800,
            "height": 300,
            "rotation": 0,
            "scaleX": 1,
            "scaleY": 1,
            "anchorX": 0.5,
            "anchorY": 0.5,
            "skewX": 0,
            "skewY": 0,
            "opacity": 1,
            "zIndex": 1
          },
          "style": {
            "backgroundColor": "#FFFFFF",
            "borderColor": "#111111",
            "borderWidth": 4,
            "borderRadius": 24
          },
          "props": {
            "title": "Ronald Read",
            "description": "평범한 직업으로 800만 달러를 모은 투자자"
          },
          "timing": {
            "start": 0,
            "duration": 5
          },
          "animations": [
            {
              "id": "animation-1",
              "kind": "preset",
              "target": "transform",
              "start": 0,
              "duration": 0.5,
              "presetId": "pop-in",
              "params": {
                "overshoot": 1.12
              }
            }
          ],
          "bindings": [
            {
              "variableId": "person_name",
              "targetPath": "props.title"
            }
          ]
        },
        {
          "id": "caption-1",
          "type": "caption",
          "name": "Bottom Caption",
          "visible": true,
          "locked": false,
          "transform": {
            "x": 540,
            "y": 1720,
            "width": 900,
            "height": 100,
            "rotation": 0,
            "scaleX": 1,
            "scaleY": 1,
            "anchorX": 0.5,
            "anchorY": 0.5,
            "skewX": 0,
            "skewY": 0,
            "opacity": 1,
            "zIndex": 10
          },
          "style": {
            "backgroundColor": "#111111DD",
            "color": "#FFFFFF",
            "borderRadius": 12
          },
          "props": {
            "text": "아무도 그를 부자라고 생각하지 않았음.",
            "fontSize": 46,
            "fontWeight": 800,
            "textAlign": "center"
          },
          "timing": {
            "start": 0,
            "duration": 5
          },
          "animations": [
            {
              "id": "animation-2",
              "kind": "preset",
              "target": "opacity",
              "start": 0.2,
              "duration": 0.4,
              "presetId": "fade-in"
            }
          ],
          "bindings": [
            {
              "variableId": "headline",
              "targetPath": "props.text"
            }
          ]
        }
      ]
    }
  ]
}
```

---

# 39. Definition of Done

A feature is not complete until:

- it is represented in the domain model
- it is serializable
- it has runtime validation
- it is editable through the GUI
- it supports undo and redo
- it renders in preview
- it renders deterministically at arbitrary time
- it has tests
- it has documentation
- it does not break existing sample projects
- errors are handled
- performance impact is considered

---

# 40. Final Directive to Claude Code

Build the application as an extensible professional motion graphics editor, not as a collection of demo pages.

Prioritize the following order:

1. correct domain model
2. deterministic timeline
3. renderer abstraction
4. editor command architecture
5. data validation and migrations
6. reusable component registry
7. visual editing
8. export
9. plugins
10. AI integration

When uncertain, choose the design that preserves:

- deterministic rendering
- serializable state
- modularity
- testability
- backward compatibility
- extensibility

At the end of each implementation phase, provide:

1. files created or changed
2. architecture decisions
3. commands to run
4. tests executed
5. known limitations
6. next recommended milestone

Do not claim completion if requirements remain unimplemented.
