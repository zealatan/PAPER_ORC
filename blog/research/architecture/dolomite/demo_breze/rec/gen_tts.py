#!/usr/bin/env python3
"""건축쇼츠 나레이션 TTS(범용, ElevenLabs eleven_v3 클론 보이스).
   - manifest.json 의 shots[].sentence_kr 를 컷 순서대로 읽어 컷당 1개 mp3 생성
   - tts/s{ID:02d}.mp3 저장, 이미 있으면 건너뜀(재개 가능). raw 보존→배속만 재조정 무료
   - 각 컷 길이 측정 → rec/narration.json  (build_video.py 가 사용)
   - 키는 상위 경로에서 .eleven_key 자동 탐색(blog/.eleven_key 공유)
   ※ eleven_v3 는 previous_text/next_text 미지원 → 문맥 파라미터 없이 호출
   환경변수: TTS_SPEED(기본 1.0 배속·음정유지), TTS_STABILITY(기본 0.4)
"""
import json, os, subprocess, time
from concurrent.futures import ThreadPoolExecutor
import urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')

KEY = None
_d = ROOT
for _ in range(8):                 # 상위로 올라가며 .eleven_key 탐색
    _kp = os.path.join(_d, '.eleven_key')
    if os.path.exists(_kp):
        KEY = open(_kp).read().strip(); break
    _d = os.path.dirname(os.path.abspath(_d))
assert KEY, ".eleven_key 못 찾음 (상위 경로 탐색 실패)"

VOICE = "Iu0W7wMhBwV2Qjzj0Fp2"
MODEL = "eleven_v3"
STABILITY = float(os.environ.get('TTS_STABILITY', '0.4'))
SPEED = float(os.environ.get('TTS_SPEED', '1.0'))

MAN = json.load(open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8'))
SHOTS = sorted(MAN['shots'], key=lambda s: s['id'])
TEXTS = [s['sentence_kr'].strip() for s in SHOTS]
IDS = [s['id'] for s in SHOTS]

TTSDIR = os.path.join(ROOT, 'tts')
os.makedirs(TTSDIR, exist_ok=True)

def ctx_prev(g): return " ".join(TEXTS[max(0, g-2):g])[-300:]
def ctx_next(g): return " ".join(TEXTS[g+1:g+3])[:300]

def dur(path):
    try:
        r = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
                            '-of','csv=p=0', path], capture_output=True, text=True)
        return float(r.stdout.strip())
    except Exception:
        return 0.0

def speedup(raw, out):
    if abs(SPEED - 1.0) < 1e-3:
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',raw,
                        '-c:a','libmp3lame','-b:a','192k', out], check=True)
    else:
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',raw,
                        '-filter:a', f'atempo={SPEED}', '-b:a','192k', out], check=True)

def gen(args):
    g, text = args
    sid = IDS[g]
    path = os.path.join(TTSDIR, f"s{sid:02d}.mp3")
    raw  = os.path.join(TTSDIR, f"s{sid:02d}.raw.mp3")
    if os.path.exists(path) and os.path.getsize(path) > 1500:
        return (sid, path, dur(path), 'skip')
    if os.path.exists(raw) and os.path.getsize(raw) > 1500:
        speedup(raw, path); return (sid, path, dur(path), 'respeed')
    # NOTE: eleven_v3 는 previous_text/next_text 미지원 → 문맥 파라미터 없이 호출
    body = json.dumps({
        "text": text,
        "model_id": MODEL,
        "voice_settings": {"stability":STABILITY,"similarity_boost":0.85,"style":0.0,"use_speaker_boost":True},
    }).encode()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}"
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, data=body, method='POST',
                headers={"xi-api-key":KEY, "Content-Type":"application/json", "Accept":"audio/mpeg"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            if len(data) < 1500: raise RuntimeError(f"too small {len(data)}")
            open(raw,'wb').write(data)
            speedup(raw, path)
            return (sid, path, dur(path), 'ok')
        except urllib.error.HTTPError as e:
            msg = e.read()[:200]
            if e.code == 429: time.sleep(3*(attempt+1)); continue
            if attempt == 4: return (sid, None, 0, f'HTTP{e.code}:{msg}')
            time.sleep(2*(attempt+1))
        except Exception as e:
            if attempt == 4: return (sid, None, 0, f'ERR:{e}')
            time.sleep(2*(attempt+1))
    return (sid, None, 0, 'fail')

def main():
    jobs = list(enumerate(TEXTS))
    results = [None]*len(jobs)
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(gen, j): j[0] for j in jobs}
        done = 0
        for fut in list(futs):
            g = futs[fut]; r = fut.result(); results[g] = r; done += 1
            if r[1] is None:
                print(f"  [{done}/{len(jobs)}] s{r[0]:02d} FAIL {r[3]}", flush=True)
            else:
                print(f"  [{done}/{len(jobs)}] s{r[0]:02d} {r[3]} {r[2]:.2f}s", flush=True)
    narr = []
    fails = 0
    for r in results:
        sid, path, d, st = r
        if path is None: fails += 1
        narr.append({'id':sid, 'file':os.path.basename(path) if path else None, 'dur':round(d,3), 'status':st})
    json.dump(narr, open(os.path.join(HERE,'narration.json'),'w',encoding='utf-8'),
              ensure_ascii=False, indent=1)
    ok = sum(1 for m in narr if m['file'])
    print('-'*44)
    print(f"완료 {ok}/{len(narr)} 성공, {fails} 실패 · 총 {sum(m['dur'] for m in narr):.1f}s")
    if fails: print("⚠️ 실패분은 재실행하면 재개됩니다.")

if __name__ == '__main__':
    main()
