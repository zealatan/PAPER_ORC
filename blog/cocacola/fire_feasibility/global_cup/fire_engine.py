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


# ══════════════════════════════════════════════════════════════════════════════
# MULTI-ASSET PORTFOLIO ENGINE
# ══════════════════════════════════════════════════════════════════════════════
# Same retirement model as run_fire_backtest(), generalised to a basket of up to
# N stocks held in fixed initial weights on a SHARED cash account:
#   - Buy each stock on the (common) buy date with its weight share of the corpus.
#   - Every stock's dividends land — net of tax — in ONE shared cash pool.
#   - Living expense is funded from that cash first; the shortfall is covered by
#     SELLING shares. Two selling modes (sell_priority):
#       * "weights" (default): sell each stock pro-rata to its INITIAL weight, so
#         the basket keeps its target allocation.
#       * "annual_income"/"yield"/"dps": cascade — fully sell the LOWEST-dividend
#         stock first, preserving the income-heavy holdings.
#   - Leftover cash is reinvested (reinvest_target): "weights" (split by initial
#     weight), "highest_yield", or "pick" (all surplus into one designated stock
#     via reinvest_pick_ticker), keeping the cadence-aware reserve. When
#     ignore_reinvest_dividends=True, reinvested shares earn NO dividends (no
#     dividend-on-dividend compounding); on a sale the base/reinvested split of a
#     holding shrinks proportionally.
# The single-stock run_fire_backtest() above is left byte-for-byte unchanged so
# the existing validation / example scripts keep passing.

@dataclass
class AssetSpec:
    """One holding in the portfolio.

    reinvest_only=True marks a stock that is NOT part of the withdrawal basket:
    it is never bought at retirement, never sold for living expenses, and pays no
    dividends — it only accumulates when surplus dividends are reinvested into it
    (a pure price-growth side-pot). Its `weight` is ignored.
    """
    name: str
    ticker: str
    close: pd.Series
    dividends: pd.Series
    weight: float               # relative weight; normalised across the basket
    reinvest_only: bool = False


@dataclass
class FireMultiResult:
    summary: Dict[str, float]
    timeline_df: pd.DataFrame          # Date + Portfolio Value + one value col per asset
    withdrawal_df: pd.DataFrame
    dividend_df: pd.DataFrame
    asset_summary_df: pd.DataFrame     # per-asset final breakdown
    depleted: bool
    depletion_date: Optional[pd.Timestamp] = None


def _trailing_annual_dps(dividends: pd.Series):
    """Return f(when)->trailing-365-day dividend-per-share as of `when`.

    Used to rank stocks by "how much do they pay right now". Empty series -> 0.
    """
    if dividends is None or dividends.empty:
        return lambda when: 0.0
    d = dividends.copy()
    d.index = pd.to_datetime(d.index).tz_localize(None)
    d = d.sort_index()
    dates = list(d.index)
    cum: List[float] = []
    running = 0.0
    for v in d.values:
        running += float(v)
        cum.append(running)

    def fn(when) -> float:
        when = pd.Timestamp(when)
        lo = when - pd.Timedelta(days=365)
        hi_i = bisect.bisect_right(dates, when)
        lo_i = bisect.bisect_right(dates, lo)
        upper = cum[hi_i - 1] if hi_i > 0 else 0.0
        lower = cum[lo_i - 1] if lo_i > 0 else 0.0
        return upper - lower

    return fn


