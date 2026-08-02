#!/usr/bin/env python3
"""적립 vs 폭락매수 인스타 릴(1080x1920).

golden_instagram_fire 파이프라인 이식 — 검증된 프레이밍/동적라벨/충돌방지 재사용,
데이터 모델만 4선(적립원금 점선·매수원금 점선 + 적립평가·매수평가 solid)으로 개조.

사용: SHORTS_STOCK=QQQ [ACCUM_THR=30] [INSTA_STAMP=0] python3 build_instagram_accum.py
데이터: assets/data/<prefix>_accum.json (gen_accum.py 산출)
"""
import json
import math
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

STOCK = os.environ.get("SHORTS_STOCK", "QQQ").upper()
THR = int(os.environ.get("ACCUM_THR", "30"))
PREFIX = {"QQQ": "qqq", "PG": "pg", "SKH": "skh", "SEC": "sec"}.get(STOCK, STOCK.lower())
NAME = {"QQQ": "나스닥 100 (QQQ)", "SKH": "SK하이닉스", "SEC": "삼성전자",
        "PG": "P&G"}.get(STOCK, STOCK)

ROOT = Path(__file__).resolve().parent
EXPORTS = ROOT / "exports"
OUT = EXPORTS / f"{PREFIX}_accum_reel.mp4"
DATA_FILE = ROOT / f"assets/data/{PREFIX}_accum.json"
ENTRY = next(e for e in json.loads(DATA_FILE.read_text()) if e["thr"] == THR)
KRW = bool(ENTRY.get("krw"))
RAW = ENTRY["payload"]["lines"]          # 4선(순서: 적립원금·매수원금·적립평가·매수평가)
LEGEND = ENTRY["payload"]["legend"]      # [{c,label 적립}, {c,label 매수}]
MONTHLY = ENTRY["monthly"]
X0 = int(RAW[0]["pts"][0][0])
END_X = max(l["pts"][-1][0] for l in RAW)

W, REEL_H, FPS = 1080, 1920, 30
BLUE, PINK = "#38bdf8", "#f59e0b"        # 적립=스카이블루, 폭락매수=앰버(B안)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SHOW_STAMP = os.environ.get("INSTA_STAMP", "1") != "0"   # (미사용; 파이어 호환)
HOOK_SECS = 2.0

# 원천 색(#2b6cb0/#c2255c)을 릴 팔레트로 매핑 + 역할 부여
def _role(line):
    color = BLUE if line["c"] == "#2b6cb0" else PINK
    dash = bool(line.get("dash"))
    return {"pts": line["pts"], "color": color, "dash": dash,
            "end": line.get("end"), "strat": "적립" if color == BLUE else "매수"}
LINES = [_role(l) for l in RAW]


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * ease(t)


def clip_points(points, limit):
    out = []
    for i, p in enumerate(points):
        if p[0] <= limit:
            out.append(p)
            continue
        if out:
            prev = points[i - 1]
            span = p[0] - prev[0]
            if span > 0:
                r = max(0.0, min(1.0, (limit - prev[0]) / span))
                out.append([limit, prev[1] + (p[1] - prev[1]) * r])
        break
    return out


def money(v):
    if KRW:
        if v >= 1e8:
            return f"{v / 1e8:.0f}억"
        if v >= 1e4:
            return f"{v / 1e4:.0f}만"
        return "0"
    if v >= 1_000_000:
        return f"${v / 1_000_000:.1f}M"
    return f"${v / 1000:.0f}K"


def monthly_label():
    if KRW:
        return f"{int(MONTHLY / 1e4)}만원"
    return f"${int(MONTHLY):,}"


def _ym(fy):
    y = int(fy)
    return f"{y}.{min(12, int((fy - y) * 12) + 1):02d}"


