"""덱->TTS->타이밍->음성트랙 폐루프. subLines 원천을 spec 단일화(HTML SUBS 파싱 제거).
reuses: rec/gen_tts.py, build_timing.py, build_voice.py (voice_id<-spec.story.voice)

STATUS: stub — 설계 wf_0c9ec72e-2f1. 구현 대기.
"""
from __future__ import annotations

def run_dub(spec):
    """-> (deck_dubbed_json, voice_track_wav, total_ms)"""
    raise NotImplementedError

def _extract(spec):
    """-> lines"""
    raise NotImplementedError

def _synth(lines, voice):
    """-> manifest (tts 클립 캐시: voice_id+텍스트해시)"""
    raise NotImplementedError

def _timing(manifest):
    """-> subTimes/subHold"""
    raise NotImplementedError

def _voice(timeline):
    """-> wav"""
    raise NotImplementedError
