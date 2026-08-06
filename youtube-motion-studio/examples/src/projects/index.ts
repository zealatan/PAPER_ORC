/**
 * The ten feature-verification example projects. Each is a pure, deterministic MotionProject built
 * from the toolkit. `featuresTested`/`componentsExpected` drive the validation report. Text is kept
 * to single lines (title/caption/subtitle/speech-bubble do not wrap) and inside the Shorts safe area.
 */
import type { MotionProject } from "@motion-studio/core";
import {
  BODY_FONT,
  C,
  SAFE_BOTTOM,
  W,
  box,
  card,
  caption,
  el,
  enter,
  project,
  scene,
  title,
} from "../toolkit";

export interface ExampleDef {
  id: string;
  name: string;
  featuresTested: string[];
  build: () => MotionProject;
}

const FADE = (start: number, d = 0.6) => [enter("fade-in", start, d)];
const POP = (start: number, d = 0.5) => [enter("pop-in", start, d)];

// ── 01 Number Hook ───────────────────────────────────────────────────────────
function numberHook(): MotionProject {
  const steps = ["0", "1억", "2억", "3억", "4억", "5억", "6억", "7억", "8억"];
  const stepEls = steps.map((t, i) =>
    title(`n-${i}`, `${t}${i === 0 ? " 원" : " 원"}`, 940, {
      size: 190,
      color: i === steps.length - 1 ? C.accent : C.text,
      start: 0.4 + i * 0.28,
      duration: i === steps.length - 1 ? 6 : 0.3,
      anim: POP(0.4 + i * 0.28, 0.24),
    }),
  );
  return project(
    "01-number-hook",
    "Number Hook",
    [
      scene("s1", "intro", 4, [
        caption("c1", "평범한 직장인이", 780, {
          size: 60,
          color: C.dim,
          anim: FADE(0.2),
        }),
        title("t1", "20년 만에 모은 돈", 960, { size: 96, anim: FADE(0.9, 0.7) }),
      ]),
      scene("s2", "count-up", 5, [
        caption("lbl", "모은 돈", 700, { size: 52, color: C.dim, anim: FADE(0.2) }),
        ...stepEls,
      ]),
      scene("s3", "reveal", 3, [
        title("big", "8억 원", 900, { size: 230, color: C.accent, anim: POP(0.1, 0.6) }),
        caption("k", "티끌 모아 태산", 1160, {
          size: 56,
          color: C.teal,
          anim: FADE(0.8),
        }),
      ]),
    ],
    { featuresTested: "heavy-font, number-swap, pop/fade, center-align" },
  );
}

