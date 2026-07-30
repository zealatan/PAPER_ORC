#!/bin/bash
# 상승(신고가) 쇼츠 합성 — rise 덱 렌더(webm) → 표준 9:16 쇼츠 + 이모지 아웃트로.
#
# 전제(순서대로):
#   1) python3 deck/build_rise_deck.py <시장>      # 단일시장 덱 (risecard subHold=5500 균일)
#   2) python3 rec/render_rise.py                  # → recordings/rise_raw/*.webm (최신 사용)
#   3) rec/build_short_rise.sh <n_cards> <hook.png> <out.mp4> [table.png]
#
# 균일 타이밍 덕에 카드 구간이 결정적: 카드시작 = t0 + INTRO, 길이 = n_cards × CARD.
# 골든 구성: 카드 n장 → [요약 테이블 5s(table.png 주면)] → 심플 아웃트로 3.5s.
# 표준 템플릿: 그래프 top696 · 하단 "배투실" 텍스트워터마크 · 상단 훅.
set -e
cd "$(dirname "$0")/.."
NCARDS="$1"; HOOK="$2"; OUT="$3"; TABLE="$4"   # TABLE(선택): gen_table.py 산출 요약표 PNG
[ -z "$OUT" ] && { echo "사용: build_short_rise.sh <n_cards> <hook.png> <out.mp4> [table.png]"; exit 1; }
WEBM=$(ls -t recordings/rise_raw/*.webm | head -1)
TEXT="assets/shorts/batusil_text.png"     # 하단 워터마크(작은 배투실 글자)
OUTRO="assets/shorts/outro_card.png"      # 심플 구독 엔드카드
INTRO=17.56       # 인트로(notice+hook+sectnum) 길이(초). subHold 균일화 후 고정값.
CARD=5.5          # risecard subHold(초) — build_rise_deck.py 와 동기 (바꾸면 여기도)
TABLE_SEC=5.0     # 요약 테이블 노출 시간
mkdir -p "$(dirname "$OUT")"; TMP=$(mktemp -d)

BE=$(ffmpeg -hide_banner -i "$WEBM" -vf "blackdetect=d=0.2:pix_th=0.10" -an -f null - 2>&1 \
     | grep -oP 'black_end:\K[0-9.]+' | head -1)
ST=$(python3 -c "print(round(${BE:-3.24}+$INTRO,2))")
DU=$(python3 -c "print(round($NCARDS*$CARD,2))")
echo "t0=${BE:-3.24} 카드시작=$ST 길이=$DU (${NCARDS}장)"

# 카드 구간 → 표준 9:16 (그래프 top696 · 배투실텍스트 y1560 · 훅 y250)
ffmpeg -hide_banner -loglevel error -y -ss "$ST" -t "$DU" -i "$WEBM" -i "$TEXT" -i "$HOOK" \
 -filter_complex "[0:v]scale=1080:-2,pad=1080:1920:(ow-iw)/2:696:black,fps=30,setsar=1[v1];\
[1:v]scale=155:-1[wm];[v1][wm]overlay=(W-w)/2:1560[v2];\
[v2][2:v]overlay=(W-w)/2:250,format=yuv420p[v]" \
 -map "[v]" -an -c:v libx264 -crf 19 -preset medium -pix_fmt yuv420p -r 30 "$TMP/cards.mp4"

# 심플 아웃트로 3.5s
ffmpeg -hide_banner -loglevel error -y -loop 1 -t 3.5 -i "$OUTRO" \
 -vf "scale=1080:1920,fps=30,format=yuv420p,setsar=1" -c:v libx264 -crf 19 -preset medium "$TMP/outro.mp4"

# (선택) 요약 테이블 5s
PARTS="[0:v]"; NIN=1
INPUTS=(-i "$TMP/cards.mp4")
if [ -n "$TABLE" ] && [ -f "$TABLE" ]; then
  ffmpeg -hide_banner -loglevel error -y -loop 1 -t "$TABLE_SEC" -i "$TABLE" \
   -vf "scale=1080:1920,fps=30,format=yuv420p,setsar=1" -c:v libx264 -crf 19 -preset medium "$TMP/table.mp4"
  INPUTS+=(-i "$TMP/table.mp4"); PARTS="$PARTS[1:v]"; NIN=2
fi
INPUTS+=(-i "$TMP/outro.mp4"); PARTS="$PARTS[${NIN}:v]"; NIN=$((NIN+1))

# 카드 (+테이블) + 아웃트로 concat (SAR 통일)
FC=""; i=0
for ((k=0;k<NIN;k++)); do FC="$FC[$k:v]setsar=1[s$k];"; done
CAT=""; for ((k=0;k<NIN;k++)); do CAT="$CAT[s$k]"; done
ffmpeg -hide_banner -loglevel error -y "${INPUTS[@]}" \
 -filter_complex "${FC}${CAT}concat=n=${NIN}:v=1[v]" -map "[v]" -an \
 -c:v libx264 -crf 19 -preset medium -pix_fmt yuv420p -movflags +faststart "$OUT"
rm -rf "$TMP"
echo "SHORT_DONE $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s)"
