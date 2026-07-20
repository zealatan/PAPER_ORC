"""
validate_engine.py
==================
Compare the original monolithic engine against the refactored modular engine.

Run from global_cup_refactored/:
    python validate_engine.py

Requirements: yfinance, pandas  (same deps as the main app)
"""

from __future__ import annotations

import sys
import math
from datetime import date, timedelta
from typing import Optional, Dict, Any

import pandas as pd
import yfinance as yf

# ── 0. Test configuration ─────────────────────────────────────────────────────

TEST_TICKERS = ["VOO", "SCHD", "JEPI", "360750.KS", "441680.KS"]
START_DATE   = date(2020, 1, 1)
END_DATE     = date(2024, 12, 31)
TRIGGER_PCT  = 10.0
INITIAL_AMT  = 10_000.0
MONTHLY_AMT  = 0.0
TAX_RATE_PCT = 15.0
TOLERANCE    = 1e-6   # relative tolerance for float comparisons

# ── 1. Original engine — copied verbatim from global_cup_dividend_reinvest_ported.py
#       (top-level Streamlit calls in that file prevent direct import)
# ─────────────────────────────────────────────────────────────────────────────


def _orig_download_price(ticker: str, start: date, end: date) -> pd.DataFrame:
    df = yf.download(
        ticker,
        start=start,
        end=end + timedelta(days=1),
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    if df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        if "Close" in df.columns.get_level_values(0):
            df.columns = df.columns.get_level_values(0)
        elif "Close" in df.columns.get_level_values(-1):
            df.columns = df.columns.get_level_values(-1)
        else:
            df.columns = df.columns.get_level_values(0)
    df = df.loc[:, ~df.columns.duplicated()].copy()
    if "Close" not in df.columns:
        return pd.DataFrame()
    df = df.dropna(subset=["Close"]).copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df


def _orig_download_dividends(ticker: str, start: date, end: date) -> pd.Series:
    try:
        div = yf.Ticker(ticker).dividends
    except Exception:
        return pd.Series(dtype=float)
    if div is None or div.empty:
        return pd.Series(dtype=float)
    div.index = pd.to_datetime(div.index).tz_localize(None)
    div = div[
        (div.index >= pd.Timestamp(start)) & (div.index <= pd.Timestamp(end))
    ]
    return div.astype(float)


def _orig_get_close(price_df: pd.DataFrame) -> pd.Series:
    if price_df.empty or "Close" not in price_df.columns:
        return pd.Series(dtype=float)
    close = price_df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = pd.to_numeric(close, errors="coerce").dropna()
    close.index = pd.to_datetime(close.index).tz_localize(None)
    return close


def _orig_annual_dividend_df(dividends: pd.Series) -> pd.DataFrame:
    if dividends.empty:
        return pd.DataFrame(columns=["Year", "Dividend per Share"])
    annual = dividends.groupby(dividends.index.year).sum().reset_index()
    annual.columns = ["Year", "Dividend per Share"]
    return annual


def _orig_run_analysis(ticker: str, start: date, end: date, trigger_pct: float) -> Optional[Dict]:
    price_df = _orig_download_price(ticker, start, end)
    if price_df.empty:
        return None
    close = _orig_get_close(price_df)
    if close.empty:
        return None
    dividends = _orig_download_dividends(ticker, start, end)
    current_date  = close.index[-1]
    current_price = float(close.iloc[-1])
    high_date     = close.idxmax()
    high_price    = float(close.max())
    drawdown_pct  = (current_price / high_price - 1.0) * 100.0 if high_price > 0 else 0.0
    trigger_price = high_price * (1.0 - trigger_pct / 100.0)
    trigger_hit   = drawdown_pct <= -trigger_pct
    annual_df     = _orig_annual_dividend_df(dividends)
    if dividends.empty:
        ttm_dividend   = 0.0
        dividend_yield = 0.0
    else:
        ttm_start      = current_date - pd.Timedelta(days=365)
        ttm_dividend   = float(dividends[dividends.index >= ttm_start].sum())
        dividend_yield = (ttm_dividend / current_price * 100.0) if current_price > 0 else 0.0
    return {
        "current_price": current_price,
        "high_price":    high_price,
        "drawdown_pct":  drawdown_pct,
        "trigger_price": trigger_price,
        "trigger_hit":   trigger_hit,
        "ttm_dividend":  ttm_dividend,
        "dividend_yield":dividend_yield,
        "close":         close,
        "dividends":     dividends,
    }


def _orig_next_trade_date(close, target):
    idx = close.index[close.index >= pd.Timestamp(target)]
    return pd.Timestamp(idx[0]) if len(idx) > 0 else None


def _orig_first_trade_date_of_month(close, year, month):
    return _orig_next_trade_date(close, pd.Timestamp(date(year, month, 1)))


def _orig_run_reinvest(
    close: pd.Series,
    dividends: pd.Series,
    initial: float,
    monthly: float,
    tax_pct: float,
) -> Optional[Dict]:
    close = close.dropna().copy()
    if close.empty or initial <= 0:
        return None
    close.index = pd.to_datetime(close.index).tz_localize(None)
    dividends = dividends.copy()
    if not dividends.empty:
        dividends.index = pd.to_datetime(dividends.index).tz_localize(None)
        dividends = dividends[
            (dividends.index >= close.index[0]) & (dividends.index <= close.index[-1])
        ]
        dividends = dividends.sort_index().astype(float)
    tax_rate = max(0.0, min(100.0, float(tax_pct))) / 100.0
    monthly_buy_dates = set()
    months = sorted(set((d.year, d.month) for d in close.index))
    for y, m in months:
        d = _orig_first_trade_date_of_month(close, y, m)
        if d is not None and d != close.index[0] and monthly > 0:
            monthly_buy_dates.add(d)
    div_by_trade: Dict = {}
    for div_date, div_ps in dividends.items():
        td = _orig_next_trade_date(close, pd.Timestamp(div_date))
        if td is None:
            continue
        div_by_trade.setdefault(td, []).append((pd.Timestamp(div_date), float(div_ps)))
    shares = 0.0
    total_ext = 0.0
    cum_gross = 0.0
    cum_tax   = 0.0
    cum_net   = 0.0
    for d, price in close.items():
        d = pd.Timestamp(d)
        price = float(price)
        if d == close.index[0]:
            shares += initial / price if price > 0 else 0.0
            total_ext += initial
        if d in monthly_buy_dates:
            shares += monthly / price if price > 0 else 0.0
            total_ext += monthly
        for _, div_ps in div_by_trade.get(d, []):
            if shares <= 0 or div_ps <= 0:
                continue
            gross = shares * div_ps
            tax   = gross * tax_rate
            net   = gross - tax
            shares += net / price if price > 0 else 0.0
            cum_gross += gross
            cum_tax   += tax
            cum_net   += net
    final_price = float(close.iloc[-1])
    final_value = shares * final_price
    days = max((close.index[-1] - close.index[0]).days, 1)
    years = days / 365.25
    cagr  = ((final_value / total_ext) ** (1.0 / years) - 1.0) * 100.0 if total_ext > 0 and final_value > 0 else 0.0
    return {
        "final_value":   final_value,
        "total_ext":     total_ext,
        "final_shares":  shares,
        "cum_gross":     cum_gross,
        "cum_tax":       cum_tax,
        "cum_net":       cum_net,
        "cagr":          cagr,
    }


# ── 2. Refactored engine — import from global_cup package ────────────────────

sys.path.insert(0, ".")   # ensure global_cup/ is importable from this directory

from global_cup.data_loader import download_price, download_dividends, get_close_series
from global_cup.analysis    import run_analysis, annual_dividend_dataframe
from global_cup.dividend_reinvest import run_dividend_reinvest_backtest
from global_cup.market_config import UserInput


def _ref_run_analysis(ticker: str, start: date, end: date, trigger_pct: float) -> Optional[Dict]:
    inp = UserInput(
        market_key="United States",
        ticker_label=ticker,
        ticker=ticker,
        trigger_pct=trigger_pct,
        start_date=start,
        end_date=end,
    )
    res = run_analysis(inp)
    if res is None:
        return None
    return {
        "current_price": res.current_price,
        "high_price":    res.high_price,
        "drawdown_pct":  res.drawdown_pct,
        "trigger_price": res.trigger_price,
        "trigger_hit":   res.trigger_hit,
        "ttm_dividend":  res.ttm_dividend,
        "dividend_yield":res.dividend_yield,
        "close":         res.close,
        "dividends":     res.dividends,
    }


def _ref_run_reinvest(
    close: pd.Series,
    dividends: pd.Series,
    initial: float,
    monthly: float,
    tax_pct: float,
) -> Optional[Dict]:
    res = run_dividend_reinvest_backtest(
        close=close,
        dividends=dividends,
        initial_amount=initial,
        monthly_amount=monthly,
        tax_rate_pct=tax_pct,
    )
    if res is None:
        return None
    s = res.summary
    return {
        "final_value":  s["Final Portfolio Value"],
        "total_ext":    s["Total External Invested"],
        "final_shares": s["Final Shares"],
        "cum_gross":    s["Cumulative Gross Dividend"],
        "cum_tax":      s["Cumulative Tax"],
        "cum_net":      s["Cumulative Net Dividend"],
        "cagr":         s["CAGR %"],
    }


# ── 3. Comparison helpers ─────────────────────────────────────────────────────

def _near(a: float, b: float, tol: float = TOLERANCE) -> bool:
    if a == b:
        return True
    denom = max(abs(a), abs(b), 1e-12)
    return abs(a - b) / denom < tol


def _check(label: str, orig, ref, results: list[dict]) -> None:
    if isinstance(orig, bool):
        ok = (orig == ref)
    elif isinstance(orig, (int, float)):
        ok = _near(float(orig), float(ref))
    else:
        ok = (orig == ref)
    status = "PASS" if ok else "FAIL"
    results.append({"label": label, "status": status, "orig": orig, "ref": ref})


# ── 4. Main test loop ─────────────────────────────────────────────────────────

def main() -> None:
    all_results: list[dict] = []
    ticker_summaries: dict[str, str] = {}

    for ticker in TEST_TICKERS:
        print(f"\n{'='*60}")
        print(f"  Ticker: {ticker}")
        print(f"  Period: {START_DATE} → {END_DATE}")
        print(f"{'='*60}")

        ticker_results: list[dict] = []

        orig = _orig_run_analysis(ticker, START_DATE, END_DATE, TRIGGER_PCT)
        ref  = _ref_run_analysis (ticker, START_DATE, END_DATE, TRIGGER_PCT)

        if orig is None and ref is None:
            print("  SKIP — no data returned by either engine")
            ticker_summaries[ticker] = "SKIP"
            continue
        if orig is None or ref is None:
            print(f"  FAIL — one engine returned None (orig={orig is None}, ref={ref is None})")
            ticker_summaries[ticker] = "FAIL"
            continue

        # Analysis checks
        _check(f"[{ticker}] current_price", orig["current_price"], ref["current_price"], ticker_results)
        _check(f"[{ticker}] high_price",    orig["high_price"],    ref["high_price"],    ticker_results)
        _check(f"[{ticker}] drawdown_pct",  orig["drawdown_pct"],  ref["drawdown_pct"],  ticker_results)
        _check(f"[{ticker}] trigger_price", orig["trigger_price"], ref["trigger_price"], ticker_results)
        _check(f"[{ticker}] trigger_hit",   orig["trigger_hit"],   ref["trigger_hit"],   ticker_results)
        _check(f"[{ticker}] ttm_dividend",  orig["ttm_dividend"],  ref["ttm_dividend"],  ticker_results)
        _check(f"[{ticker}] dividend_yield",orig["dividend_yield"],ref["dividend_yield"],ticker_results)

        # Dividend reinvestment checks
        orig_r = _orig_run_reinvest(orig["close"], orig["dividends"], INITIAL_AMT, MONTHLY_AMT, TAX_RATE_PCT)
        ref_r  = _ref_run_reinvest (ref["close"],  ref["dividends"],  INITIAL_AMT, MONTHLY_AMT, TAX_RATE_PCT)

        if orig_r is not None and ref_r is not None:
            _check(f"[{ticker}] reinvest.final_value",  orig_r["final_value"],  ref_r["final_value"],  ticker_results)
            _check(f"[{ticker}] reinvest.total_ext",    orig_r["total_ext"],    ref_r["total_ext"],    ticker_results)
            _check(f"[{ticker}] reinvest.final_shares", orig_r["final_shares"], ref_r["final_shares"], ticker_results)
            _check(f"[{ticker}] reinvest.cum_gross",    orig_r["cum_gross"],    ref_r["cum_gross"],    ticker_results)
            _check(f"[{ticker}] reinvest.cum_tax",      orig_r["cum_tax"],      ref_r["cum_tax"],      ticker_results)
            _check(f"[{ticker}] reinvest.cum_net",      orig_r["cum_net"],      ref_r["cum_net"],      ticker_results)
            _check(f"[{ticker}] reinvest.cagr",         orig_r["cagr"],         ref_r["cagr"],         ticker_results)

        for r in ticker_results:
            icon = "✅" if r["status"] == "PASS" else "❌"
            print(f"  {icon} {r['status']:4s}  {r['label']}")
            if r["status"] == "FAIL":
                print(f"         orig={r['orig']!r}  ref={r['ref']!r}")

        all_results.extend(ticker_results)

        ticker_fail = any(r["status"] == "FAIL" for r in ticker_results)
        ticker_summaries[ticker] = "FAIL" if ticker_fail else "PASS"

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  VALIDATION SUMMARY")
    print(f"{'='*60}")

    for ticker, status in ticker_summaries.items():
        icon = "✅" if status == "PASS" else ("⚠️ " if status == "SKIP" else "❌")
        print(f"  {icon}  {ticker:20s}  {status}")

    total  = len(all_results)
    passed = sum(1 for r in all_results if r["status"] == "PASS")
    failed = total - passed

    print(f"\n  Checks passed: {passed}/{total}")

    if failed == 0 and total > 0:
        print("\n  ✅  ALL CHECKS PASSED — engine is preserved correctly.")
        sys.exit(0)
    elif total == 0:
        print("\n  ⚠️   NO DATA — all tickers skipped (network issue?)")
        sys.exit(2)
    else:
        print(f"\n  ❌  {failed} CHECK(S) FAILED — review differences above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
