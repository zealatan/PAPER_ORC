# -*- coding: utf-8 -*-
"""D단계 덱 조립 → 자립형 viewable HTML.
   spec(scenarios/strategy/narration/business) → 씬 JSON → pg_final.html DEFAULT 이후 강제주입.
   철칙: 차트 pts·수치는 backtest 인용. cocacola 패치 IIFE(v8-hook/revert1/survheat1/src1)는
   1889라인 직후 SCENES 덮어쓰기로 무력화.
   사용: python deck/build_deck.py  →  deck/pg_v1.html · deck/pg_deck.json
"""
import json, sys, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "spec"))
import spec as S
import pandas as pd

spec = S.load_spec(str(ROOT / "spec" / "PG.json"))
SC = {s["id"]: s for s in spec["backtest"]["fire"]["scenarios"]}
STRAT = spec["backtest"]["strategy_compare"]["strategies"]
BIZ = spec["data"]["business"]
NARR = json.load(open(ROOT / "spec" / "narration_draft.json"))
# 사용자 HUD 편집분(라벨 위치·anno 숨김 등) — 있으면 덱 기본 OV로 주입(재빌드해도 유지)
_ovf = ROOT / "spec" / "deck_ov.json"
DECK_OV = json.load(open(_ovf, encoding="utf-8")) if _ovf.exists() else {}

BLUE, ORANGE, RED, GREEN, INK = "var(--blue)", "#e08a3c", "var(--red)", "var(--green)", "var(--ink-soft)"


def money(x): return f"${x:,}"
def money_short(x):                     # 끝 라벨용 약칭 (선과 안 겹치게 짧게)
    x = round(x)
    if x >= 1_000_000: return f"${x/1e6:.2f}M".replace(".00M", "M")
    if x >= 1_000: return f"${round(x/1000)}k"
    return f"${x:,}"


def nice_ceil(v):
    if v <= 0: return 100000
    mag = 10 ** (len(str(int(v))) - 1)
    for m in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if m * mag >= v: return int(m * mag)
    return int(10 * mag)


def yticks(ymax):
    n = 5; step = ymax / n
    out = []
    for i in range(1, n + 1):
        v = round(step * i)
        lab = f"${v/1e6:.1f}M" if ymax >= 1e6 else f"${round(v/1000)}k"
        out.append([v, lab])
    return out


XTICKS = [[2000, "2000"], [2005, "'05"], [2010, "'10"], [2015, "'15"], [2020, "'20"], [2025, "'25"]]


def fire_chart(init, strat_key):
    """원금 init, 전략(nominal/real)의 월$1k/$2k/$3k 3선 차트."""
    specs = [(1000, BLUE, 3.4), (2000, ORANGE, 3.0), (3000, RED, 3.0)]
    series, ally = [], []
    for mo, c, w in specs:
        s = SC[f"{strat_key}_{init}_{mo}"]
        ally += [p[1] for p in s["pts"]]
        # 범례가 색→월 식별 → 끝라벨은 짧게(생존=금액 / 파산='YY 파산)로 겹침 최소화
        end = money_short(s['final']) if s["survived"] else f"'{s['depletion'][2:4]} 파산"
        series.append({"pts": s["pts"], "c": c, "w": w, "name": f"월 ${mo//1000}천", "end": end})
    # 파산 끝라벨 겹침 방지: 파산 연도가 3년 이내로 붙으면 뒤엣것 라벨 숨김(annoMain·범례가 정보 보완)
    deps = sorted((float(SC[f"{strat_key}_{init}_{mo}"]["depletion"][:4]), i)
                  for i, (mo, _, _) in enumerate(specs)
                  if not SC[f"{strat_key}_{init}_{mo}"]["survived"])
    _kx = -999
    for _yr, _i in deps:
        if _yr - _kx < 3:
            series[_i]["end"] = ""
        else:
            _kx = _yr
    ymax = nice_ceil(max(ally))
    # 색 범례 복원(🔵월$1천 🟠월$2천 🔴월$3천) — series.name 사용. 물가표(우상단)·선시작(좌상단) 회피 위해 좌중단 배치.
    return {"kind": "line", "x": [2000, 2026.6], "y": [0, ymax], "yticks": yticks(ymax),
            "xticks": XTICKS, "series": series, "legAt": [20, 46],
            "hline": {"v": init, "c": INK, "dash": 1, "label": f"은퇴 원금 {money(init)}"}}


SCOMP = spec["backtest"]["strategy_compare"]          # 3부 전체 데이터
TRIG_Y = sorted({int(t["date"][:4]) for t in SCOMP["deck_triggers"]})


