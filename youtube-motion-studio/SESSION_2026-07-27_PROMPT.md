# 오늘 작업 재현/인계 프롬프트 (2026-07-27, youtube-motion-studio)

아래 프롬프트를 다른 세션/에이전트에게 그대로 주면 오늘 한 작업을 이해·검증·이어갈 수 있다.

---

## 역할/컨텍스트

너는 `/home/messi/PAPER_ORC/youtube-motion-studio` 모노레포(pnpm 9 + TypeScript 5 strict + ESM)를 이어받는다.
이 저장소는 **브라우저·화면녹화 없이 JSON에서 유튜브 영상(MP4)을 결정론적으로 렌더하는 헤드리스 모션그래픽 엔진**이다.
프레임(t)은 `(project, t)`만의 순수함수(spec §23). 백엔드 무관 씬그래프 IR → SVG 백엔드(resvg 래스터화) → ffmpeg(H.264)로 뽑는다.

- 상위 워크스페이스 규칙: `/home/messi/PAPER_ORC/blog/CLAUDE.md`. **`git commit -a` 금지**, 커밋은 `git add <내 경로>`로 선별, push 전 `git pull`. 공유 브랜치 `fire-inflation`.
- 기존 제작 파이프라인(레거시): `blog/PG/deck/` — 13MB HTML 덱을 브라우저로 열어 화면녹화. 이 엔진은 그 대체재를 지향(결정론·헤드리스·자동화·테스트가능).
- 스펙: `youtube-motion-studio/IMPLEMENTATION_PLAN.md`, 원본 마스터 스펙 `YouTube_Motion_Studio_Master_Spec.md`(있으면 참조).

## 저장소 구조

```
packages/schemas        JSON Schema (project.schema.json 등)
packages/core           MotionProject 타입/Zod 스키마/검증/정규화/마이그레이션/
                        commands·history·bindings·theme·template·subtitle·ai·io(importProject)
packages/renderer-core  씬그래프(DrawNode: rect/ellipse/line/polyline/text/image/group),
                        transform·easing·animation·timeline(evaluateProjectAtTime)·
                        renderers/svg.ts(renderProjectToSvg, skipBackground 옵션)·renderers/pixi.ts
packages/components     18+ 빌트인 컴포넌트(title·caption·subtitle·line-chart·bar-chart·table·image 등)
packages/legacy-adapter PG 덱 JSON → MotionProject 변환(pgDeckAdapter), chartExtract, textNormalize
packages/plugin-sdk     플러그인 매니페스트/호스트
apps/editor             React18+Zustand5 GUI 에디터(Canvas·Inspector·Timeline·Import Deck 버튼)
apps/renderer           Node MP4 export 파이프라인
```

게이트(작업 후 항상 통과시켜라):

```
cd /home/messi/PAPER_ORC/youtube-motion-studio
pnpm format && pnpm typecheck && pnpm lint && pnpm test && pnpm build
```

---

## 오늘(2026-07-27) 실제로 한 작업

### 커밋된 것

**커밋 `d1a77d5` — 차트 축·다중시리즈·범례**

- `packages/components/src/chart/lineChart.ts`: 재작성. `series?: {values,color,label}[]`(다중 시리즈, 공유 y스케일), `yTicks?: [number,string][]`(y축 그리드+눈금 라벨, marginL=96), `legend?: {color,label}[]`(상단 수평 범례, marginT=44) 지원. 단일 `values`도 하위호환.
- `packages/components/src/chart/barChart.ts`: 재작성. `labels?: string[]`(x축 라벨, labelH=34) + 베이스라인 추가.
- `packages/legacy-adapter/src/chartExtract.ts`: 재작성. enginechart/reelchart → 다중시리즈 line-chart(+범례), divbars/hbars2/menuboard → 라벨 bar-chart, checks → table. helpers: `num/str/parseMoney/downsample/seriesY/asObj/asArr/tuplesToTicks`, `PALETTE`.
- `packages/legacy-adapter/tests/deckAdapter.test.ts`: 차트 단언을 `props.series[0].values`로 갱신.

**커밋 `5d7efdc` — 폰트 로딩 + 히어로 헤비 웨이트**

- 문제: resvg에 폰트 옵션을 안 넘겨 얇은 기본폰트로 떨어지고, title 컴포넌트가 `fontFamily`를 안 내보냄 → 큰 글자 `70년`이 덱의 헤비 웨이트와 안 맞음.
- `apps/renderer/src/frames.ts`: `FontConfig{files?,defaultFamily?,loadSystemFonts?}` 추가. `renderFrameToPng(...,fonts=DEFAULT_FONTS)`가 `new Resvg(svg,{fitTo,font:{loadSystemFonts,fontFiles,defaultFontFamily}})`로 폰트 주입. 기본 defaultFamily="Noto Sans CJK KR".
- `apps/renderer/src/exportVideo.ts` + `types.ts`: `ExportOptions.fonts?: FontConfig`를 pump config 통해 배선.
- `packages/components/src/text/title.ts`: `fontFamily?` prop 추가 → 설정 시 TextNode에 emit.
- `packages/legacy-adapter/src/deckAdapter.ts`: `export const DISPLAY_FONT="Black Han Sans"`. 히어로 title에 `fontWeight:900, fontFamily:DISPLAY_FONT`. (`textAlign`→`align` 오타도 수정.)
- 폰트 파일: `blog/PG/fonts/BlackHanSans-Regular.ttf` (내부 패밀리명 "Black Han Sans"). resvg `fontFiles`로 로드.
- 테스트: title fontFamily emit/omit 2케이스 추가(components.test.ts).

