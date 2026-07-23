#!/bin/bash
# 롱폼 mp4에서 구간을 잘라 9:16 세로 쇼츠 합성.
# 사용: build_short.sh <src.mp4> <start초> <길이초> <hook.png> <out.mp4>
# 레이아웃: 블러 배경(같은 영상 확대) + 가운데 16:9 원본 + 상단 훅 + 하단 배투실
set -e
cd "$(dirname "$0")/.."
SRC="$1"; START="$2"; DUR="$3"; HOOK="$4"; OUT="$5"
BATU="$(ls /tmp/claude-*/*/scratchpad/batusil.png 2>/dev/null | head -1)"
[ -z "$BATU" ] && BATU="assets/shorts/batusil.png"
mkdir -p "$(dirname "$OUT")"

ffmpeg -hide_banner -loglevel warning -y \
  -ss "$START" -t "$DUR" -i "$SRC" \
  -i "$HOOK" -i "$BATU" \
  -filter_complex "\
    [0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:1,eq=brightness=-0.24:saturation=0.55[bg];\
    [0:v]scale=1080:-2[fg];\
    [bg][fg]overlay=(W-w)/2:(H-h)/2+20[v1];\
    [2:v]scale=140:-1[wm];\
    [v1][1:v]overlay=(W-w)/2:150[v2];\
    [v2][wm]overlay=(W-w)/2:1735,format=yuv420p[v]" \
  -map "[v]" -map 0:a \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p \
  -c:a aac -b:a 256k -movflags +faststart "$OUT"
echo "SHORT_DONE $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s)"
