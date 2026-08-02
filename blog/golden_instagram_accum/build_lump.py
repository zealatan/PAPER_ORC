#!/usr/bin/env python3
"""번외: 적립 vs 폭락매수 vs 일시금 — 같은 총액을 방법만 다르게 넣은 3선 비교.

accum 데이터(<pref>_accum.json)의 적립식·N%폭락매수 평가선을 재사용하고,
같은 총 투입원금을 시작연도에 한 번에 넣은 **일시금(buy&hold + 배당 재투자)** 선을
fire_engine으로 계산해 얹는다. 정적 PNG + 애니 릴 둘 다 산출.

사용: SHORTS_STOCK=KT [ACCUM_THR=30] python3 build_lump.py
데이터: assets/data/<pref>_accum.json (gen_accum.py 산출) + yfinance 원천가(일시금 계산용).
출력: exports/<pref>_lump_compare.png, exports/<pref>_lump_reel.mp4(+_top100px.mp4)
"""
import sys, os, json, math, subprocess
from datetime import date
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, "..", "..", "global_cup_suite")))
from global_cup.fire_engine import run_fire_backtest

STOCK = os.environ.get("SHORTS_STOCK", "KT").upper()
THR = int(os.environ.get("ACCUM_THR", "30"))
PREFIX = {"QQQ": "qqq", "PG": "pg", "SKH": "skh", "SEC": "sec", "KT": "kt"}.get(STOCK, STOCK.lower())
NAME = {"QQQ": "나스닥 100 (QQQ)", "SKH": "SK하이닉스", "SEC": "삼성전자",
        "PG": "P&G", "KT": "KT"}.get(STOCK, STOCK)
TICKER = {"QQQ": "QQQ", "KTNG": "033780.KS", "SKH": "000660.KS",
          "SEC": "005930.KS", "KT": "030200.KS"}.get(STOCK)

EXPORTS = ROOT / "exports"
DATA_FILE = ROOT / f"assets/data/{PREFIX}_accum.json"
ENTRY = next(e for e in json.loads(DATA_FILE.read_text()) if e["thr"] == THR)
KRW = bool(ENTRY.get("krw"))
TOTAL = ENTRY["invested"]                       # 총 투입원금(세 방법 공통)
MONTHLY = ENTRY["monthly"]
X0 = int(ENTRY["x0"])
TAX = 15.4 if KRW else 15.0
steady_pts = ENTRY["payload"]["lines"][2]["pts"]   # 적립식 평가선
smart_pts = ENTRY["payload"]["lines"][3]["pts"]    # N%폭락매수 평가선
steady_fin = ENTRY["steady"]["final"]
smart_fin = ENTRY["smart"]["final"]

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
# 3선 색: 폭락매수=초록·적립=파랑·일시금=핑크(승/평/패 직관 매핑)
C_SMART, C_STEADY, C_LUMP = "#4ade80", "#60a5fa", "#f472b6"
W, H, FPS = 1080, 1920, 30
HOOK, REVEAL, GSEC = 2.0, 30.0, 40.0
box = (164, 660, 964, 1360)


def font(s, b=False):
    return ImageFont.truetype(BOLD if b else FONT, s)


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * ease(t)


def money(v):
    if KRW:
        return f"{v / 1e8:.1f}억" if v >= 1e8 else f"{int(round(v / 1e4)):,}만"
    return f"${v / 1e6:.1f}M" if v >= 1e6 else f"${v / 1e3:.0f}K"


def clip_points(pts, limit):
    out = []
    for i, p in enumerate(pts):
        if p[0] <= limit:
            out.append(p); continue
        if out:
            pr = pts[i - 1]; sp = p[0] - pr[0]
            if sp > 0:
                r = max(0.0, min(1.0, (limit - pr[0]) / sp))
                out.append([limit, pr[1] + (p[1] - pr[1]) * r])
        break
    return out


def nice_ceil(x):
    ex = 10 ** math.floor(math.log10(x)); f = x / ex
    for n in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if f <= n:
            return int(n * ex)
    return int(10 * ex)


