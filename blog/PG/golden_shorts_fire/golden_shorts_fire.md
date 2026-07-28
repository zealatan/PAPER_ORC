# golden_shorts_fire — 은퇴 시나리오 쇼츠 GOLDEN REFERENCE ❄️FROZEN

> **상태: 동결(FROZEN) · 2026-07-28.** 이 문서 + `golden_shorts_fire.py` + `assets/` = **정본**.
> 앞으로 "은퇴 시나리오 쇼츠"는 이 스펙이 기준. 값을 바꿀 땐 반드시 이 문서도 같이 갱신.
> 확정 영상: `golden_shorts_fire.mp4` (1080×1920, 30fps, **6페이지·총 54.6초**).

배투실 PG(프록터 앤 갬블) 배당 백테스트 쇼츠. "5억으로 은퇴하면 매달 얼마까지 써도 안 망하나"를
은퇴원금 5종($200,000~$1,000,000)으로, 월 $1천/$2천/$3천 인출 3선을 **x축 이동
(randomdatavstime 스타일)** 애니메이션으로 보여준다.

---

## 0. 파일 구성 · 재현 방법

```
blog/PG/golden_shorts_fire/
├── golden_shorts_fire.py            # ★영상 생성기: 5개 그래프 HTML 생성(pg_fires.json 기반). import 가능(NEWRA/CMAP/FIRES 노출)
├── build_golden_shorts_fire.py      # 렌더(playwright)+합치기(ffmpeg) → mp4
├── gen_fires.py                     # ★백테스트 엔진 실행(SHORTS_STOCK=PG|QQQ|KTNG) → assets/<stock>_fires.json(원금 5종)
├── gen_golden_shorts_fire_editor.py       # ★편집기 생성기(SHORTS_STOCK 스위치): golden 재사용해 6슬라이드 조립
├── golden_shorts_fire_editor.html         # ★통합 쇼츠 편집기(6슬라이드·golden 반영) — 브라우저로 열어 편집(§11)
├── golden_shorts_fire.md            # 이 문서(정본 스펙)
├── golden_shorts_fire.mp4           # 확정 영상
├── golden_shorts_fire_{1..5}.html   # 영상용 생성물 5장 — 생성기가 덮어씀(gitignore)
└── assets/
    ├── paper.jpg                    # ★그래프 배경 종이 텍스처(밝은 흰색·고운 섬유질, 1400×933)
    ├── paper_b64.txt                # 위 종이의 base64 data URI(카드 background) — paper.jpg에서 생성
    ├── pg_fires.json                # ★PG 파이어 데이터(원금 5종) — gen_fires.py 산출, golden 영상·편집기가 소비
    ├── assets.json                  # 편집기용 제품/배지/로고 base64(PRODUCTS/BADGE/PGLOGO/…)
    ├── ktng_fires.json · qqq_fires.json  # (예시) KT&G·QQQ 백테스트 payload(원금 5종) — gen_fires.py 산출
    └── thumb_mag.png                # PG 마젠타 썸네일 래스터(영상 슬라이드 0)
```
> 종이 텍스처 교체: 새 이미지를 `assets/paper.jpg`(가로 1400 다운스케일)로 저장 → base64로 `paper_b64.txt` 갱신 → 생성기 재실행.

외부 의존(저장소 내 영구):
- 폰트: `blog/fonts/PretendardVariable.woff2` → 런타임 base64 임베드(@font-face)
- 데이터: `assets/pg_fires.json` (gen_fires.py 엔진 산출, 원금 5종). *(pg_deck.json은 롱폼 덱용 별개)*
- 로고·기본 릴CSS: `blog/PG/deck/pg_final.html` (로고 path + 라인 1611:1634 rc_css)

