# PG (프록터 앤 갬블) 배당 백테스트 영상 — 세션 인수인계

> **이 문서가 다음 세션 진입점.** P&G(PG) 배당 백테스트 롱폼+쇼츠 제작 건.
> **먼저 `blog/PRODUCTION_MANUAL.md` 정독** — 코카콜라·JNJ·MCD로 검증된 전 파이프라인·함정·명령어.
> **완성 기준 구현체 = `blog/MCD/`** (직전 완결작, 유튜브 업로드 완료). 막히면 MCD의 해당 파일·`MCD/HANDOVER.md`와 대조.

> ❄️ **은퇴 시나리오 쇼츠 = 확정(FROZEN)**, 2026-07-28. 정본: **`blog/PG/golden_shorts_fire/`**
> (생성기 `golden_shorts_fire.py` + 빌드 `build_golden_shorts_fire.py` + 상세스펙 `golden_shorts_fire.md` + 에셋).
> x축 이동 애니·팔레트A·18px 통일. 재현 `python3 build_golden_shorts_fire.py`. **이 종류 쇼츠는 이 스펙 기준.**

## 현재 상태 (2026-07-24 · 스캐폴딩 + A단계 완료)
**PG 폴더 스캐폴딩 완료** — MCD에서 재사용 파이프라인만 선별 복사(`mcd→pg`·`MCD→PG` 치환, **base64 무결성 유지**, 전 스크립트 컴파일 OK). `deck/tools/gen_dec_edit.py`는 폴더명에서 STOCK=PG 자동인식.

**A단계(데이터·백테스트·전략) 완료 — 실측 PG 숫자:**
- 데이터: 2000-2026, 배당 107건, 연배당 $0.67(2000) → $4.18(2025) · 종가 $26.81~$179.70
- 파산 시뮬: 생존 15/18, 최대 평가액 $3.15M
- 전략: **적립 재투자 $994,925 > 폭락매수 $830,354 (−16.5%, 현금 47% 놀았음)** — MCD와 같은 "적립 승" 서사
- 산출물: `data/pg_price.csv`·`pg_div.csv`, `spec/PG.json`(data + backtest.fire + strategy_compare 채워짐)

## ⚠️ PG에서 반드시 복원할 것 (MCD에서 축소된 그래프 회귀 — PG가 그 "다음 종목")
MCD fire 차트에서 두 요소가 축소됐음. **PG부터 복원.** 시각 기준 = `blog/JNJ/deck/jnj_v1.html`(범례·물가테이블 올바른 렌더).
1. **범례** — `deck/build_deck.py` fire 차트 반환부의 `"noLegend": True` **삭제** → 색 범례(🔵월$1천 🟠월$2천 🔴월$3천) 복원. series엔 이미 `name` 있음, 엔진 수정 불필요.
2. **물가연동 인출액 테이블** — `if init == 200000: d["table"] = infl_table` → **모든 fire(real/real2002) 차트에 부착**하도록 조건 확대. `infl_table` 생성코드·엔진 `.engtable`는 이미 있음(재사용).

## 남은 단계 (B~G) — 명령어
```
# ── B 리서치 (deep-research) — PG는 소비재 배당왕. curation/PG.yaml + spec.data.business 채우기 ──
#    필요 팩트(출처 필수): 연속 배당증액 연수(배당왕 ~68년? 재확인)·payout·사업모델(생활용품 브랜드 포트폴리오)·
#    시총·배당수익률·최근 실적. deep-research로.
# ── C 대본 ──
python3 spec/gen_story.py          # ⚠ 아직 MCD 서사 → PG로 전면 재작성(구조·헬퍼·숫자 자동인용 유지)
# ── D 덱 ──  (★ 위 그래프 회귀 복원 먼저!)
python3 deck/build_deck.py         # → deck/pg_v1.html + deck/pg_deck.json
python3 deck/tools/gen_dec_edit.py # → architecture_docs/PG/ 편집 UI 생성(+루트 인덱스에 PG 카드 자동추가)
# narration_lines 재생성(매뉴얼 §1, 경로 pg) → gen_tts → build_timing → build_voice → build_dubbed
# ── E~G ──
python3 rec/render_pw.py           # 롱폼 렌더 → 트림(blackdetect) → mix_audio.sh → recordings/longform_final.mp4
# gen_hook.py(PG 문구) → build_short_v2.sh ×2 → 썸네일(thumbnail-designer) → 유튜브 메타
```

