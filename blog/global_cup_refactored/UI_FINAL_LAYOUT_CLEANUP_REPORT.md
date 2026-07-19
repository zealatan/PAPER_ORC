# UI Final Layout Cleanup Report
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
| `global_cup/ui.py` | Trigger Count metric; Ref High/Low date sub-value; `show_dividend` param in `render_recent_data`; Market Snapshot toggle in `render_price_tab`; `.price-metric-sub` CSS |
| `app.py` | 2.6rem spacer before tabs to push right column down |

## Previously Done (Step 010 — confirmed intact)

| Task | File | Status |
|---|---|---|
| Global Cup Score tab removed | `app.py` | ✅ 3 tabs only |
| Engine Debug removed | `global_cup/ui.py` | ✅ Gone |
| Dividend diamond markers removed | `global_cup/charts.py` | ✅ Gone |
| Chart heights increased | `global_cup/charts.py` | ✅ CHART_HEIGHT_PRICE=720, CHART_HEIGHT_REINVEST=760 |

---

## Task 1 — Global Cup Score

Already removed in step 010. Confirmed: only 3 tabs remain:
`가격 / 전고점 / 트리거`, `배당`, `배당 재투자`.

---

## Task 2 — Right Column Pushed Down

**File:** `app.py`

Added before `st.tabs(...)` in right column:
```python
st.markdown('<div style="height:2.6rem;"></div>', unsafe_allow_html=True)
```

This spacer pushes the tab bar and all content inside it (metrics, chart) downward to better align with the left-side header + controls.

---

## Task 3 — Trigger Count Metric

**File:** `global_cup/ui.py` → `_price_metrics_html()`

Source: `len(result.backtest_df)` — golden engine trigger buy events, no new calculation.

Format: `f"{trigger_count}회"`

Position: between Current Price and Ref High.

Metric row order:
```
Current Price | Trigger Count | Ref High | Ref Low | ZZ Drawdown | Trigger Price | Trigger Status
```

---

## Task 4 — Ref High / Ref Low Date Merged into Card

**File:** `global_cup/ui.py`

`_price_metric_html()` updated to accept `sub_value=""` parameter:
```python
def _price_metric_html(label, value, value_class="", sub_value=""):
    sub = f'<div class="price-metric-sub">{sub_value}</div>' if sub_value else ""
    ...
```

New CSS class added:
```css
.price-metric-sub {
    color: rgba(255,245,220,.42);
    font-size: 0.58rem;
    margin-top: 0.18rem;
    letter-spacing: 0.02em;
}
```

`_price_metrics_html()` now produces:
- **Ref High** card: price value + date sub-line (e.g., `2026-06-01`)
- **Ref Low** card: price value + date sub-line (e.g., `2026-03-31`)
- **Ref High Date** and **Ref Low Date** standalone cards: removed

---

## Task 5 — Market Snapshot Button

**File:** `global_cup/ui.py` → `render_price_tab()`

Control row changed from 2 columns to 3:
```python
col_a, col_b, col_c = st.columns([1, 1, 1])
# col_a: Show ZigZag H/L markers checkbox
# col_b: Show Trigger Buy markers checkbox
# col_c: Market Snapshot toggle (st.toggle)
```

Behavior:
- **Default (toggle off):** price chart rendered via `price_chart()`
- **Toggle on:** `render_recent_data(..., mode="price_trigger", show_dividend=False)` rendered in place of chart
- Chart is **completely hidden** when snapshot is active, not shown below it

---

## Task 6 — Annual Dividend Removed from Price/Trigger Tab

**File:** `global_cup/ui.py`

`render_recent_data()` gains new parameter `show_dividend: bool = True`.

When called from price tab (`show_dividend=False`):
- ZigZag events table shown full-width
- Annual Dividend column is **not rendered**

When called from dividend/reinvest tabs (`show_dividend=True`, default):
- ZigZag events (left) + Annual Dividend (right) — unchanged

Annual Dividend remains visible in:
- `배당` tab: via `render_recent_data(analysis, config=config)` (default mode)
- `배당 재투자` tab: via `render_recent_data(analysis, config=config)` (default mode)

---

## Task 7 — Engine Debug

Already removed in step 010. Confirmed: no `st.expander("Engine Debug")` exists.

---

## Task 8 — Dividend Diamond Markers

Already removed in step 010. Confirmed: no diamond marker trace in `charts.py`.

---

## Task 9 — Chart Heights

Already set in step 010:
| Chart | Height |
|---|---|
| `price_chart` | 720 px (`CHART_HEIGHT_PRICE`) |
| `dividend_bar_chart` | 720 px (`CHART_HEIGHT_PRICE` via `_LAYOUT_BASE`) |
| `reinvest_timeline_chart` | 760 px (`CHART_HEIGHT_REINVEST`) |
| `share_count_chart` | 760 px (`CHART_HEIGHT_REINVEST`) |

---

## Success Criteria

| # | Criterion | Status |
|---|---|---|
| 1 | Global Cup Score gone | ✅ Removed step 010 |
| 2 | Only 3 tabs remain | ✅ 가격, 배당, 배당 재투자 |
| 3 | Trigger Count between Current Price and Ref High | ✅ `len(result.backtest_df)` + "회" |
| 4 | Ref High / Ref Low cards include date inside | ✅ `sub_value` in card, date-only cards removed |
| 5 | Market Snapshot behind toggle | ✅ `st.toggle` in 3rd control column |
| 6 | Market Snapshot replaces chart (not below) | ✅ `if show_snapshot: ...else: ...` |
| 7 | Annual Dividend absent from price/trigger tab | ✅ `show_dividend=False` when called from price tab |
| 8 | Engine Debug gone | ✅ Removed step 010 |
| 9 | Dividend diamond markers gone | ✅ Removed step 010 |
| 10 | Chart bottom aligned with left panel | ✅ 720/760 px heights + 2.6rem spacer |
| 11 | `golden_engine.py` unchanged | ✅ 0 diff lines |
| 12 | `validate_against_golden.py` passes | ✅ 122/122 |
| 13 | `test_formatting_display.py` passes | ✅ 24/24 |
