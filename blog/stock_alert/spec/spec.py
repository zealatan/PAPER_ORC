"""video_spec — 배투실 배당 백테스트 영상 파이프라인의 단일 진실원(프로토콜).

종목 1편 = 하나의 spec 딕셔너리. 모든 단계가 이걸 읽고/되채운다.
필드 규칙:
  [IN]      사람/큐레이션 입력      — ticker, company, theme, window, data.business, story.hook,
                                     deck_layout, assets, backtest.fire.grid 파라미터
  [CALC]    엔진 산출(덮어씀)       — data.monthly_price/dividends, backtest.*, scenes[].subTimes/subHold
  [DERIVED] 다른 필드에서 조립      — scenes[].data(어댑터), scenes[].subLines(story→자막)

설계 근거: multi-agent 조사(wf_0c9ec72e-2f1). 계약을 여기서 못박아야 하위 모듈이 필드명에 합의한다.
"""
from __future__ import annotations
import json, os, copy
from dataclasses import dataclass, field
from typing import Any

SCHEMA_VERSION = "1.0"

# ── 통화별 CPI 시리즈(fixed_real 물가반영용). fire_engine는 외부 cpi:pd.Series 주입 필수 ──
CPI_BY_CURRENCY = {"USD": "CPIAUCSL", "KRW": "KORCPIALLMINMEI"}

# 각 단계가 되채우는 섹션(merge_calc 대상)
CALC_SECTIONS = ("data", "backtest", "story", "scenes", "assets", "outputs")


def new_spec(ticker: str, company: str, *, theme: str = "dividend_compounding",
             currency: str = "USD", start: str = "2000-01-01", end: str = "2026-07-31") -> dict:
    """빈 spec 골격 생성([IN] 최소치만 채운 상태)."""
    return {
        "schema_version": SCHEMA_VERSION,
        "ticker": ticker,
        "company": company,
        "theme": theme,
        "currency": currency,
        "window": {"start": start, "end": end},
        "data": {"monthly_price": [], "dividends": [], "annual_dividends": [], "business": {}},
        "backtest": {
            "fire": {
                "grid": {"inits": [200000, 400000, 600000], "monthlies": [1000, 2000, 3000],
                         "strategies": ["fixed_nominal", "fixed_real"], "tax_rate_pct": 15},
                "scenarios": [],
            },
            "strategy_compare": {},
        },
        "story": {"hook": {}, "sections": [],
                  "voice": {"voice_id": "", "model": "eleven_v3", "lang": "ko",
                            "atempo": 1.12, "ms_per_char": 225}},
        "scenes": [],
        "deck_layout": {"ov": {}, "cp": {}, "theme": "paper", "paper": "photo"},
        "assets": {"bg_clips": {}, "brand_media": {}, "thumbnail": {}, "publish": {}},
        "outputs": {},
    }


# ── 계약 검증 ─────────────────────────────────────────────────────────────
_REQUIRED_IN = ["ticker", "company", "currency", "window"]  # 사람이 반드시 채워야 하는 최소 [IN]


def validate(spec: dict, *, stage: str | None = None) -> list[str]:
    """계약 위반을 문자열 리스트로 반환(빈 리스트 = OK).
    stage 지정 시 그 단계 실행에 필요한 선행 필드까지 점검."""
    errs: list[str] = []
    if spec.get("schema_version") != SCHEMA_VERSION:
        errs.append(f"schema_version != {SCHEMA_VERSION} (got {spec.get('schema_version')})")
    for k in _REQUIRED_IN:
        if not spec.get(k):
            errs.append(f"[IN] 필수 필드 누락: {k}")
    w = spec.get("window") or {}
    if not (w.get("start") and w.get("end")):
        errs.append("[IN] window.start/end 필요")
    if spec.get("currency") not in CPI_BY_CURRENCY:
        errs.append(f"currency '{spec.get('currency')}' — CPI 매핑 없음 {tuple(CPI_BY_CURRENCY)}")

    # 단계별 선행 조건
    need = {
        "backtest": [("data.monthly_price", spec.get("data", {}).get("monthly_price"))],
        "deck":     [("backtest.fire.scenarios", spec.get("backtest", {}).get("fire", {}).get("scenarios")),
                     ("scenes", spec.get("scenes"))],
        "dub":      [("scenes", spec.get("scenes")),
                     ("story.voice.voice_id", spec.get("story", {}).get("voice", {}).get("voice_id"))],
        "render":   [("outputs.deck_json", spec.get("outputs", {}).get("deck_json"))],
    }
    for path, val in need.get(stage or "", []):
        if not val:
            errs.append(f"[{stage}] 선행 필드 비어있음: {path}")
    return errs


def merge_calc(spec: dict, section: str, payload: Any) -> dict:
    """엔진 산출을 spec의 한 섹션에 되채운다(in-place, spec 반환).
    section 예: 'data', 'backtest', 'scenes', 'outputs'. dict는 얕은병합, 그 외는 대입."""
    if section not in CALC_SECTIONS:
        raise ValueError(f"merge_calc: 알 수 없는 섹션 '{section}' (허용 {CALC_SECTIONS})")
    cur = spec.get(section)
    if isinstance(cur, dict) and isinstance(payload, dict):
        cur.update(payload)
    else:
        spec[section] = payload
    return spec


# ── IO ────────────────────────────────────────────────────────────────────
def load_spec(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_spec(spec: dict, path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)


def clone(spec: dict) -> dict:
    return copy.deepcopy(spec)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:  # spec 검증 CLI: python spec.py <spec.json> [stage]
        s = load_spec(sys.argv[1])
        stage = sys.argv[2] if len(sys.argv) > 2 else None
        problems = validate(s, stage=stage)
        if problems:
            print(f"✗ {len(problems)} 계약 위반:")
            for p in problems:
                print("  -", p)
            sys.exit(1)
        print(f"✓ {sys.argv[1]} 계약 OK" + (f" (stage={stage})" if stage else ""))
    else:
        print(json.dumps(new_spec("KO", "Coca-Cola"), ensure_ascii=False, indent=1))
