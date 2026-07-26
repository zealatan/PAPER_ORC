#!/usr/bin/env python3
"""stock_alert_rise_v1.html(?rec)을 playwright로 녹화 → 무음 webm. 블랙 마커로 트림."""
import os, glob, json, re
from playwright.sync_api import sync_playwright
ROOT = os.path.join(os.path.dirname(__file__), '..')
OUTDIR = os.path.join(ROOT, 'recordings', 'rise_raw'); os.makedirs(OUTDIR, exist_ok=True)
HTML = os.path.abspath(os.path.join(ROOT, 'deck', 'stock_alert_rise_v1.html'))
URL = 'file://' + HTML + '?rec'
_d = json.load(open(os.path.join(ROOT,'deck','stock_alert_rise_deck.json'),encoding='utf-8'))['scenes']
_PACE = float(re.search(r'var PACE\s*=\s*([\d.]+)', open(os.path.join(ROOT,'deck','stock_alert_final.html'),encoding='utf-8').read()).group(1))
_tot = sum(s.get('dur',0)*_PACE for s in _d)
DUR_MS = int(_tot + 2500)
print('scenes', len(_d), 'playback ms', int(_tot), flush=True)
with sync_playwright() as p:
    b = p.firefox.launch(headless=True, firefox_user_prefs={"media.autoplay.default":0,"media.autoplay.blocking_policy":0})
    ctx = b.new_context(viewport={"width":1920,"height":1080}, record_video_dir=OUTDIR, record_video_size={"width":1920,"height":1080})
    pg = ctx.new_page(); pg.goto(URL, wait_until="load"); pg.wait_for_timeout(2000)
    pg.add_style_tag(content=".bearbadge{display:none!important}")   # 우상단 배투실 워터마크 숨김(쇼츠는 하단 오버레이만)
    pg.evaluate("""()=>{const d=document.createElement('div');d.id='__blk';d.style.cssText='position:fixed;inset:0;background:#000;z-index:2147483647';document.body.appendChild(d);}""")
    pg.wait_for_timeout(900)
    pg.evaluate("()=>document.dispatchEvent(new KeyboardEvent('keydown',{key:'Home'}))")
    pg.wait_for_timeout(150)
    pg.evaluate("()=>{const b=document.getElementById('__blk');if(b)b.remove();}")
    pg.wait_for_timeout(DUR_MS)
    ctx.close(); b.close()
vids = sorted(glob.glob(OUTDIR+"/*.webm"), key=os.path.getmtime)
print("WEBM", vids[-1] if vids else "NONE")
