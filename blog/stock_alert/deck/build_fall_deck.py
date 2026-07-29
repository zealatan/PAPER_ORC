# -*- coding: utf-8 -*-
"""stock_alert 낙폭 덱(쇼츠용) — 단일시장·균일타이밍. build_rise_deck.py 의 낙폭판.
   data/weekN.json → 씬 JSON(drawcard) → stock_alert_final.html 주입 → stock_alert_fall_v1.html.

   상승(build_rise_deck)과 동일 구조: 시장필터 + risecard 대신 drawcard + subHold 균일(5500).
   drawcard 차트 = 전고점(파랑)·현재(빨강)·−20/−50 기준선·과거 −30% 폭락 별표.
   ※ 더빙 롱폼용 4시장 덱은 build_deck.py(그대로 유지). 이건 무음 쇼츠 전용.
   사용: python3 deck/build_fall_deck.py <시장>     (미국/한국/ETF/유럽)
"""
import base64
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECK = ROOT / "deck"
DATA = ROOT / "data"

weeks = sorted(DATA.glob("week*.json"))
if not weeks:
    raise SystemExit("data/weekN.json 없음 — 먼저 weekly_scan.py 실행")
WEEK = json.loads(weeks[-1].read_text(encoding="utf-8"))

RED, INK = "var(--red)", "var(--ink-soft)"
BLUE = "#2563eb"          # 전고점 마커/라벨
LINE = "#2b3d40"          # 가격 선
CAT = {"ETF": "📊 ETF", "미국": "🇺🇸 미국주식", "한국": "🇰🇷 한국주식", "유럽": "🇪🇺 유럽주식"}
SEC = {"ETF": ("①", "ETF 낙폭 TOP5"), "미국": ("②", "미국 주식 낙폭 TOP5"),
       "한국": ("③", "한국 주식 낙폭 TOP5"), "유럽": ("④", "유럽 주식 낙폭 TOP5")}
MARKET_ORDER = ["ETF", "미국", "한국", "유럽"]

TICKERS_DIR = ROOT.parent.parent / "global_cup_suite" / "data"
CUR_SYM = {"USD": "$", "KRW": "₩", "EUR": "€", "GBP": "£", "CHF": "CHF ", "JPY": "¥"}
_ccy = {}
for _f in TICKERS_DIR.glob("tickers_*.csv"):
    for _r in csv.DictReader(open(_f, encoding="utf-8")):
        _ccy[_r["ticker"].strip()] = _r["currency"].strip()


def cur_sym(ticker):
    return CUR_SYM.get(_ccy.get(ticker, "USD"), "$")


LOGODIR = DECK / "logos"
ETF_PREFIX = [("KODEX", "KODEX"), ("TIGER", "TIGER"), ("KBSTAR", "KBSTAR"), ("RISE", "RISE"),
              ("SOL", "SOL"), ("ARIRANG", "ARIRANG"), ("PLUS", "PLUS"), ("ACE", "ACE"),
              ("HANARO", "HANARO"), ("KIWOOM", "KIWOOM"), ("Vanguard", "VANGUARD"),
              ("iShares", "ISHARES"), ("SPDR", "SPDR"), ("Invesco", "INVESCO"),
              ("Schwab", "SCHWAB"), ("JPMorgan", "JPMORGAN"), ("Global X", "GLOBALX")]


def _logo_uri(key):
    for ext, mt in ((".png", "image/png"), (".svg", "image/svg+xml")):
        f = LOGODIR / (key + ext)
        if f.exists():
            return f"data:{mt};base64," + base64.b64encode(f.read_bytes()).decode()
    return ""


def logo_for(row, market):
    if market == "ETF":
        up = row["label"].upper()
        for pre, k in ETF_PREFIX:
            if up.startswith(pre.upper()) or (" " + pre.upper()) in up:
                return _logo_uri(k)
        return ""
    return _logo_uri(row["ticker"].split(".")[0])


def name_of(label):
    return label.split(" / ")[0].strip()