**재현:**
```bash
cd blog/PG/golden_shorts_fire
python3 build_golden_shorts_fire.py     # 그래프 생성→녹화→합성까지 한 번에 → golden_shorts_fire.mp4
# (HTML만 다시 뽑으려면) python3 golden_shorts_fire.py
```
필요: `playwright`(chromium), `ffmpeg`.

---

## 0.5 ★ 제작 파이프라인 (신규 종목 → 편집기)

> **이 golden은 "은퇴 시나리오 쇼츠" 제작 틀이다.** 스펙(요소 위치·크기·색·애니 §1~§4)은 종목 무관 고정,
> **종목별로 바뀌는 입력만 갈아끼우면** 해당 종목용 `golden_shorts_fire_editor.html` 이 나온다.

**입력(INPUT):** ① 종목(티커·기업명) ② 백테스트 시나리오(은퇴원금 **5종** × 월 인출 3종 · 은퇴 시점 · 물가반영 등)
**출력(OUTPUT):** 해당 종목으로 채워진 **`golden_shorts_fire_editor.html`** (썸네일+그래프5 = **6슬라이드**)

| 단계 | 주체 | 내용 | 산출/근거 |
|---|---|---|---|
| **1. 종목·시나리오 확정** | 사람 | 어떤 종목을, 어떤 은퇴원금/인출/은퇴시점으로 돌릴지 결정 | = INPUT |
| **2. 에셋 투입(슬라이드1 썸네일)** | 사람+에이전트 | **썸네일 사진 = 사람**이 찾아 제공(제품/이미지). **기업 로고 = 에이전트**가 찾음(SVG/PNG). 문구도 종목에 맞게. → 편집기 슬라이드1에 배치 | 편집기 슬라이드1(편집가능 요소) |
| **3. 요소 스펙 준수** | 에이전트 | **모든 요소의 크기·위치·색은 이 문서(§1·§2·§3)대로** — 훅 7cqw·마젠타 금액, 로고 y축정렬, 문구 색, 팔레트A 등 | §1~§3 |
| **4. 백테스트→그래프(슬라이드2~6)** | 에이전트 | 시나리오를 **백테스트 엔진(global_cup_suite `run_fire_backtest`)으로 직접 돌려** 데이터 획득 → 그래프 5장에 채움. 여기서도 **모든 요소 스펙(§2·§4)대로**(x축이동 애니·18px·좌측 은퇴원금·범례밖·번호훅·ylabelmin 등) | §4·§5 |

**단계 4 실행 체인(§5 참조):** `SHORTS_STOCK=<종목> python3 gen_fires.py`(엔진 직접 실행·원금 5종 → `assets/<stock>_fires.json`) → 편집기 생성기(`SHORTS_STOCK=<종목>`)가 그 payload를 슬라이드2~6에 주입.
> **데이터는 반드시 엔진에서.** 수치 하드코딩/임의조작 금지. 엔진 출력과 편집기 데이터 일치 검증 권장(§5 무결성 검증 방식).

**종목 교체 시 실제로 바뀌는 것:** 로고·썸네일 사진·문구(2)·해당 종목 백테스트 데이터(4)·기업명 텍스트.
**절대 안 바뀌는 것:** 레이아웃·색 규칙·글자 크기·애니메이션(§1~§4) = 이 golden 스펙.

---

## 1. 캔버스 · 레이아웃 지오메트리

| 요소 | 값 |
|---|---|
| 페이지(body) | 1080 × 1920, 배경 `#000`, overflow hidden, 폰트 Pretendard |
| `.graphbox` | `left:0;right:0; top:50%; translateY(-50%)`, **aspect 1.78/1**, `container-type:size` → 폭 1080 · 높이 **606.7px**, 세로 중앙. **1cqw = 10.8px** |
| `.hook`(상단 훅) | body 자식. `top:20%`(≈384px), 가로 중앙 정렬 |
| `.legout`(범례) | body 자식. `top:28%`(≈538px), flex 가로 중앙 |
| `.rc-card`(차트 카드) | graphbox 안 **풀블리드**(`inset:0`), 흰색+종이텍스처, `border-radius:0` |
| `.rc-chart`(SVG) | 카드 채움. **viewBox `0 0 960 540`**, `preserveAspectRatio xMidYMid meet` (960:540 = 1.777 ≒ 카드비율, 그래서 viewBox 1단위 ≈ 1.125px) |

