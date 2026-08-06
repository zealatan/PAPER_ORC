/**
 * Ten cinematic showcase projects (720×1280 / 15fps / 5–10s). The goal is not feature coverage but
 * "look what this engine can do": gradient backgrounds, heavy typography, Ken Burns keyframe zoom,
 * staggered reveals, layered translucent "glow", and charts — composed into distinct visual styles.
 * Every project is deterministic (fixed timestamp, no clock/random).
 */
import type { MotionProject } from "@motion-studio/core";
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

export interface ShowcaseDef {
  id: string;
  name: string;
  style: string;
  featuresTested: string[];
  posterTime?: number;
  build: () => MotionProject;
}

const FADE = (s: number, d = 0.5) => [enter("fade-in", s, d)];
const POP = (s: number, d = 0.45) => [enter("pop-in", s, d)];
const CX = W / 2;

// 01 ── Apple Product Reveal ────────────────────────────────────────────────────
function apple(): MotionProject {
  const dark = gradient(["#0a0a0c", "#161a20", "#0a0a0c"], 120);
  return project(
    "01-apple-reveal",
    "Apple Product Reveal",
    [
      scene(
        "logo",
        "logo",
        1.3,
        [dot("l", CX, 620, 42, "#f2f2f4", { anim: FADE(0.15, 0.5) })],
        dark,
      ),
      scene(
        "product",
        "product",
        2.0,
        [
          panel("glow", box(CX, 620, 460, 620), {
            fill: "#3a4a66",
            radius: 200,
            opacity: 0.18,
            anim: FADE(0.1, 0.7),
          }),
          panel("prod", box(CX, 620, 360, 520), {
            fill: "#1c222c",
            border: "#3a4557",
            borderWidth: 2,
            radius: 48,
            anim: [...FADE(0.2, 0.7), kenBurns(0, 2.0, 1.0, 1.08)],
          }),
          label("pl", "티타늄 · 한 몸", 980, {
            size: 30,
            color: "#8a94a6",
            anim: FADE(0.9),
          }),
        ],
        dark,
      ),
      scene(
        "name",
        "name",
        1.6,
        [
          bigText("t", "TITAN Pro", 600, {
            size: 108,
            color: "#f4f5f7",
            anim: [...FADE(0.1, 0.6), kenBurns(0, 1.6, 1.0, 1.05)],
          }),
          label("s", "다시, 경계를 넘다", 720, {
            size: 34,
            color: "#9aa3b2",
            anim: FADE(0.6),
          }),
        ],
        dark,
      ),
      scene(
        "spec",
        "spec",
        1.6,
        [
          panel("c", box(CX, 640, 560, 440), {
            fill: "#12151b",
            border: "#262c36",
            borderWidth: 2,
            radius: 32,
            anim: POP(0.1, 0.5),
          }),
          label("s1", "A19 Pro 칩", 520, { size: 40, color: "#ffffff", anim: FADE(0.3) }),
          label("s2", "48MP · 5배 광학", 640, {
            size: 40,
            color: "#ffffff",
            anim: FADE(0.45),
          }),
          label("s3", "36시간 배터리", 760, {
            size: 40,
            color: "#ffffff",
            anim: FADE(0.6),
          }),
        ],
        dark,
      ),
      scene(
        "price",
        "price",
        1.4,
        [
          bigText("p", "₩1,790,000", 600, {
            size: 82,
            color: "#f4f5f7",
            anim: POP(0.1, 0.5),
          }),
          label("pm", "부터", 700, { size: 32, color: "#8a94a6", anim: FADE(0.5) }),
        ],
        dark,
      ),
      scene(
        "cta",
        "cta",
        1.1,
        [
          bigText("c", "지금, 예약 구매", 620, {
            size: 68,
            color: "#ffffff",
            anim: [...FADE(0.1, 0.5), kenBurns(0, 1.1, 1.0, 1.06)],
          }),
        ],
        dark,
      ),
    ],
    { style: "Apple Keynote", posterHint: "name" },
  );
}

