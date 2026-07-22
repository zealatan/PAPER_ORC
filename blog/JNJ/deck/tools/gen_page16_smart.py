#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
16페이지용: 영리(폭락시에만 일괄 투자) 백테스트 → 17페이지와 동일한 enginechart JSON 생성.
배당 재투자 ON/OFF 두 곡선 + 누적 원금 점선.
"""
import json
from datetime import date
import ko_smart_vs_steady as E

prices, divs = E.load_csv("ko_price.csv", "ko_div.csv")
me_idx = E.month_end_indices(prices)
trig = E.compute_triggers(prices)

smart_on  = E.run_smart(prices, divs, me_idx, trig, reinvest=True)
smart_off = E.run_smart(prices, divs, me_idx, trig, reinvest=False)

print("트리거:", [(d.isoformat(), round(c,2)) for d,c,hi,dd in trig])
print("영리 재투자 ON  최종:", E.money(smart_on["final"]))
print("영리 미재투자 OFF 최종:", E.money(smart_off["final"]))
print("총 소득(누적 원금):", E.money(E.MONTHLY_INCOME*len(me_idx)))

def to_year(d):  # 소수 연도
    start = date(d.year, 1, 1)
    end   = date(d.year+1, 1, 1)
    return round(d.year + (d - start).days / (end - start).days, 2)

def subsample(series, step=3):
    """월말 series를 분기(3개월)로 솎아내고 마지막 점 보장."""
    pts = [[to_year(d), round(v)] for d, v in series]
    out = pts[::step]
    if out[-1] != pts[-1]:
        out.append(pts[-1])
    return out

on_pts  = subsample(smart_on["series"])
off_pts = subsample(smart_off["series"])

principal = round(E.MONTHLY_INCOME * len(me_idx))
end_on  = f"${smart_on['final']/1e6:.2f}M"
end_off = f"${smart_off['final']/1e6:.2f}M"

chart = {
  "kind": "line",
  "x": [2000, 2026.6],
  "y": [0, 1250000],
  "yticks": [[200000,"$0.2M"],[400000,"$0.4M"],[600000,"$0.6M"],
             [800000,"$0.8M"],[1000000,"$1.0M"],[1200000,"$1.2M"]],
  "xticks": [[2000,"2000"],[2005,"'05"],[2010,"'10"],
             [2015,"'15"],[2020,"'20"],[2025,"'25"]],
  "series": [
    {"pts": on_pts,  "c":"var(--blue)", "w":3.4, "name":"배당 재투자",  "end":end_on},
    {"pts": off_pts, "c":"#e08a3c",     "w":3,   "name":"배당 미재투자","end":end_off},
  ],
  "dline": {"p": [[2000,0],[2026.6, principal]], "c":"var(--ink-soft)",
            "dash":1, "label": f"누적 원금 ${principal:,.0f}"}
}

data = {
  "title": "엔진 시뮬레이션 — 모았다가 [폭락에 일괄 투입] {{coke}}",
  "sub": f"현금 적립 후 −30% 폭락 {len(trig)}회에 일괄 투입 · 배당 재투자 vs 미재투자 (global_cup 엔진, 세율 15.4%)",
  "annoMain": f"폭락 투자 배당 재투자 {E.money(smart_on['final'])} — 원금 ${principal:,.0f}의 {smart_on['final']/principal:.1f}배",
  "annoSub": "현금 모았다가 폭락 때만 일괄 투입할 때의 복리 곡선",
  "chart": chart,
}

with open("page16_data.json","w") as f:
    json.dump(data, f, ensure_ascii=False)
print("\n포인트 수: ON", len(on_pts), "OFF", len(off_pts), "→ page16_data.json 저장")
