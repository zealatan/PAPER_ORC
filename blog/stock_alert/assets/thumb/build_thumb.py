#!/usr/bin/env python3
"""
stock_alert 롱폼 썸네일 (2026년 30주차 — 전고점 대비 최대 낙폭 랭킹)
1280x720 PNG, PIL 합성. 배투실 마스코트+BlackHanSans 헤드라인+실제 백테스트 낙폭 차트.
숫자 출처: blog/stock_alert/data/week1.json (weekly_scan.py 실측)
  - Kolon TissueGene(950160.KQ): high 112,900(2026-06-17) -> 15,000(2026-07-24) = -86.71%
  - LG전자(066570.KS): high 392,500(2026-06-02) -> 169,200 = -56.89%
  - 미래에셋증권(006800.KS): high 83,800(2026-05-06) -> 36,900 = -55.97%
"""
import json
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
ROOT = "/home/messi/PAPER_ORC/blog"
FONT_HEAD = f"{ROOT}/fonts/BlackHanSans-Regular.ttf"
FONT_CHIP = "/usr/share/fonts/truetype/nanum/NanumSquareRoundB.ttf"
FONT_CHIP2 = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
MASCOT = f"{ROOT}/stock_alert/assets/shorts/batusil_label.png"
DATA = f"{ROOT}/stock_alert/data/week1.json"
OUT = f"{ROOT}/stock_alert/assets/thumb/thumb_week30.png"

RED = (224, 38, 32)
RED_BRIGHT = (255, 56, 48)
YELLOW = (255, 205, 32)
CREAM = (238, 226, 197)
KRAFT = (210, 182, 138)
KRAFT_DK = (94, 68, 40)
WHITE = (255, 255, 255)
BLACK = (10, 8, 8)


def font(path, size):
    return ImageFont.truetype(path, size)


def text_outline(draw, xy, text, f, fill, outline, ow, anchor="la", spacing=0):
    x, y = xy
    for dx in range(-ow, ow + 1):
        for dy in range(-ow, ow + 1):
            if dx * dx + dy * dy <= ow * ow:
                draw.text((x + dx, y + dy), text, font=f, fill=outline, anchor=anchor)
    draw.text((x, y), text, font=f, fill=fill, anchor=anchor)


def rounded_poly_rect(draw, box, radius, fill, outline=None, width=0, rotate=0, center=None):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([4, 4, w + 4, h + 4], radius=radius, fill=fill, outline=outline, width=width)
    if rotate:
        layer = layer.rotate(rotate, resample=Image.BICUBIC, expand=True)
    return layer


def paste_rot(base, layer, cx, cy):
    lw, lh = layer.size
    base.alpha_composite(layer, (int(cx - lw / 2), int(cy - lh / 2)))


def torn_paper(size, base_color, edge_color, jag=6, seed=0):
    """찢긴 종이 태그 텍스처 (사각형 + 톱니 가장자리)"""
    w, h = size
    pad = jag * 2
    layer = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    import random
    rnd = random.Random(seed)
    pts = []
    steps = 14
    # top edge
    for i in range(steps + 1):
        x = pad + i * w / steps
        y = pad + rnd.uniform(-jag, jag)
        pts.append((x, y))
    # right edge
    for i in range(1, steps + 1):
        y = pad + i * h / steps
        x = pad + w + rnd.uniform(-jag, jag)
        pts.append((x, y))
    # bottom edge
    for i in range(1, steps + 1):
        x = pad + w - i * w / steps
        y = pad + h + rnd.uniform(-jag, jag)
        pts.append((x, y))
    # left edge
    for i in range(1, steps + 1):
        y = pad + h - i * h / steps
        x = pad + rnd.uniform(-jag, jag)
        pts.append((x, y))
    d.polygon(pts, fill=base_color)
    return layer


def make_bg():
    img = Image.new("RGB", (W, H), (8, 8, 12))
    px = img.load()
    for y in range(H):
        t = y / H
        # dark navy-black top -> warm dark red-black bottom
        r = int(10 + t * 26)
        g = int(9 + t * 6)
        b = int(16 + t * 6 - t * 10)
        b = max(8, b)
        for x in range(0, W, 1):
            pass
        for x in range(W):
            px[x, y] = (r, g, b)
    img = img.filter(ImageFilter.GaussianBlur(0))
    return img.convert("RGBA")


def add_grid(base):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    step = 64
    col = (200, 40, 40, 16)
    for x in range(0, W, step):
        d.line([(x, 0), (x, int(H * 0.62))], fill=col, width=1)
    for y in range(0, int(H * 0.62), step):
        d.line([(0, y), (W, y)], fill=col, width=1)
    base.alpha_composite(layer)


