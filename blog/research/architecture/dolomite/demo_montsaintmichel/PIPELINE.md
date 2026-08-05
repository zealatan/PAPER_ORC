# 건축쇼츠 제작 파이프라인 — 몽생미셸 데모

"신비한 건축사전" 스타일 세로 쇼츠(1080×1920) 제작 전체 과정.
이 폴더(`demo_montsaintmichel/`)가 레퍼런스 구현. **`rec/`는 종목 무관 재사용형** — 새 주제도 `manifest.json` + `images/` 만 갖추면 그대로 돈다.

---

## 0. 전체 흐름 한눈에

```
 주제/자료조사
     │  (build_*_baked.py — 단일 빌더가 프롬프트·매니페스트·갤러리 전부 생성)
     ▼
 prompts.txt · manifest.json · gallery.html · script.md · t2v.txt · i2v.txt
     │
     │  ┌─ [사람] 프롬프트 복사 → 외부 t2v(Veo/Kling) 또는 i2v(이미지→영상)
     ▼  ▼
 영상 클립 23개  ──drop──▶  gallery.html 슬롯  ──📁 저장──▶  images/shot01.mp4 … shot23.mp4
     │
     ▼   ┌──────────────── rec/ 렌더 파이프라인 (이 세션에서 구축) ────────────────┐
     │   │ 1) gen_tts.py    ElevenLabs 나레이션        → tts/sNN.mp3 + narration.json │
     │   │ 2) build_video.py 클립+TTS+하단자막 합성      → out/<NAME>_final.mp4         │
     │   │ 3) export.py     배포 파생물                 → _narration.mp3·_cuts.zip·_web.mp4│
     │   └──────────────────────────────────────────────────────────────────────────┘
     ▼
 out/montsaintmichel_final.mp4  (최종 배포본)
```

핵심 원칙(BAKED·숫자만): **치수·숫자·화살표는 t2v 프롬프트에 구워 AI가 화면에 직접 렌더**, 단어 라벨·제목 없음.
**한글은 화면 자막이 아니라 원래 TTS 나레이션** — 단, 이번 데모는 사용자 요청으로 **하단 한글 자막을 추가 번인**(최소 노출 청크).

---

## 1. 폴더 구조

```
demo_montsaintmichel/
├─ manifest.json          ★ 원본 데이터(shots[23]: id·t·dur·sentence_kr·style_class·transition·prompt_final…)
├─ prompts.txt / t2v.txt / i2v.txt / script.md   프롬프트·대본(빌더 산출물)
├─ gallery.html           프롬프트 갤러리 + 영상 드롭 업로드/저장/자동불러오기 UI
├─ images/                ★ 렌더 입력 클립  shot01.mp4 … shot23.mp4
├─ rec/                   ★ 렌더 파이프라인
│   ├─ gen_tts.py         TTS 생성
│   ├─ build_video.py     영상 합성 + 자막 번인
│   ├─ export.py          배포 파생물(mp3/zip/웹mp4)
│   ├─ render.sh          원커맨드 오케스트레이터
│   └─ narration.json     (자동생성) 컷별 나레이션 길이
├─ tts/                   (자동생성) sNN.mp3 + sNN.raw.mp3
└─ out/                   (자동생성) 최종본·파생물·tmp/
```

`.eleven_key`(ElevenLabs API 키)는 이 폴더에 없어도 됨 — 상위 경로에서 자동 탐색해 `blog/.eleven_key` 공유 사용.

---

## 2. 렌더 파이프라인 (rec/)

### 원커맨드
```bash
cd rec
./render.sh                 # TTS → 합성 → export 전체
STEP=tts    ./render.sh     # TTS만
STEP=build  ./render.sh     # 합성만 (클립 교체 후 재렌더)
STEP=export ./render.sh     # 배포물만
```

### 단계별
| # | 스크립트 | 입력 | 출력 | 핵심 |
|---|---|---|---|---|
| 1 | `gen_tts.py` | manifest `sentence_kr` | `tts/sNN.mp3`, `narration.json` | ElevenLabs `eleven_v3` 클론보이스. 컷당 1 mp3. **이미 있으면 건너뜀(재개)**, raw 보존→배속만 재조정 무료 |
| 2 | `build_video.py` | `images/shotNN.mp4` + `tts/` + manifest | `out/<NAME>_final.mp4` | 오디오 드리븐 합성 + 하단 자막 번인 |
| 3 | `export.py` | `out/<NAME>_final.mp4` + `tts/` | `_narration.mp3`·`_cuts.zip`·`_web.mp4` | 통합 나레이션 / 컷 mp3 묶음 / 30MB 이하 압축본 |

