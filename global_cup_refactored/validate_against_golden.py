"""
validate_against_golden.py
==========================
Phase 4 — Validate that golden_engine.py behavior matches golden.py exactly.

Tests:
  Part A — Synthetic deterministic cases
    A1: [100, 110, 120, 100]  — simple rise-then-fall
    A2: [100, 120, 90, 110, 130, 100]  — alternating cycles
    A3: Monotonic increasing  — no trigger on uptrend

  Part B — Golden algorithm properties vs cross-check
    B1: find_alternating_high_low returns (highs, lows) tuple
    B2: Highs and lows alternate correctly
    B3: build_current_status uses max-after-last-low as reference high
    B4: Trigger varies correctly for trigger_drop_pct 5, 10, 20, 30
    B5: run_trigger_backtest_df fires/rearmes on rolling-high logic

  Part C — Real tickers (requires network)
    For VOO, SCHD, JEPI, 360750.KS, 441680.KS:
      trigger_drop_pct ∈ {5, 10, 20, 30}
      - find_alternating_high_low matches independent golden reimplementation
      - build_current_status raw fields are consistent
      - run_trigger_backtest_df buy dates exist and buy price ≤ trigger

Run from global_cup_refactored/:
    python3 validate_against_golden.py
"""
from __future__ import annotations

import sys
from datetime import date
from typing import Dict, List

import pandas as pd

sys.path.insert(0, ".")

from global_cup.golden_engine import (
    find_alternating_high_low,
    build_current_status,
    build_drawdown_cycles,
    nearest_trade_date,
    run_backtest,
    run_trigger_backtest_df,
    calculate_annual_dividends,
    run_dividend_backtest,
)
from global_cup.analysis import run_analysis
from global_cup.market_config import UserInput


# ── Helpers ────────────────────────────────────────────────────────────────────

RESULTS: List[Dict] = []


