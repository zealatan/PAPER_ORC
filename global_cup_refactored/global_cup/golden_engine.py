"""
golden_engine.py
================
Golden source engine — behavior copied exactly from golden.py.

Adjustments vs golden.py:
  1. Removed `import streamlit` and all st.* calls (not needed for engine functions)
  2. build_current_status: always returns a dict (removed the None-return on drop_bucket=None
     so the refactored app can display any drawdown level); added _raw_* numeric fields for
     integration into AnalysisResult; original Korean fields preserved unchanged.
  3. Added run_trigger_backtest_df() — thin wrapper that extracts the trigger-mode buy
     dates/prices as an English-column DataFrame for chart marker compatibility.
  4. Colors inlined (COLOR_HIGH, COLOR_LOW, etc.) — no longer imported from Streamlit UI layer.

DO NOT modify the algorithm inside any of these functions.
The logic must remain byte-for-byte identical to golden.py.
"""
from __future__ import annotations

from datetime import date
from typing import List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go

# ── Chart marker constants (from golden.py theme) ─────────────────────────────

COLOR_HIGH = "#ca6702"
COLOR_LOW  = "#005f73"
COLOR_CREAM = "#e9d8a6"
COLOR_MINT  = "#94d2bd"
FONT_CHART_MARKER_TEXT = 9


# ── Core ZigZag detection ──────────────────────────────────────────────────────

def find_alternating_high_low(close, threshold=0.10):
    """
    Copied from golden.py.
    Returns (highs, lows) — two separate lists of (timestamp, price) tuples.
    Default threshold = 0.10 (10%), matching golden.py default.

    Algorithm:
    - Before direction is established: tracks both candidate_high and candidate_low
      and updates whichever is more extreme.
    - Direction established when price crosses threshold from candidate_low (upward)
      or candidate_high (downward).
    - After direction: tracks current extreme, confirms pivot when price reverses
      by >= threshold from that extreme.
    """
    close = close.dropna()

    if len(close) < 3:
        return [], []

    highs = []
    lows = []
    trend = None

    candidate_high_idx = close.index[0]
    candidate_high_val = close.iloc[0]
    candidate_low_idx = close.index[0]
    candidate_low_val = close.iloc[0]

    for idx, val in close.iloc[1:].items():
        if trend is None:
            if val >= candidate_low_val * (1.0 + threshold):
                trend = "up"
                candidate_high_idx = idx
                candidate_high_val = val
            elif val <= candidate_high_val * (1.0 - threshold):
                trend = "down"
                candidate_low_idx = idx
                candidate_low_val = val
            else:
                if val > candidate_high_val:
                    candidate_high_idx = idx
                    candidate_high_val = val
                if val < candidate_low_val:
                    candidate_low_idx = idx
                    candidate_low_val = val
            continue

        if trend == "up":
            if val > candidate_high_val:
                candidate_high_idx = idx
                candidate_high_val = val

            drawdown = (val / candidate_high_val) - 1.0

            if drawdown <= -threshold:
                highs.append((candidate_high_idx, candidate_high_val))
                trend = "down"
                candidate_low_idx = idx
                candidate_low_val = val

        elif trend == "down":
            if val < candidate_low_val:
                candidate_low_idx = idx
                candidate_low_val = val

            rebound = (val / candidate_low_val) - 1.0

            if rebound >= threshold:
                lows.append((candidate_low_idx, candidate_low_val))
                trend = "up"
                candidate_high_idx = idx
                candidate_high_val = val

    return highs, lows


# ── Classifiers ────────────────────────────────────────────────────────────────

def classify_drop_bucket(change_pct):
    """Copied from golden.py. Returns Korean label or None."""
    if -20 < change_pct <= -10:
        return "10~20% 하락"
    if -30 < change_pct <= -20:
        return "20~30% 하락"
    if change_pct <= -30:
        return "30% 이상 하락"
    return None