def add_vignette(base):
    layer = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(layer)
    d.ellipse([-260, -260, W + 260, H + 180], fill=255)
    layer = layer.filter(ImageFilter.GaussianBlur(180))
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 235))
    inv = Image.eval(layer, lambda p: 255 - p)
    dark.putalpha(inv)
    base.alpha_composite(dark)


def draw_crash_chart(base):
    """실제 950160.KQ 데이터(week1.json pts idx69-83) 기반 폭락 라인차트를 대각선으로 확대."""
    d = json.load(open(DATA, encoding="utf-8"))
    kolon = d["markets"]["한국"][0]
    pts_all = kolon["pts"]
    seg = pts_all[66:84]  # 랠리 -> 절벽 낙하 구간
    vals = [p[1] for p in seg]
    vmin, vmax = min(vals), max(vals)

    x0, x1 = 470, 1250
    y0, y1 = 96, 452
    n = len(vals)
    coords = []
    for i, v in enumerate(vals):
        x = x0 + (x1 - x0) * (i / (n - 1))
        norm = (v - vmin) / (vmax - vmin + 1e-9)
        y = y1 - norm * (y1 - y0) * 0.94
        coords.append((x, y))

    # glow layer
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line(coords, fill=(255, 40, 30, 230), width=14, joint="curve")
    for c in coords:
        gd.ellipse([c[0] - 6, c[1] - 6, c[0] + 6, c[1] + 6], fill=(255, 40, 30, 230))
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    base.alpha_composite(glow)

    # fill under line (loss area)
    fill_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fill_layer)
    poly = coords + [(x1, y1 + 140), (x0, y1 + 140)]
    fd.polygon(poly, fill=(200, 30, 24, 70))
    base.alpha_composite(fill_layer)

    # crisp line
    line = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(line)
    ld.line(coords, fill=(255, 236, 230, 255), width=5, joint="curve")
    ld.line(coords, fill=(255, 70, 58, 255), width=3, joint="curve")
    base.alpha_composite(line)

    peak_i = vals.index(vmax)
    peak = coords[peak_i]
    cur = coords[-1]

    d2 = ImageDraw.Draw(base)
    # peak marker
    d2.ellipse([peak[0] - 9, peak[1] - 9, peak[0] + 9, peak[1] + 9], fill=WHITE, outline=BLACK, width=2)
    # current marker (pulsing red)
    for rr, aa in [(26, 60), (18, 110), (10, 255)]:
        d2.ellipse([cur[0] - rr, cur[1] - rr, cur[0] + rr, cur[1] + rr],
                   fill=(255, 40, 30, aa) if rr != 10 else (255, 60, 50, 255))

    return peak, cur, kolon


