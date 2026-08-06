#!/usr/bin/env python3
"""낙폭(하락) 쇼츠 상단 훅 PNG. 1080x440, 투명. line1: 시장+하락(빨강)+TOPn+📉, line2: 노랑 주차.
   상승판 gen_hook_rise.py 의 낙폭 대칭. 개수·주차는 인자로.
   사용: python3 rec/gen_hook_fall.py --week 31 --market US --top 10
         (인자 없으면 4시장 기본 세트 생성)"""
import argparse
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), '..')
FONT = os.path.join(ROOT, '..', 'fonts', 'BlackHanSans-Regular.ttf')
EMOJI = '/snap/gnome-42-2204/245/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
OUT = os.path.join(ROOT, 'assets', 'shorts')
W, H = 1080, 440
WHITE = (248, 248, 245); RED = (231, 76, 60); YELLOW = (255, 216, 61); STK = (20, 20, 20)
MK = {"US": "미국 주식 ", "KR": "한국 주식 ", "EU": "유럽 주식 ", "ETF": "ETF "}


def emoji_img(ch, px):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new('RGBA', (140, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((70, 70), ch, font=f, anchor='mm', embedded_color=True)
    im = im.crop(im.getbbox()); s = px / im.height
    return im.resize((int(im.width * s), px), Image.LANCZOS)


def make(fname, segs, line2, emoji, s1=74, s2=60):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(FONT, s1); f2 = ImageFont.truetype(FONT, s2)
    em = emoji_img(emoji, int(s1 * 0.86))
    widths = [dr.textlength(t, font=f1) for t, _ in segs]
    gap = 14; tot = sum(widths) + gap + em.width
    x = (W - tot) // 2; y1 = 120
    for (t, col), w in zip(segs, widths):
        dr.text((x, y1), t, font=f1, fill=col, stroke_width=8, stroke_fill=STK, anchor='lm'); x += w
    img.alpha_composite(em, (int(x + gap), int(y1 - em.height // 2)))
    dr.text((W // 2, y1 + 96), line2, font=f2, fill=YELLOW, stroke_width=7, stroke_fill=STK, anchor='mm')
    img.save(os.path.join(OUT, fname)); print(fname, img.size)


def hook(market, week, top):
    make(f'hook_{market}.png',
         [(MK[market], WHITE), ("하락", RED), (f" TOP{top}", WHITE)],
         f"2026년 week {week}", "📉")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--week', type=int, default=31)
    ap.add_argument('--market', choices=list(MK))
    ap.add_argument('--top', type=int, default=5)
    a = ap.parse_args()
    if a.market:
        hook(a.market, a.week, a.top)
    else:
        for m in ("US", "KR", "EU", "ETF"):
            hook(m, a.week, 5)
