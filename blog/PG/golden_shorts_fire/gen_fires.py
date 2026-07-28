#!/usr/bin/env python3
"""
gen_fires.py — 파이프라인 단계4(통합): 백테스트 엔진 → assets/<stock>_fires.json (원금 5종).

사용:  SHORTS_STOCK=PG|QQQ|KTNG  python3 gen_fires.py
시나리오: 2000년 은퇴 · 물가반영(fixed_real) · 원금 5종 × 월 인출 3종.
  · USD 종목: 원금 $20/40/60/80/100만, 월 $1/2/3천, 세금 15%, 미국 CPI(로컬).
  · KRW 종목: 원금 2/4/6/8/10억,   월 100/200/300만, 세금 15.4%, 한국 CPI(FRED).
엔진: global_cup_suite/global_cup/fire_engine.run_fire_backtest (원천·수정 금지).
데이터: PG=로컬 CSV(../data), QQQ/KTNG=yfinance. 출력: assets/<stock>_fires.json.
"""
import sys, json, os, io, math, urllib.request
from datetime import date
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "global_cup_suite")))
from global_cup.fire_engine import run_fire_backtest

STOCK = os.environ.get("SHORTS_STOCK", "PG")
CMAP_USD = {1000: "#2b6cb0", 2000: "#d98f2b", 3000: "#c2255c"}
CMAP_KRW = {1_000_000: "#2b6cb0", 2_000_000: "#d98f2b", 3_000_000: "#c2255c"}

def us_cpi():
    df = pd.read_csv(os.path.join(HERE, "..", "ref", "fred_CPIAUCSL.csv"), parse_dates=["date"])
    return pd.Series(pd.to_numeric(df["val"], errors="coerce").values, index=df["date"]).dropna()
def kr_cpi():
    raw = urllib.request.urlopen("https://fred.stlouisfed.org/graph/fredgraph.csv?id=KORCPIALLMINMEI", timeout=60).read().decode()
    df = pd.read_csv(io.StringIO(raw)); df.columns = ["date", "val"]; df["date"] = pd.to_datetime(df["date"])
    return pd.Series(pd.to_numeric(df["val"], errors="coerce").values, index=df["date"]).dropna()
def yf_series(ticker):
    import yfinance as yf
    t = yf.Ticker(ticker)
    h = t.history(start="2000-01-01", end="2026-07-31", auto_adjust=False); h.index = h.index.tz_localize(None)
    close = h["Close"]; close.index = pd.to_datetime(close.index)
    dv = t.dividends; dv.index = pd.to_datetime(dv.index.tz_localize(None))
    return close, dv
def csv_series(prefix):
    d = os.path.join(HERE, "..", "data")
    close = pd.read_csv(os.path.join(d, prefix + "_price.csv"), parse_dates=["date"]).set_index("date")["close"]
    div = pd.read_csv(os.path.join(d, prefix + "_div.csv"), parse_dates=["date"]).set_index("date")["div"]
    close.index = pd.to_datetime(close.index).tz_localize(None); div.index = pd.to_datetime(div.index).tz_localize(None)
    return close, div

# ── 종목 설정 ──
if STOCK == "PG":
    close, div = csv_series("pg"); cpi = us_cpi(); KRW = False; TAX = 15.0
elif STOCK == "QQQ":
    close, div = yf_series("QQQ"); cpi = us_cpi(); KRW = False; TAX = 15.0
elif STOCK == "KTNG":
    close, div = yf_series("033780.KS"); cpi = kr_cpi(); KRW = True; TAX = 15.4
else:
    raise SystemExit("unknown SHORTS_STOCK: " + STOCK)

if KRW:
    PRIN = [2, 4, 6, 8, 10]; PRIN = [p * 100_000_000 for p in PRIN]; MOS = [1_000_000, 2_000_000, 3_000_000]; CMAP = CMAP_KRW
    def money(v): return ("%.1f억" % (v / 1e8)) if v >= 1e8 else ("%d만" % round(v / 1e4))
    def hnum(v): return money(v).replace(".0", "")
else:
    PRIN = [200_000, 400_000, 600_000, 800_000, 1_000_000]; MOS = [1000, 2000, 3000]; CMAP = CMAP_USD
    def money(v): return "$" + format(int(round(v / 10000) * 10000), ",")
    def hnum(v): return "$" + format(int(v), ",")

def to_year(d):
    y0 = pd.Timestamp(d.year, 1, 1); y1 = pd.Timestamp(d.year + 1, 1, 1)
    return round(d.year + (d - y0).days / (y1 - y0).days, 2)
def scen(init, mo):
    r = run_fire_backtest(close, div, init, annual_withdrawal=mo * 12, strategy="fixed_real",
        frequency="monthly", tax_rate_pct=TAX, reinvest_dividends=False, reinvest_surplus=True,
        cpi=cpi, start_date=date(2000, 1, 1))
    s = r.summary; tl = r.timeline_df.copy(); tl["Date"] = pd.to_datetime(tl["Date"]); tl["ym"] = tl["Date"].dt.to_period("M")
    m = tl.groupby("ym").last().reset_index(drop=True)
    pts = [[to_year(x["Date"]), round(x["Portfolio Value"])] for _, x in m.iloc[::3].iterrows()]
    last = [to_year(m.iloc[-1]["Date"]), round(m.iloc[-1]["Portfolio Value"])]
    if pts[-1][0] != last[0]: pts.append(last)
    dep = s["Depletion Date"]
    if not s["Survived"] and dep is not None:
        yr = to_year(pd.Timestamp(dep)); pts = [p for p in pts if p[0] <= yr]; pts.append([yr, 0])
    return pts, bool(s["Survived"]), (dep.strftime("%Y-%m") if dep is not None else None), round(s["Final Value"])
def nice_ceil(x):
    e = 10 ** math.floor(math.log10(x)); f = x / e
    for n in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if f <= n: return int(n * e)
    return int(10 * e)

fires = []
print("[%s] 원금별 결과" % STOCK)
for init in PRIN:
    lines, mx, row = [], 0, []
    for mo in MOS:
        pts, surv, dep, fin = scen(init, mo)
        mx = max(mx, max(p[1] for p in pts))
        end = ("생존 " + money(fin)) if surv else ("’%s 파산" % dep[2:4])
        lines.append({"c": CMAP[mo], "name": "", "surv": surv, "end": end, "pts": pts})
        row.append(("생존 " + money(fin)) if surv else ("파산 " + str(dep)))
    ymax = nice_ceil(mx * 1.05)
    pd_ = {"ymax": ymax, "hline": {"v": init, "label": "은퇴 원금 " + hnum(init)},
           "tip": "compact", "yleft": True, "lines": lines}
    if KRW: pd_["krw"] = True
    if init == PRIN[0]: pd_["ylabelmin"] = ymax   # 최소원금: y숫자 숨김(기준선만)
    fires.append({"amt": init, "hook": hnum(init), "payload": pd_})   # hook=순수 금액(예 $200,000 / 2억)
    print("  %-10s %s" % (hnum(init), " · ".join(row)))

pref = {"PG": "pg", "QQQ": "qqq", "KTNG": "ktng"}[STOCK]
out = os.path.join(HERE, "assets", pref + "_fires.json")
json.dump(fires, open(out, "w"), ensure_ascii=False)
print("→", out, "(원금", len(fires), "종)")
