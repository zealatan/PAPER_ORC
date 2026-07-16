from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from .market_config import AnalysisResult, MarketConfig, UserInput
from .analysis import fmt_money
from .config import get_market_rule
from .formatting import get_currency_symbol
from .golden_engine import add_high_low_markers as _golden_add_hl_markers

CHART_HEIGHT_PRICE = 360
CHART_HEIGHT_REINVEST = 380

_LAYOUT_BASE = dict(
    height=CHART_HEIGHT_PRICE,
    paper_bgcolor="rgba(255,249,237,1)",
    plot_bgcolor="rgba(255,253,244,1)",
    font=dict(color="#1f2b18", size=10),
    margin=dict(l=36, r=26, t=48, b=38),
)

_AXIS = dict(showgrid=True, gridcolor="rgba(31,43,24,.08)")


# ── ZigZag marker helpers ──────────────────────────────────────────────────────

def add_high_low_markers(
    fig: go.Figure,
    zigzag_points: list,
    show_labels: bool = True,
) -> go.Figure:
    """
    Add alternating ZigZag H (triangle-up) and L (triangle-down) markers to fig.

    zigzag_points: list of ZigZagPoint objects from find_alternating_high_low().
    show_labels: if True, annotate each marker with 'H' or 'L'.
    """
    highs = [p for p in zigzag_points if p.point_type == "H"]
    lows  = [p for p in zigzag_points if p.point_type == "L"]

    if highs:
        fig.add_trace(go.Scatter(
            x=[p.date  for p in highs],
            y=[p.price for p in highs],
            mode="markers+text" if show_labels else "markers",
            name="ZigZag High",
            marker=dict(size=7, color="#ca6702", symbol="triangle-up"),
            text=["H"] * len(highs) if show_labels else None,
            textposition="top center",
            textfont=dict(size=8),
            hovertemplate="H: %{y:.2f}<br>%{x}<extra></extra>",
        ))

    if lows:
        fig.add_trace(go.Scatter(
            x=[p.date  for p in lows],
            y=[p.price for p in lows],
            mode="markers+text" if show_labels else "markers",
            name="ZigZag Low",
            marker=dict(size=7, color="#2453d6", symbol="triangle-down"),
            text=["L"] * len(lows) if show_labels else None,
            textposition="bottom center",
            textfont=dict(size=8),
            hovertemplate="L: %{y:.2f}<br>%{x}<extra></extra>",
        ))

    return fig


def add_trigger_buy_markers(
    fig: go.Figure,
    backtest_df: pd.DataFrame,
) -> go.Figure:
    """
    Add Buy markers at each trigger event found by run_backtest().
    backtest_df: output of run_backtest() — may be None or empty.
    """
    if backtest_df is None or backtest_df.empty:
        return fig

    fig.add_trace(go.Scatter(
        x=backtest_df["Buy Date"],
        y=backtest_df["Buy Price"],
        mode="markers+text",
        name="Trigger Buy",
        marker=dict(size=8, color="#22c55e", symbol="star"),
        text=["Buy"] * len(backtest_df),
        textposition="top center",
        textfont=dict(size=8),
        hovertemplate=(
            "Buy: %{y:.2f}<br>%{x}"
            "<extra></extra>"
        ),
    ))
    return fig


# ── Primary price chart ────────────────────────────────────────────────────────

