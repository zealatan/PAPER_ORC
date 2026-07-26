# 배투실 롱폼+쇼츠 제작 실전 매뉴얼

> 코카콜라(공개)·JNJ 두 편을 실제로 만들며 검증한 **지금 되는(as-built)** 노하우.
> `pipeline/README.md`(=`JNJ/PROTOCOL.md`)는 "종목만 바꾸면 찍히는 라인"의 *설계 청사진*(대부분 stub).
> **이 문서는 그 청사진이 아니라, 실제로 손으로 돌리는 워크플로우와 함정 모음이다.**
> 기준 구현체 = `blog/JNJ/`(가장 정제됨). 새 종목은 JNJ를 복제해 시작하는 게 가장 빠르다.

**최상위 원칙: 데이터는 엔진 · 대본은 인용 · QA는 대조.** 금융 콘텐츠라 정확성이 1순위. LLM이 숫자를 지어내지 못하게 막는 게 존재 이유. 논쟁적 수치(전략 비교 등)는 **멀티에이전트 워크플로우로 적대 검증**한다(§7).

---

## 0. 산출물
- **롱폼** ~3분 (배당 백테스트, 21씬 3부 구성) → `recordings/longform_final.mp4`
- **쇼츠 2편** 9:16 세로 (그래프 위주, 롱폼에서 구간 컷) → `recordings/jnj_short_{fire,strat}.mp4`
- **썸네일** 롱폼 가로(16:9) + 쇼츠 세로(9:16)
- **유튜브 업로드 메타**(제목·설명·타임스탬프·해시태그)

콘텐츠 구조(코카콜라 공개 후 학습): **백테스트 중심 3부**. ①후킹(같은 돈, 다른 운명) ②파산 시나리오(FIRE: 원금×인출액별 생존/파산, 물가반영) ③매수 방법(폭락 타이밍 vs 매달 적립). 회사소개는 최소화(훅↔반전 사이 2씬).

---

## 1. 파이프라인 A~G (실제 스크립트·순서)

| 단계 | 산출 | 스크립트(JNJ 기준) |
|---|---|---|
| **A 데이터·백테스트** | spec/JNJ.json 채움 | `spec/fetch_data.py` · `spec/gen_backtest.py`(FIRE 그리드) · `spec/gen_strategy.py`(전략 비교+XIRR) |
| **B 리서치** | 큐레이션 사실+출처 | deep-research 워크플로우 → `curation/JNJ.yaml`·`assets/JNJ_NEWS.md` |
| **C 대본** | 나레이션+씬 | `spec/gen_story.py` → `narration_draft.json`·`SCRIPT.md`(숫자는 backtest 자동인용=지어내기 차단) |
| **D 덱** | 자립형 HTML | `deck/build_deck.py` → `deck/jnj_v1.html`+`jnj_deck.json` |
| **E 더빙** | 음성+타이밍 | `rec/gen_tts.py`→`build_timing.py`→`build_voice.py`, `deck/build_dubbed.py` |
| **F 렌더** | 롱폼 mp4 | `rec/render_pw.py`(playwright)→트림→`rec/mix_audio.sh` |
| **G 썸네일·쇼츠** | 썸네일+쇼츠2 | 썸네일 PIL · `rec/gen_hook.py`+`rec/build_short_v2.sh` |

### 새 종목 end-to-end 명령 순서(더빙 텍스트 바뀔 때 전체)
```bash
python3 spec/fetch_data.py           # yfinance → data/*.csv
python3 spec/gen_backtest.py         # FIRE 시나리오 → spec.json
python3 spec/gen_strategy.py         # 전략 비교+XIRR → spec.json
python3 spec/gen_story.py            # 대본 → narration_draft.json
python3 deck/build_deck.py           # 덱 → jnj_v1.html + jnj_deck.json
# narration_lines.json 재생성(아래 스니펫) → gen_tts → build_timing → build_voice
python3 rec/gen_tts.py               # TTS(변경분만, raw 보존→재-atempo 무료)
python3 rec/build_timing.py          # subTimes/subHold + voice_timeline
python3 rec/build_voice.py           # voice_track.wav (+ 1페이지 beep)
python3 deck/build_dubbed.py         # jnj_dubbed.html (KEY=tplCatalog_jnj_dubbed)
python3 rec/render_pw.py             # 롱폼 녹화(webm) — 아래 F 참고
# 트림+믹싱 → longform_final.mp4, 그다음 쇼츠 컷
```
narration_lines.json 재생성(코카콜라 extract_lines.py는 경로 하드코딩이라 JNJ는 인라인):
```python
import json; d=json.load(open('deck/jnj_deck.json',encoding='utf-8'))
out=[{'scene':i,'tpl':s.get('tpl'),'lines':s.get('subLines') or []} for i,s in enumerate(d['scenes'])]
json.dump(out, open('rec/narration_lines.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
```

