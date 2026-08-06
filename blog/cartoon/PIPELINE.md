# 만화 백테스트 쇼츠 — 제작 파이프라인

**입력 2개만 주면 쇼츠 mp4까지 자동 생성**
1. `cartoon_8cut.png` — 8컷(4×2) 만화 이미지 1장
2. `scenario.json` — 종목·기간·금액·컷별 오버레이 정의

**출력**: `scenes/*.mp4`(컷별) → `cartoon_full.mp4`(1:1 통합) → `cartoon_shorts.mp4`(9:16)

---

## 파이프라인 단계

```
[8컷 PNG] ─┐
           ├─▶ ① 패널 추출 ──▶ panels/panel_1..8.png (정사각형·배경정규화)
[scenario]─┤
           ├─▶ ② 데이터 페치 ─▶ data/*.json (yfinance→평가액 시계열·추매반영)
           │
           └─▶ ③ 씬 빌드 ────▶ scenes/scene_N.html (컷별 오버레이 renderAt(t))
                    │
                    ▼
               ④ 렌더 (playwright 프레임캡처 → ffmpeg) ─▶ scenes/scene_N.mp4
                    │
                    ▼
               ⑤ 통합 (ffmpeg concat) ─▶ cartoon_full.mp4 (1080²)
                    │
                    ▼
               ⑥ 쇼츠 리프레임 (pad 9:16) ─▶ cartoon_shorts.mp4 (1080×1920)
                    │
                    └─(옵션)▶ ⑦ 자막편집기 HTML / TTS / 하드섭
```

### ① 패널 추출 `extract_panels.py`
- 4×2 그리드 경계 자동검출(여백/테두리 스캔) → 8컷 크롭
- 검은 테두리 제거(가장자리 30px 내 다크라인 검출)
- 배경 정규화(옅은 오프화이트 → 순백 255, 이음새 제거)
- 정사각형 패딩 → `panels/panel_1..8.png`
- **범용**(만화 무관, 그리드만 맞으면 재사용)

### ② 데이터 페치 `fetch_data.py`
- `scenario.tickers`의 각 종목 yfinance 종가/배당 수집(기간=buy_date~asof)
- 평가액 시계열 계산: `shares0 = 100만/price[buy]`, 추매일에 `+1000만/price[inj]` 주식 추가
- 산출: `data/<key>_series.json` (dates·value·pre·final·redFrom 등)
- **범용**(종목/날짜/금액 파라미터화)

### ③ 씬 빌드 `build_scene.py` — 오버레이 타입 라이브러리
컷마다 `scenario.panels[i].overlay` 타입에 파라미터를 넣어 씬 HTML 생성.
각 타입은 `renderAt(t)` 결정적 렌더 계약을 따름(프레임 캡처용).

| overlay 타입 | 용도 | 주요 params |
|---|---|---|
| `logo` | 종목 로고 표시(팝인·플로팅) | logos[], layout(가로/세로), pos |
| `cover_chart` | 만화 위 작은 차트 카드(가짜그래프 덮기) | series[], window, cover_rect |
| `returns_card` | 실제 수익 카드(카운트업) | series[], asof, cover_rect |
| `allin_gauge` | 추가투입 게이지 HUD | amount_each, anchor(팻말 위 등) |
| `injection_backtest` | 상승→추매 스텝→하락 백테스트 | series[], inj_idx, x_split, card_rect |
| `loss_counter` | 현재 손실 카운트다운 | totals, breakdown, cover_rect |
| `static` | 만화 원본 그대로(모션 없음) | (없음) |
| `checklist` | 체크리스트 순차 등장(교훈) | items[] |

- 각 타입은 배경=`panels/panel_i.png`, 오버레이만 다름
- **좌표는 배경 자동검출로 보정**(가짜그래프/텍스트박스/캐릭터 bbox 검출 → cover_rect·비가림 여백 산출)

