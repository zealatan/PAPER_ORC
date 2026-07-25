#!/bin/bash
# 카드 인트로(1초) + 롱폼 그래프 구간 → 9:16 세로 쇼츠.
# 사용: build_short_v2.sh <src.mp4> <graph_start> <graph_dur> <hook.png> <out.mp4>
set -e
cd "$(dirname "$0")/.."
SRC="$1"; GS="$2"; GD="$3"; HOOK="$4"; OUT="$5"
BATU="assets/shorts/batusil_label.png"
CARD="assets/shorts/card_full.png"
TMP="$(mktemp -d)"
mkdir -p "$(dirname "$OUT")"

# 공통 베이스: 자막박스 크롭(914) → 세로 캔버스 배치 + 하단 배투실
# 카드 인트로는 훅 없음(카드 자체 아치 로고와 중복 방지). 그래프에만 상단 훅.
# 자막·숫자 모두 유지(크롭 없음). 슬라이드 우상단 배투실만 '깨끗한 종이 패치'로 덮어 제거.
# 카드 인트로: 자체 배투실 그대로(제목 카드) · 오버레이 없음.
VF_INTRO="[0:v]scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2+40:black,fps=30,format=yuv420p[v]"
VF_GRAPH="[0:v]split[b][p];[p]crop=140:184:1645:22[pt];[b][pt]overlay=1778:22[gc];\
[gc]scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2+40:black,fps=30[v1];\
[2:v]scale=170:-1[wm];\
[v1][1:v]overlay=(W-w)/2:200[v2];[v2][wm]overlay=(W-w)/2:1470,format=yuv420p[v]"

# 1) 카드 인트로 1초 (무음) — 훅 미적용
ffmpeg -hide_banner -loglevel error -y \
  -loop 1 -t 1.0 -i "$CARD" -i "$HOOK" -i "$BATU" -f lavfi -t 1.0 -i anullsrc=r=48000:cl=stereo \
  -filter_complex "$VF_INTRO" -map "[v]" -map 3:a \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -r 30 -c:a aac -b:a 256k -t 1.0 "$TMP/intro.mp4"

# 2) 그래프 구간 — 상단 훅 적용
ffmpeg -hide_banner -loglevel error -y -ss "$GS" -t "$GD" -i "$SRC" -i "$HOOK" -i "$BATU" \
  -filter_complex "$VF_GRAPH" -map "[v]" -map 0:a \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -r 30 -c:a aac -b:a 256k "$TMP/graphs.mp4"

# 3) 이어붙이기 (concat 필터, 재인코딩)
ffmpeg -hide_banner -loglevel error -y -i "$TMP/intro.mp4" -i "$TMP/graphs.mp4" \
  -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p \
  -c:a aac -b:a 256k -movflags +faststart "$OUT"
rm -rf "$TMP"
echo "SHORT_DONE $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s)"