// ── 02 A/B Comparison ─────────────────────────────────────────────────────────
function abComparison(): MotionProject {
  const colCx = { a: 300, b: 780 };
  const cardT = (cx: number) => box(cx, 1000, 452, 720);
  return project(
    "02-ab-comparison",
    "A/B Comparison",
    [
      scene("s1", "title", 3, [
        title("t", "같은 3억 원으로 은퇴", 520, { size: 92, anim: FADE(0.2, 0.6) }),
      ]),
      scene("s2", "compare", 10, [
        title("th", "같은 3억 원으로 은퇴", 360, { size: 74, color: C.dim }),
        // A card (warning / red)
        card("cardA", cardT(colCx.a), {
          border: C.red,
          borderWidth: 4,
          anim: [enter("slide-left", 0.2, 0.6, { distance: 240 })],
        }),
        title("aT", "A", 740, {
          size: 110,
          color: C.red,
          cx: colCx.a,
          width: 420,
          start: 0.2,
          anim: POP(0.4),
        }),
        caption("aL1", "매년 3,000만 원", 940, {
          size: 40,
          color: C.text,
          cx: colCx.a,
          width: 420,
          start: 0.2,
          anim: FADE(0.7),
        }),
        caption("aL2", "정액 인출", 1010, {
          size: 40,
          color: C.dim,
          cx: colCx.a,
          width: 420,
          start: 0.2,
          anim: FADE(0.8),
        }),
        caption("aL3", "자산 고갈", 1230, {
          size: 48,
          color: C.red,
          background: "#2a1414",
          cx: colCx.a,
          width: 400,
          start: 0.2,
          anim: FADE(1.0),
        }),
        // B card (safe / teal)
        card("cardB", cardT(colCx.b), {
          border: C.teal,
          borderWidth: 4,
          anim: [enter("slide-right", 0.6, 0.6, { distance: 240 })],
        }),
        title("bT", "B", 740, {
          size: 110,
          color: C.teal,
          cx: colCx.b,
          width: 420,
          start: 0.6,
          anim: POP(0.8),
        }),
        caption("bL1", "배당금 범위에서", 940, {
          size: 40,
          color: C.text,
          cx: colCx.b,
          width: 420,
          start: 0.6,
          anim: FADE(1.1),
        }),
        caption("bL2", "생활", 1010, {
          size: 40,
          color: C.dim,
          cx: colCx.b,
          width: 420,
          start: 0.6,
          anim: FADE(1.2),
        }),
        caption("bL3", "자산 유지", 1230, {
          size: 48,
          color: C.teal,
          background: "#0f2420",
          cx: colCx.b,
          width: 400,
          start: 0.6,
          anim: FADE(1.4),
        }),
        caption("foot", "차이는 인출 방식", 1470, {
          size: 58,
          color: C.accent,
          background: "#1a1a1a",
          start: 5.5,
          anim: POP(5.5, 0.5),
        }),
      ]),
    ],
    { featuresTested: "two-column, cards, color-contrast, layering, long-korean" },
  );
}

// ── 03 Multi-Series Line Chart ────────────────────────────────────────────────
function multiLineChart(): MotionProject {
  const coke = [30, 33, 38, 41, 47, 52, 60, 71, 83, 96, 112, 130];
  const sp = [30, 32, 35, 38, 42, 45, 50, 55, 61, 68, 74, 82];
  const cash = [30, 30, 30, 30, 31, 31, 31, 32, 32, 32, 33, 33];
  return project(
    "03-multi-line-chart",
    "Multi-Series Line Chart",
    [
      scene("s1", "title", 3, [
        title("t", "3억 원을 20년간", 760, { size: 100, anim: FADE(0.2) }),
        title("t2", "투자했다면", 900, { size: 100, color: C.accent, anim: FADE(0.7) }),
      ]),
      scene("s2", "chart", 11, [
        title("th", "20년 뒤 자산 (억 원)", 360, { size: 60, color: C.dim }),
        el({
          id: "chart",
          type: "line-chart",
          transform: box(W / 2, 1010, 900, 980),
          props: {
            series: [
              { values: coke, color: C.red, label: "코카콜라" },
              { values: sp, color: C.accent, label: "S&P 500" },
              { values: cash, color: C.teal, label: "현금" },
            ],
            yTicks: [
              [0, "0"],
              [30, "30"],
              [60, "60"],
              [90, "90"],
              [120, "120"],
              [150, "150"],
            ],
            legend: [
              { color: C.red, label: "코카콜라" },
              { color: C.accent, label: "S&P 500" },
              { color: C.teal, label: "현금" },
            ],
            strokeWidth: 7,
          },
          animations: FADE(0.2, 0.8),
          zIndex: 2,
        }),
        caption("lbl", "코카콜라 13.0억 · S&P 8.2억 · 현금 3.3억", 1560, {
          size: 40,
          color: C.dim,
        }),
      ]),
    ],
    {
      featuresTested: "line-chart series, yTicks, legend, shared-scale",
      dataDisclaimer: "검증용 가상 데이터 — 실제 수익률 아님",
    },
  );
}