> 훅·범례는 graphbox 밖(body 자식)이라 cqw가 뷰포트(1080) 기준. 카드 내부 요소의 cqw는 graphbox(1080) 기준 — 값은 같다.

**SVG 차트 내부 마진(viewBox 960×540 좌표계):** `ML=64`(좌), `MR=176`(우, yleft), `MT=150`(상), `MB=66`(하).
- x 도메인: `x0=2000` … `x1=2026.6`
- y 도메인: `0` … `YMAX`(그래프별)
- 플롯 폭 = 960-64-176 = **720**, 플롯 높이 = 540-150-66 = **324**

---

## 2. 요소별 위치·크기·색·폰트 (전수)

모든 텍스트 = **Pretendard**(`!important`로 강제 통일). 색은 §3 표 참조.

### 상단(그래프 밖)
| 요소 | 내용 | 위치 | 크기 | 색/굵기 |
|---|---|---|---|---|
| 훅 `.hook` | `N. 은퇴원금 <금액>` (N=1~5, 금액=`<b>`) | top 20%, 중앙 | **7cqw(≈76px)** | 흰 `#fff` / **900**. `<b>`금액=**마젠타 `#d12e77`** |
| 범례 `.legout` | 3개: `월 $1천/$2천/$3천 인출` | top 28%, 중앙, gap 4.5cqw | 텍스트 **3cqw** / 500, 색 `#e8e6e0` · 스와치 2.8cqw 정사각 radius .4cqw | 스와치색=선색(§3) |

### 헤더(카드 좌상단) `.rc-chd` — `top:2cqw; left:6.67cqw`(=그래프 y축 ML에 정렬, 업로드 잘림 방지)
| 요소 | 내용 | 크기 | 색/굵기 |
|---|---|---|---|
| 로고 `.rc-logo` | P&G SVG(pg_final에서 추출) | height 3.4cqw | 원본색(파랑) |
| `.rc-tk` | `프록터 앤 갬블 (PG)` | 2cqw | `#111` / 600 |
| `.rc-per` | `2000년 은퇴 · 물가반영 · 월 인출액별` | 1.3cqw | **`#111`(검정)** / 400 |

### 차트(SVG, viewBox 좌표)
| 요소 | 위치(viewBox) | 크기 | 색/굵기 | 비고 |
|---|---|---|---|---|
| y축 눈금선 `.ytick` | y=Y(v), x `ML→W-MR` | stroke 1 | `rgba(0,0,0,.22)` | hline과 겹치는 눈금·`ylabelmin` 미만 생략 |
| y축 라벨 `.rc-ax.rc-al` | x=**ML+2=66**, y=gridY-7, anchor **start** | **18px** | `#000` / 400 | `'$'+값.toLocaleString()` (예 `$1,000,000`) |
| x축 라벨 `.rc-ax.rc-axx` | y=**H-MB+22=496**, anchor middle | **18px** | `#000` / 400 | **4자리 연도**(`String(yr)`), 매 프레임 재생성 |
| 기준선 `.rc-base` | y=**H-MB=474**, x `ML→W-MR` | stroke ~2 | **`#000`** | 하단 x축선 |
| 은퇴원금선 `.rc-hline` | y=Y(hline.v), x 70→780 | width **2.8** | `#555`, dash `5 5`, opacity .45 | 점선 |
| **은퇴원금 라벨** `.rc-hlab` | x=**ML+4=68**, y=hy-9, anchor **start**(좌측 y축) | **18px** | `#333` / **700 볼드** | `은퇴 원금 $AMOUNT`. 항상 표시 |
| 데이터 선 `.rc-ln` | pts 경로 | width **3.4**, round cap/join | 선색(§3) | 3선 |
| 끝점 점 `circle` | (ex,ey) | **r=4.5** | 선색 | 각 선 tip |
| 끝점 값/파산 `.rc-labv` | 기본 (ex+9, ey+6) anchor start; 겹침 회피 시 좌측 anchor end | **18px** | 선색 / 600 | 생존=`fmt(값)`(예 `$740,000`), 사망=`end`(예 `’09 파산`) |