def classify_current_status(change_pct):
    """Copied from golden.py. Returns HTML span or empty string."""
    if change_pct <= -30:
        return '<span class="status-down-30">30% 이상 하락</span>'
    if change_pct <= -20:
        return '<span class="status-down-20">20~30% 하락</span>'
    if change_pct <= -10:
        return '<span class="status-down-10">10~20% 하락</span>'
    return ""


# ── build_current_status ───────────────────────────────────────────────────────

def build_current_status(close, name, ticker, universe, threshold=0.10):
    """
    Copied from golden.py.

    Reference high = max price after the most recent ZigZag low.
    Falls back to all-time max if no ZigZag lows detected.

    Modified vs golden.py:
    - Always returns a dict (does not return None when drop_bucket is None),
      so the refactored app can display any drawdown level.
    - Adds _raw_* keys with raw numeric values for AnalysisResult integration.
    """
    close = close.dropna()

    if close.empty:
        return None

    _, lows = find_alternating_high_low(close, threshold=threshold)

    current_date = close.index[-1]
    current_price = float(close.iloc[-1])

    if lows:
        last_low_idx, last_low_price = lows[-1]
        after_last_low = close[close.index >= last_low_idx]

        if after_last_low.empty:
            return None

        reference_high_idx = after_last_low.idxmax()
        reference_high_price = float(after_last_low.max())
        reference_type = "마지막 전저점 이후 최고가"
        reference_low_date_str = last_low_idx.strftime("%Y-%m-%d")
        reference_low_price_fmt = f"{float(last_low_price):,.2f}"
        reference_low_price_raw = float(last_low_price)
        reference_low_date_raw = last_low_idx
    else:
        reference_high_idx = close.idxmax()
        reference_high_price = float(close.max())
        reference_type = "선택 기간 내 최고가"
        reference_low_date_str = "-"
        reference_low_price_fmt = "-"
        reference_low_price_raw = float(close.min())
        reference_low_date_raw = close.idxmin()

    change_pct = (current_price / reference_high_price - 1.0) * 100.0
    drop_bucket = classify_drop_bucket(change_pct)

    return {
        # ── Original golden.py fields (Korean) ────────────────────────────────
        "유니버스": universe,
        "기업": name,
        "티커": ticker,
        "하락 구간": drop_bucket,
        "기준": reference_type,
        "기준 전저점 날짜": reference_low_date_str,
        "기준 전저점 가격": reference_low_price_fmt,
        "현재 기준 전고점 날짜": reference_high_idx.strftime("%Y-%m-%d"),
        "현재 기준 전고점 가격": f"{reference_high_price:,.2f}",
        "현재 날짜": current_date.strftime("%Y-%m-%d"),
        "현재 가격": f"{current_price:,.2f}",
        "전고점 대비 변화율": f"{change_pct:.2f}%",
        "상태": classify_current_status(change_pct),
        "변화율 숫자": round(float(change_pct), 2),
        # ── Raw numeric fields (added for AnalysisResult integration) ─────────
        "_ref_high_price": reference_high_price,
        "_ref_high_date":  reference_high_idx,
        "_ref_low_price":  reference_low_price_raw,
        "_ref_low_date":   reference_low_date_raw,
        "_change_pct":     change_pct,
        "_current_price":  current_price,
        "_current_date":   current_date,
    }


# ── build_drawdown_cycles ──────────────────────────────────────────────────────

def build_drawdown_cycles(close, name, ticker, universe, threshold=0.10):
    """Copied from golden.py."""
    highs, lows = find_alternating_high_low(close, threshold=threshold)
    cycles = []

    for high_idx, high_price in highs:
        next_lows = [
            (low_idx, low_price)
            for low_idx, low_price in lows
            if low_idx > high_idx
        ]

        if not next_lows:
            continue

        low_idx, low_price = next_lows[0]
        drop_pct = (low_price / high_price - 1.0) * 100.0

        cycles.append(
            {
                "유니버스": universe,
                "기업": name,
                "티커": ticker,
                "전고점 날짜": high_idx.strftime("%Y-%m-%d"),
                "전고점 가격": f"{float(high_price):,.2f}",
                "전저점 날짜": low_idx.strftime("%Y-%m-%d"),
                "전저점 가격": f"{float(low_price):,.2f}",
                "하락률": f"{drop_pct:.2f}%",
                "하락률 숫자": round(float(drop_pct), 2),
            }
        )

    return cycles


