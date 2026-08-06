"""④⑤⑥ 렌더(playwright 프레임캡처→ffmpeg) · 통합(concat) · 쇼츠 리프레임."""
import os
import subprocess
import shutil
import pathlib


def render_scene(html_path, dur_s, out_mp4, fps=30, workdir=None,
                 autohold=None, max_dur=16.0):
    """scene HTML(window.__renderAt(t_ms), window.__ready) → mp4. 결정적 프레임 캡처.
    autohold(초) 지정 시: 애니가 '멈춘(연속 프레임 동일)' 시점을 감지해 +autohold초 뒤 종료.
      → duration 수동 지정 불필요. (dur_s는 무시)
    autohold=None: dur_s초 고정 렌더.
    """
    from playwright.sync_api import sync_playwright
    import hashlib
    workdir = workdir or (out_mp4 + '_frames')
    if os.path.exists(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir)
    url = 'file://' + str(pathlib.Path(html_path).resolve())
    errs = []
    count = 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1080, 'height': 1080})
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(url)
        pg.wait_for_function('window.__ready===true', timeout=15000)

        def shot(i):
            path = os.path.join(workdir, f'f{i:04d}.png')
            pg.evaluate('t=>window.__renderAt(t)', i * 1000 / fps)
            pg.screenshot(path=path)
            return path

        if autohold is None:
            n = int(fps * dur_s) + 1
            for i in range(n):
                shot(i)
            count = n
        else:
            prev = None
            moved = False
            settle = None
            maxn = int(fps * max_dur)
            i = 0
            while i <= maxn:
                path = shot(i)
                h = hashlib.md5(open(path, 'rb').read()).hexdigest()
                if prev is not None and h != prev:
                    moved = True
                    settle = None                       # 변화 재발생 → 정착 리셋(다단계 애니 대응)
                if moved and settle is None and prev is not None and h == prev:
                    settle = i - 1                      # 직전 프레임에서 정착
                if settle is not None and (i - settle) >= int(fps * autohold):
                    break
                prev = h
                i += 1
            count = i + 1
        b.close()
    if errs:
        print('  [warn] pageerror:', errs[:2])
    if autohold is not None:
        print(f'  [autohold] {count} 프레임 ({count/fps:.1f}s, 정착후 {autohold}s hold)')
    subprocess.run(['ffmpeg', '-y', '-framerate', str(fps),
                    '-i', os.path.join(workdir, 'f%04d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', out_mp4],
                   capture_output=True)
    shutil.rmtree(workdir)
    return out_mp4


def concat(mp4_list, out_mp4):
    lst = out_mp4 + '.txt'
    with open(lst, 'w') as f:
        for m in mp4_list:
            f.write(f"file '{os.path.abspath(m)}'\n")
    subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                    '-i', lst, '-c', 'copy', out_mp4], capture_output=True)
    os.remove(lst)
    return out_mp4


def reframe_shorts(in_mp4, out_mp4, inner_width=1004, bg='white', valign='center'):
    """1:1 → 9:16(1080x1920) 여백 패딩. 양옆 잘림 방지."""
    yoff = '(oh-ih)/2' if valign == 'center' else ('80' if valign == 'top' else '(oh-ih)-80')
    vf = f"scale={inner_width}:{inner_width},pad=1080:1920:(ow-iw)/2:{yoff}:color={bg}"
    subprocess.run(['ffmpeg', '-y', '-i', in_mp4, '-vf', vf,
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', out_mp4], capture_output=True)
    return out_mp4
