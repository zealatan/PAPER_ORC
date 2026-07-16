"""
backtest_engine.py
==================
Trigger-based and dividend-focused backtest engines.

nearest_trade_date() and run_backtest() use the ZigZag engine to find
historically significant highs and simulate buy events when the trigger
level is hit. DO NOT replace ZigZag highs with close.max() here.

run_dividend_reinvest_backtest() is the full reinvestment simulation and
is re-exported here for a single import point. Its implementation lives in
dividend_reinvest.py and must not be changed.
"""
from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

import pandas as pd

from .zigzag_engine import (
    ZIGZAG_DEFAULT_THRESHOLD,
    find_alternating_high_low,
)
# Re-export so callers can import from backtest_engine directly
from .dividend_reinvest import run_dividend_reinvest_backtest  # noqa: F401


# ── Helpers ────────────────────────────────────────────────────────────────────

def nearest_trade_date(
    close: pd.Series,
    target_date: pd.Timestamp,
) -> Optional[pd.Timestamp]:
    """
    Return the first date in close.index that is >= target_date.
    Returns None if target_date is beyond the last available date.
    """
    idx = close.index[close.index >= pd.Timestamp(target_date)]
    if len(idx) == 0:
        return None
    return pd.Timestamp(idx[0])


def _first_trade_date_of_month(
    close: pd.Series, year: int, month: int
) -> Optional[pd.Timestamp]:
    return nearest_trade_date(close, pd.Timestamp(date(year, month, 1)))


# ── Annual dividend aggregation ────────────────────────────────────────────────

def calculate_annual_dividends(dividends: pd.Series) -> pd.DataFrame:
    """
    Aggregate a dividend series by calendar year.

    Returns a DataFrame with columns ['Year', 'Dividend per Share'].
    Returns an empty DataFrame (with those columns) if dividends is empty.
    """
    if dividends is None or dividends.empty:
        return pd.DataFrame(columns=["Year", "Dividend per Share"])
    dividends = dividends.copy()
    dividends.index = pd.to_datetime(dividends.index).tz_localize(None)
    annual = dividends.groupby(dividends.index.year).sum().reset_index()
    annual.columns = ["Year", "Dividend per Share"]
    return annual


# ── Trigger-based backtest ─────────────────────────────────────────────────────

def run_backtest(
    close: pd.Series,
    dividends: pd.Series,
    trigger_pct: float,
    threshold: float = ZIGZAG_DEFAULT_THRESHOLD,
) -> pd.DataFrame:
    """
    Simulate trigger-based buy events driven by ZigZag swing highs.

    For every ZigZag high detected by find_alternating_high_low():
      1. Compute trigger_price = high_price * (1 - trigger_pct / 100)
      2. Scan forward for the first close <= trigger_price
      3. If found, record a "Trigger Buy" event

    DO NOT substitute find_alternating_high_low() with close.max() or
    any rolling-high approach. The trigger logic is anchored to ZigZag
    swing highs, not the absolute period maximum.

    Returns a DataFrame with columns:
        Peak Date, Peak Price, Trigger Price,
        Buy Date, Buy Price, Drawdown at Buy %,
        Annual Div at Buy, Yield at Buy %
    """
    if close.empty:
        return pd.DataFrame()

    close = close.copy()
    close.index = pd.to_datetime(close.index).tz_localize(None)

    points = find_alternating_high_low(close, threshold)
    highs  = [(p.date, p.price) for p in points if p.point_type == "H"]

    annual_div_df = calculate_annual_dividends(dividends)

    rows: List[Dict] = []
    for h_date, h_price in highs:
        trigger_price  = h_price * (1.0 - trigger_pct / 100.0)
        close_after    = close[close.index > h_date]
        triggered      = close_after[close_after <= trigger_price]

        if triggered.empty:
            continue

        buy_date  = triggered.index[0]
        buy_price = float(triggered.iloc[0])
        drawdown  = (buy_price / h_price - 1.0) * 100.0 if h_price > 0 else 0.0

        buy_year    = buy_date.year
        year_row    = annual_div_df[annual_div_df["Year"] == buy_year]
        annual_div  = float(year_row["Dividend per Share"].iloc[0]) if not year_row.empty else 0.0
        yield_at_buy = (annual_div / buy_price * 100.0) if buy_price > 0 else 0.0

        rows.append({
            "Peak Date":        h_date,
            "Peak Price":       round(h_price, 4),
            "Trigger Price":    round(trigger_price, 4),
            "Buy Date":         buy_date,
            "Buy Price":        round(buy_price, 4),
            "Drawdown at Buy %":round(drawdown, 2),
            "Annual Div at Buy":round(annual_div, 4),
            "Yield at Buy %":   round(yield_at_buy, 2),
        })

    return pd.DataFrame(rows)


# ── Dividend-focused backtest ──────────────────────────────────────────────────

def run_dividend_backtest(
    close: pd.Series,
    dividends: pd.Series,
    trigger_pct: float = 10.0,
    threshold: float = ZIGZAG_DEFAULT_THRESHOLD,
) -> Dict:
    """
    Combine trigger-based buy events with dividend analysis.

    Returns a dict:
        trades          pd.DataFrame  — run_backtest() output
        annual_divs     pd.DataFrame  — yearly dividend totals
        total_triggers  int
        avg_yield_at_buy float        — mean yield at each trigger buy
    """
    trades     = run_backtest(close, dividends, trigger_pct, threshold)
    annual_div = calculate_annual_dividends(dividends)

    avg_yield = 0.0
    if not trades.empty and "Yield at Buy %" in trades.columns:
        avg_yield = float(trades["Yield at Buy %"].mean())

    return {
        "trades":         trades,
        "annual_divs":    annual_div,
        "total_triggers": len(trades),
        "avg_yield_at_buy": round(avg_yield, 2),
    }
