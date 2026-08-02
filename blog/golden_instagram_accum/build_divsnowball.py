#!/usr/bin/env python3
"""번외: 배당 눈덩이 — 배당 재투자 O vs X의 '연 배당금'·'누적 배당금' 차이.

한 번 매수 후 계속 보유하며, 배당을 (O)재투자 / (X)현금 수령했을 때
'받는(발생하는) 배당금' 자체가 어떻게 벌어지는지 본다(주가·총자산 아님).
  · 재투자 O: 세후배당으로 당일 종가 매수 → 주식수 증가 → 배당 눈덩이
  · 재투자 X: 주식수 고정 → 배당은 DPS 성장만큼만 증가
2패널(① 연 배당금 회계연도 막대 · ② 누적 배당금 area) 애니 릴 + 정적 PNG.

사용: SHORTS_STOCK=KTNG python3 build_divsnowball.py
출력: exports/<pref>_divsnowball.png · exports/<pref>_divsnowball_reel(_top100px).mp4
"""
import os, math, subprocess, sys
from datetime import date
from pathlib import Path

import pandas as pd, yfinance as yf
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, "..", "..", "global_cup_suite")))
from global_cup.fire_engine import run_fire_backtest

STOCK = os.environ.get("SHORTS_STOCK", "KTNG").upper()
# 종목 설정. fy_start=배당 회계연도 시작월(KT&G 등 기말배당 익년 지급 → 4월; 미국 분기배당 → 1=달력).
CFG = {
    "KTNG": dict(ticker="033780.KS", start=2005, amount=100_000_000, krw=True,  name="KT&G",     fy_start=4, pref="ktng"),
    "SEC":  dict(ticker="005930.KS", start=2005, amount=100_000_000, krw=True,  name="삼성전자",  fy_start=4, pref="sec"),
    "SKH":  dict(ticker="000660.KS", start=2005, amount=100_000_000, krw=True,  name="SK하이닉스", fy_start=4, pref="skh"),
    "SCHD": dict(ticker="SCHD",      start=2012, amount=100_000,     krw=False, name="SCHD",     fy_start=1, pref="schd"),
    "MO":   dict(ticker="MO",        start=2005, amount=100_000,     krw=False, name="알트리아",   fy_start=1, pref="mo"),
    "O":    dict(ticker="O",         start=2000, amount=100_000,     krw=False, name="리얼티인컴", fy_start=1, pref="o"),  # 월배당 REIT. 2005 2:1분할·2021 1.032합병 종가·배당 일관보정(확인)
}[STOCK]
TICKER, START, AMT, KRW, NAME, FYS0, PREFIX = (CFG["ticker"], CFG["start"], CFG["amount"],
                                               CFG["krw"], CFG["name"], CFG["fy_start"], CFG["pref"])
TAX = 0.154 if KRW else 0.15
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
def font(s, b=False): return ImageFont.truetype(BOLD if b else FONT, s)
def ease(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)

def won(v):     # 축 라벨: KRW 억/만 · USD $M/$K
    if KRW: return f"{v/1e8:.2f}억" if v >= 1e8 else f"{int(round(v/1e4)):,}만"
    return f"${v/1e6:.2f}M" if v >= 1e6 else f"${v/1e3:.0f}K"
def unit(v):    # 범례 값: KRW 만원 · USD $
    return f"{v/1e4:,.0f}만원" if KRW else f"${v:,.0f}"
def amt_lbl(v):
    if KRW: return f"{v//100000000}억" if v >= 1e8 else f"{int(v//1e4):,}만원"
    return f"${v:,.0f}"

# ── 데이터 & 두 시나리오 배당 시계열 ──
t = yf.Ticker(TICKER)
h = t.history(start=f"{START}-01-01", end="2026-07-31", auto_adjust=False); h.index = h.index.tz_localize(None)
close = h["Close"].dropna(); dv = t.dividends; dv.index = dv.index.tz_localize(None); dv = dv[dv.index >= close.index[0]]
p0 = close.iloc[0]
def yr(d):
    y0 = date(d.year, 1, 1); y1 = date(d.year + 1, 1, 1); return d.year + (d - y0).days / (y1 - y0).days
