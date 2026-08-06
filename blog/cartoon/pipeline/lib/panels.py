"""① 패널 추출 — 8컷(4x2) 만화 PNG → 정사각형 배경정규화 패널 8장."""
from PIL import Image
import numpy as np
import os


def _grid_lines(profile, n_expected, span, thr=0.45):
    """dark 비율 프로파일에서 그리드 선(런) 중심들을 검출."""
    hot = [i for i, v in enumerate(profile) if v > thr]
    lines = []
    s = None
    p = -2
    for v in hot:
        if v != p + 1:
            if s is not None:
                lines.append((s + p) // 2)
            s = v
        p = v
    if s is not None:
        lines.append((s + p) // 2)
    return lines


def _grid_edges(im):
    """4x2 그리드 경계(컬럼 5, 로우 3) — 실제 검은 그리드 선을 검출(캡션바 제외)."""
    a = np.array(im.convert('L'))
    H, W = a.shape
    dark = a < 90
    colprof = dark.mean(axis=0)   # 열별 dark 비율 → 세로선
    rowprof = dark.mean(axis=1)   # 행별 dark 비율 → 가로선
    vlines = _grid_lines(colprof, 5, W)
    hlines = _grid_lines(rowprof, 3, H)
    # 세로선: 5개(외곽+3내부) 기대. 부족하면 균등분할 폴백
    if len(vlines) >= 5:
        # 균등 4열에 가장 가까운 5개 선택
        want = [W * i / 4 for i in range(5)]
        col = [min(vlines, key=lambda x: abs(x - w)) for w in want]
    else:
        col = [round(W * i / 4) for i in range(5)]
    # 가로선: 캡션바 위 그리드 하단까지. 상단(≈0)·중간·하단 3선.
    hl = [y for y in hlines if y < H * 0.95]
    if len(hl) >= 3:
        top = min(hl)
        bot = max(hl)
        mids = [y for y in hl if top + (bot - top) * 0.3 < y < top + (bot - top) * 0.7]
        mid = mids[len(mids) // 2] if mids else (top + bot) // 2
        row = [top, mid, bot]
    else:
        white_rows = [y for y in range(H) if a[y].mean() > 250]
        ww = [y for y in white_rows if y > H * 0.82]
        rb = min(ww) if ww else H
        row = [round(rb * i / 2) for i in range(3)]
    return col, row


def _inside(gray, margin=34, thr=0.55):
    a = np.array(gray)
    h, w = a.shape
    dr = (a < 110).mean(axis=1)
    dc = (a < 110).mean(axis=0)
    top = 0
    for y in range(min(margin, h)):
        if dr[y] > thr:
            top = y + 1
    bot = h
    for y in range(min(margin, h)):
        if dr[h - 1 - y] > thr:
            bot = h - 1 - y
    left = 0
    for x in range(min(margin, w)):
        if dc[x] > thr:
            left = x + 1
    right = w
    for x in range(min(margin, w)):
        if dc[w - 1 - x] > thr:
            right = w - 1 - x
    return left, top, right, bot


def _whiten(rgb):
    a = np.array(rgb).astype(np.int16)
    mn = a.min(axis=2)
    mx = a.max(axis=2)
    bg = (mn >= 244) & ((mx - mn) <= 12)
    a[bg] = [255, 255, 255]
    return Image.fromarray(a.astype(np.uint8))


def extract(cartoon_png, out_dir):
    """8컷 크롭 → 테두리제거 → 배경정규화 → 정사각형 패딩 → out_dir/panel_1..8.png"""
    os.makedirs(out_dir, exist_ok=True)
    im = Image.open(cartoon_png).convert('RGB')
    col, row = _grid_edges(im)
    paths = []
    n = 0
    for r in range(2):
        for c in range(4):
            n += 1
            cell = im.crop((col[c], row[r], col[c + 1], row[r + 1]))
            l, t, rt, b = _inside(cell.convert('L'))
            inner = _whiten(cell.crop((l + 1, t + 1, rt - 1, b - 1)))
            pw, ph = inner.size
            side = max(pw, ph)
            sq = Image.new('RGB', (side, side), (255, 255, 255))
            sq.paste(inner, ((side - pw) // 2, (side - ph) // 2))
            p = os.path.join(out_dir, f'panel_{n}.png')
            sq.save(p)
            paths.append(p)
    return paths
