# -*- coding: utf-8 -*-
"""D단계 덱 조립 → 자립형 viewable HTML.
   spec(scenarios/strategy/narration/business) → 씬 JSON → mcd_final.html DEFAULT 이후 강제주입.
   철칙: 차트 pts·수치는 backtest 인용. cocacola 패치 IIFE(v8-hook/revert1/survheat1/src1)는
   1889라인 직후 SCENES 덮어쓰기로 무력화.
   사용: python deck/build_deck.py  →  deck/mcd_v1.html · deck/mcd_deck.json
"""
import json, sys, math
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "spec"))
import spec as S
import pandas as pd

spec = S.load_spec(str(ROOT / "spec" / "MCD.json"))
SC = {s["id"]: s for s in spec["backtest"]["fire"]["scenarios"]}
STRAT = spec["backtest"]["strategy_compare"]["strategies"]
BIZ = spec["data"]["business"]
NARR = json.load(open(ROOT / "spec" / "narration_draft.json"))

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
        tag = f"월 ${mo//1000}천"                       # 월 $1천 / $2천 / $3천 (선 색으로 구분)
        end = f"{tag} {money_short(s['final'])}" if s["survived"] else f"{tag} {s['depletion'][:4]} 파산"
        series.append({"pts": s["pts"], "c": c, "w": w, "name": f"월 ${mo:,}", "end": end})
    ymax = nice_ceil(max(ally))
    # 범례 제거 → 각 선 끝 라벨(월 $X)로 대체(라벨이 선에 붙어 겹침 불가)
    return {"kind": "line", "x": [2000, 2026.6], "y": [0, ymax], "yticks": yticks(ymax),
            "xticks": XTICKS, "series": series, "noLegend": True,
            "hline": {"v": init, "c": INK, "dash": 1, "label": f"은퇴 원금 {money(init)}"}}


SCOMP = spec["backtest"]["strategy_compare"]          # 3부 전체 데이터
TRIG_Y = sorted({int(t["date"][:4]) for t in SCOMP["deck_triggers"]})


