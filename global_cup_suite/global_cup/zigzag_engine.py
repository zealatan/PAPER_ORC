"""
zigzag_engine.py
================
ZigZag alternating high/low detection engine.

find_alternating_high_low() is the core trusted function.
All other functions in this module depend on it.

DO NOT replace find_alternating_high_low() with close.max(),
rolling max, or any simplified high-detection logic.
The alternating swing detection is intentional.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd

# ── Constants ──────────────────────────────────────────────────────────────────

ZIGZAG_DEFAULT_THRESHOLD = 0.05   # 5% minimum swing to qualify as a new pivot


# ── Core data type ─────────────────────────────────────────────────────────────

@dataclass
class ZigZagPoint:
    date: pd.Timestamp
    price: float
    point_type: str   # 'H' (swing high) or 'L' (swing low)

    def as_dict(self) -> Dict:
        return {"date": self.date, "price": self.price, "type": self.point_type}


# ── ZigZag detection ───────────────────────────────────────────────────────────

def find_alternating_high_low(
    close: pd.Series,
    threshold: float = ZIGZAG_DEFAULT_THRESHOLD,
) -> List[ZigZagPoint]:
    """
    Classic ZigZag algorithm.

    Scans the close series and records alternating swing highs (H) and swing
    lows (L). A new swing is confirmed only when price reverses by at least
    `threshold` fraction (e.g. 0.05 = 5%) from the current extreme.

    Key properties:
    - Points always alternate H, L, H, L, ... (never two H or two L in a row)
    - Each reversal must exceed `threshold` to qualify
    - The final point represents the most recent unconfirmed extreme (in-progress)
    - Returns [] for series shorter than 2 points

    DO NOT substitute with close.max(), rolling max, or period-high logic.
    """
    if close is None or len(close) < 2:
        return []

    prices = close.values.astype(float)
    dates  = close.index
    n      = len(prices)

    # ── Step 1: find initial direction ────────────────────────────────────────
    # Scan forward until we see a move of at least `threshold` in either direction.
    # The starting point becomes the first confirmed extreme (L if market goes up,
    # H if market goes down).

    points: List[ZigZagPoint] = []
    direction: Optional[str]  = None   # 'up' → tracking a new high
                                        # 'down' → tracking a new low

    # Index and price of the current unconfirmed extreme
    ext_idx   = 0
    ext_price = prices[0]
    ext_date  = dates[0]

    for i in range(1, n):
        p = float(prices[i])
        change = (p - ext_price) / ext_price

        if change >= threshold:
            # First significant move is upward → starting point was a low
            points.append(ZigZagPoint(date=pd.Timestamp(ext_date),
                                      price=ext_price, point_type="L"))
            ext_idx, ext_price, ext_date = i, p, dates[i]
            direction = "up"
            break

        elif change <= -threshold:
            # First significant move is downward → starting point was a high
            points.append(ZigZagPoint(date=pd.Timestamp(ext_date),
                                      price=ext_price, point_type="H"))
            ext_idx, ext_price, ext_date = i, p, dates[i]
            direction = "down"
            break

    if direction is None:
        # No qualifying move found (e.g. flat or near-flat series)
        # Return the single endpoint as a tentative high (series ended near start)
        final_price = float(prices[-1])
        final_date  = dates[-1]
        point_type  = "H" if final_price >= float(prices[0]) else "L"
        points.append(ZigZagPoint(date=pd.Timestamp(final_date),
                                  price=final_price, point_type=point_type))
        return points

    # ── Step 2: track alternating extremes ────────────────────────────────────
    for i in range(ext_idx + 1, n):
        p = float(prices[i])

        if direction == "up":
            if p >= ext_price:
                # Still moving up: update candidate high
                ext_idx, ext_price, ext_date = i, p, dates[i]
            else:
                pct_drop = (ext_price - p) / ext_price
                if pct_drop >= threshold:
                    # Confirmed high: record H, start tracking new low
                    points.append(ZigZagPoint(date=pd.Timestamp(ext_date),
                                              price=ext_price, point_type="H"))
                    ext_idx, ext_price, ext_date = i, p, dates[i]
                    direction = "down"

        else:  # direction == "down"
            if p <= ext_price:
                # Still moving down: update candidate low
                ext_idx, ext_price, ext_date = i, p, dates[i]
            else:
                pct_rise = (p - ext_price) / ext_price
                if pct_rise >= threshold:
                    # Confirmed low: record L, start tracking new high
                    points.append(ZigZagPoint(date=pd.Timestamp(ext_date),
                                              price=ext_price, point_type="L"))
                    ext_idx, ext_price, ext_date = i, p, dates[i]
                    direction = "up"

    # ── Step 3: append the last unconfirmed extreme ───────────────────────────
    # This is the in-progress swing (may still move further before reversing).
    candidate_type = "H" if direction == "up" else "L"
    candidate = ZigZagPoint(date=pd.Timestamp(ext_date),
                             price=ext_price, point_type=candidate_type)

    last = points[-1] if points else None
    if last is None or candidate.date > last.date or candidate.price != last.price:
        points.append(candidate)

    return points


# ── Drop bucket classifier ─────────────────────────────────────────────────────

def classify_drop_bucket(drawdown_pct: float) -> str:
    """
    Map a drawdown percentage (negative number) to a named severity bucket.

    drawdown_pct is expected to be <= 0.
    abs() is used so callers may pass positive or negative values.
    """
    drop = abs(drawdown_pct)
    if drop < 3.0:
        return "At High"
    elif drop < 10.0:
        return "Minor Pullback"
    elif drop < 20.0:
        return "Correction"
    elif drop < 30.0:
        return "Bear Territory"
    else:
        return "Deep Drawdown"


# ── Current-status classifier ──────────────────────────────────────────────────

def classify_current_status(drawdown_pct: float, trigger_pct: float) -> str:
    """
    Return a human-readable label for the current market state relative to the
    ZigZag reference high and the user-specified trigger threshold.
    """
    drop = abs(drawdown_pct)
    if drop < 1.0:
        return "At High"
    elif drop < trigger_pct:
        return "Watching"
    else:
        return "Trigger Hit"


# ── build_current_status ───────────────────────────────────────────────────────

def build_current_status(
    close: pd.Series,
    trigger_pct: float,
    threshold: float = ZIGZAG_DEFAULT_THRESHOLD,
) -> Dict:
    """
    Compute the current drawdown status using the ZigZag reference high.

    The reference high is the most recent confirmed ZigZag swing high.
    Falls back to close.max() only when no ZigZag highs have been detected yet
    (e.g. monotonic uptrend without any confirmed reversal).

    Returns a dict with:
        zigzag_points     list[ZigZagPoint]
        ref_high_price    float
        ref_high_date     pd.Timestamp
        ref_low_price     float
        ref_low_date      pd.Timestamp
        current_price     float
        current_date      pd.Timestamp
        drawdown_pct      float   (computed from ref_high_price)
        trigger_price     float
        trigger_hit       bool
        drop_bucket       str
        status_label      str
        high_count        int
        low_count         int
    """
    if close is None or close.empty:
        return {
            "zigzag_points": [], "ref_high_price": 0.0, "ref_high_date": None,
            "ref_low_price": 0.0, "ref_low_date": None, "current_price": 0.0,
            "current_date": None, "drawdown_pct": 0.0, "trigger_price": 0.0,
            "trigger_hit": False, "drop_bucket": "At High",
            "status_label": "At High", "high_count": 0, "low_count": 0,
        }

    points = find_alternating_high_low(close, threshold)

    highs = [p for p in points if p.point_type == "H"]
    lows  = [p for p in points if p.point_type == "L"]

    current_price = float(close.iloc[-1])
    current_date  = close.index[-1]

    # Reference high: most recent ZigZag high, fallback to period high
    if highs:
        ref_high = highs[-1]
        ref_high_price = ref_high.price
        ref_high_date  = ref_high.date
    else:
        ref_high_price = float(close.max())
        ref_high_date  = close.idxmax()

    # Reference low: most recent ZigZag low, fallback to period low
    if lows:
        ref_low = lows[-1]
        ref_low_price = ref_low.price
        ref_low_date  = ref_low.date
    else:
        ref_low_price = float(close.min())
        ref_low_date  = close.idxmin()

    drawdown_pct  = (current_price / ref_high_price - 1.0) * 100.0 if ref_high_price > 0 else 0.0
    trigger_price = ref_high_price * (1.0 - trigger_pct / 100.0)
    trigger_hit   = drawdown_pct <= -trigger_pct

    return {
        "zigzag_points":   points,
        "ref_high_price":  ref_high_price,
        "ref_high_date":   ref_high_date,
        "ref_low_price":   ref_low_price,
        "ref_low_date":    ref_low_date,
        "current_price":   current_price,
        "current_date":    current_date,
        "drawdown_pct":    drawdown_pct,
        "trigger_price":   trigger_price,
        "trigger_hit":     trigger_hit,
        "drop_bucket":     classify_drop_bucket(drawdown_pct),
        "status_label":    classify_current_status(drawdown_pct, trigger_pct),
        "high_count":      len(highs),
        "low_count":       len(lows),
    }


# ── build_drawdown_cycles ──────────────────────────────────────────────────────

def build_drawdown_cycles(
    close: pd.Series,
    threshold: float = ZIGZAG_DEFAULT_THRESHOLD,
) -> pd.DataFrame:
    """
    Return a DataFrame of all peak-to-trough cycles detected by the ZigZag engine.

    Columns: Peak Date, Peak Price, Trough Date, Trough Price,
             Drawdown %, Duration (days)

    Each row represents one complete cycle: a confirmed ZigZag high followed
    by the next confirmed ZigZag low.
    """
    points = find_alternating_high_low(close, threshold)
    highs  = [(p.date, p.price) for p in points if p.point_type == "H"]
    lows   = [(p.date, p.price) for p in points if p.point_type == "L"]

    rows = []
    for h_date, h_price in highs:
        subsequent = [(l_d, l_p) for l_d, l_p in lows if l_d > h_date]
        if not subsequent:
            continue
        l_date, l_price = subsequent[0]
        drawdown = (l_price / h_price - 1.0) * 100.0 if h_price > 0 else 0.0
        rows.append({
            "Peak Date":      h_date,
            "Peak Price":     round(h_price, 4),
            "Trough Date":    l_date,
            "Trough Price":   round(l_price, 4),
            "Drawdown %":     round(drawdown, 2),
            "Duration (days)":(l_date - h_date).days,
        })

    return pd.DataFrame(rows)
