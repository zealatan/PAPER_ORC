"""run(spec) 결정론적 백테스트 오케스트레이터: FIRE 그리드 + 전략비교.
reuses: fire_engine.run_fire_backtest(:73), golden_engine.run_backtest(:266, 4모드), gen_fire_corpus.ser()

STATUS: stub — 설계 wf_0c9ec72e-2f1. 구현 대기.
"""
from __future__ import annotations

def run(spec):
    """-> spec.backtest 전체 되채움"""
    raise NotImplementedError

def _run_fire_grid(close, div, cpi, grid):
    """-> scenarios[]"""
    raise NotImplementedError

def _run_strategy_compare(close, div):
    """-> {lump,dca,buy_dip,trigger_dates}"""
    raise NotImplementedError

def _timeline_to_pts(timeline_df, every=3):
    """-> pts[[x,y]]"""
    raise NotImplementedError
