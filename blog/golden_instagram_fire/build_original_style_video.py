#!/usr/bin/env python3
"""원본 accumAnim 감성으로 다시 그리는 1080×1920 QQQ FIRE 릴스."""

import math
import os
import subprocess
from pathlib import Path

SHOW_STAMP = os.environ.get("INSTA_STAMP", "1") != "0"   # 생존/파산 스탬프 표시(기본 켜짐, 0이면 끔)

from PIL import Image, ImageDraw

from build_instagram_video import (
    BOLD, COLORS, DATA, EXPORTS, FONT, FPS, MOS, PREFIX, PRINCIPALS, REEL_H,
    SUFFIX, W, X0, clip_points, ease, font, header, lerp, money, principal_label,
)

P1, P2 = PRINCIPALS   # 표시 원금 2종(USD 40만/80만 · KRW 4억/8억)

ROOT = Path(__file__).resolve().parent
OUT = EXPORTS / f"{PREFIX}_fire_original_style_reel.mp4"

# 종목 로고(있으면 타이틀 위 중앙에 컬러 그대로). 없으면 생략.
LOGO_PATH = ROOT / f"assets/logos/{PREFIX}_logo.png"
LOGO_IMAGE = None
if LOGO_PATH.exists():
    LOGO_IMAGE = Image.open(LOGO_PATH).convert("RGBA")
    LOGO_IMAGE.thumbnail((240, 92), Image.Resampling.LANCZOS)   # 제목 왼쪽 인라인용 소형

ALT_YAXIS = os.environ.get("ALT_YAXIS", "1") != "0"   # 기본 ON: y축을 활성 리빌에 맞추고 완성 고스트 초과분은 화면 밖


def axes(draw, box, progress, x_end, y_top):
    left, top, right, bottom = box
    axis_right = lerp(left, right, progress)
    axis_top = top
    for i in range(3):
        value = y_top * i / 2
        y = bottom - (bottom - top) * i / 2
        draw.line((left, y, axis_right, y), fill="#292929", width=2)
        draw.text((left - 18, y), money(value), anchor="rm",
                  fill="#aaaaaa", font=font(31))
    x_ids = (0,) if progress < .12 else ((0, 4) if progress < .28 else range(5))
    for i in x_ids:
        year = X0 + (x_end - X0) * i / 4
        x = left + (right - left) * progress * i / 4
        draw.line((x, axis_top, x, bottom), fill="#1b1b1b", width=2)
        label = f"{year:.1f}" if x_end - X0 < 2 else f"{year:.0f}"
        draw.text((x, bottom + 30), label, anchor="ma",
                  fill="#aaaaaa", font=font(30))
    draw.line((left, bottom, axis_right, bottom), fill="#888888", width=3)
    draw.line((left, bottom, left, axis_top), fill="#888888", width=3)
    return axis_top


def stamp(draw, text, color):
    cx, cy, ww, hh = 550, 1210, 410, 180
    draw.rounded_rectangle((cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2),
                           24, outline=color, width=8)
    draw.rounded_rectangle((cx - ww / 2 + 15, cy - hh / 2 + 15,
                            cx + ww / 2 - 15, cy + hh / 2 - 15),
                           17, outline=color, width=3)
    draw.text((cx, cy), text, anchor="mm", fill=color, font=font(79, True))


HOOK_SECS = 2.0   # 초반 2초: $80만 최종 결과를 다 보여줘 후킹


