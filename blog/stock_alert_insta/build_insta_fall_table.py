#!/usr/bin/env python3
"""stock_alert 인스타 이식(B: PIL 재구축) — 낙폭 4시장 테이블 릴(1080×1920).

FALL_TABLES_GOLDEN(HTML+녹화)을 PIL로 재구축. 디자인 동일: 검정+흰 종이카드,
타이틀 "<국기> <시장> 주식 하락 TOPn"(하락=마젠타), 순위·로고·종목명·▼낙폭%(라즈베리),
마스코트 우상단, 페이지표시. 폰트만 Pretendard→Noto CJK 대체(PIL woff2 불가).

우선 정적 페이지 렌더러 + 한국 샘플. 이후 애니(행 스태거·카운트업·페이지 페이드) + 4시장 조립.
"""
import os, json, base64, subprocess
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def clamp(x): return max(0.0, min(1.0, x))
def eo(p): p = clamp(p); return 1 - (1 - p) ** 3   # ease-out cubic

ROOT = Path(__file__).resolve().parent
BLOG = ROOT.parent
GF = BLOG / "golden_shorts_fire"
SA = BLOG / "stock_alert"          # 원본(읽기전용): 로고·데이터·마스코트·썸네일 공유
DATA = SA / "data"                 # 주간 스캔 산출(원본 파이프라인이 갱신)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
EMOJI = "/snap/gnome-42-2204/245/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
def font(s, b=True): return ImageFont.truetype(BOLD if b else FONT, s)
W, H = 1080, 1920

MAGENTA, RASP, NAME_C, TH_C, NOTE_C, PIND_C = "#d12e77", "#c2255c", "#141414", "#8a857c", "#6b6560", "#7d7871"
MK = {"미국": "미국 주식", "한국": "한국 주식", "유럽": "유럽 주식", "ETF": "ETF"}
FLAG = {"미국": "🇺🇸", "한국": "🇰🇷", "유럽": "🇪🇺", "ETF": "📊"}
ORDER = ["미국", "한국", "유럽", "ETF"]
KR_NAME = {'005930': '삼성전자', '000660': 'SK하이닉스', '402340': 'SK스퀘어', '005380': '현대차',
           '009150': '삼성전기', '373220': 'LG에너지솔루션', '032830': '삼성생명', '028260': '삼성물산',
           '329180': 'HD현대중공업', '000270': '기아', '011070': 'LG이노텍', '006800': '미래에셋증권',
           '066570': 'LG전자', '064400': 'LG CNS', '950160': '코오롱티슈진', '010950': 'S-Oil',
           '078930': 'GS', '161390': '한국타이어', '012450': '한화에어로스페이스',
           '034020': '두산에너빌리티', '012330': '현대모비스',
           '005490': 'POSCO홀딩스', '010130': '고려아연', '051910': 'LG화학'}

# 에셋
_p = open(GF / "assets" / "paper_b64.txt").read().strip()
if _p.startswith("data:"): _p = _p.split(",", 1)[1]
PAPER = Image.open(BytesIO(base64.b64decode(_p))).convert("RGB")
MASCOT = None   # 마크 사용 안 함(제거)
LOGO_DIR = SA / "deck" / "logos"
_lc = {}


def logo(ticker):
    base = ticker.split(".")[0]
    for c in (base, base.upper()):
        p = LOGO_DIR / f"{c}.png"
        if p.exists():
            if p not in _lc: _lc[p] = Image.open(p).convert("RGBA")
            return _lc[p]
    return None


def name_of(r):
    return KR_NAME.get(r["ticker"].split(".")[0], r["label"].split(" / ")[0])


def emoji_img(ch, px):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), ch, font=f, anchor="mm", embedded_color=True)
    bb = im.getbbox()
    if not bb: return None
    im = im.crop(bb); s = px / im.height
    return im.resize((max(1, int(im.width * s)), px), Image.LANCZOS)


def paper_card(w, h, radius=26):
    # 종이 텍스처를 카드 크기로 cover 크롭 + 둥근 모서리
    src = PAPER; sr = max(w / src.width, h / src.height)
    rs = src.resize((int(src.width * sr) + 1, int(src.height * sr) + 1), Image.LANCZOS)
    card = rs.crop((0, 0, w, h)).convert("RGBA")
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius, fill=255)
    card.putalpha(mask)
    return card


