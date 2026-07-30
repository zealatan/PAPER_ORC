#!/usr/bin/env python3
"""
golden_shorts_fire — 렌더/합치기 파이프라인 (누적 고스트 파이어 쇼츠 · GOLDEN REFERENCE)

실행:  python3 build_golden_shorts_fire.py   (종목: SHORTS_STOCK=PG|QQQ|KTNG)
결과:  golden_shorts_fire[_<STOCK>].mp4  (1080x1920, 30fps)

구성(3페이지):
  0) 썸네일 assets/<thumb>.png ............ 1.25초 정지
  1) golden_shorts_fire_1.html ............ 누적 고스트 그래프(accumAnim, 약 40초)
  2) golden_shorts_fire_table.html ........ 원금×월인출 결과 테이블(5초 정지, 미세 줌)

전제:  golden_shorts_fire.py / gen_fire_table.py 를 먼저 실행(본 스크립트가 자동).
의존:  playwright(chromium), ffmpeg.
"""
import os, time, subprocess
from playwright.sync_api import sync_playwright
import golden_shorts_fire as G   # ACCUM_TOTAL_MS

HERE  = os.path.dirname(os.path.abspath(__file__))
_STK  = os.environ.get("SHORTS_STOCK", "PG")
THUMB = os.path.join(HERE, "assets", {"QQQ": "qqq_thumb.png"}.get(_STK, "thumb_mag.png"))
OUT   = os.path.join(HERE, "golden_shorts_fire.mp4" if _STK == "PG" else "golden_shorts_fire_%s.mp4" % _STK)
WORK  = os.path.join(HERE, "_build")
THUMB_SEC = 1.25
TABLE_SEC = 5.0
GRAPH_SEC = G.ACCUM_TOTAL_MS / 1000.0     # 누적 애니 총 길이(초)
REC_WAIT_MS = int(G.ACCUM_TOTAL_MS + 1500)
W, H = 1080, 1920

def sh(*a): subprocess.run(a, check=True)

# 0) 그래프·테이블 HTML 생성
sh("python3", os.path.join(HERE, "golden_shorts_fire.py"))
sh("python3", os.path.join(HERE, "gen_fire_table.py"))

os.makedirs(WORK, exist_ok=True)
for f in os.listdir(WORK):
    os.remove(os.path.join(WORK, f))

# 1) 누적 그래프 녹화(폰트 대기 → accumAnim 트리거 → 총길이+여유 대기)
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=1,
                        record_video_dir=WORK, record_video_size={'width': W, 'height': H})
    pg = ctx.new_page(); t0 = time.monotonic()
    pg.goto('file://%s/golden_shorts_fire_1.html' % HERE)
    pg.wait_for_function("()=>document.fonts.check('900 100px Pretendard')", timeout=8000)
    off = time.monotonic() - t0
    pg.evaluate("()=>accumAnim(document.querySelector('.graphbox'))")
    pg.wait_for_timeout(REC_WAIT_MS)
    graph_webm = pg.video.path()
    ctx.close()
    # 1.5) 결과 테이블 → PNG(3배 해상도 · 다운스케일 시 선명)
    tpg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=3)
    tpg.goto('file://%s/golden_shorts_fire_table.html' % HERE)
    tpg.wait_for_function("()=>document.fonts.check('900 40px Pretendard')", timeout=8000)
    tpg.wait_for_timeout(500)
    tpg.screenshot(path=os.path.join(WORK, "table.png"))
    b.close()

# 2) 썸네일 정지 클립
sh("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-t", str(THUMB_SEC),
   "-i", THUMB, "-vf", "scale=%d:%d,fps=30,format=yuv420p" % (W, H),
   "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", os.path.join(WORK, "c0.mp4"))

# 3) 누적 그래프 클립(시작 오프셋 보정 후 GRAPH_SEC 만큼)
sh("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "%.2f" % (off + 0.15),
   "-i", graph_webm, "-t", "%.2f" % GRAPH_SEC, "-vf", "scale=%d:%d,fps=30,format=yuv420p" % (W, H),
   "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", os.path.join(WORK, "c1.mp4"))

# 4) 결과 테이블 5초 정지 클립(아주 미세한 줌 → 유튜브 정지화면 취급 방지 → 글씨 선명)
_tf = int(TABLE_SEC * 30)
sh("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
   "-i", os.path.join(WORK, "table.png"),
   "-vf", "zoompan=z='min(zoom+0.00022,1.033)':d=%d:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=%dx%d:fps=30,format=yuv420p" % (_tf, W, H),
   "-frames:v", str(_tf),
   "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", os.path.join(WORK, "c2.mp4"))

# 5) concat: c0=썸네일 + c1=누적그래프 + c2=테이블
listf = os.path.join(WORK, "list.txt")
with open(listf, "w") as f:
    for i in range(3):
        f.write("file '%s'\n" % os.path.join(WORK, "c%d.mp4" % i))
sh("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
   "-i", listf, "-c:v", "libx264", "-b:v", "18M", "-maxrate", "22M", "-bufsize", "36M",
   "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT)

print("DONE ->", OUT)
