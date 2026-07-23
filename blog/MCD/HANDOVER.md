# MCD (맥도날드) 배당 백테스트 영상 — 세션 인수인계

> **이 문서가 진입점.** 맥도날드(MCD) 배당 백테스트 롱폼+쇼츠 제작 건.
> **먼저 `blog/PRODUCTION_MANUAL.md`를 정독**하라 — 코카콜라·JNJ로 검증된 전 파이프라인·함정·명령어가 거기 있다. 이 문서는 MCD 고유 상태·해야 할 일만 담는다.
> **기준 구현체 = `blog/JNJ/`**(가장 정제됨). 막히면 JNJ의 해당 파일과 대조.

## 현재 상태 (덱 초안 완료, 2026-07-23)
**A~D 완료.** 데이터·백테스트·리서치·대본·덱까지 MCD 실측/실팩트로 완성, playwright QA 통과.
- A 데이터/백테스트: `spec/MCD.json` 채움(적립 $2,096,010 XIRR 12.2% > 폭락 $1,275,195 9.2%, −39%)
- B 리서치: `curation/MCD.yaml`(5에이전트 교차검증) → `spec.data.business`
- C 대본: `spec/gen_story.py` MCD 서사로 전면 재작성(배당귀족49년·부동산모델·맥밸류). `narration_draft.json`·`SCRIPT.md`
- D 덱: `deck/build_deck.py` 콘텐츠 MCD화 → `deck/mcd_v1.html`(자립형 ~10MB)
- 로고: **실제 골든아치**(`assets/mcd_logo.svg`, Wikimedia, #FFC72C) → 엔진 MEDIA·투명 PNG 반영
- 배경: MCD 3종 신규(`deck/bg/mcd_{storefront,customer,interior}.mp4`, Pexels 로열티프리) → herostat/checks/card
- **템플릿 다양화 이식 완료(2026-07-23)**: 비차트 씬에 새 TPL 7종 신설(`mcd_final.html` TPL맵+CSS, `build_deck` 실측 데이터 주입) — 그래프는 현 스타일 고수.
  · `stmt`(영수증 A/통장 B, 실잔고 궤적) · `hero`(풀블리드 49년+골든아치) · `menuboard`(임대료/로열티 메뉴판) · `sectint`(2부 레드/3부 그린) · `drivethru`(타이밍) · `stampcard`(적립)
  · 타이틀 박스→골드 밑줄, quotebig=피터 린치 명언.
  · 2002년(닷컴 저점) 은퇴 3씬 추가(fire_X_2002, 엔진 기지원) — "진입 시점 2년이 생사" 교훈. is2002 annoMain은 실측 생존 기반으로 수정(JNJ 하드코딩 "셋 다 파산" 제거 — MCD는 반대로 셋 다 생존).
  · 배경영상 10씬으로 확대(새 TPL 배경을 반투명 rgba 오버레이로 → 영상 은은히 비침, 텍스트 가독성 유지). CHAPBG 10종, 덱 ~12MB. 총 24씬 ~4.5분.
  · 엔진 주의: TPL 콘텐츠는 `.fit`(safe-area, scale .88)로 래핑됨 → 레이아웃은 `.tpl-X>.fit`, 배경은 루트(.zoom)에.
- **남음: E 더빙 · F 렌더 · G 썸네일·쇼츠**

### (이하 스캐폴딩 시점 기록 — 참고용)
JNJ를 복제해 **재사용 파이프라인만** 옮겨놓음(`jnj→mcd`, `JNJ→MCD` 치환, 15개 스크립트 컴파일 통과).

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

---

## 🎨 손그림 일러스트 스타일 (신규 트랙, 2026-07-23) — `blog/research/`
> 크로스-프로덕션 자산(MCD 전용 아님). 경쟁채널 **혼잡스**(부업/AI, 구독 7.8만)의 시그니처 **클린 흑백 웹툰 라인아트**를 우리 로컬 Flux로 재현해, 배당/백테스트 콘텐츠(특히 A/B 두 은퇴자 씬)에 손그림으로 얹는 **선택 트랙**. 기존 AI영상클립+enginechart 표준 프로덕션과 별개 옵션이다. (기존 `blog/animation_style/` 세피아 스토리북과도 다른, 새로운 클린 웹툰 화풍.)

### 위치
- 벤치마킹: `research/benchmarks/honjabs-channel.md` (제목공식·썸네일시스템·퍼널)
- 리버스 스토리보드: `research/storyboards/honjabs-{top1,2,3,rec1,2,3}-sb.html` — 씬별 프레임캡쳐 + 왜통하나(초록)/배당치환(파랑) 분석. 혼잡스 조회TOP3 + 최근3편(AI 피벗).
- 스타일 학습·레시피: `research/style_study/`
  - **`honjabs-style.md`** — 화풍 해부 + Flux 재현 프롬프트/시드 (핵심 진입점)
  - `honjabs-body-illust.md` — 본문 어휘(손·미니피규어·소품·로봇) 카탈로그 + 반자동 파이프라인 제안
  - `gen_honjabs_style.py`·`gen_body_vocab.py`·`gen_sets.py` — 생성기

### 재현 방법 (로컬 생성, 클라우드 API 아님)
- **ComfyUI**(`comfyui` conda env, 127.0.0.1:8188) + **flux1-schnell-fp8**. GPU=GB10(ARM/Blackwell). `python gen_sets.py`로 큐 제출 → `/history`에서 view API로 수거(스크립트에 컬렉터 패턴 있음). GPU 점유 시 느림·큐 꼬이면 `/interrupt`+`/queue {"clear":true}`.
- **STYLE 프리픽스(고정)**: "Clean minimalist Korean webtoon manhwa line art illustration, thin uniform confident black ink outlines, flat pure black and white, no cross-hatching/gradient/color, pure white background, vector-like clean linework, no text."
- **캐릭터 일관성 = 시드 고정**: 채널 캐릭터(안경+니트가디건 중년 투자멘토) = **seed 555**. 동일 시드+동일 인물설명이면 여러 표정도 같은 사람 유지 → **LoRA 불필요**.
- 스팟 아이콘은 CHAR 없이 "... isolated line-art icon centered on white, no text".

### 이미 만든 자산 (`research/style_study/`)
- **`content_sets/` 20장** = Set A 배당은유 8(은퇴자 고민/안도·돈나무·저수지·모래시계·저금통·우상향그래프·월배당캘린더) + Set B 두은퇴자 A/B 스토리 6(대비·소비·재투자·파산·생존·히트맵) + Set C 캐릭터시트 6표정. 라벨시트 `setA/B/C_*.png`.
- `vocab/` 12 = 본문 어휘(가리키기·엄지척·제지·A4/폰/지시봉 든 손·자는사람·군중·발표대·로봇·현금·상점).
- 원본 코퍼스: `corpus/`(썸네일 43)·`body_corpus/`(본문 180)·`lora_dataset/`(정제 33+캡션, LoRA 대비용·현재 미사용).

### 덱에 적용하려면 (MCD/JNJ 공통)
- 덱의 **solostory(A/B) 씬 배경**을 Set B의 A(소비·파산)·B(재투자) 일러스트로 교체 → 손그림 A/B 씬 완성. (현재 배경 bgid=`trader_a`/`sprout_b` AI실사.)
- 새 씬은 `gen_sets.py`에 한 줄(seed·scene) 추가로 무한 생성. 종목별 소품만 교체(MCD=골든아치·감자튀김, JNJ=타이레놀·밴드에이드 등).
- ⚠ **선택 트랙** — 표준 프로덕션(AI영상+차트덱)과 섞을지, 특정 씬만 손그림으로 갈지는 기획 결정 사항.

### 참고: JNJ 덱 현황
- `JNJ/deck/jnj_{final,v1,dubbed}.html` 3개 모두 **아직 코카콜라 내용 100%**(타이틀·36회 언급·A/B 숫자 전부 KO). JNJ/HANDOVER.md에 "개조할 베이스"로 명시된 **의도된 WIP** — content 교체(§JNJ 3-A~D)와 백테스트 JNJ 재실행이 남은 상태. MCD는 이 교체가 완료된 기준 구현체.

