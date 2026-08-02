#!/usr/bin/env python3
"""
gen_accum.py — 적립(accum) 시나리오 백테스트 → assets/<stock>_accum.json.

시나리오: 2000년부터 매달 $1,000 투입. 두 전략 비교(임계값 3종: 20/30/50%):
  · 적립식(steady) — 매달 말 전액 매수(DCA)
  · X% 하락매수(smart) — 현금 모았다가 고점 대비 -X% 통과 시 100% 투입
  배당 재투자 ON. 그래프 3장(20/30/50%), 각 2선(적립식 vs 폭락매수). hline=총 투입원금.
엔진: blog/PG/deck/tools/ko_smart_vs_steady.py (코카콜라·PG 검증본, 수정 금지 · TRIGGER_DD 전역 override).
사용: SHORTS_STOCK=PG python3 gen_accum.py
"""
import sys, json, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
STOCK = os.environ.get("SHORTS_STOCK", "PG")
PREF = {"PG": "pg", "QQQ": "qqq", "KTNG": "ktng", "SKH": "skh", "SEC": "sec"}[STOCK]
sys.path.insert(0, os.path.join(HERE, "..", "PG", "deck", "tools"))
import ko_smart_vs_steady as E

E.MONTHLY_INCOME = {"SKH": 1000000.0, "SEC": 1000000.0}.get(STOCK, 1000.0)   # 월 적립액(SKH·삼성 100만원 / 그 외 $1,000·1,000원)
KRW = STOCK in ("KTNG", "SKH", "SEC")
START_YEAR = {"SKH": 2006, "SEC": 2016}.get(STOCK, 2000)   # 종목별 시작연도(SK하이닉스 2006~, 삼성전자 2016~)

# 데이터: PG=로컬 CSV / 그 외=yfinance
if STOCK == "PG":
    DATA = os.path.join(HERE, "..", "PG", "data")
    prices, divs = E.load_csv(os.path.join(DATA, "pg_price.csv"), os.path.join(DATA, "pg_div.csv"))
else:
    import yfinance as yf
    _TK = {"QQQ": "QQQ", "KTNG": "033780.KS", "SKH": "000660.KS", "SEC": "005930.KS"}[STOCK]
    _t = yf.Ticker(_TK)
    _h = _t.history(start="%d-01-01" % START_YEAR, end="2026-07-31", auto_adjust=False); _h.index = _h.index.tz_localize(None)
    prices = [(d.date(), float(c)) for d, c in _h["Close"].items() if c == c]   # NaN 종가 제거(NaN!=NaN)
    _dv = _t.dividends; _dv.index = _dv.index.tz_localize(None)
    divs = [(d.date(), float(v)) for d, v in _dv.items() if v == v]
    print("[%s] yfinance 가격 %d행 · 배당 %d건" % (_TK, len(prices), len(divs)))
# 시작연도 필터(2000 초과 시)
prices = [(d, c) for d, c in prices if d.year >= START_YEAR]
divs = [(d, v) for d, v in divs if d.year >= START_YEAR]
me_idx = E.month_end_indices(prices)
TOTAL_IN = round(E.MONTHLY_INCOME * len(me_idx))   # 총 투입원금

THRESH = {"SEC": [20, 30]}.get(STOCK, [20, 30, 50])   # 삼성전자(2016~)는 -50% 미발생 → 20/30만
C_STEADY = "#2b6cb0"   # 적립식 = 스틸블루(팔레트A)
C_SMART  = "#c2255c"   # 폭락매수 = 라즈베리(팔레트A)

def to_year(d):
    from datetime import date
    y0 = date(d.year, 1, 1); y1 = date(d.year + 1, 1, 1)
    return round(d.year + (d - y0).days / (y1 - y0).days, 3)
def sub(series, step=1):   # 월별 전량 샘플(급등·폭락 등 단기 변동 반영)
    pts = [[to_year(d), round(v)] for d, v in series]
    out = pts[::step]
    if out[-1] != pts[-1]: out.append(pts[-1])
    return out
def usd(v): return ((("%.1f억" % (v/1e8)) if v >= 1e8 else ("%s만" % format(int(round(v/1e4)), ","))) if KRW else ("$" + format(int(round(v)), ",")))
def nice_ceil(x):
    e = 10 ** math.floor(math.log10(x)); f = x / e
    for n in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if f <= n: return int(n * e)
    return int(10 * e)

