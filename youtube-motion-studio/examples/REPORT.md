# YouTube Motion Studio — 10개 기능 검증 예제 리포트

기존 엔진(렌더러·컴포넌트·차트·애니메이션·폰트·병렬 렌더)을 **실제 결과물로 검증**하기 위해
세로형 Shorts 예제 10개를 생성·렌더·검증했다. 새 엔진 기능은 추가하지 않았고, 폰트 다중 파일
전달을 위한 최소 변경만 했다(아래 §변경된 엔진 파일).

생성물 위치: `examples/<id>/` — `project.json`, `output.mp4`, `representative.png`,
`preview/scene-XX-{start,middle,end}.png`, `contact-sheet.png`, `validation.json`.
갤러리: `examples/gallery/index.html`, 통합 리포트: `examples/gallery/report.json`.

## 1. 생성된 예제 10개 · 길이 · 렌더 시간 · 검증 기능

| #   | 예제                    |  길이 | 프레임 |              병렬 렌더 | 컴포넌트                        | 검증한 기능                                          |
| --- | ----------------------- | ----: | -----: | ---------------------: | ------------------------------- | ---------------------------------------------------- |
| 01  | Number Hook             |   12s |    360 |                   6.7s | title, caption                  | 헤비폰트, 숫자 교체, pop/fade, 중앙정렬              |
| 02  | A/B Comparison          |   13s |    390 |                  33.7s | +rectangle                      | 2열 카드, 색대비, 레이어, slide                      |
| 03  | Multi-Series Line Chart |   14s |    420 |                  51.5s | +line-chart                     | series, yTicks, legend, 공유스케일                   |
| 04  | Dividend Bar Chart      |   13s |    390 |                  31.0s | +bar-chart                      | bar labels, 기준선, 라벨간격                         |
| 05  | Person Story            |   13s |    390 |                  27.4s | +character, profile-card        | 캐릭터, 프로필카드, 타임라인, **아바타 placeholder** |
| 06  | Company Analysis        |   15s |    450 |                  16.5s | +table, topic-circle            | 복합 레이아웃, 표 셀정렬, 차트+카드                  |
| 07  | Top Five Ranking        | 11.5s |    345 |                  17.0s | title, caption, rectangle       | 반복 컴포넌트, **stagger**, 순위정렬                 |
| 08  | Compound Growth         |   15s |    450 |                  44.8s | line-chart                      | 숫자교체, 차트+타임라인, 마커, area/easing           |
| 09  | Question & Answer       |   14s |    420 |                  19.1s | character, speech-bubble        | 말풍선, 캐릭터 배치, Q/A 구분, 강조                  |
| 10  | Full Showcase           |   20s |    600 | **10.1s** (직렬 28.9s) | title·subtitle·line/bar-chart   | 전 컴포넌트, 자막, 병렬 렌더                         |

- **렌더 성공 10/10**, 전부 `1080×1920 / 30fps / H.264 / yuv420p`, moov atom 정상, 경고 0.
- 총 병렬 렌더 시간 ~258s, 총 출력 1.6MB.

## 2. 실패/우회한 기능 (엔진 한계)

원칙: 우선 기존 기능으로 우회, 불가능할 때만 최소 변경. 아래는 **우회**로 처리한 항목이다.

1. **숫자 카운트업(0→8억 연속 증가)** — 애니메이션 프리셋은 transform(위치·스케일·투명도)만
   바꾸고 텍스트/숫자 값은 못 바꾼다. → 스펙이 허용한 **"숫자 교체"**로 우회: 중간값을 각각
   타이밍이 다른 title 요소로 깔아 pop-in 시퀀스(01, 08, 10).
2. **라인차트 "왼→오 그려지는" 드로우 애니메이션** — line-chart는 정적 폴리라인이고, 부분 클립
   리빌을 표현할 프리셋이 없다. → 차트 전체 fade-in + 최종값 캡션으로 우회(03, 08).
3. **막대 순차 등장 / 개별 막대 강조 / 막대 위 값 표시** — bar-chart는 모든 막대를 한 번에 그리고
   per-bar 강조·값라벨을 지원하지 않는다. → 차트 전체 slide-up + "최고 6월 83만 원" 캡션 +
   요약 카드로 우회(04).
4. **장면 간 전환(디졸브/슬라이드)** — 타임라인은 한 시점에 한 장면만 활성화하고 크로스-장면
   합성이 없다(하드 컷). → 각 장면 안에서 요소별 entrance 애니(fade/slide/pop)로 전환감 구현.
5. **말풍선 다중 줄** — speech-bubble/title/caption/subtitle은 단일 줄(줄바꿈 없음). → 긴 문장은
   여러 요소로 분리하거나 짧게 재작성(09, 02).

이들은 "치명적 부재"가 아니라 **후속 컴포넌트/애니 채널 확장 과제**다(§5 다음 우선순위).

## 3. 변경된 엔진 파일 (최소 변경)