def price_chart(
    inp: UserInput,
    config: MarketConfig,
    result: AnalysisResult,
    show_zigzag: bool = True,
    show_buys: bool = True,
) -> go.Figure:
    """
    Full price chart with:
    1. Close price line
    2. ZigZag H markers (triangle-up, text=H)  — if show_zigzag
    3. ZigZag L markers (triangle-down, text=L) — if show_zigzag
    4. Trigger buy markers (star, text=Buy)     — if show_buys
    5. Current price marker
    6. ZigZag trigger level hline
    """
    fig = go.Figure()

    # ── 1. Price line ──────────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=result.close.index,
        y=result.close,
        mode="lines",
        name=f"{inp.ticker} Close",
        line=dict(color=config.line, width=4),
        showlegend=False,
    ))

    # ── 2 & 3. ZigZag H/L markers (golden engine) ────────────────────────────
    if show_zigzag:
        _golden_add_hl_markers(
            fig, result.close, inp.ticker, inp.ticker,
            threshold=inp.trigger_pct / 100.0,
        )

    # ── 4. Trigger buy markers ─────────────────────────────────────────────────
    if show_buys and result.backtest_df is not None:
        add_trigger_buy_markers(fig, result.backtest_df)

    # ── 5. Current price marker ────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=[result.current_date],
        y=[result.current_price],
        mode="markers+text",
        name="Current",
        marker=dict(size=8, color=config.chart2, symbol="circle"),
        text=["NOW"],
        textposition="bottom center",
        textfont=dict(size=8),
    ))

    # ── 6. Trigger hline (ZigZag-based reference high) ────────────────────────
    zz_trigger = result.zigzag_trigger_price
    fig.add_hline(
        y=zz_trigger,
        line_dash="dash",
        line_color="#b42318",
        annotation_text=(
            f"Trigger {inp.trigger_pct:.0f}%: {fmt_money(zz_trigger)}"
        ),
        annotation_position="bottom right",
    )

    stock_name = inp.ticker_label.split(" / ")[0].strip()
    fig.update_layout(
        title=dict(text=stock_name, x=0.5, xanchor="center"),
        hovermode="closest",
        legend=dict(
            orientation="h", y=-0.13,
            x=0.5, xanchor="center",
            font=dict(size=8),
        ),
        **_LAYOUT_BASE,
    )
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
    return fig


# ── Remaining charts (unchanged) ──────────────────────────────────────────────

def dividend_bar_chart(config: MarketConfig, result: AnalysisResult, inp=None) -> go.Figure | None:
    annual = result.annual_dividend_df
    if annual.empty:
        return None

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=annual["Year"],
        y=annual["Dividend per Share"],
        name="Annual Dividend per Share",
        marker=dict(color=config.chart1),
    ))
    title_text = inp.ticker_label.split(" / ")[0].strip() if inp else "Annual Dividend per Share"
    fig.update_layout(title=dict(text=title_text, x=0.5, xanchor="center"), **_LAYOUT_BASE)
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
    return fig


def reinvest_timeline_chart(
    inp: UserInput,
    config: MarketConfig,
    timeline_df: pd.DataFrame,
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timeline_df["Date"],
        y=timeline_df["External Invested"],
        mode="lines",
        name="External Invested",
        line=dict(color="#8a8f7a", width=3),
    ))
    fig.add_trace(go.Scatter(
        x=timeline_df["Date"],
        y=timeline_df["Portfolio Value"],
        mode="lines",
        name="Dividend Reinvested Value",
        line=dict(color=config.line, width=4),
    ))
    fig.update_layout(
        title=f"{inp.ticker_label} / Dividend Reinvestment Backtest",
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.13, font=dict(size=8)),
        **{**_LAYOUT_BASE, "height": CHART_HEIGHT_REINVEST},
    )
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
    return fig


