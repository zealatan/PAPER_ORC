# Global Cup Market Dashboard

A premium, dark-green Streamlit dashboard for global market analysis — drawdown tracking, dividend analysis, dividend reinvestment backtesting, and a **Global Cup Score** ranking system.

## Folder Structure

```
global_cup_refactored/
├── app.py                   # Streamlit entry point
├── landing.html             # Public-facing landing page
├── requirements.txt
├── README.md
├── data/
│   ├── tickers_us.csv       # ~150 US stocks & ETFs
│   ├── tickers_korea.csv    # ~70 Korean stocks & ETFs
│   ├── tickers_japan.csv    # Japan stocks & ETFs
│   ├── tickers_eu.csv       # European stocks & ETFs
│   └── tickers_global.csv   # Global ETFs & international stocks
├── global_cup/
│   ├── __init__.py
│   ├── config.py            # App constants, tax rules, market rules
│   ├── market_config.py     # Dataclasses, MARKETS registry, flag helpers
│   ├── data_loader.py       # yfinance downloads, CSV loader, caching
│   ├── analysis.py          # Drawdown, trigger, dividend yield calculation
│   ├── dividend_reinvest.py # Full dividend reinvestment backtest engine
│   ├── scoring.py           # Global Cup Score (0–100) + ranking labels
│   ├── charts.py            # Plotly figure builders
│   └── ui.py                # CSS, nav, controls, tabs, ranking cards
└── md_files/
    └── step_001_global_cup_refactor_prompt.md
```

## How to Run

```bash
cd global_cup_refactored
pip install -r requirements.txt
streamlit run app.py
```

The landing page (`landing.html`) can be served separately with any static file server.

## Ticker CSV Files

Each CSV has the following columns:

| Column     | Description                              |
|------------|------------------------------------------|
| `label`    | Display name shown in the dropdown       |
| `ticker`   | yfinance-compatible ticker symbol        |
| `category` | ETF / Stock / Covered Call ETF           |
| `country`  | Market country                           |
| `currency` | Base currency (USD / KRW / JPY / EUR …)  |

You can add, remove, or edit rows freely. The app loads these at startup and falls back to a compact built-in list if a CSV is missing.

## Global Cup Score

The score (0–100) ranks how **attractive** a ticker currently looks as a buy opportunity.

| Component           | Weight | Logic                                          |
|---------------------|--------|------------------------------------------------|
| Drawdown score      | 35%    | Bigger pullback from all-time high → higher    |
| Dividend yield      | 30%    | Higher trailing 12-month yield → higher        |
| Momentum (contrarian)| 20%  | Recent pullback → higher (contrarian signal)   |
| Dividend consistency| 15%    | More years with dividends in period → higher   |

### Ranking Labels

| Label      | Score Range |
|------------|-------------|
| Gold       | 80 – 100    |
| Silver     | 65 – 79     |
| Bronze     | 50 – 64     |
| Watchlist  | 0 – 49      |

## Disclaimer

This dashboard is for educational and visualization purposes only.
**It is not financial advice.** Past dividend or price data does not guarantee future results.
Always do your own research before making investment decisions.
