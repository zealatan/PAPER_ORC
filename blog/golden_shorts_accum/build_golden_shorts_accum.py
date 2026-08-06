#!/usr/bin/env python3
"""
golden_shorts_accum — 렌더/합치기 파이프라인 (은퇴 시나리오 쇼츠 · GOLDEN REFERENCE)

실행:  python3 build_golden_shorts_accum.py
결과:  golden_shorts_accum.mp4  (1080x1920, 30fps, 총 ~33.2초)

전제:  golden_shorts_accum.py 를 먼저 실행해 3개 그래프 HTML 을 생성한다(본 스크립트가 자동 실행).
의존:  playwright(chromium), ffmpeg. 폰트/데이터/썸네일은 저장소 내에서 로드.

구성(슬라이드 순서):
  0) 썸네일 assets/thumb_mag.png  ........ 1.25초 정지
  1) golden_shorts_accum_1.html ($200,000) 10.7초 (애니 10.08초 + 정지)
  2) golden_shorts_accum_2.html ($400,000) 10.7초
  3) golden_shorts_accum_3.html ($600,000) 10.7초

타이밍 상수(=GOLDEN 값, 함부로 바꾸지 말 것):
  DUR(애니)          = 10.08초  ← golden_shorts_accum.py NEWRA 안에 있음(여기선 대기시간만 맞춤)
  THUMB_SEC          = 1.25초
  CLIP_SEC(그래프)   = 10.7초
  REC_WAIT_MS        = 11000ms (애니 끝나고 정지 프레임까지 녹화)
  START_TRIM         = off+0.15초 (playwright 페이지로드 오프셋 보정)
"""
import os, time, json, subprocess
from playwright.sync_api import sync_playwright

HERE   = os.path.dirname(os.path.abspath(__file__))
_STK   = os.environ.get("SHORTS_STOCK", "PG")   # 종목별 썸네일·출력
THUMB  = os.path.join(HERE, "assets", {"SKH": "skh_thumb.png"}.get(_STK, "thumb_mag.png"))
OUT    = os.path.join(HERE, "golden_shorts_accum.mp4" if _STK == "PG" else "golden_shorts_accum_%s.mp4" % _STK)
WORK   = os.path.join(HERE, "_build")           # 중간 산출물(클립/webm)
THUMB_SEC  = 1.25
CLIP_SEC   = 10.7
TABLE_SEC  = 5.0
REC_WAIT_MS= 11000
W, H = 1080, 1920

def sh(*a): subprocess.run(a, check=True)

# 0) 데이터·그래프·테이블 HTML 생성
sh("python3", os.path.join(HERE, "gen_accum.py"))
sh("python3", os.path.join(HERE, "golden_shorts_accum.py"))
sh("python3", os.path.join(HERE, "gen_accum_table.py"))

import glob
NG = len(glob.glob(os.path.join(HERE, "golden_shorts_accum_[0-9].html")))   # 그래프 장수(원금 종수, 현재 5)

os.makedirs(WORK, exist_ok=True)
for f in os.listdir(WORK):
    os.remove(os.path.join(WORK, f))

# 1) 각 그래프를 새 컨텍스트로 녹화(폰트 로드 대기 → reelAnim 수동 트리거 → 정지까지 대기)
offs = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for n in range(1, NG + 1):
        ctx = b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=1,
                            record_video_dir=WORK, record_video_size={'width': W, 'height': H})
        pg = ctx.new_page(); t0 = time.monotonic()
        pg.goto('file://%s/golden_shorts_accum_%d.html' % (HERE, n))
        pg.wait_for_function("()=>document.fonts.check('900 100px Pretendard')", timeout=8000)
        off = time.monotonic() - t0
        pg.evaluate("()=>reelAnim(document.querySelector('.graphbox'))")
        pg.wait_for_timeout(REC_WAIT_MS)
        offs[n] = (pg.video.path(), off)
        ctx.close()
    # 1.5) 결과 테이블 페이지 → PNG(정지용) · 3배 해상도로 캡처(다운스케일 시 선명)
    tpg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=3)
    tpg.goto('file://%s/golden_shorts_accum_table.html' % HERE)
    tpg.wait_for_function("()=>document.fonts.check('900 40px Pretendard')", timeout=8000)
    tpg.wait_for_timeout(500)
    tpg.screenshot(path=os.path.join(WORK, "table.png"))
    b.close()

# 2) 썸네일 정지 클립
sh("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-t", str(THUMB_SEC),
   "-i", THUMB, "-vf", "scale=%d:%d,fps=30,format=yuv420p" % (W, H),
   "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", os.path.join(WORK, "c0.mp4"))

# 3) 그래프 클립 트림(시작 오프셋 보정 후 CLIP_SEC 만큼)
for i, n in enumerate(range(1, NG + 1), 1):
    webm, off = offs[n]
    sh("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "%.2f" % (off + 0.15),
       "-i", webm, "-t", str(CLIP_SEC), "-vf", "scale=%d:%d,fps=30,format=yuv420p" % (W, H),
       "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", os.path.join(WORK, "c%d.mp4" % i))

# 3.5) 결과 테이블 5초 정지 클립 (마지막 페이지)
# 3x 캡처 table.png(3240×5760)에 아주 미세한 줌(모션) → 유튜브가 정지화면 취급 안 하고 비트레이트 할당 → 글씨 선명
# 단일 이미지 입력 + zoompan d=총프레임 + -frames:v (loop 없이 정확히 TABLE_SEC초)
_tf = int(TABLE_SEC * 30)
sh("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
   "-i", os.path.join(WORK, "table.png"),
   "-vf", "zoompan=z='min(zoom+0.00022,1.033)':d=%d:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=%dx%d:fps=30,format=yuv420p" % (_tf, W, H),
   "-frames:v", str(_tf),
   "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", os.path.join(WORK, "c%d.mp4" % (NG + 1)))

# 4) concat: c0=썸네일 + c1..cNG=그래프 + c(NG+1)=테이블
listf = os.path.join(WORK, "list.txt")
with open(listf, "w") as f:
    for i in range(NG + 2):
        f.write("file '%s'\n" % os.path.join(WORK, "c%d.mp4" % i))
sh("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
   "-i", listf, "-c:v", "libx264", "-b:v", "18M", "-maxrate", "22M", "-bufsize", "36M",
   "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT)

print("DONE ->", OUT)
