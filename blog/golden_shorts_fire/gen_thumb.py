#!/usr/bin/env python3
"""gen_thumb.py — 골든 썸네일(신용카드 스타일) 생성기.

검정 배경 + [신용카드](70% 축소) + 헤드라인, 중앙 그룹 배치.
카드 = [브랜드로고+티커] · "N년 결과" 칩 · 최대원금 결과 미니그래프. (IC칩 없음)
헤드라인 = "<종목> 으로 은퇴 / 얼마 있어야 할까?" (종목명만 마젠타, 나머지 흰색).
데이터 = assets/<stock>_fires.json 최대 원금 라인. 출력 = assets/<stock>_thumb.png (build 소비).

사용:  SHORTS_STOCK=SPY python3 gen_thumb.py
종목 추가 = CFG에 lead/tail(+brand png) 한 줄. 브랜드 로고 없으면 티커 텍스트로 대체.
규격: SCALE=0.70 · TEXT_CY=1138(QQQ 문구 위치) · GAP=44 (카드-문구 간격).
"""
import os, json, base64
from PIL import Image
from playwright.sync_api import sync_playwright
import golden_shorts_fire as G

HERE  = os.path.dirname(os.path.abspath(__file__))
STOCK = os.environ.get("SHORTS_STOCK", "PG")
F     = G.FIRES
KRW   = bool(F[0]["payload"].get("krw"))
_mx   = F[-1]
LINES = _mx["payload"]["lines"]
X0    = int(_mx["payload"].get("x0", 2000))
YEARS = int(max(p[0] for l in LINES for p in l["pts"]) - X0)   # floor(경과 연수)
SCALE, TEXT_CY, GAP = 0.70, 1138, 44        # 카드 축소율 · 문구 세로중심(QQQ 기준 위치) · 카드-문구 간격
_PAD = 66.0 / 720.0                          # 카드 캡처의 그림자 여백 비율

def _b64(f):
    return "data:image/png;base64," + base64.b64encode(open(os.path.join(HERE, "assets", f), "rb").read()).decode()

# ── 종목별 카드 헤더/헤드라인 (brand=카드용 로고 png · 없으면 티커 텍스트) ──
CFG = {
    "SPY":  {"brand": "spy_logo.png", "lead": "S&P500",   "tail": "으로 은퇴"},   # spy_logo=State Street+SPY 합본
    "QQQ":  {"brand": "qqq_logo.png", "ticker": "QQQ", "lead": "나스닥100", "tail": "으로 은퇴"},
    "PG":   {"ticker": "PG",       "lead": "P&G",      "tail": "로 은퇴"},
    "MO":   {"ticker": "MO",       "lead": "알트리아",  "tail": "로 은퇴"},
    "SCHD": {"ticker": "SCHD",     "lead": "미국배당",  "tail": "으로 은퇴"},
    "AAPL": {"ticker": "AAPL",     "lead": "애플",      "tail": "로 은퇴"},
    "QYLD": {"ticker": "QYLD",     "lead": "월배당 QYLD", "tail": "로 은퇴"},
    "SEC":  {"ticker": "삼성전자",  "lead": "삼성전자",  "tail": "로 은퇴"},
    "KTNG": {"ticker": "KT&amp;G", "lead": "KT&amp;G",  "tail": "로 은퇴"},
}
cfg = CFG.get(STOCK, {"ticker": STOCK, "lead": STOCK, "tail": "로 은퇴"})

def fmtc(v):
    if KRW:
        return ("%.1f억" % (v / 1e8)).replace(".0", "") if v >= 1e8 else "%d만" % round(v / 1e4)
    return ("$%.1fM" % (v / 1e6)).replace(".0", "") if v >= 1e6 else "$" + format(int(round(v / 1000) * 1000), ",")

# ── 미니그래프 SVG (최대원금 3선) ──
COL = ["#2b6cb0", "#d98f2b", "#c2255c"]
xs = [p[0] for l in LINES for p in l["pts"]]; ys = [p[1] for l in LINES for p in l["pts"]]
x0v, x1v = min(xs), max(xs); y1v = max(ys) * 1.08
W, Hc, ML, MR, MT, MB = 880, 470, 66, 196, 18, 74
def X(x): return ML + (W - ML - MR) * (x - x0v) / (x1v - x0v)
def Y(y): return MT + (Hc - MT - MB) * (1 - y / y1v)
paths = ""; ends = []
for i, l in enumerate(LINES):
    pts = l["pts"]; d = "M" + " L".join("%.1f,%.1f" % (X(p[0]), Y(p[1])) for p in pts)
    paths += '<path d="%s" fill="none" stroke="%s" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>' % (d, COL[i])
    ex, ey = X(pts[-1][0]), Y(pts[-1][1])
    lab = fmtc(pts[-1][1]) if l.get("surv") else ""   # 파산선($0)은 라벨 생략(x축 연도와 겹침 방지)
    ends.append([ey, ex, COL[i], lab]); paths += '<circle cx="%.1f" cy="%.1f" r="7" fill="%s"/>' % (ex, ey, COL[i])
ends.sort(); _py = -99
for ey, ex, c, lab in ends:
    if not lab:
        continue
    yy = ey if ey - _py >= 34 else _py + 34; _py = yy
    paths += '<text x="%.1f" y="%.1f" font-size="33" font-weight="800" fill="%s">%s</text>' % (ex + 13, yy + 11, c, lab)
xax = '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#d8d3ca" stroke-width="2"/>' % (ML, Y(0), W - MR, Y(0))
for yr in range(X0, int(x1v) + 1, 10):
    xax += '<text x="%.1f" y="%.1f" font-size="25" fill="#9a938c" text-anchor="middle" font-weight="600">%d</text>' % (X(yr), Hc - MB + 38, yr)