def _row_layer(i, r, ry0, row_pitch, geo, show_logo, val):
    """행 1개를 투명 레이어에 그려 반환(개별 alpha·slide 위해)."""
    ix0, ix1, rk_cx, lg_x, nm_x = geo
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    cy = ry0 + i * row_pitch + row_pitch // 2
    d.text((rk_cx, cy), str(i + 1), anchor="mm", fill=RASP, font=font(36))
    if show_logo:
        lg = logo(r["ticker"])
        if lg:
            s = min(104 / lg.width, 46 / lg.height)   # contain(비율 유지)
            lw, lh = max(1, int(lg.width * s)), max(1, int(lg.height * s))
            lgr = lg.resize((lw, lh), Image.LANCZOS)
            lay.paste(lgr, (int(lg_x), int(cy - lh / 2)), lgr)
            d = ImageDraw.Draw(lay)
    nm = name_of(r); nf = font(33); maxw = (ix1 - 210) - nm_x
    while d.textlength(nm, font=nf) > maxw and len(nm) > 4: nm = nm[:-2] + "…"
    d.text((nm_x, cy), nm, anchor="lm", fill=NAME_C, font=nf)
    d.text((ix1, cy), f"▼{val:.1f}%", anchor="rm", fill=RASP, font=font(35))
    return lay


