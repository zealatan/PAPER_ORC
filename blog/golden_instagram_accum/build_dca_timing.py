#!/usr/bin/env python3
"""번외: 적립 시작 시점 비교 — 폭락장부터 적립 vs 그 뒤부터 적립.

같은 금액을 매달 적립하되 '시작 연도'만 다르게(예: TQQQ 2022 폭락장 vs 2023).
평가액 2선(solid) + 각 누적원금 점선(dashed). 회복 자산은 폭락장에 담을수록 유리.
2페이지 요약표(투입·평가·배수·XIRR).

사용: DCA_TICKER=TQQQ python3 build_dca_timing.py
출력: exports/<pref>_dcatiming.png · <pref>_dcatiming_reel(_top100px).mp4
"""
import os, math, subprocess, sys
from datetime import date
from pathlib import Path
import pandas as pd, yfinance as yf
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent; EXPORTS = ROOT / "exports"
sys.path.insert(0, os.path.join(ROOT, "..", "PG", "deck", "tools"))
import ko_smart_vs_steady as E   # xirr

TICKER = os.environ.get("DCA_TICKER", "TQQQ").upper()
NAME = TICKER   # 타이틀은 티커만
Y1, Y2 = int(os.environ.get("DCA_Y1", "2022")), int(os.environ.get("DCA_Y2", "2023"))
MO = float(os.environ.get("DCA_MO", "1000"))
PREFIX = TICKER.lower()
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
def font(s, b=False): return ImageFont.truetype(BOLD if b else FONT, s)
def ease(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * ease(t)
def dol(v): return f"${v:,.0f}"
def usd(v): return f"${v/1e6:.2f}M" if v >= 1e6 else (f"${v/1e3:.0f}K" if v >= 1e4 else f"${v:,.0f}")

C1, C2 = "#4ade80", "#38bdf8"   # Y1(폭락장 시작)=초록, Y2=금색
W, REEL_H, FPS = 1080, 1920, 30
BRAND = "#fbbf24"   # 브랜드 골드
HOOK, REVEAL, GSEC = 2.0, 12.0, 16.0
box = (164, 660, 964, 1360)

t = yf.Ticker(TICKER); h = t.history(start=f"{Y1-1}-06-01", end="2026-07-31", auto_adjust=False)
h.index = h.index.tz_localize(None); close = h["Close"].dropna()
def yr(d):
    d = pd.Timestamp(d); return d.year + (d.dayofyear - 1) / (366 if d.is_leap_year else 365)


def scenario(start_year):
    px = close[close.index >= pd.Timestamp(f"{start_year}-01-01")]
    buys = px.resample("ME").last().dropna(); bd = list(buys.index)
    sh = inv = 0.0; bi = 0; nav = []; invp = []; flows = []
    for d, p in px.items():
        while bi < len(bd) and d >= bd[bi]:
            sh += MO / buys.iloc[bi]; inv += MO; flows.append((bd[bi].date(), -MO)); bi += 1
        nav.append((yr(d), sh * p)); invp.append((yr(d), inv))
    fin = sh * px.iloc[-1]; flows.append((px.index[-1].date(), fin))
    return dict(nav=nav, invp=invp, fin=fin, inv=inv, mult=fin / inv, xirr=E.xirr(flows), n=len(bd))


S1 = scenario(Y1); S2 = scenario(Y2)
X0 = yr(close[close.index >= pd.Timestamp(f"{Y1}-01-01")].index[0].date())
END_X = yr(close.index[-1].date())
def nc(x):
    e = 10 ** math.floor(math.log10(x)); f = x / e
    for n in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if f <= n: return int(n * e)
    return int(10 * e)
Y_TOP0 = nc(max(S1["fin"], S2["fin"]) * 1.05)
TXT, LINE, EDGE = "#b3b3b3", "#242424", "#3a3a3a"


def clipd(pts, lim):
    out = []
    for i, p in enumerate(pts):
        if p[0] <= lim: out.append(p); continue
        if out:
            pr = pts[i - 1]; sp = p[0] - pr[0]
            if sp > 0: r = max(0, min(1, (lim - pr[0]) / sp)); out.append((lim, pr[1] + (p[1] - pr[1]) * r))
        break
    return out


def dashed(d, xy, fill, w, on=16, off=12):
    rem, dr = on, True
    for (x0, y0), (x1, y1) in zip(xy, xy[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg == 0: continue
        pos = 0.0
        while pos < seg:
            st = min(rem, seg - pos); a, b = pos / seg, (pos + st) / seg
            if dr: d.line((x0 + (x1 - x0) * a, y0 + (y1 - y0) * a, x0 + (x1 - x0) * b, y0 + (y1 - y0) * b), fill=fill, width=w)
            pos += st; rem -= st
            if rem <= 1e-6: dr = not dr; rem = on if dr else off


def header(d):
    cx = W // 2; l1, l2 = f"{NAME} 적립, 언제 시작?", f"{Y1} 폭락장 vs {Y2}, {int(END_X)-Y1}년 뒤"
    size = 74
    while size > 44 and max(font(size, True).getlength(l1), font(size, True).getlength(l2)) > 1000: size -= 2
    tf = font(size, True); asc, desc = tf.getmetrics(); lh = asc + desc
    ty = 689 - 150 + 18 - (2 * lh + 5)
    d.text((cx, ty), l1, anchor="ma", fill="#f5f5f5", font=tf)
    d.text((cx, ty + lh + 5), l2, anchor="ma", fill="#f5f5f5", font=tf)


def render(tt):
    im = Image.new("RGB", (W, REEL_H), "#000000"); d = ImageDraw.Draw(im); header(d)
    left, top, right, bottom = box
    if tt < HOOK: clip_end = END_X; prog = 1.0
    else: prog = ease((tt - HOOK) / REVEAL); clip_end = lerp(X0, END_X, prog)
    ap = prog if tt >= HOOK else 1.0
    vis = MO
    for S in (S1, S2):
        vv = [v for _, v in clipd(S["nav"], clip_end)]
        if vv: vis = max(vis, *vv)
    y_top = max(nc(vis * 1.08), 1)
    # 축
    axr = lerp(left, right, ap)
    for i in range(3):
        v = y_top * i / 2; y = bottom - (bottom - top) * i / 2
        d.line((left, y, axr, y), fill=LINE, width=2); d.text((left - 18, y), (usd(v) if v > 0 else "0"), anchor="rm", fill=TXT, font=font(31))
    xids = (0,) if ap < .12 else ((0, 4) if ap < .28 else range(5))
    for i in xids:
        yv = X0 + (clip_end - X0) * i / 4; x = left + (right - left) * ap * i / 4
        d.line((x, top, x, bottom), fill=LINE, width=2); d.text((x, bottom + 30), f"{yv:.0f}", anchor="ma", fill=TXT, font=font(30))
    d.line((left, bottom, axr, bottom), fill=EDGE, width=2); d.line((left, bottom, left, top), fill=EDGE, width=2)
    d.text((left, top - 16), f"{Y1}.01~{int(END_X)}.{round((END_X-int(END_X))*12)+1:02d}", anchor="ls", fill="#8a8a8a", font=font(32))

    def to_xy(pts):
        return [(left + (a - X0) / max(clip_end - X0, 1e-4) * (right - left) * ap, max(top, bottom - b / y_top * (bottom - top))) for a, b in pts]
    # 누적원금 점선(은은) 먼저
    for S, col in [(S1, C1), (S2, C2)]:
        cp = clipd(S["invp"], clip_end)
        if len(cp) >= 2: dashed(d, to_xy(cp), col, 3)
    # 평가액 solid + 끝점 링
    live = []
    for S, col, y in [(S1, C1, Y1), (S2, C2, Y2)]:
        cp = clipd(S["nav"], clip_end)
        if len(cp) < 2: live.append((y, col, MO, 1.0)); continue
        xy = to_xy(cp); d.line(xy, fill=col, width=9, joint="curve")
        ex, ey = xy[-1]; d.ellipse((ex - 12, ey - 12, ex + 12, ey + 12), outline=col, width=5, fill="#000000")
        final = clip_end >= END_X - .05
        live.append((y, col, S["fin"] if final else cp[-1][1], (S["fin"] if final else cp[-1][1]) / max(clipd(S["invp"], clip_end)[-1][1], 1)))
    # 하단 범례
    lf, vf = font(34), font(44, True)
    for i, (y, col, val, mult) in enumerate(live):
        yy = bottom + 138 + i * 66
        d.rounded_rectangle((190, yy - 7, 230, yy + 7), 4, fill=col)
        d.text((252, yy), f"{y}년부터 적립", anchor="lm", fill="#dddddd", font=lf)
        d.text((938, yy), f"{dol(val)} ({mult:.2f}배)", anchor="rm", fill="#f5f5f5", font=vf)
    d.text((72, 1712), f"매달 {dol(MO)} 적립 · 첫 거래월말 매수 · 배당 미미(무시)", fill="#666666", font=font(25))
    d.text((984, 1710), "번외 · 1/2", anchor="ra", fill="#777777", font=font(28))
    return im


def render_table():
    im = Image.new("RGB", (W, REEL_H), "#000000"); d = ImageDraw.Draw(im)
    d.multiline_text((W // 2, 230), f"{NAME} 적립\n{Y1} 폭락장 vs {Y2} 시작", fill="#f5f5f5", font=font(58, True), spacing=8, anchor="ma", align="center")
    cx1, cx2 = 640, 910; ty = 560
    d.text((cx1, ty), f"{Y1}부터", anchor="mm", fill=C1, font=font(44, True)); d.text((cx1, ty + 48), "폭락장 시작", anchor="mm", fill="#8a8a8a", font=font(28))
    d.text((cx2, ty), f"{Y2}부터", anchor="mm", fill=C2, font=font(44, True))
    d.line((120, ty + 70, 980, ty + 70), fill=EDGE, width=2)
    rows = [("투입 원금", dol(S1["inv"]), dol(S2["inv"]), None),
            ("평가액", dol(S1["fin"]), dol(S2["fin"]), S1["fin"] >= S2["fin"]),
            ("원금 대비", f"{S1['mult']:.2f}배", f"{S2['mult']:.2f}배", S1["mult"] >= S2["mult"]),
            ("XIRR(연)", f"{S1['xirr']*100:.0f}%", f"{S2['xirr']*100:.0f}%", S1["xirr"] >= S2["xirr"])]
    for i, (lab, v1, v2, win1) in enumerate(rows):
        ry = ty + 140 + i * 130
        d.text((130, ry), lab, anchor="lm", fill="#cfcfcf", font=font(38))
        d.text((cx1, ry), v1, anchor="mm", fill=C1, font=font(48, True))
        d.text((cx2, ry), v2, anchor="mm", fill=C2, font=font(48, True))
        if win1 is not None: d.text((cx1 if win1 else cx2, ry + 50), "▲ 우위", anchor="mm", fill=(C1 if win1 else C2), font=font(28, True))
        if i < 3: d.line((120, ry + 65, 980, ry + 65), fill="#161616", width=2)
    py = ty + 140 + 4 * 130 + 40
    d.multiline_text((W // 2, py), f"무서운 폭락장에 시작해도\n{int(END_X)-Y1}년 뒤 {S1['mult']:.1f}배 — 미룰 이유 없다", fill="#f5f5f5", font=font(40, True), spacing=10, anchor="ma", align="center")
    d.text((72, 1712), f"매달 {dol(MO)} 적립 · 과거 데이터 백테스트 · 레버리지는 변동성 극대", fill="#666666", font=font(24))
    d.text((984, 1710), "번외 · 2/2", anchor="ra", fill="#777777", font=font(28))
    return im


def main():
    render(999).save(EXPORTS / f"{PREFIX}_dcatiming.png")
    print(f"{Y1}: {dol(S1['fin'])} {S1['mult']:.2f}배 XIRR {S1['xirr']*100:.0f}% | {Y2}: {dol(S2['fin'])} {S2['mult']:.2f}배 XIRR {S2['xirr']*100:.0f}%")
    base = EXPORTS / f"{PREFIX}_dcatiming_reel.mp4"
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{REEL_H}", "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(base)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    table = render_table(); gf = round(GSEC * FPS); fade = round(0.5 * FPS); hold = round(4.0 * FPS)
    for fr in range(gf + fade + hold):
        if fr < gf: img = render(fr / FPS)
        elif fr < gf + fade: img = Image.blend(render(GSEC), table, (fr - gf) / fade)
        else: img = table
        mv = memoryview(img.tobytes())
        while mv: mv = mv[p.stdin.write(mv):]
    p.stdin.close()
    if p.wait() != 0: raise SystemExit("ffmpeg failed")
    framed = EXPORTS / f"{PREFIX}_dcatiming_reel_top100px.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(base), "-vf", "scale=960:1820:flags=lanczos,pad=1080:1920:60:50:black",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(framed)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("reel →", framed)


if __name__ == "__main__":
    main()
