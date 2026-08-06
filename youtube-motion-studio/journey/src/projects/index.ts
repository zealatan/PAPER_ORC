/**
 * "The Journey of Time" — the director's challenge. One ~74s film, not an example reel. Time is the
 * story; money is the vehicle. The engine has no camera, no morph, no cross-scene compositing and
 * cuts are hard, so continuity is built from MATCH CUTS: the last shape of a chapter and the first
 * shape of the next share position + size, and a keyframe-scale "camera" carries momentum across the
 * cut — a hard cut reads as an object morph / push-through, never a fade. Each chapter uses a
 * different transition (circle→donut, camera-into-chart, number zoom-through, dots→logos, photos
 * merge, card-becomes-background, number explosion, pull-out); the clock that opens the film closes it.
 *
 * TIMING MODEL (important): the timeline feeds each element `sceneLocalTime - timing.start` to its
 * animations, so animation/keyframe `start` is ELEMENT-RELATIVE. Convention here: `start` places the
 * element on the scene timeline, `duration` is how long it lives, and every animation begins at 0
 * (element birth). Helpers below enforce this.
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
const CY = 900;
const YELLOW = "#ffd000";
const WHITE = "#ffffff";

// Element-relative animation helpers (fire at element birth).
const IN = (d = 0.7) => [enter("fade-in", 0, d)];
const POPIN = (d = 0.45) => [enter("pop-in", 0, d)];
const KB = (dur: number, from: number, to: number) => kenBurns(0, dur, from, to);
const UP = (d = 0.6, dist = 240) => [enter("slide-up", 0, d, { distance: dist })];

function ring(
  idp: string,
  color: string,
  inner: string,
  r: number,
  start: number,
  duration: number,
  anim: ReturnType<typeof IN>,
): MotionElement[] {
  return [
    dot(`${idp}o`, CX, CY, r, color, { start, duration, anim, z: 3 }),
    dot(`${idp}i`, CX, CY, r * 0.82, inner, { start, duration, z: 4 }),
  ];
}

function around(cx: number, cy: number, r: number, n: number): Array<[number, number]> {
  return Array.from({ length: n }, (_, i) => {
    const a = (i / n) * Math.PI * 2 - Math.PI / 2;
    return [cx + Math.cos(a) * r, cy + Math.sin(a) * r] as [number, number];
  });
}

// ── Chapter 1 · Time (0–10) — slow, tension, the clock is born ───────────────────
function ch1(): Scene {
  return scene(
    "c1",
    "time",
    10,
    [
      dot("depth", CX, CY, 520, "#0c0c0c", {
        start: 0,
        duration: 10,
        anim: [...IN(1.0), KB(10, 1.0, 1.3)],
        z: 1,
      }),
      ...ring("clk", "#20242c", "#050505", 200, 0.3, 9.7, [
        ...IN(1.2),
        KB(9.7, 0.9, 1.15),
      ]),
      panel("h1", box(CX, CY - 90, 10, 150), {
        fill: WHITE,
        radius: 5,
        start: 2.4,
        duration: 7.6,
        anim: IN(0.25),
      }),
      panel("h2", box(CX + 95, CY, 150, 10), {
        fill: WHITE,
        radius: 5,
        start: 3.0,
        duration: 7.0,
        anim: IN(0.2),
      }),
      panel("h3", box(CX, CY + 90, 10, 150), {
        fill: YELLOW,
        radius: 5,
        start: 3.5,
        duration: 6.5,
        anim: IN(0.18),
      }),
      label("t", "TIME", CY, {
        size: 72,
        color: "#6a6a6a",
        start: 5.0,
        duration: 5.0,
        anim: IN(1.2),
        z: 6,
      }),
      label("l", "가장 조용한 힘", CY + 340, {
        size: 40,
        color: "#4a4a4a",
        start: 6.4,
        duration: 3.6,
        anim: IN(0.7),
      }),
    ],
    gradient(["#000000", "#0a0a0c", "#000000"], 120),
  );
}

// ── Chapter 2 · Time becomes Data (10–28) — 18s LONG TAKE, camera into the chart ──
function ch2(): Scene {
  const seg = around(CX, CY, 200, 12).map(([x, y], i) =>
    dot(`sg${i}`, x, y, 16, i < 8 ? "#2ee66a" : "#20242c", {
      start: 0.2 + i * 0.12,
      duration: 5.0,
      anim: POPIN(0.3),
      z: 5,
    }),
  );
  return scene(
    "c2",
    "data",
    18,
    [
      // MATCH: opens on ch1's clock geometry → the circle morphs into a donut chart
      ...ring("clk", "#20242c", "#04120a", 200, 0, 5.5, [KB(5.5, 1.15, 1.4)]),
      ...seg,
      label("pct", "68%", CY, {
        size: 88,
        color: WHITE,
        start: 1.2,
        duration: 4.0,
        anim: IN(0.6),
        z: 8,
      }),
      label("dl", "배당 성향", CY + 150, {
        size: 34,
        color: "#7fd6a0",
        start: 1.6,
        duration: 3.4,
        anim: IN(0.6),
        z: 8,
      }),
      // camera pushes INTO a chart that grows out of the donut center (continuous scale momentum)
      el({
        id: "ch",
        type: "line-chart",
        transform: box(CX, CY + 40, 960, 820),
        props: {
          values: [8, 12, 10, 20, 30, 26, 44, 60, 80, 110, 150, 205],
          color: "#2ee66a",
          area: true,
          strokeWidth: 8,
          yTicks: [
            [0, "0"],
            [70, "70"],
            [140, "140"],
            [210, "210"],
          ],
        },
        start: 5.0,
        duration: 13,
        animations: [...IN(1.4), KB(13, 0.55, 1.5)],
        zIndex: 2,
      }),
      label("cl", "시간이 데이터가 된다", 420, {
        size: 46,
        color: "#9adcb6",
        start: 6.0,
        duration: 5.0,
        anim: IN(0.7),
        z: 6,
      }),
      // numbers count up along the curve, then the last one fills the frame (zoom-through)
      bigText("n1", "$120,000", CY, {
        size: 96,
        color: WHITE,
        start: 11.5,
        duration: 1.6,
        anim: IN(0.4),
        z: 10,
      }),
      bigText("n2", "$540,000", CY, {
        size: 120,
        color: WHITE,
        start: 13.1,
        duration: 1.6,
        anim: IN(0.4),
        z: 10,
      }),
      bigText("n3", "$1,240,000", CY, {
        size: 150,
        color: YELLOW,
        start: 14.7,
        duration: 3.3,
        anim: [...IN(0.5), KB(3.3, 1.0, 2.8)],
        z: 11,
      }),
    ],
    gradient(["#04100a", "#0a2016", "#030906"], 120),
  );
}

// ── Chapter 3 · Data becomes Companies (28–44) — dots→logos, photos merge, card→bg ─
function ch3(): Scene {
  const cities: Array<[string, number, number]> = [
    ["뉴욕", 260, 720],
    ["런던", 470, 640],
    ["서울", 720, 600],
    ["도쿄", 840, 760],
    ["싱가포르", 560, 940],
  ];
  const logoColors = ["#e6e6e6", "#ff4757", "#4aa3ff", "#2ee66a", YELLOW];
  const links = [
    [260, 720, 470, 640],
    [470, 640, 720, 600],
    [720, 600, 840, 760],
    [840, 760, 560, 940],
    [560, 940, 260, 720],
  ];
  const linkEls = links.map(([x1, y1, x2, y2], i) => {
    const mx = (x1 + x2) / 2,
      my = (y1 + y2) / 2;
    const len = Math.hypot(x2 - x1, y2 - y1);
    const ang = (Math.atan2(y2 - y1, x2 - x1) * 180) / Math.PI;
    return panel(`lk${i}`, box(mx, my, len, 4, { rotation: ang }), {
      fill: "#3a6ea5",
      radius: 2,
      opacity: 0.6,
      start: 0.6 + i * 0.12,
      duration: 4.2,
      anim: IN(0.4),
    });
  });
  const cityDots = cities.map(([, x, y], i) =>
    dot(`cd${i}`, x, y, 16, YELLOW, {
      start: 0.3 + i * 0.12,
      duration: 4.2,
      anim: IN(0.3),
      z: 4,
    }),
  );
  const cityLabels = cities.map(([name, x, y], i) =>
    label(`cn${i}`, name, y + 54, {
      size: 28,
      color: "#cdd9ee",
      cx: x,
      width: 200,
      start: 0.5 + i * 0.12,
      duration: 3.8,
      anim: IN(0.5),
    }),
  );
  // MATCH: logos land on the SAME positions as the city dots → the map becomes the companies
  const logos = cities.map(([, x, y], i) =>
    el({
      id: `lg${i}`,
      type: "topic-circle",
      transform: box(x, y, 150, 150),
      props: {
        label: ["A", "C", "J", "M", "V"][i],
        fill: logoColors[i],
        color: "#0a0a0a",
        fontSize: 74,
      },
      start: 5.0 + i * 0.18,
      duration: 3.2,
      animations: POPIN(0.4),
      zIndex: 6,
    }),
  );
  // photos merge: four spread panels, then one panel scales up over them
  const photos = [
    [300, 720],
    [780, 720],
    [300, 1080],
    [780, 1080],
  ].map(([x, y], i) =>
    panel(`ph${i}`, box(x, y, 260, 300), {
      fill: ["#241a10", "#1c2230", "#22201a", "#182028"][i],
      border: "#5a4326",
      borderWidth: 2,
      radius: 10,
      start: 8.6 + i * 0.1,
      duration: 2.0,
      anim: IN(0.3),
      z: 3,
    }),
  );
  return scene(
    "c3",
    "companies",
    16,
    [
      ...linkEls,
      ...cityDots,
      ...cityLabels,
      label("m", "세계는 하나로 연결된다", 400, {
        size: 44,
        color: WHITE,
        start: 2.2,
        duration: 3.2,
        anim: IN(0.6),
        z: 7,
      }),
      ...logos,
      label("lgl", "세상을 움직이는 기업", 1320, {
        size: 42,
        color: "#c9d3e4",
        start: 5.6,
        duration: 2.6,
        anim: IN(0.5),
        z: 7,
      }),
      ...photos,
      panel("merge", box(CX, 900, 640, 760), {
        fill: "#161d12",
        border: "#3a5a2e",
        borderWidth: 2,
        radius: 14,
        start: 10.0,
        duration: 2.2,
        anim: [...IN(0.5), KB(2.2, 0.7, 1.1)],
        z: 5,
      }),
      label("mgl", "하나의 이야기로", 900, {
        size: 48,
        color: "#e8d3ad",
        start: 10.6,
        duration: 1.6,
        anim: IN(0.5),
        z: 6,
      }),
      // card grows to fill the frame → becomes the background of ch4 (color match)
      panel("card", box(CX, CY, 720, 460), {
        fill: "#0a1a2e",
        border: "#1d3a5f",
        borderWidth: 2,
        radius: 28,
        start: 12.4,
        duration: 3.6,
        anim: [...IN(0.5), KB(3.6, 1.0, 3.4)],
        z: 8,
      }),
      label("cardl", "그리고, 부(富)", CY, {
        size: 60,
        color: WHITE,
        start: 13.0,
        duration: 2.4,
        anim: IN(0.5),
        z: 9,
      }),
    ],
    gradient(["#050912", "#0a1832", "#04070f"], 120),
  );
}

// ── Chapter 4 · Companies become Wealth (44–60) — explosive, text as object ──────
function ch4(): Scene {
  return scene(
    "c4",
    "wealth",
    16,
    [
      label("t", "주가는 흔들려도", 380, {
        size: 46,
        color: "#8fb4d6",
        start: 0.3,
        duration: 3.4,
        anim: IN(0.5),
        z: 6,
      }),
      el({
        id: "line",
        type: "line-chart",
        transform: box(CX, 980, 940, 820),
        props: {
          values: [100, 130, 90, 120, 175, 110, 160, 230],
          color: "#4aa3ff",
          area: true,
          strokeWidth: 8,
          yTicks: [
            [80, "80"],
            [150, "150"],
            [230, "230"],
          ],
        },
        start: 0.3,
        duration: 10.5,
        animations: [...IN(1.0), KB(10.5, 1.0, 1.2)],
        zIndex: 2,
      }),
      label("t2", "배당은 멈추지 않는다", 380, {
        size: 46,
        color: "#7fd6a0",
        start: 4.0,
        duration: 2.8,
        anim: IN(0.5),
        z: 6,
      }),
      el({
        id: "bars",
        type: "bar-chart",
        transform: box(CX, 1080, 820, 560),
        props: {
          values: [30, 42, 51, 63, 78, 96],
          labels: ["21", "22", "23", "24", "25", "26"],
          color: "#2ee66a",
          gap: 20,
        },
        start: 4.4,
        duration: 6.5,
        animations: UP(0.7, 260),
        zIndex: 3,
      }),
      // text as a 3D object: skewed, scaling past the camera
      el({
        id: "comp",
        type: "title",
        transform: box(CX, CY, W - 80, 260, { skewX: -14, rotation: -4 }),
        props: {
          text: "복리",
          fontSize: 300,
          color: YELLOW,
          align: "center",
          fontWeight: 900,
          fontFamily: "Black Han Sans",
        },
        start: 7.4,
        duration: 3.4,
        animations: [...IN(0.5), KB(3.4, 0.8, 1.6)],
        zIndex: 8,
      }),
      label("cl", "시간이 돈을 키운다", CY + 300, {
        size: 44,
        color: "#e8d9a0",
        start: 8.2,
        duration: 2.6,
        anim: IN(0.5),
        z: 8,
      }),
      // number explosion fills the frame
      dot("boom", CX, CY, 60, YELLOW, {
        start: 11.0,
        duration: 5.0,
        anim: [KB(1.4, 0.2, 15)],
        z: 9,
      }),
      bigText("n", "$8,000,000", CY, {
        size: 150,
        color: "#0a0a0a",
        start: 11.9,
        duration: 4.1,
        anim: [...IN(0.4), KB(4.1, 1.0, 1.9)],
        z: 11,
      }),
      label("nl", "40년이 만든 숫자", CY + 240, {
        size: 42,
        color: "#3a3a2a",
        start: 12.8,
        duration: 3.2,
        anim: IN(0.5),
        z: 11,
      }),
    ],
    gradient(["#0a1a2e", "#0d2440", "#050d18"], 120),
  );
}

// ── Chapter 5 · Everything returns to Time (60–74) — pull out, the clock returns ──
function ch5(): Scene {
  return scene(
    "c5",
    "return",
    14,
    [
      dot("depth", CX, CY, 520, "#0c0c0c", {
        start: 0,
        duration: 14,
        anim: [KB(14, 1.35, 0.95)],
        z: 1,
      }),
      // MATCH to ch1: the clock returns — camera pulls OUT (reverse zoom)
      ...ring("clk", "#20242c", "#050505", 200, 0.3, 13.7, [
        ...IN(1.4),
        KB(13.7, 1.4, 1.0),
      ]),
      panel("h1", box(CX, CY - 90, 10, 150), {
        fill: "#6a6a6a",
        radius: 5,
        start: 1.2,
        duration: 12.8,
        anim: IN(0.8),
      }),
      panel("h2", box(CX + 95, CY, 150, 10), {
        fill: "#6a6a6a",
        radius: 5,
        start: 1.6,
        duration: 12.4,
        anim: IN(0.8),
      }),
      bigText("m1", "The greatest investment", 1420, {
        size: 58,
        color: "#8a8a8a",
        start: 4.0,
        duration: 10,
        anim: IN(1.0),
        z: 6,
      }),
      bigText("m2", "was never money.", 1510, {
        size: 58,
        color: "#8a8a8a",
        start: 5.4,
        duration: 8.6,
        anim: IN(1.0),
        z: 6,
      }),
      bigText("m3", "It was time.", 1510, {
        size: 96,
        color: YELLOW,
        start: 8.4,
        duration: 5.6,
        anim: [...IN(1.0), KB(5.6, 1.0, 1.08)],
        z: 7,
      }),
      label("brand", "YouTube Motion Studio", 1720, {
        size: 34,
        color: "#4a4a4a",
        start: 11.0,
        duration: 3.0,
        anim: IN(0.8),
        z: 6,
      }),
    ],
    gradient(["#000000", "#080808", "#000000"], 120),
  );
}

function journeyFilm(): MotionProject {
  return project(
    "journey-time",
    "The Journey of Time",
    [ch1(), ch2(), ch3(), ch4(), ch5()],
    {
      theme: "Time is the greatest investment",
      accent: YELLOW,
      note: "director's challenge — one continuous ~74s film, match-cut transitions",
    },
  );
}

export const SCENARIOS: ScenarioDef[] = [
  {
    id: "journey-time",
    name: "The Journey of Time",
    style: "Apple × Bloomberg × MagnatesMedia × Netflix (not copied)",
    featuresTested: [
      "match-cut",
      "camera-push",
      "circle-to-donut",
      "camera-into-chart",
      "number-zoom-through",
      "map-to-logos",
      "photo-merge",
      "card-to-background",
      "text-as-object",
      "long-take",
      "clock-bookend",
    ],
    build: journeyFilm,
    posterTime: 52.0,
  },
];
