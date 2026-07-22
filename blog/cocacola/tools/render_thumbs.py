# -*- coding: utf-8 -*-
"""cocacola_v4.html 덱을 0311 상태로 로드 → 35씬 각각 .frame 스크린샷 → thumbs/."""
import json, os, pathlib
from playwright.sync_api import sync_playwright

DECK = pathlib.Path("cocacola_v4.html").resolve()
STATE = json.load(open("/mnt/c/Users/LYAN/Downloads/cocacola_v3_저장_20260719_0311.json", encoding="utf-8"))
KEY = "tplCatalog_cocacola_v4g"
OUT = pathlib.Path("thumbs"); OUT.mkdir(exist_ok=True)
N = len(STATE["scenes"])

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox","--disable-gpu"])
    pg = b.new_page(viewport={"width":1280,"height":760}, device_scale_factor=2)
    pg.goto(DECK.as_uri())
    # 상태 심고 리로드
    pg.evaluate("([k,v])=>localStorage.setItem(k,v)", [KEY, json.dumps(STATE, ensure_ascii=False)])
    pg.reload()
    pg.wait_for_timeout(1500)
    dots = pg.query_selector_all("#dots .dot")
    print("dots:", len(dots))
    for i in range(N):
        dots[i].click()             # 각 dot이 show(i) 호출
        pg.wait_for_timeout(1700)   # enter 애니 + countUp 세틀
        el = pg.query_selector(".frame")
        el.screenshot(path=str(OUT/f"s{i+1:02d}.png"))
        print(f"  씬 {i+1}/{N} 캡처")
    b.close()
print("→ thumbs/ 완료")