// 02 ── Bloomberg Finance ────────────────────────────────────────────────────────
function bloomberg(): MotionProject {
  const navy = gradient(["#05070d", "#0c1830", "#05070d"], 100);
  const ticker = (y: number) =>
    panel("tk", box(CX, y, W, 90), { fill: "#000000cc", radius: 0, z: 30 });
  return project(
    "02-bloomberg",
    "Bloomberg Finance",
    [
      scene(
        "break",
        "breaking",
        1.2,
        [
          panel("bar", box(CX, 600, 620, 130), {
            fill: "#c81e1e",
            radius: 10,
            anim: [enter("slide-left", 0.1, 0.4, { distance: 400 })],
          }),
          bigText("b", "BREAKING", 600, { size: 74, color: "#ffffff", anim: FADE(0.25) }),
          label("b2", "실시간 마켓", 720, {
            size: 34,
            color: "#ff8a8a",
            anim: FADE(0.5),
          }),
        ],
        navy,
      ),
      scene(
        "stock",
        "stock",
        1.5,
        [
          bigText("s", "NVEX", 560, { size: 132, color: "#ffffff", anim: POP(0.1, 0.5) }),
          bigText("v", "▲ +12.4%", 720, { size: 74, color: "#2ee66a", anim: FADE(0.4) }),
          ticker(1210),
          label("t", "NASDAQ · 거래량 급증", 1210, {
            size: 30,
            color: "#ffb020",
            z: 31,
            anim: FADE(0.6),
          }),
        ],
        navy,
      ),
      scene(
        "num",
        "numbers",
        1.8,
        [
          label("l", "목표주가", 480, { size: 34, color: "#8fa0bd" }),
          bigText("n1", "$142", 640, {
            size: 120,
            color: "#ffffff",
            start: 0,
            duration: 0.9,
            anim: POP(0.1, 0.4),
          }),
          bigText("n2", "$159", 640, {
            size: 140,
            color: "#2ee66a",
            start: 0.9,
            duration: 1.0,
            anim: POP(0.9, 0.4),
          }),
          ticker(1210),
          label("t2", "애널리스트 상향", 1210, { size: 30, color: "#ffb020", z: 31 }),
        ],
        navy,
      ),
      scene(
        "chart",
        "chart",
        2.0,
        [
          label("ct", "12개월 추이", 360, { size: 34, color: "#8fa0bd" }),
          el({
            id: "ch",
            type: "line-chart",
            transform: box(CX, 760, 620, 640),
            props: {
              values: [100, 104, 98, 112, 120, 118, 130, 142, 138, 150, 155, 159],
              color: "#2ee66a",
              area: true,
              strokeWidth: 6,
              yTicks: [
                [90, "90"],
                [110, "110"],
                [130, "130"],
                [150, "150"],
              ],
            },
            animations: FADE(0.15, 0.6),
            zIndex: 2,
          }),
          ticker(1210),
          label("t3", "NVEX  $159.20  ▲ 12.4%", 1210, {
            size: 30,
            color: "#ffb020",
            z: 31,
          }),
        ],
        navy,
      ),
      scene(
        "sum",
        "summary",
        1.3,
        [
          panel("lt", box(CX, 1080, W, 200), { fill: "#0a1428ee", radius: 0, z: 20 }),
          bigText("st", "매수 우위", 1040, {
            size: 60,
            color: "#2ee66a",
            z: 21,
            anim: FADE(0.1),
          }),
          label("sl", "12개월 목표 $180", 1130, {
            size: 34,
            color: "#cbd5e6",
            z: 21,
            anim: FADE(0.4),
          }),
        ],
        navy,
      ),
    ],
    { style: "Bloomberg TV", posterHint: "chart" },
  );
}

