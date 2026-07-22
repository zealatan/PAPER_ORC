"""spec.scenes + deck_layout(ov/cp) -> 덱 JSON({scenes,ov,cp,theme,paper}).
reuses: build_cur33.py out 구조. OV/CP를 index->sid 매핑으로 교체(순서변경에 강건).

STATUS: stub — 설계 wf_0c9ec72e-2f1. 구현 대기.
"""
from __future__ import annotations

def build_deck(spec):
    """-> deck_json"""
    raise NotImplementedError

def write_deck(deck_json, path): ...
    """"""
    raise NotImplementedError

def _resolve_ov_cp_by_sid(scenes, deck_layout): ...
    """"""
    raise NotImplementedError
