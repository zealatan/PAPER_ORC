#!/usr/bin/env python3
"""cocacola_final.html 의 show()/subDuration() 타이밍을 그대로 복제해
   현재 덱(cocacola_deck_current.json)의 총 재생 시간을 계산한다."""
import json, re, sys, os

HTML = os.path.join(os.path.dirname(__file__), '..', 'deck', 'cocacola_final.html')
DECK = os.path.join(os.path.dirname(__file__), '..', 'data', 'cocacola_deck_current.json')

# ---- HTML에서 상수 추출 ----
src = open(HTML, encoding='utf-8').read()
def grab(pat):
    m = re.search(pat, src)
    return m.group(1) if m else None

PACE = float(grab(r'var PACE\s*=\s*([\d.]+)'))
SUB_SPEED = float(grab(r'var SUB_SPEED\s*=\s*([\d.]+)'))
FAST_MS = int(grab(r'var FAST_MS\s*=\s*(\d+)'))
# SUBS 객체
subs_txt = re.search(r'var SUBS\s*=\s*(\{.*?\n\});', src, re.S).group(1)
subs_txt = re.sub(r'(?m)^(\s*)(\d+)\s*:', r'\1"\2":', subs_txt)  # 숫자 키 → "키"
SUBS = json.loads(subs_txt)
SUBS = {int(k): v for k, v in SUBS.items()}
# SUB_FAST
sf_txt = re.search(r'var SUB_FAST\s*=\s*(\{.*?\});', src, re.S).group(1)
sf_txt = re.sub(r'([{,]\s*)(\d+)\s*:', r'\1"\2":', sf_txt)
SUB_FAST = json.loads(sf_txt)
SUB_FAST = {int(k): v for k, v in SUB_FAST.items()}
# SUB_SPEED_SKIP
ss_txt = re.search(r'var SUB_SPEED_SKIP\s*=\s*(\{[^}]*\})', src).group(1)
ss_txt = re.sub(r'(\w+)\s*:\s*true', r'"\1": true', ss_txt)
SUB_SPEED_SKIP = {int(k): v for k, v in json.loads(ss_txt).items()}

deck = json.load(open(DECK, encoding='utf-8'))
SCENES = deck['scenes']

def sub_speed(i):
    return 1 if SUB_SPEED_SKIP.get(i) else SUB_SPEED
def sub_rate(i):
    return SCENES[i].get('subRate') or 1
def sub_get_lines(i):
    return SCENES[i].get('subLines') or SUBS.get(i) or []
def sub_line_ms(t):
    c = len(re.sub(r'\s', '', t))
    return min(7000, max(1200, c * 225))
def sub_fix_from(i, L):
    s = SUB_FAST.get(i)
    if not s: return 0
    idx = L.index(s) if s in L else -1
    return idx if idx > 0 else 0
def sub_line_dur(i, k, ln, L):
    base = FAST_MS if k < sub_fix_from(i, L) else sub_line_ms(ln)
    return round(base * sub_rate(i) * sub_speed(i))
def sub_start_times(i, L):
    sc = SCENES[i]
    if sc.get('subTimes') and len(sc['subTimes']) == len(L):
        return list(sc['subTimes'])
    t, arr = 0, []
    for k in range(len(L)):
        arr.append(t); t += sub_line_dur(i, k, L[k], L)
    return arr
def sub_duration(i):
    sc = SCENES[i]
    if sc.get('subHold'): return sc['subHold']
    L = sub_get_lines(i)
    if not L: return 0
    starts = sub_start_times(i, L)
    end = 0
    for k in range(len(L)):
        e = starts[k] + sub_line_dur(i, k, L[k], L)
        if e > end: end = e
    return end

total = 0
print(f"{'#':>2} {'tpl':<12} {'hold(ms)':>9} {'src':<8}")
for i, sc in enumerate(SCENES):
    sd = sub_duration(i)
    if sd > 0:
        hold = sd; srckind = 'sub'
    else:
        hold = sc.get('dur', 0) * (1 if sc.get('tpl') == 'videohook' else PACE)
        srckind = 'dur'
    total += hold
    print(f"{i:>2} {sc.get('tpl',''):<12} {hold:>9.0f} {srckind:<8}")
print("-"*40)
print(f"TOTAL: {total/1000:.1f}s  ({int(total//60000)}m {int((total/1000)%60)}s)")
print(f"TOTAL_MS={int(total)}")
