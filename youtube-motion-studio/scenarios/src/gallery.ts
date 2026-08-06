/** Static showcase gallery + combined report from each clip's validation.json. */
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { SCENARIOS } from "./projects/index";
import { SCENARIOS_DIR, type Validation } from "./pipeline";

function load(): Validation[] {
  const out: Validation[] = [];
  for (const s of SCENARIOS) {
    const p = join(SCENARIOS_DIR, s.id, "validation.json");
    if (existsSync(p)) out.push(JSON.parse(readFileSync(p, "utf8")) as Validation);
  }
  return out;
}

const esc = (s: string): string =>
  s.replace(
    /[&<>"]/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!,
  );

export function buildGallery(): { count: number } {
  const vals = load();
  writeFileSync(
    join(SCENARIOS_DIR, "gallery", "report.json"),
    JSON.stringify(
      {
        total: vals.length,
        allRenderSuccess: vals.every((v) => v.renderSuccess),
        totalFileSizeMB: Number(vals.reduce((a, v) => a + v.fileSizeMB, 0).toFixed(2)),
        totalRenderMs: vals.reduce((a, v) => a + v.renderTimeMs, 0),
        clips: vals,
      },
      null,
      2,
    ),
  );
  writeFileSync(join(SCENARIOS_DIR, "gallery", "index.html"), html(vals));
  return { count: vals.length };
}

function html(vals: Validation[]): string {
  const cards = vals
    .map(
      (v) => `
    <article class="card">
      <div class="media"><video src="../${esc(v.exampleId)}/output.mp4" poster="../${esc(v.exampleId)}/poster.png" controls preload="none" muted playsinline loop></video></div>
      <div class="body">
        <div class="row"><h2>${esc(v.name)}</h2><span class="ok">${v.renderSuccess ? "●" : "○"}</span></div>
        <p class="style">${esc(v.style)}</p>
        <div class="stats"><span>${v.duration}s</span><span>${v.resolution}</span><span>${v.fps}fps</span><span>${v.fileSizeMB} MB</span><span>${(v.renderTimeMs / 1000).toFixed(1)}s 렌더</span></div>
        <div class="chips">${v.components.map((c) => `<span class="chip">${esc(c)}</span>`).join("")}</div>
      </div>
    </article>`,
    )
    .join("");
  const ok = vals.filter((v) => v.renderSuccess).length;
  const mb = vals.reduce((a, v) => a + v.fileSizeMB, 0).toFixed(1);
  return `<!doctype html>
<html lang="ko"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>YouTube Motion Studio — Cinematic Scenarios</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; } body { margin: 0; background: #07080b; color: #f0f2f6; font-family: "Noto Sans CJK KR", system-ui, sans-serif; }
  header { padding: 44px 24px 6px; } h1 { margin: 0; font-size: 30px; letter-spacing: -0.5px; }
  .lead { color: #9aa3b2; margin: 8px 0 0; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 18px; padding: 24px; }
  .card { background: #0f121a; border: 1px solid #1e2530; border-radius: 16px; overflow: hidden; }
  .media { background: #000; aspect-ratio: 9/16; } video { width: 100%; height: 100%; object-fit: contain; display: block; }
  .body { padding: 12px 14px 16px; } .row { display: flex; justify-content: space-between; align-items: baseline; }
  h2 { margin: 0; font-size: 17px; } .ok { color: #2ee66a; } .style { color: #ffd000; font-size: 12px; margin: 2px 0 10px; letter-spacing: 0.3px; }
  .stats { display: flex; flex-wrap: wrap; gap: 6px; font-size: 11px; color: #9aa3b2; margin-bottom: 8px; }
  .stats span { background: #0a0d13; border: 1px solid #1e2530; border-radius: 6px; padding: 2px 7px; font-variant-numeric: tabular-nums; }
  .chips { display: flex; flex-wrap: wrap; gap: 5px; } .chip { font-size: 10px; background: #12212b; color: #33d6c8; border: 1px solid #1d3a44; border-radius: 999px; padding: 2px 8px; }
</style></head>
<body>
  <header><h1>YouTube Motion Studio — Cinematic Scenarios</h1>
  <p class="lead">10편 · 렌더 성공 ${ok}/${vals.length} · 720×1280 / 15fps / H.264 · 총 ${mb} MB · 결정론적 렌더</p></header>
  <main class="grid">${cards}</main>
</body></html>`;
}