---

## 2. 재사용 자산 (종목무관)
- **백테스트 엔진**: `global_cup_suite/global_cup/{fire_engine,golden_engine,backtest_engine}.py`, 전략엔진 `deck/tools/ko_smart_vs_steady.py`(검증됨, 절대 수정 금지 — 조작 의혹 방어의 근거)
- **덱 엔진**: `deck/jnj_final.html`(3.2MB 렌더러, 씬 JSON을 읽어 TPL로 렌더). cocacola_final.html에서 파생.
- **더빙/렌더 헬퍼**: `rec/{gen_tts,build_timing,build_voice}.py`, `rec/render_pw.py`, `rec/mix_audio.sh`, `rec/{keep_fs,send_key,nav_raise}.py`(x11grab용, 지금은 playwright라 거의 불필요)
- **폰트**: `fonts/BlackHanSans-Regular.ttf`(썸네일·훅 굵은 한글)
- **마스코트/로고**: `assets/shorts/batusil.png`(덱 BATUSIL data URI에서 추출), `assets/jnj_logo.svg`
- **쇼츠 썸네일 편집기(정식 템플릿)**: `blog/prototypes/thumbs/thumb_editor.html` — 자립형·오프라인·모바일 터치. 요소(제품그룹·배투실 마크·P&G/맥도날드/J&J 로고·텍스트박스)를 드래그·크기(cqw)·색상·외곽선 편집. 🖼임포트(폰 갤러리 임의 이미지)·📐가이드(모눈+가로세로 중심선, **PNG엔 미포함**)·💾PNG(1080×1920 캔버스 직접 렌더, 라이브러리 無)·💾HTML(현재 상태 자립형 저장→다시 열어 재편집). 종목 무관 재사용. 게시판: `thumb_editor_artifact.html`(claude.ai 아티팩트용, head/body 스켈레톤 대응). 제품컷 자산 `assets/products*/`, 손글씨 라벨=Caveat 폰트.

---

## 3. ⚠ 핵심 함정 (hard-won, 반드시 숙지)

### 덱(D)
- **cocacola 패치 IIFE 4종**(v8-hook/revert1/survheat1/src1, `jnj_final.html` ~1795–1889)이 로드 시 SCENES를 코카콜라로 덮어씀. build_deck이 `/* FIRE 세트` ~ src1 `})();` 블록을 통째 제거하고 `if(!localStorage.getItem(KEY)){SCENES=...;OV={};CP={}}` 주입. KEY=`tplCatalog_jnj_v2`.
- **편집 지속성**: HUD 편집은 localStorage에 저장 → 재빌드해도 새로고침 후 유지. 트레이드오프: 저장본 있으면 코드 재빌드가 안 보임. 구조 변경 시 localStorage 비우거나 KEY 교체.
- **제목 크기 마스터**: `.btitle{font-size:2em !important}`(~1537) 가 모든 슬라이드 제목 지배. 여기 하나로 통제.
- **차트 애니메이션**: 선은 stroke 드로잉(`--d` 지연 최대 ~3.2s). **playwright 캡처 전 5.5s 대기 필수.**
- **fire 차트 범례 겹침**: 떠다니는 고정 범례는 선/기준선라벨과 필연 충돌 → **범례 제거(`noLegend:true`) + 각 선 끝에 '월 $X' 라벨**(선에 부착돼 충돌 불가). 기준선 라벨은 끝라벨 회피 위해 후보 x에서 우측끝(0.8+) 제외.
- **hbars2 정직 분해(§7 사례)**: 폭락매수는 실투입만 표기(319k 전액 아님) — 실투입/자본이득/배당/유휴현금(빗금) 4단, 우측 적립은 전액. XIRR 병기.

### 자막
- **`#subbar`는 `left:50%;width:fit-content;max-width:94cqw;white-space:nowrap;display:block`**. `display:flex`는 fit-content를 깨뜨려 조기 줄바꿈 → **flex 금지**. `white-space:nowrap`으로 무조건 1줄. 유연 알약형(로고 `border-radius`).
- **본문과 절대 안 겹침**: solostory accent 배지·card 칩이 자막 위에 붙는 케이스 → 자막 bottom 2.4cqw로 내리고 1줄 유지로 해결.
- 전수조사 방법(§6).

