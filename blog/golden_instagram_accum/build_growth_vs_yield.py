#!/usr/bin/env python3
"""번외: 배당성장 vs 고배당 — 같은 돈을 두 유형에 넣었을 때 배당·원금의 갈림.

배당성장주(SCHD 등)와 고배당주(QYLD 등)에 같은 금액을 넣고 보유(재투자 X, 배당은 현금).
  · ① 연 배당금: 고배당은 높게 시작하나 정체·감소, 배당성장은 낮게 시작해 매년 상승 → 추월
  · ② 원금(주가) 평가액: 고배당은 NAV 침식, 배당성장은 성장
2패널 애니 릴 + 2페이지 요약표(연배당·누적배당·원금·총자산).

사용: PAIR=SCHD_QYLD python3 build_growth_vs_yield.py
출력: exports/<pref>_gvy.png · exports/<pref>_gvy_reel(_top100px).mp4
"""
import os, math, subprocess
from datetime import date
from pathlib import Path
import yfinance as yf
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent; EXPORTS = ROOT / "exports"
PAIR = os.environ.get("PAIR", "SCHD_QYLD").upper()
PAIRS = {
    "SCHD_QYLD": dict(g="SCHD", y="QYLD", gname="SCHD", yname="QYLD", start=2014, amount=10000, pref="schd_qyld"),
    "SCHD_JEPI": dict(g="SCHD", y="JEPI", gname="SCHD", yname="JEPI", start=2021, amount=10000, pref="schd_jepi"),
}[PAIR]
GTK, YTK, GNAME, YNAME, START, AMT, PREFIX = (PAIRS["g"], PAIRS["y"], PAIRS["gname"], PAIRS["yname"],
                                              PAIRS["start"], PAIRS["amount"], PAIRS["pref"])
TAX = 0.15
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
def font(s, b=False): return ImageFont.truetype(BOLD if b else FONT, s)
def ease(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)
def usd(v): return f"${v/1e6:.2f}M" if v >= 1e6 else (f"${v/1e3:.0f}K" if v >= 1e4 else f"${v:,.0f}")
def dol(v): return f"${v:,.0f}"

GREEN, GOLD, TXT, LINE, EDGE = "#4ade80", "#fbbf24", "#b3b3b3", "#242424", "#3a3a3a"
W, H, FPS = 1080, 1920, 30
HOOK, REVEAL, GSEC = 2.0, 16.0, 20.0
ax0, ay0, ax1, ay1 = 180, 556, 980, 846
bx0, by0, bx1, by1 = 180, 990, 980, 1280


def yr(d):
    y0 = date(d.year, 1, 1); y1 = date(d.year + 1, 1, 1); return d.year + (d - y0).days / (y1 - y0).days


def load(tk):
    t = yf.Ticker(tk); h = t.history(start=f"{START-1}-06-01", end="2026-07-31", auto_adjust=False)
    h.index = h.index.tz_localize(None); c = h["Close"].dropna(); c = c[c.index.year >= START]
    dv = t.dividends; dv.index = dv.index.tz_localize(None); dv = dv[dv.index >= c.index[0]]
    p0 = c.iloc[0]; sh = AMT / p0
    ann = {}; cum = 0.0
    for d, v in dv.items(): ann[d.year] = ann.get(d.year, 0) + sh * float(v) * (1 - TAX); cum += sh * float(v) * (1 - TAX)
    nav = [(yr(d.date()), sh * px) for d, px in c.items()]
    return dict(ann=ann, cum=cum, nav=nav, nav_now=sh * c.iloc[-1], sh=sh, x0=yr(c.index[0].date()), xend=yr(c.index[-1].date()))


G = load(GTK); Y = load(YTK)
X0 = min(G["x0"], Y["x0"]); END_X = max(G["xend"], Y["xend"])
YEARS = sorted(set(y for y in range(START, 2026) if y in G["ann"] and y in Y["ann"]))
LASTY = YEARS[-1]
def nc(x):
    e = 10 ** math.floor(math.log10(x)); f = x / e
    for n in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if f <= n: return int(n * e)
    return int(10 * e)
yaA = nc(max(max(G["ann"].values()), max(Y["ann"].values())) * 1.12)
yaB = nc(max(G["nav_now"], AMT, max(v for _, v in G["nav"])) * 1.08)
CROSS = next((y for y in YEARS if G["ann"][y] > Y["ann"][y]), None)   # 연배당 추월 연도


