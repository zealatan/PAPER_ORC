#!/usr/bin/env python3
"""쇼츠 상단 훅 텍스트 오버레이 PNG 생성 (1080폭, 투명).
   상단: STOCK_ALERT 로고(빨간 script) → 그 아래 훅 문구 1행 흰색 + 2행 노란 하이라이트."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.join(os.path.dirname(__file__), '..')
FONT = os.path.join(ROOT, 'fonts', 'BlackHanSans-Regular.ttf')
OUT = os.path.join(ROOT, 'assets', 'shorts')
LOGO = os.path.join(OUT, 'stock_alert_logo.png')
os.makedirs(OUT, exist_ok=True)

W = 1080
YELLOW = (255, 216, 61)
INK = (28, 24, 20)
WHITE = (248, 248, 245)

def draw_text_center(dr, cy, text, font, fill, stroke=0, stroke_fill=(0,0,0)):
    bbox = dr.textbbox((0,0), text, font=font, stroke_width=stroke)
    tw = bbox[2]-bbox[0]; th = bbox[3]-bbox[1]
    x = (W - tw)//2 - bbox[0]; y = cy - th//2 - bbox[1]
    dr.text((x, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)

def make(fname, line1, line2, s1=60, s2=96):
    H = 380
    img = Image.new('RGBA', (W, H), (0,0,0,0))
    # STOCK_ALERT 아치 로고 — 작게 줄여 '상단 중앙 배지'로. 텍스트와 겹치지 않게 위로 분리
    logo = Image.open(LOGO).convert('RGBA')
    lw = 200; lh = int(logo.height * lw / logo.width)
    logo = logo.resize((lw, lh))
    LOGO_Y = 4
    # 로고 뒤 부드러운 흰 글로우(어두운 배경 위 가독성)
    glow = Image.new('RGBA', (W, H), (0,0,0,0))
    gx = (W - lw)//2
    glow.paste(logo, (gx, LOGO_Y), logo)
    glow = glow.filter(ImageFilter.GaussianBlur(7))
    img.alpha_composite(glow)
    img.paste(logo, (gx, LOGO_Y), logo)
    dr = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(FONT, s1)
    f2 = ImageFont.truetype(FONT, s2)
    # 1행: 흰색 + 진한 외곽선 (아치 아래로 분리 배치)
    line1_cy = LOGO_Y + lh + 46
    draw_text_center(dr, line1_cy, line1, f1, WHITE, stroke=8, stroke_fill=(20,20,20))
    # 2행: 노란 하이라이트 박스 + 남색 글씨
    b2 = dr.textbbox((0,0), line2, font=f2)
    tw2 = b2[2]-b2[0]; th2 = b2[3]-b2[1]
    cy2 = line1_cy + 100
    pad_x, pad_y = 32, 16
    bx0 = (W - tw2)//2 - pad_x; bx1 = (W + tw2)//2 + pad_x
    by0 = cy2 - th2//2 - pad_y - 6; by1 = cy2 + th2//2 + pad_y - 6
    dr.rounded_rectangle([bx0, by0, bx1, by1], radius=26, fill=YELLOW)
    draw_text_center(dr, cy2, line2, f2, INK, stroke=0)
    img.save(os.path.join(OUT, fname))
    print(f"{fname}: [로고] '{line1}' / '{line2}'  ({img.size})")

# 쇼츠1 — 전략(폭락 매수 vs 적립). 노란 하이라이트=승자(꾸준히)
make('hook_strat.png', '30% 하락 시 매수 vs', '매월 꾸준히 매수')
# 쇼츠2 — 파이어(40만 달러 2002 진입)
make('hook_fire.png', 'STOCK_ALERT 주식 40만 달러로', '파이어 가능할까?')
