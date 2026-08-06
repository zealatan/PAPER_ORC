#!/usr/bin/env python3
"""유니버스 전 종목의 시총(주식)/총자산(ETF) 스냅샷을 미리 받아 asset_size.csv로 저장.

- 소스: yfinance .info  (주식=marketCap, ETF=totalAssets)
- GUI(낙폭·신고가 스캐너)가 티커로 즉시 조인해 표에 표시 → 스캔 지연 0.
- 재개 가능: 기존 asset_size.csv를 읽어 값 있는 티커는 건너뜀(재실행으로 빈칸만 보충).
- 한국 ETF는 Yahoo에 AUM 없음 → asset_size 빈칸(추후 KRX 소스로 보완).

출력 컬럼: ticker, asset_size, kind(marketcap|aum), source_currency
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

DATA = Path(__file__).resolve().parent
OUT = DATA / "asset_size.csv"
CSV_GLOB = "tickers_*.csv"


def load_universe() -> pd.DataFrame:
    frames = []
    for csv in sorted(DATA.glob(CSV_GLOB)):
        df = pd.read_csv(csv)
        if {"ticker", "category", "currency"}.issubset(df.columns):
            frames.append(df[["ticker", "category", "currency"]])
    uni = pd.concat(frames, ignore_index=True).drop_duplicates("ticker")
    return uni.reset_index(drop=True)


def load_existing() -> dict:
    if not OUT.exists():
        return {}
    df = pd.read_csv(OUT)
    out = {}
    for _, r in df.iterrows():
        val = r.get("asset_size")
        if pd.notna(val):
            out[str(r["ticker"])] = {
                "asset_size": float(val),
                "kind": r.get("kind", ""),
                "source_currency": r.get("source_currency", ""),
            }
    return out


def fetch_one(ticker: str, category: str) -> dict | None:
    try:
        info = yf.Ticker(ticker).info
    except Exception:
        return None
    mc = info.get("marketCap")
    ta = info.get("totalAssets")
    # 주식=시총, ETF=총자산. 둘 중 존재하는 값 채택(카테고리 우선).
    if "ETF" in str(category).upper():
        val, kind = ta, "aum"
        if val is None:            # 일부 ETF는 marketCap로만 잡히기도
            val, kind = mc, "aum"
    else:
        val, kind = mc, "marketcap"
        if val is None:
            val, kind = ta, "marketcap"
    if val is None or float(val) <= 0:
        return None
    return {"asset_size": float(val), "kind": kind,
            "source_currency": info.get("currency", "")}


def main() -> None:
    uni = load_universe()
    have = load_existing()
    rows = []
    todo = [(t, c) for t, c in zip(uni["ticker"], uni["category"])
            if t not in have]
    total = len(uni)
    done_cached = len(have)
    print(f"유니버스 {total}종목 · 캐시 {done_cached} · 신규 {len(todo)}", flush=True)

    # 기존 값 보존
    for t, d in have.items():
        rows.append({"ticker": t, **d})

    for i, (ticker, category) in enumerate(todo, start=1):
        res = fetch_one(ticker, category)
        if res is not None:
            rows.append({"ticker": ticker, **res})
        if i % 25 == 0 or i == len(todo):
            # 주기적 저장(중단돼도 진행분 보존)
            pd.DataFrame(rows, columns=["ticker", "asset_size", "kind",
                                        "source_currency"]).to_csv(OUT, index=False)
            got = sum(1 for r in rows if pd.notna(r.get("asset_size")))
            print(f"  {i}/{len(todo)} 처리 · 누적 {got}종목 값 확보", flush=True)

    pd.DataFrame(rows, columns=["ticker", "asset_size", "kind",
                                "source_currency"]).to_csv(OUT, index=False)
    print(f"완료 → {OUT}  ({len(rows)}종목)", flush=True)


if __name__ == "__main__":
    main()