### 아직 커밋 안 한 것 — **멀티코어 병렬 렌더 엔진** (검증 완료, 게이트·커밋 필요)

동기: DGX Spark(NVIDIA GB10, ARM Grace 20코어, NVENC 사용가능). 병목은 **resvg 래스터화 256ms/프레임**인데 **1코어 직렬**이라 전체 덱(7638프레임)이 ~33분. resvg-js `.render()`는 동기 네이티브 호출이라 한 Node 프로세스 Promise.all로는 병렬 불가(이벤트루프 블록) → **OS 프로세스 병렬** 필요.

- `apps/renderer/src/sceneWorker.mts` (신규): 자식 프로세스가 단일-장면 sub-project JSON을 파싱해 `exportVideo`로 세그먼트 MP4 하나 렌더. **주의: `importProject`로 재-import하면 정규화된 데이터에 마이그레이션이 다시 돌아 `scenes`가 undefined가 됨 → JSON.parse 후 직접 exportVideo에 넘긴다.**
- `apps/renderer/src/parallelExport.ts` (신규): `renderDeckParallel(project, {outPath, fontFile?, concurrency?, ffmpegPath?, onSceneDone?})`. 장면별 `{...project, scenes:[scene]}` sub-project를 임시 JSON으로 쓰고, 동시성 풀(기본 `availableParallelism()-2`)로 sceneWorker 자식들을 스폰(`spawn(process.execPath,['--import','tsx',WORKER,json,out,font])`), 전부 끝나면 `ffmpeg -f concat -c copy` 로 합침. `packages/... index.ts`에서 export.
- `apps/renderer/src/index.ts` (수정): `renderDeckParallel`, `ParallelExportOptions/Result`, `FontConfig` re-export.

**실측 결과(오늘):** 20장면 동시(워커 19개, node CPU 615%+), 전체 덱 7639프레임/254.6s/1080p/배경영상 합성 정상, wall **434.6s(7.2분)** = 직렬 대비 **~4.5×**. 산출물 로컬: `scratchpad/pg_deck_parallel.mp4`(1080p 73MB), 720p 압축본 전송함.

**4.5×에 그친 이유:** 장면별 병렬이라 총시간이 **가장 긴 장면 하나**에 바운드(가장 긴 enginechart가 바닥).

---

## 지금 상태 / 다음 할 일

1. **병렬 엔진 게이트+커밋**: 위 3파일(`sceneWorker.mts`, `parallelExport.ts`, `apps/renderer/src/index.ts`) — `pnpm format/typecheck/lint/test/build` 통과 후 선별 `git add`로 커밋. (임시 스모크 `_*.mts`, `runparallel.mts`는 삭제 완료.)
2. **최적화 ① 긴 장면 프레임-청크 분할**: 장면 내부 프레임 범위를 여러 프로세스로 쪼개 렌더→PNG시퀀스/세그먼트 concat. 4.5× → 15×+ 목표. concat `-c copy`는 세그먼트 코덱 파라미터 동일해야 함(현재 libx264/yuv420p 통일).
3. **최적화 ② NVENC**: `ExportOptions.encoder`(libx264|h264_nvenc) 추가해 인코딩을 GB10 GPU로 offload(확인됨: h264_nvenc/hevc_nvenc/av1_nvenc). CPU를 래스터에 집중. NVENC 동시 세션 한도 주의.
4. **화질 잔여 격차(폰트 외)**: 브랜드 로고/마스코트 이미지 컴포넌트, 하이라이트 pill·카드 그림자 등 덱 특화 스타일 컴포넌트 이식(레거시 HTML 덱 대비).

## 검증용 스니펫 (레거시 PG 덱을 새 엔진으로 렌더)

```ts
// apps/renderer/src/ 안에 .mts로 두고: pnpm --filter @motion-studio/renderer exec tsx src/<name>.mts
import { readFileSync } from "node:fs";
import { pgDeckAdapter } from "@motion-studio/legacy-adapter";
import { renderDeckParallel } from "./parallelExport";
const { project } = await pgDeckAdapter.import(
  readFileSync("/home/messi/PAPER_ORC/blog/PG/deck/pg_deck.json", "utf8"),
  { assetBasePath: "/home/messi/PAPER_ORC/blog/PG/deck/bg" },
); // 배경영상 4종: pg_storefront/pg_customer/pg_reflect/pg_interior
await renderDeckParallel(project, {
  outPath: "/tmp/out.mp4",
  fontFile: "/home/messi/PAPER_ORC/blog/PG/fonts/BlackHanSans-Regular.ttf",
  onSceneDone: (d, t, n) => console.log(`[${d}/${t}] ${n}`),
});
```

## 함정 메모

- 임시 tsx 스크립트는 `apps/renderer/src/` 안에 둬야 워크스페이스 resolution이 됨. 최상위 await는 `async main()`으로 감싸거나 `.mts`.
- `pkill -f "<name>"`는 **런처 bash 자신의 명령줄까지 매칭**해 자가-종료(exit 144)함 → 고유 스크립트명 쓰고 pkill 지양.
- 전체 덱 배경합성 렌더는 **같은 출력 경로로 두 번 띄우면 두 ffmpeg가 한 파일을 써서 손상**(moov atom 없음)됨. 반드시 고유 경로.
- 채팅 파일 업로드 한도 30MiB → 1080p 4분(73MB)은 720p로 압축해 전송.

```

```
