/**
 * Ten directed cinematic scenarios (1080×1920 / 30fps / 5–8s) for real YouTube Shorts. The point is
 * story + direction, not a feature checklist. Design rules: black ground, white type, one yellow
 * accent, one message per screen, hook within 2 seconds. Effects the SVG backend cannot render
 * (blur, particles, camera shake, flash, mask reveal, reflection, motion blur) are staged with
 * design instead: micro-cut jitter for "shake", a white scene for "flash", layered translucent
 * shapes for "glow", full-bleed panels with keyframe scale for "camera push".
 */
import type { MotionElement, MotionProject } from "@motion-studio/core";
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

const FADE = (s: number, d = 0.5) => [enter("fade-in", s, d)];
const POP = (s: number, d = 0.4) => [enter("pop-in", s, d)];
const CX = W / 2;
const YELLOW = "#ffd000";
const BLACK = gradient(["#000000", "#080808"], 90);

// 01 ── Time Is Money ────────────────────────────────────────────────────────────
function timeIsMoney(): MotionProject {
  const chartBg = gradient(["#08110a", "#0d1f14", "#050a07"], 120);
  const coins = Array.from({ length: 18 }, (_, i) =>
    dot(`coin${i}`, 200 + (i % 6) * 140, 760 + Math.floor(i / 6) * 150, 34, YELLOW, {
      anim: POP(0.1 + i * 0.03, 0.3),
      z: 3,
    }),
  );
  return project(
    "01-time-is-money",
    "Time Is Money",
    [
      scene(
        "s1",
        "hook",
        1.3,
        [
          bigText("t", "시간", 940, {
            size: 340,
            color: "#ffffff",
            anim: [...FADE(0.1, 0.6), kenBurns(0, 1.3, 1.0, 1.12)],
          }),
        ],
        BLACK,
      ),
      scene(
        "s2",
        "clock",
        1.1,
        [
          dot("face", CX, 900, 200, "#101418", {
            border: "#3a4150",
            borderWidth: 6,
            anim: [...FADE(0.05, 0.5), kenBurns(0, 1.1, 0.9, 1.05)],
          }),
          panel("h1", box(CX, 830, 12, 150), {
            fill: "#ffffff",
            radius: 6,
            anim: FADE(0.3),
          }),
          panel("h2", box(CX + 55, 900, 120, 12), {
            fill: YELLOW,
            radius: 6,
            anim: FADE(0.4),
          }),
          label("cl", "1분 1초가 자산이다", 1200, {
            size: 44,
            color: "#8a94a6",
            anim: FADE(0.6),
          }),
        ],
        BLACK,
      ),
      scene(
        "s3",
        "tick",
        1.2,
        [
          dot("face", CX, 860, 220, "#0c1510", { border: "#2f6f4a", borderWidth: 6 }),
          panel("t1", box(CX, 720, 12, 150), {
            fill: "#ffffff",
            radius: 6,
            start: 0,
            duration: 0.4,
            anim: FADE(0.0, 0.15),
          }),
          panel("t2", box(CX + 110, 900, 150, 12), {
            fill: "#ffffff",
            radius: 6,
            start: 0.4,
            duration: 0.4,
            anim: FADE(0.4, 0.15),
          }),
          panel("t3", box(CX, 1050, 12, 150), {
            fill: "#ffffff",
            radius: 6,
            start: 0.8,
            duration: 0.4,
            anim: FADE(0.8, 0.15),
          }),
          label("cl", "시간은 흐른다", 1240, {
            size: 44,
            color: "#7fd6a0",
            anim: FADE(0.2),
          }),
        ],
        chartBg,
      ),
      scene(
        "s4",
        "coins",
        1.2,
        [
          ...coins,
          label("cl", "시간이 돈이 된다", 1300, {
            size: 48,
            color: YELLOW,
            anim: FADE(0.7),
          }),
        ],
        chartBg,
      ),
      scene(
        "s5",
        "reveal",
        1.2,
        [
          panel("glow", box(CX, 900, 720, 400), {
            fill: YELLOW,
            radius: 200,
            opacity: 0.14,
            anim: FADE(0.1, 0.6),
          }),
          bigText("c", "복리", 920, {
            size: 320,
            color: YELLOW,
            anim: [...POP(0.1, 0.5), kenBurns(0.1, 1.0, 1.0, 1.08)],
          }),
        ],
        BLACK,
      ),
    ],
    { style: "Time → Money", accent: YELLOW },
  );
}