// ── 04 Dividend Bar Chart ─────────────────────────────────────────────────────
function dividendBarChart(): MotionProject {
  return project(
    "04-dividend-bar-chart",
    "Dividend Bar Chart",
    [
      scene("s1", "title", 2.5, [
        title("t", "월별 배당금", 900, {
          size: 130,
          color: C.accent,
          anim: POP(0.1, 0.5),
        }),
      ]),
      scene("s2", "bars", 10.5, [
        title("th", "월별 배당금 (만원)", 360, { size: 58, color: C.dim }),
        el({
          id: "bars",
          type: "bar-chart",
          transform: box(W / 2, 940, 880, 820),
          props: {
            values: [42, 55, 38, 71, 64, 83],
            labels: ["1월", "2월", "3월", "4월", "5월", "6월"],
            color: C.accent,
            gap: 22,
          },
          animations: [enter("slide-up", 0.2, 0.7, { distance: 300 })],
          zIndex: 2,
        }),
        caption("peak", "최고 6월 83만 원", 1360, {
          size: 46,
          color: C.teal,
          anim: FADE(1.6),
        }),
        card("sumCard", box(W / 2, 1490, 620, 130), {
          fill: "#151a15",
          border: C.accent,
          anim: POP(6.0, 0.5),
        }),
        caption("sum", "월평균 59만 원", 1490, {
          size: 58,
          color: C.accent,
          start: 6.0,
          anim: FADE(6.2),
        }),
      ]),
    ],
    { featuresTested: "bar-chart labels, baseline, label-spacing, small-screen" },
  );
}

// ── 05 Person Story ───────────────────────────────────────────────────────────
function personStory(): MotionProject {
  const stop = (id: string, age: string, textLine: string, cy: number, start: number) => [
    card(`${id}-c`, box(W / 2, cy, 860, 200), {
      anim: [enter("slide-up", start, 0.6, { distance: 160 })],
    }),
    title(`${id}-a`, age, cy - 40, {
      size: 68,
      color: C.accent,
      start,
      anim: FADE(start + 0.2),
    }),
    caption(`${id}-t`, textLine, cy + 45, {
      size: 44,
      color: C.text,
      start,
      anim: FADE(start + 0.35),
    }),
  ];
  return project(
    "05-person-story",
    "Person Story",
    [
      scene("s1", "profile", 3.5, [
        el({
          id: "char",
          type: "character",
          transform: box(W / 2, 720, 320, 440),
          props: { color: C.teal, faceColor: "#0a0a0a" },
          animations: POP(0.2, 0.6),
          zIndex: 2,
        }),
        el({
          id: "pc",
          type: "profile-card",
          transform: box(W / 2, 1150, 760, 280),
          props: {
            title: "김도윤",
            subtitle: "평범한 정비공",
            accent: C.accent,
            background: C.bgCard,
            color: C.text,
          },
          animations: FADE(0.8, 0.6),
          zIndex: 3,
        }),
      ]),
      scene("s2", "timeline", 9.5, [
        title("th", "20년의 기록", 340, { size: 66, color: C.dim }),
        card("spine", box(W / 2, 950, 8, 760), {
          fill: C.border,
          border: "",
          borderWidth: 0,
          radius: 4,
        }),
        ...stop("st1", "35세", "매달 30만 원 투자 시작", 640, 0.3),
        ...stop("st2", "55세", "투자 자산 2억 4천만 원", 950, 1.6),
        ...stop("st3", "65세", "배당으로 생활비 충당", 1260, 2.9),
        caption("end", "시간이 가장 큰 자산이었다", 1500, {
          size: 52,
          color: C.accent,
          background: "#1a1a1a",
          start: 5.5,
          anim: POP(5.5, 0.5),
        }),
      ]),
    ],
    {
      featuresTested:
        "character, profile-card, timeline, placeholder-avatar, multi-scene",
    },
  );
}