hl = '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#b8b1a8" stroke-width="2" stroke-dasharray="6 5"/>' % (ML, Y(_mx["amt"]), W - MR, Y(_mx["amt"]))
GRAPH = '<svg viewBox="0 0 %d %d" style="display:block;width:100%%;height:auto" font-family="Pretendard,sans-serif">%s%s%s</svg>' % (W, Hc, hl, xax, paths)

# ── 카드 헤더 ──
if cfg.get("brand"):
    HDR = '<img class="brand" src="%s">' % _b64(cfg["brand"])
    if cfg.get("ticker"):
        HDR += '<span class="tk">%s</span>' % cfg["ticker"]
else:
    HDR = '<span class="tk big">%s</span>' % cfg.get("ticker", STOCK)

CARD_HTML = """<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:'Pretendard';font-weight:100 900;src:url('{FONT}') format('woff2')}}
*{{margin:0;box-sizing:border-box}}html,body{{background:transparent}}
.pad{{padding:66px}}
.card{{position:relative;background:#fff;border:1px solid rgba(20,25,35,.06);border-radius:40px;padding:26px 30px 18px;
  box-shadow:0 2px 4px rgba(20,25,35,.05),0 26px 60px rgba(0,0,0,.55)}}
.hdr{{display:flex;align-items:center;gap:14px;margin:2px 4px 6px}}
.hdr .brand{{height:58px;width:auto}}
.hdr .tk{{font:900 44px Pretendard;color:#111;letter-spacing:-.01em}}
.hdr .tk.big{{font-size:52px;color:#1b3660}}
.hdr .res{{margin-left:auto;font:800 24px Pretendard;color:#8a857c;letter-spacing:.02em}}
</style><div class="pad"><div class="card">
<div class="hdr">{HDR}<span class="res">{YEARS}년 결과</span></div>{GRAPH}
</div></div>""".format(FONT=G.FONTSRC, HDR=HDR, YEARS=YEARS, GRAPH=GRAPH)

TEXT_HTML = """<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:'Pretendard';font-weight:100 900;src:url('{FONT}') format('woff2')}}
html,body{{margin:0;background:transparent}}
.t{{text-align:center;padding:10px 30px}}
.a{{color:#fff;font:900 62px Pretendard;letter-spacing:-.02em;line-height:1}}.a .m{{color:#d12e77}}
.b{{color:#abe0d3;font:900 62px Pretendard;letter-spacing:-.02em;line-height:1;margin-top:24px}}  /* QQQ 크기(62px)·2줄=옅은 청록 */
</style><div class="t"><div class="a"><span class="m">{LEAD}</span> {TAIL}</div><div class="b">얼마 있어야 할까?</div></div>""".format(
    FONT=G.FONTSRC, LEAD=cfg["lead"], TAIL=cfg["tail"])

if __name__ == "__main__":
    ch_html = os.path.join(HERE, "_thumb_card_%s.html" % STOCK)
    tx_html = os.path.join(HERE, "_thumb_text_%s.html" % STOCK)
    ch_png  = os.path.join(HERE, "_thumb_card_%s.png" % STOCK)
    tx_png  = os.path.join(HERE, "_thumb_text_%s.png" % STOCK)
    open(ch_html, "w", encoding="utf-8").write(CARD_HTML)
    open(tx_html, "w", encoding="utf-8").write(TEXT_HTML)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1012, "height": 760}, device_scale_factor=2)
        pg.goto("file://" + ch_html); pg.wait_for_function("()=>document.fonts.check('900 40px Pretendard')", timeout=8000)
        pg.wait_for_timeout(300); pg.query_selector(".pad").screenshot(path=ch_png, omit_background=True)
        pg2 = b.new_page(viewport={"width": 1080, "height": 420}, device_scale_factor=2)
        pg2.goto("file://" + tx_html); pg2.wait_for_function("()=>document.fonts.check('900 40px Pretendard')", timeout=8000)
        pg2.wait_for_timeout(300); pg2.query_selector(".t").screenshot(path=tx_png, omit_background=True)
        b.close()

    Wpx, Hpx = 1080, 1920
    card = Image.open(ch_png).convert("RGBA"); txt = Image.open(tx_png).convert("RGBA")
    tw, th = txt.width // 2, txt.height // 2; txt_r = txt.resize((tw, th), Image.LANCZOS)
    cw = int(910 * SCALE); chh = int(card.height * cw / card.width); card_r = card.resize((cw, chh), Image.LANCZOS)
    ty = int(TEXT_CY - th / 2)                      # 문구 세로중심 = QQQ 문구 위치(1138)에 일치
    cy = int(ty - GAP - chh * (1 - _PAD))           # 카드는 문구 바로 위(QQQ 로고 위치에 최대한 근접)
    canvas = Image.new("RGBA", (Wpx, Hpx), (11, 12, 15, 255))
    canvas.alpha_composite(card_r, ((Wpx - cw) // 2, cy)); canvas.alpha_composite(txt_r, ((Wpx - tw) // 2, ty))
    out = os.path.join(HERE, "assets", "%s_thumb.png" % {"PG": "pg", "QQQ": "qqq", "KTNG": "ktng", "SCHD": "schd",
                       "SPY": "spy", "MO": "mo", "SEC": "sec", "AAPL": "aapl"}.get(STOCK, STOCK.lower()))
    canvas.convert("RGB").save(out)
    print("wrote %s (%s · %d년 · 최대원금 %s · 카드%d%%)" % (out, STOCK, YEARS, _mx["amt"], int(SCALE * 100)))