// 02 ── Nobody Knew ──────────────────────────────────────────────────────────────
function nobodyKnew(): MotionProject {
  return project(
    "02-nobody-knew",
    "Nobody Knew",
    [
      scene(
        "s1",
        "hook",
        1.6,
        [
          bigText("t", "Nobody knew...", 940, {
            size: 92,
            color: "#ffffff",
            anim: [...FADE(0.2, 0.9), kenBurns(0, 1.6, 1.0, 1.06)],
          }),
        ],
        BLACK,
      ),
      scene(
        "s2",
        "place",
        1.5,
        [
          panel("photo", box(CX, 860, 720, 720), {
            fill: "#12161d",
            border: "#2a3240",
            borderWidth: 2,
            radius: 20,
            anim: [...FADE(0.1, 0.7), kenBurns(0, 1.5, 1.0, 1.12)],
          }),
          panel("inner", box(CX, 820, 640, 560), {
            fill: "#1b222c",
            radius: 12,
            opacity: 0.85,
          }),
          label("cap", "평범한 주유소", 1340, {
            size: 46,
            color: "#9aa3b2",
            anim: FADE(0.9),
          }),
        ],
        BLACK,
      ),
      scene(
        "s3",
        "man",
        1.3,
        [
          el({
            id: "man",
            type: "character",
            transform: box(CX, 900, 420, 620),
            props: { color: "#3a4150", faceColor: "#0a0a0a" },
            animations: [...FADE(0.1, 0.6), kenBurns(0, 1.3, 1.0, 1.06)],
            zIndex: 2,
          }),
          label("cap", "한 남자", 1360, { size: 52, color: "#ffffff", anim: FADE(0.6) }),
        ],
        BLACK,
      ),
      scene(
        "s4",
        "invest",
        1.2,
        [
          bigText("t", "매달, 조용히", 860, {
            size: 96,
            color: "#ffffff",
            anim: FADE(0.1),
          }),
          label("l", "배당주에 투자했다", 1010, {
            size: 48,
            color: "#9aa3b2",
            anim: FADE(0.5),
          }),
        ],
        BLACK,
      ),
      scene(
        "s5",
        "number",
        1.6,
        [
          panel("glow", box(CX, 900, 900, 460), {
            fill: YELLOW,
            radius: 240,
            opacity: 0.12,
            anim: FADE(0.1, 0.6),
          }),
          bigText("n", "$8,000,000", 920, {
            size: 150,
            color: YELLOW,
            anim: [...POP(0.1, 0.6), kenBurns(0.1, 1.5, 1.0, 1.1)],
          }),
        ],
        BLACK,
      ),
    ],
    { style: "Cinematic minimal", accent: YELLOW },
  );
}

