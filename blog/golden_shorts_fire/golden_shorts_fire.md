# golden_shorts_fire — 은퇴(FIRE) 시나리오 쇼츠 GOLDEN TEMPLATE ❄️FROZEN

> **상태: 동결 템플릿(FROZEN) · 2026-07-30.** 이 문서 + `golden_shorts_fire.py` + `gen_fires.py` + `gen_fire_table.py` +
> `gen_golden_shorts_fire_editor.py` + `build_golden_shorts_fire.py` + `assets/` = **정본**.
> 앞으로 "은퇴 인출 시나리오 쇼츠"는 이 템플릿이 기준. 값·레이아웃을 바꾸면 이 문서도 같이 갱신.
> 레퍼런스 빌드: **QQQ**(닷컴 꼭지 2000년 은퇴). 산출물 `golden_shorts_fire_<STOCK>.mp4`(1080×1920, 30fps, **3페이지·약 52초**).

"은퇴원금이 얼마면, 매달 얼마까지 뽑아 써도 30년을 버티나?"를 **원금 5종 × 월 인출 3종**으로 보여주는 쇼츠.
핵심 연출 = **누적 고스트(accumAnim)**: 원금을 작은 것($20만)부터 순차로 그리고, 끝난 원금은 회색 고스트로 남긴 채
다음(더 큰) 원금을 그 위에 겹쳐 그린다 → "돈이 많을수록 더 높이·오래 버틴다"가 한 화면에 쌓인다.

---

## 0. 파일 구성 · 재현

```
blog/golden_shorts_fire/
├── golden_shorts_fire.py          # ★영상 그래프 생성기(누적 그래프 1장). ACCUM/ACCUM_DATA/ACCUM_TOTAL_MS/FIRES/CSS_F 노출
├── gen_fires.py                   # ★백테스트 엔진 실행(SHORTS_STOCK) → assets/<stock>_fires.json (원금5종×인출3종)
├── gen_fire_table.py              # ★3페이지 결과 테이블. ROWS/MOS/NOTE 노출(에디터 재사용)
├── gen_golden_shorts_fire_editor.py  # ★편집기 생성기 → 3슬라이드(썸네일+누적그래프+테이블)
├── build_golden_shorts_fire.py    # 렌더(playwright)+합치기(ffmpeg) → golden_shorts_fire[_<STOCK>].mp4
├── golden_shorts_fire.md          # ★이 문서(정본 스펙)
├── QQQ_YOUTUBE.md                 # 업로드 메타(제목/설명/태그/고정댓글)
└── assets/
    ├── <stock>_fires.json         # gen_fires 산출 데이터(원금5종)
    ├── paper_b64.txt              # 종이 텍스처
    ├── qqq_logo.png qqq_thumb.png # 종목별 로고(Invesco)·썸네일
    └── assets.json                # 편집기 제품/배지/로고 base64
```

**재현(종목 교체 = SHORTS_STOCK):**
```
SHORTS_STOCK=QQQ python3 gen_fires.py                       # 데이터
SHORTS_STOCK=QQQ python3 build_golden_shorts_fire.py        # 영상(그래프·테이블 자동 생성 포함)
SHORTS_STOCK=QQQ python3 gen_golden_shorts_fire_editor.py   # 편집기(썸네일 편집용)
```
mp4·에디터 html·`golden_shorts_fire_1.html`·`_table.html`은 재생성물 → gitignore. 소스·에셋만 커밋.

---

## 1. 영상 구성 (3페이지 · 약 52초)

| # | 페이지 | 길이 | 내용 |
|---|--------|------|------|
| 0 | 썸네일 | 1.25s | `assets/<stock>_thumb.png` 정지 |
| 1 | **누적 그래프** | ~43s | 인트로 훅 3s + 원금5종 누적 애니 |
| 2 | 결과 테이블 | 5s | 원금×월인출 매트릭스(미세 줌) |

빌드 비트레이트: 소스 clip crf14 + concat `-b:v 18M -maxrate 22M`(유튜브 재압축 대비). 테이블은 3배 캡처+zoompan.

---

