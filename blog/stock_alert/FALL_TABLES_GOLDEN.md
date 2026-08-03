# 낙폭 테이블 통합 쇼츠 — GOLDEN TEMPLATE ❄️FROZEN

> **상태: 동결(FROZEN) · 2026-08-03.** 이 문서 + `rec/gen_fall_reel.py` + `rec/build_fall_reel.py` +
> `fall_scan.py`(--asof) + `assets/shorts/{thumb_fall_multi,mascot_knit}.png` + `deck/logos/*` = **정본**.
> 앞으로 "주간 4시장 낙폭 테이블 쇼츠"는 이 템플릿이 기준. 값·레이아웃을 바꾸면 이 문서도 같이 갱신.
> 레퍼런스 빌드: **week31**(2026-07-31 금요일 기준). 산출물 `shorts/short_fall_tables_wNN.mp4`(1080×1920·30fps·약 38초).

그래프 카드 없이 **미국·한국·유럽·ETF 4시장의 전고점 대비 낙폭 TOP10을 표 한 장씩**으로 보여주는 쇼츠.
디자인은 [`golden_shorts_fire`](../golden_shorts_fire/golden_shorts_fire.md)에서 상속(검정 배경·흰 종이카드·Pretendard·마젠타 강조).

---

## 0. 재현 (주간)

```bash
cd blog/stock_alert
WK=31; ASOF=2026-07-31          # ASOF = 그 주 금요일(마지막 종가일)

# 1) 4시장 스캔 → data/fall_weekNN.json  (--asof로 날짜 통일)
for m in 미국 한국 유럽 ETF; do
  python3 fall_scan.py --market $m --week $WK --top 10 --min-drop 20 --min-size 0 --asof $ASOF
done

# 2) 썸네일(인트로) 준비 — 사람이 제작해 저장 (thumb 편집기/디자인)
#    assets/shorts/thumb_fall_multi.png  (1080×1920, 없으면 생성 인트로로 폴백)

# 3) 애니 HTML 생성 → 녹화(mp4)   ※ 녹화는 playwright 설치된 miniconda python으로
python3 rec/gen_fall_reel.py --week $WK
/home/messi/miniconda3/bin/python3 rec/build_fall_reel.py --week $WK
#    → shorts/short_fall_tables_wNN.mp4
```

`_fall_reel.html`·`_reel_build/`·`shorts/*.mp4`은 **재생성물 → gitignore.** 소스·에셋·데이터·로고만 커밋.

---

## 1. 파일 구성

```
blog/stock_alert/
├── fall_scan.py               # ★4시장 낙폭 스캔(시총순 대형주). --asof로 마지막 종가일 고정
├── rec/gen_fall_reel.py       # ★애니 HTML 생성기 → _fall_reel.html (폰트·종이·배지·로고·데이터 임베드)
├── rec/build_fall_reel.py     # ★playwright(chromium) 녹화 → mp4 (miniconda python)
├── rec/gen_table.py           # (구) 정적 표 PNG — 구 쇼츠 파이프라인용. KR_NAME 공유
├── FALL_TABLES_GOLDEN.md      # ★이 문서(정본 스펙)
├── assets/shorts/
│   ├── thumb_fall_multi.png   # 인트로/썸네일 카드(주간 제작·교체)
│   └── mascot_knit.png        # 배투실 뜨개 마스코트 마크(누끼본, 우상단 워터마크)
├── deck/logos/<티커앞>.png     # 종목 로고(누적 재사용). 미국=티커·한국=6자리·유럽=티커앞. ETF는 안 씀
└── data/fall_weekNN.json      # fall_scan 산출(레퍼런스: fall_week31.json)
```

재사용 에셋(golden_shorts_fire에서 참조·읽기전용): `blog/fonts/PretendardVariable.woff2`,
`golden_shorts_fire/assets/paper_b64.txt`(종이), `.../assets.json` BADGE(폴백용).

---

## 2. 영상 구성 (약 38초)

| # | 페이지 | 길이 | 내용 |
|---|--------|------|------|
| 0 | 인트로/썸네일 | 2.6s | `thumb_fall_multi.png` (4국기 스티커 + KOREA USA EU ETF + 하락 TOP10 + week) |
| 1 | 미국 표 | 8.7s | 낙폭 TOP10 (애니 1.7s + 정지 7.0s) |
| 2 | 한국 표 | 8.7s | 〃 |
| 3 | 유럽 표 | 8.7s | 〃 (보통 TOP9) |
| 4 | ETF 표 | 8.7s | 〃 (로고 없음) |

