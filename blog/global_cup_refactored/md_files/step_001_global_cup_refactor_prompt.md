# Step 001 — Global Cup Refactor Prompt

**Archived:** 2026-06-05

---

You are Claude Code acting as a senior full-stack Python/Streamlit refactoring engineer.

## PROJECT CONTEXT

This project currently has two important files:

1. `global_cup_landing_final.html`
   - A polished standalone landing page for "Global Cup — Market Dashboard"
   - Dark green / cream premium visual style
   - Orbit cards for Korea, US, EU, Japan, Global
   - Intended as the public-facing landing page

2. `global_cup_dividend_reinvest_ported(1).py`
   - A Streamlit app
   - Uses yfinance, pandas, plotly
   - Provides market dashboard, ticker selection, dividend analysis, drawdown trigger, and dividend reinvestment simulation
   - Contains many hardcoded ticker dictionaries directly inside the Python file
   - Visual style partially matches the landing page but still feels like a Streamlit app

## MAIN GOAL

Do NOT destroy the current working version.
First back up the existing files.
Then create a clean refactored version in a new separate folder.
The goal is to turn this into a maintainable "Global Cup Market Dashboard" project.

**IMPORTANT:**
- Do not simplify away existing functionality.
- Do not remove dividend reinvestment logic.
- Do not remove market/ticker support.
- Do not change the core visual identity.
- Preserve the dark green / cream Global Cup branding.

## STEP 0 — SAFETY BACKUP

Create a backup folder: `backup_original/`

Copy the current files into it:
- `backup_original/global_cup_landing_final.html`
- `backup_original/global_cup_dividend_reinvest_ported.py`

## STEP 1 — CREATE NEW REFACTOR FOLDER

```
global_cup_refactored/
├── app.py
├── landing.html
├── requirements.txt
├── README.md
├── data/
│   ├── tickers_us.csv
│   ├── tickers_korea.csv
│   ├── tickers_japan.csv
│   ├── tickers_eu.csv
│   └── tickers_global.csv
├── global_cup/
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── market_config.py
│   ├── analysis.py
│   ├── dividend_reinvest.py
│   ├── scoring.py
│   ├── charts.py
│   └── ui.py
└── md_files/
    └── step_001_global_cup_refactor_prompt.md
```

## STEP 2 — MOVE LANDING PAGE

Copy `global_cup_landing_final.html` into `global_cup_refactored/landing.html`.
Only make minimal edits if required:
- Make links/buttons point to the Streamlit dashboard entry point where appropriate.
- Keep the existing visual design.

## STEP 3 — SPLIT PYTHON CODE

Refactor `global_cup_dividend_reinvest_ported.py` into modules.

### `app.py`
- Streamlit entry point only
- Page setup
- Calls UI rendering functions
- No giant ticker dictionaries
- No huge CSS block unless delegated to `ui.py`

### `global_cup/config.py`
- App constants, Page title, Market rules, Default dates, Tax rules

### `global_cup/market_config.py`
- MarketConfig dataclass, UserInput dataclass, AnalysisResult dataclass, DividendReinvestResult dataclass
- Market definitions, Flag class helper

### `global_cup/data_loader.py`
- yfinance price download, dividend download
- cache decorators, ticker CSV loading, close series extraction

### `global_cup/analysis.py`
- drawdown calculation, high price calculation, trigger price calculation
- dividend yield calculation, annual dividend table generation

### `global_cup/dividend_reinvest.py`
- dividend reinvestment simulator, event table generation
- annual summary, timeline calculation, tax handling

### `global_cup/scoring.py`
- Global Cup score system (0 to 100)
- Score combines: drawdown attractiveness, dividend yield, recent momentum, dividend consistency
- Ranking labels: Gold / Silver / Bronze / Watchlist

### `global_cup/charts.py`
- Plotly chart creation: Price chart, Dividend chart, Reinvestment timeline chart, Score/ranking visualization

### `global_cup/ui.py`
- CSS injection, Top nav, Market selector UI, Sidebar/expander controls
- Metric cards, Ranking cards, Chart sections, Dataframe sections

## STEP 4 — EXTRACT TICKERS TO CSV

CSV columns: `label,ticker,category,country,currency`

## STEP 5 — IMPROVE PRODUCT DIRECTION

Add a "Global Cup Ranking" section showing which market/ticker looks attractive using:
- Global Cup Score (0-100)
- Drawdown %
- Dividend yield %
- Recent momentum %
- Trigger status

## STEP 6 — UI/UX REQUIREMENTS

Preserve Global Cup style: dark green background, cream cards, rounded pill buttons, premium dashboard style.

## STEP 7 — REQUIREMENTS

```
streamlit
yfinance
pandas
plotly
```

## STEP 8 — README

Project description, folder structure, run command, ticker CSV explanation, score explanation, disclaimer.

## STEP 9 — VALIDATION

```
python -m py_compile app.py
python -m py_compile global_cup/*.py
```

## STEP 10 — REPORT

Final summary of all files created/modified and any limitations.

---

*This file is an archived copy of the refactoring prompt issued on 2026-06-05.*
