#!/usr/bin/env python3
"""363줄 나레이션을 클론 보이스로 TTS 생성 (eleven_v3, 앞뒤 문맥 연결).
   - tts/ 에 s{scene}_l{line}.mp3 저장, 이미 있으면 건너뜀(재개 가능)
   - 각 클립 길이 측정 → rec/tts_manifest.json
"""
import json, os, sys, subprocess, time
from concurrent.futures import ThreadPoolExecutor
import urllib.request, urllib.error

ROOT = os.path.join(os.path.dirname(__file__), '..')
KEY = None
for _kp in (os.path.join(ROOT, '.eleven_key'), os.path.join(ROOT, '..', '.eleven_key')):
    if os.path.exists(_kp):
        KEY = open(_kp).read().strip(); break
assert KEY, ".eleven_key 못 찾음 (MCD/ 또는 blog/)"
VOICE = "Iu0W7wMhBwV2Qjzj0Fp2"
MODEL = "eleven_v3"
STABILITY = float(os.environ.get('TTS_STABILITY', '0.4'))  # 톤: 낮을수록 표현적/자연
SPEED = float(os.environ.get('TTS_SPEED', '1.062'))         # atempo 배속(음정 유지). 1.18→1.062: 10% 감속
LINES = json.load(open(os.path.join(os.path.dirname(__file__), 'narration_lines.json'), encoding='utf-8'))
TTSDIR = os.path.join(ROOT, 'tts')
os.makedirs(TTSDIR, exist_ok=True)

# 평탄화: 문맥(previous/next) 위해 전체 줄을 순서대로
flat = []   # (scene, k, text)
for sc in LINES:
    for k, ln in enumerate(sc['lines']):
        flat.append((sc['scene'], k, ln))
texts = [t for _,_,t in flat]

def ctx_prev(g):
    return " ".join(texts[max(0,g-2):g])[-300:]
def ctx_next(g):
    return " ".join(texts[g+1:g+3])[:300]

def dur(path):
    try:
        r = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',path],
                           capture_output=True, text=True)
        return float(r.stdout.strip())
    except Exception:
        return 0.0

def speedup(raw, out):
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',raw,
                    '-filter:a',f'atempo={SPEED}','-b:a','192k',out], check=True)

def gen(args):
    g, (scene, k, text) = args
    path = os.path.join(TTSDIR, f"s{scene:02d}_l{k:02d}.mp3")
    raw = os.path.join(TTSDIR, f"s{scene:02d}_l{k:02d}.raw.mp3")
    if os.path.exists(path) and os.path.getsize(path) > 1500:
        return (scene, k, path, dur(path), 'skip')
    if os.path.exists(raw) and os.path.getsize(raw) > 1500:   # 원본 있으면 API 없이 재처리
        speedup(raw, path)
        return (scene, k, path, dur(path), 'respeed')
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
            if len(data) < 1500:
                raise RuntimeError(f"too small {len(data)}")
            with open(raw, 'wb') as f:
                f.write(data)
            speedup(raw, path)          # atempo 배속 적용 (raw는 보존 → 속도 재조정 무료)
            return (scene, k, path, dur(path), 'ok')
        except urllib.error.HTTPError as e:
            msg = e.read()[:200]
            if e.code == 429:
                time.sleep(3*(attempt+1)); continue
            if attempt == 4:
                return (scene, k, None, 0, f'HTTP{e.code}:{msg}')
            time.sleep(2*(attempt+1))
        except Exception as e:
            if attempt == 4:
                return (scene, k, None, 0, f'ERR:{e}')
            time.sleep(2*(attempt+1))
    return (scene, k, None, 0, 'fail')

def main():
    jobs = list(enumerate(flat))
    results = [None]*len(jobs)
    done = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(gen, j): j[0] for j in jobs}
        for fut in futs:
            pass
        for fut in list(futs):
            g = futs[fut]
            r = fut.result()
            results[g] = r
            done += 1
            if r[2] is None:
                print(f"  [{done}/{len(jobs)}] FAIL s{r[0]}_l{r[1]}: {r[4]}", flush=True)
            elif done % 30 == 0:
                print(f"  [{done}/{len(jobs)}] ...", flush=True)
    # manifest
    manifest = []
    fails = 0
    for r in results:
        scene, k, path, d, st = r
        if path is None: fails += 1
        manifest.append({'scene':scene,'line':k,'file':os.path.basename(path) if path else None,
                         'dur':round(d,3),'status':st})
    json.dump(manifest, open(os.path.join(os.path.dirname(__file__),'tts_manifest.json'),'w',encoding='utf-8'),
              ensure_ascii=False, indent=1)
    ok = sum(1 for m in manifest if m['file'])
    print('-'*40)
    print(f"완료: {ok}/{len(manifest)} 성공, {fails} 실패")
    print(f"총 오디오 길이: {sum(m['dur'] for m in manifest):.1f}s")
    if fails: print("⚠️ 실패분은 재실행하면 재개됩니다.")

main()
