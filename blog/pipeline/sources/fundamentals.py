"""data.business 생산. ★결정론 소스 없음 = 최대 공백.
증배연수만 배당시리즈에서 결정론 계산, 나머지는 curation/overrides/{ticker}.yaml + sources[].

STATUS: stub — 설계 wf_0c9ec72e-2f1. 구현 대기.
"""
from __future__ import annotations

def build_business(ticker, overrides_path):
    """-> business dict"""
    raise NotImplementedError

def consecutive_div_growth_years(annual_dividends):
    """-> int (결정론)"""
    raise NotImplementedError

def fetch_info(ticker):
    """-> dict (yfinance .info, 불안정)"""
    raise NotImplementedError
