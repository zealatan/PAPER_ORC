"""story.hook/sections/scenes.subLines 생성·검증. 대본은 backtest 숫자만 인용(cites[]).
reuses: gen_storyboard_v3.py 글자수->dur, rec/extract_lines.py 평탄화

STATUS: stub — 설계 wf_0c9ec72e-2f1. 구현 대기.
"""
from __future__ import annotations

def sections_to_sublines(spec):
    """-> scenes[].subLines"""
    raise NotImplementedError

def verify_citations(spec):
    """-> list[mismatch] (대본 인용 vs 엔진값)"""
    raise NotImplementedError

def scene_dur_from_text(text, rate=5):
    """-> sec"""
    raise NotImplementedError
