#!/bin/bash
# 마스터 영상 + 목소리(+선택 BGM) → 최종 영상
# 사용:
#   mix_audio.sh <영상.mp4> <목소리.wav|mp3> [출력.mp4] [BGM.mp3]
# - 영상은 재인코딩 없이 그대로 복사(-c:v copy) → 화질 손실 0
# - 목소리는 loudnorm으로 -16 LUFS 정규화(유튜브 표준 근처)
# - BGM 주면 목소리에 맞춰 자동 다운(사이드체인 덕킹) 후 -22 LUFS로 섞음
set -e
VID="$1"; VOICE="$2"; OUT="${3:-recordings/cocacola_final_video.mp4}"; BGM="$4"
[ -z "$VID" ] || [ -z "$VOICE" ] && { echo "사용: mix_audio.sh <영상> <목소리> [출력] [BGM]"; exit 1; }
mkdir -p "$(dirname "$OUT")"

if [ -z "$BGM" ]; then
  ffmpeg -hide_banner -y -i "$VID" -i "$VOICE" \
    -filter_complex "[1:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[a]" \
    -map 0:v:0 -map "[a]" -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart "$OUT"
else
  ffmpeg -hide_banner -y -i "$VID" -i "$VOICE" -i "$BGM" \
    -filter_complex "\
      [1:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[voice]; \
      [2:a]aresample=48000,volume=0.35[bg]; \
      [bg][voice]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[bgduck]; \
      [voice][bgduck]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-15:TP=-1.5[a]" \
    -map 0:v:0 -map "[a]" -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart "$OUT"
fi
echo "완료 → $OUT"