// 03 ── Mini Documentary ─────────────────────────────────────────────────────────
function documentary(): MotionProject {
  const sepia = gradient(["#140f0a", "#2a1e12", "#140f0a"], 115);
  return project(
    "03-documentary",
    "Mini Documentary",
    [
      scene(
        "year",
        "1970",
        1.6,
        [
          bigText("y", "1970", 600, {
            size: 190,
            color: "#e8d9bf",
            anim: [...FADE(0.1, 0.7), kenBurns(0, 1.6, 1.0, 1.06)],
          }),
        ],
        sepia,
      ),
      scene(
        "photo",
        "photo",
        2.2,
        [
          panel("frame", box(CX, 560, 500, 560), {
            fill: "#241a10",
            border: "#5a4326",
            borderWidth: 3,
            radius: 8,
            anim: [...FADE(0.1, 0.8), kenBurns(0, 2.2, 1.0, 1.12)],
          }),
          panel("inner", box(CX, 560, 460, 520), {
            fill: "#3a2c18",
            radius: 4,
            opacity: 0.9,
          }),
          label("cap", "가난한 청소부, 로널드", 960, {
            size: 34,
            color: "#c9b48f",
            anim: FADE(0.9),
          }),
        ],
        sepia,
      ),
      scene(
        "map",
        "map",
        1.6,
        [
          label("m", "버몬트, 미국", 460, {
            size: 34,
            color: "#c9b48f",
            anim: FADE(0.2),
          }),
          dot("d1", 230, 680, 14, "#c98a3a", { anim: POP(0.3, 0.4) }),
          dot("d2", 360, 640, 14, "#c98a3a", { anim: POP(0.5, 0.4) }),
          dot("d3", 500, 700, 14, "#c98a3a", { anim: POP(0.7, 0.4) }),
          panel("line", box(360, 670, 300, 4), {
            fill: "#5a4326",
            radius: 2,
            anim: FADE(0.9),
          }),
        ],
        sepia,
      ),
      scene(
        "time",
        "timeline",
        2.0,
        [
          panel("spine", box(CX, 640, 6, 500), { fill: "#5a4326", radius: 3 }),
          bigText("a", "1970", 460, { size: 54, color: "#e8d9bf", anim: FADE(0.2) }),
          label("a2", "청소부 시작", 520, {
            size: 30,
            color: "#c9b48f",
            anim: FADE(0.35),
          }),
          bigText("b", "2014", 720, { size: 54, color: "#e8d9bf", anim: FADE(0.7) }),
          label("b2", "조용히 세상을 떠나다", 780, {
            size: 30,
            color: "#c9b48f",
            anim: FADE(0.85),
          }),
        ],
        sepia,
      ),
      scene(
        "today",
        "today",
        1.4,
        [
          bigText("t", "$8,000,000", 600, {
            size: 92,
            color: "#ffcf7a",
            anim: [...POP(0.1, 0.5), kenBurns(0, 1.4, 1.0, 1.05)],
          }),
          label("t2", "아무도 몰랐던 유산", 720, {
            size: 34,
            color: "#c9b48f",
            anim: FADE(0.6),
          }),
        ],
        sepia,
      ),
    ],
    { style: "MagnatesMedia", posterHint: "photo" },
  );
}

// 04 ── Ronald Read Story ────────────────────────────────────────────────────────
function ronald(): MotionProject {
  const black = gradient(["#000000", "#0a0a0a"], 90);
  return project(
    "04-ronald-read",
    "Ronald Read Story",
    [
      scene(
        "hook",
        "hook",
        1.6,
        [
          bigText("h", "아무도 몰랐다", 620, {
            size: 96,
            color: "#ffffff",
            anim: [...FADE(0.15, 0.7), kenBurns(0, 1.6, 1.0, 1.05)],
          }),
        ],
        black,
      ),
      scene(
        "split",
        "split",
        2.0,
        [
          panel("lp", box(200, 640, 320, 620), {
            fill: "#0f0f0f",
            border: "#242424",
            borderWidth: 2,
            radius: 24,
            anim: [enter("slide-left", 0.1, 0.5, { distance: 300 })],
          }),
          panel("rp", box(520, 640, 320, 620), {
            fill: "#0f0f0f",
            border: "#242424",
            borderWidth: 2,
            radius: 24,
            anim: [enter("slide-right", 0.3, 0.5, { distance: 300 })],
          }),
          bigText("lt", "주유소", 560, {
            size: 54,
            color: "#33d6c8",
            cx: 200,
            width: 300,
            anim: FADE(0.5),
          }),
          label("ll", "35년 근무", 660, {
            size: 32,
            color: "#c9d3e4",
            cx: 200,
            width: 300,
            anim: FADE(0.6),
          }),
          bigText("rt", "커피값", 560, {
            size: 54,
            color: "#ffd000",
            cx: 520,
            width: 300,
            anim: FADE(0.7),
          }),
          label("rl", "아껴 배당주", 660, {
            size: 32,
            color: "#c9d3e4",
            cx: 520,
            width: 300,
            anim: FADE(0.8),
          }),
        ],
        black,
      ),
      scene(
        "div",
        "dividend",
        1.6,
        [
          bigText("d", "배당 재투자", 580, {
            size: 84,
            color: "#ffffff",
            anim: POP(0.1, 0.5),
          }),
          label("d2", "50년, 눈덩이처럼", 700, {
            size: 36,
            color: "#9aa3b2",
            anim: FADE(0.5),
          }),
        ],
        black,
      ),
      scene(
        "num",
        "number",
        1.6,
        [
          bigText("n", "$8,000,000", 620, {
            size: 96,
            color: "#ffd000",
            anim: [...POP(0.1, 0.55), kenBurns(0, 1.6, 1.0, 1.06)],
          }),
        ],
        black,
      ),
      scene(
        "end",
        "ending",
        1.4,
        [
          bigText("e", "조용한 부자", 600, {
            size: 88,
            color: "#ffffff",
            anim: FADE(0.1, 0.7),
          }),
          label("e2", "시간과 인내의 승리", 720, {
            size: 34,
            color: "#9aa3b2",
            anim: FADE(0.6),
          }),
        ],
        black,
      ),
    ],
    { style: "Documentary", posterHint: "num" },
  );
}

