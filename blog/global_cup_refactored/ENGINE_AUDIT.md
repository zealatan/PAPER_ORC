# ENGINE AUDIT
### Global Cup Market Dashboard — Calculation Engine Analysis
**Audited:** 2026-06-05  
**Auditor:** Claude Code (claude-sonnet-4-6)  
**Source of truth:** `invest/global_cup_dividend_reinvest_ported.py`

---

## ⚠️  CRITICAL FINDING — ZigZag Engine Does Not Exist in This Codebase

The previous step-002 prompt warns heavily about preserving a function named
`find_alternating_high_low()` and a "ZigZag engine".  After a full audit of
every Python file in the project, **none of those functions exist**:

| Function mentioned in prompt | Present in codebase? |
|---|---|
| `find_alternating_high_low()` | **NO** |
| `build_current_status()` | **NO** |
| `build_drawdown_cycles()` | **NO** |
| `run_backtest()` | **NO** |
| `run_dividend_backtest()` | **NO** |

Files searched:
- `invest/global_cup_dividend_reinvest_ported.py` (1 597 lines)
- `invest/backup_original/global_cup_dividend_reinvest_ported.py`
- All files under `invest/global_cup_refactored/`

The prompt may describe a planned future engine, a different version of the
project, or functions that were removed before the current version was
committed.  **The actual engine uses simpler, direct pandas operations.**

---

## 1. Actual Engine — `run_analysis()`

**File:** `invest/global_cup_dividend_reinvest_ported.py` lines 898–954  
**Refactored equivalent:** `global_cup_refactored/global_cup/analysis.py` lines 31–85

### 1a. How the reference HIGH is selected

```python
high_date  = close.idxmax()   # date of the absolute period maximum
high_price = float(close.max()) # value of the absolute period maximum
```

This is a **simple all-time high** over the user-selected date range.  
There is NO alternating ZigZag pattern, NO rolling window, NO cycle detection.

The reference high is the single highest closing price in the entire date range.

### 1b. How the reference LOW is selected

There is no separate reference low in the current engine.

The "low" concept is implicit: `current_price` is compared against `high_price`
to produce the drawdown percentage.

### 1c. How current drawdown is computed

```python
drawdown_pct = (current_price / high_price - 1.0) * 100.0
```

- `current_price` = `close.iloc[-1]` (the last close in the date range)
- `high_price`    = `close.max()` (the period maximum)
- Result is always ≤ 0.0 when below the high, 0.0 at the high

### 1d. How trigger detection works

```python
trigger_price = high_price * (1.0 - inp.trigger_pct / 100.0)
trigger_hit   = drawdown_pct <= -inp.trigger_pct
```

- User sets `trigger_pct` (default 10%)
- A trigger fires when current price has dropped ≥ trigger_pct from the period high
- `trigger_hit` is a boolean; no "drop bucket" or multi-level classification exists

### 1e. Dividend TTM yield calculation

```python
ttm_start    = current_date - pd.Timedelta(days=365)
ttm_dividend = float(dividends[dividends.index >= ttm_start].sum())
dividend_yield = (ttm_dividend / current_price * 100.0)
```

Trailing-twelve-months dividend divided by current price.

---

## 2. Dividend Reinvestment Engine — `run_dividend_reinvest_backtest()`

**File:** `invest/global_cup_dividend_reinvest_ported.py` lines 980–1144  
**Refactored equivalent:** `global_cup_refactored/global_cup/dividend_reinvest.py`

### Algorithm (chronological simulation)

1. **Initial buy** on the first trading day: `shares = initial_amount / price`
2. **Monthly buy** on the first trading day of each subsequent calendar month
   (only if `monthly_amount > 0`)
3. **Dividend reinvestment**: for each dividend ex-date, find the next trading
   day (using `_next_trade_date()`), compute gross dividend from current share
   count, subtract `tax_rate`, reinvest net amount at that day's closing price
4. **Timeline** is built row-by-row, tracking cumulative portfolio value, PnL,
   and share count
5. **CAGR** is computed from final value / total external invested over the
   number of actual calendar years

### Tax handling

```python
tax_rate  = tax_rate_pct / 100.0   # clamped to [0, 100]
tax       = gross_dividend * tax_rate
net_dividend = gross_dividend - tax
reinvest_shares = net_dividend / price
```

Market-specific default tax rates:
- United States: 15.0%
- Korea:         15.4%
- Japan:         20.315%
- European Union / Global: 15.0%

### Helper: `_next_trade_date(close, target_date)`

Returns the first date in `close.index` that is ≥ `target_date`.
Used to map dividend ex-dates to actual trading days.

### Helper: `_first_trade_date_of_month(close, year, month)`

Returns the first trading day of a given calendar month.
Used to schedule monthly DCA buys.

---

## 3. Data Layer

| Function | File | Purpose |
|---|---|---|
| `download_price()` | `data_loader.py` | `yf.download()` with `auto_adjust=False`, MultiIndex flattening, timezone normalization |
| `download_dividends()` | `data_loader.py` | `yf.Ticker(t).dividends` filtered to date range |
| `get_close_series()` | `data_loader.py` | Extract clean `pd.Series` from price DataFrame |

Both download functions are decorated with `@st.cache_data(ttl=3600)`.

---

## 4. Scoring Engine (refactored addition — informational only)

**File:** `global_cup_refactored/global_cup/scoring.py`

Four components, combined with fixed weights:

| Component | Weight | Formula |
|---|---|---|
| Drawdown attractiveness | 35% | `min(100, abs(drawdown_pct) * 3.5)` |
| Dividend yield | 30% | `min(100, yield_pct * 15)` |
| Momentum (contrarian) | 20% | `50 - momentum_3m * 2` clamped to [0,100] |
| Dividend consistency | 15% | `years_with_div / total_years * 100` |

Score is informational only — does **not** affect the drawdown, trigger, or
dividend engines.

---

## 5. Functions That Depend on the Core Engine

| Caller | Depends on | Location |
|---|---|---|
| `render_price_tab` | `run_analysis()` → `high_price`, `high_date`, `trigger_price` | `ui.py` |
| `render_score_section` | `run_analysis()` → `drawdown_pct`, `dividend_yield` | `ui.py` |
| `render_market_ranking` | `run_analysis()` × 5 markets | `ui.py` |
| `render_dividend_reinvest_tab` | `run_dividend_reinvest_backtest()` | `ui.py` |
| `calculate_score` | `run_analysis()` output fields | `scoring.py` |
| `price_chart` | `result.high_price`, `result.high_date`, `result.trigger_price` | `charts.py` |
| `validate_engine.py` | Both engines | `validate_engine.py` |

---

## 6. Refactoring Status

| Module | Status |
|---|---|
| `global_cup/data_loader.py` | ✅ Logic identical to original |
| `global_cup/analysis.py` | ✅ Logic identical to original |
| `global_cup/dividend_reinvest.py` | ✅ Logic identical to original |
| `global_cup/market_config.py` | ✅ Dataclasses + market registry preserved |
| `global_cup/config.py` | ✅ Constants extracted cleanly |
| `global_cup/charts.py` | ✅ Chart rendering extracted; logic unchanged |
| `global_cup/scoring.py` | ✅ New informational-only module |
| `global_cup/ui.py` | ✅ All UI rendering extracted |
| `app.py` | ✅ Thin orchestration layer |

Original file `global_cup_dividend_reinvest_ported.py` and
`backup_original/` directory are **untouched**.