def investment_simulation_chart(
    inp: UserInput,
    config: MarketConfig,
    no_reinvest_df: pd.DataFrame,
    reinvest_df: pd.DataFrame | None = None,
    show_reinvest: bool = False,
    trigger_dates=None,
) -> go.Figure:
    """No-reinvest baseline curve, with reinvest curve overlaid when requested.

    The no-reinvest portfolio is always plotted. When show_reinvest is True and
    reinvest_df is provided, an additional reinvest curve is overlaid on the
    same axes for visual comparison.
    """
    fig = go.Figure()

    if "External Invested" in no_reinvest_df.columns:
        fig.add_trace(go.Scatter(
            x=no_reinvest_df["Date"],
            y=no_reinvest_df["External Invested"],
            mode="lines",
            name="총 외부 투자금",
            line=dict(color="#8a8f7a", width=2, dash="dot"),
        ))

    if "Portfolio Value" in no_reinvest_df.columns:
        fig.add_trace(go.Scatter(
            x=no_reinvest_df["Date"],
            y=no_reinvest_df["Portfolio Value"],
            mode="lines",
            name="배당 미재투자",
            line=dict(color="#ca6702", width=3),
        ))

    if (
        show_reinvest
        and reinvest_df is not None
        and not reinvest_df.empty
        and "Portfolio Value" in reinvest_df.columns
    ):
        fig.add_trace(go.Scatter(
            x=reinvest_df["Date"],
            y=reinvest_df["Portfolio Value"],
            mode="lines",
            name="배당 재투자",
            line=dict(color=config.line, width=4),
        ))

    # ── Trigger buy markers on the displayed value curve ──────────────────────
    if trigger_dates is not None and len(trigger_dates) > 0:
        marker_df = (
            reinvest_df
            if (show_reinvest and reinvest_df is not None and not reinvest_df.empty)
            else no_reinvest_df
        )
        if marker_df is not None and "Portfolio Value" in marker_df.columns:
            val_by_date = {
                pd.Timestamp(d).normalize(): v
                for d, v in zip(marker_df["Date"], marker_df["Portfolio Value"])
            }
            xs, ys = [], []
            for td in trigger_dates:
                key = pd.Timestamp(td).normalize()
                if key in val_by_date:
                    xs.append(key)
                    ys.append(val_by_date[key])
            if xs:
                fig.add_trace(go.Scatter(
                    x=xs, y=ys, mode="markers",
                    name="트리거 매수",
                    marker=dict(size=9, color="#22c55e", symbol="star",
                                line=dict(width=1, color="#0b3d1a")),
                    hovertemplate="트리거 매수<br>%{x|%Y-%m-%d}<extra></extra>",
                ))

    stock_name = inp.ticker_label.split(" / ")[0].strip()
    fig.update_layout(
        title=dict(text=stock_name, x=0.5, xanchor="center"),
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.13, font=dict(size=8)),
        **{**_LAYOUT_BASE, "height": 330},
    )
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
    return fig


def share_quantity_comparison_bar_chart(
    config: MarketConfig,
    no_reinvest,
    reinvest=None,
    show_reinvest: bool = False,
) -> go.Figure:
    """Single bar of base shares, optionally stacked with reinvest-added shares.

    Accepts DividendReinvestResult objects and reads ``summary["Final Shares"]``.
    OFF: one bar = 기본 보유수량.
    ON:  stacked bar = 기본 보유수량 + 배당 재투자 추가수량.
    """
    base_shares = float(no_reinvest.summary["Final Shares"]) if no_reinvest is not None else 0.0
    extra_shares = 0.0
    if show_reinvest and reinvest is not None:
        reinvest_shares = float(reinvest.summary["Final Shares"])
        extra_shares = max(reinvest_shares - base_shares, 0.0)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=["보유 수량"],
        y=[base_shares],
        name="기본 보유수량",
        marker_color="#8a8f7a",
        text=[f"{base_shares:,.2f}"],
        textposition="inside",
    ))

    if show_reinvest:
        fig.add_trace(go.Bar(
            x=["보유 수량"],
            y=[extra_shares],
            name="배당 재투자 추가수량",
            marker_color=config.line,
            text=[f"+{extra_shares:,.2f}"],
            textposition="inside",
        ))

    fig.update_layout(
        title="보유 수량 비교",
        barmode="stack",
        hovermode="x",
        legend=dict(orientation="h", y=-0.18, font=dict(size=8)),
        **{**_LAYOUT_BASE, "height": 180},
    )
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(title="Shares", **_AXIS)
    return fig


