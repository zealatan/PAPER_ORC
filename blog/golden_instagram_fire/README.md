# golden_instagram_fire ❄️ FROZEN (golden reference)

FIRE 백테스트 **인스타 릴(1080×1920)** 파이프라인의 동결 골든 소스.
"○○로 은퇴했다면 얼마나 버텼을까?" — 원금 2종 × 월 인출 2종을 순차 애니메이션으로 그린다.

> 이 폴더는 골든 레퍼런스다. 새 실험은 복제 후 진행하고, 여기 소스는 합의 없이 바꾸지 말 것.

## 완성 릴 스펙 (현재 동결본)

- 캔버스 1080×1920, 30fps. 상단 2초 **후킹**(큰 원금 최종 결과 미리보기) → 작은 원금 → 큰 원금 순차 리빌 → 결과표(2/2) 페이드.
- 표시 원금 2종: USD `$40만/$80만`, KRW `4억/8억`. 월 인출 2종: `$2,000/$4,000` 또는 `200만/400만원`.
- 헤더: **로고(있으면) + "○○로 은퇴" 흰색 타이틀**을 한 덩어리로 가로 중앙, 아래 부제·범례 중앙.
- 그래프 박스: **회색 반투명 정사각 패널**(불투명도 20%) 안에 플롯. 4억(작은 원금)은 완성 후 정지, 8억만 애니메이션.
- **y축은 활성 리빌에 맞춰 확장**(ALT, 기본 ON), 완성 고스트의 축 초과분은 화면 밖으로.
- 가격 라벨: 리빌 중엔 끝점에 현재 평가액을 **투명 배경**으로 실시간, **완성 시에만 흰 박스**. 항상 선 위.
- "진행 YYYY.M"은 리빌 위치(`clip_end`) 기준으로 이동.
- 통화 자동 감지(payload `krw`) → 억/만원 vs $K/$M. 데이터가 최신가까지 반영.
- 스탬프(생존/파산) 기본 끔.

## 재현

```bash
# 1) 데이터(월별 백테스트 JSON). SHORTS_STOCK: QQQ SPY SCHD QYLD JEPI HYNIX ...
SHORTS_STOCK=HYNIX python3 gen_monthly_fires.py
# 2) 결과표(02-table) + 캐러셀 PNG
SHORTS_STOCK=HYNIX python3 build_instagram_qqq.py
# 3) 릴 렌더(스탬프 없이)
INSTA_STAMP=0 SHORTS_STOCK=HYNIX python3 build_original_style_video.py
# 4) 최종 프레이밍 — 좌우 60 / 상하 50 여백
ffmpeg -y -i exports/hynix_fire_original_style_reel.mp4 \
  -vf "scale=960:1820:flags=lanczos,pad=1080:1920:60:50:black" \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart \
  exports/hynix_fire_reel_up50.mp4
```

## 새 종목 추가

- `gen_monthly_fires.py`: 종목 분기(yfinance 티커·CPI·세금) + `START_YEAR`·`pref` 맵에 한 줄.
- `build_instagram_qqq.py`의 `CONFIG`: `prefix/ticker/name/x1/sub/note` 한 줄.
- 풀네임 표시는 `build_instagram_video.py`의 `NAME`, 로고는 `assets/logos/<prefix>_logo.png`.
- 원화 종목은 `gen`에서 `KRW=True`만 주면 억/만원 포맷·원금(4억/8억)·인출(200/400만원) 자동.

## 데이터 무결성 — 액면분할/병합 체크

yfinance는 분할·병합을 종가에 **자동 보정**한다(`auto_adjust=False`여도 splits는 항상 보정, 배당만 미보정). 신규 종목은 아래로 미보정 급점프가 없는지 확인 후 사용:

```python
t = yf.Ticker(TK); h = t.history(start="2000-01-01", end="…", auto_adjust=False)
r = h["Close"] / h["Close"].shift(1)           # 하루 등락비
print(t.splits)                                 # 알려진 분할이력
print(r[(r>1.4)|(r<0.6)].dropna())              # 40%+ 급변(=미보정 분할 의심) → 비어야 정상
```

검증 완료(2026-08 기준, 40%+ 미보정 급변 0건 → 보정 정상):
- **KT&G 033780** 분할 없음
- **삼성전자 005930** 2018-05 액면분할 50:1
- **SK하이닉스 000660** 2003-04 병합 21:1

## 스크립트

- `gen_monthly_fires.py` — 백테스트 원천(`global_cup.fire_engine`) → `assets/data/<pref>_fires_monthly.json`.
- `build_instagram_video.py` — 공용 상수·데이터·통화포맷·`header()`(로고+타이틀 반환). (2-cut 릴도 여기)
- `build_original_style_video.py` — **메인 릴** 렌더(애니메이션 상태머신·패널·라벨).
- `build_instagram_qqq.py` — 1/2 캐러셀 + 2/2 결과표 PNG.

## 폴더

```text
golden_instagram_fire/
├── gen_monthly_fires.py · build_*.py
├── assets/data/   # 종목별 월별 FIRE JSON (커밋)
├── assets/logos/  # <prefix>_logo.png (커밋)
├── slides/        # 생성 HTML(참고)
└── exports/       # mp4·png (gitignore)
```

`exports/`(대용량 mp4/png)와 `__pycache__/`는 `.gitignore` 제외.
시청자용 인스타 설명글: `captions.md` (종목별 캡션·해시태그).
