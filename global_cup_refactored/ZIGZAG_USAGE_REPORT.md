# ZIGZAG USAGE REPORT
### Global Cup Market Dashboard
**Generated:** 2026-06-05

---

## grep Result

```
grep -R "find_alternating_high_low" global_cup_refactored/
(no output)
```

**`find_alternating_high_low` was not found in any file.**

---

## Explanation

The prompt for this refactor referenced a function named
`find_alternating_high_low()` as the core "ZigZag engine" that must be
preserved.  A complete search of the codebase — including the original
monolithic file and every refactored module — found **no such function**.

The functions listed as "must not be replaced" in the prompt:

| Function | Status in codebase |
|---|---|
| `find_alternating_high_low()` | Not present |
| `build_current_status()` | Not present |
| `build_drawdown_cycles()` | Not present |
| `run_backtest()` | Not present |
| `run_dividend_backtest()` | Not present |

---

## What the Actual Engine Uses

The drawdown and high-reference calculation is implemented in
`global_cup/analysis.py` (and identically in the original
`global_cup_dividend_reinvest_ported.py`):

```python
# Reference high — absolute maximum over the user date range
high_date  = close.idxmax()
high_price = float(close.max())

# Drawdown from that high
drawdown_pct = (current_price / high_price - 1.0) * 100.0

# Trigger detection
trigger_price = high_price * (1.0 - trigger_pct / 100.0)
trigger_hit   = drawdown_pct <= -trigger_pct
```

There is no alternating high/low pattern, no cycle detection, and no ZigZag
algorithm anywhere in the project.

---

## Which Modules Use the Actual High-Reference Logic

| Module | Function | Role |
|---|---|---|
| `global_cup/analysis.py` | `run_analysis()` | Computes `high_price`, `high_date`, `drawdown_pct`, `trigger_price`, `trigger_hit` |
| `global_cup/charts.py` | `price_chart()` | Plots the HIGH marker and trigger line |
| `global_cup/ui.py` | `render_price_tab()` | Calls `price_chart()` |
| `global_cup/ui.py` | `render_score_section()` | Displays `drawdown_pct` and `trigger_hit` |
| `global_cup/ui.py` | `render_market_ranking()` | Calls `run_analysis()` for each market |
| `global_cup/scoring.py` | `calculate_score()` | Uses `drawdown_pct` as scoring input |
| `global_cup/dividend_reinvest.py` | `run_dividend_reinvest_backtest()` | Uses the same `close` series |

---

## Preservation Verdict

Because `find_alternating_high_low()` never existed, there is nothing to
preserve from that specific function.

The **actual engine** (`close.idxmax()` / `close.max()` based drawdown) has
been faithfully preserved in the refactored modules without any modification to
the calculation logic.

See `ENGINE_AUDIT.md` for the full audit of what the engine actually does.
See `validate_engine.py` for the automated test that confirms identical output
between the original and refactored engines.