### 설계 포인트
- **오디오 드리븐 타이밍**: 각 컷 화면 길이 = 그 컷 나레이션 길이. 클립이 길면 트림, 짧으면 **마지막 프레임 프리즈**(ffmpeg `tpad`)로 연장 → A/V 싱크가 concat 전체에서 어긋나지 않음.
- **자막 최소 노출**: 한 문장을 문장부호 우선 + 어절 그리디로 **≤`MAXCH`자 청크**로 쪼개, 컷 시간을 글자 수 비례로 분배해 순차 표시. 하단 중앙, 나눔스퀘어 Bold 번인.
- **클립 오디오 제거**, TTS만 사용. 출력 1080×1920 / 30fps / H.264 crf19.

### 튜닝 환경변수
| 변수 | 기본 | 설명 |
|---|---|---|
| `NAME` | 폴더명에서 `demo_` 제거 | 출력 파일 접두 |
| `MAXCH` | 12 | 자막 한 청크 최대 글자수(작을수록 더 잘게) |
| `SUBS` | 1 | `0`이면 자막 끔(원칙상 무자막 버전) |
| `TTS_SPEED` | 1.0 | 나레이션 배속(음정 유지, atempo). raw 보존이라 재실행 저렴 |
| `TTS_STABILITY` | 0.4 | 낮을수록 표현적 |
| `WEB_MB` | 28 | 웹 압축본 목표 용량 |
| `W`/`H`/`FPS` | 1080/1920/30 | 해상도·프레임레이트 |

예: `MAXCH=10 STEP=build ./render.sh` (자막 더 잘게 재합성) · `SUBS=0 STEP=build ./render.sh` (무자막본).

---

## 3. 새 주제로 재사용하는 법

1. 새 폴더 `demo_<주제>/` 에 **`manifest.json`**(shots[].{id, sentence_kr} 필수) 준비 — 빌더로 생성.
2. `rec/` 폴더를 그대로 복사.
3. 프롬프트로 t2v 클립 생성 → `gallery.html`에 드롭·저장하거나 직접 `images/shotNN.mp4`로 배치.
4. `cd rec && ./render.sh` → `out/<주제>_final.mp4` 완성.

출력명·경로 전부 폴더에서 자동 도출되므로 스크립트 수정 불필요.

---

## 4. 함정 & 해결(중요)

| 증상 | 원인 | 해결 |
|---|---|---|
| TTS 전부 400 실패 | `eleven_v3`는 `previous_text/next_text` **미지원** | 문맥 파라미터 제거하고 호출 (현재 코드 반영됨) |
| 자막 앞에 유령 `,` | ASS `Dialogue` 필드 수 초과(`,,0,0,0,,`) → 남는 콤마가 Text로 샘 | 정답 `,,0,0,,` (현재 코드 반영됨) |
| 메신저 업로드 실패 | 원본 mp4 > 30MB | `export.py`의 `_web.mp4`(2-pass, 기본 28MB) 사용 |
| 나눔스퀘어 폰트 못 찾음 | fontsdir 미지정 | `subtitles=…:fontsdir=/usr/share/fonts/truetype/nanum` |

- 클립 원본은 브라우저 다운로드 폴더(`~/다운로드/shotNN.mp4`, 중복 `(1)` 무시)에서 `images/`로 복사.
- `gallery.html`은 `file://`로 열어도 `images/shotNN.*` 자동 로드됨(상대경로). 저장은 Chrome/Edge에서 `📁 폴더 저장`(File System Access API) 권장.

---

## 5. 이번 데모 확정 사양

- 23컷 · 87초 · 1080×1920 · 나레이션(ElevenLabs `Iu0W7wMhBwV2Qjzj0Fp2`) + 하단 자막
- cut12 자막: "대신에, 묘수를 고안해냅니다. 모래를 퍼내지 말고, 물로 밀어내기로."
- cut08/09: 디오라마→실사 대규모 극적 타임랩스 + 휘프전환/슬램줌인(동적 전환·모션그래픽)
- 최종본 `out/montsaintmichel_final.mp4`(53MB) / 배포 압축본 `_web.mp4`(≈28MB)
