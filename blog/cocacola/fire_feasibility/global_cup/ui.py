from __future__ import annotations

from datetime import date, datetime
from typing import Optional

import pandas as pd
import streamlit as st

from .analysis import fmt_money, fmt_pct, run_analysis
from .formatting import format_year, format_amount, format_percent, get_currency_symbol
from .charts import (
    add_high_low_markers,
    add_trigger_buy_markers,
    annual_dividend_income_chart,
    dividend_bar_chart,
    investment_comparison_chart,
    investment_quantity_chart,
    investment_simulation_chart,
    price_chart,
    reinvest_timeline_chart,
    score_gauge_chart,
    share_count_chart,
    share_quantity_comparison_bar_chart,
)
from .config import LANDING_URL, TRIGGER_DEFAULT, get_market_rule
from .dividend_reinvest import run_dividend_reinvest_backtest
from .high_scanner import SCAN_THRESHOLD, filter_by_min_drop, scan_market
from .market_config import (
    MARKETS,
    AnalysisResult,
    MarketConfig,
    UserInput,
    get_flag_class,
    get_flag_svg,
)
from .scoring import ScoreResult, calculate_score, get_rank_color, get_rank_medal


# Hide the Plotly modebar so its top-right icons don't overlap centered titles.
PLOTLY_CONFIG = {"displayModeBar": False}


# ── CSS ────────────────────────────────────────────────────────────────────────

