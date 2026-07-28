/**
 * "Everything is Connected" — a 10-second one-shot. ONE scene, ONE unbroken timeline: there are no
 * scene cuts at all, so the viewer never feels "a new scene begins." Objects share the optical
 * center and hand off along the timeline — star → watch screw → gears → pie chart → (fly through the
 * hole) → line chart → Apple logo → glass building → dashboard → particles → $8,000,000 → (rewind) →
 * the watch. A continuous keyframe-scale "camera" pushes the whole way; big transitions are
 * zoom-throughs (an object grows past the lens) rather than fades.
 *
 * One scene ⇒ film-time == scene-local time. Animations are element-relative (they begin at the
 * element's own birth), so each object's `start` places it on the single timeline and its animation
 * starts at 0.
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

function film(): Scene {
  const gearTeeth = around(215, 16).map(([x, y], i) =>
    dot(`gt${i}`, x, y, 13, i % 2 ? "#39424f" : "#5a6577", {
      start: 1.5 + i * 0.03,
      duration: 1.4,
      anim: [enter("pop-in", 0, 0.18)],
      z: 6,
    }),
  );
  const pie = around(200, 12).map(([x, y], i) =>
    dot(`pie${i}`, x, y, 22, ["#4aa3ff", "#2ee66a", GOLD, "#ff5a5a"][i % 4]!, {
      start: 2.5 + i * 0.04,
      duration: 1.2,
      anim: [enter("pop-in", 0, 0.2)],
      z: 6,
    }),
  );
  const windows = Array.from({ length: 12 }, (_, i) =>
    panel(
      `win${i}`,
      box(300 + (i % 3) * 240, 640 + Math.floor(i / 3) * 220, 180, 150, { skewX: -18 }),
      {
        fill: "#16324a",
        border: "#2f6a9a",
        borderWidth: 2,
        radius: 6,
        opacity: 0.5,
        start: 6.0 + (i % 3) * 0.06,
        duration: 1.0,
        anim: IN(0.3),
        z: 5,
      },
    ),
  );
  const dash = [
    panel("d1", box(300, 780, 300, 200), {
      fill: "#0e1826",
      border: "#22415f",
      borderWidth: 2,
      radius: 16,
      start: 6.9,
      duration: 1.3,
      anim: [enter("pop-in", 0, 0.3)],
      z: 6,
    }),
    panel("d2", box(760, 780, 300, 200), {
      fill: "#0e1826",
      border: GOLD,
      borderWidth: 2,
      radius: 16,
      start: 7.1,
      duration: 1.1,
      anim: [enter("pop-in", 0, 0.3)],
      z: 6,
    }),
    bigText("d1v", "+128%", 780, {
      size: 66,
      color: "#2ee66a",
      cx: 300,
      width: 280,
      start: 6.95,
      duration: 1.25,
      anim: IN(0.3),
      z: 7,
    }),
    bigText("d2v", "3.4%", 780, {
      size: 66,
      color: GOLD,
      cx: 760,
      width: 280,
      start: 7.15,
      duration: 1.05,
      anim: IN(0.3),
      z: 7,
    }),
    el({
      id: "dch",
      type: "line-chart",
      transform: box(CX, 1120, 820, 420),
      props: {
        values: [20, 34, 28, 52, 70, 96],
        color: "#4aa3ff",
        area: true,
        strokeWidth: 6,
      },
      start: 7.0,
      duration: 1.2,
      animations: IN(0.4),
      zIndex: 5,
    }),
  ];
  const lift = around(360, 20).map(([x, y], i) =>
    dot(`lf${i}`, x, y - 40, 14, GOLD, {
      start: 7.9 + i * 0.015,
      duration: 0.8,
      anim: IN(0.2),
      z: 8,
    }),
  );
  const rewind = around(320, 18).map(([x, y], i) =>
    dot(`rw${i}`, x, y, 15, "#c9a020", {
      start: 9.15 + i * 0.01,
      duration: 0.55,
      anim: IN(0.12),
      z: 8,
    }),
  );

  return scene(
    "one",
    "connected",
    10,
    [
      // continuous depth push for the whole 10s (parallax ground)
      dot("depth", CX, CY, 560, "#0a0a0c", {
        start: 0,
        duration: 10,
        anim: [KB(10, 0.9, 1.25)],
        z: 0,
      }),

      // 0.0–1.6  star → watch screw
      dot("star", CX, CY, 190, WHITE, {
        start: 0,
        duration: 1.7,
        anim: [...IN(0.4), KB(1.7, 0.02, 1.05)],
        z: 10,
      }),
      ...ring(
        "screw",
        "#2b313c",
        "#050608",
        215,
        1.15,
        1.6,
        [...IN(0.4), KB(1.6, 0.95, 1.2)],
        5,
      ),

      // 1.5–2.9  gears
      ...gearTeeth,

      // 2.5–3.7  pie chart (gear becomes data)
      ...pie,
      label("pl", "모든 것은 연결돼 있다", 1420, {
        size: 40,
        color: "#8fa0bd",
        start: 2.6,
        duration: 1.0,
        anim: IN(0.4),
        z: 12,
      }),

      // 3.4–4.3  fly through the hole (dark disc grows past the lens)
      dot("thru", CX, CY, 150, "#04070c", {
        start: 3.4,
        duration: 0.9,
        anim: [KB(0.9, 1.0, 11)],
        z: 9,
      }),

      // 3.9–5.6  line chart, camera rides it
      el({
        id: "graph",
        type: "line-chart",
        transform: box(CX, 1080, 1000, 760),
        props: {
          values: [10, 16, 13, 26, 40, 34, 60, 92, 140],
          color: "#2ee66a",
          area: true,
          strokeWidth: 10,
        },
        start: 3.9,
        duration: 1.9,
        animations: [...IN(0.5), KB(1.9, 0.85, 1.5)],
        zIndex: 3,
      }),

      // 5.2–6.3  the line bends into the Apple logo
      el({
        id: "apple",
        type: "topic-circle",
        transform: box(760, 900, 150, 150),
        props: { label: "", fill: "#e8e8e8", color: "#0a0a0a", fontSize: 90 },
        start: 5.2,
        duration: 1.2,
        animations: [enter("pop-in", 0, 0.4), KB(1.2, 0.6, 2.6)],
        zIndex: 9,
      }),
      label("al", "Apple", 1080, {
        size: 40,
        color: "#c9d3e4",
        cx: 760,
        width: 260,
        start: 5.4,
        duration: 0.9,
        anim: IN(0.3),
        z: 10,
      }),

      // 6.0–7.0  glass skyscraper (logo becomes a reflection) → pass through
      ...windows,

      // 6.9–8.2  dashboard
      ...dash,

      // 7.9–8.7  particles lift
      ...lift,

      // 8.4–9.4  particles gather into the number, it fills the screen
      panel("nglow", box(CX, CY, 1000, 520), {
        fill: GOLD,
        radius: 260,
        opacity: 0.12,
        start: 8.5,
        duration: 1.0,
        anim: IN(0.4),
        z: 10,
      }),
      bigText("num", "$8,000,000", CY, {
        size: 150,
        color: GOLD,
        start: 8.5,
        duration: 1.0,
        anim: [enter("pop-in", 0, 0.4), KB(1.0, 0.7, 1.15)],
        z: 11,
      }),

      // 9.1–9.7  explosion → rewind (particles travel backwards)
      dot("boom", CX, CY, 60, GOLD, {
        start: 9.1,
        duration: 0.6,
        anim: [KB(0.6, 0.3, 16)],
        z: 9,
      }),
      ...rewind,

      // 9.3–10.0  everything was inside the watch — the clock returns, one tick, black
      ...ring(
        "end",
        "#2b313c",
        "#050608",
        200,
        9.35,
        0.65,
        [...IN(0.3), KB(0.65, 1.8, 1.0)],
        12,
      ),
      panel("hand", box(CX, CY - 80, 8, 130), {
        fill: GOLD,
        radius: 4,
        start: 9.7,
        duration: 0.3,
        anim: IN(0.1),
        z: 14,
      }),
    ],
    gradient(["#000000", "#060708", "#000000"], 120),
  );
}

function connectedFilm(): MotionProject {
  return project("oneshot-connected", "Everything is Connected", [film()], {
    theme: "Everything is connected — one continuous shot",
    accent: GOLD,
    note: "single-scene 10s one-shot; AI atmosphere composited underneath via video background",
  });
}

export const SCENARIOS: ScenarioDef[] = [
  {
    id: "oneshot-connected",
    name: "Everything is Connected",
    style: "Netflix doc × Apple keynote — one continuous camera",
    featuresTested: [
      "single-scene-continuous",
      "object-handoff",
      "zoom-through",
      "camera-push",
      "star-to-watch",
      "gear-to-pie",
      "chart-to-logo",
      "particles-to-number",
      "rewind-to-watch",
    ],
    build: connectedFilm,
    posterTime: 4.6,
  },
];