def price_trigger_chart():
    """씬24: MCD 주가 + -30% 폭락 매수 신호(★)."""
    ps = SCOMP["price_series"]; lo, hi = SCOMP["price_range"]
    ymax = nice_ceil(hi); ymin = 0
    yt = [[v, f"${v}"] for v in range(0, ymax + 1, max(50, round(ymax / 5 / 50) * 50))][1:]
    return {"kind": "line", "x": [2000, 2026.6], "y": [ymin, ymax], "yticks": yt, "xticks": XTICKS,
            "series": [{"pts": ps, "c": INK, "w": 2.8, "name": "MCD 주가", "end": f"${ps[-1][1]}"}],
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
infl_rows = [[f"'{str(y)[2:]}", *[f"${round(mo*cpi_at(y)/base):,}" for mo in (1000,2000,3000)]]
             for y in (2000, 2005, 2010, 2015, 2020, 2026)]
infl_table = {"title": "물가연동 실제 월 인출액", "cols": ["연", "$1k", "$2k", "$3k"],
              "rows": infl_rows, "x": 60, "y": 5}  # 상단 빈 공간(생존선·끝점라벨과 겹침 방지)

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
                {"pts": b["pts"], "c": BLUE, "w": 3.6, "name": "B · 월 $1천 (아껴 씀)", "end": money_short(b["final"])},
                {"pts": a["pts"], "c": RED, "w": 3.2, "name": "A · 월 $3천 (넉넉히)",
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
    return {"title": "MCD, 요즘 어떤가 — [최신 근황]", "sub": "2026년 기준 · 출처 MCD IR·SEC",
            "name": "존슨앤드존슨 (MCD)", "tag": "64년 배당왕",
            "items": [
                ["실적 신기록", "사상 첫 매출 $100B 돌파 — 2026 가이던스 상향"],
                ["신약 성장", "트렘피아 +72% · 다잘렉스 +19%"],
                ["의료기기 확장", "수술로봇 오타바(OTTAVA) FDA 승인"],
                ["최대 리스크", "탈크 소송 진행 중 — 파산 전략 무산"]],
            "verdict": "방어력과 소송 리스크가 공존하는 배당왕",
            "anno": "방어주의 안정성 vs 진행 중인 소송 불확실성"}


def divbars_data():
    vals = [[int(y), round(v, 2)] for y, v in spec["data"]["annual_dividends"] if int(y) <= 2025]
    return {"_divcupRevert": "revert1", "title": f"{BIZ['dividend_king_years']}년 연속 [배당 인상]",
            "sub": "주당 연간 배당금 · $ (2000~2025 실측)", "vals": vals, "unit": "$", "cut": [], "flat": [],
            "annoMain": "한 해도 거르지 않고 매년 인상",
            "annoSub": f"${vals[0][1]:.2f} → ${vals[-1][1]:.2f} · 주당 연배당 약 {vals[-1][1]/vals[0][1]:.0f}배"}


def dur_for(lines):
    chars = sum(len(l.replace(" ", "")) for l in lines)
    return max(3000, int((chars / 5 / 1.18 + 1.2) * 1000))


# 씬 인덱스 → 배경영상 bgid (내러티브 씬만; 차트/생존지도/막대 씬은 종이=null 유지)
# 씬 인덱스 → 배경영상 (23씬 기준; 차트/생존지도/막대 씬은 종이=null)
BGID = {
    1: "hourglass_time",   # 후킹 solo A (지출 과다 → 시간 소진)
    2: "sprout_growth",    # 후킹 solo B (아껴 재투자 → 성장)
    4: "lab_research",     # herostat
    6: "lab_research",     # checks 뉴스
    7: "warm_window",      # interlude → 백테스트1 (사용자 지정: 창가햇살)
    11: "sprout_growth",   # interlude → 백테스트2
    12: "hourglass_time",  # 3부 타이밍(폭락 대기)
    13: "sprout_growth",   # 3부 적립
    19: "warm_window",     # quotebig
    20: "warm_window",     # card
}

scenes = []
solo_ct = {}               # 섹션별 solostory 카운터
for n in NARR:
    tpl, lines = n["tpl"], n["lines"]
    cam = {"s": 1.0 if tpl == "videohook" else 1.03, "x": 50, "y": 50}
    sc = {"tpl": tpl, "dur": dur_for(lines), "cam": cam, "bgid": BGID.get(n["scene"]),
          "subLines": lines, "data": {}}
    d = sc["data"]

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
            d.update({"_fire": True, "side": "a", "label": "A", "kick": "2000년, MCD로 은퇴한 두 사람",
                      "tag": "같은 돈, 넉넉한 생활비", "rows": [
                        "은퇴자금 <b>$400,000</b>", "매달 <b>$3,000</b>씩 넉넉하게 썼다",
                        "부족분은 주식을 팔아 충당"], "accent": "18년 뒤 2018년, 잔고 $0 — 파산"})
        elif n["sec"] == "hook":                  # 후킹 B 생존
            d.update({"side": "b", "label": "B", "kick": "2000년, MCD로 은퇴한 두 사람",
                      "tag": "같은 돈, 아낀 생활비", "rows": [
                        "은퇴자금 <b>$400,000</b> — A와 동일", "매달 <b>$1,000</b>씩만 아껴 썼다",
                        "남는 배당은 재투자"], "accent": "26년 뒤 $2,435,842 — 6배로 증가"})
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
    elif tpl == "herostat":
        d.update({"eyebrow": "머니 리서치 — 종목 소개",
                  "num": f"{BIZ['dividend_king_years']}년",
                  "label": "연속 배당 증액 — 배당왕  {{mcd}}",
                  "sub": f"2023년 Kenvue(소비자건강) 분사 → 제약 + 의료기기 두 축 · 시총 ${BIZ['market_cap_b']:.0f}B"})
    elif tpl == "kpirow":
        seg = {s["ko"]: s for s in BIZ["segments"]}
        d.update({"title": "사업은 견조하게 [성장] 중",
                  "sub": f"2025 회계연도 (전년 대비) · 배당수익률 {BIZ['dividend_yield_pct']}%",
                  "tiles": [
                    {"value": f"${seg['제약']['fy2025_rev_b']:.1f}B", "label": "제약 매출",
                     "delta": f"{seg['제약']['share_pct']:.0f}%", "dir": "up"},
                    {"value": f"${seg['의료기기']['fy2025_rev_b']:.1f}B", "label": "의료기기 매출",
                     "delta": f"{seg['의료기기']['share_pct']:.0f}%", "dir": "up"},
                    {"value": f"${BIZ['fy2025_revenue_b']:.1f}B", "label": "총매출",
                     "delta": f"+{BIZ['fy2025_yoy_pct']:.0f}%", "dir": "up"},
                    {"value": f"${BIZ['annual_dividend_ps']}", "label": "연 배당(주당)",
                     "delta": f"{BIZ['dividend_king_years']}년째", "dir": "up"}],
                  "src": "MCD IR · SEC 8-K (FY2025)"})
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
            yr_tag = "2002년 은퇴" if is2002 else "2000년 은퇴"
            d.update({"_fire": True, "sub": "",
                      "title": f"{money(init)} · {yr_tag} [물가반영]",
                      "chart": fire_chart(init, strat_key)})
            if is2002:   # 닷컴버블 저점 은퇴 = 은퇴 직후 폭락(순서 위험)
                dep = lambda mo: (rN2(init, mo)["depletion"] or "")[:4]
                d["annoMain"] = {200000: "셋 다 파산 — 은퇴 직후 폭락의 저주",
                                 400000: f"월 $2천마저 {dep(2000)}년 파산",
                                 600000: f"월 $3천은 {dep(3000)}년 파산"}[init]
            else:
                d["annoMain"] = {200000: "월 $1천도 겨우 · $2천·$3천 파산",
                                 400000: "월 $3천은 2013년 파산",
                                 600000: "물가 반영해도 셋 다 생존"}[init]
                if init == 200000:
                    d["table"] = infl_table
        elif chart_id == "price_trigger":   # 씬24: 주가 + 폭락 신호
            d.update({"sub": "", "title": "MCD 주가와 [−30% 폭락] 매수 신호",
                      "annoMain": f"25년간 −30% 폭락은 {TRIG_Y[0]}·{TRIG_Y[1]}년, 딱 2번",
                      "chart": price_trigger_chart()})
        elif chart_id == "smart_result":    # 씬25: 폭락 매수 결과
            d.update({"_fire": True, "sub": "", "title": "[폭락 때만] 몰아 투자",
                      "annoMain": f"폭락만 노려도 {money(SCOMP['smart']['final_on'])} — 현금 {SCOMP['smart']['avg_cash_ratio_pct']:.0f}%가 놀았다",
                      "chart": smart_result_chart()})
        elif chart_id == "steady_result":   # 씬26: 적립 결과
            d.update({"sub": "", "title": "매달 $1,000 [적립식]",
                      "annoMain": f"적립 + 배당 재투자 {money(SCOMP['steady']['final_on'])}",
                      "chart": steady_result_chart()})
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
        d.update({"quote": "타이밍을 맞히려 하지 말고,|쓰는 돈을 지키고 [꾸준히 모아 재투자]하라.",
                  "source": f"{BIZ['dividend_king_years']}년 연속 증배, 배당왕 존슨앤드존슨", "img": None})
    elif tpl == "card":
        d.update({"eyebrow": "머니 리서치 — 배당주 백테스트",
                  "main": "{{mcd}}|[64년 배당왕]",
                  "sub": "배당으로 은퇴하는 이야기 — 다음 종목도 이어집니다",
                  "chips": [[f"${BIZ.get('annual_dividend_ps',5.36)}", "연 배당"],
                            [f"{BIZ['dividend_king_years']}년", "연속 증배"],
                            [f"${BIZ['market_cap_b']:.0f}B", "시가총액"]]})
    scenes.append(sc)

deck = {"scenes": scenes, "ov": {}, "cp": {}, "theme": "paper", "paper": "photo"}
json.dump(deck, open(ROOT / "deck" / "mcd_deck.json", "w"), ensure_ascii=False, indent=1)

# ── HTML 주입: KEY 교체 + 코카콜라 패치 IIFE 블록 제거 + '저장된 편집 우선' 조건부 주입 ──
#   → HUD 편집(localStorage 저장)이 새로고침 후에도 유지됨. 최초 로드(저장본 없음)에만 하드코딩 주입.
html = (ROOT / "deck" / "mcd_final.html").read_text(encoding="utf-8")
html = html.replace("const KEY = 'tplCatalog_cocacola_v4g';", "const KEY = 'tplCatalog_mcd_v2';")
blk_start = html.index("/* FIRE 세트")             # 패치 IIFE 블록 시작(v8-hook 앞 주석)
p = html.index("var VER='src1';", blk_start)
blk_end = html.index("})();", p) + len("})();")     # src1 IIFE 끝
override = ("/* ══ MCD 덱 주입 — 저장된 편집(localStorage) 있으면 그대로 유지, 없을 때만 주입.\n"
            "      코카콜라 패치 IIFE 4종은 편집 오염 방지 위해 제거함. ══ */\n"
            "if(!localStorage.getItem(KEY)){\n"
            "  SCENES = " + json.dumps(scenes, ensure_ascii=False) + ";\n"
            "  OV = {}; CP = {}; THEME='paper'; PAPER='photo';\n"
            "}\n")
html = html[:blk_start] + override + html[blk_end:]

# ── 배경영상 data URI embed → 자립형(다운로드 후 바로 재생) ──
import base64
bgdir = ROOT / "deck" / "bg"
for mp4 in sorted(bgdir.glob("*.mp4")):
    ref = f"bg/{mp4.name}"
    if ref in html:
        uri = "data:video/mp4;base64," + base64.b64encode(mp4.read_bytes()).decode()
        html = html.replace(ref, uri)
(ROOT / "deck" / "mcd_v1.html").write_text(html, encoding="utf-8")

print(f"씬 {len(scenes)}개 조립 · 총 dur {sum(s['dur'] for s in scenes)/1000:.0f}s")
print("enginechart:", [n.get("chart") for n in NARR if n["tpl"] == "enginechart"])
print("물가표 최근행:", infl_rows[-1])
print(f"→ deck/mcd_v1.html ({len(html)//1024}KB, 자립형) · deck/mcd_deck.json")
