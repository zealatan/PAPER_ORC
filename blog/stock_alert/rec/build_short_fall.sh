#!/bin/bash
# 낙폭(하락) 쇼츠 합성 — 카드 추출/템플릿 로직은 build_short_rise.sh 와 완전 동일(공유 엔진).
# 상승/낙폭 차이는 훅(📉)뿐이라 엔진을 공유한다. 하단 배투실 텍스트·아웃트로도 동일.
#
# 전제(순서):
#   1) python3 deck/build_fall_deck.py <시장>     # 단일시장 낙폭 덱(drawcard subHold=5500)
#   2) python3 rec/render_rise.py fall             # → recordings/rise_raw/*.webm
#   3) rec/build_short_fall.sh <n_cards> assets/shorts/hook_<시장>.png shorts/short_<시장>.mp4
#
# 사용: build_short_fall.sh <n_cards> <hook.png(📉)> <out.mp4>
exec "$(dirname "$0")/build_short_rise.sh" "$@"