// 03 ── Stock Crash ──────────────────────────────────────────────────────────────
function stockCrash(): MotionProject {
  const red = gradient(["#0a0000", "#1a0505", "#0a0000"], 100);
  // "shake" = micro-cuts of the same number at jittered offsets (no position keyframes in engine).
  const jolt = (id: string, cx: number, cy: number): MotionProject["scenes"][number] =>
    scene(
      id,
      id,
      0.1,
      [bigText(`${id}t`, "-52%", cy, { size: 220, color: "#ff3b3b", cx })],
      BLACK,
    );
  return project(
    "03-stock-crash",
    "Stock Crash",
    [
      scene(
        "s1",
        "up",
        1.4,
        [
          bigText("t", "+128%", 900, {
            size: 240,
            color: "#2ee66a",
            anim: [...POP(0.1, 0.5), kenBurns(0.1, 1.4, 1.0, 1.05)],
          }),
          label("l", "모두가 환호했다", 1120, {
            size: 46,
            color: "#7fd6a0",
            anim: FADE(0.6),
          }),
        ],
        BLACK,
      ),
      scene("flash", "flash", 0.13, [], gradient(["#ffffff", "#f0f0f0"], 90)),
      jolt("j1", 560, 900),
      jolt("j2", 520, 940),
      jolt("j3", 555, 880),
      scene(
        "s2",
        "down",
        1.4,
        [
          bigText("t", "-52%", 900, {
            size: 240,
            color: "#ff3b3b",
            anim: [...POP(0.05, 0.4), kenBurns(0.05, 1.4, 1.1, 1.0)],
          }),
          label("l", "하루아침에 반토막", 1120, {
            size: 46,
            color: "#ff8a8a",
            anim: FADE(0.5),
          }),
        ],
        red,
      ),
      scene(
        "s3",
        "chart",
        1.3,
        [
          el({
            id: "ch",
            type: "line-chart",
            transform: box(CX, 960, 900, 700),
            props: {
              values: [100, 118, 128, 122, 96, 70, 55, 48],
              color: "#ff3b3b",
              area: true,
              strokeWidth: 8,
              yTicks: [
                [40, "40"],
                [80, "80"],
                [120, "120"],
              ],
            },
            animations: FADE(0.1, 0.5),
            zIndex: 2,
          }),
        ],
        red,
      ),
      scene(
        "s4",
        "message",
        1.6,
        [
          bigText("m", "하지만", 820, { size: 100, color: "#ffffff", anim: FADE(0.1) }),
          bigText("m2", "배당은 계속됐다", 1000, {
            size: 108,
            color: YELLOW,
            anim: [...POP(0.4, 0.5), kenBurns(0.4, 1.2, 1.0, 1.06)],
          }),
        ],
        BLACK,
      ),
    ],
    { style: "Volatility drama", accent: YELLOW },
  );
}

// 04 ── One Dollar ───────────────────────────────────────────────────────────────
function oneDollar(): MotionProject {
  const swap = (
    id: string,
    text: string,
    size: number,
    s: number,
    d: number,
    color = "#ffffff",
  ) => bigText(id, text, 900, { size, color, start: s, duration: d, anim: POP(s, 0.35) });
  return project(
    "04-one-dollar",
    "One Dollar",
    [
      scene(
        "s1",
        "start",
        1.2,
        [
          dot("coin", CX, 780, 90, YELLOW, {
            anim: [...POP(0.1, 0.4), kenBurns(0.1, 1.2, 1.0, 1.1)],
          }),
          bigText("t", "$1", 1050, { size: 200, color: "#ffffff", anim: FADE(0.3) }),
          label("l", "단돈 1달러", 1260, { size: 44, color: "#8a94a6", anim: FADE(0.5) }),
        ],
        BLACK,
      ),
      scene(
        "s2",
        "grow",
        3.0,
        [
          swap("g1", "$5", 200, 0.0, 0.8),
          swap("g2", "$100", 240, 0.8, 0.8),
          swap("g3", "$1,000", 280, 1.6, 0.8),
          panel("glow", box(CX, 900, 900, 420), {
            fill: YELLOW,
            radius: 220,
            opacity: 0.13,
            start: 2.4,
            anim: FADE(2.4, 0.4),
          }),
          swap("g4", "$10,000", 320, 2.4, 0.6, YELLOW),
        ],
        BLACK,
      ),
      scene(
        "s3",
        "time",
        1.6,
        [
          bigText("t", "30년", 860, {
            size: 260,
            color: "#ffffff",
            anim: [...POP(0.1, 0.5), kenBurns(0.1, 1.5, 1.0, 1.06)],
          }),
          label("l", "복리가 한 일", 1120, { size: 48, color: YELLOW, anim: FADE(0.7) }),
        ],
        BLACK,
      ),
    ],
    { style: "Number growth", accent: YELLOW },
  );
}