## ⚠ PG 고유 수동 슬롯 (반드시 손봐야)
1. **대본** — `spec/gen_story.py` 나레이션이 **아직 MCD 내용**(맥도날드·49년 배당귀족·부동산 프랜차이즈 등). PG 서사로 완전 재작성. 구조(막·씬·헬퍼)는 유지.
2. **비즈니스 팩트** — `spec/PG.json`의 `data.business`가 **플레이스홀더**(`div_years=null`, `_source`에 TODO). B 리서치로 실측 채움.
3. **로고** — 엔진 `MEDIA["pg"]`가 아직 **MCD 골든아치 이미지**. P&G 로고 SVG 만들어 교체(`assets/pg_logo`, `assets/shorts/pg_logo.png`). gen_hook·썸네일도 이 로고.
4. **배경영상** — `deck/bg/pg_*.mp4`가 아직 **MCD 음식/매장 영상**(파일명만 pg_). PG(생활용품·가정·마트) 클립으로 교체(Pexels, curl_cffi impersonate). build_deck CHAPBG 매핑 조정.
5. **큐레이션** — `curation/PG.yaml`·`assets/PG_NEWS.md` 신규(B에서).

## 🛠 편집 시스템 (MCD에서 상속 — 다음 세션에서 바로 사용) ★파이프라인 HTML
파이프라인 편집 UI는 **종목별**. **PG 편집 UI는 D단계(build_deck) 후 `gen_dec_edit.py` 실행하면 생성**된다(지금은 PG 덱이 없어 아직 없음 — 정상).
```
# 서버(이걸로 띄워야 저장·반영 됨 · 세션마다 재실행. 정적 http.server ✗):
cd ~/PAPER_ORC/blog && python3 pipeline/edit_server.py 8090
# 접속:
http://localhost:8090/architecture_docs/dec_pipeline.html     ← 종목 선택 인덱스
    · MCD 편집:   architecture_docs/MCD/dec_pipeline.html      (완성됨, 참고용)
    · PG 편집:    architecture_docs/PG/dec_pipeline.html       (PG 덱 빌드 후 생성)
    · 허브+스테이지 편집: architecture_docs/top_pipeline_standalone.html
```
- 편집화면: 💾 저장(영구)→소스 JSON+자동 재굽기 · 🔄 최신본(localStorage 비우고 리로드) · 🚀 덱에 반영(구조 재정렬/추가/삭제)
- **데이터 3계층 함정**: JSON(소스)=원본 · HTML=빌드 스냅샷 · localStorage=브라우저 임시본. `if(!localStorage)` → localStorage가 이김 → 새 버전 안 보이면 🔄 최신본. **상세는 `MCD/HANDOVER.md`의 "🛠 덱 편집 시스템" 섹션 참조.**
- 관련 스크립트: `pipeline/edit_server.py`(저장 API) · `pipeline/inject_stage_editor.py`(top_pipeline 스테이지 편집 주입).

## 표준 (MCD에서 이미 상속됨 — 그대로 씀)
- **쇼츠**(build_short_v2.sh): 슬라이드 우상단 배투실은 **종이패치**로 제거(크롭 금지=숫자/자막 보존), 훅 로고=배지 상단, 하단 워터마크=`batusil_label.png`(마크+글자). 상세 `MCD/HANDOVER.md` 표준 섹션.
- 덱 타이틀 글자크기 LOCKED, 배투실 마스코트 베이지 얼굴, 자막 nowrap 등.

## 검증
- 덱은 playwright headless firefox 전수조사(매뉴얼 §4). 렌더도 firefox(H.264 bg).
- 논쟁적 수치(전략 비교·수익률)는 멀티에이전트 적대 검증(매뉴얼 §7).
