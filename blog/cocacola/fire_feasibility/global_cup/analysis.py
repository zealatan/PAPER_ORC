from __future__ import annotations

from typing import Optional

import pandas as pd

from .market_config import AnalysisResult, UserInput
from .data_loader import download_price, download_dividends, get_close_series
from .golden_engine import (
    find_alternating_high_low,
    build_current_status as _golden_build_current_status,
    run_trigger_backtest_df,
)


def fmt_money(x: float) -> str:
    if x is None or pd.isna(x):
        return "-"
    return f"{x:,.0f}" if abs(x) >= 100 else f"{x:,.2f}"


def fmt_pct(x: float) -> str:
    if x is None or pd.isna(x):
        return "-"
    return f"{x:.2f}%"


def annual_dividend_dataframe(dividends: pd.Series) -> pd.DataFrame:
    if dividends.empty:
        return pd.DataFrame(columns=["Year", "Dividend per Share"])
    annual = dividends.groupby(dividends.index.year).sum().reset_index()
    annual.columns = ["Year", "Dividend per Share"]
    return annual


def run_analysis(inp: UserInput) -> Optional[AnalysisResult]:
    price_df = download_price(inp.ticker, inp.start_date, inp.end_date)
    if price_df.empty:
        return None

    close = get_close_series(price_df)
    if close.empty:
        return None

    dividends = download_dividends(inp.ticker, inp.start_date, inp.end_date)

    # ── Legacy fields: period-high based (preserved for validate_engine.py) ────
    current_date  = close.index[-1]
    current_price = float(close.iloc[-1])
    high_date     = close.idxmax()
    high_price    = float(close.max())
    drawdown_pct  = (current_price / high_price - 1.0) * 100.0 if high_price > 0 else 0.0
    trigger_price = high_price * (1.0 - inp.trigger_pct / 100.0)
    trigger_hit   = drawdown_pct <= -inp.trigger_pct

    annual_df = annual_dividend_dataframe(dividends)

    if dividends.empty:
        ttm_dividend          = 0.0
        dividend_yield        = 0.0
        latest_dividend_year  = "-"
        latest_annual_dividend = 0.0
    else:
        ttm_start = current_date - pd.Timedelta(days=365)
        ttm_dividend   = float(dividends[dividends.index >= ttm_start].sum())
        dividend_yield = (ttm_dividend / current_price * 100.0) if current_price > 0 else 0.0

        if annual_df.empty:
            latest_dividend_year   = "-"
            latest_annual_dividend = 0.0
        else:
            latest_dividend_year   = str(int(annual_df["Year"].iloc[-1]))
            latest_annual_dividend = float(annual_df["Dividend per Share"].iloc[-1])

    # ── Golden engine fields ─────────────────────────────────────────────────────
    threshold = inp.trigger_pct / 100.0
    highs, lows = find_alternating_high_low(close, threshold=threshold)

    gcs = _golden_build_current_status(
        close, inp.ticker, inp.ticker, "App", threshold=threshold
    )

    if gcs is not None:
        ref_high_price   = gcs["_ref_high_price"]
        ref_high_date    = gcs["_ref_high_date"]
        ref_low_price    = gcs["_ref_low_price"]
        ref_low_date     = gcs["_ref_low_date"]
        zz_drawdown_pct  = gcs["_change_pct"]
        zz_trigger_price = ref_high_price * (1.0 - inp.trigger_pct / 100.0)
        zz_trigger_hit   = zz_drawdown_pct <= -inp.trigger_pct
        drop_bucket_val  = gcs["하락 구간"] or "At High"
        abs_dd = abs(zz_drawdown_pct)
        if abs_dd < 1.0:
            status_label_val = "At High"
        elif zz_trigger_hit:
            status_label_val = "Trigger Hit"
        else:
            status_label_val = "Watching"
    else:
        ref_high_price   = float(close.max())
        ref_high_date    = close.idxmax()
        ref_low_price    = float(close.min())
        ref_low_date     = close.idxmin()
        zz_drawdown_pct  = drawdown_pct
        zz_trigger_price = trigger_price
        zz_trigger_hit   = trigger_hit
        drop_bucket_val  = "At High"
        status_label_val = "At High"

    bt = run_trigger_backtest_df(close, inp.trigger_pct)

    return AnalysisResult(
        current_date=current_date,
        current_price=current_price,
        high_date=high_date,
        high_price=high_price,
        drawdown_pct=drawdown_pct,
        trigger_price=trigger_price,
        trigger_hit=trigger_hit,
        ttm_dividend=ttm_dividend,
        dividend_yield=dividend_yield,
        latest_dividend_year=latest_dividend_year,
        latest_annual_dividend=latest_annual_dividend,
        annual_dividend_df=annual_df,
        price_df=price_df,
        close=close,
        dividends=dividends,
        # Golden engine fields
        zigzag_points=(highs, lows),
        zigzag_ref_high_price=ref_high_price,
        zigzag_ref_high_date=ref_high_date,
        zigzag_ref_low_price=ref_low_price,
        zigzag_ref_low_date=ref_low_date,
        zigzag_drawdown_pct=zz_drawdown_pct,
        zigzag_trigger_price=zz_trigger_price,
        zigzag_trigger_hit=zz_trigger_hit,
        drop_bucket=drop_bucket_val,
        status_label=status_label_val,
        high_count=len(highs),
        low_count=len(lows),
        backtest_df=bt if not bt.empty else None,
    )
