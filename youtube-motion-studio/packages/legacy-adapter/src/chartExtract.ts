/**
 * Translate the PG deck's chart/table data into real chart-component props (spec §26.3, step 7:
 * "replace legacy components incrementally"). Returns the target component type + props, or null
 * when the data cannot be translated (the caller then falls back to a placeholder).
 */
function num(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function str(value: unknown, fallback: string): string {
  return typeof value === "string" && value.length > 0 ? value : fallback;
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

const PALETTE = ["#4aa3ff", "#ffd000", "#3fc890", "#ff7a68", "#c084fc"];

interface ExtractedSeries {
  values: number[];
  color: string;
  label?: string;
}

function tuplesToTicks(raw: unknown): [number, string][] {
  return asArr(raw)
    .filter((t): t is unknown[] => Array.isArray(t) && t.length >= 2)
    .map((t) => [num(t[0]), String(t[1])] as [number, string]);
}

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
      const series: ExtractedSeries[] = asArr(chart.series)
        .map((s, i) => {
          const o = asObj(s);
          return {
            values: downsample(seriesY(o.pts)),
            color: str(o.c, PALETTE[i % PALETTE.length]!),
          };
        })
        .filter((s) => s.values.length >= 2);
      if (series.length === 0) return null;
      return {
        type: "line-chart",
        props: {
          series,
          area: series.length === 1,
          yTicks: tuplesToTicks(chart.yticks),
          color: series[0]!.color,
        },
      };
    }
    case "reelchart": {
      const series: ExtractedSeries[] = asArr(data.lines)
        .map((l, i) => {
          const o = asObj(l);
          return {
            values: downsample(seriesY(o.pts)),
            color: str(o.c, PALETTE[i % PALETTE.length]!),
            label: str(o.name, ""),
          };
        })
        .filter((s) => s.values.length >= 2);
      if (series.length === 0) return null;
      const legend = asArr(data.legend)
        .map((e) => ({
          color: str(asObj(e).c, "#888888"),
          label: str(asObj(e).label, ""),
        }))
        .filter((e) => e.label.length > 0);
      return { type: "line-chart", props: { series, legend, strokeWidth: 5 } };
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
      const rows = [...asArr(left.rows), ...asArr(right.rows)].map((r) => asObj(r));
      if (rows.length === 0) return null;
      const values = rows.map(
        (row) => parseMoney(row.label) || num(row.inv) + num(row.gain) + num(row.div),
      );
      const labels = rows.map((row) => str(row.name, ""));
      return { type: "bar-chart", props: { values, labels, color: "#3fc890" } };
    }
    case "menuboard": {
      const segments = asArr(data.segments).map((s) => asObj(s));
      if (segments.length === 0) return null;
      return {
        type: "bar-chart",
        props: {
          values: segments.map((s) => num(s.pct)),
          labels: segments.map((s) => str(s.ko, "")),
          color: "#4a8dff",
        },
      };
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