# ── nearest_trade_date ─────────────────────────────────────────────────────────

def nearest_trade_date(close, target_date):
    """Copied from golden.py."""
    target_ts = pd.Timestamp(target_date)
    idx = close.index[close.index >= target_ts]

    if len(idx) == 0:
        return None

    return idx[0]


# ── run_backtest ───────────────────────────────────────────────────────────────

def run_backtest(close, mode, initial_amount, periodic_amount, trigger_drop_pct):
    """
    Copied from golden.py.

    Modes:
      "시작일 일시불 투자"    — lump sum on start date
      "매년 초 정액 투자"     — periodic buy on Jan 1 each year
      "매월 1일 정액 투자"    — periodic buy on 1st of each month
      "트리거 발생 시 정액 투자" — buy when rolling high drops by trigger_drop_pct%;
                                  rearm when price rebounds by trigger_drop_pct% from post-trigger low

    Returns (summary_dict, display_trade_df, portfolio_df).
    Returns (None, empty_df, empty_df) if no trades.
    """
    close = close.dropna()

    if close.empty:
        return None, pd.DataFrame(), pd.DataFrame()

    trades = []

    if mode == "시작일 일시불 투자":
        buy_date = close.index[0]
        price = float(close.loc[buy_date])
        shares = initial_amount / price if price > 0 else 0.0
        trades.append((buy_date, price, initial_amount, shares, "Initial Buy"))

    elif mode == "매년 초 정액 투자":
        for year in sorted(set(close.index.year)):
            d = nearest_trade_date(close, date(year, 1, 1))
            if d is not None:
                price = float(close.loc[d])
                shares = periodic_amount / price if price > 0 else 0.0
                trades.append((d, price, periodic_amount, shares, "Yearly Buy"))

    elif mode == "매월 1일 정액 투자":
        months = sorted(set((x.year, x.month) for x in close.index))
        for y, m in months:
            d = nearest_trade_date(close, date(y, m, 1))
            if d is not None:
                price = float(close.loc[d])
                shares = periodic_amount / price if price > 0 else 0.0
                trades.append((d, price, periodic_amount, shares, "Monthly Buy"))

    elif mode == "트리거 발생 시 정액 투자":
        trigger = trigger_drop_pct / 100.0

        reference_high = float(close.iloc[0])
        reference_high_date = close.index[0]

        trigger_armed = True
        post_trigger_low = None

        for d, price in close.items():
            price = float(price)

            if trigger_armed:
                if price > reference_high:
                    reference_high = price
                    reference_high_date = d

                drawdown = price / reference_high - 1.0

                if drawdown <= -trigger:
                    shares = periodic_amount / price if price > 0 else 0.0
                    trades.append(
                        (
                            d,
                            price,
                            periodic_amount,
                            shares,
                            f"BUY: {trigger_drop_pct}% Drop From High "
                            f"({reference_high_date.strftime('%Y-%m-%d')}, {reference_high:,.2f})",
                        )
                    )
                    trigger_armed = False
                    post_trigger_low = price

            else:
                if post_trigger_low is None:
                    post_trigger_low = price
                if price < post_trigger_low:
                    post_trigger_low = price

                rebound = price / post_trigger_low - 1.0
                if rebound >= trigger:
                    reference_high = price
                    reference_high_date = d
                    trigger_armed = True
                    post_trigger_low = None

    if not trades:
        return None, pd.DataFrame(), pd.DataFrame()

    raw_trade_df = pd.DataFrame(
        trades,
        columns=["매수일", "매수가", "투자금", "매수수량", "매수유형"],
    )

    total_invested = float(raw_trade_df["투자금"].sum())
    total_shares   = float(raw_trade_df["매수수량"].sum())
    final_price    = float(close.iloc[-1])
    final_value    = total_shares * final_price
    profit         = final_value - total_invested
    return_pct     = profit / total_invested * 100.0 if total_invested > 0 else 0.0

    first_price         = float(close.iloc[0])
    buy_and_hold_return = (final_price / first_price - 1.0) * 100.0 if first_price > 0 else 0.0

    summary = {
        "총 투자금": total_invested,
        "최종 평가금액": final_value,
        "수익금": profit,
        "수익률": return_pct,
        "총 매수 횟수": len(raw_trade_df),
        "총 보유 수량": total_shares,
        "최종 가격": final_price,
        "단순 가격 상승률": buy_and_hold_return,
    }

    portfolio_rows = []
    cumulative_shares   = 0.0
    cumulative_invested = 0.0
    trade_idx    = 0
    sorted_trades = raw_trade_df.sort_values("매수일").reset_index(drop=True)

    for d, price in close.items():
        while (trade_idx < len(sorted_trades)
               and sorted_trades.loc[trade_idx, "매수일"] <= d):
            cumulative_shares   += float(sorted_trades.loc[trade_idx, "매수수량"])
            cumulative_invested += float(sorted_trades.loc[trade_idx, "투자금"])
            trade_idx += 1

        value = cumulative_shares * float(price)
        pnl   = value - cumulative_invested
        ret   = pnl / cumulative_invested * 100.0 if cumulative_invested > 0 else 0.0

        portfolio_rows.append({
            "날짜": d,
            "가격": float(price),
            "보유수량": cumulative_shares,
            "누적 투자금": cumulative_invested,
            "평가금액": value,
            "손익": pnl,
            "수익률": ret,
        })

    portfolio_df = pd.DataFrame(portfolio_rows)

    display_trade_df = raw_trade_df.copy()
    display_trade_df["매수일"]  = display_trade_df["매수일"].dt.strftime("%Y-%m-%d")
    display_trade_df["매수가"]  = display_trade_df["매수가"].map(lambda x: f"{x:,.2f}")
    display_trade_df["투자금"]  = display_trade_df["투자금"].map(lambda x: f"{x:,.2f}")
    display_trade_df["매수수량"] = display_trade_df["매수수량"].map(lambda x: f"{x:,.6f}")

    return summary, display_trade_df, portfolio_df


