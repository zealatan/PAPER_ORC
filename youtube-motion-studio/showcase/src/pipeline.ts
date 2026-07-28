/**
 * Showcase build pipeline: generate → preview → render → validate → gallery. Reuses the existing
 * engine (renderFrameToPng / renderDeckParallel). Small output (720×1280 @ 15fps) keeps every clip
 * well under the 1–3 MB target.
 */
import { spawnSync } from "node:child_process";
import {
  cpSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { validateProject, type MotionProject } from "@motion-studio/core";
import {
  createRegistry,
  renderDeckParallel,
  renderFrameToPng,
  resolveForRender,
  type FontConfig,
} from "@motion-studio/renderer";
import { SHOWCASES, type ShowcaseDef } from "./projects/index";

const HERE = dirname(fileURLToPath(import.meta.url));
export const SHOWCASE_DIR = join(HERE, "..");
const FONTS_DIR = join(SHOWCASE_DIR, "fonts");

export const FONTS: FontConfig = {
  files: [
    join(FONTS_DIR, "BlackHanSans-Regular.ttf"),
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
  ],
  defaultFamily: "Noto Sans CJK KR",
  loadSystemFonts: false,
};

export interface Validation {
  exampleId: string;
  name: string;
  style: string;
  renderSuccess: boolean;
  hasMoovAtom: boolean;
  resolution: string;
  fps: number;
  duration: number;
  fileSizeMB: number;
  frameCount: number;
  scenes: number;
  components: string[];
  renderTimeMs: number;
  framesPerSecond: number;
}

const dir = (id: string): string => join(SHOWCASE_DIR, id);
const ensure = (p: string): string => (mkdirSync(p, { recursive: true }), p);
const ffprobe = (file: string, a: string[]): string =>
  (
    spawnSync("ffprobe", ["-v", "error", ...a, file], { encoding: "utf8" }).stdout ?? ""
  ).trim();

function components(project: MotionProject): string[] {
  const set = new Set<string>();
  const walk = (els: MotionProject["scenes"][number]["elements"]): void => {
    for (const e of els) {
      set.add(e.type);
      if (e.children) walk(e.children);
    }
  };
  for (const s of project.scenes) walk(s.elements);
  return [...set].sort();
}

const starts = (p: MotionProject): number[] => {
  const out: number[] = [];
  let acc = 0;
  for (const s of p.scenes) {
    out.push(acc);
    acc += s.duration;
  }
  return out;
};
const total = (p: MotionProject): number => p.scenes.reduce((a, s) => a + s.duration, 0);

export function loadProject(id: string): MotionProject {
  const p = join(dir(id), "project.json");
  if (existsSync(p)) return JSON.parse(readFileSync(p, "utf8")) as MotionProject;
  return SHOWCASES.find((e) => e.id === id)!.build();
}
export function outputsExist(id: string): boolean {
  return (
    existsSync(join(dir(id), "output.mp4")) &&
    existsSync(join(dir(id), "validation.json"))
  );
}

export function generate(ex: ShowcaseDef): void {
  const project = ex.build();
  validateProject(project);
  ensure(dir(ex.id));
  writeFileSync(join(dir(ex.id), "project.json"), JSON.stringify(project, null, 2));
}

export function preview(ex: ShowcaseDef): void {
  const project = loadProject(ex.id);
  const registry = createRegistry();
  const resolved = resolveForRender(project);
  const st = starts(project);
  const previewDir = ensure(join(dir(ex.id), "preview"));
  const frames: string[] = [];
  project.scenes.forEach((scene, i) => {
    const phases: Array<[string, number]> = [
      ["start", st[i]! + 0.15],
      ["middle", st[i]! + scene.duration / 2],
      ["end", st[i]! + scene.duration - 0.15],
    ];
    for (const [phase, t] of phases) {
      const name = `scene-${String(i + 1).padStart(2, "0")}-${phase}.png`;
      writeFileSync(
        join(previewDir, name),
        renderFrameToPng(resolved, t, registry, 360, false, FONTS),
      );
      frames.push(join(previewDir, name));
    }
  });
  // Poster: the project's chosen hero moment (or middle of the richest scene), full width.
  const heroT =
    ex.posterTime ??
    st[richest(project)]! + project.scenes[richest(project)]!.duration / 2;
  writeFileSync(
    join(dir(ex.id), "poster.png"),
    renderFrameToPng(resolved, heroT, registry, 720, false, FONTS),
  );
  contactSheet(frames, join(dir(ex.id), "contact-sheet.png"));
}

function richest(p: MotionProject): number {
  return p.scenes.reduce(
    (b, s, i) => (s.elements.length > p.scenes[b]!.elements.length ? i : b),
    0,
  );
}

function contactSheet(frames: string[], outPath: string): void {
  if (!frames.length) return;
  const tmp = mkdtempSync(join(tmpdir(), "cs-"));
  try {
    frames.forEach((f, i) => cpSync(f, join(tmp, `${String(i).padStart(3, "0")}.png`)));
    const cols = 3;
    const rows = Math.ceil(frames.length / cols);
    spawnSync(
      "ffmpeg",
      [
        "-y",
        "-v",
        "error",
        "-framerate",
        "1",
        "-i",
        join(tmp, "%03d.png"),
        "-frames:v",
        "1",
        "-vf",
        `scale=240:426,tile=${cols}x${rows}:padding=8:margin=8:color=#0b0d12`,
        outPath,
      ],
      { encoding: "utf8" },
    );
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}

export async function render(ex: ShowcaseDef): Promise<{ renderTimeMs: number }> {
  const project = loadProject(ex.id);
  ensure(dir(ex.id));
  const t0 = process.hrtime.bigint();
  await renderDeckParallel(project, {
    outPath: join(dir(ex.id), "output.mp4"),
    fonts: FONTS,
  });
  return { renderTimeMs: Number(process.hrtime.bigint() - t0) / 1e6 };
}

export function validate(ex: ShowcaseDef, timing: { renderTimeMs: number }): Validation {
  const project = loadProject(ex.id);
  const out = join(dir(ex.id), "output.mp4");
  const width = Number(
    ffprobe(out, [
      "-select_streams",
      "v:0",
      "-show_entries",
      "stream=width",
      "-of",
      "csv=p=0",
    ]) || 0,
  );
  const height = Number(
    ffprobe(out, [
      "-select_streams",
      "v:0",
      "-show_entries",
      "stream=height",
      "-of",
      "csv=p=0",
    ]) || 0,
  );
  const duration = Number(
    ffprobe(out, ["-show_entries", "format=duration", "-of", "csv=p=0"]) || 0,
  );
  const nb = ffprobe(out, [
    "-select_streams",
    "v:0",
    "-count_frames",
    "-show_entries",
    "stream=nb_read_frames",
    "-of",
    "csv=p=0",
  ]);
  const frameCount = Number(nb || Math.round(total(project) * project.settings.fps));
  const bytes = existsSync(out) ? statSync(out).size : 0;
  const hasMoovAtom = width > 0 && height > 0 && duration > 0;
  const v: Validation = {
    exampleId: ex.id,
    name: ex.name,
    style: ex.style,
    renderSuccess: hasMoovAtom && bytes > 0,
    hasMoovAtom,
    resolution: `${width}x${height}`,
    fps: project.settings.fps,
    duration: Number(duration.toFixed(2)),
    fileSizeMB: Number((bytes / (1024 * 1024)).toFixed(2)),
    frameCount,
    scenes: project.scenes.length,
    components: components(project),
    renderTimeMs: Math.round(timing.renderTimeMs),
    framesPerSecond: Number((frameCount / (timing.renderTimeMs / 1000)).toFixed(1)),
  };
  writeFileSync(join(dir(ex.id), "validation.json"), JSON.stringify(v, null, 2));
  return v;
}
