# -*- coding: utf-8 -*-
"""낙폭(전고점 대비 하락) 주간 스캔 — 시총순 대형주 선정. 상승 rise_scan.py 의 낙폭 대칭.

선정 규칙(상승과 대칭):
 - 트리거: 전고점 대비 **하락 ≥ min_drop%** (기본 20). scan_market + filter_by_min_drop.
 - 선정: 시총 내림차순 **TOP** (기본 10). → 삼성전자·SK하이닉스 같은 대형주.
   (weekly_scan.py 는 '낙폭 깊이순'이라 소형 크래시가 상위 — 이건 '시총순'.)
 - 차트보강: weekly_scan._enrich 재사용(pts·−30% 별표 crash_x·낙폭횟수 counts).
 - 표시통화: build_fall_deck 이 CSV 통화로 표기(미$·한₩·유€). 유럽 혼합통화 주의는 미결(현재 낙폭은 미/한 위주).

출력: data/fall_weekN.json (build_fall_deck.py 가 읽음. weekly_scan 의 weekN.json 과 별개).
사용:
  python3 fall_scan.py --market 한국 --week 31
  python3 fall_scan.py --market 미국 --week 31 --top 10 --min-drop 20
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from datetime import date, timedelta
from pathlib import Path

warnings.filterwarnings("ignore")
import pandas as pd  # noqa: E402

SELF = Path(__file__).resolve()
PROJ = SELF.parent
ROOT = PROJ.parent.parent
sys.path.insert(0, str(ROOT / "global_cup_suite"))
sys.path.insert(0, str(PROJ))
import weekly_scan as ws                                        # noqa: E402  (candidates·_row·_enrich 재사용)
from global_cup.high_scanner import scan_market, filter_by_min_drop   # noqa: E402

ASSET = ROOT / "global_cup_suite" / "data" / "asset_size.csv"

# 데이터 오류로 제외하는 종목(6자리코드/티커앞). 정상화되면 제거.
#  402340 SK스퀘어: 야후 주가 ~8-10배 뻥튀기 → 시총(→top 진입)·낙폭 모두 왜곡.
EXCLUDE = {"402340"}


def run(market: str, top: int, min_drop: float, pool: int, min_size: float, asof: date | None = None):
    # asof(포함할 마지막 종가일) 지정 시 end=asof+1일(yfinance end 배타적)로 고정 → 시장 간 날짜 통일.
    end = (asof + timedelta(days=1)) if asof else date.today()
    start = end - timedelta(days=365 * ws.LOOKBACK_YEARS)
    a = pd.read_csv(ASSET); a["ticker"] = a["ticker"].astype(str)
    SIZE = dict(zip(a["ticker"], a["asset_size"]))

    tickers = ws.candidates(pool)[market]
    df = scan_market(tickers, start, end)
    df = filter_by_min_drop(df, min_drop)              # 하락 ≥ min_drop%
    df = df[~df["ticker"].astype(str).str.split(".").str[0].isin(EXCLUDE)]  # 데이터오류 제외
    if df.empty:
        print(f"[{market}] 하락 {min_drop}%↑ 종목 없음"); return []
    df["size"] = df["ticker"].astype(str).map(SIZE)
    df = df.sort_values("size", ascending=False, na_position="last")
    # ★ 시총 하한(min_size, 시장 통화) 우선 → top 미달 시 중소형으로 backfill.
    big = df[df["size"] >= min_size]
    small = df[~(df["size"] >= min_size)]              # NaN(시총 없음) 포함, 하위 backfill
    n_big = min(len(big), top)
    df = pd.concat([big.head(top), small.head(top - n_big)]).head(top)
    if len(big) < top:
        print(f"  (시총 {min_size/1e12:.0f}조↑ {len(big)}개 → 중소형 {top-len(big)}개 backfill)", flush=True)

    rows = []
    for _, x in df.iterrows():
        r = ws._row(x.to_dict(), market)
        e = ws._enrich(r)
        r["pts"], r["counts"], r["listed"] = e["pts"], e["counts"], e["listed"]
        r["crash_x"] = e.get("crash_x", [])
        r["size"] = float(x["size"]) if pd.notna(x["size"]) else None
        rows.append(r)
        sz = f"₩{x['size']/1e12:.1f}조" if pd.notna(x['size']) else "?"
        print(f"  {r['label'].split(' / ')[0][:20]:20} {r['drawdown_pct']:6.1f}%  시총 {sz}", flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market", required=True, choices=["미국", "한국", "유럽", "ETF"])
    ap.add_argument("--week", type=int, required=True)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--min-drop", type=float, default=20.0)
    ap.add_argument("--pool", type=int, default=100)
    ap.add_argument("--min-size", type=float, default=10e12,
                    help="시총 하한(시장 통화, 기본 10조=한국원). 미달 시 중소형 backfill.")
    ap.add_argument("--asof", help="포함할 마지막 종가일 YYYY-MM-DD(예: 지난주 금요일). 미지정=오늘. 시장 간 날짜 통일용.")
    a = ap.parse_args()

    asof = date.fromisoformat(a.asof) if a.asof else None
    rows = run(a.market, a.top, a.min_drop, a.pool, a.min_size, asof)
    out = PROJ / "data" / f"fall_week{a.week}.json"
    d = json.loads(out.read_text(encoding="utf-8")) if out.exists() else \
        {"week": a.week, "mode": "fall", "markets": {}}
    d["date"] = (a.asof or date.today().strftime("%Y-%m-%d"))   # asof 지정 시 기준일로 기록
    d.setdefault("markets", {})[a.market] = rows
    out.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"저장 → {out.name} (시장={list(d['markets'])})")


if __name__ == "__main__":
    main()
