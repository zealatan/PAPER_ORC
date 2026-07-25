# -*- coding: utf-8 -*-
"""stock_alert 덱 조립 — 주간 전고점 대비 낙폭 카운트다운.
   data/weekN.json → 씬 JSON → stock_alert_final.html 에 주입 → stock_alert_v1.html.

   씬: notice · 훅(sectint) · [섹션(sectint) + drawcard×5]×3(ETF/미국/한국) · 통합TOP3 · 마무리
   drawcard 차트 = engChart line + hline(전고점) + dot(현재). 숫자·pts는 weekly_scan 인용(지어내기 차단).
   사용: python3 deck/build_deck.py            (최신 weekN.json 사용)
"""
import base64
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # blog/stock_alert
DECK = ROOT / "deck"
DATA = ROOT / "data"

# 최신 주차 데이터
weeks = sorted(DATA.glob("week*.json"))
if not weeks:
    raise SystemExit("data/weekN.json 없음 — 먼저 weekly_scan.py 실행")
WEEK = json.loads(weeks[-1].read_text(encoding="utf-8"))

RED, INK = "var(--red)", "var(--ink-soft)"
BLUE = "#2563eb"          # 전고점 마커/라벨
LINE = "#2b3d40"          # 가격 선(전고점=파랑·현재=빨강과 구분되는 먹색)
CAT = {"ETF": "📊 ETF", "미국": "🇺🇸 미국주식", "한국": "🇰🇷 한국주식", "유럽": "🇪🇺 유럽주식"}
SEC = {"ETF": ("①", "ETF 낙폭 TOP5"), "미국": ("②", "미국 주식 낙폭 TOP5"),
       "한국": ("③", "한국 주식 낙폭 TOP5"), "유럽": ("④", "유럽 주식 낙폭 TOP5")}
MARKET_ORDER = ["ETF", "미국", "한국", "유럽"]

# ── 통화 심볼 (티커 → CSV currency → 심볼) ──
TICKERS_DIR = ROOT.parent.parent / "global_cup_suite" / "data"
CUR_SYM = {"USD": "$", "KRW": "₩", "EUR": "€", "GBP": "£", "CHF": "CHF ", "JPY": "¥"}
_ccy = {}
for _f in TICKERS_DIR.glob("tickers_*.csv"):
    for _r in csv.DictReader(open(_f, encoding="utf-8")):
        _ccy[_r["ticker"].strip()] = _r["currency"].strip()


def cur_sym(ticker):
    return CUR_SYM.get(_ccy.get(ticker, "USD"), "$")

# ── 로고 해석 (logos/<TICKER|코드>.png · ETF는 운용사 브랜드) ──
LOGODIR = DECK / "logos"
ETF_PREFIX = [("KODEX", "KODEX"), ("TIGER", "TIGER"), ("KBSTAR", "KBSTAR"), ("RISE", "RISE"),
              ("SOL", "SOL"), ("ARIRANG", "ARIRANG"), ("PLUS", "PLUS"), ("ACE", "ACE"),
              ("HANARO", "HANARO"), ("KIWOOM", "KIWOOM"), ("Vanguard", "VANGUARD"),
              ("iShares", "ISHARES"), ("SPDR", "SPDR"), ("Invesco", "INVESCO"),
              ("Schwab", "SCHWAB"), ("JPMorgan", "JPMORGAN")]


def _logo_uri(key):
    for ext, mt in ((".png", "image/png"), (".svg", "image/svg+xml")):
        f = LOGODIR / (key + ext)
        if f.exists():
            import base64
            return f"data:{mt};base64," + base64.b64encode(f.read_bytes()).decode()
    return ""


def logo_for(row, market):
    if market == "ETF":
        up = row["label"].upper()
        for pre, k in ETF_PREFIX:
            if up.startswith(pre.upper()) or (" " + pre.upper()) in up:
                return _logo_uri(k)
        return ""
    return _logo_uri(row["ticker"].split(".")[0])   # 미국=티커 · 한국=6자리코드


def money(v, sym="$"):
    if sym != "$":
        return f"{sym}{v:,.0f}"
    return f"${v:,.0f}" if v >= 100 else f"${v:,.2f}"


def name_of(label):
    return label.split(" / ")[0].strip()


