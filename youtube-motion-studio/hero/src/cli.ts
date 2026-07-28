/** Showcase CLI: generate | preview | render | validate | gallery | all (+--skip-existing, +NN- filter). */
import { SCENARIOS } from "./projects/index";
import { buildGallery } from "./gallery";
import {
  generate,
  outputsExist,
  preview,
  render,
  validate,
  type Validation,
} from "./pipeline";

const args = process.argv.slice(2);
const stage = args[0] ?? "all";
const skipExisting = args.includes("--skip-existing");
const only = args.find((a) => /^\d\d-/.test(a));
const targets = only ? SCENARIOS.filter((s) => s.id === only) : SCENARIOS;
const log = (m: string): void => void process.stdout.write(m + "\n");

async function runAll(): Promise<void> {
  const results: Validation[] = [];
  for (const ex of targets) {
    if (skipExisting && outputsExist(ex.id)) {
      log(`↷ ${ex.id}`);
      continue;
    }
    generate(ex);
    preview(ex);
    const timing = await render(ex);
    const v = validate(ex, timing);
    results.push(v);
    log(
      `  ${v.renderSuccess ? "✓" : "✗"} ${ex.id.padEnd(20)} ${v.resolution} ${v.duration}s ${v.frameCount}f ${v.fileSizeMB}MB moov=${v.hasMoovAtom} (${(v.renderTimeMs / 1000).toFixed(1)}s)`,
    );
  }
  const g = buildGallery();
  const ok = results.filter((r) => r.renderSuccess).length;
  log(`\ngallery ✓ ${g.count} → hero/gallery/index.html`);
  log(`DONE render success ${ok}/${results.length}`);
}

async function main(): Promise<void> {
  switch (stage) {
    case "generate":
      for (const ex of targets) {
        generate(ex);
        log(`generate ✓ ${ex.id}`);
      }
      break;
    case "preview":
      for (const ex of targets) {
        preview(ex);
        log(`preview ✓ ${ex.id}`);
      }
      break;
    case "render":
      for (const ex of targets) {
        const t = await render(ex);
        log(`render ✓ ${ex.id} (${(t.renderTimeMs / 1000).toFixed(1)}s)`);
      }
      break;
    case "validate":
      for (const ex of targets) {
        const v = validate(ex, { renderTimeMs: 0 });
        log(`validate ${v.renderSuccess ? "✓" : "✗"} ${ex.id} ${v.fileSizeMB}MB`);
      }
      break;
    case "gallery":
      buildGallery();
      log("gallery ✓");
      break;
    case "all":
      await runAll();
      break;
    default:
      log(`unknown stage: ${stage}`);
      process.exit(1);
  }
}

main().catch((e: unknown) => {
  process.stderr.write(String(e instanceof Error ? e.stack : e) + "\n");
  process.exit(1);
});
