#!/usr/bin/env python3
"""배포용 산출물 export(범용): 최종본에서 파생물 생성
  - out/<NAME>_narration.mp3   : TTS 컷 순서 통합 나레이션
  - out/<NAME>_cuts.zip        : 컷별 개별 mp3 묶음
  - out/<NAME>_web.mp4         : 30MB 이하 2-pass 압축본(메신저 업로드용)
환경변수: NAME · WEB_MB(목표 용량 MB, 기본 28)
"""
import json, os, re, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
OUT  = os.path.join(ROOT, 'out'); TMP = os.path.join(OUT, 'tmp'); os.makedirs(TMP, exist_ok=True)
TTS  = os.path.join(ROOT, 'tts')
NAME = os.environ.get('NAME') or re.sub(r'^demo_', '', os.path.basename(os.path.abspath(ROOT)))
WEB_MB = float(os.environ.get('WEB_MB', 28))

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.stderr.write(' '.join(str(c) for c in cmd)+"\n"+r.stderr[-1500:]+"\n"); raise SystemExit(1)
    return r

def dur(p):
    r = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p],
                       capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except: return 0.0

SHOTS = sorted(json.load(open(os.path.join(ROOT,'manifest.json')))['shots'], key=lambda s: s['id'])
cut_mp3s = [os.path.join(TTS, f"s{s['id']:02d}.mp3") for s in SHOTS if os.path.exists(os.path.join(TTS, f"s{s['id']:02d}.mp3"))]

# 1) 통합 나레이션 mp3
narr = os.path.join(OUT, f'{NAME}_narration.mp3')
lst = os.path.join(TMP, 'narr_concat.txt')
open(lst,'w').write(''.join(f"file '{os.path.abspath(p)}'\n" for p in cut_mp3s))
run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',lst,
     '-c:a','libmp3lame','-b:a','192k', narr])
print(f"  나레이션 mp3  {dur(narr):.1f}s  → {os.path.relpath(narr, ROOT)}")

# 2) 컷별 mp3 zip
zpath = os.path.join(OUT, f'{NAME}_cuts.zip')
with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in cut_mp3s: z.write(p, os.path.basename(p))
print(f"  컷 mp3 zip    {len(cut_mp3s)}개  → {os.path.relpath(zpath, ROOT)}")

# 3) 웹 압축 mp4 (2-pass, 목표<=WEB_MB)
final = os.path.join(OUT, f'{NAME}_final.mp4')
if os.path.exists(final):
    d = dur(final)
    v_kbps = max(600, int((WEB_MB*8*1024)/d) - 128)   # 오디오 128k 감안
    web = os.path.join(OUT, f'{NAME}_web.mp4')
    logp = os.path.join(TMP, 'ff2pass')
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',final,'-c:v','libx264',
         '-b:v',f'{v_kbps}k','-pass','1','-passlogfile',logp,'-an','-f','mp4','/dev/null'])
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',final,'-c:v','libx264',
         '-b:v',f'{v_kbps}k','-pass','2','-passlogfile',logp,'-c:a','aac','-b:a','128k', web])
    for e in ('-0.log','-0.log.mbtree'):
        try: os.remove(logp+e)
        except OSError: pass
    mb = os.path.getsize(web)/1024/1024
    print(f"  웹 압축 mp4   {mb:.1f}MB (목표 {WEB_MB}MB) → {os.path.relpath(web, ROOT)}")
else:
    print(f"  ⚠️ {NAME}_final.mp4 없음 — build_video.py 먼저 실행")
