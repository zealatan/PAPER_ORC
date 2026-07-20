"""
빡센 검증 — how much can we trust the FIRE engine?

Four independent kinds of checks (not "does the logic match its own spec", but
"is the result actually correct / the data actually right / the money conserved"):

  1. CLOSED-FORM   — recompute the answer with engine-independent math and require
                     penny agreement (no-div buy&hold; div-as-cash buy&hold;
                     withdrawal-no-div depletion).
  2. CONSERVATION  — from the timeline alone verify the exact identity
                     V_final = corpus + Σ net_div − Σ withdrawn + Σ market_PnL.
                     (money is neither created nor destroyed)
  3. DATA          — yfinance KO dividends vs published record; KO 2012 2:1 split
                     is back-adjusted consistently (no 2x jump).
  4. INVARIANTS    — random scenarios: shares/cash never negative, withdrawals
                     fully paid unless depleted, value stays 0 after depletion.

Run:
  PYB=/home/zealatan/.pyenv/versions/3.11.8/bin/python3.11
  SP=/home/zealatan/YOUTUBE/blog/global_cup_refactored/.venv/lib/python3.11/site-packages
  PYTHONPATH=$SP:. $PYB validate_fire.py
"""
from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import yfinance as yf

from global_cup.fire_engine import run_fire_backtest

TAX = 15.0
_P, _F = 0, 0  # pass / fail counters


