# golden_shorts_accum — 적립 vs 폭락매수 쇼츠 GOLDEN REFERENCE

> **상태: 동결(FROZEN) · 2026-07-28.** 이 문서 + `golden_shorts_accum.py` + `gen_accum*.py` + `assets/` = 정본. 확정 영상 `golden_shorts_accum.mp4`(5페이지·38.2초).
> `golden_shorts_fire`(은퇴 인출 시나리오)의 **자매편** — 시각 스펙(레이아웃·색·애니 §1~§4)은 공유, **데이터·구성만 적립용**.

배투실 배당 백테스트 쇼츠 — **"매달 꾸준히 적립(DCA) vs 폭락 때만 몰아서 매수"** 승부.
2000년부터 매달 정액 적립(배당 재투자), **적립식 vs X% 하락매수** 2선을 임계값 3종(20/30/50%)으로 비교.
각 그래프 = **평가액 실선 2 + 누적 투입원금 점선 2**(각각). x축 이동(randomdatavstime) 애니.

**구성: 총 5페이지**
| 페이지 | 내용 |
|---|---|
| 1 | 썸네일 (fire 골든과 공유·미변경) |
| 2 | 적립식 vs **20%** 하락매수 |
| 3 | 적립식 vs **30%** 하락매수 |
| 4 | 적립식 vs **50%** 하락매수 |
| 5 | **결과 테이블**(최종액·CAGR·XIRR) — 약 5초 정지 |

> **정규화:** 월 적립 = **미국 $1,000 / 한국 1,000원**(`gen_accum.py` `E.MONTHLY_INCOME`). CAGR/XIRR은 스케일 무관.
> **판단 문구 없음** — 원금·결과·수익률만 제시(쇼츠에서 승자 단정 X).

---

## 0. 파일 구성 · 재현 방법

```
blog/golden_shorts_accum/
├── gen_accum.py                       # ★백테스트: 적립식(steady)+폭락매수(smart 20/30/50%) → assets/pg_accum.json (엔진 ko_smart_vs_steady)
├── gen_accum_table.py                 # ★5p 결과 테이블(CAGR/XIRR) HTML 생성 (golden_shorts_accum import)
├── golden_shorts_accum.py             # ★영상 그래프 생성기: pg_accum.json → 그래프 3장 HTML. import 가능(NEWRA/FONTSRC/paper/FIRES 노출)
├── gen_golden_shorts_accum_editor.py  # ★편집기 생성기: 5슬라이드(썸네일+적립 그래프3+결과 테이블) 조립
├── golden_shorts_accum_editor.html    # ★편집기 — 브라우저로 열어 편집(§11)
├── build_golden_shorts_accum.py       # 렌더+합치기 → mp4 (썸네일+그래프3+테이블) ※표 5초 통합 예정
├── golden_shorts_accum.md             # 이 문서
├── golden_shorts_accum_{1..3}.html    # 영상용 그래프 3장(생성물·gitignore) · golden_shorts_accum_table.html(테이블)
└── assets/
    ├── paper.jpg · paper_b64.txt      # 그래프 배경 종이 텍스처(fire와 동일)
    ├── pg_accum.json                  # ★적립 데이터 — gen_accum.py 산출(그래프 3장 payload + steady/smart의 final·xirr·cagr)
    ├── assets.json                    # 편집기용 제품/배지/로고 base64
    └── thumb_mag.png                  # 썸네일 래스터(fire와 공유)
```
> **엔진:** `blog/PG/deck/tools/ko_smart_vs_steady.py`(코카콜라·PG 검증본) — `run_steady`(적립식)·`run_smart`(폭락매수)·`compute_triggers`(TRIGGER_DD 전역 override로 임계값 20/30/50% 파라미터화). 수정 금지.

외부 의존(저장소 내 영구):
- 폰트: `blog/fonts/PretendardVariable.woff2` → 런타임 base64 임베드(@font-face)
- 데이터: `assets/pg_fires.json` (gen_fires.py 엔진 산출, 원금 5종). *(pg_deck.json은 롱폼 덱용 별개)*
- 로고·기본 릴CSS: `blog/PG/deck/pg_final.html` (로고 path + 라인 1611:1634 rc_css)

**재현:**
```bash
cd blog/golden_shorts_accum
python3 build_golden_shorts_accum.py     # 그래프 생성→녹화→합성까지 한 번에 → golden_shorts_accum.mp4
# (HTML만 다시 뽑으려면) python3 golden_shorts_accum.py
```
필요: `playwright`(chromium), `ffmpeg`.

---

## 0.5 ★ 제작 파이프라인 (신규 종목 → 편집기)