def _yearly_total_shares(timeline_df: pd.DataFrame) -> pd.DataFrame:
    """Return one row per calendar year: end-of-year ``Total Shares``."""
    if timeline_df is None or timeline_df.empty:
        return pd.DataFrame(columns=["Year", "Total Shares"])
    if "Total Shares" not in timeline_df.columns or "Date" not in timeline_df.columns:
        return pd.DataFrame(columns=["Year", "Total Shares"])
    df = timeline_df[["Date", "Total Shares"]].copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.year
    yearly = (
        df.sort_values("Date")
        .groupby("Year", as_index=False)
        .agg({"Total Shares": "last"})
    )
    return yearly


def investment_quantity_chart(
    inp: UserInput,
    config: MarketConfig,
    no_reinvest,
    reinvest=None,
    show_reinvest: bool = False,
) -> go.Figure | None:
    """Yearly share-count bars. OFF = base only; ON = stacked base + reinvest extra.

    Reads ``timeline_df`` (Date + Total Shares), groups by year, takes the last
    observation per year. Returns ``None`` if the no-reinvest input has no
    usable share quantity series — the UI caller should warn the user.
    """
    if no_reinvest is None or no_reinvest.timeline_df.empty:
        return None

    base_yearly = _yearly_total_shares(no_reinvest.timeline_df)
    if base_yearly.empty:
        return None

    fig = go.Figure()

    base_x = base_yearly["Year"].astype(int).astype(str).tolist()
    base_y = base_yearly["Total Shares"].astype(float).tolist()

    fig.add_trace(go.Bar(
        x=base_x,
        y=base_y,
        name="기본 보유수량",
        marker_color="#8a8f7a",
        hovertemplate="%{x}<br>기본 보유수량: %{y:,.4f}<extra></extra>",
    ))

    if show_reinvest and reinvest is not None and not reinvest.timeline_df.empty:
        reinvest_yearly = _yearly_total_shares(reinvest.timeline_df)
        if not reinvest_yearly.empty:
            merged = base_yearly.merge(
                reinvest_yearly,
                on="Year",
                how="outer",
                suffixes=("_base", "_reinvest"),
            ).sort_values("Year")
            merged["Total Shares_base"] = merged["Total Shares_base"].fillna(0.0)
            merged["Total Shares_reinvest"] = merged["Total Shares_reinvest"].fillna(0.0)
            merged["Extra"] = (
                merged["Total Shares_reinvest"] - merged["Total Shares_base"]
            ).clip(lower=0.0)

            fig.data = ()
            fig.add_trace(go.Bar(
                x=merged["Year"].astype(int).astype(str).tolist(),
                y=merged["Total Shares_base"].astype(float).tolist(),
                name="기본 보유수량",
                marker_color="#8a8f7a",
                hovertemplate="%{x}<br>기본 보유수량: %{y:,.4f}<extra></extra>",
            ))
            fig.add_trace(go.Bar(
                x=merged["Year"].astype(int).astype(str).tolist(),
                y=merged["Extra"].astype(float).tolist(),
                name="배당 재투자 추가수량",
                marker_color=config.line,
                hovertemplate="%{x}<br>배당 재투자 추가수량: +%{y:,.4f}<extra></extra>",
            ))

    fig.update_layout(
        title=dict(text=inp.ticker_label.split(" / ")[0].strip(), x=0.5, xanchor="center"),
        barmode="stack",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="top", y=-0.22,
                    x=0.5, xanchor="center", font=dict(size=8)),
        **{**_LAYOUT_BASE, "height": 330, "margin": dict(l=36, r=26, t=48, b=64)},
    )
    fig.update_xaxes(title=None, type="category", **_AXIS)
    fig.update_yaxes(title="Shares", **_AXIS)
    return fig