> **글자 크기 통일:** y축·x축·은퇴원금·끝점값·파산 라벨 = **전부 18px**(훅만 76px). 이게 GOLDEN 규칙.

---

## 3. 색상 (전수)

**팔레트 A**(마젠타 톤과 조화, 크림/흰 종이 대비). 원본 덱 색을 `CMAP`으로 치환:

| 역할 | 원본(deck) | → GOLDEN | 쓰임 |
|---|---|---|---|
| 월 $1천 인출 | `#1f6fe0` | **`#2b6cb0`** (스틸블루) | 선·끝점·범례·스와치 |
| 월 $2천 인출 | `#e0821c` | **`#d98f2b`** (오커) | 〃 |
| 월 $3천 인출 | `#e01e37` | **`#c2255c`** (라즈베리) | 〃 |
| 훅 강조(금액) | — | **`#d12e77`** (마젠타) | `.hook b`, 썸네일 "5억으로 은퇴" |
| 축 글자·축선 | — | `#000` | y/x라벨, base |
| 은퇴원금 라벨 | — | `#333` | hlab |
| 헤더 문구 | — | `#111` | rc-tk, rc-per |
| y눈금선 | — | `rgba(0,0,0,.22)` | ytick |
| 은퇴원금 점선 | — | `#555` .45 | hline |
| 범례 텍스트 | — | `#e8e6e0` | legout |
| 배경 | — | `#000`(페이지) · **밝은 흰 종이 텍스처**(카드, `assets/paper.jpg`) | 카드 `background:#fff url(paper) center/cover` |

---

## 4. 애니메이션 스펙 (x축 이동 = 도메인 확장/재스케일)

핵심: **y축은 고정, x축 도메인의 오른쪽 끝만 시간에 따라 자라남**(왼쪽 2000 고정). 눈금 라벨이 이동·재스케일되고
선은 그만큼만 그려지며, 끝점 점+값이 tip을 따라간다. **마지막 프레임 = 기존 정적 축과 100% 동일.**

| 파라미터 | 값 | 의미 |
|---|---|---|
| `DUR` | **10080ms** | 애니 길이. 원본 4200 → ×2 → ×1.2 = 10080(2배+20% 느리게) |
| `INIT` | 0.3 | 시작 초기 창(년). prog0의 R=x0+INIT=2000.3 → **2000년부터 시작** |
| `PADf(prog)` | `1.4*(1-prog)+0.05` | 오른쪽 여유(년): 초반 넓게(끝점 드리프트)→끝에서 ~0(정적축과 일치) |
| `x0,x1` | 2000, 2026.6 | 도메인 좌/우 최대 |

**프레임 함수(요약):**
- `R = (x0+INIT) + prog*(x1-(x0+INIT))` — 이번 프레임 도메인 오른쪽 끝(진행 년도)
- `Xr(y,R,prog) = ML + (y-x0)/((R+PADf)-x0) * 720` — 시간가변 x 매핑
- `Y(v) = (H-MB) - v/YMAX*324` — y는 고정
- `drawXAxis`: 눈금 매 프레임 재생성. `yearStep(span)`: span≤7→1, ≤16→2, ≤35→5, else 10년. 라벨 4자리.
- `clipX(pts,R)`: 각 선을 x≤R 까지 자르고, R 지점을 선형보간해 tip 생성. 선이 R보다 먼저 끝났으면(파산) 마지막 점에 **고정**하고 `ended=true`.
- 끝점 라벨: `running ? fmt(ey) : end`. `fmt`=만원 반올림 후 `$`+콤마(예 `$740,000`).
- **겹침 처리:** 은퇴원금 라벨을 **좌측 y축**으로 옮겨서 우측 끝점값과 구조적으로 안 겹침 → `hlb`는 **항상 opacity 1**.
  (코드의 `_hlhide` 우측겹침 로직은 남아있지만 비활성 — 좌측 이동으로 무력화.)
