"""
Monthly-dividend payer — the two living-expense cases.

Focus: a MONTHLY dividend stock (O, Realty Income). Two situations:

  CASE 1  월 생활비 > 월 배당   → dividend partially covers; SELL shares for the
                                   monthly shortfall. Portfolio slowly draws down.
  CASE 2  월 생활비 < 월 배당   → dividend more than covers; a SURPLUS remains.
                                   What to do with the surplus is a choice:
                                     (a) keep as idle cash   (reinvest_surplus=False)
                                     (b) reinvest into shares (reinvest_surplus=True)

This prints a month-by-month table for a sample year for each case so the
mechanic (sell vs. surplus, idle vs. reinvest) is explicit.

Run:
  PYB=/home/zealatan/.pyenv/versions/3.11.8/bin/python3.11
  SP=/home/zealatan/YOUTUBE/blog/global_cup_refactored/.venv/lib/python3.11/site-packages
  PYTHONPATH=$SP:. $PYB example_monthly_cases.py
"""
from __future__ import annotations

from datetime import date

import pandas as pd
import yfinance as yf

from global_cup.fire_engine import run_fire_backtest

TICKER = "O"
CORPUS = 500_000.0
START = date(2015, 1, 1)
SAMPLE_YEAR = 2023


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


def _monthly_table(r, year: int) -> pd.DataFrame:
    tl = r.timeline_df.copy()
    tl["ym"] = tl["Date"].dt.to_period("M")
    div_by_month = tl.groupby("ym")["Dividend"].sum()
    wd = r.withdrawal_df.copy()
    wd["ym"] = wd["Date"].dt.to_period("M")
    rows = []
    for _, w in wd[wd["Date"].dt.year == year].iterrows():
        ym = w["ym"]
        net_div = float(div_by_month.get(ym, 0.0))
        expense = float(w["Requested"])
        from_cash = float(w["From Cash"])
        sold = float(w["Sold Value"])
        surplus = net_div - expense  # +: leftover, -: needed selling
        rows.append({
            "월": str(ym),
            "월배당(net)$": round(net_div, 2),
            "생활비$": round(expense, 2),
            "배당충당$": round(from_cash, 2),
            "매도$": round(sold, 2),
            "잉여/부족$": round(surplus, 2),
            "잔여주식": round(float(w["Shares After"]), 2),
            "잔여현금$": round(float(w["Cash After"]), 2),
        })
    return pd.DataFrame(rows)


def _run(expense_mo, **kw):
    close, div = _load(TICKER)
    return run_fire_backtest(
        close, div, CORPUS,
        annual_withdrawal=expense_mo * 12,
        strategy="fixed_nominal", frequency="monthly",
        tax_rate_pct=15.0, start_date=START, **kw,
    )


def _report(title, r):
    s = r.summary
    print("\n" + "=" * 84)
    print(title)
    print(f"  생존={s['Survived']} · 최종자산=${s['Final Value']:,.0f} · "
          f"총인출=${s['Total Withdrawn']:,.0f} · 총배당(net)=${s['Total Net Dividend']:,.0f} · "
          f"총매도=${s['Total Shares Sold Value']:,.0f} · "
          f"잉여재투자=${s['Total Reinvested Surplus']:,.0f}")
    print(f"\n  ── {SAMPLE_YEAR}년 월별 ──")
    print(_monthly_table(r, SAMPLE_YEAR).to_string(index=False))


def main():
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 20)

    # CASE 1: expense ($3,000/mo) > O monthly dividend (~$2,300/mo) → sell shortfall
    _report("CASE 1  생활비 $3,000 > 월배당  (부족분 매도)",
            _run(3_000.0, reinvest_dividends=False))

    # CASE 2a: expense ($1,500/mo) < dividend → surplus kept as idle cash
    _report("CASE 2a 생활비 $1,500 < 월배당  (잉여 = 현금 보유)",
            _run(1_500.0, reinvest_dividends=False, reinvest_surplus=False))

    # CASE 2b: expense ($1,500/mo) < dividend → surplus reinvested into shares
    _report("CASE 2b 생활비 $1,500 < 월배당  (잉여 = 재투자)",
            _run(1_500.0, reinvest_dividends=False, reinvest_surplus=True))


if __name__ == "__main__":
    main()