## 2. 누적 그래프 (accumAnim) — 핵심 스펙

- **인트로 훅(`intro=3000ms`)**: 전체 5원금 라인을 **회색**(값·기준선·점 없음)으로 깔아 "결과 미리보기". (스탬프·문구 없음.)
- **누적 본편**: 원금 순서대로 그림. 각 원금 = `dur` 동안 그리고 `hold` 유지. 끝나면 **회색 고스트**로 남고 다음 원금이 위에.
  - 페이스: `dur=[4.5,5.5,8,7,9]s`, `hold=[1.1,1.1,.7,.7,2.2]s` (ACCUM_DATA).
- **모든 원금이 3선 전부** 그림(생존선 + 높은인출 파산선).
  - **생존선**: 라인끝=포트폴리오 값(예 $3,860,000) + **녹색 "생활비 $X / 생존" 스탬프**(X=최대 생존 인출액). 고스트엔 원금 라벨(plab, 예 $800K).
    - 끝점 값 라벨은 `fmtV`: USD **$10M↑만 축약**($41,230,000→$41.2M, 잘림 방지) · 그 이하·원화·y축 눈금은 `fmtY` 전체표기 유지. QQQ 참조($3.86M)는 무변화.
  - **파산선**: 라인끝 `$0`(원화 `₩0`). **전멸 원금**(전 인출 파산)=**라즈베리 "파산" 스탬프** 쾅.
- **x축**=이전 원금 최대범위까지 고정 → 그 뒤로 확장. **y축**=보이는 전체 최대값 동적 재스케일(+은퇴원금 hline 포함).
- **원금 전환 카운트업(`trans=700ms`)**: 원금 i→i+1 전환 시 은퇴원금 숫자가 **실시간 증가**($200,000→$400,000)하며 y축 재스케일 + 이전 라인이 회색으로 하강. `drawTrans()`가 vmaxUpTo/extentUpTo(누적 최대값·범위)로 모프.
- 끝점 라벨 세로 겹침 회피: 위→아래 정렬 후 **x가 92px 내로 겹치고 세로로 30px 미만 붙을 때만 아래로 밀어** 30px 확보(자연 간격이 충분하거나 파산 시점이 다른 라벨은 그대로 유지 — 전종목·전연도 안전).

## 3. 레이아웃 (2026-07-29 확정)

- **그래프 카드**: 종이 배경 full-width(1080), 차트는 `aspect-ratio:1.125/1`로 letterbox되어 **≈960px**(양옆 종이 여백 60px씩). viewBox `0 0 960 960`(MT=132, MB=74, **ML=50, MR=140**=끝점라벨 세이프존). 카드 **상단 고정 `top:22%`**(하단 여백↑).
- **상단 헤더**: `.tophdr` = [종목 로고(흰색 `filter:brightness(0) invert(1)`)] + **제목**(`TITLE`, 예 "QQQ 나스닥 100"), 한 줄(nowrap).
- **범례는 그래프 안**(카드 상단, `top:24.5%`, 어두운 글씨 `#333`). 회사명은 그래프에서 삭제.
- **하단 훅 문구 없음**(원금은 그래프 안 "은퇴 원금 $X" 기준선 라벨로 표시).
- **은퇴원금 형광펜**: hline 라벨 뒤 노란 밴드(`#ffe14d` op.62, 텍스트 bbox에 맞춰 `markHl()` 매 프레임).
- **배투실 워터마크**: `assets.json` BADGE를 그래프 우상단(`top:28.5%;right:8%`·범례 아래·오른쪽 여백)에 작게.
- **글씨 크기**: 축·끝점 숫자 27px, **은퇴원금(hline `rc-hlab`)만 40px**(1.5배 강조). 훅 강조=마젠타 `#d12e77`.
- 색(팔레트A): 월1천 `#2b6cb0` / 2천 `#d98f2b` / 3천 `#c2255c`. 생존 스탬프 녹색 `#2b8a3e`, 파산 라즈베리 `#c2255c`.

## 4. 3페이지 테이블 (gen_fire_table.py)

