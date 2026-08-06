"""
validate_fire_inflation.py
==========================
FIRE 물가 반영(strategy="fixed_real") 로버스트 검증 — 합성 데이터, 네트워크 불필요.

fire_page.py의 "물가 반영 (실질 인출)" 토글이 엔진에 넘기는 fixed_real 경로를 검증한다.
켜지면 은퇴 시작일=1.0 기준 합성 CPI로 인출액을 매 시점 물가만큼 인상(구매력 고정).

Run from global_cup_suite/ (repo 루트, validate_fire.py와 동일 방식):
    python -m _validation.validate_fire_inflation

검증 항목:
  A. 명목 고정 앵커         — 배당 0·가격 평평이면 Total Withdrawn == 월×개월 정확
  B. fixed_real 폐쇄형 일치  — 각 인출 == 월생활비 × asof(cpi,d)/cpi_base, 오차 0
                              (엔진은 cpi_base를 buy_date=은퇴시작에 앵커 → 1.0)
  C. rate=0 ≡ fixed_nominal — all-ones CPI는 명목과 동일
  D. 단조성                 — 물가율↑ → 총인출↑ & 생존연수↓
  E. 판정 뒤집힘            — 명목=생존인 corpus가 물가 반영 시 고갈로 전환
  F. 다종목 바스켓 · 초단기 창
"""
import sys
from datetime import date

import numpy as np
import pandas as pd

from global_cup.fire_engine import run_fire_backtest_multi, AssetSpec

IDX = pd.date_range("2000-01-01", "2020-01-01", freq="B")
START, END = date(2000, 1, 1), date(2020, 1, 1)

_P = _F = 0


def check(name, cond, detail=""):
    global _P, _F
    if cond:
        _P += 1
        print(f"  ✅ PASS  {name}" + (f"  —  {detail}" if detail else ""))
    else:
        _F += 1
        print(f"  ❌ FAIL  {name}" + (f"  —  {detail}" if detail else ""))


def make_cpi(rate_pct, start=START, end=END):
    """fire_page.py와 동일한 합성 CPI 생성 로직 (은퇴 시작일 앵커=1.0)."""
    if rate_pct <= 0:
        return None
    midx = pd.date_range(pd.Timestamp(start), pd.Timestamp(end), freq="MS").union([pd.Timestamp(start)])
    yrs = (midx - pd.Timestamp(start)) / pd.Timedelta(days=365.25)
    return pd.Series((1.0 + rate_pct / 100.0) ** yrs.values, index=midx)


def asof(series, when):
    sub = series[series.index <= when]
    return float(sub.iloc[-1]) if len(sub) else float(series.iloc[0])


def flat_asset(price=100.0, weight=100.0):
    return AssetSpec("Test", "TST", pd.Series(price, index=IDX), pd.Series(dtype=float), weight)


def run(strategy, corpus, monthly, cpi=None, assets=None, end=END):
    return run_fire_backtest_multi(
        assets or [flat_asset()], initial_amount=corpus,
        annual_withdrawal=monthly * 12, frequency="monthly", tax_rate_pct=0.0,
        reinvest_surplus=False, strategy=strategy, cpi=cpi,
        start_date=START, end_date=end)


