/**
 * "Time Creates Wealth" — a 10-second hero film. The engine layer (information + motion graphics):
 * a point grows into a clock, machine gears morph into a circular data grid, the camera runs across
 * a chart past company logos, particles gather into $8,000,000, the number reforms into the opening
 * clock, and the closing line. Built entirely from MATCH CUTS + keyframe-scale "camera" (no repeated
 * fades); the AI/emotion beats (clock close-up, gears, particles, light) are meant to sit UNDER this
 * as WAN video backgrounds via the engine's video-composite path — see hero/AI_SHOTLIST.md.
 *
 * Timing is element-relative (timeline feeds `sceneLocalTime - timing.start`): `start` places the
 * element, `duration` is its lifetime, animations begin at 0 (element birth).
 */
import type { MotionElement, MotionProject, Scene } from "@motion-studio/core";
import {
  W,
  bigText,
  box,
  dot,
  el,
  enter,
  gradient,
  kenBurns,
  label,
  panel,
  project,
  scene,
} from "../toolkit";

export interface ScenarioDef {
  id: string;
  name: string;
  style: string;
  featuresTested: string[];
  posterTime?: number;
  build: () => MotionProject;
}

const CX = W / 2;
const CY = 940;
const YELLOW = "#ffd000";
const WHITE = "#ffffff";
const IN = (d = 0.5) => [enter("fade-in", 0, d)];
const POPIN = (d = 0.4) => [enter("pop-in", 0, d)];
const KB = (dur: number, from: number, to: number) => kenBurns(0, dur, from, to);
const BG = gradient(["#000000", "#070707", "#000000"], 120);

function ring(
  idp: string,
  color: string,
  inner: string,
  r: number,
  start: number,
  duration: number,
  anim: ReturnType<typeof IN>,
  z = 3,
): MotionElement[] {
  return [
    dot(`${idp}o`, CX, CY, r, color, { start, duration, anim, z }),
    dot(`${idp}i`, CX, CY, r * 0.8, inner, { start, duration, z: z + 1 }),
  ];
}
function around(r: number, n: number): Array<[number, number]> {
  return Array.from({ length: n }, (_, i) => {
    const a = (i / n) * Math.PI * 2 - Math.PI / 2;
    return [CX + Math.cos(a) * r, CY + Math.sin(a) * r] as [number, number];
  });
}

// 0.0–1.5 — a point grows into the clock's center (camera push in)
function s1(): Scene {
  return scene(
    "s1",
    "point",
    1.5,
    [
      dot("p", CX, CY, 200, WHITE, {
        start: 0,
        duration: 1.5,
        anim: [...IN(0.4), KB(1.5, 0.04, 1.0)],
        z: 5,
      }),
      ...ring("clk", "#2a2f38", "#050505", 210, 0.7, 0.8, [
        ...IN(0.5),
        KB(0.8, 0.9, 1.05),
      ]),
    ],
    BG,
  );
}

// 1.5–3.0 — into the clock: gears rotate, then morph to a circular data grid (machine → data)
function s2(): Scene {
  const teeth = around(210, 14).map(([x, y], i) =>
    dot(`t${i}`, x, y, 14, i % 2 ? "#3a4150" : "#586274", {
      start: 0.0 + i * 0.045,
      duration: 1.5,
      anim: POPIN(0.2),
      z: 4,
    }),
  );
  const radial = Array.from({ length: 6 }, (_, i) =>
    panel(`r${i}`, box(CX, CY, 6, 360, { rotation: i * 30 }), {
      fill: "#1a3a4a",
      radius: 3,
      opacity: 0.55,
      start: 0.75 + i * 0.05,
      duration: 0.75,
      anim: IN(0.25),
      z: 2,
    }),
  );
  return scene(
    "s2",
    "gear",
    1.5,
    [
      ...ring("clk", "#2a2f38", "#04120f", 210, 0, 1.0, [KB(1.0, 1.05, 1.25)]),
      ...teeth,
      ...ring(
        "grid1",
        "#1f5a5a",
        "#040a0a",
        150,
        0.75,
        0.75,
        [...IN(0.3), KB(0.75, 0.9, 1.0)],
        2,
      ),
      ...ring("grid2", "#164040", "#040a0a", 240, 0.8, 0.7, IN(0.3), 1),
      ...radial,
      label("m", "기계가 데이터가 된다", 1420, {
        size: 40,
        color: "#5fb0a0",
        start: 0.9,
        duration: 0.6,
        anim: IN(0.4),
        z: 8,
      }),
    ],
    gradient(["#020a0a", "#06181a", "#010505"], 120),
  );
}