### 더빙(E)
- ElevenLabs `eleven_v3`, voice_id=`Iu0W7wMhBwV2Qjzj0Fp2`("메시" 클론). **previous/next_text 미지원** → 속도는 ffmpeg `atempo`.
- **raw .mp3 보존이 핵심**: 재-atempo(속도 변경)는 raw에서 재처리라 **API 무료**. 속도 바꾸려면 tts/의 sped mp3만 지우고(raw 유지) `TTS_SPEED` 바꿔 gen_tts 재실행. 텍스트 바뀐 클립만 raw+sped 둘 다 지워야 재API.
- 현재 속도 `SPEED=1.062`(초기 1.18에서 10% 감속). 자막 속도는 subHold가 클립 길이에서 파생돼 자동 연동.
- **1페이지(씬0) 무더빙**: gen_story 씬0 `lines:[]` → 자막·TTS 없음. build_voice가 `assets/sfx/notice_beep.mp3`를 t=250ms에 배치.
- 키 파일 `blog/.eleven_key`(gitignore, 절대 커밋·노출 금지).

### 렌더(F) — ★가장 중요한 전환
- **playwright headless firefox `record_video`를 쓴다(x11grab 아님).** 이유: display :1을 점유·풀스크린 취약한 x11grab 대신, headless라 안전·결정적. 1920×1080, ~25fps webm, `?rec` 풀블리드(크롬·HUD 없음). 폰 시청 쇼츠엔 25fps 충분. (진짜 60fps 필요 시에만 `rec/record_full.sh` x11grab.)
- **오디오 정밀 정렬 = 블랙 마커 기법**: `render_pw.py`가 씬0 시작 직전 검은 오버레이(~0.9s) 삽입 → `ffmpeg blackdetect`로 `black_end`(=씬0 시작) 찾아 그 지점부터 트림. `video ≈ deck_time − 0.13`.
- **헤드리스 크롬은 H.264 배경영상 못 디코드(검게 렌더)** → 렌더·캡처는 **firefox**로. (SVG 로고 래스터화만 chromium: firefox headless는 `omit_background` 투명 스크린샷 미지원.)
- 렌더 후: 트림+h264 인코딩 → `rec/mix_audio.sh`(voice loudnorm −16 LUFS) → `longform_final.mp4`. DUR는 `render_pw.py`가 jnj_deck_dubbed.json subHold 합으로 자동 계산.

### 쇼츠(G)
- **포맷(코카콜라 복제)**: 9:16 캔버스 = **검정 배경**(초기엔 블러였으나 검정으로) + 가운데 16:9 원본 + 상단 훅(로고+2행 문구) + 하단 배투실 워터마크. **첫 1초 = 롱폼 마지막 카드 페이지**(브랜딩). 대사 씬 빼고 **그래프 씬만**.
- `rec/build_short_v2.sh <src> <graph_start> <graph_dur> <hook.png> <out>`: 카드 1초 무음 인트로 + 그래프 구간 concat. VF는 pad(검정)+overlay.
- 훅 PNG `rec/gen_hook.py`(PIL+BlackHanSans): 상단 JNJ 로고(빨간 script, 글로우) + 1행 흰색 외곽선 + 2행 노란 하이라이트박스. 로고 밑 공백 최소·그래프까지 위로 붙임.
- 씬 시간대는 jnj_deck_dubbed.json subHold 누적으로 계산(§6 스니펫).
- **주의**: 전략 쇼츠는 hbars2(비교 차트) 포함 → 그 데이터 바뀌면 롱폼 재렌더 후 재컷. 파산 쇼츠는 fire 차트만이라 독립.

### 썸네일
- 롱폼 가로: **덱 bg 영상 프레임을 배경**으로(예 `hourglass_time`=시간/은퇴자금 소진 메타포) 어둡게+그라디언트 스크림 → JNJ 로고 + 큰 헤드라인(흰+노란 하이라이트) + 마스코트. PIL 합성(`assets/thumb_hourglass.png` 참고).
- 노부부·돈다발 AI합성은 선택(코카콜라 `recordings/recordings/thumb_final.png`). 손그림 일러스트 버전은 `thumb_illust_v1.png`.
- 쇼츠 세로(9:16): **정식 도구 = `blog/prototypes/thumbs/thumb_editor.html`** (§2). 검은 배경 위 제품컷(흰테두리)+필기체 라벨(Caveat)+로고+큰 문구(dihichi식). 요소 드래그·리사이즈 후 **💾PNG로 1080×1920 저장**. 종목 무관(로고·제품 임포트). 대안: 마지막 카드 페이지 세로 프레임(`assets/shorts/thumb_card.png`). 쇼츠 썸네일 지정은 **YouTube 모바일 앱에서만** 가능.

