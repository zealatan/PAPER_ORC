#!/usr/bin/env python3
"""번외: 고점 은퇴 후 하락장 방어력 — 성장 vs 배당성장 vs 고배당.

같은 시점(고점)에 같은 원금·월 인출로 은퇴한 뒤, '고점→저점 하락장'에서 자산이 얼마나 녹나.
평가액 3선(하락) + 은퇴 원금 흰 기준선. 2페이지 요약표(구간최저·낙폭).

사용: RS_START=2022 RS_END=2023-03-31 python3 build_retire_stocks.py
출력: exports/retirestocks_<start>.png · _reel(_top100px).mp4
"""
import os, math, subprocess, sys
from datetime import date
from pathlib import Path
import pandas as pd, yfinance as yf
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent; EXPORTS = ROOT / "exports"
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, "..", "..", "global_cup_suite")))
from global_cup.fire_engine import run_fire_backtest

START = int(os.environ.get("RS_START", "2022"))
ENDW = pd.Timestamp(os.environ.get("RS_END", "2023-03-31"))
P = float(os.environ.get("RS_PRINCIPAL", "800000"))
MO = float(os.environ.get("RS_WITHDRAW", "4000"))
# 종목 메타(유형·색). RS_STOCKS="TQQQ,QLD"로 선택(기본 QQQ,SCHD,QYLD).
# 데이터선 색: 브랜드 골드(#fbbf24)는 제외(브랜드 전용). QYLD=오렌지로 분리.
META = {"QQQ": ("성장", "#38bdf8"), "SCHD": ("배당성장", "#4ade80"), "QYLD": ("고배당", "#ff8c42"),
        "TQQQ": ("나스닥 3배", "#f472b6"), "QLD": ("나스닥 2배", "#38bdf8"), "SPY": ("S&P500", "#60a5fa")}
