#!/usr/bin/env python3
"""주간 전고점 대비 낙폭 스캔 러너 → data/weekN.json 생성.

global_cup 엔진(high_scanner.scan_market) 재사용. 미국주식·한국주식·ETF 3시장을
스캔해 낙폭 깊은 순 TOP5 + 통합 TOP3를 뽑아 DECK_DESIGN.md 데이터 계약대로 저장.

전고점 = 마지막 ZigZag 전저점 이후 최고가(스윙고점) · threshold 15%(SCAN_THRESHOLD).

사용:
  python3 stock_alert/weekly_scan.py                # 전체 스캔(수십 분, week=1)
  python3 stock_alert/weekly_scan.py --week 2       # 주차 지정
  python3 stock_alert/weekly_scan.py --limit 6      # 시장별 앞 6종목만(빠른 테스트)
  python3 stock_alert/weekly_scan.py --top 5 --top3 3
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

SELF = Path(__file__).resolve()
PROJ = SELF.parent                      # blog/stock_alert
ROOT = PROJ.parent.parent               # PAPER_ORC
DATA = PROJ / "data"
TICKERS = ROOT / "global_cup_suite" / "data"    # 재사용 유니버스(이미 시총/AUM 내림차순 구축)
sys.path.insert(0, str(ROOT / "global_cup_suite"))

from global_cup.high_scanner import scan_market                # noqa: E402
from global_cup.data_loader import download_price, get_close_series  # noqa: E402

LOOKBACK_YEARS = 6      # 직전 전고점 포착에 충분한 창
ETF_CATS = ("ETF", "Covered Call ETF")

# 레버리지·인버스 ETF 제외 패턴(이름 기반). "2차전지" 등 섹터명은 매칭 안 되게 주의.
LEV = re.compile(
    r"레버리지|인버스|곱버스|[23]배|[23]X\b|leverage|inverse|ultrapro|"
    r"ultra\s|direxion|bull\s?[23]|bear\s?[23]|-1x|\b[23]x\b",
    re.I,
)


def _csv(name: str) -> list[dict]:
    p = TICKERS / f"tickers_{name}.csv"
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def _exclude() -> set:
    f = DATA / "exclude.json"
    if f.exists():
        try:
            return set(json.loads(f.read_text(encoding="utf-8")).get("exclude", []))
        except Exception:
            pass
    return set()


def candidates(pool: int) -> dict[str, dict[str, str]]:
    """시장별 후보 {label: ticker}.
    - 미국/한국/유럽: Stock 상위 pool개(CSV=시총 내림차순)
    - ETF: 미국 AUM 상위 pool//2 + 한국 AUM 상위 pool//2, 레버리지/인버스 제외
    - data/exclude.json 티커는 후보에서 제외 → 다음 순위가 채움.
    """
    ex = _exclude()

    def stocks(f):
        return [(r["label"], r["ticker"]) for r in _csv(f)
                if r["category"].strip() == "Stock" and r["ticker"] not in ex]

    def etfs(f):
        return [(r["label"], r["ticker"]) for r in _csv(f)
                if r["category"].strip() in ETF_CATS and not LEV.search(r["label"]) and r["ticker"] not in ex]

    half = pool // 2
    return {
        "ETF": dict(etfs("us")[:half] + etfs("korea")[:half]),
        "미국": dict(stocks("us")[:pool]),
        "한국": dict(stocks("korea")[:pool]),
        "유럽": dict(stocks("eu")[:pool]),
    }


def _row(r: dict, market: str) -> dict:
    def s(v):
        try:
            return v.strftime("%Y-%m-%d")
        except Exception:
            return str(v)
    return {
        "label": r["label"], "ticker": r["ticker"], "market": market,
        "high_date": s(r["high_date"]), "high_price": round(float(r["high_price"]), 2),
        "current_price": round(float(r["current_price"]), 2), "current_date": s(r["current_date"]),
        "drawdown_pct": round(float(r["drawdown_pct"]), 2),
        "reason": "",       # 뉴스 큐레이션 수동 슬롯
    }


HIST_START = date(2000, 1, 1)     # 차트 = 2000년~현재(없으면 상장 이후 자동)


def _enrich(row: dict, n: int = 80) -> dict:
    """drawcard 확장 데이터: 전체 히스토리(2000~/상장이후) 가격경로 + 낙폭 횟수(20/30/50).
    build_drawdown_cycles 로 전 기간 고점→저점 사이클을 세어 각 깊이 도달 횟수 집계(누적 '이상').
    """
    from global_cup.golden_engine import build_drawdown_cycles
    try:
        import pandas as pd
        df = download_price(row["ticker"], HIST_START, date.today())
        c = get_close_series(df)
        if c.empty:
            return {"pts": [], "counts": {"d20": 0, "d30": 0, "d50": 0}, "listed": ""}
        step = max(1, len(c) // n)
        s = c.iloc[::step]
        if s.index[-1] != c.index[-1]:
            s = pd.concat([s, c.iloc[[-1]]])
        pts = [[i, round(float(v), 2)] for i, v in enumerate(s)]
        cyc = build_drawdown_cycles(c, row["label"], row["ticker"], "Scan", threshold=0.10)
        dd = [x.get("하락률 숫자", 0.0) for x in (cyc or [])]   # 리스트 of dict, '하락률 숫자'=음수
        def cnt(th):
            return int(sum(1 for x in dd if x <= -th))
        return {"pts": pts, "counts": {"d20": cnt(20), "d30": cnt(30), "d50": cnt(50)},
                "listed": s.index[0].strftime("%Y-%m-%d")}
    except Exception:
        return {"pts": [], "counts": {"d20": 0, "d30": 0, "d50": 0}, "listed": ""}


def run(week: int, top: int, top3: int, pool: int) -> dict:
    end = date.today()
    start = end - timedelta(days=365 * LOOKBACK_YEARS)
    out_markets, all_rows = {}, []
    cands = candidates(pool)

    for name, tickers in cands.items():
        n = len(tickers)
        print(f"[{name}] 스캔 시작 — {n}종목(시총 상위, 레버리지/인버스 제외)", flush=True)

        def cb(done, total, label, _n=name):
            if done % 25 == 0 or done == total:
                print(f"  [{_n}] {done}/{total}", flush=True)

        df = scan_market(tickers, start, end, progress_cb=cb)
        rows = [_row(df.iloc[i].to_dict(), name) for i in range(len(df))]  # 이미 낙폭 깊은 순 정렬
        out_markets[name] = rows[:top]
        all_rows.extend(rows)
        print(f"[{name}] 완료 — 유효 {len(rows)}종목, TOP{top} 추출", flush=True)

    all_rows.sort(key=lambda r: r["drawdown_pct"])   # 시장무관 통합
    top3_rows = all_rows[:top3]

    # 화면에 뜨는 종목(시장별 TOP + 통합 TOP3)에만 확장데이터(pts·낙폭횟수) 부착 — JSON 경량 유지
    for r in [x for rows in out_markets.values() for x in rows] + top3_rows:
        if "pts" not in r:
            e = _enrich(r)
            r["pts"], r["counts"], r["listed"] = e["pts"], e["counts"], e["listed"]

    result = {
        "week": week, "date": end.strftime("%Y-%m-%d"),
        "markets": out_markets, "top3": top3_rows,
    }
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", type=int, default=1)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--top3", type=int, default=3)
    ap.add_argument("--pool", type=int, default=100, help="시장별 시총 상위 후보 수(ETF는 미/한 절반씩)")
    a = ap.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    res = run(a.week, a.top, a.top3, a.pool)
    out = DATA / f"week{a.week}.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n✓ {out.relative_to(PROJ)} 저장")
    for name, rows in res["markets"].items():
        print(f"  {name}: " + " · ".join(f'{r["ticker"]} {r["drawdown_pct"]}%' for r in rows))
    print("  통합 TOP3: " + " · ".join(f'{r["ticker"]}({r["market"]}) {r["drawdown_pct"]}%' for r in res["top3"]))


if __name__ == "__main__":
    main()
