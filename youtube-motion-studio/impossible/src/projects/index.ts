/**
 * "One Impossible Camera Shot" — a single-scene 10s take (zero cuts). The world changes around a
 * camera that never stops: a glowing particle becomes a watch screw, gears stretch into chart bars,
 * the center hole becomes a tunnel the camera flies through, a line chart the camera rides past
 * company logos, particles rise into $8,000,000, the camera passes THROUGH the number, and only the
 * watch remains — one tick, black, "Time built everything."
 *
 * To read as a lens rather than vector art, this leans on: PARALLAX DEPTH (faint layers scaling at
 * different rates), FOREGROUND OCCLUSION (a large dark shape sweeps past the lens at each hand-off),
 * and a downstream cinematic grade (bloom + vignette + grain, applied in the pipeline post-pass).
 * One scene ⇒ film-time == scene-local; animations are element-relative (begin at element birth).
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
const GOLD = "#ffd000";
const WHITE = "#ffffff";
const IN = (d = 0.5) => [enter("fade-in", 0, d)];
const KB = (dur: number, from: number, to: number) => kenBurns(0, dur, from, to);

function ring(
  idp: string,
  color: string,
  inner: string,
  r: number,
  start: number,
  duration: number,
  anim: ReturnType<typeof IN>,
  z = 4,
): MotionElement[] {
  return [
    dot(`${idp}o`, CX, CY, r, color, { start, duration, anim, z }),
    dot(`${idp}i`, CX, CY, r * 0.78, inner, { start, duration, z: z + 1 }),
  ];
}
function around(r: number, n: number): Array<[number, number]> {
  return Array.from({ length: n }, (_, i) => {
    const a = (i / n) * Math.PI * 2 - Math.PI / 2;
    return [CX + Math.cos(a) * r, CY + Math.sin(a) * r] as [number, number];
  });
}
/** A large dark shape that scales past the lens over its life — reads as the camera passing an object. */
function occlude(
  id: string,
  start: number,
  dur: number,
  from = 0.6,
  to = 9,
): MotionElement {
  return dot(id, CX, CY, 180, "#040507", {
    start,
    duration: dur,
    anim: [KB(dur, from, to)],
    z: 9,
  });
}