// ── 06 Company Analysis ───────────────────────────────────────────────────────
function companyAnalysis(): MotionProject {
  const kpi = (
    id: string,
    val: string,
    label: string,
    cx: number,
    cy: number,
    start: number,
    color: string,
  ) => [
    card(`${id}-c`, box(cx, cy, 430, 300), { anim: POP(start, 0.5) }),
    title(`${id}-v`, val, cy - 30, {
      size: 76,
      color,
      cx,
      width: 400,
      start,
      anim: FADE(start + 0.2),
    }),
    caption(`${id}-l`, label, cy + 70, {
      size: 40,
      color: C.dim,
      cx,
      width: 400,
      start,
      anim: FADE(start + 0.3),
    }),
  ];
  return project(
    "06-company-analysis",
    "Company Analysis",
    [
      scene("s1", "logo", 3, [
        el({
          id: "logo",
          type: "topic-circle",
          transform: box(W / 2, 760, 260, 260),
          props: { label: "NC", fill: C.accent, color: "#0a0a0a", fontSize: 96 },
          animations: POP(0.1, 0.6),
          zIndex: 2,
        }),
        title("t", "NOVA Consumer", 1010, { size: 92, anim: FADE(0.6) }),
        caption("t2", "가상의 소비재 기업", 1140, {
          size: 44,
          color: C.dim,
          anim: FADE(1.0),
        }),
      ]),
      scene("s2", "kpi", 5, [
        title("th", "핵심 지표", 340, { size: 64, color: C.dim }),
        ...kpi("k1", "12.4조", "매출", 300, 640, 0.2, C.accent),
        ...kpi("k2", "18.2%", "영업이익률", 780, 640, 0.5, C.teal),
        ...kpi("k3", "3.4%", "배당수익률", 300, 990, 0.8, C.accent),
        ...kpi("k4", "41%", "부채비율", 780, 990, 1.1, C.text),
      ]),
      scene("s3", "revenue", 4, [
        title("th", "최근 5년 매출 (조원)", 360, { size: 56, color: C.dim }),
        el({
          id: "rev",
          type: "line-chart",
          transform: box(W / 2, 1000, 880, 900),
          props: {
            values: [8.9, 9.8, 10.6, 11.5, 12.4],
            color: C.accent,
            area: true,
            strokeWidth: 8,
            yTicks: [
              [0, "0"],
              [4, "4"],
              [8, "8"],
              [12, "12"],
            ],
          },
          animations: FADE(0.2, 0.7),
          zIndex: 2,
        }),
      ]),
      scene("s4", "table", 3, [
        el({
          id: "tbl",
          type: "table",
          transform: box(W / 2, 800, 860, 520),
          props: {
            rows: [
              ["지표", "값"],
              ["매출", "12.4조"],
              ["영업이익률", "18.2%"],
              ["배당수익률", "3.4%"],
              ["부채비율", "41%"],
            ],
            color: C.text,
            lineColor: C.border,
          },
          animations: FADE(0.2, 0.6),
          zIndex: 2,
        }),
        caption("c", "성장은 느리지만 현금흐름은 안정적", 1400, {
          size: 46,
          color: C.teal,
          background: "#101010",
          anim: FADE(0.8),
        }),
      ]),
    ],
    {
      featuresTested: "multi-component, table-cells, chart+cards, hierarchy, spacing",
      dataDisclaimer: "가상 기업 데이터",
    },
  );
}

// ── 07 Top Five Ranking ───────────────────────────────────────────────────────
function topFive(): MotionProject {
  const items: Array<[string, string]> = [
    ["5위", "낮은 비용"],
    ["4위", "분산"],
    ["3위", "현금흐름"],
    ["2위", "인출률"],
    ["1위", "꾸준함"],
  ];
  const rows = items.flatMap(([rank, label], i) => {
    const cy = 560 + i * 190;
    const start = 0.3 + i * 1.2;
    const top = rank === "1위";
    return [
      card(`r${i}-c`, box(W / 2, cy, 860, 160), {
        fill: top ? "#2a2410" : C.bgCard,
        border: top ? C.accent : C.border,
        borderWidth: top ? 4 : 2,
        start,
        anim: [enter("slide-left", start, 0.5, { distance: 300 })],
      }),
      title(`r${i}-rank`, rank, cy, {
        size: top ? 88 : 72,
        color: top ? C.accent : C.teal,
        cx: 250,
        width: 220,
        start,
        anim: POP(start + 0.1, 0.4),
      }),
      caption(`r${i}-lbl`, label, cy, {
        size: top ? 64 : 52,
        color: C.text,
        cx: 660,
        width: 480,
        start,
        anim: FADE(start + 0.25),
      }),
    ];
  });
  return project(
    "07-top-five",
    "Top Five Ranking",
    [
      scene("s1", "title", 2.5, [
        title("t1", "은퇴에서 중요한 것", 820, { size: 96, anim: FADE(0.2) }),
        title("t2", "TOP 5", 970, { size: 150, color: C.accent, anim: POP(0.7, 0.5) }),
      ]),
      scene("s2", "list", 9, [
        title("th", "중요한 것 TOP 5", 360, { size: 60, color: C.dim }),
        ...rows,
        caption("end", "수익률보다 지속 가능성", 1520, {
          size: 52,
          color: C.accent,
          background: "#1a1a1a",
          start: 6.8,
          anim: POP(6.8, 0.5),
        }),
      ]),
    ],
    { featuresTested: "repeated-component, stagger, list-spacing, rank-align" },
  );
}