def draw_down_arrow(base, cx, cy, s, alpha=46):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts = [
        (cx - s * 0.30, cy - s * 0.95), (cx + s * 0.30, cy - s * 0.95),
        (cx + s * 0.30, cy + s * 0.05), (cx + s * 0.62, cy + s * 0.05),
        (cx, cy + s * 0.62), (cx - s * 0.62, cy + s * 0.05),
        (cx - s * 0.30, cy + s * 0.05),
    ]
    d.polygon(pts, fill=(255, 30, 24, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    base.alpha_composite(layer)


def pill(draw_base, x, y, text, f, fg, bg, pad_x=16, pad_y=8, outline=None):
    tb = draw_base_font_bbox(f, text)
    w = tb[2] - tb[0] + pad_x * 2
    h = tb[3] - tb[1] + pad_y * 2
    layer = Image.new("RGBA", (w + 6, h + 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([3, 3, w + 3, h + 3], radius=h // 2, fill=bg, outline=outline, width=2 if outline else 0)
    d.text((3 + pad_x - tb[0], 3 + pad_y - tb[1]), text, font=f, fill=fg)
    return layer, w + 6, h + 6


def draw_base_font_bbox(f, text):
    dummy = Image.new("RGBA", (4, 4))
    dd = ImageDraw.Draw(dummy)
    return dd.textbbox((0, 0), text, font=f)


def brush_label(base, cx, cy, text, f, rotate=-3, fg=WHITE, bg=RED, w_pad=28, h_pad=14):
    tb = draw_base_font_bbox(f, text)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    w, h = int(tw + w_pad * 2), int(th + h_pad * 2)
    layer = Image.new("RGBA", (w + 10, h + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # brush-stroke-ish rounded rect w/ ragged ends
    d.rounded_rectangle([5, 5, w + 5, h + 5], radius=h // 3, fill=bg)
    d.text((5 + w_pad - tb[0], 5 + h_pad - tb[1]), text, font=f, fill=fg)
    layer = layer.rotate(rotate, resample=Image.BICUBIC, expand=True)
    paste_rot(base, layer, cx, cy)


def main():
    base = make_bg()
    add_grid(base)

    # big soft down-arrow watermark behind chart (single, subtle, tucked into right side)
    draw_down_arrow(base, 1100, 300, 460, alpha=22)

    peak, cur, kolon = draw_crash_chart(base)

    add_vignette(base)

    d = ImageDraw.Draw(base)

    # ---- top-left torn kraft tag ----
    tag = torn_paper((300, 66), KRAFT, KRAFT_DK, jag=7, seed=3)
    tag = tag.rotate(-4, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(tag, (14, 14))
    f_tag = font(FONT_CHIP, 30)
    tb = draw_base_font_bbox(f_tag, "이번 주 낙폭 랭킹")
    d.text((14 + 300 / 2 - (tb[2] - tb[0]) / 2 - tb[0] - 4, 14 + 66 / 2 - (tb[3] - tb[1]) / 2 - tb[1] + 8),
           "이번 주 낙폭 랭킹", font=f_tag, fill=(40, 26, 12))

    # ---- top-center week badge + market pills ----
    f_week = font(FONT_CHIP, 30)
    wl, ww, wh = pill(d, 0, 0, "2026년 · 30주차", f_week, WHITE, RED)
    base.alpha_composite(wl, (int(W / 2 - ww / 2), 16))

    f_pill = font(FONT_CHIP2, 22)
    markets = [("ETF", (40, 110, 190)), ("미국", (150, 30, 30)), ("한국", (30, 60, 140)), ("유럽", (60, 40, 130))]
    total_w = 0
    pills = []
    for name, col in markets:
        pl, pw, ph = pill(d, 0, 0, name, f_pill, WHITE, (*col, 235), pad_x=14, pad_y=6)
        pills.append((pl, pw, ph))
        total_w += pw + 10
    sx = int(W / 2 - total_w / 2)
    py = 16 + wh + 10
    for pl, pw, ph in pills:
        base.alpha_composite(pl, (sx, py))
        sx += pw + 10

    # ---- mascot watermark top-right ----
    mascot = Image.open(MASCOT).convert("RGBA")
    mw = 108
    mh = int(mascot.height * mw / mascot.width)
    mascot_s = mascot.resize((mw, mh), Image.LANCZOS)
    plate = Image.new("RGBA", (mw + 20, mh + 20), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plate)
    pd.rounded_rectangle([0, 0, mw + 20, mh + 20], radius=18, fill=(10, 8, 8, 150))
    plate.alpha_composite(mascot_s, (10, 10))
    base.alpha_composite(plate, (W - mw - 34, 14))

    # ---- ticker citation chip near current point ----
    f_chip = font(FONT_CHIP, 25)
    label = f"코오롱티슈진(950160)  {kolon['drawdown_pct']:.1f}%"
    cl, cw, ch = pill(d, 0, 0, label, f_chip, WHITE, (150, 20, 18, 235))
    cx = min(max(int(cur[0] - cw / 2), 470), W - cw - 20)
    cy = min(int(cur[1] + 26), 470)
    base.alpha_composite(cl, (cx, cy))
    f_small = font(FONT_CHIP2, 19)
    d.text((cx + cw / 2, cy + ch + 4), "전고점 대비 (2026-06-17 -> 07-24)", font=f_small,
           fill=(235, 200, 190), anchor="ma")

    f_peak = font(FONT_CHIP2, 20)
    text_outline(d, (peak[0], peak[1] - 26), "전고점", f_peak, WHITE, BLACK, 2, anchor="mb")

    # ---- red brush caption above headline ----
    f_brush = font(FONT_CHIP, 34)
    brush_label(base, 300, 410, "이번 주 최대 낙폭은?", f_brush, rotate=-2)

    # ---- bottom scrim ----
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    top_y = 372
    for y in range(top_y, H):
        t = (y - top_y) / (H - top_y)
        a = int(255 * min(1.0, t * 1.5))
        sd.line([(0, y), (W, y)], fill=(4, 3, 3, a))
    base.alpha_composite(scrim)

    # ---- headline ----
    f_h1 = font(FONT_HEAD, 96)
    f_h2 = font(FONT_HEAD, 150)

    text_outline(d, (44, 452), "전고점 대비", f_h1, WHITE, BLACK, 9, anchor="la")
    text_outline(d, (40, 536), "-87%?!", f_h2, YELLOW, BLACK, 11, anchor="la")

    f_sub = font(FONT_CHIP, 30)
    text_outline(d, (W - 40, 648), "이번 주 낙폭 TOP5 총정리", f_sub, WHITE, BLACK, 5, anchor="ra")

    base.convert("RGB").save(OUT, quality=95)
    print("saved", OUT)


if __name__ == "__main__":
    main()
