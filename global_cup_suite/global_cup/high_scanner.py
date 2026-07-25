"""
high_scanner.py
===============
Scan every ticker in a selected market for its drawdown from the most recent
"직전 전고점" (the immediately preceding swing high) and bucket the results by
severity (20% / 30% / 50% down).

The reference high is computed by golden_engine.build_current_status(), which
defines it as the maximum price *after the most recent ZigZag low* — i.e. the
peak of the current downswing, exactly matching "바로 직전 전고점".

This module is pure of Streamlit UI; it only reuses the cached download_price().
"""
from __future__ import annotations

from datetime import date
from typing import Callable, Dict, List, Optional

import pandas as pd

from .data_loader import download_price, get_close_series
from .golden_engine import build_current_status

# ZigZag swing threshold used to locate the prior high. Raised 10%→15% because a
# single ~10% dead-cat bounce would register a fresh swing low and drag the
# "직전 전고점" down onto that bounce peak, understating the real drawdown from the
# true high (e.g. 삼성전자 2026-07: -18.6% off a 7/6 bounce vs -28.6% off the real
# 6/18 high). 15% ignores those minor rebounds and anchors on the meaningful prior
# swing high. (build_current_status in golden_engine is unaffected — it takes the
# threshold as a param and other pages still call it with the 10% default.)
SCAN_THRESHOLD = 0.15

# Output column order (raw numeric values; formatting happens in the UI layer).
SCAN_COLUMNS = [
    "label", "ticker", "high_date", "high_price",
    "current_price", "current_date", "drawdown_pct",
]


def scan_ticker(
    label: str,
    ticker: str,
    start_date: date,
    end_date: date,
    threshold: float = SCAN_THRESHOLD,
) -> Optional[Dict]:
    """Return one drawdown row for a single ticker, or None if unavailable.

    drawdown_pct is a negative number (e.g. -32.4 means 32.4% below the prior high).
    """
    try:
        price_df = download_price(ticker, start_date, end_date)
    except Exception:
        return None
    if price_df is None or price_df.empty:
        return None

    close = get_close_series(price_df)
    if close.empty or len(close) < 3:
        return None

    gcs = build_current_status(close, label, ticker, "Scan", threshold=threshold)
    if gcs is None:
        return None

    return {
        "label":         label,
        "ticker":        ticker,
        "high_date":     gcs["_ref_high_date"],
        "high_price":    float(gcs["_ref_high_price"]),
        "current_price": float(gcs["_current_price"]),
        "current_date":  gcs["_current_date"],
        "drawdown_pct":  float(gcs["_change_pct"]),   # negative
    }


def scan_market(
    tickers: Dict[str, str],
    start_date: date,
    end_date: date,
    threshold: float = SCAN_THRESHOLD,
    progress_cb: Optional[Callable[[int, int, str], None]] = None,
) -> pd.DataFrame:
    """Scan every {label: ticker} in a market and return a raw DataFrame.

    Columns: label, ticker, high_date, high_price, current_price,
             current_date, drawdown_pct
    Rows are sorted by drawdown_pct ascending (deepest drop first).
    progress_cb(done, total, label) is invoked after each ticker (optional).
    """
    rows: List[Dict] = []
    items = list(tickers.items())
    total = len(items)

    for i, (label, ticker) in enumerate(items, start=1):
        row = scan_ticker(label, ticker, start_date, end_date, threshold)
        if row is not None:
            rows.append(row)
        if progress_cb is not None:
            progress_cb(i, total, label)

    if not rows:
        return pd.DataFrame(columns=SCAN_COLUMNS)

    df = pd.DataFrame(rows, columns=SCAN_COLUMNS)
    return df.sort_values("drawdown_pct").reset_index(drop=True)


def filter_by_min_drop(df: pd.DataFrame, min_drop_pct: float) -> pd.DataFrame:
    """Rows whose drawdown is at least `min_drop_pct` percent below the prior high.

    Cumulative / "이상" semantics: a stock down 55% appears in the 20%, 30% and
    50% buckets alike.
    """
    if df is None or df.empty:
        return df if df is not None else pd.DataFrame(columns=SCAN_COLUMNS)
    return df[df["drawdown_pct"] <= -abs(min_drop_pct)].reset_index(drop=True)


# ── PERIOD RETURN side (YTD / N-year window returns) ────────────────────────────
# Independent of ZigZag: simple pct change from the first close on/after
# `period_start` to the latest close. Tickers whose history does not reach back to
# period_start (e.g. a recent IPO for a 1-year window) are skipped so they cannot
# pollute the ranking with a partial-period return.

SCAN_COLUMNS_RETURN = [
    "label", "ticker", "base_date", "base_price",
    "current_price", "current_date", "return_pct",
]


def scan_ticker_return(
    label: str,
    ticker: str,
    start_date: date,
    end_date: date,
    period_start: date,
    coverage_tol_days: int = 7,
) -> Optional[Dict]:
    """Return one period-return row for a single ticker, or None.

    return_pct = pct change from the first close on/after `period_start` to the
    latest close (positive when up). Returns None if the ticker has no data
    covering `period_start` within `coverage_tol_days` (keeps fixed-window
    rankings honest — no partial-history IPOs).
    """
    try:
        price_df = download_price(ticker, start_date, end_date)
    except Exception:
        return None
    if price_df is None or price_df.empty:
        return None

    close = get_close_series(price_df).dropna()
    if close.empty or len(close) < 3:
        return None

    ps = pd.Timestamp(period_start)
    base_slice = close[close.index >= ps]
    if base_slice.empty:
        return None

    base_date = base_slice.index[0]
    # Coverage guard: the first close on/after period_start must be within
    # coverage_tol_days of it (i.e. the ticker actually traded back then).
    if (base_date - ps).days > coverage_tol_days:
        return None

    base_price = float(base_slice.iloc[0])
    if base_price <= 0:
        return None

    current_price = float(close.iloc[-1])
    current_date = close.index[-1]
    return_pct = (current_price / base_price - 1.0) * 100.0

    return {
        "label":         label,
        "ticker":        ticker,
        "base_date":     base_date,
        "base_price":    base_price,
        "current_price": current_price,
        "current_date":  current_date,
        "return_pct":    return_pct,
    }