# ── calculate_annual_dividends ─────────────────────────────────────────────────

def calculate_annual_dividends(dividends, portfolio_df):
    """Copied from golden.py."""
    if dividends.empty or portfolio_df.empty:
        return pd.DataFrame()

    portfolio_df = portfolio_df.copy()
    portfolio_df["날짜"] = pd.to_datetime(portfolio_df["날짜"]).dt.tz_localize(None)

    dividends = dividends.copy()
    dividends.index = pd.to_datetime(dividends.index).tz_localize(None)

    annual_div_per_share = dividends.groupby(dividends.index.year).sum()

    rows = []
    for year, div_per_share in annual_div_per_share.items():
        year_portfolio = portfolio_df[portfolio_df["날짜"].dt.year == year]
        if year_portfolio.empty:
            continue

        year_end_row = year_portfolio.sort_values("날짜").iloc[-1]
        shares_at_year_end = float(year_end_row["보유수량"])
        dividend_cash = shares_at_year_end * float(div_per_share)

        rows.append({
            "연도": int(year),
            "연간 주당 배당금": float(div_per_share),
            "연말 보유수량": shares_at_year_end,
            "연간 배당금": dividend_cash,
        })

    annual_df = pd.DataFrame(rows)
    if annual_df.empty:
        return annual_df

    annual_df["누적 배당금"] = annual_df["연간 배당금"].cumsum()
    return annual_df


# ── run_dividend_backtest ──────────────────────────────────────────────────────

