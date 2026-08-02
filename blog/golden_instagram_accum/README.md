# golden_instagram_accum ❄️ FROZEN (golden reference)

**적립 vs 폭락매수** 인스타 릴(1080×1920) 파이프라인. "매달 꾸준히 적립 vs 폭락 때만 매수 — 뭐가 이겼을까?"를 실제 과거 데이터로 비교한다. `golden_instagram_fire`(은퇴 인출)의 자매편이며 렌더 인프라를 이식·개조했다.

> 골든 레퍼런스. 새 실험은 복제 후 진행하고 여기 소스는 합의 없이 바꾸지 말 것.

## 완성 릴 스펙(동결본)

- 캔버스 1080×1920, 30fps, 총 40초(2초 후킹 + 30초 리빌 + 홀드). x축이 시간따라 확장(y는 활성 리빌 최댓값에 맞춰 성장).
- 대표 **30% 하락매수** 1종만 표시(`ACCUM_THR`로 20/50 전환 가능).
- **4선**: 적립 평가액(스카이블루 `#38bdf8`)·폭락매수 평가액(앰버 `#f59e0b`) 뚜렷 + 각 누적투자원금 **점선 2개**(은은). 끝점=원형 링 마커.
- 헤더: 흰색 2줄 "매달 적립 vs 폭락매수 / {종목}, 뭐가 이겼을까?".
- 날짜(테스트 기간)는 그래프 **왼쪽 상단 위**.
- 결과 수치는 **하단 범례 옆**(스와치+전략명+평가액, 리빌 중 라이브 업데이트): "매달 $1,000 적립 · 30% 하락 시 매수".
- 축/그리드 라인은 은은한 `#242424`(굵은 축선 없음), 글자는 `#b3b3b3`로 구분(레퍼런스 감성).
- 하단 기준 표기 + 좌우60/상하50 프레이밍.

## 재현

```bash
cd blog/golden_instagram_accum
# 1) 데이터(엔진 ko_smart_vs_steady) → assets/data/<pref>_accum.json
SHORTS_STOCK=QQQ python3 gen_accum.py
# 2) 릴 렌더(대표 30%)
SHORTS_STOCK=QQQ [ACCUM_THR=30] python3 build_instagram_accum.py
# 3) 프레이밍
ffmpeg -y -i exports/qqq_accum_reel.mp4 \
  -vf "scale=960:1820:flags=lanczos,pad=1080:1920:60:50:black" \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart \
  exports/qqq_accum_reel_up50.mp4
```

종목: QQQ·PG(로컬CSV)·SKH(SK하이닉스 000660·2006~)·SEC(삼성전자 005930·2016~)·KT(030200.KS·2000~). 통화 자동(억/만원 vs $K/$M).

## 번외 — 적립 vs 폭락매수 vs 일시금 (build_lump.py) ❄️

같은 총 투입원금을 **방법만 다르게** 넣은 3선 비교. 적립식·N%폭락매수 평가선(accum JSON 재사용) + 총액을 시작연도에 **한 번에** 넣은 **일시금(buy&hold + 배당 재투자, `fire_engine`)** 선을 얹는다. 정적 PNG + 애니 릴 동시 산출.

```bash
SHORTS_STOCK=KT [ACCUM_THR=30] python3 build_lump.py
# → exports/kt_lump_compare.png · exports/kt_lump_reel(_top100px).mp4
```

- 3선 색: 폭락매수=초록 `#4ade80`·적립=파랑 `#60a5fa`·일시금=핑크 `#f472b6`(승/평/패 직관 매핑). 끝점 링.
- 회색 점선 = **투입원금(손익분기)** 기준선, y축 좌측 "투입원금/금액" 2줄 라벨.
- 제목 "적립 vs 폭락매수 vs 일시금 / {종목} · 같은 돈, 넣는 방법만 다르게". 우하단 "번외".
- 인사이트: **고점 일시금의 타이밍 위험**. KT(2000 통신버블 고점)는 일시금이 원금(3.2억) 밑(2.5억)에 그친 반면 나눠 산 두 방법은 7~9억. 단 우상향장에선 일시금이 유리할 때가 많음(면책).

