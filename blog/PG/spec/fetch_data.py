# -*- coding: utf-8 -*-
"""PG 원시 데이터 조달 → 재현용 CSV 저장 (코카콜라 골든과 동일 형식).
   사용: python spec/fetch_data.py
   산출: data/pg_price.csv (date,close 무수정 종가) · data/pg_div.csv (date,div 주당배당)
"""
import csv
from datetime import date, timedelta
from pathlib import Path
import yfinance as yf

TICKER = "PG"
START, END = date(2000, 1, 1), date(2026, 7, 31)
OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)

t = yf.Ticker(TICKER)
h = t.history(start=START.isoformat(), end=(END + timedelta(days=1)).isoformat(),
              auto_adjust=False)  # 무수정(unadjusted) 종가 — Adj Close 이중반영 금지
h.index = h.index.tz_localize(None)
prices = [(d.date(), float(c)) for d, c in h["Close"].items()
          if START <= d.date() <= END]

dv = t.dividends
dv.index = dv.index.tz_localize(None)
divs = [(d.date(), float(v)) for d, v in dv.items() if START <= d.date() <= END]

with open(OUT / "pg_price.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["date", "close"])
    for d, c in prices:
        w.writerow([d.isoformat(), f"{c:.6f}"])
with open(OUT / "pg_div.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["date", "div"])
    for d, v in divs:
        w.writerow([d.isoformat(), f"{v:.6f}"])

print(f"[PG] 가격 {len(prices)}행 ({prices[0][0]}~{prices[-1][0]}), 배당 {len(divs)}건")
print(f"  종가 범위 ${min(c for _,c in prices):.2f} ~ ${max(c for _,c in prices):.2f}")
print(f"  최근 배당 {divs[-1][0]} ${divs[-1][1]:.2f}/주 · 연 배당 ≈ ${sum(v for d,v in divs if d.year==2025):.2f}")
print(f"→ {OUT}/pg_price.csv · pg_div.csv")
