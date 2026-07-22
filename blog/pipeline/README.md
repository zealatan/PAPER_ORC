# 배투실 영상 파이프라인

배당 백테스트 유튜브 영상을 **종목만 바꾸면 찍히는 라인**으로. 종목 1편 = `video_spec.json` 하나.
모든 단계가 이 spec을 읽고/되채운다 — 이게 **프로토콜**이다.

> 설계 근거: 멀티에이전트 병렬 조사 `wf_0c9ec72e-2f1` (백테스트/FIRE/덱/더빙·렌더 4개 서브시스템).
> 아키텍처 문서: https://claude.ai/code/artifact/45ab02e4-037c-4db0-8b24-b431e967606d

## 프로토콜 (`spec.py`)
`[IN]` 사람/큐레이션 · `[CALC]` 엔진 산출(덮어씀) · `[DERIVED]` 조립. 계약은 `spec.py`가 단일 원천.
```
python spec.py spec/KO.golden.json           # 계약 검증
python spec.py spec/KO.golden.json backtest  # 단계별 선행필드 검증
```

## 디렉토리
```
pipeline/
  spec.py                 ★ 계약: VideoSpec new_spec/validate/merge_calc/load/save   [구현됨]
  orchestrate.py            최상위 러너 (--spec --from --to)                          [stub]
  data/loader.py            headless 로더 + 월봉 리샘플 + CPI                          [stub]
  backtest/run.py           run(spec): FIRE 그리드 + 전략비교(목돈/적립/폭락매수)       [stub]
  sources/fundamentals.py   data.business (★결정론 소스 없음 → 큐레이션)               [stub]
  story/narration.py        대본 + 인용검증(대본 숫자 == 엔진값)                        [stub]
  deck/adapters.py          ★핵심: spec → tpl data 변환 (enginechart 등 18종)         [stub]
  deck/build.py             spec.scenes+deck_layout → 덱 JSON (sid 키)               [stub]
  deck/template.html        cocacola_final.html 종목고정부 제거 범용 렌더러            [예정]
  dub/run_dub.py            TTS→타이밍→음성트랙 폐루프                                 [stub]
  render/run_render.sh      덱주입→녹화→믹싱 (DUR 자동)                                [stub]
  assets/build_assets.py    썸네일·bg매핑·publish 메타                                 [stub]
  qa/reconcile.py           대조: 대본↔엔진, 덱↔backtest, 골든회귀                     [stub]
  curation/overrides/KO.yaml  큐레이션 사업개요(+출처)                                 [작성됨]
  spec/KO.golden.json       코카콜라 [IN] spec + 골든 참조                             [작성됨]
  out/KO/golden/            ★리팩터 전 동결한 회귀 기준선                              [동결됨]
```

## 재사용(★ 이미 구축됨 — 종목무관)
- 백테스트: `global_cup/{fire_engine,golden_engine,backtest_engine,data_loader,dividend_reinvest}.py` (검증됨)
- 더빙: `rec/{gen_tts,build_timing,build_voice,extract_lines}.py`
- 렌더: `rec/{record_full.sh,keep_fs.py,send_key.py,nav_raise.py,mix_audio.sh}`

## 구축 순서
1. **`spec.py`** — 계약 확정 ✅
2. **골든 동결** — `out/KO/golden/` (deck_dubbed·TTS·입력CSV) ✅ · `spec/KO.golden.json` ✅ · `overrides/KO.yaml` ✅
3. `data/loader.py` — streamlit 캐시 분리 headless + 월봉 리샘플 + CPI
4. `backtest/run.py` — FIRE 그리드+전략비교. `validate_fire` 불변식 통과 확인
5. `deck/adapters.py` — spec→tpl data (골든 좌표와 diff, **최난도**)
6. `deck/build.py` + `template.html` — sid 기반 ov/cp + 하드코딩 5블록 외부화
7. `sources/fundamentals.py` + `story/narration.py` — 큐레이션 + 인용검증
8. `dub/run_dub.py` — TTS 폐루프 (타이밍은 허용오차 대조)
9. `render/run_render.sh` — DUR 자동·{ticker} 경로화
10. `assets` + `orchestrate.py` + `qa/reconcile.py` — end-to-end 재현 → 골든 회귀 그린
11. 다른 티커 스모크(MSFT 등) — data→backtest→deck 구동, 에셋/큐레이션 공백 노출

## 5대 리스크
1. **사업개요 결정론 소스 부재** — 지역매출·브랜드는 코드로 못 만듦(증배연수만 계산 가능). 큐레이션 YAML+출처를 1급 입력으로.
2. **덱 HTML baked-in 5블록** — DEFAULT_SCENES/IIFE/SUBS/CHAPBG/MEDIA. OV/CP가 index 기반 → **sid 안정키 선행**, playwright 스냅샷 회귀 필수.
3. **TTS 타이밍 비결정성** — subTimes/subHold가 실측 길이 의존. tts/ 클립 캐시(voice_id+텍스트 해시) 고정 안 하면 매번 재녹화.
4. **엔진 계약 위반** — ZigZag close.max() 금지, fixed_real은 외부 cpi 주입 필수(USD→CPIAUCSL), golden mode 한국어 리터럴.
5. **에셋 종목의존** — bg클립·로고·썸네일은 수동 제작물. "종목만 바꾸면"은 데이터/백테스트/덱까지만 참. 에셋=수동 슬롯으로 경계 명확히.

## 원칙
**데이터는 엔진 · 대본은 인용 · QA는 대조.** 금융 콘텐츠라 정확성이 1순위. LLM이 숫자를 지어내지 못하게 막는 게 파이프라인의 존재 이유.
