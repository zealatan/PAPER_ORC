#!/bin/bash
# 본 녹화: 씬0 재시작 + 자동복구(keep_fs) 병행 + 1080p60 무음 NVENC
set -e
cd "$(dirname "$0")/.."
export DISPLAY=:1 XAUTHORITY=/run/user/1000/gdm/Xauthority
WID="${1:-0x1c00017}"
OUT="${2:-recordings/cocacola_deck_master.mp4}"
DUR="${3:-721}"
mkdir -p "$(dirname "$OUT")"

# 1) 씬0 재시작(+포커스)
python3 rec/send_key.py Home >/dev/null
# 2) 자동복구 루프 병행 (녹화보다 길게)
python3 rec/keep_fs.py "$WID" $((DUR+8)) >/tmp/keepfs_full.log 2>&1 &
KP=$!
# 3) 녹화
ffmpeg -hide_banner -loglevel warning -y \
  -f x11grab -draw_mouse 0 -framerate 60 -video_size 1920x1080 -i :1 \
  -t "$DUR" \
  -c:v h264_nvenc -preset p5 -rc vbr -cq 19 -b:v 0 -maxrate 60M -bufsize 120M \
  -pix_fmt yuv420p -movflags +faststart "$OUT"
kill $KP 2>/dev/null || true
echo "RECORD_DONE $OUT"
