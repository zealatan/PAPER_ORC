# ZIGZAG ENGINE AUDIT
**Phase 2 — Global Cup ZigZag Engine Restore**
**Date:** 2026-06-06  **Status: PASS**

---

## Audit Questions

| Question | Finding |
|---|---|
| Is ZigZag engine called? | **NO** — function does not exist |
| Is build_current_status used? | **NO** — function does not exist |
| Are H/L markers connected to charts? | **NO** — no triangle-up/down in charts.py or ui.py |
| Are trade events connected to charts? | **NO** — no Buy marker code anywhere |
| Is trigger logic active? | **PARTIAL** — close.max() based only, not ZigZag-based |
| Is dividend reinvestment engine active? | **YES** — run_dividend_reinvest_backtest() wired |

---

## Root Cause Analysis

### Root Cause 1 — MISSING ENGINE (critical)

None of the six required ZigZag functions exist in any Python file:
`find_alternating_high_low`, `build_current_status`, `build_drawdown_cycles`,
`run_backtest`, `run_dividend_backtest`, `add_high_low_markers`.

These functions were never implemented; the refactor inherited the simpler
`close.max()` approach from the original monolith.

### Root Cause 2 — SIMPLE HIGH SUBSTITUTION (critical)

`global_cup/analysis.py` computes the reference high as:
```python
high_date  = close.idxmax()
high_price = float(close.max())
```
This finds the single absolute maximum over the entire date range. It does not
detect alternating swing highs and lows. As a result:
- Only one HIGH marker ever appears on the chart
- No LOW markers appear
- Trigger fires against the all-time high, not the most recent local high
- No cycle detection, no "drop bucket", no status classification

### Root Cause 3 — CHART PIPELINE INCOMPLETE (critical)

`global_cup/charts.py` has no H/L marker traces. The current `price_chart()`
plots only: close line, single-high marker (triangle-up), single-current marker
(circle), trigger hline, dividend diamond markers.

`ui.py` has no calls to any H/L marker function.

### Root Cause 4 — NO TRIGGER BACKTEST (moderate)

The app produces a single boolean `trigger_hit`. There is no historical backtest
of trigger events: no `run_backtest()` to find all past ZigZag highs, compute
their trigger prices, and record when/if each was hit. Buy markers therefore
cannot appear on the chart.

---

## Fix Plan

1. Create `global_cup/zigzag_engine.py` with the full ZigZag detection engine
2. Create `global_cup/backtest_engine.py` with trigger backtest and dividend analysis
3. Extend `AnalysisResult` with new ZigZag fields (no existing fields removed)
4. Update `analysis.py` to call ZigZag engine and populate new fields
5. Update `charts.py` to add `add_high_low_markers()` and `add_trigger_buy_markers()`
6. Update `ui.py` to use ZigZag fields, add Show/Hide checkbox, add debug expander
7. Preserve existing `high_price`/`drawdown_pct` from `close.max()` so
   `validate_engine.py` continues to pass