// ── 08 Compound Growth ────────────────────────────────────────────────────────
function compoundGrowth(): MotionProject {
  const curve = [0, 0.3, 0.7, 1.2, 1.9, 2.8, 4.0, 5.6, 7.8, 10.8, 14.9, 20.4, 27.9];
  const markers: Array<[string, string, number]> = [
    ["10년", "8,650만 원", 0.5],
    ["20년", "2억 6,000만 원", 4.5],
    ["30년", "6억 1,000만 원", 8.5],
  ];
  return project(
    "08-compound-growth",
    "Compound Growth",
    [
      scene("s1", "setup", 3, [
        title("t", "매달 50만 원", 820, {
          size: 128,
          color: C.accent,
          anim: POP(0.1, 0.5),
        }),
        caption("c", "연 7% 수익률 가정", 990, {
          size: 52,
          color: C.dim,
          anim: FADE(0.7),
        }),
      ]),
      scene("s2", "growth", 12, [
        title("th", "복리 곡선 (만원 → 억)", 340, { size: 54, color: C.dim }),
        el({
          id: "curve",
          type: "line-chart",
          transform: box(W / 2, 940, 900, 820),
          props: {
            values: curve,
            color: C.teal,
            area: true,
            strokeWidth: 9,
            yTicks: [
              [0, "0"],
              [10, "1.3억"],
              [20, "3.9억"],
              [30, "6.1억"],
            ],
          },
          animations: FADE(0.2, 0.8),
          zIndex: 2,
        }),
        ...markers.flatMap(([age, val, start], i) => [
          title(`m${i}-a`, age, 1440, {
            size: 64,
            color: C.accent,
            start,
            duration: 12 - start,
            anim: POP(start, 0.4),
          }),
          title(`m${i}-v`, val, 1540, {
            size: 76,
            color: C.text,
            start,
            duration: 12 - start,
            anim: FADE(start + 0.2),
          }),
        ]),
        caption("end", "복리는 후반부에 강해진다", 1700, { size: 44, color: C.teal }),
      ]),
    ],
    {
      featuresTested: "number-swap, chart+timeline, markers, long-timespan, easing",
      dataDisclaimer: "가정값 기반 계산 예시",
    },
  );
}

