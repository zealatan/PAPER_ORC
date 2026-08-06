#!/usr/bin/env bash
# 건축쇼츠 한 방 렌더(범용): TTS → 영상합성(자막) → 배포물 export
# 사용:  ./render.sh            # 전체
#        STEP=tts   ./render.sh # TTS만
#        STEP=build ./render.sh # 합성만
#        STEP=export ./render.sh# 배포물만
# 튜닝 환경변수: NAME · MAXCH(자막청크길이) · SUBS=0(자막끔) · TTS_SPEED · WEB_MB
set -e
cd "$(dirname "$0")"
STEP="${STEP:-all}"
[ "$STEP" = all -o "$STEP" = tts ]    && { echo "▶ 1/3 TTS (ElevenLabs)";      python3 gen_tts.py; }
[ "$STEP" = all -o "$STEP" = build ]  && { echo "▶ 2/3 영상 합성 + 자막";        python3 build_video.py; }
[ "$STEP" = all -o "$STEP" = export ] && { echo "▶ 3/3 배포물 export";           python3 export.py; }
echo "✔ 완료 → out/"
