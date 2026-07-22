# 코카콜라(KO) 배당 백테스트 영상 — 완성·공개됨

첫 편. **공개**: https://www.youtube.com/watch?v=-yv2igFEaZc (배투실)
JNJ와 **동일한 구조**로 정리(각 영상 = 자기 폴더). 이후 편의 **참고 기준**.

## 구조
```
cocacola/
  deck/         cocacola_final.html(렌더 엔진) + _recload*.html(덱 주입 로더)
                bg/(배경영상 18) · clip/(훅클립) · template.html · thumbnail.html
  data/         cocacola_deck_dubbed.json(최종 덱) · cocacola_deck_current.json
                ko_price.csv · ko_div.csv · ko_smart_vs_steady.py(전략엔진) · *.json
  narration/    cocacola_narration.txt · cocacola_subtitles.srt · 대본 md · prompt.md
  rec/          더빙·렌더 체인(gen_tts→build_timing→build_voice→record_full→mix) + narration_lines/manifest/timeline
  tools/        gen_storyboard_v3 · build_cur33 · gen_pages* · render_thumbs 등 덱 제작 도구
  recordings/   최종 영상·쇼츠·썸네일 (gitignore)
  tts/          TTS 클립 캐시 (gitignore)
  src_img/      씬 소스 이미지 · thumbs/ · thumbs_sm/(스토리보드 썸네일)
  fonts/        BlackHanSans
```

## 경로 규칙 (이동 후)
- 렌더 URL: `http://127.0.0.1:8000/cocacola/deck/cocacola_final.html?rec` (http는 blog/ 서빙)
- rec 스크립트: 덱=`../deck/`, 데이터=`../data/` (이동 시 수정 완료). `ROOT=rec/..=cocacola/`
- 백테스트 엔진: `blog/engines`(→ `global_cup_suite/global_cup` 심링크, 공용)

## 재현
- 타이밍: `cd cocacola && python3 rec/calc_duration.py` → 717초
- 자막추출: `python3 rec/extract_lines.py`
- 파이프라인 골든(회귀 기준): `blog/pipeline/out/KO/golden/`

> 상세 제작 방법은 `blog/JNJ/HANDOVER.md`(코카콜라 방식 그대로) 참고.