- **파산 라벨 좌우 분리**(`_dep`): 파산 끝점이 서로 5년 이내면 하나를 anchor end(좌)로 밀어 겹침 방지.
- rAF 루프, `prog=(ts-start)/DUR`, prog≥1이면 정지(마지막 프레임 유지).

**타임라인(그래프당):** 애니 10.08초 + 정지 → 클립 **10.7초**로 트림.

---

## 5. 그래프 데이터 생성 — ★엔진: global_cup_suite

> **데이터 원천은 반드시 `global_cup_suite`의 fire 엔진.** 수치 임의 조작·하드코딩 금지.
> golden_shorts_fire.py 는 엔진을 재실행하지 않고 **하류 산출물(pg_deck.json)만 소비**한다.

**엔진:** `global_cup_suite/global_cup/fire_engine.py` → **`run_fire_backtest()`** (여러 종목/세션 공유 → ⚠️합의 없이 수정 금지).
실제 FIRE 인출 시뮬(월 인출·물가반영 `fixed_real`·세금 15%·잉여현금 재투자·배당 미재투자)을 돌려 pts·생존·파산일 계산.

**전체 체인(원천 → 쇼츠):**
```
data/pg_price.csv · pg_div.csv · ref/fred_CPIAUCSL.csv       (원본: spec/fetch_data.py 수집)
        │
        ▼  gen_fires.py (SHORTS_STOCK=PG)  ── run_fire_backtest 로 원금5[$20/40/60/80/100만]×월인출3[$1/2/3천] 직접 실행
assets/pg_fires.json   [{amt, hook, payload{ymax, hline{v,label}, tip, yleft, lines[3], [ylabelmin], [krw]}}] × 5
        │
        ▼  golden_shorts_fire.py (import·소비만, 엔진 재실행 X) → 편집기 생성기도 G.FIRES 재사용
golden_shorts_fire_{1..5}.html
```
- 라인 pts는 엔진 요약의 월말 리샘플 3개월 간격 `[십진연도, 평가금액]`, 파산 시 파산연도에 [yr,0] 추가.
- `gen_fires.py` 가공: `CMAP` 팔레트A 치환 · `hline.label`="은퇴 원금 <금액>" · 최소원금만 `ylabelmin`(y숫자 숨김) · KRW면 `krw:true`.
- 데이터 갱신·원금/인출 변경 시 `gen_fires.py` 만 다시 실행하면 됨(엔진 재구동).

**무결성 검증(2026-07-28):** `run_fire_backtest` fresh 재실행 결과와 pg_fires.json 을 전수 비교 → 기존 3원금은 롱폼 덱(pg_deck.json)과도 완전 일치. 하드코딩 없음.
> 참고: 롱폼 덱 파이프라인(`spec/gen_backtest.py`→`deck/build_deck.py`→pg_deck.json)은 별개로 유지. golden 쇼츠는 위 `gen_fires.py` 경로를 쓴다(단일 소스).

