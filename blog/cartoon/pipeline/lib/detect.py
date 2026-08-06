"""배경 자동보정 유틸 — 만화 패널에서 가짜그래프/텍스트박스/캐릭터 bbox 검출.
좌표는 항상 1080x1080 기준 정수로 환산해 반환(패널은 1080 stage에 object-fit:contain=꽉참).
"""
from PIL import Image
import numpy as np


def _load(png):
    im = Image.open(png).convert('RGB')
    return np.array(im).astype(int), im.size  # (H,W,3), (W,H)


def _bbox_1080(xs, ys, W, H):
    if len(xs) == 0:
        return None
    return {
        'x0': round(xs.min() / W * 1080), 'x1': round(xs.max() / W * 1080),
        'y0': round(ys.min() / H * 1080), 'y1': round(ys.max() / H * 1080),
        'cx': round((xs.min() + xs.max()) / 2 / W * 1080),
        'cy': round((ys.min() + ys.max()) / 2 / H * 1080),
    }


def green_bbox(png):
    """초록 텍스트/화살표(가짜 +xx%) 영역."""
    a, (W, H) = _load(png)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (g > 90) & (g > r + 30) & (g > b + 30)
    ys, xs = np.where(m)
    return _bbox_1080(xs, ys, W, H)


def red_bbox(png):
    """빨강 텍스트/박스(손실 -x,xxx,xxx / 하향 화살표) 영역."""
    a, (W, H) = _load(png)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (r > 150) & (g < 90) & (b < 90)
    ys, xs = np.where(m)
    return _bbox_1080(xs, ys, W, H)


def character_right_edge(png, ymin_frac=0.45, xmax_frac=0.62):
    """캐릭터(하반부 흑백 선화) 오른쪽 끝 x(1080). 로고/카드 좌측 안전선."""
    a, (W, H) = _load(png)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dark = (a.max(2) < 130) & (abs(r - g) < 40) & (abs(g - b) < 40)
    ys, xs = np.where(dark)
    m = (ys > H * ymin_frac) & (xs < W * xmax_frac)
    return round(xs[m].max() / W * 1080) if m.any() else 0


def bubble_bottom(png, ymax_frac=0.45):
    """상단 말풍선 아래 y(1080). 카드 상단 안전선."""
    a, (W, H) = _load(png)
    dark = a.max(2) < 130
    ys, xs = np.where(dark)
    m = ys < H * ymax_frac
    return round(ys[m].max() / H * 1080) if m.any() else 0


def phone_pos(png):
    """캐릭터가 든 폰 근사 위치(중앙-하단 회색). (x,y) 1080 or None."""
    a, (W, H) = _load(png)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    gray = (abs(r - g) < 14) & (abs(g - b) < 14) & (r > 150) & (r < 225)
    ys, xs = np.where(gray)
    m = (xs > W * 0.35) & (xs < W * 0.7) & (ys > H * 0.55) & (ys < H * 0.9)
    if m.sum() < 20:
        return None
    return (round(xs[m].mean() / W * 1080), round(ys[m].mean() / H * 1080))


def piggy_pos(png):
    """돼지저금통(우하단 선화) 중심 근사. (x,y) 1080."""
    a, (W, H) = _load(png)
    dark = a.max(2) < 110
    reg = np.zeros_like(dark)
    reg[int(H * 0.72):, int(W * 0.62):] = True
    ys, xs = np.where(dark & reg)
    if len(xs) == 0:
        return (round(0.75 * 1080), round(0.88 * 1080))
    return (round((xs.min() + xs.max()) / 2 / W * 1080),
            round((ys.min() + ys.max()) / 2 / H * 1080))
