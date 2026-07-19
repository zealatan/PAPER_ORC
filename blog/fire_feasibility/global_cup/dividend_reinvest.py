from __future__ import annotations

from datetime import date
from typing import Dict, Optional

import pandas as pd

from .market_config import DividendReinvestResult


# ── Internal helpers ───────────────────────────────────────────────────────────

def _next_trade_date(close: pd.Series, target_date: pd.Timestamp) -> Optional[pd.Timestamp]:
    idx = close.index[close.index >= pd.Timestamp(target_date)]
    if len(idx) == 0:
        return None
    return pd.Timestamp(idx[0])


def _first_trade_date_of_month(close: pd.Series, year: int, month: int) -> Optional[pd.Timestamp]:
    first_day = pd.Timestamp(date(year, month, 1))
    return _next_trade_date(close, first_day)


def _years_between(start: pd.Timestamp, end: pd.Timestamp) -> float:
    days = max((pd.Timestamp(end) - pd.Timestamp(start)).days, 1)
    return days / 365.25


# ── Main backtest engine ───────────────────────────────────────────────────────

def run_dividend_reinvest_backtest(
    close: pd.Series,
    dividends: pd.Series,
    initial_amount: float,
    monthly_amount: float,
    tax_rate_pct: float,
    reinvest_dividends: bool = True,
    invest_on_trigger: bool = False,
    trigger_dates=None,
) -> Optional[DividendReinvestResult]:
    close = close.dropna().copy()
    if close.empty or initial_amount <= 0:
        return None

    close.index = pd.to_datetime(close.index).tz_localize(None)

    dividends = dividends.copy()
    if not dividends.empty:
        dividends.index = pd.to_datetime(dividends.index).tz_localize(None)
        dividends = dividends[
            (dividends.index >= close.index[0]) & (dividends.index <= close.index[-1])
        ]
        dividends = dividends.sort_index().astype(float)

    tax_rate = max(0.0, min(100.0, float(tax_rate_pct))) / 100.0

    event_rows = []
    monthly_buy_dates = set()
    months = sorted(set((d.year, d.month) for d in close.index))
    for y, m in months:
        d = _first_trade_date_of_month(close, y, m)
        if d is not None and d != close.index[0] and monthly_amount > 0:
            monthly_buy_dates.add(d)

    # Recurring external buys: either monthly (default) or only on trigger days.
    # In trigger mode the same `monthly_amount` is invested at each trigger event
    # instead of every month.
    if invest_on_trigger:
        recurring_buy_dates = set()
        for td in (trigger_dates or []):
            d = _next_trade_date(close, pd.Timestamp(td))
            if d is not None and d != close.index[0] and monthly_amount > 0:
                recurring_buy_dates.add(d)
        recurring_buy_label = "Trigger Buy"
    else:
        recurring_buy_dates = monthly_buy_dates
        recurring_buy_label = "Monthly Buy"

    dividend_events_by_trade_date: Dict = {}
    for div_date, div_per_share in dividends.items():
        trade_date = _next_trade_date(close, pd.Timestamp(div_date))
        if trade_date is None:
            continue
        dividend_events_by_trade_date.setdefault(trade_date, []).append(
            (pd.Timestamp(div_date), float(div_per_share))
        )

    shares = 0.0
    cash = 0.0
    total_external_invested = 0.0
    cumulative_gross_dividend = 0.0
    cumulative_tax = 0.0
    cumulative_net_dividend = 0.0
    cumulative_reinvested_amount = 0.0
    timeline_rows = []

    for d, price in close.items():
        d = pd.Timestamp(d)
        price = float(price)

        if d == close.index[0]:
            buy_shares = initial_amount / price if price > 0 else 0.0
            shares += buy_shares
            total_external_invested += initial_amount
            event_rows.append({
                "Date": d, "Type": "Initial Buy", "Price": price,
                "Cash Amount": initial_amount, "Gross Dividend": 0.0,
                "Tax": 0.0, "Net Dividend": 0.0, "Dividend per Share": 0.0,
                "Shares Bought": buy_shares, "Total Shares": shares,
                "External Invested": total_external_invested,
            })

        if d in recurring_buy_dates:
            buy_shares = monthly_amount / price if price > 0 else 0.0
            shares += buy_shares
            total_external_invested += monthly_amount
            event_rows.append({
                "Date": d, "Type": recurring_buy_label, "Price": price,
                "Cash Amount": monthly_amount, "Gross Dividend": 0.0,
                "Tax": 0.0, "Net Dividend": 0.0, "Dividend per Share": 0.0,
                "Shares Bought": buy_shares, "Total Shares": shares,
                "External Invested": total_external_invested,
            })

        for original_div_date, div_per_share in dividend_events_by_trade_date.get(d, []):
            if shares <= 0 or div_per_share <= 0:
                continue
            gross_dividend = shares * div_per_share
            tax = gross_dividend * tax_rate
            net_dividend = gross_dividend - tax

            cumulative_gross_dividend += gross_dividend
            cumulative_tax += tax
            cumulative_net_dividend += net_dividend

            if reinvest_dividends:
                reinvest_shares = net_dividend / price if price > 0 else 0.0
                cumulative_reinvested_amount += net_dividend
                shares += reinvest_shares
                event_type = "Dividend Reinvest"
            else:
                reinvest_shares = 0.0
                cash += net_dividend
                event_type = "Dividend Cash"

            event_rows.append({
                "Date": d, "Type": event_type, "Price": price,
                "Cash Amount": net_dividend, "Gross Dividend": gross_dividend,
                "Tax": tax, "Net Dividend": net_dividend,
                "Dividend per Share": div_per_share,
                "Shares Bought": reinvest_shares, "Total Shares": shares,
                "External Invested": total_external_invested,
                "Original Dividend Date": original_div_date,
            })

        value = shares * price + cash
        pnl = value - total_external_invested
        ret_pct = pnl / total_external_invested * 100.0 if total_external_invested > 0 else 0.0
        timeline_rows.append({
            "Date": d, "Price": price, "Total Shares": shares,
            "External Invested": total_external_invested,
            "Portfolio Value": value, "PnL": pnl, "Return %": ret_pct,
            "Cash": cash,
            "Cumulative Gross Dividend": cumulative_gross_dividend,
            "Cumulative Tax": cumulative_tax,
            "Cumulative Net Dividend": cumulative_net_dividend,
            "Cumulative Reinvested Amount": cumulative_reinvested_amount,
        })

    timeline_df = pd.DataFrame(timeline_rows)
    event_df = pd.DataFrame(event_rows)

    final_price = float(close.iloc[-1])
    final_value = shares * final_price + cash
    total_profit = final_value - total_external_invested
    total_return_pct = (
        total_profit / total_external_invested * 100.0
        if total_external_invested > 0 else 0.0
    )
    years = _years_between(close.index[0], close.index[-1])
    cagr = (
        ((final_value / total_external_invested) ** (1.0 / years) - 1.0) * 100.0
        if total_external_invested > 0 and final_value > 0 else 0.0
    )

    recent_annual_dividend_per_share = 0.0
    if not dividends.empty:
        annual_div = dividends.groupby(dividends.index.year).sum()
        if not annual_div.empty:
            recent_annual_dividend_per_share = float(annual_div.iloc[-1])

    current_estimated_annual_dividend_gross = shares * recent_annual_dividend_per_share
    current_estimated_annual_dividend_net = current_estimated_annual_dividend_gross * (1.0 - tax_rate)
    yield_on_cost_net = (
        current_estimated_annual_dividend_net / total_external_invested * 100.0
        if total_external_invested > 0 else 0.0
    )
    current_yield_net = (
        current_estimated_annual_dividend_net / final_value * 100.0
        if final_value > 0 else 0.0
    )

    if event_df.empty:
        annual_df = pd.DataFrame()
    else:
        div_events = event_df[event_df["Type"].isin(["Dividend Reinvest", "Dividend Cash"])].copy()
        if div_events.empty:
            annual_df = pd.DataFrame()
        else:
            div_events["Year"] = div_events["Date"].dt.year
            annual_df = div_events.groupby("Year", as_index=False).agg({
                "Gross Dividend": "sum",
                "Tax": "sum",
                "Net Dividend": "sum",
                "Shares Bought": "sum",
            })
            annual_df["Cumulative Net Dividend"] = annual_df["Net Dividend"].cumsum()

    summary = {
        "Initial Amount": float(initial_amount),
        "Monthly Amount": float(monthly_amount),
        "Tax Rate %": float(tax_rate_pct),
        "Total External Invested": float(total_external_invested),
        "Final Portfolio Value": float(final_value),
        "Total Profit": float(total_profit),
        "Total Return %": float(total_return_pct),
        "CAGR %": float(cagr),
        "Final Shares": float(shares),
        "Cumulative Gross Dividend": float(cumulative_gross_dividend),
        "Cumulative Tax": float(cumulative_tax),
        "Cumulative Net Dividend": float(cumulative_net_dividend),
        "Current Estimated Annual Dividend Gross": float(current_estimated_annual_dividend_gross),
        "Current Estimated Annual Dividend Net": float(current_estimated_annual_dividend_net),
        "Yield on Cost Net %": float(yield_on_cost_net),
        "Current Yield Net %": float(current_yield_net),
        "Recent Annual Dividend Per Share": float(recent_annual_dividend_per_share),
        "Final Price": float(final_price),
    }

    return DividendReinvestResult(
        summary=summary,
        event_df=event_df,
        timeline_df=timeline_df,
        annual_df=annual_df,
    )
