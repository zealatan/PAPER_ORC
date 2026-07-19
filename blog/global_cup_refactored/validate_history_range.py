"""Diagnostic script: verify historical data range for key tickers via yfinance."""
from datetime import date, timedelta

import yfinance as yf

REQUESTED_START = date(2000, 1, 1)
REQUESTED_END   = date.today()

TICKERS = [
    ("VOO",       2011, 1,  1),   # VOO IPO was Sep 2010; warn if starts after 2011-01-01
    ("SPY",       2001, 1,  1),   # SPY has data since 1993; warn if starts after 2001-01-01
    ("QQQ",       2001, 1,  1),   # QQQ since 1999; warn if starts after 2001-01-01
    ("379780.KS", None, None, None),
    ("379800.KS", None, None, None),
]

print("=" * 70)
print(f"  validate_history_range.py")
print(f"  Requested start: {REQUESTED_START}  |  Requested end: {REQUESTED_END}")
print("=" * 70)

all_ok = True

for entry in TICKERS:
    ticker_sym, warn_year, warn_month, warn_day = entry
    print(f"\n  Ticker: {ticker_sym}")
    try:
        df = yf.download(
            ticker_sym,
            start=REQUESTED_START,
            end=REQUESTED_END + timedelta(days=1),
            auto_adjust=False,
            progress=False,
            threads=False,
        )
    except Exception as exc:
        print(f"    ERROR downloading: {exc}")
        all_ok = False
        continue

    if df.empty:
        print("    No data returned (ticker may not exist or have no history).")
        continue

    first_date = df.index[0].date()
    last_date  = df.index[-1].date()
    row_count  = len(df)

    print(f"    requested_start : {REQUESTED_START}")
    print(f"    actual_first    : {first_date}")
    print(f"    actual_last     : {last_date}")
    print(f"    row_count       : {row_count:,}")

    if warn_year is not None:
        warn_limit = date(warn_year, warn_month, warn_day)
        if first_date > warn_limit:
            print(f"    WARNING: data starts after {warn_limit} — expected earlier history")
            all_ok = False
        else:
            print(f"    OK: data starts on or before {warn_limit}")

print()
print("=" * 70)
print("  Result:", "ALL OK" if all_ok else "WARNINGS — see above")
print("=" * 70)
