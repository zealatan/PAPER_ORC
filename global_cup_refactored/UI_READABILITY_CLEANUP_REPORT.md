# UI Readability Cleanup Report
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
| `global_cup/ui.py` | CSS: form labels, tabs, metric cards, reinvest summary, checkboxes/toggles; `_price_metrics_html` trimmed to 2 cards |
| `app.py` | Removed `render_market_ranking` import and ranking expander block |

---

## Task 1 — Brighter Form Labels

Added CSS for number input and slider labels:
```css
div[data-testid="stNumberInput"] label,
div[data-testid="stSlider"] label {
    color: #e8e3cf !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    opacity: 1.0 !important;
}
```
Applies to all markets (KR/US/EU/JP/Global) — label text matches the currency suffix e.g. `초기 투자금 (KRW)`, `초기 투자금 (USD)`.

---

## Task 2 — Enlarged Dividend Reinvestment Summary

| Property | Before | After |
|---|---|---|
| `.reinvest-metric-label` font-size | 0.58rem | 0.72rem |
| `.reinvest-metric-label` color | rgba(255,245,220,.42) | rgba(255,245,220,.52) |
| `.reinvest-metric-value` font-size | 0.78rem | **1.5rem** |
| `.reinvest-metric-value` font-weight | 800 | 700 |
| `.reinvest-metric-value` color | #d9caa8 | #e8e0cc |
| `.reinvest-metric` padding | 0.38rem 0.58rem | 0.7rem 0.85rem |
| `.reinvest-metric` border-radius | 9px | 11px |
| `.reinvest-metric-grid` gap | 5px | 8px |
| `.reinvest-summary-title` font-size | 0.68rem | 0.78rem |
| `.reinvest-summary-title` color | rgba(255,245,220,.62) | rgba(255,245,220,.70) |

---

## Task 3 — Enlarged Tab Labels

| Property | Before | After |
|---|---|---|
| `.stTabs [data-baseweb="tab"]` padding | .65rem 1.1rem | .78rem 1.5rem |
| `.stTabs [data-baseweb="tab"]` font-size | (unset — browser default) | **1rem** |
| `.stTabs [data-baseweb="tab"]` font-weight | 950 | 600 |

---

## Task 4 — Enlarged Top Metric Cards

| Property | Before | After |
|---|---|---|
| `.price-metric` padding | 0.48rem 0.72rem | 0.85rem 1.1rem |
| `.price-metric` min-width | 96px | 140px |
| `.price-metric` border-radius | 11px | 14px |
| `.price-metric-label` font-size | 0.62rem | 0.78rem |
| `.price-metric-label` color | rgba(255,245,220,.48) | rgba(255,245,220,.55) |
| `.price-metric-value` font-size | 0.87rem | **1.75rem** |

---

## Task 5 — Secondary Metric Cards Removed

**File:** `global_cup/ui.py` → `_price_metrics_html()`

Removed cards:
- Ref High (price + date sub-value)
- Ref Low (price + date sub-value)
- ZZ Drawdown
- Trigger Price
- Trigger Status

Remaining cards:
```
Current Price  |  Trigger Count
```

Underlying data (`result.zigzag_ref_high_price`, `result.zigzag_trigger_price`, etc.) unchanged — only removed from display.

---

## Task 6 — Brighter Checkbox/Toggle Labels

Added CSS:
```css
div[data-testid="stCheckbox"] label,
div[data-testid="stCheckbox"] span,
div[data-testid="stToggle"] label,
div[data-testid="stToggle"] span {
    color: #f0ead6 !important;
    font-weight: 500 !important;
}
```
Applies to: Show ZigZag H/L markers / Show Trigger Buy markers / Market Snapshot toggle.

---

## Task 7 — Global Cup Market Ranking Removed

**File:** `app.py`

Removed:
```python
from global_cup.ui import render_market_ranking   # import removed

with st.expander("Global Cup Market Ranking", expanded=False):
    render_market_ranking()
```

`render_market_ranking()` function remains in `ui.py` (not deleted), but is no longer called.

---

## Task 8 — Visual Balance

With only Current Price and Trigger Count remaining:
- Each card uses `flex: 1` and fills 50% of the metric row
- Larger padding (0.85rem 1.1rem) and bigger font (1.75rem) make both cards visually strong
- `min-width: 140px` prevents extreme compression on narrow screens

---

## Success Criteria

| # | Criterion | Status |
|---|---|---|
| 1 | 초기 투자금 / 월 추가 투자금 / 배당세율 labels readable | ✅ #e8e3cf, 600 weight |
| 2 | 배당 재투자 요약 values significantly larger | ✅ 0.78rem → 1.5rem |
| 3 | Tab labels larger | ✅ 1rem font-size, .78rem 1.5rem padding |
| 4 | Current Price and Trigger Count larger | ✅ 1.75rem value font |
| 5 | Ref High removed | ✅ |
| 6 | Ref Low removed | ✅ |
| 7 | ZZ Drawdown removed | ✅ |
| 8 | Trigger Price removed | ✅ |
| 9 | Trigger Status removed | ✅ |
| 10 | Show ZigZag / Show Trigger Buy / Market Snapshot labels brighter | ✅ #f0ead6, 500 weight |
| 11 | Global Cup Market Ranking removed | ✅ Import and expander deleted from app.py |
| 12 | No engine changes | ✅ golden_engine.py 0 diff lines |
| 13 | `validate_against_golden.py` passes | ✅ 122/122 |
| 14 | `test_formatting_display.py` passes | ✅ 24/24 |
