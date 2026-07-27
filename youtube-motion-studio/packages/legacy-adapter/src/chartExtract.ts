/**
 * Translate the PG deck's chart/table data into real chart-component props (spec §26.3, step 7:
 * "replace legacy components incrementally"). Returns the target component type + props, or null
 * when the data cannot be translated (the caller then falls back to a placeholder).
 */
function num(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function parseMoney(value: unknown): number {
  if (typeof value === "number") return value;
  if (typeof value !== "string") return 0;
  const n = Number(value.replace(/[^0-9.]/g, ""));
  return Number.isFinite(n) ? n : 0;
}

function downsample(values: number[], max = 80): number[] {
  if (values.length <= max) return values;
  const step = values.length / max;
  const out: number[] = [];
  for (let i = 0; i < max; i += 1) out.push(values[Math.floor(i * step)] ?? 0);
  return out;
}

function seriesY(pts: unknown): number[] {
  if (!Array.isArray(pts)) return [];
  return pts.map((p) => (Array.isArray(p) ? num(p[1]) : 0));
}

const asObj = (v: unknown): Record<string, unknown> =>
  v && typeof v === "object" ? (v as Record<string, unknown>) : {};
const asArr = (v: unknown): unknown[] => (Array.isArray(v) ? v : []);

export interface ExtractedChart {
  type: string;
  props: Record<string, unknown>;
}

export function extractChart(
  tpl: string,
  data: Record<string, unknown>,
): ExtractedChart | null {
  switch (tpl) {
    case "enginechart": {
      const chart = asObj(data.chart);
      const series = asArr(chart.series);
      const first = asObj(series[0]);
      const values = downsample(seriesY(first.pts));
      if (values.length < 2) return null;
      return { type: "line-chart", props: { values, area: true, color: "#4aa3ff" } };
    }
    case "reelchart": {
      const lines = asArr(data.lines);
      const first = asObj(lines[0]);
      const values = downsample(seriesY(first.pts));
      if (values.length < 2) return null;
      const color = typeof first.c === "string" ? first.c : "#4aa3ff";
      return { type: "line-chart", props: { values, color, strokeWidth: 5 } };
    }
    case "divbars": {
      const vals = asArr(data.vals).map((v) => (Array.isArray(v) ? num(v[1]) : num(v)));
      const values = downsample(vals, 60);
      if (values.length < 1) return null;
      return { type: "bar-chart", props: { values, color: "#ffd000", gap: 3 } };
    }
    case "hbars2": {
      const left = asObj(data.left);
      const right = asObj(data.right);
      const rows = [...asArr(left.rows), ...asArr(right.rows)].map((r) => {
        const row = asObj(r);
        return parseMoney(row.label) || num(row.inv) + num(row.gain) + num(row.div);
      });
      if (rows.length === 0) return null;
      return { type: "bar-chart", props: { values: rows, color: "#3fc890" } };
    }
    case "menuboard": {
      const segments = asArr(data.segments).map((s) => num(asObj(s).pct));
      if (segments.length === 0) return null;
      return { type: "bar-chart", props: { values: segments, color: "#4a8dff" } };
    }
    case "checks": {
      const rows = asArr(data.items)
        .filter((r) => Array.isArray(r))
        .map((r) => (r as unknown[]).map((c) => String(c)));
      if (rows.length === 0) return null;
      return { type: "table", props: { rows } };
    }
    default:
      return null;
  }
}
