# blog/ — 배투실 영상 워크스페이스 (다중 세션 공유)

이 디렉터리 아래에서 **여러 Claude 세션이 서로 다른 종목/프로젝트를 동시에** 작업합니다
(예: 8090=PG, 8091=stock_alert). 충돌을 막기 위해 아래 온보딩 규칙을 **세션 시작 시 반드시** 따르세요.

## 🚦 세션 시작 프로토콜 (필수)
1. **먼저 읽기**: [`architecture_docs/SESSION_HANDOFF.md`](architecture_docs/SESSION_HANDOFF.md) — 지금 어떤 세션이 어떤 종목/포트를 잡고 있는지 + 동시성 규칙. 이어서 [`architecture_docs/EDIT_SAVE_GUIDE.md`](architecture_docs/EDIT_SAVE_GUIDE.md) — 편집·저장 구조.
2. **자기 작업 등록**: `SESSION_HANDOFF.md`에 "이 세션 = <종목>, 포트 <N>" 한 줄 추가(또는 회신 섹션에 기록).
3. **끝나면** 자기 상태 갱신(작업 종료/인계 사항).

## ⚠️ 동시성 규칙 (락 미구현 — 사람/세션이 지킴)
- 🟢 **다른 종목**끼리는 자유롭게 병렬 (파일이 `<STOCK>/spec`·`<STOCK>/deck`로 분리됨).
- 🔴 **같은 종목을 두 세션/두 탭이 동시 저장 금지** — JSON 덮어쓰기 유실 + 13MB `*_v1.html` 동시 write로 손상. **"한 종목엔 한 세션."**
- 🔴 남이 잡은 종목, 공유 엔진 `global_cup_suite/global_cup/`은 합의 없이 건드리지 말 것.
- edit_server(`pipeline/edit_server.py`)는 `stock` 파라미터로 라우팅 → 서버 하나가 모든 종목 처리. 자기 포트가 겹치지 않게.

## 💾 편집·저장 핵심 (상세는 EDIT_SAVE_GUIDE.md)
- **JSON = 원본 · HTML = 생성물.** GUI 편집 = JS가 JSON에 저장 → 서버가 컴파일러 실행해 HTML 재생성.
- **반드시 서버 주소(`http://<host>:<port>`)로 접속.** `file://`로 로컬 HTML 직접 열면 저장 POST가 갈 곳이 없어 **유실**됨(= "편집 자꾸 원복"의 원인). 예외: 자립형 `prototypes/thumbs/thumb_editor.html`.
- 영구저장 버튼("🚀 덱에 반영"/"저장(영구)"/"💾 자막 저장")을 눌러야 JSON에 박힘. 안 누르면 localStorage 임시본만 남아 유실.

## 🔀 git — 공유 브랜치 주의
- 여러 세션이 같은 브랜치(현재 `fire-inflation`)에 커밋함.
- **`git commit -a` 금지** — 남의 미커밋 파일까지 삼킴. 작업 전 `git pull`, 커밋 시 **`git add <내 경로>`로 선별**.
- push 전 `git pull`로 다른 세션 커밋부터 받기.

## 📂 종목별 진입점
- PG: `PG/HANDOVER.md` · MCD: 완료·업로드 · stock_alert: `stock_alert/RISE_HANDOVER.md`·`DECK_DESIGN.md`
- 편집 UI: `architecture_docs/<STOCK>/dec_pipeline.html`·`dec_edit_page{N}.html` (서버로 접속)
- 제작 매뉴얼: `PRODUCTION_MANUAL.md`
