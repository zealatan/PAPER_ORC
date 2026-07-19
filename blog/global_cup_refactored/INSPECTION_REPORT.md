# INSPECTION REPORT
**Phase 1 — Global Cup ZigZag Engine Restore**
**Date:** 2026-06-06  **Status: PASS**

---

## Functions Found

| Function | Status | Location |
|---|---|---|
| `find_alternating_high_low` | **MISSING** | — |
| `build_current_status` | **MISSING** | — |
| `build_drawdown_cycles` | **MISSING** | — |
| `run_backtest` | **MISSING** | — |
| `run_dividend_backtest` | **MISSING** | — |
| `run_dividend_reinvest_backtest` | FOUND | `global_cup/dividend_reinvest.py` |
| `add_high_low_markers` | **MISSING** | — |

Only one of the seven required functions exists. Six must be created.

## Active Streamlit Entry Point

`global_cup_refactored/app.py`

## Active Chart Rendering Path

`global_cup/charts.py` → functions: `price_chart`, `dividend_bar_chart`,
`reinvest_timeline_chart`, `share_count_chart`, `score_gauge_chart`

`price_chart` is called by `ui.py → render_price_tab`.

Neither `add_high_low_markers` nor any ZigZag calls exist in the chart pipeline.

## Files Searched

- All `.py` under `global_cup_refactored/`
- `../global_cup_dividend_reinvest_ported.py` (original)
- `../backup_original/global_cup_dividend_reinvest_ported.py` (backup)

**Important:** The six missing functions do not exist in the original file either.
They must be implemented from the described specification. The original file uses
`close.idxmax()` / `close.max()` — a simple period-high approach — without any
ZigZag pattern detection. The ZigZag engine is to be created as the trusted
replacement that provides alternating H/L detection.

## Phase 1 Verdict

PASS — inspection completed. Root cause ready for Phase 2.
