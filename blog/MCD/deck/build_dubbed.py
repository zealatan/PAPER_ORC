#!/usr/bin/env python3
"""mcd_final.html + mcd_deck_dubbed.json(subTimes/subHold 반영) → deck/mcd_dubbed.html.
   build_deck.py와 동일한 주입(KEY 교체·패치 IIFE 제거·bg data URI)에 더빙 씬을 넣는다.
   KEY='tplCatalog_mcd_dubbed' → 프리뷰/렌더용 자립형(편집 localStorage와 분리)."""
import json, base64
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
scenes = json.load(open(ROOT / "deck" / "mcd_deck_dubbed.json", encoding="utf-8"))["scenes"]
# 사용자 HUD 편집분(라벨 위치·anno 숨김) 주입 — 렌더에서도 유지
_ovf = ROOT / "spec" / "deck_ov.json"
DECK_OV = json.load(open(_ovf, encoding="utf-8")) if _ovf.exists() else {}

html = (ROOT / "deck" / "mcd_final.html").read_text(encoding="utf-8")
html = html.replace("const KEY = 'tplCatalog_cocacola_v4g';", "const KEY = 'tplCatalog_mcd_dubbed';")
blk_start = html.index("/* FIRE 세트")
p = html.index("var VER='src1';", blk_start)
blk_end = html.index("})();", p) + len("})();")
override = ("/* ══ MCD 더빙 덱 주입(subTimes/subHold 포함) ══ */\n"
            "if(!localStorage.getItem(KEY)){\n"
            "  SCENES = " + json.dumps(scenes, ensure_ascii=False) + ";\n"
            "  OV = " + json.dumps(DECK_OV, ensure_ascii=False) + "; CP = {}; THEME='paper'; PAPER='photo';\n"
            "}\n")
html = html[:blk_start] + override + html[blk_end:]

bgdir = ROOT / "deck" / "bg"
for mp4 in sorted(bgdir.glob("*.mp4")):
    ref = f"bg/{mp4.name}"
    if ref in html:
        uri = "data:video/mp4;base64," + base64.b64encode(mp4.read_bytes()).decode()
        html = html.replace(ref, uri)

out = ROOT / "deck" / "mcd_dubbed.html"
out.write_text(html, encoding="utf-8")
sub_scenes = sum(1 for s in scenes if s.get("subHold"))
print(f"→ deck/mcd_dubbed.html ({len(html)//1024}KB) · 씬 {len(scenes)} · subHold 반영 {sub_scenes}")
print(f"  씬0 subLines: {scenes[0].get('subLines')}  (비어야 정상)")