def render(t):
    image = Image.new("RGB", (W, REEL_H), "#000000")
    draw = ImageDraw.Draw(image)
    header(draw)   # 로고 제거

    row400, row800 = DATA[P1], DATA[P2]
    end400 = max(line["pts"][-1][0] for line in row400["payload"]["lines"])
    end800 = max(line["pts"][-1][0] for line in row800["payload"]["lines"])

    def y_ceiling(row, principal, limit):
        visible = principal
        for line in row["payload"]["lines"]:
            values = [v for _, v in clip_points(line["pts"], limit)]
            if values:
                visible = max(visible, *values)
        return max(principal, visible * 1.08 if visible > principal else visible)

    if t < HOOK_SECS:
        # 후킹: 큰 원금(P2) 결과를 완성 상태로 미리 보여준다.
        phase = "hook"
        progress = axis_progress = 1
        x_end = clip_end = end800
        principal = P2
        y_top = y_ceiling(row800, P2, end800)
        held = False
        ghost_rows = [row400]
        active_row = row800
    else:
        s = t - HOOK_SECS
        if s < 9.0:
            phase = "400"
            progress = ease(s / 8.0)
            axis_progress = progress
            x_end = clip_end = lerp(X0, end400, progress)
            y_top = y_ceiling(row400, P1, clip_end)
            principal = P1
            held = s >= 8.0
            ghost_rows = []
            active_row = row400
        elif s < 10.4:
            phase = "transition"
            tp = ease((s - 9.0) / 1.4)
            progress = axis_progress = 1
            x_end = clip_end = end400
            principal = lerp(P1, P2, tp)
            y_top = principal
            held = False
            ghost_rows = [row400]
            active_row = None
        else:
            phase = "800"
            progress = ease((s - 10.4) / 11.0)
            axis_progress = 1
            clip_end = lerp(X0, end800, progress)
            x_end = max(end400, clip_end)
            y_top = y_ceiling(row800, P2, clip_end)
            principal = P2
            held = s - 10.4 >= 11.0
            ghost_rows = [row400]
            active_row = row800

    # 기본: 고스트(완성 원금) 전체 최댓값까지 y축 확장 → 4억이 정지·완성 상태로 다 보임.
    # ALT: y축은 활성 리빌에 맞추고, 고스트의 축 초과분은 화면 위로 잘라냄(대안 샘플).
    if not ALT_YAXIS:
        for g in ghost_rows:
            g_end = max(line["pts"][-1][0] for line in g["payload"]["lines"])
            y_top = max(y_top, y_ceiling(g, 0, g_end))

    # 패널 없이 검정 배경에 바로 그린다.
    # 은퇴 원금: 노란 마커(원금선 색) + 회색 라벨 + 흰 볼드 금액.
    cy = 692
    draw.line((72, cy, 112, cy), fill="#ffe14d", width=7)
    tx = 130
    draw.text((tx, cy), "은퇴 원금", fill="#9a9a9a", font=font(36), anchor="lm")
    tx += font(36).getlength("은퇴 원금") + 22
    draw.text((tx, cy), principal_label(principal), fill="#ffffff",
              font=font(64, True), anchor="lm")
    # 테스트 기간(고정): 데이터 시작~끝을 YYYY.MM 로.
    def _ym(fy):
        y = int(fy)
        return f"{y}.{min(12, int((fy - y) * 12) + 1):02d}"
    period_txt = f"{_ym(row800['payload']['lines'][0]['pts'][0][0])}~{_ym(end800)}"
    draw.text((964, cy), period_txt, anchor="rm",
              fill="#aaaaaa", font=font(34, True))
    box = (164, 785, 964, 1540)   # 정규 플롯 위치(크기 고정)
    axis_top = axes(draw, box, axis_progress, x_end, y_top)
    left, top, right, bottom = box

    if y_top >= principal:
        hy = bottom - principal / y_top * (bottom - top)
        draw.line((left, hy, lerp(left, right, axis_progress), hy),
                  fill="#ffe14d", width=5)

    end_labels = []   # 종료점 라벨은 나중에 그려 항상 선 위로 올린다.

    def draw_lines(source_row, color_mode, limit):
        for idx, line in enumerate(source_row["payload"]["lines"]):
            pts = clip_points(line["pts"], limit)
            if ALT_YAXIS and color_mode == "ghost":
                pts = [p for p in pts if p[1] <= y_top]   # 축 초과분은 화면 위로 잘라냄
            if len(pts) < 2:
                continue
            xy = [
                 (left + (year - X0) / max(x_end - X0, .0001)
                 * (right - left) * axis_progress,
                 max(axis_top, bottom - val / max(y_top, 1) * (bottom - top)))
                for year, val in pts
            ]
            color = "#666666" if color_mode == "ghost" else COLORS[idx]
            draw.line(xy, fill=color, width=5 if color_mode == "ghost" else 9,
                      joint="curve")
            if color_mode != "ghost":
                ex, ey = xy[-1]
                draw.ellipse((ex - 7, ey - 7, ex + 7, ey + 7), fill=color)
                anchor = "ra" if ex > right - 175 else "la"
                tx = ex - 10 if anchor == "ra" else ex + 10
                ty = max(top + 12, ey - 18)
                # 완성=끝점 도달 → 최종 라벨(생존/파산)+흰 박스,
                # 리빌 중 → 이동하는 끝점의 현재 평가액을 투명 배경으로.
                final = limit >= line["pts"][-1][0] - .05
                short = MOS[idx].replace("생활비 ", "")   # "월 인출 200만원"
                value = line["end"] if final else money(pts[-1][1])
                end_labels.append((tx, ty, short, value, color, anchor, final))

    for ghost_row in ghost_rows:
        # 고스트(이전 원금)는 이미 완성 → 전체를 정지 상태로 그린다.
        ghost_end = max(line["pts"][-1][0] for line in ghost_row["payload"]["lines"])
        draw_lines(ghost_row, "ghost", ghost_end)
    if active_row is not None:
        draw_lines(active_row, "active", clip_end)

    # 가격 라벨: 1줄 "월 인출 XXX" + 2줄 값. 완성 라벨만 흰 배경, 리빌 중엔 투명. 항상 선 위.
    sf, vf = font(28), font(33, True)
    a2, d2 = vf.getmetrics()
    line_gap = a2 + d2
    for tx, ty, short, value, color, anchor, final in end_labels:
        block_w = max(sf.getlength(short), vf.getlength(value))
        if anchor == "ra":
            bx_l, bx_r = tx - block_w, tx
        else:
            bx_l, bx_r = tx, tx + block_w
        if final:
            draw.rounded_rectangle((bx_l - 12, ty - 6, bx_r + 12, ty + line_gap * 2 - 2),
                                   9, fill="#ffffff")
        draw.text((tx, ty), short, anchor=anchor, fill=color, font=sf)
        draw.text((tx, ty + line_gap), value, anchor=anchor, fill=color, font=vf)

    if held and SHOW_STAMP:
        # 판정은 데이터 기준: 월 $2,000(첫 선)이 30년 생존했는가.
        survived = DATA[int(principal)]["payload"]["lines"][0]["surv"]
        if survived:
            stamp(draw, "생 존", "#58d68d")
        else:
            stamp(draw, "파 산", "#ff4d8d")

    draw.text((984, 1710), "1/2", anchor="ra", fill="#777777", font=font(28))
    return image


def main():
    table = Image.open(EXPORTS / f"02-table{SUFFIX}.png").convert("RGB")
    table_reel = Image.new("RGB", (W, REEL_H), "#000000")
    table_reel.paste(table, (0, (REEL_H - table.height) // 2))
    graph_seconds, fade_seconds, table_seconds = 25.0, .5, 4.0
    total = round((graph_seconds + fade_seconds + table_seconds) * FPS)
    command = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{REEL_H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin
    for frame in range(total):
        t = frame / FPS
        if t < graph_seconds:
            image = render(t)
        elif t < graph_seconds + fade_seconds:
            image = Image.blend(render(graph_seconds), table_reel,
                                ease((t - graph_seconds) / fade_seconds))
        else:
            image = table_reel
        payload = memoryview(image.tobytes())
        while payload:
            written = process.stdin.write(payload)
            if not written:
                raise BrokenPipeError("ffmpeg rawvideo pipe closed")
            payload = payload[written:]
    process.stdin.close()
    if process.wait() != 0:
        raise SystemExit("ffmpeg render failed")
    print(f"created: {OUT}")


if __name__ == "__main__":
    main()
