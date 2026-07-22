#!/usr/bin/env python3
"""현재 덱(cocacola_deck_current.json)의 씬별 자막 줄(subGetLines)을 순서대로 추출.
   TTS 더빙의 입력 텍스트. 출력: rec/narration_lines.json + 사람이 읽는 요약."""
import json, re, os, sys

HTML = os.path.join(os.path.dirname(__file__), '..', 'deck', 'cocacola_final.html')
DECK = os.path.join(os.path.dirname(__file__), '..', 'data', 'cocacola_deck_current.json')
OUT  = os.path.join(os.path.dirname(__file__), 'narration_lines.json')

src = open(HTML, encoding='utf-8').read()
subs_txt = re.search(r'var SUBS\s*=\s*(\{.*?\n\});', src, re.S).group(1)
subs_txt = re.sub(r'(?m)^(\s*)(\d+)\s*:', r'\1"\2":', subs_txt)
SUBS = {int(k): v for k, v in json.loads(subs_txt).items()}

deck = json.load(open(DECK, encoding='utf-8'))
SCENES = deck['scenes']

def sub_get_lines(i):
    return SCENES[i].get('subLines') or SUBS.get(i) or []

result = []
total_lines = 0
total_chars = 0
for i, sc in enumerate(SCENES):
    lines = sub_get_lines(i)
    result.append({'scene': i, 'tpl': sc.get('tpl'), 'lines': lines,
                   'from': 'subLines' if sc.get('subLines') else ('SUBS' if SUBS.get(i) else 'none')})
    total_lines += len(lines)
    total_chars += sum(len(re.sub(r'\s','',l)) for l in lines)

json.dump(result, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

for r in result:
    if r['lines']:
        print(f"씬{r['scene']:>2} [{r['tpl']:<11}] {len(r['lines']):>2}줄 ({r['from']})")
print('-'*40)
print(f"총 씬(자막 있는): {sum(1 for r in result if r['lines'])}")
print(f"총 줄 수: {total_lines}")
print(f"총 글자 수(공백제외): {total_chars}  → 예상 크레딧 ≈ {total_chars}")
print(f"저장: {OUT}")