def run_dividend_backtest(close, dividends, mode, initial_amount, periodic_amount, trigger_drop_pct):
    """Copied from golden.py."""
    summary, trade_df, portfolio_df = run_backtest(
        close=close,
        mode=mode,
        initial_amount=initial_amount,
        periodic_amount=periodic_amount,
        trigger_drop_pct=trigger_drop_pct,
    )

    if summary is None:
        return None, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    annual_dividend_df = calculate_annual_dividends(dividends, portfolio_df)

    total_dividend = 0.0
    if not annual_dividend_df.empty:
        total_dividend = float(annual_dividend_df["연간 배당금"].sum())

    final_value              = float(summary["최종 평가금액"])
    total_invested           = float(summary["총 투자금"])
    final_value_with_dividend = final_value + total_dividend
    profit_with_dividend     = final_value_with_dividend - total_invested
    return_with_dividend     = (
        profit_with_dividend / total_invested * 100.0
        if total_invested > 0 else 0.0
    )

    dividend_summary = summary.copy()
    dividend_summary["누적 배당금"]       = total_dividend
    dividend_summary["배당 포함 최종자산"] = final_value_with_dividend
    dividend_summary["배당 포함 수익금"]   = profit_with_dividend
    dividend_summary["배당 포함 수익률"]   = return_with_dividend

    return dividend_summary, trade_df, portfolio_df, annual_dividend_df


# ── run_dividend_reinvest_backtest (golden.py version) ─────────────────────────