def run_fire_backtest_multi(
    assets: List[AssetSpec],
    initial_amount: float,
    *,
    annual_withdrawal: float = 0.0,
    withdrawal_rate: float = 0.0,
    strategy: str = "fixed_nominal",       # fixed_nominal|fixed_real|pct_portfolio
    frequency: str = "monthly",            # monthly|annual
    tax_rate_pct: float = 15.0,
    reinvest_dividends: bool = False,      # immediate full reinvest into the payer
    reinvest_surplus: bool = True,         # spend expense, reinvest leftover cash
    sell_priority: str = "weights",        # weights|annual_income|yield|dps
                                           #   weights: sell each stock pro-rata to
                                           #   its initial weight (keep allocation);
                                           #   others: cascade, lowest metric first
    reinvest_target: str = "weights",      # weights|highest_yield|pick|select
    reinvest_pick_ticker: Optional[str] = None,      # single target when target="pick"
    reinvest_pick_tickers: Optional[List[str]] = None,  # chosen stocks when target="select"
    ignore_reinvest_dividends: bool = False,     # reinvested shares earn NO dividends
    cpi: Optional[pd.Series] = None,
    start_date: Optional[date] = None,
) -> Optional[FireMultiResult]:
    # ── clean + validate; basket stocks need weight, reinvest-only ones don't ────
    specs: List[AssetSpec] = []
    for a in assets:
        c = a.close.dropna().copy()
        if c.empty:
            continue
        if not a.reinvest_only and a.weight <= 0:
            continue
        c.index = pd.to_datetime(c.index).tz_localize(None)
        if start_date is not None:
            c = c[c.index >= pd.Timestamp(start_date)]
        if c.empty:
            continue
        specs.append(AssetSpec(a.name, a.ticker, c, a.dividends,
                               float(a.weight), a.reinvest_only))

    basket = [s for s in specs if not s.reinvest_only]
    if not basket or initial_amount <= 0:
        return None

    wsum = sum(s.weight for s in basket)
    if wsum <= 0:
        return None
    for s in specs:
        s.weight = (s.weight / wsum) if not s.reinvest_only else 0.0   # basket → sum 1.0

    if frequency not in _PERIODS_PER_YEAR:
        frequency = "monthly"
    ppy = _PERIODS_PER_YEAR[frequency]
    tax = max(0.0, min(100.0, float(tax_rate_pct))) / 100.0

    # ── common calendar: buy on the first date all BASKET stocks have data;
    #    reinvest-only stocks just contribute their trade dates (bought later) ────
    buy_date = max(s.close.index[0] for s in basket)
    master = pd.DatetimeIndex(sorted(set().union(*[
        set(s.close.index[s.close.index >= buy_date]) for s in specs
    ])))
    if len(master) == 0:
        return None

    n = len(specs)
    prices = []          # per-asset price series aligned to master (ffilled)
    div_on = []          # per-asset {trade_date: gross dps}
    annual_dps_fn = []   # per-asset trailing-annual dps function
    all_div_dates: set = set()
    for s in specs:
        px = s.close.reindex(master).ffill()
        prices.append(px)
        d_on: Dict[pd.Timestamp, float] = {}
        dv = s.dividends
        if dv is not None and not dv.empty:
            dv = dv.copy()
            dv.index = pd.to_datetime(dv.index).tz_localize(None)
            dv = dv[(dv.index >= master[0]) & (dv.index <= master[-1])]
            for ex_date, dps in dv.sort_index().items():
                nxt = master[master >= ex_date]
                if len(nxt):
                    d_on[nxt[0]] = d_on.get(nxt[0], 0.0) + float(dps)
        div_on.append(d_on)
        all_div_dates.update(d_on.keys())
        annual_dps_fn.append(_trailing_annual_dps(s.dividends))

    div_dates_sorted = sorted(all_div_dates)

    withdraw_dates = _period_start_dates(master.to_series(), frequency, after=buy_date)
    wd_sorted = sorted(withdraw_dates)

    cpi_base = _asof(cpi, buy_date) if cpi is not None else 1.0

    # ── initial buy (split corpus by weight) ────────────────────────────────────
    shares = [0.0] * n
    buy_px = [0.0] * n
    amount_i = [0.0] * n
    for i, s in enumerate(specs):
        if s.reinvest_only:            # not bought at retirement — grows via reinvest
            buy_px[i] = 0.0
            amount_i[i] = 0.0
            shares[i] = 0.0
            continue
        px0 = float(prices[i].iloc[0])
        buy_px[i] = px0
        amt = initial_amount * s.weight
        amount_i[i] = amt
        shares[i] = amt / px0 if px0 > 0 else 0.0

    cash = 0.0
    total_invested = initial_amount
    tot_gross_div = tot_tax = tot_net_div = 0.0
    tot_withdrawn = tot_shortfall_sold = tot_reinvested_surplus = 0.0
    net_div_i = [0.0] * n
    sold_val_i = [0.0] * n

    peak_value = sum(shares[i] * buy_px[i] for i in range(n))
    min_value = peak_value
    max_dd = 0.0
    depleted = False
    depletion_date: Optional[pd.Timestamp] = None

    timeline_rows: List[dict] = []
    withdrawal_rows: List[dict] = []
    dividend_rows: List[dict] = []

    asset_cols = [f"{s.ticker}" for s in specs]

    # portion of each holding bought via reinvestment (earns no dividend when
    # ignore_reinvest_dividends=True); pick target index for reinvest_target="pick"
    reinv_shares = [0.0] * n
    pick_idx: Optional[int] = None
    if reinvest_pick_ticker:
        for i, s in enumerate(specs):
            if s.ticker == reinvest_pick_ticker:
                pick_idx = i
                break
    # indices of the chosen stocks for reinvest_target="select"
    pick_indices: List[int] = []
    if reinvest_pick_tickers:
        chosen = set(reinvest_pick_tickers)
        pick_indices = [i for i, s in enumerate(specs) if s.ticker in chosen]

    def _sell_shares(i, sold_sh):
        """Reduce holding i by sold_sh, shrinking its reinvested (non-dividend)
        portion proportionally so the base (dividend-earning) ratio is preserved."""
        old = shares[i]
        if old <= 0:
            return
        take = min(sold_sh, old)
        reinv_shares[i] -= reinv_shares[i] * (take / old)
        shares[i] = old - take

    for pos, d in enumerate(master):
        d = pd.Timestamp(d)
        # NaN (a reinvest-only stock before its data starts) → 0 so it neither
        # holds value nor can be bought until it actually exists
        price = []
        for i in range(n):
            pv = float(prices[i].iloc[pos])
            price.append(0.0 if pd.isna(pv) else pv)
        day_div = 0.0
        day_withdrawal = 0.0

        # 1) dividends across ALL stocks land in the shared cash pool.
        #    when ignore_reinvest_dividends, only the BASE (non-reinvested) shares
        #    earn dividends — reinvested shares are treated as non-paying.
        for i in range(n):
            if specs[i].reinvest_only:      # reinvest-only stocks never pay dividends
                continue
            dps = div_on[i].get(d)
            div_shares = shares[i] - (reinv_shares[i] if ignore_reinvest_dividends else 0.0)
            if dps and div_shares > 0 and dps > 0:
                gross = div_shares * dps
                t = gross * tax
                net = gross - t
                tot_gross_div += gross
                tot_tax += t
                tot_net_div += net
                net_div_i[i] += net
                day_div += net
                if reinvest_dividends and price[i] > 0:
                    shares[i] += net / price[i]
                    reinv_shares[i] += net / price[i]
                else:
                    cash += net
                dividend_rows.append({
                    "Date": d, "Ticker": specs[i].ticker, "Price": price[i],
                    "Div/Share": dps, "Gross": gross, "Tax": t, "Net": net,
                    "Reinvested": bool(reinvest_dividends),
                })

        # 2) withdrawal on a period boundary
        if d in withdraw_dates and not depleted:
            port_value = sum(shares[i] * price[i] for i in range(n)) + cash
            if strategy == "pct_portfolio":
                need = port_value * (withdrawal_rate / ppy)
            elif strategy == "fixed_real":
                infl = (_asof(cpi, d) / cpi_base) if (cpi is not None and cpi_base) else 1.0
                need = (annual_withdrawal / ppy) * infl
            else:  # fixed_nominal
                need = annual_withdrawal / ppy
            need = max(0.0, need)

            paid_from_cash = min(cash, need)
            cash -= paid_from_cash
            shortfall = need - paid_from_cash
            sold_value = 0.0
            sold_detail: List[str] = []

            if shortfall > 1e-9:
                if sell_priority == "weights":
                    # sell each stock PROPORTIONALLY to its initial weight, so the
                    # basket keeps its target allocation. Renormalize the split
                    # across stocks that still have value and iterate, so a
                    # maxed-out stock's unmet portion spills onto the others.
                    per_asset_sold = [0.0] * n
                    for _ in range(n):
                        if shortfall <= 1e-9:
                            break
                        eligible = [i for i in range(n)
                                    if not specs[i].reinvest_only
                                    and price[i] > 0 and shares[i] * price[i] > 1e-9]
                        if not eligible:
                            break
                        wsum_e = sum(specs[i].weight for i in eligible)
                        round_sold = 0.0
                        for i in eligible:
                            frac = (specs[i].weight / wsum_e) if wsum_e > 0 \
                                else (1.0 / len(eligible))
                            target = shortfall * frac
                            take = min(target, shares[i] * price[i])
                            if take <= 0:
                                continue
                            _sell_shares(i, take / price[i])
                            sold_value += take
                            sold_val_i[i] += take
                            per_asset_sold[i] += take
                            round_sold += take
                        shortfall -= round_sold
                        if round_sold <= 1e-12:
                            break
                    for i in range(n):
                        if per_asset_sold[i] > 1e-9:
                            sold_detail.append(f"{specs[i].ticker}:{per_asset_sold[i]:,.0f}")
                else:
                    # rank stocks: lowest dividend metric sold FIRST (cascade)
                    def _metric(i):
                        adps = annual_dps_fn[i](d)
                        if sell_priority == "annual_income":
                            return shares[i] * adps
                        if sell_priority == "dps":
                            return adps
                        # "yield": annual dps / price
                        return (adps / price[i]) if price[i] > 0 else 0.0

                    order = sorted((i for i in range(n) if not specs[i].reinvest_only),
                                   key=lambda i: (_metric(i), i))
                    for i in order:
                        if shortfall <= 1e-9:
                            break
                        if price[i] <= 0 or shares[i] <= 0:
                            continue
                        asset_value = shares[i] * price[i]
                        if asset_value >= shortfall:
                            sold_sh = shortfall / price[i]
                            _sell_shares(i, sold_sh)
                            sold_value += shortfall
                            sold_val_i[i] += shortfall
                            sold_detail.append(f"{specs[i].ticker}:{shortfall:,.0f}")
                            shortfall = 0.0
                        else:
                            _sell_shares(i, shares[i])
                            sold_value += asset_value
                            sold_val_i[i] += asset_value
                            sold_detail.append(f"{specs[i].ticker}:{asset_value:,.0f}(all)")
                            shortfall -= asset_value
                tot_shortfall_sold += sold_value
                if shortfall > 1e-9:
                    # couldn't cover the expense even after liquidating everything
                    depleted = True
                    depletion_date = d

            day_withdrawal = paid_from_cash + sold_value
            tot_withdrawn += day_withdrawal
            withdrawal_rows.append({
                "Date": d, "Requested": need, "From Cash": paid_from_cash,
                "Sold Value": sold_value, "Paid Out": day_withdrawal,
                "Sold Detail": ", ".join(sold_detail),
                "Funded By": "dividend cash" if sold_value <= 1e-9 else
                             ("mixed" if paid_from_cash > 1e-9 else "share sale"),
                "Cash After": cash, "Depleted": depleted,
            })

            # 3) reinvest leftover cash, keeping a cadence-aware reserve
            if reinvest_surplus and cash > 1e-9 and not depleted:
                ni = bisect.bisect_right(div_dates_sorted, d)
                if ni < len(div_dates_sorted):
                    next_div = div_dates_sorted[ni]
                    lo = bisect.bisect_right(wd_sorted, d)
                    hi = bisect.bisect_left(wd_sorted, next_div)
                    reserve = need * max(0, hi - lo)
                    investable = cash - reserve
                    if investable > 1e-9:
                        if reinvest_target == "select" and pick_indices:
                            # split surplus EQUALLY across the chosen stocks that
                            # currently have a price (so out-of-basket / not-yet-
                            # existing reinvest targets are handled cleanly)
                            buyable = [i for i in pick_indices if price[i] > 0]
                            spent = 0.0
                            if buyable:
                                each = investable / len(buyable)
                                for i in buyable:
                                    bought = each / price[i]
                                    shares[i] += bought
                                    reinv_shares[i] += bought
                                    spent += each
                            tot_reinvested_surplus += spent
                            cash -= spent
                        elif reinvest_target == "pick" and pick_idx is not None \
                                and price[pick_idx] > 0:
                            # buy the user-designated stock with all the surplus
                            j = pick_idx
                            bought = investable / price[j]
                            shares[j] += bought
                            reinv_shares[j] += bought
                            tot_reinvested_surplus += investable
                            cash -= investable
                        elif reinvest_target == "highest_yield":
                            ys = [((annual_dps_fn[i](d) / price[i]) if price[i] > 0 else -1.0, i)
                                  for i in range(n)]
                            _, j = max(ys)
                            if price[j] > 0:
                                bought = investable / price[j]
                                shares[j] += bought
                                reinv_shares[j] += bought
                                tot_reinvested_surplus += investable
                                cash -= investable
                        else:  # "weights": split by initial weight
                            spent = 0.0
                            for i in range(n):
                                if price[i] <= 0:
                                    continue
                                chunk = investable * specs[i].weight
                                bought = chunk / price[i]
                                shares[i] += bought
                                reinv_shares[i] += bought
                                spent += chunk
                            tot_reinvested_surplus += spent
                            cash -= spent

        value = sum(shares[i] * price[i] for i in range(n)) + cash
        peak_value = max(peak_value, value)
        min_value = min(min_value, value)
        if peak_value > 0:
            max_dd = max(max_dd, (peak_value - value) / peak_value)

        row = {
            "Date": d, "Cash": cash, "Dividend": day_div,
            "Withdrawal": day_withdrawal, "Portfolio Value": value,
            "Cumulative Withdrawn": tot_withdrawn,
            "Cumulative Net Dividend": tot_net_div,
        }
        for i in range(n):
            row[asset_cols[i]] = shares[i] * price[i]      # value (stacked chart)
            row[f"SH::{asset_cols[i]}"] = shares[i]         # share count
        timeline_rows.append(row)

    timeline_df = pd.DataFrame(timeline_rows)
    end_date = master[-1]
    end_px = []
    for i in range(n):
        pv = float(prices[i].iloc[-1])
        end_px.append(0.0 if pd.isna(pv) else pv)   # never-existed reinvest target → 0
    final_value = sum(shares[i] * end_px[i] for i in range(n)) + cash

    years = max((end_date - buy_date).days, 1) / 365.25
    if depleted and depletion_date is not None:
        survived_years = max((depletion_date - buy_date).days, 0) / 365.25
    else:
        survived_years = years

    real_final = final_value * (cpi_base / _asof(cpi, end_date)) if (cpi is not None) else final_value

    asset_summary_df = pd.DataFrame([{
        "Name": specs[i].name, "Ticker": specs[i].ticker,
        "Weight %": specs[i].weight * 100.0, "Initial Amount": amount_i[i],
        "Buy Price": buy_px[i], "End Price": end_px[i],
        "Final Shares": shares[i], "Final Value": shares[i] * end_px[i],
        "Total Net Dividend": net_div_i[i], "Total Sold Value": sold_val_i[i],
        "Reinvest Only": specs[i].reinvest_only,
    } for i in range(n)])

    summary = {
        "Initial Amount": float(initial_amount),
        "Strategy": strategy,
        "Frequency": frequency,
        "Annual Withdrawal": float(annual_withdrawal),
        "Withdrawal Rate %": float(withdrawal_rate * 100.0),
        "Tax Rate %": float(tax_rate_pct),
        "Sell Priority": sell_priority,
        "Reinvest Target": reinvest_target,
        "Reinvest Pick": (specs[pick_idx].ticker if pick_idx is not None else None),
        "Reinvest Select": [specs[i].ticker for i in pick_indices],
        "Ignore Reinvest Dividends": bool(ignore_reinvest_dividends),
        "Reinvest Dividends": bool(reinvest_dividends),
        "N Assets": n,
        "Asset Tickers": asset_cols,
        "Final Value": float(final_value),
        "Final Value Real": float(real_final),
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
    }

    return FireMultiResult(
        summary=summary,
        timeline_df=timeline_df,
        withdrawal_df=pd.DataFrame(withdrawal_rows),
        dividend_df=pd.DataFrame(dividend_rows),
        asset_summary_df=asset_summary_df,
        depleted=depleted,
        depletion_date=depletion_date,
    )