# ── 일시금(buy&hold + 배당 재투자) 선: 총액을 X0 첫날 한 번에 ──
def load_raw():
    if STOCK == "PG":
        sys.path.insert(0, os.path.join(ROOT, "..", "PG", "deck", "tools"))
        import ko_smart_vs_steady as E
        DATA = os.path.join(ROOT, "..", "PG", "data")
        prices, divs = E.load_csv(os.path.join(DATA, "pg_price.csv"), os.path.join(DATA, "pg_div.csv"))
        close = pd.Series({pd.Timestamp(d): c for d, c in prices if d.year >= X0})
        dv = pd.Series({pd.Timestamp(d): v for d, v in divs if d.year >= X0})
        return close.sort_index(), dv.sort_index()
    import yfinance as yf
    t = yf.Ticker(TICKER)
    h = t.history(start=f"{X0}-01-01", end="2026-07-31", auto_adjust=False)
    h.index = h.index.tz_localize(None)
    close = h["Close"].dropna()
    dv = t.dividends; dv.index = dv.index.tz_localize(None); dv = dv[dv.index >= close.index[0]]
    return close, dv


def to_year(d):
    y0 = date(d.year, 1, 1); y1 = date(d.year + 1, 1, 1)
    return d.year + (d - y0).days / (y1 - y0).days


close, dv = load_raw()
_r = run_fire_backtest(close, dv, TOTAL, annual_withdrawal=0, strategy="fixed_real",
                       reinvest_dividends=True, reinvest_surplus=True, tax_rate_pct=TAX,
                       start_date=date(X0, 1, 1))
_tl = _r.timeline_df.copy(); _tl["Date"] = pd.to_datetime(_tl["Date"])
lump_pts = [[to_year(x["Date"].date()), round(x["Portfolio Value"])] for _, x in _tl.iterrows()]
lump_fin = round(_r.summary["Final Value"])

END_X = max(steady_pts[-1][0], smart_pts[-1][0], lump_pts[-1][0])
SERIES = [("smart", smart_pts, C_SMART, smart_fin, f"{THR}% 하락 시 매수"),
          ("steady", steady_pts, C_STEADY, steady_fin, f"매달 {money(MONTHLY) if not KRW else str(int(MONTHLY // 1e4)) + '만원'} 적립"),
          ("lump", lump_pts, C_LUMP, lump_fin, f"{X0}년 일시금 투자")]
left, top, right, bottom = box


def _ym(fy):
    y = int(fy); return f"{y}.{min(12, int((fy - y) * 12) + 1):02d}"
PERIOD = f"{_ym(X0 + 0.02)}~{_ym(END_X)}"


