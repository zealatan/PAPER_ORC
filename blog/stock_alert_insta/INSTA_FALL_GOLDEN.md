# stock_alert 인스타 이식 — 낙폭 테이블 (PIL 재구축) ❄️FROZEN

원본 [`stock_alert/FALL_TABLES_GOLDEN`](../stock_alert/FALL_TABLES_GOLDEN.md)(HTML+브라우저 녹화)을
**PIL로 재구축**한 인스타 버전. 디자인·데이터·에셋은 원본과 공유하고, 렌더러만 자체 구현.

> 이 폴더는 **원본 stock_alert의 대안 렌더러 1개**(`build_insta_fall_table.py`)만 소유한다.
> 로고·데이터·마스코트·썸네일·종이질감은 **원본에서 읽기전용 참조**(중복 안 함) → 주간 스캔 갱신 그대로 반영.

## 산출물 (2종)
- **릴(영상)**: 1080×1920, 인트로(옵션)+4시장 표, 행 스태거·▼낙폭% 카운트업·페이지 크로스페이드. ~35–37초.
- **캐러셀(정적)**: 4:5(1080×1350)·1:1(1080×1080) 각 4장(미국·한국·유럽·ETF).

## 재현
```bash
cd blog/stock_alert_insta
# 데이터는 원본이 갱신: (원본에서) fall_scan.py --market … --week N --asof …
python3 build_insta_fall_table.py                 # 릴(영상) → shorts/insta_fall_w31.mp4  (INTRO=1 로 썸네일 인트로)
python3 -c "import build_insta_fall_table as b; b.main_cards()"   # 캐러셀 → carousel/{4x5,1x1}/*.png
```

## 디자인 (원본 골든 상속)
- 검정 배경 + **흰 종이질감 카드**(`golden_shorts_fire/assets/paper_b64.txt`), 둥근 26·soft shadow.
- 타이틀 `<국기> <시장> 주식 하락 TOPn` — **하락=마젠타 `#d12e77`**, 나머지 흰색. 국기=NotoColorEmoji. 아래 `2026 · week N`(골드 `#d9b44a`).
- 표: [순위][로고][종목명][전고점比]. **순위·▼낙폭%=라즈베리 `#c2255c`**, 종목명 `#141414`, th `#8a857c`. ETF는 로고 열 없음.
- 로고: `stock_alert/deck/logos/<티커앞>.png`, **contain(비율 유지)** height≤46(릴)/pitch비례(카드). 한글명 `KR_NAME`.
- 마스코트 `mascot_knit.png` 우상단. 페이지표시(릴 `N/총`).
- 폰트: 원본 Pretendard → **Noto Sans CJK 대체**(PIL은 woff2 불가). 나머지 좌표·색은 원본 CSS %를 픽셀로 이식.

## 애니(릴)
페이지 페이드→카드 슬라이드업(30px)·타이틀 슬라이드다운(22px) / 행 스태거(delay i×0.065s, ease-out) / **▼낙폭% 0→최종 카운트업**(0.68s) / 페이지 크로스페이드(0.5s). 타이밍: 인트로 2.6s·시장당 8.7s.

## 파일
- `build_insta_fall_table.py` — 릴(`render_page`)·캐러셀(`render_card`, HH=1350/1080 적응형)·조립(`main`/`main_cards`).
- 출력 `carousel/`·`shorts/`·`save_cards.html`은 gitignore(재생성물).

메모리: [[stock-alert-project]] · 원본 디자인: [[pg-golden-shorts-fire]]