> **이 golden은 "은퇴 시나리오 쇼츠" 제작 틀이다.** 스펙(요소 위치·크기·색·애니 §1~§4)은 종목 무관 고정,
> **종목별로 바뀌는 입력만 갈아끼우면** 해당 종목용 `golden_shorts_accum_editor.html` 이 나온다.

**입력(INPUT):** ① 종목(티커·기업명) ② 백테스트 시나리오(은퇴원금 **5종** × 월 인출 3종 · 은퇴 시점 · 물가반영 등)
**출력(OUTPUT):** **`golden_shorts_accum_editor.html`** (썸네일+적립그래프3+테이블 = **5슬라이드**)

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

## 5. 데이터 생성 — ★엔진: ko_smart_vs_steady

**엔진:** `blog/PG/deck/tools/ko_smart_vs_steady.py` (코카콜라·PG 검증본 · 수정 금지).
- `run_steady(prices,divs,me_idx,reinvest)` — **적립식**: 매달 말 전액 매수(DCA). `series`=(date,value) 월말.
- `run_smart(prices,divs,me_idx,triggers,reinvest)` — **폭락매수**: 현금 모았다가 트리거 때 100% 투입.
- `compute_triggers(prices)` — 고점 대비 `TRIGGER_DD`(-30% 기본) 통과 시 발동, `REARM_DD`(-10%) 회복 시 재무장.
  → **임계값 파라미터화:** `E.TRIGGER_DD = -0.20/-0.30/-0.50` 전역 override 후 재계산.
- `xirr(flows)` — 월 투입 현금흐름 기준 연환산 수익률.

**체인:**
```
blog/PG/data/pg_price.csv · pg_div.csv   (무수정 종가·배당)
        │
        ▼  gen_accum.py (SHORTS_STOCK=PG) — MONTHLY=1000, 배당재투자 ON
        │     · run_steady → 적립식 평가/원금 시리즈
        │     · thr∈{20,30,50}: TRIGGER_DD override → compute_triggers → run_smart → 폭락 평가/원금 시리즈
        │     · XIRR·CAGR 계산
assets/pg_accum.json  [{thr, hook, payload{4선}, invested, steady{final,xirr,cagr}, smart{...}, monthly, krw}] × 3
        │
        ▼  golden_shorts_accum.py(그래프3) · gen_accum_table.py(테이블) · 편집기 생성기(G.FIRES)
```

**그래프 = 4선(각각):** 평가 실선 2(적립식 `#2b6cb0` / 폭락매수 `#c2255c`) + **누적 투입원금 점선 2**(`dash:true`,`nolabel:true` — 점·라벨 없음). 적립식 원금=매끄러운 상승, 폭락매수 원금=트리거 계단식. hline 없음.

**⚠️ 샘플링 = 월별(`sub(series, step=1)`):** 엔진의 **월말 시리즈를 전량(매달) 사용**. 3개월 간격 등 성기게 뽑으면 **최근 급등·폭락을 건너뛰어** 그래프에 반영 안 됨(실측: SK하이닉스 2026-06 고점→07 −42% 폭락이 분기 샘플에선 사라짐). 단기 변동 정확 반영을 위해 **반드시 step=1**.

**정규화:** `E.MONTHLY_INCOME`(미국 $1,000 / 한국 1,000원, **SK하이닉스 10만원**). CAGR/XIRR은 스케일 무관, 최종액만 비례.

**시작연도 파라미터(`x0`/`START_YEAR`):** 기본 2000. **감자·상장이슈 종목은 늦춤**(SK하이닉스=2006, 워크아웃·감자 회피). payload `x0`가 NEWRA x축 시작·부제 연도를 결정.

**통화(`krw`):** KRW 종목(KTNG·SKH)은 payload·fire에 `krw:true` → 그래프 fmt·y축·테이블 모두 **억/만원** 표기. 데이터=yfinance(PG만 로컬 CSV).

**결과(PG · 월 $1,000 적립 · 배당재투자 · 26.6년 · 총투입 $320k):**
| 전략 | 최종액 | CAGR | XIRR | 트리거 |
|---|---|---|---|---|
| 매달 적립식 | $994,925 | 4.4% | **7.7%** | — |
| 20% 하락매수 | $981,505 | 4.3% | 7.6% | 9회 |
| 30% 하락매수 | $830,354 | 3.7% | 6.6% | 2회 |
| 50% 하락매수 | $498,119 | 1.7% | 3.2% | 1회 |
→ 깊은 하락을 기다릴수록 현금이 놀아 성과 저하. (승자 단정은 쇼츠에 표기 안 함)