def scan_market_return(
    tickers: Dict[str, str],
    start_date: date,
    end_date: date,
    period_start: date,
    coverage_tol_days: int = 7,
    progress_cb: Optional[Callable[[int, int, str], None]] = None,
) -> pd.DataFrame:
    """Scan every {label: ticker} and return period-return rows.

    Columns: label, ticker, base_date, base_price, current_price,
             current_date, return_pct
    Rows are sorted by return_pct descending (biggest gainer first).
    `period_start` defines the window (e.g. date(y,1,1) for YTD, or end - 1yr).
    """
    rows: List[Dict] = []
    items = list(tickers.items())
    total = len(items)

    for i, (label, ticker) in enumerate(items, start=1):
        row = scan_ticker_return(
            label, ticker, start_date, end_date, period_start, coverage_tol_days)
        if row is not None:
            rows.append(row)
        if progress_cb is not None:
            progress_cb(i, total, label)

    if not rows:
        return pd.DataFrame(columns=SCAN_COLUMNS_RETURN)

    df = pd.DataFrame(rows, columns=SCAN_COLUMNS_RETURN)
    return df.sort_values("return_pct", ascending=False).reset_index(drop=True)


# ── BREAKOUT side (weekly-fresh new-high trigger + long-term return payload) ─────
# The mirror of the drawdown series in *spirit*, not in metric: a stock qualifies
# only if it set a NEW HIGH this week (fresh weekly trigger — the ranking churns
# every week as different names break out), and it is ranked by its long-term
# return (the dramatic "+982%" payload). This solves the "period-return is static"
# problem: freshness comes from the trigger, magnitude from the payload.

SCAN_COLUMNS_BREAKOUT = [
    "label", "ticker", "high_date", "high_price",
    "current_price", "current_date",
    "base_date", "base_price", "return_pct",
]


def scan_ticker_breakout(
    label: str,
    ticker: str,
    start_date: date,
    end_date: date,
    period_start: date,
    high_lookback_days: Optional[int] = 252,
    fresh_days: int = 5,
    coverage_tol_days: int = 7,
) -> Optional[Dict]:
    """Return one breakout row, or None.

    Qualifies only if the ticker's highest close over the last `high_lookback_days`
    (None = all-time) occurred within the last `fresh_days` trading days — i.e. it
    set a fresh 52-week (or all-time) high *this week*. `return_pct` is the payload:
    pct change from the first close on/after `period_start` to now. Returns None if
    not a fresh high, or if history does not cover `period_start` (keeps the
    long-term payload honest — no partial-history IPOs).
    """
    try:
        price_df = download_price(ticker, start_date, end_date)
    except Exception:
        return None
    if price_df is None or price_df.empty:
        return None

    close = get_close_series(price_df).dropna()
    if close.empty or len(close) < max(fresh_days + 1, 3):
        return None

    # ── fresh-high trigger ────────────────────────────────────────────────────
    window = close.tail(high_lookback_days) if high_lookback_days else close
    high_date = window.idxmax()
    high_price = float(window.max())
    fresh_cut = close.index[-fresh_days]
    if high_date < fresh_cut:
        return None   # highest price in the window is not from this week → skip

    # ── long-term return payload (with coverage guard) ────────────────────────
    ps = pd.Timestamp(period_start)
    base_slice = close[close.index >= ps]
    if base_slice.empty:
        return None
    base_date = base_slice.index[0]
    if (base_date - ps).days > coverage_tol_days:
        return None   # not enough history for the fixed window
    base_price = float(base_slice.iloc[0])
    if base_price <= 0:
        return None

    current_price = float(close.iloc[-1])
    current_date = close.index[-1]
    return_pct = (current_price / base_price - 1.0) * 100.0

    return {
        "label":         label,
        "ticker":        ticker,
        "high_date":     high_date,
        "high_price":    high_price,
        "current_price": current_price,
        "current_date":  current_date,
        "base_date":     base_date,
        "base_price":    base_price,
        "return_pct":    return_pct,
    }


def scan_market_breakout(
    tickers: Dict[str, str],
    start_date: date,
    end_date: date,
    period_start: date,
    high_lookback_days: Optional[int] = 252,
    fresh_days: int = 5,
    coverage_tol_days: int = 7,
    progress_cb: Optional[Callable[[int, int, str], None]] = None,
) -> pd.DataFrame:
    """Scan a market for stocks that set a fresh high this week, ranked by their
    long-term (`period_start`) return descending.

    Columns: label, ticker, high_date, high_price, current_price, current_date,
             base_date, base_price, return_pct
    """
    rows: List[Dict] = []
    items = list(tickers.items())
    total = len(items)

    for i, (label, ticker) in enumerate(items, start=1):
        row = scan_ticker_breakout(
            label, ticker, start_date, end_date, period_start,
            high_lookback_days, fresh_days, coverage_tol_days)
        if row is not None:
            rows.append(row)
        if progress_cb is not None:
            progress_cb(i, total, label)

    if not rows:
        return pd.DataFrame(columns=SCAN_COLUMNS_BREAKOUT)

    df = pd.DataFrame(rows, columns=SCAN_COLUMNS_BREAKOUT)
    return df.sort_values("return_pct", ascending=False).reset_index(drop=True)