STOCKS = [(tk, META[tk][0], META[tk][1]) for tk in os.environ.get("RS_STOCKS", "QQQ,SCHD,QYLD").split(",")]
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
def font(s, b=False): return ImageFont.truetype(BOLD if b else FONT, s)
def ease(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * ease(t)
def dol(v): return f"${v:,.0f}"
def usd(v): return f"${v/1e6:.2f}M" if v >= 1e6 else (f"${v/1e3:.0f}K" if v >= 1e4 else f"${v:,.0f}")
W, REEL_H, FPS = 1080, 1920, 30
HOOK, REVEAL, GSEC = 2.0, 11.0, 15.0
box = (164, 660, 964, 1360)
TXT, LINE, EDGE = "#b3b3b3", "#242424", "#3a3a3a"

cpi = pd.read_csv(os.path.join(ROOT, "..", "PG", "ref", "fred_CPIAUCSL.csv"), parse_dates=["date"])
cpi = pd.Series(pd.to_numeric(cpi["val"], errors="coerce").values, index=cpi["date"]).dropna()
def yr(d):
    d = pd.Timestamp(d); return d.year + (d.dayofyear - 1) / (366 if d.is_leap_year else 365)


def scenario(tk):
    t = yf.Ticker(tk); h = t.history(start=f"{START-1}-06-01", end="2023-09-30", auto_adjust=False)
    h.index = h.index.tz_localize(None); c = h["Close"].dropna(); dv = t.dividends; dv.index = dv.index.tz_localize(None)
    r = run_fire_backtest(c, dv, P, annual_withdrawal=MO * 12, strategy="fixed_real", frequency="monthly",
                          tax_rate_pct=15.0, reinvest_dividends=False, reinvest_surplus=True, cpi=cpi, start_date=date(START, 1, 1))
    tl = r.timeline_df.copy(); tl["Date"] = pd.to_datetime(tl["Date"]); tl = tl[tl["Date"] <= ENDW]
    nav = [(yr(d), v) for d, v in zip(tl["Date"], tl["Portfolio Value"])]
    mn = tl["Portfolio Value"].min()
    return dict(nav=nav, mn=mn, dd=1 - mn / P, endv=tl["Portfolio Value"].iloc[-1])


DATA = [(tk, ty, col, scenario(tk)) for tk, ty, col in STOCKS]
X0 = DATA[0][3]["nav"][0][0]; END_X = yr(ENDW)
def nc(x):
    e = 10 ** math.floor(math.log10(x)); f = x / e
    for n in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if f <= n: return int(n * e)
    return int(10 * e)
Y_TOP = nc(P * 1.12)


def clipd(pts, lim):
    out = []
    for i, p in enumerate(pts):
        if p[0] <= lim: out.append(p); continue
        if out:
            pr = pts[i - 1]; sp = p[0] - pr[0]
            if sp > 0: r = max(0, min(1, (lim - pr[0]) / sp)); out.append((lim, pr[1] + (p[1] - pr[1]) * r))
        break
    return out


BRAND = os.environ.get("RS_BRAND", "#fbbf24")   # 시그니처 브랜드색(골드) — 전 릴 공통


def header(d):
    cx = W // 2
    l1 = " vs ".join(tk for tk, _, _ in STOCKS)      # 주제=티커(브랜드 그린)
    l2 = f"{START}년 고점 은퇴 · 하락장"              # 설명(흰색)
    size = 74
    while size > 44 and max(font(size, True).getlength(l1), font(size, True).getlength(l2)) > 1000: size -= 2
    tf = font(size, True); asc, desc = tf.getmetrics(); lh = asc + desc
    ty = 689 - 150 + 18 - (2 * lh + 5)
    d.text((cx, ty), l1, anchor="ma", fill="#f5f5f5", font=tf)
    d.text((cx, ty + lh + 5), l2, anchor="ma", fill="#f5f5f5", font=tf)


def render(tt):
    im = Image.new("RGB", (W, REEL_H), "#000000"); d = ImageDraw.Draw(im); header(d)
    left, top, right, bottom = box
    clip_end = END_X if tt < HOOK else lerp(X0, END_X, ease((tt - HOOK) / REVEAL))
    y_top = Y_TOP
    for i in range(3):
        v = y_top * i / 2; y = bottom - (bottom - top) * i / 2
        d.line((left, y, right, y), fill=LINE, width=2); d.text((left - 18, y), (usd(v) if v > 0 else "0"), anchor="rm", fill=TXT, font=font(31))
    # x축(월 단위 라벨: 짧은 구간)
    months = [(2022.0, "2022.01"), (2022.25, "04"), (2022.5, "07"), (2022.75, "10"), (2023.0, "2023.01")]
    for xv, lab in months:
        if xv < X0 - .02 or xv > END_X + .02: continue
        x = left + (xv - X0) / (END_X - X0) * (right - left)
        d.line((x, top, x, bottom), fill=LINE, width=2); d.text((x, bottom + 30), lab, anchor="ma", fill=TXT, font=font(28))
    d.line((left, bottom, right, bottom), fill=EDGE, width=2); d.line((left, bottom, left, top), fill=EDGE, width=2)
    d.text((left, top - 16), f"{START}.01~{ENDW.year}.{ENDW.month:02d}", anchor="ls", fill="#8a8a8a", font=font(32))
    hy = bottom - P / y_top * (bottom - top)
    d.line((left, hy, right, hy), fill="#ffffff", width=4)
    d.multiline_text((left - 18, hy - 6), f"은퇴 원금\n{dol(P)}", anchor="rd", align="right", spacing=2, fill="#ffffff", font=font(25, True))

    def to_xy(pts):
        return [(left + (a - X0) / (END_X - X0) * (right - left), max(top, bottom - b / y_top * (bottom - top))) for a, b in pts]
    live = []
    for tk, ty, col, S in DATA:
        cp = clipd(S["nav"], clip_end)
        if len(cp) < 2: live.append((tk, ty, col, 0.0)); continue
        xy = to_xy(cp); d.line(xy, fill=col, width=8, joint="curve")
        ex, ey = xy[-1]; d.ellipse((ex - 11, ey - 11, ex + 11, ey + 11), outline=col, width=5, fill="#000000")
        cur_min = min(v for _, v in cp); live.append((tk, ty, col, 1 - cur_min / P))
    lf, vf = font(32), font(40, True)
    for i, (tk, ty, col, dd) in enumerate(live):
        yy = bottom + 132 + i * 60
        d.rounded_rectangle((190, yy - 7, 230, yy + 7), 4, fill=col)
        d.text((252, yy), f"{tk} ({ty})", anchor="lm", fill="#dddddd", font=lf)
        d.text((938, yy), f"최저 -{round(dd*100)}%", anchor="rm", fill="#f5f5f5", font=vf)
    d.text((72, 1712), f"원금 {dol(P)} · 월 {dol(MO)} 인출(물가연동) · 배당세 15%", fill="#666666", font=font(25))
    d.text((984, 1710), "번외 · 1/2", anchor="ra", fill="#777777", font=font(28))
    return im


def render_table():
    im = Image.new("RGB", (W, REEL_H), "#000000"); d = ImageDraw.Draw(im)
    d.multiline_text((W // 2, 230), f"{START}년 고점 은퇴\n하락장 방어력", fill="#f5f5f5", font=font(58, True), spacing=8, anchor="ma", align="center")
    d.text((W // 2, 430), f"{dol(P)} · 월 {dol(MO)} 인출 · {START}.01~{ENDW.year}.{ENDW.month:02d}", fill="#9a9a9a", font=font(30), anchor="ma")
    cxs = {2: [520, 830], 3: [430, 660, 890]}.get(len(STOCKS), [W // 2]); ty = 560
    for (tk, tyname, col), cx in zip(STOCKS, cxs):
        d.text((cx, ty), tk, anchor="mm", fill=col, font=font(42, True)); d.text((cx, ty + 48), tyname, anchor="mm", fill="#8a8a8a", font=font(27))
    d.line((90, ty + 66, 1000, ty + 66), fill=EDGE, width=2)
    rows = [("구간 최저점", [usd(D[3]["mn"]) for D in DATA], [D[3]["mn"] for D in DATA]),
            ("최저 낙폭", [f"-{round(D[3]['dd']*100)}%" for D in DATA], [-D[3]["dd"] for D in DATA])]
    for i, (lab, vals, cmp) in enumerate(rows):
        ry = ty + 150 + i * 150; best = max(range(len(STOCKS)), key=lambda k: cmp[k])
        d.text((100, ry), lab, anchor="lm", fill="#cfcfcf", font=font(40))
        for k, (cx, (tk, tyn, col)) in enumerate(zip(cxs, STOCKS)):
            d.text((cx, ry), vals[k], anchor="mm", fill=col, font=font(50, True))
            if k == best: d.text((cx, ry + 52), "▲ 방어", anchor="mm", fill=col, font=font(28, True))
        if i < 1: d.line((90, ry + 72, 1000, ry + 72), fill="#161616", width=2)
    py = ty + 150 + 2 * 150 + 30
    rank = " > ".join(D[1] for D in sorted(DATA, key=lambda D: D[3]["dd"]))
    d.multiline_text((W // 2, py), f"은퇴 직후 하락장 방어력\n{rank}", fill="#f5f5f5", font=font(38, True), spacing=12, anchor="ma", align="center")
    d.multiline_text((W // 2, py + 150), "낙폭이 깊을수록 바닥에서 더 팔아 없애\n회복장이 와도 되돌리기 어렵다", fill="#9a9a9a", font=font(30), spacing=8, anchor="ma", align="center")
    d.text((72, 1712), f"원금 {dol(P)} · 월 {dol(MO)} 인출·물가연동 · 과거 데이터 백테스트", fill="#666666", font=font(23))
    d.text((984, 1710), "번외 · 2/2", anchor="ra", fill="#777777", font=font(28))
    return im


def main():
    render(999).save(EXPORTS / f"retirestocks_{START}.png")
    for tk, ty, col, S in DATA: print(f"{tk}: 최저 {dol(S['mn'])} (-{round(S['dd']*100)}%)")
    base = EXPORTS / f"retirestocks_{START}_reel.mp4"
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
    framed = EXPORTS / f"retirestocks_{START}_reel_top100px.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(base), "-vf", "scale=960:1820:flags=lanczos,pad=1080:1920:60:50:black",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(framed)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("reel →", framed)


if __name__ == "__main__":
    main()