_CSS = """
<style>
:root {
    --bg:    #0b1008;
    --cream: #fff5dc;
    --paper: #fff9ed;
    --text:  #1f2b18;
    --muted: #d9caa8;
}

.stApp {
    background:
        radial-gradient(circle at 18% 16%, rgba(231,255,155,.16), transparent 28rem),
        radial-gradient(circle at 82% 8%,  rgba(255,255,255,.09), transparent 30rem),
        linear-gradient(180deg, #0b1008 0%, #111a0e 54%, #070a05 100%);
    color: var(--cream);
}

.main .block-container,
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewBlockContainer"],
section[data-testid="stMain"] .block-container {
    max-width: 1240px;
    padding-top: 2.7rem !important;
    padding-bottom: 4rem;
}

/* Shrink the top header bar (keep it, so the ⋮ menu still works) so the
   Market page selector sits just below it without overlap or a big gap. */
header, [data-testid="stHeader"] {
    background: transparent !important;
    height: 2.5rem !important;
    min-height: 2.5rem !important;
}

h1, h2, h3, h4, p, label, span, div {
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
}

h1, h2, h3, h4 { color: var(--cream) !important; }

.top-nav {
    height: 62px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.7rem;
}

.brand {
    display: flex;
    align-items: center;
    gap: .75rem;
    font-size: 1.25rem;
    font-weight: 950;
    color: var(--cream);
}

.brand-mark {
    width: 38px; height: 38px;
    border-radius: 999px;
    display: grid; place-items: center;
    background: linear-gradient(135deg, #f7ffd4, #8dbb55);
    color: #14200d;
    box-shadow: 0 12px 28px rgba(142,185,87,.22);
}

.home-pill {
    border: 1px solid rgba(255,255,255,.16);
    border-radius: 999px;
    color: var(--cream) !important;
    background: rgba(255,255,255,.08);
    padding: .75rem 1.2rem;
    font-weight: 950;
    text-decoration: none !important;
    display: inline-flex;
    align-items: center;
    transition: background .18s;
}

.home-pill:hover { background: rgba(255,255,255,.14); }

div[data-testid="stExpander"] {
    background: rgba(255,255,255,.035) !important;
    border: 1px solid rgba(255,255,255,.07) !important;
    border-radius: 10px !important;
}

.market-badge-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 0.8rem;
}

.market-code-box {
    width: 56px; height: 56px;
    border-radius: 16px;
    background: #fff9ed;
    color: #1f2b18;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; font-weight: 950; letter-spacing: -.5px;
    border: 1px solid rgba(255,255,255,.7);
    box-shadow: 0 12px 30px rgba(0,0,0,.22);
    flex-shrink: 0; line-height: 1;
}

.market-flag-box {
    width: 56px; height: 56px;
    border-radius: 16px;
    background: #fff9ed;
    display: flex; align-items: center; justify-content: center;
    border: 1px solid rgba(255,255,255,.7);
    box-shadow: 0 12px 30px rgba(0,0,0,.22);
    flex-shrink: 0;
}

.drawn-flag {
    width: 38px; height: 25px;
    border-radius: 6px;
    box-shadow: inset 0 0 0 1px rgba(0,0,0,.12);
    position: relative; overflow: hidden; flex-shrink: 0;
}

.flag-jp {
    background:
        radial-gradient(circle at 50% 50%, #bc002d 0 28%, transparent 29%),
        #fff;
}

.flag-us {
    background:
        linear-gradient(to bottom,
            #b22234  0%   7.7%, #fff    7.7%  15.4%,
            #b22234 15.4% 23.1%, #fff  23.1%  30.8%,
            #b22234 30.8% 38.5%, #fff  38.5%  46.2%,
            #b22234 46.2% 53.9%, #fff  53.9%  61.6%,
            #b22234 61.6% 69.3%, #fff  69.3%  77%,
            #b22234 77%   84.7%, #fff  84.7%  92.4%,
            #b22234 92.4% 100%);
}
.flag-us::before {
    content: ""; position: absolute;
    left: 0; top: 0; width: 45%; height: 54%;
    background: #3c3b6e; border-radius: 10px 0 4px 0;
}

.flag-eu {
    background:
        radial-gradient(circle at 50% 16%, #ffcc00 0 4%, transparent 5%),
        radial-gradient(circle at 72% 25%, #ffcc00 0 4%, transparent 5%),
        radial-gradient(circle at 84% 50%, #ffcc00 0 4%, transparent 5%),
        radial-gradient(circle at 72% 75%, #ffcc00 0 4%, transparent 5%),
        radial-gradient(circle at 50% 84%, #ffcc00 0 4%, transparent 5%),
        radial-gradient(circle at 28% 75%, #ffcc00 0 4%, transparent 5%),
        radial-gradient(circle at 16% 50%, #ffcc00 0 4%, transparent 5%),
        radial-gradient(circle at 28% 25%, #ffcc00 0 4%, transparent 5%),
        #003399;
}

.flag-kr {
    background:
        radial-gradient(circle at 50% 44%, #cd2e3a 0 19%, transparent 20%),
        radial-gradient(circle at 50% 58%, #0047a0 0 19%, transparent 20%),
        #fff;
}

.flag-glb {
    width: 36px; height: 36px; border-radius: 50%;
    background:
        radial-gradient(circle at 35% 35%, #6ee7b7 0 12%, transparent 13%),
        radial-gradient(circle at 65% 60%, #22c55e  0 18%, transparent 19%),
        radial-gradient(circle at 50% 50%, #38bdf8  0 60%, #1d4ed8 100%);
}

.market-title {
    font-family: Georgia, "Times New Roman", serif;
    font-size: clamp(26px, 3vw, 40px);
    line-height: 1; letter-spacing: -1.2px;
    font-weight: 500; color: var(--cream);
    margin-bottom: 0;
}

.market-subtitle {
    color: var(--muted);
    line-height: 1.4; max-width: 640px;
    font-size: 0.78rem; margin-bottom: 0.7rem;
}

div[data-testid="stTextInput"],
div[data-testid="stSelectbox"] {
    background: rgba(255,255,255,.075) !important;
    border: 1px solid rgba(255,255,255,.14) !important;
    border-radius: 8px !important;
    padding: 0 .65rem 0 !important;
    box-shadow: 0 6px 16px rgba(0,0,0,.1) !important;
}

div[data-testid="stTextInput"] label,
div[data-testid="stSelectbox"] label {
    color: #fff5dc !important;
    font-weight: 900 !important;
    font-size: .58rem !important;
    line-height: 1.05 !important;
    background: transparent !important;
    margin-bottom: 0 !important;
    min-height: 0 !important;
}

div[data-testid="stNumberInput"] label,
div[data-testid="stSlider"] label {
    color: #e8e3cf !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    opacity: 1.0 !important;
}

div[data-testid="stCheckbox"] label,
div[data-testid="stCheckbox"] label p,
div[data-testid="stCheckbox"] span,
div[data-testid="stToggle"] label,
div[data-testid="stToggle"] label p,
div[data-testid="stToggle"] span {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 600 !important;
    opacity: 1.0 !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div > div,
div[data-baseweb="input"],
div[data-baseweb="input"] > div,
div[data-baseweb="base-input"],
div[data-baseweb="base-input"] > div {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #fff5dc !important;
}

input, input[type="text"] {
    background: transparent !important;
    background-color: transparent !important;
    color: #fff5dc !important;
    -webkit-text-fill-color: #fff5dc !important;
    border: none !important;
    box-shadow: none !important;
    caret-color: #fff5dc !important;
    font-weight: 700 !important;
}

input::placeholder {
    color: rgba(255,245,220,.50) !important;
    -webkit-text-fill-color: rgba(255,245,220,.50) !important;
    font-weight: 400 !important;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] svg {
    color: #fff5dc !important;
    fill: rgba(255,245,220,.75) !important;
}

div[data-baseweb="popover"],
div[data-baseweb="popover"] * { color: #1f2b18 !important; }

.stTabs { margin-top: 0 !important; }

.stTabs [data-baseweb="tab-list"] {
    gap: .5rem !important;
    background: rgba(255,255,255,.06) !important;
    padding: .3rem !important;
    border-radius: 999px !important;
    border: 1px solid rgba(255,255,255,.09) !important;
    margin-bottom: .8rem !important;
    justify-content: center !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 999px !important;
    padding: .35rem 1.5rem !important;
    min-height: 0 !important;
    height: auto !important;
    color: rgba(255,245,220,.72) !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    background: transparent !important;
    transition: background .18s, color .18s !important;
}

.stTabs [aria-selected="true"] {
    background: #fff5dc !important;
    color: #1f2b18 !important;
}

.stTabs [data-baseweb="tab-panel"],
div[data-testid="stTabsContent"],
div[data-testid="stTabPanel"] {
    background: transparent !important;
    padding-top: 0 !important;
    border: none !important;
    box-shadow: none !important;
}

.chart-wrap {
    background: rgba(255,249,237,.96);
    border-radius: 34px;
    padding: 1rem;
    box-shadow: 0 22px 58px rgba(0,0,0,.16);
    border: 1px solid rgba(255,255,255,.56);
    margin-bottom: 1.2rem;
    overflow: hidden;
}

div[data-testid="stPlotlyChart"] {
    background: rgba(255,249,237,.96) !important;
    border-radius: 28px !important;
    overflow: hidden !important;
}

.recent-title {
    color: var(--cream);
    font-size: 1.3rem;
    font-weight: 950;
    margin: 1.6rem 0 .8rem;
}

[data-testid="stDataFrame"] {
    background: #fff9ed !important;
    border-radius: 28px !important;
    overflow: hidden !important;
    padding: .4rem !important;
    box-shadow: 0 18px 45px rgba(0,0,0,.16) !important;
}

.stCaptionContainer,
.stCaptionContainer p { color: rgba(255,245,220,.62) !important; }

.score-card {
    background: rgba(255,249,237,.96);
    border-radius: 28px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 18px 45px rgba(0,0,0,.18);
    border: 1px solid rgba(255,255,255,.56);
    color: #1f2b18;
    margin-bottom: 1rem;
}

.rank-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border-radius: 999px;
    padding: 6px 14px;
    font-weight: 950;
    font-size: 15px;
    color: #1f2b18;
    margin-bottom: 10px;
}

.ranking-row {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 10px 16px;
    border-radius: 16px;
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(255,255,255,.08);
    margin-bottom: 8px;
}

.ranking-pos {
    font-size: 22px;
    font-weight: 950;
    color: var(--cream);
    width: 28px;
    text-align: center;
}

.ranking-market {
    flex: 1;
    color: var(--cream);
    font-weight: 700;
}

.ranking-score {
    font-size: 18px;
    font-weight: 950;
    color: var(--cream);
}

@media (max-width: 900px) {
    .market-title { font-size: 34px; letter-spacing: -1.2px; }
    .chart-wrap { border-radius: 24px; padding: .75rem; }
    .market-code-box, .market-flag-box { width: 50px; height: 50px; border-radius: 14px; }
    .market-code-box { font-size: 20px; }
}

div[data-testid="stExpander"],
div[data-testid="stExpander"] *,
div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] summary *,
div[data-testid="stExpander"] label,
div[data-testid="stExpander"] p,
div[data-testid="stExpander"] span,
div[data-testid="stExpander"] div[role="radiogroup"] label,
div[data-testid="stExpander"] div[role="radiogroup"] label * {
    color: #fff5dc !important;
    -webkit-text-fill-color: #fff5dc !important;
}

div[data-testid="stExpander"] svg {
    color: #fff5dc !important;
    fill: #fff5dc !important;
}

/* ── Market Snapshot section ──────────────────────────────────────────────── */

.snapshot-section {
    margin-top: 2.2rem;
    margin-bottom: 1.5rem;
}

.snapshot-header {
    color: var(--cream);
    font-size: 1.55rem;
    font-weight: 950;
    letter-spacing: -0.4px;
    margin-bottom: 0;
}

.snapshot-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,.10);
    margin: 0.55rem 0 1.1rem;
}

.snapshot-col-label {
    color: rgba(255,245,220,.62);
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-bottom: 0.55rem;
}

/* ── Summary metric cards ──────────────────────────────────────────────────── */

.snap-metrics-row {
    display: flex;
    gap: 8px;
    margin-bottom: 0.9rem;
    flex-wrap: wrap;
}

.snap-metric {
    background: rgba(255,255,255,.055);
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 13px;
    padding: 0.6rem 0.85rem;
    flex: 1;
    min-width: 90px;
    box-shadow: 0 4px 14px rgba(0,0,0,.12);
    transition: background .18s;
}

.snap-metric:hover {
    background: rgba(255,255,255,.09);
}

.snap-metric-label {
    color: rgba(255,245,220,.55);
    font-size: 0.67rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.22rem;
}

.snap-metric-value {
    color: var(--cream);
    font-size: 0.95rem;
    font-weight: 950;
    line-height: 1.2;
    letter-spacing: -0.3px;
}

/* ── Premium data table ────────────────────────────────────────────────────── */

.premium-table-wrap {
    background: rgba(255,249,237,.96);
    border-radius: 16px;
    box-shadow: 0 14px 40px rgba(0,0,0,.18);
    border: 1px solid rgba(31,43,24,.10);
    max-height: 400px;
    overflow-x: auto;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: #8eb957 rgba(255,249,237,.96);
}

.premium-table-wrap::-webkit-scrollbar {
    width: 5px;
}

.premium-table-wrap::-webkit-scrollbar-track {
    background: rgba(255,249,237,.96);
    border-radius: 8px;
}

.premium-table-wrap::-webkit-scrollbar-thumb {
    background: #8eb957;
    border-radius: 8px;
}

.premium-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 10px;
    font-family: 'SF Mono', 'JetBrains Mono', 'Fira Code', monospace, ui-sans-serif;
}

.premium-table thead th {
    background: #1f2b18;
    color: #fff5dc;
    font-weight: 800;
    font-size: 9.5px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 4px 6px;
    text-align: right;
    position: sticky;
    top: 0;
    z-index: 10;
    border-bottom: 2px solid rgba(31,43,24,.30);
    white-space: nowrap;
}

.premium-table thead th:first-child {
    text-align: left;
    padding-left: 8px;
}

.premium-table tbody td {
    padding: 3px 6px;
    text-align: right;
    color: #263522;
    font-weight: 600;
    border-bottom: 1px solid rgba(31,43,24,.07);
    font-size: 10.5px;
    white-space: nowrap;
}

.premium-table tbody td:first-child {
    text-align: left;
    color: #3f5f38;
    font-weight: 700;
    padding-left: 8px;
}

.premium-table tbody tr:hover td {
    background: rgba(142,185,87,.08) !important;
    transition: background .12s;
}

/* Neutral alternating rows only — no full-row color */
.row-neutral td { background: rgba(255,249,237,.96); }
.row-alt td     { background: rgba(244,238,220,.50); }

/* Close cell text accent only — no row-level tint */
td.close-up   { color: #6f8f3f !important; font-weight: 700 !important; }
td.close-down { color: #a14d36 !important; font-weight: 700 !important; }

/* Volume cells — muted sage */
td.vol-cell {
    color: #6c745e !important;
    font-size: 12px !important;
    font-weight: 500 !important;
}

/* Alternating rows for dividend table */
.div-row-even td { background: rgba(244,238,220,.45); }
.div-row-odd  td { background: rgba(255,249,237,.94); }

/* Dividend growth positive/negative */
.div-positive { color: #6f8f3f !important; font-weight: 800 !important; }
.div-negative { color: #a14d36 !important; font-weight: 800 !important; }

/* ── Type badges (ZigZag events table) ─────────────────────────────────────── */

.type-badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 9999px;
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 0.03em;
    line-height: 1.55;
    white-space: nowrap;
}

.badge-high    { background: rgba(111,143,63,.16); color: #6f8f3f; border: 1px solid rgba(111,143,63,.28); }
.badge-low     { background: rgba(161,77,54,.13);  color: #a14d36; border: 1px solid rgba(161,77,54,.28); }
.badge-buy     { background: rgba(200,164,93,.16); color: #7a5e20; border: 1px solid rgba(200,164,93,.28); }
.badge-current { background: rgba(31,43,24,.09);   color: #3f5f38; border: 1px solid rgba(31,43,24,.18); }

/* ── Year badges (Annual Dividend table) ───────────────────────────────────── */

.div-badge {
    display: inline-block;
    padding: 0 3px;
    border-radius: 9999px;
    font-size: 7px;
    font-weight: 800;
    margin-left: 2px;
    vertical-align: middle;
    line-height: 1.4;
}

/* Year column (with badge): shrink to minimum content width */
.premium-table th:first-child,
.premium-table td:first-child {
    width: 1%;
    white-space: nowrap;
}

/* 2nd & 3rd column headers: allow wrapping to 2 lines to reduce width */
.premium-table th:nth-child(2),
.premium-table th:nth-child(3) {
    white-space: normal !important;
    word-break: keep-all;
    max-width: 4.5em;
    line-height: 1.15;
}

.badge-div-latest  { background: rgba(111,143,63,.16); color: #6f8f3f; border: 1px solid rgba(111,143,63,.28); }
.badge-div-highest { background: rgba(200,164,93,.16); color: #7a5e20; border: 1px solid rgba(200,164,93,.28); }
.badge-div-lowest  { background: rgba(161,77,54,.13);  color: #a14d36; border: 1px solid rgba(161,77,54,.28); }

/* ── Price-tab metric cards (dark-glass) ───────────────────────────────────── */

.price-metric-row {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 0.85rem;
}

.price-metric {
    background: rgba(255,255,255,.055);
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 14px;
    padding: 0.85rem 1.1rem;
    flex: 1;
    min-width: 140px;
    box-shadow: 0 3px 10px rgba(0,0,0,.12);
    transition: background .15s;
}

.price-metric:hover { background: rgba(255,255,255,.09); }

.price-metric-label {
    color: rgba(255,245,220,.55);
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.18rem;
}

.price-metric-value {
    color: var(--cream);
    font-size: 1.2rem;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.4px;
}

.price-metric-trigger-hit  { color: #f87171 !important; }
.price-metric-trigger-ok   { color: #86efac !important; }

.price-metric-sub {
    color: rgba(255,245,220,.42);
    font-size: 0.58rem;
    margin-top: 0.18rem;
    letter-spacing: 0.02em;
}

/* ── Reinvest summary (left col, dark-glass) ───────────────────────────────── */

.reinvest-summary-section {
    margin-top: 0.6rem;
    padding: 0.6rem 0.7rem;
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.085);
    border-radius: 13px;
    box-shadow: 0 4px 18px rgba(0,0,0,.12);
}

.reinvest-summary-title {
    color: rgba(255,245,220,.70);
    font-size: 0.68rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-bottom: 0.4rem;
}

.reinvest-metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 5px;
}

.reinvest-metric {
    background: rgba(255,255,255,.038);
    border: 1px solid rgba(255,255,255,.065);
    border-radius: 9px;
    padding: 0.35rem 0.45rem;
}

.reinvest-metric-label {
    color: rgba(255,245,220,.52);
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.1rem;
}

.reinvest-metric-value {
    color: #e8e0cc;
    font-size: 0.86rem;
    font-weight: 700;
    letter-spacing: -0.3px;
    line-height: 1.15;
}

.reinvest-caption {
    color: rgba(255,245,220,.36);
    font-size: 0.56rem;
    margin-top: 0.3rem;
    line-height: 1.4;
}

/* ── Compact controls (ticker / trigger / dates / reinvest inputs) ──────────── */
[data-testid="stVerticalBlock"] { gap: 0.45rem; }

[data-testid="stWidgetLabel"],
.stTextInput label, .stSelectbox label, .stNumberInput label {
    margin-bottom: 0.1rem !important;
}
[data-testid="stWidgetLabel"] p,
.stTextInput label, .stSelectbox label, .stNumberInput label {
    font-size: 0.7rem !important;
    line-height: 1.1 !important;
    color: rgba(255,245,220,.6) !important;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    height: 30px !important;
    line-height: 30px !important;
    font-size: 0.8rem !important;
}

/* Kill baseweb's built-in ~40px min-height on inputs and select controls */
[data-testid="stTextInput"] div[data-baseweb="input"],
[data-testid="stTextInput"] div[data-baseweb="base-input"],
[data-testid="stNumberInput"] div[data-baseweb="input"],
[data-testid="stNumberInput"] div[data-baseweb="base-input"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    min-height: 30px !important;
    height: 30px !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div > div {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    line-height: 30px !important;
}

[data-testid="stCheckbox"] { margin-top: 0.05rem; }
[data-testid="stCheckbox"] label { font-size: 0.8rem !important; }

/* Description sentences (st.caption) — as small as possible */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
small, .stCaption {
    font-size: 0.66rem !important;
    line-height: 1.35 !important;
    color: rgba(255,245,220,.5) !important;
}

/* Section subheaders (st.subheader) — tighter */
[data-testid="stHeading"] h1,
[data-testid="stHeading"] h2,
[data-testid="stHeading"] h3 {
    font-size: 1.15rem !important;
    margin-bottom: 0.15rem !important;
    padding-top: 0.2rem !important;
}

/* Tabs: compact so all fit on one row */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0.15rem;
    flex-wrap: nowrap;
    overflow-x: auto;
    justify-content: center !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
    min-width: auto !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] p,
[data-testid="stTabs"] [data-baseweb="tab"] div {
    font-size: 0.8rem !important;
    white-space: nowrap;
}

@media (max-width: 768px) {
    .snap-metrics-row { gap: 6px; }
    .snap-metric { min-width: 80px; padding: 0.5rem 0.7rem; }
    .snap-metric-value { font-size: 0.85rem; }
    .premium-table { font-size: 9px; }
    .premium-table tbody td { font-size: 9px; padding: 2px 4px; }
    .premium-table thead th { font-size: 8.5px; padding: 3px 4px; }
    .premium-table-wrap { max-height: 320px; }
    .price-metric-row { gap: 5px; }
    .price-metric { min-width: 78px; }
    .reinvest-metric-grid { grid-template-columns: repeat(3, 1fr); }

    /* ── Mobile: stack ONLY the top-level layout columns (left/right).
       :not(...) excludes horizontal blocks nested inside a column, so the
       inner columns keep their Streamlit ratio (e.g. ticker/trigger 8:2). */
    [data-testid="stHorizontalBlock"]:not([data-testid="stColumn"] *) {
        flex-direction: column !important;
        gap: 1.6rem !important;
    }
    [data-testid="stHorizontalBlock"]:not([data-testid="stColumn"] *) > [data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    /* Inner columns: force ONE row, no wrap; keep their inline ratio untouched.
       min-width:0 lets the narrow trigger column shrink instead of wrapping. */
    [data-testid="stColumn"] [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 0.4rem !important;
    }
    [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        min-width: 0 !important;
    }

    /* Kill the desktop alignment spacer that pushes the right tabs down */
    .right-col-spacer { height: 0 !important; display: none !important; }

    /* Tighten page padding so content uses full mobile width */
    .main .block-container {
        padding-left: 0.7rem !important;
        padding-right: 0.7rem !important;
        padding-top: 0.4rem !important;
    }

    /* Keep tabs on one row, horizontal-scroll if needed */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        flex-wrap: nowrap;
        overflow-x: auto;
        gap: 0.1rem;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] p,
    [data-testid="stTabs"] [data-baseweb="tab"] div {
        font-size: 0.72rem !important;
    }
}

/* Buttons — Streamlit's default renders near-white on the dark theme and is
   invisible. Match the brand mark: lime→olive gradient with dark text. */
.stButton > button,
[data-testid="stButton"] button,
[data-testid="baseButton-secondary"],
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #f7ffd4, #8dbb55) !important;
    color: #14200d !important;
    border: 1px solid rgba(255,255,255,.18) !important;
    border-radius: 999px !important;
    font-weight: 800 !important;
    padding: .5rem 1.2rem !important;
    box-shadow: 0 10px 24px rgba(142,185,87,.22) !important;
    transition: filter .15s, transform .05s;
}
.stButton > button *,
[data-testid="stButton"] button * {
    color: #14200d !important;
}
.stButton > button:hover,
[data-testid="stButton"] button:hover {
    filter: brightness(1.06);
    border-color: rgba(255,255,255,.35) !important;
}
.stButton > button:active,
[data-testid="stButton"] button:active {
    transform: translateY(1px);
}
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


# ── Top nav ────────────────────────────────────────────────────────────────────

def render_top_nav() -> None:
    st.markdown(
        f"""
