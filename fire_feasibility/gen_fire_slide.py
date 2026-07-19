# -*- coding: utf-8 -*-
"""KO FIRE 파산 시나리오 백테스트 → 덱 슬라이드용 데이터(JSON) 생성."""
import io, json
from datetime import date
from pathlib import Path
import pandas as pd
from curl_cffi import requests as cr
from global_cup.fire_engine import run_fire_backtest

DATA = Path(__file__).parent / "data"

def fred(series_id):
    cache = DATA / f"fred_{series_id}.csv"
    if cache.exists():
        df = pd.read_csv(cache, parse_dates=["date"])
    else:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
        r = cr.get(url, impersonate="chrome", timeout=30); r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text)); df.columns = ["date","val"]
        df["date"] = pd.to_datetime(df["date"]); df.to_csv(cache, index=False)
    s = pd.Series(pd.to_numeric(df["val"], errors="coerce").values, index=df["date"])
    return s.dropna()

close = pd.read_csv(DATA/"ko_price_raw.csv", parse_dates=["date"]).set_index("date")["close"]
div   = pd.read_csv(DATA/"ko_div.csv", parse_dates=["date"]).set_index("date")["div"]
close.index = pd.to_datetime(close.index).tz_localize(None)
div.index   = pd.to_datetime(div.index).tz_localize(None)
uscpi = fred("CPIAUCSL")   # US CPI, monthly, 물가연동 인출용

INIT = 200_000.0
START = date(2000,1,1)

def run(rate):
    return run_fire_backtest(
        close, div, INIT,
        annual_withdrawal=INIT*rate, strategy="fixed_real",
        frequency="monthly", tax_rate_pct=15.0,
        reinvest_dividends=False, reinvest_surplus=True,
        cpi=uscpi, start_date=START)

print("=== 인출률 스윕 (물가연동, $100k, 2000 은퇴) ===")
sweep=[]
for rate in (0.04,0.05,0.06,0.08,0.10):
    r=run(rate); s=r.summary
    dep = s["Depletion Date"]
    sweep.append((rate, s["Survived"], s["Final Value"], s["Total Withdrawn"], s["Survived Years"], dep))
    print(f" {rate*100:4.0f}%  생존={s['Survived']!s:5} 최종=${s['Final Value']:>12,.0f} "
          f"총인출=${s['Total Withdrawn']:>10,.0f} 생존연수={s['Survived Years']:.1f} "
          f"파산일={dep.date() if dep is not None else '-'}")

def to_year(d):
    y0=pd.Timestamp(d.year,1,1); y1=pd.Timestamp(d.year+1,1,1)
    return round(d.year + (d-y0).days/(y1-y0).days, 2)

def timeline_pts(rate):
    r=run(rate); s=r.summary
    tl=r.timeline_df.copy(); tl["Date"]=pd.to_datetime(tl["Date"])
    tl["ym"]=tl["Date"].dt.to_period("M")
    m=tl.groupby("ym").last().reset_index(drop=True)
    pts=[[to_year(row["Date"]), round(row["Portfolio Value"])] for _,row in m.iloc[::3].iterrows()]
    last=[to_year(m.iloc[-1]["Date"]), round(m.iloc[-1]["Portfolio Value"])]
    if pts[-1][0]!=last[0]: pts.append(last)
    # 파산 시 마지막 점을 0으로 명시 (라인이 바닥에 닿게)
    dep=s["Depletion Date"]
    if not s["Survived"] and dep is not None:
        pts=[p for p in pts if p[0] <= to_year(pd.Timestamp(dep))]
        pts.append([to_year(pd.Timestamp(dep)), 0])
    return pts, s

# 메인 = 4%, + 파산 곡선들
r = run(0.04); s = r.summary
pts4,_  = timeline_pts(0.04)
pts5,_  = timeline_pts(0.05)
pts8,_  = timeline_pts(0.08)

print("\n=== 4% 메인 시나리오 ===")
print(f"  생존: {s['Survived']} · 최종 평가액: ${s['Final Value']:,.0f} (실질 ${s['Final Value Real']:,.0f})")
print(f"  총 인출: ${s['Total Withdrawn']:,.0f} · 총 배당(net): ${s['Total Net Dividend']:,.0f}")
print(f"  최대낙폭: {s['Max Drawdown %']:.1f}% · 최저평가액: ${s['Min Portfolio Value']:,.0f}")
print(f"  기간: {s['Years']:.1f}년 · 시작 KO ${s['Buy Price']:.2f} → 종료 ${s['End Price']:.2f}")
print(f"  포인트 수: 4%={len(pts4)} 5%={len(pts5)} 8%={len(pts8)}")

out = {
  "init": INIT, "rate": 0.04,
  "final": round(s["Final Value"]), "final_real": round(s["Final Value Real"]),
  "total_withdrawn": round(s["Total Withdrawn"]),
  "total_div": round(s["Total Net Dividend"]),
  "years": round(s["Years"],1), "survived": bool(s["Survived"]),
  "maxdd": round(s["Max Drawdown %"],1),
  "buy_px": round(s["Buy Price"],2), "end_px": round(s["End Price"],2),
  "pts4": pts4, "pts5": pts5, "pts8": pts8,
  "sweep": [{"rate":rt, "survived":bool(sv), "final":round(fv), "withdrawn":round(tw),
             "survyears":round(sy,1), "depl": (dp.strftime("%Y-%m") if dp is not None else None)}
            for (rt,sv,fv,tw,sy,dp) in sweep],
}
Path("fire_slide_data.json").write_text(json.dumps(out, ensure_ascii=False))
print("\n→ fire_slide_data.json 저장")
