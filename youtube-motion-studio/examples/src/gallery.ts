/**
 * Gallery + combined report generator. Reads each example's validation.json and emits a static,
 * dependency-free dark-themed index.html plus a machine-readable report.json.
 */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { EXAMPLES } from "./projects/index";
import { EXAMPLES_DIR, type Validation } from "./pipeline";

function loadValidations(): Validation[] {
  const out: Validation[] = [];
  for (const ex of EXAMPLES) {
    const p = join(EXAMPLES_DIR, ex.id, "validation.json");
    if (existsSync(p)) out.push(JSON.parse(readFileSync(p, "utf8")) as Validation);
  }
  return out;
}

export function buildGallery(): { count: number } {
  const vals = loadValidations();
  const report = {
    generatedFrom: "@motion-studio/examples",
    total: vals.length,
    allRenderSuccess: vals.every((v) => v.renderSuccess),
    allHaveMoov: vals.every((v) => v.hasMoovAtom),
    totalRenderTimeMs: vals.reduce((a, v) => a + v.renderTimeMs, 0),
    examples: vals,
  };
  writeFileSync(
    join(EXAMPLES_DIR, "gallery", "report.json"),
    JSON.stringify(report, null, 2),
  );
  writeFileSync(join(EXAMPLES_DIR, "gallery", "index.html"), html(vals));
  return { count: vals.length };
}

const esc = (s: string): string =>
  s.replace(
    /[&<>"]/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!,
  );

function card(v: Validation): string {
  const chips = (items: string[], cls: string): string =>
    items.map((t) => `<span class="chip ${cls}">${esc(t)}</span>`).join("");
  const kb = (v.outputSizeBytes / 1024).toFixed(0);
  const speedup = v.serialRenderTimeMs
    ? ` · 병렬 ${(v.serialRenderTimeMs / v.renderTimeMs).toFixed(1)}×`
    : "";
  return `
  <article class="card">
    <div class="media">
      <video src="../${esc(v.exampleId)}/output.mp4" poster="../${esc(v.exampleId)}/representative.png" controls preload="none" muted playsinline></video>
    </div>
    <div class="body">
      <h2>${esc(v.exampleId.replace(/^\d+-/, ""))} <span class="ok">${v.renderSuccess ? "✓" : "✗"}</span></h2>
      <p class="sub">${esc(v.name)}</p>
      <div class="stats">
        <span>${v.durationSeconds.toFixed(1)}s</span>
        <span>${v.frameCount}f</span>
        <span>${(v.renderTimeMs / 1000).toFixed(1)}s 렌더${speedup}</span>
        <span>${v.framesPerSecond} fps</span>
        <span>${kb} KB</span>
      </div>
      <div class="chips">${chips(v.componentsUsed, "comp")}</div>
      <div class="chips">${chips(v.featuresTested, "feat")}</div>
      ${v.dataDisclaimer ? `<p class="disc">⚠ ${esc(v.dataDisclaimer)}</p>` : ""}
      ${v.warnings.length ? `<p class="warn">⚠ ${v.warnings.map(esc).join(" · ")}</p>` : ""}
      <p class="links"><a href="../${esc(v.exampleId)}/project.json">project.json</a> · <a href="../${esc(v.exampleId)}/output.mp4">mp4</a> · <a href="../${esc(v.exampleId)}/contact-sheet.png">contact sheet</a></p>
    </div>
  </article>`;
}

function html(vals: Validation[]): string {
  const okCount = vals.filter((v) => v.renderSuccess).length;
  return `<!doctype html>
<html lang="ko"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>YouTube Motion Studio — 검증 예제 갤러리</title>
<style>
  :root { color-scheme: dark; --bg:#0a0b0d; --card:#15181f; --border:#2b313c; --text:#f2f4f8; --dim:#9aa3b2; --accent:#ffd000; --teal:#33d6c8; }
  * { box-sizing:border-box; } body { margin:0; background:var(--bg); color:var(--text); font-family:"Noto Sans CJK KR",system-ui,sans-serif; }
  header { padding:40px 24px 8px; } h1 { margin:0; font-size:28px; } .lead { color:var(--dim); margin:6px 0 0; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:20px; padding:24px; }
  .card { background:var(--card); border:1px solid var(--border); border-radius:16px; overflow:hidden; display:flex; flex-direction:column; }
  .media { background:#000; aspect-ratio:9/16; } video { width:100%; height:100%; object-fit:contain; display:block; }
  .body { padding:14px 16px 18px; } h2 { margin:0; font-size:18px; text-transform:capitalize; } .ok { color:var(--teal); }
  .sub { color:var(--dim); margin:2px 0 10px; font-size:13px; }
  .stats { display:flex; flex-wrap:wrap; gap:8px; font-size:12px; color:var(--dim); margin-bottom:10px; }
  .stats span { background:#0f1319; border:1px solid var(--border); border-radius:6px; padding:2px 8px; font-variant-numeric:tabular-nums; }
  .chips { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:8px; } .chip { font-size:11px; border-radius:999px; padding:3px 9px; }
  .chip.comp { background:#12212b; color:var(--teal); border:1px solid #1d3a44; }
  .chip.feat { background:#2a2410; color:var(--accent); border:1px solid #4a3f16; }
  .disc, .warn { font-size:12px; margin:6px 0 0; } .disc { color:var(--dim); } .warn { color:#ff9a5a; }
  .links { font-size:12px; margin:10px 0 0; } .links a { color:var(--teal); text-decoration:none; } .links a:hover { text-decoration:underline; }
</style></head>
<body>
  <header>
    <h1>YouTube Motion Studio — 기능 검증 예제</h1>
    <p class="lead">10개 예제 · 렌더 성공 ${okCount}/${vals.length} · 전부 1080×1920 / 30fps / H.264 · 결정론적 렌더</p>
  </header>
  <main class="grid">${vals.map(card).join("")}</main>
</body></html>`;
}
