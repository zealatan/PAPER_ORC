# MCD (맥도날드) 배당 백테스트 영상 — 세션 인수인계

> **이 문서가 진입점.** 맥도날드(MCD) 배당 백테스트 롱폼+쇼츠 제작 건.
> **먼저 `blog/PRODUCTION_MANUAL.md`를 정독**하라 — 코카콜라·JNJ로 검증된 전 파이프라인·함정·명령어가 거기 있다. 이 문서는 MCD 고유 상태·해야 할 일만 담는다.
> **기준 구현체 = `blog/JNJ/`**(가장 정제됨). 막히면 JNJ의 해당 파일과 대조.

## 현재 상태 (스캐폴딩 완료, 2026-07-23)
JNJ를 복제해 **재사용 파이프라인만** 옮겨놓음(`jnj→mcd`, `JNJ→MCD` 치환, 15개 스크립트 컴파일 통과). 종목별 데이터·산출물은 **미생성**(MCD용으로 새로 돌려야 함).

**복사됨(그대로 쓰면 됨):**
- `spec/`: fetch_data.py(티커=MCD) · gen_backtest.py · gen_strategy.py(XIRR 포함) · gen_story.py · spec.py
- `deck/`: **mcd_final.html**(엔진, JNJ 개선 전부 상속 — 타이틀 네모박스·글자크기 LOCKED·fire 끝라벨·hbars2 정직분해·자막 nowrap) · build_deck.py · build_dubbed.py · preview.html · tools/ko_smart_vs_steady.py · bg/*.mp4(6종)
- `rec/`: gen_tts · build_timing · build_voice · render_pw · gen_hook · mix_audio.sh · build_short_v2.sh · keep_fs · send_key · nav_raise
- `fonts/BlackHanSans` · `assets/shorts/batusil.png` · `assets/sfx/notice_beep.mp3`
- 빈 디렉토리: data/ tts/ recordings/ curation/

**API 키**: `blog/.eleven_key`(부모 폴더) 자동 참조(gen_tts fallback `../.eleven_key`). MCD로 복사 불필요.

## ⚠ 반드시 손봐야 할 MCD 고유 항목 (수동 슬롯)
1. **대본 전면 재작성** — `spec/gen_story.py`의 나레이션이 **아직 JNJ 내용**(존슨앤드존슨·배당왕 64년·탈크 소송·오타바 로봇 등). MCD로 완전히 새로 써야 함. 구조(21씬 3부)·`man()` 헬퍼·숫자 자동인용은 유지. checks(최신뉴스)·herostat(정체성)·kpirow(사업)·divbars(배당연수)의 **팩트는 B단계 리서치로 채움**.
2. **MCD 로고** — 엔진 MEDIA `{{mcd}}` 토큰이 현재 **JNJ 빨간 로고 이미지**를 가리킴(키만 mcd로 바뀜). 맥도날드 골든아치 로고 SVG(`assets/mcd_logo.svg`) 만들어 교체. 쇼츠 훅(gen_hook.py)·썸네일도 이 로고 사용 → `assets/shorts/mcd_logo.png`(chromium 투명 래스터화).
3. **배경영상 bg/** — 복사된 6종은 범용(모래시계·새싹·창가 등)이라 대체로 재사용 가능. 단 `lab_research`(제약 연구실)는 MCD엔 안 맞음 → 음식/매장 느낌 클립으로 교체 권장(Pexels, curl_cffi impersonate). build_deck의 BGID 씬 매핑도 조정.
4. **큐레이션/리서치(B)** — `curation/MCD.yaml`·`assets/MCD_NEWS.md` 신규. **결정론 소스 없음** → deep-research로 출처와 함께: 연속 배당 증액 연수(MCD는 배당귀족, 2024 기준 48년+ — 재확인), payout, 사업(프랜차이즈·부동산 모델), 최근 실적, 시총, 배당수익률.
5. **썸네일** — `thumbnail-designer` 에이전트에 위임(레퍼런스 `blog/assets/thumb_references/`). MCD 대표 제품=빅맥·감자튀김·골든아치. 헤드라인 숫자는 백테스트 인용.

## 제작 순서 (PRODUCTION_MANUAL §1·§8 참조)
```
python3 spec/fetch_data.py     # MCD 주가·배당 CSV (yfinance)
python3 spec/gen_backtest.py   # FIRE 그리드
python3 spec/gen_strategy.py   # 폭락 vs 적립 + XIRR
# ── B 리서치(curation/MCD.yaml) → C gen_story.py 대본 전면 재작성 ──
python3 spec/gen_story.py
python3 deck/build_deck.py     # → mcd_v1.html + mcd_deck.json
# narration_lines 재생성(매뉴얼 §1 스니펫, 경로 mcd) → gen_tts → build_timing → build_voice → build_dubbed
python3 rec/render_pw.py       # 롱폼 렌더 → 트림(blackdetect) → mix_audio.sh → longform_final.mp4
# gen_hook.py(MCD 문구) → build_short_v2.sh ×2 → 썸네일 → 유튜브 메타
```

## MCD 콘텐츠 각도 (아이디어)
- **정체성**: 배당귀족(수십 년 연속 증배) + 실제로는 "부동산 회사"라 불리는 프랜차이즈 모델.
- **후킹**: 같은 은퇴자금·같은 MCD, 매달 쓰는 돈만 달랐던 두 사람(JNJ와 동일 구조).
- **고유 팩트**: 프랜차이즈 로열티·리스 수익, 글로벌 매장 수, 물가상승기 방어력(외식 저가 포지셔닝).
- 숫자는 전부 backtest/리서치 인용. 지어내기 금지(매뉴얼 원칙).

## 표준(다음 제작부터 적용, 이미 상속됨) — PRODUCTION_MANUAL §9
- 덱 타이틀 = 자막처럼 네모박스(적응형). 글자크기 LOCKED(타이틀 3.45cqw 등, 변경금지). 썸네일은 thumbnail-designer 에이전트.
- **쇼츠 구도 하향**: build_short_v2.sh VF = 그래프 offset `(oh-ih)/2+170`, 훅 `y=400`, 워터마크 `y=1650`(중앙 정렬, 위 쏠림 해소). MCD 사본에 반영됨.
- **배투실 마스코트 얼굴 채움**: `assets/shorts/batusil.png`가 살구빛 채운 버전으로 교체됨(윤곽선만 아님). MCD 사본에 반영됨.

## 검증
- 덱은 playwright headless firefox로 전수조사(매뉴얼 §4). 렌더도 firefox(H.264 bg 때문). 
- **논쟁적 수치(전략 비교·수익률)는 멀티에이전트 워크플로우로 적대 검증**(매뉴얼 §7, JNJ hbars2 사례).
