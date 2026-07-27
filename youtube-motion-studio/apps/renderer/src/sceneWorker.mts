/**
 * Per-scene render worker (spec §24, parallel export). A child process renders exactly one scene's
 * sub-project to an MP4 segment. resvg's rasterize call is synchronous and blocks the event loop, so
 * true multi-core rendering requires OS processes, not Promise.all — this worker is one such process.
 *
 * argv: <subProjectJsonPath> <outPath> [fontFile]
 * The parent writes a single-scene MotionProject JSON; this worker imports and exports it.
 */
import { readFileSync } from "node:fs";
import type { MotionProject } from "@motion-studio/core";
import { exportVideo } from "./exportVideo";
import type { FontConfig } from "./frames";

function resolveFonts(fontFile: string | undefined): FontConfig | undefined {
  // A full FontConfig (multiple files, system-font toggle) arrives via MS_FONTS; the positional
  // font argument is the single-file shorthand.
  if (process.env.MS_FONTS) return JSON.parse(process.env.MS_FONTS) as FontConfig;
  if (fontFile)
    return {
      files: [fontFile],
      defaultFamily: "Noto Sans CJK KR",
      loadSystemFonts: true,
    };
  return undefined;
}

async function main(): Promise<void> {
  const [jsonPath, outPath, fontFile] = process.argv.slice(2);
  if (!jsonPath || !outPath) throw new Error("usage: sceneWorker <json> <out> [font]");
  // The parent slices an already-validated MotionProject; re-importing would re-run migrations
  // against normalized data. Parse and render directly.
  const project = JSON.parse(readFileSync(jsonPath, "utf8")) as MotionProject;
  await exportVideo(project, { outPath, fonts: resolveFonts(fontFile) });
  process.stdout.write(`SEGMENT_DONE ${outPath}\n`);
}

main().catch((error: unknown) => {
  process.stderr.write(`SEGMENT_FAIL ${String(error)}\n`);
  process.exit(1);
});