// 05 ── Apple Style ──────────────────────────────────────────────────────────────
function appleStyle(): MotionProject {
  const dark = gradient(["#08080a", "#15181e", "#08080a"], 125);
  return project(
    "05-apple-style",
    "Apple Style",
    [
      scene(
        "s1",
        "logo",
        1.2,
        [
          dot("l", CX, 940, 54, "#f2f2f4", {
            anim: [...FADE(0.15, 0.5), kenBurns(0.15, 1.0, 0.9, 1.05)],
          }),
        ],
        dark,
      ),
      scene(
        "s2",
        "simple",
        1.3,
        [
          bigText("t", "Simple.", 940, {
            size: 150,
            color: "#f4f5f7",
            anim: [...FADE(0.1, 0.7), kenBurns(0, 1.3, 1.0, 1.04)],
          }),
        ],
        dark,
      ),
      scene(
        "s3",
        "powerful",
        1.1,
        [
          bigText("t", "Powerful.", 940, {
            size: 150,
            color: "#f4f5f7",
            anim: FADE(0.1, 0.7),
          }),
        ],
        dark,
      ),
      scene(
        "s4",
        "product",
        1.6,
        [
          panel("glow", box(CX, 860, 520, 760), {
            fill: "#4a6a9a",
            radius: 200,
            opacity: 0.16,
            anim: FADE(0.1, 0.7),
          }),
          panel("prod", box(CX, 840, 400, 620), {
            fill: "#1c222c",
            border: "#3a4557",
            borderWidth: 2,
            radius: 52,
            anim: [...FADE(0.15, 0.7), kenBurns(0, 1.6, 1.0, 1.06)],
          }),
          panel("refl", box(CX, 1320, 400, 200), {
            fill: "#151a22",
            radius: 52,
            opacity: 0.35,
          }),
        ],
        dark,
      ),
      scene(
        "s5",
        "spec",
        1.1,
        [
          bigText("t", "A19 Pro", 900, { size: 120, color: "#ffffff", anim: FADE(0.1) }),
          label("l", "가장 강력한 칩", 1050, {
            size: 44,
            color: "#8a94a6",
            anim: FADE(0.4),
          }),
        ],
        dark,
      ),
      scene(
        "s6",
        "price",
        1.2,
        [
          bigText("t", "₩1,790,000", 900, {
            size: 100,
            color: "#f4f5f7",
            anim: POP(0.1, 0.5),
          }),
          label("l", "지금 만나보세요", 1060, {
            size: 40,
            color: YELLOW,
            anim: FADE(0.5),
          }),
        ],
        dark,
      ),
    ],
    { style: "Apple Keynote", accent: YELLOW },
  );
}

// 06 ── Documentary ──────────────────────────────────────────────────────────────
function documentary(): MotionProject {
  const sepia = gradient(["#120d08", "#281c10", "#120d08"], 115);
  const framed = (id: string, cap: string): MotionElement[] => [
    panel(`${id}f`, box(CX, 840, 640, 720), {
      fill: "#241a10",
      border: "#5a4326",
      borderWidth: 3,
      radius: 8,
      anim: [...FADE(0.1, 0.7), kenBurns(0, 1.5, 1.0, 1.12)],
    }),
    panel(`${id}i`, box(CX, 800, 560, 620), { fill: "#3a2c18", radius: 4, opacity: 0.9 }),
    label(`${id}c`, cap, 1360, { size: 44, color: "#c9b48f", anim: FADE(0.9) }),
  ];
  return project(
    "06-documentary",
    "Documentary",
    [
      scene(
        "s1",
        "year",
        1.4,
        [
          bigText("y", "1973", 940, {
            size: 300,
            color: "#e8d9bf",
            anim: [...FADE(0.1, 0.7), kenBurns(0, 1.4, 1.0, 1.06)],
          }),
        ],
        sepia,
      ),
      scene("s2", "news", 1.4, framed("n", "그날의 신문"), sepia),
      scene("s3", "photo", 1.3, framed("p", "빛바랜 사진 한 장"), sepia),
      scene(
        "s4",
        "map",
        1.2,
        [
          label("m", "작은 마을에서", 620, {
            size: 44,
            color: "#c9b48f",
            anim: FADE(0.2),
          }),
          ...[300, 460, 640, 780].map((x, i) =>
            dot(`d${i}`, x, 940, 18, "#c98a3a", { anim: POP(0.2 + i * 0.15, 0.3) }),
          ),
          panel("line", box(540, 940, 480, 5), {
            fill: "#5a4326",
            radius: 3,
            anim: FADE(0.9),
          }),
        ],
        sepia,
      ),
      scene("s5", "company", 1.3, framed("c", "그리고 한 기업"), sepia),
      scene(
        "s6",
        "end",
        1.5,
        [
          bigText("e", "모든 것이", 840, {
            size: 110,
            color: "#e8d9bf",
            anim: FADE(0.1),
          }),
          bigText("e2", "바뀌었다", 1010, {
            size: 130,
            color: "#ffcf7a",
            anim: [...POP(0.4, 0.5), kenBurns(0.4, 1.1, 1.0, 1.06)],
          }),
        ],
        sepia,
      ),
    ],
    { style: "MagnatesMedia", accent: "#ffcf7a" },
  );
}