def dur(lines):
    return 2500 + sum(1400 for x in lines if str(x).strip())


def base_scene(tpl, lines, data, bgid=None):
    return {"tpl": tpl, "dur": dur(lines), "cam": {"s": 1, "x": 50, "y": 50},
            "bgid": bgid, "subLines": lines, "data": data}


def draw_chart(row):
    pts = row.get("pts") or []
    if len(pts) < 2:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    hi, cur = row["high_price"], row["current_price"]
    lo = min(min(ys), cur, hi * 0.5)       # -50% 선까지 항상 보이게
    top = max(max(ys), hi)
    span = (top - lo) or (top * 0.1)
    y0, y1 = max(0, lo - span * 0.13), top + span * 0.22   # 하단 13%=자막 여백 · 상단 22%=테이블 띠
    ly = (row.get("listed", "") or "")[:4]
    sym = cur_sym(row["ticker"])
    pk_i = max(range(len(pts)), key=lambda i: pts[i][1])   # 그래프상 전고점 위치
    crash_x = row.get("crash_x") or []
    chart = {
        "kind": "line", "cur": sym,
        "x": [xs[0], xs[-1]], "y": [y0, y1],
        "yticks": [],   # 전고점 가격은 아래 peak 마커에만 표기(중복 제거)
        "xticks": [[xs[0], ly], [xs[-1], "현재"]],
        "series": [{"pts": pts, "c": LINE, "w": 3, "name": row["ticker"]}],
        "hline": {"v": hi, "c": BLUE, "label": ""},   # 전고점 수평선(파랑) · 라벨은 peak 마커에
        "hlines": [{"v": hi * 0.8, "c": "#e0902f", "label": "−20%"},
                   {"v": hi * 0.5, "c": RED, "label": "−50%"}],
        "peak": {"x": pts[pk_i][0], "y": pts[pk_i][1], "c": BLUE, "label": f"전고점 {sym}{hi:,.0f}"},
        "dot": {"x": xs[-1], "y": cur, "c": RED, "label": "현재"},
        "noLegend": True,
    }
    if crash_x:   # 과거 −30% 하락 시점 = 빨간 별표 + 세로 점선 (PG '폭락 신호' 방식)
        chart["stars"] = {"series": 0, "years": crash_x, "label": "−30% 하락",
                          "labelAt": [crash_x[0], hi * 0.58]}
    return chart


def week_label():
    from datetime import date as _d
    try:
        y, w, _ = _d.fromisoformat(WEEK.get("date", "")).isocalendar()
        return f"{y}년 {w}주차"
    except Exception:
        return ""


def notice_scene():
    return base_scene("notice", [], {
        "title": "유의사항",
        "lines": [
            "이 영상은 투자 참고용이며 특정 종목 매수·매도 권유가 아닙니다.",
            "모든 수치는 야후 파이낸스 종가 기준 · 직전 전고점 대비 낙폭입니다.",
            "투자의 책임은 투자자 본인에게 있습니다.",
        ]})


def sectint_scene(part, head, lines, tone="d"):
    return base_scene("sectint", lines, {"tone": tone, "part": part, "head": head})


def sectnum_scene(num, label, lines, tone="g"):
    return base_scene("sectnum", lines, {"tone": tone, "num": str(num), "label": label})


def drawcard_scene(row, rank, market):
    dd = abs(row["drawdown_pct"])
    nm = name_of(row["label"])
    tail = (" " + row["reason"]) if row.get("reason") else ""
    lines = [f"{rank}위, {nm}.", f"전고점 대비 {dd:.1f}% 빠졌습니다.{tail}"]
    return base_scene("drawcard", lines, {
        "rank": f"#{rank}", "cat": f"{CAT[market]} · {row['ticker']}",
        "title": nm, "dd": f"▼{dd:.1f}%", "peakdate": row.get("high_date", ""),
        "chart": draw_chart(row), "counts": row.get("counts"),
        "logo": logo_for(row, market), "issuerlogo": market == "ETF",
        "reason": row.get("reason", ""),
    })


