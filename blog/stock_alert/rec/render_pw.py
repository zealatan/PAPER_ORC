#!/usr/bin/env python3
"""playwright headless firefox로 더빙 덱(?rec 풀블리드)을 녹화 → 무음 webm.
   블랙 마커(씬0 시작 직전 검은화면)를 넣어 ffmpeg blackdetect로 정확 트림 가능.
   출력: recordings/longform_silent.webm (+ 마커정보 stdout)."""
import os, glob, json
from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUTDIR = os.path.join(ROOT, 'recordings', 'pw_raw')
os.makedirs(OUTDIR, exist_ok=True)
URL = "http://127.0.0.1:8091/stock_alert/deck/stock_alert_dubbed.html?rec"
import json as _json, re as _re
_d = _json.load(open(os.path.join(ROOT,'deck','stock_alert_deck_dubbed.json'), encoding='utf-8'))['scenes']
_PACE = float(_re.search(r'var PACE\s*=\s*([\d.]+)', open(os.path.join(ROOT,'deck','stock_alert_final.html'),encoding='utf-8').read()).group(1))
_tot = sum(s.get('subHold', s.get('dur',0)*(1 if s.get('tpl')=='videohook' else _PACE)) for s in _d)
DUR_MS = int(_tot + 1500)   # 덱 총 재생시간 + 꼬리 (자동 계산)

with sync_playwright() as p:
    b = p.firefox.launch(headless=True, firefox_user_prefs={
        "media.autoplay.default": 0, "media.autoplay.blocking_policy": 0})
    ctx = b.new_context(viewport={"width": 1920, "height": 1080},
        record_video_dir=OUTDIR, record_video_size={"width": 1920, "height": 1080})
    pg = ctx.new_page()
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(2000)   # 폰트/초기 로드
    # 블랙 마커 오버레이 삽입(전체 덮기)
    pg.evaluate("""()=>{
      const d=document.createElement('div'); d.id='__blk';
      d.style.cssText='position:fixed;inset:0;background:#000;z-index:2147483647';
      document.body.appendChild(d);
    }""")
    pg.wait_for_timeout(900)    # 블랙 유지(감지용, ~0.9s)
    # 씬0 재시작(블랙 뒤에서) 후 블랙 제거 → 이 순간이 t=0
    pg.evaluate("()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'Home'}))")
    pg.wait_for_timeout(150)
    pg.evaluate("()=>{const b=document.getElementById('__blk'); if(b)b.remove();}")
    pg.wait_for_timeout(DUR_MS)
    ctx.close()   # webm finalize
    b.close()

vids = sorted(glob.glob(OUTDIR + "/*.webm"), key=os.path.getmtime)
print("WEBM", vids[-1] if vids else "NONE")