def _yearly_dividend_income(result) -> tuple[pd.DataFrame, str]:
    """Return (yearly DataFrame with columns [Year, Income], source_label).

    Picks the best available column from result.annual_df in this priority:
    1. ``Net Dividend`` (already grouped per year)
    2. yearly diff of ``Cumulative Net Dividend``
    3. ``Gross Dividend`` (already grouped per year)

    Returns an empty DataFrame + empty source label when no usable column is found.
    """
    if result is None:
        return pd.DataFrame(columns=["Year", "Income"]), ""

    annual_df = getattr(result, "annual_df", None)
    if annual_df is None or annual_df.empty or "Year" not in annual_df.columns:
        return pd.DataFrame(columns=["Year", "Income"]), ""

    if "Net Dividend" in annual_df.columns:
        out = annual_df[["Year", "Net Dividend"]].rename(columns={"Net Dividend": "Income"})
        return out.sort_values("Year").reset_index(drop=True), "Net Dividend"

    if "Cumulative Net Dividend" in annual_df.columns:
        s = annual_df.sort_values("Year").reset_index(drop=True)
        income = s["Cumulative Net Dividend"].diff()
        income.iloc[0] = s["Cumulative Net Dividend"].iloc[0]
        out = pd.DataFrame({"Year": s["Year"], "Income": income})
        return out, "Cumulative Net Dividend (yearly diff)"

    if "Gross Dividend" in annual_df.columns:
        out = annual_df[["Year", "Gross Dividend"]].rename(columns={"Gross Dividend": "Income"})
        return out.sort_values("Year").reset_index(drop=True), "Gross Dividend"

    return pd.DataFrame(columns=["Year", "Income"]), ""


def annual_dividend_income_chart(
    inp: UserInput,
    config: MarketConfig,
    no_reinvest,
    reinvest=None,
    show_reinvest: bool = False,
) -> go.Figure | None:
    """Yearly net-dividend-income bars. OFF = base only; ON = stacked base + reinvest extra.

    Returns ``None`` when no usable income data is available — the UI caller
    should display a warning instead of rendering an empty chart.
    """
    base_yearly, base_source = _yearly_dividend_income(no_reinvest)
    if base_yearly.empty:
        return None

    currency = get_market_rule(config.key)["currency"]
    symbol = get_currency_symbol(currency)
    y_axis_title = f"Dividend Income ({currency})"
    hover_base = "%{x}<br>기본 연배당금: " + symbol + "%{y:,.0f} " + currency + "<extra></extra>"
    hover_extra = "%{x}<br>배당 재투자 추가 연배당금: +" + symbol + "%{y:,.0f} " + currency + "<extra></extra>"

    fig = go.Figure()

    if show_reinvest and reinvest is not None:
        reinvest_yearly, _ = _yearly_dividend_income(reinvest)
        if not reinvest_yearly.empty:
            merged = base_yearly.merge(
                reinvest_yearly, on="Year", how="outer", suffixes=("_base", "_reinvest"),
            ).sort_values("Year")
            merged["Income_base"] = merged["Income_base"].fillna(0.0)
            merged["Income_reinvest"] = merged["Income_reinvest"].fillna(0.0)
            merged["Extra"] = (merged["Income_reinvest"] - merged["Income_base"]).clip(lower=0.0)

            x_years = merged["Year"].astype(int).astype(str).tolist()
            fig.add_trace(go.Bar(
                x=x_years,
                y=merged["Income_base"].astype(float).tolist(),
                name="기본 연배당금",
                marker_color="#8a8f7a",
                hovertemplate=hover_base,
            ))
            fig.add_trace(go.Bar(
                x=x_years,
                y=merged["Extra"].astype(float).tolist(),
                name="배당 재투자 추가 연배당금",
                marker_color=config.line,
                hovertemplate=hover_extra,
            ))
        else:
            fig.add_trace(go.Bar(
                x=base_yearly["Year"].astype(int).astype(str).tolist(),
                y=base_yearly["Income"].astype(float).tolist(),
                name="기본 연배당금",
                marker_color="#8a8f7a",
                hovertemplate=hover_base,
            ))
    else:
        fig.add_trace(go.Bar(
            x=base_yearly["Year"].astype(int).astype(str).tolist(),
            y=base_yearly["Income"].astype(float).tolist(),
            name="기본 연배당금",
            marker_color="#8a8f7a",
            hovertemplate=hover_base,
        ))

    fig.update_layout(
        title=dict(text=inp.ticker_label.split(" / ")[0].strip(), x=0.5, xanchor="center"),
        barmode="stack",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="top", y=-0.22,
                    x=0.5, xanchor="center", font=dict(size=8)),
        **{**_LAYOUT_BASE, "height": 330, "margin": dict(l=36, r=26, t=48, b=64)},
    )
    fig.update_xaxes(title=None, type="category", **_AXIS)
    fig.update_yaxes(title=y_axis_title, tickprefix=symbol, separatethousands=True, **_AXIS)
    return fig