// ── 09 Question and Answer ────────────────────────────────────────────────────
function questionAnswer(): MotionProject {
  return project(
    "09-question-answer",
    "Question and Answer",
    [
      scene("s1", "question", 5, [
        caption("qlbl", "질문", 440, {
          size: 60,
          color: C.accent,
          background: "#1a1a1a",
          width: 240,
          anim: POP(0.1, 0.5),
        }),
        el({
          id: "asker",
          type: "character",
          transform: box(280, 1120, 300, 400),
          props: { color: C.teal, faceColor: "#0a0a0a" },
          animations: [enter("slide-left", 0.3, 0.6, { distance: 200 })],
          zIndex: 2,
        }),
        el({
          id: "qb",
          type: "speech-bubble",
          transform: box(660, 780, 640, 300),
          props: {
            text: "배당주만 사면 은퇴?",
            background: C.text,
            color: "#111111",
            radius: 28,
          },
          animations: POP(0.6, 0.5),
          zIndex: 3,
        }),
      ]),
      scene("s2", "answer", 9, [
        caption("albl", "답변", 380, {
          size: 60,
          color: C.teal,
          background: "#1a1a1a",
          width: 240,
          anim: POP(0.1, 0.5),
        }),
        el({
          id: "expert",
          type: "character",
          transform: box(800, 1120, 300, 400),
          props: { color: C.accent, faceColor: "#0a0a0a" },
          animations: [enter("slide-right", 0.3, 0.6, { distance: 200 })],
          zIndex: 2,
        }),
        el({
          id: "ab",
          type: "speech-bubble",
          transform: box(430, 720, 720, 260),
          props: {
            text: "배당률보다 중요한 건",
            background: C.text,
            color: "#111111",
            radius: 28,
          },
          animations: POP(0.7, 0.5),
          zIndex: 3,
        }),
        caption("k1", "기업의 현금흐름", 1450, {
          size: 62,
          color: C.accent,
          background: "#111111",
          start: 2.0,
          anim: POP(2.0, 0.5),
        }),
        caption("k2", "배당 지속성", 1560, {
          size: 62,
          color: C.teal,
          background: "#111111",
          start: 3.0,
          anim: POP(3.0, 0.5),
        }),
      ]),
    ],
    { featuresTested: "speech-bubble, character-position, q/a-distinction, emphasis" },
  );
}

// ── 10 Full Showcase ──────────────────────────────────────────────────────────
function fullShowcase(): MotionProject {
  const curve = [0, 0.4, 0.9, 1.6, 2.6, 4.0, 5.9, 8.5, 12.1, 17.0, 23.7, 32.6];
  const p = project(
    "10-full-showcase",
    "Full Showcase Short",
    [
      scene("s1", "hook", 3, [
        title("h1", "평범한 사람이", 720, { size: 108, anim: FADE(0.2) }),
        title("h2", "매달 50만 원 투자하면", 880, {
          size: 92,
          color: C.accent,
          anim: FADE(0.7),
        }),
        title("h3", "30년 뒤?", 1080, { size: 150, color: C.teal, anim: POP(1.3, 0.5) }),
      ]),
      scene("s2", "condition", 3, [
        title("th", "투자 조건", 400, { size: 64, color: C.dim }),
        card("c1", box(W / 2, 760, 760, 220), { anim: POP(0.2, 0.5) }),
        title("c1v", "월 50만 원", 760, {
          size: 92,
          color: C.accent,
          start: 0.2,
          anim: FADE(0.4),
        }),
        card("c2", box(W / 2, 1060, 760, 220), { anim: POP(0.6, 0.5) }),
        title("c2v", "연 7% 수익", 1060, {
          size: 92,
          color: C.teal,
          start: 0.6,
          anim: FADE(0.8),
        }),
      ]),
      scene("s3", "numbers", 3, [
        caption("lbl", "자산이 불어난다", 700, {
          size: 52,
          color: C.dim,
          anim: FADE(0.2),
        }),
        title("n1", "1.8억", 980, {
          size: 150,
          color: C.text,
          start: 0.3,
          duration: 0.9,
          anim: POP(0.3, 0.4),
        }),
        title("n2", "3.9억", 980, {
          size: 170,
          color: C.accent,
          start: 1.2,
          duration: 0.9,
          anim: POP(1.2, 0.4),
        }),
        title("n3", "6.1억", 980, {
          size: 210,
          color: C.teal,
          start: 2.1,
          duration: 1.5,
          anim: POP(2.1, 0.4),
        }),
      ]),
      scene("s4", "chart", 4, [
        title("th", "복리 곡선", 380, { size: 60, color: C.dim }),
        el({
          id: "curve",
          type: "line-chart",
          transform: box(W / 2, 1000, 880, 900),
          props: {
            values: curve,
            color: C.teal,
            area: true,
            strokeWidth: 9,
            yTicks: [
              [0, "0"],
              [10, "1.9억"],
              [20, "3.8억"],
              [30, "6.1억"],
            ],
          },
          animations: FADE(0.2, 0.8),
          zIndex: 2,
        }),
      ]),
      scene("s5", "compare", 3, [
        title("th", "10 · 20 · 30년", 400, { size: 66, color: C.dim }),
        el({
          id: "cmp",
          type: "bar-chart",
          transform: box(W / 2, 1000, 820, 760),
          props: {
            values: [18, 39, 61],
            labels: ["10년", "20년", "30년"],
            color: C.accent,
            gap: 40,
          },
          animations: [enter("slide-up", 0.2, 0.6, { distance: 260 })],
          zIndex: 2,
        }),
      ]),
      scene("s6", "summary", 2, [
        title("s", "시간이 곧 복리다", 900, {
          size: 104,
          color: C.accent,
          anim: POP(0.1, 0.5),
        }),
      ]),
      scene("s7", "cta", 2, [
        title("f1", "큰돈보다", 860, { size: 120, anim: FADE(0.1) }),
        title("f2", "긴 시간이 먼저임", 1030, {
          size: 120,
          color: C.teal,
          anim: POP(0.5, 0.5),
        }),
        caption("cta", "구독하고 함께 모으기", 1480, {
          size: 48,
          color: C.accent,
          background: "#1a1a1a",
          start: 0.8,
          anim: FADE(1.0),
        }),
      ]),
    ],
    {
      featuresTested: "full-showcase, all-components, stagger, subtitle, parallel-render",
      isShowcase: true,
    },
  );
  // Subtitle track spanning the hook scene — verifies the time-aware subtitle component.
  p.scenes[0]!.elements.push(
    el({
      id: "sub",
      type: "subtitle",
      transform: box(W / 2, SAFE_BOTTOM - 40, W - 160, 130),
      props: {
        cues: [
          { start: 0.3, end: 1.4, text: "평범한 사람이" },
          { start: 1.4, end: 3.0, text: "매달 50만 원씩" },
        ],
        fontSize: 46,
        color: C.text,
        fontFamily: BODY_FONT,
      },
      zIndex: 20,
    }),
  );
  return p;
}

