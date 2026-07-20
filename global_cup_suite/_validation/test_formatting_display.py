"""Test suite for global_cup.formatting display helpers."""
import sys
import traceback

from global_cup.formatting import format_year, format_amount, format_percent, get_currency_symbol

PASS = 0
FAIL = 0


def check(desc: str, got, expected):
    global PASS, FAIL
    if got == expected:
        print(f"  ✅ PASS  {desc}  [{got!r}]")
        PASS += 1
    else:
        print(f"  ❌ FAIL  {desc}")
        print(f"         expected: {expected!r}")
        print(f"         got:      {got!r}")
        FAIL += 1


print("=" * 60)
print("  format_year")
print("=" * 60)
check("format_year(2020.0)",          format_year(2020.0),          "2020")
check("format_year(2026)",            format_year(2026),            "2026")
check("format_year('2,020.0000')",    format_year("2,020.0000"),    "2020")
check("format_year(2020)",            format_year(2020),            "2020")
check("format_year('2024')",          format_year("2024"),          "2024")

print()
print("=" * 60)
print("  format_amount")
print("=" * 60)
check("KRW integer",                  format_amount(25230,    "KRW"), "25,230 원")
check("KRW rounding",                 format_amount(25230.55, "KRW"), "25,231 원")
check("KRW zero decimals explicitly", format_amount(25230,    "KRW", decimals=0), "25,230 원")
check("JPY integer",                  format_amount(25230,    "JPY"), "25,230 엔")
check("USD two decimals",             format_amount(25230.55, "USD"), "$25,230.55")
check("EUR two decimals",             format_amount(25230.5,  "EUR"), "€25,230.50")
check("GBP",                          format_amount(1000.0,   "GBP"), "£1,000.00")
check("HKD",                          format_amount(1000.0,   "HKD"), "HK$1,000.00")
check("CHF",                          format_amount(1000.0,   "CHF"), "1,000.00 CHF")
check("CAD",                          format_amount(1000.0,   "CAD"), "C$1,000.00")
check("AUD",                          format_amount(1000.0,   "AUD"), "A$1,000.00")

print()
print("=" * 60)
print("  format_percent")
print("=" * 60)
check("format_percent(-47.7)",        format_percent(-47.7),        "-47.70%")
check("format_percent(0.2)",          format_percent(0.2),          "0.20%")
check("format_percent(100.0)",        format_percent(100.0),        "100.00%")

print()
print("=" * 60)
print("  get_currency_symbol")
print("=" * 60)
check("KRW symbol", get_currency_symbol("KRW"), "원")
check("USD symbol", get_currency_symbol("USD"), "$")
check("JPY symbol", get_currency_symbol("JPY"), "엔")
check("EUR symbol", get_currency_symbol("EUR"), "€")
check("CHF symbol", get_currency_symbol("CHF"), "CHF")

print()
print("=" * 60)
print(f"  TOTAL: {PASS + FAIL} checks  |  PASS: {PASS}  |  FAIL: {FAIL}")
print("=" * 60)

sys.exit(0 if FAIL == 0 else 1)
