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
           '078930': 'GS', '161390': '한국타이어', '012450': '한화에어로스페이스',
           '034020': '두산에너빌리티', '012330': '현대모비스',
           '005490': 'POSCO홀딩스', '010130': '고려아연', '051910': 'LG화학'}


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
    # 그래프와 같은 중앙 세이프밴드(top≈560~1400)에 배치 — 풀스크린이면 Shorts UI에 가려짐.
    BAND_TOP, BAND_BOT = 560, 1400
    LX, RX = 120, W - 120                       # 좌우도 살짝 안쪽(우측 액션버튼 회피)
    f_t1 = ImageFont.truetype(FONT, 64); f_t2 = ImageFont.truetype(FONT, 44)
    # 제목 (밴드 상단)
    seg = [(f'{mklabel} ', WHITE), (kw, accent), (f' TOP{n}', WHITE)]
    ws = [dr.textlength(t, font=f_t1) for t, _ in seg]
    em = emoji(emo, 54); tot = sum(ws) + 14 + em.width; x = (W - tot) // 2; yt = BAND_TOP
    for (t, c), w in zip(seg, ws):
        dr.text((x, yt), t, font=f_t1, fill=c, stroke_width=6, stroke_fill=STK, anchor='lm'); x += w
    img.paste(em, (int(x + 14), int(yt - em.height // 2)), em)
    dr.text((W // 2, yt + 68), f'2026년 week {a.week}', font=f_t2, fill=YELLOW, stroke_width=4, stroke_fill=STK, anchor='mm')

    # 테이블 (제목 아래 ~ 밴드 하단, 행높이 적응)
    top = yt + 130; avail = BAND_BOT - top
    rowh = min(96, avail // n)
    tbl_h = rowh * n; y0 = top + (avail - tbl_h) // 2
    fs = 44 if n > 6 else 50
    f_rk = ImageFont.truetype(FONT, fs); f_nm = ImageFont.truetype(FONT, fs); f_dd = ImageFont.truetype(FONT, fs)
    NAME_X = LX + 100
    for i, r in enumerate(rows):
        y = y0 + i * rowh
        if i % 2 == 0:
            dr.rectangle([LX - 20, y, RX + 20, y + rowh - 8], fill=(34, 31, 27))
        cy = y + (rowh - 8) // 2
        dr.text((LX, cy), f'{i+1}', font=f_rk, fill=YELLOW, anchor='lm')
        v = r.get('drawdown_pct') if a.dir == 'fall' else r.get('return_pct')
        val = abs(v) if a.dir == 'fall' else v
        sign = '' if a.dir == 'fall' else ('+' if v >= 0 else '')
        vtxt = f'{arrow}{sign}{val:.1f}%'
        # 이름은 값(우측) 앞에서 잘리게 폭 제한 — ETF 등 긴 이름 겹침 방지
        name_max = (RX - dr.textlength(vtxt, font=f_dd) - 28) - NAME_X
        nm = name_of(r)
        while nm and dr.textlength(nm, font=f_nm) > name_max:
            nm = nm[:-1]
        if nm != name_of(r):
            nm = nm[:-1] + '…'
        dr.text((NAME_X, cy), nm, font=f_nm, fill=WHITE, anchor='lm')
        dr.text((RX, cy), vtxt, font=f_dd, fill=accent, anchor='rm')

    out = a.out or os.path.join(OUT, f'table_{code}.png')
    img.save(out); print(out, img.size)


if __name__ == '__main__':
    main()
