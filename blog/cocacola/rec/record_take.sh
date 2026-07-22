#!/bin/bash
# 덱을 씬0부터 재시작하고 지정 시간만큼 1080p60 무음 녹화 (GPU NVENC)
# 사용: record_take.sh <출력.mp4> <녹화초>
set -e
cd "$(dirname "$0")/.."
export DISPLAY=:1 XAUTHORITY=/run/user/1000/gdm/Xauthority
OUT="${1:-recordings/take.mp4}"; DUR="${2:-720}"
mkdir -p "$(dirname "$OUT")"

# 1) firefox 포커스 + 씬0 재시작
python3 rec/send_key.py Home >/dev/null
# 2) 즉시 녹화 시작 (씬0 페이드인 극초반 ~0.3s만 생략됨 — 문제없음)
exec ffmpeg -hide_banner -loglevel warning -y \
  -f x11grab -draw_mouse 0 -framerate 60 -video_size 1920x1080 -i :1 \
  -t "$DUR" \
  -c:v h264_nvenc -preset p5 -rc vbr -cq 19 -b:v 0 -maxrate 60M -bufsize 120M \
  -pix_fmt yuv420p -movflags +faststart "$OUT"
