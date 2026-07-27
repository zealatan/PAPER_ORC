/**
 * PG deck adapter (spec §26). Imports the `pg_deck.json` scene format into a MotionProject:
 * titles/subtitles/quotes become real text elements, per-scene `subLines` become a time-distributed
 * subtitle, background videos become asset requests, and complex chart/table templates are imported
 * as labelled placeholders and listed in the migration report (spec §26.3, step 1: isolate the
 * reusable project data first; do not rewrite the original renderer).
 */
import {
  createEmptyProject,
  importProject,
  type MotionElement,
  type MotionProject,
  type Scene,
} from "@motion-studio/core";
import { normalizeDeckLines, normalizeDeckText } from "./textNormalize";
import type {
  LegacyImportOptions,
  LegacyTemplateAdapter,
  MigrationNote,
  MigrationReport,
} from "./types";

interface DeckScene {
  tpl?: string;
  dur?: number;
  bgid?: string | null;
  sid?: number;
  subLines?: unknown;
  data?: Record<string, unknown>;
}

interface DeckJson {
  scenes?: DeckScene[];
  theme?: string;
  paper?: string;
}

const CHART_TPLS = new Set([
  "enginechart",
  "reelchart",
  "hbars2",
  "divbars",
  "menuboard",
  "checks",
]);

/** Extract eyebrow / title / caption text from a scene's data by template. */
function extractText(
  tpl: string,
  data: Record<string, unknown>,
): { eyebrow?: string; title?: string; caption?: string } {
  const pick = (keys: string[]): string | undefined => {
    for (const key of keys) {
      const value = normalizeDeckText(data[key]);
      if (value) return value;
    }
    return undefined;
  };

  switch (tpl) {
    case "notice":
      return {
        title: pick(["title"]),
        caption: normalizeDeckLines(data.lines) || undefined,
      };
    case "hero":
      return { eyebrow: pick(["eye"]), title: pick(["big"]), caption: pick(["under"]) };
    case "sectint":
      return { eyebrow: pick(["phrase"]), title: pick(["head"]), caption: pick(["sub"]) };
    case "quotebig":
      return { title: pick(["quote"]), caption: pick(["source"]) };
    case "card":
      return {
        eyebrow: pick(["eyebrow"]),
        title: pick(["main"]),
        caption: pick(["sub"]),
      };
    default:
      return {
        eyebrow: undefined,
        title: pick(["title", "title1", "big", "main", "head"]),
        caption: pick(["sub", "under", "annoMain"]),
      };
  }
}

function makeElement(
  id: string,
  type: string,
  x: number,
  y: number,
  width: number,
  height: number,
  props: Record<string, unknown>,
  durationSeconds: number,
  zIndex: number,
): MotionElement {
  return {
    id,
    type,
    name: id,
    visible: true,
    locked: false,
    transform: {
      x,
      y,
      width,
      height,
      rotation: 0,
      scaleX: 1,
      scaleY: 1,
      anchorX: 0,
      anchorY: 0,
      skewX: 0,
      skewY: 0,
      opacity: 1,
      zIndex,
    },
    style: {},
    props,
    timing: { start: 0, duration: durationSeconds },
    animations: [],
  };
}

function subtitleCues(
  subLines: unknown,
  duration: number,
): Array<{ start: number; end: number; text: string }> {
  if (!Array.isArray(subLines) || subLines.length === 0) return [];
  const lines = subLines.map((l) => normalizeDeckText(l)).filter(Boolean);
  if (lines.length === 0) return [];
  const seg = duration / lines.length;
  return lines.map((text, i) => ({
    start: Math.round(i * seg * 100) / 100,
    end: Math.round((i + 1) * seg * 100) / 100,
    text,
  }));
}

function parseDeck(input: string): DeckJson | null {
  try {
    const parsed: unknown = JSON.parse(input);
    if (
      parsed &&
      typeof parsed === "object" &&
      Array.isArray((parsed as DeckJson).scenes)
    ) {
      return parsed as DeckJson;
    }
  } catch {
    return null;
  }
  return null;
}

