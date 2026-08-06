/**
 * CLI: `pnpm --filter @motion-studio/renderer render <project.json> <out.mp4>`
 * (runs via tsx so workspace TypeScript sources resolve directly).
 */
import { readFileSync } from "node:fs";
import { importProject } from "@motion-studio/core";
import { exportVideo } from "./exportVideo";

async function main(): Promise<void> {
  const [, , inPath, outPath] = process.argv;
  if (!inPath || !outPath) {
    process.stderr.write("usage: render <project.json> <out.mp4>\n");
    process.exit(1);
    return;
  }

  const { project } = importProject(readFileSync(inPath, "utf8"));
  const result = await exportVideo(project, { outPath }, (p) => {
    if (p.frame % 15 === 0 || p.frame === p.totalFrames) {
      process.stderr.write(`\rframe ${p.frame}/${p.totalFrames}`);
    }
  });
  process.stderr.write("\n");
  process.stdout.write(`${JSON.stringify(result.report, null, 2)}\n`);
}

main().catch((error: unknown) => {
  process.stderr.write(
    `Export failed: ${error instanceof Error ? error.message : String(error)}\n`,
  );
  process.exit(1);
});
