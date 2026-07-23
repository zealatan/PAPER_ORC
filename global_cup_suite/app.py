"""
🏆 Global Cup Suite — 하나의 엔진, 하나의 GUI

두 도구를 상단 탭으로 합친 통합 진입점:
  • 🏆 Global Cup 대시보드 — 전고점 낙폭 · 배당 · 재투자 백테스트 (dashboard_page.render)
  • 🔥 FIRE 타당성 백테스트 — 은퇴 목돈 인출 생존/고갈 시뮬레이션 (fire_page.render)

두 페이지는 `global_cup/` 패키지(엔진)를 공유한다. 각 페이지는 `render()` 함수를
노출하는 일반 모듈이며, 상단 탭(st.segmented_control)에서 고른 페이지의 render()만
호출한다. 한 실행에 한 페이지만 렌더되므로 위젯 키 충돌·yfinance 이중 로딩이 없다.

멀티페이지 구조 메모:
  - 페이지는 import 가능한 모듈(dashboard_page / fire_page)이고 각자 render()를 가진다.
    (예전엔 exec(compile(open(...)))로 스크립트를 문자열 실행했으나, 스택트레이스·정적
    분석·테스트가 어려워 render() 함수 호출 방식으로 정리했다.)
  - Streamlit 네이티브 st.navigation(position="top")은 쓰지 않는다: inject_css가 헤더
    (stHeader)를 2.5rem로 줄여 그 안에 렌더되는 상단 nav가 잘렸다(global_cup/ui.py 참고).
    그래서 헤더에 의존하지 않는 st.segmented_control(네이티브 버튼) 탭바를 직접 그린다.
  - 다크 테마는 .streamlit/config.toml에서 네이티브 기본값으로 고정한다.

Run:
  streamlit run app.py
"""
import streamlit as st

# 페이지 모듈은 render() 함수만 노출한다. import 시엔 st 명령을 부르지 않으므로(모듈 상단은
# import/상수뿐) set_page_config보다 먼저 import해도 안전하다.
import dashboard_page
import fire_page
from global_cup.ui import inject_css

# set_page_config는 어떤 st 명령보다 먼저, 딱 한 번.
st.set_page_config(page_title="Global Cup Suite", page_icon="🏆", layout="wide")

# 공용 테마 — 두 페이지가 같은 inject_css(다크 올리브/크림/라임)를 공유한다.
inject_css()

# ── 상단 탭바 스타일: segmented_control을 크고 또렷한 탭 버튼으로 ────────────────────
st.markdown("""
<style>
div[data-testid="stButtonGroup"], div[data-testid="stSegmentedControl"] {
    margin:.2rem 0 1.5rem;
}
/* 각 탭 버튼 */
div[data-testid="stButtonGroup"] button, div[data-testid="stSegmentedControl"] button {
    font-family:Georgia,"Times New Roman",serif !important;
    font-size:1.05rem !important; font-weight:600 !important;
    padding:.62rem 1.5rem !important; letter-spacing:-.3px;
}
/* 선택된 탭 강조 (라임) */
div[data-testid="stButtonGroup"] button[aria-checked="true"],
div[data-testid="stSegmentedControl"] button[aria-checked="true"],
div[data-testid="stButtonGroup"] button[kind="segmented_controlActive"] {
    background:linear-gradient(135deg,#f7ffd4,#8dbb55) !important;
    color:#14200d !important;
}
</style>
""", unsafe_allow_html=True)

# ── 상단 탭 = 두 도구 ────────────────────────────────────────────────────────────
# 선택된 페이지의 render()만 호출해 그 페이지만 그린다.
TOOLS = {
    "🏆  Global Cup 대시보드": dashboard_page.render,
    "🔥  FIRE 타당성 백테스트": fire_page.render,
}
_options = list(TOOLS)
choice = st.segmented_control("도구 선택", _options, default=_options[0],
                              label_visibility="collapsed", key="suite_tool")
if not choice:                      # 아무 것도 선택 안 된 순간엔 첫 탭으로
    choice = _options[0]

# 선택된 페이지의 render()만 호출 → 한 실행에 한 페이지만 렌더 → 위젯 키 충돌 없음.
# 페이지 내부의 st.stop()은 StopException으로 전파되어 정상적으로 전체 실행을 멈춘다
# (탭바는 이미 위에서 렌더됨).
TOOLS[choice]()
