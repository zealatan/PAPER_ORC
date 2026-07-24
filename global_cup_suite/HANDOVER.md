# global_cup_suite 인수인계 (HANDOVER)

> 최종 업데이트: 2026-07-24 · 작성 세션 주제: **FIRE 물가 반영(실질 인출) 기능 추가**

---

## 0. 지금 상태 한 줄 요약

FIRE 타당성 백테스트에 **물가 반영(실질 인출) 기능**을 추가했다. 엔진은 원래 `fixed_real`을
지원했는데 UI가 안 쓰고 있었다 → FIRE 페이지에 토글을 붙여 연결했다. **미커밋 상태.**

---

## 1. 이번 세션의 현재 수정사항 (⚠️ 아직 미커밋)

`git status` 기준 미커밋 변경:

| 파일 | 상태 | 내용 |
|---|---|---|
| `fire_page.py` | `M` (+35/-1) | 물가 반영 토글 + 합성 CPI + 엔진 연결 + 가정 캡션 |
| `_validation/validate_fire_inflation.py` | `??` (신규) | 물가 반영 회귀 테스트 (13 checks) |

### 무엇을 왜 바꿨나
- **문제**: FIRE 페이지가 `run_fire_backtest_multi(..., strategy="fixed_nominal")`로 하드코딩되어
  **월 생활비가 명목 고정**이었다. 물가 무시 → 은퇴 후반 실질 구매력 감소를 반영 못 해
  결과가 **낙관적**으로 나왔다("생존"이 실제론 "고갈"일 수 있음).
- **엔진은 이미 지원**: `global_cup/fire_engine.py`는 `strategy="fixed_real"` + `cpi` 시리즈로
  물가 반영을 지원한다(`need = (annual_withdrawal/ppy) * cpi(d)/cpi_base`). UI 연결만 없었다.

### fire_page.py 변경 상세
1. 입력부(은퇴 자금/월 생활비 바로 아래)에 한 줄 추가:
   - `물가 반영 (실질 인출)` 토글 — 기본값 **ON** (`key`는 currency별로 자동 분리)
   - `연 물가상승률 (%)` 입력 — 기본 **2.5%**, 토글 OFF면 disabled, `key=f"infl_{currency}"`
2. 엔진 호출 직전, 토글 ON이면 **합성 CPI 시리즈** 생성:
   - 은퇴 시작일=1.0 앵커, 연 `inflation_rate%`로 월별 상승
   - `pd.date_range(start, end, freq="MS").union([start])` + `(1+r)^years`
3. 엔진 호출: `strategy=fire_strategy`(ON이면 `fixed_real`, 아니면 `fixed_nominal`) + `cpi=cpi_series`
4. verdict 아래 **가정 캡션**: ON이면 "💡 물가 반영 ON · …", OFF면 "⚠️ 물가 반영 OFF · … 낙관적일 수 있습니다."

### 설계 결정 (기억할 것)
- **기본값 ON**: FIRE에서 실질 인출이 정확한 기본값. 명목 고정은 결과를 왜곡하므로.
- **물가율 = 사용자 입력(합성 CPI)**, FRED 실측 CPI 아님:
  - 이유: 6개 마켓(US/ETF/Global/Korea/Japan/EU) **전체에 일관 적용**하기 위함.
    실측 CPI(`data/fred_CPIAUCSL.csv`=미국, `data/fred_KORCPIALLMINMEI.csv`=한국)는
    **미국·한국만 있어** 일본/EU/글로벌에 공백이 생긴다. 입력식은 투명하고 스트레스 테스트도 쉬움.
- **CPI 앵커 의미론(검증으로 확정)**: `cpi_base`는 **은퇴 시작(buy_date)=1.0**. 첫 인출(시작
  1개월 뒤)은 이미 ~1개월치 물가 반영(예: 1000→1002.10). 이건 버그 아니라 올바른 실질 동작.

---

## 2. 검증 (완료, 전부 통과)

| 층 | 방법 | 결과 |
|---|---|---|
| 엔진 정확성 | `python -m _validation.validate_fire_inflation` (합성·네트워크 불필요) | **13 passed, 0 failed** |
| UI end-to-end | `AppTest`로 USD·KRW 두 통화 ON/OFF | 예외 0 |
| 정적 | `ruff check fire_page.py _validation/validate_fire_inflation.py` | 물가 코드 새 경고 없음 |

`validate_fire_inflation.py`가 검증하는 것: 명목 앵커 · **fixed_real 폐쇄형 일치(오차 0)** ·
rate=0≡명목 · 단조성(물가율↑→총인출↑·생존↓) · **판정 뒤집힘 실증** · 다종목/초단기 창.

> 실행법: repo 루트(`global_cup_suite/`)에서 `python -m _validation.validate_fire_inflation`
> (`python _validation/…`는 import 경로 때문에 실패 — 기존 `validate_fire.py`와 동일한 관례.)

---

## 3. 다음 사람이 할 일

- [ ] **커밋** — 현재 `main` 브랜치이므로 브랜치 분리 후 커밋 권장. 예:
      `git checkout -b fire-inflation && git add global_cup_suite/fire_page.py global_cup_suite/_validation/validate_fire_inflation.py`
- [ ] (선택) **하이브리드 CPI**: 미국·한국은 FRED 실측 CPI(`data/fred_*.csv`) 사용, 나머지
      마켓만 입력값 폴백. 지금은 전 마켓 입력값 방식으로 통일. 요청 시 확장.
- [ ] (선택) 물가율 프리셋(예: 한국 2.5% / 미국 2% 기본)을 마켓별로 다르게.

---

## 4. 이번 세션에서 이미 커밋된 배경 작업 (참고)

이 세션 초반 작업은 이미 커밋됨(`mcdonald`/`mcd` 커밋에 포함). 현재 미커밋 아님:
- **exec → render() 리팩터링**: `dashboard_page.py`·`fire_page.py`를 `render()` 함수 모듈로,
  `app.py`가 import 후 `TOOLS[choice]()` 호출. (`exec(compile(...))` 제거)
- **README.md** 최신화(segmented_control·render 구조 반영).
- **제품 기획안** 문서: `docs/PRODUCT_PLAN.md`(구독 SaaS 기획), `docs/ROADMAP_TASKS.md`
  (Phase 0~3 실행 태스크, 조사 기반 — Stripe 한국 불가·데이터 라이선스 비용 등 중대 정정 포함).
  → 제품화(로그인/결제/DB) 방향은 이 두 문서가 진입점.

---

## 5. 파일 지도 (핵심)
- `app.py` — 진입점(상단 탭 → 페이지 `render()` 호출)
- `dashboard_page.py` / `fire_page.py` — 각 페이지, `render()` 노출
- `global_cup/fire_engine.py` — FIRE 엔진(`fixed_nominal`|`fixed_real`|`pct_portfolio`)
- `global_cup/ui.py` — 공용 `inject_css`(헤더 2.5rem 축소 → 네이티브 top-nav 못 쓰는 이유)
- `_validation/` — 독립 실행 검증 스크립트(`python -m _validation.<name>`)
- `data/` — tickers_*.csv, fred_*.csv(CPI/환율)
- `docs/` — 제품 기획안·로드맵
