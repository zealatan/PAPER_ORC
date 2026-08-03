#!/usr/bin/env python3
"""번외: 은퇴 시점 비교 — 고점 은퇴 vs 그 뒤 은퇴(수익률 순서 위험).

같은 원금·같은 월 인출(물가연동)로 은퇴하되 '은퇴 연도'만 다르게(예: TQQQ 2022 고점 vs 2023).
평가액 2선 + 은퇴 원금 흰 기준선. 고점 직후 폭락+인출은 바닥에서 강제 매도 → 회복 열매 놓침.
2페이지 요약표(원금·최종·최저점·원금대비).

사용: RT_TICKER=TQQQ python3 build_retire_timing.py
출력: exports/<pref>_retiretiming.png · <pref>_retiretiming_reel(_top100px).mp4
"""
import os, math, subprocess, sys
from datetime import date
from pathlib import Path
import pandas as pd, yfinance as yf
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent; EXPORTS = ROOT / "exports"
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, "..", "..", "global_cup_suite")))
from global_cup.fire_engine import run_fire_backtest

TICKER = os.environ.get("RT_TICKER", "TQQQ").upper()
NAME = TICKER   # 타이틀은 티커만
Y1, Y2 = int(os.environ.get("RT_Y1", "2022")), int(os.environ.get("RT_Y2", "2023"))
P = float(os.environ.get("RT_PRINCIPAL", "800000"))       # 은퇴 원금
MO = float(os.environ.get("RT_WITHDRAW", "4000"))         # 월 인출(물가연동)
PREFIX = TICKER.lower()
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
def font(s, b=False): return ImageFont.truetype(BOLD if b else FONT, s)
def ease(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * ease(t)
def dol(v): return f"${v:,.0f}"
def usd(v): return f"${v/1e6:.2f}M" if v >= 1e6 else (f"${v/1e3:.0f}K" if v >= 1e4 else f"${v:,.0f}")

C1, C2 = "#fb7185", "#4ade80"   # Y1(고점 은퇴)=금색, Y2=초록(회복장 은퇴)
W, REEL_H, FPS = 1080, 1920, 30
BRAND = "#fbbf24"   # 브랜드 골드
HOOK, REVEAL, GSEC = 2.0, 12.0, 16.0
box = (164, 660, 964, 1360)

cpi = pd.read_csv(os.path.join(ROOT, "..", "PG", "ref", "fred_CPIAUCSL.csv"), parse_dates=["date"])
cpi = pd.Series(pd.to_numeric(cpi["val"], errors="coerce").values, index=cpi["date"]).dropna()
t = yf.Ticker(TICKER); h = t.history(start=f"{Y1-1}-06-01", end="2026-07-31", auto_adjust=False)
h.index = h.index.tz_localize(None); close = h["Close"].dropna(); dv = t.dividends; dv.index = dv.index.tz_localize(None)
def yr(d):
    d = pd.Timestamp(d); return d.year + (d.dayofyear - 1) / (366 if d.is_leap_year else 365)


def scenario(y):
    r = run_fire_backtest(close, dv, P, annual_withdrawal=MO * 12, strategy="fixed_real", frequency="monthly",
                          tax_rate_pct=15.0, reinvest_dividends=False, reinvest_surplus=True, cpi=cpi, start_date=date(y, 1, 1))
    tl = r.timeline_df.copy(); tl["Date"] = pd.to_datetime(tl["Date"])
    nav = [(yr(d), v) for d, v in zip(tl["Date"], tl["Portfolio Value"])]
    return dict(nav=nav, fin=r.summary["Final Value"], mn=tl["Portfolio Value"].min(),
                surv=r.summary["Survived"], mult=r.summary["Final Value"] / P)


S1 = scenario(Y1); S2 = scenario(Y2)
X0 = S1["nav"][0][0]; END_X = yr(close.index[-1].date())   # nav[..][0]은 이미 연도 float
def nc(x):
    e = 10 ** math.floor(math.log10(x)); f = x / e
    for n in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if f <= n: return int(n * e)
    return int(10 * e)
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


def header(d):
    cx = W // 2; l1, l2 = f"{NAME}로 은퇴, 언제 했나", f"{Y1} 고점 vs {Y2}, 1년 차이"
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
    vis = P
    for S in (S1, S2):
        vv = [v for _, v in clipd(S["nav"], clip_end)]
        if vv: vis = max(vis, *vv)
    y_top = max(nc(vis * 1.08), 1)
    for i in range(3):   # x축 고정(2022~END), 데이터만 리빌
        v = y_top * i / 2; y = bottom - (bottom - top) * i / 2
        d.line((left, y, right, y), fill=LINE, width=2); d.text((left - 18, y), (usd(v) if v > 0 else "0"), anchor="rm", fill=TXT, font=font(31))
    for i in range(5):
        yv = X0 + (END_X - X0) * i / 4; x = left + (right - left) * i / 4
        d.line((x, top, x, bottom), fill=LINE, width=2); d.text((x, bottom + 30), f"{yv:.0f}", anchor="ma", fill=TXT, font=font(30))
    d.line((left, bottom, right, bottom), fill=EDGE, width=2); d.line((left, bottom, left, top), fill=EDGE, width=2)
    d.text((left, top - 16), f"{Y1}.01~{int(END_X)}.{round((END_X-int(END_X))*12)+1:02d}", anchor="ls", fill="#8a8a8a", font=font(32))
    if y_top >= P:
        hy = bottom - P / y_top * (bottom - top)
        d.line((left, hy, right, hy), fill="#ffffff", width=4)
        d.multiline_text((left - 18, hy - 6), f"은퇴 원금\n{dol(P)}", anchor="rd", align="right", spacing=2, fill="#ffffff", font=font(26, True))

    def to_xy(pts):
        return [(left + (a - X0) / (END_X - X0) * (right - left), max(top, bottom - b / y_top * (bottom - top))) for a, b in pts]
    live = []
    for S, col, y in [(S1, C1, Y1), (S2, C2, Y2)]:
        cp = clipd(S["nav"], clip_end)
        if len(cp) < 2: live.append((y, col, P, 1.0)); continue
        xy = to_xy(cp); d.line(xy, fill=col, width=9, joint="curve")
        ex, ey = xy[-1]; d.ellipse((ex - 12, ey - 12, ex + 12, ey + 12), outline=col, width=5, fill="#000000")
        final = clip_end >= END_X - .05; val = S["fin"] if final else cp[-1][1]
        live.append((y, col, val, val / P))
    lf, vf = font(34), font(44, True)
    for i, (y, col, val, mult) in enumerate(live):
        yy = bottom + 138 + i * 66
        d.rounded_rectangle((190, yy - 7, 230, yy + 7), 4, fill=col)
        d.text((252, yy), f"{y}년 은퇴", anchor="lm", fill="#dddddd", font=lf)
        d.text((938, yy), f"{usd(val)} ({mult:.1f}배)", anchor="rm", fill="#f5f5f5", font=vf)
    d.text((72, 1712), f"원금 {dol(P)} · 월 {dol(MO)} 인출(물가연동) · 배당세 15%", fill="#666666", font=font(25))
    d.text((984, 1710), "번외 · 1/2", anchor="ra", fill="#777777", font=font(28))
    return im


def render_table():
    im = Image.new("RGB", (W, REEL_H), "#000000"); d = ImageDraw.Draw(im)
    d.multiline_text((W // 2, 230), f"{NAME}로 은퇴\n{Y1} 고점 vs {Y2}", fill="#f5f5f5", font=font(58, True), spacing=8, anchor="ma", align="center")
    cx1, cx2 = 620, 900; ty = 560
    d.text((cx1, ty), f"{Y1} 은퇴", anchor="mm", fill=C1, font=font(44, True)); d.text((cx1, ty + 48), "고점 은퇴", anchor="mm", fill="#8a8a8a", font=font(28))
    d.text((cx2, ty), f"{Y2} 은퇴", anchor="mm", fill=C2, font=font(44, True))
    d.line((100, ty + 70, 1000, ty + 70), fill=EDGE, width=2)
    rows = [("은퇴 원금", dol(P), dol(P), None),
            ("최종 평가액", usd(S1["fin"]), usd(S2["fin"]), S1["fin"] >= S2["fin"]),
            ("최저점", usd(S1["mn"]), usd(S2["mn"]), S1["mn"] >= S2["mn"]),
            ("원금 대비", f"{S1['mult']:.1f}배", f"{S2['mult']:.1f}배", S1["mult"] >= S2["mult"])]
    for i, (lab, v1, v2, win1) in enumerate(rows):
        ry = ty + 140 + i * 130
        d.text((110, ry), lab, anchor="lm", fill="#cfcfcf", font=font(38))
        d.text((cx1, ry), v1, anchor="mm", fill=C1, font=font(46, True))
        d.text((cx2, ry), v2, anchor="mm", fill=C2, font=font(46, True))
        if win1 is not None: d.text((cx1 if win1 else cx2, ry + 50), "▲ 우위", anchor="mm", fill=(C1 if win1 else C2), font=font(28, True))
        if i < 3: d.line((100, ry + 65, 1000, ry + 65), fill="#161616", width=2)
    py = ty + 140 + 4 * 130 + 40
    d.multiline_text((W // 2, py), f"같은 {TICKER}, 1년 차이\n고점 은퇴는 -{round((1-S1['mn']/P)*100)}% 지옥 (수익률 순서 위험)", fill="#f5f5f5", font=font(38, True), spacing=10, anchor="ma", align="center")
    d.text((72, 1712), f"원금 {dol(P)} · 월 {dol(MO)} 인출 · 물가연동 · 과거 데이터 · 레버리지 극단적", fill="#666666", font=font(23))
    d.text((984, 1710), "번외 · 2/2", anchor="ra", fill="#777777", font=font(28))
    return im


def main():
    render(999).save(EXPORTS / f"{PREFIX}_retiretiming.png")
    print(f"{Y1}: {dol(S1['fin'])} 최저 {dol(S1['mn'])} {S1['mult']:.2f}배 | {Y2}: {dol(S2['fin'])} 최저 {dol(S2['mn'])} {S2['mult']:.2f}배")
    base = EXPORTS / f"{PREFIX}_retiretiming_reel.mp4"
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
    framed = EXPORTS / f"{PREFIX}_retiretiming_reel_top100px.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(base), "-vf", "scale=960:1820:flags=lanczos,pad=1080:1920:60:50:black",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(framed)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("reel →", framed)


if __name__ == "__main__":
    main()