- 타이밍 조절: `gen_fall_reel.py`의 `INTRO_MS`·`MK_MS`(=애니 ≈1.7s + 정지). 현재 정지 **7초**.
- 페이지 전환: 페이드(`.pg` opacity .5s). **구독 아웃트로 없음.**

## 3. 디자인 (golden_shorts_fire 상속)

- **검정 배경 + 흰 종이질감 카드**(paper_b64, radius 26, soft shadow) + **Pretendard**(100–900).
- **타이틀**: `<국기> <시장> 주식 <b>하락</b> TOPn 📉` — `하락`=마젠타 `#d12e77`, 나머지 흰색.
- **표**: 열 = [순위][로고][종목명][전고점比]. ETF는 로고 열 없음(운용사 로고 무의미).
  - 순위·낙폭% = 라즈베리 `#c2255c`, 종목명 = `#141414`, th = `#8a857c`, 행 구분선 hairline.
  - **낙폭 표기 `▼X.X%`**(빨강). 값은 카운트업으로 0→최종.
  - 종목명 길면 값 앞에서 잘림(폭 인식 truncation, ETF 긴 이름 대비).
- **로고**: `deck/logos/<티커앞>.png` 자동 임베드(height 46px). 흰 카드용이라 **순백 로고 금지**(컬러/검정).
- **마스코트 마크**: `mascot_knit.png`(뜨개 누끼) 우상단, height 132px, soft shadow. (배투실 배지 대체.)
- **페이지 표시**: 카드 하단 중앙 `현재 / 총합`(현재=흰색·총합=회색). ⚠️경고문 없음.
- **모션**: 카드 아래→위 진입 · 타이틀 슬라이드다운 · **행 스태거 슬라이드인**(delay=i×0.065s) · **낙폭% 카운트업**(ease-out) · 페이지 페이드.

## 4. 데이터 규칙 (fall_scan)

- 트리거: 전고점 대비 **하락 ≥ 20%**. 선정: **시총 내림차순 TOP10**(min-size 0 → 시총순 그대로).
- 표에 쓰는 값은 **낙폭%(통화 무관)** — 유럽 혼합통화도 표엔 영향 없음.
- **`--asof <그주 금요일>`**: `download_price(end+1)`로 그 날 종가까지 잘라 **시장 간 날짜 통일**. `d["date"]`=asof.
- 데이터 원천 = 공유 엔진 `global_cup_suite/global_cup/high_scanner.scan_market`(종목별 독립 스캔). **수정 금지.**

### 알려진 한계 (허용)
- **유럽은 asof보다 하루 빠를 수 있음**(예: 금 7/31 요청 → 목 7/30). 원인: `data_loader.download_price`가
  `auto_adjust=False`로 받는데 **EU 종목의 최신 미조정 종가가 NaN**이라 `dropna`로 떨어짐(캐시·yfinance 버그 아님).
  공유 엔진이라 미수정 → **그대로 둠**(낙폭 차이 ~0.1%로 무시 가능). 강제로 맞추려면 fall_scan에서
  종목별 `auto_adjust=True` 재조회로 종가·낙폭을 패치하는 로컬 우회 필요(현재 미구현).

## 5. 새 주차 만들기

1. **입력(사람)**: 주차 번호 `WK`, 그 주 금요일 `ASOF`.
2. **썸네일(사람)**: `assets/shorts/thumb_fall_multi.png` 교체(주차·문구 갱신).
3. **로고(없을 때만)**: `deck/logos/<티커앞>.png` — 멀티에이전트로 Wikimedia SVG→투명 PNG(흰 카드 가시성 확인).
   한국 새 종목은 `gen_fall_reel.py`·`gen_table.py`의 `KR_NAME`에 한글명도 추가.
4. **생성**: fall_scan(4시장) → gen_fall_reel → build_fall_reel.

스펙(레이아웃·색·애니·타이밍)은 주차 무관 고정. **주차별 입력(썸네일·데이터·신규 로고)만 교체.**

---

## 6. 이력
- 2026-08-03: 초판 동결. 그래프 카드형 → **테이블 통합**으로 전환. golden_shorts_fire 디자인 이식(종이카드·Pretendard·
  마젠타·초록/빨강). 모션(행 스태거·카운트업·카드 전환). 기업 로고 열(미국·한국·유럽, ETF 제외, 신규 12로고 확보).
  경고문 → 페이지표시. 배투실 배지 → 뜨개 마스코트 누끼. `--asof`로 4시장 금요일 종가 통일(EU 하루 지연 허용).
  업로드 썸네일을 인트로로. 정지 7초.

관련 메모리: [[stock-alert-project]] · 디자인 원본: [[pg-golden-shorts-fire]]