# ── XIRR(연 환산 수익률, 월 투입 현금흐름 기준) · CAGR ──
me_dates_list = [prices[i][0] for i in me_idx]
end_d = prices[-1][0]
ASOF = "%04d.%02d.%02d" % (end_d.year, end_d.month, end_d.day)   # 데이터 기준일(마지막 거래일) — 슬라이드 우측상단 표기
years = (end_d - prices[0][0]).days / 365.25
def xirr_of(final):
    flows = [(d, -E.MONTHLY_INCOME) for d in me_dates_list] + [(end_d, final)]
    return E.xirr(flows)
def cagr_of(final):   # 총 투입원금 대비 단순 CAGR(참고용)
    return (final / TOTAL_IN) ** (1 / years) - 1

# ── 누적 투입원금 시리즈(점선용) ──
def steady_inv_series():   # 적립식: 매달 전액 투입 → 매끄럽게 상승
    out, cum = [], 0.0
    for i in me_idx:
        cum += E.MONTHLY_INCOME; out.append((prices[i][0], cum))
    return out
def smart_inv_series(trig):  # 폭락매수: 트리거 때만 현금 투입 → 계단식
    tset = set(t[0] for t in trig); me_dates = set(prices[i][0] for i in me_idx)
    cash = invested = 0.0; out = []
    for i, (d, c) in enumerate(prices):
        if d in me_dates:
            cash += cash * (E.CASH_MONTHLY - 1); cash += E.MONTHLY_INCOME
        if d in tset and cash > 0:
            invested += cash; cash = 0.0
        if d in me_dates:
            out.append((d, invested))
    return out

steady = E.run_steady(prices, divs, me_idx, reinvest=True)   # 임계값 무관(동일)
steady_pts = sub(steady["series"])
steady_inv_pts = sub(steady_inv_series())
s_xirr, s_cagr = xirr_of(steady["final"]), cagr_of(steady["final"])

fires = []   # 편집기/영상 생성기가 읽는 payload 리스트
print("[%s accum] 총 투입원금 %s · 기간 %.1f년" % (STOCK, usd(TOTAL_IN), years))
print("  적립식        최종 %-11s XIRR %.1f%%  CAGR %.1f%%" % (usd(steady["final"]), s_xirr*100, s_cagr*100))
for thr in THRESH:
    E.TRIGGER_DD = -thr / 100.0          # 임계값 override
    trig = E.compute_triggers(prices)
    smart = E.run_smart(prices, divs, me_idx, trig, reinvest=True)
    smart_pts = sub(smart["series"])
    smart_inv_pts = sub(smart_inv_series(trig))
    m_xirr, m_cagr = xirr_of(smart["final"]), cagr_of(smart["final"])
    mx = max(max(p[1] for p in steady_pts), max(p[1] for p in smart_pts))
    payload = {
        "ymax": nice_ceil(mx * 1.05),
        "tip": "compact", "yleft": True, "x0": START_YEAR, "krw": KRW,
        "lines": [
            # 원금 점선(각각) — 뒤에 깔림, 끝점 라벨 없음
            {"c": C_STEADY, "surv": True, "dash": True, "nolabel": True, "pts": steady_inv_pts},
            {"c": C_SMART,  "surv": True, "dash": True, "nolabel": True, "pts": smart_inv_pts},
            # 평가 실선(각각) — 위, 끝점=최종액
            {"c": C_STEADY, "surv": True, "end": usd(steady["final"]), "pts": steady_pts},
            {"c": C_SMART,  "surv": True, "end": usd(smart["final"]),  "pts": smart_pts},
        ],
        "legend": [{"c": C_STEADY, "label": "매달 적립식"}, {"c": C_SMART, "label": "%d%% 하락매수" % thr}],
    }
    fires.append({"thr": thr, "hook": "적립식 vs %d%% 하락매수" % thr, "payload": payload,
                  "invested": TOTAL_IN, "monthly": E.MONTHLY_INCOME, "krw": KRW, "x0": START_YEAR, "asof": ASOF,
                  "steady": {"final": round(steady["final"]), "xirr": round(s_xirr, 4), "cagr": round(s_cagr, 4)},
                  "smart":  {"final": round(smart["final"]),  "xirr": round(m_xirr, 4), "cagr": round(m_cagr, 4),
                             "trig_n": len(trig)}})
    print("  %d%% 하락매수  최종 %-11s XIRR %.1f%%  CAGR %.1f%%  (트리거 %d회)" % (thr, usd(smart["final"]), m_xirr*100, m_cagr*100, len(trig)))

out = os.path.join(HERE, "assets", "data", PREF + "_accum.json")
json.dump(fires, open(out, "w"), ensure_ascii=False)
print("→", out, "(그래프", len(fires), "장)")