### ④ 렌더 `render_scene.py`
- `scene_N_render.html`(rAF 자동시작 제거, `draw(k)`/`renderAt(t)` 노출)
- playwright chromium 1080² viewport, `window.__ready` 대기
- 프레임별 `renderAt(f/FPS*1000)` → screenshot → ffmpeg(libx264/yuv420p)
- **범용**(헤드리스 H.264 미지원이라 캔버스/DOM 렌더는 OK; 최종 concat/reframe만 mp4)

### ⑤ 통합 `concat.py`
- `scenario.panels` 순서대로 `scene_N.mp4` concat(동일 1080²·30fps)

### ⑥ 쇼츠 리프레임 `reframe.py`
- `scale=1004:1004, pad=1080:1920:center:white` → 좌우/상하 여백, 양옆 잘림 방지
- params: 내부폭(side margin), 세로정렬, 여백색, (옵션)상단 후킹·하단 로고

---

## scenario.json 스키마 (예시는 scenario.example.json)

```jsonc
{
  "title": "초보 투자자의 몰락",
  "cartoon": "cartoon_8cut.png",
  "tickers": { "SEC": {"name":"삼성전자","code":"005930.KS","color":"#16a34a"},
               "HYNIX": {"name":"SK하이닉스","code":"000660.KS","color":"#2563eb"} },
  "invest_each": 1000000,
  "buy_date": "2026-04-21",
  "injection": { "date": "2026-07-01", "amount_each": 10000000 },
  "asof": "2026-08-05",
  "panels": [
    { "n":1, "overlay":"logo",         "params":{ "use":["SEC","HYNIX"], "layout":"vertical", "anchor":"right_of_face" } },
    { "n":2, "overlay":"cover_chart",  "params":{ "use":["SEC","HYNIX"], "window":["buy_date","2026-06-05"] } },
    { "n":3, "overlay":"returns_card", "params":{ "use":["SEC","HYNIX"], "asof":"2026-06-05" } },
    { "n":4, "overlay":"allin_gauge",  "params":{ "anchor":"above_sign" } },
    { "n":5, "overlay":"injection_backtest", "params":{ "use":["SEC","HYNIX"], "end":"2026-07-14", "x_split":0.52 } },
    { "n":6, "overlay":"static" },
    { "n":7, "overlay":"loss_counter", "params":{ "use":["SEC","HYNIX"], "asof":"asof" } },
    { "n":8, "overlay":"checklist",    "params":{ "items":["원래 기준 지키기","손절 원칙","무리하지 않기"] } }
  ],
  "shorts": { "inner_width":1004, "bg":"white", "valign":"center" }
}
```

## 에피소드 구조 (episodes/epN)
```
cartoon/
  pipeline/            # 공유 엔진(모든 에피소드 공용) — 건드리지 않음
  episodes/
    ep1/               # 완성: 초보 투자자의 몰락 (삼성·하이닉스 고점추매)
      cartoon.png      # 8컷 만화 (입력)
      scenario.json    # 시나리오 (입력)
      out/             # 산출: ep1_full.mp4 · ep1_shorts.mp4 · panels/ · scenes/
    ep2/
      cartoon.png      # ← 8컷 만화 넣기
      scenario.json    # ← tickers·날짜·금액·컷별 overlay 수정 (id:"ep2")
```
- 산출물명은 `scenario.id`(없으면 폴더명) 기준 → `<id>_full.mp4` / `<id>_shorts.mp4`.

## 실행 CLI
```bash
cd cartoon/pipeline
python build.py --scenario ../episodes/ep1/scenario.json           # 전체(패널→쇼츠)
python build.py --scenario ../episodes/ep2/scenario.json --only 5  # 5번 씬만 재생성
python build.py --scenario ../episodes/ep2/scenario.json --start concat  # 씬 재사용, 통합부터
python build.py --scenario ../episodes/ep2/scenario.json --no-shorts      # 1:1까지만
```

### 새 에피소드(ep2) 만들기
1. `episodes/ep2/cartoon.png` 에 8컷 만화 배치
2. `episodes/ep2/scenario.json` 편집 — 종목(tickers)·매수일·추매일/금액·asof·컷별 overlay/params
3. `python build.py --scenario ../episodes/ep2/scenario.json`