---

## 4. 검증 인프라 (playwright)
- **전수조사/캡처**: headless firefox, `firefox_user_prefs={media.autoplay.default:0}`. 씬 이동 = jnj_v1.html 로드 → `#btoggle`(일시정지) → `#bprev`×25(씬0) → `#bnext`로 목표 → **5.5s 대기(애니 완료)** → 자막 주입 → 스크린샷.
- ⚠ `?rec`에서만 Home 키 재시작 동작. 비-rec은 auto재생이라 한 씬 밀림 주의.
- 덱 메인스크립트가 IIFE라 `contentWindow.show` 접근 불가 → 외부 제어는 **Home 키 디스패치** 또는 HUD 버튼 클릭.

---

## 5. LAN 프리뷰 (DGX 오디오출력 없음)
```bash
python3 -m http.server 8080 --bind 0.0.0.0   # blog/JNJ/ 에서
```
`deck/preview.html` = jnj_dubbed.html?rec iframe + voice_track.mp3 동기재생(재생 버튼 클릭 시 Home 디스패치로 씬0 정렬). URL 예: `http://<box-ip>:8080/deck/preview.html`. 완성 mp4도 `http://<box-ip>:8080/recordings/*.mp4`로 다운로드.

---

## 6. 유튜브 업로드 포맷 (코카콜라 검증)
설명 = **상단 해시태그 3개 → 스토리형 후킹 2줄 → "직접 만든 백테스트 앱으로…" 방법 문장 → 고유 앵글 티저 → ⏱ 타임스탬프 → 하단 전체 해시태그**. 타임스탬프 첫 챕터 0:00, 3개 이상(자동 챕터 활성). 실제 씬 시각으로 검증(subHold 누적). 예시는 `JNJ/assets/YOUTUBE_UPLOAD.md`.
쇼츠: 제목에 `#shorts`, 설명 짧게+해시태그. 쇼츠→롱폼 상호 링크 추천.

---

## 7. 데이터 정확성 = 멀티에이전트 적대 검증 (사례)
JNJ hbars2 '원금 오표기' 사건: 폭락매수 원금을 $319k(전액)로 그렸으나 실제 실투입은 $119k, 나머지 $273k는 유휴현금 → 씬15와 모순. 사용자 제보 + "metric도 CAGR/XIRR 아니냐" → **Workflow(7에이전트: 엔진의미·지표계산·씬일관성 → 종합판정 → 적대검증 3/3 confirmed)**로 확정: 결론(적립 승)은 절대금액·XIRR(10.0%>9.2%) 모두 유지, CAGR은 정기적립엔 정의불가 → XIRR이 정답. 수정: 막대 정직분해+XIRR 병기+나레이션 보완. **교훈: 비교·수익률 주장은 반드시 엔진 재현+적대검증. CAGR 대신 XIRR(화폐가중).**

---

## 8. 새 종목 시작 체크리스트
1. `blog/JNJ/` 복제 → `blog/<TICKER>/`. 경로·KEY(`tplCatalog_<ticker>_v2`) 치환.
2. A: fetch_data(티커 교체) → gen_backtest → gen_strategy.
3. B: deep-research로 사업개요+출처(결정론 소스 없음 — 큐레이션 필수). 배당 증배 연수·payout·부문매출·시총·수익률.
4. C: gen_story(숫자 인용 자동). 흐름·톤 사용자 확인.
5. D: build_deck → playwright 전수조사(겹침·차트). 배경영상(Pexels, curl_cffi impersonate) 신규 필요.
6. E: narration_lines 재생성 → gen_tts(신규라 전량 API) → timing → voice → build_dubbed.
7. F: render_pw → 트림 → mix → longform_final.
8. G: 훅 PNG(gen_hook, 종목 문구) → build_short_v2 ×2 → 세로/가로 썸네일 → 업로드 메타.
9. 논쟁 수치 있으면 §7 멀티에이전트 검증.

**"종목만 바꾸면"은 데이터·백테스트·덱까지만 참.** bg영상·로고·훅문구·썸네일·큐레이션은 수동 슬롯.

---

## 9. 다음 제작 반영사항 (변경 로그 · 2026-07-23~)
> JNJ 완성 후 확정된 개선. 새 종목은 아래를 기본으로 적용한다. (JNJ 소스 `jnj_final.html`에 이미 반영됨 — 새 종목은 JNJ 복제라 자동 상속.)