def main():
    print("=" * 72)
    print("FIRE 물가 반영(fixed_real) — 로버스트 검증")
    print("=" * 72)

    print("\n── A. 명목 고정 앵커 (배당 0·가격 평평 → 인출=순매도) ──")
    nom = run("fixed_nominal", 10_000_000, 1_000)
    check("명목 Total Withdrawn == 월×개월 정확", abs(nom.summary["Total Withdrawn"] - 240_000) < 1e-6,
          f"{nom.summary['Total Withdrawn']:,.2f}")

    print("\n── B. fixed_real 인출액 == 폐쇄형 (비고갈) ──")
    cpi = make_cpi(2.5)
    real = run("fixed_real", 10_000_000, 1_000, cpi=cpi)
    wd = real.timeline_df[real.timeline_df["Withdrawal"] > 1e-9][["Date", "Withdrawal"]]
    cpi_base = asof(cpi, pd.Timestamp(START))   # 엔진과 동일: buy_date(=은퇴 시작) 앵커
    expected = [1_000 * asof(cpi, pd.Timestamp(d)) / cpi_base for d in wd["Date"]]
    max_err = float(np.max(np.abs(np.array(expected) - wd["Withdrawal"].values)))
    check("모든 인출 기간 == 월×CPI비율 (폐쇄형)", max_err < 1e-6, f"max abs err={max_err:.2e}")
    check("cpi_base == 1.0 (은퇴 시작 앵커)", abs(cpi_base - 1.0) < 1e-9, f"cpi_base={cpi_base:.8f}")
    check("첫 인출 == 폐쇄형 기대(≈1002, 1개월 물가 반영)", abs(wd["Withdrawal"].iloc[0] - expected[0]) < 1e-6,
          f"{wd['Withdrawal'].iloc[0]:.4f}")
    check("마지막 인출 > 첫 인출 (물가로 증가)", wd["Withdrawal"].iloc[-1] > wd["Withdrawal"].iloc[0] * 1.4,
          f"{wd['Withdrawal'].iloc[0]:.1f} → {wd['Withdrawal'].iloc[-1]:.1f}")
    check("real Total Withdrawn == Σ 기대인출", abs(real.summary["Total Withdrawn"] - sum(expected)) < 1e-4,
          f"{real.summary['Total Withdrawn']:,.2f}")

    print("\n── C. rate=0 이면 fixed_real ≡ fixed_nominal ──")
    check("make_cpi(0) is None (→ 앱이 fixed_nominal 사용)", make_cpi(0.0) is None)
    ones = pd.Series(1.0, index=make_cpi(2.5).index)
    real0 = run("fixed_real", 10_000_000, 1_000, cpi=ones)
    check("all-ones CPI real == nominal",
          abs(real0.summary["Total Withdrawn"] - nom.summary["Total Withdrawn"]) < 1e-6)

    print("\n── D. 단조성: 물가율↑ → 총인출↑ & 생존연수↓ ──")
    rows = []
    for r in [0.0, 2.0, 4.0, 8.0, 15.0]:
        strat = "fixed_real" if r > 0 else "fixed_nominal"
        s = run(strat, 300_000, 1_000, cpi=make_cpi(r)).summary
        rows.append((s["Total Withdrawn"], s["Survived Years"]))
        print(f"     물가 {r:4.1f}% → 총인출 {s['Total Withdrawn']:>10,.0f} · 생존 {s['Survived Years']:5.1f}년")
    tw = [x[0] for x in rows]
    sy = [x[1] for x in rows]
    check("총인출 단조 증가", all(tw[i] <= tw[i + 1] + 1e-6 for i in range(len(tw) - 1)))
    check("생존연수 단조 감소(비증가)", all(sy[i] >= sy[i + 1] - 1e-6 for i in range(len(sy) - 1)))

    print("\n── E. 판정 뒤집힘: 명목=생존, 물가반영=고갈 ──")
    flip = None
    for corpus in range(240_000, 340_000, 5_000):
        n = run("fixed_nominal", corpus, 1_000)
        rr = run("fixed_real", corpus, 1_000, cpi=make_cpi(2.5))
        if n.summary["Survived"] and not rr.summary["Survived"]:
            flip = (corpus, rr.summary["Survived Years"])
            break
    check("명목=생존 & 물가반영=고갈 corpus 존재", flip is not None,
          f"corpus={flip[0]:,} → 물가반영 시 {flip[1]:.1f}년 후 고갈" if flip else "못 찾음")

    print("\n── F. 다종목 바스켓 + 초단기 창 ──")
    multi = run("fixed_real", 5_000_000, 1_000, cpi=make_cpi(3.0),
                assets=[flat_asset(100, 60), flat_asset(50, 40)])
    check("다종목 바스켓 정상 실행", multi is not None and multi.summary["Total Withdrawn"] > 0)
    short = run("fixed_real", 1_000_000, 1_000, cpi=make_cpi(2.5, START, date(2000, 3, 1)),
                end=date(2000, 3, 1))
    check("2개월 초단기 창도 예외 없이 실행", short is not None)

    print("\n" + "=" * 72)
    print(f"RESULT: {_P} passed, {_F} failed")
    print("=" * 72)
    sys.exit(1 if _F else 0)


if __name__ == "__main__":
    main()