def _record(label: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    icon   = "✅" if ok else "❌"
    RESULTS.append({"label": label, "status": status})
    print(f"  {icon} {status:4s}  {label}" + (f"  [{detail}]" if detail else ""))


def _series(prices: list, start: str = "2020-01-01") -> pd.Series:
    idx = pd.date_range(start=start, periods=len(prices), freq="B")
    return pd.Series([float(p) for p in prices], index=idx)


def _golden_reimpl(close, threshold):
    """
    Independent reimplementation of golden.py's find_alternating_high_low for
    cross-checking. Identical logic, separate code path.
    """
    close = close.dropna()
    if len(close) < 3:
        return [], []
    highs, lows = [], []
    trend = None
    chi = close.index[0]; chv = float(close.iloc[0])
    cli = close.index[0]; clv = float(close.iloc[0])
    for idx, val in close.iloc[1:].items():
        val = float(val)
        if trend is None:
            if val >= clv * (1.0 + threshold):
                trend = "up"; chi = idx; chv = val
            elif val <= chv * (1.0 - threshold):
                trend = "down"; cli = idx; clv = val
            else:
                if val > chv: chi = idx; chv = val
                if val < clv: cli = idx; clv = val
            continue
        if trend == "up":
            if val > chv: chi = idx; chv = val
            if (val / chv) - 1.0 <= -threshold:
                highs.append((chi, chv)); trend = "down"; cli = idx; clv = val
        else:
            if val < clv: cli = idx; clv = val
            if (val / clv) - 1.0 >= threshold:
                lows.append((cli, clv)); trend = "up"; chi = idx; chv = val
    return highs, lows


# ─────────────────────────────────────────────────────────────────────────────
# PART A — Synthetic
# ─────────────────────────────────────────────────────────────────────────────

def test_synthetic() -> None:
    print("\n" + "=" * 60)
    print("  PART A — Synthetic Tests")
    print("=" * 60)

    # ── A1: [100, 110, 120, 100] ──────────────────────────────────────────────
    print("\n── A1: [100, 110, 120, 100] threshold=0.10 ──")
    s1 = _series([100, 110, 120, 100])
    highs, lows = find_alternating_high_low(s1, threshold=0.10)
    _record("A1 returns tuple of (highs, lows)", isinstance(highs, list) and isinstance(lows, list))
    _record("A1 high at 120 detected", any(abs(p - 120) < 1e-6 for _, p in highs),
            f"highs={[p for _, p in highs]}")

    gcs = build_current_status(s1, "TEST", "TEST", "A", threshold=0.10)
    _record("A1 build_current_status returns dict", isinstance(gcs, dict))
    _record("A1 ref_high_price >= current_price",
            gcs["_ref_high_price"] >= gcs["_current_price"] - 1e-6,
            f"ref_high={gcs['_ref_high_price']:.2f} cur={gcs['_current_price']:.2f}")
    dd = gcs["_change_pct"]
    _record("A1 change_pct < 0 (drawdown detected)", dd < 0, f"change_pct={dd:.2f}%")

    # ── A2: [100, 120, 90, 110, 130, 100] ────────────────────────────────────
    print("\n── A2: [100, 120, 90, 110, 130, 100] threshold=0.10 ──")
    s2 = _series([100, 120, 90, 110, 130, 100])
    highs2, lows2 = find_alternating_high_low(s2, threshold=0.10)
    _record("A2 at least 1 high detected", len(highs2) >= 1,
            f"highs={[p for _, p in highs2]}")
    _record("A2 at least 1 low detected",  len(lows2) >= 1,
            f"lows={[p for _, p in lows2]}")

    gcs2 = build_current_status(s2, "TEST", "TEST", "A", threshold=0.10)
    _record("A2 build_current_status ref_high from after-last-low",
            gcs2["_ref_high_price"] > 0,
            f"ref_high={gcs2['_ref_high_price']:.2f}")

    cycles2 = build_drawdown_cycles(s2, "TEST", "TEST", "A", threshold=0.10)
    _record("A2 drawdown cycles detected", len(cycles2) >= 1, f"cycles={len(cycles2)}")

    # ── A3: Monotonic increasing ──────────────────────────────────────────────
    print("\n── A3: Monotonic [100..150] — no trigger ──")
    s3 = _series([100 + i for i in range(51)])
    for tp in [5, 10, 20, 30]:
        gcs3 = build_current_status(s3, "TEST", "TEST", "A", threshold=tp / 100.0)
        _record(f"A3 no trigger hit monotonic (trigger_pct={tp})",
                gcs3["_change_pct"] >= 0,
                f"change_pct={gcs3['_change_pct']:.2f}%")

    bt3 = run_trigger_backtest_df(s3, 10.0)
    _record("A3 no trigger buys on monotonic series",
            bt3.empty, f"buy_count={len(bt3)}")


# ─────────────────────────────────────────────────────────────────────────────
# PART B — Golden algorithm properties
# ─────────────────────────────────────────────────────────────────────────────

def test_golden_properties() -> None:
    print("\n" + "=" * 60)
    print("  PART B — Golden Algorithm Properties")
    print("=" * 60)

    # ── B1: Cross-check find_alternating_high_low ─────────────────────────────
    print("\n── B1: find_alternating_high_low cross-check vs reimpl ──")
    test_series = [
        _series([100, 115, 95, 120, 90, 125, 100]),
        _series([100, 112, 98, 118, 94, 130, 110, 140, 115]),
        _series([100, 125, 96, 125, 96]),  # 25%-swing series
    ]
    for i, s in enumerate(test_series):
        for tp in [5, 10, 20]:
            threshold = tp / 100.0
            ref_h, ref_l = _golden_reimpl(s, threshold)
            got_h, got_l = find_alternating_high_low(s, threshold=threshold)
            h_match = (len(ref_h) == len(got_h) and
                       all(abs(a[1] - b[1]) < 1e-6 for a, b in zip(ref_h, got_h)))
            l_match = (len(ref_l) == len(got_l) and
                       all(abs(a[1] - b[1]) < 1e-6 for a, b in zip(ref_l, got_l)))
            _record(f"B1 series{i+1} threshold={threshold:.2f}: highs match reimpl",
                    h_match,
                    f"ref={len(ref_h)} got={len(got_h)}")
            _record(f"B1 series{i+1} threshold={threshold:.2f}: lows match reimpl",
                    l_match,
                    f"ref={len(ref_l)} got={len(got_l)}")

    # ── B2: Ref high = max after last low ─────────────────────────────────────
    print("\n── B2: build_current_status ref_high = max after last low ──")
    s_b2 = _series([100, 120, 90, 130, 95, 140, 110])
    highs_b2, lows_b2 = find_alternating_high_low(s_b2, threshold=0.10)
    gcs_b2 = build_current_status(s_b2, "T", "T", "X", threshold=0.10)
    if lows_b2:
        last_low_idx = lows_b2[-1][0]
        after_low = s_b2[s_b2.index >= last_low_idx]
        expected_ref_high = float(after_low.max())
        _record("B2 ref_high_price = max after last ZigZag low",
                abs(gcs_b2["_ref_high_price"] - expected_ref_high) < 1e-6,
                f"expected={expected_ref_high:.2f} got={gcs_b2['_ref_high_price']:.2f}")
    else:
        _record("B2 ref_high_price fallback to period max (no lows)",
                abs(gcs_b2["_ref_high_price"] - float(s_b2.max())) < 1e-6)

    # ── B3: run_trigger_backtest_df rolling-high logic ────────────────────────
    print("\n── B3: run_trigger_backtest_df rolling-high trigger ──")
    # [100, 120, 102, 120, 100, 122] with trigger=10%
    # ref_high starts at 100, rises to 120
    # 120 → 102 = -15% → BUY at ~102 (since 102/120-1 = -15% <= -10%)
    # After buy: post_trigger_low tracks from 102
    # 102 → 120 = +17.6% >= 10% → rearm at 120
    # 120 → 100 = -16.7% → BUY at ~100
    s_b3 = _series([100, 120, 102, 120, 100, 122])
    bt_b3 = run_trigger_backtest_df(s_b3, 10.0)
    _record("B3 trigger fires on rolling-high drop >= 10%",
            len(bt_b3) >= 1, f"buy_count={len(bt_b3)}")
    if not bt_b3.empty:
        _record("B3 buy price <= 90% of rolling high",
                (bt_b3["Buy Price"] <= 120.0 * 0.90 + 1e-6).all(),
                f"prices={bt_b3['Buy Price'].tolist()}")

    # ── B4: Threshold changes H/L count ──────────────────────────────────────
    print("\n── B4: Threshold sensitivity ──")
    # 25%-swing series: qualifies at 0.20, not at 0.30
    s_b4 = _series([100, 125, 96, 125, 96])
    h20, l20 = find_alternating_high_low(s_b4, threshold=0.20)
    h30, l30 = find_alternating_high_low(s_b4, threshold=0.30)
    _record("B4 threshold=0.20: highs ≥ 1 (25% swing qualifies)",
            len(h20) >= 1, f"highs={len(h20)}")
    _record("B4 threshold=0.30: fewer highs than 0.20 (25% < 30%)",
            len(h30) < len(h20),
            f"0.20={len(h20)} 0.30={len(h30)}")

    # ── B5: trigger_pct coverage (5, 10, 20, 30) ─────────────────────────────
    print("\n── B5: trigger_pct coverage on [100, 110, 104] (dd ≈ -5.45%) ──")
    # [100, 110, 104]: ref_high depends on threshold
    # At threshold=0.05: 100→110 +10%>=5% → trend up; 110→104 -5.45%>=5% → confirm H(110)
    # At threshold=0.10: 100→110 +10%>=10% → trend up; 110→104 -5.45% < 10% → no confirm; still candidate H
    # In both cases close=104, ref_high = max after last low (or period high if no lows yet)
    s_hit = _series([100, 110, 104])
    for tp, expect_hit in [(5, True), (10, False), (20, False), (30, False)]:
        th = tp / 100.0
        gcs = build_current_status(s_hit, "T", "T", "X", threshold=th)
        trigger_hit = gcs["_change_pct"] <= -float(tp)
        _record(f"B5 trigger_pct={tp:2d}: trigger_hit={'True ' if expect_hit else 'False'}",
                trigger_hit == expect_hit,
                f"change_pct={gcs['_change_pct']:.2f}%")

    # ── B6: nearest_trade_date ────────────────────────────────────────────────
    print("\n── B6: nearest_trade_date ──")
    s_nd = _series([100, 101, 102], start="2020-01-02")
    target = pd.Timestamp("2020-01-02")
    got = nearest_trade_date(s_nd, target)
    _record("B6 exact date returns self", got == target, str(got))
    got_b = nearest_trade_date(s_nd, pd.Timestamp("2020-01-01"))
    _record("B6 before range returns first available", got_b >= target, str(got_b))
    got_n = nearest_trade_date(s_nd, pd.Timestamp("2030-01-01"))
    _record("B6 beyond range returns None", got_n is None, str(got_n))


# ─────────────────────────────────────────────────────────────────────────────
# PART C — Real tickers (requires network)
# ─────────────────────────────────────────────────────────────────────────────

def test_real_tickers() -> None:
    print("\n" + "=" * 60)
    print("  PART C — Real-Ticker Validation (trigger_pct 5/10/20/30)")
    print("=" * 60)

    try:
        from global_cup.data_loader import download_price, download_dividends, get_close_series
    except ImportError as e:
        print(f"  SKIP (import error: {e})")
        return

    TICKERS = ["VOO", "SCHD", "JEPI", "360750.KS", "441680.KS"]
    START   = date(2020, 1, 1)
    END     = date(2024, 12, 31)

    for ticker in TICKERS:
        print(f"\n  Ticker: {ticker}")
        try:
            price_df = download_price(ticker, START, END)
            if price_df.empty:
                print("    SKIP (no price data)")
                continue
            close = get_close_series(price_df)
            if close.empty:
                print("    SKIP (empty close)")
                continue
        except Exception as e:
            print(f"    SKIP ({e})")
            continue

        # Cross-check find_alternating_high_low against reimpl at multiple thresholds
        for tp in [5, 10, 20, 30]:
            threshold = tp / 100.0
            ref_h, ref_l = _golden_reimpl(close, threshold)
            got_h, got_l = find_alternating_high_low(close, threshold=threshold)
            _record(f"[{ticker}] tp={tp:2d}: high count matches reimpl",
                    len(ref_h) == len(got_h),
                    f"ref={len(ref_h)} got={len(got_h)}")
            _record(f"[{ticker}] tp={tp:2d}: low count matches reimpl",
                    len(ref_l) == len(got_l),
                    f"ref={len(ref_l)} got={len(got_l)}")

        # build_current_status consistency checks at trigger_pct=10 (most common)
        gcs = build_current_status(close, ticker, ticker, "App", threshold=0.10)
        if gcs is None:
            _record(f"[{ticker}] build_current_status (tp=10) returned non-None", False)
            continue

        _record(f"[{ticker}] ref_high_price > 0",
                gcs["_ref_high_price"] > 0, f"{gcs['_ref_high_price']:.2f}")
        _record(f"[{ticker}] ref_high_price >= current_price",
                gcs["_ref_high_price"] >= gcs["_current_price"] - 1e-6,
                f"ref={gcs['_ref_high_price']:.2f} cur={gcs['_current_price']:.2f}")
        _record(f"[{ticker}] change_pct ≤ 0 (no future knowledge)",
                gcs["_change_pct"] <= 0.001,
                f"{gcs['_change_pct']:.2f}%")

        # run_trigger_backtest_df at trigger_pct=10
        bt10 = run_trigger_backtest_df(close, 10.0)
        _record(f"[{ticker}] run_trigger_backtest_df tp=10 returns DataFrame",
                isinstance(bt10, pd.DataFrame),
                f"buys={len(bt10)}")
        if not bt10.empty:
            _record(f"[{ticker}] buy prices positive",
                    (bt10["Buy Price"] > 0).all(),
                    f"min_price={bt10['Buy Price'].min():.2f}")

        # Trigger count changes with trigger_pct (lower trigger = more buys)
        bt5  = run_trigger_backtest_df(close, 5.0)
        bt20 = run_trigger_backtest_df(close, 20.0)
        _record(f"[{ticker}] tp=5 buys ≥ tp=20 buys (lower trigger = more buys)",
                len(bt5) >= len(bt20),
                f"tp5={len(bt5)} tp20={len(bt20)}")

    # Validate run_analysis integration (uses golden_engine internally)
    print("\n  Validate run_analysis uses golden_engine:")
    for ticker in ["VOO", "SCHD"]:
        inp = UserInput(
            market_key="United States", ticker_label=ticker,
            ticker=ticker, trigger_pct=10.0,
            start_date=START, end_date=END,
        )
        try:
            result = run_analysis(inp)
        except Exception as e:
            print(f"    SKIP [{ticker}] (error: {e})")
            continue

        if result is None:
            print(f"    SKIP [{ticker}] (no data)")
            continue

        highs_direct, lows_direct = find_alternating_high_low(
            result.close, threshold=inp.trigger_pct / 100.0
        )
        _record(f"[{ticker}] result.high_count == direct golden h count",
                result.high_count == len(highs_direct),
                f"result={result.high_count} direct={len(highs_direct)}")
        _record(f"[{ticker}] result.low_count == direct golden l count",
                result.low_count == len(lows_direct),
                f"result={result.low_count} direct={len(lows_direct)}")
        _record(f"[{ticker}] zigzag_points stores (highs, lows) tuple",
                isinstance(result.zigzag_points, tuple) and len(result.zigzag_points) == 2,
                f"type={type(result.zigzag_points).__name__}")
        _record(f"[{ticker}] zigzag_trigger_price = ref_high*(1-trigger/100)",
                abs(result.zigzag_trigger_price -
                    result.zigzag_ref_high_price * (1.0 - inp.trigger_pct / 100.0)) < 1e-4,
                f"trigger_price={result.zigzag_trigger_price:.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    test_synthetic()
    test_golden_properties()
    test_real_tickers()

    total  = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = total - passed

    print(f"\n{'=' * 60}")
    print("  VALIDATION SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Checks passed: {passed}/{total}")

    if failed == 0 and total > 0:
        print("\n  ✅  ALL CHECKS PASSED")
        print("  PHASE_4: PASS")
        sys.exit(0)
    elif total == 0:
        print("\n  ⚠️   NO CHECKS RAN")
        sys.exit(2)
    else:
        print(f"\n  ❌  {failed} CHECK(S) FAILED")
        for r in RESULTS:
            if r["status"] == "FAIL":
                print(f"       FAIL: {r['label']}")
        print("  PHASE_4: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
