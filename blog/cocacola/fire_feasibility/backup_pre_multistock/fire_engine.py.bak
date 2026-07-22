"""
FIRE withdrawal backtest engine (USD basis, dividend-timing aware).

Models: retire with a lump-sum corpus, buy a stock, then draw living expenses
over time. Dividends land in a cash account on their actual pay dates (net of
withholding tax); withdrawals are funded from that cash first and only sell
shares for the shortfall. Answers "did the money last, and what's left?".

Accuracy choices:
  - Raw close + explicit dividends (no Adj Close double-count).
  - Dividends credited on the first trade date on/after each ex-date, net of
    `tax_rate_pct` withholding.
  - Withdrawals happen on period boundaries (first trade day of each month/
    year) strictly AFTER the buy date; the buy day itself is not a withdrawal.
  - Fractional shares allowed (whole-share mode is a future option).
  - No FX — everything is in the stock's native (USD) terms.

Withdrawal strategies:
  - "fixed_nominal"  : constant `annual_withdrawal` USD / period.
  - "fixed_real"     : `annual_withdrawal` inflation-adjusted via `cpi`
                       (this is also how the 4% rule is expressed:
                        annual_withdrawal = 0.04 * initial_amount).
  - "pct_portfolio"  : withdraw `withdrawal_rate` (annual) of current value,
                       spread across the period count — never fully depletes.
"""
from __future__ import annotations

import bisect
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional

import pandas as pd

_PERIODS_PER_YEAR = {"monthly": 12, "annual": 1}


@dataclass
class FireResult:
    summary: Dict[str, float]
    timeline_df: pd.DataFrame
    withdrawal_df: pd.DataFrame
    dividend_df: pd.DataFrame
    depleted: bool
    depletion_date: Optional[pd.Timestamp] = None


# ── helpers ────────────────────────────────────────────────────────────────────

def _asof(series: pd.Series, when: pd.Timestamp, default: float = 1.0) -> float:
    sub = series[series.index <= when]
    if len(sub):
        return float(sub.iloc[-1])
    return float(series.iloc[0]) if len(series) else default


def _period_start_dates(close: pd.Series, frequency: str, after: pd.Timestamp) -> set:
    """First trade date of each period (month/year) strictly after `after`."""
    idx = close.index
    if frequency == "annual":
        keys = idx.year
    else:
        keys = [(d.year, d.month) for d in idx]
    firsts = {}
    for d, k in zip(idx, keys):
        if k not in firsts:
            firsts[k] = d
    return {d for d in firsts.values() if d > after}


# ── engine ─────────────────────────────────────────────────────────────────────