X0 = yr(close.index[0].date()); END_X = yr(close.index[-1].date())
def fy(dt): return dt.year if dt.month >= FYS0 else dt.year - 1

sh_o = AMT / p0; sh_x = AMT / p0
annO, annX = {}, {}; cumO_pts = [(X0, 0.0)]; cumX_pts = [(X0, 0.0)]; cO = cX = 0.0
for dt_, dps in dv.sort_index().items():
    px = close.asof(dt_); f = fy(dt_)
    nx = sh_x * float(dps) * (1 - TAX); no = sh_o * float(dps) * (1 - TAX)
    annX[f] = annX.get(f, 0) + nx; annO[f] = annO.get(f, 0) + no
    y = yr(dt_.date()); cX += nx; cumX_pts += [(y, cX - nx), (y, cX)]
    cO += no; cumO_pts += [(y, cO - no), (y, cO)]; sh_o += no / px
cumX_pts.append((END_X, cX)); cumO_pts.append((END_X, cO))
LAST_FY = max(f for f in annX if yr(date(f + 1, 1, 1)) <= END_X)   # 완결 회계연도만
fys = [f for f in sorted(annX) if f <= LAST_FY]

def nc(x):
    e = 10 ** math.floor(math.log10(x)); f = x / e
    for n in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if f <= n: return int(n * e)
    return int(10 * e)
def clipd(pts, lim):
    out = []
    for i, p in enumerate(pts):
        if p[0] <= lim: out.append(p); continue
        if out:
            pr = pts[i - 1]; sp = p[0] - pr[0]
            if sp > 0: r = max(0, min(1, (lim - pr[0]) / sp)); out.append((lim, pr[1] + (p[1] - pr[1]) * r))
        break
    return out
yaA = nc(max(annO[f] for f in fys) * 1.1); yaB = nc(cO * 1.08)
GREEN, GOLD, TXT, LINE, EDGE = "#4ade80", "#fbbf24", "#b3b3b3", "#242424", "#3a3a3a"
W, H, FPS = 1080, 1920, 30
HOOK, REVEAL, GSEC = 2.0, 16.0, 20.0
ax0, ay0, ax1, ay1 = 180, 470, 980, 830
bx0, by0, bx1, by1 = 180, 1050, 980, 1440
EXPORTS = ROOT / "exports"
FYNOTE = "회계연도(중간+기말)" if FYS0 != 1 else "연도"


