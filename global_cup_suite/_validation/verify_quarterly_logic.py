"""
Logic verification with SYNTHETIC data (price fixed at $100).

Quarterly payer, dividends on the 1st trading day of Jan/Apr/Jul/Oct.
User's model to confirm:
  - Jan dividend should fund Jan+Feb+Mar living expenses.
  - If the quarter's dividend < 3 months of expenses  -> SELL shares.
  - If it's MORE                                        -> reinvest the surplus.

Constant price makes every number hand-checkable:
  corpus $120,000 @ $100 = 1200 shares.
  dividend $3.00/share gross, 15% tax -> $2.55/share net -> 1200*2.55 = $3,060/quarter.

Run:
  PYB=/home/zealatan/.pyenv/versions/3.11.8/bin/python3.11
  SP=/home/zealatan/YOUTUBE/blog/global_cup_refactored/.venv/lib/python3.11/site-packages
  PYTHONPATH=$SP:. $PYB verify_quarterly_logic.py
"""
from __future__ import annotations

from datetime import date

import pandas as pd

from global_cup.fire_engine import run_fire_backtest

PRICE = 100.0
DPS = 3.0                       # gross dividend per share
PAY_MONTHS = (1, 4, 7, 10)     # quarterly


def _synthetic():
    idx = pd.bdate_range("2019-12-02", "2021-01-29")     # business days
    close = pd.Series(PRICE, index=idx)
    # dividend on the first business day of each pay month in 2020 + Jan 2021
    div_dates = []
    for (y, m) in [(2020, m) for m in PAY_MONTHS] + [(2021, 1)]:
        first_bd = idx[(idx.year == y) & (idx.month == m)][0]
        div_dates.append(first_bd)
    div = pd.Series(DPS, index=pd.DatetimeIndex(div_dates))
    return close, div


def _table(r, year=2020):
    tl = r.timeline_df.copy()
    tl["ym"] = tl["Date"].dt.to_period("M")
    div_m = tl.groupby("ym")["Dividend"].sum()
    # reinvested surplus per month: infer from shares delta not from sale/div — read timeline
    wd = r.withdrawal_df.copy()
    wd["ym"] = wd["Date"].dt.to_period("M")
    rows = []
    for _, w in wd[wd["Date"].dt.year == year].iterrows():
        ym = w["ym"]
        rows.append({
            "월": str(ym),
            "배당net$": round(float(div_m.get(ym, 0.0)), 2),
            "생활비$": round(float(w["Requested"]), 2),
            "배당충당$": round(float(w["From Cash"]), 2),
            "매도$": round(float(w["Sold Value"]), 2),
            "충당방식": w["Funded By"],
            "잔여주식": round(float(w["Shares After"]), 3),
            "잔여현금$": round(float(w["Cash After"]), 2),
        })
    return pd.DataFrame(rows)


def run_case(title, expense_mo):
    close, div = _synthetic()
    r = run_fire_backtest(
        close, div, 120_000.0,
        annual_withdrawal=expense_mo * 12,
        strategy="fixed_nominal", frequency="monthly",
        tax_rate_pct=15.0, reinvest_surplus=True,
        start_date=date(2019, 12, 2),
    )
    s = r.summary
    print("\n" + "=" * 88)
    print(f"{title}  (월 생활비 ${expense_mo:,.0f} · 분기배당 net $3,060 = 3개월치 ${expense_mo*3:,.0f}와 비교)")
    print(f"  최종주식={s['Final Shares']:.3f} · 최종현금=${s['Final Cash']:,.2f} · "
          f"총매도=${s['Total Shares Sold Value']:,.2f} · 재투자=${s['Total Reinvested Surplus']:,.2f}")
    print(_table(r).to_string(index=False))


def main():
    pd.set_option("display.width", 220); pd.set_option("display.max_columns", 20)
    # CASE A: 3-month expense $6,000 > quarterly net $3,060  -> must SELL
    run_case("CASE A  배당 < 3개월 생활비  → 매도 발생", 2_000.0)
    # CASE B: 3-month expense $1,500 < quarterly net $3,060  -> reinvest surplus
    run_case("CASE B  배당 > 3개월 생활비  → 잉여 재투자", 500.0)


if __name__ == "__main__":
    main()