---

## 6. 영상 조립 (build_golden_shorts_accum.py)

| 슬라이드 | 소스 | 길이 | 방식 |
|---|---|---|---|
| 0 썸네일 | `assets/thumb_mag.png` | **1.25초** | 정지 이미지 loop |
| 1~3 그래프 | `golden_shorts_accum_{1..3}.html` (적립식 vs 20/30/50% 하락매수) | 각 **10.7초** | playwright 녹화 |
| 4 결과 테이블 | `golden_shorts_accum_table.html` | **5초** | PNG 정지 |

- **장수 자동:** build가 `golden_shorts_accum_[0-9].html` 개수(NG=3)를 세어 녹화 후, 테이블 PNG를 5초 클립으로 뒤에 붙임.
- **녹화:** 1080×1920 컨텍스트, 폰트 로드 대기(`document.fonts.check('900 100px Pretendard')`) → `reelAnim()` 수동 트리거 → `REC_WAIT_MS=11000` 대기.
- **트림:** `-ss (off+0.15) -t 10.7` (off=페이지로드 오프셋). 슬라이드마다 scale 1080:1920, fps 30, yuv420p.
- **합성:** concat(c0=썸네일 + c1..c3=그래프 + c4=테이블) → h264 crf20 `+faststart`. **총 ≈38.2초.**
- 중간산출물은 `_build/`(git 추적 불필요).

---

## 7. 썸네일 (슬라이드 1 · GOLDEN 레퍼런스 레이아웃)

**표준 = PG 제품클러스터형**(배경 `#000`, 전부 가로중앙 x50%). 위→아래: **제품클러스터 → 브랜드로고 → 마젠타 금액문구 → 흰 문구**.
- **영상**은 확정 래스터 `assets/thumb_mag.png` 사용(1.25초). **편집기**(`golden_shorts_accum_editor.html`) 슬라이드0가 **아래 디폴트값으로 동일 레이아웃을 편집가능 요소로 재현**.

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

## 11. 통합 편집기 golden_shorts_accum_editor.html

`gen_golden_shorts_accum_editor.py` 가 **golden_shorts_accum.py 를 import** 해 NEWRA·CMAP·fire_payload·logo·paper 를 재사용,
**5슬라이드 편집기**(썸네일+적립그래프3+결과 테이블)를 조립(→ `golden_shorts_accum_editor.html`, 자립형 ~4MB). `NSLIDE=FIRES.length+2`(테이블 포함). 테이블은 `.tablebg`(cqw 스케일), ▶재생 시 5초 정지.

**슬라이드 구성(= golden spec 반영):**
| # | 슬라이드 | 내용 |
|---|---|---|
| 1(idx0) | 썸네일 | **편집가능 요소**(§7 디폴트값): 제품클러스터·P&G로고·"5억으로 은퇴"(마젠타)·"적정 생활비는?". drag/resize/color/text/PNG. |
| 2~4(idx1~3) | 적립식 vs 20/30/50% 하락매수 | **4선**(평가 실선2+누적원금 점선2)·**x·y축 둘 다 동적 재스케일**·번호 훅(임계값 마젠타)·범례 2선·끝점 라벨 겹침 회피. |
| 5(idx4) | 결과 테이블 | 최종액·CAGR·**XIRR** (`.tablebg`, 5초 정지). |

**기능(thumb_editor 엔진 이식):** 요소 add/드래그/리사이즈/색/텍스트수정/삭제/앞으로 · 선택요소 숫자박스(X/Y/크기/색) ·
📐가이드 · 👁렌더모드(편집UI 숨김) · ⬇⬆JSON(레이아웃 저장/불러오기 `pg_editor_layout.json`) · 💾PNG(요소만, 썸네일용).
그래프 애니 golden(DUR 10080). 재생 ▶로 5슬라이드 순환(테이블 5초 정지 후 처음으로).

**재생성:** `cd blog/golden_shorts_accum && python3 gen_golden_shorts_accum_editor.py` (assets.json + golden import 필요).
그래프 디자인/데이터는 golden_shorts_accum.py 를 고치면 편집기에도 자동 반영(단일 소스).
> golden 그래프 CSS 는 gen_golden_shorts_accum_editor.py 안에도 복제돼 있음(주석 표기) — golden_shorts_accum.py 와 **동일하게 유지**.
> 이 편집기가 구 `blog/prototypes/pg_editor.html`(옛 디자인)을 대체.

관련 메모리: [[pg-merged-reelchart]] · [[pg-subtitle-save-architecture]] · [[video-pipeline-and-jnj]] · [[shorts-thumbnail-template]]
