#!/usr/bin/env python3
"""build_fall_reel.py — _fall_reel.html 을 playwright(chromium)로 녹화 → mp4.
golden_shorts_fire/build 파이프라인과 동일 방식(폰트 대기 → startReel 트리거 → REEL_MS 대기).
miniconda python(playwright 설치본)으로 실행:
   /home/messi/miniconda3/bin/python3 rec/build_fall_reel.py --week 31
"""
import argparse
import os
import subprocess
import time

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SA = os.path.dirname(HERE)
W, H = 1080, 1920


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--week', type=int, required=True)
    ap.add_argument('--html', default=os.path.join(SA, '_fall_reel.html'))
    ap.add_argument('--out')
    a = ap.parse_args()
    out = a.out or os.path.join(SA, 'shorts', f'short_fall_tables_w{a.week}.mp4')
    work = os.path.join(SA, '_reel_build')
    os.makedirs(work, exist_ok=True)
    for f in os.listdir(work):
        os.remove(os.path.join(work, f))

    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=1,
                            record_video_dir=work, record_video_size={'width': W, 'height': H})
        pg = ctx.new_page()
        pg.goto('file://' + a.html)
        pg.wait_for_function("()=>document.fonts.check('900 100px Pretendard')", timeout=8000)
        pg.wait_for_timeout(300)
        reel_ms = pg.evaluate("()=>window.REEL_MS")
        pg.evaluate("()=>window.startReel()")
        pg.wait_for_timeout(int(reel_ms) + 500)
        webm = pg.video.path()
        ctx.close()
        b.close()

    # webm → mp4 (유튜브 재압축 대비 고비트레이트)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', webm,
                    '-t', f'{reel_ms/1000:.2f}',
                    '-c:v', 'libx264', '-crf', '16', '-preset', 'medium',
                    '-pix_fmt', 'yuv420p', '-r', '30', '-movflags', '+faststart', out], check=True)
    dur = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                   '-of', 'csv=p=0', out]).decode().strip()
    print(f'REEL_DONE {out} ({dur}s, reel_ms={reel_ms})')


if __name__ == '__main__':
    main()
