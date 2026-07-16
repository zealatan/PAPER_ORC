from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd


@dataclass
class ScoreResult:
    score: float           # 0–100 composite
    rank_label: str        # Gold / Silver / Bronze / Watchlist
    drawdown_score: float
    yield_score: float
    momentum_score: float
    consistency_score: float


# ── Component scorers ──────────────────────────────────────────────────────────

def _drawdown_score(drawdown_pct: float) -> float:
    """Larger pullback from high → more attractive. 0–100."""
    return min(100.0, abs(drawdown_pct) * 3.5)


def _yield_score(dividend_yield: float) -> float:
    """Higher trailing dividend yield → more attractive. 0–100."""
    return min(100.0, dividend_yield * 15.0)


def _momentum_score(close: pd.Series, months: int = 3) -> float:
    """
    Contrarian view: recent pullback = more attractive.
    Returns 0–100; score is higher when recent return is negative.
    """
    if close.empty or len(close) < 20:
        return 50.0
    cutoff = close.index[-1] - pd.Timedelta(days=months * 30)
    past = close[close.index <= cutoff]
    if past.empty:
        return 50.0
    past_price = float(past.iloc[-1])
    current_price = float(close.iloc[-1])
    if past_price <= 0:
        return 50.0
    momentum_pct = (current_price / past_price - 1.0) * 100.0
    # -20% momentum → 90 pts; 0% → 50 pts; +20% → 10 pts
    return max(0.0, min(100.0, 50.0 - momentum_pct * 2.0))


def _consistency_score(annual_dividend_df: pd.DataFrame, years_in_period: float) -> float:
    """Fraction of years with a positive dividend payment. 0–100."""
    if annual_dividend_df.empty or years_in_period < 1:
        return 0.0
    years_with_div = len(annual_dividend_df[annual_dividend_df["Dividend per Share"] > 0])
    total_years = max(1, round(years_in_period))
    return min(100.0, (years_with_div / total_years) * 100.0)


# ── Composite scorer ───────────────────────────────────────────────────────────

def calculate_score(
    drawdown_pct: float,
    dividend_yield: float,
    close: pd.Series,
    annual_dividend_df: pd.DataFrame,
    years_in_period: float = 5.0,
) -> ScoreResult:
    """
    Weights:
      35% drawdown attractiveness
      30% dividend yield
      20% momentum (contrarian)
      15% dividend consistency
    """
    d = _drawdown_score(drawdown_pct)
    y = _yield_score(dividend_yield)
    m = _momentum_score(close)
    c = _consistency_score(annual_dividend_df, years_in_period)

    total = 0.35 * d + 0.30 * y + 0.20 * m + 0.15 * c

    if total >= 80:
        rank = "Gold"
    elif total >= 65:
        rank = "Silver"
    elif total >= 50:
        rank = "Bronze"
    else:
        rank = "Watchlist"

    return ScoreResult(
        score=round(total, 1),
        rank_label=rank,
        drawdown_score=round(d, 1),
        yield_score=round(y, 1),
        momentum_score=round(m, 1),
        consistency_score=round(c, 1),
    )


# ── Rank cosmetics ─────────────────────────────────────────────────────────────

_RANK_COLORS: Dict[str, str] = {
    "Gold":      "#FFD700",
    "Silver":    "#C0C0C0",
    "Bronze":    "#CD7F32",
    "Watchlist": "#8a8f7a",
}

_RANK_MEDALS: Dict[str, str] = {
    "Gold":      "🥇",
    "Silver":    "🥈",
    "Bronze":    "🥉",
    "Watchlist": "👁",
}


def get_rank_color(rank_label: str) -> str:
    return _RANK_COLORS.get(rank_label, "#8a8f7a")


def get_rank_medal(rank_label: str) -> str:
    return _RANK_MEDALS.get(rank_label, "")
