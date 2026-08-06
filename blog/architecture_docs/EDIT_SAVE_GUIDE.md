# 덱/파이프라인 편집·저장 구조 가이드 (편집 워크플로우)

> 2026-07-27 대화에서 확정. "편집했는데 자꾸 원복" 문제의 근본 원인과 올바른 저장 흐름 정리.
> 핵심 원칙: **JSON = 원본 데이터 · HTML = 화면(생성물) · GUI 편집 → 반드시 서버에 저장(=JSON 기록)**.

## 1. 원리 (JSON=원본, HTML=화면)
- **JSON = 원본 데이터**(원본). **HTML = 그 JSON으로 매번 다시 그려지는 화면**(생성물).
- JSON이 바뀌어도 HTML은 자동으로 안 바뀜 → **컴파일러가 JSON을 읽어 HTML을 다시 생성**해야 갱신됨.
- 그래서 **HTML 파일(코드)을 직접 고치면 무의미**(다음 생성 때 덮어써지고, 애초에 덱은 JSON에서 만들어짐).
- **GUI에서 편집 = HTML 파일을 고치는 게 아니라, JavaScript가 그 조작을 JSON에 저장**하는 것.

## 1.5 화면(GUI) 네비게이션 구조 — 어디서 편집하나
링크로 계층 이동. **전부 서버(8090)로 접속해서 열어야** 편집·저장이 됨(§5).
```
architecture_docs/top_pipeline_standalone.html   ← 최상위 허브(프로토콜·매뉴얼·리서치·인수인계·"③ 덱 생성")
        │  "③ 덱 생성" 링크
        ▼
architecture_docs/dec_pipeline.html              ← 종목(프로젝트) 선택 허브
        │  MCD / PG / stock_alert … 링크
        ▼
architecture_docs/PG/dec_pipeline.html           ← PG 파이프라인(페이지 카드 구조 편집 · "🚀 덱에 반영")
        │  각 페이지 카드 → dec_edit_page{N}.html · 덱 프리뷰 pg_v1.html/pg_final.html
        ▼
architecture_docs/PG/dec_edit_page{N}.html       ← 페이지별 편집 GUI(내용·위치·자막 · "저장(영구)"/"💾 자막 저장")
```
- **여기서 "GUI 편집"** = 위 `PG/dec_pipeline.html`(구조)과 `PG/dec_edit_page{N}.html`(내용) 화면에서 드래그·수정하는 것.
- 종목 추가 시 `architecture_docs/<STOCK>/dec_pipeline.html`·`dec_edit_page{N}.html`이 그 종목 컴파일러로 생성됨(구조 동일).

## 2. 파일 경로 (종목 = PG 예시, 다른 종목은 `blog/<STOCK>/`)
**원본 JSON (서버가 저장·덮어씀)** — `blog/PG/spec/`
- `deck_plan.json` — 페이지 구조(순서·추가·삭제)  ← 파이프라인 "덱에 반영"
- `narration_final.json` — 자막  ← 페이지 "💾 자막 저장"
- `deck_edited_scenes.json` — 전체 씬 스냅샷  ← 페이지 "저장(영구)"
- `deck_ov.json` — 요소 위치·색  ← 페이지 "저장(영구)"

**결과물 (컴파일러가 생성)** — `blog/PG/deck/`, `blog/architecture_docs/`
- `deck/pg_deck.json`, `deck/pg_v1.html` (덱)
- `architecture_docs/[PG/]dec_pipeline.html`, `dec_edit_page{N}.html` (편집 GUI)

## 3. 컴파일러 2개
| 컴파일러 | 읽는 JSON | 만드는 HTML |
|---|---|---|
| `deck/build_deck.py` | spec/*.json·deck_plan·편집JSON들 | `pg_v1.html` (덱 본체) |
| `deck/tools/gen_dec_edit.py` | `pg_deck.json` + `deck_plan.json` | `dec_pipeline.html` + `dec_edit_page{N}.html` (편집 GUI) |

## 4. 저장 흐름 (서버 = edit_server.py 가 오케스트레이션)
```
GUI 편집 → [저장 버튼] → 브라우저가 서버로 HTTP POST (/api/save-deck|save-subs|save-pipeline)
  → edit_server.py 가: (a) 새 내용을 JSON 파일에 덮어씀  (b) 곧바로 컴파일러 실행(build_deck [+gen_dec_edit])
  → HTML(pg_v1.html·dec_pipeline.html 등) 재생성 → "최신본"/새로고침으로 로드
```
- 빌더는 파일을 감시하지 않음. **서버가 저장 직후 빌더를 직접 실행**하고, 빌더는 늘 고정 경로 JSON을 새로 읽음.

## 5. ★가장 중요★ — 반드시 서버(8090)로 접속 (file:// 금지)
저장 버튼은 **서버로 POST**를 보냄. 그래서:
| 접속 방식 | 저장 | 결과 |
|---|---|---|
| `http://192.168.2.144:8090` (PG 편집 서버) | POST가 edit_server 도달 → JSON 저장 | ✅ 유지 |
| `file:///.../dec_edit_page.html` (로컬 파일 직접 열기) | 갈 서버 없음 → POST 실패 | ❌ 유실 (= "편집 원복"의 진짜 원인) |

- **주소창이 `192.168.2.144:8090`으로 시작하는지 항상 확인.** 파일 더블클릭 금지.
- **예외**: 썸네일 편집기 `blog/prototypes/thumbs/thumb_editor.html`는 서버 없이 도는 자립형 → `file://` OK. 저장은 💾HTML/💾PNG **파일 다운로드** 방식.

## 6. 포트
| 포트 | 정체 | 저장 |
|---|---|---|
| **8090** | `edit_server.py` — **PG 작업용 (이걸 사용)** | ✅ |
| 8091 | 별도 인스턴스(다른 용도) — PG엔 쓰지 말 것 | — |
| 8080 | plain `http.server`(MCD 프리뷰용) | ❌ (저장 API 없음) |
- **PG는 8090 사용.** 8080은 저장 API 없음.

## 7. 다시 열 때 (재접속)
- 서버(8090/8091) 켜져 있으면 → **그냥 접속하면 자동으로 최신 JSON 상태**로 화면 생성됨. **IMPORT 불필요.**
- JSON은 서버 디스크 파일이라 브라우저 닫아도·재부팅해도 안 사라짐(영구). localStorage(브라우저 임시)와 다름.
- ↓JSON(내보내기)·↑불러오기 = 백업/다른PC 이전용 특수 버튼. 일상 작업엔 안 씀.

## 8. localStorage 함정 (안 누르면 유실)
- GUI 편집은 자동으로 **localStorage(브라우저 임시 초안)**에 먼저 저장됨.
- **"덱에 반영"/"저장(영구)"을 안 누르면** → localStorage에만 있고 JSON엔 안 감 → 캐시 지우거나 다른 기기 가면 사라짐.
- "덱에 반영" 누르면 → JSON 저장 + localStorage 자동 비움 + 서버본으로 새로고침(깔끔).
- (덱 렌더는 무조건 서버 빌드본을 쓰도록 고쳐둠 — 옛 localStorage가 새 빌드를 가리던 버그 제거. [[pg-subtitle-save-architecture]])

## 요약 한 줄
> **서버(8090/8091)로 접속 → GUI에서 편집 → 영구저장 버튼(덱에 반영/저장영구) 클릭 = 서버가 JSON에 쓰고 재빌드.** file://로 열거나 저장버튼 안 누르면 유실.
