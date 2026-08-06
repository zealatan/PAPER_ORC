/**
 * Zod schemas mirroring the JSON Schema in `@motion-studio/schemas` and the interfaces in
 * `./types.ts`. Zod is the in-app runtime validator (spec §7). Types remain authoritative in
 * `./types.ts`; the recursive element schema is annotated against {@link MotionElement} so the
 * two stay structurally aligned, and validation results are bridged to the domain types in
 * `./validate.ts`.
 */
import { z } from "zod";
import type { MotionElement, MotionProject } from "./types";

const semver = z
  .string()
  .regex(/^\d+\.\d+\.\d+$/, "must be a semantic version like 1.0.0");

const color = z.string().min(1, "must be a non-empty color string");

/** Open, data-driven bag of values (styles, props, metadata, params). */
const openRecord = z.record(z.unknown());

export const SafeAreaSettingsSchema = z
  .object({
    top: z.number().optional(),
    right: z.number().optional(),
    bottom: z.number().optional(),
    left: z.number().optional(),
  })
  .strict();

export const ProjectSettingsSchema = z
  .object({
    width: z.number().int().positive(),
    height: z.number().int().positive(),
    fps: z.number().positive(),
    durationMode: z.enum(["scenes", "fixed"]),
    fixedDuration: z.number().positive().optional(),
    backgroundColor: color,
    pixelRatio: z.number().positive(),
    safeArea: SafeAreaSettingsSchema.optional(),
  })
  .strict();

export const ThemeReferenceSchema = z
  .object({
    themeId: z.string().min(1),
    overrides: openRecord.optional(),
  })
  .strict();

export const VariableDefinitionSchema = z
  .object({
    id: z.string().min(1),
    name: z.string(),
    type: z.enum([
      "string",
      "number",
      "boolean",
      "color",
      "date",
      "imageAsset",
      "videoAsset",
      "audioAsset",
      "json",
    ]),
    value: z.unknown(),
    defaultValue: z.unknown().optional(),
    description: z.string().optional(),
    required: z.boolean().optional(),
    group: z.string().optional(),
  })
  .strict();

export const AssetSourceSchema = z.discriminatedUnion("kind", [
  z.object({ kind: z.literal("local-path"), path: z.string() }).strict(),
  z.object({ kind: z.literal("object-url"), key: z.string() }).strict(),
  z.object({ kind: z.literal("data-url"), value: z.string() }).strict(),
  z.object({ kind: z.literal("remote-url"), url: z.string() }).strict(),
  z
    .object({
      kind: z.literal("generated"),
      generatorId: z.string(),
      params: z.unknown().optional(),
    })
    .strict(),
]);

export const AssetReferenceSchema = z
  .object({
    id: z.string().min(1),
    type: z.enum(["image", "video", "audio", "svg", "font", "json", "unknown"]),
    name: z.string(),
    source: AssetSourceSchema,
    mimeType: z.string().optional(),
    width: z.number().optional(),
    height: z.number().optional(),
    duration: z.number().optional(),
    checksum: z.string().optional(),
    metadata: openRecord.optional(),
  })
  .strict();

export const AudioTrackSchema = z
  .object({
    id: z.string().min(1),
    kind: z.enum(["voiceover", "music", "sfx", "video-audio"]),
    assetId: z.string(),
    start: z.number().min(0),
    duration: z.number().min(0),
    trimStart: z.number().min(0).optional(),
    trimEnd: z.number().min(0).optional(),
    volume: z.number().min(0).optional(),
    muted: z.boolean().optional(),
    fadeIn: z.number().min(0).optional(),
    fadeOut: z.number().min(0).optional(),
    playbackRate: z.number().positive().optional(),
    duckingGroup: z.string().optional(),
  })
  .strict();

export const BackgroundDefinitionSchema = z.discriminatedUnion("type", [
  z.object({ type: z.literal("none") }).strict(),
  z.object({ type: z.literal("solid"), color }).strict(),
  z
    .object({
      type: z.literal("gradient"),
      angle: z.number().optional(),
      stops: z
        .array(z.object({ color, position: z.number().min(0).max(1) }).strict())
        .min(2),
    })
    .strict(),
  z
    .object({
      type: z.literal("image"),
      assetId: z.string(),
      fit: z.enum(["cover", "contain", "fill", "none"]).optional(),
    })
    .strict(),
  z
    .object({
      type: z.literal("video"),
      assetId: z.string(),
      fit: z.enum(["cover", "contain", "fill", "none"]).optional(),
      loop: z.boolean().optional(),
    })
    .strict(),
]);

export const TransitionDefinitionSchema = z
  .object({
    type: z.enum([
      "cut",
      "fade",
      "slide",
      "push",
      "zoom",
      "wipe",
      "blur-fade",
      "dip-to-black",
      "dip-to-white",
    ]),
    duration: z.number().min(0),
    params: openRecord.optional(),
  })
  .strict();

