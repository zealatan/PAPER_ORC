#!/usr/bin/env python3
"""쇼츠 심플 아웃트로 엔드카드(9:16): 배투실 마스코트 + 빨간 '구독하기 🔔' 버튼만.
   (요약 테이블이 카드 뒤에 오므로 아웃트로는 최대한 심플하게.)"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), '..')
FONT = os.path.join(ROOT, '..', 'fonts', 'BlackHanSans-Regular.ttf')
EMOJI = '/snap/gnome-42-2204/245/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
OUT = os.path.join(ROOT, 'assets', 'shorts')
BATU = os.path.join(OUT, 'batusil_label.png')
W, H = 1080, 1920
WHITE = (245, 245, 242); RED = (214, 58, 48)


def emoji(ch, px):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new('RGBA', (140, 140), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((70, 70), ch, font=f, anchor='mm', embedded_color=True)
    im = im.crop(im.getbbox()); s = px / im.height
    return im.resize((int(im.width * s), px), Image.LANCZOS)


img = Image.new('RGB', (W, H), (24, 22, 19))
dr = ImageDraw.Draw(img)
# 배투실 마스코트(중앙)
bt = Image.open(BATU).convert('RGBA'); bw = 460
bt = bt.resize((bw, int(bt.height * bw / bt.width)), Image.LANCZOS)
img.paste(bt, ((W - bw) // 2, 620), bt)
by = 620 + bt.height
# 빨간 구독 버튼 + 벨
btn_w, btn_h = 520, 150; bx0 = (W - btn_w) // 2; by0 = by + 130
dr.rounded_rectangle([bx0, by0, bx0 + btn_w, by0 + btn_h], radius=42, fill=RED)
bell = emoji('🔔', 66); f_cta = ImageFont.truetype(FONT, 72)
lbl = '구독하기'; tw = dr.textlength(lbl, font=f_cta); gap = 20; tot = tw + gap + bell.width
sx = (W - tot) // 2; cy = by0 + btn_h // 2
dr.text((sx, cy), lbl, font=f_cta, fill=WHITE, anchor='lm')
img.paste(bell, (int(sx + tw + gap), int(cy - bell.height // 2)), bell)
img.save(os.path.join(OUT, 'outro_card.png'))
print('outro_card.png (simple)', img.size)