export const pgDeckAdapter: LegacyTemplateAdapter = {
  detect(input) {
    const deck = parseDeck(input);
    if (!deck?.scenes) return { isLegacy: false, confidence: 0 };
    const looksLikeDeck = deck.scenes.some(
      (s) => typeof s.tpl === "string" && "dur" in s,
    );
    return looksLikeDeck
      ? { isLegacy: true, kind: "pg-deck", confidence: 0.9 }
      : { isLegacy: false, confidence: 0 };
  },

  import(input, options: LegacyImportOptions = {}) {
    const deck = parseDeck(input);
    if (!deck?.scenes) {
      return Promise.reject(new Error("Input is not a recognized PG deck JSON."));
    }

    const width = options.width ?? 1920;
    const height = options.height ?? 1080;
    const now = options.now ?? "2026-01-01T00:00:00.000Z";
    const unsupported: MigrationNote[] = [];
    const assetRequests = new Map<string, string>();
    let elementCount = 0;

    const scenes: Scene[] = deck.scenes.map((deckScene, index) => {
      const tpl = deckScene.tpl ?? "unknown";
      const sid = deckScene.sid ?? index + 1;
      const sceneId = `scene-${sid}`;
      const duration = Math.max(0.1, (deckScene.dur ?? 5000) / 1000);
      const data = deckScene.data ?? {};
      const elements: MotionElement[] = [];

      const isChart = CHART_TPLS.has(tpl);
      const text = extractText(tpl, data);

      if (text.eyebrow) {
        elements.push(
          makeElement(
            `${sceneId}-eyebrow`,
            "caption",
            160,
            140,
            width - 320,
            90,
            {
              text: text.eyebrow,
              fontSize: 40,
              background: "",
              color: "#9aa3b2",
            },
            duration,
            2,
          ),
        );
      }
      if (text.title) {
        elements.push(
          makeElement(
            `${sceneId}-title`,
            "title",
            120,
            isChart ? 60 : 380,
            width - 240,
            220,
            {
              text: text.title,
              fontSize: isChart ? 64 : 88,
              color: "#ffffff",
              textAlign: "center",
            },
            duration,
            3,
          ),
        );
      }
      if (text.caption) {
        elements.push(
          makeElement(
            `${sceneId}-caption`,
            "caption",
            160,
            isChart ? 300 : 660,
            width - 320,
            100,
            {
              text: text.caption,
              fontSize: 40,
              background: "",
              color: "#c9d3e4",
            },
            duration,
            3,
          ),
        );
      }

      if (isChart) {
        unsupported.push({
          sceneId,
          reason: `"${tpl}" chart/table not translated — imported as a placeholder.`,
        });
        elements.push(
          makeElement(
            `${sceneId}-placeholder`,
            "rectangle",
            160,
            440,
            width - 320,
            height - 640,
            {
              _legacyTpl: tpl,
            },
            duration,
            1,
          ),
        );
        elements.push(
          makeElement(
            `${sceneId}-placeholder-label`,
            "caption",
            160,
            640,
            width - 320,
            90,
            {
              text: `[legacy ${tpl}]`,
              fontSize: 40,
              background: "",
              color: "#8fa1bd",
            },
            duration,
            2,
          ),
        );
      }

      const cues = subtitleCues(deckScene.subLines, duration);
      if (cues.length > 0) {
        elements.push(
          makeElement(
            `${sceneId}-subtitle`,
            "subtitle",
            120,
            height - 180,
            width - 240,
            120,
            {
              cues,
              fontSize: 44,
            },
            duration,
            20,
          ),
        );
      }

      if (deckScene.bgid) {
        assetRequests.set(
          deckScene.bgid,
          `Background video "${deckScene.bgid}" from the PG deck`,
        );
      }

      elementCount += elements.length;
      return {
        id: sceneId,
        name: `${sid}. ${tpl}`,
        duration,
        background: { type: "solid", color: "#0e1726" },
        elements,
      };
    });

    const baseProject = createEmptyProject({
      id: options.projectId ?? "pg-deck-import",
      name: "P&G Deck (imported)",
      now,
      settings: { width, height },
      themeId: "minimal-dark",
    });
    const draft: MotionProject = { ...baseProject, scenes };

    // Validate + normalize through the standard pipeline so the result is guaranteed loadable.
    const { project } = importProject(draft);

    const report: MigrationReport = {
      unsupported,
      assetRequests: [...assetRequests.entries()].map(([id, description]) => ({
        id,
        description,
        kind: "video",
      })),
      notes: [
        `Imported ${scenes.length} scenes from the PG deck (theme "${deck.theme ?? "?"}").`,
        "Text, subtitles and structure were translated; chart/table templates are placeholders.",
      ],
      importedScenes: scenes.length,
      importedElements: elementCount,
    };

    return Promise.resolve({ project, report });
  },
};
