# 상승(52주 신고가) 쇼츠 — 주간 재현 런북

낙폭(하락) 파이프라인의 상승판. 매주 시장별로 "이번 주 52주 신고가 경신 + 5년 수익률"
쇼츠를 찍어낸다. 아래 순서만 따르면 재현된다. (예시는 미국 기준, `<시장>`=미국/한국/유럽)

## 0. 개념 (바뀌지 않는 규칙)
- **트리거**: 이번 주(최근 5거래일) **52주 신고가** 경신 종목만. (`scan_market_breakout`, `high_lookback_days=252`, `fresh_days=5`)
- **선정**: 시총(표시통화 환산) 내림차순 **TOP5** (후보 부족하면 있는 만큼 — 한국이 3개면 TOP3).
- **payload**: 5년 수익률(양수 초록▲ / 음수 회색▼). 사상최고가 아니어도 52주 최고면 OK(전체 히스토리 그대로 표시).
- **표시통화**: 미국=$ · 한국=₩(조) · 유럽=€(전 통화 EUR 환산).
- **템플릿**: 그래프 top696 · 하단 "배투실" 텍스트워터마크 · 상단 훅 · 끝 아웃트로 3.5s. 카드당 5.5초 균일.

## 1. 시총/AUM 스냅샷 (주 1회, 유니버스 갱신 시)
```
cd ../../global_cup_suite/data
python3 build_asset_size.py        # yfinance marketCap/totalAssets
python3 enrich_kr_etf_aum.py       # 한국 ETF AUM은 네이버(Yahoo 미제공)
```
→ `global_cup_suite/data/asset_size.csv` (시총·source_currency). rise_scan이 이걸 읽음.

## 2. 스캔 → 데이터 (시장별)
```
python3 rise_scan.py --market 미국 --week 31
python3 rise_scan.py --market 한국 --week 31
python3 rise_scan.py --market 유럽 --week 31
```
→ `data/rise_week31.json` 에 시장별 병합. (통화환산·차트보강·시총순 TOP 자동)
- 새 종목이 나오면 로고 필요 → **§5** 참고.

## 3. 덱 빌드 → 렌더 (시장별, 순차)
```
python3 deck/build_rise_deck.py 미국      # 단일시장 덱(risecard subHold=5500 균일)
rm -f recordings/rise_raw/*.webm
python3 rec/render_rise.py                 # → recordings/rise_raw/*.webm  (~2분)
```
※ 렌더는 stock_alert_rise_v1.html + rise_raw/webm 을 덮어쓰므로 **시장마다 빌드→렌더→쇼츠**를 순차로.

## 4. 쇼츠 합성
```
rec/build_short_rise.sh <n_cards> assets/shorts/hook_미국_rise.png shorts/short_US_rise.mp4
```
- `<n_cards>` = 그 시장 카드 수(미국·유럽 5, 한국 3).
- 훅이 없으면 `rec/gen_hook_rise.py` 로 생성(시장·개수 문구 편집).
- 결과: 표준 템플릿 + 아웃트로. 카드 균일 5.5초라 **#1까지 안 잘림**.

전 시장 반복:
```
# 미국
python3 deck/build_rise_deck.py 미국 && rm -f recordings/rise_raw/*.webm && python3 rec/render_rise.py
rec/build_short_rise.sh 5 assets/shorts/hook_US_rise.png shorts/short_US_rise.mp4
# 한국
python3 deck/build_rise_deck.py 한국 && rm -f recordings/rise_raw/*.webm && python3 rec/render_rise.py
rec/build_short_rise.sh 3 assets/shorts/hook_KR_rise.png shorts/short_KR_rise.mp4
# 유럽
python3 deck/build_rise_deck.py 유럽 && rm -f recordings/rise_raw/*.webm && python3 rec/render_rise.py
rec/build_short_rise.sh 5 assets/shorts/hook_EU_rise.png shorts/short_EU_rise.mp4
```

## 5. 로고 (새 종목만)
`deck/logos/<TICKER앞부분>.png` (미국=티커, 한국=6자리코드, 유럽=티커앞, ETF=운용사).
없으면 **멀티에이전트**로 확보 — Wikimedia 공식 SVG → 투명 PNG(cairosvg). Clearbit은 이 환경에서 DNS 막힘.
예) `deck/logos/AAPL.png` `010950.png` `HSBA.png`. 누적되니 한 번 받으면 재사용.

## 6. 요약글
`shorts/shorts_captions_rise_wNN.md` — 제목·설명·순위·해시태그. (shorts/는 gitignore → `git add -f`)

## 고정 자산 (한 번 만들고 재사용, 바꿀 때만 재생성)
- `rec/gen_hook_rise.py` → `assets/shorts/hook_{US,KR,EU}_rise.png` (시장·TOPn 문구)
- `rec/gen_outro.py` → `assets/shorts/outro_card.png` (이모지 구독 엔드카드)
- `assets/shorts/batusil_text.png` (하단 작은 배투실 글자)

## 주의(gotcha)
- **통화**: tickers_eu.csv는 EU 전 종목을 EUR로 잘못 기재. 실제 통화는 asset_size.csv `source_currency`. rise_scan이 이걸로 환산. GBp(런던): 시총=파운드(×GBP), 가격=펜스(÷100×GBP).
- **타이밍**: 덱은 자막길이로 씬전환 → 종목명 편차로 불균등. risecard `subHold=5500` 으로 균일화함. 바꾸면 `build_short_rise.sh` 의 `CARD` 도 같이.
- **워터마크**: 우상단 배투실은 render_rise가 `.bearbadge{display:none}` 로 숨김. 하단은 텍스트워터마크.
- **KEY**: risecard 구조 바꾸면 stock_alert_final.html 렌더러 재확인. 쇼츠는 무음(자막 숨김).
- 쇼츠 mp4는 gitignore(재생성 가능). 덱/스크립트/데이터/로고만 커밋.
