"""
validate_zigzag_engine.py
=========================
Validation suite for the ZigZag engine and its integration.

Tests:
  Part A — Synthetic deterministic cases (no network required)
  Part B — Real-ticker self-consistency checks (requires network)
  Part C — Dividend reinvestment comparison against original engine

Run from global_cup_refactored/:
    python3 validate_zigzag_engine.py
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from typing import Dict, List

import pandas as pd

sys.path.insert(0, ".")

from global_cup.zigzag_engine  import (
    find_alternating_high_low,
    build_current_status,
    build_drawdown_cycles,
    classify_drop_bucket,
    classify_current_status,
)
from global_cup.backtest_engine import (
    run_backtest,
    run_dividend_backtest,
    calculate_annual_dividends,
    nearest_trade_date,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

RESULTS: List[Dict] = []

def _record(label: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    icon   = "✅" if ok else "❌"
    RESULTS.append({"label": label, "status": status})
    print(f"  {icon} {status:4s}  {label}" + (f"  [{detail}]" if detail else ""))


def _series(prices: list, start: str = "2020-01-01") -> pd.Series:
    idx = pd.date_range(start=start, periods=len(prices), freq="B")
    return pd.Series([float(p) for p in prices], index=idx)


# ─────────────────────────────────────────────────────────────────────────────
# PART A — Synthetic tests
# ─────────────────────────────────────────────────────────────────────────────

def test_synthetic() -> None:
    print("\n" + "="*60)
    print("  PART A — Synthetic Tests")
    print("="*60)

    # ── A1: Simple rise-then-fall ─────────────────────────────────────────────
    # [100, 110, 120, 100]
    # Expected: high detected at 120, drawdown detected from 120→100
    print("\n── A1: Simple rise-then-fall [100,110,120,100] ──")
    s = _series([100, 110, 120, 100])
    pts = find_alternating_high_low(s, threshold=0.05)

    highs = [p for p in pts if p.point_type == "H"]
    lows  = [p for p in pts if p.point_type == "L"]
    _record("A1 high detected",   len(highs) >= 1)
    _record("A1 high price = 120", any(abs(h.price - 120) < 1e-6 for h in highs),
            f"highs={[h.price for h in highs]}")

    status = build_current_status(s, trigger_pct=10.0)
    dd = status["drawdown_pct"]
    _record("A1 drawdown detected (< 0)",  dd < 0, f"drawdown={dd:.2f}%")
    expected_dd = (100.0 / 120.0 - 1.0) * 100.0   # ≈ -16.67
    _record("A1 drawdown ≈ -16.7%",        abs(dd - expected_dd) < 0.1,
            f"actual={dd:.2f}% expected={expected_dd:.2f}%")

    # ── A2: Alternating cycles ────────────────────────────────────────────────
    # [100, 120, 90, 110, 130, 100]
    # Expected: alternating H/L cycle detected (L H L H L)
    print("\n── A2: Alternating [100,120,90,110,130,100] ──")
    s2 = _series([100, 120, 90, 110, 130, 100])
    pts2 = find_alternating_high_low(s2, threshold=0.05)
    highs2 = [p for p in pts2 if p.point_type == "H"]
    lows2  = [p for p in pts2 if p.point_type == "L"]

    _record("A2 multiple highs (≥2)",  len(highs2) >= 2, f"highs={[h.price for h in highs2]}")
    _record("A2 multiple lows  (≥2)",  len(lows2)  >= 2, f"lows={[l.price for l in lows2]}")
    _record("A2 points alternate H/L",
            all(pts2[i].point_type != pts2[i+1].point_type for i in range(len(pts2)-1)),
            str([p.point_type for p in pts2]))

    cycles = build_drawdown_cycles(s2, threshold=0.05)
    _record("A2 drawdown cycles detected", len(cycles) >= 1,
            f"cycles={len(cycles)}")

    # ── A3: Monotonic increase — no false trigger ─────────────────────────────
    # 11-point monotonic series: 100, 101, ..., 110
    print("\n── A3: Monotonic increase — no false trigger ──")
    s3 = _series([100 + i for i in range(11)])
    status3 = build_current_status(s3, trigger_pct=10.0)
    _record("A3 no trigger hit on monotonic increase",
            not status3["trigger_hit"],
            f"trigger_hit={status3['trigger_hit']}, drawdown={status3['drawdown_pct']:.2f}%")

    pts3 = find_alternating_high_low(s3, threshold=0.05)
    _record("A3 no false lows on monotonic increase",
            all(p.point_type != "L" or p == pts3[0] for p in pts3),
            str([p.point_type for p in pts3]))

    # ── A4: drop bucket labels ────────────────────────────────────────────────
    print("\n── A4: Drop bucket classification ──")
    cases = [(-1.0, "At High"), (-7.0, "Minor Pullback"),
             (-15.0, "Correction"), (-25.0, "Bear Territory"), (-35.0, "Deep Drawdown")]
    for dd, expected in cases:
        got = classify_drop_bucket(dd)
        _record(f"A4 bucket {dd}% → '{expected}'", got == expected,
                f"got='{got}'")

    # ── A5: status labels ─────────────────────────────────────────────────────
    print("\n── A5: Status label classification ──")
    _record("A5 status 'At High'",     classify_current_status(-0.5, 10.0) == "At High")
    _record("A5 status 'Watching'",    classify_current_status(-5.0, 10.0) == "Watching")
    _record("A5 status 'Trigger Hit'", classify_current_status(-11.0, 10.0) == "Trigger Hit")

    # ── A6: trigger backtest fires at correct price ───────────────────────────
    print("\n── A6: Trigger backtest fires correctly ──")
    # [100, 120, 90, 110, 130, 100] with trigger=10%
    # ZigZag high at 120 → trigger = 108. Price 90 < 108 → buy at 90.
    # ZigZag high at 130 → trigger = 117. Price 100 < 117 → buy at 100.
    trades = run_backtest(s2, pd.Series(dtype=float), trigger_pct=10.0, threshold=0.05)
    _record("A6 at least 1 trigger buy", len(trades) >= 1,
            f"trades={len(trades)}")
    if not trades.empty:
        _record("A6 buy price ≤ trigger price",
                (trades["Buy Price"] <= trades["Trigger Price"] + 1e-6).all(),
                f"buy={trades['Buy Price'].tolist()}, trigger={trades['Trigger Price'].tolist()}")

    # ── A7: nearest_trade_date ────────────────────────────────────────────────
    print("\n── A7: nearest_trade_date ──")
    s7 = _series([100, 101, 102, 103, 104], start="2020-01-02")
    target = pd.Timestamp("2020-01-02")
    got7 = nearest_trade_date(s7, target)
    _record("A7 exact date returns self",    got7 == target, str(got7))
    got7b = nearest_trade_date(s7, pd.Timestamp("2020-01-01"))
    _record("A7 weekend/before returns next", got7b >= target, str(got7b))
    got7c = nearest_trade_date(s7, pd.Timestamp("2030-01-01"))
    _record("A7 beyond range returns None",   got7c is None, str(got7c))

    # ── A8: calculate_annual_dividends ────────────────────────────────────────
    print("\n── A8: calculate_annual_dividends ──")
    divs = pd.Series(
        [0.5, 0.5, 0.6, 0.6],
        index=pd.to_datetime(["2020-03-01","2020-09-01","2021-03-01","2021-09-01"])
    )
    adf = calculate_annual_dividends(divs)
    _record("A8 two years in output",   len(adf) == 2, str(adf["Year"].tolist()))
    _record("A8 2020 total = 1.0",      abs(float(adf[adf["Year"]==2020]["Dividend per Share"]) - 1.0) < 1e-9)
    _record("A8 2021 total = 1.2",      abs(float(adf[adf["Year"]==2021]["Dividend per Share"]) - 1.2) < 1e-9)

    # ── A9: empty series edge cases ───────────────────────────────────────────
    print("\n── A9: Edge cases (empty / 1-point) ──")
    _record("A9 empty series returns []",    find_alternating_high_low(pd.Series(dtype=float)) == [])
    _record("A9 1-point series returns list", isinstance(find_alternating_high_low(_series([100])), list))
    status_empty = build_current_status(pd.Series(dtype=float), trigger_pct=10.0)
    _record("A9 build_current_status on empty returns dict", isinstance(status_empty, dict))


# ─────────────────────────────────────────────────────────────────────────────
# PART B — Real-ticker self-consistency (requires network)
# ─────────────────────────────────────────────────────────────────────────────

def test_real_tickers() -> None:
    print("\n" + "="*60)
    print("  PART B — Real-Ticker Self-Consistency")
    print("="*60)

    try:
        import yfinance as yf
        from global_cup.data_loader import download_price, download_dividends, get_close_series
        from global_cup.market_config import UserInput
        from global_cup.analysis import run_analysis
    except ImportError as e:
        print(f"  SKIP (import error: {e})")
        return

    TICKERS = ["VOO", "SCHD", "JEPI", "360750.KS", "441680.KS"]
    START   = date(2020, 1, 1)
    END     = date(2024, 12, 31)

    for ticker in TICKERS:
        print(f"\n  Ticker: {ticker}")
        inp = UserInput(
            market_key="United States", ticker_label=ticker,
            ticker=ticker, trigger_pct=10.0,
            start_date=START, end_date=END,
        )
        try:
            result = run_analysis(inp)
        except Exception as e:
            print(f"    SKIP (download error: {e})")
            continue

        if result is None:
            print(f"    SKIP (no data)")
            continue

        # Self-consistency checks
        _record(f"[{ticker}] current_price > 0",
                result.current_price > 0, f"{result.current_price:.2f}")
        _record(f"[{ticker}] zigzag_ref_high_price ≥ current_price",
                result.zigzag_ref_high_price >= result.current_price - 1e-6,
                f"ref_high={result.zigzag_ref_high_price:.2f} cur={result.current_price:.2f}")
        _record(f"[{ticker}] zigzag_ref_high_price ≥ zigzag_ref_low_price",
                result.zigzag_ref_high_price >= result.zigzag_ref_low_price - 1e-6,
                f"high={result.zigzag_ref_high_price:.2f} low={result.zigzag_ref_low_price:.2f}")
        _record(f"[{ticker}] zigzag_drawdown_pct ≤ 0",
                result.zigzag_drawdown_pct <= 0.001,
                f"{result.zigzag_drawdown_pct:.2f}%")
        _record(f"[{ticker}] trigger_hit matches drawdown",
                result.zigzag_trigger_hit == (result.zigzag_drawdown_pct <= -10.0),
                f"dd={result.zigzag_drawdown_pct:.2f}% hit={result.zigzag_trigger_hit}")
        _record(f"[{ticker}] drop_bucket non-empty",
                bool(result.drop_bucket), result.drop_bucket)
        _record(f"[{ticker}] status_label non-empty",
                bool(result.status_label), result.status_label)
        _record(f"[{ticker}] H/L alternate strictly",
                all(result.zigzag_points[i].point_type != result.zigzag_points[i+1].point_type
                    for i in range(len(result.zigzag_points)-1)),
                f"types={[p.point_type for p in result.zigzag_points]}")


# ─────────────────────────────────────────────────────────────────────────────
# PART C — Dividend reinvestment comparison (original vs refactored)
# ─────────────────────────────────────────────────────────────────────────────

def test_dividend_reinvest() -> None:
    print("\n" + "="*60)
    print("  PART C — Dividend Reinvest: original vs refactored")
    print("="*60)

    try:
        import yfinance as yf
        from global_cup.data_loader import download_price, download_dividends, get_close_series
        from global_cup.backtest_engine import run_dividend_reinvest_backtest
    except ImportError as e:
        print(f"  SKIP (import error: {e})")
        return

    TICKERS = ["VOO", "SCHD", "JEPI"]
    START   = date(2020, 1, 1)
    END     = date(2024, 12, 31)
    INIT    = 10_000.0
    MONTHLY = 0.0
    TAX     = 15.0

    def _orig_reinvest(close, dividends, init, monthly, tax_pct):
        """Inline copy of original run_dividend_reinvest_backtest logic."""
        import pandas as pd
        from datetime import date as _date
        close = close.dropna().copy()
        if close.empty or init <= 0:
            return None
        close.index = pd.to_datetime(close.index).tz_localize(None)
        dividends = dividends.copy()
        if not dividends.empty:
            dividends.index = pd.to_datetime(dividends.index).tz_localize(None)
            dividends = dividends[(dividends.index >= close.index[0]) &
                                  (dividends.index <= close.index[-1])]
            dividends = dividends.sort_index().astype(float)
        tax_rate = max(0.0, min(100.0, float(tax_pct))) / 100.0
        monthly_buy_dates = set()
        months = sorted(set((d.year, d.month) for d in close.index))
        for y, m in months:
            first = close.index[close.index >= pd.Timestamp(_date(y, m, 1))]
            if len(first) > 0:
                d = pd.Timestamp(first[0])
                if d != close.index[0] and monthly > 0:
                    monthly_buy_dates.add(d)
        div_by_trade = {}
        for div_date, div_ps in dividends.items():
            idx2 = close.index[close.index >= pd.Timestamp(div_date)]
            if len(idx2) == 0:
                continue
            td = pd.Timestamp(idx2[0])
            div_by_trade.setdefault(td, []).append((pd.Timestamp(div_date), float(div_ps)))
        shares = cum_gross = cum_tax = cum_net = total_ext = 0.0
        for d, price in close.items():
            d = pd.Timestamp(d); price = float(price)
            if d == close.index[0]:
                shares += init / price if price > 0 else 0.0
                total_ext += init
            if d in monthly_buy_dates:
                shares += monthly / price if price > 0 else 0.0
                total_ext += monthly
            for _, div_ps in div_by_trade.get(d, []):
                if shares <= 0 or div_ps <= 0: continue
                gross = shares * div_ps; tax = gross * tax_rate; net = gross - tax
                shares += net / price if price > 0 else 0.0
                cum_gross += gross; cum_tax += tax; cum_net += net
        final_price = float(close.iloc[-1])
        final_value = shares * final_price
        days = max((close.index[-1] - close.index[0]).days, 1)
        years = days / 365.25
        cagr = ((final_value / total_ext)**(1/years) - 1)*100 if total_ext > 0 and final_value > 0 else 0.0
        return {"final_value": final_value, "total_ext": total_ext,
                "shares": shares, "cum_gross": cum_gross, "cum_tax": cum_tax,
                "cum_net": cum_net, "cagr": cagr}

    def _near(a, b, tol=1e-6):
        denom = max(abs(a), abs(b), 1e-12)
        return abs(a - b) / denom < tol

    for ticker in TICKERS:
        print(f"\n  Ticker: {ticker}")
        try:
            price_df = download_price(ticker, START, END)
            if price_df.empty:
                print("    SKIP (no price data)")
                continue
            close    = get_close_series(price_df)
            dividends = download_dividends(ticker, START, END)
        except Exception as e:
            print(f"    SKIP ({e})")
            continue

        orig = _orig_reinvest(close, dividends, INIT, MONTHLY, TAX)
        ref  = run_dividend_reinvest_backtest(close, dividends, INIT, MONTHLY, TAX)

        if orig is None or ref is None:
            print("    SKIP (None result)")
            continue

        s = ref.summary
        _record(f"[{ticker}] reinvest.final_value",
                _near(orig["final_value"], s["Final Portfolio Value"]))
        _record(f"[{ticker}] reinvest.cum_net",
                _near(orig["cum_net"], s["Cumulative Net Dividend"]))
        _record(f"[{ticker}] reinvest.cagr",
                _near(orig["cagr"], s["CAGR %"]))


# ─────────────────────────────────────────────────────────────────────────────
# PART D — Threshold propagation
# ─────────────────────────────────────────────────────────────────────────────

def test_threshold_propagation() -> None:
    print("\n" + "="*60)
    print("  PART D — Threshold Propagation (trigger_pct → threshold)")
    print("="*60)

    divs_empty = pd.Series(dtype=float)

    # Series with 7%-ish swings (between 5% and 10%)
    # threshold=0.05: multiple H/L detected
    # threshold=0.10: no qualifying multi-pivot → single in-progress point only
    s7 = _series([100, 107, 99, 106, 98, 105])

    print("\n── D1: 7%-swing series: threshold=0.05 detects multiple H/L ──")
    pts05 = find_alternating_high_low(s7, threshold=0.05)
    h05 = [p for p in pts05 if p.point_type == "H"]
    l05 = [p for p in pts05 if p.point_type == "L"]
    _record("D1 threshold=0.05: high_count ≥ 2",
            len(h05) >= 2, f"high_count={len(h05)}")
    _record("D1 threshold=0.05: low_count ≥ 2",
            len(l05) >= 2, f"low_count={len(l05)}")

    print("\n── D2: 7%-swing series: threshold=0.10 detects fewer H/L ──")
    pts10 = find_alternating_high_low(s7, threshold=0.10)
    h10 = [p for p in pts10 if p.point_type == "H"]
    _record("D2 threshold=0.10: high_count < threshold=0.05 high_count",
            len(h10) < len(h05),
            f"0.05_highs={len(h05)} 0.10_highs={len(h10)}")

    print("\n── D3: build_current_status respects explicit threshold ──")
    st05 = build_current_status(s7, trigger_pct=5.0,  threshold=0.05)
    st10 = build_current_status(s7, trigger_pct=10.0, threshold=0.10)
    _record("D3 trigger_pct=5 (threshold=0.05): high_count ≥ 2",
            st05["high_count"] >= 2, f"high_count={st05['high_count']}")
    _record("D3 trigger_pct=10 (threshold=0.10): high_count < trigger_pct=5 result",
            st10["high_count"] < st05["high_count"],
            f"5%={st05['high_count']} 10%={st10['high_count']}")

    print("\n── D4: Bug demo — omitting threshold collapses to default 0.05 ──")
    st10_buggy = build_current_status(s7, trigger_pct=10.0)           # default=0.05
    st10_fixed = build_current_status(s7, trigger_pct=10.0, threshold=0.10)
    _record("D4 bug: default threshold gives same count as threshold=0.05",
            st10_buggy["high_count"] == st05["high_count"],
            f"buggy={st10_buggy['high_count']} should_match={st05['high_count']}")
    _record("D4 fix: explicit threshold=0.10 gives different count",
            st10_fixed["high_count"] != st10_buggy["high_count"],
            f"fixed={st10_fixed['high_count']} buggy={st10_buggy['high_count']}")

    print("\n── D5: run_backtest accepts threshold parameter ──")
    bt05 = run_backtest(s7, divs_empty, trigger_pct=5.0,  threshold=0.05)
    bt10 = run_backtest(s7, divs_empty, trigger_pct=10.0, threshold=0.10)
    _record("D5 run_backtest threshold=0.05 returns DataFrame",
            isinstance(bt05, pd.DataFrame), f"type={type(bt05).__name__}")
    _record("D5 run_backtest threshold=0.10 returns DataFrame",
            isinstance(bt10, pd.DataFrame), f"type={type(bt10).__name__}")

    print("\n── D6: 25%-swing series (threshold 0.20 vs 0.30) ──")
    # Swings of 25%: qualifies at 0.20, not at 0.30
    s25 = _series([100, 125, 96, 125, 96])
    h20 = [p for p in find_alternating_high_low(s25, threshold=0.20) if p.point_type == "H"]
    h30 = [p for p in find_alternating_high_low(s25, threshold=0.30) if p.point_type == "H"]
    _record("D6 threshold=0.20: high_count ≥ 2 (25%-swing qualifies)",
            len(h20) >= 2, f"high_count={len(h20)}")
    _record("D6 threshold=0.30: high_count < threshold=0.20 (25% < 30%)",
            len(h30) < len(h20),
            f"0.20_highs={len(h20)} 0.30_highs={len(h30)}")

    print("\n── D7: trigger_pct coverage (5, 10, 20, 30) — no false triggers ──")
    # Monotonic: no trigger hit at any threshold
    s_mono = _series([100 + i for i in range(50)])
    for tp in [5, 10, 20, 30]:
        th = tp / 100.0
        st = build_current_status(s_mono, trigger_pct=float(tp), threshold=th)
        _record(f"D7 trigger_pct={tp:2d} (threshold={th:.2f}): no trigger on monotonic",
                not st["trigger_hit"],
                f"status={st['status_label']} dd={st['drawdown_pct']:.2f}%")

    print("\n── D8: trigger_hit varies correctly with trigger_pct ──")
    # [100, 110, 104]: ZigZag high at 110 (at threshold=0.05), current=104, dd=-5.45%
    # trigger_pct=5 → trigger_hit = -5.45 <= -5 → True
    # trigger_pct=10 → trigger_hit = -5.45 <= -10 → False
    s_hit = _series([100, 110, 104])
    for tp, expect in [(5, True), (10, False), (20, False), (30, False)]:
        th = tp / 100.0
        st = build_current_status(s_hit, trigger_pct=float(tp), threshold=th)
        _record(f"D8 trigger_pct={tp:2d}: trigger_hit={'True ' if expect else 'False'} (dd≈-5.45%)",
                st["trigger_hit"] == expect,
                f"dd={st['drawdown_pct']:.2f}% hit={st['trigger_hit']}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    test_synthetic()
    test_real_tickers()
    test_dividend_reinvest()
    test_threshold_propagation()

    total  = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = total - passed

    print(f"\n{'='*60}")
    print("  VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"  Checks passed: {passed}/{total}")

    if failed == 0 and total > 0:
        print("\n  ✅  ALL CHECKS PASSED")
        print("  PHASE_5: PASS")
        sys.exit(0)
    elif total == 0:
        print("\n  ⚠️   NO CHECKS RAN")
        sys.exit(2)
    else:
        print(f"\n  ❌  {failed} CHECK(S) FAILED")
        for r in RESULTS:
            if r["status"] == "FAIL":
                print(f"       FAIL: {r['label']}")
        print("  PHASE_5: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
