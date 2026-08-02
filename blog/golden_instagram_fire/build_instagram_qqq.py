#!/usr/bin/env python3
"""<STOCK> FIRE 데이터로 1080×1350 인스타 캐러셀 2장을 만든다.

종목 전환: SHORTS_STOCK=SPY python3 build_instagram_qqq.py (기본 QQQ).
QQQ는 기존 파일명(01-backtest.png/02-table.png) 유지, 그 외는 _<STOCK> 접미사.
"""

import html
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

STOCK = os.environ.get("SHORTS_STOCK", "QQQ")
# 종목별 라벨·부제·x축끝·표 코멘트(원금 20/40/80만 표시 기준). 새 종목은 여기에 한 줄 추가.
# x1=캐러셀 x축 끝 연도 라벨(x0는 데이터가 보유). sub=부제.
CONFIG = {
    "QQQ": {"prefix": "qqq", "ticker": "QQQ", "name": "나스닥 100 (QQQ)", "x1": 2030,
            "sub": "2000년 은퇴 · 30년 · 물가연동 인출 · 배당 생활비 사용",
            "note": "$80만·월 $2,000 인출도 ’12년 파산.\n"
                    "2000년 고점 은퇴는 모든 조합이 중도 파산."},
    "SPY": {"prefix": "spy", "ticker": "SPY", "x1": 2030,
            "sub": "2000년 은퇴 · 30년 · 물가연동 인출 · 배당 생활비 사용",
            "note": "$80만·월 $2,000만 30년 생존.\n"
                    "$40만과 월 $4,000 인출은 모두 중도 파산."},
    "SCHD": {"prefix": "schd", "ticker": "SCHD", "x1": 2027,
             "sub": "2016년 은퇴 · 10년 경과 · 물가연동 인출 · 배당 생활비 사용",
             "note": "$40만·$80만 모두 월 $4,000 인출까지 생존.\n"
                     "배당성장으로 원금이 오히려 크게 불어남."},
    "QYLD": {"prefix": "qyld", "ticker": "QYLD", "x1": 2027,
             "sub": "2015년 은퇴 · 11년 경과 · 물가연동 인출 · 배당 생활비 사용",
             "note": "$80만은 월 $4,000 인출도 생존.\n"
                     "$40만은 월 $4,000이면 ’24년 파산."},
    "TQQQ": {"prefix": "tqqq", "ticker": "TQQQ", "name": "TQQQ (나스닥 3배)", "x1": 2027,
             "sub": "2022년 고점 은퇴 · 나스닥 3배 레버리지 · 물가연동 인출 · 배당 생활비 사용",
             "note": "$40만은 월 $4,000 인출 시 ’26년 파산, 월 $2,000도 원금 밑돎.\n"
                     "고점 직후 -80% 폭락+인출 — 같은 TQQQ라도 시작 시점이 생존을 가름."},
    "JEPI": {"prefix": "jepi", "ticker": "JEPI", "x1": 2027,
             "sub": "2020년 은퇴 · 6년 경과 · 물가연동 인출 · 배당 생활비 사용",
             "note": "$40만·$80만 모두 월 $4,000 인출까지 생존.\n"
                     "고배당 인컴으로 6년간 원금 유지·증가."},
    "HYNIX": {"prefix": "hynix", "ticker": "HYNIX", "name": "SK하이닉스", "x1": 2027,
              "sub": "2010년 은퇴 · 15년 경과 · 물가연동 인출 · 배당 생활비 사용",
              "note": "4억은 월 200만원만 생존, 월 400만원은 ’25년 파산.\n"
                      "8억은 둘 다 생존 — 반도체 초강세로 원금 급증."},
    "SEC": {"prefix": "sec", "ticker": "SEC", "name": "삼성전자", "x1": 2027,
            "sub": "2010년 은퇴 · 15년 경과 · 물가연동 인출 · 배당 생활비 사용",
            "note": "4억·8억 모두 월 400만원 인출까지 생존.\n"
                    "반도체 대표주로 15년간 원금 크게 증가."},
    "KTNG": {"prefix": "ktng", "ticker": "KTNG", "name": "KT&G", "x1": 2027,
             "sub": "2005년 은퇴 · 21년 경과 · 물가연동 인출 · 배당 생활비 사용",
             "note": "4억·8억 모두 월 400만원 인출까지 생존.\n"
                     "대표 고배당 방어주로 원금 꾸준히 증가."},
    "SFIRE": {"prefix": "sfire", "ticker": "SFIRE", "name": "삼성화재", "x1": 2027,
              "sub": "2000년 은퇴 · 26년 경과 · 물가연동 인출 · 배당 생활비 사용",
              "note": "4억은 월 400만원 인출 시 ’23년 파산.\n"
                      "8억은 둘 다 생존 — 배당·주가로 원금 크게 증가."},
    "KT": {"prefix": "kt", "ticker": "KT", "name": "KT", "x1": 2010,
           "sub": "2000년 은퇴(통신버블 고점) · 물가연동 인출 · 배당 생활비 사용",
           "note": "8억도 월 200만원에 ’09년 파산, 4억은 ’04년.\n"
                   "2000년 통신 고점 은퇴는 모든 조합이 중도 파산."},
}
CFG = CONFIG[STOCK]
TICKER = CFG["ticker"]
NAME = CFG.get("name", TICKER)   # 타이틀 표시명(티커 대신 풀네임)
SUB = CFG["sub"]
SUFFIX = "" if STOCK == "QQQ" else f"_{STOCK}"

