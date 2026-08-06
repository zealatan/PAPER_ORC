# YouTube Motion Studio — Cinematic Showcase 리포트

목적: 기능 테스트가 아니라 **"이 엔진으로 이런 영상까지 만들 수 있다"**를 보여주는 고품질
쇼케이스. 새 엔진 기능은 만들지 않고 **우회 · 조합 · 디자인**으로만 완성했다.

출력: 전부 `720×1280 / 15fps / H.264 / yuv420p / 무음`, 5~10초. 갤러리 `showcase/gallery/index.html`.
각 폴더: `project.json` `output.mp4` `poster.png` `contact-sheet.png` `validation.json`.

## 1. 생성된 MP4 10개 · 크기 · 렌더 시간

| #   | 스타일        | 클립                 |  길이 |   크기 | 렌더 |
| --- | ------------- | -------------------- | ----: | -----: | ---: |
| 01  | Apple Keynote | Apple Product Reveal | 9.07s | 0.14MB | 2.5s |
| 02  | Bloomberg TV  | Bloomberg Finance    | 7.87s | 0.14MB | 3.9s |
| 03  | MagnatesMedia | Mini Documentary     | 8.80s | 0.13MB | 2.4s |
| 04  | Documentary   | Ronald Read Story    | 8.20s | 0.09MB | 1.9s |
| 05  | Kurzgesagt    | Infographic          | 7.20s | 0.09MB | 1.7s |
| 06  | Netflix       | Netflix Style        | 7.87s | 0.07MB | 0.9s |
| 07  | Dashboard     | Business Dashboard   | 6.20s | 0.11MB | 4.4s |
| 08  | Finance       | Finance Timeline     | 8.00s | 0.10MB | 3.1s |
| 09  | Kinetic Type  | Motion Typography    | 5.80s | 0.08MB | 0.7s |
| 10  | Showreel      | Ultimate Showreel    | 9.27s | 0.16MB | 1.6s |

- **렌더 성공 10/10**, 전부 moov atom 정상, 길이 5~10초 준수.
- **총 용량 1.2MB**(개당 0.07~~0.16MB) — 목표 1~~3MB보다 훨씬 작음. 벡터 그래픽 + 15fps + 720p라
  git 저장·미리보기에 이상적(스펙의 "매우 작아야 한다"에 부합).
- 총 렌더 ~23초(10편 합).

## 2. 이 엔진이 "실제로 잘하는" 것 — 쇼케이스에서 활용

- **그라디언트 배경**(linear, angle+stops): Apple 다크, Bloomberg 네이비, 다큐 세피아,
  Kurzgesagt 딥블루/퍼플 — 스타일 정체성의 핵심.
- **Ken Burns / 카메라 줌**: 키프레임 `scale` 채널로 텍스트·패널을 천천히 확대(01·03·06·10).
- **헤비 타이포**(Black Han Sans) + 정적 tilt(키네틱 09).
- **stagger 등장**(timing 오프셋), 프리셋(fade/pop/scale/zoom/slide).
- **차트**(축·범례·area), **표**, **topic-circle 로고**, **레이어드 반투명 "글로우"**(디자인).

## 3. 현재 엔진으로 표현하지 못한 부분 (우회 방식)

절대 원칙(새 기능 금지)대로 아래는 **디자인으로 우회**했다. SVG 백엔드가 렌더하지 않는 것들:

| 원했던 것                       | 엔진 상태        | 우회                                   |
| ------------------------------- | ---------------- | -------------------------------------- |
| Blur / Glow (가우시안)          | filter 미렌더    | 큰 반투명 패널을 뒤에 깔아 유사 글로우 |
| Drop Shadow                     | 미지원           | 어두운 오프셋 패널 or 생략             |
| Mask / Clip 리빌                | radius clip만    | 차트 draw-on 대신 fade/scale           |
| 회전 애니메이션                 | rotate 채널 없음 | 정적 tilt(transform.rotation)만        |
| 실제 사진/이미지                | 에셋 없음        | 그라디언트·패널로 스타일화한 "액자"    |
| Radial / per-element 그라디언트 | 배경 linear만    | 원형 반투명 dot/panel로 대체           |
| 텍스트 자동 줄바꿈              | 단일 줄          | 여러 요소로 분리                       |
| 장면 간 디졸브 전환             | 하드 컷          | 요소 entrance 애니로 전환감            |
| 모션 블러                       | 없음             | 생략                                   |

→ 영상 품질은 이 우회들로 충분히 "시네마틱"하게 나왔지만, 진짜 고급 룩(블러 글로우·이미지·
디졸브)을 위해선 아래 기능이 필요하다.

## 4. 앞으로 필요한 기능 Top 10

1. **이미지/사진 에셋 파이프라인** — data-URL/파일 이미지 로드 + object-fit(다큐·제품·인물 필수).
2. **필터: Gaussian Blur / Drop Shadow / Glow** — SVG `feGaussianBlur`/`feDropShadow` 렌더.
3. **장면 전환 합성**(transitionIn/Out) — 디졸브·슬라이드·딥투블랙 실제 블렌딩.
4. **회전·위치 키프레임 채널** — 현재 scale/opacity만; rotate/translate 추가(키네틱·궤도 모션).
5. **Radial / conic 그라디언트 + per-element 그라디언트** — 비네트·스포트라이트·버튼.
6. **클립 기반 draw-on 애니메이션** — 차트 선/막대가 그려지는 표현, 마스크 와이프.
7. **숫자 카운터 컴포넌트**(시간 인식 포맷·이징) — 금융/실적 영상의 핵심.
8. **텍스트 자동 줄바꿈 + 리치 텍스트**(부분 색/굵기) — 긴 문장·강조.
9. **모션 블러 / 셔터** — 빠른 이동·컷에 영화적 질감.
10. **긴 장면 프레임-청크 병렬 렌더** — 렌더 속도(현재 장면 단위 병렬의 한계).

## 5. 가장 완성도 높은 영상

- **02 Bloomberg** — 하단 티커(lower-third) + BREAKING 바 + 숫자 교체 + area 라인차트가 실제
  방송 그래픽처럼 맞물린다. "엔진으로 방송 CG가 된다"를 가장 잘 보여줌.
- 그다음 **10 Ultimate Showreel**(10장면에 차트·카드·타임라인·로고·타이포·엔딩을 8.9초에 압축)과
  **01 Apple**(그라디언트+Ken Burns+여백의 절제미).

## 6. 재현

```
pnpm showcase:all              # generate→preview→render→validate→gallery
pnpm showcase:all --skip-existing
```

생성물은 gitignore(재현 가능). 소스만 커밋.