def investment_comparison_chart(
    inp: UserInput,
    config: MarketConfig,
    reinvest_df: pd.DataFrame,
    no_reinvest_df: pd.DataFrame,
) -> go.Figure:
    """Compare portfolio value with and without dividend reinvestment."""
    fig = go.Figure()

    baseline_df = reinvest_df if "External Invested" in reinvest_df.columns else no_reinvest_df
    if "External Invested" in baseline_df.columns:
        fig.add_trace(go.Scatter(
            x=baseline_df["Date"],
            y=baseline_df["External Invested"],
            mode="lines",
            name="총 외부 투자금",
            line=dict(color="#8a8f7a", width=2, dash="dot"),
        ))

    if "Portfolio Value" in no_reinvest_df.columns:
        fig.add_trace(go.Scatter(
            x=no_reinvest_df["Date"],
            y=no_reinvest_df["Portfolio Value"],
            mode="lines",
            name="배당 미재투자",
            line=dict(color="#ca6702", width=3),
        ))

    if "Portfolio Value" in reinvest_df.columns:
        fig.add_trace(go.Scatter(
            x=reinvest_df["Date"],
            y=reinvest_df["Portfolio Value"],
            mode="lines",
            name="배당 재투자",
            line=dict(color=config.line, width=4),
        ))

    fig.update_layout(
        title=f"{inp.ticker_label} / 배당 재투자 vs 미재투자",
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.13, font=dict(size=8)),
        **{**_LAYOUT_BASE, "height": 330},
    )
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
    return fig


def share_count_chart(config: MarketConfig, timeline_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timeline_df["Date"],
        y=timeline_df["Total Shares"],
        mode="lines",
        name="Total Shares",
        line=dict(color=config.chart1, width=4),
    ))
    fig.update_layout(
        title="Share Count Growth",
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.13, font=dict(size=8)),
        **{**_LAYOUT_BASE, "height": CHART_HEIGHT_REINVEST},
    )
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
    return fig


def score_gauge_chart(score: float, rank_label: str, rank_color: str) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "", "font": {"size": 38, "color": "#1f2b18"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#1f2b18"},
            "bar": {"color": rank_color, "thickness": 0.3},
            "bgcolor": "rgba(255,249,237,1)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 50],  "color": "rgba(200,200,200,0.18)"},
                {"range": [50, 65], "color": "rgba(205,127,50,0.18)"},
                {"range": [65, 80], "color": "rgba(192,192,192,0.18)"},
                {"range": [80, 100],"color": "rgba(255,215,0,0.18)"},
            ],
            "threshold": {
                "line": {"color": rank_color, "width": 4},
                "thickness": 0.75,
                "value": score,
            },
        },
        title={"text": f"Global Cup Score — {rank_label}", "font": {"size": 15, "color": "#1f2b18"}},
    ))
    fig.update_layout(
        height=130,
        paper_bgcolor="rgba(255,249,237,1)",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig
