# -*- coding: utf-8 -*-
"""전체 씬 자막 오버레이 PNG 생성.
- 소스: cocacola_script_scene_33.md (md 줄바꿈 = 자막 라인 단위)
- 출력: subtitles/ 폴더에 투명배경 1920x1080 오버레이 PNG (씬별)
- 규칙: 밝은 배경 슬라이드 → 어두운 박스+밝은 글씨 / 어두운 배경 → 밝은 박스+어두운 글씨
- 스타일: 각진 사각형, 하단 자막 안전영역, Noto Sans KR Bold
"""
import re, os, json
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
FONT_PATH = "/home/zealatan/.fonts/NotoSansKR-Bold.otf"
OUT = "subtitles"
MD = "cocacola_script_scene_33.md"

# ── 밝은 배경(크림/차트) 씬 = 어두운 박스. 나머지는 배경영상(어두움) = 밝은 박스 ──
# 필요시 이 집합만 수정하면 씬별 박스색이 반전됩니다.
BRIGHT_BG_SCENES = {18, 27, 28, 29, 30, 31}

DARK_BOX  = dict(box=(14, 20, 32, 214),  text=(244, 247, 251))   # 밝은 배경용
LIGHT_BOX = dict(box=(245, 247, 251, 235), text=(18, 21, 27))    # 어두운 배경용

MARGIN_X = 150
PAD_Y = 18           # 박스 내부 상하 여백
LINE_GAP = 8
FONT_SIZE = 52
MIN_FONT = 42
BOTTOM_MARGIN = 70   # 프레임 하단에서 박스 바닥까지
INTERIOR = (W - MARGIN_X * 2) - 80   # 박스 좌우 안쪽 여백 감안한 텍스트 최대폭


def parse_scenes(md):
    scenes = []
    for m in re.finditer(r'## Scene (\d+)[^\n]*\n(.*?)(?=\n## Scene |\Z)', md, re.S):
        num = int(m.group(1))
        body = re.sub(r'###[^\n]*', '', m.group(2)).replace('---', '')
        lines = [re.sub(r'\s+', ' ', l).strip() for l in body.split('\n') if l.strip()]
        scenes.append((num, lines))
    return scenes


def wrap_to_fit(draw, text, base_font_path):
    """한 줄에 맞으면 그대로. 넘치면 2줄로 분할. 그래도 넘치면 폰트 축소."""
    for size in range(FONT_SIZE, MIN_FONT - 1, -2):
        font = ImageFont.truetype(base_font_path, size)
        if draw.textlength(text, font=font) <= INTERIOR:
            return [text], font
    # 2줄 분할 (어절 기준 균형)
    words = text.split(' ')
    if len(words) > 1:
        best = None
        for i in range(1, len(words)):
            l1 = ' '.join(words[:i]); l2 = ' '.join(words[i:])
            for size in range(FONT_SIZE, MIN_FONT - 1, -2):
                font = ImageFont.truetype(base_font_path, size)
                if draw.textlength(l1, font=font) <= INTERIOR and draw.textlength(l2, font=font) <= INTERIOR:
                    diff = abs(draw.textlength(l1, font=font) - draw.textlength(l2, font=font))
                    if best is None or (size, -diff) > (best[0], -best[3]):
                        best = (size, l1, l2, diff, font)
            if best and best[0] == FONT_SIZE:
                break
        if best:
            return [best[1], best[2]], best[4]
    font = ImageFont.truetype(base_font_path, MIN_FONT)
    return [text], font


def render(text, style, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lines, font = wrap_to_fit(d, text, FONT_PATH)

    asc, desc = font.getmetrics()
    line_h = asc + desc
    n = len(lines)
    bh = line_h * n + LINE_GAP * (n - 1) + PAD_Y * 2
    by1 = H - BOTTOM_MARGIN
    by0 = by1 - bh
    bx0, bx1 = MARGIN_X, W - MARGIN_X

    # 각진 박스
    d.rectangle([bx0, by0, bx1, by1], fill=style["box"])
    # 텍스트 (중앙 정렬)
    ty = by0 + PAD_Y
    for ln in lines:
        tw = d.textlength(ln, font=font)
        d.text(((W - tw) / 2, ty), ln, font=font, fill=style["text"])
        ty += line_h + LINE_GAP

    img.save(path, "PNG")
    return lines


def main():
    os.makedirs(OUT, exist_ok=True)
    scenes = parse_scenes(open(MD, encoding="utf-8").read())
    manifest = []
    count = 0
    for num, lines in scenes:
        style = DARK_BOX if num in BRIGHT_BG_SCENES else LIGHT_BOX
        bright = num in BRIGHT_BG_SCENES
        for i, text in enumerate(lines, 1):
            fn = f"s{num:02d}_l{i:02d}.png"
            rendered = render(text, style, os.path.join(OUT, fn))
            manifest.append({
                "file": fn, "scene": num, "line": i, "text": text,
                "wrapped": rendered,
                "bg": "bright" if bright else "dark",
                "box": "dark" if bright else "light",
            })
            count += 1
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print(f"generated {count} subtitle PNGs -> {OUT}/")
    print(f"manifest: {OUT}/manifest.json")


if __name__ == "__main__":
    main()