def run_fire_backtest(
    close: pd.Series,
    dividends: pd.Series,
    initial_amount: float,
    *,
    annual_withdrawal: float = 0.0,
    withdrawal_rate: float = 0.0,          # annual fraction, for pct_portfolio
    strategy: str = "fixed_nominal",       # fixed_nominal|fixed_real|pct_portfolio
    frequency: str = "monthly",            # monthly|annual
    tax_rate_pct: float = 15.0,
    reinvest_dividends: bool = False,      # immediate full reinvest; withdrawals sell
    reinvest_surplus: bool = True,         # spend expense, reinvest leftover cash
                                           #   (default per user; ideal for MONTHLY
                                           #   payers. For quarterly/annual it also
                                           #   reinvests the multi-month buffer and
                                           #   causes churn — a cadence-aware reserve
                                           #   is future work.)
    cpi: Optional[pd.Series] = None,       # required for fixed_real
    start_date: Optional[date] = None,
) -> Optional[FireResult]:
    close = close.dropna().copy()
    if close.empty or initial_amount <= 0:
        return None
    close.index = pd.to_datetime(close.index).tz_localize(None)
    if start_date is not None:
        close = close[close.index >= pd.Timestamp(start_date)]
    if close.empty:
        return None

    if frequency not in _PERIODS_PER_YEAR:
        frequency = "monthly"
    ppy = _PERIODS_PER_YEAR[frequency]
    tax = max(0.0, min(100.0, float(tax_rate_pct))) / 100.0

    # dividends → per-trade-date net cash-per-share
    dividends = dividends.copy()
    div_on: Dict[pd.Timestamp, float] = {}
    if not dividends.empty:
        dividends.index = pd.to_datetime(dividends.index).tz_localize(None)
        dividends = dividends[(dividends.index >= close.index[0]) &
                              (dividends.index <= close.index[-1])]
        for ex_date, dps in dividends.sort_index().items():
            nxt = close.index[close.index >= ex_date]
            if len(nxt):
                div_on[nxt[0]] = div_on.get(nxt[0], 0.0) + float(dps)

    buy_date = close.index[0]
    buy_px = float(close.iloc[0])
    withdraw_dates = _period_start_dates(close, frequency, after=buy_date)
    # sorted schedules for the cadence-aware surplus reserve
    wd_sorted = sorted(withdraw_dates)
    div_dates_sorted = sorted(div_on.keys())

    cpi_base = _asof(cpi, buy_date) if cpi is not None else 1.0

    shares = initial_amount / buy_px
    cash = 0.0

    total_invested = initial_amount
    tot_gross_div = tot_tax = tot_net_div = 0.0
    tot_withdrawn = tot_shortfall_sold = tot_reinvested_surplus = 0.0
    peak_value = shares * buy_px
    min_value = peak_value
    max_dd = 0.0
    depleted = False
    depletion_date: Optional[pd.Timestamp] = None

    timeline_rows: List[dict] = []
    withdrawal_rows: List[dict] = []
    dividend_rows: List[dict] = []

    for d, price in close.items():
        d = pd.Timestamp(d)
        price = float(price)
        day_div = 0.0
        day_withdrawal = 0.0
        day_sold = 0.0

        # 1) dividends land first (income available for this period's spending)
        dps = div_on.get(d)
        if dps and shares > 0 and dps > 0:
            gross = shares * dps
            t = gross * tax
            net = gross - t
            tot_gross_div += gross
            tot_tax += t
            tot_net_div += net
            day_div = net
            if reinvest_dividends and price > 0:
                shares += net / price
            else:
                cash += net
            dividend_rows.append({
                "Date": d, "Price": price, "Div/Share": dps,
                "Gross": gross, "Tax": t, "Net": net,
                "Reinvested": bool(reinvest_dividends), "Shares": shares,
            })

        # 2) withdrawal on period boundary
        if d in withdraw_dates and not depleted:
            if strategy == "pct_portfolio":
                cur_value = shares * price + cash
                need = cur_value * (withdrawal_rate / ppy)
            elif strategy == "fixed_real":
                infl = (_asof(cpi, d) / cpi_base) if (cpi is not None and cpi_base) else 1.0
                need = (annual_withdrawal / ppy) * infl
            else:  # fixed_nominal
                need = annual_withdrawal / ppy

            need = max(0.0, need)
            # (1) fund from dividend cash first, (2) sell shares for the shortfall
            paid_from_cash = min(cash, need)
            cash -= paid_from_cash
            shortfall = need - paid_from_cash
            sold_value = 0.0

            if shortfall > 1e-9 and price > 0:
                shares_value = shares * price
                if shares_value >= shortfall:
                    day_sold = shortfall / price
                    shares -= day_sold
                    sold_value = shortfall
                else:
                    # not enough shares to cover — liquidate remainder, deplete
                    day_sold = shares
                    sold_value = shares_value
                    shares = 0.0
                    depleted = True
                    depletion_date = d
                tot_shortfall_sold += sold_value

            day_withdrawal = paid_from_cash + sold_value  # actually handed out
            tot_withdrawn += day_withdrawal
            withdrawal_rows.append({
                "Date": d, "Price": price, "Requested": need,
                "From Cash": paid_from_cash, "Sold Shares": day_sold,
                "Sold Value": sold_value, "Paid Out": day_withdrawal,
                "Funded By": "dividend cash" if shortfall <= 1e-9 else
                             ("mixed" if paid_from_cash > 1e-9 else "share sale"),
                "Shares After": shares, "Cash After": cash, "Depleted": depleted,
            })

            # 3) reinvest leftover cash — but keep a cadence-aware RESERVE:
            #    the expenses that must be funded from cash before the next
            #    dividend arrives (so quarterly/annual buffers aren't churned).
            if reinvest_surplus and cash > 1e-9 and price > 0:
                ni = bisect.bisect_right(div_dates_sorted, d)
                if ni < len(div_dates_sorted):
                    # keep enough cash to fund the withdrawals due before the
                    # next dividend refreshes it; reinvest only the excess.
                    next_div = div_dates_sorted[ni]
                    lo = bisect.bisect_right(wd_sorted, d)
                    hi = bisect.bisect_left(wd_sorted, next_div)
                    reserve = need * max(0, hi - lo)
                    investable = cash - reserve
                    if investable > 1e-9:
                        shares += investable / price
                        tot_reinvested_surplus += investable
                        cash -= investable
                # else: no future dividend to refresh cash — keep it all as
                # cash to fund remaining withdrawals (avoids end-of-life churn).

        value = shares * price + cash
        peak_value = max(peak_value, value)
        min_value = min(min_value, value)
        if peak_value > 0:
            max_dd = max(max_dd, (peak_value - value) / peak_value)

        timeline_rows.append({
            "Date": d, "Price": price, "Shares": shares, "Cash": cash,
            "Dividend": day_div, "Withdrawal": day_withdrawal,
            "Portfolio Value": value,
            "Cumulative Withdrawn": tot_withdrawn,
            "Cumulative Net Dividend": tot_net_div,
        })

    timeline_df = pd.DataFrame(timeline_rows)
    end_date = close.index[-1]
    end_px = float(close.iloc[-1])
    final_value = shares * end_px + cash

    years = max((end_date - buy_date).days, 1) / 365.25
    if depleted and depletion_date is not None:
        survived_years = max((depletion_date - buy_date).days, 0) / 365.25
    else:
        survived_years = years

    real_final = final_value * (cpi_base / _asof(cpi, end_date)) if (cpi is not None) else final_value

    summary = {
        "Initial Amount": float(initial_amount),
        "Strategy": strategy,
        "Frequency": frequency,
        "Annual Withdrawal": float(annual_withdrawal),
        "Withdrawal Rate %": float(withdrawal_rate * 100.0),
        "Tax Rate %": float(tax_rate_pct),
        "Reinvest Dividends": bool(reinvest_dividends),
        "Final Value": float(final_value),
        "Final Value Real": float(real_final),
        "Final Shares": float(shares),
        "Final Cash": float(cash),
        "Total Withdrawn": float(tot_withdrawn),
        "Total Net Dividend": float(tot_net_div),
        "Total Gross Dividend": float(tot_gross_div),
        "Total Dividend Tax": float(tot_tax),
        "Total Shares Sold Value": float(tot_shortfall_sold),
        "Total Reinvested Surplus": float(tot_reinvested_surplus),
        "Min Portfolio Value": float(min_value),
        "Max Drawdown %": float(max_dd * 100.0),
        "Years": float(years),
        "Survived Years": float(survived_years),
        "Survived": (not depleted),
        "Depletion Date": depletion_date,
        "Buy Price": buy_px,
        "End Price": end_px,
    }

    return FireResult(
        summary=summary,
        timeline_df=timeline_df,
        withdrawal_df=pd.DataFrame(withdrawal_rows),
        dividend_df=pd.DataFrame(dividend_rows),
        depleted=depleted,
        depletion_date=depletion_date,
    )