// 05 ── Infographic (Kurzgesagt) ─────────────────────────────────────────────────
function infographic(): MotionProject {
  const space = gradient(["#141a3a", "#2a1f5a", "#101430"], 130);
  const colors = ["#ff6b6b", "#ffd93d", "#6bcB77", "#4d96ff", "#c56bff"];
  return project(
    "05-infographic",
    "Infographic",
    [
      scene(
        "q",
        "question",
        1.6,
        [
          bigText("q", "복리란?", 580, {
            size: 120,
            color: "#ffffff",
            anim: [...POP(0.1, 0.5), kenBurns(0, 1.6, 1.0, 1.05)],
          }),
          label("q2", "60초 만에 이해하기", 720, {
            size: 34,
            color: "#b9c2ff",
            anim: FADE(0.6),
          }),
        ],
        space,
      ),
      scene(
        "icons",
        "icons",
        2.0,
        [
          ...colors.map((c, i) =>
            dot(`i${i}`, 130 + i * 115, 620, 42, c, { anim: POP(0.2 + i * 0.2, 0.4) }),
          ),
          label("il", "작은 습관이 쌓이면", 820, {
            size: 34,
            color: "#d4dcff",
            anim: FADE(1.3),
          }),
        ],
        space,
      ),
      scene(
        "diagram",
        "diagram",
        2.0,
        [
          dot("a", 180, 640, 46, "#ffd93d", { anim: POP(0.1, 0.4) }),
          panel("l1", box(360, 640, 220, 8), {
            fill: "#6b7bd6",
            radius: 4,
            anim: FADE(0.5),
          }),
          dot("b", 540, 640, 60, "#6bcB77", { anim: POP(0.6, 0.4) }),
          label("la", "원금", 730, {
            size: 30,
            color: "#d4dcff",
            cx: 180,
            width: 200,
            anim: FADE(0.3),
          }),
          label("lb", "복리 자산", 760, {
            size: 32,
            color: "#d4dcff",
            cx: 540,
            width: 240,
            anim: FADE(0.8),
          }),
        ],
        space,
      ),
      scene(
        "conc",
        "conclusion",
        1.6,
        [
          panel("c", box(CX, 620, 600, 260), {
            fill: "#1a2050cc",
            border: "#4d5bb0",
            borderWidth: 2,
            radius: 28,
            anim: POP(0.1, 0.5),
          }),
          bigText("ct", "시간 × 꾸준함", 600, {
            size: 64,
            color: "#ffd93d",
            anim: FADE(0.3),
          }),
          label("cl", "그것이 복리다", 710, {
            size: 34,
            color: "#d4dcff",
            anim: FADE(0.6),
          }),
        ],
        space,
      ),
    ],
    { style: "Kurzgesagt", posterHint: "icons" },
  );
}