# ── 씬 조립 ──────────────────────────────────────────────────────────────────────
scenes = [
    notice_scene(),
    sectint_scene(week_label(), "이번 주, 전고점에서|가장 많이 무너진 종목은?",
                  ["이번 주 전고점 대비 가장 많이 빠진 종목을 시장별로 모았습니다."]),
]
sec_no = 0
for market in MARKET_ORDER:
    if market not in WEEK["markets"]:
        continue
    sec_no += 1
    part, head = SEC[market]
    rows = WEEK["markets"][market]
    scenes.append(sectnum_scene(sec_no, head, [f"{head}, 5위부터 봅니다."]))   # 큰 숫자 + 라벨
    for row, rank in zip(reversed(rows), range(len(rows), 0, -1)):
        scenes.append(drawcard_scene(row, rank, market))

t3 = WEEK["top3"]
t3txt = "|".join(f"{i+1}. {name_of(r['label'])} {abs(r['drawdown_pct']):.0f}%" for i, r in enumerate(t3))
scenes += [
    sectint_scene("종합", "이번 주 통합 낙폭 TOP3|" + t3txt,
                  ["시장을 통틀어 가장 많이 빠진 세 종목입니다."], tone="g"),
    sectint_scene("", "다음 주에 또 만나요|구독하고 기다리기",
                  ["매주 낙폭 랭킹을 올립니다. 구독하고 다음 주도 받아보세요."]),
]

# ── 라벨 위치 전파: deck_ov.json 의 peak/now/counts 오프셋을 전 drawcard 씬에 적용 ──
#    한 슬라이드에서 전고점/현재/테이블을 드래그→💾저장 하면 전 슬라이드에 같은 위치로 전파됨.
_ovf = ROOT / "spec" / "deck_ov.json"
_saved = {}
if _ovf.exists():
    try:
        _saved = json.loads(_ovf.read_text(encoding="utf-8"))
    except Exception:
        _saved = {}
_tmpl = {}
for _k, _v in _saved.items():
    if ":" in _k:
        _ek = _k.split(":", 1)[1]
        if _ek in ("peak", "now", "counts") and _ek not in _tmpl:
            _tmpl[_ek] = _v          # 첫 발견 오프셋을 템플릿으로(= 사용자가 조정한 위치)
OV_OUT = {}
for _i, _sc in enumerate(scenes):
    if _sc["tpl"] == "drawcard":
        for _ek, _off in _tmpl.items():
            OV_OUT[f"{_i}:{_ek}"] = _saved.get(f"{_i}:{_ek}", _off)   # 씬별 개별조정 우선, 없으면 템플릿

# ── HTML 주입: KEY 교체 + 코카콜라 패치 IIFE 블록 제거 + 조건부 SCENES 주입 ──
html = (DECK / "stock_alert_final.html").read_text(encoding="utf-8")
html = html.replace("const KEY = 'tplCatalog_cocacola_v4g';", "const KEY = 'tplCatalog_stock_alert_v29';")
bs = html.index("/* FIRE 세트")
p = html.index("var VER='src1';", bs)
be = html.index("})();", p) + len("})();")
override = ("/* ══ STOCK_ALERT 낙폭 카운트다운 주입 (localStorage 저장본 있으면 유지) ══ */\n"
            "if(!localStorage.getItem(KEY)){\n"
            "  SCENES = " + json.dumps(scenes, ensure_ascii=False) + ";\n"
            "  OV = " + json.dumps(OV_OUT, ensure_ascii=False) + "; CP = {}; THEME='paper'; PAPER='photo';\n"
            "}\n")
html = html[:bs] + override + html[be:]

# 배경영상 data URI embed (있으면)
bgdir = DECK / "bg"
for mp4 in sorted(bgdir.glob("*.mp4")):
    ref = f"bg/{mp4.name}"
    if ref in html:
        html = html.replace(ref, "data:video/mp4;base64," + base64.b64encode(mp4.read_bytes()).decode())

(DECK / "stock_alert_v1.html").write_text(html, encoding="utf-8")
(DECK / "stock_alert_deck.json").write_text(json.dumps({"scenes": scenes}, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"씬 {len(scenes)}개 · 총 {sum(s['dur'] for s in scenes)/1000:.0f}s")
print("drawcard:", sum(1 for s in scenes if s['tpl'] == 'drawcard'), "개")
print(f"→ deck/stock_alert_v1.html ({len(html)//1024}KB) · deck/stock_alert_deck.json")
