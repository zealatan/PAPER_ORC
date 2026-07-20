"""
🏆 Global Cup Suite — 하나의 엔진, 하나의 GUI

두 도구를 상단 탭으로 합친 통합 진입점:
  • 🏆 Global Cup 대시보드 — 전고점 낙폭 · 배당 · 재투자 백테스트 (dashboard_page.py)
  • 🔥 FIRE 타당성 백테스트 — 은퇴 목돈 인출 생존/고갈 시뮬레이션 (fire_page.py)

두 페이지는 `global_cup/` 패키지(엔진)를 공유한다. 상단 탭(st.segmented_control)에서
고른 페이지 스크립트만 실행하므로 위젯 키 충돌·yfinance 이중 로딩이 없다.

주의: 예전엔 st.navigation(position="top")을 썼으나 inject_css가 헤더를 찌그러뜨려
탭이 숨겨졌고, 이어서 st.radio를 탭처럼 스타일했으나 라디오 동그라미를 display:none
처리하면서 실제 클릭 대상(input)까지 숨겨져 브라우저에서 탭 전환이 안 됐다. 그래서
클릭이 확실한 st.segmented_control(네이티브 버튼)로 교체했다. 다크 테마는
.streamlit/config.toml에서 네이티브 기본값으로 고정한다.

Run:
  streamlit run app.py
"""
import os
import streamlit as st

# set_page_config는 어떤 st 명령보다 먼저, 딱 한 번.
st.set_page_config(page_title="Global Cup Suite", page_icon="🏆", layout="wide")

# 공용 테마 — 두 페이지가 같은 inject_css(다크 올리브/크림/라임)를 공유한다.
from global_cup.ui import inject_css
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
_HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = {
    "🏆  Global Cup 대시보드": "dashboard_page.py",
    "🔥  FIRE 타당성 백테스트": "fire_page.py",
}
_options = list(TOOLS)
choice = st.segmented_control("도구 선택", _options, default=_options[0],
                              label_visibility="collapsed", key="suite_tool")
if not choice:                      # 아무 것도 선택 안 된 순간엔 첫 탭으로
    choice = _options[0]

# 선택된 페이지 스크립트를 그대로 실행 (원본 flush-left 본문 → 들여쓰기/문자열 파손 없음).
# 한 번에 한 페이지만 실행되므로 위젯 키 충돌이 없다. 페이지 내부의 st.stop()은
# 정상적으로 전체 실행을 멈춘다(탭바는 이미 위에서 렌더됨).
_page = os.path.join(_HERE, TOOLS[choice])
with open(_page, encoding="utf-8") as _f:
    _src = _f.read()
exec(compile(_src, _page, "exec"), {"__name__": "__main__", "__file__": _page})
