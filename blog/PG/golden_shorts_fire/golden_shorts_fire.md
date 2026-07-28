# golden_shorts_fire — 은퇴 시나리오 쇼츠 GOLDEN REFERENCE ❄️FROZEN

> **상태: 동결(FROZEN) · 2026-07-28.** 이 문서 + `golden_shorts_fire.py` + `assets/` = **정본**.
> 앞으로 "은퇴 시나리오 쇼츠"는 이 스펙이 기준. 값을 바꿀 땐 반드시 이 문서도 같이 갱신.
> 확정 영상: `golden_shorts_fire.mp4` (1080×1920, 30fps, **총 33.23초**).

배투실 PG(프록터 앤 갬블) 배당 백테스트 쇼츠. "5억으로 은퇴하면 매달 얼마까지 써도 안 망하나"를
은퇴원금 $200,000 / $400,000 / $600,000 세 시나리오로, 월 $1천/$2천/$3천 인출 3선을 **x축 이동
(randomdatavstime 스타일)** 애니메이션으로 보여준다.

---

## 0. 파일 구성 · 재현 방법

```
blog/PG/golden_shorts_fire/
├── golden_shorts_fire.py            # ★생성기: 3개 그래프 HTML 생성(디자인·애니·데이터 전부 여기)
├── build_golden_shorts_fire.py      # 렌더(playwright)+합치기(ffmpeg) → mp4
├── golden_shorts_fire.md            # 이 문서(정본 스펙)
├── golden_shorts_fire.mp4           # 확정 영상
├── golden_shorts_fire_{1,2,3}.html  # 생성물($200k/$400k/$600k) — 생성기가 덮어씀
└── assets/
    ├── paper_b64.txt                # 흰 종이 텍스처 base64(data URI)
    └── thumb_mag.png                # 마젠타 썸네일(슬라이드 0)
```

외부 의존(저장소 내 영구):
- 폰트: `blog/fonts/PretendardVariable.woff2` → 런타임 base64 임베드(@font-face)
- 데이터: `blog/PG/deck/pg_deck.json` scenes[6/7/8]
- 로고·기본 릴CSS: `blog/PG/deck/pg_final.html` (로고 path + 라인 1611:1634 rc_css)

**재현:**
```bash
cd blog/PG/golden_shorts_fire
python3 build_golden_shorts_fire.py     # 그래프 생성→녹화→합성까지 한 번에 → golden_shorts_fire.mp4
# (HTML만 다시 뽑으려면) python3 golden_shorts_fire.py
```
필요: `playwright`(chromium), `ffmpeg`.

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
| 훅 `.hook` | `N. 은퇴원금 $AMOUNT` (N=1/2/3, 금액=`<b>`) | top 20%, 중앙 | **7cqw(≈76px)** | 흰 `#fff` / **900**. `<b>`금액=**마젠타 `#d12e77`** |
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
| 배경 | — | `#000`(페이지) · 흰 종이텍스처(카드) | |

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

## 5. 그래프 데이터 생성

**출처:** `pg_deck.json` → `scenes[idx].data`. idx=6→$200k, 7→$400k, 8→$600k.

`data` 구조:
```
{ ymax, hline:{v,label}, tip, legend[], lines:[ {c, name, surv, end, pts:[[year,value],...]} ] }
```
- `pts`: `[십진연도, 평가금액]`. 연도 2000.08 … 2026.56(월 단위 샘플). value 달러.
- `surv`: 생존 여부. `end`: 끝 라벨(생존시 `생존 $73만`류, 사망시 `’09 파산`류).

**생성기 가공:**
1. `CMAP`으로 선색 치환(§3).
2. `hline.label` 을 **풀넘버**로 덮어씀: `은퇴 원금 $%s`(amt 콤마). (원본은 `$40만`류)
3. payload = `{ymax, hline, tip:"compact", yleft:true, lines, [ylabelmin]}`.
4. **`ylabelmin`**: `$200,000` 그래프만 `160000` → y숫자($50k/$100k/$150k) 전부 제거, **기준선만**. 다른 그래프는 미설정(표시).

**시나리오 결과(실측·2000년 은퇴·물가반영):**
| 그래프 | 월$1천(파랑) | 월$2천(주황) | 월$3천(빨강) |
|---|---|---|---|
| $200,000 | ’16 파산 | ’06 파산 | ’04 파산 → **셋 다 파산** |
| $400,000 | **생존 $740,000** | ’16 파산 | ’09 파산 |
| $600,000 | **생존 $1,730,000**(172만$) | **생존 $490,000**(48만$) | ’16 파산 |

---

## 6. 영상 조립 (build_golden_shorts_fire.py)

| 슬라이드 | 소스 | 길이 | 방식 |
|---|---|---|---|
| 0 썸네일 | `assets/thumb_mag.png` | **1.25초** | 정지 이미지 loop |
| 1 $200k | `golden_shorts_fire_1.html` | 10.7초 | playwright 녹화 |
| 2 $400k | `..._2.html` | 10.7초 | 〃 |
| 3 $600k | `..._3.html` | 10.7초 | 〃 |

- **녹화:** 1080×1920 컨텍스트, 폰트 로드 대기(`document.fonts.check('900 100px Pretendard')`) → `reelAnim()` 수동 트리거 → `REC_WAIT_MS=11000` 대기.
- **트림:** `-ss (off+0.15) -t 10.7` (off=페이지로드 오프셋). 슬라이드마다 scale 1080:1920, fps 30, yuv420p.
- **합성:** concat demuxer → h264 crf20 `+faststart`. **총 ≈33.23초.**
- 중간산출물은 `_build/`(git 추적 불필요).

---

## 7. 썸네일 (thumb_mag.png)

업로드 원본 이미지("주식 5억으로 은퇴 / 적정 생활비는?")를 **위치·크기 그대로 유지**하고,
"**5억으로 은퇴**" 골드 글자 픽셀만 **마젠타 `#d12e77`** 계열로 재색칠(안티에일리어싱 커버리지 보존).
> ⚠️ 썸네일은 재생성 금지(레이아웃 어긋남). `assets/thumb_mag.png` 그대로 사용.

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

관련 메모리: [[pg-merged-reelchart]] · [[pg-subtitle-save-architecture]] · [[video-pipeline-and-jnj]]
