#!/usr/bin/env python3
"""한국 ETF 순자산(AUM)을 네이버 금융에서 받아 asset_size.csv에 병합.

Yahoo는 한국 ETF 총자산을 주지 않으므로(그리고 KRX는 해외 IP 차단), 네이버 금융
etfItemList API로 전체 한국 ETF의 시가총액(marketSum, 억원)을 한 번에 받아
XXXXXX.KS 티커에 매핑해 asset_size.csv를 갱신한다.

멱등: 이미 값이 있는 티커는 덮어쓰지 않음(--force로 강제 갱신).
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parent
OUT = DATA / "asset_size.csv"
NAVER = "https://finance.naver.com/api/sise/etfItemList.nhn"


def fetch_naver_etf() -> dict:
    """{ '069500': aum_krw_float } — 네이버 marketSum(억원) × 1e8."""
    req = urllib.request.Request(NAVER, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=20).read()
    data = json.loads(raw.decode("cp949"))
    out = {}
    for it in data.get("result", {}).get("etfItemList", []):
        code = str(it.get("itemcode", "")).strip()
        ms = it.get("marketSum")
        if code and ms not in (None, "", 0):
            try:
                out[code] = float(ms) * 1e8   # 억원 → 원(KRW)
            except (TypeError, ValueError):
                pass
    return out


def load_universe_kr_etf() -> set:
    """유니버스 CSV에서 한국 ETF 티커(XXXXXX.KS) 집합."""
    out = set()
    for csv in DATA.glob("tickers_*.csv"):
        df = pd.read_csv(csv)
        if not {"ticker", "category", "country"}.issubset(df.columns):
            continue
        m = (df["country"] == "Korea") & (df["category"].astype(str).str.contains("ETF"))
        out |= set(df.loc[m, "ticker"].astype(str))
    return out


def main() -> None:
    force = "--force" in sys.argv
    aum = fetch_naver_etf()
    print(f"네이버 ETF AUM 수신: {len(aum)}종목", flush=True)

    kr_etfs = load_universe_kr_etf()
    print(f"유니버스 한국 ETF: {len(kr_etfs)}종목", flush=True)

    if OUT.exists():
        df = pd.read_csv(OUT)
    else:
        df = pd.DataFrame(columns=["ticker", "asset_size", "kind", "source_currency"])
    df["ticker"] = df["ticker"].astype(str)
    have = {t: (pd.notna(v) and float(v) > 0)
            for t, v in zip(df["ticker"], df["asset_size"])}

    updated, added = 0, 0
    rows = {r["ticker"]: dict(r) for _, r in df.iterrows()}
    # 유니버스의 한국 ETF만 대상으로(오염 방지) — 없으면 추가, 비었으면 갱신.
    for tkr in kr_etfs:
        code = tkr.replace(".KS", "").replace(".KQ", "")
        val = aum.get(code)
        if val is None:
            continue
        if tkr not in rows:
            rows[tkr] = {"ticker": tkr, "asset_size": val,
                         "kind": "aum", "source_currency": "KRW"}
            added += 1
        elif force or not have.get(tkr, False):
            rows[tkr].update(asset_size=val, kind="aum", source_currency="KRW")
            updated += 1

    print(f"추가 {added} · 갱신 {updated}", flush=True)
    out_df = pd.DataFrame(list(rows.values()),
                          columns=["ticker", "asset_size", "kind", "source_currency"])
    out_df.to_csv(OUT, index=False)
    filled = sum(1 for _, r in out_df.iterrows()
                 if str(r["ticker"]).endswith(".KS") and r.get("kind") == "aum"
                 and pd.notna(r["asset_size"]))
    print(f"갱신 {updated}종목 · asset_size.csv 총 {len(out_df)}행 · "
          f"KR ETF(.KS, aum) 채워짐 {filled}종목", flush=True)


if __name__ == "__main__":
    main()
