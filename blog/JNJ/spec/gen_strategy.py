# -*- coding: utf-8 -*-
"""3부 매수 방법 (코카콜라와 동일 2전략 구조) → spec.backtest.strategy_compare.
   영리(폭락 타이밍, -30% 때 현금 100% 투입) vs 우직(매달 적립). 각 배당 재투자 ON/OFF.
   산출: 주가+트리거(씬24), 폭락매수 결과(씬25), 적립 결과(씬26), hbars2(씬27) 데이터.
   엔진: deck/tools/ko_smart_vs_steady.py(코카콜라 검증본).
"""
import sys
from datetime import date, timedelta
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "deck" / "tools"))
sys.path.insert(0, str(ROOT / "spec"))
import ko_smart_vs_steady as E
import spec as S

prices, divs = E.load_csv(str(ROOT / "data" / "jnj_price.csv"), str(ROOT / "data" / "jnj_div.csv"))
me_idx = E.month_end_indices(prices)
me_dates = {prices[i][0] for i in me_idx}
trig = E.compute_triggers(prices)
tset = {t[0] for t in trig}
MI, CM = E.MONTHLY_INCOME, E.CASH_MONTHLY
principal = round(MI * len(me_idx))


def to_year(d):
    y0 = date(d.year, 1, 1); y1 = date(d.year + 1, 1, 1)
    return round(d.year + (d - y0).days / (y1 - y0).days, 3)


def sub(series, step=3):
    pts = [[to_year(d), round(v)] for d, v in series]
    out = pts[::step]
    if out[-1] != pts[-1]: out.append(pts[-1])
    return out


# ── 전략 실행 (재투자 ON/OFF) ──
smart_on = E.run_smart(prices, divs, me_idx, trig, reinvest=True)
smart_off = E.run_smart(prices, divs, me_idx, trig, reinvest=False)
steady_on = E.run_steady(prices, divs, me_idx, reinvest=True)
steady_off = E.run_steady(prices, divs, me_idx, reinvest=False)

# 폭락매수 '주식평가액(재투자)' + '누적 투입(계단식)' 재구성
#   누적 투입 = 폭락 때 실제로 주식에 넣은 금액의 누적(현금 대기분은 제외) → $319k 소득 중 일부만
cash = shares = 0.0; cum_inv = 0.0; last = prices[0][0] - timedelta(days=1)
stock_series = []; invested_series = []
for d, c in prices:
    if d in me_dates:
        cash += cash * (CM - 1); cash += MI
    shares = E.apply_dividends_between(shares, prices, divs, last, d, True); last = d
    if d in tset and cash > 0:
        cum_inv += cash                 # 폭락 시점에 실제 투입한 현금 누적
        shares += cash / c; cash = 0.0
    if d in me_dates:
        stock_series.append((d, shares * c))
        invested_series.append((d, cum_inv))
dend, cend = prices[-1]
shares = E.apply_dividends_between(shares, prices, divs, last, dend, True)
stock_series.append((dend, shares * cend))
invested_series.append((dend, cum_inv))

# 월봉 주가 (씬24용)
price_monthly = [(prices[i][0], prices[i][1]) for i in me_idx]
trig_years = [to_year(t[0]) for t in trig]
trig_price_pts = [[to_year(t[0]), round(t[1], 2)] for t in trig]


# ── XIRR(화폐가중 수익률): 두 전략 동일하게 매월 -MI 기여 + 최종 +총자산 ──
#    두 전략 모두 같은 $319k를 같은 타이밍으로 넣으므로 XIRR이 공정한 정률 비교지표.
me_dates_sorted = [prices[i][0] for i in me_idx]
def _xirr(final_val):
    cfs = [(d, -MI) for d in me_dates_sorted] + [(prices[-1][0], final_val)]
    t0 = cfs[0][0]
    def npv(r):
        return sum(cf / (1.0 + r) ** ((d - t0).days / 365.0) for d, cf in cfs)
    r = 0.1
    for _ in range(200):
        f = npv(r); df = (npv(r + 1e-6) - f) / 1e-6
        if abs(df) < 1e-12:
            break
        rn = r - f / df
        if not (-0.99 < rn < 10):
            rn = (r + (0.0 if rn < 0 else 1.0)) / 2.0   # 발산 방지
        if abs(rn - r) < 1e-9:
            r = rn; break
        r = rn
    return r
xirr_smart = _xirr(smart_on["final"])
xirr_steady = _xirr(steady_on["final"])


def money(x): return f"${round(x):,}"


strat = {
    "premise": {"monthly_income": MI, "months": len(me_idx), "principal": principal,
                "cash_apr": E.CASH_APR, "div_tax": E.DIV_TAX,
                "trigger_dd": E.TRIGGER_DD, "rearm_dd": E.REARM_DD},
    "deck_triggers": [{"date": d.isoformat(), "close": round(c, 2), "high": round(hi, 2),
                       "dd_pct": round(dd * 100, 1)} for d, c, hi, dd in trig],
    "trigger_years": trig_years,
    "trigger_price_pts": trig_price_pts,
    # 씬24: 주가 + 폭락 신호
    "price_series": sub(price_monthly, 2),
    "price_range": [round(min(c for _, c in price_monthly)), round(max(c for _, c in price_monthly))],
    # 씬25: 폭락매수 결과
    "smart": {"name": "폭락 매수", "final_on": round(smart_on["final"]), "final_off": round(smart_off["final"]),
              "invested": round(smart_on["invested"]), "cash_left": round(smart_on["cash"]),
              "avg_cash_ratio_pct": round(smart_on["avg_cash_ratio"] * 100, 1),
              "xirr_on": round(xirr_smart * 100, 1),
              "total_series": sub(smart_on["series"]), "stock_series": sub(stock_series),
              "invested_series": sub(invested_series)},
    # 씬26: 적립 결과
    "steady": {"name": "매달 적립", "final_on": round(steady_on["final"]), "final_off": round(steady_off["final"]),
               "xirr_on": round(xirr_steady * 100, 1),
               "series_on": sub(steady_on["series"]), "series_off": sub(steady_off["series"])},
    # 하위호환(기존 필드)
    "strategies": {
        "smart": {"name": "폭락 매수", "final": round(smart_on["final"]),
                  "mult": round(smart_on["final"] / principal, 2),
                  "avg_cash_ratio_pct": round(smart_on["avg_cash_ratio"] * 100, 1),
                  "pts": sub(smart_on["series"])},
        "steady": {"name": "매달 적립", "final": round(steady_on["final"]),
                   "mult": round(steady_on["final"] / principal, 2), "pts": sub(steady_on["series"])},
    },
}

spec = S.load_spec(str(ROOT / "spec" / "JNJ.json"))
spec["backtest"]["strategy_compare"] = strat
S.save_spec(spec, str(ROOT / "spec" / "JNJ.json"))

print(f"현금흐름: 월 ${MI:,.0f} × {len(me_idx)}개월 = 원금 {money(principal)}")
print(f"트리거 {len(trig)}회 · 연도 {sorted({d.year for d,_,_,_ in trig})}")
print(f"폭락매수  재투자 {money(smart_on['final'])} / 미재투자 {money(smart_off['final'])} (투입 {money(smart_on['invested'])})")
print(f"적립     재투자 {money(steady_on['final'])} / 미재투자 {money(steady_off['final'])}")
diff = (smart_on["final"] / steady_on["final"] - 1) * 100
print(f"폭락 vs 적립(재투자): {diff:+.1f}%  (영리 현금비중 {smart_on['avg_cash_ratio']*100:.0f}%)")
print("→ spec/JNJ.json (backtest.strategy_compare) 갱신")
