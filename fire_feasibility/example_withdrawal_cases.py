"""
Withdrawal mechanics by dividend frequency — worked examples.

Model (USD basis): retire with a corpus, buy the stock, spend a fixed MONTHLY
living expense. Each month:
  - dividends received sit in a cash account (net of 15% withholding),
  - the month's expense is paid FROM that cash first,
  - only the shortfall is covered by SELLING shares.

Because dividend cash carries over, a single quarterly/semiannual/annual
payment funds several months of expenses before any selling is needed. This
script prints a month-by-month table for one sample year for each frequency
so the funding pattern (dividend cash vs. share sale) is visible.

Run:
  PYB=/home/zealatan/.pyenv/versions/3.11.8/bin/python3.11
  SP=/home/zealatan/YOUTUBE/blog/global_cup_refactored/.venv/lib/python3.11/site-packages
  PYTHONPATH=$SP:. $PYB example_withdrawal_cases.py
"""
from __future__ import annotations

from datetime import date

import pandas as pd
import yfinance as yf

from global_cup.dividend_schedule import classify
from global_cup.fire_engine import run_fire_backtest

# one representative payer per cadence
CASES = [
    ("월배당  (monthly)",    "O"),     # Realty Income
    ("분기배당 (quarterly)", "KO"),    # Coca-Cola
    ("반기배당 (semiannual)", "LYG"),   # Lloyds
    ("연배당  (annual)",     "NSRGY"), # Nestle
]

CORPUS = 500_000.0          # 은퇴 자금 $500k
MONTHLY_EXPENSE = 2_000.0   # 월 생활비 $2,000  (= $24k/yr)
START = date(2015, 1, 1)
SAMPLE_YEAR = 2023          # year to print month-by-month


def _load(ticker: str):
    df = yf.download(ticker, start="2014-06-01", auto_adjust=False,
                     progress=False, threads=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    close = pd.to_numeric(df["Close"], errors="coerce").dropna()
    close.index = pd.to_datetime(close.index).tz_localize(None)
    div = yf.Ticker(ticker).dividends
    div.index = pd.to_datetime(div.index).tz_localize(None)
    return close, div.astype(float)


def _monthly_table(r, close, div, year: int) -> pd.DataFrame:
    """Build a per-month view for `year` from engine output."""
    wd = r.withdrawal_df.copy()
    wd["ym"] = wd["Date"].dt.to_period("M")
    # dividends received per calendar month (net) from timeline
    tl = r.timeline_df.copy()
    tl["ym"] = tl["Date"].dt.to_period("M")
    div_by_month = tl.groupby("ym")["Dividend"].sum()

    rows = []
    for _, w in wd[wd["Date"].dt.year == year].iterrows():
        ym = w["ym"]
        rows.append({
            "월": str(ym),
            "배당수령$": round(float(div_by_month.get(ym, 0.0)), 2),
            "생활비$": round(float(w["Requested"]), 2),
            "배당현금충당$": round(float(w["From Cash"]), 2),
            "매도금액$": round(float(w["Sold Value"]), 2),
            "충당방식": w["Funded By"],
            "잔여주식": round(float(w["Shares After"]), 2),
        })
    return pd.DataFrame(rows)


def main():
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 20)

    for label, ticker in CASES:
        close, div = _load(ticker)
        sch = classify(div)
        r = run_fire_backtest(
            close, div, CORPUS,
            annual_withdrawal=MONTHLY_EXPENSE * 12,
            strategy="fixed_nominal", frequency="monthly",
            tax_rate_pct=15.0, reinvest_dividends=False,
            start_date=START,
        )
        s = r.summary
        print("\n" + "=" * 78)
        print(f"{label}  [{ticker}]  detected={sch.frequency} "
              f"({sch.payments_per_year}/yr, months={sch.typical_months})")
        print(f"코퍼스 ${CORPUS:,.0f} · 월 생활비 ${MONTHLY_EXPENSE:,.0f} · "
              f"{START}~{s['End Price'] and r.timeline_df['Date'].iloc[-1].date()}")
        print(f"  생존={s['Survived']} · 최종자산=${s['Final Value']:,.0f} · "
              f"총인출=${s['Total Withdrawn']:,.0f} · "
              f"총배당(net)=${s['Total Net Dividend']:,.0f} · "
              f"총매도=${s['Total Shares Sold Value']:,.0f}")
        print(f"\n  ── {SAMPLE_YEAR}년 월별 대처 ──")
        tbl = _monthly_table(r, close, div, SAMPLE_YEAR)
        print(tbl.to_string(index=False))


if __name__ == "__main__":
    main()