// 06 ── Netflix Style ────────────────────────────────────────────────────────────
function netflix(): MotionProject {
  const black = gradient(["#000000", "#050505"], 90);
  return project(
    "06-netflix",
    "Netflix Style",
    [
      scene(
        "hold",
        "hold",
        1.0,
        [label("d", "2026", 640, { size: 30, color: "#333333" })],
        black,
      ),
      scene(
        "q1",
        "quote1",
        1.8,
        [
          bigText("q", "모두가 팔 때", 600, {
            size: 104,
            color: "#ffffff",
            anim: [...FADE(0.2, 0.8), kenBurns(0, 1.8, 1.0, 1.04)],
          }),
        ],
        black,
      ),
      scene(
        "photo",
        "photo",
        1.6,
        [
          panel("p", box(CX, 640, W, H, {}), {
            fill: "#0d0d0d",
            radius: 0,
            anim: [...FADE(0.1, 0.6), kenBurns(0, 1.6, 1.05, 1.15)],
          }),
          panel("v", box(CX, 640, 520, 520), {
            fill: "#e50914",
            radius: 260,
            opacity: 0.14,
          }),
          bigText("pt", "그는 샀다", 640, {
            size: 96,
            color: "#ffffff",
            z: 5,
            anim: FADE(0.4, 0.7),
          }),
        ],
        black,
      ),
      scene(
        "q2",
        "quote2",
        1.9,
        [
          bigText("q2", "공포가 기회다", 600, {
            size: 104,
            color: "#ffffff",
            anim: [...FADE(0.2, 0.8), kenBurns(0, 1.9, 1.0, 1.05)],
          }),
        ],
        black,
      ),
      scene(
        "end",
        "ending",
        1.5,
        [
          bigText("e", "부는", 560, { size: 88, color: "#ffffff", anim: FADE(0.1) }),
          bigText("e2", "인내의 보상", 700, {
            size: 100,
            color: "#e50914",
            anim: [...POP(0.5, 0.5), kenBurns(0.5, 1.0, 1.0, 1.06)],
          }),
        ],
        black,
      ),
    ],
    { style: "Netflix", posterHint: "q2" },
  );
}

// 07 ── Business Dashboard ───────────────────────────────────────────────────────
function dashboard(): MotionProject {
  const bg = gradient(["#0a0d14", "#111826", "#0a0d14"], 120);
  const heat = ["#123", "#1d3a5f", "#2f6fb0", "#4aa3ff", "#7fc3ff"];
  const kpi = (
    id: string,
    v: string,
    l: string,
    cx: number,
    color: string,
    s: number,
  ) => [
    panel(`${id}c`, box(cx, 360, 210, 200), {
      fill: "#141b28",
      border: "#26303f",
      borderWidth: 2,
      radius: 20,
      anim: POP(s, 0.4),
    }),
    bigText(`${id}v`, v, 330, {
      size: 52,
      color,
      cx,
      width: 200,
      start: s,
      anim: FADE(s + 0.15),
    }),
    label(`${id}l`, l, 420, {
      size: 26,
      color: "#8fa0bd",
      cx,
      width: 200,
      start: s,
      anim: FADE(s + 0.25),
    }),
  ];
  return project(
    "07-dashboard",
    "Business Dashboard",
    [
      scene(
        "title",
        "title",
        1.2,
        [
          bigText("t", "Q4 실적 대시보드", 600, {
            size: 68,
            color: "#ffffff",
            anim: FADE(0.1, 0.6),
          }),
        ],
        bg,
      ),
      scene(
        "grid",
        "grid",
        2.6,
        [
          ...kpi("k1", "12.4조", "매출", 180, "#4aa3ff", 0.1),
          ...kpi("k2", "18%", "이익률", 400, "#33d6c8", 0.3),
          ...kpi("k3", "3.4%", "배당", 620, "#ffd000", 0.5),
          el({
            id: "bars",
            type: "bar-chart",
            transform: box(255, 780, 420, 460),
            props: {
              values: [8.9, 10.6, 11.5, 12.4],
              labels: ["21", "22", "23", "24"],
              color: "#4aa3ff",
              gap: 18,
            },
            animations: [enter("slide-up", 0.6, 0.5, { distance: 200 })],
            zIndex: 2,
          }),
          el({
            id: "line",
            type: "line-chart",
            transform: box(560, 780, 260, 460),
            props: {
              values: [3, 5, 4, 8, 7, 11],
              color: "#33d6c8",
              area: true,
              strokeWidth: 5,
            },
            animations: FADE(0.9, 0.5),
            zIndex: 2,
          }),
        ],
        bg,
      ),
      scene(
        "data",
        "data",
        2.4,
        [
          el({
            id: "tbl",
            type: "table",
            transform: box(230, 640, 400, 520),
            props: {
              rows: [
                ["부문", "성장"],
                ["가전", "+12%"],
                ["모바일", "+8%"],
                ["반도체", "+21%"],
              ],
              color: "#e6edf7",
              lineColor: "#26303f",
            },
            animations: FADE(0.1, 0.5),
            zIndex: 2,
          }),
          ...Array.from({ length: 12 }, (_, i) =>
            dot(
              `h${i}`,
              500 + (i % 4) * 55,
              520 + Math.floor(i / 4) * 55,
              22,
              heat[(i * 3) % heat.length]!,
              { anim: POP(0.4 + i * 0.04, 0.3) },
            ),
          ),
          label("hl", "지역별 히트맵", 720, {
            size: 28,
            color: "#8fa0bd",
            cx: 555,
            width: 260,
            anim: FADE(1.0),
          }),
        ],
        bg,
      ),
    ],
    { style: "Business Dashboard", posterHint: "grid" },
  );
}

