/**
 * @motion-studio/legacy-adapter — import legacy video decks into MotionProject data (spec §26).
 */
export { pgDeckAdapter, DISPLAY_FONT } from "./deckAdapter";
export { normalizeDeckText, normalizeDeckLines } from "./textNormalize";
export type {
  LegacyTemplateAdapter,
  DetectionResult,
  LegacyImportResult,
  LegacyImportOptions,
  MigrationReport,
  MigrationNote,
  AssetRequestNote,
} from "./types";