def render(tt):
    im = Image.new("RGB", (W, H), "#000000"); d = ImageDraw.Draw(im)
    d.multiline_text((W // 2, 150), f"배당 재투자하면, 배당이 눈덩이\n{NAME}에 {amt_lbl(AMT)} 투자",
                     fill="#f5f5f5", font=font(60, True), spacing=6, anchor="ma", align="center")
    prog = 1.0 if tt < HOOK else ease((tt - HOOK) / REVEAL)
    rev = X0 + (END_X - X0) * prog
    # 패널 A: 연 배당금 막대(회계연도)
    d.text((ax0, ay0 - 62), "① 연 배당금 (%s)" % ("회계연도" if FYS0 != 1 else "연도"), fill="#eaeaea", font=font(36, True))
    for i in range(3):
        v = yaA * i / 2; y = ay1 - (ay1 - ay0) * i / 2; d.line((ax0, y, ax1, y), fill=LINE, width=2)
        d.text((ax0 - 14, y), (won(v) if v > 0 else "0"), anchor="rm", fill=TXT, font=font(26))
    n = len(fys); slot = (ax1 - ax0) / n; bw = slot * 0.34
    for i, f in enumerate(fys):
        fr = ease(max(0., min(1., rev - f)))
        if fr <= 0: continue
        xc = ax0 + slot * (i + 0.5)
        for val, col, off in [(annX[f], GOLD, -bw * 0.55), (annO[f], GREEN, bw * 0.55)]:
            bh = (ay1 - ay0) * val / yaA * fr
            if bh > 0: d.rectangle((xc + off - bw / 2, ay1 - bh, xc + off + bw / 2, ay1), fill=col)
        if f % 5 == 0 or f == fys[-1]: d.text((xc, ay1 + 8), f"{f}", anchor="ma", fill=TXT, font=font(24))
    d.line((ax0, ay1, ax1, ay1), fill=EDGE, width=2)
    # 패널 B: 누적 배당금 area
    d.text((bx0, by0 - 62), "② 누적 배당금", fill="#eaeaea", font=font(36, True))
    for i in range(3):
        v = yaB * i / 2; y = by1 - (by1 - by0) * i / 2; d.line((bx0, y, bx1, y), fill=LINE, width=2)
        d.text((bx0 - 14, y), (won(v) if v > 0 else "0"), anchor="rm", fill=TXT, font=font(26))
    for i in range(5):
        yv = X0 + (END_X - X0) * i / 4; x = bx0 + (bx1 - bx0) * i / 4
        d.line((x, by0, x, by1), fill=LINE, width=2); d.text((x, by1 + 8), f"{yv:.0f}", anchor="ma", fill=TXT, font=font(24))
    d.line((bx0, by1, bx1, by1), fill=EDGE, width=2)
    BX = lambda y: bx0 + (y - X0) / (END_X - X0) * (bx1 - bx0)
    BY = lambda v: by1 - v / yaB * (by1 - by0)
    co = clipd(cumO_pts, rev); cx = clipd(cumX_pts, rev)
    if len(co) >= 2 and len(cx) >= 2:
        oxy = [(BX(y), BY(v)) for y, v in co]; xxy = [(BX(y), BY(v)) for y, v in cx]
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.polygon(oxy + [(oxy[-1][0], by1), (bx0, by1)], fill=(74, 222, 128, 45))
        od.polygon(xxy + [(xxy[-1][0], by1), (bx0, by1)], fill=(251, 191, 36, 70))
        im2 = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB"); im.paste(im2); d = ImageDraw.Draw(im)
        d.line(oxy, fill=GREEN, width=6); d.line(xxy, fill=GOLD, width=6)
    # 동적 범례: 재투자 O/X · 연배당금·누적배당금(라이브)
    cur_f = max([f for f in fys if f <= rev], default=fys[0])
    cum_o = co[-1][1] if len(co) >= 1 else 0.0; cum_x = cx[-1][1] if len(cx) >= 1 else 0.0
    for i, (lab, col, ann, cum) in enumerate([("재투자 O", GREEN, annO[cur_f], cum_o),
                                              ("재투자 X", GOLD, annX[cur_f], cum_x)]):
        yy = 1520 + i * 60
        d.rounded_rectangle((bx0, yy - 7, bx0 + 40, yy + 7), 4, fill=col)
        d.text((bx0 + 52, yy), lab, anchor="lm", fill="#dddddd", font=font(30))
        d.text((bx1, yy), f"연배당금 {unit(ann)} · 누적배당금 {unit(cum)}", anchor="rm", fill=col, font=font(28, True))
    d.text((72, 1712), f"{START}년 {amt_lbl(AMT)}({AMT/p0:,.0f}주) 매수 · {FYNOTE} · 배당세 {TAX*100:.1f}%",
           fill="#666666", font=font(24))
    d.text((984, 1710), "번외", anchor="ra", fill="#777777", font=font(28))
    return im


def main():
    png = EXPORTS / f"{PREFIX}_divsnowball.png"; render(999).save(png)
    print("연배당 O", unit(annO[fys[-1]]), "X", unit(annX[fys[-1]]), "| 누적 O", won(cO), "X", won(cX))
    print("PNG →", png)
    base = EXPORTS / f"{PREFIX}_divsnowball_reel.mp4"
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(base)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fr in range(round(GSEC * FPS)):
        mv = memoryview(render(fr / FPS).tobytes())
        while mv: mv = mv[p.stdin.write(mv):]
    p.stdin.close()
    if p.wait() != 0: raise SystemExit("ffmpeg failed")
    framed = EXPORTS / f"{PREFIX}_divsnowball_reel_top100px.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(base), "-vf",
                    "scale=960:1820:flags=lanczos,pad=1080:1920:60:50:black", "-c:v", "libx264",
                    "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    str(framed)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("reel →", framed)


if __name__ == "__main__":
    main()