<div class="top-nav">
  <div class="brand">
    <div class="brand-mark">📈</div>
    <div>Global Cup</div>
  </div>
  <a class="home-pill" href="{LANDING_URL}" target="_self">← Back to home</a>
</div>
""",
        unsafe_allow_html=True,
    )


# ── Market selector ────────────────────────────────────────────────────────────

def _get_market_from_query() -> str:
    market = st.query_params.get("market", "ETF")
    return market if market in MARKETS else "ETF"


def render_market_selector() -> MarketConfig:
    default_market = _get_market_from_query()
    market_keys = list(MARKETS.keys())

    with st.expander("Market page selector", expanded=False):
        selected = st.radio(
            "Market",
            market_keys,
            index=market_keys.index(default_market),
            horizontal=True,
            key="selected_market",
        )

    st.query_params["market"] = selected
    return MARKETS[selected]


# ── Left-column controls ───────────────────────────────────────────────────────

def _parse_date(raw: str, fallback: date) -> date:
    try:
        return datetime.strptime(raw.strip(), "%Y-%m-%d").date()
    except ValueError:
        return fallback


def _parse_trigger(raw: str, fallback: float = TRIGGER_DEFAULT) -> float:
    try:
        return max(1.0, min(80.0, float(raw.strip())))
    except ValueError:
        return fallback


def render_market_header(config: MarketConfig) -> None:
    flag_svg = get_flag_svg(config.key)
    st.markdown(
        f"""