export const EXAMPLES: ExampleDef[] = [
  {
    id: "01-number-hook",
    name: "Number Hook",
    featuresTested: ["heavy-font", "number-swap", "pop/fade", "center-align"],
    build: numberHook,
  },
  {
    id: "02-ab-comparison",
    name: "A/B Comparison",
    featuresTested: ["two-column", "cards", "color-contrast", "layering"],
    build: abComparison,
  },
  {
    id: "03-multi-line-chart",
    name: "Multi-Series Line Chart",
    featuresTested: ["line-chart-series", "yTicks", "legend", "shared-scale"],
    build: multiLineChart,
  },
  {
    id: "04-dividend-bar-chart",
    name: "Dividend Bar Chart",
    featuresTested: ["bar-chart-labels", "baseline", "label-spacing"],
    build: dividendBarChart,
  },
  {
    id: "05-person-story",
    name: "Person Story",
    featuresTested: ["character", "profile-card", "timeline", "placeholder-avatar"],
    build: personStory,
  },
  {
    id: "06-company-analysis",
    name: "Company Analysis",
    featuresTested: ["multi-component", "table", "chart+cards", "hierarchy"],
    build: companyAnalysis,
  },
  {
    id: "07-top-five",
    name: "Top Five Ranking",
    featuresTested: ["repeated-component", "stagger", "list-spacing", "rank-align"],
    build: topFive,
  },
  {
    id: "08-compound-growth",
    name: "Compound Growth",
    featuresTested: ["number-swap", "chart+timeline", "markers", "easing"],
    build: compoundGrowth,
  },
  {
    id: "09-question-answer",
    name: "Question and Answer",
    featuresTested: ["speech-bubble", "character-position", "q/a", "emphasis"],
    build: questionAnswer,
  },
  {
    id: "10-full-showcase",
    name: "Full Showcase Short",
    featuresTested: ["all-components", "stagger", "subtitle", "parallel-render"],
    build: fullShowcase,
  },
];
