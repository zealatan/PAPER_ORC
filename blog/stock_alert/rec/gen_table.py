#!/usr/bin/env python3
"""쇼츠 요약 테이블 PNG (9:16). 카드 10장 뒤 ~5초 요약용. 낙폭/상승 겸용.
   낙폭=▼빨강 · 상승=▲초록. 데이터=fall_weekN.json / rise_weekN.json.
   사용: python3 rec/gen_table.py --market 한국 --week 31 --dir fall
         → assets/shorts/table_KR.png
"""
import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), '..')
FONT = os.path.join(ROOT, '..', 'fonts', 'BlackHanSans-Regular.ttf')
EMOJI = '/snap/gnome-42-2204/245/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
OUT = os.path.join(ROOT, 'assets', 'shorts')
W, H = 1080, 1920
YELLOW = (255, 216, 61); WHITE = (238, 238, 235); STK = (15, 15, 15)
RED = (231, 76, 60); GREEN = (56, 190, 110)
MK = {"미국": ("US", "미국 주식"), "한국": ("KR", "한국 주식"),
      "유럽": ("EU", "유럽 주식"), "ETF": ("ETF", "ETF")}
# 한국 종목 한글명(없으면 라벨 영문 사용)
KR_NAME = {'005930': '삼성전자', '000660': 'SK하이닉스', '402340': 'SK스퀘어', '005380': '현대차',
           '009150': '삼성전기', '373220': 'LG에너지솔루션', '032830': '삼성생명', '028260': '삼성물산',
           '329180': 'HD현대중공업', '000270': '기아', '011070': 'LG이노텍', '006800': '미래에셋증권',
           '066570': 'LG전자', '064400': 'LG CNS', '950160': '코오롱티슈진', '010950': 'S-Oil',
           '078930': 'GS', '161390': '한국타이어'}


def emoji(ch, px):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new('RGBA', (140, 140), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((70, 70), ch, font=f, anchor='mm', embedded_color=True)
    im = im.crop(im.getbbox()); s = px / im.height
    return im.resize((int(im.width * s), px), Image.LANCZOS)


def name_of(row):
    code = row['ticker'].split('.')[0]
    return KR_NAME.get(code, row['label'].split(' / ')[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--market', required=True, choices=list(MK))
    ap.add_argument('--week', type=int, required=True)
    ap.add_argument('--dir', choices=['fall', 'rise'], default='fall')
    ap.add_argument('--out')
    a = ap.parse_args()

    code, mklabel = MK[a.market]
    data = json.load(open(os.path.join(ROOT, 'data', f'{a.dir}_week{a.week}.json'), encoding='utf-8'))
    rows = data['markets'][a.market]
    n = len(rows)
    accent = RED if a.dir == 'fall' else GREEN
    kw = '하락' if a.dir == 'fall' else '신고가'
    emo = '📉' if a.dir == 'fall' else '📈'
    arrow = '▼' if a.dir == 'fall' else '▲'

    img = Image.new('RGB', (W, H), (24, 22, 19)); dr = ImageDraw.Draw(img)
    f_t1 = ImageFont.truetype(FONT, 72); f_t2 = ImageFont.truetype(FONT, 50)
    # 제목 (시장 + 하락/신고가(색) + TOPn + 이모지)
    seg = [(f'{mklabel} ', WHITE), (kw, accent), (f' TOP{n}', WHITE)]
    ws = [dr.textlength(t, font=f_t1) for t, _ in seg]
    em = emoji(emo, 60); tot = sum(ws) + 14 + em.width; x = (W - tot) // 2; yt = 150
    for (t, c), w in zip(seg, ws):
        dr.text((x, yt), t, font=f_t1, fill=c, stroke_width=7, stroke_fill=STK, anchor='lm'); x += w
    img.paste(em, (int(x + 14), int(yt - em.height // 2)), em)
    dr.text((W // 2, yt + 80), f'2026년 week {a.week}', font=f_t2, fill=YELLOW, stroke_width=5, stroke_fill=STK, anchor='mm')

    # 테이블 (세로 중앙, 행높이 적응)
    avail = 1520; y0 = 300
    rowh = min(150, avail // n)
    tbl_h = rowh * n; y0 = 320 + (avail - tbl_h) // 2
    f_rk = ImageFont.truetype(FONT, 46); f_nm = ImageFont.truetype(FONT, 50); f_dd = ImageFont.truetype(FONT, 50)
    for i, r in enumerate(rows):
        y = y0 + i * rowh
        if i % 2 == 0:
            dr.rectangle([50, y, W - 50, y + rowh - 12], fill=(34, 31, 27))
        cy = y + (rowh - 12) // 2
        dr.text((100, cy), f'{i+1}', font=f_rk, fill=YELLOW, anchor='lm')
        dr.text((210, cy), name_of(r), font=f_nm, fill=WHITE, anchor='lm')
        v = r.get('drawdown_pct') if a.dir == 'fall' else r.get('return_pct')
        val = abs(v) if a.dir == 'fall' else v
        sign = '' if a.dir == 'fall' else ('+' if v >= 0 else '')
        dr.text((W - 100, cy), f'{arrow}{sign}{val:.1f}%', font=f_dd, fill=accent, anchor='rm')

    out = a.out or os.path.join(OUT, f'table_{code}.png')
    img.save(out); print(out, img.size)


if __name__ == '__main__':
    main()