def dashed(d, xy, fill, w, on=14, off=10):
    rem, dr = on, True
    for (x0, y0), (x1, y1) in zip(xy, xy[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg == 0:
            continue
        pos = 0.0
        while pos < seg:
            st = min(rem, seg - pos); a, b = pos / seg, (pos + st) / seg
            if dr:
                d.line((x0 + (x1 - x0) * a, y0 + (y1 - y0) * a,
                        x0 + (x1 - x0) * b, y0 + (y1 - y0) * b), fill=fill, width=w)
            pos += st; rem -= st
            if rem <= 1e-6:
                dr = not dr; rem = on if dr else off


def render(t):
    im = Image.new("RGB", (W, H), "#000000"); d = ImageDraw.Draw(im)
    cx = W // 2
    l1, l2 = "적립 vs 폭락매수 vs 일시금", f"{NAME} · 같은 돈, 넣는 방법만 다르게"
    sz = 70
    while sz > 40 and max(font(sz, True).getlength(l1), font(sz, True).getlength(l2)) > 1000:
        sz -= 2
    tf = font(sz, True); asc, desc = tf.getmetrics(); lh = asc + desc
    d.multiline_text((cx, 689 - 150 + 18 - (2 * lh + 5)), f"{l1}\n{l2}", fill="#f5f5f5",
                     font=tf, spacing=5, anchor="ma", align="center")

    if t < HOOK:
        clip_end = END_X; prog = 1.0
    else:
        prog = ease((t - HOOK) / REVEAL); clip_end = lerp(X0, END_X, prog)
    ap = prog if t >= HOOK else 1.0

    vis = TOTAL
    for _, pts, _, _, _ in SERIES:
        vv = [v for _, v in clip_points(pts, clip_end)]
        if vv:
            vis = max(vis, *vv)
    y_top = nice_ceil(vis * 1.08)

    LINE, EDGE, TXT = "#242424", "#3a3a3a", "#b3b3b3"
    ar = lerp(left, right, ap)
    for i in range(3):
        val = y_top * i / 2; y = bottom - (bottom - top) * i / 2
        d.line((left, y, ar, y), fill=LINE, width=2)
        d.text((left - 18, y), (money(val) if val > 0 else "0"), anchor="rm", fill=TXT, font=font(31))
    xids = (0,) if ap < .12 else ((0, 4) if ap < .28 else range(5))
    for i in xids:
        yr = X0 + (clip_end - X0) * i / 4; x = left + (right - left) * ap * i / 4
        d.line((x, top, x, bottom), fill=LINE, width=2)
        d.text((x, bottom + 30), f"{yr:.0f}", anchor="ma", fill=TXT, font=font(30))
    d.line((left, bottom, ar, bottom), fill=EDGE, width=2)
    d.line((left, bottom, left, top), fill=EDGE, width=2)
    d.text((left, top - 16), PERIOD, anchor="ls", fill="#8a8a8a", font=font(32))

    def to_xy(pts):
        return [(left + (yr - X0) / max(clip_end - X0, 1e-4) * (right - left) * ap,
                 max(top, bottom - v / y_top * (bottom - top))) for yr, v in pts]

    # 투입원금 손익분기선(점선) + "투입원금/금액" 2줄 라벨
    if y_top >= TOTAL:
        by = bottom - TOTAL / y_top * (bottom - top)
        dashed(d, [(left, by), (ar, by)], "#666666", 3)
        d.multiline_text((left - 18, by - 6), f"투입원금\n{money(TOTAL)}", anchor="rd",
                         align="right", spacing=2, fill="#9a9a9a", font=font(23, True))

    live = []
    for key, pts, col, fin, lab in SERIES:
        cp = clip_points(pts, clip_end)
        if len(cp) < 2:
            continue
        xy = to_xy(cp); d.line(xy, fill=col, width=8, joint="curve")
        ex, ey = xy[-1]
        d.ellipse((ex - 11, ey - 11, ex + 11, ey + 11), outline=col, width=5, fill="#000000")
        final = clip_end >= pts[-1][0] - .05
        live.append((lab, col, money(fin) if final else money(cp[-1][1])))
    lf, vf = font(34), font(46, True)
    for i, (lab, col, val) in enumerate(live):
        yy = bottom + 132 + i * 70
        d.rounded_rectangle((190, yy - 7, 230, yy + 7), 4, fill=col)
        d.text((252, yy), lab, anchor="lm", fill="#dddddd", font=lf)
        d.text((938, yy), val, anchor="rm", fill=col, font=vf)

    tax = "15.4%" if KRW else "15%"
    d.text((72, 1712), f"{X0}년부터 · 배당 재투자 · 세금 {tax} · 총 투입액 동일({money(TOTAL)})",
           fill="#666666", font=font(25))
    d.text((984, 1710), "번외", anchor="ra", fill="#777777", font=font(28))
    return im


def main():
    png = EXPORTS / f"{PREFIX}_lump_compare.png"
    render(1.0).save(png)   # 정적 3선 비교(완성 프레임)
    print("적립", money(steady_fin), "폭락", money(smart_fin), "일시금", money(lump_fin))
    print("PNG →", png)

    base = EXPORTS / f"{PREFIX}_lump_reel.mp4"
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "slow",
           "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(base)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fr in range(round(GSEC * FPS)):
        mv = memoryview(render(fr / FPS).tobytes())
        while mv:
            mv = mv[p.stdin.write(mv):]
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("ffmpeg failed")
    framed = EXPORTS / f"{PREFIX}_lump_reel_top100px.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(base),
                    "-vf", "scale=960:1820:flags=lanczos,pad=1080:1920:60:50:black",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", str(framed)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("reel →", framed)


if __name__ == "__main__":
    main()
