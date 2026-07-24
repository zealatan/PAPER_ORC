#!/usr/bin/env python3
"""stock_alert 프로젝트 전용 페이지 생성기 (gen_dec_edit.py 와 독립).

배투실 '주간 전고점 대비 낙폭 알림' 프로젝트의 대시보드 HTML을 생성한다.
- 출력: blog/architecture_docs/stock_alert/dec_pipeline.html  (이 파일 하나만 씀)
- 루트 인덱스(dec_pipeline.html)·gen_dec_edit.py 는 절대 건드리지 않는다.
  (루트 카드는 gen_dec_edit 의 `architecture_docs/*/dec_pipeline.html` glob 이 자동 포함)
- 유니버스 종목 수는 global_cup_suite 의 티커 CSV 에서 라이브로 읽는다(하드코딩 금지).
- 주간 스캔 결과가 있으면(data/weekN.json) 랭킹 표를 렌더, 없으면 '스캔 대기' 표시.

사용: python3 blog/stock_alert/gen_page.py
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from html import escape as esc
from pathlib import Path

# ── 경로 ────────────────────────────────────────────────────────────────────────
SELF = Path(__file__).resolve()
PROJ = SELF.parent                                  # blog/stock_alert
BLOG = PROJ.parent                                  # blog
ROOT = BLOG.parent                                  # PAPER_ORC
DATA_DIR = PROJ / "data"                            # 주간 스캔 결과 JSON
TICKERS = ROOT / "global_cup_suite" / "data"        # 재사용 유니버스
OUT = BLOG / "architecture_docs" / "stock_alert" / "dec_pipeline.html"

ETF_CATS = ("ETF", "Covered Call ETF")

# ── 유니버스 집계 (라이브) ────────────────────────────────────────────────────────
def _rows(name: str) -> list[dict]:
    p = TICKERS / f"tickers_{name}.csv"
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def universe_counts() -> dict:
    """앱 페이지 기준: 나라=Stock 만, ETF=전 나라 ETF 합산."""
    files = {"us": "미국", "korea": "한국", "japan": "일본", "eu": "eu", "global": "global"}
    stock = {}
    etf_total = 0
    for key in files:
        r = _rows(key)
        stock[key] = sum(1 for x in r if x["category"].strip() == "Stock")
        etf_total += sum(1 for x in r if x["category"].strip() in ETF_CATS)
    return {"us": stock["us"], "korea": stock["korea"], "etf": etf_total}


# ── 주간 스캔 결과 로드 ──────────────────────────────────────────────────────────
def load_weeks() -> list[dict]:
    """data/week*.json 을 주차 순으로 반환. 각 파일 = {week, date, markets:{...}} 형태 가정."""
    if not DATA_DIR.exists():
        return []
    weeks = []
    for p in sorted(DATA_DIR.glob("week*.json")):
        try:
            weeks.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            pass
    return weeks


# ── HTML 조각 ───────────────────────────────────────────────────────────────────
NAV = (
    '<nav style="font-family:ui-monospace,Consolas,monospace;font-size:12.5px;'
    'padding:9px 16px;background:#17282a;color:#cfd3d1;display:flex;gap:15px;'
    'flex-wrap:wrap;align-items:center;position:sticky;top:0;z-index:9999;'
    'border-bottom:1px solid #2c4144">'
    '<span style="color:#c98a1a;font-weight:700;letter-spacing:.04em">배투실 문서</span>'
    '<a href="../dec_pipeline.html" style="color:#cfd3d1;text-decoration:none">◆ 종목 선택</a>'
    '<a href="../top_pipeline_standalone.html" style="color:#cfd3d1;text-decoration:none">파이프라인 허브</a>'
    '<a href="../production_manual.html" style="color:#cfd3d1;text-decoration:none">제작 매뉴얼</a>'
    '<a href="../research.html" style="color:#cfd3d1;text-decoration:none">리서치</a>'
    '<span style="color:#e8a33d;font-weight:700">STOCK_ALERT</span></nav>'
)

CSS = (
    'body{margin:0;font-family:"Pretendard","Apple SD Gothic Neo",sans-serif;'
    'background:#f2ede2;color:#17282a;padding:0 20px}'
    '.wrap{max-width:820px;margin:0 auto;padding:44px 0 80px}'
    '.eyebrow{font-family:ui-monospace,monospace;font-size:12px;color:#c98a1a;'
    'font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px}'
    'h1{font-size:31px;font-weight:800;margin:0 0 8px;letter-spacing:-.02em}'
    '.lede{color:#5c6d6b;margin:0 0 28px;font-size:15px;line-height:1.6}'
    'h2{font-size:15px;font-weight:800;margin:34px 0 12px;letter-spacing:-.01em;'
    'border-left:3px solid #c98a1a;padding-left:9px}'
    '.uni{display:flex;gap:10px;flex-wrap:wrap}'
    '.uni .c{flex:1;min-width:130px;background:#fbf8f1;border:1px solid #ddd4c3;'
    'border-radius:12px;padding:15px 17px}'
    '.uni .c .n{font-size:27px;font-weight:800;font-family:ui-monospace,monospace;color:#17282a}'
    '.uni .c .k{font-size:12.5px;color:#5c6d6b;margin-top:2px}'
    '.pipe{display:flex;gap:7px;flex-wrap:wrap;align-items:center;font-size:13px;color:#3d4f4d}'
    '.pipe .s{background:#fbf8f1;border:1px solid #ddd4c3;border-radius:8px;padding:7px 11px}'
    '.pipe .a{color:#c98a1a;font-weight:800}'
    '.plan{background:#fbf8f1;border:1px solid #ddd4c3;border-radius:12px;padding:6px 20px}'
    '.plan li{margin:9px 0;font-size:14px;line-height:1.55}'
    '.plan b{color:#17282a}'
    'table{width:100%;border-collapse:collapse;font-size:13.5px;margin-top:4px}'
    'th,td{text-align:left;padding:8px 10px;border-bottom:1px solid #e4dcc9}'
    'th{color:#5c6d6b;font-weight:700;font-size:12px}'
    'td.dd{font-family:ui-monospace,monospace;font-weight:800;color:#c0392b;text-align:right}'
    '.week{background:#fbf8f1;border:1px solid #ddd4c3;border-radius:12px;padding:16px 20px;margin-bottom:14px}'
    '.badge{display:inline-block;font-family:ui-monospace,monospace;font-size:11px;'
    'font-weight:700;padding:2px 8px;border-radius:6px;background:#17282a;color:#f2ede2}'
    '.empty{color:#8a9694;font-size:13.5px;padding:14px 0}'
    '.foot{margin-top:40px;font-size:12px;color:#8a9694;line-height:1.6}'
    '.foot code{background:#f4eee1;padding:1px 6px;border-radius:5px}'
)


def _market_table(name: str, rows: list[dict]) -> str:
    body = "".join(
        f'<tr><td>{i+1}</td><td>{esc(str(r.get("label", r.get("ticker", ""))))}</td>'
        f'<td class="dd">{r.get("drawdown_pct", 0):.1f}%</td></tr>'
        for i, r in enumerate(rows)
    )
    return (f'<h2>{esc(name)}</h2><table><tr><th>#</th><th>종목</th>'
            f'<th style="text-align:right">전고점 대비</th></tr>{body}</table>')


def _weeks_html(weeks: list[dict]) -> str:
    if not weeks:
        return ('<div class="empty">아직 스캔 결과가 없습니다. '
                '<code>data/week1.json</code> 이 생성되면 여기에 시장별 낙폭 랭킹이 표시됩니다.</div>')
    out = []
    for w in reversed(weeks):                       # 최신 주차 먼저
        wk = esc(str(w.get("week", "?")))
        dt = esc(str(w.get("date", "")))
        mk = w.get("markets", {})
        tables = "".join(_market_table(nm, rows) for nm, rows in mk.items())
        out.append(f'<div class="week"><span class="badge">week {wk}</span> '
                   f'<span style="color:#5c6d6b;font-size:12.5px"> · {dt}</span>{tables}</div>')
    return "".join(out)


# ── 빌드 ────────────────────────────────────────────────────────────────────────
def build() -> str:
    u = universe_counts()
    weeks = load_weeks()

    uni = (
        f'<div class="uni">'
        f'<div class="c"><div class="n">{u["us"]}</div><div class="k">🇺🇸 미국 주식</div></div>'
        f'<div class="c"><div class="n">{u["korea"]}</div><div class="k">🇰🇷 한국 주식</div></div>'
        f'<div class="c"><div class="n">{u["etf"]}</div><div class="k">📊 ETF (전체)</div></div>'
        f'</div>'
    )

    pipe = (
        '<div class="pipe">'
        '<span class="s">주간 스캔<br>scan_market ×3</span><span class="a">→</span>'
        '<span class="s">낙폭 랭킹<br>TOP N</span><span class="a">→</span>'
        '<span class="s">뉴스 큐레이션<br>왜 떨어졌나</span><span class="a">→</span>'
        '<span class="s">카운트다운 덱</span><span class="a">→</span>'
        '<span class="s">더빙·렌더</span><span class="a">→</span>'
        '<span class="s">롱폼 + 쇼츠</span></div>'
    )

    plan = (
        '<ul class="plan">'
        '<li><b>컨셉</b> — 매주 전고점 대비 낙폭이 큰 종목을 미국·한국·ETF 통합 유니버스에서 랭킹</li>'
        '<li><b>포맷</b> — 롱폼 1편 + 쇼츠 2~3편 (3시장 통합 1영상)</li>'
        '<li><b>앵글</b> — 낙폭 랭킹 중심(단순). 각 종목: 낙폭 −X% · 전고점→현재 차트 · 한 줄 이유</li>'
        '<li><b>전고점 정의</b> — 마지막 ZigZag 전저점 이후 최고가 (스윙고점, ATH 아님). '
        'threshold 15% (trigger %와 별개 · high_scanner.py)</li>'
        '</ul>'
    )

    return (
        '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>STOCK_ALERT — 주간 전고점 낙폭 알림 · 배투실</title>'
        f'<style>{CSS}</style></head><body>{NAV}<div class="wrap">'
        '<div class="eyebrow">배투실 · 영상 파이프라인 · 신규 프로젝트</div>'
        '<h1>STOCK_ALERT — 주간 전고점 대비 낙폭 알림</h1>'
        '<p class="lede">매주 미국주식·한국주식·ETF 통합 유니버스를 스캔해 '
        '전고점에서 가장 많이 무너진 종목을 랭킹으로 알려주는 정기 콘텐츠. '
        '롱폼 + 쇼츠로 제작한다.</p>'
        f'<h2>유니버스 (라이브)</h2>{uni}'
        f'<h2>파이프라인</h2>{pipe}'
        f'<h2>확정 기획</h2>{plan}'
        f'<h2>주간 리포트</h2>{_weeks_html(weeks)}'
        '<div class="foot">이 페이지 = <code>blog/stock_alert/gen_page.py</code> 실행으로 생성 '
        '(gen_dec_edit.py 와 독립). 루트 인덱스 카드는 <code>architecture_docs/*/dec_pipeline.html</code> '
        'glob 이 자동 포함.</div>'
        '</div></body></html>'
    )


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    html = build()
    OUT.write_text(html, encoding="utf-8")
    u = universe_counts()
    print(f"✓ {OUT.relative_to(BLOG)} ({len(html)//1024}KB · "
          f"유니버스 미국 {u['us']}·한국 {u['korea']}·ETF {u['etf']} · "
          f"주간 {len(load_weeks())}건)")


if __name__ == "__main__":
    main()
