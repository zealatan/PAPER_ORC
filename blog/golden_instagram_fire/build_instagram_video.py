#!/usr/bin/env python3
"""<STOCK> FIRE 그래프의 x/y축과 데이터가 함께 움직이는 인스타 영상.

종목 전환: SHORTS_STOCK=SPY (기본 QQQ). 라벨·데이터·출력명이 종목별로 갈린다.
"""

import json
import math
import os
import subprocess
from pathlib import Path

STOCK = os.environ.get("SHORTS_STOCK", "QQQ")
PREFIX = {"QQQ": "qqq", "SPY": "spy", "MO": "mo", "AAPL": "aapl",
          "QYLD": "qyld", "SCHD": "schd", "PG": "pg", "JEPI": "jepi",
          "HYNIX": "hynix", "SEC": "sec", "KTNG": "ktng"}.get(STOCK, STOCK.lower())
TICKER = STOCK
# 타이틀 표시명(티커 대신 풀네임). 길면 header에서 폰트 자동 축소.
NAME = {"QQQ": "나스닥 100 (QQQ)", "HYNIX": "SK하이닉스", "SEC": "삼성전자",
        "KTNG": "KT&G"}.get(STOCK, STOCK)
SUFFIX = "" if STOCK == "QQQ" else f"_{STOCK}"

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
EXPORTS = ROOT / "exports"
OUT = EXPORTS / f"{PREFIX}_fire_2cut_reel.mp4"
MONTHLY_DATA = ROOT / f"assets/data/{PREFIX}_fires_monthly.json"
DATA_SOURCE = MONTHLY_DATA if MONTHLY_DATA.exists() else ROOT / f"assets/data/{PREFIX}_fires.json"
_ALL = json.loads(DATA_SOURCE.read_text())
KRW = bool(_ALL[0]["payload"].get("krw"))          # 원화 종목(하이닉스 등) 감지
# 표시 원금 2종: USD $40만/$80만, KRW 4억/8억.
PRINCIPALS = (400_000_000, 800_000_000) if KRW else (400_000, 800_000)
DATA = {row["amt"]: row for row in _ALL if row["amt"] in PRINCIPALS}

# 은퇴 시작연도(x축 원점)는 데이터가 들고 있다(payload.x0). QQQ/SPY=2000, SCHD=2016.
X0 = int(next(iter(DATA.values()))["payload"].get("x0", 2000))
# 부제(편집 문구). 30년은 QQQ/SPY의 계획 지평, 짧은 이력 종목은 경과연수로.
PERIOD = {
    "QQQ": "2000년 은퇴 · 30년 · 물가연동 인출",
    "SPY": "2000년 은퇴 · 30년 · 물가연동 인출",
    "SCHD": "2016년 은퇴 · 10년 경과 · 물가연동 인출",
    "QYLD": "2015년 은퇴 · 11년 경과 · 물가연동 인출",
    "JEPI": "2020년 은퇴 · 6년 경과 · 물가연동 인출",
    "HYNIX": "2010년 은퇴 · 15년 경과 · 물가연동 인출",
    "SEC": "2010년 은퇴 · 15년 경과 · 물가연동 인출",
    "KTNG": "2005년 은퇴 · 21년 경과 · 물가연동 인출",
}.get(STOCK, f"{X0}년 은퇴 · 물가연동 인출")

W, H, REEL_H, FPS = 1080, 1350, 1920, 30
COLORS = ("#58a6ff", "#ff4d8d")
# 인출 라벨: USD 달러, KRW 만원.
MOS = (("월 생활비 인출 200만원", "월 생활비 인출 400만원") if KRW
       else ("월 생활비 인출 $2,000", "월 생활비 인출 $4,000"))
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def monthly_points(points):
    """분기 저장점을 월 간격으로 선형 보간해 애니메이션 끝점 이동을 촘촘하게 한다."""
    if len(points) < 2:
        return points
    out = []
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        months = max(1, round((x1 - x0) * 12))
        for month in range(months):
            ratio = month / months
            out.append([
                x0 + (x1 - x0) * ratio,
                round(y0 + (y1 - y0) * ratio),
            ])
    out.append(points[-1])
    return out