## 현재 상태 / 남은 일반화 작업
- ✅ **범용 완성**: ①패널추출 ②데이터페치 ④렌더 ⑤통합 ⑥리프레임 (이미 스크립트로 동작)
- 🔶 **템플릿화 필요**: ③ 오버레이 7종을 각각 `build_scene.py`의 파라미터 함수로 승격
  (지금은 컷별 개별 스크립트 `scene_page*.html` 생성기로 분산 — 로직은 완성, 인터페이스만 통일하면 됨)
- 🔶 **좌표 자동보정**: 가짜그래프/텍스트박스/캐릭터 bbox 검출을 유틸 함수로(현재 컷마다 수동 검출)
- ⬜ **드라이버** `pipeline/build.py`(config→단계 오케스트레이션)

## 재사용 자산(이미 존재)
- 패널추출·배경정규화·데이터페치·프레임렌더·concat·reframe 로직 → 본 세션 스크립트
- 오버레이 렌더 로직 → `scene_page1/3/4/5/7.html`, `scene_cover.html`(각 타입의 레퍼런스 구현)
- 자막편집기 → `subtitle_editor.html`(영상+자막 편집·SRT/VTT 내보내기)

---

# 🔩 표준/보강 (EP3 골든 이후 확립)

## 프레임-우선 레이아웃 (권장)
- 그래프 자리(프레임)를 먼저 확정: `episodes/_frame_layout.json`(셀-프랙션·가로비율) · 시각 템플릿 `_frame_template.png`.
- 만화는 그 자리를 **박스 윤곽선·플레이스홀더 없이 빈 흰 공간**으로만 남긴다. 캐릭터·말풍선은 프레임 밖(차트컷 ⑥⑦⑧은 캐릭터 좌상단 작게).
- 빈 프레임은 자동검출 안 되므로 **예정 좌표를 그대로 슬롯으로** 사용: `_frame_slots.json` (셀 종횡비 ar로 stage 변환 `x=((1-ar)/2+cfx*ar)*1080`, `y=cfy*1080`). 슬롯은 에피소드 공통 상수.
- AI 전달물 = 빈 템플릿(캐릭터·프레임 고정) + 컷별 텍스트만. 가이드 `episodes/_DRAW_HANDOFF.md`.

## 자동 2초 hold (auto-hold)
- 수치 슬라이드는 **애니 정착 후 2초 hold**가 표준.
- 시나리오 `panels[n]`에 `"hold": 2.0` → `build.py`가 `render_scene(autohold=2.0)` 호출.
- `render.py`가 **프레임 변화(md5) 감지**로 애니 종료(마지막 정착)를 찾아 +2초 뒤 종료. duration 수동 지정 불필요.
- 다단계 애니(표 셀 순차 등)는 변화 재발생 시 정착 리셋 → 마지막 정착 기준.

## 오버레이 스타일 규칙
- 카드 배경 = 회색 10% 패널 `rgba(120,120,125,0.10)`.
- **% + 실제 금액(만원) 동시 표기**. 표 셀 = 금액(위)+배수(아래).
- 강조 수치는 크게 모션(바운스). 폰트는 슬롯 크기 비례, 넉넉히.
- 그리드 추출은 실제 그리드선 검출(`panels._grid_edges`) — 균등분할 폴백. 하단 캡션바 제외.

## scenario.json 추가 필드
- `panels[n].hold` (초): 지정 시 auto-hold(정착+hold). 없으면 `durations[n]`(고정).
- 데이터 모드: `benchmark` 키 있으면 `build_income`(고분배 vs 벤치마크), `ticker`+`invest_total`이면 `build_dca`, `tickers`+`injection`이면 `build_series`.

## ❄️ 골든
- **EP3 = FROZEN 골든** (`episodes/ep3/GOLDEN.md`). 위 표준을 모두 반영. 개선은 새 에피소드/브랜치에서.
