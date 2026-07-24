# STOCK_ALERT — 덱(슬라이드) 설계 확정본

> 주간 전고점 대비 낙폭 카운트다운 영상. MCD/PG 덱 파이프라인을 상속(A단계)하되,
> 씬 구성은 아래대로 **재정의**한다. build_deck 이 `data/weekN.json` 에서 씬을 **동적 생성**.

## 확정 결정 (2026-07-24)
- 포맷: **롱폼 1편 + 쇼츠 2~3편**, 3시장 통합 1영상, 낙폭 랭킹만(단순 앵글)
- 카운트다운 깊이: **시장별 TOP5, 종목당 개별 슬라이드(15 drawcard)** · 영상 ~4분
- drawcard 차트: **전고점→현재 미니 라인차트** (기존 `enginechart` 라인 코어 재활용, 전고점·현재 마크, 하락 강조)
- 전고점 정의: 마지막 ZigZag 전저점 이후 최고가(스윙고점, ATH 아님) · threshold 15% (trigger %와 별개)

## 씬 구성 (22씬 · weekly_scan.json 에서 동적 생성)
| # | tpl | 씬 | 비고 |
|---|---|---|---|
| 1 | `notice` | 유의사항·경고 | ♻️ 재사용 |
| 2 | `alerthook` | 훅 — "이번 주 전고점에서 가장 많이 무너진 종목은?" (TOP1 티저) | 🆕 |
| 3 | `sectint` | ① ETF 낙폭 TOP5 전환 | ♻️ |
| 4–8 | `drawcard` ×5 | ETF 5위→1위 | 🆕 핵심 |
| 9 | `sectint` | ② 미국 주식 낙폭 TOP5 | ♻️ |
| 10–14 | `drawcard` ×5 | 미국 5→1 | 🆕 |
| 15 | `sectint` | ③ 한국 주식 낙폭 TOP5 | ♻️ |
| 16–20 | `drawcard` ×5 | 한국 5→1 | 🆕 |
| 21 | `ranktop` | 통합 낙폭 TOP3 (시장 무관) | 🆕 (hbars2 변형) |
| 22 | `card` | 마무리 · 다음 주 예고 · 구독 | ♻️ |

## 신규 TPL 스펙

### `drawcard` (종목 1개 = 슬라이드 1개, 카운트다운 주력)
표시 요소:
- 순위 배지 `#5..#1` + 카테고리(🇺🇸/🇰🇷/📊)
- 종목명 · 티커
- **큰 낙폭 `▼ X.X%`** (빨강, 시선 집중)
- 전고점→현재 **미니 라인차트**: 전고점 마크(날짜·가격) → 현재 마크(날짜·가격), 하락 구간 강조
- 한 줄 이유 `💬 "…"` (뉴스 큐레이션 — 수동/리서치 슬롯)

데이터 필드(스캐너 출력 그대로):
`label · ticker · high_date · high_price · current_price · current_date · drawdown_pct` + `reason`(신규)

### `alerthook` (훅)
- TOP1 종목 낙폭을 티저(블러/실루엣) → 궁금증 유발. 로고 + 2행 카피.

### `ranktop` (통합 TOP3)
- 시장 무관 낙폭 상위 3개를 한 화면. hbars2(가로 막대) 변형 — 시장 배지 + 낙폭 막대.

## TPL 재사용/신규 요약
- ♻️ 재사용: `notice` · `sectint` · `card` · `enginechart`(라인차트 코어)
- 🆕 신규: `alerthook` · `drawcard` · `ranktop`

## 데이터 계약 — `data/weekN.json`
```json
{
  "week": 1,
  "date": "2026-07-24",
  "markets": {
    "ETF":  [{"label":"…","ticker":"…","high_date":"…","high_price":0,
              "current_price":0,"current_date":"…","drawdown_pct":-0.0,"reason":"…"}, "…(5)"],
    "미국": ["…(5)"],
    "한국": ["…(5)"]
  },
  "top3": ["…(3, 시장무관)"]
}
```
- `markets`·`top3` = weekly_scan 러너가 `scan_market()` 결과에서 TOP5/TOP3 추출.
- `reason` = 뉴스 큐레이션(반자동) 채움.

## build_deck 적응 (A단계에서)
- MCD build_deck 의 FIRE/strategy 씬 생성부 → 위 매핑으로 교체:
  `for market in [ETF, 미국, 한국]: sectint + drawcard×5` + notice/alerthook/ranktop/card.
- gen_dec_edit 의 하드코딩 SCENES(24) → deck json 에서 제목·tpl 유도(동적 씬 수 대응).

## 다음 단계
**A. MCD 스캐폴딩을 `blog/stock_alert/`로 복제** → 덱 렌더러·build_deck·gen_dec_edit·edit_server 상속 →
위 씬/TPL로 재정의. (복제 시 12MB 덱 HTML base64 무결성 유지 — PG 클론 레시피 기준.)