// 07 ── Invisible Investor ───────────────────────────────────────────────────────
function invisibleInvestor(): MotionProject {
  const beat = (
    id: string,
    text: string,
    color: string,
  ): MotionProject["scenes"][number] =>
    scene(
      id,
      id,
      0.75,
      [bigText(id, text, 940, { size: 130, color, anim: POP(0.0, 0.32) })],
      BLACK,
    );
  return project(
    "07-invisible-investor",
    "Invisible Investor",
    [
      scene(
        "s1",
        "logo",
        1.3,
        [
          el({
            id: "logo",
            type: "topic-circle",
            transform: box(CX, 860, 300, 300),
            props: { label: "$", fill: YELLOW, color: "#0a0a0a", fontSize: 150 },
            animations: [...POP(0.1, 0.5), kenBurns(0.1, 1.2, 0.9, 1.05)],
            zIndex: 2,
          }),
          label("l", "사람도, 목소리도 없이", 1200, {
            size: 44,
            color: "#8a94a6",
            anim: FADE(0.6),
          }),
        ],
        BLACK,
      ),
      beat("b1", "배당금", "#ffffff"),
      beat("b2", "재투자", YELLOW),
      beat("b3", "배당금", "#ffffff"),
      beat("b4", "재투자", YELLOW),
      scene(
        "s2",
        "years",
        1.0,
        [bigText("y", "40년", 940, { size: 260, color: "#ffffff", anim: POP(0.1, 0.5) })],
        BLACK,
      ),
      scene(
        "s3",
        "explode",
        1.5,
        [
          panel("glow", box(CX, 900, 980, 480), {
            fill: YELLOW,
            radius: 240,
            opacity: 0.13,
            anim: FADE(0.1, 0.5),
          }),
          bigText("n", "+4,200%", 920, {
            size: 170,
            color: YELLOW,
            anim: [...POP(0.1, 0.6), kenBurns(0.1, 1.4, 1.0, 1.12)],
          }),
        ],
        BLACK,
      ),
    ],
    { style: "Faceless finance", accent: YELLOW },
  );
}

// 08 ── Future ───────────────────────────────────────────────────────────────────
function future(): MotionProject {
  const push = (
    id: string,
    year: string,
    colors: string[],
  ): MotionProject["scenes"][number] =>
    scene(
      id,
      id,
      1.0,
      [
        panel(`${id}bg`, box(CX, 960, 1080, 1920), {
          fill: colors[1]!,
          radius: 0,
          opacity: 0.5,
          anim: [kenBurns(0, 1.0, 1.05, 1.2)],
        }),
        bigText(id, year, 940, {
          size: 260,
          color: "#ffffff",
          anim: [...FADE(0.05, 0.4), kenBurns(0.05, 0.95, 1.0, 1.08)],
        }),
      ],
      gradient(colors, 120),
    );
  return project(
    "08-future",
    "Future",
    [
      push("s1", "2026", ["#0a0d14", "#12203a", "#0a0d14"]),
      push("s2", "2030", ["#0a1020", "#183050", "#0a1020"]),
      push("s3", "2040", ["#0a1828", "#1d4a6a", "#0a1828"]),
      push("s4", "2050", ["#0a2030", "#2472a0", "#0a2030"]),
      scene(
        "end",
        "end",
        2.2,
        [
          bigText("q1", "당신은 지금", 760, {
            size: 92,
            color: "#ffffff",
            anim: FADE(0.1),
          }),
          bigText("q2", "어디에", 920, { size: 120, color: YELLOW, anim: FADE(0.5) }),
          bigText("q3", "투자하는가?", 1090, {
            size: 100,
            color: "#ffffff",
            anim: [...POP(0.9, 0.5), kenBurns(0.9, 1.2, 1.0, 1.05)],
          }),
        ],
        gradient(["#0a2436", "#2e86b8", "#0a2436"], 120),
      ),
    ],
    { style: "Future push", accent: YELLOW },
  );
}

