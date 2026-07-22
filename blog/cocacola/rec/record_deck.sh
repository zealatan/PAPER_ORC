#!/bin/bash
# 코카콜라 덱 1080p60 화면녹화 (GPU NVENC, 무음)
# 사용법: ./record_deck.sh [출력파일] [초]   (초 생략 시 수동 중지: Ctrl-C 또는 stop 파일)
set -e
export DISPLAY=:1 XAUTHORITY=/run/user/1000/gdm/Xauthority
OUT="${1:-recordings/cocacola_$(date +%H%M%S).mp4}"
DUR="${2:-}"
mkdir -p "$(dirname "$OUT")"
ARGS=(-hide_banner -y
  -f x11grab -draw_mouse 0 -framerate 60 -video_size 1920x1080 -i :1
  -c:v h264_nvenc -preset p5 -rc vbr -cq 19 -b:v 0 -maxrate 60M -bufsize 120M
  -pix_fmt yuv420p -movflags +faststart)
[ -n "$DUR" ] && ARGS+=(-t "$DUR")
echo "녹화 시작 → $OUT  (${DUR:-무제한}s)"
exec ffmpeg "${ARGS[@]}" "$OUT"
