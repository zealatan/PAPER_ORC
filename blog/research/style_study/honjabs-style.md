# 혼잡스 그림체 학습 — 클린 웹툰 라인아트 재현 레시피

> 벤치마킹 대상: 유튜브 채널 **혼잡스**(구독 7.8만). 43편 썸네일 코퍼스 분석 → Flux 재현 프롬프트 확정.
> ⚠ 원저작 이미지는 `corpus/`에 분석·학습용으로만 보관. 우리 재현물은 `proof/`.

## 1. 그림체 해부 (43편에서 추출)
혼잡스 화풍 = **순수 흑백 한국 웹툰(네이버웹툰) 라인아트**. 우리 기존 `animation_style/illustration_bible.md`(따뜻한 세피아·크로스해칭·스토리북·노인 캐리커처)와 **정반대 결**이다.

| 항목 | 혼잡스 |
|---|---|
| 라인 | 얇고 균일한 검정 아웃라인, 벡터 느낌(깔끔) |
| 톤 | 순수 흑백. 그라디언트·크로스해칭 **없음**. 내부 음영 최소 |
| 배경 | 순백(pure white) |
| 머리 | 꽉 찬 검정 덩어리 + 흰 틈새 스트로크 몇 개 |
| 의상 | 흰 셔츠(선만) + **솔리드 검정 넥타이**(살짝 풀림), 가끔 니트베스트 |
| 얼굴 | 납작한 웹툰 얼굴, 단순한 이목구비. 표정으로 감정 판매(무표정/놀람/걱정/생각) |
| 구도 | 상반신 3/4, **인물은 우측 / 좌측은 텍스트 여백** |
| 액센트 컬러 | 극소량만(클로드 주황·카톡 노랑·구글·빨강 강조어). 나머지 무채색 |
| 부속(합성) | 우상단 바코드 그래픽 · 하단 미니 스팟 일러스트(절규·자는 사람·폰·고양이·당근·컨베이어) · 손글씨 주석 |

## 2. 재현 레시피 (ComfyUI Flux · flux1-schnell-fp8)
`gen_honjabs_style.py` 로 재현. 기존 파이프라인과 동일 엔진, **STYLE 프리픽스만 교체**.

**STYLE (고정 프리픽스)**
```
Clean minimalist Korean webtoon manhwa line art illustration, thin uniform confident black ink
outlines, flat pure black and white, no cross-hatching, no gradient, no color, minimal interior
shading, solid black hair mass with a few white gap strokes, simple expressive caricature face,
high contrast, pure white background, vector-like clean linework, editorial thumbnail illustration.
```
**CHAR (혼잡스 남자 · 고정 캐릭터)**
```
A young Korean office worker man in his early 30s, neat short black hair, wearing a crisp white
dress shirt with a loosened dark necktie, clean shaven, simple facial features, upper body
three-quarter view.
```
**파라미터**: 1280×720 · steps 4 · cfg 1.0 · euler/simple · denoise 1.0 (기존과 동일)
**포즈별 고정 시드**(검증 완료): 무표정 `101` · 놀람(뺨에 손) `202` · 생각(턱 괴기) `303`
**구도 지시**: scene 끝에 `empty space on the left for text` 를 붙이면 혼잡스식 좌측 텍스트 여백 확보.

## 3. 검증 결과 (proof/)
- `honstyle_neutral.png` (seed 101) — **최상 매치**. 인물 우측·좌측 여백·솔리드 검정 넥타이·검정 머리 덩어리까지 혼잡스 레이아웃 그대로.
- `honstyle_shock.png` (seed 202) — 놀란 표정(입 벌림) 재현. 넥타이가 회색으로 빠질 때 있음.
- `honstyle_think.png` (seed 303) — 턱 괴는 생각 포즈. 은퇴/고민 주제에 적합.

## 4. 타깃과의 갭 & 튜닝 노트 (다음 반복에서 좁힐 것)
- **얼굴이 살짝 '서구 애니(디즈니)' 톤** → 혼잡스는 더 납작. 보강 토큰: `flat 2D face, minimal nose, simple dot eyes, Naver webtoon style, no rendering`.
- **넥타이 회색화** 방지 → `solid black necktie` 강조 or 후처리에서 검정 채움.
- **머리 스파이크 과함** → `neat tidy hair, smooth hair silhouette`.
- **바코드·스팟일러·손글씨 주석은 생성하지 말고 PIL 합성**(혼잡스도 텍스트/그래픽은 별도 레이어) — 썸네일 합성 단계에서 추가.

## 5. 이 스타일을 언제 쓰나
- 혼잡스식 **정보성·재테크 썸네일/인서트**. 클린·모던·고대비 → 피드에서 텍스트 가독성 최상.
- 기존 세피아 스토리북(warm)과 **투 트랙**: 감성·서사=세피아 / 정보·후킹=클린 웹툰.
- 승격 시 `blog/animation_style/`에 STYLE 변형(`STYLE_WEBTOON`)으로 편입 가능.

## 6. 다음 단계 옵션
- (a) **프롬프트 튜닝 반복** — 위 갭 토큰 적용해 얼굴을 더 웹툰화(즉시 가능).
- (b) **LoRA 학습** — `corpus/` 43장으로 Flux LoRA 파인튜닝하면 얼굴·라인까지 혼잡스에 근접(트레이너 세팅 필요, 별도 작업).
- (c) **썸네일 합성 파이프라인 연결** — 이 캐릭터 베이스 + 3단 텍스트 + 바코드/스팟일러 합성으로 완성 썸네일.