ROOT = Path(__file__).resolve().parent
MONTHLY_DATA = ROOT / f"assets/data/{CFG['prefix']}_fires_monthly.json"
DATA_SOURCE = MONTHLY_DATA if MONTHLY_DATA.exists() else ROOT / f"assets/data/{CFG['prefix']}_fires.json"
ALL_DATA = json.loads(DATA_SOURCE.read_text())
KRW = bool(ALL_DATA[0]["payload"].get("krw"))    # 원화 종목 감지
PRINCIPALS = (400_000_000, 800_000_000) if KRW else (400_000, 800_000)
DATA = [row for row in ALL_DATA if row["amt"] in PRINCIPALS]
X0 = int(DATA[0]["payload"].get("x0", 2000))   # x축 원점(은퇴연도)
X1 = CFG["x1"]                                   # x축 끝 라벨
SLIDES = ROOT / "slides"
EXPORTS = ROOT / "exports"
W, H = 1080, 1350
COLORS = ("#58a6ff", "#ff4d8d")
MOS = (("월 생활비 인출 200만원", "월 생활비 인출 400만원") if KRW
       else ("월 생활비 인출 $2,000", "월 생활비 인출 $4,000"))
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def money(value):
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    return f"${value / 1_000:.0f}K"


def shell(title, kicker, body, page):
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<style>
*{{box-sizing:border-box}}html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden}}
body{{background:#000;color:#f5f5f5;font-family:Arial,'Noto Sans KR',sans-serif}}
.page{{width:{W}px;height:{H}px;padding:70px 68px 56px;position:relative}}
.kicker{{color:#ff4d8d;font-size:25px;font-weight:800;letter-spacing:2.2px;margin-bottom:14px}}
h1{{font-size:56px;line-height:1.12;margin:0;font-weight:900;letter-spacing:-2.5px}}
.sub{{color:#aaa;font-size:23px;margin-top:15px}}.body{{margin-top:44px}}
.foot{{position:absolute;bottom:32px;left:68px;right:68px;color:#777;font-size:17px;
display:flex;justify-content:space-between}}.brand{{color:#ddd;font-weight:800}}
</style></head><body><main class="page">
<div class="kicker">{kicker}</div><h1>{title}</h1>
<div class="sub">{SUB}</div>
<section class="body">{body}</section>
<footer class="foot"><span><b class="brand">배당투자 실험실</b> · 과거 데이터 백테스트</span><span>{page}/2</span></footer>
</main></body></html>"""


def graph_slide():
    cards = []
    for row in DATA:
        lines = row["payload"]["lines"]
        all_pts = [p for line in lines for p in line["pts"]]
        x0, x1 = X0, X1
        ymax = max(p[1] for p in all_pts) * 1.08
        gx, gy, gw, gh = 26, 63, 810, 105
        paths = []
        for color, line in zip(COLORS, lines):
            pts = []
            for year, val in line["pts"]:
                x = gx + (year - x0) / (x1 - x0) * gw
                y = gy + gh - val / ymax * gh
                pts.append(f"{x:.1f},{y:.1f}")
            paths.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" '
                         'stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
        result = " · ".join(html.escape(line["end"]) for line in lines)
        cards.append(f"""<div class="card">
<div class="amount">{html.escape(row["hook"])}</div><div class="result">{result}</div>
<svg viewBox="0 0 860 190" aria-label="{html.escape(row['hook'])} 백테스트">
<line x1="{gx}" y1="{gy+gh}" x2="{gx+gw}" y2="{gy+gh}" stroke="#333" stroke-width="2"/>
<text x="{gx}" y="188">{X0}</text><text x="{gx+gw}" y="188" text-anchor="end">{X1}</text>
{''.join(paths)}</svg></div>""")
    legend = "".join(f'<span><i style="background:{c}"></i>{m}</span>' for c, m in zip(COLORS, MOS))
    body = f"""<style>
.legend{{display:flex;gap:28px;margin-bottom:20px;color:#bbb;font-size:20px}}
.legend span{{display:flex;align-items:center;gap:9px}}.legend i{{width:24px;height:5px;border-radius:4px}}
.card{{height:174px;border:1px solid #242424;border-radius:16px;margin-bottom:13px;position:relative;
background:#090909;padding:15px 22px}}.amount{{font-size:27px;font-weight:900}}
.result{{position:absolute;right:22px;top:18px;color:#aaa;font-size:17px}}
svg{{position:absolute;left:22px;right:22px;top:42px;width:calc(100% - 44px);height:126px}}
svg text{{fill:#666;font-size:15px}}
</style><div class="legend">{legend}</div>{''.join(cards)}"""
    return shell(f"{TICKER}로 은퇴했다면<br>얼마나 버텼을까?", f"{TICKER} FIRE BACKTEST", body, 1)


def table_slide():
    rows = []
    for row in DATA:
        cells = []
        for line in row["payload"]["lines"]:
            cls = "ok" if line["surv"] else "bad"
            cells.append(f'<td class="{cls}">{html.escape(line["end"])}</td>')
        rows.append(f'<tr><th>{html.escape(row["hook"])}</th>{"".join(cells)}</tr>')
    body = f"""<style>
table{{width:100%;border-collapse:separate;border-spacing:0;border:1px solid #292929;border-radius:18px;
overflow:hidden;background:#080808}}th,td{{height:112px;border-right:1px solid #222;border-bottom:1px solid #222;
text-align:center;padding:12px}}thead th{{height:82px;color:#aaa;font-size:21px;background:#101010}}
tbody th{{font-size:25px;color:#fff;background:#0d0d0d}}td{{font-size:22px;font-weight:800}}
tr:last-child th,tr:last-child td{{border-bottom:0}}th:last-child,td:last-child{{border-right:0}}
.ok{{color:#58d68d}}.bad{{color:#ff5f70}}.read{{margin-top:28px;border-left:5px solid #ff4d8d;
padding:4px 0 4px 22px;color:#ddd;font-size:24px;line-height:1.55}}.note{{margin-top:25px;color:#777;font-size:17px;line-height:1.5}}
</style><table><thead><tr><th>은퇴 원금</th><th>{MOS[0]}</th><th>{MOS[1]}</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<div class="read">{CFG["note"].replace(chr(10), "<br>")}</div>
<div class="note">배당소득세 15% 반영 · 인출액은 물가에 따라 증가<br>
투자 권유가 아니며 과거 성과는 미래 수익을 보장하지 않습니다.</div>"""
    return shell("은퇴 원금 × 월 생활비<br>생존 결과", f"{TICKER} FIRE RESULT", body, 2)


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)


def header(draw, title, page):
    # 킥커(XXX FIRE ...) 삭제. 타이틀·부제만.
    draw.multiline_text((68, 84), title, fill="#f5f5f5", font=font(54, True),
                        spacing=4)
    draw.text((68, 226), SUB, fill="#999999", font=font(22))
    draw.text((68, 1300), "배당투자 실험실 · 과거 데이터 백테스트",
              fill="#777777", font=font(17))
    draw.text((984, 1300), f"{page}/2", anchor="ra", fill="#777777", font=font(17))


def render_graph(path):
    im = Image.new("RGB", (W, H), "#000000")
    d = ImageDraw.Draw(im)
    header(d, f"{NAME}로 은퇴했다면\n얼마나 버텼을까?", 1)
    lx = 68
    for color, label in zip(COLORS, MOS):
        d.rounded_rectangle((lx, 331, lx + 25, 337), 3, fill=color)
        d.text((lx + 34, 319), label, fill="#bbbbbb", font=font(19))
        lx += 180
    for idx, row in enumerate(DATA):
        top = 395 + idx * 350
        d.rounded_rectangle((68, top, 1012, top + 316), 16, fill="#090909",
                            outline="#242424", width=2)
        d.text((94, top + 24), row["hook"], fill="#ffffff", font=font(34, True))
        summary = " · ".join(line["end"] for line in row["payload"]["lines"])
        d.text((984, top + 31), summary, anchor="ra", fill="#999999", font=font(20))
        gx0, gx1, gy0, gy1 = 96, 982, top + 102, top + 267
        d.line((gx0, gy1, gx1, gy1), fill="#333333", width=2)
        points = [p for line in row["payload"]["lines"] for p in line["pts"]]
        ymax = max(p[1] for p in points) * 1.08
        for color, line in zip(COLORS, row["payload"]["lines"]):
            xy = [(gx0 + (year - X0) / (X1 - X0) * (gx1 - gx0),
                   gy1 - val / ymax * (gy1 - gy0)) for year, val in line["pts"]]
            d.line(xy, fill=color, width=5, joint="curve")
        d.text((gx0, top + 272), str(X0), fill="#666666", font=font(17))
        d.text((gx1, top + 272), str(X1), anchor="ra", fill="#666666", font=font(17))
    im.save(path, quality=95)


def render_table(path):
    im = Image.new("RGB", (W, H), "#000000")
    d = ImageDraw.Draw(im)
    header(d, "은퇴 원금 × 월 생활비\n생존 결과", 2)
    x = (68, 380, 696, 1012)
    y0, hh, rh = 370, 96, 155
    d.rounded_rectangle((x[0], y0, x[-1], y0 + hh + rh * len(DATA)), 18,
                        fill="#080808", outline="#292929", width=2)
    heads = ("은퇴 원금", *MOS)
    for i, text in enumerate(heads):
        d.rectangle((x[i], y0, x[i + 1], y0 + hh), fill="#101010")
        # 인출 열 라벨은 길어서 폭에 맞게 축소(원금 열은 32 유지).
        d.text(((x[i] + x[i + 1]) / 2, y0 + hh / 2), text, anchor="mm",
               fill="#aaaaaa", font=font(32 if i == 0 else 27, True))
    for r, row in enumerate(DATA):
        yt, yb = y0 + hh + r * rh, y0 + hh + (r + 1) * rh
        d.rectangle((x[0], yt, x[1], yb), fill="#0d0d0d")
        d.text(((x[0] + x[1]) / 2, (yt + yb) / 2), row["hook"], anchor="mm",
               fill="#ffffff", font=font(38, True))
        for c, line in enumerate(row["payload"]["lines"], 1):
            color = "#58d68d" if line["surv"] else "#ff5f70"
            result = line["end"].replace("생존 ", "생존\n")
            d.multiline_text(((x[c] + x[c + 1]) / 2, (yt + yb) / 2), result,
                             anchor="mm", align="center", spacing=8,
                             fill=color, font=font(34, True))
        d.line((x[0], yb, x[-1], yb), fill="#222222", width=2)
    for xx in x[1:-1]:
        d.line((xx, y0, xx, y0 + hh + rh * len(DATA)), fill="#222222", width=2)
    d.rectangle((68, 970, 73, 1060), fill="#ff4d8d")
    d.text((94, 969), CFG["note"],
           fill="#dddddd", font=font(23, True), spacing=10)
    tax_disp = "15.4%" if KRW else "15%"
    d.multiline_text((68, 1100),
                     f"{X0}년 첫 거래일 종가 매수 기준 · 배당소득세 {tax_disp} 원천징수 · 인출액 물가연동\n"
                     "배당은 생활비로 먼저 쓰고 잉여만 재투자 · 과거 데이터 백테스트\n"
                     "투자 권유가 아니며 과거 성과는 미래 수익을 보장하지 않습니다.",
                     fill="#777777", font=font(16), spacing=6)
    im.save(path, quality=95)


def main():
    SLIDES.mkdir(exist_ok=True)
    EXPORTS.mkdir(exist_ok=True)
    pages = ((f"01-backtest{SUFFIX}", graph_slide()), (f"02-table{SUFFIX}", table_slide()))
    for name, markup in pages:
        path = SLIDES / f"{name}.html"
        path.write_text(markup)
    render_graph(EXPORTS / f"01-backtest{SUFFIX}.png")
    render_table(EXPORTS / f"02-table{SUFFIX}.png")
    print("created:", *(str(EXPORTS / f"{name}.png") for name, _ in pages), sep="\n")


if __name__ == "__main__":
    main()