// 09 ── Kinetic Typography ───────────────────────────────────────────────────────
function kinetic(): MotionProject {
  const beat = (
    id: string,
    word: string,
    size: number,
    color: string,
    rot: number,
    preset: string,
  ): MotionProject["scenes"][number] =>
    scene(
      id,
      id,
      0.6,
      [
        bigText(id, word, 960, {
          size,
          color,
          rotation: rot,
          anim: [enter(preset, 0.0, 0.28)],
        }),
      ],
      BLACK,
    );
  return project(
    "09-kinetic",
    "Kinetic Typography",
    [
      beat("s1", "THIS", 200, "#ffffff", -7, "slide-left"),
      beat("s2", "IS", 180, "#ffffff", 5, "slide-right"),
      beat("s3", "NOT", 220, "#ff3b3b", -4, "pop-in"),
      beat("s4", "ABOUT", 160, "#ffffff", 6, "slide-up"),
      beat("s5", "MONEY", 240, YELLOW, -5, "zoom-in"),
      scene(
        "turn",
        "turn",
        2.0,
        [
          bigText("t1", "IT'S ABOUT", 800, {
            size: 110,
            color: "#ffffff",
            anim: FADE(0.1),
          }),
          bigText("t2", "TIME", 1040, {
            size: 300,
            color: "#33d6c8",
            anim: [...POP(0.4, 0.5), kenBurns(0.4, 1.5, 1.0, 1.1)],
          }),
        ],
        BLACK,
      ),
    ],
    { style: "Kinetic Typography", accent: YELLOW },
  );
}

// 10 ── Ultimate Reel ────────────────────────────────────────────────────────────
function ultimateReel(): MotionProject {
  const bg = gradient(["#07080c", "#131a2a", "#07080c"], 125);
  return project(
    "10-ultimate-reel",
    "Ultimate Reel",
    [
      scene(
        "s1",
        "create",
        1.0,
        [
          bigText("t", "CREATE", 960, {
            size: 190,
            color: "#ffffff",
            anim: [...FADE(0.05, 0.4), kenBurns(0.05, 0.95, 1.0, 1.1)],
          }),
        ],
        BLACK,
      ),
      scene(
        "s2",
        "photo",
        1.0,
        [
          panel("g", box(CX, 900, 640, 780), {
            fill: "#26406a",
            radius: 240,
            opacity: 0.2,
          }),
          panel("p", box(CX, 900, 520, 660), {
            fill: "#16202f",
            border: "#2f4a6a",
            borderWidth: 2,
            radius: 40,
            anim: [kenBurns(0, 1.0, 1.0, 1.12)],
          }),
        ],
        bg,
      ),
      scene(
        "s3",
        "chart",
        1.0,
        [
          el({
            id: "ch",
            type: "line-chart",
            transform: box(CX, 980, 880, 900),
            props: {
              values: [10, 14, 12, 22, 30, 44, 62, 88],
              color: "#33d6c8",
              area: true,
              strokeWidth: 8,
              yTicks: [
                [0, "0"],
                [40, "40"],
                [80, "80"],
              ],
            },
            animations: FADE(0.05, 0.4),
            zIndex: 2,
          }),
        ],
        bg,
      ),
      scene(
        "s4",
        "dash",
        1.0,
        [
          panel("c1", box(320, 900, 300, 360), {
            fill: "#141b28",
            border: "#26303f",
            borderWidth: 2,
            radius: 24,
            anim: POP(0.05, 0.32),
          }),
          panel("c2", box(760, 900, 300, 360), {
            fill: "#141b28",
            border: YELLOW,
            borderWidth: 2,
            radius: 24,
            anim: POP(0.25, 0.32),
          }),
          bigText("c1v", "18%", 900, {
            size: 90,
            color: "#33d6c8",
            cx: 320,
            width: 280,
            start: 0.05,
            anim: FADE(0.25),
          }),
          bigText("c2v", "12.4조", 900, {
            size: 80,
            color: YELLOW,
            cx: 760,
            width: 280,
            start: 0.25,
            anim: FADE(0.45),
          }),
        ],
        bg,
      ),
      scene(
        "s5",
        "timeline",
        1.0,
        [
          panel("sp", box(CX, 900, 700, 6), { fill: "#26303f", radius: 3 }),
          ...[280, 540, 800].map((x, i) =>
            dot(`d${i}`, x, 900, 20, "#33d6c8", { anim: POP(0.05 + i * 0.15, 0.3) }),
          ),
          label("l", "시간이 곧 복리다", 1080, {
            size: 46,
            color: "#a9b6cc",
            anim: FADE(0.55),
          }),
        ],
        bg,
      ),
      scene(
        "s6",
        "number",
        1.0,
        [
          bigText("n", "+610%", 960, {
            size: 200,
            color: "#2ee66a",
            anim: [...POP(0.05, 0.4), kenBurns(0.05, 0.95, 1.0, 1.12)],
          }),
        ],
        BLACK,
      ),
      scene(
        "s7",
        "product",
        1.0,
        [
          panel("glow", box(CX, 900, 460, 640), {
            fill: "#4a6a9a",
            radius: 180,
            opacity: 0.16,
          }),
          panel("prod", box(CX, 900, 340, 520), {
            fill: "#1c222c",
            border: "#3a4557",
            borderWidth: 2,
            radius: 44,
            anim: [kenBurns(0, 1.0, 1.0, 1.08)],
          }),
        ],
        bg,
      ),
      scene(
        "s8",
        "brand",
        1.4,
        [
          bigText("b", "Motion Studio", 820, {
            size: 96,
            color: "#ffffff",
            anim: [...FADE(0.1, 0.5), kenBurns(0, 1.4, 1.0, 1.05)],
          }),
          bigText("b2", "Create Without Limits", 1000, {
            size: 60,
            color: YELLOW,
            anim: FADE(0.5),
          }),
        ],
        BLACK,
      ),
    ],
    { style: "Engine reel", accent: YELLOW },
  );
}

