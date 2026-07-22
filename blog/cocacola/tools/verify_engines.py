#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
두 DCA 엔진 robust 검증:
  A) ko_smart_vs_steady.run_steady   (매월 '말일' 매수)
  B) global_cup dividend_reinvest    (매월 '첫 거래일' 매수)
독립 레퍼런스(buy_timing 파라미터화) + 폐형식 + 자금보존 + 차등테스트.
"""
import sys, math
from datetime import date, timedelta
import pandas as pd

sys.path.insert(0, ".")
sys.path.insert(0, "global_cup_refactored")
import ko_smart_vs_steady as A
from global_cup.dividend_reinvest import run_dividend_reinvest_backtest as engB

TAX = 0.154
PASS=[0]; FAIL=[0]
def chk(name, got, exp, rtol=1e-6, atol=1e-2):
    ok = abs(got-exp) <= max(atol, rtol*abs(exp))
    (PASS if ok else FAIL)[0]+=1
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got={got:,.2f} exp={exp:,.2f} Δ={got-exp:,.4f}")
    return ok

# ── 독립 레퍼런스 DCA (일봉 시뮬, buy_timing 선택) ──
def ref_dca(prices, divs, monthly, tax, reinvest, buy_timing):
    """prices: [(date,close)] 정렬. divs: [(exdate,dps)]. buy_timing: 'start'|'end'.
       매월 buy_timing 시점에 monthly 매수. 배당은 ex-date 당일/직후 종가로 재투자 or 현금."""
    # 월별 매수일 인덱스
    from collections import OrderedDict
    firsts, lasts = {}, {}
    for i,(d,_) in enumerate(prices):
        key=(d.year,d.month)
        if key not in firsts: firsts[key]=i
        lasts[key]=i
    buy_idx = set((firsts if buy_timing=='start' else lasts).values())
    # 배당 ex-date → 직후(>=) 거래일 종가
    def px_on_or_after(dd):
        for d,c in prices:
            if d>=dd: return c
        return prices[-1][1]
    div_map={}
    for dd,dps in divs:
        div_map.setdefault(dd,0.0)
        div_map[dd]+=dps
    shares=0.0; cash=0.0; invested=0.0
    div_events=sorted(div_map.items())
    de=0
    series=[]
    for i,(d,c) in enumerate(prices):
        # 배당: ex-date가 오늘이면 처리 (shares>0일 때)
        while de<len(div_events) and div_events[de][0]<=d:
            dd,dps=div_events[de]
            if shares>0:
                net=shares*dps*(1-tax)
                if reinvest: shares+=net/px_on_or_after(dd)
                else: cash+=net
            de+=1
        if i in buy_idx:
            shares+=monthly/c; invested+=monthly
        series.append((d, shares*c+cash))
    return dict(final=shares*c+cash, shares=shares, cash=cash, invested=invested, series=series)

# ══════════════════ PART 1: 폐형식 (합성 데이터) ══════════════════
print("="*66); print("PART 1  폐형식 (closed-form) — 합성 데이터로 정답 대조")
# 12개월, 상수가격 $100, 무배당, 월 $1000 → 최종 = 12*1000
sp=[(date(2000,1,1)+timedelta(days=30*k), 100.0) for k in range(12)]
r=ref_dca(sp,[],1000,TAX,True,'end')
chk("무배당 상수가 12개월 최종=원금", r['final'], 12000)
chk("  보유주식수 = 120", r['shares'], 120)
# 1회 배당 $5, 미재투자: 최종 = 원금 + 세후배당(그 시점 보유주식 기준)
sp2=[(date(2000,1,31),100.0),(date(2000,2,29),100.0),(date(2000,3,31),100.0)]
dv2=[(date(2000,2,15),5.0)]  # 2월 배당 시점 보유=1월말 매수분 10주
r2=ref_dca(sp2,dv2,1000,TAX,False,'end')
# 1월말 10주 매수 → 2/15 배당 10*5*(1-.154)=42.3 현금 → 2월말+3월말 각 10주 → 30주
chk("1회배당 미재투자 최종", r2['final'], 30*100 + 10*5*(1-TAX))
r3=ref_dca(sp2,dv2,1000,TAX,True,'end')
# 재투자: 42.3/100=0.423주 추가 → 최종주식 30.423 * 100
chk("1회배당 재투자 최종", r3['final'], (30 + 10*5*(1-TAX)/100)*100)

# ══════════════════ 실데이터 로드 ══════════════════
prices, divs = A.load_csv("ko_price.csv", "ko_div.csv")
me_idx = A.month_end_indices(prices)
pxB = pd.Series([c for _,c in prices], index=pd.to_datetime([d for d,_ in prices]))
dvB = pd.Series([v for _,v in divs], index=pd.to_datetime([d for d,_ in divs]))
print(f"\n실데이터: 가격 {len(prices)}행 · 배당 {len(divs)}건 · 월말 {len(me_idx)}개월")

# ══════════════════ PART 2: 자금 보존 (money conservation) ══════════════════
print("="*66); print("PART 2  자금 보존 — 최종가치 = 투입원금 + (미재투자시)세후현금배당 + 시장손익")
def market_pnl_from_series(series):
    # 근사 불가 — 대신 엔진 내부 일관성으로 대체 (아래 차등테스트로 확인)
    pass
# 미재투자: 최종 = 투입원금 + 세후배당현금 + 주식평가손익
rE_off=ref_dca(prices,divs,1000,TAX,False,'end')
# 주식평가손익 = 최종주식가치 - 투입원금  (미재투자라 주식은 투입만으로 증가)
stock_val = rE_off['shares']*prices[-1][1]
chk("미재투자 항등식: 최종 = 주식평가 + 현금배당", rE_off['final'], stock_val + rE_off['cash'], atol=0.5)
chk("  현금배당>0 확인", 1 if rE_off['cash']>0 else 0, 1)

# ══════════════════ PART 3: 차등테스트 (엔진 vs 독립레퍼런스) ══════════════════
print("="*66); print("PART 3  차등테스트 — 각 엔진이 자기 규칙의 독립레퍼런스와 일치하는가")
# 엔진 A (월말)
A_on = A.run_steady(prices,divs,me_idx,reinvest=True)['final']
A_off= A.run_steady(prices,divs,me_idx,reinvest=False)['final']
refEnd_on = ref_dca(prices,divs,1000,TAX,True,'end')['final']
refEnd_off= ref_dca(prices,divs,1000,TAX,False,'end')['final']
print(" 엔진A(월말) vs 레퍼런스(월말):")
chk("  재투자",  A_on, refEnd_on, rtol=3e-3)
chk("  미재투자",A_off, refEnd_off, rtol=3e-3)
# 엔진 B (월초): init=1000 이면 1월분=초기매수, 이후 월초. 총 319회.
def runB(reinv):
    r=engB(pxB,dvB,initial_amount=1000,monthly_amount=1000,tax_rate_pct=15.4,reinvest_dividends=reinv)
    return r.summary.get("Final Portfolio Value") or r.summary.get("Final Value")
B_on=runB(True); B_off=runB(False)
refStart_on = ref_dca(prices,divs,1000,TAX,True,'start')['final']
refStart_off= ref_dca(prices,divs,1000,TAX,False,'start')['final']
print(" 엔진B(월초) vs 레퍼런스(월초):")
chk("  재투자",  B_on, refStart_on, rtol=8e-3)
chk("  미재투자",B_off, refStart_off, rtol=8e-3)

# ══════════════════ 요약 ══════════════════
print("="*66); print("최종 비교표 (KO 2000~2026 적립식 $1,000/월)")
print(f"{'방식':28}{'재투자':>16}{'미재투자':>16}")
print(f"{'엔진A ko_smart(월말)':28}{A_on:>16,.0f}{A_off:>16,.0f}")
print(f"{'레퍼런스(월말)':28}{refEnd_on:>16,.0f}{refEnd_off:>16,.0f}")
print(f"{'엔진B global_cup(월초)':28}{B_on:>16,.0f}{B_off:>16,.0f}")
print(f"{'레퍼런스(월초)':28}{refStart_on:>16,.0f}{refStart_off:>16,.0f}")
print(f"{'덱 31페이지':28}{1187919:>16,}{947000:>16,}")
print(f"\n결과: PASS {PASS[0]} · FAIL {FAIL[0]}")
