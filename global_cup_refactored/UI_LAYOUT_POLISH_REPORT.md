# UI Layout Polish Report
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

## Task 1 — Table Color Polish

**CSS classes updated in `global_cup/ui.py` (`_CSS` block):**

| Class | Before | After |
|---|---|---|
| `.premium-table-wrap` bg | `#f8fbfa` | `rgba(255,249,237,.96)` — warm cream |
| `.premium-table-wrap` border | `rgba(0,95,115,.14)` cyan | `rgba(31,43,24,.10)` forest |
| scrollbar thumb | `#94d2bd` teal | `#8eb957` sage green |
| `thead th` gradient | `#005f73 → #0a9396` (bright teal) | `#263522 → #3f5f38` (dark forest) |
| `thead th` text | `#ffffff` | `#fff5dc` (warm cream) |
| `thead` border | `rgba(0,95,115,.35)` | `rgba(31,43,24,.25)` |
| `tbody td` text | `#001219` | `#1f2b18` |
| `tbody td:first-child` text | `#005f73` | `#3f5f38` |
| `tbody tr:hover` bg | `rgba(148,210,189,.28)` cyan | `rgba(142,185,87,.18)` sage |
| `.row-up td` bg | `rgba(34,197,94,.065)` bright green | `rgba(142,185,87,.10)` muted positive |
| `.row-down td` bg | `rgba(239,68,68,.065)` bright red | `rgba(174,32,18,.07)` muted negative |
| `.row-neutral td` bg | `rgba(248,251,250,1)` cold white | `rgba(255,249,237,.96)` warm cream |
| `.div-row-even td` bg | `rgba(0,95,115,.048)` cyan tint | `rgba(244,238,220,.55)` warm alternate |
| `.div-row-odd td` bg | `rgba(248,251,250,1)` | `rgba(255,249,237,.96)` |
| `td.vol-cell` color | `#4a6572` | `#6c745e` sage muted |
| `.div-positive` | `#15803d` bright | `#3a6b1a` muted forest green |
| `.div-negative` | `#dc2626` bright red | `#8b1c1c` muted forest red |

**New CSS classes added:**
- `td.close-up` — muted green text `#4a7c1e` on Close cell (price went up)
- `td.close-down` — muted red text `#8b1c1c` on Close cell (price went down)

**`_recent_data_html()` updated:** Close cell now gets `close-up`/`close-down` class for text-level coloring instead of relying only on row background.

---

## Task 2 — Price/High/Low/Trigger Metrics

**New functions added to `global_cup/ui.py`:**
- `_price_metric_html(label, value, value_class)` — renders one dark-glass metric card
- `_price_metrics_html(result: AnalysisResult) -> str` — builds 8-metric row HTML

**`render_price_tab()` updated:** Calls `st.markdown(_price_metrics_html(result))` at the top, before the checkboxes.

**8 metrics displayed (golden engine fields):**

| Metric | Source field |
|---|---|
| Current Price | `result.current_price` |
| Ref High | `result.zigzag_ref_high_price` |
| Ref High Date | `result.zigzag_ref_high_date` |
| Ref Low | `result.zigzag_ref_low_price` |
| Ref Low Date | `result.zigzag_ref_low_date` |
| ZZ Drawdown | `result.zigzag_drawdown_pct` |
| Trigger Price | `result.zigzag_trigger_price` |
| Trigger Status | `result.zigzag_trigger_hit` → "▼ HIT" (red) / "— OK" (green) |

Reference high = max price after last ZigZag low (golden engine behavior, not simple close.max()).

**CSS added:** `.price-metric-row`, `.price-metric`, `.price-metric-label`, `.price-metric-value`, `.price-metric-trigger-hit`, `.price-metric-trigger-ok` — dark-glass style matching existing dashboard theme.

---

## Task 3 — Dividend Reinvestment Summary → Left Column

**Architecture change:**

Before:
- Left col: market header + controls
- Right tab (배당 재투자): inputs → compute → metrics → chart → tables

After:
- Left col: market header + controls + reinvest inputs + **summary metric grid**
- Right tab (배당 재투자): chart + tables only

**New functions added to `global_cup/ui.py`:**
- `render_reinvest_controls_left(config) → (params_dict, summary_container)` — renders 3 number_inputs (초기 투자금, 월 추가 투자금, 배당세율) in left column; returns params + `st.container()` placeholder
- `render_reinvest_summary_left(reinvest, currency, tax_rate_pct)` — renders 8-metric dark-glass grid in the left placeholder

**CSS added:** `.reinvest-summary-section`, `.reinvest-summary-title`, `.reinvest-metric-grid`, `.reinvest-metric`, `.reinvest-metric-label`, `.reinvest-metric-value`, `.reinvest-caption`

**`render_dividend_reinvest_tab()` updated:**
- New signature: `(inp, config, result, reinvest=None)`
- Removed all input widgets (moved to left)
- Removed all metric display (moved to left)
- Now only renders: timeline chart, share count chart, annual dividend table, event log table

**`app.py` updated:**
- Added import `run_dividend_reinvest_backtest` from `global_cup.dividend_reinvest`
- Added imports `render_reinvest_controls_left`, `render_reinvest_summary_left`
- `render_reinvest_controls_left(config)` called inside `with left:` block
- `reinvest_result = run_dividend_reinvest_backtest(...)` computed once after analysis
- `render_reinvest_summary_left(...)` called via `with reinvest_summary_container:`
- `render_dividend_reinvest_tab(...)` now receives `reinvest=reinvest_result`

---

## Task 4 — Responsive Behavior

CSS `@media (max-width: 768px)` extended:
- `.price-metric-row { gap: 5px; }`, `.price-metric { min-width: 78px; }`
- `.reinvest-metric-grid { grid-template-columns: 1fr; }` — stacks to single column on mobile

---

## Files Modified

| File | What changed |
|---|---|
| `global_cup/ui.py` | CSS updated (table palette + new classes); `_recent_data_html` close-cell coloring; new `_price_metric_html`, `_price_metrics_html`; `render_price_tab` + metrics; new `render_reinvest_controls_left`, `render_reinvest_summary_left`; `render_dividend_reinvest_tab` stripped to chart+tables only |
| `app.py` | Added imports; reinvest controls in left col; reinvest computation moved to app; summary populated via container; chart tab receives pre-computed reinvest |

## Files NOT Modified (by design)

- `global_cup/golden_engine.py` — **untouched**, 0 diff lines
- `global_cup/analysis.py` — untouched
- `global_cup/charts.py` — untouched
- `global_cup/market_config.py` — untouched
- `global_cup/dividend_reinvest.py` — untouched
- All validation scripts — untouched

---

## Success Criteria Checklist

| # | Criterion | Status |
|---|---|---|
| 1 | Table colors premium (dark forest header, warm cream bg, subtle tints) | ✅ |
| 2 | Price tab shows Ref High, Ref Low, Drawdown, Trigger from golden engine | ✅ |
| 3 | Reinvest summary moved to left column under controls | ✅ |
| 4 | Right tab focuses on chart only | ✅ |
| 5 | No engine calculation changes | ✅ |
| 6 | `validate_against_golden.py` 122/122 PASS | ✅ |