**시나리오 결과(실측·2000년 은퇴·물가반영·원금 5종):**
| 원금 | 월$1천(파랑) | 월$2천(주황) | 월$3천(빨강) |
|---|---|---|---|
| $200,000 | ’16 파산 | ’06 파산 | ’04 파산 → **셋 다 파산** |
| $400,000 | **생존 $740,000** | ’16 파산 | ’09 파산 |
| $600,000 | **생존 $1,730,000** | **생존 $490,000** | ’16 파산 |
| $800,000 | 생존 $2,720,000 | 생존 $1,480,000 | 생존 $230,000 |
| $1,000,000 | 생존 $3,710,000 | 생존 $2,470,000 | 생존 $1,230,000 |

---

## 6. 영상 조립 (build_golden_shorts_fire.py)

| 슬라이드 | 소스 | 길이 | 방식 |
|---|---|---|---|
| 0 썸네일 | `assets/thumb_mag.png` | **1.25초** | 정지 이미지 loop |
| 1~5 그래프 | `golden_shorts_fire_{1..5}.html` ($20/40/60/80/100만) | 각 **10.7초** | playwright 녹화 |

- **장수 자동:** build 스크립트가 `golden_shorts_fire_[0-9].html` 개수(NG=5)를 세어 그만큼 녹화·합성.
- **녹화:** 1080×1920 컨텍스트, 폰트 로드 대기(`document.fonts.check('900 100px Pretendard')`) → `reelAnim()` 수동 트리거 → `REC_WAIT_MS=11000` 대기.
- **트림:** `-ss (off+0.15) -t 10.7` (off=페이지로드 오프셋). 슬라이드마다 scale 1080:1920, fps 30, yuv420p.
- **합성:** concat demuxer(c0=썸네일 + c1..c5) → h264 crf20 `+faststart`. **총 ≈54.6초.**
- 중간산출물은 `_build/`(git 추적 불필요).

---

## 7. 썸네일 (슬라이드 1 · GOLDEN 레퍼런스 레이아웃)

**표준 = PG 제품클러스터형**(배경 `#000`, 전부 가로중앙 x50%). 위→아래: **제품클러스터 → 브랜드로고 → 마젠타 금액문구 → 흰 문구**.
- **영상**은 확정 래스터 `assets/thumb_mag.png` 사용(1.25초). **편집기**(`golden_shorts_fire_editor.html`) 슬라이드0가 **아래 디폴트값으로 동일 레이아웃을 편집가능 요소로 재현**.

**요소 스펙(= 편집기 슬라이드0 디폴트값, PG 기준):**
| 요소 | 위치(x, y %) | 크기 | 색 | 종목 교체 |
|---|---|---|---|---|
| **제품 클러스터**(제품+필기체 라벨+낙서 한 이미지) | (50, **37**) | width **78cqw** | 이미지 | **사람이** 해당 종목 사진 제공 |
| **브랜드 로고** | (50, **54**) | width **15cqw** | 원본색(P&G 파랑) | **에이전트가** 로고 준비 |
| **문구1(금액)** `5억으로 은퇴` | (50, **60**) | **7cqw** | **마젠타 `#d12e77`** | 금액만 교체(예 `6억으로 은퇴`) |
| **문구2** `적정 생활비는?` | (50, **66**) | **7cqw** | 흰 `#fff` | 고정 |

- 폰트 Pretendard **900**, letter-spacing −.02em. 문구는 두 줄 모두 중앙.
- **종목 교체 시:** 제품클러스터 이미지(사람)·로고(에이전트)·문구1 금액만 바꾸면 됨. 위치·크기·색은 위 값 **그대로**.
- 편집기에서 요소 드래그·숫자박스로 미세조정 가능, 💾PNG로 저장 → 영상 build 시 `assets/`에 넣고 `THUMB` 경로 지정.
> PG 영상 정본 `thumb_mag.png`는 재생성 금지(래스터). 편집기 디폴트가 이 래스터와 동일 레이아웃.
> 참고 스펙: `blog/prototypes/thumbs/SHORTS_THUMBNAIL_SPEC.md`(측정 원본).