## 번외 — 배당 눈덩이 (build_divsnowball.py) ❄️

한 번 매수 후 보유하며 배당을 **재투자 O vs X** 했을 때, 주가·총자산이 아니라 **'받는 배당금' 자체**(연·누적)가 어떻게 벌어지는지. 재투자 O는 세후배당으로 당일 종가 매수→주식수 증가→배당 눈덩이. 재투자 X는 주식수 고정→DPS 성장만큼만.

```bash
SHORTS_STOCK=KTNG python3 build_divsnowball.py   # KTNG/SEC/SKH/SCHD/MO/O (CFG 한 줄로 추가)
# → exports/ktng_divsnowball.png · ktng_divsnowball_reel(_top100px).mp4
```

- 2패널: **① 연 배당금**(회계연도 그룹 막대 O/X) + **② 누적 배당금**(area, 재투자 O 초록 `#4ade80` / X 금색 `#fbbf24`).
- 애니: 막대가 해마다 자라고 누적 area가 벌어짐(2초 후킹+16초 리빌). 동적 범례 "재투자 O/X · 연배당금 ○○만원 · 누적배당금 ○○만원"(라이브).
- **회계연도(`fy_start`)**: KT&G 등 기말배당 익년(2월) 지급 → 4월 시작으로 묶어 달력연도 왜곡 제거(미국 분기배당은 1=달력).
- 엔진: 재투자 O는 `fire_engine`(reinvest_dividends), 배당 발생액은 직접 시뮬(주식수×DPS×(1-세)).
- 인사이트(KT&G 2005~ 1억): 재투자 O 연 3,462만·누적 3.32억 vs X 연 1,656만·누적 2.18억. 배당 눈덩이로 '배당 받는 힘'이 2배.

## 번외 — 배당성장 vs 고배당 (build_growth_vs_yield.py) ❄️

같은 금액을 **배당성장주(SCHD)와 고배당주(QYLD)** 에 넣고 보유(재투자 X). 2패널 애니 + 2페이지 요약표.

```bash
PAIR=SCHD_QYLD python3 build_growth_vs_yield.py   # SCHD_QYLD / SCHD_JEPI (PAIRS 한 줄 추가)
# → exports/schd_qyld_gvy.png · schd_qyld_gvy_reel(_top100px).mp4
```

- **① 연 배당금**(막대): 고배당(금색)은 높게 시작해 정체·감소, 배당성장(초록)은 낮게 시작해 상승 → 추월(CROSS 연도).
- **② 원금(주가) 평가액**(라인 + 투자원금 점선): 고배당 NAV 침식(원금선 아래), 배당성장 성장.
- 2페이지 요약표: 연배당·누적배당·원금·총자산 4행 × 2열(▲우위 표기). **정직**하게 고배당이 '누적배당'만 우위.
- 인사이트(SCHD vs QYLD, 2014~ $10K): 연배당 추월 2025, 원금 $27.6K vs $6.9K, 총자산 $33.5K vs $16.3K. 고배당은 받은 배당 총액↑지만 배당성장이 배당·원금·총자산 우위.

## 데이터 구조

`assets/data/<pref>_accum.json` = 임계값 3종(20/30/50) 리스트. 각 항목의 `payload.lines` 4선(적립원금 점선·매수원금 점선·적립평가·매수평가), `steady`/`smart`{final,xirr,cagr}, `invested`/`monthly`. 엔진: `blog/PG/deck/tools/ko_smart_vs_steady.py`(수정 금지).

## 스크립트

- `gen_accum.py` — 백테스트 → 데이터 JSON.
- `build_instagram_accum.py` — 릴 렌더(자체 완결, PIL 직접 렌더 + 점선 헬퍼 + 끝점 링 + 동적 라벨).

## TODO

- 2페이지 결과표(전략·최종평가액·CAGR·XIRR) — 미구현(현재 릴 하단에 "1/2" 표기).

`exports/`(mp4/png)·`__pycache__/`는 `.gitignore` 제외.