def render_page(market, rows, week, page, total, t=99.0):
    n = len(rows); show_logo = market != "ETF"
    cx0, cy0, cx1 = 54, 307, 1026
    row_pitch, head_h = 72, 66
    cy1 = cy0 + 34 + head_h + n * row_pitch + 20 + 34 + 26
    cw, ch = cx1 - cx0, cy1 - cy0
    card_a = clamp(t / 0.5); card_dy = 30 * (1 - eo(t / 0.55))
    title_a = clamp(t / 0.45); title_dy = -22 * (1 - eo(t / 0.5))
    pind_a = clamp((t - 0.15) / 0.5)

    bg = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    # ── 카드 레이어(종이+헤더+행+노트) ──
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((cx0, cy0 + 16, cx1, cy1 + 16), 26, fill=(0, 0, 0, 150))
    layer = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(28)), layer)
    layer.paste(paper_card(cw, ch), (cx0, cy0), paper_card(cw, ch)); ld = ImageDraw.Draw(layer)
    ix0, ix1 = cx0 + 30, cx1 - 30; rk_cx = ix0 + 37; lg_x = ix0 + 80; nm_x = lg_x + (118 if show_logo else 0)
    hy = cy0 + 34 + 26
    ld.text((rk_cx, hy), "#", anchor="mm", fill=TH_C, font=font(26))
    ld.text((nm_x, hy), "종목", anchor="lm", fill=TH_C, font=font(26))
    ld.text((ix1, hy), "전고점比", anchor="rm", fill=TH_C, font=font(26))
    ld.line((ix0, cy0 + 34 + head_h - 6, ix1, cy0 + 34 + head_h - 6), fill=(0, 0, 0, 56), width=2)
    ry0 = cy0 + 34 + head_h
    geo = (ix0, ix1, rk_cx, lg_x, nm_x)
    for i, r in enumerate(rows):
        if i > 0: ld.line((ix0, ry0 + i * row_pitch, ix1, ry0 + i * row_pitch), fill="#e2ded7", width=1)
    for i, r in enumerate(rows):
        rt = (t - (0.42 + i * 0.065)) / 0.55
        if rt <= 0: continue
        ra = clamp(rt); rdy = 18 * (1 - eo(rt))
        val = abs(r.get("drawdown_pct", 0)) * eo((t - (0.42 + i * 0.065)) / 0.68)
        rl = _row_layer(i, r, ry0, row_pitch, geo, show_logo, val)
        if rdy: rl = rl.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, -rdy))
        if ra < 1: a = rl.split()[3].point(lambda v: int(v * ra)); rl.putalpha(a)
        layer = Image.alpha_composite(layer, rl)
    ImageDraw.Draw(layer).text(((cx0 + cx1) // 2, cy1 - 40), f"전고점 대비 낙폭 · 2026년 week {week}", anchor="mm", fill=NOTE_C, font=font(19))
    # 카드 레이어 → bg (슬라이드+페이드)
    if card_dy: layer = layer.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, -card_dy))
    if card_a < 1: layer.putalpha(layer.split()[3].point(lambda v: int(v * card_a)))
    bg = Image.alpha_composite(bg, layer)
    d = ImageDraw.Draw(bg)

    # ── 타이틀(검정 위 → alpha로 어둡게) ──
    def dim(hexc, a):
        h = hexc.lstrip("#"); return tuple(int(int(h[k:k+2], 16) * a) for k in (0, 2, 4))
    tf = font(52); flag = emoji_img(FLAG[market], 50)
    parts = [(" " + MK[market] + " ", "#ffffff"), ("하락", MAGENTA), (f" TOP{n}", "#ffffff")]
    tw = (flag.width if flag else 0) + sum(d.textlength(tt, font=tf) for tt, _ in parts)
    x = (W - tw) / 2; ty = 163 + title_dy
    if flag and title_a > 0:
        fl = flag.copy(); fl.putalpha(fl.split()[3].point(lambda v: int(v * title_a)))
        bg.paste(fl, (int(x), int(ty - flag.height / 2)), fl); d = ImageDraw.Draw(bg); x += flag.width
    for tt, c in parts:
        d.text((x, ty), tt, anchor="lm", fill=dim(c, title_a), font=tf); x += d.textlength(tt, font=tf)
    d.text((W // 2, ty + 56), f"2026 · week {week}", anchor="mm", fill=dim("#d9b44a", title_a), font=font(32))
    # 마스코트(카드와 함께 페이드)
    if MASCOT and card_a > 0:
        mh = 132; mw = int(MASCOT.width * mh / MASCOT.height)
        mk = MASCOT.resize((mw, mh), Image.LANCZOS)
        if card_a < 1: mk.putalpha(mk.split()[3].point(lambda v: int(v * card_a)))
        bg.paste(mk, (1026 - mw, 142), mk); d = ImageDraw.Draw(bg)
    # 페이지표시
    pf = font(44); seg = f"{page}"; rest = f" / {total}"
    twp = d.textlength(seg, font=pf) + d.textlength(rest, font=pf); px = (W - twp) / 2; py = 1670
    d.text((px, py), seg, anchor="lm", fill=dim("#ffffff", pind_a), font=pf)
    d.text((px + d.textlength(seg, font=pf), py), rest, anchor="lm", fill=dim(PIND_C, pind_a), font=pf)
    return bg.convert("RGB")


def render_card(market, rows, week, page, total, HH=1350):
    """인스타 캐러셀 정적 카드. HH=1350(4:5) / 1080(1:1). 행 간격은 높이에 적응."""
    n = len(rows); show_logo = market != "ETF"
    im = Image.new("RGB", (W, HH), "#000000")
    cx0, cx1 = 40, 1040
    ttl_y = int(HH * 0.074)                     # 타이틀 중심
    cy0 = ttl_y + int(HH * 0.086)               # 카드 상단(타이틀·주차 아래)
    cy1 = HH - int(HH * 0.045)                  # 카드 하단(여백)
    head_h = 60; note_h = 30; pad_t, pad_b = 32, 22
    row_pitch = int(((cy1 - cy0) - pad_t - pad_b - head_h - note_h) / n)
    cw, ch = cx1 - cx0, cy1 - cy0
    sh = Image.new("RGBA", (W, HH), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((cx0, cy0 + 16, cx1, cy1 + 16), 26, fill=(0, 0, 0, 150))
    im = Image.alpha_composite(im.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(28))).convert("RGB")
    im.paste(paper_card(cw, ch), (cx0, cy0), paper_card(cw, ch))
    d = ImageDraw.Draw(im)
    # 타이틀 + 주차
    tf = font(50); flag = emoji_img(FLAG[market], 48)
    parts = [(" " + MK[market] + " ", "#ffffff"), ("하락", MAGENTA), (f" TOP{n}", "#ffffff")]
    tw = (flag.width if flag else 0) + sum(d.textlength(t, font=tf) for t, _ in parts)
    x = (W - tw) / 2; ty = ttl_y
    if flag: im.paste(flag, (int(x), int(ty - flag.height / 2)), flag); d = ImageDraw.Draw(im); x += flag.width
    for t, c in parts:
        d.text((x, ty), t, anchor="lm", fill=c, font=tf); x += d.textlength(t, font=tf)
    d.text((W // 2, ty + 52), f"2026 · week {week}", anchor="mm", fill="#d9b44a", font=font(30))
    # 마스코트
    if MASCOT:
        mh = int(HH*0.082); mw = int(MASCOT.width * mh / MASCOT.height)
        mk = MASCOT.resize((mw, mh), Image.LANCZOS); im.paste(mk, (1040 - mw, int(HH*0.043)), mk); d = ImageDraw.Draw(im)
    # 헤더
    ix0, ix1 = cx0 + 30, cx1 - 30; rk_cx = ix0 + 37; lg_x = ix0 + 80; nm_x = lg_x + (118 if show_logo else 0)
    hy = cy0 + pad_t + 24
    d.text((rk_cx, hy), "#", anchor="mm", fill=TH_C, font=font(26))
    d.text((nm_x, hy), "종목", anchor="lm", fill=TH_C, font=font(26))
    d.text((ix1, hy), "전고점比", anchor="rm", fill=TH_C, font=font(26))
    d.line((ix0, cy0 + pad_t + head_h - 6, ix1, cy0 + pad_t + head_h - 6), fill=(0, 0, 0, 56), width=2)
    ry0 = cy0 + pad_t + head_h
    for i, r in enumerate(rows):
        cy = ry0 + i * row_pitch + row_pitch // 2
        if i > 0: d.line((ix0, ry0 + i * row_pitch, ix1, ry0 + i * row_pitch), fill="#e2ded7", width=1)
        d.text((rk_cx, cy), str(i + 1), anchor="mm", fill=RASP, font=font(38))
        if show_logo:
            lg = logo(r["ticker"])
            if lg:
                s = min(112 / lg.width, (row_pitch*0.62) / lg.height); lw, lh = max(1, int(lg.width * s)), max(1, int(lg.height * s))
                lgr = lg.resize((lw, lh), Image.LANCZOS); im.paste(lgr, (int(lg_x), int(cy - lh / 2)), lgr); d = ImageDraw.Draw(im)
        nm = name_of(r); nf = font(35); maxw = (ix1 - 220) - nm_x
        while d.textlength(nm, font=nf) > maxw and len(nm) > 4: nm = nm[:-2] + "…"
        d.text((nm_x, cy), nm, anchor="lm", fill=NAME_C, font=nf)
        d.text((ix1, cy), f"▼{abs(r.get('drawdown_pct', 0)):.1f}%", anchor="rm", fill=RASP, font=font(37))
    d.text(((cx0 + cx1) // 2, cy1 - 34), f"전고점 대비 낙폭 · {page}/{total}", anchor="mm", fill=NOTE_C, font=font(20))
    return im


def main_cards():
    week = 31
    data = json.load(open(DATA / f"fall_week{week}.json", encoding="utf-8"))
    markets = [m for m in ORDER if data["markets"].get(m)]
    for HH, tag in [(1350, "4x5"), (1080, "1x1")]:
        outdir = ROOT / "carousel" / tag; outdir.mkdir(parents=True, exist_ok=True)
        for pi, m in enumerate(markets):
            im = render_card(m, data["markets"][m][:10], week, pi + 1, len(markets), HH)
            im.save(outdir / f"fall_w{week}_{pi+1}_{m}.png")
        print("saved", len(markets), tag, "cards →", outdir)


_THUMB = SA / "assets" / "shorts" / "thumb_fall_multi.png"
INTRO_IMG = Image.open(_THUMB).convert("RGB").resize((W, H)) if _THUMB.exists() else None


def render_intro(t):
    # 검정 페이드인 없이 썸네일을 처음부터 그대로(딱 바로).
    return INTRO_IMG if INTRO_IMG else Image.new("RGB", (W, H), "#000000")


def main():
    import sys
    week = 31
    data = json.load(open(DATA / f"fall_week{week}.json", encoding="utf-8"))
    markets = [m for m in ORDER if data["markets"].get(m)]
    total = len(markets)
    intro_on = os.environ.get("INTRO", "0") != "0"   # 기본: 썸네일 없음(바로 표부터)
    FPS, INTRO, MKDUR, FADE = 30, 2.6, 8.7, 0.5
    # 세그먼트: (kind, market, rows, dur, pageno)
    segs = []
    if intro_on: segs.append(("intro", None, None, INTRO, 0))
    for pi, m in enumerate(markets): segs.append(("mk", m, data["markets"][m][:10], MKDUR, pi + 1))
    # 최종(정지) 프레임 캐시
    finals = {}
    for k, (kind, m, rows, dur, pg) in enumerate(segs):
        finals[k] = render_intro(99) if kind == "intro" else render_page(m, rows, week, pg, total, 99)
    starts = []; acc = 0
    for _, _, _, dur, _ in segs: starts.append(acc); acc += dur
    OUT = ROOT / "shorts" / f"insta_fall_w{week}.mp4"; OUT.parent.mkdir(exist_ok=True)
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", str(OUT)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nfr = round(acc * FPS)
    for fr in range(nfr):
        gt = fr / FPS
        k = max(i for i, s in enumerate(starts) if gt >= s - 1e-9)
        lt = gt - starts[k]; kind, m, rows, dur, pg = segs[k]
        if kind == "intro":
            img = render_intro(lt)
        elif lt < FADE and k > 0:
            cur = render_page(m, rows, week, pg, total, lt)
            img = Image.blend(finals[k - 1], cur, clamp(lt / FADE))
        elif lt < 2.0:
            img = render_page(m, rows, week, pg, total, lt)
        else:
            img = finals[k]
        mv = memoryview(img.tobytes())
        while mv: mv = mv[p.stdin.write(mv):]
    p.stdin.close()
    if p.wait() != 0: raise SystemExit("ffmpeg failed")
    print("created", OUT, f"({acc:.1f}s, {nfr} frames)")   # 네이티브 1080×1920 풀블리드


if __name__ == "__main__":
    main()
