# -*- coding: utf-8 -*-
"""stock_alert 상승 덱 조립 — 이번 주 52주 신고가 돌파 + 5년 수익률.
   data/rise_weekN.json → 씬 JSON → stock_alert_final.html 주입 → stock_alert_rise_v1.html.

   씬: notice · 훅 · [섹션 + risecard×N]×4(ETF/미국/한국/유럽) · 신고가 수익률 TOP3 · 마무리
   risecard 차트 = engChart line(초록) + 신고가 마커(초록) + 5년 전 기준점.
   사용: python3 deck/build_rise_deck.py
"""
import base64
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECK = ROOT / "deck"
DATA = ROOT / "data"

rises = sorted(DATA.glob("rise_week*.json"))
if not rises:
    raise SystemExit("data/rise_weekN.json 없음 — 먼저 상승 스캔 실행")
WEEK = json.loads(rises[-1].read_text(encoding="utf-8"))

GREEN = "#2f9e57"         # 상승 선/신고가 마커
MUTE = "#8a8f8c"          # 5년 전 기준점
INK = "var(--ink-soft)"
CAT = {"ETF": "📊 ETF", "미국": "🇺🇸 미국주식", "한국": "🇰🇷 한국주식", "유럽": "🇪🇺 유럽주식"}
SEC = {"ETF": ("①", "ETF 신고가 TOP"), "미국": ("②", "미국 주식 신고가 TOP"),
       "한국": ("③", "한국 주식 신고가 TOP"), "유럽": ("④", "유럽 주식 신고가 TOP")}
MARKET_ORDER = ["ETF", "미국", "한국", "유럽"]

# ── 통화 심볼 ──
TICKERS_DIR = ROOT.parent.parent / "global_cup_suite" / "data"
CUR_SYM = {"USD": "$", "KRW": "₩", "EUR": "€", "GBP": "£", "CHF": "CHF ", "JPY": "¥",
           "SEK": "kr ", "DKK": "kr ", "NOK": "kr "}
_ccy = {}
for _f in TICKERS_DIR.glob("tickers_*.csv"):
    for _r in csv.DictReader(open(_f, encoding="utf-8")):
        _ccy[_r["ticker"].strip()] = _r["currency"].strip()


def cur_sym(ticker):
    return CUR_SYM.get(_ccy.get(ticker, "USD"), "$")

# ── 로고 (build_deck.py와 동일 규칙) ──
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


def fmt_size(v, sym):
    if v is None:
        return ""
    v = float(v)
    if sym == "₩":
        if v >= 1e12:
            return f"₩{v/1e12:,.1f}조"
        return f"₩{v/1e8:,.0f}억"
    if v >= 1e12:
        return f"{sym}{v/1e12:,.2f}T"
    if v >= 1e9:
        return f"{sym}{v/1e9:,.1f}B"
    if v >= 1e6:
        return f"{sym}{v/1e6:,.0f}M"
    return f"{sym}{v:,.0f}"


def dur(lines):
    return 5000 + sum(2800 for x in lines if str(x).strip())


def base_scene(tpl, lines, data, bgid=None):
    return {"tpl": tpl, "dur": dur(lines), "cam": {"s": 1, "x": 50, "y": 50},
            "bgid": bgid, "subLines": lines, "data": data}


def draw_chart_rise(row):
    pts = row.get("pts") or []
    if len(pts) < 2:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    hidx = min(row.get("highidx", len(pts) - 1), len(pts) - 1)
    bidx = min(row.get("baseidx", 0), len(pts) - 1)
    hi_pt, base_pt = pts[hidx], pts[bidx]
    lo, top = min(ys), max(ys)
    span = (top - lo) or (top * 0.1)
    y0, y1 = max(0, lo - span * 0.12), top + span * 0.22
    sym = cur_sym(row["ticker"])
    ly = (row.get("listed", "") or "")[:4]
    return {
        "kind": "line", "cur": sym,
        "x": [xs[0], xs[-1]], "y": [y0, y1],
        "yticks": [],
        "xticks": [[xs[0], ly], [xs[-1], "현재"]],
        "series": [{"pts": pts, "c": GREEN, "w": 3, "name": row["ticker"]}],
        "peak": {"x": hi_pt[0], "y": hi_pt[1], "c": GREEN,
                 "label": f"신고가 {sym}{hi_pt[1]:,.0f}"},
        "dot": {"x": base_pt[0], "y": base_pt[1], "c": MUTE, "label": "5년 전"},
        "noLegend": True,
    }


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
            "모든 수치는 야후 파이낸스 종가 기준 · 52주 신고가·5년 수익률입니다.",
            "투자의 책임은 투자자 본인에게 있습니다.",
        ]})