// 3.0–5.0 — the camera runs across a living chart; logos appear as checkpoints
function s3(): Scene {
  const pts = [
    [210, 1180],
    [360, 1120],
    [520, 1150],
    [670, 1020],
    [820, 940],
  ];
  const logos: Array<[string, string]> = [
    ["A", "#e6e6e6"],
    ["M", "#2ee66a"],
    ["C", "#ff4757"],
    ["V", YELLOW],
    ["J", "#4aa3ff"],
  ];
  const checkpoints = pts.flatMap(([x, y], i) => [
    dot(`cp${i}`, x, y, 12, WHITE, {
      start: 0.5 + i * 0.28,
      duration: 2,
      anim: POPIN(0.2),
      z: 5,
    }),
    el({
      id: `lg${i}`,
      type: "topic-circle",
      transform: box(x, y - 110, 120, 120),
      props: { label: logos[i]![0], fill: logos[i]![1], color: "#0a0a0a", fontSize: 60 },
      start: 0.6 + i * 0.28,
      duration: 1.6,
      animations: POPIN(0.3),
      zIndex: 7,
    }),
  ]);
  return scene(
    "s3",
    "chart",
    2.0,
    [
      el({
        id: "ch",
        type: "line-chart",
        transform: box(CX, 1120, 980, 720),
        props: {
          values: [12, 20, 16, 34, 30, 52, 48, 78, 110, 150],
          color: "#2ee66a",
          area: true,
          strokeWidth: 9,
        },
        start: 0,
        duration: 2,
        animations: [...IN(0.5), KB(2, 0.9, 1.35)],
        zIndex: 2,
      }),
      label("t", "시간이 부를 만든다", 520, {
        size: 52,
        color: WHITE,
        start: 0.3,
        duration: 1.7,
        anim: IN(0.5),
        z: 8,
      }),
      ...checkpoints,
    ],
    gradient(["#03100a", "#08200f", "#020806"], 120),
  );
}

// 5.0–7.0 — particles gather into a number that fills the screen
function s4(): Scene {
  const grid = Array.from({ length: 28 }, (_, i) =>
    dot(`pt${i}`, 150 + (i % 7) * 130, 640 + Math.floor(i / 7) * 200, 20, YELLOW, {
      start: 0.05 + i * 0.02,
      duration: 1.0,
      anim: POPIN(0.25),
      z: 3,
    }),
  );
  return scene(
    "s4",
    "number",
    2.0,
    [
      ...grid,
      panel("glow", box(CX, CY, 1000, 520), {
        fill: YELLOW,
        radius: 260,
        opacity: 0.12,
        start: 1.0,
        duration: 1.0,
        anim: IN(0.4),
        z: 4,
      }),
      bigText("n", "$8,000,000", CY, {
        size: 150,
        color: YELLOW,
        start: 1.0,
        duration: 1.0,
        anim: [...POPIN(0.4), KB(1.0, 0.8, 1.15)],
        z: 6,
      }),
    ],
    gradient(["#050400", "#0a0800", "#020200"], 120),
  );
}

// 7.0–8.5 — the number shatters and reforms into the opening clock
function s5(): Scene {
  const shards = around(300, 16).map(([x, y], i) =>
    dot(`sh${i}`, x, y, 18, "#c9a020", {
      start: 0.0 + i * 0.02,
      duration: 0.7,
      anim: IN(0.15),
      z: 3,
    }),
  );
  return scene(
    "s5",
    "return",
    1.5,
    [
      bigText("n", "$8,000,000", CY, {
        size: 150,
        color: "#7a6416",
        start: 0,
        duration: 0.5,
        anim: IN(0.1),
        z: 6,
      }),
      ...shards,
      ...ring(
        "clk",
        "#2a2f38",
        "#050505",
        210,
        0.7,
        0.8,
        [...IN(0.4), KB(0.8, 1.3, 1.0)],
        5,
      ),
      label("m", "모든 것은 시간으로 돌아온다", 1440, {
        size: 40,
        color: "#8a8a8a",
        start: 0.9,
        duration: 0.6,
        anim: IN(0.4),
        z: 8,
      }),
    ],
    BG,
  );
}

// 8.5–10.0 — the closing line
function s6(): Scene {
  return scene(
    "s6",
    "line",
    1.5,
    [
      dot("depth", CX, CY, 460, "#0b0b0b", {
        start: 0,
        duration: 1.5,
        anim: [KB(1.5, 1.1, 0.9)],
        z: 1,
      }),
      ...ring("clk", "#141820", "#050505", 150, 0, 1.5, IN(0.6), 2),
      bigText("m1", "The greatest investment", 760, {
        size: 54,
        color: "#9a9a9a",
        start: 0.1,
        duration: 1.4,
        anim: IN(0.6),
        z: 6,
      }),
      bigText("m2", "was never money.", 850, {
        size: 54,
        color: "#9a9a9a",
        start: 0.4,
        duration: 1.1,
        anim: IN(0.6),
        z: 6,
      }),
      bigText("m3", "It was time.", 1080, {
        size: 100,
        color: YELLOW,
        start: 0.7,
        duration: 0.8,
        anim: [...IN(0.6), KB(0.8, 1.0, 1.06)],
        z: 7,
      }),
      label("brand", "YouTube Motion Studio", 1560, {
        size: 32,
        color: "#555555",
        start: 1.0,
        duration: 0.5,
        anim: IN(0.5),
        z: 6,
      }),
    ],
    BG,
  );
}

function heroFilm(): MotionProject {
  return project(
    "hero-video",
    "Time Creates Wealth",
    [s1(), s2(), s3(), s4(), s5(), s6()],
    {
      theme: "Time creates wealth",
      accent: YELLOW,
      note: "10s hero film — engine layer; AI video slots documented in AI_SHOTLIST.md",
    },
  );
}

export const SCENARIOS: ScenarioDef[] = [
  {
    id: "hero-video",
    name: "Time Creates Wealth",
    style: "Apple Event × MagnatesMedia × AI cinematic",
    featuresTested: [
      "point-to-clock",
      "gear-to-grid",
      "camera-into-chart",
      "logos-as-checkpoints",
      "particles-to-number",
      "number-to-clock",
      "match-cut",
      "clock-bookend",
    ],
    build: heroFilm,
    posterTime: 6.0,
  },
];
