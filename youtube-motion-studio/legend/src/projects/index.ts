/**
 * "One Legendary Moment" — Director Challenge #003. The whole 10s exists to support ONE frame and
 * ONE second: the camera travels through a single watch and emerges into a monumental glowing
 * financial structure (a compound "universe" — core, concentric orbits, radial data beams, orbiting
 * nodes), holds on it (the hero second), then everything collapses backwards INTO the watch — it was
 * inside it all along. One tick. Black.
 *
 * Single scene (zero cuts): objects hand off around a never-stopping keyframe-scale camera; the
 * fly-into-watch is a zoom-through (the center hole grows past the lens), not a fade. A downstream
 * bloom/vignette/grain grade (see REPORT) turns the vector art into a lens. Timing is element-relative.
 */
import type { MotionElement, MotionProject, Scene } from "@motion-studio/core";
import {
  W,
  bigText,
  box,
  dot,
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
const BGC = "#040507";
const IN = (d = 0.6) => [enter("fade-in", 0, d)];
const KB = (dur: number, from: number, to: number) => kenBurns(0, dur, from, to);

type A = ReturnType<typeof IN>;
function orbit(
  idp: string,
  r: number,
  color: string,
  start: number,
  dur: number,
  anim: A,
  z: number,
): MotionElement[] {
  return [
    dot(`${idp}o`, CX, CY, r, color, { start, duration: dur, anim, z }),
    dot(`${idp}i`, CX, CY, r - 10, BGC, { start, duration: dur, z: z + 1 }),
  ];
}
function around(r: number, n: number, phase = 0): Array<[number, number]> {
  return Array.from({ length: n }, (_, i) => {
    const a = (i / n) * Math.PI * 2 - Math.PI / 2 + phase;
    return [CX + Math.cos(a) * r, CY + Math.sin(a) * r] as [number, number];
  });
}

/** The monumental structure — assembled symmetrically at (CX,CY). This is the hero object. */
function monument(t0: number): MotionElement[] {
  const spokes = Array.from({ length: 18 }, (_, i) =>
    panel(`sp${i}`, box(CX, CY, 5, 1040, { rotation: i * 20 }), {
      fill: GOLD,
      radius: 2,
      opacity: 0.16,
      start: t0 + 0.2,
      duration: 3.2,
      anim: IN(0.6),
      z: 2,
    }),
  );
  const nodes = [
    ...around(210, 8).map(([x, y], i) =>
      dot(`n1_${i}`, x, y, 15, "#4aa3ff", {
        start: t0 + 0.7 + i * 0.03,
        duration: 2.6,
        anim: [enter("pop-in", 0, 0.3)],
        z: 8,
      }),
    ),
    ...around(360, 12, 0.26).map(([x, y], i) =>
      dot(`n2_${i}`, x, y, 14, "#2ee66a", {
        start: t0 + 0.9 + i * 0.03,
        duration: 2.4,
        anim: [enter("pop-in", 0, 0.3)],
        z: 8,
      }),
    ),
    ...around(500, 16, 0.13).map(([x, y], i) =>
      dot(`n3_${i}`, x, y, 12, GOLD, {
        start: t0 + 1.1 + i * 0.025,
        duration: 2.2,
        anim: [enter("pop-in", 0, 0.3)],
        z: 8,
      }),
    ),
  ];
  return [
    panel("mglow", box(CX, CY, 1080, 1080), {
      fill: "#3a2e00",
      radius: 540,
      opacity: 0.25,
      start: t0,
      duration: 3.3,
      anim: IN(0.9),
      z: 1,
    }),
    ...spokes,
    ...orbit("or3", 500, "#5a4a12", t0 + 0.5, 2.8, IN(0.6), 3),
    ...orbit("or2", 360, "#7a6414", t0 + 0.4, 2.9, IN(0.6), 4),
    ...orbit("or1", 210, "#c9a020", t0 + 0.3, 3.0, IN(0.6), 5),
    ...nodes,
    panel("coreglow", box(CX, CY, 360, 360), {
      fill: GOLD,
      radius: 200,
      opacity: 0.3,
      start: t0 + 0.2,
      duration: 3.1,
      anim: IN(0.7),
      z: 6,
    }),
    dot("core", CX, CY, 90, WHITE, {
      start: t0 + 0.25,
      duration: 3.05,
      anim: [...IN(0.5), KB(3.05, 0.7, 1.05)],
      z: 9,
    }),
    bigText("mnum", "8,000,000", CY + 2, {
      size: 92,
      color: "#141414",
      start: t0 + 1.0,
      duration: 2.3,
      anim: IN(0.5),
      z: 10,
    }),
    label("mcap", "복리가 지은 우주", CY + 620, {
      size: 42,
      color: "#8a7a3a",
      start: t0 + 1.4,
      duration: 1.9,
      anim: IN(0.6),
      z: 10,
    }),
  ];
}

function film(): Scene {
  const gears = around(200, 14).map(([x, y], i) =>
    dot(`g${i}`, x, y, 13, i % 2 ? "#39424f" : "#5a6577", {
      start: 2.3 + i * 0.03,
      duration: 2.0,
      anim: [enter("pop-in", 0, 0.2)],
      z: 6,
    }),
  );
  return scene(
    "one",
    "legend",
    10,
    [
      // parallax depth
      dot("dF", CX, CY, 760, "#060708", {
        start: 0,
        duration: 10,
        anim: [KB(10, 0.8, 1.7)],
        z: 0,
      }),
      dot("dN", CX, CY, 300, "#0d0f13", {
        start: 0,
        duration: 10,
        anim: [KB(10, 1.0, 1.25)],
        z: 0,
      }),

      // P1 (0–2) — a tiny metallic reflection in the dark
      dot("glint", CX + 20, CY - 20, 40, "#8a90a0", {
        start: 0.3,
        duration: 2.2,
        anim: [...IN(0.8), KB(2.2, 0.15, 1.0)],
        z: 10,
      }),

      // P2 (2–4) — it becomes a polished watch; gears; hold
      ...(() => {
        const r = [
          dot("wo", CX, CY, 220, "#2b313c", {
            start: 1.6,
            duration: 3.2,
            anim: [...IN(0.6), KB(3.2, 0.85, 1.15)],
            z: 4,
          }),
          dot("wi", CX, CY, 176, "#070a0e", { start: 1.6, duration: 3.2, z: 5 }),
        ];
        return r;
      })(),
      ...gears,
      panel("wh1", box(CX, CY - 80, 9, 150), {
        fill: "#c9cdd4",
        radius: 4,
        start: 2.6,
        duration: 1.8,
        anim: IN(0.2),
        z: 7,
      }),
      panel("wh2", box(CX + 90, CY, 150, 9), {
        fill: GOLD,
        radius: 4,
        start: 3.0,
        duration: 1.4,
        anim: IN(0.2),
        z: 7,
      }),

      // P3 (4–5.5) — fly INTO the watch: the hole becomes a tunnel (occlusion pass), universe assembling behind
      dot("tunnel", CX, CY, 176, BGC, {
        start: 4.0,
        duration: 1.4,
        anim: [KB(1.4, 1.0, 13)],
        z: 3,
      }),

      // P4 (5.5–8.5) — THE MONUMENT (hero frame + hero second) — assembles then holds
      ...monument(5.3),

      // P5 (8.5–10) — collapse backwards: the universe shrinks into the watch again; one tick; black
      dot("collapse", CX, CY, 900, BGC, {
        start: 8.4,
        duration: 0.7,
        anim: [KB(0.7, 1.4, 0.16)],
        z: 11,
      }),
      dot("wo2", CX, CY, 200, "#2b313c", {
        start: 8.8,
        duration: 1.2,
        anim: [...IN(0.4), KB(1.2, 2.2, 1.0)],
        z: 12,
      }),
      dot("wi2", CX, CY, 160, "#050608", { start: 8.8, duration: 1.2, z: 13 }),
      panel("tick", box(CX, CY - 70, 8, 120), {
        fill: GOLD,
        radius: 4,
        start: 9.4,
        duration: 0.6,
        anim: IN(0.1),
        z: 14,
      }),
    ],
    gradient(["#000000", "#040506", "#000000"], 120),
  );
}

function legendFilm(): MotionProject {
  return project("legend-moment", "One Legendary Moment", [film()], {
    theme: "A whole universe inside a single watch",
    accent: GOLD,
    note: "single-scene 10s; built to support one hero frame (the monument) + one hero second",
  });
}

export const SCENARIOS: ScenarioDef[] = [
  {
    id: "legend-moment",
    name: "One Legendary Moment",
    style: "Cinematic macro → monumental data universe → collapse",
    featuresTested: [
      "single-scene-continuous",
      "fly-into-object",
      "monument-hero-frame",
      "parallax-depth",
      "collapse-reveal",
      "watch-bookend",
    ],
    build: legendFilm,
    posterTime: 7.3,
  },
];
