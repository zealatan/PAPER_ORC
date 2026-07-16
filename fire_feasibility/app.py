"""
🔥 FIRE 타당성 백테스트 — Streamlit UI

"은퇴 시점에 목돈으로 한 종목을 사고, 매월 생활비를 인출했다면 자산이 버텼을까?"
마켓을 고르면 통화·기본 원천징수세가 자동 반영되고, 종목은 마켓별 목록에서 선택.
배당은 실제 지급 시점에 현금으로 들어오고, 생활비는 배당현금 우선 충당 후 부족분만
매도. 잉여 배당은 (다음 배당까지 버퍼를 남기고) 재투자. 통화 환산(FX)은 하지 않음.

Run:
  PYB=/home/zealatan/.pyenv/versions/3.11.8/bin/python3.11
  SP=/home/zealatan/YOUTUBE/blog/global_cup_refactored/.venv/lib/python3.11/site-packages
  PYTHONPATH=$SP $PYB -m streamlit run app.py
"""
from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from global_cup.config import get_market_rule
from global_cup.data_loader import (download_price, download_dividends,
                                    get_close_series, build_ticker_dict)
from global_cup.market_config import MARKETS
from global_cup.formatting import format_amount, get_currency_symbol
from global_cup.dividend_schedule import classify
from global_cup.fire_engine import run_fire_backtest

st.set_page_config(page_title="FIRE 타당성 백테스트", page_icon="🔥", layout="wide")

# ── constants ───────────────────────────────────────────────────────────────────
INK, ACCENT, GREY = "#1f2933", "#e5484d", "#adb5bd"
FREQ_KR = {"monthly": "월배당", "quarterly": "분기배당", "semiannual": "반기배당",
           "annual": "연배당", "irregular": "불규칙", "none": "무배당"}
MARKET_ORDER = ["United States", "ETF", "Global", "Korea", "Japan", "European Union"]
CUR_DEFAULTS = {
    "USD": dict(corpus=300_000,     corpus_step=10_000,     exp=1_500,     exp_step=100),
    "EUR": dict(corpus=300_000,     corpus_step=10_000,     exp=1_500,     exp_step=100),
    "KRW": dict(corpus=300_000_000, corpus_step=10_000_000, exp=1_500_000, exp_step=100_000),
    "JPY": dict(corpus=30_000_000,  corpus_step=1_000_000,  exp=150_000,   exp_step=10_000),
}
DEFAULT_TICKER = {"United States": "Coca-Cola / KO"}   # signature FIRE example

# ── header ──────────────────────────────────────────────────────────────────────
st.title("🔥 FIRE 타당성 백테스트")
st.caption("은퇴 목돈으로 한 종목을 사고 매월 생활비를 인출했을 때 자산이 버텼는지 검증합니다 · 통화 환산 없음")

# ── inputs ──────────────────────────────────────────────────────────────────────
with st.container(border=True):
    r1 = st.columns([1.3, 1.7, 1, 1])
    market = r1[0].selectbox("마켓", MARKET_ORDER,
                             format_func=lambda k: f"{MARKETS[k].flag} {MARKETS[k].name}")
    rule = get_market_rule(market)
    currency = rule["currency"]
    defaults = CUR_DEFAULTS.get(currency, CUR_DEFAULTS["USD"])

    tickers = build_ticker_dict(market) or {}
    labels = list(tickers)
    if not labels:
        st.error(f"'{market}' 종목 목록을 불러오지 못했습니다.")
        st.stop()
    def_label = DEFAULT_TICKER.get(market)
    def_idx = labels.index(def_label) if def_label in labels else 0
    ticker_label = r1[1].selectbox("종목", labels, index=def_idx, key=f"ticker_{market}")
    ticker = tickers[ticker_label]

    start = r1[2].date_input("은퇴 시작일", value=date(2000, 1, 1),
                             min_value=date(1970, 1, 1), max_value=date.today())
    tax = r1[3].number_input("원천징수세 (%)", value=float(rule["tax_rate"]),
                             step=0.5, min_value=0.0, max_value=100.0, key=f"tax_{market}")

    r2 = st.columns([1.3, 1.7, 2])
    sym = get_currency_symbol(currency)
    corpus = r2[0].number_input(f"은퇴 자금 ({sym})", value=defaults["corpus"],
                                step=defaults["corpus_step"], min_value=0,
                                key=f"corpus_{currency}")
    monthly = r2[1].number_input(f"월 생활비 ({sym})", value=defaults["exp"],
                                 step=defaults["exp_step"], min_value=0,
                                 key=f"exp_{currency}")
    reinvest_surplus = r2[2].toggle("잉여 배당 재투자", value=True,
                                    help="생활비 충당 후 남는 배당을 (다음 배당까지 버퍼 남기고) 재매수")

if corpus <= 0:
    st.info("은퇴 자금을 입력하세요.")
    st.stop()


def money(v, dec=0):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return format_amount(v, currency, decimals=dec)


# ── load data ───────────────────────────────────────────────────────────────────
today = date.today()
with st.spinner(f"{ticker} 데이터 로딩 중…"):
    price_df = download_price(ticker, start, today)
    close = get_close_series(price_df)
    div = download_dividends(ticker, date(max(start.year - 6, 1970), 1, 1), today)

if close.empty:
    st.error(f"'{ticker}' 가격 데이터를 불러오지 못했습니다. 다른 종목/기간을 선택하세요.")
    st.stop()

sch = classify(div)