// 08 ── Finance Timeline ─────────────────────────────────────────────────────────
function financeTimeline(): MotionProject {
  const bg = gradient(["#0a0d14", "#0f1a2e", "#0a0d14"], 110);
  const stop = (
    id: string,
    year: string,
    txt: string,
    color: string,
    cy: number,
    s: number,
  ) => [
    dot(`${id}d`, 130, cy, 16, color, { anim: POP(s, 0.4) }),
    bigText(`${id}y`, year, cy - 6, {
      size: 48,
      color,
      cx: 260,
      width: 220,
      start: s,
      anim: FADE(s + 0.1),
    }),
    label(`${id}t`, txt, cy + 46, {
      size: 28,
      color: "#a9b6cc",
      cx: 430,
      width: 420,
      start: s,
      anim: FADE(s + 0.2),
    }),
  ];
  return project(
    "08-finance-story",
    "Finance Timeline",
    [
      scene(
        "title",
        "title",
        1.2,
        [
          bigText("t", "위기의 역사", 600, {
            size: 96,
            color: "#ffffff",
            anim: FADE(0.1, 0.6),
          }),
        ],
        bg,
      ),
      scene(
        "tl",
        "timeline",
        3.4,
        [
          panel("spine", box(130, 720, 6, 620), { fill: "#26303f", radius: 3 }),
          ...stop("s1", "2000", "닷컴 버블", "#ff6b6b", 460, 0.2),
          ...stop("s2", "2008", "금융위기", "#ffb020", 620, 0.9),
          ...stop("s3", "2020", "팬데믹 폭락", "#4aa3ff", 780, 1.6),
          ...stop("s4", "2026", "지금", "#2ee66a", 940, 2.3),
        ],
        bg,
      ),
      scene(
        "chart",
        "result",
        2.2,
        [
          label("cl", "그래도 우상향", 360, { size: 34, color: "#8fa0bd" }),
          el({
            id: "ch",
            type: "line-chart",
            transform: box(CX, 760, 620, 640),
            props: {
              values: [100, 60, 90, 130, 70, 120, 180, 240],
              color: "#2ee66a",
              area: true,
              strokeWidth: 6,
              yTicks: [
                [50, "50"],
                [120, "120"],
                [190, "190"],
                [250, "250"],
              ],
            },
            animations: FADE(0.15, 0.7),
            zIndex: 2,
          }),
        ],
        bg,
      ),
      scene(
        "end",
        "ending",
        1.2,
        [
          bigText("e", "버틴 자가 이긴다", 600, {
            size: 72,
            color: "#2ee66a",
            anim: POP(0.1, 0.5),
          }),
        ],
        bg,
      ),
    ],
    { style: "Finance Timeline", posterHint: "tl" },
  );
}

