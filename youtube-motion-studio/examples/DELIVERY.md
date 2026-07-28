# 납품 보고서 — YouTube Motion Studio 기능 검증 예제 10개

**요청**: 기존 엔진의 렌더링·컴포넌트·차트·애니메이션·레거시·폰트·병렬 렌더를 실제 결과물로
검증하는 세로형 Shorts 예제 10개를 만들어라(계획만 말고 실제 생성·렌더·검증까지).

**결과 한 줄**: 10개 전부 만들었고, 전부 정상 렌더됩니다(1080×1920 / 30fps / H.264, moov 정상).
품질 게이트 통과, 새 엔진 기능은 추가하지 않고 폰트 배선만 최소 변경했습니다.

---

## 30초 만에 직접 확인하는 법

```bash
cd /home/messi/PAPER_ORC/youtube-motion-studio
pnpm examples:all            # 처음부터 전부 재생성(생성물은 재현 가능해서 git에 없음)
open examples/gallery/index.html   # 브라우저로 10개 영상 카드 확인
```

개별 영상: `examples/<번호-이름>/output.mp4` · 대표 이미지: `representative.png` ·
장면 미리보기 묶음: `contact-sheet.png` · 검증 수치: `validation.json`.

---

## 요청하신 완료 조건 10개 — 대조표

| #   | 요청 조건                             | 상태 | 근거                                               |
| --- | ------------------------------------- | :--: | -------------------------------------------------- |
| 1   | 서로 다른 기능 검증 10개 project.json |  ✅  | `examples/*/project.json`, 각기 다른 컴포넌트/기능 |
| 2   | 10개 MP4 정상 재생                    |  ✅  | `output.mp4` ×10, ffprobe 재생 확인                |
| 3   | 전부 1080×1920, 30fps                 |  ✅  | validation.json 전수 확인                          |
| 4   | 대표 이미지 + contact sheet           |  ✅  | `representative.png` + `contact-sheet.png` ×10     |
| 5   | validation.json                       |  ✅  | ×10, 요청하신 필드 포함                            |
| 6   | 갤러리에서 10개 확인                  |  ✅  | `examples/gallery/index.html`                      |
| 7   | 스키마 검증 오류 0                    |  ✅  | 생성 단계에서 `validateProject` 통과               |
| 8   | MP4 moov atom 정상                    |  ✅  | 10/10 hasMoovAtom=true                             |
| 9   | 전체 품질 게이트 통과                 |  ✅  | format·typecheck·lint·**test 135**·build           |
| 10  | REPORT.md 작성                        |  ✅  | `examples/REPORT.md`                               |

전부 충족했습니다.

## 만든 예제 10개

| #   | 예제                    |  길이 | 검증한 엔진 기능                                  |
| --- | ----------------------- | ----: | ------------------------------------------------- |
| 01  | Number Hook             |   12s | 헤비 폰트, 숫자 교체, pop/fade                    |
| 02  | A/B Comparison          |   13s | 2열 카드, 색 대비, 레이어                         |
| 03  | Multi-Series Line Chart |   14s | 다중 시리즈, Y축 눈금, 범례, 공유 스케일          |
| 04  | Dividend Bar Chart      |   13s | 막대 라벨, 기준선                                 |
| 05  | Person Story            |   13s | 캐릭터, 프로필 카드, 타임라인, 아바타 placeholder |
| 06  | Company Analysis        |   15s | 표, KPI 카드, 차트+카드 복합 레이아웃             |
| 07  | Top Five Ranking        | 11.5s | 반복 컴포넌트, 순차(stagger) 등장                 |
| 08  | Compound Growth         |   15s | 복리 곡선(area), 숫자·마커                        |
| 09  | Question & Answer       |   14s | 말풍선, 캐릭터 배치, 강조                         |
| 10  | Full Showcase           |   20s | 전 컴포넌트 + 자막 + 병렬 렌더                    |

## 솔직하게 — 엔진으로 "안 되던 것"과 처리 방식

지시하신 원칙(불가능하면 우회하고 보고)대로, 아래는 현재 엔진이 지원하지 않아 **우회**했습니다.
상세는 REPORT.md §2에 있습니다.

- **숫자 카운트업(연속 증가)**: 애니메이션이 위치·크기·투명도만 바꾸고 숫자 값은 못 바꿔서,
  "숫자 교체"(중간값을 순차로 띄우기)로 대체. — 스펙이 허용한 방식입니다.
- **차트 선이 그려지는 애니 / 막대 순차·값 라벨**: 차트는 한 번에 그려져서, 차트 전체 등장
  애니 + 캡션으로 대체.
- **장면 간 디졸브 전환**: 타임라인이 한 번에 한 장면만 그려서(하드 컷), 장면 안 요소 등장
  애니로 전환감 구현.
- **텍스트 자동 줄바꿈 없음**: 긴 문장은 여러 줄 요소로 분리.

→ 치명적 결함이 아니라 다음 개발 과제입니다(REPORT.md §9에 우선순위 6개).

## 엔진을 건드린 부분 (최소 변경, 하위호환)

예제가 제목·본문 두 폰트를 명시 파일로 쓰게 하려고 **폰트 전달 배선만** 추가했습니다:
`apps/renderer/src/parallelExport.ts`, `sceneWorker.mts` (기존 호출부 100% 하위호환, 게이트 통과).
렌더 로직·컴포넌트·차트는 손대지 않았습니다.

## 성능 참고

`renderDeckParallel`(장면 단위 병렬)로 렌더했습니다. 예제 10(20초·7장면)은 **병렬 10.1초 vs
직렬 28.9초 = 2.9배**. 장면이 긴 예제는 병렬 이득이 작아, 다음 1순위 개선으로 "긴 장면을
프레임 단위로 더 쪼개는 병렬화"를 제안합니다.

## 위치·커밋

- 코드/문서: `youtube-motion-studio/examples/` (소스만 커밋, 생성물은 재현 가능해 gitignore).
- 커밋: `3bc8e9f`(엔진 폰트 배선+병렬), `1e10d3a`(예제 패키지+REPORT), `d5ac0e3`(인계 프롬프트).
- 함께 보는 문서: `REPORT.md`(상세 결과·한계), `HANDOFF_PROMPT.md`(다음 작업자용 재현 프롬프트).

## 추천

가장 완성도 높은 예제는 **10 Full Showcase**(전 기능 종합+자막+병렬 실증), 그다음 **03(다중
시리즈 차트)**·**02(A/B 카드)**입니다. 정보 전달형 Shorts에 바로 쓸 수 있는 수준입니다.
