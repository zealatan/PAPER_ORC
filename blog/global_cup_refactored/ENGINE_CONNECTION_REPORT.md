# ENGINE CONNECTION REPORT
**Phase 4 — Global Cup ZigZag Engine Restore**
**Date:** 2026-06-06  **Status: PASS**

---

## Active Call Chain

```
app.py
  └─ run_analysis(inp)                          ← analysis.py
       ├─ build_current_status(close, trigger)  ← zigzag_engine.py
       │    └─ find_alternating_high_low(close) ← zigzag_engine.py  ← CORE ENGINE
       └─ run_backtest(close, dividends, pct)   ← backtest_engine.py
            └─ find_alternating_high_low(close) ← zigzag_engine.py
```

```
ui.py → render_price_tab()
  ├─ st.checkbox "Show ZigZag H/L markers"
  ├─ st.checkbox "Show Trigger Buy markers"
  ├─ price_chart(inp, config, result,
  │     show_zigzag=..., show_buys=...)         ← charts.py
  │     ├─ add_high_low_markers(fig, points)    ← charts.py
  │     │    ├─ ZigZag Highs: triangle-up  H
  │     │    └─ ZigZag Lows:  triangle-down L
  │     ├─ add_trigger_buy_markers(fig, df)     ← charts.py
  │     │    └─ Buy events: star  Buy
  │     └─ trigger hline from zigzag_trigger_price
  └─ Engine Debug Expander
       ├─ Ticker, Threshold, Trigger %
       ├─ ZigZag Highs count, ZigZag Lows count, Trigger Buys count
       ├─ ZigZag Ref High, ZigZag Ref Low, ZigZag Drawdown
       ├─ Drop Bucket, Status, Trigger Status
       └─ Trigger Buy Events table (backtest_df)
```

## Chart Behavior Checklist

| Requirement | Status |
|---|---|
| Price line | ✅ |
| ZigZag highs — triangle-up, text=H | ✅ |
| ZigZag lows — triangle-down, text=L | ✅ |
| Trigger buys — star, text=Buy | ✅ |
| Trade events visible in debug expander | ✅ |
| Trigger percentage configurable | ✅ (existing UI input) |
| Show/Hide H/L checkbox | ✅ |
| Show/Hide Buy markers checkbox | ✅ |
| Engine Debug Expander | ✅ |

## Fields Added to AnalysisResult

```python
zigzag_points          List[ZigZagPoint]   # all alternating H/L points
zigzag_ref_high_price  float               # most recent ZigZag high
zigzag_ref_high_date   pd.Timestamp
zigzag_ref_low_price   float               # most recent ZigZag low
zigzag_ref_low_date    pd.Timestamp
zigzag_drawdown_pct    float               # drawdown from ZigZag ref high
zigzag_trigger_price   float               # trigger computed from ZigZag high
zigzag_trigger_hit     bool
drop_bucket            str                 # "Minor Pullback", "Correction", etc.
status_label           str                 # "At High" / "Watching" / "Trigger Hit"
high_count             int
low_count              int
backtest_df            pd.DataFrame | None # one row per trigger buy event
```

## Backward Compatibility

Existing fields (`high_price`, `drawdown_pct`, `trigger_price`, `trigger_hit`)
remain computed from `close.max()` — `validate_engine.py` continues to pass.
