# -*- coding: utf-8 -*-
"""KO FIRE — 고정 월 인출($100/$200/$300), 물가 미반영(nominal) vs 반영(real)."""
import io, json
from datetime import date
from pathlib import Path
import pandas as pd
from curl_cffi import requests as cr
from global_cup.fire_engine import run_fire_backtest

DATA = Path(__file__).parent / "data"

def fred(series_id):
    cache = DATA / f"fred_{series_id}.csv"
    df = pd.read_csv(cache, parse_dates=["date"])
    s = pd.Series(pd.to_numeric(df["val"], errors="coerce").values, index=df["date"])
    return s.dropna()

close = pd.read_csv(DATA/"ko_price_raw.csv", parse_dates=["date"]).set_index("date")["close"]
div   = pd.read_csv(DATA/"ko_div.csv", parse_dates=["date"]).set_index("date")["div"]
close.index = pd.to_datetime(close.index).tz_localize(None)
div.index   = pd.to_datetime(div.index).tz_localize(None)
uscpi = fred("CPIAUCSL")

INIT = 200_000.0
START = date(2000,1,1)
MONTHLIES = [1000, 2000, 3000]

def to_year(d):
    y0=pd.Timestamp(d.year,1,1); y1=pd.Timestamp(d.year+1,1,1)
    return round(d.year + (d-y0).days/(y1-y0).days, 2)

def run(monthly, strategy):
    return run_fire_backtest(
        close, div, INIT,
        annual_withdrawal=monthly*12, strategy=strategy,
        frequency="monthly", tax_rate_pct=15.0,
        reinvest_dividends=False, reinvest_surplus=True,
        cpi=(uscpi if strategy=="fixed_real" else None), start_date=START)

def series_of(monthly, strategy):
    r=run(monthly, strategy); s=r.summary
    tl=r.timeline_df.copy(); tl["Date"]=pd.to_datetime(tl["Date"]); tl["ym"]=tl["Date"].dt.to_period("M")
    m=tl.groupby("ym").last().reset_index(drop=True)
    pts=[[to_year(row["Date"]), round(row["Portfolio Value"])] for _,row in m.iloc[::3].iterrows()]
    last=[to_year(m.iloc[-1]["Date"]), round(m.iloc[-1]["Portfolio Value"])]
    if pts[-1][0]!=last[0]: pts.append(last)
    dep=s["Depletion Date"]
    if not s["Survived"] and dep is not None:
        pts=[p for p in pts if p[0] <= to_year(pd.Timestamp(dep))]; pts.append([to_year(pd.Timestamp(dep)),0])
    return pts, s

out={"init":INIT}
for strat_key, strat in [("nominal","fixed_nominal"),("real","fixed_real")]:
    print(f"\n===== {strat_key} ({strat}) · 초기 ${INIT:,.0f} =====")
    out[strat_key]={}
    for mo in MONTHLIES:
        pts,s=series_of(mo, strat)
        out[strat_key][f"m{mo}"]={"pts":pts,"final":round(s["Final Value"]),"survived":bool(s["Survived"]),
                                  "withdrawn":round(s["Total Withdrawn"]),"div":round(s["Total Net Dividend"]),
                                  "depl":(s["Depletion Date"].strftime("%Y-%m") if s["Depletion Date"] is not None else None)}
        print(f"  월 ${mo:3d} (연 ${mo*12:,}) 생존={s['Survived']!s:5} 최종=${s['Final Value']:>10,.0f} "
              f"총인출=${s['Total Withdrawn']:>9,.0f} 배당=${s['Total Net Dividend']:>8,.0f} "
              f"파산={s['Depletion Date'].date() if s['Depletion Date'] is not None else '-'}")

allmax=max(p[1] for k in ("nominal","real") for mo in MONTHLIES for p in out[k][f"m{mo}"]["pts"])
print(f"\n전체 최대 평가액: ${allmax:,.0f}")
Path("fire_monthly_data.json").write_text(json.dumps(out, ensure_ascii=False))
print("→ fire_monthly_data.json 저장")
