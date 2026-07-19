from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional

import pandas as pd


@dataclass
class MarketConfig:
    key: str
    code: str
    name: str
    flag: str
    badge_code: str
    subtitle: str
    tickers: Dict[str, str]
    chart1: str
    chart2: str
    line: str
    bg_label: str
    default_ticker_label: str


@dataclass
class UserInput:
    market_key: str
    ticker_label: str
    ticker: str
    trigger_pct: float
    start_date: date
    end_date: date


@dataclass
class AnalysisResult:
    # ── Core price fields (computed from close.max — backward-compat) ──────────
    current_date: pd.Timestamp
    current_price: float
    high_date: pd.Timestamp
    high_price: float
    drawdown_pct: float
    trigger_price: float
    trigger_hit: bool
    ttm_dividend: float
    dividend_yield: float
    latest_dividend_year: str
    latest_annual_dividend: float
    annual_dividend_df: pd.DataFrame
    price_df: pd.DataFrame
    close: pd.Series
    dividends: pd.Series
    # ── Golden engine fields (populated by golden_engine functions) ───────────
    zigzag_points: tuple = field(default_factory=lambda: ([], []))
    zigzag_ref_high_price: float = 0.0
    zigzag_ref_high_date: Optional[pd.Timestamp] = None
    zigzag_ref_low_price: float = 0.0
    zigzag_ref_low_date: Optional[pd.Timestamp] = None
    zigzag_drawdown_pct: float = 0.0
    zigzag_trigger_price: float = 0.0
    zigzag_trigger_hit: bool = False
    drop_bucket: str = ""
    status_label: str = ""
    high_count: int = 0
    low_count: int = 0
    # ── Trigger backtest (populated by run_backtest) ───────────────────────────
    backtest_df: Optional[pd.DataFrame] = None


@dataclass
class DividendReinvestResult:
    summary: Dict[str, float]
    event_df: pd.DataFrame
    timeline_df: pd.DataFrame
    annual_df: pd.DataFrame


# ── Flag CSS class helper ──────────────────────────────────────────────────────

def get_flag_class(config: MarketConfig) -> str:
    mapping = {
        "Korea": "flag-kr",
        "United States": "flag-us",
        "European Union": "flag-eu",
        "Japan": "flag-jp",
    }
    return mapping.get(config.key, "flag-glb")


# ── Accurate inline-SVG flags ─────────────────────────────────────────────────
# Drawn to official specs so they render identically on every platform.

import math as _math

_SVG_ATTRS = (
    'xmlns="http://www.w3.org/2000/svg" '
    'style="width:40px;height:auto;display:block;border-radius:5px;'
    'box-shadow:inset 0 0 0 1px rgba(0,0,0,.12);"'
)


def _star_points(cx: float, cy: float, r_out: float, r_in: float, rot: float = -90.0) -> str:
    """Return polygon points for a 5-point star centred at (cx, cy)."""
    pts = []
    for k in range(5):
        a_out = _math.radians(rot + k * 72)
        a_in = _math.radians(rot + 36 + k * 72)
        pts.append((cx + r_out * _math.cos(a_out), cy + r_out * _math.sin(a_out)))
        pts.append((cx + r_in * _math.cos(a_in), cy + r_in * _math.sin(a_in)))
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def _flag_svg_jp() -> str:
    # 2:3 field, white; red disc (Hinomaru) diameter = 3/5 of height, centred.
    return (
        f'<svg viewBox="0 0 60 40" {_SVG_ATTRS}>'
        '<rect width="60" height="40" fill="#fff"/>'
        '<circle cx="30" cy="20" r="12" fill="#BC002D"/></svg>'
    )


def _flag_svg_us() -> str:
    # 10:19 field, 13 stripes (7 red), blue union over top 7 stripes, 50 white stars.
    sh = 100 / 13  # stripe height
    stripes = "".join(
        f'<rect y="{i * sh:.3f}" width="190" height="{sh:.3f}" fill="#B22234"/>'
        for i in range(0, 13, 2)
    )
    union_h = 7 * sh
    stars = ""
    for row in range(9):
        y = 3.4 + row * (union_h - 6.8) / 8
        n, x0 = (6, 6) if row % 2 == 0 else (5, 12)
        for c in range(n):
            stars += f'<circle cx="{x0 + c * 12:.1f}" cy="{y:.2f}" r="2" fill="#fff"/>'
    return (
        f'<svg viewBox="0 0 190 100" {_SVG_ATTRS}>'
        '<rect width="190" height="100" fill="#fff"/>'
        f'{stripes}'
        f'<rect width="76" height="{union_h:.2f}" fill="#3C3B6E"/>'
        f'{stars}</svg>'
    )


