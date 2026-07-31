#!/usr/bin/env python3
"""build_canvas.py — out/canvas.html 을 playwright로 녹화 → out/canvas.mp4 (+미리보기).

전제: gen_canvas.py 를 먼저 실행(본 스크립트가 자동). 총 길이는 gen_canvas.total_seconds 로 계산.
사용: SHORTS_SCENE=qyld python3 build_canvas.py
"""
import os, glob, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SCENE = os.environ.get("SHORTS_SCENE", "qyld")

# gen_canvas 로드(씬 길이 계산 + HTML 생성)
spec = importlib.util.spec_from_file_location("gen_canvas", os.path.join(HERE, "gen_canvas.py"))
GC = importlib.util.module_from_spec(spec); spec.loader.exec_module(GC)

subprocess.run(["python3", os.path.join(HERE, "gen_canvas.py")], check=True, env={**os.environ, "SHORTS_SCENE": SCENE})
ww, wh, blocks, seq = {"qyld": GC.scene_qyld}[SCENE]()
DUR = GC.total_seconds(seq) + 1.2   # 여유

WORK = os.path.join(HERE, "out")
html = os.path.join(WORK, "canvas.html")
vdir = os.path.join(WORK, "_vid")
for f in glob.glob(os.path.join(vdir, "*.webm")):
    os.remove(f)
os.makedirs(vdir, exist_ok=True)

from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={"width": 1080, "height": 1920}, record_video_dir=vdir, record_video_size={"width": 1080, "height": 1920})
    pg = ctx.new_page()
    pg.goto("file://" + html)
    pg.wait_for_function("()=>document.fonts.check('900 40px Pretendard')", timeout=8000)
    pg.wait_for_timeout(int(DUR * 1000))
    ctx.close(); b.close()

webm = glob.glob(os.path.join(vdir, "*.webm"))[0]
out = os.path.join(WORK, "canvas_%s.mp4" % SCENE)
prev = os.path.join(WORK, "canvas_%s_preview.mp4" % SCENE)
subprocess.run(["ffmpeg", "-y", "-i", webm, "-c:v", "libx264", "-crf", "16", "-preset", "slow",
                "-pix_fmt", "yuv420p", "-vf", "fps=30", "-movflags", "+faststart", out], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["ffmpeg", "-y", "-i", out, "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", prev], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("DONE -> %s (%.1fs)  · preview %s" % (out, DUR, prev))