def sectint_scene(part, head, lines, tone="d"):
    return base_scene("sectint", lines, {"tone": tone, "part": part, "head": head})


def sectnum_scene(num, label, lines, tone="g"):
    return base_scene("sectnum", lines, {"tone": tone, "num": str(num), "label": label})


def risecard_scene(row, rank, market):
    nm = name_of(row["label"])
    sym = cur_sym(row["ticker"])
    r = float(row["return_pct"])
    ret = f"▲+{r:.0f}%" if r >= 0 else f"▼{r:.0f}%"
    tail = " 다만 5년으론 아직 마이너스입니다." if r < 0 else ""
    lines = [f"{rank}위, {nm}.", f"이번 주 52주 신고가를 새로 썼습니다.{tail}"]
    sc = base_scene("risecard", lines, {
        "rank": f"#{rank}", "cat": f"{CAT[market]} · {row['ticker']}",
        "title": nm, "highdate": (row.get("high_date", "") or "")[:10],
        "size": fmt_size(row.get("size"), sym),
        "ret": ret, "retsign": "up" if r >= 0 else "down", "period": "5년",
        "chart": draw_chart_rise(row),
        "logo": logo_for(row, market), "issuerlogo": market == "ETF",
    })
    sc["subHold"] = 5500   # 카드 균일 시간(무음 쇼츠) — 자막길이 편차로 인한 불균등 방지
    return sc


# ── 씬 조립 ──
scenes = [
    notice_scene(),
    sectint_scene(week_label(), "이번 주, 52주 신고가를|새로 쓴 종목은?",
                  ["이번 주 52주 신고가를 돌파한 종목을 시장별로 모았습니다."]),
]
_flt = sys.argv[1] if len(sys.argv) > 1 else None      # 시장 필터(예: 한국) — 단일시장 쇼츠용
BUILD = [_flt] if _flt else MARKET_ORDER
sec_no = 0
for market in BUILD:
    rows = WEEK["markets"].get(market) or []
    if not rows:
        continue
    sec_no += 1
    part, head = SEC[market]
    scenes.append(sectnum_scene(sec_no, head, [f"{head}, 아래부터 봅니다."]))
    for row, rank in zip(reversed(rows), range(len(rows), 0, -1)):
        scenes.append(risecard_scene(row, rank, market))

# 통합 신고가 수익률 TOP3 (5년 수익률 기준)
allrows = [r for m in BUILD for r in (WEEK["markets"].get(m) or [])]
t3 = sorted(allrows, key=lambda r: -float(r["return_pct"]))[:3]
t3txt = "|".join(f"{i+1}. {name_of(r['label'])} +{float(r['return_pct']):.0f}%"
                 for i, r in enumerate(t3))
scenes += [
    sectint_scene("종합", "신고가 종목 중 5년 수익률 TOP3|" + t3txt,
                  ["이번 주 신고가 종목 중 5년 성적이 가장 좋은 셋입니다."], tone="g"),
    sectint_scene("", "다음 주에 또 만나요|구독하고 기다리기",
                  ["매주 신고가·낙폭 랭킹을 올립니다. 구독하고 다음 주도 받아보세요."]),
]

# ── HTML 주입 ──
html = (DECK / "stock_alert_final.html").read_text(encoding="utf-8")
html = html.replace("const KEY = 'tplCatalog_cocacola_v4g';",
                    "const KEY = 'tplCatalog_stock_alert_rise_v1';")
bs = html.index("/* FIRE 세트")
p = html.index("var VER='src1';", bs)
be = html.index("})();", p) + len("})();")
override = ("/* ══ STOCK_ALERT 상승(신고가) 카운트다운 주입 ══ */\n"
            "if(!localStorage.getItem(KEY)){\n"
            "  SCENES = " + json.dumps(scenes, ensure_ascii=False) + ";\n"
            "  OV = {}; CP = {}; THEME='paper'; PAPER='photo';\n"
            "}\n")
html = html[:bs] + override + html[be:]

bgdir = DECK / "bg"
for mp4 in sorted(bgdir.glob("*.mp4")):
    ref = f"bg/{mp4.name}"
    if ref in html:
        html = html.replace(ref, "data:video/mp4;base64," + base64.b64encode(mp4.read_bytes()).decode())

(DECK / "stock_alert_rise_v1.html").write_text(html, encoding="utf-8")
(DECK / "stock_alert_rise_deck.json").write_text(
    json.dumps({"scenes": scenes}, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"씬 {len(scenes)}개 · 총 {sum(s['dur'] for s in scenes)/1000:.0f}s")
print("risecard:", sum(1 for s in scenes if s['tpl'] == 'risecard'), "개")
print(f"→ deck/stock_alert_rise_v1.html ({len(html)//1024}KB)")