def check(name, cond, detail=""):
    global _P, _F
    ok = bool(cond)
    _P += ok; _F += (not ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  · {detail}" if detail else ""))


def rel(a, b):
    return abs(a - b) / max(abs(b), 1e-9)


def close_enough(a, b, rtol=1e-6, atol=1e-3):
    """Pass on either relative OR absolute agreement (handles a≈b≈0)."""
    return abs(a - b) <= atol or rel(a, b) < rtol


def load(tk, start="1990-01-01"):
    df = yf.download(tk, start=start, auto_adjust=False, progress=False, threads=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    close = pd.to_numeric(df["Close"], errors="coerce").dropna()
    close.index = pd.to_datetime(close.index).tz_localize(None)
    d = yf.Ticker(tk).dividends
    d.index = pd.to_datetime(d.index).tz_localize(None)
    return close, d.astype(float)


def net_div_to_cash(close, div, shares_const, start):
    """Σ net dividends if share count were constant (for the div-as-cash case)."""
    c = close[close.index >= pd.Timestamp(start)]
    dd = div[(div.index >= c.index[0]) & (div.index <= c.index[-1])]
    total = 0.0
    for ex, dps in dd.items():
        nxt = c.index[c.index >= ex]
        if len(nxt):
            total += shares_const * float(dps) * (1 - TAX / 100)
    return total


# ══ 1. CLOSED-FORM ═══════════════════════════════════════════════════════════════
def test_closed_form():
    print("\n1. CLOSED-FORM (engine vs independent math, penny agreement)")
    start = date(2000, 1, 1)

    # (a) no-dividend buy&hold: final == corpus * end/buy exactly
    close, div = load("BRK-B", "1997-01-01")
    r = run_fire_backtest(close, div, 100_000.0, annual_withdrawal=0.0,
                          reinvest_surplus=False, start_date=start)
    c = close[close.index >= pd.Timestamp(start)]
    expected = 100_000.0 * float(c.iloc[-1]) / float(c.iloc[0])
    check("BRK-B no-div buy&hold = corpus·end/buy", rel(r.summary["Final Value"], expected) < 1e-9,
          f"engine {r.summary['Final Value']:.2f} vs {expected:.2f}")
    check("BRK-B shares constant (no div/withdrawal)",
          rel(r.summary["Final Shares"], 100_000.0/float(c.iloc[0])) < 1e-9)

    # (b) div-as-cash buy&hold: final == shares0*end + Σ net_div, shares constant
    close, div = load("KO", "1999-01-01")
    r = run_fire_backtest(close, div, 100_000.0, annual_withdrawal=0.0,
                          reinvest_dividends=False, reinvest_surplus=False, start_date=start)
    c = close[close.index >= pd.Timestamp(start)]
    shares0 = 100_000.0 / float(c.iloc[0])
    expected = shares0 * float(c.iloc[-1]) + net_div_to_cash(close, div, shares0, start)
    check("KO div-as-cash buy&hold = shares0·end + Σnet_div",
          rel(r.summary["Final Value"], expected) < 1e-9,
          f"engine {r.summary['Final Value']:.2f} vs {expected:.2f}")
    check("KO shares constant when div not reinvested",
          rel(r.summary["Final Shares"], shares0) < 1e-9)

    # (c) withdrawal, no dividend: independent monthly-sell recompute
    close, div = load("BRK-B", "1997-01-01")
    exp_mo = 500.0
    r = run_fire_backtest(close, div, 100_000.0, annual_withdrawal=exp_mo*12,
                          reinvest_surplus=False, start_date=start)
    c = close[close.index >= pd.Timestamp(start)]
    # replay: first trade day of each month after buy sells exp_mo worth
    shares = 100_000.0 / float(c.iloc[0])
    months = {}
    for d in c.index:
        months.setdefault((d.year, d.month), d)
    buy = c.index[0]
    depleted_date = None
    for (y, m), d0 in sorted(months.items()):
        if d0 <= buy:
            continue
        px = float(c.loc[d0])
        if shares * px >= exp_mo:
            shares -= exp_mo / px
        else:
            shares = 0.0; depleted_date = d0; break
    ind_final = shares * float(c.iloc[-1]) if depleted_date is None else 0.0
    check("BRK-B withdrawal (no div) final matches independent sell-sim",
          rel(r.summary["Final Value"], ind_final) < 1e-6,
          f"engine {r.summary['Final Value']:.2f} vs {ind_final:.2f}")
    eng_dep = None if r.summary["Survived"] else pd.Timestamp(r.summary["Depletion Date"])
    check("BRK-B depletion status matches",
          (depleted_date is None) == (eng_dep is None),
          f"engine dep={eng_dep} ind dep={depleted_date}")


# ══ 2. CONSERVATION ═════════════════════════════════════════════════════════════
def test_conservation():
    print("\n2. CONSERVATION (V_final = corpus + Σnet_div − Σwithdrawn + market_PnL)")
    close, div = load("KO", "1999-01-01")
    for exp_mo, reinv in [(1500.0, True), (600.0, True), (0.0, False)]:
        r = run_fire_backtest(close, div, 300_000.0, annual_withdrawal=exp_mo*12,
                              reinvest_surplus=reinv, start_date=date(2000, 1, 1))
        tl = r.timeline_df
        # market P&L from the timeline: shares held overnight × price change
        px = tl["Price"].to_numpy()
        sh = tl["Shares"].to_numpy()
        market_pnl = float(np.sum(sh[:-1] * (px[1:] - px[:-1])))
        corpus = 300_000.0
        net_div = r.summary["Total Net Dividend"]
        withdrawn = r.summary["Total Withdrawn"]
        lhs = r.summary["Final Value"]
        rhs = corpus + net_div - withdrawn + market_pnl
        check(f"conservation exp=${exp_mo:.0f} reinvest={reinv}", close_enough(lhs, rhs),
              f"V_final {lhs:,.2f} vs identity {rhs:,.2f}  (Δ={lhs-rhs:+.4f})")


# ══ 3. DATA ═════════════════════════════════════════════════════════════════════
def test_data():
    print("\n3. DATA (yfinance vs reality)")
    close, div = load("KO", "1999-01-01")
    # KO published gross dividend/share per calendar year (declared totals)
    known = {2019: 1.60, 2020: 1.64, 2021: 1.68, 2022: 1.76, 2023: 1.84, 2024: 1.94}
    yr = div.groupby(div.index.year).sum()
    for y, v in known.items():
        got = float(yr.get(y, 0.0))
        # allow small slack for ex-date-year vs declared-year boundary shifts
        check(f"KO {y} dividends ≈ ${v}", abs(got - v) <= 0.06, f"yf sum ${got:.4f}")

    # 2012-08-13 2:1 split must be back-adjusted: no ~2x jump in raw close
    around = close[(close.index >= "2012-08-06") & (close.index <= "2012-08-20")]
    ratios = around.to_numpy()[1:] / around.to_numpy()[:-1]
    check("KO 2012 split back-adjusted (no 2x jump in close)",
          float(np.max(np.abs(ratios - 1))) < 0.10,
          f"max |daily ratio-1| = {float(np.max(np.abs(ratios-1))):.3f}")
    # dividends also split-adjusted: pre-split dps should be small (post-split scale)
    pre = div[(div.index >= "2012-01-01") & (div.index < "2012-08-13")]
    post = div[(div.index >= "2012-08-13") & (div.index < "2013-06-01")]
    if len(pre) and len(post):
        check("KO dividend per share split-adjusted (pre≈post scale)",
              rel(float(pre.mean()), float(post.mean())) < 0.30,
              f"pre ${float(pre.mean()):.3f} vs post ${float(post.mean()):.3f}")


# ══ 4. INVARIANTS ═══════════════════════════════════════════════════════════════
def test_invariants():
    print("\n4. INVARIANTS (random scenarios)")
    tickers = ["KO", "O", "AAPL", "JNJ", "SCHD", "MSFT", "PG", "T", "XOM", "VZ"]
    rng = np.random.default_rng(12345)
    n_ok = 0
    fails = []
    for i in range(24):
        tk = tickers[i % len(tickers)]
        yr = int(rng.integers(2005, 2018))
        corpus = float(rng.integers(100, 900) * 1000)
        exp_mo = float(rng.integers(0, 60) * 100)
        close, div = load(tk, f"{yr-1}-01-01")
        r = run_fire_backtest(close, div, corpus, annual_withdrawal=exp_mo*12,
                              reinvest_surplus=True, start_date=date(yr, 1, 1))
        if r is None:
            continue
        tl = r.timeline_df
        ok = True; why = ""
        if (tl["Shares"] < -1e-6).any(): ok, why = False, "negative shares"
        elif (tl["Cash"] < -1e-6).any(): ok, why = False, "negative cash"
        elif (tl["Portfolio Value"] < -1e-6).any(): ok, why = False, "negative value"
        # withdrawals fully paid unless depleted
        if ok and r.summary["Survived"] and not r.withdrawal_df.empty:
            wd = r.withdrawal_df
            unpaid = (wd["Requested"] - wd["Paid Out"] > 1e-3) & (~wd["Depleted"])
            if unpaid.any(): ok, why = False, "underpaid while solvent"
        # after depletion, value stays ~0
        if ok and not r.summary["Survived"]:
            dep = pd.Timestamp(r.summary["Depletion Date"])
            after = tl[tl["Date"] > dep]["Portfolio Value"]
            if len(after) and float(after.abs().max()) > 1e-3:
                ok, why = False, "value revived after depletion"
        n_ok += ok
        if not ok:
            fails.append(f"{tk} {yr} corpus={corpus:.0f} exp={exp_mo:.0f}: {why}")
    check(f"24 random scenarios hold all invariants", not fails,
          f"{n_ok}/24 ok" + ("" if not fails else " · " + "; ".join(fails[:3])))


def main():
    print("=" * 80)
    print("FIRE ENGINE — RIGOROUS VALIDATION")
    print("=" * 80)
    test_closed_form()
    test_conservation()
    test_data()
    test_invariants()
    print("\n" + "=" * 80)
    print(f"RESULT: {_P} passed, {_F} failed")
    print("=" * 80)


if __name__ == "__main__":
    main()
