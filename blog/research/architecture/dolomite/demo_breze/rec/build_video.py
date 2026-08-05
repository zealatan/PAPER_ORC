#!/usr/bin/env python3
"""건축쇼츠 최종 렌더(범용): images/shotNN.mp4 + tts/sNN.mp3 + 하단 자막(청크 최소노출) → out/<NAME>_final.mp4

  - 오디오 드리븐: 각 컷 길이 = 그 컷 나레이션 길이 (영상 넘치면 트림 / 모자라면 마지막 프레임 프리즈)
  - 자막: 한 문장을 짧은 청크(<=MAXCH자, 문장부호 우선)로 쪼개 컷 시간에 분배, 하단 번인(나눔스퀘어 Bold)
  - 클립 자체 오디오는 버리고 TTS만 사용
  - 종목 무관: manifest.json(shots[].{id,sentence_kr})만 있으면 어느 demo_* 폴더든 동작. 출력명=NAME(기본: 폴더명에서 demo_ 제거)
환경변수: NAME · SUBS=0 자막끄기 · MAXCH(기본 12) · FONT(기본 NanumSquare) · W/H/FPS
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
IMG  = os.path.join(ROOT, 'images')
TTS  = os.path.join(ROOT, 'tts')
OUT  = os.path.join(ROOT, 'out'); os.makedirs(OUT, exist_ok=True)
TMP  = os.path.join(OUT, 'tmp'); os.makedirs(TMP, exist_ok=True)
NAME = os.environ.get('NAME') or re.sub(r'^demo_', '', os.path.basename(os.path.abspath(ROOT)))

W   = int(os.environ.get('W', 1080))
H   = int(os.environ.get('H', 1920))
FPS = int(os.environ.get('FPS', 30))
MAXCH = int(os.environ.get('MAXCH', 12))
SUBS  = os.environ.get('SUBS', '1') != '0'
FONT  = os.environ.get('FONT', 'NanumSquare')
FONTDIR = '/usr/share/fonts/truetype/nanum'
XF    = float(os.environ.get('XFADE', '0.3'))   # 컷 사이 크로스페이드(초). 0=하드컷

MAN = json.load(open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8'))
SHOTS = sorted(MAN['shots'], key=lambda s: s['id'])
NARR = {n['id']: n for n in json.load(open(os.path.join(HERE, 'narration.json'), encoding='utf-8'))}

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(' '.join(cmd)+"\n"+r.stderr[-1500:]+"\n"); raise SystemExit(1)
    return r

def probe_dur(path):
    r = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',path],
                       capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except: return 0.0

# ---------- 자막 청크 분할 ----------
def chunk_text(s):
    s = s.strip()
    # 1) 문장부호 경계에서 절 분할(부호 유지)
    clauses = [c.strip() for c in re.split(r'(?<=[,\.\?!·])\s+', s) if c.strip()]
    chunks = []
    for c in clauses:
        c = c.rstrip(',')
        if len(c) <= MAXCH:
            chunks.append(c); continue
        # 2) 긴 절은 어절 단위로 <=MAXCH 씩 그리디 병합
        cur = ''
        for w in c.split(' '):
            cand = (cur + ' ' + w).strip()
            if len(cand) <= MAXCH or not cur:
                cur = cand
            else:
                chunks.append(cur); cur = w
        if cur: chunks.append(cur)
    return chunks or [s]

def ass_time(t):
    h = int(t//3600); m = int((t%3600)//60); sec = t%60
    return f"{h:d}:{m:02d}:{sec:05.2f}"

def ass_escape(s):
    return s.replace('\\','\\\\').replace('{','(').replace('}',')')

# ---------- 1) 컷별 정규화 세그먼트 (길이=나레이션) ----------
segs = []
timeline = []   # (start, dur, id, text)
clock = 0.0
missing = []
for idx, sh in enumerate(SHOTS):
    sid = sh['id']
    n = NARR.get(sid)
    adur = float(n['dur']) if n and n.get('file') and n['dur'] > 0.05 else float(sh.get('dur', 3))
    is_last = (idx == len(SHOTS)-1)
    tgt = adur + (0.0 if (is_last or XF<=0) else XF)   # 크로스페이드 겹침분만큼 세그 연장(총길이는 오디오와 동일 유지)
    src = os.path.join(IMG, f"shot{sid:02d}.mp4")
    seg = os.path.join(TMP, f"seg{sid:02d}.mp4")
    if not os.path.exists(src):
        missing.append(sid)
        # 회색 슬레이트로 자리 채움
        run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','lavfi',
             '-i', f'color=c=0x20242c:s={W}x{H}:r={FPS}:d={tgt:.3f}',
             '-vf', f"drawtext=fontfile={FONTDIR}/NanumSquareB.ttf:text='#{sid:02d}':fontcolor=white:fontsize=90:x=(w-tw)/2:y=(h-th)/2",
             '-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS), seg])
    else:
        vdur = probe_dur(src)
        # cover 스케일 + 센터크롭 → WxH, fps 통일, 오디오 제거, 길이=tgt
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
              f"crop={W}:{H},setsar=1,fps={FPS}")
        if vdur < tgt - 0.03:   # 모자라면 마지막 프레임 프리즈로 연장
            vf += f",tpad=stop_mode=clone:stop_duration={tgt - vdur + 0.05:.3f}"
        run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',src,
             '-an','-vf',vf,'-t',f'{tgt:.3f}',
             '-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS), seg])
    segs.append(seg)
    timeline.append((clock, adur, sid, sh['sentence_kr'].strip()))
    clock += adur

TOTAL = clock
print(f"세그먼트 {len(segs)}개 · 총 {TOTAL:.1f}s" + (f" · ⚠️클립누락 {missing}" if missing else ""))

# ---------- 2) 비디오 이어붙이기 (XF>0: 크로스페이드 체인 / else: 하드컷 concat) ----------
silent = os.path.join(TMP, 'silent.mp4')
if XF > 0 and len(segs) > 1:
    inp = []
    for s in segs: inp += ['-i', s]
    fc = []; prev = '[0:v]'
    for k in range(1, len(segs)):
        off = timeline[k][0]                      # = 앞 컷들 나레이션 누적 = 크로스페이드 시작점
        out = '[vout]' if k == len(segs)-1 else f'[vx{k}]'
        fc.append(f'{prev}[{k}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}{out}')
        prev = out
    run(['ffmpeg','-hide_banner','-loglevel','error','-y', *inp,
         '-filter_complex', ';'.join(fc), '-map','[vout]',
         '-c:v','libx264','-pix_fmt','yuv420p','-r',str(FPS), silent])
    print(f"  크로스페이드 {XF}s × {len(segs)-1}이음새")
else:
    concat_list = os.path.join(TMP, 'segs.txt')
    open(concat_list,'w').write(''.join(f"file '{os.path.abspath(s)}'\n" for s in segs))
    run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0',
         '-i', concat_list, '-c','copy', silent])

# ---------- 3) 오디오 concat (컷 순서, TTS) ----------
aud_inputs, amap = [], []
for i,(st,ad,sid,txt) in enumerate(timeline):
    n = NARR.get(sid)
    f = os.path.join(TTS, n['file']) if n and n.get('file') else None
    if f and os.path.exists(f):
        aud_inputs += ['-i', f]; amap.append(f'[{len(amap)}:a]')
    else:  # 무음 자리
        aud_inputs += ['-f','lavfi','-t',f'{ad:.3f}','-i','anullsrc=r=44100:cl=mono']; amap.append(f'[{len(amap)}:a]')
master_a = os.path.join(TMP, 'narration.m4a')
run(['ffmpeg','-hide_banner','-loglevel','error','-y', *aud_inputs,
     '-filter_complex', ''.join(amap)+f'concat=n={len(amap)}:v=0:a=1[a]',
     '-map','[a]','-c:a','aac','-b:a','192k', master_a])

# ---------- 4) 자막 ASS ----------
vf_final = None
if SUBS:
    fs = int(H*0.030)          # ~58px @1080p
    marginV = int(H*float(os.environ.get('SUBPOS','0.25')))  # 바닥에서 비율(0.25=75%높이)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV
Style: sub,{FONT},{fs},&H00FFFFFF,&H00000000,&H80000000,-1,1,4,2,2,80,80,{marginV}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, Effect, Text
"""
    lines = []
    for (st, ad, sid, txt) in timeline:
        chunks = chunk_text(txt)
        weights = [max(1,len(c)) for c in chunks]
        tot = sum(weights)
        acc = 0.0
        for c,w in zip(chunks, weights):
            seg_d = ad * (w/tot)
            cs = st + acc; ce = st + acc + seg_d; acc += seg_d
            lines.append(f"Dialogue: 0,{ass_time(cs)},{ass_time(ce)},sub,,0,0,,{ass_escape(c)}")
    ass_path = os.path.join(TMP, 'subs.ass')
    open(ass_path,'w',encoding='utf-8').write(head+'\n'.join(lines)+'\n')
    vf_final = f"subtitles={ass_path}:fontsdir={FONTDIR}"

# ---------- 5) 최종 mux (자막 번인 + 나레이션) ----------
final = os.path.join(OUT, f'{NAME}_final.mp4')
cmd = ['ffmpeg','-hide_banner','-loglevel','error','-y','-i',silent,'-i',master_a]
if vf_final: cmd += ['-vf', vf_final]
cmd += ['-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','medium','-crf','19',
        '-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest', final]
run(cmd)
print(f"✅ 완성: {final}  ({probe_dur(final):.1f}s, {W}x{H})")