def draw_dashed(draw, xy, fill, width, on=16, off=12):
    """PIL 점선: 폴리라인을 따라 on/off 길이로 세그먼트를 그린다."""
    remain, drawing = on, True
    for (x0, y0), (x1, y1) in zip(xy, xy[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg == 0:
            continue
        pos = 0.0
        while pos < seg:
            step = min(remain, seg - pos)
            t0, t1 = pos / seg, (pos + step) / seg
            if drawing:
                draw.line((x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0,
                           x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1),
                          fill=fill, width=width)
            pos += step
            remain -= step
            if remain <= 1e-6:
                drawing = not drawing
                remain = on if drawing else off


def header(d):
    # 2줄 흰색 타이틀(가로 중앙).
    cx = W // 2
    line1, line2 = "매달 적립 vs 폭락매수", f"{NAME}, 뭐가 이겼을까?"
    size = 78
    while size > 44 and max(font(size, True).getlength(line1),
                            font(size, True).getlength(line2)) > 1000:
        size -= 2
    tf = font(size, True)
    asc, desc = tf.getmetrics()
    line_h = asc + desc
    ty = 689 - 150 + 18 - (2 * line_h + 5)
    d.multiline_text((cx, ty), f"{line1}\n{line2}", fill="#f5f5f5", font=tf,
                     spacing=5, anchor="ma", align="center")


def axes(draw, box, progress, x_end, y_top):
    # 레퍼런스 감성: 라인은 은은한 어두운 회색, 글자는 그보다 밝은 회색(구분). 굵은 축선 없음.
    LINE, EDGE, TXT = "#242424", "#3a3a3a", "#b3b3b3"
    left, top, right, bottom = box
    axis_right = lerp(left, right, progress)
    for i in range(3):
        value = y_top * i / 2
        y = bottom - (bottom - top) * i / 2
        draw.line((left, y, axis_right, y), fill=LINE, width=2)
        draw.text((left - 18, y), money(value), anchor="rm", fill=TXT, font=font(31))
    x_ids = (0,) if progress < .12 else ((0, 4) if progress < .28 else range(5))
    for i in x_ids:
        year = X0 + (x_end - X0) * i / 4
        x = left + (right - left) * progress * i / 4
        draw.line((x, top, x, bottom), fill=LINE, width=2)
        lab = f"{year:.1f}" if x_end - X0 < 2 else f"{year:.0f}"
        draw.text((x, bottom + 30), lab, anchor="ma", fill=TXT, font=font(30))
    draw.line((left, bottom, axis_right, bottom), fill=EDGE, width=2)
    draw.line((left, bottom, left, top), fill=EDGE, width=2)


def render(t):
    image = Image.new("RGB", (W, REEL_H), "#000000")
    draw = ImageDraw.Draw(image)
    header(draw)

    if t < HOOK_SECS:
        clip_end = END_X
        progress = 1.0
    else:
        s = t - HOOK_SECS
        progress = ease(s / 30.0)   # 리빌 2배 느리게
        clip_end = lerp(X0, END_X, progress)
    axis_progress = progress if t >= HOOK_SECS else 1.0

    # y축: 활성 리빌된 평가액(solid) 최댓값 기준 확장(ALT)
    vis = 1.0
    for ln in LINES:
        if ln["dash"]:
            continue
        vals = [v for _, v in clip_points(ln["pts"], clip_end)]
        if vals:
            vis = max(vis, *vals)
    y_top = vis * 1.08

    box = (164, 660, 964, 1360)   # 그래프 위로(제목 여백 축소)
    axes(draw, box, axis_progress, clip_end, y_top)
    left, top, right, bottom = box
    # 날짜(테스트 기간)는 그래프 왼쪽 상단 위
    period = f"{_ym(X0 + 0.02)}~{_ym(END_X)}"
    draw.text((left, top - 16), period, anchor="ls", fill="#8a8a8a", font=font(32))

    def to_xy(pts):
        return [(left + (yr - X0) / max(clip_end - X0, .0001) * (right - left) * axis_progress,
                 max(top, bottom - val / max(y_top, 1) * (bottom - top))) for yr, val in pts]

    # 점선(누적원금)=은은, solid(평가액)=뚜렷 + 끝점 원형 마커. 값은 하단 범례 옆에.
    results = []   # (strat, color, live_value)
    for ln in sorted(LINES, key=lambda L: L["dash"], reverse=True):
        pts = clip_points(ln["pts"], clip_end)
        if len(pts) < 2:
            continue
        xy = to_xy(pts)
        if ln["dash"]:
            draw_dashed(draw, xy, ln["color"], 3)
        else:
            draw.line(xy, fill=ln["color"], width=9, joint="curve")
            ex, ey = xy[-1]
            draw.ellipse((ex - 12, ey - 12, ex + 12, ey + 12),
                         outline=ln["color"], width=5, fill="#000000")
            final = clip_end >= ln["pts"][-1][0] - .05
            value = ln["end"] if (final and ln["end"]) else money(pts[-1][1])
            results.append((ln["strat"], ln["color"], value))

    # 하단 범례: 스와치 + 전략명 + 값(우측). 그래프와의 여백은 살짝 넉넉히.
    results.sort(key=lambda r: 0 if r[0] == "적립" else 1)
    lf, vff = font(34), font(46, True)
    for i, (strat, color, value) in enumerate(results):
        yy = bottom + 138 + i * 66   # 두 줄 사이 간격 축소
        label = f"매달 {monthly_label()} 적립" if strat == "적립" else f"{THR}% 하락 시 매수"
        draw.rounded_rectangle((190, yy - 7, 230, yy + 7), 4, fill=color)
        draw.text((252, yy), label, anchor="lm", fill="#dddddd", font=lf)
        draw.text((938, yy), value, anchor="rm", fill=color, font=vff)

    tax = "15.4%" if KRW else "15%"
    draw.text((72, 1712), f"{X0}년부터 매달 적립·배당 재투자 · 세금 {tax} 반영",
              fill="#666666", font=font(25))
    draw.text((984, 1710), "1/2", anchor="ra", fill="#777777", font=font(28))
    return image


def main():
    graph_seconds = 40.0   # 2배 느리게(리빌 30s + 후킹/홀드)
    total = round(graph_seconds * FPS)
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{REEL_H}", "-r", str(FPS), "-i", "-", "-an",
           "-c:v", "libx264", "-preset", "slow", "-crf", "16",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert p.stdin
    for frame in range(total):
        payload = memoryview(render(frame / FPS).tobytes())
        while payload:
            n = p.stdin.write(payload)
            payload = payload[n:]
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print("created:", OUT)


if __name__ == "__main__":
    main()
