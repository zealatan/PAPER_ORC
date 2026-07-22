# JNJ 영상 제작 — 세션 인수인계

## 0. 목표
**존슨앤드존슨(JNJ) 배당 백테스트 유튜브 영상 1편**을 코카콜라 방식으로 제작.
산출물: ① 본편(1080p60, 본인 클론 목소리 더빙) ② 썸네일 ③ 쇼츠(세로).

이 문서 하나로 처음부터 끝까지 갈 수 있게 썼다. 막히면 `ref/`의 **코카콜라 완성본을 예시로** 참고.

## 0.5 ⭐콘텐츠 구조 — 백테스트 중심 (코카콜라 실제 성과에서 배운 것)
> 코카콜라 1편(https://youtube.com/watch?v=-yv2igFEaZc) 공개 후 확인: **시청자가 원하는 건 백테스트**다.
> 회사 소개·사업개요·닷컴버블 시점분석 같은 "설명" 파트는 관심이 떨어진다.

**그래서 JNJ는 군더더기 다 빼고 3부 구성으로 짧고 강하게:**
1. **후킹 영상** — 같은 JNJ 주식, 넉넉히 쓴 A는 파산 / 아껴 재투자한 B는 부자. 궁금증 유발.
2. **파산 시나리오 백테스트** — "얼마 있으면, 매달 얼마 쓰면 버티나/파산하나". 원금 $200k/$400k/$600k × 월 $1k/$2k/$3k FIRE 백테스트가 **핵심**.
3. **매수 방법 백테스트** — 목돈 vs 매달 적립 vs 폭락매수, 뭐가 이기나. 전략비교 백테스트.

**과감히 컷(코카콜라엔 있었지만 JNJ선 빼거나 최소화):**
- 회사 소개(herostat/card 인트로), **사업개요 섹션 전체**(regionmap/divbars/cupdrain/kpirow/quad = "지금 사도 될까" 부분), 닷컴버블 시점위험·2002년 재시작·생존지도, 긴 결론.
- (배당왕·배당성향 정도만 1~2씬으로 짧게 언급하거나 아예 생략)

→ 결과: 코카콜라 12분 → **JNJ는 5~7분** 목표. 밀도 높게. **§3-C·§3-D의 씬 골격은 이 3부에 맞춰 설계.**

---

## 1. 작업 환경 (이 GPU 박스, DGX Spark)
- 작업 루트: `/home/messi/PAPER_ORC/blog` · JNJ 폴더: `blog/JNJ/`
- **GPU 있음** → firefox가 배경영상 부드럽게 재생 + NVENC 인코딩. 렌더는 반드시 이 머신에서.
- **오디오 장치 없음** → 목소리는 TTS(일레븐랩스 클론)로만. 마이크 녹음 불가.
- **TTS 키**: `blog/.eleven_key` (gitignore됨). 클론 보이스 ID `Iu0W7wMhBwV2Qjzj0Fp2` ('messi', 본인 목소리).
- **디스플레이**: GNOME on Xorg `:1`, HDMI 1920x1080. 원격 데스크톱 접속.
- **공유 데스크톱 주의**: 다른 Claude 세션이 firefox 열면 렌더 전체화면이 깨짐 → `rec/keep_fs.py` 자동복구가 방어하지만 녹화 중 화면 안 건드리는 게 안전.

---

## 2. 이미 세팅된 것 (`blog/JNJ/`)
```
JNJ/
  HANDOVER.md         ← 이 문서
  PROTOCOL.md         ← 파이프라인 구조/플랜 (video_spec 프로토콜, 구축순서, 5리스크)
  spec/
    spec.py           ← 프로토콜 계약 (validate/merge_calc). python spec.py ../spec/JNJ.json
    JNJ.json          ← JNJ [IN] 스펙 골격 (window·FIRE그리드·voice 채워짐, 나머지 비어있음)
  curation/JNJ.yaml   ← 사업개요 리서치 템플릿 (TODO 채우기)
  deck/
    jnj_final.html    ← 코카콜라 덱 복사본 = JNJ로 개조할 베이스 (3.1MB, 렌더 엔진)
    tools/            ← 덱 제작 도구(§3-D): gen_storyboard_v3(스토리보드+dur), build_cur33(JSON조립),
                        gen_pages_30_31_32·gen_page16_smart(백테스트→차트), ko_smart_vs_steady(전략엔진)
  rec/                ← 더빙·렌더 스크립트 12개 (종목무관, ⚠경로수정 필요 §5-E)
  fonts/BlackHanSans-Regular.ttf  ← 썸네일/쇼츠 제목 폰트
  ref/                ← 코카콜라 완성 예시 (deck_dubbed / narration_lines / KO.yaml) + CPI csv
  assets/             ← JNJ 배경영상·썸네일 (비어있음, 만들어 채움)
  out/                ← 렌더 산출물
```
전역 재사용(복사 안 함, 그대로 참조):
- **백테스트 엔진**: `global_cup_suite/global_cup/{fire_engine,golden_engine,backtest_engine,data_loader,dividend_reinvest}.py`
- **파이프라인 스켈레톤**: `blog/pipeline/` (spec 계약 + 골든 + 스텁, 아직 미완성)
- **아키텍처 문서**: https://claude.ai/code/artifact/45ab02e4-037c-4db0-8b24-b431e967606d

---

## 3. 제작 워크플로우 (코카콜라 방식 그대로, 순서대로)

### A. 백테스트 데이터 산출  →  `spec/JNJ.json`의 `data`+`backtest`
JNJ 가격·배당을 받아 FIRE 시나리오(원금×월인출×물가반영)와 전략비교(목돈/적립/폭락매수)를 계산.
- 엔진: `global_cup_suite/global_cup/fire_engine.py:73 run_fire_backtest(close, dividends, initial_amount, annual_withdrawal=, strategy='fixed_nominal'|'fixed_real', frequency='monthly', tax_rate_pct=15, cpi=, ...)`
- 전략비교: `golden_engine.py:266 run_backtest(close, mode, ...)` — mode 4종(한국어 리터럴 주의): '시작일 일시불 투자'=목돈 / '매월 정액 투자'=적립 / '트리거 발생 시 정액 투자'=폭락매수
- 데이터: `data_loader.download_price/download_dividends`(yfinance) — ⚠`@st.cache_data`(streamlit) 결합 → headless 실행 시 streamlit 필요하거나, `blog/ko_smart_vs_steady.py`처럼 yfinance 직접 호출.
- **CPI(물가반영)**: `fixed_real`은 외부 `cpi: pd.Series` 주입 필수. USD→`fred_CPIAUCSL.csv`(코카콜라 골든에 있음: `pipeline/out/KO/golden/fred_CPIAUCSL.csv` 재사용).
- 그리드: 코카콜라와 동일 `inits=[200000,400000,600000], monthlies=[1000,2000,3000]` (JNJ.json에 이미 설정).
- 참고 스크립트: `blog/fire_feasibility/gen_fire_corpus.py`(원금×월인출 그리드→시나리오 JSON), `blog/ko_smart_vs_steady.py`(전략비교, KO 하드코딩→JNJ로).
- **산출**: 각 시나리오 {생존여부, 파산연도, 최종자산, 자산궤적 pts[]}. 이게 덱 차트(enginechart)의 series 데이터가 됨.

### B. 사업개요 리서치  →  `curation/JNJ.yaml`
결정론 코드로 못 만드는 부분(사업부문·배당연수·최근실적·시총). **딥리서치로 채우고 각 수치에 출처**.
- ⚠**JNJ 특이사항**: 2023년 소비자건강 **Kenvue 분사** → 현재 2개 부문(**Innovative Medicine**=제약, **MedTech**=의료기기). 코카콜라의 "200개 브랜드" 앵글 대신 "제약+의료기기 파이프라인·배당왕" 앵글.
- JNJ = **배당왕(Dividend King)**, 60년+ 연속 증배 (배당시리즈에서 연수 결정론 재계산 가능).
- `/deep-research` 스킬 활용 추천. 출처 없는 숫자는 대본에 쓰지 말 것(QA 원칙).

### C. 대본/스토리  →  `spec/JNJ.json`의 `story`  (⭐§0.5 3부 구성)
- **1부 후킹**: 같은 JNJ 주식, 넉넉히 쓴 A는 파산 / 아껴 재투자한 B는 부자 (A단계 백테스트 결과에 맞춰 숫자 조정). A/B 인물 대비.
- **2부 파산 시나리오 백테스트**: "$200k/$400k/$600k로 은퇴, 매달 $1k/$2k/$3k 쓰면?" → 각 케이스 생존/파산연도/최종자산. 물가반영(fixed_real) 버전이 임팩트. **여기가 본편의 심장.**
- **3부 매수 방법 백테스트**: 25년간 목돈 vs 매달 적립 vs 폭락(-30%)매수 → 최종자산 비교, 뭐가 이기나.
- (짧은 유의사항 1씬 + 짧은 마무리/구독 1씬만. 사업개요·시점분석·생존지도는 §0.5대로 컷.)
- **철칙**: 대본의 모든 숫자·연도는 A단계 백테스트 결과를 **인용만**. 지어내면 안 됨. `ref/cocacola_narration_lines.EXAMPLE.json`은 톤 참고용(단 코카콜라는 풀버전이라 2/3만 발췌).

### D. 덱(HTML) 제작 — 세분화 ⭐가장 복잡, 스토리보드 기반
덱의 실체 = **씬 JSON 배열** `{scenes:[{tpl,dur,cam,data,bgid,subLines,subTimes,subHold}], ov, cp, theme, paper}`.
HTML(`jnj_final.html`)은 이 JSON을 **localStorage**에서 읽어 렌더하는 **엔진**(TPL 템플릿 + engChart). 즉 "HTML 만들기"="씬 JSON 만들기".
> 참고 원본: `gen_storyboard_v3.py`(스토리보드+대본+dur), `build_cur33.py`(덱 JSON 조립), `gen_pages_30_31_32.py`·`gen_page16_smart.py`(백테스트→차트데이터). `ref/cocacola_deck_dubbed.EXAMPLE.json`=완성 덱 예시.

**D1. 씬 골격(스토리보드) 설계** — ⭐§0.5 3부에 맞춘 **린 골격 ~12~16씬**(코카콜라 31씬 → 대폭 축소):
  ```
  1부 후킹    videohook(훅영상) → notice(짧은 유의사항) → solostory×2(A 파산 / B 부자)
  2부 파산BT  interlude(전환) → enginechart×3 ($200k/$400k/$600k, 물가반영, 3케이스 파산)
              [옵션] survheat(생존지도) 1씬으로 요약 가능
  3부 매수BT  interlude → enginechart×2~3(폭락매수 vs 적립 결과) → hbars2(전략 비교)
  마무리      quotebig 또는 card (구독 유도) 1씬
  ```
  - 쓰는 tpl은 `videohook·notice·solostory·interlude·enginechart·hbars2·survheat·quotebig·card` 정도면 충분. (regionmap/divbars/cupdrain/kpirow/quad = 사업개요용 → **JNJ선 안 씀**)
  - `ref/cocacola_deck_dubbed.EXAMPLE.json`에서 **해당 tpl 씬만 골라** 형태 참고. `gen_storyboard_v3.py`의 `SB=[]`가 씬별 {대본,배경,요소,자료} 원본 형태.

**D2. 씬 dur 산출** — 대본 글자수 기반. `gen_storyboard_v3.py:62` 로직: `dur = 글자수(공백제외)/RATE(5자/s) + BUF(1.3s)`. 단, 최종 타이밍은 **더빙 TTS 실측**(subHold/subTimes)이 덮어씀(E단계). D2는 초안용.

**D3. enginechart 차트 데이터** — ⭐백테스트→차트. `engChart(c)` 렌더러가 요구하는 형태:
  - `data.chart = {kind:'line', x:[시작,끝], y:[0,최대], yticks, xticks, series:[{pts:[[year,value],...], c:색, w:굵기, name:라벨, end:끝점라벨}], hline:{v,label}}`
  - `series[].pts`가 **A단계 백테스트의 자산궤적**(fire_engine timeline_df를 [연,값]으로, ~3개월 샘플). `end`=파산연도/최종자산 라벨.
  - `data.table = {cols, rows:[[…]]}` (물가연동 인출액 표 등).
  - 방식: `gen_pages_30_31_32.py`처럼 백테스트 엔진 import→run→pts 포맷. JNJ는 `ko_smart_vs_steady`를 JNJ로 파라미터화하거나 `global_cup/fire_engine`+`golden_engine` 직접 호출.

**D4. 나머지 tpl data 채우기** — 각 tpl이 요구하는 필드(EXAMPLE.json에서 형태 확인):
  - `herostat`{eyebrow,num,label,sub} · `card`{eyebrow,main,sub,chips:[[값,라벨]]} · `regionmap`{지역/부문 데이터} · `divbars`{연도별 배당} · `cupdrain`{value,label(배당성향%)} · `kpirow`{KPI들} · `quad`{4칸} · `checks`{항목들} · `solostory`{side,label,kick,tag,rows,accent} · `quotebig`{인용문}
  - 값은 **A(백테스트)·B(사업개요)에서만** — 지어내기 금지.

**D5. 자막(subLines)** — 각 씬 `data`가 아니라 씬 최상위 `subLines:[줄1,줄2,…]`. 대본(C)을 씬별로 분배. 없으면 HTML의 `SUBS` 폴백(코카콜라 대본이므로 JNJ는 반드시 subLines로 덮어쓸 것).

**D6. 배경·토큰**:
  - `bgid` → `CHAPBG`(HTML:1764)의 `bg/<id>.mp4`. 코카콜라 20클립은 음료테마 → **JNJ 헬스케어 배경영상 새로 생성**(수동 에셋), CHAPBG에 JNJ bgid 추가.
  - `{{coke}}` 등 토큰 → `MEDIA`(HTML:1927)의 로고. JNJ 로고를 `{{jnj}}`로 추가, solostory/checks/CP의 `{{coke}}` 하드참조를 JNJ로 교체.

**D7. 덱 JSON 조립** — `build_cur33.py` 방식: `{scenes, ov, cp, theme:'paper', paper:'photo'}`.
  - `ov`(요소 위치 오버라이드)·`cp`(요소별 커스텀 HTML)는 ⚠**인덱스 기반**이라 씬 순서 바뀌면 깨짐 → JNJ 씬 구성 확정 후 조정. → `jnj_deck.json`.

**D8. localStorage 주입 + 렌더 확인** — 로더 html(코카콜라 `_recload_dubbed.html` 복사→JNJ용)이 `jnj_deck.json`을 KEY에 setItem 후 `jnj_final.html?rec`로 리다이렉트. ⚠KEY를 `tplCatalog_jnj_v1`로 바꿔 코카콜라와 분리(jnj_final.html `const KEY=` 수정).

**D9. 스토리보드 리뷰 + 편집 미세조정** — `python gen_storyboard_v3.py jnj_deck.json` 으로 썸네일+대본 스토리보드 HTML 생성해 흐름·dur 검토. 브라우저 편집모드(HUD)로 카메라(줌/팬)·자막 위치·OV/CP 미세조정 후 저장(localStorage→JSON 역추출).

> ⭐ 파이프라인(`blog/pipeline/`)에서 이 D단계는 3개 모듈로 세분: `deck/adapters.py`(D3·D4: spec→tpl data 변환) · `deck/build.py`(D7: JSON 조립, sid 키) · `deck/template.html`(D8: 렌더 엔진). 지금은 스텁 → JNJ는 수동으로 D1~D9 진행하되, 이 경계대로 작업하면 나중에 자동화로 승격 쉬움.

### E. TTS 더빙  →  본인 목소리 나레이션 + 덱 타이밍
`rec/` 스크립트 체인. ⚠**JNJ용 경로 수정 필요**(코카콜라 하드코딩):
1. `rec/extract_lines.py`, `calc_duration.py`, `build_timing.py` 내 `'cocacola_final.html'` → `'deck/jnj_final.html'`, `'cocacola_deck_current.json'`/`'cocacola_deck_dubbed.json'` → JNJ 파일명으로.
2. `rec/gen_tts.py`: `VOICE="Iu0W7wMhBwV2Qjzj0Fp2"` 그대로, `TTS_STABILITY=0.35 TTS_SPEED=1.18`(코카콜라 확정값), 앞뒤 문맥(previous/next_text) **넣지 말 것**(eleven_v3 미지원).
3. 순서: `extract_lines.py`(자막→줄) → `gen_tts.py`(363줄류 TTS, 재개가능) → `build_timing.py`(오디오 길이→subTimes/subHold→덱 타이밍 JSON) → `build_voice.py`(음성트랙 조립, pydub).
- 필요 패키지: `pip install python-xlib ewmh pydub audioop-lts`(Python 3.13은 audioop-lts 필수).

### F. 렌더  →  `out/` 마스터 mp4
firefox로 덱을 전체화면 재생하며 화면녹화(rec/record_full.sh). **코카콜라에서 확립한 함정 많음 → §5 필독**.
1. http 서버: `blog/`에서 `python3 -m http.server 8000 --bind 127.0.0.1`
2. 덱 로드: 로더 html로 JNJ 덱 JSON을 localStorage에 주입 후 `jnj_final.html?rec`로 리다이렉트
3. firefox 실행: **`gtk-launch firefox_firefox "URL"`** (직접/systemd-run은 죽음. 세션 env 필요 §5)
4. 전체화면: `rec/nav_raise.py`(EWMH). `?rec`은 HUD 숨김+풀블리드 CSS+Home재시작키 활성(코카콜라 덱에 추가돼 있음, 복사본이라 그대로 있음)
5. 녹화: `rec/record_full.sh <winid> out/jnj_master.mp4 <초>` — 씬0 재시작(Home)+keep_fs 자동복구+ffmpeg x11grab h264_nvenc. 초 = `calc_duration.py`로 산출
6. 믹싱: `rec/mix_audio.sh out/jnj_master.mp4 voice_track.wav out/jnj_final.mp4` (loudnorm -16 LUFS)

### G. 썸네일 + 쇼츠
- **썸네일**: PIL 합성. 코카콜라는 배경이미지 + 검은고딕(BlackHanSans) 제목("5억"노랑) + 배투실 마크(회색 초크, 우하단 작게). 배경 AI 이미지는 별도 생성. 옛 글자 지우기는 cv2.inpaint. 폰트 `fonts/BlackHanSans-Regular.ttf`.
- **쇼츠**: 본편에서 핵심 씬(예: $200k 3케이스 파산 차트) 세로 9:16 재편집. ffmpeg로 블러배경(cover+gblur)+중앙 16:9 영상+상단 훅 오버레이(PNG)+하단 마크. 코카콜라 쇼츠 필터 예시는 이 세션 로그 참고.

---

## 4. JNJ 특이사항 (코카콜라와 다른 점)
1. **Kenvue 분사(2023)**: 소비자건강(타이레놀·리스테린 등)은 이제 별도 회사. JNJ = 제약+의료기기. "브랜드 200개" 앵글 안 됨.
2. **섹터 앵글**: 음료→헬스케어. 훅/비주얼(배경영상 테마)을 헬스케어/제약/의료 이미지로.
3. **배당왕**: 코카콜라 64년 vs JNJ 60년+ — 둘 다 배당 안정성 앵글 강함.
4. **주가 특성**: JNJ는 KO보다 방어적. FIRE 백테스트 결과(파산연도)가 다를 것 → 대본 숫자 전부 재계산 필수.
5. **배경영상·로고**: 코카콜라 bg/*.mp4는 재사용 불가(음료 테마). JNJ용 헬스케어 배경영상 새로 생성 필요(수동 에셋).

---

## 5. 코카콜라에서 배운 함정 (반드시 읽기)
- **firefox 실행**: snap firefox는 bash 직접실행/systemd-run/snap run 다 **즉시 죽음**. 유일하게 되는 법 = `gtk-launch firefox_firefox "URL"`. 세션 env 필수: `XDG_RUNTIME_DIR=/run/user/1000`, `DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus`, `DISPLAY=:1`, `XAUTHORITY=/run/user/1000/gdm/Xauthority`.
- **창 제어**: xdotool/wmctrl 없음(sudo 불가). `pip install python-xlib ewmh` → `rec/nav_raise.py`(전체화면), `rec/send_key.py`(F11/Home/Ctrl+Shift+R via XTEST), `rec/keep_fs.py`(전체화면 자동복구).
- **렌더 중 전체화면 깨짐**: 다른 firefox 창이 열리면 깨짐 → keep_fs가 0.7s내 복구. 녹화 전 firefox 단일창 확인.
- **풀블리드**: 덱은 기본 1400px 카드(여백 있음). `?rec` 모드에서 풀블리드 CSS로 화면 꽉 채움(코카콜라 덱에 추가됨). Home키 = 리로드 없이 씬0 재시작(전체화면 유지).
- **totem 코덱 없음**: mp4 재생은 firefox나 ffplay로(totem은 h264 못 봄).
- **TTS**: eleven_v3는 previous_text/next_text **미지원**(400 에러). 속도는 voice_settings.speed 대신 **ffmpeg atempo**로. 실패분은 gen_tts 재실행하면 재개(스킵).
- **파일 전송**: SendUserFile은 30MB 한도. 큰 파일은 LAN 서버(`python3 -m http.server 8080 --bind 0.0.0.0`, box IP 192.168.2.144) 또는 다운로드 폴더 복사.
- **골든 회귀**: `pipeline/out/KO/golden/`이 코카콜라 기준선. JNJ는 신규라 골든 없음 — 첫 완성본이 JNJ 골든이 됨.

---

## 6. 참조
- **PROTOCOL.md** (이 폴더) — video_spec 프로토콜·구축순서·리스크
- **ref/*.EXAMPLE.*** — 코카콜라 완성 덱·나레이션·큐레이션 (형태 그대로 따라하기)
- **아키텍처 아트팩트**: https://claude.ai/code/artifact/45ab02e4-037c-4db0-8b24-b431e967606d
- **메모리**: `cocacola-recording-pipeline` (렌더 파이프라인 상세)
- **완성된 코카콜라**: `blog/recordings/cocacola_dubbed_final.mp4`(본편), `cocacola_shorts_bt.mp4`(쇼츠), `thumb_final_v6.png`(썸네일) — 목표 품질 기준

## 7. 첫 스텝 (다음 세션이 바로 할 것)
1. `git pull` 후 이 문서 + PROTOCOL.md 읽기
2. **A단계 백테스트부터**: `global_cup` 엔진으로 JNJ FIRE 시나리오 산출 → `spec/JNJ.json`의 backtest 채우기
3. 동시에 **B단계 리서치**(`/deep-research`로 JNJ 사업개요 → `curation/JNJ.yaml`)
4. 그다음 대본 → 덱 개조 → TTS → 렌더 → 썸네일/쇼츠 (§3 순서)

병렬화 가능한 곳(리서치·대본 섹션·썸네일안)은 멀티에이전트(Workflow)로.
