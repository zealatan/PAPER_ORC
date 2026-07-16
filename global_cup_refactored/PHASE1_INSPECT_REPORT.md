# PHASE 1 INSPECT REPORT
**Global Cup Golden Engine Transplant**
**Date:** 2026-06-06

---

## golden.py Engine Functions (lines 707–1471)

| Function | Signature | Returns |
|---|---|---|
| `find_alternating_high_low` | `(close, threshold=0.10)` | `(highs, lows)` — two lists of `(ts, price)` tuples |
| `classify_drop_bucket` | `(change_pct)` | Korean label or None |
| `classify_current_status` | `(change_pct)` | HTML span string |
| `build_current_status` | `(close, name, ticker, universe, threshold=0.10)` | dict or None |
| `build_drawdown_cycles` | `(close, name, ticker, universe, threshold=0.10)` | list of dicts |
| `nearest_trade_date` | `(close, target_date)` | pd.Timestamp or None |
| `run_backtest` | `(close, mode, initial_amount, periodic_amount, trigger_drop_pct)` | `(summary, trade_df, portfolio_df)` |
| `calculate_annual_dividends` | `(dividends, portfolio_df)` | DataFrame (Korean cols) |
| `run_dividend_backtest` | `(close, dividends, mode, ...)` | `(summary, trade_df, portfolio_df, annual_df)` |
| `run_dividend_reinvest_backtest` | `(close, dividends, mode, ...)` | 5-tuple |
| `add_high_low_markers` | `(fig, close, name, ticker, threshold=0.10)` | mutates fig in-place |

## Key Algorithm Differences from Refactored

### find_alternating_high_low
- golden: tracks both candidate_high AND candidate_low before direction establishes; direction established only at threshold crossing
- refactored (zigzag_engine.py): tracks single ext_price from index 0; direction established at first threshold crossing

### build_current_status ref-high logic
- golden: takes all ZigZag lows → last low → max price AFTER that low = reference high
- refactored: uses most recent ZigZag high directly as reference high

### run_backtest trigger mode
- golden: rolling-high tracker starting from close.iloc[0]; rearmed when price rebounds from post-trigger low by >= threshold
- refactored: ZigZag-highs based; finds first close <= trigger for each ZigZag high

### run_dividend_reinvest_backtest
- golden: year-end annual reinvestment using portfolio_df shares
- refactored (dividend_reinvest.py): per-event with tax rate; daily timeline

## Refactored Active Call Paths

```
run_analysis() [analysis.py]
  → build_current_status()      [zigzag_engine.py] ← REPLACE WITH golden_engine
  → run_backtest()              [backtest_engine.py] ← REPLACE WITH golden_engine

price_chart() [charts.py]
  → add_high_low_markers()      [charts.py] ← REPLACE WITH golden_engine version
  → add_trigger_buy_markers()   [charts.py] ← keep, update backtest_df format

render_dividend_reinvest_tab() [ui.py]
  → run_dividend_reinvest_backtest() [dividend_reinvest.py] ← KEEP refactored version
    (golden version has different signature; UI expects English keys + tax_rate param)
```

## Files to Create/Modify

| File | Action |
|---|---|
| `global_cup/golden_engine.py` | CREATE — exact copy of golden.py engine functions |
| `global_cup/analysis.py` | MODIFY — use golden_engine for ZigZag/backtest calls |
| `global_cup/charts.py` | MODIFY — use golden_engine.add_high_low_markers in price_chart |
| `global_cup/market_config.py` | MODIFY — change zigzag_points default |
| `global_cup/ui.py` | MODIFY — update Engine Debug panel for new h/l count source |
| `validate_against_golden.py` | CREATE — Phase 4 validation |

## PHASE 1: PASS
