# Time Creates Wealth — AI(WAN) 샷리스트 & 합성 지침

원칙: **AI가 감정, 엔진이 정보.** 아래 5개 비트만 WAN 실사/시네마틱 영상으로 만들어 **엔진
그래픽 아래 배경으로 합성**한다. 차트·숫자·텍스트·로고·KPI는 전부 엔진(현재 렌더)이 담당한다.

> 이 환경엔 WAN 생성 도구가 없어 AI 클립은 포함하지 못했다. 엔진 레이어는 완성·렌더됐고
> (`hero/hero-video/output.mp4`), 아래 클립을 만들어 지정 경로에 두면 즉시 합성된다.

## WAN 클립 5개 (720×1280 세로, 무음, 각 지정 길이)

| #   | 시간        | 파일명              | 프롬프트(요지)                                                                  | 모션              |
| --- | ----------- | ------------------- | ------------------------------------------------------------------------------- | ----------------- |
| A   | 0.0–1.5     | `bg/clock_core.mp4` | 극단 클로즈업, 시계 중심축의 광택 금속, 칠흑 배경, 미세한 빛 반사, 얕은 심도    | 아주 느린 push-in |
| B   | 1.5–3.0     | `bg/gears.mp4`      | 정밀 기계식 시계 기어들이 맞물려 회전, 황동/강철, 빛이 이 사이로 흐름, 시네마틱 | 기어 회전 + 광류  |
| C   | 5.0–7.0     | `bg/particles.mp4`  | 칠흑 공간에 떠다니는 금빛 입자/보케, 서서히 중앙으로 수렴, 슬로모션             | 입자 수렴         |
| D   | 7.0–8.5     | `bg/shatter.mp4`    | 금빛 파편이 흩어졌다 다시 원형으로 재조립, 슬로모션, 검정 배경                  | 파열→재조립       |
| E   | (전역 옵션) | `bg/light_leak.mp4` | 미세한 필름 광량 누출/그레인, 극도로 어두움                                     | 은은한 흐름       |

프롬프트 공통 접미: `cinematic, ultra-detailed, black background, shallow depth of field,
volumetric light, 24fps film grain, no text, vertical 9:16`.

## 합성(엔진 파이프라인 — 이미 구현됨)

엔진의 `exportVideo`는 **투명 프레임(모션그래픽)을 배경 영상 위에 ffmpeg overlay로 합성**한다
(PG 덱 배경영상에서 검증된 경로). 켜는 법:

1. 클립을 `hero/bg/`에 위 파일명으로 둔다.
2. `src/projects/index.ts`에서 해당 씬 `background`를 비디오로 바꾼다:
   ```ts
   // 예: s1 (clock core)
   scene("s1", "point", 1.5, [...], { type: "video", assetId: "clock_core" })
   // + project.assets 에 { id:"clock_core", type:"video", source:{kind:"local-path", path:"bg/clock_core.mp4"} }
   ```
   또는 파이프라인에 `assetBasePath: hero/bg` 를 주어 id로 해석.
3. `pnpm hero:render` — `hasVideoBackground`가 감지되면 자동으로 컴포짓 경로(투명 프레임 →
   `[bg][fg]overlay`)로 렌더한다.

정보 비트(3.0–5.0 차트/로고, 5.0–7.0 숫자, 8.5–10 텍스트)는 배경을 solid/gradient로 두어 엔진이
100% 담당한다. AI는 감정 비트(A·B·C·D)에만.

## Blur / Glow / Mask

엔진 SVG 백엔드는 가우시안 필터를 렌더하지 않는다. 두 가지 선택:

- **WAN 클립에 이미 블러/글로우/빛을 담아** 배경으로 깔면 그 감성이 그대로 살아난다(권장).
- 또는 렌더 후 ffmpeg 후처리(`gblur`, `bloom` 계열)로 전체에 은은한 글로우를 한 번 입힌다:
  `ffmpeg -i output.mp4 -vf "gblur=sigma=2:steps=1[b];[0][b]blend=all_mode=screen:all_opacity=0.35" glow.mp4`
  (엔진 밖 후처리 — 원본은 그대로 두고 별도 파일 생성.)
