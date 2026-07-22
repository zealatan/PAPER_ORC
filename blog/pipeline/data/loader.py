"""headless(streamlit 무의존) 가격·배당 로더 + 월봉 리샘플 + CPI.
reuses: global_cup/data_loader.py (yfinance, @st.cache_data 제거), backtest_engine.calculate_annual_dividends

STATUS: stub — 설계 wf_0c9ec72e-2f1. 구현 대기.
"""
from __future__ import annotations

def fetch_price(ticker, start, end):
    """-> pd.Series(daily close)"""
    raise NotImplementedError

def fetch_dividends(ticker, start, end):
    """-> pd.Series(ex-date DPS)"""
    raise NotImplementedError

def to_monthly(close):
    """-> pd.Series(월말 리샘플)"""
    raise NotImplementedError

def load_cpi(currency):
    """-> pd.Series (USD->CPIAUCSL, KRW->KORCPIALLMINMEI)"""
    raise NotImplementedError

def populate_data(spec):
    """-> spec (data.monthly_price/dividends/annual_dividends 채움)"""
    raise NotImplementedError
