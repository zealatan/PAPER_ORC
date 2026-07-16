"""
FIRE accuracy verification — the literal example.

"2000년에 3억원으로 은퇴, 그 3억으로 코카콜라(KO) 주식을 샀다면 지금 자산은?"

This is a standalone, reproducible ground-truth calculation used to validate the
future FIRE engine. It fetches raw data, caches it to data/ as CSV, and prints
the answer in nominal and real (2000 purchasing-power) KRW.

Data sources (verified reachable via curl_cffi in this sandbox):
  - KO raw close + dividends : yfinance (auto_adjust=False)
  - KRW/USD daily FX         : FRED DEXKOUS   (1981+; yfinance FX only 2003+)
  - Korea CPI (monthly)      : FRED KORCPIALLMINMEI (1960..2023-11)

Run:
  PYB=/home/zealatan/.pyenv/versions/3.11.8/bin/python3.11
  SP=/home/zealatan/YOUTUBE/blog/global_cup_refactored/.venv/lib/python3.11/site-packages
  PYTHONPATH=$SP $PYB verify_2000_ko.py
"""
from __future__ import annotations

import io
from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf
from curl_cffi import requests as cr

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

TICKER = "KO"
RETIRE_DATE = date(2000, 1, 1)
INITIAL_KRW = 300_000_000.0        # 3억원
US_WITHHOLDING = 0.15              # 미국 배당 원천징수 15%


# ── Data loaders (cache to CSV) ────────────────────────────────────────────────

def _fred_series(series_id: str) -> pd.Series:
    cache = DATA_DIR / f"fred_{series_id}.csv"
    if cache.exists():
        df = pd.read_csv(cache, parse_dates=["date"])
    else:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
        r = cr.get(url, impersonate="chrome", timeout=30)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = ["date", "val"]
        df["date"] = pd.to_datetime(df["date"])
        df.to_csv(cache, index=False)
    s = pd.Series(pd.to_numeric(df["val"], errors="coerce").values, index=df["date"])
    return s.dropna()


def _ko_price() -> pd.Series:
    cache = DATA_DIR / "ko_price_raw.csv"
    if cache.exists():
        s = pd.read_csv(cache, parse_dates=["date"]).set_index("date")["close"]
    else:
        df = yf.download(TICKER, start="1999-12-01", auto_adjust=False,
                         progress=False, threads=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        s = pd.to_numeric(df["Close"], errors="coerce").dropna()
        s.index = pd.to_datetime(s.index).tz_localize(None)
        s.rename_axis("date").rename("close").to_csv(cache)
    s.index = pd.to_datetime(s.index).tz_localize(None)
    return s


def _ko_dividends() -> pd.Series:
    cache = DATA_DIR / "ko_div.csv"
    if cache.exists():
        s = pd.read_csv(cache, parse_dates=["date"]).set_index("date")["div"]
    else:
        d = yf.Ticker(TICKER).dividends
        d.index = pd.to_datetime(d.index).tz_localize(None)
        s = d.astype(float)
        s.rename_axis("date").rename("div").to_csv(cache)
    s.index = pd.to_datetime(s.index).tz_localize(None)
    return s


def _asof(series: pd.Series, when: pd.Timestamp) -> float:
    """Last available value on/before `when` (FX/CPI have gaps & weekends)."""
    sub = series[series.index <= when]
    return float(sub.iloc[-1]) if len(sub) else float(series.iloc[0])


# ── Backtest (buy-and-hold, dividends reinvested net of withholding) ───────────

def run(reinvest: bool):
    close = _ko_price()
    div = _ko_dividends()
    fx = _fred_series("DEXKOUS")          # KRW per 1 USD

    close = close[close.index >= pd.Timestamp(RETIRE_DATE)]
    buy_date = close.index[0]
    buy_px = float(close.iloc[0])
    fx_buy = _asof(fx, buy_date)

    usd_initial = INITIAL_KRW / fx_buy
    shares = usd_initial / buy_px
    cash_usd = 0.0

    div = div[(div.index >= close.index[0]) & (div.index <= close.index[-1])]
    # map each ex-date dividend to next trade date
    div_on = {}
    for dt, dps in div.items():
        nxt = close.index[close.index >= dt]
        if len(nxt):
            div_on.setdefault(nxt[0], 0.0)
            div_on[nxt[0]] += float(dps)

    gross_div_usd = tax_usd = 0.0
    for dt, px in close.items():
        dps = div_on.get(dt)
        if dps:
            gross = shares * dps
            tax = gross * US_WITHHOLDING
            net = gross - tax
            gross_div_usd += gross
            tax_usd += tax
            if reinvest:
                shares += net / float(px)
            else:
                cash_usd += net

    end_date = close.index[-1]
    end_px = float(close.iloc[-1])
    fx_end = _asof(fx, end_date)

    val_usd = shares * end_px + cash_usd
    val_krw = val_usd * fx_end

    # real (2000 purchasing power) via Korea CPI
    kcpi = _fred_series("KORCPIALLMINMEI")
    cpi_buy = _asof(kcpi, buy_date)
    cpi_end = _asof(kcpi, end_date)          # note: KR CPI ends 2023-11
    real_krw = val_krw * (cpi_buy / cpi_end)

    return {
        "reinvest": reinvest,
        "buy_date": buy_date.date(), "end_date": end_date.date(),
        "buy_px": buy_px, "end_px": end_px,
        "fx_buy": fx_buy, "fx_end": fx_end,
        "usd_initial": usd_initial, "shares": shares,
        "gross_div_usd": gross_div_usd, "tax_usd": tax_usd, "cash_usd": cash_usd,
        "val_usd": val_usd, "val_krw": val_krw, "real_krw": real_krw,
        "cpi_buy": cpi_buy, "cpi_end": cpi_end,
    }


def main():
    print("=" * 70)
    print(f"KO FIRE 검증 · 초기 {INITIAL_KRW:,.0f}원 · 은퇴 {RETIRE_DATE}")
    print("=" * 70)
    for reinvest in (True, False):
        r = run(reinvest)
        tag = "배당 재투자 ON" if reinvest else "배당 현금보유"
        print(f"\n[{tag}]")
        print(f"  매수일 {r['buy_date']} · KO ${r['buy_px']:.4f} · 환율 {r['fx_buy']:,.1f}원/$")
        print(f"  → 초기 ${r['usd_initial']:,.2f}  →  {r['shares']:,.4f}주")
        print(f"  배당 총액(gross) ${r['gross_div_usd']:,.2f} · 원천세 ${r['tax_usd']:,.2f}")
        if not reinvest:
            print(f"  누적 현금배당(net) ${r['cash_usd']:,.2f}")
        print(f"  종료일 {r['end_date']} · KO ${r['end_px']:.2f} · 환율 {r['fx_end']:,.1f}원/$")
        print(f"  최종 평가액 : ${r['val_usd']:,.2f}")
        print(f"  명목(현재 원화): {r['val_krw']:,.0f} 원  ({r['val_krw']/INITIAL_KRW:.2f}배)")
        print(f"  실질(2000 구매력): {r['real_krw']:,.0f} 원  "
              f"[CPI {r['cpi_buy']:.1f}->{r['cpi_end']:.1f}, KR CPI는 2023-11까지만]")


if __name__ == "__main__":
    main()
