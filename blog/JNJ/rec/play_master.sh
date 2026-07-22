#!/bin/bash
# 마스터(또는 프록시)를 이 화면에 전체화면 재생 (ffplay, 무음, 코덱 내장)
# 사용: play_master.sh [파일]   기본=마스터
cd "$(dirname "$0")/.."
export DISPLAY=:1 XAUTHORITY=/run/user/1000/gdm/Xauthority
F="${1:-recordings/cocacola_deck_master.mp4}"
exec ffplay -fs -an -loglevel error -autoexit "$F"
