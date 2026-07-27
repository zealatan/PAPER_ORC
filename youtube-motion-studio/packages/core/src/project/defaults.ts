/**
 * Deterministic defaults and small factories for building projects (spec §6.2).
 * Factories never read the clock implicitly — timestamps are passed in so results are
 * reproducible and tests stay deterministic.
 */
import type { MotionProject, ProjectSettings, Transform2D } from "./types";

/** The schema version this build of core produces and normalizes to. */
export const CURRENT_SCHEMA_VERSION = "1.0.0";

/** Default composition settings (spec §6.2). */
export const DEFAULT_PROJECT_SETTINGS: ProjectSettings = {
  width: 1080,
  height: 1920,
  fps: 30,
  durationMode: "scenes",
  backgroundColor: "#000000",
  pixelRatio: 1,
};

/** A neutral identity transform used as a base for new elements. */
export const DEFAULT_TRANSFORM: Transform2D = {
  x: 0,
  y: 0,
  width: 100,
  height: 100,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
  anchorX: 0.5,
  anchorY: 0.5,
  skewX: 0,
  skewY: 0,
  opacity: 1,
  zIndex: 0,
};

export interface CreateProjectInput {
  id: string;
  name: string;
  /** ISO timestamp; passed explicitly to keep creation deterministic. */
  now: string;
  settings?: Partial<ProjectSettings>;
  themeId?: string;
}

/** Create a minimal, valid, empty project. */
export function createEmptyProject(input: CreateProjectInput): MotionProject {
  return {
    schemaVersion: CURRENT_SCHEMA_VERSION,
    id: input.id,
    name: input.name,
    createdAt: input.now,
    updatedAt: input.now,
    settings: { ...DEFAULT_PROJECT_SETTINGS, ...input.settings },
    theme: { themeId: input.themeId ?? "minimal-dark" },
    variables: {},
    assets: [],
    scenes: [],
    audioTracks: [],
  };
}
