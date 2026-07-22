"""대조(QA) 계층: 대본인용 vs 엔진값, 덱 pts vs backtest.pts, fundamentals vs sources, 골든회귀.
reuses: _validation/validate_fire.py 불변식 패턴, narration.verify_citations

STATUS: stub — 설계 wf_0c9ec72e-2f1. 구현 대기.
"""
from __future__ import annotations

def reconcile(spec):
    """-> report(불일치 리스트)"""
    raise NotImplementedError

def regression_vs_golden(deck_json, golden_path):
    """-> diff"""
    raise NotImplementedError
