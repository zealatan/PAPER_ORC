# -*- coding: utf-8 -*-
# gen_fire_corpus.py 와 동일 로직 · START만 2002-01-01 (닷컴버블 저점)
import json
from datetime import date
from pathlib import Path
import pandas as pd
from global_cup.fire_engine import run_fire_backtest
DATA = Path(__file__).parent / "data"
def fred(sid):
    df = pd.read_csv(DATA/f"fred_{sid}.csv", parse_dates=["date"])
    return pd.Series(pd.to_numeric(df["val"],errors="coerce").values, index=df["date"]).dropna()
close = pd.read_csv(DATA/"ko_price_raw.csv", parse_dates=["date"]).set_index("date")["close"]
div   = pd.read_csv(DATA/"ko_div.csv", parse_dates=["date"]).set_index("date")["div"]
close.index=pd.to_datetime(close.index).tz_localize(None); div.index=pd.to_datetime(div.index).tz_localize(None)
uscpi=fred("CPIAUCSL")
START=date(2002,1,1)
INITS=[200_000,400_000,600_000]; MONTHLIES=[1000,2000,3000]
def to_year(d):
    y0=pd.Timestamp(d.year,1,1); y1=pd.Timestamp(d.year+1,1,1); return round(d.year+(d-y0).days/(y1-y0).days,2)
def run(init,mo,strat):
    return run_fire_backtest(close,div,init,annual_withdrawal=mo*12,strategy=strat,frequency="monthly",
        tax_rate_pct=15.0,reinvest_dividends=False,reinvest_surplus=True,
        cpi=(uscpi if strat=="fixed_real" else None),start_date=START)
def ser(init,mo,strat):
    r=run(init,mo,strat); s=r.summary
    tl=r.timeline_df.copy(); tl["Date"]=pd.to_datetime(tl["Date"]); tl["ym"]=tl["Date"].dt.to_period("M")
    m=tl.groupby("ym").last().reset_index(drop=True)
    pts=[[to_year(x["Date"]),round(x["Portfolio Value"])] for _,x in m.iloc[::3].iterrows()]
    last=[to_year(m.iloc[-1]["Date"]),round(m.iloc[-1]["Portfolio Value"])]
    if pts[-1][0]!=last[0]: pts.append(last)
    dep=s["Depletion Date"]
    if not s["Survived"] and dep is not None:
        pts=[p for p in pts if p[0]<=to_year(pd.Timestamp(dep))]; pts.append([to_year(pd.Timestamp(dep)),0])
    return pts,s
out={}
for strat_key,strat in [("nominal","fixed_nominal"),("real","fixed_real")]:
    print(f"\n===== {strat_key} (START 2002) =====")
    print(f"{'원금':>8} | {'월$1000':>14} {'월$2000':>14} {'월$3000':>14}")
    for init in INITS:
        row=[]
        for mo in MONTHLIES:
            pts,s=ser(init,mo,strat)
            out[f"{strat_key}_{init}_{mo}"]={"pts":pts,"survived":bool(s["Survived"]),
                "final":round(s["Final Value"]),"depl":(s["Depletion Date"].strftime("%Y-%m") if s["Depletion Date"] is not None else None)}
            row.append(("생존 $%s"%format(round(s['Final Value']),',')) if s["Survived"] else ("파산 "+s["Depletion Date"].strftime("%Y")))
        print(f"${init:>7,} | {row[0]:>14} {row[1]:>14} {row[2]:>14}")
allmax=max(p[1] for v in out.values() for p in v["pts"])
print(f"\n전체 최대 평가액: ${allmax:,.0f}")
Path("fire_corpus_data_2002.json").write_text(json.dumps(out,ensure_ascii=False))
print("→ fire_corpus_data_2002.json")