// 09 ── Motion Typography ────────────────────────────────────────────────────────
function motionType(): MotionProject {
  const black = gradient(["#000000", "#080808"], 90);
  const beat = (
    id: string,
    word: string,
    size: number,
    color: string,
    rot: number,
    presetId: string,
  ): MotionProject["scenes"][number] =>
    scene(
      id,
      id,
      0.8,
      [
        bigText(id, word, 640, {
          size,
          color,
          rotation: rot,
          anim: [enter(presetId, 0.0, 0.3)],
        }),
      ],
      black,
    );
  return project(
    "09-motion-type",
    "Motion Typography",
    [
      beat("s1", "THIS", 150, "#ffffff", -6, "slide-left"),
      beat("s2", "IS", 130, "#ffffff", 4, "slide-right"),
      beat("s3", "NOT", 170, "#ff5a5a", -3, "pop-in"),
      beat("s4", "ABOUT", 120, "#ffffff", 5, "slide-up"),
      beat("s5", "MONEY", 190, "#ffd000", -4, "zoom-in"),
      scene(
        "turn",
        "turn",
        1.8,
        [
          bigText("t1", "IT'S ABOUT", 560, {
            size: 78,
            color: "#ffffff",
            anim: FADE(0.1),
          }),
          bigText("t2", "TIME", 720, {
            size: 200,
            color: "#33d6c8",
            anim: [...POP(0.4, 0.5), kenBurns(0.4, 1.4, 1.0, 1.08)],
          }),
        ],
        black,
      ),
    ],
    { style: "Kinetic Typography", posterHint: "s5" },
  );
}

