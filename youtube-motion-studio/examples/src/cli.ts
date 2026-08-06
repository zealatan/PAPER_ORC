/**
 * Examples CLI. Stages: generate | preview | render | validate | gallery | all.
 * `all` runs the full pipeline; `--skip-existing` skips examples that already have outputs.
 */
import { EXAMPLES } from "./projects/index";
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
const targets = only ? EXAMPLES.filter((e) => e.id === only) : EXAMPLES;

function log(msg: string): void {
  process.stdout.write(msg + "\n");
}

async function runAll(): Promise<void> {
  const results: Validation[] = [];
  for (const ex of targets) {
    if (skipExisting && outputsExist(ex.id)) {
      log(`↷ ${ex.id} (skip-existing)`);
      continue;
    }
    const t0 = Date.now();
    generate(ex);
    log(`  generate ✓ ${ex.id}`);
    preview(ex);
    log(`  preview  ✓ ${ex.id}`);
    const timing = await render(ex);
    log(
      `  render   ✓ ${ex.id} (${(timing.renderTimeMs / 1000).toFixed(1)}s, ${timing.workers}w${timing.serialMs ? `, serial ${(timing.serialMs / 1000).toFixed(1)}s` : ""})`,
    );
    const v = validate(ex, timing);
    results.push(v);
    log(
      `  validate ${v.renderSuccess ? "✓" : "✗"} ${ex.id} — ${v.durationSeconds}s ${v.frameCount}f ${v.resolution.width}x${v.resolution.height} moov=${v.hasMoovAtom} (${Math.round((Date.now() - t0) / 1000)}s total)`,
    );
  }
  const g = buildGallery();
  log(`\ngallery ✓ ${g.count} examples → examples/gallery/index.html`);
  const ok = results.filter((r) => r.renderSuccess).length;
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
        const timing = await render(ex);
        log(`render ✓ ${ex.id} (${(timing.renderTimeMs / 1000).toFixed(1)}s)`);
      }
      break;
    case "validate":
      for (const ex of targets) {
        const v = validate(ex, { renderTimeMs: 0, workers: 0 });
        log(`validate ${v.renderSuccess ? "✓" : "✗"} ${ex.id}`);
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