def clip_points(points, limit):
    """현재 x 위치까지 자르고, 다음 월 점과의 프레임별 보간 끝점을 붙인다."""
    if not points:
        return []
    out = []
    for index, point in enumerate(points):
        if point[0] <= limit:
            out.append(point)
            continue
        if out:
            previous = points[index - 1]
            span = point[0] - previous[0]
            if span > 0:
                ratio = max(0.0, min(1.0, (limit - previous[0]) / span))
                out.append([
                    limit,
                    previous[1] + (point[1] - previous[1]) * ratio,
                ])
        break
    return out


def keep_monthly_first_three_years(points, start_year=2000):
    """초기 3년은 월별, 이후는 분기별로 줄이되 마지막 점은 보존한다."""
    cutoff = start_year + 3
    early = [point for point in points if point[0] < cutoff]
    later = [point for point in points if point[0] >= cutoff]
    sampled = early + later[::3]
    if points and (not sampled or sampled[-1] != points[-1]):
        sampled.append(points[-1])
    return sampled


if DATA_SOURCE != MONTHLY_DATA:
    for _row in DATA.values():
        for _line in _row["payload"]["lines"]:
            _line["pts"] = monthly_points(_line["pts"])
else:
    for _row in DATA.values():
        for _line in _row["payload"]["lines"]:
            _line["pts"] = keep_monthly_first_three_years(_line["pts"])


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * ease(t)


def money(v):
    # y축 눈금 라벨. KRW=억/만, USD=$K/$M.
    if KRW:
        if v >= 1e8:
            return f"{v / 1e8:.0f}억"
        if v >= 1e4:
            return f"{v / 1e4:.0f}만"
        return "0"
    if v >= 1_000_000:
        return f"${v / 1_000_000:.1f}M"
    return f"${v / 1000:.0f}K"


def principal_label(v):
    # 카드 상단 은퇴 원금 표기. KRW=X억, USD=$X.
    return f"{round(v / 1e8)}억" if KRW else f"${v:,.0f}"


def header(d, logo_size=(0, 0)):
    # 2줄 타이틀(가로 중앙). 종목명은 파란 생존선 톤, 나머지 흰색. 로고 없음.
    cx = W // 2
    name, rest, line2 = NAME, "로 은퇴했다면", "얼마나 버텼을까?"
    line1 = name + rest
    size = 82
    while size > 46 and max(font(size, True).getlength(line1),
                            font(size, True).getlength(line2)) > 1000:
        size -= 2
    tf = font(size, True)
    asc, desc = tf.getmetrics()
    line_h = asc + desc
    # 제목 하단이 '은퇴 원금' 행(마커 y≈689) 위로 150px가 되게 배치(앵커 보정 +18).
    ty = 689 - 150 + 18 - (2 * line_h + 5)
    x1 = cx - tf.getlength(line1) / 2
    d.text((x1, ty), name, fill=COLORS[0], font=tf, anchor="la")
    d.text((x1 + tf.getlength(name), ty), rest, fill="#f5f5f5", font=tf, anchor="la")
    d.text((cx, ty + line_h + 5), line2, fill="#f5f5f5", font=tf, anchor="ma")
    return 0, 0


def graph_state(t):
    # $400K를 먼저 그리고, 축 전환 후 $800K를 그린다.
    if t < 3.6:
        amount = 400_000
        reveal = ease(t / 3.2)
        x_end = lerp(2001, 2012.4, reveal)
        y_top = 440_000
        transition = 0
    elif t < 4.4:
        amount = 800_000
        transition = ease((t - 3.6) / 0.8)
        reveal = 0
        x_end = lerp(2012.4, 2001, transition)
        y_top = lerp(440_000, 880_000, transition)
    else:
        amount = 800_000
        transition = 1
        reveal = ease((t - 4.4) / 4.1)
        x_end = lerp(2001, 2030, reveal)
        row = DATA[amount]
        visible_max = amount
        for line in row["payload"]["lines"]:
            visible_max = max(visible_max, *(v for year, v in line["pts"] if year <= x_end))
        y_top = max(880_000, math.ceil(visible_max / 200_000) * 200_000)
    return amount, reveal, x_end, y_top, transition


