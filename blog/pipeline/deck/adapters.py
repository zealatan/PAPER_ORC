"""★핵심 어댑터. video_spec 필드 -> 각 tpl이 요구하는 data 형태로 변환.
골든: cocacola_deck_dubbed.json 실측 형태. 18종 tpl data 계약.

STATUS: stub — 설계 wf_0c9ec72e-2f1. 구현 대기.
"""
from __future__ import annotations

def to_enginechart(fire_scenario_or_strategy):
    """-> data{chart.series[].pts, table.rows}"""
    raise NotImplementedError

def to_regionmap(region_revenue):
    """-> data"""
    raise NotImplementedError

def to_divbars(annual_dividends):
    """-> data"""
    raise NotImplementedError

def to_herostat(...):
    """-> data"""
    raise NotImplementedError

def build_scenes(spec):
    """-> spec.scenes (sid별 tpl dispatch)"""
    raise NotImplementedError
