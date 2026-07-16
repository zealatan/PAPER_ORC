# Currency Formatting Report
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
| `global_cup/formatting.py` | **NEW** — central display formatter module |
| `global_cup/ui.py` | Imported formatters; updated all display sites |
| `app.py` | Pass `config=config` to `render_recent_data` calls |
| `test_formatting_display.py` | **NEW** — 24-check test suite |

## Files NOT Modified

- `global_cup/golden_engine.py` — **0 diff lines**
- `global_cup/analysis.py` — untouched (internal `fmt_money`/`fmt_pct` kept)
- `global_cup/charts.py` — untouched
- `global_cup/market_config.py` — untouched
- `validate_against_golden.py` — untouched

---

## Formatter Functions (global_cup/formatting.py)

### `get_currency_symbol(currency_code) -> str`
Returns the short display symbol for a currency:
```
KRW → 원    JPY → 엔    USD → $    EUR → €
GBP → £     HKD → HK$  CHF → CHF  CAD → C$   AUD → A$
```

### `format_year(value) -> str`
Converts any year value to a clean integer string.
| Input | Output |
|---|---|
| `2020.0` | `"2020"` |
| `"2,020.0000"` | `"2020"` |
| `2026` | `"2026"` |

### `format_amount(value, currency_code, decimals=None) -> str`
Currency-aware monetary formatting:
| Input | Output |
|---|---|
| `25230, "KRW"` | `"25,230 원"` |
| `25230.55, "KRW"` | `"25,231 원"` |
| `25230, "JPY"` | `"25,230 엔"` |
| `25230.55, "USD"` | `"$25,230.55"` |
| `25230.5, "EUR"` | `"€25,230.50"` |
| `1000.0, "HKD"` | `"HK$1,000.00"` |
| `1000.0, "CHF"` | `"1,000.00 CHF"` |

KRW and JPY: zero decimal places (integer rounding). All others: 2 decimal places.

### `format_percent(value, decimals=2) -> str`
```
-47.7 → "-47.70%"
 0.2  →  "0.20%"
```

### `format_number(value, decimals=0) -> str`
Plain comma-formatted number (no currency unit).

---

## Currency Mappings

From `global_cup/config.py` `MARKET_RULES`:

| Market | Currency Code | Symbol | Decimals |
|---|---|---|---|
| Korea | KRW | 원 | 0 |
| United States | USD | $ | 2 |
| Japan | JPY | 엔 | 0 |
| European Union | EUR | € | 2 |
| Global | USD | $ | 2 |

---

## Before / After Examples

### Annual Dividend Table

| Before | After (KRW) | After (USD) |
|---|---|---|
| `2,020.0000` | `2020` | `2020` |
| `10.0000` | `10 원` | `$0.58` |

### ZigZag Events Table

| Before | After (KRW) | After (USD) |
|---|---|---|
| `25,230.00` (Price) | `25,230 원` | `$25,230.00` |
| `29,850.00` (Ref High) | `29,850 원` | `$29,850.00` |

### 52W Price Summary Metrics

| Before | After (KRW) | After (USD) |
|---|---|---|
| `25,230.00` | `25,230 원` | `$25,230.00` |

### Reinvest Summary Cards

| Before | After (KRW) | After (USD) |
|---|---|---|
| `10,000,000 KRW` | `10,000,000 원` | `$10,000.00` |
| `26,121,088 KRW` | `26,121,088 원` | `$26,121.09` |

### Reinvest Caption

Before:
```
통화: KRW / 세율: 15.4% / 최근 연배당: 60.0000 / 현재 순배당률: 0.20%
```
After:
```
통화: KRW (원) · 세율: 15.4% · 최근 연배당: 60 원 · 현재 순배당률: 0.20%
```

### Price Tab Metrics

| Before | After (KRW) |
|---|---|
| `25,230` (fmt_money) | `25,230 원` |
| `-3.58%` | `-3.58%` ✓ |

---

## Tabs Updated

| Tab | Formatting Applied |
|---|---|
| Global Cup Score | `render_recent_data(config=config)` — OHLCV + dividend with currency |
| 가격 / 전고점 / 트리거 | Price metric cards + ZigZag events table + dividend table |
| 배당 | `render_recent_data(config=config)` |
| 배당 재투자 | Reinvest summary cards + caption; annual_df Year + money cols; event_df money cols |
| Market Snapshot (all) | `_dividend_table_html` + `_render_dividend_col` + `_recent_data_html` |

---

## Key Design Decisions

1. `format_amount` uses `round()` for zero-decimal currencies (KRW/JPY) to avoid floor truncation.
2. Share counts (`Shares Bought`, `Total Shares`, `Final Shares`) retain `:,.4f` formatting — they are not monetary amounts.
3. `render_recent_data` now accepts `config: Optional[MarketConfig]` to derive currency_code internally. All callers in `app.py` pass `config=config`.
4. `currency_code` defaults to `"USD"` everywhere when config is unavailable (ranking table, edge cases).
5. Internal calculation values (`fmt_money`, `fmt_pct` in `analysis.py`) are untouched — only display strings changed.

---

## Success Criteria

| # | Criterion | Status |
|---|---|---|
| 1 | Year never shows as `2,020.0000` | ✅ `format_year` applied to all Year cells |
| 2 | KRW amounts show no decimals | ✅ `format_amount(..., "KRW")` → integer |
| 3 | JPY amounts show no decimals | ✅ `format_amount(..., "JPY")` → integer |
| 4 | USD/EUR/GBP show correct symbols | ✅ `$` / `€` / `£` prefixed |
| 5 | Currency units in tables and metric cards | ✅ Applied across all tables and cards |
| 6 | Formatting applies across all tabs | ✅ All 4 tabs + Market Snapshot |
| 7 | `golden_engine.py` unchanged | ✅ 0 diff lines |
| 8 | `validate_against_golden.py` passes | ✅ 122/122 |
| 9 | `test_formatting_display.py` passes | ✅ 24/24 |
