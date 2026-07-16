# Date Control & History Fix Report
**Date:** 2026-06-06  **Status: ALL SUCCESS**

---

## Validation

| Check | Result |
|---|---|
| `python3 -m py_compile app.py` | OK |
| `python3 -m py_compile global_cup/*.py` | ALL OK |
| `python3 validate_against_golden.py` | **122/122 PASS** |
| `python3 validate_history_range.py` | **ALL OK** |
| `golden_engine.py` modified | **NO — 0 diff lines** |

---

## Files Modified

| File | Changes |
|---|---|
| `global_cup/ui.py` | Removed `st.expander("Advanced settings")` wrapper; added `render_data_range_info()` |
| `app.py` | Added `data_range_container = st.container()` + `render_data_range_info(analysis, user_input.start_date)`; imported `render_data_range_info` |

## Files Created

| File | Purpose |
|---|---|
| `validate_history_range.py` | Diagnostics: VOO/SPY/QQQ actual data range vs 2000-01-01 request |
| `DATE_HISTORY_AUDIT.md` | Full audit of start_date flow and root cause analysis |
| `DATE_CONTROL_AND_HISTORY_FIX_REPORT.md` | This report |

## Files NOT Modified

- `global_cup/golden_engine.py` — **0 diff lines**
- `global_cup/analysis.py` — untouched
- `global_cup/data_loader.py` — untouched (already correct)
- `global_cup/charts.py` — untouched
- `global_cup/market_config.py` — untouched
- `validate_against_golden.py` — untouched

---

## Task 1 — Advanced Settings Expander Removed

**Where:** `global_cup/ui.py` → `render_controls()` (~line 840)

**Before:**
```python
with st.expander("Advanced settings", expanded=False):
    col3, col4 = st.columns(2)
    with col3:
        raw_start = st.text_input("Start date  (YYYY-MM-DD)", ...)
    with col4:
        raw_end = st.text_input("End date  (YYYY-MM-DD)", ...)
```

**After:**
```python
col3, col4 = st.columns(2)
with col3:
    raw_start = st.text_input("Start date  (YYYY-MM-DD)", ...)
with col4:
    raw_end = st.text_input("End date  (YYYY-MM-DD)", ...)
```

Left column now shows:
1. Ticker search
2. Trigger %
3. Start date ← always visible
4. End date ← always visible
5. Available data range info (after analysis)
6. Dividend reinvestment controls + summary

---

## Task 2 — Date Input UX

- `placeholder` changed from `"e.g. 2019-01-01"` to `"e.g. 2000-01-01"` to signal older dates are valid.
- Text input accepts any YYYY-MM-DD format — no widget minimum date restriction.
- `_parse_date()` handles free-form text entry with fallback to default.

---

## Task 3 — Historical Data Root Cause

**Finding: No bug exists.**

The codebase does not contain any hardcoded date truncation:
- No `2010` or `2020` cutoffs in source
- `data_loader.py` always uses `yf.download(start=start_date, end=end_date+1day)`
- Cache key is `(ticker, start_date, end_date)` — stale cache not possible across different date inputs

**Why VOO shows data from ~2010:** VOO (Vanguard S&P 500 ETF) was listed September 9, 2010.
Requesting `start=2000-01-01` correctly returns data from VOO's actual inception.
This is Yahoo Finance's earliest available data for the ticker.

---

## Task 5 — Actual Data Range Display

New function `render_data_range_info(result, requested_start)` added to `global_cup/ui.py`.

Displays in left column immediately after date inputs:
```
Available data: 2010-09-09 → 2026-06-05 / 3,959 trading days
```

If requested start is earlier than actual first date, also shows:
```
Requested start: 2000-01-01 / Data starts: 2010-09-09
```
(in amber color to draw attention without alarming)

---

## Task 6 — validate_history_range.py Output

```
validate_history_range.py
Requested start: 2000-01-01  |  Requested end: 2026-06-07

Ticker: VOO
  actual_first    : 2010-09-09
  actual_last     : 2026-06-05
  row_count       : 3,959
  OK: data starts on or before 2011-01-01

Ticker: SPY
  actual_first    : 2000-01-03
  actual_last     : 2026-06-05
  row_count       : 6,646
  OK: data starts on or before 2001-01-01

Ticker: QQQ
  actual_first    : 2000-01-03
  actual_last     : 2026-06-05
  row_count       : 6,646
  OK: data starts on or before 2001-01-01

Ticker: 379780.KS   (no warn threshold — Korean ETF launched 2021)
  actual_first    : 2021-04-09 / row_count: 1,239

Ticker: 379800.KS
  actual_first    : 2021-04-09 / row_count: 1,239

Result: ALL OK
```

---

## Success Criteria

| # | Criterion | Status |
|---|---|---|
| 1 | Advanced settings expander removed | ✅ Expander deleted from render_controls |
| 2 | Start date and End date always visible | ✅ Direct in left column |
| 3 | User can select/input 2000-01-01 | ✅ Text input, no min-date restriction |
| 4 | App uses selected start_date for yfinance | ✅ data_loader.py always did this |
| 5 | App displays actual data range | ✅ render_data_range_info() in left column |
| 6 | No hardcoded 2010/2020 truncation | ✅ None found — audit confirms |
| 7 | validate_against_golden.py passes | ✅ 122/122 |
| 8 | validate_history_range.py runs and reports | ✅ ALL OK |
| 9 | golden_engine.py unchanged | ✅ 0 diff lines |
