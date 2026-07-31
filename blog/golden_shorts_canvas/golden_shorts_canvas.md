# golden_shorts_canvas — 무한 캔버스 팬·줌 릴 (인수인계 / 스펙)

배투실 쇼츠용 **새 포맷**. 큰 흰 종이(월드) 위에 그래프·제목·콜아웃을 좌표로 배치하고,
**카메라가 시퀀스대로 팬(이동)·줌하며 하나씩** 보여준다. 줌인(도착) 시 **그 그래프의 선이 그때 그려지는**
(드로우) 애니 + 끝값 라벨 등장. 카드/패널 없이 종이 위에 바로 그린다. (Prezi/데이터 다큐 스타일.)

- **파생 계기**: 파이어 골든(`../golden_shorts_fire/`)의 단일 그래프 애니에서 확장. 데이터는 파이어 폴더 것을 읽어 쓴다.
- **첫 실증 씬**: QYLD 커버드콜 ("남는 배당 QQQ에 재투자하면?" vs QYLD 재투자 / 같은 기간 SPY 대조).

---

## 0. 파일 구조

```
golden_shorts_canvas/
├── gen_canvas.py        # ★엔진: 블록 배치 + 카메라 시퀀스 + 드로우 애니 → out/canvas.html
│                        #   linechart(), build(), block(), scene_<name>() 저작 함수 노출
├── build_canvas.py      # playwright 녹화 → out/canvas_<scene>.mp4 (+ _preview). 길이 자동 계산
├── golden_shorts_canvas.md  # ★이 문서
├── assets/
│   └── paper_b64.txt    # 종이 텍스처(파이어 폴더에서 복사). 폰트는 ../fonts/PretendardVariable.woff2 참조
├── data/
│   └── qq_cmp.json      # QYLD→QQQ vs QYLD 재투자 시계열({A,B,init}). (파이어에서 생성해 복사)
└── out/                 # 산출물(html/mp4). 임시.
```

의존: `playwright`(chromium), `ffmpeg`, `../fonts/PretendardVariable.woff2`, `assets/paper_b64.txt`.

---

## 1. 실행

```bash
SHORTS_SCENE=qyld python3 gen_canvas.py     # out/canvas.html 생성
SHORTS_SCENE=qyld python3 build_canvas.py   # 녹화 → out/canvas_qyld.mp4 (+ _preview)
```
`build_canvas.py`가 `gen_canvas.py`를 먼저 자동 실행하고, 씬 길이(hold+이동)를 계산해 그만큼 녹화한다.

---

## 2. 씬 저작 (핵심)

`gen_canvas.py`의 `scene_<name>()` 함수 하나 = 영상 하나. 리턴 `(world_w, world_h, blocks_html, seq)`.

- **블록**: `block(id, x, y, w, inner_html)` — 월드 좌표(px)에 배치. 높이는 내용 자동. `class="block"`.
  - 제목: `<h1>...<b>파랑강조</b></h1><p>부제</p>`
  - 그래프 블록: `<h2>제목</h2><div class="s">부제</div>` + `linechart(...)`
  - 콜아웃: `<div class="big">$2.66M</div><div class="s">...<b class="hl">+$97만</b></div>`
- **선차트**: `linechart(w, h, series, cols, ends=[끝라벨], dashed=원금값)`
  - `series`=`[[[x,y],...], ...]`, `cols`=색 리스트. 선은 `class="ln"`(드로우 대상), 끝점·라벨은 `dot/lab`(페이드).
- **카메라 시퀀스**: `seq=[{"t": 블록id 또는 "ALL", "hold": 정지ms}, ...]`
  - 순서대로 팬·줌. `"ALL"`=월드 전체(줌아웃). 각 도착 시 그 블록 `reveal()`(불투명+선 드로우).
  - 이동 시간 `MOVE`(기본 1450ms). 카메라는 대상 bbox+여백(80px)을 1080×1920에 fit.

새 종목/주제 = `scene_<name>()` 추가 + `__main__`/`build_canvas`의 씬 맵에 등록.

---

## 3. 좌표·프레이밍 규칙

- 월드 좌상단 원점. 카메라 `lookAt(x,y,w,h,pad)`가 블록을 세로 뷰포트(1080×1920)에 맞춰 스케일.
- ⚠️ **가로로 넓은 그래프(예 1560×940)는 세로 화면에 맞추면 위아래 여백이 남아 옆 블록이 같이 보인다.**
  - 해결: ① 그래프를 **세로형**(폭 좁게·높이 높게)으로 만들거나 ② 블록 간격을 넓혀 이웃이 프레임 밖으로 나가게 배치.
  - 현재 데모는 이 이슈가 남아 있음(제목+그래프가 함께 보이는 컷 존재). **다음 개선 1순위.**

---

## 4. 디자인 컨벤션 (파이어 골든과 통일)

- 배경 종이 `#f4f0e8` + paper 텍스처. 텍스트 먹색 `#1a1a1a`/`#7a746a`. 강조 파랑 `#2b6cb0`.
- 선 색(팔레트): 파랑 `#2b6cb0` / 주황 `#d98f2b` / 라즈베리 `#c2255c`. 폰트 Pretendard 900.
- 드로우: `.ln` dashoffset 1.55s ease, 라벨 1.05s 지연 페이드. 카메라 이동 ease-in-out.

---

## 5. 상태 / TODO

- [x] 엔진(팬·줌 + 도착시 드로우), QYLD 데모 씬, build 파이프라인, 폴더 분리.
- [ ] **프레이밍**: 세로형 그래프로 한 컷=한 그래프 꽉 차게(§3).
- [ ] 카운트업 끝값(파이어처럼), 콜아웃 강조 모션, 화살표/주석(캔버스에 손그림 요소).
- [ ] 데이터 파이프라인 정리(파이어 fires.json 직접 읽는 헬퍼, qq_cmp 재생성 스크립트).
- [ ] 인트로/아웃트로, 배투실 마크(파이어 BADGE) 배치.

관련: 파이어 골든 `../golden_shorts_fire/golden_shorts_fire.md`(데이터·엔진 원천).
메모리: [[pg-golden-shorts-fire]] · [[video-pipeline-and-jnj]]