<div class="market-badge-row">
  <div class="market-flag-box">{flag_svg}</div>
  <div class="market-title">{config.name}</div>
</div>
<div class="market-subtitle">{config.subtitle}</div>
""",
        unsafe_allow_html=True,
    )


def render_controls(config: MarketConfig) -> UserInput:
    ticker_labels = list(config.tickers.keys())
    default_idx = (
        ticker_labels.index(config.default_ticker_label)
        if config.default_ticker_label in ticker_labels
        else 0
    )

    today = date.today()
    default_start = today.replace(year=today.year - 5)

    col1, col2 = st.columns([78, 22])
    with col1:
        ticker_label = st.selectbox(
            "Ticker search",
            ticker_labels,
            index=default_idx,
            key=f"ticker_select_{config.key}",
        )

    with col2:
        raw_trigger = st.text_input(
            "Trigger %",
            value=str(int(TRIGGER_DEFAULT)),
            placeholder="e.g. 30",
            key=f"trigger_pct_{config.key}",
        )

    trigger_pct = _parse_trigger(raw_trigger)

    col3, col4 = st.columns(2)
    with col3:
        raw_start = st.text_input(
            "Start date  (YYYY-MM-DD)",
            value=default_start.strftime("%Y-%m-%d"),
            placeholder="e.g. 2000-01-01",
            key=f"start_date_{config.key}",
        )
    with col4:
        raw_end = st.text_input(
            "End date  (YYYY-MM-DD)",
            value=today.strftime("%Y-%m-%d"),
            placeholder="e.g. 2024-12-31",
            key=f"end_date_{config.key}",
        )

    start_date = _parse_date(raw_start, default_start)
    end_date = _parse_date(raw_end, today)

    return UserInput(
        market_key=config.key,
        ticker_label=ticker_label,
        ticker=config.tickers[ticker_label],
        trigger_pct=trigger_pct,
        start_date=start_date,
        end_date=end_date,
    )


# ── Data range info ────────────────────────────────────────────────────────────

def render_data_range_info(result: AnalysisResult, requested_start: "date") -> None:
    """Show actual data range vs requested start date in left column."""
    actual_first = result.close.index[0].date()
    actual_last  = result.close.index[-1].date()
    n_days       = len(result.close)

    lines = [
        f"<b>Available data:</b> {actual_first} → {actual_last} / {n_days:,} trading days"
    ]
    if requested_start < actual_first:
        lines.append(
            f"<span style='color:#c8883a;'>Requested start: {requested_start} / "
            f"Data starts: {actual_first}</span>"
        )

    st.markdown(
        "<div style='font-size:0.75rem;line-height:1.5;color:#6b7b5e;"
        f"margin-top:4px;'>" + "<br>".join(lines) + "</div>",
        unsafe_allow_html=True,
    )


# ── Score section ──────────────────────────────────────────────────────────────

def render_score_section(score_result: ScoreResult, result: AnalysisResult) -> None:
    rank_color = get_rank_color(score_result.rank_label)
    medal = get_rank_medal(score_result.rank_label)

    gauge_fig = score_gauge_chart(score_result.score, score_result.rank_label, rank_color)
    st.plotly_chart(gauge_fig, use_container_width=True, config=PLOTLY_CONFIG)

    cols = st.columns(4)
    cols[0].metric("Drawdown Score", f"{score_result.drawdown_score:.0f}/100")
    cols[1].metric("Yield Score",    f"{score_result.yield_score:.0f}/100")
    cols[2].metric("Momentum Score", f"{score_result.momentum_score:.0f}/100")
    cols[3].metric("Consistency",    f"{score_result.consistency_score:.0f}/100")

    trigger_status = "🔴 Triggered" if result.trigger_hit else "⚪ Not triggered"
    st.markdown(
        f"""
<div class="score-card">
  <div class="rank-badge" style="background:{rank_color}30; border: 1.5px solid {rank_color};">
    {medal} {score_result.rank_label}
  </div>
  <div style="display:flex; gap:24px; flex-wrap:wrap; margin-top:6px;">
    <div><b>Score:</b> {score_result.score} / 100</div>
    <div><b>Drawdown:</b> {fmt_pct(result.drawdown_pct)}</div>
    <div><b>Div Yield:</b> {fmt_pct(result.dividend_yield)}</div>
    <div><b>Trigger:</b> {trigger_status}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


# ── Price tab metrics helper ───────────────────────────────────────────────────

def _price_metric_html(label: str, value: str, value_class: str = "", sub_value: str = "") -> str:
    cls = f" {value_class}" if value_class else ""
    sub = f'<div class="price-metric-sub">{sub_value}</div>' if sub_value else ""
    return (
        f'<div class="price-metric">'
        f'<div class="price-metric-label">{label}</div>'
        f'<div class="price-metric-value{cls}">{value}</div>'
        f'{sub}'
        f'</div>'
    )


def _price_metrics_html(result: AnalysisResult, currency_code: str = "USD") -> str:
    ref_h_date = (
        result.zigzag_ref_high_date.strftime("%Y-%m-%d")
        if result.zigzag_ref_high_date else "-"
    )
    ref_l_date = (
        result.zigzag_ref_low_date.strftime("%Y-%m-%d")
        if result.zigzag_ref_low_date else "-"
    )
    trigger_class = "price-metric-trigger-hit" if result.zigzag_trigger_hit else "price-metric-trigger-ok"
    trigger_text = "▼ HIT" if result.zigzag_trigger_hit else "— OK"
    trigger_count = len(result.backtest_df) if result.backtest_df is not None else 0

    metrics = [
        _price_metric_html("Current Price", format_amount(result.current_price, currency_code)),
        _price_metric_html("Trigger Count", f"{trigger_count}회"),
    ]
    return '<div class="price-metric-row">' + "".join(metrics) + "</div>"


# ── Price tab ─────────────────────────────────────────────────────────────────

def render_price_tab(inp: UserInput, config: MarketConfig, result: AnalysisResult) -> None:
    currency_code = get_market_rule(config.key)["currency"]

    # Chart placeholder first; controls rendered below and fill it afterwards.
    chart_container = st.container()

    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        show_zigzag = st.checkbox(
            "Show ZigZag H/L markers",
            value=True,
            key=f"show_zigzag_{config.key}",
        )
    with col_b:
        show_buys = st.checkbox(
            "Show Trigger Buy markers",
            value=True,
            key=f"show_buys_{config.key}",
        )
    with col_c:
        show_snapshot = st.toggle(
            "Market Snapshot",
            value=False,
            key=f"show_snapshot_{config.key}",
        )

    with chart_container:
        if show_snapshot:
            # ── Show Market Snapshot in place of chart (no Annual Dividend) ───
            render_recent_data(result, inp=inp, config=config, mode="price_trigger", show_dividend=False)
        else:
            fig = price_chart(inp, config, result,
                              show_zigzag=show_zigzag, show_buys=show_buys)
            fig.update_layout(height=330)
            st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)


# ── Dividend tab ──────────────────────────────────────────────────────────────
"""
def render_dividend_tab(config: MarketConfig, result: AnalysisResult) -> None:
    fig = dividend_bar_chart(config, result)
    if fig is None:
        st.info(
            "배당 데이터가 없습니다. "
            "한국 종목/ETF는 yfinance 배당 데이터가 누락될 수 있습니다."
        )
        return
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
"""


"""
def render_dividend_tab(config: MarketConfig, result: AnalysisResult) -> None:
    currency_code = get_market_rule(config.key)["currency"]

    fig = dividend_bar_chart(config, result)
    if fig is None:
        st.info(
            "배당 데이터가 없습니다. "
            "한국 종목/ETF는 yfinance 배당 데이터가 누락될 수 있습니다."
        )
        return

    col_chart, col_table = st.columns([1.75, 1.0], gap="large")

    with col_chart:
        fig.update_layout(height=210)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    with col_table:
        st.markdown(
            '<div class="snapshot-col-label">Annual Dividend</div>',
            unsafe_allow_html=True,
        )

        if not result.annual_dividend_df.empty:
            st.markdown(
                _dividend_table_html(result.annual_dividend_df, currency_code),
                unsafe_allow_html=True,
            )
        else:
            st.info("배당 데이터 없음")
"""


