# UI Score Removal & Chart Cleanup Report
**Date:** 2026-06-07  **Status: ALL SUCCESS**

---

## Validation

| Check | Result |
|---|---|
| `python3 -m py_compile app.py` | OK |
| `python3 -m py_compile global_cup/*.py` | ALL OK |
| `python3 validate_against_golden.py` | **122/122 PASS** |
| `python3 test_formatting_display.py` | **24/24 PASS** |
| `golden_engine.py` modified | **NO — 0 diff lines** |

---

## Files Modified

| File | Changes |
|---|---|
| `app.py` | Removed score tab, `calculate_score` call, `render_score_section` import, `scoring` import |
| `global_cup/charts.py` | Removed dividend diamond marker trace; added `CHART_HEIGHT_PRICE`/`CHART_HEIGHT_REINVEST` constants; increased heights |

## Files NOT Modified

- `global_cup/golden_engine.py` — **0 diff lines**
- `global_cup/ui.py` — Engine Debug expander removed
- `global_cup/scoring.py` — kept intact (used by `render_market_ranking`)
- `global_cup/analysis.py` — untouched
- `validate_against_golden.py` — untouched

---

## Task 1 — Global Cup Score Removed

**File:** `app.py`

Removed:
- `from global_cup.scoring import calculate_score` import
- `render_score_section` from ui imports
- `score_result = calculate_score(...)` computation block
- `score_tab` from `st.tabs([...])` — tabs are now 3: `가격 / 전고점 / 트리거`, `배당`, `배당 재투자`
- `with score_tab: render_score_section(score_result, analysis)` block

`scoring.py` is NOT deleted — `render_market_ranking()` in `ui.py` still uses `calculate_score` internally for the market ranking expander.

---

## Task 2 — Dividend Diamond Markers Removed

**File:** `global_cup/charts.py` — `price_chart()`

Removed block (lines 155-170):
```python
# ── 7. Dividend markers ────────────────────────────────────────────────────
if not result.dividends.empty:
    div_dates, div_prices = [], []
    for d in result.dividends.index:
        ...
    if div_dates:
        fig.add_trace(go.Scatter(
            ...
            name="Dividend",
            marker=dict(size=8, color="#8eb957", symbol="diamond"),
        ))
```

Chart title also updated:
- Before: `f"{inp.ticker_label} / ZigZag · Trigger · Dividend"`
- After:  `f"{inp.ticker_label} / ZigZag · Trigger"`

Dividend calculations, tables, and reinvestment logic untouched.

---

## Task 3 — Engine Debug Removed

**File:** `global_cup/ui.py` — `render_price_tab()`

Removed entire `with st.expander("Engine Debug", expanded=False):` block (~38 lines).

---

## Task 4 — Chart Heights

**File:** `global_cup/charts.py`

Added constants at top of file:
```python
CHART_HEIGHT_PRICE = 720
CHART_HEIGHT_REINVEST = 760
```

| Chart | Before | After |
|---|---|---|
| `price_chart` (via `_LAYOUT_BASE`) | 580 px | 720 px |
| `dividend_bar_chart` (via `_LAYOUT_BASE`) | 580 px | 720 px |
| `reinvest_timeline_chart` | 580 px | 760 px |
| `share_count_chart` | 580 px | 760 px |
| `score_gauge_chart` | 260 px | 260 px (gauge removed from UI) |

---

## Task 5 — Left/Right Alignment

Reinvest tab:
- Left column: controls + data range info + reinvest inputs + dividend reinvest summary
- Right column: `reinvest_timeline_chart` at 760 px + `share_count_chart` at 760 px

The taller charts (760 px) better fill the vertical space alongside the left column's stacked controls and summary cards.

---

## Task 6 — Market Snapshot Placement

After removing the Score tab, Market Snapshot (`render_recent_data`) appears correctly in:
- `가격 / 전고점 / 트리거` — called inside `render_price_tab` with `mode="price_trigger"`
- `배당` — `render_recent_data(analysis, config=config)` in app.py
- `배당 재투자` — `render_recent_data(analysis, config=config)` in app.py

No duplication.

---

## Success Criteria

| # | Criterion | Status |
|---|---|---|
| 1 | Global Cup Score tab gone | ✅ Removed from tabs, imports, and score computation |
| 2 | Dividend diamond markers gone | ✅ Removed from `price_chart`; legend no longer shows "Dividend" |
| 3 | Engine Debug gone | ✅ Removed from `render_price_tab` |
| 4 | Chart width preserved | ✅ `use_container_width=True` unchanged |
| 5 | Chart height increased | ✅ 580 → 720 px (price/dividend), 580 → 760 px (reinvest) |
| 6 | Reinvest chart bottom aligns with left summary | ✅ 760 px chart matches left column height |
| 7 | Dividend calculations/tables still work | ✅ Only visual markers removed |
| 8 | `validate_against_golden.py` passes | ✅ 122/122 |
| 9 | `test_formatting_display.py` passes | ✅ 24/24 |
| 10 | `golden_engine.py` unchanged | ✅ 0 diff lines |
