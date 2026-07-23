# Global Cup Suite

`global_cup_refactored`(시장 분석 대시보드)와 `fire_feasibility`(FIRE 타당성 백테스트)를
**하나의 엔진 + 하나의 GUI**로 합친 통합 앱. 상단 탭으로 두 도구를 전환한다.

```
streamlit run app.py
```

## 구조

```
global_cup_suite/
├── app.py               # 진입점: set_page_config + inject_css + 상단 탭(segmented_control) → 선택 페이지 render() 호출
├── dashboard_page.py    # 🏆 Global Cup 대시보드 페이지 — render() 함수 노출
├── fire_page.py         # 🔥 FIRE 타당성 페이지 — render() 함수 노출
├── global_cup/          # 공유 엔진 패키지 (두 원본 패키지의 합집합)
│   ├── (공유 12개 모듈: analysis, charts, config, data_loader, dividend_reinvest,
│   │    formatting, golden_engine, high_scanner, market_config, scoring, ui, __init__)
│   ├── fire_engine.py         # FIRE 전용 (fire_feasibility에서)
│   ├── dividend_schedule.py   # FIRE 전용 (fire_feasibility에서)
│   ├── backtest_engine.py     # 대시보드 레거시 (미사용, 보존)
│   └── zigzag_engine.py       # 대시보드 레거시 (미사용, 보존)
├── data/                # tickers_*.csv (5) + ko_*.csv + fred_*.csv
└── requirements.txt
```

## 합친 방식

- **엔진**: 두 원본의 `global_cup/` 패키지는 공유 12개 모듈이 바이트 단위로 동일했다.
  합집합만 취했다 — 조정할 충돌이 없다.
- **GUI (멀티페이지 구조)**: 각 페이지는 `render()` 함수를 노출하는 **일반 import 모듈**
  (`dashboard_page`, `fire_page`)이다. 진입점 `app.py`가 상단 탭(`st.segmented_control`)에서
  고른 페이지의 `render()`만 호출 → 한 실행에 한 페이지만 렌더 → 위젯 키 충돌·yfinance
  이중 로딩이 없다. 각 페이지의 `st.set_page_config()`/`inject_css()` 두 줄만 진입점으로
  올렸다(페이지 안엔 `# [suite] hoisted to app.py:` 주석으로 흔적을 남겨둠).

### 왜 이 구조인가 (설계 메모)

- **`exec(compile(...))` 대신 `render()` 함수**: 예전엔 진입점이 페이지 스크립트를 문자열로
  읽어 `exec`했으나, 스택트레이스가 뭉개지고 정적 분석·단위 테스트가 불가능했다. 각 페이지
  본문을 `def render():`로 감싸 진짜 import 가능한 모듈로 바꿨다. 이제
  `streamlit.testing.v1.AppTest`로 두 탭을 헤드리스 실행해 예외를 잡을 수 있다.
- **네이티브 `st.navigation(position="top")`을 안 쓰는 이유**: `inject_css`가 헤더
  (`stHeader`)를 `2.5rem`로 줄여서(→ `global_cup/ui.py`), 그 헤더 안에 렌더되는 상단 nav가
  잘렸다. 헤더에 의존하지 않도록 `st.segmented_control`(네이티브 버튼) 탭바를 직접 그린다.
- **다크 테마**는 `.streamlit/config.toml`에서 네이티브 기본값으로 고정한다.

### 테스트

```
python -c "from streamlit.testing.v1 import AppTest; \
  at=AppTest.from_file('app.py', default_timeout=180); at.run(); \
  print('dashboard exc:', len(at.exception)); \
  at.session_state['suite_tool']='🔥  FIRE 타당성 백테스트'; at.run(); \
  print('fire exc:', len(at.exception))"
```

원본 `fire_feasibility/`, `global_cup_refactored/`는 그대로 보존돼 있다.