export const Transform2DSchema = z
  .object({
    x: z.number(),
    y: z.number(),
    width: z.number(),
    height: z.number(),
    rotation: z.number(),
    scaleX: z.number(),
    scaleY: z.number(),
    anchorX: z.number().min(0).max(1),
    anchorY: z.number().min(0).max(1),
    skewX: z.number(),
    skewY: z.number(),
    opacity: z.number().min(0).max(1),
    zIndex: z.number(),
  })
  .strict();

export const ElementTimingSchema = z
  .object({
    start: z.number().min(0),
    duration: z.number().min(0),
    trimStart: z.number().min(0).optional(),
    trimEnd: z.number().min(0).optional(),
    playbackRate: z.number().positive().optional(),
  })
  .strict();

export const VariableBindingSchema = z
  .object({
    variableId: z.string(),
    targetPath: z.string(),
    transform: z.object({ type: z.string() }).catchall(z.unknown()).optional(),
  })
  .strict();

export const EffectDefinitionSchema = z
  .object({
    id: z.string(),
    type: z.string(),
    params: openRecord.optional(),
    enabled: z.boolean().optional(),
  })
  .strict();

export const EasingDefinitionSchema = z
  .object({
    type: z.enum([
      "linear",
      "ease",
      "ease-in",
      "ease-out",
      "ease-in-out",
      "cubic-bezier",
      "bounce",
      "elastic",
      "back",
      "spring",
    ]),
    bezier: z.tuple([z.number(), z.number(), z.number(), z.number()]).optional(),
    spring: z
      .object({
        mass: z.number().optional(),
        stiffness: z.number().optional(),
        damping: z.number().optional(),
        initialVelocity: z.number().optional(),
      })
      .strict()
      .optional(),
  })
  .strict();

export const KeyframeSchema = z
  .object({
    id: z.string().min(1),
    time: z.number().min(0),
    value: z.unknown(),
    easing: EasingDefinitionSchema,
    interpolation: z.enum(["linear", "step", "bezier", "spring"]),
  })
  .strict();

export const AnimationLoopSchema = z
  .object({
    enabled: z.boolean(),
    count: z.number().int().min(0).optional(),
    direction: z.enum(["normal", "alternate"]).optional(),
  })
  .strict();

export const AnimationDefinitionSchema = z.discriminatedUnion("kind", [
  z
    .object({
      id: z.string().min(1),
      kind: z.literal("preset"),
      target: z.string(),
      start: z.number().min(0),
      duration: z.number().min(0),
      delay: z.number().min(0).optional(),
      presetId: z.string().min(1),
      params: openRecord.optional(),
      loop: AnimationLoopSchema.optional(),
    })
    .strict(),
  z
    .object({
      id: z.string().min(1),
      kind: z.literal("keyframes"),
      target: z.string(),
      start: z.number().min(0),
      duration: z.number().min(0),
      delay: z.number().min(0).optional(),
      keyframes: z.array(KeyframeSchema),
      loop: AnimationLoopSchema.optional(),
    })
    .strict(),
]);

/**
 * Recursive element schema. Annotated against {@link MotionElement} to break the type cycle and
 * keep the schema and the interface in the same shape.
 */
export const MotionElementSchema: z.ZodType<MotionElement> = z.lazy(
  () =>
    z
      .object({
        id: z.string().min(1),
        type: z.string().min(1),
        name: z.string(),
        visible: z.boolean(),
        locked: z.boolean(),
        transform: Transform2DSchema,
        style: openRecord,
        props: openRecord,
        timing: ElementTimingSchema,
        animations: z.array(AnimationDefinitionSchema),
        bindings: z.array(VariableBindingSchema).optional(),
        effects: z.array(EffectDefinitionSchema).optional(),
        children: z.array(MotionElementSchema).optional(),
        metadata: openRecord.optional(),
      })
      .strict(),
  // Cast to the authoritative interface: Zod infers `value?: unknown` for open keyframe values,
  // which is structurally looser than `Keyframe.value`. Runtime validation is unaffected.
) as unknown as z.ZodType<MotionElement>;

export const SceneSchema = z
  .object({
    id: z.string().min(1),
    name: z.string(),
    duration: z.number().positive(),
    background: BackgroundDefinitionSchema,
    elements: z.array(MotionElementSchema),
    transitionIn: TransitionDefinitionSchema.optional(),
    transitionOut: TransitionDefinitionSchema.optional(),
    metadata: openRecord.optional(),
  })
  .strict();

export const MotionProjectSchema = z
  .object({
    schemaVersion: semver,
    id: z.string().min(1),
    name: z.string(),
    createdAt: z.string(),
    updatedAt: z.string(),
    settings: ProjectSettingsSchema,
    theme: ThemeReferenceSchema,
    variables: z.record(VariableDefinitionSchema),
    assets: z.array(AssetReferenceSchema),
    scenes: z.array(SceneSchema),
    audioTracks: z.array(AudioTrackSchema),
    metadata: openRecord.optional(),
  })
  .strict();

/** Compile-time guarantee that the schema output is assignable to the domain type. */
export type MotionProjectSchemaOutput = z.infer<typeof MotionProjectSchema>;
const _assignable: MotionProjectSchemaOutput = null as unknown as MotionProject;
void _assignable;