# ── reelchart (릴스 스타일 개별 그래프) 공용 ──────────────────────
def _nice_ceil(v):
    if v <= 0:
        return 100000
    e = 10 ** math.floor(math.log10(v)); f = v / e
    for n in (1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if f <= n:
            return int(n * e)
    return int(10 * e)

_RCOL = {1000: "#1f6fe0", 2000: "#e0821c", 3000: "#e01e37"}

def reel_fire(init):
    """파이어 원금별(2000 은퇴·물가반영) 릴스 그래프 — 월$1/2/3천 3선."""
    lines, mx = [], 0
    for mo in (1000, 2000, 3000):
        s = SC[f"real_{init}_{mo}"]; pts = s["pts"]; mx = max(mx, max(p[1] for p in pts))
        end = (f"생존 ${s['final']//10000}만") if s["survived"] else (f"’{str(s['depletion'])[2:4]} 파산")
        lines.append({"c": _RCOL[mo], "name": "", "surv": bool(s["survived"]), "end": end, "pts": pts})
    return {"title1": "물가 반영해서 매달 빼 쓰면", "title2": f"<b>${init//10000}만</b>으로 몇 년 버틸까?",
            "sub": "2000년 은퇴", "ymax": _nice_ceil(mx * 1.05), "tip": "compact",
            "hline": {"v": init, "label": f"은퇴 원금 ${init//10000}만"},
            "legend": [{"c": _RCOL[mo], "label": f"월 ${mo//1000}천 인출"} for mo in (1000, 2000, 3000)],
            "lines": lines}

def reel_steady():
    so = SCOMP["steady"]["series_on"]; t0 = so[0][0]
    prin = SCOMP["premise"]["principal"]; mi = SCOMP["premise"]["monthly_income"]
    inv = [[x, min(prin, round((x - t0) * 12 * mi))] for x, _ in so]
    return {"title1": "최악의 고점에서 <b>매달 $1,000씩</b>", "title2": "P&G에 적립했더니",
            "sub": "매달 $1,000 적립 · 배당 재투자 · ’00.3~’26.7", "ymax": _nice_ceil(so[-1][1] * 1.08),
            "tip": "full", "hline": None, "legend": None,
            "lines": [{"c": "#e01e37", "name": "평가금액", "surv": True, "end": "", "pts": so},
                      {"c": "#111", "name": "원금", "surv": True, "end": "", "pts": inv}]}

def reel_crash():
    tot = SCOMP["smart"]["total_series"]; invs = SCOMP["smart"]["invested_series"]
    return {"title1": "<b>폭락 때만</b> 노려서", "title2": "P&G를 담았더니",
            "sub": "−30% 폭락 때만 매수 · 배당 재투자 · ’00.3~’26.7", "ymax": _nice_ceil(tot[-1][1] * 1.08),
            "tip": "full", "hline": None, "legend": None,
            "lines": [{"c": "#e01e37", "name": "평가금액", "surv": True, "end": "", "pts": tot},
                      {"c": "#8a93a2", "name": "투입원금", "surv": True, "end": "", "pts": invs, "dash": True}]}

def reel_compare():
    """폭락 타이밍 vs 매달 적립 — 4선 병합(순차 드로잉). page15·16을 한 차트로.
       색=전략(폭락 주황 #e0821c / 적립 파랑 #1f6fe0), 실선=평가금액·점선=원금.
       엔진 옵트인 플래그: seq(순차 드로잉)·yleft(y축 라벨 왼쪽)·라인별 phase/lab."""
    tot = SCOMP["smart"]["total_series"]; invs = SCOMP["smart"]["invested_series"]
    so = SCOMP["steady"]["series_on"]; t0 = so[0][0]
    prin = SCOMP["premise"]["principal"]; mi = SCOMP["premise"]["monthly_income"]
    inv = [[x, min(prin, round((x - t0) * 12 * mi))] for x, _ in so]
    peak = max(max(p[1] for p in tot), max(p[1] for p in so))
    return {"title1": "폭락 타이밍 <b>vs</b> 매달 적립", "title2": "26년, 한 화면에서",
            "sub": "−30% 폭락 매수 vs 매달 $1,000 · 배당 재투자 · ’00.3~’26.7",
            "ymax": _nice_ceil(peak * 1.08), "seq": True, "yleft": True, "hline": None,
            "legend": [{"c": "#e0821c", "label": "30% 하락매입"},
                       {"c": "#1f6fe0", "label": "매월매입"}],
            "lines": [
                {"c": "#e0821c", "name": "폭락 평가", "lab": "value", "phase": 0, "surv": True, "end": "", "pts": tot},
                {"c": "#e0821c", "name": "폭락원금", "lab": "named", "phase": 0, "surv": True, "end": "", "pts": invs, "dash": True},
                {"c": "#1f6fe0", "name": "적립 평가", "lab": "value", "phase": 1, "surv": True, "end": "", "pts": so},
                {"c": "#1f6fe0", "name": "적립원금", "lab": "named", "phase": 1, "surv": True, "end": "", "pts": inv, "dash": True}]}


def price_trigger_chart():
    """씬24: PG 주가 + -30% 폭락 매수 신호(★)."""
    ps = SCOMP["price_series"]; lo, hi = SCOMP["price_range"]
    ymax = nice_ceil(hi); ymin = 0
    yt = [[v, f"${v}"] for v in range(0, ymax + 1, max(50, round(ymax / 5 / 50) * 50))][1:]
    return {"kind": "line", "x": [2000, 2026.6], "y": [ymin, ymax], "yticks": yt, "xticks": XTICKS,
            "series": [{"pts": ps, "c": INK, "w": 2.8, "name": "PG 주가", "end": f"${ps[-1][1]}"}],
            "stars": {"series": 0, "years": TRIG_Y, "label": "−30% 폭락 매수",
                      "labelAt": [2013, round(ymax * 0.28)]},
            "legAt": [30, 18]}


def smart_result_chart():
    """씬25: 폭락 매수 — 총자산 + 주식평가액 + 누적 투입(계단식). ★=투입 시점.
       ※ 누적 투입=폭락 때 실제 넣은 금액($119,416), 총소득 $319k 아님(나머지는 현금 대기)."""
    sm = SCOMP["smart"]
    ally = [p[1] for p in sm["total_series"]] + [p[1] for p in sm["stock_series"]]
    ymax = nice_ceil(max(ally))
    return {"kind": "line", "x": [2000, 2026.6], "y": [0, ymax], "yticks": yticks(ymax), "xticks": XTICKS,
            "series": [
                {"pts": sm["total_series"], "c": BLUE, "w": 3.4, "name": "총자산(현금 포함)", "end": money_short(sm["final_on"])},
                {"pts": sm["stock_series"], "c": GREEN, "w": 2.8, "name": "주식평가액", "end": ""}],
            "dline": {"p": sm["invested_series"], "c": INK, "dash": 1,
                      "label": f"누적 투입 {money(sm['invested'])}"},
            "stars": {"series": 1, "years": TRIG_Y, "label": "폭락 때 투입",
                      "labelAt": [2013, round(ymax * 0.5)]},
            "legAt": [30, 20]}


def steady_result_chart():
    """씬26: 적립식 — 배당 재투자 vs 미재투자."""
    sd = SCOMP["steady"]; prin = SCOMP["premise"]["principal"]
    ally = [p[1] for p in sd["series_on"]] + [p[1] for p in sd["series_off"]]
    ymax = nice_ceil(max(ally))
    return {"kind": "line", "x": [2000, 2026.6], "y": [0, ymax], "yticks": yticks(ymax), "xticks": XTICKS,
            "series": [
                {"pts": sd["series_on"], "c": BLUE, "w": 3.4, "name": "배당 재투자", "end": money_short(sd["final_on"])},
                {"pts": sd["series_off"], "c": ORANGE, "w": 3.0, "name": "배당 미재투자", "end": money_short(sd["final_off"])}],
            "dline": {"p": [[2000, 0], [2026.6, prin]], "c": INK, "dash": 1, "label": f"누적 원금 {money(prin)}"},
            "legAt": [30, 20]}


# 물가연동 실제 인출액 표 (CPI 기반)
cpi_df = pd.read_csv(ROOT / "ref" / "fred_CPIAUCSL.csv", parse_dates=["date"])
cpi = pd.Series(pd.to_numeric(cpi_df["val"], errors="coerce").values, index=cpi_df["date"]).dropna()
def cpi_at(y):
    sub = cpi[cpi.index <= pd.Timestamp(y, 6, 1)]
    return float(sub.iloc[-1])
base = cpi_at(2000)
_infl_years = (2000, 2005, 2010, 2015, 2020, 2026)
infl_rows = [[f"'{str(y)[2:]}", *[f"${round(mo*cpi_at(y)/base):,}" for mo in (1000,2000,3000)]]
             for y in _infl_years]
# 가로형(전치) 표 — 헤더밴드(플롯 위 빈 띠)에 얹어 차트 원금별로 선·기준선라벨과 안 겹치게.
_yr_cols = [f"'{str(y)[2:]}" for y in _infl_years]
infl_table = {"title": "물가연동 실제 월 인출액 (CPI)",
              "cols": ["인출", *_yr_cols],
              "rows": [["월 $1천", *[r[1] for r in infl_rows]],
                       ["월 $2천", *[r[2] for r in infl_rows]],
                       ["월 $3천", *[r[3] for r in infl_rows]]],
              "x": 52, "y": 2}  # 제목 우측·플롯 상단 빈 띠(모든 원금 차트에서 선/기준선라벨과 비겹침)

# ── 씬별 data 조립 ──
# 파산 차트는 물가반영(real) 중심 (사용자 결정)
CHART_MAP = {
    "fire_200k": ("real", 200000), "fire_400k": ("real", 400000), "fire_600k": ("real", 600000),
    "fire_200k_2002": ("real2002", 200000), "fire_400k_2002": ("real2002", 400000),
    "fire_600k_2002": ("real2002", 600000),
}
SEC_TITLE = {s["id"]: s["title"] for s in spec["story"]["sections"]}
gN = lambda i, mo: SC[f"nominal_{i}_{mo}"]
rN = lambda i, mo: SC[f"real_{i}_{mo}"]
rN2 = lambda i, mo: SC[f"real2002_{i}_{mo}"]     # 2002년 은퇴


def reveal_chart():
    """후킹 반전: A(월$3k, 파산) vs B(월$1k, 생존) 명목 자산궤적."""
    a, b = gN(400000, 3000), gN(400000, 1000)
    ally = [p[1] for p in a["pts"]] + [p[1] for p in b["pts"]]
    ymax = nice_ceil(max(ally))
    return {"kind": "line", "x": [2000, 2026.6], "y": [0, ymax], "yticks": yticks(ymax),
            "xticks": XTICKS,
            "series": [
                {"pts": b["pts"], "c": BLUE, "w": 3.6, "name": "B · 월 $1천", "end": money_short(b["final"])},
                {"pts": a["pts"], "c": RED, "w": 3.2, "name": "A · 월 $3천",
                 "end": f"{a['depletion'][:4]} 파산"}],
            "hline": {"v": 400000, "c": INK, "dash": 1, "label": "은퇴 원금 $400,000"},
            "legAt": [34, 20]}


def survheat_grid():
    inits = [200000, 400000, 600000]; mos = [1000, 2000, 3000]
    def grid(fn):
        out = []
        for i in inits:
            out.append([0 if not fn(i, mo)["survived"] else (2 if fn(i, mo)["final"] >= i else 1)
                        for mo in mos])
        return out
    return {"_survheat": "survheat1", "title": "은퇴 시나리오 [생존 지도]",
            "sub": "2000년 은퇴 · 물가 반영 인출 · 세로=은퇴자금, 가로=월 생활비",
            "rows": ["$200k", "$400k", "$600k"], "cols": ["$1,000", "$2,000", "$3,000"],
            "grids": [{"label": "2000년 은퇴 · 물가반영", "cells": grid(rN)}],
            "annoMain": "적게 쓸수록 · 원금 클수록 [생존]",
            "annoSub": "초록 생존 · 노랑 위험(원금 하회) · 빨강 파산"}


def news_checks():
    return {"title": "PG, 요즘 어떤가 — [FY2025 실적]", "sub": f"실적 {BIZ['latest_q_label']}(6/30 종료) · 배당·밸류에이션 {BIZ['yield_asof']} 기준 · PG IR·SEC",
            "name": "P&G (PG)", "tag": f"{BIZ['div_years']}년 배당왕",
            "items": [
                [f"매출 ${BIZ['rev_total_b']:.1f}B", f"유기적 매출 +{BIZ['organic_sales_pct']:.0f}% — 가격·믹스로 성장"],
                [f"순이익 ${BIZ['net_income_b']:.1f}B", f"전년비 +{BIZ['net_income_growth_pct']:.0f}%"],
                [f"EPS ${BIZ['eps']}", f"+{BIZ['eps_growth_pct']:.0f}% · 주주환원 ${BIZ['shareholder_return_b']:.0f}B+"],
                [f"배당수익률 ~{BIZ['dividend_yield_pct']}%", f"시총 ${BIZ['market_cap_b']:.0f}B · payout {BIZ['payout_ratio_pct']:.0f}%"]],
            "verdict": "생활필수품 브랜드로 버는 70년 배당왕",
            "anno": "매출은 제자리여도 가격·믹스로 이익 성장"}


def divbars_data():
    src = spec["data"].get("annual_dividends_full") or spec["data"]["annual_dividends"]  # 전체 배당 이력(1962~) 우선
    vals = [[int(y), round(v, 2)] for y, v in src if int(y) <= 2025]
    yr0, v0, vN = int(src[0][0]), float(src[0][1]), float(src[-1][1])
    return {"_divcupRevert": "revert1", "title": f"{BIZ['div_years']}년 연속 [배당 인상]",
            "sub": f"주당 연간 배당금 · $ ({yr0}~2025 실측 · 분할조정)", "vals": vals, "unit": "$", "cut": [], "flat": [],
            "annoMain": "한 해도 거르지 않고 매년 인상",
            "annoSub": f"${v0:.2f} → ${vN:.2f} · 주당 연배당 약 {round(vN/v0)}배"}


def dur_for(lines):
    chars = sum(len(l.replace(" ", "")) for l in lines)
    return max(3000, int((chars / 5 / 1.18 + 1.2) * 1000))


# 씬 인덱스 → 배경영상 bgid (내러티브 씬만; 차트/생존지도/막대 씬은 종이=null 유지)
# 씬 인덱스 → 배경영상 (23씬 기준; 차트/생존지도/막대 씬은 종이=null)
BGID = {                   # 전 씬 맥도날드 실사(사용자 지정) — 톤 매칭
    1: "pg_feast",        # 후킹 A (넉넉히 지출 → 푸짐한 버거+감자)
    2: "pg_friends",      # 후킹 B (아껴 재투자 → 밝은 사람들/성장)
    4: "pg_storefront",   # herostat — 실제 맥도날드 매장 외관(establishing)
    6: "pg_customer",     # checks 뉴스 — 손님이 버거+콜라(가성비 소비자)
    7: "pg_fryer",        # interlude → 백테스트1 (튀김 = 본격 분석)
    11: "pg_brunch",      # interlude → 백테스트2 (식사 = 모으는 입장)
    12: "pg_wait",        # 3부 타이밍(드라이브스루 대기)
    13: "pg_crew",        # 3부 적립(주방 꾸준함)
    19: "pg_reflect",     # quotebig (무드 있는 식사 = 결론)
    20: "pg_interior",    # card — 따뜻한 매장 인테리어(브랜딩 마무리)
}

scenes = []
solo_ct = {}               # 섹션별 solostory 카운터
# 후킹(명목 40만) 실측 파생 — accent 문구 드리프트 방지
_hkA = SC["nominal_400000_3000"]; _hkB = SC["nominal_400000_1000"]
_hkA_yr = _hkA["depletion"][:4]; _hkA_n = int(_hkA_yr) - 2000
_hkB_mult = round(_hkB["final"] / 400000)

# ── 새 element TPL 데이터 (비차트 씬 다양화 · 전부 실측 인용) ──
def _bal(scen, yr):
    c = [p for p in scen.get("pts", []) if abs(p[0] - yr) < 0.6]
    return round(c[-1][1]) if c else 0
NEWSOLO = {}
RECEIPT = {"side": "a", "who": "A · 넉넉히", "amount": "$3,000", "note": "매달 인출 · 부족분 주식 매도",
    "subhead": "은퇴계좌 명세", "foot": "거래 승인 거부", "stamp": "파산",
    "rows": [["은퇴자금", "$400,000", "top"], ["매달 인출", "−$3,000", "dim"],
             [f"2005 잔고", money(_bal(_hkA, 2005)), ""],
             [f"2007 잔고", money(_bal(_hkA, 2007)), ""],
             [f"{_hkA_yr} 잔고", "$0", "bust"]]}
PASSBOOK = {"side": "b", "who": "B · 아껴", "amount": "$1,000", "note": "남는 배당 전액 재투자",
    "subhead": "적립 통장", "foot": f"— 약 {_hkB_mult}배 —", "stamp": "생존",
    "rows": [["은퇴자금", "$400,000", "top"], ["배당 재투자", "＋", "dim"],
             [f"2015 잔고", money(_bal(_hkB, 2015)), ""],
             [f"2020 잔고", money(_bal(_hkB, 2020)), ""],
             [f"2026 잔고", money(_hkB["final"]), "win"]]}
HERO = {"eye": f"생활필수품 배당왕 · 전 세계 단 {BIZ['rarity_count']}곳뿐",
    "big": f"{BIZ['div_years']}년", "under": "연속 배당 증액 — Dividend King"}
_SEG = BIZ["segments"]                                    # 5개 보고부문
# 파이차트 부문색 (덱 톤과 조화: 파랑·주황·초록·빨강·골드) — 범례·조각 공용
_SEG_COLORS = ["#4a8dff", "#e08a3c", "#3fc890", "#ff7a68", "#ffd64a"]
_SEG_TOT = sum(s["rev_b"] for s in _SEG)                  # 83.5B (합계)
# page4: 배경영상(pg_storefront) 위 애니메이션 도넛 파이(5부문 순차 그리기)+색상 범례
MENU = {"title": f"생활필수품 [브랜드 제국] · {BIZ['brands_count']}개 브랜드",
    "sub": "FY2025 부문별 매출 · SEC 8-K (as-of 2026-07)",
    "total": f"${_SEG_TOT:.1f}B",
    "segments": [
        {"ko": s["ko"], "pct": s["share_pct"], "rev": f"${s['rev_b']:.1f}B",
         "brands": s["brands"], "color": c}
        for s, c in zip(_SEG, _SEG_COLORS)]}
# page4: 제품 엘리먼트 제거(사용자 요청) — 정중앙 파이 카드만. 필요시 assets/products/ 4종 재활용 가능.
MENU["products"] = []
SECT_P2 = {"tone": "d", "num": "2", "phrase": "은퇴 시나리오", "part": "2부 · 은퇴 시나리오", "head": "얼마면, 매달 얼마까지|써도 버틸까?", "sub": "물가상승까지 반영한, 진짜 냉혹한 그림."}
SECT_P3 = {"tone": "g", "num": "3", "phrase": "매수 방법", "part": "3부 · 매수 방법", "head": "매달 천 달러씩 25년,|어떻게 사야 가장 클까?", "sub": "두 투자자가 있습니다."}
DRIVETHRU = {"head": "DRIVE-THRU · 타이밍 투자자", "corner": "2000~",
    "items": [["폭락 대기 (−30%)", "현금 연 3%"], ["배당", "전액 재투자"]],
    "wait": "▶ −30% 대기 중…", "tot": f"25년간 폭락 [{len(TRIG_Y)}]시기뿐"}
STAMPCARD = {"title": "적립 투자자 · 시간을 믿는다", "sub": "매달 1칸씩 · 25년 · 배당 전액 재투자",
    "total": 25, "filled": 25, "foot": f"꼬박꼬박 → {money(SCOMP['steady']['final_on'])}"}
for n in NARR:
    tpl, lines = n["tpl"], n["lines"]
    cam = {"s": 1.0 if tpl == "videohook" else 1.03, "x": 50, "y": 50}
    sc = {"tpl": tpl, "dur": dur_for(lines), "cam": cam,
          "bgid": {"checks": "pg_customer", "quotebig": "pg_reflect", "card": "pg_interior"}.get(tpl),
          "subLines": lines, "data": {}}
    d = sc["data"]

    # ── 새 element TPL 리매핑 (비차트 씬만; 차트·notice·checks·hbars2·divbars·quote·card는 유지) ──
    _rm = None   # (tpl, data, bgid) — 새 TPL 뒤에 배경영상 배치(반투명 오버레이로 은은히)
    if tpl == "herostat":
        _rm = ("hero", HERO, "pg_storefront")
    elif tpl == "kpirow":
        _rm = ("menuboard", MENU, "pg_storefront")   # 부문별 매출: 슈퍼마켓 매대 영상 위 애니 파이차트
    elif tpl == "interlude":
        _rm = ("sectint", SECT_P2, "pg_reflect") if n["sec"] == "part2" else ("sectint", SECT_P3, "pg_storefront")
    elif tpl == "solostory":
        _r = NEWSOLO.get(n["sec"], 0); NEWSOLO[n["sec"]] = _r + 1
        if n["sec"] == "hook":
            _rm = ("stmt", RECEIPT, "pg_feast") if _r == 0 else ("stmt", PASSBOOK, "pg_friends")
        elif n["sec"] == "part3":
            _rm = ("drivethru", DRIVETHRU, "pg_wait") if _r == 0 else ("stampcard", STAMPCARD, "pg_crew")
    if _rm:
        sc["tpl"], sc["data"], sc["bgid"] = _rm
        scenes.append(sc); continue

    if tpl == "videohook":
        d["src"] = "bg/elderly_calm.mp4"  # 오프닝 훅 = 노부부(같은 돈 다른 운명)
        d["aiNote"] = " "             # 기본 'AI 제작' 문구 억제(스톡 영상이므로)
    elif tpl == "notice":
        d.update({"title": "유의사항", "lines": [
            "정보 제공용 · <b>투자 권유 아님</b>",
            "<b>과거 수익률 ≠ 미래 보장</b>"]})
    elif tpl == "solostory":
        # 섹션 기반(씬 번호 변동에 견고): 각 섹션의 첫 solostory=a, 둘째=b
        role = solo_ct.get(n["sec"], 0); solo_ct[n["sec"]] = role + 1
        if n["sec"] == "hook" and role == 0:      # 후킹 A 파산
            d.update({"_fire": True, "side": "a", "label": "A", "kick": "2000년, PG로 은퇴한 두 사람",
                      "tag": "같은 돈, 넉넉한 생활비", "rows": [
                        "은퇴자금 <b>$400,000</b>", "매달 <b>$3,000</b>씩 넉넉하게 썼다",
                        "부족분은 주식을 팔아 충당"], "accent": f"{_hkA_n}년 뒤 {_hkA_yr}년, 잔고 $0 — 파산"})
        elif n["sec"] == "hook":                  # 후킹 B 생존
            d.update({"side": "b", "label": "B", "kick": "2000년, PG로 은퇴한 두 사람",
                      "tag": "같은 돈, 아낀 생활비", "rows": [
                        "은퇴자금 <b>$400,000</b> — A와 동일", "매달 <b>$1,000</b>씩만 아껴 썼다",
                        "남는 배당은 재투자"], "accent": f"26년 뒤 {money(_hkB['final'])} — 약 {_hkB_mult}배로 증가"})
        elif role == 0:                           # 3부 타이밍(폭락)
            d.update({"_fire": True, "side": "a", "label": "타이밍", "kick": "2000년, 두 투자자",
                      "tag": "타이밍을 노린다", "rows": [
                        "폭락(−30%)을 기다렸다 <b>싸게</b> 매수", "평소엔 현금으로 대기 (연 3%)",
                        "배당은 전액 재투자"], "accent": "−30% 대기…"})
        else:                                     # 3부 적립
            d.update({"side": "b", "label": "적립", "kick": "2000년, 두 투자자",
                      "tag": "시간을 믿는다", "rows": [
                        "매달 꼬박꼬박 매수 <b>(적립식)</b>", "타이밍은 신경 안 씀",
                        "배당은 전액 재투자"], "accent": "25년 →"})
    elif tpl == "herostat":   # (사문화 — herostat은 위 _rm에서 hero로 치환·continue됨. 참조 안전용 PG 값 유지)
        d.update({"eyebrow": "머니 리서치 — 종목 소개",
                  "num": f"{BIZ['div_years']}년",
                  "label": f"연속 배당 증액 — {BIZ['div_label']}  {{{{pg}}}}",
                  "sub": f"세제·기저귀·면도 등 {BIZ['brands_count']}개 핵심 브랜드 · 전 세계 단 {BIZ['rarity_count']}곳뿐인 배당왕 · 시총 ${BIZ['market_cap_b']:.0f}B"})
    elif tpl == "kpirow":     # (사문화 — kpirow은 위 _rm에서 menuboard로 치환·continue됨)
        d.update({"title": "생활필수품 [브랜드 제국]",
                  "sub": f"FY2025 부문별 매출 · 배당수익률 {BIZ['dividend_yield_pct']}% ({BIZ['yield_asof']})",
                  "tiles": [
                    {"value": f"${s['rev_b']:.1f}B", "label": s['ko'],
                     "delta": f"매출 {s['share_pct']:.0f}%", "dir": "up"}
                    for s in BIZ["segments"][:4]],
                  "src": "PG FY2025 8-K · SEC"})
    elif tpl == "interlude":
        pass  # 자막만
    elif tpl == "survheat":
        d.update(survheat_grid())
    elif tpl == "checks":
        d.update(news_checks())
    elif tpl == "divbars":
        d.update(divbars_data())
    elif tpl == "enginechart":
        chart_id = n.get("chart")
        # 글자 최소화: 짧은 제목 + 차트 + 핵심 한 줄(annoMain)만.
        if chart_id == "reveal":       # 후킹 반전 (명목 A vs B)
            d.update({"_fire": True, "sub": "",
                      "title": "같은 $400,000 · 매달 쓴 돈만 다르면?",
                      "annoMain": "지출이 26년 뒤 운명을 갈랐다",
                      "chart": reveal_chart()})
        elif chart_id in CHART_MAP:    # 파산 시나리오 (물가반영)
            strat_key, init = CHART_MAP[chart_id]
            is2002 = chart_id.endswith("_2002")
            if not is2002:   # 2000년 은퇴 세트 → 릴스 스타일 개별 그래프
                sc["tpl"] = "reelchart"; d.clear(); d.update(reel_fire(init))
                scenes.append(sc); continue
            yr_tag = "2002년 은퇴"          # 2002 세트는 유지(deck_plan에서 드롭 예정)
            d.update({"_fire": True, "sub": "",
                      "title": f"{money(init)} · {yr_tag} [물가반영]",
                      "chart": fire_chart(init, strat_key)})
            if is2002:   # 닷컴 저점(2002)에 싸게 진입 → PG는 오히려 크게 유리 (실측 기반)
                _sv = [mo for mo in (1000, 2000, 3000) if rN2(init, mo)["survived"]]
                if len(_sv) == 3:
                    d["annoMain"] = "닷컴 저점 진입 — 물가 반영해도 셋 다 생존"
                elif _sv:
                    d["annoMain"] = f"월 ${_sv[-1] // 1000}천까지 생존 · 나머지는 파산"
                else:
                    d["annoMain"] = "셋 다 파산"
            else:
                _ry = lambda mo: (SC[f"real_{init}_{mo}"]["depletion"] or "")[:4]
                d["annoMain"] = {
                    200000: f"물가 반영하면 셋 다 파산 — 월 $1천도 {_ry(1000)}년",
                    400000: f"월 $1천만 생존 · $2천 {_ry(2000)}·$3천 {_ry(3000)}년 파산",
                    600000: f"월 $3천은 물가에 밀려 {_ry(3000)}년 파산"}[init]
            d["table"] = infl_table   # 모든 FIRE 차트(real·real2002 · 20/40/60만)에 물가표 부착
        elif chart_id == "price_trigger":   # 씬24: 주가 + 폭락 신호
            d.update({"sub": "", "title": "PG 주가와 [−30% 폭락] 매수 신호",
                      "annoMain": f"25년간 −30% 폭락은 {'·'.join(str(y) for y in TRIG_Y)}년, 세 시기뿐",
                      "chart": price_trigger_chart()})
        elif chart_id == "smart_result":    # 씬25: 폭락 vs 적립 4선 병합(page16=적립은 deck_plan에서 드롭)
            sc["tpl"] = "reelchart"; d.clear(); d.update(reel_compare())
        elif chart_id == "steady_result":   # 씬26: (병합됨) — deck_plan.json에서 이 페이지 드롭. 폴백용 개별 차트 유지
            sc["tpl"] = "reelchart"; d.clear(); d.update(reel_steady())
    elif tpl == "hbars2":
        sm, sd = SCOMP["smart"], SCOMP["steady"]
        prin = SCOMP["premise"]["principal"]
        gap = (sm["final_on"] / sd["final_on"] - 1) * 100
        mx = nice_ceil(max(sm["final_on"], sd["final_on"]))
        # 폭락매수 정직 분해: 실투입(주식화 원금) + 자본이득 + 배당재투자 + 유휴현금(끝까지 안 굴린 돈)
        sm_inv = sm["invested"]                                  # 119,416
        sm_cash = sm["cash_left"]                                # 273,016
        sm_gain = sm["final_off"] - sm_inv - sm_cash             # 509,474
        sm_div = sm["final_on"] - sm["final_off"]                # 374,111
        d.update({"title": "폭락 타이밍 vs 매달 적립", "sub": "",
                  "left": {"head": "폭락에 몰아서",
                           "invLabel": f"실투입 {money(sm_inv)} · 대기현금 {money(sm_cash)}", "max": mx,
                           "rows": [
                             {"name": "배당 미재투자", "inv": sm_inv, "gain": sm_gain, "cash": sm_cash,
                              "label": money(sm["final_off"])},
                             {"name": "배당 재투자", "inv": sm_inv, "gain": sm_gain,
                              "div": sm_div, "cash": sm_cash, "label": money(sm["final_on"])}]},
                  "right": {"head": "매달 꾸준히", "invLabel": f"원금 {money(prin)} 전액 투입", "max": mx,
                            "rows": [
                              {"name": "배당 미재투자", "inv": prin, "gain": sd["final_off"] - prin,
                               "label": money(sd["final_off"])},
                              {"name": "배당 재투자", "inv": prin, "gain": sd["final_off"] - prin,
                               "div": sd["final_on"] - sd["final_off"], "label": money(sd["final_on"]), "win": True}]},
                  "annoMain": f"완벽한 타이밍도 오히려 [{gap:+.0f}%]",
                  "annoSub": f"수익률(XIRR)도 적립 {sd['xirr_on']:.1f}% > 폭락 {sm['xirr_on']:.1f}% · 폭락매수는 현금 {sm['avg_cash_ratio_pct']:.0f}%가 놀았다"})
    elif tpl == "quotebig":
        d.update({"quote": "시간은 당신의 친구,|충동은 당신의 [적]이다",
                  "source": "존 보글 — 뱅가드 창업자·인덱스펀드의 아버지", "img": None})
    elif tpl == "card":
        d.update({"eyebrow": "머니 리서치 — 배당주 백테스트",
                  "main": f"{{{{pg}}}}|[{BIZ['div_years']}년 {BIZ['div_label']}]",
                  "sub": "배당으로 은퇴하는 이야기 — 다음 종목도 이어집니다",
                  "chips": [[f"${BIZ['annual_dividend_ps']}", "연 배당"],
                            [f"{BIZ['div_years']}년", "연속 증배"],
                            [f"${BIZ['market_cap_b']:.0f}B", "시가총액"]]})
    scenes.append(sc)

# ── deck_plan.json 적용(있으면): 파이프라인 편집기의 재정렬·추가·삭제를 실제 씬에 반영 ──
#    ref = 안정적 sid(원본 1-based 페이지). 새 씬(ref가 base에 없음)은 이전 빌드에서 내용 보존, 없으면 빈 sectint.
import copy as _copy
for _i, _s in enumerate(scenes):
    _s["sid"] = _i + 1
_planf = ROOT / "spec" / "deck_plan.json"
if _planf.exists():
    try:
        _plan = json.load(open(_planf, encoding="utf-8"))
        _pgs = [it for it in _plan if it.get("t") == "pg"]
        if _pgs:
            _base = {s["sid"]: s for s in scenes}
            _prev = {}
            _pf = ROOT / "deck" / "pg_deck.json"
            if _pf.exists():
                try:
                    _prev = {s.get("sid"): s for s in json.load(open(_pf))["scenes"] if s.get("sid") is not None}
                except Exception:
                    _prev = {}
            _tmpl = next((s for s in scenes if s.get("tpl") == "sectint"), scenes[0])
            _out = []
            for _it in _pgs:
                _ref = _it.get("ref")
                if _ref in _base:                       # 기존 씬 유지(순서=plan)
                    _out.append(_base[_ref])
                elif _ref in _prev:                     # 이전 빌드의 새 씬 → 내용 보존
                    _out.append(_prev[_ref])
                else:                                   # 신규 → 빈 sectint 복제
                    _ns = _copy.deepcopy(_tmpl)
                    _ns["sid"] = _ref if _ref is not None else f"new{len(_out)}"
                    _ns["subLines"] = []
                    _ns["data"] = {"tone": "d", "part": "새 씬",
                                   "head": (_it.get("title") or "새 페이지") + "|",
                                   "sub": "덱 편집기에서 내용을 채우세요"}
                    _out.append(_ns)
            scenes = _out
            print(f"deck_plan 적용 → {len(scenes)}씬 (재정렬·추가·삭제 반영)")
    except Exception as _e:
        print("deck_plan 적용 실패(원본 유지):", _e)

# ── 자막 편집 스냅샷 적용: 덱 에디터 💾저장(→deck_edited_scenes.json)한 자막을 재빌드에도 유지 ──
#   build_deck가 이 파일을 안 읽어 '최신본'(재빌드) 누르면 자동자막으로 되돌아가던 문제 해결.
#   sid로 매핑(구조 바뀌어도 안전), 미스 시 인덱스 폴백.
#   우선순위: 패널 자막저장(narration_final)이 스냅샷보다 최신이면 그 씬은 패널 편집을 유지(스냅샷 스킵).
_esf = ROOT / "spec" / "deck_edited_scenes.json"
_nff = ROOT / "spec" / "narration_final.json"
if _esf.exists():
    try:
        _es = json.load(open(_esf, encoding="utf-8"))
        _es = _es.get("scenes", _es) if isinstance(_es, dict) else _es
        _sub_by_sid = {s.get("sid"): s.get("subLines") for s in _es
                       if s.get("sid") is not None and s.get("subLines")}
        _nf_sids = set()                                # 패널 자막저장(narration_final) = 자막의 소스 오브 트루스 → 항상 우선(스냅샷 스킵)
        if _nff.exists():                               # 사용자 워크플로우가 패널 편집이므로 무조건 우선(스냅샷은 미편집 씬만 채움)
            _nf = json.load(open(_nff, encoding="utf-8"))
            _nf_sids = {int(k) + 1 for k in _nf if str(k).lstrip("-").isdigit()}  # narration_final 키=sid-1
        _n = 0
        for _i, _s in enumerate(scenes):
            if _s.get("sid") in _nf_sids:               # 패널 편집이 더 최신 → base(narration_final) 유지
                continue
            _ov = _sub_by_sid.get(_s.get("sid"))
            if _ov is None and _i < len(_es):           # sid 미스 시 인덱스 폴백
                _ov = _es[_i].get("subLines") or None
            if _ov:
                _s["subLines"] = _ov; _n += 1
        print(f"자막 스냅샷 적용(deck_edited_scenes): {_n}씬 · 패널최신 제외 {len(_nf_sids)}")
        # 씬별 솔리드 배경색(bgcol): GUI에서 지정·💾저장한 배경색을 재빌드에도 유지(자막과 무관하게 항상 적용)
        _bg_by_sid = {s.get("sid"): s.get("bgcol") for s in _es
                      if s.get("sid") is not None and s.get("bgcol")}
        _nb = 0
        for _i, _s in enumerate(scenes):
            _bc = _bg_by_sid.get(_s.get("sid"))
            if _bc is None and _i < len(_es):
                _bc = _es[_i].get("bgcol")
            if _bc:
                _s["bgcol"] = _bc; _nb += 1
        if _nb:
            print(f"씬 배경색 적용(bgcol): {_nb}씬")
    except Exception as _e:
        print("자막 스냅샷 적용 실패(무시):", _e)

deck = {"scenes": scenes, "ov": {}, "cp": {}, "theme": "blueprint", "paper": "photo"}  # 사용자 선택: 블루프린트(설계도) 배경
json.dump(deck, open(ROOT / "deck" / "pg_deck.json", "w"), ensure_ascii=False, indent=1)

# ── HTML 주입: KEY 교체 + 코카콜라 패치 IIFE 블록 제거 + '저장된 편집 우선' 조건부 주입 ──
#   → HUD 편집(localStorage 저장)이 새로고침 후에도 유지됨. 최초 로드(저장본 없음)에만 하드코딩 주입.
html = (ROOT / "deck" / "pg_final.html").read_text(encoding="utf-8")
html = html.replace("const KEY = 'tplCatalog_cocacola_v4g';", "const KEY = 'tplCatalog_pg_v4';")  # v3→v4: 옛 localStorage 스냅샷(자막 가림) 무력화 → 재빌드된 SCENES(자막·OV 포함) 강제 로드
blk_start = html.index("/* FIRE 세트")             # 패치 IIFE 블록 시작(v8-hook 앞 주석)
p = html.index("var VER='src1';", blk_start)
blk_end = html.index("})();", p) + len("})();")     # src1 IIFE 끝
override = ("/* ══ PG 덱 주입 — 항상 서버 빌드본(자막·OV 포함)을 사용. localStorage 스냅샷은 무시.\n"
            "      (옛 localStorage가 저장·재굽기된 최신본을 가려 '저장해도 안 바뀜'으로 보이던 문제 근절.\n"
            "       편집분은 서버 deck_ov.json·deck_edited_scenes.json·narration_final.json에 저장돼 매 빌드 재적용됨.)\n"
            "      코카콜라 패치 IIFE 4종은 편집 오염 방지 위해 제거함. ══ */\n"
            "SCENES = " + json.dumps(scenes, ensure_ascii=False) + ";\n"
            "OV = " + json.dumps(DECK_OV, ensure_ascii=False) + "; CP = {}; THEME='blueprint'; PAPER='photo';\n"
            "try{ localStorage.removeItem(KEY); }catch(e){}\n")
html = html[:blk_start] + override + html[blk_end:]

# ── 배경영상 data URI embed → 자립형(다운로드 후 바로 재생) ──
import base64
bgdir = ROOT / "deck" / "bg"
for mp4 in sorted(bgdir.glob("*.mp4")):
    ref = f"bg/{mp4.name}"
    if ref in html:
        uri = "data:video/mp4;base64," + base64.b64encode(mp4.read_bytes()).decode()
        html = html.replace(ref, uri)
(ROOT / "deck" / "pg_v1.html").write_text(html, encoding="utf-8")

print(f"씬 {len(scenes)}개 조립 · 총 dur {sum(s['dur'] for s in scenes)/1000:.0f}s")
print("enginechart:", [n.get("chart") for n in NARR if n["tpl"] == "enginechart"])
print("물가표 최근행:", infl_rows[-1])
print(f"→ deck/pg_v1.html ({len(html)//1024}KB, 자립형) · deck/pg_deck.json")