원금(행 5) × 월 인출(열 3) 매트릭스. **초록**=30년 생존 최종액 / **빨강**=파산 연도(예 '06 파산).
`ROWS/MOS/NOTE` 모듈 노출 → 편집기 3페이지에서 그대로 재사용. 흰 종이 카드·미세 줌으로 유튜브 화질 보정.
- **헤더 글씨=본문 크기**(th 27px·th.pr 26px, 편집기 2.5/2.4cqw). NOTE 세금은 통화별(원화 15.4% / 달러 15%).
- **경고 문구(`DISC`)**: NOTE 아래 구분선+⚠️ 붉은색(`#a3453a`) — "과거 데이터 백테스트 · 미래 수익 미보장 · 투자 권유 아님". `gen_fire_table.DISC` 모듈 노출 → 편집기 `__TDISC__` 재사용(전 종목 공통).

---

## 5. 데이터 원천 (수정 금지)

모든 pts/생존/파산 수치 = **`global_cup_suite/global_cup/fire_engine.py::run_fire_backtest`**(공유 엔진).
`gen_fires.py`(SHORTS_STOCK)가 엔진을 직접 돌려 `assets/<stock>_fires.json` 산출.
- USD 종목: 원금 $20/40/60/80/100만, 월 $1/2/3천, 세금 15%, 미국 CPI(로컬 csv).
- KRW 종목: 원금 2/4/6/8/10억, 월 100/200/300만, 세금 15.4%, 한국 CPI(FRED).
- 데이터: PG=로컬 CSV, 그 외=yfinance(NaN 종가 필터). 물가반영 인출(fixed_real)·배당은 생활비로 사용.
- ⚠️ fire_engine은 공유 엔진 → 합의 없이 수정 금지. 수치 임의 하드코딩 금지.

## 6. 새 종목 만들기 (템플릿 사용법)

1. **입력 결정(사람)**: 종목 티커, 은퇴 시작연도(엔진 기본 2000; 이슈 회피 시 gen_fires에서 조정), 통화.
2. **에셋(사람+에이전트)**: `assets/<stock>_thumb.png`(썸네일) 사람 제작 · `assets/<stock>_logo.png`(로고) 준비.
3. **코드 종목 분기 추가**: `gen_fires.py`(티커·통화·시작연도), `golden_shorts_fire.py`/편집기의 종목 헤더(`LOGO/LOGOVB/COMPANY/TITLE`), `build`의 THUMB 맵.
4. **생성**: gen_fires → build → 편집기. 썸네일은 편집기에서 사진 import 후 PNG 저장.

스펙(레이아웃·색·애니·테이블)은 종목 무관 고정. **종목별 입력(로고·썸네일·데이터·제목·시작연도)만 교체.**

---

## 7. 이력

- 2026-07-28: 초판(원금별 5장 개별·x축 이동 애니, PG). 이후 QQQ·Invesco·무빙슬라이드 시도.
- 2026-07-29: **누적 고스트로 대개편**(원금별 5장 → 연속 1장 + 테이블). 정사각 그래프·상단 헤더 제목·범례 인그래프·은퇴원금 강조·인트로 훅.
- 2026-07-29(마감): 원금 **전환 카운트업**·그래프 **960px 세이프존**(종이 full-width·양옆 여백)·**은퇴원금 형광펜**·**배투실 워터마크**.
- 2026-07-29(멀티에이전트 리뷰 반영): 테이블 **헤더 글씨=본문 크기**·끝점 **$10M↑ 축약(fmtV)**·NOTE **세금 통화별**·편집기 **ACCUM_TOTAL 인트로/전환 포함**·THUMB 유령키 제거.
- 2026-07-30: **애플(AAPL)** 종목 추가(START_YEAR 2016·애플 로고 실루엣). 끝점 라벨 **겹침 회피 재작성**(위→아래·x근접시만 30px, 프로즌 참조 픽셀 동일). 테이블 **경고 문구(DISC)** 추가 → 카드 밖 하단·**2배 확대(32px)·간결화**. **현재 정본(freeze).**

관련 메모리: [[pg-golden-shorts-fire]] · 자매편 적립: [[pg-golden-shorts-accum]]