function film(): Scene {
  const gearTeeth = around(215, 16).map(([x, y], i) =>
    dot(`gt${i}`, x, y, 13, i % 2 ? "#39424f" : "#5a6577", {
      start: 1.5 + i * 0.03,
      duration: 1.5,
      anim: [enter("pop-in", 0, 0.18)],
      z: 6,
    }),
  );
  const pie = around(200, 12).map(([x, y], i) =>
    dot(`pie${i}`, x, y, 22, ["#4aa3ff", "#2ee66a", GOLD, "#ff5a5a"][i % 4]!, {
      start: 2.4 + i * 0.04,
      duration: 1.3,
      anim: [enter("pop-in", 0, 0.2)],
      z: 6,
    }),
  );
  const logos: Array<[string, string, number, number]> = [
    ["A", "#e8e8e8", 300, 1200],
    ["M", "#2ee66a", 470, 1120],
    ["V", GOLD, 640, 1080],
    ["J", "#4aa3ff", 780, 980],
    ["C", "#ff5a5a", 900, 900],
  ];
  const checkpoints = logos.flatMap(([ch, col, x, y], i) => [
    dot(`cp${i}`, x, y, 12, WHITE, {
      start: 4.2 + i * 0.22,
      duration: 1.6,
      anim: [enter("pop-in", 0, 0.2)],
      z: 7,
    }),
    el({
      id: `lg${i}`,
      type: "topic-circle",
      transform: box(x, y - 120, 118, 118),
      props: { label: ch, fill: col, color: "#0a0a0a", fontSize: 58 },
      start: 4.3 + i * 0.22,
      duration: 1.4,
      animations: [enter("pop-in", 0, 0.3)],
      zIndex: 8,
    }),
  ]);
  const lift = around(380, 22).map(([x, y], i) =>
    dot(`lf${i}`, x, y - 30, 13, GOLD, {
      start: 6.4 + i * 0.02,
      duration: 1.4,
      anim: IN(0.25),
      z: 8,
    }),
  );
  const rewind = around(340, 20).map(([x, y], i) =>
    dot(`rw${i}`, x, y, 15, "#c9a020", {
      start: 8.7 + i * 0.01,
      duration: 0.6,
      anim: IN(0.12),
      z: 8,
    }),
  );

  return scene(
    "one",
    "impossible",
    10,
    [
      // ── parallax depth: three layers pushing at different rates (near = faster) ──
      dot("depthF", CX, CY, 720, "#060708", {
        start: 0,
        duration: 10,
        anim: [KB(10, 0.8, 1.9)],
        z: 0,
      }),
      dot("depthM", CX, CY, 460, "#0a0b0d", {
        start: 0,
        duration: 10,
        anim: [KB(10, 0.9, 1.45)],
        z: 0,
      }),
      dot("depthN", CX, CY, 240, "#101216", {
        start: 0,
        duration: 10,
        anim: [KB(10, 1.0, 1.2)],
        z: 0,
      }),

      // ── Phase 1 (0–2): glowing particle → watch screw ──
      panel("glow0", box(CX, CY, 360, 360), {
        fill: WHITE,
        radius: 200,
        opacity: 0.1,
        start: 0,
        duration: 1.6,
        anim: [...IN(0.5), KB(1.6, 0.05, 1.0)],
        z: 9,
      }),
      dot("star", CX, CY, 150, WHITE, {
        start: 0,
        duration: 1.7,
        anim: [...IN(0.4), KB(1.7, 0.03, 1.0)],
        z: 11,
      }),
      ...ring(
        "screw",
        "#2b313c",
        "#050608",
        210,
        1.1,
        1.7,
        [...IN(0.4), KB(1.7, 0.95, 1.25)],
        5,
      ),

      // ── Phase 2 (2–4): gears → bars/donut → fly through the hole (occlusion pass) ──
      ...gearTeeth,
      ...pie,
      label("pl", "시간은 형태를 바꾼다", 1440, {
        size: 40,
        color: "#8fa0bd",
        start: 2.5,
        duration: 1.0,
        anim: IN(0.4),
        z: 12,
      }),
      occlude("thru1", 3.4, 0.9, 1.0, 12),

      // ── Phase 3 (4–6): ride the line chart, logos belong to the world ──
      el({
        id: "graph",
        type: "line-chart",
        transform: box(CX, 1080, 1020, 780),
        props: {
          values: [8, 14, 11, 24, 40, 32, 58, 86, 130, 150],
          color: "#2ee66a",
          area: true,
          strokeWidth: 10,
        },
        start: 3.9,
        duration: 2.2,
        animations: [...IN(0.5), KB(2.2, 0.8, 1.55)],
        zIndex: 3,
      }),
      ...checkpoints,

      // ── Phase 4 (6–8): launch up, particles gather into the monumental number (HERO frame) ──
      occlude("thru2", 6.0, 0.7, 1.0, 10),
      panel("nglow", box(CX, CY, 1040, 560), {
        fill: GOLD,
        radius: 280,
        opacity: 0.13,
        start: 7.0,
        duration: 2.0,
        anim: IN(0.5),
        z: 10,
      }),
      ...lift,
      bigText("num", "$8,000,000", CY, {
        size: 156,
        color: GOLD,
        start: 7.1,
        duration: 1.7,
        anim: [enter("pop-in", 0, 0.5), KB(1.7, 0.72, 1.18)],
        z: 12,
      }),
      label("nl", "TIME × PATIENCE", CY + 250, {
        size: 40,
        color: "#8a7a2a",
        start: 7.6,
        duration: 1.2,
        anim: IN(0.4),
        z: 12,
      }),

      // ── Phase 5 (8–10): camera passes THROUGH the number → only the watch → tick → line ──
      occlude("thru3", 8.4, 0.7, 0.8, 14),
      ...rewind,
      ...ring(
        "end",
        "#2b313c",
        "#050608",
        200,
        8.9,
        1.1,
        [...IN(0.3), KB(1.1, 1.9, 1.0)],
        12,
      ),
      panel("hand", box(CX, CY - 78, 8, 126), {
        fill: GOLD,
        radius: 4,
        start: 9.3,
        duration: 0.7,
        anim: IN(0.1),
        z: 14,
      }),
      bigText("end1", "Time built everything.", 1500, {
        size: 56,
        color: "#b0b0b0",
        start: 9.0,
        duration: 1.0,
        anim: IN(0.7),
        z: 13,
      }),
    ],
    gradient(["#000000", "#050607", "#000000"], 120),
  );
}

function impossibleFilm(): MotionProject {
  return project("impossible-shot", "One Impossible Camera Shot", [film()], {
    theme: "One impossible continuous take — time built everything",
    accent: GOLD,
    note: "single-scene 10s; parallax depth + occlusion; cinematic grade applied in post",
  });
}

export const SCENARIOS: ScenarioDef[] = [
  {
    id: "impossible-shot",
    name: "One Impossible Camera Shot",
    style: "Netflix macro doc × Apple keynote — impossible continuous take",
    featuresTested: [
      "single-scene-continuous",
      "parallax-depth",
      "foreground-occlusion",
      "object-handoff",
      "portal-through",
      "hero-frame",
      "particles-to-number",
    ],
    build: impossibleFilm,
    posterTime: 7.7,
  },
];
