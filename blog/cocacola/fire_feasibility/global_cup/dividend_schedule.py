"""
Dividend frequency classification & schedule extraction.

For the FIRE tool (USD basis) the *timing* of dividend payments matters: a
monthly payer feeds withdrawals differently than a quarterly or annual one.
This module classifies a stock's payout cadence from its yfinance dividend
history and extracts a clean payment schedule.

Design notes (validated against real tickers):
  - Frequency is decided from per-CALENDAR-YEAR payment counts (median of
    complete years), NOT from months-seen or raw median gap — companies shift
    pay months year to year, which scatters `months` but not the yearly count.
  - Special/supplemental dividends (e.g. MAIN) inflate the count above the
    regular cadence; we snap to the nearest canonical frequency and flag the
    stock as having irregular/special payments so downstream code can treat
    the base cadence and the extras separately.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pandas as pd

# Canonical payout frequencies: payments-per-year -> label
CANONICAL: Dict[int, str] = {
    12: "monthly",     # 월배당
    4:  "quarterly",   # 분기배당
    2:  "semiannual",  # 반기배당
    1:  "annual",      # 연배당
}
_CANON_PPY = sorted(CANONICAL)  # [1, 2, 4, 12]


@dataclass
class DividendSchedule:
    frequency: str                 # monthly|quarterly|semiannual|annual|irregular|none
    payments_per_year: int         # canonical cadence (12/4/2/1), 0 if none
    observed_per_year: float       # actual recent avg incl. specials
    median_interval_days: float    # median gap between consecutive ex-dates
    has_specials: bool             # extra payments beyond the canonical cadence
    typical_months: List[int]      # ex-div months of the *regular* cadence
    n_recent: int                  # payments counted in the lookback window
    first_date: Optional[pd.Timestamp] = None
    last_date: Optional[pd.Timestamp] = None
    per_year_counts: Dict[int, int] = field(default_factory=dict)  # year -> count


def _snap_ppy(observed: float) -> int:
    """Snap an observed payments/year to the nearest canonical cadence.

    Nearest in log-space so 3 lands on 4 (quarterly) not 2, and 16 lands on
    12 (monthly). Anything >= ~1.5x above monthly is still monthly (specials).
    """
    import math
    logs = {p: abs(math.log(observed) - math.log(p)) for p in _CANON_PPY}
    return min(logs, key=logs.get)


def classify(div: pd.Series, lookback_years: int = 5) -> DividendSchedule:
    """Classify dividend cadence from an ex-date -> amount Series."""
    if div is None or div.empty:
        return DividendSchedule("none", 0, 0.0, float("nan"), False, [], 0)

    div = div.copy()
    div.index = pd.to_datetime(div.index).tz_localize(None)
    div = div[div > 0].sort_index()
    if div.empty:
        return DividendSchedule("none", 0, 0.0, float("nan"), False, [], 0)

    last = div.index.max()
    window = div[div.index >= (last - pd.Timedelta(days=int(lookback_years * 365.25 + 5)))]
    if len(window) < 2:
        window = div  # short history: use everything

    # per-calendar-year counts; prefer COMPLETE years for the cadence estimate
    per_year = window.groupby(window.index.year).size().to_dict()
    years_sorted = sorted(per_year)
    complete_years = years_sorted[:-1] if len(years_sorted) > 1 else years_sorted
    counts = [per_year[y] for y in complete_years] or [per_year[y] for y in years_sorted]
    base_count = float(pd.Series(counts).median())

    gaps = window.index.to_series().diff().dt.days.dropna()
    median_gap = float(gaps.median()) if len(gaps) else float("nan")

    span_days = max((window.index.max() - window.index.min()).days, 1)
    observed_ppy = len(window) / (span_days / 365.25)

    ppy = _snap_ppy(base_count if base_count > 0 else observed_ppy)
    frequency = CANONICAL[ppy]

    # specials: actual payout rate runs >=20% above the canonical cadence
    # (catches MAIN's monthly + supplemental; ignores 1-off timing drift and
    # a single special averaged over the window)
    has_specials = bool(observed_ppy >= ppy * 1.2) if ppy else False

    # typical months of the regular cadence: most common ex-div months,
    # taking the `ppy` most frequent ones
    month_counts = window.index.month.value_counts()
    typical_months = sorted(month_counts.index[:ppy].tolist()) if ppy else []

    return DividendSchedule(
        frequency="irregular" if (has_specials and ppy < 12) else frequency,
        payments_per_year=ppy,
        observed_per_year=round(observed_ppy, 2),
        median_interval_days=round(median_gap, 1) if median_gap == median_gap else median_gap,
        has_specials=has_specials,
        typical_months=typical_months,
        n_recent=len(window),
        first_date=div.index.min(),
        last_date=div.index.max(),
        per_year_counts=per_year,
    )
