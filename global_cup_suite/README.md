# Global Cup Suite

`global_cup_refactored`(시장 분석 대시보드)와 `fire_feasibility`(FIRE 타당성 백테스트)를
**하나의 엔진 + 하나의 GUI**로 합친 통합 앱. 상단 탭으로 두 도구를 전환한다.

```
streamlit run app.py
```

## 구조

```
global_cup_suite/
├── app.py               # 진입점: set_page_config + inject_css + st.navigation(position="top")
├── dashboard_page.py    # 🏆 Global Cup 대시보드 페이지 (원본 대시보드 app.py 본문)
├── fire_page.py         # 🔥 FIRE 타당성 페이지 (원본 FIRE app.py 본문)
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
- **GUI**: `st.navigation(..., position="top")`으로 상단 탭 전환. **선택된 페이지 스크립트만
  실행**되므로 위젯 키 충돌·yfinance 이중 로딩이 없다. 각 페이지 파일은 원본 `app.py`와
  동일하며, 각자 호출하던 `st.set_page_config()`/`inject_css()` 두 줄만 진입점으로 올렸다
  (해당 줄은 `# [suite] hoisted to app.py:` 주석으로 남겨둠).

원본 `fire_feasibility/`, `global_cup_refactored/`는 그대로 보존돼 있다.
