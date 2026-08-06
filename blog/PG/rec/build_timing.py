#!/usr/bin/env python3
"""TTS 클립 길이로 덱 타이밍(subTimes/subHold)을 만들어 더빙 덱 생성 +
   음성 트랙 절대 타임라인(voice_timeline.json) 산출."""
import json, re, os

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, '..')
HTML = os.path.join(ROOT, 'deck', 'pg_final.html')       # PACE·SUBS 소스
DECK = os.path.join(ROOT, 'deck', 'pg_deck.json')        # 입력 덱
MANI = os.path.join(HERE, 'tts_manifest.json')
OUT_DECK = os.path.join(ROOT, 'deck', 'pg_deck_dubbed.json')  # 타이밍 반영 덱
OUT_TL   = os.path.join(HERE, 'voice_timeline.json')

GAP_MS  = 120   # 줄 사이 간격
TAIL_MS = 350   # 씬 끝 여유

src = open(HTML, encoding='utf-8').read()
PACE = float(re.search(r'var PACE\s*=\s*([\d.]+)', src).group(1))
subs_txt = re.search(r'var SUBS\s*=\s*(\{.*?\n\});', src, re.S).group(1)
subs_txt = re.sub(r'(?m)^(\s*)(\d+)\s*:', r'\1"\2":', subs_txt)
SUBS = {int(k): v for k, v in json.loads(subs_txt).items()}

deck = json.load(open(DECK, encoding='utf-8'))
SCENES = deck['scenes']
mani = json.load(open(MANI, encoding='utf-8'))
DUR = {}  # (scene,line) -> ms
FILE = {}
for m in mani:
    if m['file']:
        DUR[(m['scene'], m['line'])] = int(round(m['dur']*1000))
        FILE[(m['scene'], m['line'])] = m['file']

def sub_get_lines(i):
    return SCENES[i].get('subLines') or SUBS.get(i) or []

timeline = []   # {file, abs_ms, dur_ms}
cursor = 0
for i, sc in enumerate(SCENES):
    lines = sub_get_lines(i)
    if not lines:
        # 나레이션 없는 씬(씬0 등): 기존 로직 hold = dur*PACE (videohook은 1)
        hold = sc.get('dur', 0) * (1 if sc.get('tpl') == 'videohook' else PACE)
        cursor += hold
        continue
    # 줄별 길이
    durs = [DUR.get((i, k), 1200) for k in range(len(lines))]
    subTimes = []
    t = 0
    for k in range(len(lines)):
        subTimes.append(int(t))
        t += durs[k] + GAP_MS
    subHold = int(subTimes[-1] + durs[-1] + TAIL_MS)
    # 덱에 반영
    sc['subLines'] = lines
    sc['subTimes'] = subTimes
    sc['subHold'] = subHold
    # 타임라인(절대시각)
    for k in range(len(lines)):
        f = FILE.get((i, k))
        if f:
            timeline.append({'file': f, 'abs_ms': int(cursor + subTimes[k]), 'dur_ms': durs[k]})
    cursor += subHold

json.dump(deck, open(OUT_DECK, 'w', encoding='utf-8'), ensure_ascii=False)
json.dump({'total_ms': int(cursor), 'items': timeline},
          open(OUT_TL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print(f"더빙 덱: {OUT_DECK}")
print(f"음성 타임라인: {OUT_TL}  (클립 {len(timeline)}개)")
print(f"총 길이: {cursor/1000:.1f}s  ({int(cursor//60000)}m {int((cursor/1000)%60)}s)")
print(f"(기존 마스터 721s 대비 변화)")