def run_dividend_reinvest_backtest(
    close, dividends, mode, initial_amount, periodic_amount, trigger_drop_pct
):
    """
    Copied from golden.py.

    Dividend reinvestment scenario:
    - Runs the same base buy strategy as run_backtest().
    - For each year: sum all dividends per share, buy additional shares at year-end price.
    - Reinvested shares receive dividends in later years.

    Returns (reinvest_summary, trade_df, portfolio_df, reinvest_df, reinvest_timeline_df).
    """
    summary, trade_df, portfolio_df = run_backtest(
        close=close,
        mode=mode,
        initial_amount=initial_amount,
        periodic_amount=periodic_amount,
        trigger_drop_pct=trigger_drop_pct,
    )

    if summary is None:
        return None, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    if dividends.empty or portfolio_df.empty:
        reinvest_summary = summary.copy()
        reinvest_summary["누적 배당금"]             = 0.0
        reinvest_summary["재투자 추가 주식수"]       = 0.0
        reinvest_summary["재투자 후 총 주식수"]      = float(summary["총 보유 수량"])
        reinvest_summary["배당 재투자 주식 평가액"]  = float(summary["최종 평가금액"])
        reinvest_summary["총 자산(배당금+주식평가액)"] = float(summary["최종 평가금액"])
        reinvest_summary["배당 재투자 최종자산"]     = float(summary["최종 평가금액"])
        reinvest_summary["배당 재투자 수익금"]       = float(summary["수익금"])
        reinvest_summary["배당 재투자 수익률"]       = float(summary["수익률"])
        reinvest_summary["최근 연간 주당 배당금"]    = 0.0
        reinvest_summary["현재 예상 연배당금"]       = 0.0
        reinvest_summary["현재 예상 배당률"]         = 0.0
        return reinvest_summary, trade_df, portfolio_df, pd.DataFrame(), pd.DataFrame()

    close = close.dropna().copy()
    close.index = pd.to_datetime(close.index).tz_localize(None)

    dividends = dividends.copy()
    dividends.index = pd.to_datetime(dividends.index).tz_localize(None)

    portfolio_df = portfolio_df.copy()
    portfolio_df["날짜"] = pd.to_datetime(portfolio_df["날짜"]).dt.tz_localize(None)

    annual_div_per_share = dividends.groupby(dividends.index.year).sum()

    reinvest_rows       = []
    extra_shares_total  = 0.0
    cumulative_dividend = 0.0
    reinvest_events     = []

    for year, div_per_share in annual_div_per_share.items():
        year_portfolio = portfolio_df[portfolio_df["날짜"].dt.year == year]
        if year_portfolio.empty:
            continue

        year_end_row  = year_portfolio.sort_values("날짜").iloc[-1]
        year_end_date = pd.Timestamp(year_end_row["날짜"])

        close_until_year_end = close[close.index <= year_end_date]
        if close_until_year_end.empty:
            continue

        year_end_price          = float(close_until_year_end.iloc[-1])
        base_shares             = float(year_end_row["보유수량"])
        total_shares_before     = base_shares + extra_shares_total
        dividend_cash           = total_shares_before * float(div_per_share)
        stock_value_before      = total_shares_before * year_end_price
        reinvested_shares       = dividend_cash / year_end_price if year_end_price > 0 else 0.0

        extra_shares_total  += reinvested_shares
        cumulative_dividend += dividend_cash

        total_shares_after     = total_shares_before + reinvested_shares
        stock_value_after      = total_shares_after * year_end_price
        div_yield_on_year_end  = (
            dividend_cash / stock_value_before * 100.0
            if stock_value_before > 0 else 0.0
        )
        estimated_next_annual  = total_shares_after * float(div_per_share)

        reinvest_rows.append({
            "연도":                    int(year),
            "연말 날짜":                year_end_date,
            "연말 가격":                year_end_price,
            "연간 주당 배당금":          float(div_per_share),
            "기존 전략 보유수량":        base_shares,
            "재투자 전 총 주식수":       total_shares_before,
            "재투자 전 주식 평가액":     stock_value_before,
            "연간 배당금":               dividend_cash,
            "연말 평가액 대비 배당률":   div_yield_on_year_end,
            "재투자 매수수량":           reinvested_shares,
            "재투자 후 총 주식수":       total_shares_after,
            "재투자 후 주식 평가액":     stock_value_after,
            "총 자산(누적배당+주식평가액)": cumulative_dividend + stock_value_after,
            "예상 다음해 연배당금":       estimated_next_annual,
            "누적 재투자 주식수":        extra_shares_total,
            "누적 배당금":               cumulative_dividend,
        })

        reinvest_events.append({
            "날짜":            year_end_date,
            "재투자 매수수량":  reinvested_shares,
            "누적 재투자 주식수": extra_shares_total,
            "누적 배당금":      cumulative_dividend,
        })

    reinvest_df = pd.DataFrame(reinvest_rows)

    timeline_rows              = []
    event_idx                  = 0
    current_extra_shares       = 0.0
    current_cumul_dividend     = 0.0

    for _, row in portfolio_df.sort_values("날짜").iterrows():
        d = pd.Timestamp(row["날짜"])

        while (event_idx < len(reinvest_events)
               and reinvest_events[event_idx]["날짜"] <= d):
            current_extra_shares   = float(reinvest_events[event_idx]["누적 재투자 주식수"])
            current_cumul_dividend = float(reinvest_events[event_idx]["누적 배당금"])
            event_idx += 1

        base_shares  = float(row["보유수량"])
        price        = float(row["가격"])
        total_shares = base_shares + current_extra_shares
        value        = total_shares * price

        timeline_rows.append({
            "날짜":             d,
            "가격":             price,
            "기존 전략 보유수량": base_shares,
            "누적 재투자 주식수": current_extra_shares,
            "재투자 후 총 주식수": total_shares,
            "누적 배당금":       current_cumul_dividend,
            "배당 재투자 평가금액": value,
        })

    reinvest_timeline_df = pd.DataFrame(timeline_rows)

    final_price          = float(close.iloc[-1])
    original_shares      = float(summary["총 보유 수량"])
    final_total_shares   = original_shares + extra_shares_total
    final_value_reinvested = final_total_shares * final_price
    total_invested       = float(summary["총 투자금"])
    profit_reinvested    = final_value_reinvested - total_invested
    return_reinvested    = (
        profit_reinvested / total_invested * 100.0
        if total_invested > 0 else 0.0
    )

    total_recv = cumulative_dividend + final_value_reinvested
    recent_div = float(annual_div_per_share.iloc[-1]) if not annual_div_per_share.empty else 0.0
    est_annual = final_total_shares * recent_div
    est_yield  = est_annual / final_value_reinvested * 100.0 if final_value_reinvested > 0 else 0.0

    reinvest_summary = summary.copy()
    reinvest_summary["누적 배당금"]              = cumulative_dividend
    reinvest_summary["재투자 추가 주식수"]        = extra_shares_total
    reinvest_summary["재투자 후 총 주식수"]       = final_total_shares
    reinvest_summary["배당 재투자 주식 평가액"]   = final_value_reinvested
    reinvest_summary["총 자산(배당금+주식평가액)"] = total_recv
    reinvest_summary["배당 재투자 최종자산"]      = final_value_reinvested
    reinvest_summary["배당 재투자 수익금"]        = profit_reinvested
    reinvest_summary["배당 재투자 수익률"]        = return_reinvested
    reinvest_summary["최근 연간 주당 배당금"]     = recent_div
    reinvest_summary["현재 예상 연배당금"]        = est_annual
    reinvest_summary["현재 예상 배당률"]          = est_yield

    return reinvest_summary, trade_df, portfolio_df, reinvest_df, reinvest_timeline_df


