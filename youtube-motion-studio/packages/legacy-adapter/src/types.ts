/**
 * Legacy template adapter contracts (spec §26). An adapter detects a legacy deck and imports its
 * *reusable data* into a MotionProject, listing anything it could not translate in a migration
 * report — it never rewrites the original (spec §26.3: gradual integration).
 */
import type { MotionProject } from "@motion-studio/core";

export interface DetectionResult {
  isLegacy: boolean;
  /** Identifier of the recognized legacy format, e.g. "pg-deck". */
  kind?: string;
  confidence: number;
}

export interface MigrationNote {
  sceneId?: string;
  /** What could not be translated (e.g. a chart/table template). */
  reason: string;
}

export interface AssetRequestNote {
  id: string;
  description: string;
  kind: "image" | "video" | "audio" | "other";
}

export interface MigrationReport {
  /** Scenes/features that were imported as placeholders. */
  unsupported: MigrationNote[];
  /** Charts/tables that were translated to real components (informational). */
  translated: MigrationNote[];
  /** Assets referenced by the legacy deck that must be provided. */
  assetRequests: AssetRequestNote[];
  /** Free-form notes. */
  notes: string[];
  importedScenes: number;
  importedElements: number;
}

export interface LegacyImportResult {
  project: MotionProject;
  report: MigrationReport;
}

export interface LegacyImportOptions {
  width?: number;
  height?: number;
  /** ISO timestamp for created/updated (kept explicit for deterministic imports). */
  now?: string;
  projectId?: string;
  /**
   * Directory holding the deck's background videos (`<bgid>.mp4`). When set, backgrounds are
   * attached as real video assets + video scene backgrounds; otherwise they become asset requests.
   */
  assetBasePath?: string;
}

export interface LegacyTemplateAdapter {
  detect(input: string): DetectionResult;
  import(input: string, options?: LegacyImportOptions): Promise<LegacyImportResult>;
}
