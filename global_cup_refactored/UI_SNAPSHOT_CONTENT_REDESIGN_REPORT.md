# UI Snapshot Content Redesign Report
**Date:** 2026-06-06  **Status: ALL SUCCESS**

---

## Validation

| Check | Result |
|---|---|
| `python3 -m py_compile app.py` | OK |
| `python3 -m py_compile global_cup/*.py` | ALL OK |
| `python3 validate_against_golden.py` | **122/122 PASS** |
| `golden_engine.py` modified | **NO — 0 diff lines** |

---

## Task 1 — Table Color Redesign

**Classes updated in `global_cup/ui.py` (`_CSS` block):**

| Element | Before | After |
|---|---|---|
| `thead th` background | `linear-gradient(#263522, #3f5f38)` gradient | `#1f2b18` solid — editorial dark |
| `tbody td` text | `#1f2b18` | `#263522` — warmer body text |
| `tbody tr:hover` background | `rgba(142,185,87,.18)` | `rgba(142,185,87,.08)` — very subtle |
| Row tinting | `.row-up`/`.row-down` full-row backgrounds | Removed — **no full-row color** |
| Alternating rows | n/a | `.row-alt` / `.row-neutral` — neutral warm tones |
| `close-up` text | `#4a7c1e` | `#6f8f3f` accent green |
| `close-down` text | `#8b1c1c` | `#a14d36` accent red |
| `div-positive` | `#3a6b1a` | `#6f8f3f` |
| `div-negative` | `#8b1c1c` | `#a14d36` |

**New CSS classes added:**

_Type badges (ZigZag events table):_
- `.type-badge` — pill shape, inline-block, font-weight 800
- `.badge-high` — green pill (`#6f8f3f`)
- `.badge-low` — red pill (`#a14d36`)
- `.badge-buy` — gold pill (`#7a5e20`)
- `.badge-current` — neutral forest pill

_Dividend year badges:_
- `.div-badge` — smaller pill, vertical-align middle
- `.badge-div-latest` — green
- `.badge-div-highest` — gold
- `.badge-div-lowest` — red

---

## Task 2 — New ZigZag Events Table

**New function: `_zigzag_events_html(result: AnalysisResult, trigger_pct: float) -> str`**

Builds HTML table from golden engine outputs already stored in `AnalysisResult`:

| Column | Source |
|---|---|
| Type | Badge: High / Low / Trigger Buy / Current |
| Date | From `result.zigzag_points` / `result.backtest_df` / `result.current_date` |
| Price | From same sources |
| Ref High | `result.zigzag_ref_high_price` (Current row only) |
| Ref Low | `result.zigzag_ref_low_price` (Current row only) |
| Drawdown | `result.zigzag_drawdown_pct` (Current) / trigger label (Buy rows) |
| Note | 자동 매수 / 현재 상태 / blank |

Rows sorted chronologically. Uses golden engine field `result.zigzag_points = (highs, lows)` tuple — no re-computation, no `close.max()`.

---

## Task 3 — OHLCV Table Moved to Collapsed Expander

In both `mode="price_trigger"` and `mode="default"`, the OHLCV table is now inside:
```python
with st.expander("Raw Recent OHLCV Data", expanded=False):
    st.markdown(_recent_data_html(result.price_df), ...)
```
Default: **collapsed**. Users can expand on demand.

---

## Task 4 — Annual Dividend Table Badges

**Updated `_dividend_table_html()`:**
- Identifies `latest_year`, `highest_year`, `lowest_year` from the "Dividend per Share" column
- Adds inline badge spans to the Year cell:
  - `Latest` — green badge on most recent year
  - `High` — gold badge on year with highest dividend
  - `Low` — red badge on year with lowest dividend
- No over-coloring of full rows — only badge accents

---

## Task 5 — Snapshot Layout

**`render_recent_data(result, inp=None, mode="default")` — refactored with mode param**

`mode="price_trigger"` (called from inside `render_price_tab`):
- `st.columns([2, 1])` — left wide: ZigZag events table; right: Annual Dividend + summary
- Below columns: collapsed OHLCV expander

`mode="default"` (called from score_tab, dividend_tab, reinvest_tab in app.py):
- `st.columns([2, 1])` — left: 52W price metrics + collapsed OHLCV; right: Annual Dividend + summary

**New shared helper: `_render_dividend_col(result)`** — renders dividend summary metrics + badged table, reused in both modes.

**`render_price_tab()` updated:** Adds `render_recent_data(result, inp, mode="price_trigger")` at the bottom of the tab.

---

## Where Raw OHLCV Moved

| Location | Mode | State |
|---|---|---|
| `price_trigger` snapshot (inside price tab) | `st.expander("Raw Recent OHLCV Data")` | Collapsed by default |
| `default` snapshot (inside other tabs) | `st.expander("Raw Recent OHLCV Data")` | Collapsed by default |

---

## `app.py` Changes

| Before | After |
|---|---|
| `render_recent_data(analysis)` below ALL tabs | Removed from below-tabs position |
| `with score_tab:` — score only | Adds `render_recent_data(analysis)` at bottom |
| `with dividend_tab:` — dividend only | Adds `render_recent_data(analysis)` at bottom |
| `with reinvest_tab:` — reinvest only | Adds `render_recent_data(analysis)` at bottom |
| `with price_tab:` — price_tab only | `render_price_tab` internally calls price_trigger mode |

Market Snapshot now lives INSIDE each tab (not below the tab grid), eliminating layout duplication.

---

## Files Modified

| File | Changes |
|---|---|
| `global_cup/ui.py` | CSS redesigned (solid header, no full-row colors, badges); `_recent_data_html` uses alternating rows; `_dividend_table_html` adds year badges; new `_zigzag_events_html`, `_render_dividend_col`; `render_recent_data` refactored with `mode` param; `render_price_tab` calls price_trigger mode |
| `app.py` | Removed below-tabs `render_recent_data`; added inside score/dividend/reinvest tabs |

## Files NOT Modified

- `global_cup/golden_engine.py` — **untouched, 0 diff**
- `global_cup/analysis.py` — untouched
- `global_cup/charts.py` — untouched
- `global_cup/market_config.py` — untouched
- `validate_against_golden.py` — untouched

---

## Success Criteria Checklist

| # | Criterion | Status |
|---|---|---|
| 1 | Table color premium (solid dark header, no harsh row tints, badge accents) | ✅ |
| 2 | Price tab shows High/Low/Trigger Buy/Current rows from golden engine | ✅ |
| 3 | OHLCV moved to collapsed `st.expander("Raw Recent OHLCV Data")` | ✅ |
| 4 | Annual Dividend table still visible with year badges | ✅ |
| 5 | No engine calculation changes | ✅ |
| 6 | `validate_against_golden.py` 122/122 PASS | ✅ |
