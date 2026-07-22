# 배투실 — Animation Style 스튜디오

JNJ·개별 영상과 **무관한 독립 폴더.** 손그림(펜·잉크 세피아 그림책) 화풍의 일러스트를
ComfyUI Flux로 생성·관리한다. (참고 톤: 에그머니 채널)

## 구조
```
animation_style/
  illustration_bible.md   ← 화풍·캐릭터·시드 락 (프롬프트 단일 원천)
  gen/generate.py         ← ComfyUI Flux 생성기 (바이블 STYLE+캐릭터 자동 결합)
  refs/                   ← 확정 시안 (ref_A / ref_B / ref_AvsB)
  out/                    ← 생성 일러스트
```

## 전제
- ComfyUI 실행 중(localhost:8188) + `flux1-schnell-fp8.safetensors` 로드. GPU 공유 시 큐 확인.
- 1280x720, steps 4 / cfg 1 / euler / simple. 생성 ~35초/장.

## 사용
```
python gen/generate.py <name> <seed> "<영어 씬 프롬프트>" [A|B|none]
# 예 (캐릭터 A, 고정 시드 101):
python gen/generate.py hook_A 101 "holding an empty money sack, coins vanishing, luxury room, shocked expression" A
```
STYLE과 캐릭터 묘사는 `illustration_bible.md`와 `generate.py`에 동일하게 락돼 있어
**같은 시드+같은 캐릭터**면 씬이 달라도 인물이 유지된다(완벽 동일 X, "같은 그림책 세계관" 수준).

## 캐릭터 (락)
- **A** 부자→파산: 뚱뚱·대머리·나비넥타이 정장·둥근 뿔테 · **seed 101**
- **B** 검소→부자: 마른·백발·가디건·가는 안경 · **seed 202**

## 참고
- 우하단 AI 잡글씨(가짜 서명)는 최종에서 크롭/가림.
- 이 화풍을 영상에 쓸 땐: 정적 일러스트 + 카메라 줌·팬(켄번즈). 차트 씬은 종이·펜선 톤으로 통일.