// 10 ── Ultimate Showreel ────────────────────────────────────────────────────────
function showreel(): MotionProject {
  const bg = gradient(["#08090d", "#141a2a", "#08090d"], 125);
  const black = gradient(["#000000", "#070707"], 90);
  return project(
    "10-showreel",
    "Ultimate Showreel",
    [
      scene(
        "q",
        "question",
        1.0,
        [
          bigText("q", "30년 뒤,", 560, {
            size: 104,
            color: "#ffffff",
            anim: FADE(0.05, 0.4),
          }),
          bigText("q2", "당신은?", 700, {
            size: 104,
            color: "#ffd000",
            anim: FADE(0.35, 0.4),
          }),
        ],
        black,
      ),
      scene(
        "photo",
        "photo",
        0.9,
        [
          panel("g", box(CX, 620, 440, 560), {
            fill: "#26406a",
            radius: 220,
            opacity: 0.2,
          }),
          panel("p", box(CX, 620, 360, 480), {
            fill: "#16202f",
            border: "#2f4a6a",
            borderWidth: 2,
            radius: 36,
            anim: [kenBurns(0, 0.9, 1.0, 1.1)],
          }),
        ],
        bg,
      ),
      scene(
        "chart",
        "chart",
        1.1,
        [
          el({
            id: "ch",
            type: "line-chart",
            transform: box(CX, 700, 600, 640),
            props: {
              values: [10, 14, 12, 20, 28, 40, 58, 82],
              color: "#33d6c8",
              area: true,
              strokeWidth: 6,
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
        "cards",
        "cards",
        1.0,
        [
          panel("c1", box(200, 620, 200, 260), {
            fill: "#141b28",
            border: "#26303f",
            borderWidth: 2,
            radius: 20,
            anim: POP(0.05, 0.35),
          }),
          panel("c2", box(520, 620, 200, 260), {
            fill: "#141b28",
            border: "#ffd000",
            borderWidth: 2,
            radius: 20,
            anim: POP(0.25, 0.35),
          }),
          bigText("c1v", "1.8억", 620, {
            size: 54,
            color: "#ffffff",
            cx: 200,
            width: 200,
            start: 0.05,
            anim: FADE(0.2),
          }),
          bigText("c2v", "6.1억", 620, {
            size: 60,
            color: "#ffd000",
            cx: 520,
            width: 200,
            start: 0.25,
            anim: FADE(0.4),
          }),
        ],
        bg,
      ),
      scene(
        "time",
        "timeline",
        1.0,
        [
          panel("sp", box(CX, 640, 500, 6), { fill: "#26303f", radius: 3 }),
          ...(
            [
              ["10년", 200],
              ["20년", 360],
              ["30년", 520],
            ] as Array<[string, number]>
          ).flatMap(([t, x], i) => [
            dot(`d${i}`, x, 640, 16, "#33d6c8", { anim: POP(0.1 + i * 0.2, 0.3) }),
            label(`dl${i}`, t, 560, {
              size: 28,
              color: "#a9b6cc",
              cx: x,
              width: 140,
              anim: FADE(0.2 + i * 0.2),
            }),
          ]),
          label("tl", "복리는 시간의 함수", 760, {
            size: 32,
            color: "#a9b6cc",
            anim: FADE(0.7),
          }),
        ],
        bg,
      ),
      scene(
        "num",
        "numbers",
        0.9,
        [
          bigText("n", "+610%", 640, {
            size: 150,
            color: "#2ee66a",
            anim: [...POP(0.05, 0.4), kenBurns(0.05, 0.85, 1.0, 1.1)],
          }),
        ],
        black,
      ),
      scene(
        "logos",
        "logos",
        0.9,
        [
          ...["A", "N", "K", "P"].map((c, i) =>
            el({
              id: `lg${i}`,
              type: "topic-circle",
              transform: box(150 + i * 140, 640, 110, 110),
              props: {
                label: c,
                fill: ["#4aa3ff", "#ff6b6b", "#ffd000", "#33d6c8"][i],
                color: "#0a0a0a",
                fontSize: 48,
              },
              animations: POP(0.05 + i * 0.12, 0.35),
              zIndex: 2,
            }),
          ),
          label("ll", "글로벌 배당주", 780, {
            size: 32,
            color: "#a9b6cc",
            anim: FADE(0.7),
          }),
        ],
        bg,
      ),
      scene(
        "type",
        "type",
        1.0,
        [
          bigText("t", "큰돈보다", 560, {
            size: 108,
            color: "#ffffff",
            anim: FADE(0.05),
          }),
          bigText("t2", "긴 시간", 710, {
            size: 130,
            color: "#ffd000",
            anim: [...POP(0.3, 0.4), kenBurns(0.3, 0.7, 1.0, 1.08)],
          }),
        ],
        black,
      ),
      scene(
        "end",
        "ending",
        1.3,
        [
          bigText("e", "Motion Studio", 600, {
            size: 76,
            color: "#ffffff",
            anim: [...FADE(0.1, 0.6), kenBurns(0, 1.3, 1.0, 1.05)],
          }),
          label("e2", "하나의 엔진, 무한한 이야기", 710, {
            size: 32,
            color: "#9aa3b2",
            anim: FADE(0.6),
          }),
        ],
        black,
      ),
    ],
    { style: "Showreel", posterHint: "num" },
  );
}

export const SHOWCASES: ShowcaseDef[] = [
  {
    id: "01-apple-reveal",
    name: "Apple Product Reveal",
    style: "Apple Keynote",
    featuresTested: ["gradient", "large-type", "ken-burns", "glow-layer"],
    build: apple,
    posterTime: 4.3,
  },
  {
    id: "02-bloomberg",
    name: "Bloomberg Finance",
    style: "Bloomberg TV",
    featuresTested: ["ticker", "lower-third", "number-swap", "line-chart"],
    build: bloomberg,
    posterTime: 6.2,
  },
  {
    id: "03-documentary",
    name: "Mini Documentary",
    style: "MagnatesMedia",
    featuresTested: ["ken-burns", "framed-photo", "timeline", "sepia-gradient"],
    build: documentary,
    posterTime: 3.0,
  },
  {
    id: "04-ronald-read",
    name: "Ronald Read Story",
    style: "Documentary",
    featuresTested: ["split-layout", "scene-flow", "typography"],
    build: ronald,
    posterTime: 5.9,
  },
  {
    id: "05-infographic",
    name: "Infographic",
    style: "Kurzgesagt",
    featuresTested: ["flat-icons", "connections", "gradient", "cards"],
    build: infographic,
    posterTime: 3.2,
  },
  {
    id: "06-netflix",
    name: "Netflix Style",
    style: "Netflix",
    featuresTested: ["huge-type", "minimalism", "ken-burns", "red-accent"],
    build: netflix,
    posterTime: 7.2,
  },
  {
    id: "07-dashboard",
    name: "Business Dashboard",
    style: "Dashboard",
    featuresTested: ["complex-layout", "kpi", "charts", "table", "heatmap"],
    build: dashboard,
    posterTime: 2.3,
  },
  {
    id: "08-finance-story",
    name: "Finance Timeline",
    style: "Finance Timeline",
    featuresTested: ["timeline", "events", "chart", "stagger"],
    build: financeTimeline,
    posterTime: 4.2,
  },
  {
    id: "09-motion-type",
    name: "Motion Typography",
    style: "Kinetic Typography",
    featuresTested: ["huge-type", "slide", "scale", "static-tilt", "timing"],
    build: motionType,
    posterTime: 4.8,
  },
  {
    id: "10-showreel",
    name: "Ultimate Showreel",
    style: "Showreel",
    featuresTested: ["everything", "charts", "cards", "timeline", "logos", "typography"],
    build: showreel,
    posterTime: 5.6,
  },
];