def render_graph(t):
    im = Image.new("RGB", (W, REEL_H), "#000000")
    d = ImageDraw.Draw(im)
    header(d)
    progress = ease(t / 16.4)

    def chart(amount, card_top):
        row = DATA[amount]
        final_year = max(line["pts"][-1][0] for line in row["payload"]["lines"])
        x_end = lerp(2000, final_year, progress)
        final_max = max(v for line in row["payload"]["lines"] for _, v in line["pts"])
        unit = 100_000 if amount == 400_000 else 200_000
        final_top = math.ceil(final_max / unit) * unit * 1.1
        # y축은 첫 프레임에 0→은퇴원금 범위로 시작한 뒤 위로 확장한다.
        y_top = lerp(amount, final_top, progress)

        d.rounded_rectangle((48, card_top, 1032, card_top + 462), 22,
                            fill="#080808", outline="#292929", width=2)
        d.text((78, card_top + 24), f"${amount:,}", fill="#ffffff",
               font=font(54, True))
        d.text((1002, card_top + 38), f"진행 {x_end:.1f}", anchor="ra",
               fill="#999999", font=font(31, True))
        left, right = 164, 1000
        top, bottom = card_top + 118, card_top + 385
        axis_right = lerp(left, right, progress)
        axis_top = top

        for i in range(3):
            value = y_top * i / 2
            y = bottom - (bottom - top) * i / 2
            d.line((left, y, axis_right, y), fill="#202020", width=2)
            d.text((left - 13, y), money(value), anchor="rm",
                   fill="#888888", font=font(25))
        x_tick_ids = (0,) if progress < .12 else ((0, 3) if progress < .28 else range(4))
        for i in x_tick_ids:
            year = 2000 + (x_end - 2000) * i / 3
            x = left + (right - left) * progress * i / 3
            d.line((x, axis_top, x, bottom), fill="#161616", width=1)
            year_label = f"{year:.1f}" if x_end - 2000 < 2 else f"{year:.0f}"
            d.text((x, bottom + 19), year_label, anchor="ma",
                   fill="#888888", font=font(25))
        d.line((left, bottom, axis_right, bottom), fill="#666666", width=3)
        d.line((left, bottom, left, axis_top), fill="#666666", width=3)

        if y_top >= amount:
            hy = bottom - amount / y_top * (bottom - top)
            d.line((left, hy, right, hy), fill="#ffe14d", width=3)
            d.text((right - 6, hy - 10), f"원금 ${amount:,}", anchor="rs",
                   fill="#ffe14d", font=font(25, True))
        else:
            d.text((right - 6, top + 8), f"축 확장 중 · 원금 ${amount:,}", anchor="ra",
                   fill="#ffe14d", font=font(25, True))

        for color, line in zip(COLORS, row["payload"]["lines"]):
            pts = clip_points(line["pts"], x_end)
            if len(pts) < 2:
                continue
            xy = [
                 (left + (year - 2000) / max(x_end - 2000, .0001)
                 * (right - left) * progress,
                 max(axis_top, bottom - val / max(y_top, 1) * (bottom - top)))
                for year, val in pts
            ]
            d.line(xy, fill=color, width=8, joint="curve")
            ex, ey = xy[-1]
            d.ellipse((ex - 5, ey - 5, ex + 5, ey + 5), fill=color)
            if x_end >= line["pts"][-1][0] - .05:
                anchor = "ra" if ex > right - 130 else "la"
                tx = ex - 8 if anchor == "ra" else ex + 8
                d.text((tx, max(top + 10, ey - 12)), line["end"], anchor=anchor,
                       fill=color, font=font(25, True))

    chart(400_000, 625)
    chart(800_000, 1120)

    d.text((68, 1810), "배당투자 실험실 · 과거 데이터 백테스트",
           fill="#777777", font=font(28))
    d.text((984, 1810), "1/2", anchor="ra", fill="#777777", font=font(28))
    return im


def main():
    table = Image.open(EXPORTS / f"02-table{SUFFIX}.png").convert("RGB")
    table_reel = Image.new("RGB", (W, REEL_H), "#000000")
    table_reel.paste(table, (0, (REEL_H - H) // 2))
    graph_seconds = 17.5
    fade_seconds = 0.5
    table_seconds = 4.0
    total_frames = round((graph_seconds + fade_seconds + table_seconds) * FPS)
    command = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{REEL_H}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin
    for frame in range(total_frames):
        t = frame / FPS
        if t < graph_seconds:
            image = render_graph(t)
        elif t < graph_seconds + fade_seconds:
            image = Image.blend(
                render_graph(graph_seconds),
                table_reel,
                ease((t - graph_seconds) / fade_seconds),
            )
        else:
            image = table_reel
        # 대형 raw frame은 pipe가 부분 write를 반환할 수 있으므로 끝까지 전송한다.
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
