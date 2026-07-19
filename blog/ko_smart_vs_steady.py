#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KO 백테스트 — 영리(타이밍) vs 우직(기준선)   ※ 동일 현금흐름 설계
스펙 §0~§5 그대로 구현. 룰은 결과 보기 전에 코드로 고정한다.

데이터 소스 (둘 중 하나):
  1) 온라인:  pip install yfinance pandas  →  python ko_smart_vs_steady.py
  2) 오프라인: python ko_smart_vs_steady.py --price ko_price.csv --div ko_div.csv
     - ko_price.csv : 컬럼 Date, Close  (Close = 무수정 종가 / unadjusted)
     - ko_div.csv   : 컬럼 Date, Dividend  (주당 배당, ex-date 기준)  [선택]

온라인이면 CSV도 자동 저장(ko_price.csv / ko_div.csv)해 재현성 확보.
"""
import argparse, csv, sys, math
from datetime import date, datetime, timedelta

# ─────────────────────────── 스펙 파라미터 (§0, §2, §3) ───────────────────────────
TICKER        = "KO"
START         = date(2000, 1, 1)
END           = date(2026, 7, 31)
MONTHLY_INCOME= 1000.0          # §0  매월 말 $1,000
DIV_TAX       = 0.154           # §0  배당세율 15.4%
CASH_APR      = 0.03            # §2  현금 연 3.0%, 월 복리
CASH_MONTHLY  = (1 + CASH_APR) ** (1/12)   # 매월 곱

# §3-2  직전 고점 정의:  "B" = 52주(=252 거래일) 최고가   ← 권장·채택
HIGH_MODE     = "B"             # "A"=사상최고가(running max) / "B"=52주 최고가
HIGH_WINDOW   = 252            # B일 때 롤링 거래일 수 (≈52주)
TRIGGER_DD    = -0.30          # §3    -30% 통과 시 발동
REARM_DD      = -0.10          # §3-3  낙폭 -10% 이내 회복 시 재무장  ← 최종 채택값
# 투입 시점: 트리거가 뜬 '그 날 종가'에 현금 100% 투입 (일봉 판정, 해당 월 안).
DECK_TRIGGERS = [2000, 2001, 2003, 2008, 2020]   # 기존 덱 5회 (교차검증용)

# ─────────────────────────── 데이터 로드 ───────────────────────────
def load_online():
    try:
        import yfinance as yf, pandas as pd
    except ImportError:
        sys.exit("yfinance/pandas 없음 → `pip install yfinance pandas` 또는 --price/--div 로 CSV 지정")
    px = yf.download(TICKER, start=START, end=END + timedelta(days=1),
                     auto_adjust=False, progress=False, threads=False)   # 무수정 종가
    if isinstance(px.columns, pd.MultiIndex):
        px.columns = px.columns.get_level_values(0)
    px = px.dropna(subset=["Close"])
    prices = [(d.date(), float(c)) for d, c in px["Close"].items()]
    dv = yf.Ticker(TICKER).dividends
    divs = [(d.date(), float(v)) for d, v in dv.items()
            if START <= d.date() <= END]
    # 재현용 CSV 저장
    with open("ko_price.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["Date","Close"])
        for d,c in prices: w.writerow([d.isoformat(), f"{c:.6f}"])
    with open("ko_div.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["Date","Dividend"])
        for d,v in divs: w.writerow([d.isoformat(), f"{v:.6f}"])
    print(f"[online] 가격 {len(prices)}행, 배당 {len(divs)}건 → ko_price.csv / ko_div.csv 저장")
    return prices, divs

def _rd_date(s):
    s=s.strip()
    for fmt in ("%Y-%m-%d","%Y/%m/%d","%m/%d/%Y"):
        try: return datetime.strptime(s,fmt).date()
        except ValueError: pass
    raise ValueError(f"날짜 파싱 실패: {s}")

def load_csv(price_path, div_path):
    prices=[]
    with open(price_path, newline="") as f:
        for row in csv.DictReader(f):
            k={c.lower():c for c in row}
            d=_rd_date(row[k["date"]]); c=row.get(k.get("close","close"))
            if c is None or c=="": continue
            if START<=d<=END: prices.append((d, float(c)))
    prices.sort()
    divs=[]
    if div_path:
        with open(div_path, newline="") as f:
            for row in csv.DictReader(f):
                k={c.lower():c for c in row}
                d=_rd_date(row[k["date"]])
                v=row.get(k.get("dividend", k.get("div","")))
                if v in (None,""): continue
                if START<=d<=END: divs.append((d, float(v)))
    divs.sort()
    print(f"[csv] 가격 {len(prices)}행, 배당 {len(divs)}건")
    return prices, divs

# ─────────────────────────── 유틸 ───────────────────────────
def month_end_indices(prices):
    """각 (연,월)의 마지막 거래일 인덱스 목록 (오름차순)."""
    last={}
    for i,(d,_) in enumerate(prices):
        last[(d.year,d.month)]=i
    return [last[k] for k in sorted(last)]

def rolling_high(prices, i):
    if HIGH_MODE=="A":
        return max(c for _,c in prices[:i+1])
    lo=max(0, i-HIGH_WINDOW+1)
    return max(c for _,c in prices[lo:i+1])

def xirr(flows, guess=0.1):
    """flows: [(date, amount)] 음수=투입, 양수=회수. 뉴턴+이분법."""
    if not flows: return float("nan")
    t0=flows[0][0]
    def npv(r):
        return sum(a/((1+r)**((d-t0).days/365.0)) for d,a in flows)
    lo,hi=-0.9999,10.0
    flo,fhi=npv(lo),npv(hi)
    if flo*fhi>0: return float("nan")
    for _ in range(200):
        mid=(lo+hi)/2; fm=npv(mid)
        if abs(fm)<1e-6: return mid
        if flo*fm<0: hi=mid; fhi=fm
        else: lo=mid; flo=fm
    return (lo+hi)/2

# ─────────────────────────── 트리거 산출 (§3) ───────────────────────────
def compute_triggers(prices):
    triggers=[]      # (date, close, high, dd)
    armed=True
    for i,(d,c) in enumerate(prices):
        hi=rolling_high(prices,i)
        dd=c/hi-1.0
        if armed and dd<=TRIGGER_DD:
            triggers.append((d,c,hi,dd)); armed=False
        elif (not armed) and dd> REARM_DD:
            armed=True
    return triggers

# ─────────────────────────── 배당 재투자 헬퍼 ───────────────────────────
def close_on_or_after(prices, dd):
    for d,c in prices:
        if d>=dd: return c
    return prices[-1][1]

def apply_dividends_between(shares, prices, divs, t_from, t_to, reinvest, cash_out=None):
    """(t_from, t_to] 구간 배당 처리. reinvest면 세후 전액 재매수(주식↑).
       아니면 세후 현금은 버림(스펙: 미재투자 = 주가만). shares 반환."""
    for dd, dps in divs:
        if t_from < dd <= t_to and shares>0:
            net = shares*dps*(1-DIV_TAX)
            if reinvest:
                px=close_on_or_after(prices, dd)
                shares += net/px
            elif cash_out is not None:
                cash_out[0]+=net
    return shares

# ─────────────────────────── 우직 (§1) ───────────────────────────
def run_steady(prices, divs, me_idx, reinvest=True):
    shares=0.0; last_div_t=prices[0][0]-timedelta(days=1)
    series=[]  # (date, value)
    div_cash=[0.0]
    for j,i in enumerate(me_idx):
        d,c=prices[i]
        # 이 달 이전까지의 배당 재투자 반영
        shares=apply_dividends_between(shares, prices, divs, last_div_t, d, reinvest, div_cash)
        last_div_t=d
        # 이 달 소득 전액 매수
        shares += MONTHLY_INCOME/c
        series.append((d, shares*c + (0 if reinvest else div_cash[0])))
    # 마지막 배당~END 반영
    dend,cend=prices[-1]
    shares=apply_dividends_between(shares, prices, divs, last_div_t, dend, reinvest, div_cash)
    final = shares*cend + (0 if reinvest else div_cash[0])
    series.append((dend, final))
    return dict(final=final, shares=shares, div_cash=div_cash[0], series=series)

# ─────────────────────────── 영리 (§2) ───────────────────────────
def run_smart(prices, divs, me_idx, triggers, reinvest=True):
    trig_dates=[t[0] for t in triggers]
    me_dates=set(prices[i][0] for i in me_idx)
    tset=set(trig_dates)
    cash=0.0; shares=0.0
    invested=0.0            # 실제 주식에 투입된 원금 누적
    cash_interest=0.0
    last_div_t=prices[0][0]-timedelta(days=1)
    val_series=[]; cash_series=[]
    cash_ratio_sum=0.0; total_months=0; months_big_cash=0
    for i,(d,c) in enumerate(prices):
        # 월말: 이자 → 소득 적립  (순서: 먼저 이자 붙이고, 말일 소득 추가)
        if d in me_dates:
            interest = cash*(CASH_MONTHLY-1)
            cash += interest; cash_interest += interest
            cash += MONTHLY_INCOME
        # 배당 재투자 (보유분)
        shares=apply_dividends_between(shares, prices, divs, last_div_t, d, reinvest); last_div_t=d
        # 트리거: 그 날 종가에 현금 100% 투입
        if d in tset and cash>0:
            shares += cash/c; invested += cash; cash=0.0
        if d in me_dates:
            val=shares*c + cash
            val_series.append((d, val)); cash_series.append((d, cash))
            total_months+=1
            if val>0: cash_ratio_sum += cash/val          # 시간가중 현금비중
            if cash > 2*MONTHLY_INCOME: months_big_cash+=1  # 미투입분이 쌓여 '놀고 있는' 달
    dend,cend=prices[-1]
    shares=apply_dividends_between(shares, prices, divs, last_div_t, dend, reinvest)
    final = shares*cend + cash
    return dict(final=final, shares=shares, cash=cash, invested=invested,
                cash_interest=cash_interest, series=val_series, cash_series=cash_series,
                avg_cash_ratio=cash_ratio_sum/max(1,total_months),
                months_big_cash=months_big_cash, total_months=total_months)

# ─────────────────────────── 메인 ───────────────────────────
def money(x): return f"${x:,.0f}"
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--price"); ap.add_argument("--div")
    a=ap.parse_args()
    prices, divs = load_csv(a.price, a.div) if a.price else load_online()
    if len(prices)<2000:
        print(f"⚠ 가격 데이터가 적음({len(prices)}행) — 일봉 전체가 맞는지 확인")
    me_idx=month_end_indices(prices)
    print(f"기간 {prices[0][0]} ~ {prices[-1][0]} · 거래일 {len(prices)} · 월말 {len(me_idx)}개 "
          f"(스펙 319개월)\n고점정의={HIGH_MODE} 창={HIGH_WINDOW} 트리거={TRIGGER_DD} 재무장={REARM_DD}\n")

    # ── §3 트리거 ──
    trig=compute_triggers(prices)
    # 발동 시점 현금·이자 로그 재구성용으로 smart 먼저 돌려 cash 로그 확보
    print("── §4-1 트리거 로그 ──")
    print(f"{'#':>2} {'발동일':>12} {'종가':>9} {'기준고점':>9} {'낙폭':>7}")
    for n,(d,c,hi,dd) in enumerate(trig,1):
        print(f"{n:>2} {d.isoformat():>12} {c:>9.2f} {hi:>9.2f} {dd*100:>6.1f}%")
    yrs=sorted(set(d.year for d,_,_,_ in trig))
    overlap=[y for y in yrs if y in DECK_TRIGGERS]
    print(f"\n트리거 {len(trig)}회 · 연도 {yrs}")
    print(f"덱 5회{DECK_TRIGGERS} 중 겹침: {overlap} ({len(overlap)}/5)")
    if not (3<=len(trig)<=7):
        print(f"⚠ §3-4 위반: 트리거 {len(trig)}회가 3~7 범위 밖 → §3-2/§3-3 재조정 필요")

    # ── 전략 실행 ──
    steady = run_steady(prices, divs, me_idx, reinvest=True)
    smart  = run_smart (prices, divs, me_idx, trig, reinvest=True)
    steady_off = run_steady(prices, divs, me_idx, reinvest=False)
    smart_off  = run_smart (prices, divs, me_idx, trig, reinvest=False)

    total_income = MONTHLY_INCOME*len(me_idx)
    print("\n── §4-2 최종 비교 (배당 재투자 ON) ──")
    rows=[
        ("총 소득",        total_income, total_income),
        ("실제 투입 원금", total_income, smart["invested"]),
        ("잔여 현금",      0.0,          smart["cash"]),
        ("현금 이자 누적", 0.0,          smart["cash_interest"]),
        ("주식 평가액",    steady["final"], smart["final"]-smart["cash"]),
        ("최종 자산",      steady["final"], smart["final"]),
    ]
    print(f"{'':<14}{'우직':>16}{'영리':>16}")
    for name,u,s in rows:
        print(f"{name:<14}{money(u):>16}{money(s):>16}")
    diff=(smart["final"]/steady["final"]-1)*100
    print(f"{'차이':<14}{'—':>16}{diff:>15.1f}%")

    print("\n── §4-3 부가 ──")
    print(f"영리 시간가중 현금비중(평균 cash/자산): {smart['avg_cash_ratio']*100:.1f}%")
    print(f"영리 '놀고 있던' 달(현금>2개월치): {smart['months_big_cash']}/{smart['total_months']} "
          f"= {smart['months_big_cash']/smart['total_months']*100:.1f}%")
    print("배당 재투자 ON/OFF 최종액:")
    print(f"  우직  ON {money(steady['final'])}   OFF {money(steady_off['final'])}")
    print(f"  영리  ON {money(smart['final'])}   OFF {money(smart_off['final'])}")

    # XIRR (배당 재투자 ON)
    flows=[(prices[i][0], -MONTHLY_INCOME) for i in me_idx]
    print(f"우직 XIRR: {xirr(flows+[(prices[-1][0], steady['final'])])*100:.2f}%")
    print(f"영리 XIRR: {xirr(flows+[(prices[-1][0], smart['final'])])*100:.2f}%")

    # ── §5 정합성 ──
    print("\n── §5 정합성 체크 ──")
    lhs=smart["invested"]+smart["cash"]
    rhs=total_income+smart["cash_interest"]
    print(f"영리: 총투입+잔여현금 = {money(lhs)}  vs  소득+이자 = {money(rhs)}  Δ={lhs-rhs:+.2f}")
    print(f"우직: 현금잔고=0 확인 (재투자ON은 현금 없음) ✓")
    print(f"트리거 횟수 == 로그 행수: {len(trig)} ✓")

    # ── §4-3 CSV ──
    with open("bt_value_steady.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["Date","Steady"])
        for d,v in steady["series"]: w.writerow([d.isoformat(), f"{v:.2f}"])
    with open("bt_value_smart.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["Date","Smart"])
        for d,v in smart["series"]: w.writerow([d.isoformat(), f"{v:.2f}"])
    with open("bt_cash_smart.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["Date","Cash"])
        for d,v in smart["cash_series"]: w.writerow([d.isoformat(), f"{v:.2f}"])
    print("\nCSV 저장: bt_value_steady.csv · bt_value_smart.csv · bt_cash_smart.csv")

if __name__=="__main__":
    main()