export const SCENARIOS: ScenarioDef[] = [
  {
    id: "01-time-is-money",
    name: "Time Is Money",
    style: "Time → Money",
    featuresTested: ["ken-burns", "faux-glow", "particles-as-dots", "typography"],
    build: timeIsMoney,
    posterTime: 5.4,
  },
  {
    id: "02-nobody-knew",
    name: "Nobody Knew",
    style: "Cinematic minimal",
    featuresTested: ["photo-zoom", "character", "huge-number", "minimal"],
    build: nobodyKnew,
    posterTime: 6.4,
  },
  {
    id: "03-stock-crash",
    name: "Stock Crash",
    style: "Volatility drama",
    featuresTested: ["micro-cut-shake", "white-flash", "chart", "number"],
    build: stockCrash,
    posterTime: 5.7,
  },
  {
    id: "04-one-dollar",
    name: "One Dollar",
    style: "Number growth",
    featuresTested: ["scale", "number-replace", "faux-glow", "timing"],
    build: oneDollar,
    posterTime: 5.4,
  },
  {
    id: "05-apple-style",
    name: "Apple Style",
    style: "Apple Keynote",
    featuresTested: ["minimal", "reflection-panel", "ken-burns", "gradient"],
    build: appleStyle,
    posterTime: 5.0,
  },
  {
    id: "06-documentary",
    name: "Documentary",
    style: "MagnatesMedia",
    featuresTested: ["ken-burns", "framed-photo", "timeline", "cross-fade"],
    build: documentary,
    posterTime: 7.7,
  },
  {
    id: "07-invisible-investor",
    name: "Invisible Investor",
    style: "Faceless finance",
    featuresTested: ["logo", "counter-swap", "timing"],
    build: invisibleInvestor,
    posterTime: 6.3,
  },
  {
    id: "08-future",
    name: "Future",
    style: "Future push",
    featuresTested: ["camera-push", "timeline", "text-composition"],
    build: future,
    posterTime: 5.4,
  },
  {
    id: "09-kinetic",
    name: "Kinetic Typography",
    style: "Kinetic Typography",
    featuresTested: ["typography", "motion-timing", "hierarchy"],
    build: kinetic,
    posterTime: 4.2,
  },
  {
    id: "10-ultimate-reel",
    name: "Ultimate Reel",
    style: "Engine reel",
    featuresTested: ["everything", "transitions", "charts", "cards", "camera"],
    build: ultimateReel,
    posterTime: 7.9,
  },
];