# ── add_high_low_markers ───────────────────────────────────────────────────────

def add_high_low_markers(fig, close, name, ticker, threshold=0.10):
    """
    Copied from golden.py.
    Calls find_alternating_high_low() internally and adds H/L traces to fig.
    """
    highs, lows = find_alternating_high_low(close, threshold=threshold)

    if highs:
        fig.add_trace(go.Scatter(
            x=[x for x, _ in highs],
            y=[y for _, y in highs],
            mode="markers+text",
            name="전고점",
            marker=dict(
                color=COLOR_HIGH,
                size=8,
                symbol="triangle-up",
                line=dict(width=1.0, color=COLOR_CREAM),
            ),
            text=["H"] * len(highs),
            textposition="top center",
            textfont=dict(color=COLOR_HIGH, size=FONT_CHART_MARKER_TEXT),
        ))

    if lows:
        fig.add_trace(go.Scatter(
            x=[x for x, _ in lows],
            y=[y for _, y in lows],
            mode="markers+text",
            name="전저점",
            marker=dict(
                color=COLOR_LOW,
                size=8,
                symbol="triangle-down",
                line=dict(width=1.0, color=COLOR_MINT),
            ),
            text=["L"] * len(lows),
            textposition="bottom center",
            textfont=dict(color=COLOR_LOW, size=FONT_CHART_MARKER_TEXT),
        ))


# ── run_trigger_backtest_df (integration wrapper) ──────────────────────────────

def run_trigger_backtest_df(close: pd.Series, trigger_drop_pct: float) -> pd.DataFrame:
    """
    Run the golden.py trigger-mode backtest and return an English-column
    DataFrame with columns [Buy Date, Buy Price] for use by
    add_trigger_buy_markers() in charts.py.

    Logic is identical to run_backtest() mode="트리거 발생 시 정액 투자"
    (periodic_amount is irrelevant for buy-date/price detection).
    """
    close = close.dropna()
    if close.empty:
        return pd.DataFrame(columns=["Buy Date", "Buy Price"])

    close_tz = close.copy()
    close_tz.index = pd.to_datetime(close_tz.index).tz_localize(None)

    trigger          = trigger_drop_pct / 100.0
    reference_high   = float(close_tz.iloc[0])
    reference_high_date = close_tz.index[0]
    trigger_armed    = True
    post_trigger_low = None

    rows = []
    for d, price in close_tz.items():
        price = float(price)

        if trigger_armed:
            if price > reference_high:
                reference_high      = price
                reference_high_date = d

            drawdown = price / reference_high - 1.0

            if drawdown <= -trigger:
                rows.append({"Buy Date": d, "Buy Price": price})
                trigger_armed    = False
                post_trigger_low = price

        else:
            if post_trigger_low is None:
                post_trigger_low = price
            if price < post_trigger_low:
                post_trigger_low = price

            rebound = price / post_trigger_low - 1.0
            if rebound >= trigger:
                reference_high      = price
                reference_high_date = d
                trigger_armed       = True
                post_trigger_low    = None

    return pd.DataFrame(rows)
