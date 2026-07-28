# 인계/재현 프롬프트 — YouTube Motion Studio 10개 검증 예제

아래 프롬프트를 다른 세션/에이전트에게 그대로 주면 이 작업을 이해·검증·이어갈 수 있다.

---

## 역할

너는 `/home/messi/PAPER_ORC/youtube-motion-studio` (pnpm 9 모노레포, TS5 strict, ESM)의
`@motion-studio/examples` 패키지를 이어받는다. 이 패키지는 **엔진의 기존 기능을 실제 결과물로
검증**하기 위한 세로형 Shorts 예제 10개를 결정론적으로 생성·렌더·검증한다. 새 엔진 기능을
추가하는 게 목적이 아니다. 저장소 규칙은 `blog/CLAUDE.md`(**`git commit -a` 금지**, `git add`
선별, push 전 `git pull`, 공유 브랜치 `fire-inflation`).

## 이미 완료된 상태 (커밋됨)

- 커밋 `3bc8e9f` — 엔진: 장면 단위 병렬 렌더(`parallelExport.ts`/`sceneWorker.mts`) + 다중 폰트파일
  `FontConfig`(`MS_FONTS` env)로 워커 전달. 하위호환.
- 커밋 `1e10d3a` — `@motion-studio/examples` 패키지 + 루트 `examples:*` 스크립트 + REPORT.md.
- 생성 산출물(mp4/png/json)은 **gitignore**(재생성 가능). 소스만 커밋됨.

검증 완료: 10/10 렌더 성공, 전부 1080×1920/30fps/H.264/yuv420p/moov정상, 게이트 전부 통과
(format·typecheck·lint·test 135·build).

## 구조 (examples/)

```
examples/
  package.json, tsconfig.json          # @motion-studio/examples 워크스페이스 패키지
  fonts/BlackHanSans-Regular.ttf       # 제목용 헤비 폰트(vendored)
  .gitignore                           # [0-9][0-9]-*/, gallery/report.json, gallery/index.html
  REPORT.md                            # 결과·한계·우회·다음 우선순위
  src/
    toolkit.ts        # 빌더: box/el/enter/scene/project/title/caption/card + 팔레트 C + 폰트
    projects/index.ts # EXAMPLES: ExampleDef[] — 10개 build():MotionProject (결정론적)
    pipeline.ts       # generate/preview/render/validate + FONTS(FontConfig) + EXAMPLES_DIR
    gallery.ts        # 정적 index.html + report.json
    cli.ts            # generate|preview|render|validate|gallery|all (+--skip-existing, +NN- 필터)
  <id>/               # 생성물(gitignored): project.json output.mp4 representative.png
                      #                     preview/scene-XX-{start,middle,end}.png
                      #                     contact-sheet.png validation.json
  gallery/index.html, gallery/report.json  # 생성물(gitignored)
```

## 실행

```
cd /home/messi/PAPER_ORC/youtube-motion-studio
pnpm examples:all                 # 전체: generate→preview→render→validate→gallery
pnpm examples:all --skip-existing # output.mp4+validation.json 있는 예제 건너뜀
pnpm examples:generate|preview|render|validate|gallery   # 단계별
# 단일 예제: pnpm --filter @motion-studio/examples exec tsx src/cli.ts render 03-multi-line-chart
```

게이트(작업 후 항상): `pnpm format && pnpm typecheck && pnpm lint && pnpm test && pnpm build`.

## 엔진 API 요점 (예제 저작 시 반드시 지킬 것)

- **좌표계**: `transform.x/y`는 요소 **anchor 지점**(기본 anchor 0.5 → x,y=박스 중심). 컨텐츠는
  로컬 `[0,0]→[w,h]`에 그려짐. `box(cx,cy,w,h)` 헬퍼가 중심 기준 박스를 만든다. 열 배치는
  `title/caption`의 `cx` 옵션으로(기본 W/2 — 안 주면 전부 중앙에 겹침 = 실제로 밟은 버그).
- **단일 줄만**: title/caption/subtitle/speech-bubble/text는 줄바꿈 없음 → 다중 줄은 요소 분리.
- **애니메이션**: 프리셋은 transform만(fade-in/pop-in/scale-in/zoom-in/slide-{left,right,up,down}).
  텍스트/숫자 값은 못 바꿈 → 카운트업은 "숫자 교체"(타이밍 다른 title 요소)로 우회.
- **장면**: 타임라인은 한 시점에 한 장면만 활성(크로스-장면 디졸브 없음) → 전환감은 요소 entrance 애니.
- **스키마 strict**: 요소/transform/timing/animation 모두 `.strict()`. `validateProject`로 generate 시 검증됨.
- **컴포넌트**(검증됨): title·caption·subtitle·text·rectangle·circle·line-chart·bar-chart·table·
  image·image-card·profile-card·character·speech-bubble·topic-circle·youtube-comment·phone-frame·notification.
  - line-chart props: `series:[{values,color,label?}]`, `yTicks:[[num,str]]`, `legend:[{color,label}]`, `strokeWidth`, `area`, `color`, `values`.
  - bar-chart: `values:number[]`, `labels?:string[]`, `color`, `gap`.
  - table: `rows:string[][]`, `color`, `lineColor`. profile-card: `title/subtitle/accent/background/color`(avatar 없으면 placeholder).
  - rectangle=카드: `element.style.{backgroundColor,borderColor,borderWidth,borderRadius}`.

## 폰트 정책 (결정론)

`FONTS`(pipeline.ts): `loadSystemFonts:false` + 명시 파일만.

- 제목 `Black Han Sans` → `examples/fonts/BlackHanSans-Regular.ttf`(vendored).
- 본문 `Noto Sans CJK KR` → `/usr/share/fonts/opentype/noto/NotoSansCJK-{Regular,Bold}.ttc`(명시 경로).
- title props에 `fontFamily:"Black Han Sans"`, defaultFamily는 "Noto Sans CJK KR".

## 성능

장면 단위 병렬이라 총시간 ≈ 가장 긴 장면 하나. 예제10(7장면) 병렬 10.1s vs 직렬 28.9s = 2.9×.
긴 단일 장면 예제(03/08)는 이득 작음.

## 남은 개선 (우선순위)

1. **긴 장면 프레임-청크 병렬 분할**(가장 큰 실사용 이득) — `parallelExport.ts`를 장면 대신
   프레임 범위로 쪼개 렌더→concat.
2. 숫자 카운터 컴포넌트(시간 인식) 3. 차트 draw-on 애니(progress prop) 4. 텍스트 자동 줄바꿈
3. 장면 전환 합성(transitionIn/Out 블렌딩) 6. NVENC 인코딩 옵션(GB10 GPU).

## 함정 (실제로 밟음)

- `title/caption`에 `cx` 안 주면 열별 텍스트가 전부 중앙에 겹친다.
- `pkill -f "<이름>"`은 런처 bash 자신도 매칭해 자가종료(exit 144) → 고유 스크립트명 사용.
- 렌더 중 `pnpm format` 등 동시 실행 금지(파일 재기록 혼선). 렌더는 백그라운드+대기.
- 채팅 업로드 30MiB 한도(예제 mp4는 수백KB라 무관, 전체 덱은 720p로 압축 필요).
- 생성 산출물은 gitignore — `git add examples/`는 소스만 잡힘(의도됨).

```

```