1. **썸네일 담당 에이전트** — `thumbnail-designer`(`~/PAPER_ORC/.claude/agents/thumbnail-designer.md`). 썸네일 작업은 이 에이전트에 위임(Agent tool, subagent_type: thumbnail-designer). 승인 레퍼런스는 **`blog/assets/thumb_references/`**(coca_thumb_ref·jnj_thumb_ref). 새 승인본 나오면 여기 축적. 스타일=돈다발+대표제품+노부부+빨간로고+찢긴종이 라벨+흰/노랑 대형 헤드라인(§3 썸네일 참조).
2. **타이틀 네모박스(자막과 통일)** — `.btitle`에 알약 박스 적용(jnj_final.html ~1537). 차트 씬=어두운 박스+흰 글씨, bg영상 씬(`.frame.has-bg`)=밝은 박스+어두운 글씨 → 각 씬의 자막과 세트로 보임. 하이라이트 토큰(노란 강조)은 유지됨. 검증: 씬6(bg)·8·17(차트).
3. **글자크기 LOCKED(숫자 고정)** — 전 슬라이드 현재 크기가 최적. 함부로 바꾸지 말 것. 명시값: **타이틀 `.btitle 3.45cqw !important`**(마스터, 전 슬라이드 지배) · **자막 `#subbar 1.9cqw`** · 차트축 `.etick 30px`/`.echart .axlab 2.9cqw` · 끝라벨 세로간격 `eLH 38`. jnj_final.html ~1537에 주석으로 박제.

4. **쇼츠 구도 하향(위 쏠림 해소)** — `rec/build_short_v2.sh` VF에서 모든 요소를 아래로 내려 세로 중앙 정렬. 확정값: 그래프 pad offset `(oh-ih)/2+170`, 훅 overlay `y=400`, 배투실 워터마크 `y=1650`. (이전 −110/120/1470은 상단 쏠림.) JNJ·MCD 둘 다 반영.
5. **배투실 마스코트 얼굴 채움** — 윤곽선만 있던 얼굴 내부를 옅은 살구빛 `(255,240,226)`으로 flood-fill. 방법: alpha>60=그려짐, 모서리에서 flood로 바깥 표시 → 나머지 내부(모든 pocket 포함) 채움. `assets/shorts/batusil.png` 교체(JNJ·MCD). 원본 윤곽선 버전은 덱 BATUSIL data URI에 아직 있음(원하면 덱도 교체 가능).

> ⚠ 2·3·4·5는 JNJ 소스에 반영됨. **이미 업로드된 JNJ 롱폼/쇼츠에 소급 적용하려면 재렌더 필요**(사용자가 원할 때만). 기본은 "다음 제작부터". MCD는 클론이라 자동 상속.

6. **쇼츠 썸네일 HTML 편집기(정식 템플릿, 2026-07-27)** — `blog/prototypes/thumbs/thumb_editor.html`(§2). dihichi 벤치마킹 스타일: 검정 배경·제품컷 흰테두리·필기체 라벨·큰 2줄 문구·빨간 포인트. 드래그·크기(cqw)·색상·외곽선·🖼임포트·📐가이드·💾PNG(1080×1920)·💾HTML(재편집). **종목무관 범용** — P&G·맥도날드·J&J 로고 내장, 임의 이미지 임포트. 아티팩트 게시판 `thumb_editor_artifact.html`. thumbnail-designer 에이전트(#1)와 병행: 에이전트=AI시안, 편집기=수동 배치·미세조정.
7. **reelchart 릴스형 차트(PG 덱)** — 선 성장 + 선끝 값 실시간 카운트업(dihichi식). `pg_final.html` reelchart tpl + `reelAnim()`(기존 countUps 훅에 연결). 파이어 원금 3장·분할투자 2장에 적용, 2002 세트는 deck_plan에서 드롭(sid 안정→자막 보존). 새 종목 이식 시 `build_deck.py` reel_fire/reel_steady/reel_crash + `_nice_ceil` 참고. per-scene y축·흰카드·per 로고.

---

## 10. 리서치·벤치마킹 (`blog/research/`)
다른 채널 영상을 분석해 후킹·구조·썸네일 패턴을 축적. `benchmarks/<slug>.md`(우리 분석 위주, 원저작물 전문 저장 금지) · `thumbs/`(레퍼 썸네일) · `hooks/`(후킹 캡처). 첫 항목: `4uk-fire-sp500.md`(4억 파이어 → S&P500 리메이크, 백테스트 답 확정). 기획 시 여기 훑고, 썸네일 작업 시 thumbnail-designer에 함께 참고시킴.
