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

# ZigZag swing threshold used to locate the prior high. 10% matches golden.py's
# default and gives a stable "직전 전고점" that ignores minor noise.
SCAN_THRESHOLD = 0.10

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