def clipd(pts, lim):
    out = []
    for i, p in enumerate(pts):
        if p[0] <= lim: out.append(p); continue
        if out:
            pr = pts[i - 1]; sp = p[0] - pr[0]
            if sp > 0: r = max(0, min(1, (lim - pr[0]) / sp)); out.append((lim, pr[1] + (p[1] - pr[1]) * r))
        break
    return out


def render(tt):
    im = Image.new("RGB", (W, H), "#000000"); d = ImageDraw.Draw(im)
    d.multiline_text((W // 2, 290), f"배당성장 vs 고배당\n{GNAME} vs {YNAME} · {dol(AMT)} ({START}년~)",
                     fill="#f5f5f5", font=font(56, True), spacing=6, anchor="ma", align="center")
    prog = 1.0 if tt < HOOK else ease((tt - HOOK) / REVEAL); rev = X0 + (END_X - X0) * prog
    # 패널 A: 연 배당금 막대(G 초록=배당성장, Y 금색=고배당)
    d.text((ax0, ay0 - 62), "① 연 배당금", fill="#eaeaea", font=font(36, True))
    for i in range(3):
        v = yaA * i / 2; y = ay1 - (ay1 - ay0) * i / 2; d.line((ax0, y, ax1, y), fill=LINE, width=2)
        d.text((ax0 - 14, y), (usd(v) if v > 0 else "0"), anchor="rm", fill=TXT, font=font(26))
    n = len(YEARS); slot = (ax1 - ax0) / n; bw = slot * 0.34
    for i, yv in enumerate(YEARS):
        fr = ease(max(0., min(1., rev - yv)))
        if fr <= 0: continue
        xc = ax0 + slot * (i + 0.5)
        for val, col, off in [(Y["ann"][yv], GOLD, -bw * 0.55), (G["ann"][yv], GREEN, bw * 0.55)]:
            bh = (ay1 - ay0) * val / yaA * fr
            if bh > 0: d.rectangle((xc + off - bw / 2, ay1 - bh, xc + off + bw / 2, ay1), fill=col)
        if yv % 3 == 0 or yv == YEARS[-1]: d.text((xc, ay1 + 8), f"{yv}", anchor="ma", fill=TXT, font=font(23))
    d.line((ax0, ay1, ax1, ay1), fill=EDGE, width=2)
    # 패널 B: 원금(주가) 평가액 라인 + 투자원금 기준선
    d.text((bx0, by0 - 62), "② 원금(주가) 평가액", fill="#eaeaea", font=font(36, True))
    for i in range(3):
        v = yaB * i / 2; y = by1 - (by1 - by0) * i / 2; d.line((bx0, y, bx1, y), fill=LINE, width=2)
        d.text((bx0 - 14, y), (usd(v) if v > 0 else "0"), anchor="rm", fill=TXT, font=font(26))
    for i in range(5):
        yv = X0 + (END_X - X0) * i / 4; x = bx0 + (bx1 - bx0) * i / 4
        d.line((x, by0, x, by1), fill=LINE, width=2); d.text((x, by1 + 8), f"{yv:.0f}", anchor="ma", fill=TXT, font=font(24))
    d.line((bx0, by1, bx1, by1), fill=EDGE, width=2)
    BX = lambda y: bx0 + (y - X0) / (END_X - X0) * (bx1 - bx0)
    BY = lambda v: by1 - v / yaB * (by1 - by0)
    ar = bx0 + (bx1 - bx0) * prog
    by_ref = BY(AMT)
    # 투자원금 점선
    rem = 14; dr = True; x = bx0
    while x < ar:
        seg = min(14 if dr else 10, ar - x)
        if dr: d.line((x, by_ref, x + seg, by_ref), fill="#666666", width=3)
        x += seg; dr = not dr
    d.multiline_text((bx0 - 14, by_ref - 6), f"투자원금\n{dol(AMT)}", anchor="rd", align="right", spacing=2, fill="#9a9a9a", font=font(22, True))
    live = []
    for s, col in [(G, GREEN), (Y, GOLD)]:
        cp = clipd(s["nav"], rev)
        if len(cp) >= 2:
            xy = [(BX(a), BY(b)) for a, b in cp]; d.line(xy, fill=col, width=6, joint="curve")
            live.append(cp[-1][1])
        else: live.append(AMT)
    # 동적 범례: 유형 · 연배당 · 원금(라이브)
    cur_y = max([y for y in YEARS if y <= rev], default=YEARS[0])
    for i, (nm, sub, col, ann, nav) in enumerate([(GNAME, "배당성장", GREEN, G["ann"][cur_y], live[0]),
                                                  (YNAME, "고배당", GOLD, Y["ann"][cur_y], live[1])]):
        yy = 1400 + i * 62
        d.rounded_rectangle((bx0, yy - 7, bx0 + 40, yy + 7), 4, fill=col)
        d.text((bx0 + 52, yy), f"{nm} ({sub})", anchor="lm", fill="#dddddd", font=font(30))
        d.text((bx1, yy), f"연배당 {dol(ann)} · 원금 {dol(nav)}", anchor="rm", fill=col, font=font(29, True))
    d.text((984, 1710), "번외 · 1/2", anchor="ra", fill="#777777", font=font(28))
    return im


def render_table():
    im = Image.new("RGB", (W, H), "#000000"); d = ImageDraw.Draw(im)
    d.multiline_text((W // 2, 220), f"{START}년 {dol(AMT)}, {LASTY - START + 1}년 뒤", fill="#f5f5f5", font=font(58, True), spacing=8, anchor="ma", align="center")
    d.text((W // 2, 380), "배당성장 vs 고배당 · 배당 현금수령 · 세후", fill="#9a9a9a", font=font(32), anchor="ma")
    cx0, cx1, cx2 = 250, 660, 910; ty = 540
    d.text((cx1, ty), f"{GNAME}", anchor="mm", fill=GREEN, font=font(36, True)); d.text((cx1, ty + 40), "배당성장", anchor="mm", fill="#8a8a8a", font=font(24))
    d.text((cx2, ty), f"{YNAME}", anchor="mm", fill=GOLD, font=font(36, True)); d.text((cx2, ty + 40), "고배당", anchor="mm", fill="#8a8a8a", font=font(24))
    d.line((150, ty + 70, 950, ty + 70), fill=EDGE, width=2)
    rows = [("연 배당금 (현재)", G["ann"][LASTY], Y["ann"][LASTY]),
            ("누적 배당금", G["cum"], Y["cum"]),
            ("원금 평가액", G["nav_now"], Y["nav_now"]),
            ("총자산 (원금+배당)", G["cum"] + G["nav_now"], Y["cum"] + Y["nav_now"])]
    for i, (lab, gv, yv) in enumerate(rows):
        ry = ty + 140 + i * 130; win = gv >= yv
        d.text((150, ry), lab, anchor="lm", fill="#cfcfcf", font=font(31))
        d.text((cx1, ry), dol(gv), anchor="mm", fill=GREEN, font=font(40, True))
        d.text((cx2, ry), dol(yv), anchor="mm", fill=GOLD, font=font(40, True))
        d.text((cx1 if win else cx2, ry + 42), "▲ 우위", anchor="mm", fill=(GREEN if win else GOLD), font=font(22, True))
        if i < 3: d.line((150, ry + 65, 950, ry + 65), fill="#161616", width=2)
    py = ty + 140 + 4 * 130 + 40
    d.multiline_text((W // 2, py), "고배당은 받은 배당 총액이 많지만\n배당성장은 연배당 추월 + 원금·총자산 압도", fill="#f5f5f5", font=font(36, True), spacing=10, anchor="ma", align="center")
    d.text((72, 1712), f"{START}년 {dol(AMT)} 매수·보유 · 재투자X · 배당세 15% · 과거 데이터", fill="#666666", font=font(24))
    d.text((984, 1710), "번외 · 2/2", anchor="ra", fill="#777777", font=font(28))
    return im


def main():
    render(999).save(EXPORTS / f"{PREFIX}_gvy.png")
    print(f"{GNAME} 연배당 {dol(G['ann'][LASTY])}/누적 {dol(G['cum'])}/원금 {dol(G['nav_now'])} | {YNAME} 연배당 {dol(Y['ann'][LASTY])}/누적 {dol(Y['cum'])}/원금 {dol(Y['nav_now'])} | 추월 {CROSS}")
    base = EXPORTS / f"{PREFIX}_gvy_reel.mp4"
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
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
    framed = EXPORTS / f"{PREFIX}_gvy_reel_top100px.mp4"
    subprocess.run(["ffmpeg", "-y", "-i", str(base), "-vf", "scale=960:1820:flags=lanczos,pad=1080:1920:60:50:black",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(framed)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("reel →", framed)


if __name__ == "__main__":
    main()
