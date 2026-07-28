/**
 * "Ultimate Showcase" — one continuous ~90s cinematic showreel (1080×1920 / 30fps), not a gallery
 * of examples. It threads typography, charts, a dashboard, a timeline, world-map connections,
 * company logos, photo montage, and big numbers into a single trailer-like arc. Every scene pushes
 * (keyframe-scale "camera"), fades between beats, and keeps to black / white / yellow.
 *
 * No new engine features: "camera moves" are keyframe scale, "dip to black" is a fading full-frame
 * panel, "photos" are gradient panels, "particles/glow" are layered translucent shapes.
 */
import type { MotionElement, MotionProject } from "@motion-studio/core";
import type { Scene } from "@motion-studio/core";
import {
  W,
  H,
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
const YELLOW = "#ffd000";
const WHITE = "#ffffff";
const FADE = (s: number, d = 0.6) => [enter("fade-in", s, d)];
const POP = (s: number, d = 0.5) => [enter("pop-in", s, d)];
const BLACK = gradient(["#000000", "#070707"], 90);

/** Dip-to-black bridge: a full-frame panel that fades in over the last `d`s of a scene. */
function dipOut(dur: number, d = 0.6): MotionElement {
  return panel("dip", box(CX, H / 2, W, H), {
    fill: "#000000",
    radius: 0,
    opacity: 1,
    z: 90,
    start: dur - d,
    anim: FADE(dur - d, d),
  });
}

// ── Scene 1 (0–8) — Every second changes everything ─────────────────────────────
function s1(): Scene {
  return scene(
    "s1",
    "hook",
    8,
    [
      label("tick", "· · · · ·", 620, {
        size: 60,
        color: "#2a2a2a",
        start: 0.2,
        duration: 2.4,
        anim: FADE(0.3, 1.0),
      }),
      bigText("a", "Every second", 940, {
        size: 120,
        color: WHITE,
        start: 1.4,
        duration: 3.4,
        anim: [...FADE(1.6, 1.0), kenBurns(1.4, 3.4, 1.0, 1.08)],
      }),
      bigText("b", "changes", 860, {
        size: 190,
        color: WHITE,
        start: 5.0,
        duration: 3.0,
        anim: [...FADE(5.0, 0.5), kenBurns(5.0, 3.0, 1.0, 2.2)],
      }),
      bigText("c", "everything.", 1080, {
        size: 190,
        color: YELLOW,
        start: 5.3,
        duration: 2.7,
        anim: [...FADE(5.3, 0.5), kenBurns(5.3, 2.7, 1.0, 2.2)],
      }),
      dipOut(8, 0.7),
    ],
    BLACK,
  );
}

// ── Scene 2 (8–18) — Time becomes a chart ───────────────────────────────────────
function s2(): Scene {
  const chartBg = gradient(["#05100a", "#0a1f14", "#040a07"], 120);
  return scene(
    "s2",
    "clock",
    10,
    [
      dot("face", CX, 860, 260, "#0a1510", {
        border: "#2f6f4a",
        borderWidth: 8,
        anim: [...FADE(0.2, 0.8), kenBurns(0, 5, 0.85, 1.05)],
      }),
      // hands appear at rotating angles → spinning illusion, accelerating
      panel("h1", box(CX, 700, 12, 170), {
        fill: WHITE,
        radius: 6,
        start: 0.8,
        duration: 0.5,
        anim: FADE(0.8, 0.15),
      }),
      panel("h2", box(CX + 130, 860, 170, 12), {
        fill: WHITE,
        radius: 6,
        start: 1.3,
        duration: 0.45,
        anim: FADE(1.3, 0.12),
      }),
      panel("h3", box(CX, 1020, 12, 170), {
        fill: WHITE,
        radius: 6,
        start: 1.75,
        duration: 0.4,
        anim: FADE(1.75, 0.1),
      }),
      panel("h4", box(CX - 130, 860, 170, 12), {
        fill: YELLOW,
        radius: 6,
        start: 2.15,
        duration: 0.5,
        anim: FADE(2.15, 0.1),
      }),
      label("l", "시간은 흐르고, 자산이 된다", 1320, {
        size: 44,
        color: "#7fd6a0",
        start: 1.0,
        anim: FADE(1.2),
      }),
      // faint chart wakes up, then dominates as the clock fades
      el({
        id: "ch",
        type: "line-chart",
        transform: box(CX, 980, 940, 780),
        props: {
          values: [20, 26, 24, 40, 52, 66, 60, 84, 100, 128],
          color: "#2ee66a",
          area: true,
          strokeWidth: 8,
          yTicks: [
            [0, "0"],
            [60, "60"],
            [120, "120"],
          ],
        },
        animations: [...FADE(4.6, 1.4), kenBurns(4.6, 5.4, 1.0, 1.12)],
        zIndex: 8,
      }),
      bigText("t", "복리", 900, {
        size: 150,
        color: YELLOW,
        start: 6.5,
        duration: 3.5,
        anim: [...FADE(6.7, 0.7), kenBurns(6.5, 3.5, 1.0, 1.1)],
      }),
      dipOut(10, 0.7),
    ],
    chartBg,
  );
}

// ── Scene 3 (18–28) — World map connections ─────────────────────────────────────
function s3(): Scene {
  const night = gradient(["#050912", "#0a1832", "#04070f"], 120);
  const cities: Array<[string, number, number]> = [
    ["뉴욕", 250, 760],
    ["런던", 470, 680],
    ["도쿄", 830, 760],
    ["서울", 700, 620],
    ["싱가포르", 560, 980],
  ];
  const links: Array<[number, number, number, number, number]> = [
    [250, 760, 470, 680, 0.6],
    [470, 680, 700, 620, 0.9],
    [700, 620, 830, 760, 1.2],
    [830, 760, 560, 980, 1.5],
    [560, 980, 250, 760, 1.8],
  ];
  const linkEls = links.map(([x1, y1, x2, y2, s], i) => {
    const mx = (x1 + x2) / 2,
      my = (y1 + y2) / 2;
    const len = Math.hypot(x2 - x1, y2 - y1);
    const ang = (Math.atan2(y2 - y1, x2 - x1) * 180) / Math.PI;
    return panel(`lk${i}`, box(mx, my, len, 4, { rotation: ang }), {
      fill: "#3a6ea5",
      radius: 2,
      opacity: 0.7,
      anim: FADE(s, 0.5),
    });
  });
  return scene(
    "s3",
    "map",
    10,
    [
      ...linkEls,
      ...cities.flatMap(([name, x, y], i) => [
        dot(`c${i}`, x, y, 16, YELLOW, { anim: POP(0.3 + i * 0.28, 0.4), z: 4 }),
        label(`cl${i}`, name, y + 60, {
          size: 32,
          color: "#cdd9ee",
          cx: x,
          width: 220,
          start: 0.3 + i * 0.28,
          anim: FADE(0.5 + i * 0.28),
        }),
      ]),
      bigText("t", "세계는 연결돼 있다", 1360, {
        size: 72,
        color: WHITE,
        start: 2.6,
        anim: [...FADE(2.8, 0.7), kenBurns(2.6, 7, 1.0, 1.14)],
      }),
      label("l", "돈은 국경을 넘는다", 1480, {
        size: 40,
        color: "#8fa9cf",
        start: 3.4,
        anim: FADE(3.6),
      }),
      dipOut(10, 0.7),
    ],
    night,
  );
}

// ── Scene 4 (28–40) — Company logos + KPI cards ─────────────────────────────────
function s4(): Scene {
  const logos: Array<[string, string, string]> = [
    ["A", "Apple", "#e6e6e6"],
    ["C", "Coca-Cola", "#ff4757"],
    ["J", "JNJ", "#4aa3ff"],
    ["M", "Microsoft", "#2ee66a"],
    ["V", "Visa", "#ffd000"],
    ["L", "LVMH", "#c9a24a"],
  ];
  const grid = logos.flatMap(([ch, name, color], i) => {
    const x = 250 + (i % 3) * 290;
    const y = 640 + Math.floor(i / 3) * 320;
    const s = 0.2 + i * 0.5;
    return [
      el({
        id: `lg${i}`,
        type: "topic-circle",
        transform: box(x, y, 190, 190),
        props: { label: ch, fill: color, color: "#0a0a0a", fontSize: 96 },
        animations: POP(s, 0.4),
        zIndex: 3,
      }),
      label(`ln${i}`, name, y + 135, {
        size: 30,
        color: "#c9d3e4",
        cx: x,
        width: 260,
        start: s,
        anim: FADE(s + 0.2),
      }),
    ];
  });
  return scene(
    "s4",
    "logos",
    12,
    [
      ...grid,
      // KPI cards float up as the "camera passes"
      panel("k1", box(CX, 1440, 880, 150), {
        fill: "#12151c",
        border: "#2a2f3a",
        borderWidth: 2,
        radius: 20,
        start: 6.5,
        anim: [enter("slide-up", 6.5, 0.6, { distance: 200 })],
      }),
      label("k1l", "평균 배당성장 8.4%  ·  시총 합계 $12T", 1440, {
        size: 40,
        color: YELLOW,
        start: 6.5,
        anim: FADE(6.9),
      }),
      bigText("t", "세상을 움직이는 기업들", 380, {
        size: 66,
        color: WHITE,
        start: 8.5,
        anim: [...FADE(8.7, 0.6), kenBurns(8.5, 3.5, 1.0, 1.08)],
      }),
      dipOut(12, 0.7),
    ],
    BLACK,
  );
}

// ── Scene 5 (40–52) — Dashboard comes alive ─────────────────────────────────────
function s5(): Scene {
  const navy = gradient(["#070b12", "#111a2c", "#060a10"], 120);
  const kpi = (
    id: string,
    v: string,
    l: string,
    x: number,
    y: number,
    c: string,
    s: number,
  ): MotionElement[] => [
    panel(`${id}c`, box(x, y, 300, 200), {
      fill: "#131b28",
      border: "#26303f",
      borderWidth: 2,
      radius: 18,
      anim: POP(s, 0.4),
    }),
    bigText(`${id}v`, v, y - 20, {
      size: 62,
      color: c,
      cx: x,
      width: 280,
      start: s,
      anim: FADE(s + 0.15),
    }),
    label(`${id}l`, l, y + 55, {
      size: 28,
      color: "#8fa0bd",
      cx: x,
      width: 280,
      start: s,
      anim: FADE(s + 0.25),
    }),
  ];
  return scene(
    "s5",
    "dashboard",
    12,
    [
      bigText("t", "LIVE 대시보드", 340, {
        size: 56,
        color: "#8fa0bd",
        start: 0.1,
        anim: FADE(0.2),
      }),
      ...kpi("a", "12.4조", "Revenue", 260, 560, "#4aa3ff", 0.3),
      ...kpi("b", "3.1조", "Cash Flow", 560, 560, "#2ee66a", 0.6),
      ...kpi("c", "3.4%", "Dividend", 820, 560, YELLOW, 0.9),
      el({
        id: "line",
        type: "line-chart",
        transform: box(360, 1050, 560, 520),
        props: {
          values: [30, 42, 38, 55, 62, 78, 95],
          color: "#4aa3ff",
          area: true,
          strokeWidth: 6,
          yTicks: [
            [0, "0"],
            [50, "50"],
            [100, "100"],
          ],
        },
        animations: [...FADE(1.4, 0.7), kenBurns(1.4, 8, 1.0, 1.06)],
        zIndex: 2,
      }),
      el({
        id: "bars",
        type: "bar-chart",
        transform: box(820, 1050, 300, 520),
        props: {
          values: [40, 62, 55, 88],
          labels: ["1Q", "2Q", "3Q", "4Q"],
          color: "#2ee66a",
          gap: 16,
        },
        animations: [enter("slide-up", 2.0, 0.6, { distance: 200 })],
        zIndex: 2,
      }),
      // "donut" gauge faked with concentric rings + %
      dot("ring", CX, 1500, 120, YELLOW, { start: 3.0, anim: POP(3.0, 0.5), z: 3 }),
      dot("ringi", CX, 1500, 84, "#070b12", { start: 3.0, z: 4 }),
      label("rl", "ROE 22%", 1500, {
        size: 40,
        color: WHITE,
        start: 3.2,
        z: 5,
        anim: FADE(3.4),
      }),
      label("m", "Margin 18%  ·  성장 살아있다", 1650, {
        size: 36,
        color: "#a9b6cc",
        start: 4.0,
        anim: FADE(4.2),
      }),
      dipOut(12, 0.7),
    ],
    navy,
  );
}

// ── Scene 6 (52–64) — Into the chart: crisis timeline ───────────────────────────
function s6(): Scene {
  const bg = gradient(["#0a0d14", "#0f1a2e", "#080b12"], 110);
  const event = (
    id: string,
    year: string,
    txt: string,
    color: string,
    s: number,
  ): MotionElement[] => [
    panel(`${id}c`, box(CX, 1500, 760, 150), {
      fill: "#101827dd",
      border: color,
      borderWidth: 2,
      radius: 18,
      start: s,
      duration: 2.6,
      anim: POP(s, 0.4),
    }),
    bigText(`${id}y`, year, 1470, {
      size: 52,
      color,
      start: s,
      duration: 2.6,
      cx: 320,
      width: 260,
      anim: FADE(s + 0.1),
    }),
    label(`${id}t`, txt, 1520, {
      size: 38,
      color: "#dbe4f0",
      start: s,
      duration: 2.6,
      cx: 660,
      width: 440,
      anim: FADE(s + 0.2),
    }),
  ];
  return scene(
    "s6",
    "timeline",
    12,
    [
      label("t", "위기를 지나온 자본", 340, {
        size: 50,
        color: "#8fa0bd",
        start: 0.1,
        anim: FADE(0.2),
      }),
      el({
        id: "ch",
        type: "line-chart",
        transform: box(CX, 920, 940, 900),
        props: {
          values: [100, 128, 70, 96, 150, 90, 140, 210, 175, 240],
          color: "#2ee66a",
          area: true,
          strokeWidth: 8,
          yTicks: [
            [50, "50"],
            [130, "130"],
            [210, "210"],
          ],
        },
        animations: [...FADE(0.4, 0.8), kenBurns(0.4, 11, 1.0, 1.18)],
        zIndex: 2,
      }),
      ...event("e1", "2000", "닷컴 버블", "#ff6b6b", 1.6),
      ...event("e2", "2008", "금융위기", "#ffb020", 4.2),
      ...event("e3", "2020", "팬데믹", "#4aa3ff", 6.8),
      ...event("e4", "2026", "회복, 그리고 신고가", "#2ee66a", 9.2),
      dipOut(12, 0.7),
    ],
    bg,
  );
}

// ── Scene 7 (64–74) — Photo montage → Ronald Read ───────────────────────────────
function s7(): Scene {
  const sepia = gradient(["#0f0b07", "#241a10", "#0c0805"], 115);
  // Each "photo" is an abstract composition (framed panel + soft subject glow + silhouette),
  // not a blank rectangle — real image assets aren't wired, so it's staged with shapes.
  const photos: Array<[string, string, string, number]> = [
    ["#2a1c0e", "#c98a3a", "주유소", 0.0],
    ["#161c28", "#7fa0c8", "청소부", 1.0],
    ["#232016", "#c8b24a", "사무실", 2.0],
    ["#2a1614", "#d88a6a", "가족", 3.0],
    ["#141c26", "#6ab0d8", "도시", 4.0],
    ["#1e160f", "#c9a060", "노년", 5.0],
  ];
  const frames = photos.flatMap(([fill, accent, cap, s], i) => [
    panel(`p${i}`, box(CX, 820, 620, 720), {
      fill,
      border: "#5a4326",
      borderWidth: 2,
      radius: 8,
      start: s,
      duration: 1.0,
      anim: [...FADE(s, 0.25), kenBurns(s, 1.0, 1.0, 1.14)],
      z: 2,
    }),
    dot(`pg${i}`, CX, 720, 190, accent, {
      start: s,
      duration: 1.0,
      anim: FADE(s + 0.05, 0.3),
      z: 3,
    }),
    dot(`ps${i}`, CX, 900, 90, "#0c0a08", { start: s, duration: 1.0, z: 4 }),
    label(`pc${i}`, cap, 1300, {
      size: 44,
      color: "#e8d3ad",
      start: s,
      duration: 1.0,
      anim: FADE(s + 0.15),
    }),
  ]);
  return scene(
    "s7",
    "photos",
    10,
    [
      ...frames,
      panel("last", box(CX, 820, 660, 760), {
        fill: "#1a140e",
        border: "#7a5a2e",
        borderWidth: 3,
        radius: 8,
        start: 6.2,
        anim: [...FADE(6.2, 0.6), kenBurns(6.2, 3.8, 1.0, 1.1)],
        z: 2,
      }),
      bigText("name", "Ronald Read", 780, {
        size: 84,
        color: "#e8d9bf",
        start: 6.6,
        z: 5,
        anim: FADE(6.8, 0.6),
      }),
      bigText("nk", "Nobody knew.", 1360, {
        size: 76,
        color: WHITE,
        start: 7.6,
        z: 5,
        anim: [...FADE(7.8, 0.7), kenBurns(7.6, 2.4, 1.0, 1.08)],
      }),
      dipOut(10, 0.8),
    ],
    sepia,
  );
}

// ── Scene 8 (74–82) — The number ────────────────────────────────────────────────
function s8(): Scene {
  return scene(
    "s8",
    "number",
    8,
    [
      panel("glow", box(CX, 960, 980, 520), {
        fill: YELLOW,
        radius: 260,
        opacity: 0.1,
        start: 1.0,
        anim: FADE(1.2, 1.2),
      }),
      bigText("n", "$8,000,000", 960, {
        size: 150,
        color: YELLOW,
        start: 0.8,
        anim: [...FADE(1.0, 1.4), kenBurns(0.8, 7, 1.0, 1.12)],
      }),
      label("l", "청소부가 남긴 유산", 1200, {
        size: 40,
        color: "#8a94a6",
        start: 4.0,
        anim: FADE(4.3),
      }),
      dipOut(8, 0.9),
    ],
    BLACK,
  );
}

// ── Scene 9 (82–88) — Time. Discipline. Patience. ───────────────────────────────
function s9(): Scene {
  return scene(
    "s9",
    "values",
    6,
    [
      bigText("n", "$8M", 480, {
        size: 90,
        color: "#5a5a3a",
        start: 0.0,
        anim: FADE(0.1, 0.6),
      }),
      bigText("w1", "Time.", 800, {
        size: 130,
        color: WHITE,
        start: 0.6,
        anim: FADE(0.7, 0.7),
      }),
      bigText("w2", "Discipline.", 990, {
        size: 130,
        color: WHITE,
        start: 1.6,
        anim: [enter("slide-left", 1.6, 0.6, { distance: 400 })],
      }),
      bigText("w3", "Patience.", 1180, {
        size: 130,
        color: YELLOW,
        start: 2.6,
        anim: [...POP(2.6, 0.6), kenBurns(2.6, 3.4, 1.0, 1.12)],
      }),
      dipOut(6, 0.8),
    ],
    BLACK,
  );
}

// ── Scene 10 (88–92) — Montage flash → brand ────────────────────────────────────
function s10(): Scene {
  const words = ["Typography", "Charts", "Timeline", "Numbers", "Camera"];
  const flash = words.map((w, i) =>
    bigText(`f${i}`, w, 960, {
      size: 96,
      color: i % 2 ? YELLOW : WHITE,
      start: i * 0.22,
      duration: 0.22,
      anim: [enter("pop-in", i * 0.22, 0.14)],
    }),
  );
  return scene(
    "s10",
    "brand",
    4.2,
    [
      ...flash,
      bigText("b", "YouTube Motion Studio", 860, {
        size: 78,
        color: WHITE,
        start: 1.3,
        anim: [...FADE(1.4, 0.7), kenBurns(1.3, 2.9, 1.0, 1.06)],
      }),
      bigText("t1", "Create Stories.", 1080, {
        size: 88,
        color: YELLOW,
        start: 2.2,
        anim: FADE(2.4, 0.6),
      }),
      label("t2", "Not Slides.", 1210, {
        size: 56,
        color: "#9aa3b2",
        start: 2.9,
        anim: FADE(3.1),
      }),
    ],
    BLACK,
  );
}

function ultimate(): MotionProject {
  return project(
    "ultimate-90",
    "Ultimate Showcase — 90s",
    [s1(), s2(), s3(), s4(), s5(), s6(), s7(), s8(), s9(), s10()],
    {
      style: "Apple × Bloomberg × MagnatesMedia × Netflix",
      accent: YELLOW,
      note: "single continuous ~90s cinematic showreel",
    },
  );
}

export const SCENARIOS: ScenarioDef[] = [
  {
    id: "ultimate-90",
    name: "Ultimate Showcase — 90s",
    style: "Apple × Bloomberg × MagnatesMedia × Netflix",
    featuresTested: [
      "typography",
      "charts",
      "dashboard",
      "timeline",
      "camera-push",
      "photo-montage",
      "logos",
      "data-viz",
      "scene-bridges",
    ],
    build: ultimate,
    posterTime: 78.0,
  },
];
