# -*- coding: utf-8 -*-
"""A단계 백테스트 → spec/STOCK_ALERT.json 되채움.
   2부(파산 시나리오): FIRE 그리드 원금[200k,400k,600k] × 월인출[1k,2k,3k] × 전략[nominal,real].
   gen_fire_corpus.py(코카콜라 골든) 패턴을 STOCK_ALERT로 이식. 데이터는 엔진, 대본은 인용.
   사용: python spec/gen_backtest.py
"""
import json, sys
from datetime import date
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent          # blog/STOCK_ALERT
sys.path.insert(0, str(ROOT.parent.parent / "global_cup_suite"))  # global_cup 패키지
from global_cup.fire_engine import run_fire_backtest

DATA = ROOT / "data"
REF = ROOT / "ref"

# ── 데이터 로드 (무수정 종가 + ex-date 배당 + 미국 CPI) ──
close = pd.read_csv(DATA / "stock_alert_price.csv", parse_dates=["date"]).set_index("date")["close"]
div   = pd.read_csv(DATA / "stock_alert_div.csv",   parse_dates=["date"]).set_index("date")["div"]
close.index = pd.to_datetime(close.index).tz_localize(None)
div.index   = pd.to_datetime(div.index).tz_localize(None)
cpi_df = pd.read_csv(REF / "fred_CPIAUCSL.csv", parse_dates=["date"])
uscpi = pd.Series(pd.to_numeric(cpi_df["val"], errors="coerce").values, index=cpi_df["date"]).dropna()

START = date(2000, 1, 1)
INITS = [200_000, 400_000, 600_000]
MONTHLIES = [1000, 2000, 3000]
STRATS = [("nominal", "fixed_nominal"), ("real", "fixed_real")]


def to_year(d):
    y0 = pd.Timestamp(d.year, 1, 1); y1 = pd.Timestamp(d.year + 1, 1, 1)
    return round(d.year + (d - y0).days / (y1 - y0).days, 2)


def run(init, mo, strat, start=None):
    return run_fire_backtest(
        close, div, init, annual_withdrawal=mo * 12, strategy=strat, frequency="monthly",
        tax_rate_pct=15.0, reinvest_dividends=False, reinvest_surplus=True,
        cpi=(uscpi if strat == "fixed_real" else None), start_date=(start or START))


def scenario(init, mo, strat_key, strat, start=None, id_prefix=None):
    r = run(init, mo, strat, start)
    s = r.summary
    # 자산궤적: 월말 리샘플 후 3개월 간격 [연,값]
    tl = r.timeline_df.copy()
    tl["Date"] = pd.to_datetime(tl["Date"]); tl["ym"] = tl["Date"].dt.to_period("M")
    m = tl.groupby("ym").last().reset_index(drop=True)
    pts = [[to_year(x["Date"]), round(x["Portfolio Value"])] for _, x in m.iloc[::3].iterrows()]
    last = [to_year(m.iloc[-1]["Date"]), round(m.iloc[-1]["Portfolio Value"])]
    if pts[-1][0] != last[0]:
        pts.append(last)
    dep = s["Depletion Date"]
    if not s["Survived"] and dep is not None:
        yr = to_year(pd.Timestamp(dep))
        pts = [p for p in pts if p[0] <= yr]
        pts.append([yr, 0])
    return {
        "id": f"{id_prefix or strat_key}_{init}_{mo}",
        "strategy": strat_key, "init": init, "monthly": mo,
        "survived": bool(s["Survived"]),
        "final": round(s["Final Value"]),
        "final_real": round(s["Final Value Real"]),
        "depletion": (dep.strftime("%Y-%m") if dep is not None else None),
        "max_drawdown_pct": round(s["Max Drawdown %"], 1),
        "total_withdrawn": round(s["Total Withdrawn"]),
        "pts": pts,
    }


scenarios = []
print(f"{'전략':>8} {'원금':>9} | {'월$1k':>16} {'월$2k':>16} {'월$3k':>16}")
for strat_key, strat in STRATS:
    for init in INITS:
        row = []
        for mo in MONTHLIES:
            sc = scenario(init, mo, strat_key, strat)
            scenarios.append(sc)
            row.append(f"생존 ${sc['final']:,}" if sc["survived"] else f"파산 {sc['depletion']}")
        print(f"{strat_key:>8} ${init:>7,} | {row[0]:>16} {row[1]:>16} {row[2]:>16}")

# ── 닷컴버블 저점 은퇴(2002) real 시나리오 (전후 비교용) ──
from datetime import date as _date
START2002 = _date(2002, 1, 1)
print("\n[닷컴버블 저점 2002년 은퇴 · 물가반영]")
for init in INITS:
    row = []
    for mo in MONTHLIES:
        sc = scenario(init, mo, "real", "fixed_real", start=START2002, id_prefix="real2002")
        scenarios.append(sc)
        row.append(f"생존 ${sc['final']:,}" if sc["survived"] else f"파산 {sc['depletion']}")
    print(f"real2002 ${init:>7,} | {row[0]:>16} {row[1]:>16} {row[2]:>16}")

# ── 월봉 가격 / 연배당 (spec.data 참고용) ──
mp = close.resample("ME").last().dropna()
monthly_price = [[d.strftime("%Y-%m"), round(v, 2)] for d, v in mp.items()]
ann = div.groupby(div.index.year).sum()
annual_div = [[int(y), round(v, 4)] for y, v in ann.items()]

# ── spec 되채움 ──
sys.path.insert(0, str(ROOT / "spec"))
import spec as S
spec = S.load_spec(str(ROOT / "spec" / "STOCK_ALERT.json"))
S.merge_calc(spec, "data", {
    "monthly_price": monthly_price,
    "dividends": [[d.strftime("%Y-%m-%d"), round(v, 4)] for d, v in div.items()],
    "annual_dividends": annual_div,
})
fire = spec["backtest"]["fire"]
fire["scenarios"] = scenarios
allmax = max(p[1] for sc in scenarios for p in sc["pts"])
fire["chart_ymax"] = allmax
S.save_spec(spec, str(ROOT / "spec" / "STOCK_ALERT.json"))

n_surv = sum(1 for s in scenarios if s["survived"])
print(f"\n생존 {n_surv}/18 · 파산 {18 - n_surv}/18 · 전체 최대 평가액 ${allmax:,}")
print(f"연배당(주당) 2000 ${annual_div[0][1]:.2f} → 2025 ${dict((y,v) for y,v in annual_div).get(2025,0):.2f}")
print("→ spec/STOCK_ALERT.json (data + backtest.fire.scenarios) 갱신")