def render_dividend_tab(config: MarketConfig, result: AnalysisResult, inp: UserInput = None) -> None:
    currency_code = get_market_rule(config.key)["currency"]

    fig = dividend_bar_chart(config, result, inp=inp)
    if fig is None:
        st.info(
            "배당 데이터가 없습니다. "
            "한국 종목/ETF는 yfinance 배당 데이터가 누락될 수 있습니다."
        )
        return

    # 그래프: 전체 너비로 크게
    fig.update_layout(height=210)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    # Annual Dividend table: 10년 단위 병렬 배치
    st.markdown(
        '<div class="snapshot-col-label" style="margin-top:1.1rem;">Annual Dividend</div>',
        unsafe_allow_html=True,
    )

    if result.annual_dividend_df.empty:
        st.info("배당 데이터 없음")
        return

    div_df = result.annual_dividend_df.copy()

    # Append Dividend Yield column (DPS / end-of-year close * 100) right after Dividend per Share.
    if (
        "Year" in div_df.columns
        and "Dividend per Share" in div_df.columns
        and result.price_df is not None
        and not result.price_df.empty
        and "Close" in result.price_df.columns
    ):
        close = result.price_df["Close"]
        close_idx = pd.to_datetime(close.index)
        yearly_close = close.groupby(close_idx.year).last()
        years_int = pd.to_numeric(div_df["Year"], errors="coerce").astype("Int64")
        end_close = years_int.map(lambda y: yearly_close.get(int(y)) if pd.notna(y) else None)
        dps = pd.to_numeric(div_df["Dividend per Share"], errors="coerce")
        end_close_num = pd.to_numeric(end_close, errors="coerce")
        yield_pct = (dps / end_close_num) * 100.0
        yield_pct = yield_pct.where(end_close_num.gt(0))
        insert_at = div_df.columns.get_loc("Dividend per Share") + 1
        div_df.insert(insert_at, "Dividend Yield", yield_pct.values)

    # 10년 단위 chunk
    chunk_size = 10
    chunks = [
        div_df.iloc[i:i + chunk_size]
        for i in range(0, len(div_df), chunk_size)
    ]

    cols = st.columns(min(len(chunks), 2), gap="medium")
    
    for i, chunk in enumerate(chunks):
    	with cols[i % len(cols)]:
            html = _dividend_table_html(chunk, currency_code)
            html = html.replace(
                'class="premium-table-wrap"',
                'class="premium-table-wrap" style="max-height:300px;"',
                1,
            )
            st.markdown(html, unsafe_allow_html=True)
    
    
    """
    for i, chunk in enumerate(chunks):
        with cols[i % len(cols)]:
            st.markdown(
                _dividend_table_html(chunk, currency_code),
                unsafe_allow_html=True,
            )
    """


# ── Dividend reinvest — left-column controls + summary ────────────────────────

def render_reinvest_controls_left(config: MarketConfig):
    """Render reinvest input controls in the left column.

    Returns (params_dict, summary_container) where summary_container is a
    st.container() placeholder that will be populated after analysis runs.
    """
    rule = get_market_rule(config.key)
    currency = rule["currency"]
    default_tax = float(rule["tax_rate"])

    st.markdown('<div style="height:1.4rem;"></div>', unsafe_allow_html=True)

    # When trigger-investment mode is on, the recurring amount is spent at each
    # trigger instead of monthly — reflect that in the field label.
    trigger_mode = st.session_state.get("enable_trigger_investment", False)
    recurring_label = (
        f"트리거당 투자금 ({currency})" if trigger_mode else f"월 추가 투자금 ({currency})"
    )

    col1, col2 = st.columns(2)
    with col1:
        initial_amount = st.number_input(
            f"초기 투자금 ({currency})",
            min_value=0,
            value=10000 if currency != "KRW" else 10000000,
            step=1000 if currency != "KRW" else 1000000,
            key=f"reinvest_initial_{config.key}",
        )
    with col2:
        monthly_amount = st.number_input(
            recurring_label,
            min_value=0,
            value=0,
            step=100 if currency != "KRW" else 100000,
            key=f"reinvest_monthly_{config.key}",
        )

    # 배당세율은 15.4% 고정 (입력칸 제거)
    tax_rate_pct = 15.4

    chk_col1, chk_col2 = st.columns(2)
    with chk_col1:
        reinvest_enabled = st.checkbox(
            "배당 재투자",
            value=True,
            key="enable_dividend_reinvestment",
            help="체크 시 세후 배당금을 자동 재투자합니다. 해제 시 배당금은 현금으로 누적됩니다.",
        )
    with chk_col2:
        invest_on_trigger = st.checkbox(
            "트리거 시 재투자",
            value=False,
            key="enable_trigger_investment",
            help="체크 시 '월 추가 투자금'을 매월이 아니라 트리거 발동일에만 그 금액만큼 투입합니다. "
                 "(초기 투자금은 그대로)",
        )

    summary_container = st.container()

    return {
        "initial_amount": float(initial_amount),
        "monthly_amount": float(monthly_amount),
        "tax_rate_pct": float(tax_rate_pct),
        "currency": currency,
        "reinvest_enabled": bool(reinvest_enabled),
        "invest_on_trigger": bool(invest_on_trigger),
    }, summary_container


def render_reinvest_summary_left(
    reinvest, currency: str, tax_rate_pct: float, trigger_count: int = 0
) -> None:
    """Render dark-glass metric grid in the left column placeholder."""
    if reinvest is None:
        st.caption("배당 재투자 계산 불가 — 데이터 확인")
        return

    s = reinvest.summary

    def _rm(label: str, value: str) -> str:
        return (
            f'<div class="reinvest-metric">'
            f'<div class="reinvest-metric-label">{label}</div>'
            f'<div class="reinvest-metric-value">{value}</div>'
            f'</div>'
        )

    sym = get_currency_symbol(currency)
    grid = (
    	_rm("총 외부 투자금",    f'{sym}{s["Total External Invested"]:,.0f}')
    	+ _rm("최종 평가금액",   f'{sym}{s["Final Portfolio Value"]:,.0f}')
    	+ _rm("총 수익률",       format_percent(s["Total Return %"]))
    	+ _rm("CAGR",            format_percent(s["CAGR %"]))
    	+ _rm("최종 보유수량",   f'{s["Final Shares"]:,.0f}')
    	+ _rm("누적 순배당",     f'{sym}{s["Cumulative Net Dividend"]:,.0f}')
    	+ _rm("예상 순연배당",   f'{sym}{s["Current Estimated Annual Dividend Net"]:,.0f}')
    	+ _rm("Yield on Cost",   format_percent(s["Yield on Cost Net %"]))
    	+ _rm("트리거 횟수",     f'{trigger_count}회')
    )


    """
    grid = (
        _rm("총 외부 투자금",    format_amount(s["Total External Invested"],          currency))
        + _rm("최종 평가금액",   format_amount(s["Final Portfolio Value"],            currency))
        + _rm("총 수익률",       format_percent(s["Total Return %"]))
        + _rm("CAGR",            format_percent(s["CAGR %"]))
        + _rm("최종 보유수량",   f'{s["Final Shares"]:,.0f}')
        + _rm("누적 순배당",     format_amount(s["Cumulative Net Dividend"],          currency))
        + _rm("예상 순연배당",   format_amount(s["Current Estimated Annual Dividend Net"], currency))
        + _rm("Yield on Cost",   format_percent(s["Yield on Cost Net %"]))
    )
    """

    caption = (
        f'통화: {currency} ({sym}) · 세율: {tax_rate_pct:.1f}% · '
        f'최근 연배당: {format_amount(s["Recent Annual Dividend Per Share"], currency)} · '
        f'현재 순배당률: {format_percent(s["Current Yield Net %"])}'
    )

    st.markdown(
        f'<div class="reinvest-summary-section">'
        f'<div class="reinvest-summary-title">배당 재투자 요약</div>'
        f'<div class="reinvest-metric-grid">{grid}</div>'
        f'<div class="reinvest-caption">{caption}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Invest simulation tab (price chart + reinvest timeline chart) ─────────────

def render_invest_simulation_tab(
    inp: UserInput,
    config: MarketConfig,
    result: AnalysisResult,
    reinvest=None,
    no_reinvest=None,
    reinvest_enabled: bool = False,
) -> None:
    """No-reinvest baseline chart, with reinvest curve overlaid when checkbox is on."""
    if no_reinvest is None or no_reinvest.timeline_df.empty:
        st.warning("시뮬레이션 타임라인 데이터가 없습니다.")
        return

    show_reinvest = bool(
        reinvest_enabled
        and reinvest is not None
        and not reinvest.timeline_df.empty
    )

    reinvest_df = reinvest.timeline_df if show_reinvest else None
    trigger_dates = (
        list(result.backtest_df["Buy Date"])
        if result is not None and result.backtest_df is not None
        and "Buy Date" in result.backtest_df.columns
        else []
    )
    value_fig = investment_simulation_chart(
        inp,
        config,
        no_reinvest.timeline_df,
        reinvest_df=reinvest_df,
        show_reinvest=show_reinvest,
        trigger_dates=trigger_dates,
    )
    st.plotly_chart(value_fig, use_container_width=True, config=PLOTLY_CONFIG)


# ── Invest quantity tab (yearly share count bars) ─────────────────────────────

def render_invest_quantity_tab(
    inp: UserInput,
    config: MarketConfig,
    result: AnalysisResult,
    no_reinvest=None,
    reinvest=None,
    reinvest_enabled: bool = False,
) -> None:
    """Full-size yearly share-quantity bar chart for the 투자 수량 tab."""
    if no_reinvest is None or no_reinvest.timeline_df.empty:
        st.warning("보유 수량 데이터를 계산할 수 없습니다. 초기 투자금과 가격 데이터를 확인하세요.")
        return

    show_reinvest = bool(
        reinvest_enabled
        and reinvest is not None
        and not reinvest.timeline_df.empty
    )

    fig = investment_quantity_chart(
        inp,
        config,
        no_reinvest,
        reinvest=reinvest if show_reinvest else None,
        show_reinvest=show_reinvest,
    )

    if fig is None:
        st.warning("연도별 보유 수량 데이터를 추출할 수 없습니다. (Total Shares 컬럼 누락)")
        return

    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)