def _flag_svg_eu() -> str:
    # 2:3 blue field; 12 gold five-point stars evenly on a centred circle.
    cx, cy, ring = 45, 30, 20
    stars = ""
    for i in range(12):
        a = _math.radians(i * 30)
        sx = cx + ring * _math.sin(a)
        sy = cy - ring * _math.cos(a)
        stars += f'<polygon points="{_star_points(sx, sy, 4.2, 1.7)}" fill="#FFCC00"/>'
    return (
        f'<svg viewBox="0 0 90 60" {_SVG_ATTRS}>'
        '<rect width="90" height="60" fill="#003399"/>'
        f'{stars}</svg>'
    )


def _kr_trigram(pattern) -> str:
    """3 stacked bars; pattern = list of 3 (True=solid, False=broken), top→bottom."""
    bars = ""
    for j, solid in enumerate(pattern):
        y = -3.6 + j * 3.6 - 0.9
        if solid:
            bars += f'<rect x="-6.5" y="{y:.2f}" width="13" height="1.8"/>'
        else:
            bars += (
                f'<rect x="-6.5" y="{y:.2f}" width="5.2" height="1.8"/>'
                f'<rect x="1.3" y="{y:.2f}" width="5.2" height="1.8"/>'
            )
    return bars


def _flag_svg_kr() -> str:
    # 2:3 white field; taegeuk (red top / blue bottom); 4 trigrams per official spec:
    #   TL Geon ☰ | TR Ri ☲ | BL Gam ☵ | BR Gon ☷
    cx, cy, R = 45.0, 30.0, 15.0
    taegeuk = (
        f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#0047A0"/>'
        f'<path d="M{cx},{cy - R} a{R},{R} 0 0,1 0,{2 * R} '
        f'a{R / 2},{R / 2} 0 0,1 0,{-R} a{R / 2},{R / 2} 0 0,0 0,{-R} z" '
        f'fill="#CD2E3A" transform="rotate(-90 {cx} {cy})"/>'
    )
    S, B = True, False
    corners = [
        (17.1, 11.4, 123.69, [S, S, S]),  # top-left     Geon ☰
        (72.9, 11.4, 56.31, [S, B, S]),   # top-right    Ri   ☲
        (17.1, 48.6, 56.31, [B, S, B]),   # bottom-left  Gam  ☵
        (72.9, 48.6, 123.69, [B, B, B]),  # bottom-right Gon  ☷
    ]
    tg = "".join(
        f'<g transform="translate({x},{y}) rotate({rot})" fill="#000">{_kr_trigram(pat)}</g>'
        for x, y, rot, pat in corners
    )
    return (
        f'<svg viewBox="0 0 90 60" {_SVG_ATTRS}>'
        '<rect width="90" height="60" fill="#fff"/>'
        f'{taegeuk}{tg}</svg>'
    )


def _flag_svg_globe() -> str:
    # Simple stylised globe for the "Global" market.
    return (
        f'<svg viewBox="0 0 60 60" {_SVG_ATTRS.replace("height:auto", "height:40px")}>'
        '<circle cx="30" cy="30" r="28" fill="#1d6fd6"/>'
        '<path d="M12 22 q8 -6 16 -2 q6 3 4 9 q-3 5 -10 3 q-8 -2 -10 -10z" fill="#3ca55c"/>'
        '<path d="M34 34 q7 -3 12 2 q3 5 -3 9 q-8 3 -11 -4 q-2 -5 2 -7z" fill="#3ca55c"/>'
        '<g fill="none" stroke="rgba(255,255,255,.5)" stroke-width="1">'
        '<circle cx="30" cy="30" r="28"/>'
        '<ellipse cx="30" cy="30" rx="12" ry="28"/>'
        '<line x1="2" y1="30" x2="58" y2="30"/></g></svg>'
    )


def get_flag_svg(market_key: str) -> str:
    """Return an accurate inline-SVG flag for the given market key."""
    builders = {
        "Japan": _flag_svg_jp,
        "United States": _flag_svg_us,
        "European Union": _flag_svg_eu,
        "Korea": _flag_svg_kr,
    }
    return builders.get(market_key, _flag_svg_globe)()


# ── Base ticker dictionaries (fallback when CSV files are absent) ──────────────

_US_TICKERS_BASE: Dict[str, str] = {
    "VOO / Vanguard S&P 500 ETF": "VOO",
    "QQQ / Nasdaq 100 ETF": "QQQ",
    "SCHD / Dividend ETF": "SCHD",
    "JEPI / Equity Premium Income": "JEPI",
    "JEPQ / Nasdaq Premium Income": "JEPQ",
    "AAPL / Apple": "AAPL",
    "MSFT / Microsoft": "MSFT",
    "NVDA / NVIDIA": "NVDA",
    "KO / Coca-Cola": "KO",
}

_KOREA_TICKERS_BASE: Dict[str, str] = {
    "KODEX 200 / 069500.KS": "069500.KS",
    "TIGER 200 / 102110.KS": "102110.KS",
    "TIGER 미국S&P500 / 360750.KS": "360750.KS",
    "TIGER 미국나스닥100 / 133690.KS": "133690.KS",
    "TIGER 미국배당다우존스 / 458730.KS": "458730.KS",
    "삼성전자 / 005930.KS": "005930.KS",
    "SK하이닉스 / 000660.KS": "000660.KS",
    "현대차 / 005380.KS": "005380.KS",
    "NAVER / 035420.KS": "035420.KS",
}

