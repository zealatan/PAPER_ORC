# -*- coding: utf-8 -*-
"""상승(52주 신고가) 주간 스캔 — 시장별 TOP 선정 + 통화환산 + 차트보강 → data/rise_weekN.json.

낙폭용 weekly_scan.py 의 상승판. scan_market_breakout(이번 주 52주 신고가) 종목을
시총순으로 뽑아(미달이면 전부), 시장 표시통화로 환산하고, 차트포인트/신고가/5년전
인덱스를 붙여 rise_weekN.json 에 시장별로 병합한다.

핵심 규칙(다음 주에도 동일):
 - 트리거: 이번 주(최근 fresh_days거래일) 52주 신고가 경신 (scan_market_breakout, high_lookback_days=252)
 - 선정: 시총(표시통화 환산) 내림차순 TOP (기본 5). 후보 부족하면 있는 만큼.
 - payload: 5년 수익률(period_start=5년전).
 - 표시통화: 미국=USD($) · 한국=KRW(₩) · 유럽=EUR(€, 전 통화 환산).
   · 유럽은 SEK/GBP/CHF/DKK/NOK/USD 를 실시간 FX로 €환산.
     ⚠️ GBp(런던): yfinance 시총=파운드단위(×GBP레이트), 가격=펜스단위(÷100 후 ×GBP레이트).
 - 차트: pts[highidx] 를 실제 high_price 로 보정(코오롱/네슬레류 마커 정확도).

사용:
  python3 rise_scan.py --market 미국 --week 30
  python3 rise_scan.py --market 유럽 --week 30 --top 5
  python3 rise_scan.py --market 한국 --week 30
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from datetime import date
from pathlib import Path

warnings.filterwarnings("ignore")
import pandas as pd  # noqa: E402

SELF = Path(__file__).resolve()
PROJ = SELF.parent
ROOT = PROJ.parent.parent                        # PAPER_ORC
sys.path.insert(0, str(ROOT / "global_cup_suite"))
sys.path.insert(0, str(PROJ))
import weekly_scan as ws                          # noqa: E402  (candidates 재사용)
from global_cup.high_scanner import scan_market_breakout                 # noqa: E402
from global_cup.data_loader import download_price, get_close_series      # noqa: E402

ASSET = ROOT / "global_cup_suite" / "data" / "asset_size.csv"
HIST_START = date(2000, 1, 1)
N_PTS = 80

# 시장별 표시통화
MARKET_CUR = {"미국": "USD", "한국": "KRW", "유럽": "EUR"}


def _fx_to(disp: str) -> dict:
    """{src_ccy: rate} — src통화 1단위 = ? disp통화. disp==src는 1.0."""
    if disp == "EUR":
        pairs = {"SEK": "SEKEUR=X", "CHF": "CHFEUR=X", "GBP": "GBPEUR=X",
                 "DKK": "DKKEUR=X", "NOK": "NOKEUR=X", "USD": "USDEUR=X"}
    elif disp == "USD":
        pairs = {"EUR": "EURUSD=X", "GBP": "GBPUSD=X", "CHF": "CHFUSD=X",
                 "SEK": "SEKUSD=X", "DKK": "DKKUSD=X", "NOK": "NOKUSD=X", "KRW": "KRWUSD=X"}
    else:  # KRW 등은 환산 불필요(단일통화 시장)
        pairs = {}
    out = {disp: 1.0}
    for ccy, pair in pairs.items():
        try:
            c = get_close_series(download_price(pair, date(2026, 1, 1), date.today()))
            out[ccy] = float(c.iloc[-1])
        except Exception:
            pass
    return out


def mc_to(v, src, R):
    """시총 환산: GBp도 파운드단위(yfinance) → GBP레이트."""
    return float(v) * R.get("GBP" if src == "GBp" else src, 1.0)


def px_to(v, src, R):
    """가격 환산: GBp는 펜스 → /100."""
    if src == "GBp":
        return float(v) / 100.0 * R.get("GBP", 1.0)
    return float(v) * R.get(src, 1.0)


def enrich(ticker, high_date, high_price, src_ccy, R):
    c = get_close_series(download_price(ticker, HIST_START, date.today()))
    if c.empty:
        return None
    step = max(1, len(c) // N_PTS)
    s = c.iloc[::step]
    if s.index[-1] != c.index[-1]:
        s = pd.concat([s, c.iloc[[-1]]])
    pts = [[i, round(px_to(float(v), src_ccy, R), 2)] for i, v in enumerate(s)]
    sd = list(s.index)
    near = lambda dt: min(range(len(sd)), key=lambda k: abs((sd[k] - pd.Timestamp(dt)).days))
    hidx = near(high_date)
    pts[hidx][1] = round(px_to(float(high_price), src_ccy, R), 2)   # 마커 정확도 보정
    return {"pts": pts, "highidx": hidx, "baseidx": near(pd.Timestamp(date(2021, 7, 26))),
            "listed": s.index[0].strftime("%Y-%m-%d")}


def run(market: str, week: int, top: int, fresh_days: int, years: int):
    end = date.today()
    period_start = date(end.year - years, end.month, min(end.day, 28))
    disp = MARKET_CUR[market]
    R = _fx_to(disp)
    print(f"[{market}] 표시통화={disp} FX={ {k: round(v,4) for k,v in R.items()} }", flush=True)

    a = pd.read_csv(ASSET); a["ticker"] = a["ticker"].astype(str)
    CCY = dict(zip(a["ticker"], a["source_currency"]))
    SIZE = dict(zip(a["ticker"], a["asset_size"]))

    tickers = ws.candidates(100)[market]
    df = scan_market_breakout(tickers, date(2005, 1, 1), end, period_start,
                              high_lookback_days=252, fresh_days=fresh_days)
    if df.empty:
        print(f"[{market}] 이번 주 신고가 종목 없음"); return []
    df["src"] = df["ticker"].astype(str).map(CCY)
    df["size_disp"] = df.apply(
        lambda r: mc_to(SIZE[str(r["ticker"])], r["src"], R) if pd.notna(SIZE.get(str(r["ticker"]))) else 0,
        axis=1)
    df = df.sort_values("size_disp", ascending=False).head(top)

    rows = []
    for _, x in df.iterrows():
        e = enrich(x["ticker"], x["high_date"], x["high_price"], x["src"], R)
        if e is None:
            continue
        rows.append({
            "label": x["label"], "ticker": x["ticker"], "market": market,
            "high_date": str(x["high_date"])[:10],
            "high_price": round(px_to(float(x["high_price"]), x["src"], R), 2),
            "current_price": round(px_to(float(x["current_price"]), x["src"], R), 2),
            "return_pct": round(float(x["return_pct"]), 2),
            "size": round(float(x["size_disp"]), 0),
            **e})
        print(f"  {x['label'][:26]:26} {x['return_pct']:+.0f}%  {disp} {x['size_disp']/1e9:.1f}B", flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market", required=True, choices=list(MARKET_CUR))
    ap.add_argument("--week", type=int, required=True)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--fresh-days", type=int, default=5)
    ap.add_argument("--years", type=int, default=5)
    a = ap.parse_args()

    rows = run(a.market, a.week, a.top, a.fresh_days, a.years)
    out = PROJ / "data" / f"rise_week{a.week}.json"
    d = json.loads(out.read_text(encoding="utf-8")) if out.exists() else \
        {"week": a.week, "date": date.today().strftime("%Y-%m-%d"), "mode": "rise", "markets": {}}
    d.setdefault("markets", {})[a.market] = rows
    out.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"저장 → {out.name} (시장={list(d['markets'])})")


if __name__ == "__main__":
    main()