# ── Annual dividend income tab (yearly net dividend bars) ─────────────────────

def render_annual_dividend_income_tab(
    inp: UserInput,
    config: MarketConfig,
    result: AnalysisResult,
    no_reinvest=None,
    reinvest=None,
    reinvest_enabled: bool = False,
) -> None:
    """Full-size yearly dividend-income bar chart for the 연배당금 tab."""
    if no_reinvest is None:
        st.warning("연배당금 데이터를 계산할 수 없습니다. 초기 투자금과 가격 데이터를 확인하세요.")
        return

    show_reinvest = bool(
        reinvest_enabled
        and reinvest is not None
        and not reinvest.timeline_df.empty
    )

    fig = annual_dividend_income_chart(
        inp,
        config,
        no_reinvest,
        reinvest=reinvest if show_reinvest else None,
        show_reinvest=show_reinvest,
    )

    if fig is None:
        st.warning(
            "연도별 배당금 데이터를 추출할 수 없습니다. "
            "(Net Dividend / Gross Dividend 등 사용 가능한 컬럼 없음)"
        )
        return

    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)


# ── Dividend reinvest tab (chart + tables only) ────────────────────────────────

def render_dividend_reinvest_tab(
    inp: UserInput, config: MarketConfig, result: AnalysisResult,
    selected=None,
) -> None:
    """Chart + table view for the reinvest tab. Inputs/summary are in left col."""
    if selected is None:
        st.info("배당 재투자 백테스트를 계산할 수 없습니다. 초기 투자금과 가격 데이터를 확인하세요.")
        return

    currency_code = get_market_rule(config.key)["currency"]

    if result.dividends.empty:
        st.warning("yfinance 배당 데이터가 비어 있습니다. 한국 ETF/일부 해외 종목은 배당 데이터가 누락될 수 있습니다.")

    if not selected.timeline_df.empty:
        st.plotly_chart(
            reinvest_timeline_chart(inp, config, selected.timeline_df),
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )
        st.plotly_chart(
            share_count_chart(config, selected.timeline_df),
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )

    if not selected.annual_df.empty:
        st.markdown('<div class="recent-title">연도별 배당 재투자 요약</div>', unsafe_allow_html=True)
        annual_view = selected.annual_df.copy()
        # Year column: format as plain integer
        if "Year" in annual_view.columns:
            annual_view["Year"] = annual_view["Year"].map(format_year)
        # Money columns: currency-aware
        for c in ["Gross Dividend", "Tax", "Net Dividend", "Cumulative Net Dividend"]:
            if c in annual_view.columns:
                annual_view[c] = annual_view[c].map(
                    lambda x: format_amount(x, currency_code) if pd.notna(x) else "-"
                )
        # Share count column: 4 decimal places (fractional shares)
        if "Shares Bought" in annual_view.columns:
            annual_view["Shares Bought"] = annual_view["Shares Bought"].map(
                lambda x: f"{x:,.4f}" if pd.notna(x) else "-"
            )
        st.dataframe(annual_view, use_container_width=True)

    if not selected.event_df.empty:
        st.markdown('<div class="recent-title">배당 재투자 이벤트 로그</div>', unsafe_allow_html=True)
        event_view = selected.event_df.tail(80).copy()
        if "Date" in event_view.columns:
            event_view["Date"] = event_view["Date"].dt.strftime("%Y-%m-%d")
        if "Original Dividend Date" in event_view.columns:
            event_view["Original Dividend Date"] = pd.to_datetime(
                event_view["Original Dividend Date"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")
        # Money columns
        for c in ["Price", "Cash Amount", "Gross Dividend", "Tax", "Net Dividend",
                  "Dividend per Share", "External Invested"]:
            if c in event_view.columns:
                event_view[c] = event_view[c].map(
                    lambda x: format_amount(x, currency_code) if pd.notna(x) else "-"
                )
        # Share count columns: 4 decimal places
        for c in ["Shares Bought", "Total Shares"]:
            if c in event_view.columns:
                event_view[c] = event_view[c].map(
                    lambda x: f"{x:,.4f}" if pd.notna(x) else "-"
                )
        st.dataframe(event_view, use_container_width=True)


# ── Market Snapshot helpers ────────────────────────────────────────────────────

def _snap_metric_html(label: str, value: str) -> str:
    return (
        f'<div class="snap-metric">'
        f'<div class="snap-metric-label">{label}</div>'
        f'<div class="snap-metric-value">{value}</div>'
        f'</div>'
    )


def _recent_data_html(price_df: pd.DataFrame, currency_code: str = "USD") -> str:
    show_cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in price_df.columns]
    view_df = price_df[show_cols].tail(40).copy()
    view_df.index = view_df.index.strftime("%Y-%m-%d")

    has_prev_close = "Close" in view_df.columns and len(view_df) > 1
    prev_closes = view_df["Close"].shift(1) if has_prev_close else None

    header_cells = "".join(f"<th>{c}</th>" for c in ["Date"] + show_cols)
    rows_html = ""
    for i, (idx, row) in enumerate(view_df.iterrows()):
        row_class = "row-alt" if i % 2 == 0 else "row-neutral"

        close_class = ""
        if has_prev_close and prev_closes is not None and i > 0:
            curr_close = float(row["Close"]) if "Close" in show_cols else 0
            prev_close = float(prev_closes.iloc[i])
            close_class = "close-up" if curr_close >= prev_close else "close-down"

        cells = f"<td>{idx}</td>"
        for col in show_cols:
            val = row[col]
            if col == "Volume":
                cell_val = f"{int(val):,}" if pd.notna(val) else "-"
                cells += f'<td class="vol-cell">{cell_val}</td>'
            elif col == "Close" and close_class:
                cell_val = format_amount(val, currency_code) if pd.notna(val) else "-"
                cells += f'<td class="{close_class}">{cell_val}</td>'
            else:
                cell_val = format_amount(val, currency_code) if pd.notna(val) else "-"
                cells += f"<td>{cell_val}</td>"
        rows_html += f'<tr class="{row_class}">{cells}</tr>'

    return (
        f'<div class="premium-table-wrap">'
        f'<table class="premium-table">'
        f'<thead><tr>{header_cells}</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table></div>'
    )


def _dividend_table_html(div_df: pd.DataFrame, currency_code: str = "USD") -> str:
    if div_df.empty:
        return ""
    cols = list(div_df.columns)
    header_cells = "".join(f"<th>{c}</th>" for c in cols)

    year_col = "Year" if "Year" in cols else None
    div_col  = "Dividend per Share" if "Dividend per Share" in cols else None

    # Resolve year strings for badge detection (use format_year for robustness)
    latest_year  = format_year(div_df[year_col].iloc[-1])  if year_col else None
    if div_col and not div_df[div_col].empty:
        highest_year = format_year(div_df.loc[div_df[div_col].idxmax(), year_col]) if year_col else None
        lowest_year  = format_year(div_df.loc[div_df[div_col].idxmin(), year_col]) if year_col else None
    else:
        highest_year = lowest_year = None

    rows_html = ""
    for i, (_, row) in enumerate(div_df.iterrows()):
        row_class = "div-row-even" if i % 2 == 0 else "div-row-odd"
        cells = ""
        for col in cols:
            val = row[col]
            if col == year_col:
                yr_str = format_year(val)
                badge = ""
                if yr_str == highest_year:
                    badge = ' <span class="div-badge badge-div-highest">H</span>'
                elif yr_str == lowest_year:
                    badge = ' <span class="div-badge badge-div-lowest">L</span>'
                cells += f"<td>{yr_str}{badge}</td>"
            elif col == div_col:
                cells += f"<td>{format_amount(val, currency_code)}</td>"
            elif col == "Dividend Yield":
                if pd.notna(val):
                    try:
                        cells += f"<td>{float(val):.2f}%</td>"
                    except (TypeError, ValueError):
                        cells += "<td>-</td>"
                else:
                    cells += "<td>-</td>"
            else:
                # Any other numeric columns: plain format
                try:
                    cells += f"<td>{float(val):,.4f}</td>"
                except (TypeError, ValueError):
                    cells += f"<td>{val}</td>"
        rows_html += f'<tr class="{row_class}">{cells}</tr>'

    return (
        f'<div class="premium-table-wrap">'
        f'<table class="premium-table">'
        f'<thead><tr>{header_cells}</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table></div>'
    )


def _zigzag_events_html(result: AnalysisResult, trigger_pct: float, currency_code: str = "USD") -> str:
    """Build ZigZag High / Low + Trigger Buy + Current events table from golden engine output."""
    highs, lows = result.zigzag_points if isinstance(result.zigzag_points, tuple) else ([], [])

    badge_map = {
        "High":        "badge-high",
        "Low":         "badge-low",
        "Trigger Buy": "badge-buy",
        "Current":     "badge-current",
    }

    rows: list[dict] = []

    for ts, price in highs:
        rows.append(dict(
            type="High", date=pd.Timestamp(ts), price=float(price),
            ref_high=None, ref_low=None, drawdown=None, note="",
        ))

    for ts, price in lows:
        rows.append(dict(
            type="Low", date=pd.Timestamp(ts), price=float(price),
            ref_high=None, ref_low=None, drawdown=None, note="",
        ))

    if result.backtest_df is not None and not result.backtest_df.empty:
        for _, brow in result.backtest_df.iterrows():
            rows.append(dict(
                type="Trigger Buy",
                date=pd.Timestamp(brow["Buy Date"]),
                price=float(brow["Buy Price"]),
                ref_high=None, ref_low=None,
                drawdown=f"−{trigger_pct:.0f}%",
                note="자동 매수",
            ))

    rows.append(dict(
        type="Current",
        date=pd.Timestamp(result.current_date),
        price=result.current_price,
        ref_high=result.zigzag_ref_high_price,
        ref_low=result.zigzag_ref_low_price if result.zigzag_ref_low_price else None,
        drawdown=result.zigzag_drawdown_pct,
        note="현재 상태",
    ))

    rows.sort(key=lambda r: r["date"])

    def _fmt(v) -> str:
        if v is None: return "<span style='color:#6c745e'>—</span>"
        if isinstance(v, (int, float)): return format_amount(v, currency_code)
        return str(v)

    def _fmt_dd(v) -> str:
        if v is None: return "<span style='color:#6c745e'>—</span>"
        if isinstance(v, float):
            cls = "close-up" if v > 0 else ("close-down" if v < 0 else "")
            return f'<span class="{cls}">{format_percent(v)}</span>'
        return str(v)

    headers = ["Type", "Date", "Price", "Ref High", "Ref Low", "Drawdown", "Note"]
    header_cells = "".join(f"<th>{h}</th>" for h in headers)

    rows_html = ""
    for i, row in enumerate(rows):
        bc = badge_map.get(row["type"], "badge-current")
        type_cell = f'<span class="type-badge {bc}">{row["type"]}</span>'
        date_str  = row["date"].strftime("%Y-%m-%d")
        alt = "row-alt" if i % 2 == 0 else "row-neutral"
        cells = (
            f"<td>{type_cell}</td>"
            f"<td style='text-align:left;color:#6c745e;'>{date_str}</td>"
            f"<td>{_fmt(row['price'])}</td>"
            f"<td>{_fmt(row['ref_high'])}</td>"
            f"<td>{_fmt(row['ref_low'])}</td>"
            f"<td>{_fmt_dd(row['drawdown'])}</td>"
            f"<td style='color:#6c745e; font-size:11px'>{row['note']}</td>"
        )
        rows_html += f'<tr class="{alt}">{cells}</tr>'

    return (
        f'<div class="premium-table-wrap" style="max-height:500px">'
        f'<table class="premium-table">'
        f'<thead><tr>{header_cells}</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table></div>'
    )


# ── Market Snapshot (recent data + dividend) ───────────────────────────────────

def _render_dividend_col(result: AnalysisResult, currency_code: str = "USD") -> None:
    """Render annual dividend summary + table (shared by both snapshot modes)."""
    st.markdown(
        '<div class="snapshot-col-label">Annual Dividend</div>',
        unsafe_allow_html=True,
    )
    if not result.annual_dividend_df.empty:
        div_col    = "Dividend per Share"
        div_series = result.annual_dividend_df[div_col] if div_col in result.annual_dividend_df.columns else pd.Series(dtype=float)

        years_tracked = len(result.annual_dividend_df)
        latest_div    = format_amount(div_series.iloc[-1], currency_code) if not div_series.empty else "-"
        avg_div       = format_amount(div_series.mean(),   currency_code) if not div_series.empty else "-"

        if len(div_series) >= 2 and float(div_series.iloc[-2]) != 0:
            growth_val  = (float(div_series.iloc[-1]) / float(div_series.iloc[-2]) - 1) * 100
            growth_cls  = "div-positive" if growth_val >= 0 else "div-negative"
            growth_str  = f'<span class="{growth_cls}">{growth_val:+.1f}%</span>'
        else:
            growth_str  = "-"

        st.markdown(
            '<div class="snap-metrics-row">'
            + _snap_metric_html("Years", str(years_tracked))
            + _snap_metric_html("Latest", latest_div)
            + _snap_metric_html("Avg", avg_div)
            + f'<div class="snap-metric"><div class="snap-metric-label">Growth</div>'
              f'<div class="snap-metric-value">{growth_str}</div></div>'
            + "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(_dividend_table_html(result.annual_dividend_df, currency_code), unsafe_allow_html=True)
    else:
        st.info("배당 데이터 없음")


# ── Recent data table ─────────────────────────────────────────────────────────

def render_recent_data(
    result: AnalysisResult,
    inp: Optional[UserInput] = None,
    config: Optional[MarketConfig] = None,
    mode: str = "default",
    show_dividend: bool = True,
) -> None:
    currency_code = get_market_rule(config.key)["currency"] if config is not None else "USD"

    st.markdown('<div class="snapshot-section">', unsafe_allow_html=True)
    st.markdown('<div class="snapshot-header">Market Snapshot</div>', unsafe_allow_html=True)
    st.markdown('<div class="snapshot-divider"></div>', unsafe_allow_html=True)

    if mode == "price_trigger" and inp is not None:
        if show_dividend:
            # ── price_trigger mode: ZigZag events (left) + dividend (right) ──
            col_main, col_div = st.columns([2, 1])
            with col_main:
                st.markdown(
                    '<div class="snapshot-col-label">ZigZag High / Low &amp; Trigger Events</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(_zigzag_events_html(result, inp.trigger_pct, currency_code), unsafe_allow_html=True)
            with col_div:
                _render_dividend_col(result, currency_code)
        else:
            # ── price tab snapshot: ZigZag events only (full width) ───────────
            st.markdown(
                '<div class="snapshot-col-label">ZigZag High / Low &amp; Trigger Events</div>',
                unsafe_allow_html=True,
            )
            st.markdown(_zigzag_events_html(result, inp.trigger_pct, currency_code), unsafe_allow_html=True)

        # Collapsed OHLCV below
        with st.expander("Raw Recent OHLCV Data", expanded=False):
            st.markdown(_recent_data_html(result.price_df, currency_code), unsafe_allow_html=True)

    else:
        # ── default mode: 52W metrics + collapsed OHLCV (left) + dividend (right) ──
        close_s = result.price_df["Close"] if "Close" in result.price_df.columns else pd.Series(dtype=float)
        high_s  = result.price_df["High"]  if "High"  in result.price_df.columns else pd.Series(dtype=float)
        low_s   = result.price_df["Low"]   if "Low"   in result.price_df.columns else pd.Series(dtype=float)
        vol_s   = result.price_df["Volume"] if "Volume" in result.price_df.columns else pd.Series(dtype=float)

        latest_close = format_amount(close_s.iloc[-1], currency_code) if not close_s.empty else "-"
        latest_vol   = f"{int(vol_s.iloc[-1]):,}"                     if not vol_s.empty  else "-"
        w52_high     = format_amount(high_s.tail(252).max(), currency_code) if not high_s.empty else "-"
        w52_low      = format_amount(low_s.tail(252).min(),  currency_code) if not low_s.empty  else "-"

        col_price, col_div = st.columns([2, 1])

        with col_price:
            st.markdown(
                '<div class="snapshot-col-label">Price Summary</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="snap-metrics-row">'
                + _snap_metric_html("Latest Close", latest_close)
                + _snap_metric_html("Latest Volume", latest_vol)
                + _snap_metric_html("52W High", w52_high)
                + _snap_metric_html("52W Low", w52_low)
                + "</div>",
                unsafe_allow_html=True,
            )
            with st.expander("Raw Recent OHLCV Data", expanded=False):
                st.markdown(_recent_data_html(result.price_df, currency_code), unsafe_allow_html=True)

        with col_div:
            _render_dividend_col(result, currency_code)

    st.markdown("</div>", unsafe_allow_html=True)


# ── Cross-market ranking ──────────────────────────────────────────────────────

def render_market_ranking() -> None:
    """Cached lightweight ranking of each market's default ticker."""
    st.markdown('<div class="recent-title">Global Cup Ranking</div>', unsafe_allow_html=True)
    st.caption("Default ticker per market — cached. Scores update each hour.")

    from datetime import date as _date, timedelta as _td
    today = _date.today()
    start = today.replace(year=today.year - 5)

    ranking_rows = []
    for mkey, mconfig in MARKETS.items():
        default_label = mconfig.default_ticker_label
        default_ticker = mconfig.tickers.get(default_label)
        if not default_ticker:
            continue
        inp = UserInput(
            market_key=mkey,
            ticker_label=default_label,
            ticker=default_ticker,
            trigger_pct=TRIGGER_DEFAULT,
            start_date=start,
            end_date=today,
        )
        result = run_analysis(inp)
        if result is None:
            continue
        years = max(1.0, (result.close.index[-1] - result.close.index[0]).days / 365.25)
        sc = calculate_score(
            drawdown_pct=result.drawdown_pct,
            dividend_yield=result.dividend_yield,
            close=result.close,
            annual_dividend_df=result.annual_dividend_df,
            years_in_period=years,
        )
        ranking_rows.append((mkey, mconfig, sc, result))

    ranking_rows.sort(key=lambda r: r[2].score, reverse=True)

    for pos, (mkey, mconfig, sc, result) in enumerate(ranking_rows, start=1):
        rank_color = get_rank_color(sc.rank_label)
        medal = get_rank_medal(sc.rank_label)
        flag_class = get_flag_class(mconfig)
        trigger_icon = "🔴" if result.trigger_hit else "⚪"
        st.markdown(
            f"""
<div class="ranking-row">
  <div class="ranking-pos">{pos}</div>
  <div class="drawn-flag {flag_class}" style="flex-shrink:0;"></div>
  <div class="ranking-market">
    <b>{mconfig.name}</b><br>
    <span style="font-size:12px;color:rgba(255,245,220,.62);">{mconfig.default_ticker_label}</span>
  </div>
  <div style="text-align:right;">
    <div class="ranking-score" style="color:{rank_color};">{sc.score}</div>
    <div style="font-size:11px;color:rgba(255,245,220,.55);">{medal} {sc.rank_label}</div>
  </div>
  <div style="text-align:right; min-width:90px;">
    <div style="font-size:13px; color:rgba(255,245,220,.8);">{fmt_pct(result.drawdown_pct)}</div>
    <div style="font-size:11px; color:rgba(255,245,220,.55);">drawdown</div>
  </div>
  <div style="text-align:right; min-width:80px;">
    <div style="font-size:13px; color:rgba(255,245,220,.8);">{fmt_pct(result.dividend_yield)}</div>
    <div style="font-size:11px; color:rgba(255,245,220,.55);">div yield</div>
  </div>
  <div style="font-size:18px;">{trigger_icon}</div>
</div>
""",
            unsafe_allow_html=True,
        )


# ── 전고점 대비 낙폭 스캐너 ──────────────────────────────────────────────────────

def _drawdown_table_html(df: pd.DataFrame, currency_code: str = "USD") -> str:
    """Render a scanner result subset as a styled premium table.

    Columns: 종목 · 전고점 날짜 · 전고점 가격 · 현재 가격 · 낙폭%
    """
    if df is None or df.empty:
        return ""

    header_cells = "".join(
        f"<th>{c}</th>"
        for c in ["종목", "전고점 날짜", "전고점 가격", "현재 가격", "낙폭%"]
    )

    rows_html = ""
    for i, (_, row) in enumerate(df.iterrows()):
        row_class = "row-alt" if i % 2 == 0 else "row-neutral"

        high_date = pd.Timestamp(row["high_date"]).strftime("%Y-%m-%d") \
            if pd.notna(row["high_date"]) else "-"
        high_price    = format_amount(row["high_price"], currency_code)
        current_price = format_amount(row["current_price"], currency_code)
        dd = float(row["drawdown_pct"])

        rows_html += (
            f'<tr class="{row_class}">'
            f'<td style="text-align:left;">{row["label"]}</td>'
            f'<td>{high_date}</td>'
            f'<td>{high_price}</td>'
            f'<td>{current_price}</td>'
            f'<td class="close-down"><b>{dd:.2f}%</b></td>'
            f'</tr>'
        )

    return (
        f'<div class="premium-table-wrap">'
        f'<table class="premium-table">'
        f'<thead><tr>{header_cells}</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table></div>'
    )


def render_high_drawdown_tab(config: MarketConfig, inp: UserInput) -> None:
    """Scan every ticker in the selected market and list those down 20/30/50%
    from their most recent prior high (직전 전고점)."""
    currency_code = get_market_rule(config.key)["currency"]
    tickers = config.tickers or {}
    total_n = len(tickers)

    st.markdown(
        '<div class="recent-title">전고점 대비 낙폭 스캐너</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        f"{config.name} 종목 {total_n}개를 직전 전고점 대비 현재 낙폭 기준으로 스캔합니다.  "
        f"(기간: {inp.start_date} ~ {inp.end_date})"
    )

    # Cache results in session_state keyed by MARKET ONLY, so a scan survives
    # reruns triggered by unrelated controls — changing the ticker or the date
    # inputs never clears the table. We also stash the date range that was
    # actually scanned so we can flag when the current inputs have drifted.
    state_key = f"hd_scan::{config.key}"

    if total_n == 0:
        st.warning("이 마켓에 스캔할 종목이 없습니다.")
        return

    if st.button(f"🔍 전체 종목 스캔 ({total_n}개)", key=f"hd_btn::{config.key}"):
        progress = st.progress(0.0)
        status = st.empty()

        def _cb(done: int, total: int, label: str) -> None:
            progress.progress(done / total if total else 1.0)
            status.markdown(f"스캔 중… **{done}/{total}**  ·  {label}")

        df = scan_market(
            tickers, inp.start_date, inp.end_date,
            threshold=SCAN_THRESHOLD, progress_cb=_cb,
        )
        progress.empty()
        status.empty()
        st.session_state[state_key] = {
            "df": df,
            "start": inp.start_date,
            "end": inp.end_date,
        }

    cached = st.session_state.get(state_key)
    if cached is None:
        st.info("‘전체 종목 스캔’ 버튼을 눌러 분석을 시작하세요. (종목 수에 따라 수십 초 걸릴 수 있어요.)")
        return

    df = cached["df"]
    scanned_start, scanned_end = cached["start"], cached["end"]

    # If the current date inputs no longer match what was scanned, keep showing
    # the previous results (don't reset) and offer a re-scan hint.
    if (scanned_start, scanned_end) != (inp.start_date, inp.end_date):
        st.caption(
            f"⚠️ 현재 표는 {scanned_start} ~ {scanned_end} 기준 스캔 결과입니다. "
            f"현재 선택한 기간({inp.start_date} ~ {inp.end_date})으로 갱신하려면 다시 스캔하세요."
        )

    if df.empty:
        st.warning("데이터를 불러온 종목이 없습니다. 기간이나 티커를 확인하세요.")
        return

    buckets = [
        ("20% 이상 하락", 20.0),
        ("30% 이상 하락", 30.0),
        ("50% 이상 하락", 50.0),
    ]
    for title, min_drop in buckets:
        sub = filter_by_min_drop(df, min_drop)
        st.markdown(
            f'<div class="snapshot-col-label" style="margin-top:1.2rem;">'
            f'{title} <span style="opacity:.55;">({len(sub)}종목)</span></div>',
            unsafe_allow_html=True,
        )
        if sub.empty:
            st.caption("해당 구간 종목 없음")
            continue
        st.markdown(_drawdown_table_html(sub, currency_code), unsafe_allow_html=True)

    st.caption(
        f"스캔 완료: {len(df)}/{total_n}개 종목 데이터 확보 · "
        f"직전 전고점 판정 ZigZag 임계 {SCAN_THRESHOLD*100:.0f}%"
    )