예제 렌더에 필요한 **폰트 다중 파일 전달**만 추가했다(기능 추가 아님, 배선만):

- `apps/renderer/src/parallelExport.ts` — `ParallelExportOptions.fonts?: FontConfig` 추가,
  worker에 `MS_FONTS`(JSON) 환경변수로 전달.
- `apps/renderer/src/sceneWorker.mts` — `MS_FONTS`가 있으면 전체 FontConfig로 렌더(없으면 기존
  단일 fontFile 인자).

영향: 기존 호출부 100% 하위호환(둘 다 optional). 검증: 전체 게이트 통과.
(참고: `title.fontFamily`, `frames.FontConfig`는 이전 폰트 작업에서 이미 반영·커밋됨.)

## 4. 새로 만든 예제 전용 파일

- `examples/package.json`, `examples/tsconfig.json` — `@motion-studio/examples` 워크스페이스 패키지.
- `examples/fonts/BlackHanSans-Regular.ttf` — 제목용 헤비 폰트(저장소 내 명시 파일).
- `examples/src/toolkit.ts` — 엄격 타입 빌더(el/box/enter/scene/project/title/caption/card + 팔레트·폰트).
- `examples/src/projects/index.ts` — 10개 프로젝트 정의(결정론적, 고정 타임스탬프).
- `examples/src/pipeline.ts` — generate/preview/render/validate 단계 + 폰트 config.
- `examples/src/gallery.ts` — 정적 갤러리 HTML + 통합 report.json.
- `examples/src/cli.ts` — `generate|preview|render|validate|gallery|all` (+`--skip-existing`).
- 루트: `package.json`(examples:* 스크립트), `pnpm-workspace.yaml`, `.prettierignore`, `eslint.config.js`(생성물 무시).

## 5. 폰트 정책 (결정론)

`loadSystemFonts: false` + 명시 파일만 사용해 시스템 폰트 해석에 의존하지 않는다.

- 제목: `Black Han Sans` — `examples/fonts/`에 저장소 내 vendoring.
- 본문: `Noto Sans CJK KR` — `/usr/share/fonts/opentype/noto/NotoSansCJK-{Regular,Bold}.ttc`를
  **명시 경로**로 지정(파일 ~20MB×2라 vendoring 대신 절대경로 참조). 다른 머신 이식 시 이 두
  파일 경로만 맞추면 된다(개선 후보: examples/fonts로 vendoring).

## 6. 성능 (병렬 vs 직렬)

- 예제 10(20s·600f·7장면): **병렬 10.1s vs 직렬 28.9s = 2.9×**.
- 병렬은 **장면 단위**라 총시간이 가장 긴 장면 하나에 바운드된다. 장면이 많고 짧은 예제(10:7장면)는
  이득이 크고(2.9×), 긴 단일 장면이 지배적인 예제(03:11s 차트, 08:12s 차트)는 이득이 작아 30~50s가
  걸린다. → **다음 우선순위: 긴 장면을 프레임 청크로 분할**(예제10 기준 2.9× → 이론상 코어수까지).

## 7. 완료 조건 점검

1. 서로 다른 기능 검증 10개 project.json ✅
2. 10개 MP4 정상 재생(moov 있음) ✅
3. 전부 1080×1920/30fps ✅
4. 대표 이미지 + contact sheet 10/10 ✅
5. validation.json 10/10 ✅
6. 갤러리에서 10개 확인 ✅ (`examples/gallery/index.html`)
7. 스키마 검증 오류 0 ✅ (generate 단계 validateProject 통과)
8. moov atom 정상 10/10 ✅
9. 전체 품질 게이트 통과 ✅ (format·typecheck·lint·test 135·build)
10. 본 리포트 ✅

## 8. 가장 완성도 높은 예제

**10 Full Showcase** — 7장면에 title/caption/subtitle/line-chart/bar-chart/rectangle을 모두 엮고,
시간 인식 자막까지 실제로 동작하며, 병렬 렌더 2.9× 이득을 실증한다. 그 다음은 **03(다중 시리즈
차트 + 축 + 범례)**와 **02(A/B 카드)**로, 정보 전달형 Shorts에 바로 쓸 수 있는 완성도다.

## 9. 다음 개발 우선순위 (제안)

1. **긴 장면 프레임-청크 병렬 분할** — 현재 장면 단위 병렬의 한계 해소(가장 큰 실사용 이득).
2. **숫자 카운터 컴포넌트** — 시간 인식 숫자(포맷/이징) 네이티브 지원(01·08·10의 우회 제거).
3. **차트 드로우-온 애니메이션** — line/bar에 progress prop 또는 클립 리빌.
4. **텍스트 자동 줄바꿈** — title/caption/speech-bubble 멀티라인(레이아웃 우회 제거).
5. **장면 전환 합성** — transitionIn/Out(디졸브·슬라이드)을 타임라인에서 실제 블렌딩.
6. **NVENC 인코딩 옵션** — GB10 GPU로 인코딩 offload(래스터와 병행).
