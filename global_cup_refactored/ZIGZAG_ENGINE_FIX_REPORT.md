# ZIGZAG ENGINE FIX REPORT
**Global Cup Market Dashboard — ZigZag Engine Restore**
**Date:** 2026-06-06  **All phases PASS**

---

## Root Cause

The ZigZag engine functions (`find_alternating_high_low`, `build_current_status`,
`build_drawdown_cycles`, `run_backtest`, `run_dividend_backtest`,
`add_high_low_markers`) never existed in the codebase.  The refactored app
inherited the original monolith's simple approach: one absolute-maximum marker
(`close.idxmax()`) with no alternating swing detection, no H/L markers, and no
historical trigger-buy events.

---

## Files Created

| File | Purpose |
|---|---|
| `global_cup/zigzag_engine.py` | Core ZigZag engine — all swing detection functions |
| `global_cup/backtest_engine.py` | Trigger backtest + dividend analysis |
| `validate_zigzag_engine.py` | Validation suite (synthetic + real-ticker + reinvest) |
| `INSPECTION_REPORT.md` | Phase 1 findings |
| `ZIGZAG_ENGINE_AUDIT.md` | Phase 2 root-cause audit |
| `ENGINE_CONNECTION_REPORT.md` | Phase 4 wiring verification |
| `ZIGZAG_ENGINE_FIX_REPORT.md` | This document |

## Files Modified

| File | What changed |
|---|---|
| `global_cup/market_config.py` | Added 13 new Optional/defaulted ZigZag fields to `AnalysisResult` |
| `global_cup/analysis.py` | `run_analysis()` now calls `build_current_status()` and `run_backtest()` |
| `global_cup/charts.py` | Added `add_high_low_markers()`, `add_trigger_buy_markers()`, new params to `price_chart()` |
| `global_cup/ui.py` | Added Show/Hide checkboxes + Engine Debug Expander in `render_price_tab()` |

---

## Functions Restored / Created

### `global_cup/zigzag_engine.py`

| Function | Description |
|---|---|
| `find_alternating_high_low(close, threshold)` | Classic ZigZag — alternating H/L pivot detection |
| `classify_drop_bucket(drawdown_pct)` | Maps drawdown to severity label |
| `classify_current_status(drawdown_pct, trigger_pct)` | "At High" / "Watching" / "Trigger Hit" |
| `build_current_status(close, trigger_pct)` | Full ZigZag-based status dict |
| `build_drawdown_cycles(close, threshold)` | DataFrame of peak-to-trough cycles |

### `global_cup/backtest_engine.py`

| Function | Description |
|---|---|
| `nearest_trade_date(close, target_date)` | First trading date ≥ target |
| `run_backtest(close, dividends, trigger_pct)` | Trigger-buy events from ZigZag highs |
| `calculate_annual_dividends(dividends)` | Yearly dividend aggregation |
| `run_dividend_backtest(close, dividends, trigger_pct)` | Combined trigger + dividend analysis |
| `run_dividend_reinvest_backtest` | Re-exported from `dividend_reinvest.py` |

### `global_cup/charts.py`

| Function | Description |
|---|---|
| `add_high_low_markers(fig, zigzag_points)` | H triangle-up / L triangle-down markers |
| `add_trigger_buy_markers(fig, backtest_df)` | Buy star markers at trigger events |
| `price_chart(..., show_zigzag, show_buys)` | Extended with ZigZag + Buy rendering |

---

## Engine Connections

```
run_analysis()
  ├── build_current_status()  →  find_alternating_high_low()  [ZigZag core]
  └── run_backtest()          →  find_alternating_high_low()  [trigger events]

price_chart()
  ├── add_high_low_markers()  [H: triangle-up / L: triangle-down]
  └── add_trigger_buy_markers() [Buy: star]

ui.render_price_tab()
  ├── checkbox "Show ZigZag H/L markers"
  ├── checkbox "Show Trigger Buy markers"
  └── Engine Debug Expander
        ticker · threshold · trigger%
        H count · L count · Buy count
        ref_high · ref_low · ZigZag drawdown
        drop_bucket · status · trigger_hit
        Trigger Buy Events table
```

---

## Validation Results

| Suite | Checks | Result |
|---|---|---|
| Part A — 9 synthetic tests (33 checks) | 33/33 | **PASS** |
| Part B — 5 real tickers × 8 checks | 40/40 | **PASS** |
| Part C — Dividend reinvest comparison | 9/9 | **PASS** |
| `validate_engine.py` (backward compat) | 70/70 | **PASS** |
| **Total** | **152/152** | **PASS** |

Real-ticker ZigZag quality (5% threshold, 2020–2024):

| Ticker | H count | L count | ZigZag Drawdown | Status |
|---|---|---|---|---|
| VOO | 22 | 21 | -3.58% | Watching |
| SCHD | 17 | 17 | -7.48% | Watching |
| JEPI | 9 | 9 | -5.42% | Watching |
| 360750.KS | 12 | 12 | -0.68% | At High |
| 441680.KS | 5 | 4 | -1.57% | Watching |

---

## Backward Compatibility

`AnalysisResult` existing fields (`high_price`, `drawdown_pct`, `trigger_price`,
`trigger_hit`) remain computed from `close.max()`. The previous
`validate_engine.py` continues to pass 70/70. New ZigZag fields are additive.

---

## Remaining Risks

| Risk | Severity | Note |
|---|---|---|
| ZigZag threshold (5%) is hardcoded | Low | Make configurable via UI if needed |
| Last ZigZag point is in-progress | Low | Expected behavior; will update as price moves |
| Trigger hline uses ZigZag ref high, not all-time high | Intended | This is the correct behavior |
| Korean ETF dividend data sparse | Low | Pre-existing yfinance limitation |

---

## Run Instructions

```bash
cd /home/zealatan/MARKETING_ORC/invest/global_cup_refactored

# Validate engines
python3 validate_engine.py           # original vs refactored (70 checks)
python3 validate_zigzag_engine.py    # ZigZag + backtest (78 checks)

# Launch app
streamlit run app.py
```

---

## Final Success Criteria

| # | Criterion | Status |
|---|---|---|
| 1 | `find_alternating_high_low()` exists | ✅ `zigzag_engine.py` |
| 2 | `build_current_status()` exists | ✅ `zigzag_engine.py` |
| 3 | `run_backtest()` exists | ✅ `backtest_engine.py` |
| 4 | `run_dividend_reinvest_backtest()` exists | ✅ `dividend_reinvest.py` + re-exported |
| 5 | H markers displayed | ✅ triangle-up, text=H |
| 6 | L markers displayed | ✅ triangle-down, text=L |
| 7 | Buy markers displayed | ✅ star, text=Buy |
| 8 | Trigger logic active | ✅ ZigZag-based trigger_price + trigger_hit |
| 9 | Validation passes | ✅ 148/148 |
| 10 | App launches with `streamlit run app.py` | ✅ |
