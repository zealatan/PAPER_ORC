#!/bin/bash
# 카드 인트로(1초) + 롱폼 그래프 구간 → 9:16 세로 쇼츠.
# 사용: build_short_v2.sh <src.mp4> <graph_start> <graph_dur> <hook.png> <out.mp4>
set -e
cd "$(dirname "$0")/.."
SRC="$1"; GS="$2"; GD="$3"; HOOK="$4"; OUT="$5"
BATU="assets/shorts/batusil.png"
CARD="assets/shorts/card_clean.png"
TMP="$(mktemp -d)"
mkdir -p "$(dirname "$OUT")"

# 공통 세로 합성 필터 (검은 배경 + 가운데 16:9 + 상단 훅 + 하단 배투실)
VF="[0:v]scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2+170:black,fps=30[v1];\
[2:v]scale=140:-1[wm];\
[v1][1:v]overlay=(W-w)/2:400[v2];\
[v2][wm]overlay=(W-w)/2:1650,format=yuv420p[v]"

# 1) 카드 인트로 1초 (무음)
ffmpeg -hide_banner -loglevel error -y \
  -loop 1 -t 1.0 -i "$CARD" -i "$HOOK" -i "$BATU" -f lavfi -t 1.0 -i anullsrc=r=48000:cl=stereo \
  -filter_complex "$VF" -map "[v]" -map 3:a \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -r 30 -c:a aac -b:a 256k -t 1.0 "$TMP/intro.mp4"

# 2) 그래프 구간
ffmpeg -hide_banner -loglevel error -y -ss "$GS" -t "$GD" -i "$SRC" -i "$HOOK" -i "$BATU" \
  -filter_complex "$VF" -map "[v]" -map 0:a \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -r 30 -c:a aac -b:a 256k "$TMP/graphs.mp4"

# 3) 이어붙이기 (concat 필터, 재인코딩)
ffmpeg -hide_banner -loglevel error -y -i "$TMP/intro.mp4" -i "$TMP/graphs.mp4" \
  -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p \
  -c:a aac -b:a 256k -movflags +faststart "$OUT"
rm -rf "$TMP"
echo "SHORT_DONE $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s)"