## 8. 폰트
`PretendardVariable.woff2`(2MB, unpkg) → `@font-face{font-weight:100 900; src:base64}` 로 HTML에 임베드.
시스템엔 Noto만 있어 900이 얇게 폴백되던 문제를 임베드로 해결.

---

## 9. 결정 로그(왜 이 값인가)
- **x축 이동**: 사용자가 randomdatavstime 릴 스타일 지정. 고정축 선그리기 → 도메인 확장으로 교체(디자인 100% 유지 조건).
- **2000년 시작**: INIT 2.0→0.3 (초기 창이 커서 2002부터처럼 보이던 것 수정).
- **속도**: 4200 → 8400(2배) → 10080(추가 20%). 사용자 지시 순차 반영.
- **축/라벨 검정·18px 통일**: 종이 배경 가독성 + 은퇴원금 라벨 기준 크기 통일.
- **은퇴원금 라벨 좌측 이동·18px·볼드**: 우측 끝점값과 겹침 근본 제거 + 강조.
- **$200k y숫자 전삭제**: 소액 구간 눈금 난잡 → 기준선만.
- **헤더 y축 정렬(6.67cqw)**: 업로드 세이프에어리어에 로고 좌측 잘림 → 안쪽(26px→72px)으로.
- **팔레트 A**: 파랑/주황/에메랄드 "허접"·"촌스럽다" 피드백 → 스틸블루/오커/라즈베리 확정.

---

## 11. 통합 편집기 golden_shorts_fire_editor.html

`gen_golden_shorts_fire_editor.py` 가 **golden_shorts_fire.py 를 import** 해 NEWRA·CMAP·fire_payload·logo·paper 를 재사용,
**6슬라이드 편집기**(썸네일+그래프5)를 조립한다(→ `golden_shorts_fire_editor.html`, 자립형 ~4MB). `NSLIDE=FIRES.length+1`로 원금 개수에 자동 대응.

**슬라이드 구성(= golden spec 반영):**
| # | 슬라이드 | 내용 |
|---|---|---|
| 1(idx0) | 썸네일 | **편집가능 요소**(§7 디폴트값): 제품클러스터·P&G로고·"5억으로 은퇴"(마젠타)·"적정 생활비는?". drag/resize/color/text/PNG. |
| 2~6(idx1~5) | $20/40/60/80/100만 그래프 | golden 그대로: **x축 이동 애니(NEWRA)**·팔레트A·종이배경·18px·검정축·좌측 은퇴원금·범례 밖(legout)·**번호 훅(금액 마젠타)**·최소원금은 y숫자 없음(ylabelmin). |

**기능(thumb_editor 엔진 이식):** 요소 add/드래그/리사이즈/색/텍스트수정/삭제/앞으로 · 선택요소 숫자박스(X/Y/크기/색) ·
📐가이드 · 👁렌더모드(편집UI 숨김) · ⬇⬆JSON(레이아웃 저장/불러오기 `pg_editor_layout.json`) · 💾PNG(요소만, 썸네일용).
그래프 애니 타이밍 golden(DUR 10080·THUMB_HOLD 1250). 재생 ▶로 6슬라이드 자동재생.

**재생성:** `cd blog/PG/golden_shorts_fire && python3 gen_golden_shorts_fire_editor.py` (assets.json + golden import 필요).
그래프 디자인/데이터는 golden_shorts_fire.py 를 고치면 편집기에도 자동 반영(단일 소스).
> golden 그래프 CSS 는 gen_golden_shorts_fire_editor.py 안에도 복제돼 있음(주석 표기) — golden_shorts_fire.py 와 **동일하게 유지**.
> 이 편집기가 구 `blog/prototypes/pg_editor.html`(옛 디자인)을 대체.

관련 메모리: [[pg-merged-reelchart]] · [[pg-subtitle-save-architecture]] · [[video-pipeline-and-jnj]] · [[shorts-thumbnail-template]]