# ── run backtest ────────────────────────────────────────────────────────────────
result = run_fire_backtest(
    close, div, float(corpus),
    annual_withdrawal=float(monthly) * 12,
    strategy="fixed_nominal", frequency="monthly",
    tax_rate_pct=float(tax), reinvest_surplus=reinvest_surplus,
    start_date=start,
)
if result is None:
    st.error("백테스트를 실행할 수 없습니다. 입력값을 확인하세요.")
    st.stop()

s, tl = result.summary, result.timeline_df

# ── verdict banner ──────────────────────────────────────────────────────────────
freq_txt = f"{FREQ_KR.get(sch.frequency, sch.frequency)} · {sch.payments_per_year}회/년"
if sch.has_specials:
    freq_txt += " (특별배당 포함)"
name = ticker_label.split(" / ")[0]

if s["Survived"]:
    st.success(f"✅ **생존** — {name}({freq_txt}) · {s['Years']:.1f}년간 월 {money(monthly)} 인출 후 "
               f"최종 자산 **{money(s['Final Value'])}**")
else:
    dep = pd.Timestamp(s["Depletion Date"]).date()
    st.error(f"❌ **고갈** — {name}({freq_txt}) · 자산이 **{dep}**에 소진됨 "
             f"(약 {s['Survived Years']:.1f}년 지속)")

# ── metric cards ────────────────────────────────────────────────────────────────
m = st.columns(4)
m[0].metric("최종 자산", money(s["Final Value"]),
            delta=f"{(s['Final Value']/corpus - 1)*100:+.0f}% vs 원금")
m[1].metric("총 인출액", money(s["Total Withdrawn"]))
m[2].metric("총 배당(세후)", money(s["Total Net Dividend"]))
m[3].metric("총 매도액", money(s["Total Shares Sold Value"]))

m2 = st.columns(4)
m2[0].metric("최종 보유주식", f"{s['Final Shares']:,.0f}주")
m2[1].metric("잉여 재투자액", money(s["Total Reinvested Surplus"]))
m2[2].metric("최대 낙폭 (MDD)", f"{s['Max Drawdown %']:.0f}%")
m2[3].metric("최저 자산", money(s["Min Portfolio Value"]))

# ── portfolio value chart ───────────────────────────────────────────────────────
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=tl["Date"], y=tl["Portfolio Value"], name="포트폴리오 가치",
    line=dict(color=ACCENT, width=2), fill="tozeroy", fillcolor="rgba(229,72,77,0.08)",
))
fig.add_trace(go.Scatter(
    x=tl["Date"], y=tl["Cumulative Withdrawn"] + corpus, name="원금 + 누적인출",
    line=dict(color=GREY, width=1.5, dash="dot"),
))
fig.add_hline(y=corpus, line=dict(color=INK, width=1, dash="dash"),
              annotation_text=f"은퇴 원금 {money(corpus)}", annotation_position="top left")
if not s["Survived"] and s["Depletion Date"] is not None:
    fig.add_vline(x=pd.Timestamp(s["Depletion Date"]), line=dict(color=ACCENT, width=1.5),
                  annotation_text="고갈", annotation_position="top")
fig.update_layout(
    height=420, margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified", plot_bgcolor="white",
    yaxis=dict(title=f"자산 ({sym})", gridcolor="#eef1f4", zeroline=False),
    xaxis=dict(gridcolor="#eef1f4"),
)
st.plotly_chart(fig, width="stretch")

# ── annual breakdown ────────────────────────────────────────────────────────────
tl2 = tl.copy()
tl2["Year"] = tl2["Date"].dt.year
annual = tl2.groupby("Year").agg(
    배당세후=("Dividend", "sum"), 인출=("Withdrawal", "sum"),
    연말자산=("Portfolio Value", "last"), 연말주식=("Shares", "last"),
).round(0)
annual["매도필요"] = (annual["인출"] - annual["배당세후"]).clip(lower=0).round(0)

with st.expander("📅 연도별 상세", expanded=False):
    show = annual.reset_index()[["Year", "배당세후", "인출", "매도필요", "연말주식", "연말자산"]]
    show.columns = ["연도", "배당(세후)", "인출", "매도필요", "연말 주식수", "연말 자산"]
    money_cols = ["배당(세후)", "인출", "매도필요", "연말 자산"]
    for c in money_cols:
        show[c] = show[c].map(lambda v: money(v))
    show["연말 주식수"] = show["연말 주식수"].map(lambda v: f"{v:,.0f}")
    show["연도"] = show["연도"].astype(str)
    st.dataframe(show, width="stretch", hide_index=True)

# ── raw price chart (bottom) ────────────────────────────────────────────────────
st.markdown(f"#### 📉 {name} 주가 ({ticker})")
pfig = go.Figure()
pfig.add_trace(go.Scatter(
    x=tl["Date"], y=tl["Price"], name="주가",
    line=dict(color="#3b5bdb", width=2), fill="tozeroy", fillcolor="rgba(59,91,219,0.06)",
))
if not s["Survived"] and s["Depletion Date"] is not None:
    pfig.add_vline(x=pd.Timestamp(s["Depletion Date"]), line=dict(color=ACCENT, width=1.5),
                   annotation_text="고갈", annotation_position="top")
pfig.update_layout(
    height=420, margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified", plot_bgcolor="white",
    yaxis=dict(title=f"주가 ({sym})", gridcolor="#eef1f4", zeroline=False),
    xaxis=dict(gridcolor="#eef1f4"),
)
st.plotly_chart(pfig, width="stretch")

st.caption(f"데이터: {tl['Date'].iloc[0].date()} ~ {tl['Date'].iloc[-1].date()} · "
           f"{market} · {ticker} · 배당 {sch.n_recent}건(최근) · Copyright © zealatan")
