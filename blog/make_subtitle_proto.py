# -*- coding: utf-8 -*-
"""자막 프로토타입 PNG 1장 생성 — 밝은 배경/어두운 배경 두 규칙 비교."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
PANEL_H = H // 2

FONT_PATH = "/home/zealatan/.fonts/NotoSansKR-Bold.otf"
LABEL_FONT = "/home/zealatan/.fonts/NotoSansKR.otf"
font = ImageFont.truetype(FONT_PATH, 52)
label_font = ImageFont.truetype(LABEL_FONT, 26)

img = Image.new("RGB", (W, H))
draw = ImageDraw.Draw(img)

# ── 배경: 위=밝은 슬라이드(크림), 아래=어두운 슬라이드(네이비) ──
def vgrad(y0, y1, c0, c1):
    for y in range(y0, y1):
        t = (y - y0) / (y1 - y0)
        r = int(c0[0] + (c1[0]-c0[0])*t)
        g = int(c0[1] + (c1[1]-c0[1])*t)
        b = int(c0[2] + (c1[2]-c0[2])*t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

vgrad(0, PANEL_H, (247, 243, 233), (231, 223, 205))          # 밝은 배경
vgrad(PANEL_H, H, (18, 24, 38), (10, 14, 24))                # 어두운 배경

def rounded_bar(base, cx_top, box_rgba, text, text_rgb, accent=None):
    """자막용 기다란 라운드 박스 + 텍스트를 base 이미지에 합성."""
    # 박스 크기 (16:9 프레임 하단 안전영역 감성)
    margin_x = 150
    bw = W - margin_x * 2
    bh = 83   # 기존 118에서 30% 축소
    # 박스 하단을 패널 하단에서 약간 띄움
    by1 = cx_top + PANEL_H - 70
    by0 = by1 - bh
    bx0, bx1 = margin_x, W - margin_x
    radius = 0  # 각진 사각형

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle([bx0, by0, bx1, by1], radius=radius, fill=box_rgba)
    base.alpha_composite(overlay)

    d = ImageDraw.Draw(base)
    tb = d.textbbox((0, 0), text, font=font)
    tw, th = tb[2]-tb[0], tb[3]-tb[1]
    tx = (W - tw) // 2
    ty = by0 + (bh - th) // 2 - tb[1]
    d.text((tx, ty), text, font=font, fill=text_rgb)

base = img.convert("RGBA")

# 밝은 배경 → 어두운 박스 + 밝은 글씨
rounded_bar(base, 0,
            box_rgba=(14, 20, 32, 214),
            text="워런 버핏이 평생 팔지 않은 종목, 바로 코카콜라입니다.",
            text_rgb=(244, 247, 251))

# 어두운 배경 → 밝은 박스 + 어두운 글씨
rounded_bar(base, PANEL_H,
            box_rgba=(245, 247, 251, 235),
            text="같은 종목에 투자했는데도 결과는 이렇게 크게 달라졌습니다.",
            text_rgb=(18, 21, 27))

# ── 코너 라벨 ──
d = ImageDraw.Draw(base)
d.text((40, 30), "밝은 배경 · 어두운 박스 + 밝은 글씨", font=label_font, fill=(120, 110, 90))
d.text((40, PANEL_H + 30), "어두운 배경 · 밝은 박스 + 어두운 글씨", font=label_font, fill=(150, 160, 180))
# 중앙 구분선
d.line([(0, PANEL_H), (W, PANEL_H)], fill=(90, 90, 90), width=2)

base.convert("RGB").save("subtitle_proto.png", "PNG")
print("saved subtitle_proto.png")
