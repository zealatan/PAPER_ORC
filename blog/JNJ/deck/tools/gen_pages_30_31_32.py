#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""30·31·32 재생성 (엔진A ko_smart_vs_steady 통일 + 30페이지 주식평가액 선 추가).
   사용: python gen_pages_30_31_32.py <덱.json> <출력.json>"""
import json, sys
from datetime import date, timedelta
sys.path.insert(0, ".")
import ko_smart_vs_steady as E

DECK, OUT = sys.argv[1], sys.argv[2]
prices, divs = E.load_csv("ko_price.csv", "ko_div.csv")
me_idx = E.month_end_indices(prices)
me_dates = set(prices[i][0] for i in me_idx)
trig = E.compute_triggers(prices)
tset = set(t[0] for t in trig)
CM, TAX, MI = E.CASH_MONTHLY, E.DIV_TAX, E.MONTHLY_INCOME

def to_year(d):
    s = date(d.year, 1, 1); e = date(d.year + 1, 1, 1)
    return round(d.year + (d - s).days / (e - s).days, 2)

def sub(series, step=2):
    pts = [[to_year(d), round(v)] for d, v in series]
    out = pts[::step]
    if out[-1] != pts[-1]: out.append(pts[-1])
    return out

# ── 엔진A 결과 ──
sm_on  = E.run_smart(prices, divs, me_idx, trig, reinvest=True)   # 총자산(재투자)
st_on  = E.run_steady(prices, divs, me_idx, reinvest=True)
st_off = E.run_steady(prices, divs, me_idx, reinvest=False)

# 스마트 '주식평가액'(재투자) 별도 재구성: 월말 (date, shares*c)
cash = shares = 0.0; last = prices[0][0] - timedelta(days=1)
stock_series = []
for d, c in prices:
    if d in me_dates:
        cash += cash * (CM - 1); cash += MI
    shares = E.apply_dividends_between(shares, prices, divs, last, d, True); last = d
    if d in tset and cash > 0:
        shares += cash / c; cash = 0.0
    if d in me_dates:
        stock_series.append((d, shares * c))
# 마지막 배당~end
dend, cend = prices[-1]
shares = E.apply_dividends_between(shares, prices, divs, last, dend, True)
stock_series.append((dend, shares * cend))
stock_by_year = {round(to_year(d), 4): v for d, v in stock_series}
stock_final = shares * cend

principal = round(MI * len(me_idx))   # 319,000
def money(x): return f"${round(x):,}"

deck = json.load(open(DECK, encoding="utf-8"))
S = deck["scenes"]

# ══════════ page 30 (idx29): 기존 유지 + 주식평가액 선 추가 ══════════
p30 = S[29]["data"]; ch = p30["chart"]
# 기존 총자산(재투자) series[0]의 x에 맞춰 주식평가액 lookup
base = ch["series"][0]["pts"]
stock_pts = []
for x, _ in base:
    key = round(x, 4)
    v = stock_by_year.get(key)
    if v is None:  # 근사: 가장 가까운 키
        v = min(stock_by_year.items(), key=lambda kv: abs(kv[0] - x))[1]
    stock_pts.append([x, round(v)])
# 주식평가액 선 삽입 (재투자 총자산 다음, 미재투자 앞)
stock_line = {"pts": stock_pts, "c": "var(--green)", "w": 2.6, "dash": 0,
              "name": "주식평가액(재투자)", "end": money(stock_final)}
new_series = [ch["series"][0], stock_line] + ch["series"][1:]
ch["series"] = new_series
p30["annoSub"] = ("★=−30% 폭락 5회 투입 · 초록(주식평가액)이 투입 때마다 계단처럼 [점프] · "
                  "파랑=총자산(대기현금 포함) · 2020 이후엔 현금이 안 쓰여 격차 재확대")

# ══════════ page 31 (idx30): steady 재생성 (엔진A) ══════════
p31 = S[30]["data"]
p31["sub"] = "배당 재투자 vs 미재투자 · 평가액 추이 (ko_smart 엔진=월말 매수, 세율 15.4%)"
p31["annoMain"] = f"적립식 배당 재투자 {money(st_on['final'])} — 원금 ${principal:,}의 {st_on['final']/principal:.1f}배"
p31["annoSub"] = "매달 사서 배당까지 재투자할 때의 복리 곡선 (엔진 통일: 30페이지와 동일 월말 매수)"
ch31 = p31["chart"]
ch31["series"] = [
    {"pts": sub(st_on["series"]),  "c": "var(--blue)", "w": 3.4, "name": "배당 재투자",  "end": f"${st_on['final']/1e6:.2f}M"},
    {"pts": sub(st_off["series"]), "c": "#e08a3c",     "w": 3,   "name": "배당 미재투자", "end": f"${st_off['final']/1e6:.2f}M"},
]
ch31["dline"] = {"p": [[2000, 0], [2026.6, principal]], "c": "var(--ink-soft)", "dash": 1, "label": f"누적 원금 ${principal:,}"}

# ══════════ page 32 (idx31): hbars2 우측(steady) 교체 ══════════
p32 = S[31]["data"]
smart_re, smart_no = sm_on["final"], E.run_smart(prices, divs, me_idx, trig, reinvest=False)["final"]
st_gain = st_off["final"] - principal
st_div  = st_on["final"] - st_off["final"]
p32["right"]["rows"] = [
    {"name": "배당 미재투자", "inv": principal, "gain": round(st_gain), "label": money(st_off["final"])},
    {"name": "배당 재투자",   "inv": principal, "gain": round(st_gain), "div": round(st_div),
     "label": money(st_on["final"]), "win": True},
]
diff = smart_re - st_on["final"]; pct = diff / st_on["final"] * 100
p32["annoMain"] = f"완벽한 폭락 타이밍, 겨우 [+{pct:.1f}%]"
p32["annoSub"] = f"미재투자였다면 영리가 역전패 ({money(smart_no)} < {money(st_off['final'])})"

json.dump(deck, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
print("── 재생성 요약 ──")
print(f"page30 주식평가액 선 추가: 최종 {money(stock_final)} (총자산 {money(sm_on['final'])})")
print(f"page31 적립식: 재투자 {money(st_on['final'])} / 미재투자 {money(st_off['final'])}")
print(f"page32 우측: 미재투자 {money(st_off['final'])} / 재투자 {money(st_on['final'])} (div {money(st_div)})")
print(f"page32 영리 vs 우직: {money(smart_re)} vs {money(st_on['final'])} → +{pct:.2f}%")
print(f"영리 미재투자 {money(smart_no)} < 우직 미재투자 {money(st_off['final'])} (역전) ✓")
print("→", OUT)
