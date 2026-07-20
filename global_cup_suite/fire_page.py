"""
🔥 FIRE 타당성 백테스트 — Streamlit UI

"은퇴 시점에 목돈으로 한 종목을 사고, 매월 생활비를 인출했다면 자산이 버텼을까?"
마켓을 고르면 통화·기본 원천징수세가 자동 반영되고, 종목은 마켓별 목록에서 선택.
배당은 실제 지급 시점에 현금으로 들어오고, 생활비는 배당현금 우선 충당 후 부족분만
매도. 잉여 배당은 (다음 배당까지 버퍼를 남기고) 같은 종목에 재투자.

디자인은 Global Cup 엔진 UI 테마(inject_css) 재사용 — 다크 올리브 배경·크림 텍스트·
라임 액센트·세리프 헤더·마켓별 차트 색상.

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
from global_cup.market_config import MARKETS, get_flag_svg
from global_cup.formatting import format_amount, get_currency_symbol
from global_cup.dividend_schedule import classify
from global_cup.fire_engine import run_fire_backtest_multi, AssetSpec
from global_cup.ui import inject_css

# [suite] hoisted to app.py: st.set_page_config(page_title="FIRE 타당성 백테스트", page_icon="🔥", layout="wide")
# [suite] hoisted to app.py: inject_css()   # Global Cup dark theme (background, fonts, glass inputs, flags)

# ── FIRE-specific supplemental theme ────────────────────────────────────────────
st.markdown("""
<style>
.fire-brand { display:flex; align-items:center; gap:.9rem; margin:.2rem 0 1.4rem; }
.fire-brand .brand-mark { width:46px; height:46px; font-size:24px; }
.fire-title { font-family:Georgia,"Times New Roman",serif; font-weight:500;
    font-size:clamp(28px,3.2vw,42px); letter-spacing:-1.2px; line-height:1; color:#fff5dc; }
.fire-sub { color:#d9caa8; font-size:.82rem; margin-top:.35rem; max-width:680px; }

div[data-testid="stNumberInput"], div[data-testid="stDateInput"] {
    background:rgba(255,255,255,.075) !important; border:1px solid rgba(255,255,255,.14) !important;
    border-radius:8px !important; box-shadow:0 6px 16px rgba(0,0,0,.1) !important; }
div[data-testid="stDateInput"] label { color:#e8e3cf !important; font-weight:600 !important;
    font-size:.82rem !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { background:rgba(255,255,255,.03);
    border:1px solid rgba(255,255,255,.08) !important; border-radius:14px; }

.verdict { border-radius:14px; padding:.95rem 1.3rem; margin:1.1rem 0 .3rem;
    font-size:1.0rem; font-weight:600; border:1px solid; }
.verdict.ok  { background:rgba(53,182,109,.13); border-color:rgba(53,182,109,.5); color:#daffe9; }
.verdict.bad { background:rgba(226,54,54,.13); border-color:rgba(226,54,54,.5); color:#ffdede; }
.verdict b   { color:#ffffff; }

/* 카드 8개를 3열 고정 → 3·3·2 세 줄 배치 (폰에서도 3열 유지) */
.mgrid { display:grid; grid-template-columns:repeat(3,1fr); gap:.5rem; margin:.4rem 0 1.2rem; }
.mcard { background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.09);
    border-radius:12px; padding:.55rem .6rem; box-shadow:0 8px 20px rgba(0,0,0,.16); min-width:0; }
.mcard .lbl { color:#d9caa8; font-size:.66rem; font-weight:700; line-height:1.15;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.mcard .val { color:#fff9ed; font-size:1.08rem; font-weight:800; line-height:1.15;
    margin-top:.12rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.mcard .sub { color:#9db386; font-size:.62rem; margin-top:.1rem; }
.mcard .sub.neg { color:#e88; }

.chart-h { font-family:Georgia,serif; color:#fff5dc; font-size:1.05rem; margin:.6rem 0 .1rem; }

/* 가로 스크롤 래퍼 — 폰에서 표가 잘려도 좌우로 밀어 다 볼 수 있게 */
.table-scroll { overflow-x:auto; -webkit-overflow-scrolling:touch;
    border-radius:10px; margin:.1rem 0 .3rem; }
.table-scroll::-webkit-scrollbar { height:7px; }
.table-scroll::-webkit-scrollbar-thumb { background:rgba(255,255,255,.22); border-radius:6px; }
table.fire-table { width:100%; border-collapse:collapse; font-size:.8rem; }
table.fire-table th { color:#d9caa8; text-align:right; padding:.42rem .6rem; font-weight:700;
    border-bottom:1px solid rgba(255,255,255,.14); white-space:nowrap; }
table.fire-table td { color:#f2ecd8; text-align:right; padding:.36rem .6rem;
    border-bottom:1px solid rgba(255,255,255,.05); white-space:nowrap; }
table.fire-table td:first-child, table.fire-table th:first-child { text-align:left; }

/* 컴팩트: 위젯 사이 세로 간격을 줄여 스크롤 감소 (Global처럼 촘촘하게).
   2열 가로 유지는 CSS가 아니라 입력부를 st.columns 안에 넣는 구조로 해결한다
   (Streamlit 모바일 스택 규칙은 '컬럼 밖' 가로블록만 세로로 쌓기 때문). */
div[data-testid="stVerticalBlock"] { gap:.55rem !important; }
div[data-testid="stNumberInput"] label, div[data-testid="stDateInput"] label,
div[data-testid="stSelectbox"] label { margin-bottom:.1rem !important; font-size:.78rem !important; }
div[data-testid="stColumn"] { min-width:0 !important; }
</style>
""", unsafe_allow_html=True)

# ── constants ───────────────────────────────────────────────────────────────────
FREQ_KR = {"monthly": "월배당", "quarterly": "분기배당", "semiannual": "반기배당",
           "annual": "연배당", "irregular": "불규칙", "none": "무배당"}
MARKET_ORDER = ["United States", "ETF", "Global", "Korea", "Japan", "European Union"]
CUR_DEFAULTS = {
    "USD": dict(corpus=300_000,     corpus_step=10_000,     exp=1_500,     exp_step=100),
    "EUR": dict(corpus=300_000,     corpus_step=10_000,     exp=1_500,     exp_step=100),
    "KRW": dict(corpus=300_000_000, corpus_step=10_000_000, exp=1_500_000, exp_step=100_000),
    "JPY": dict(corpus=30_000_000,  corpus_step=1_000_000,  exp=150_000,   exp_step=10_000),
}
DEFAULT_TICKER = {"United States": "Coca-Cola / KO"}
MAX_ASSETS = 5
# per-asset chart palette (fits the olive/cream engine theme on cream paper)
ASSET_PALETTE = ["#ca6702", "#005f73", "#0a9396", "#bb3e03", "#94d2bd"]

# engine-parameter dropdowns: {UI label: engine value}
SELL_PRIORITY_OPTS = {
    "비율대로": "weights",
    "연배당 적은순": "annual_income",
    "배당률 낮은순": "yield",
    "주당배당 낮은순": "dps",
}
REINVEST_TARGET_OPTS = {
    "초기 비율대로 분산": "weights",
    "배당수익률 높은 종목에 몰아서": "highest_yield",
    "특정 종목에 집중": "specific",
}
SELL_PRIORITY_DESC = {
    "weights": "각 종목을 초기 비율대로 나눠서 매도 (구성 유지)",
    "annual_income": "연배당금(절대액)이 가장 적은 종목부터 처분",
    "yield": "배당수익률(연배당÷평가액)이 가장 낮은 종목부터 처분",
    "dps": "주당 배당금(DPS)이 가장 낮은 종목부터 처분",
}
REINVEST_TARGET_DESC = {
    "weights": "초기 비율대로 분산 재투자",
    "highest_yield": "배당수익률이 가장 높은 종목에 몰아서 재투자",
    "specific": "선택한 종목 한 곳에 잉여 배당을 전액 재투자",
}


def _rgba(hexc, a):
    h = hexc.lstrip("#")
    return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"


# ── header ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="fire-brand">
  <div class="brand-mark">🔥</div>
  <div>
    <div class="fire-title">FIRE 타당성 백테스트</div>
    <div class="fire-sub">은퇴 목돈으로 한 종목을 사고 매월 생활비를 인출했을 때 자산이 버텼는지 검증합니다 · 통화 환산 없음</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── inputs ──────────────────────────────────────────────────────────────────────
# 입력부를 단일 컬럼 안에 감싼다 → 내부 2열 행들이 'stColumn 자손'이 되어 Streamlit의
# 모바일 세로-스택 규칙(:not([data-testid="stColumn"] *))에서 제외 → Global Cup 대시보드
# 처럼 폰에서도 2열 가로 유지. (body 들여쓰기는 그대로: with A, B 결합)
with st.columns([1])[0], st.container(border=True):
    # 마켓 — 한 줄 (단독)
    market = st.selectbox("마켓", MARKET_ORDER,
                          format_func=lambda k: f"{MARKETS[k].flag}  {MARKETS[k].name}")
    mc = MARKETS[market]
    rule = get_market_rule(market)
    currency = rule["currency"]
    defaults = CUR_DEFAULTS.get(currency, CUR_DEFAULTS["USD"])

    tickers = build_ticker_dict(market) or {}
    labels = list(tickers)
    if not labels:
        st.error(f"'{market}' 종목 목록을 불러오지 못했습니다.")
        st.stop()
    def_label = DEFAULT_TICKER.get(market)
    default_sel = [def_label] if def_label in labels else labels[:1]
    # 종목 — 한 줄 (단독)
    sel_labels = st.multiselect(
        f"종목 (최대 {MAX_ASSETS}개)", labels, default=default_sel,
        max_selections=MAX_ASSETS, key=f"tickers_{market}")

    sym = get_currency_symbol(currency)

    # 은퇴 시작일 · 원천징수세 — 한 줄
    rA = st.columns(2)
    start = rA[0].date_input("은퇴 시작일", value=date(2000, 1, 1),
                             min_value=date(1970, 1, 1), max_value=date.today())
    tax = rA[1].number_input("원천징수세 (%)", value=float(rule["tax_rate"]),
                             step=0.5, min_value=0.0, max_value=100.0, key=f"tax_{market}")

    # 은퇴 자금 · 월 생활비 — 한 줄
    rB = st.columns(2)
    corpus = rB[0].number_input(f"은퇴 자금 ({sym})", value=defaults["corpus"],
                                step=defaults["corpus_step"], min_value=0, key=f"corpus_{currency}")
    monthly = rB[1].number_input(f"월 생활비 ({sym})", value=defaults["exp"],
                                 step=defaults["exp_step"], min_value=0, key=f"exp_{currency}")

    reinvest_surplus = st.toggle("잉여 배당 재투자", value=True,
                                 help="생활비 충당 후 남는 배당을 다음 배당까지 버퍼를 남기고 재매수 "
                                      "(대상 종목은 아래 '잉여 배당 집중 투자 종목'에서 선택)")

    if not sel_labels:
        st.info("종목을 1개 이상 선택하세요.")
        st.stop()

    # ── 비중(%) · 매도 우선순위 — 한 줄 ───────────────────────────────────────────
    # 비중 안의 종목별 입력은 세로로 쌓는다(컬럼 3단 중첩 회피). 종목이 1개면 그대로 깔끔.
    eq = round(100.0 / len(sel_labels), 2)
    wrow = st.columns([1.05, 1])
    with wrow[0]:
        # 라벨을 한 줄로(비중 헤더 제거) → 오른쪽 '매도 우선순위'와 입력칸 높이 정렬.
        raw_weights = []
        for lbl in sel_labels:
            short = lbl.split(" / ")[-1]
            w = st.number_input(f"비중(%) · {short}", value=eq, min_value=0.0, max_value=100.0,
                                step=5.0, key=f"w_{market}_{lbl}")
            raw_weights.append(float(w))
    with wrow[1]:
        # 매도 우선순위 — 기본값: 연배당금(절대액)이 가장 적은 종목부터 매도.
        _sell_default = list(SELL_PRIORITY_OPTS.values()).index("annual_income")
        sell_label = st.selectbox(
            "매도 우선순위", list(SELL_PRIORITY_OPTS),
            index=_sell_default, key=f"sell_{market}",
            help="생활비가 배당보다 클 때(배당 < 생활비) 어떤 종목부터 팔지 — "
                 "선택한 기준이 낮은 종목부터 매도")
        sell_priority = SELL_PRIORITY_OPTS[sell_label]

    wsum = sum(raw_weights)
    if wsum <= 0:
        st.warning("비중 합이 0입니다. 하나 이상 0보다 크게 설정하세요.")
        st.stop()
    if abs(wsum - 100.0) > 0.5:
        st.caption(f"⚠️ 비중 합 {wsum:.1f}% — 100%로 정규화하여 계산합니다.")

    # 잉여 배당은 항상 '한 종목 전액 집중 재투자'. 대상 종목만 아래에서 고른다.
    # (예전 '재투자 대상' 드롭다운은 제거 — 언제나 specific 모드.)
    reinvest_target = "specific"
    _pick_default = sel_labels[0] if sel_labels else labels[0]
    reinvest_pick_label = st.selectbox(
        "잉여 배당 집중 투자 종목  ·  바스켓 밖 종목도 가능", labels,
        index=labels.index(_pick_default) if _pick_default in labels else 0,
        key=f"reinv_pick_{market}",
        disabled=not reinvest_surplus,
        help="배당이 생활비보다 커서 남는 금액을 전액 이 종목에 재매수합니다 "
             "(잉여 배당 재투자 토글이 켜져 있을 때). 바스켓에 없는 종목을 고르면 "
             "초기 투자 없이 재투자만 받는 포지션으로 추가됩니다.")
    reinvest_ticker = tickers.get(reinvest_pick_label)

if corpus <= 0:
    st.info("은퇴 자금을 입력하세요.")
    st.stop()


def money(v, dec=0):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    return format_amount(v, currency, decimals=dec)


# ── load data for the whole basket ──────────────────────────────────────────────
today = date.today()
assets = []          # engine input (AssetSpec)
meta = []            # display meta: name, ticker, weight%, close, sch, color
with st.spinner(f"{len(sel_labels)}개 종목 데이터 로딩 중…"):
    for lbl, w in zip(sel_labels, raw_weights):
        if w <= 0:
            continue
        tk = tickers[lbl]
        nm = lbl.split(" / ")[0]
        price_df = download_price(tk, start, today)
        cl = get_close_series(price_df)
        if cl.empty:
            st.warning(f"'{tk}' 가격 데이터를 불러오지 못해 제외합니다.")
            continue
        dv = download_dividends(tk, date(max(start.year - 6, 1970), 1, 1), today)
        assets.append(AssetSpec(nm, tk, cl, dv, float(w)))
        meta.append({"name": nm, "ticker": tk, "weight": float(w),
                     "close": cl, "sch": classify(dv)})

# ── reinvest target OUTSIDE the basket: load it as a reinvest-only asset ──────────
reinvest_asset = None
_basket_tickers = {m["ticker"] for m in meta}
if (reinvest_surplus and reinvest_target == "specific"
        and reinvest_ticker and reinvest_ticker not in _basket_tickers):
    with st.spinner(f"재투자 대상 '{reinvest_ticker}' 데이터 로딩 중…"):
        _rdf = download_price(reinvest_ticker, start, today)
        _rcl = get_close_series(_rdf)
        if _rcl.empty:
            st.warning(f"재투자 대상 '{reinvest_ticker}' 가격 데이터를 불러오지 못해 "
                       f"'초기 비율대로 분산'으로 대체합니다.")
            reinvest_target = "weights"
        else:
            _rnm = (reinvest_pick_label.split(" / ")[0]
                    if reinvest_pick_label else reinvest_ticker)
            _rdv = download_dividends(reinvest_ticker,
                                      date(max(start.year - 6, 1970), 1, 1), today)
            reinvest_asset = AssetSpec(_rnm, reinvest_ticker, _rcl, _rdv, 0.0)
            # 스택/리베이스 차트에도 보이도록 meta에 편입 (초기배분 0 → wn 0%).
            meta.append({"name": _rnm, "ticker": reinvest_ticker, "weight": 0.0,
                         "close": _rcl, "sch": classify(_rdv), "reinvest_only": True})

if not assets:
    st.error("유효한 종목이 없습니다. 다른 종목/기간을 선택하세요.")
    st.stop()

# normalized weights (for display), aligned with `meta`
wtot = sum(m["weight"] for m in meta)
for m in meta:
    m["wn"] = m["weight"] / wtot * 100.0
for i, m in enumerate(meta):
    m["color"] = ASSET_PALETTE[i % len(ASSET_PALETTE)]

# ── market header (flag + serif name + basket) ──────────────────────────────────
chips = " ".join(
    f'<span style="display:inline-flex;align-items:center;gap:.3rem;'
    f'background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);'
    f'border-radius:999px;padding:.15rem .6rem;margin:.15rem .2rem;font-size:.78rem;color:#f2ecd8;">'
    f'<b style="color:{m["color"]};">●</b>{m["name"]} · {m["ticker"]} '
    f'<b style="color:#fff9ed;">{m["wn"]:.0f}%</b></span>'
    for m in meta)
st.markdown(
    f"""<div class="market-badge-row" style="margin-top:.4rem;">
  <div class="market-flag-box">{get_flag_svg(market)}</div>
  <div><div class="market-title">{mc.name} · {len(meta)}종목 포트폴리오</div></div>
</div>
<div style="margin:.4rem 0 .2rem;">{chips}</div>""",
    unsafe_allow_html=True,
)

result = run_fire_backtest_multi(
    assets, float(corpus), annual_withdrawal=float(monthly) * 12,
    strategy="fixed_nominal", frequency="monthly",
    tax_rate_pct=float(tax), reinvest_surplus=reinvest_surplus,
    sell_priority=sell_priority,       # UI: 매도 우선순위
    reinvest_target=reinvest_target,   # UI: 잉여 배당 재투자 대상
    reinvest_ticker=reinvest_ticker,   # UI: '특정 종목에 집중'일 때 대상 티커
    reinvest_asset=reinvest_asset,     # UI: 바스켓 밖 종목이면 재투자 전용 편입
    start_date=start,
)
if result is None:
    st.error("백테스트를 실행할 수 없습니다. 입력값을 확인하세요.")
    st.stop()

s, tl = result.summary, result.timeline_df
asum = result.asset_summary_df

# ── verdict banner ──────────────────────────────────────────────────────────────
basket = " + ".join(m["ticker"] for m in meta)
if s["Survived"]:
    st.markdown(
        f'<div class="verdict ok">✅ <b>생존</b> — {basket} · '
        f'{s["Years"]:.1f}년간 월 {money(monthly)} 인출 후 최종 자산 <b>{money(s["Final Value"])}</b></div>',
        unsafe_allow_html=True)
else:
    dep = pd.Timestamp(s["Depletion Date"]).date()
    st.markdown(
        f'<div class="verdict bad">❌ <b>고갈</b> — {basket} · '
        f'자산이 <b>{dep}</b>에 소진됨 (약 {s["Survived Years"]:.1f}년 지속)</div>',
        unsafe_allow_html=True)

# ── metric cards ────────────────────────────────────────────────────────────────
delta_pct = (s["Final Value"] / corpus - 1) * 100
delta_cls = "sub" if delta_pct >= 0 else "sub neg"


def card(lbl, val, sub_html=""):
    return f'<div class="mcard"><div class="lbl">{lbl}</div><div class="val">{val}</div>{sub_html}</div>'


cards = [
    card("최종 자산", money(s["Final Value"]),
         f'<div class="{delta_cls}">{delta_pct:+.0f}% vs 원금</div>'),
    card("총 인출액", money(s["Total Withdrawn"])),
    card("총 배당 (세후)", money(s["Total Net Dividend"])),
    card("총 매도액", money(s["Total Shares Sold Value"])),
    card("종목 수", f'{s["N Assets"]}개'),
    card("잉여 재투자액", money(s["Total Reinvested Surplus"])),
    card("최대 낙폭 (MDD)", f'{s["Max Drawdown %"]:.0f}%'),
    card("최저 자산", money(s["Min Portfolio Value"])),
]
st.markdown(f'<div class="mgrid">{"".join(cards)}</div>', unsafe_allow_html=True)

# ── chart helper ────────────────────────────────────────────────────────────────
def _style(fig, ytitle):
    # Match Global Cup's chart style (charts.py _LAYOUT_BASE): an OPAQUE cream
    # paper baked into the figure + dark ink text. This keeps axis labels (years,
    # x/y values) readable regardless of the app theme, and uses the same size as
    # the Global Cup dashboard (CHART_HEIGHT_PRICE = 360).
    fig.update_layout(
        height=360, margin=dict(l=40, r=26, t=44, b=38),
        paper_bgcolor="rgba(255,249,237,1)", plot_bgcolor="rgba(255,253,244,1)",
        font=dict(color="#1f2b18", family="Inter, sans-serif", size=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(color="#1f2b18", size=10)),
        hovermode="x unified",
        yaxis=dict(title=ytitle, showgrid=True, gridcolor="rgba(31,43,24,.08)",
                   zeroline=False, tickfont=dict(color="#1f2b18", size=10),
                   title_font=dict(color="#1f2b18", size=11)),
        xaxis=dict(showgrid=True, gridcolor="rgba(31,43,24,.08)",
                   tickfont=dict(color="#1f2b18", size=10)),
    )
    return fig


# ── portfolio value chart (stacked per stock + cash) ─────────────────────────────
st.markdown('<div class="chart-h">💰 자산 추이 (종목별 스택)</div>', unsafe_allow_html=True)
fig = go.Figure()
for m in meta:
    fig.add_trace(go.Scatter(
        x=tl["Date"], y=tl[m["ticker"]], name=f'{m["ticker"]} ({m["wn"]:.0f}%)',
        mode="lines", line=dict(width=0.6, color=m["color"]),
        stackgroup="v", fillcolor=_rgba(m["color"], .55)))
if (tl["Cash"] > 1e-6).any():
    fig.add_trace(go.Scatter(
        x=tl["Date"], y=tl["Cash"], name="현금(배당)",
        mode="lines", line=dict(width=0.4, color="#b0985f"),
        stackgroup="v", fillcolor=_rgba("#b0985f", .35)))
fig.add_trace(go.Scatter(
    x=tl["Date"], y=tl["Cumulative Withdrawn"] + corpus, name="원금 + 누적인출",
    line=dict(color="#33402a", width=1.4, dash="dot")))
fig.add_hline(y=corpus, line=dict(color="#6f9a3f", width=1, dash="dash"),
              annotation_text=f"은퇴 원금 {money(corpus)}", annotation_position="top left",
              annotation_font_color="#5a6b3f")
if not s["Survived"] and s["Depletion Date"] is not None:
    fig.add_vline(x=pd.Timestamp(s["Depletion Date"]), line=dict(color="#e23636", width=1.5),
                  annotation_text="고갈", annotation_position="top", annotation_font_color="#c0392b")
st.plotly_chart(_style(fig, f"자산 ({sym})"), width="stretch", theme=None)

# ── per-stock breakdown table ───────────────────────────────────────────────────
st.markdown('<div class="chart-h">📦 종목별 결과</div>', unsafe_allow_html=True)
sch_by_tk = {m["ticker"]: m["sch"] for m in meta}
brk = asum.copy()
brk["배당주기"] = brk["Ticker"].map(
    lambda tk: FREQ_KR.get(sch_by_tk[tk].frequency, sch_by_tk[tk].frequency))
brk_show = pd.DataFrame({
    "종목": brk["Name"] + " · " + brk["Ticker"],
    "비중": brk["Weight %"].map(lambda v: f"{v:.0f}%"),
    "배당주기": brk["배당주기"],
    "초기 투자금": brk["Initial Amount"].map(money),
    "최종 평가액": brk["Final Value"].map(money),
    "총 배당(세후)": brk["Total Net Dividend"].map(money),
    "총 매도액": brk["Total Sold Value"].map(money),
})
st.markdown('<div class="table-scroll">'
            + brk_show.to_html(index=False, classes="fire-table", border=0, escape=False)
            + '</div>', unsafe_allow_html=True)
_reinv_txt = REINVEST_TARGET_DESC[reinvest_target] if reinvest_surplus else "재투자 안 함"
if reinvest_surplus and reinvest_target == "specific" and reinvest_ticker:
    _reinv_txt = f"{reinvest_ticker} 한 종목에 잉여 배당 전액 집중 재투자"
st.caption(f"매도 우선순위: {SELL_PRIORITY_DESC[sell_priority]} · 잉여 배당: {_reinv_txt}")

# ── annual breakdown ────────────────────────────────────────────────────────────
tl2 = tl.copy(); tl2["Year"] = tl2["Date"].dt.year
annual = tl2.groupby("Year").agg(
    배당세후=("Dividend", "sum"), 인출=("Withdrawal", "sum"),
    연말자산=("Portfolio Value", "last")).round(0)
annual["매도필요"] = (annual["인출"] - annual["배당세후"]).clip(lower=0).round(0)

# 종목별 연말 보유 주식수량 (엔진 timeline의 f"{ticker}__sh" 컬럼, 연말=마지막값)
share_cols = []
for m in meta:
    scol = f'{m["ticker"]}__sh'
    if scol in tl2.columns:
        name = f'{m["ticker"]} 수량(주)'
        annual[name] = tl2.groupby("Year")[scol].last()
        share_cols.append(name)

with st.expander("📅 연도별 상세 (종목별 보유 수량 포함)", expanded=False):
    base_cols = ["Year", "배당세후", "인출", "매도필요", "연말자산"]
    show = annual.reset_index()[base_cols + share_cols].copy()
    show.columns = ["연도", "배당(세후)", "인출", "매도필요", "연말 자산"] + share_cols
    for c in ["배당(세후)", "인출", "매도필요", "연말 자산"]:
        show[c] = show[c].map(lambda v: money(v))
    for c in share_cols:
        show[c] = show[c].map(lambda v: f"{v:,.1f}")
    show["연도"] = show["연도"].astype(str)
    st.markdown('<div class="table-scroll">'
                + show.to_html(index=False, classes="fire-table", border=0, escape=False)
                + '</div>', unsafe_allow_html=True)

# ── rebased price chart — 종목별 탭으로 각각 표시 (시작=100 리베이스) ─────────────────
st.markdown('<div class="chart-h">📉 종목별 주가 (시작=100 리베이스)</div>', unsafe_allow_html=True)
start_ts = pd.Timestamp(tl["Date"].iloc[0])
px_tabs = st.tabs([m["ticker"] for m in meta])
for _tab, m in zip(px_tabs, meta):
    with _tab:
        cl = m["close"]
        cl = cl[cl.index >= start_ts]
        if cl.empty or float(cl.iloc[0]) <= 0:
            st.caption("이 종목의 가격 데이터가 없습니다.")
            continue
        base = float(cl.iloc[0])
        pfig = go.Figure()
        pfig.add_trace(go.Scatter(
            x=cl.index, y=cl.values / base * 100.0, name=m["ticker"],
            line=dict(color=m["color"], width=1.8), fill="tozeroy",
            fillcolor=_rgba(m["color"], .12)))
        if not s["Survived"] and s["Depletion Date"] is not None:
            pfig.add_vline(x=pd.Timestamp(s["Depletion Date"]), line=dict(color="#e23636", width=1.5),
                           annotation_text="고갈", annotation_position="top",
                           annotation_font_color="#c0392b")
        st.plotly_chart(_style(pfig, "리베이스 (시작=100)"), width="stretch",
                        theme=None, key=f"px_tab_{m['ticker']}")

st.markdown(
    f'<div class="market-subtitle" style="margin-top:.6rem;">데이터 {tl["Date"].iloc[0].date()} ~ '
    f'{tl["Date"].iloc[-1].date()} · {market} · {basket} · '
    f'Copyright © zealatan</div>', unsafe_allow_html=True)
