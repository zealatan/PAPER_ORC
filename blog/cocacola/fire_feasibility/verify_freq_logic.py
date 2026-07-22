"""
Logic verification with SYNTHETIC data (price fixed at $100) — semiannual & annual.

Same method as verify_quarterly_logic.py, generalized. One dividend payment must
fund `cycle_months` of living expenses (6 for semiannual, 12 for annual):
  - payment net < cycle_months * expense  -> SELL the shortfall over the cycle
  - payment net > cycle_months * expense  -> reinvest the surplus

Constant price $100, corpus $120,000 = 1200 shares, 15% tax.
  semiannual dps $6 gross -> $5.10 net -> 1200*5.10 = $6,120 / payment (funds 6 mo)
  annual     dps $12 gross -> $10.20 net -> 1200*10.20 = $12,240 / payment (funds 12 mo)

Run:
  PYB=/home/zealatan/.pyenv/versions/3.11.8/bin/python3.11
  SP=/home/zealatan/YOUTUBE/blog/global_cup_refactored/.venv/lib/python3.11/site-packages
  PYTHONPATH=$SP:. $PYB verify_freq_logic.py
"""
from __future__ import annotations

from datetime import date

import pandas as pd

from global_cup.fire_engine import run_fire_backtest

PRICE = 100.0
TAX = 0.15


def _synthetic(pay_months, dps, last="2021-08-31"):
    idx = pd.bdate_range("2019-12-02", last)
    close = pd.Series(PRICE, index=idx)
    years = sorted(set(idx.year))
    div_dates = []
    for y in years:
        for m in pay_months:
            sel = idx[(idx.year == y) & (idx.month == m)]
            if len(sel):
                div_dates.append(sel[0])   # first business day of pay month
    div = pd.Series(dps, index=pd.DatetimeIndex(sorted(div_dates)))
    return close, div


def _table(r, year=2020):
    tl = r.timeline_df.copy(); tl["ym"] = tl["Date"].dt.to_period("M")
    div_m = tl.groupby("ym")["Dividend"].sum()
    wd = r.withdrawal_df.copy(); wd["ym"] = wd["Date"].dt.to_period("M")
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


def run_case(freq_label, pay_months, dps, cycle_months, expense_mo, kind, last):
    close, div = _synthetic(pay_months, dps, last)
    net_pay = 1200 * dps * (1 - TAX)
    r = run_fire_backtest(
        close, div, 120_000.0,
        annual_withdrawal=expense_mo * 12,
        strategy="fixed_nominal", frequency="monthly",
        tax_rate_pct=TAX * 100, reinvest_surplus=True,
        start_date=date(2019, 12, 2),
    )
    s = r.summary
    expect = "매도" if expense_mo * cycle_months > net_pay else "재투자"
    print("\n" + "=" * 92)
    print(f"{freq_label}  {kind}  월생활비 ${expense_mo:,.0f} · 지급월 {list(pay_months)}")
    print(f"  1회 배당 net ${net_pay:,.0f}  vs  {cycle_months}개월 생활비 ${expense_mo*cycle_months:,.0f}"
          f"  → 예상: {expect}")
    print(f"  총매도=${s['Total Shares Sold Value']:,.2f} · 재투자=${s['Total Reinvested Surplus']:,.2f} · "
          f"최종주식={s['Final Shares']:.3f}")
    print(_table(r).to_string(index=False))


def main():
    pd.set_option("display.width", 240); pd.set_option("display.max_columns", 20)

    # ── SEMIANNUAL: pay Jan & Jul, one payment funds 6 months ──
    run_case("반기배당 (semiannual)", (1, 7), 6.0, 6, 1_200.0, "CASE A 배당<6개월생활비 → 매도", "2021-08-31")
    run_case("반기배당 (semiannual)", (1, 7), 6.0, 6,   800.0, "CASE B 배당>6개월생활비 → 재투자", "2021-08-31")

    # ── ANNUAL: pay Jan, one payment funds 12 months ──
    run_case("연배당 (annual)", (1,), 12.0, 12, 1_200.0, "CASE A 배당<12개월생활비 → 매도", "2021-02-28")
    run_case("연배당 (annual)", (1,), 12.0, 12,   800.0, "CASE B 배당>12개월생활비 → 재투자", "2021-02-28")


if __name__ == "__main__":
    main()