def dur(lines):
    return 5000 + sum(2800 for x in lines if str(x).strip())


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
    lo = min(min(ys), cur, hi * 0.5)
    top = max(max(ys), hi)
    span = (top - lo) or (top * 0.1)
    y0, y1 = max(0, lo - span * 0.13), top + span * 0.22
    ly = (row.get("listed", "") or "")[:4]
    sym = cur_sym(row["ticker"])
    pk_i = max(range(len(pts)), key=lambda i: pts[i][1])
    crash_x = row.get("crash_x") or []
    chart = {
        "kind": "line", "cur": sym,
        "x": [xs[0], xs[-1]], "y": [y0, y1], "yticks": [],
        "xticks": [[xs[0], ly], [xs[-1], "현재"]],
        "series": [{"pts": pts, "c": LINE, "w": 3, "name": row["ticker"]}],
        "hline": {"v": hi, "c": BLUE, "label": ""},
        "hlines": [{"v": hi * 0.8, "c": "#e0902f", "label": "−20%"},
                   {"v": hi * 0.5, "c": RED, "label": "−50%"}],
        "peak": {"x": pts[pk_i][0], "y": pts[pk_i][1], "c": BLUE, "label": f"전고점 {sym}{hi:,.0f}"},
        "dot": {"x": xs[-1], "y": cur, "c": RED, "label": "현재"},
        "noLegend": True,
    }
    if crash_x:
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
        "lines": ["이 영상은 투자 참고용이며 특정 종목 매수·매도 권유가 아닙니다.",
                  "모든 수치는 야후 파이낸스 종가 기준 · 직전 전고점 대비 낙폭입니다.",
                  "투자의 책임은 투자자 본인에게 있습니다."]})


def sectint_scene(part, head, lines, tone="d"):
    return base_scene("sectint", lines, {"tone": tone, "part": part, "head": head})


def sectnum_scene(num, label, lines, tone="g"):
    return base_scene("sectnum", lines, {"tone": tone, "num": str(num), "label": label})


def drawcard_scene(row, rank, market):
    dd = abs(row["drawdown_pct"])
    nm = name_of(row["label"])
    lines = [f"{rank}위, {nm}.", f"전고점 대비 {dd:.1f}% 빠졌습니다."]
    sc = base_scene("drawcard", lines, {
        "rank": f"#{rank}", "cat": f"{CAT[market]} · {row['ticker']}",
        "title": nm, "dd": f"▼{dd:.1f}%", "peakdate": row.get("high_date", ""),
        "chart": draw_chart(row), "counts": row.get("counts"),
        "logo": logo_for(row, market), "issuerlogo": market == "ETF",
        "reason": row.get("reason", ""),
    })
    sc["subHold"] = 5500   # 카드 균일 시간(무음 쇼츠) — build_short_fall.sh 의 CARD 와 동기
    return sc


# ── 씬 조립 (단일시장) ──
_flt = sys.argv[1] if len(sys.argv) > 1 else None
BUILD = [_flt] if _flt else MARKET_ORDER
scenes = [notice_scene(),
          sectint_scene(week_label(), "이번 주, 전고점에서|가장 많이 무너진 종목은?",
                        ["이번 주 전고점 대비 가장 많이 빠진 종목을 시장별로 모았습니다."])]
sec_no = 0
for market in BUILD:
    rows = WEEK["markets"].get(market) or []
    if not rows:
        continue
    sec_no += 1
    part, head = SEC[market]
    scenes.append(sectnum_scene(sec_no, head, [f"{head}, 아래부터 봅니다."]))
    for row, rank in zip(reversed(rows), range(len(rows), 0, -1)):
        scenes.append(drawcard_scene(row, rank, market))
scenes.append(sectint_scene("", "다음 주에 또 만나요|구독하고 기다리기",
                            ["매주 낙폭 랭킹을 올립니다. 구독하고 다음 주도 받아보세요."]))

# ── HTML 주입 ──
html = (DECK / "stock_alert_final.html").read_text(encoding="utf-8")
html = html.replace("const KEY = 'tplCatalog_cocacola_v4g';",
                    "const KEY = 'tplCatalog_stock_alert_fall_v1';")
bs = html.index("/* FIRE 세트")
p = html.index("var VER='src1';", bs)
be = html.index("})();", p) + len("})();")
override = ("/* ══ STOCK_ALERT 낙폭 쇼츠(단일시장·균일) 주입 ══ */\n"
            "if(!localStorage.getItem(KEY)){\n"
            "  SCENES = " + json.dumps(scenes, ensure_ascii=False) + ";\n"
            "  OV = {}; CP = {}; THEME='paper'; PAPER='photo';\n}\n")
html = html[:bs] + override + html[be:]
for mp4 in sorted((DECK / "bg").glob("*.mp4")):
    ref = f"bg/{mp4.name}"
    if ref in html:
        html = html.replace(ref, "data:video/mp4;base64," + base64.b64encode(mp4.read_bytes()).decode())

(DECK / "stock_alert_fall_v1.html").write_text(html, encoding="utf-8")
(DECK / "stock_alert_fall_deck.json").write_text(
    json.dumps({"scenes": scenes}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"씬 {len(scenes)}개 · drawcard {sum(1 for s in scenes if s['tpl']=='drawcard')}개 · 시장={BUILD}")
print(f"→ deck/stock_alert_fall_v1.html ({len(html)//1024}KB)")
