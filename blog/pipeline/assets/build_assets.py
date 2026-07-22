"""썸네일·배경클립 매핑·publish 메타. bg클립 생성은 범위 밖(수동 슬롯).
reuses: 오늘 만든 thumbnail 합성(PIL), CHAPBG 매핑

STATUS: stub — 설계 wf_0c9ec72e-2f1. 구현 대기.
"""
from __future__ import annotations

def build_thumbnail(spec):
    """-> png"""
    raise NotImplementedError

def resolve_bg_clips(bg_clips):
    """-> CHAPBG dict"""
    raise NotImplementedError

def publish_meta(spec):
    """-> {title,desc,tags}"""
    raise NotImplementedError