_EU_TICKERS_BASE: Dict[str, str] = {
    "VGK / Vanguard FTSE Europe ETF": "VGK",
    "IEUR / iShares Core MSCI Europe ETF": "IEUR",
    "FEZ / Euro STOXX 50 ETF": "FEZ",
    "SAP / SAP": "SAP",
    "ASML / ASML": "ASML",
    "SIE.DE / Siemens": "SIE.DE",
    "ALV.DE / Allianz": "ALV.DE",
}

_JAPAN_TICKERS_BASE: Dict[str, str] = {
    "EWJ / iShares MSCI Japan ETF": "EWJ",
    "DXJ / WisdomTree Japan Hedged": "DXJ",
    "7203.T / Toyota": "7203.T",
    "6758.T / Sony": "6758.T",
    "7974.T / Nintendo": "7974.T",
    "9984.T / SoftBank Group": "9984.T",
}

_GLOBAL_TICKERS_BASE: Dict[str, str] = {
    "VT / Vanguard Total World ETF": "VT",
    "ACWI / iShares MSCI ACWI ETF": "ACWI",
    "URTH / MSCI World ETF": "URTH",
    "VXUS / Total International Stock": "VXUS",
    "VWO / Emerging Markets ETF": "VWO",
}


# ── Market registry ────────────────────────────────────────────────────────────

MARKETS: Dict[str, MarketConfig] = {
    "ETF": MarketConfig(
        key="ETF",
        code="ETF",
        name="ETF",
        flag="📊",
        badge_code="ETF",
        subtitle="글로벌 ETF의 배당, 전고점 대비 하락률, 트리거 신호를 확인합니다.",
        tickers={},  # populated from all-country ETFs by build_ticker_dict at startup
        chart1="#7a5cff",
        chart2="#2574d9",
        line="#7a5cff",
        bg_label="ETF DASHBOARD",
        default_ticker_label="Invesco QQQ Trust / QQQ",
    ),
    "Korea": MarketConfig(
        key="Korea",
        code="KOR",
        name="Korea Market",
        flag="🇰🇷",
        badge_code="KR",
        subtitle="한국 주식/ETF의 배당, 전고점 대비 하락률, 트리거 신호를 확인합니다.",
        tickers=dict(_KOREA_TICKERS_BASE),
        chart1="#f04b4b",
        chart2="#2453d6",
        line="#e93434",
        bg_label="KOREA DASHBOARD",
        default_ticker_label="TIGER 미국S&P500 / 360750.KS",
    ),
    "United States": MarketConfig(
        key="United States",
        code="USA",
        name="United States",
        flag="🇺🇸",
        badge_code="US",
        subtitle="미국 주식/ETF의 배당, 전고점 대비 하락률, 트리거 신호를 확인합니다.",
        tickers=dict(_US_TICKERS_BASE),
        chart1="#2453d6",
        chart2="#e23636",
        line="#2453d6",
        bg_label="US DASHBOARD",
        default_ticker_label="Invesco QQQ Trust / QQQ",
    ),
    "European Union": MarketConfig(
        key="European Union",
        code="EU",
        name="European Union",
        flag="🇪🇺",
        badge_code="EU",
        subtitle="유럽 ETF/대표 종목의 배당, 전고점 대비 하락률, 트리거 신호를 확인합니다.",
        tickers=dict(_EU_TICKERS_BASE),
        chart1="#214fd8",
        chart2="#ffd84a",
        line="#ffd84a",
        bg_label="EU DASHBOARD",
        default_ticker_label="VGK / Vanguard FTSE Europe ETF",
    ),
    "Japan": MarketConfig(
        key="Japan",
        code="JPN",
        name="Japan Market",
        flag="🇯🇵",
        badge_code="JP",
        subtitle="일본 ETF/대표 종목의 배당, 전고점 대비 하락률, 트리거 신호를 확인합니다.",
        tickers=dict(_JAPAN_TICKERS_BASE),
        chart1="#d92545",
        chart2="#ff9aac",
        line="#d92545",
        bg_label="JAPAN DASHBOARD",
        default_ticker_label="EWJ / iShares MSCI Japan ETF",
    ),
    "Global": MarketConfig(
        key="Global",
        code="GLB",
        name="Global Market",
        flag="🌍",
        badge_code="GLB",
        subtitle="글로벌 ETF의 배당, 전고점 대비 하락률, 트리거 신호를 확인합니다.",
        tickers=dict(_GLOBAL_TICKERS_BASE),
        chart1="#35b66d",
        chart2="#2574d9",
        line="#35b66d",
        bg_label="GLOBAL DASHBOARD",
        default_ticker_label="VT / Vanguard Total World ETF",
    ),
}
