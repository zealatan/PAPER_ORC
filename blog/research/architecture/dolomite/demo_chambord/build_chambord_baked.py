#!/usr/bin/env python3
"""demo_chambord 빌더 — 샹보르: 왕이 사냥하러 지었으나 거의 안 산, 이중나선 계단의 세계 최대급 성.
   미모 우선 + 4-스킨 + 위트/대화체 + 연속-무빙 + CLEAN PLATE(숫자 없음, 후처리 오버레이).
   ※ 고증(deep-research/CMN) 반영: 다빈치 '설계' 아님(전설/영감만·삭제) · 365굴뚝/84계단/800기둥 삭제 ·
     440실·1519·72일·코송강 늪지·이중나선(안 마주침)·미완성은 확인됨. 갤러리 CSS/JS는 ../demo_montsaintmichel 재사용.
"""
import json, os, re, html
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
REF  = os.path.join(HERE, '..', 'demo_montsaintmichel', 'gallery.html')

TOPIC = '샹보르 성 — 왕이 짓고도 안 산, 이중나선의 거대한 성 (Château de Chambord)'
SUBJECT = ("Château de Chambord — the largest chateau in the Loire Valley, a colossal white French-Renaissance "
    "chateau in a vast walled forest park: a massive central keep (donjon) flanked by huge round corner towers, "
    "and above it an extraordinary roofscape crowded with hundreds of ornate chimneys, turrets, dormers and cupolas "
    "crowned by a tall central lantern tower, like a little stone town in the sky; set on the marshy banks of the "
    "small River Cosson, symmetrical and immense.")

CLEAN = (" Absolutely NO rendered text, numbers, digits, labels, dimension lines, callouts, counters, arrows-with-text "
    "or graphic annotations of any kind anywhere in the frame — a completely clean plate; all numeric graphics are "
    "added later as a separate post overlay. no watermark.")
STYLE_REAL = ("photorealistic cinematic drone footage with a subtle tilt-shift miniature feel, physically-based "
    "lighting, subtle film grain, soft cinematic color grade, vertical 9:16, Loire Valley France setting, a colossal "
    "white French-Renaissance chateau with a fantastical crowded roofscape rising from a vast forest, soft "
    f"silvery-golden light.{CLEAN}")
STYLE_DIORAMA = ("signature floating-diorama miniature cutaway: a rectangular slab of the forest and marshy riverbank "
    "with the great chateau on it, cut out and floating in a WARM graduated amber-to-charcoal void, flat cut-sides "
    "exposing wet ground and foundations, lit by a warm low amber key light with soft golden fill and gentle rim "
    "glow, faint volumetric haze, portrait telephoto look, shallow depth of field, photorealistic miniature render, "
    f"warm cinematic color grade, vertical 9:16.{CLEAN}")
STYLE_XRAY = ("see-through x-ray / technical scan visualization, deep graduated navy-black void, the chateau and its "
    "central tower rendered as a glowing translucent cyan wireframe with x-ray layers revealing the double-helix "
    "staircase inside — two intertwined spiral ramps around a hollow open core — a soft horizontal scan-line "
    f"sweeping through, holographic engineering feel, subtle film grain, cyan accents, vertical 9:16.{CLEAN}")
STYLE_BLUEPRINT = ("an architectural blueprint that morphs into photoreal reality, vertical 9:16. The shot BEGINS as "
    "a clean cyan-and-white line drawing on deep blueprint-blue paper with a faint grid, then a bright wipe sweeps "
    f"across and it MORPHS into the real white stone structure with soft light.{CLEAN}")
DYN_REAL = f"photorealistic cinematic footage, soft cinematic color grade, vertical 9:16, Loire Valley forest setting.{CLEAN}"
DYN_DIORAMA = f"signature floating-diorama miniature, warm graduated amber-charcoal void, warm cinematic color grade, vertical 9:16.{CLEAN}"
DYN_XRAY = f"see-through x-ray / scan visualization, deep navy-black void, glowing translucent cyan wireframe revealing an intertwined double-helix staircase, scan-line sweep, vertical 9:16.{CLEAN}"
DYN_BLUEPRINT = f"architectural blueprint morphing into a real white stone Renaissance palace, blueprint-blue paper with grid, cyan line-drawing wiping into real stone, vertical 9:16.{CLEAN}"
BASE  = {'real':STYLE_REAL,'diorama':STYLE_DIORAMA,'xray':STYLE_XRAY,'blueprint':STYLE_BLUEPRINT}
DBASE = {'real':DYN_REAL,'diorama':DYN_DIORAMA,'xray':DYN_XRAY,'blueprint':DYN_BLUEPRINT}
CLS_KO   = {'real':'실사','diorama':'디오라마','xray':'X-ray','blueprint':'청사진'}
CLS_STYLE= {'real':'color:#8fd06f;border-color:#8fd06f55','diorama':'color:#e8a33d;border-color:#e8a33d55',
            'xray':'color:#5bd0ff;border-color:#5bd0ff55','blueprint':'color:#7aa2ff;border-color:#7aa2ff55'}

# role, cls, transition, dur, dyn, effect, kr, desc, camera, anno
SHOTS = [
 ('hook','real','cut',5,1,'지도→드론 다이브 줌 + 성 리빌', "프랑스 루아르, 드넓은 숲 한가운데 — 어마어마하게 큰 하얀 성이 나타납니다.",
   "DYNAMIC opening: start on a clean minimal stylized map of France (soft grey, no text) as a glowing cyan pin drops onto the Loire Valley; a fast Google-Earth-style DIVE ZOOM plunges down through soft clouds into a real cinematic drone view sweeping over a vast dense forest toward a colossal white Renaissance chateau whose fantastical roofscape of chimneys and towers rises above the trees. no words anywhere.", "", ""),
 ('subject','real','cut',5,0,'', "샹보르. 루아르에서 가장 큰 성이에요.",
   "a majestic full 360-degree orbit at soft golden hour around the enormous white chateau, its extraordinary crowded roofscape of ornate chimneys, turrets and a tall central lantern tower glowing warmly, the vast forest spreading all around.",
   "a slow cinematic 360-degree orbit around the immense chateau and its crowded roofscape", ""),
 ('hook','real','cut',4,0,'', "왕이 사냥하러 지은 별궁이라는데 — 사냥 오두막치곤 좀 과하죠?",
   "a low cinematic drone glide sweeping along the immense symmetrical white facade to convey its overwhelming scale, tiny visitors far below for a sense of size, bright soft daylight.",
   "a slow low glide along the vast facade showing its overwhelming size", ""),
 ('cause','diorama','cut',5,0,'', "1519년, 프랑수아 1세가 사냥터 한복판, 코송 강가 늪지에 이 거대한 성을 올리기 시작합니다.",
   "a warm floating-diorama cutaway of the forest and the marshy banks of a small river, the great chateau's massive central keep beginning to rise on timber and stone foundations set into the wet ground, wet-ground and foundation strata exposed on the cut sides.",
   "a slow orbit as the huge keep rises from the marshy foundations on the floating slab", "[오버레이] 1519 · 코송 강 늪지"),
 ('scale','blueprint','cut',5,1,'궁전 도면→실물 모프', "방만 440개. 애초에 도면부터가 궁전이었죠.",
   "DYNAMIC blueprint-to-real: a vast symmetrical Renaissance palace floor-plan — a central keep ringed by hundreds of rooms and four huge round towers — draws itself on blueprint-blue paper, then a bright wipe MORPHS it into the real colossal white stone chateau, revealing this was a palace, not a lodge.", "", "[오버레이] 방 440"),
 ('solution','xray','cut',5,1,'이중나선 스캔 리빌', "그리고 한가운데엔 — 나선이 두 개 겹쳐 돌아가는 이중나선 계단이 숨어 있어요.",
   "DYNAMIC x-ray reveal: the chateau's central tower turns translucent as a scan-line sweeps in to reveal the famous double-helix staircase inside — two separate intertwined spiral ramps winding upward around a hollow open central core, glowing cyan wireframe, the camera cranes up through the twin spirals.", "", ""),
 ('solution','diorama','cut',5,0,'', "오르는 사람과 내려오는 사람이, 서로 보이면서도 계단에선 절대 안 마주칩니다.",
   "a warm floating-diorama cutaway of the double-helix staircase: two tiny figures, one climbing and one descending on the two separate intertwined ramps, catching glimpses of each other across the open central well yet never sharing a single step, the two spiral paths clearly never crossing.",
   "a slow orbit around the twin intertwined ramps following the two figures who never meet", "[오버레이] 두 나선 · 안 마주침"),
 ('scale','real','cut',5,0,'', "지붕에 올라서면, 굴뚝과 탑이 도시처럼 빽빽이 솟아 있죠.",
   "a beautiful real shot up on the chateau's roof terrace among a dense forest of ornate carved chimneys, turrets, dormers and cupolas crowned by the tall central lantern tower, like a little stone town in the sky, warm golden light.",
   "a slow glide through the crowded rooftop of chimneys and turrets toward the central lantern", ""),
 ('fail','real','cut',5,0,'', "이렇게까지 지어놓고 — 정작 왕은, 전해지기로 평생 72일밖에 안 머물렀대요.",
   "a wide serene golden aerial of the immense chateau standing almost empty in its vast lonely forest, a sense of overwhelming grandeur barely ever used, quiet irony in the soft light.",
   "a slow high aerial pulling back over the vast, nearly empty chateau in its forest", "[오버레이] 약 72일"),
 ('end','diorama','cut',5,0,'', "완성도 못 본 채 왕은 떠나고, 성은 오래도록 춥고 텅 비어 있었죠.",
   "a warm floating-diorama of the great chateau with scaffolding still on unfinished parts and cold empty halls hinted inside, drifting dust, a single tiny caretaker figure, the warm light dimming to a lonely tone.",
   "a slow orbit around the unfinished, empty chateau as the light dims", ""),
 ('scale','real','cut',5,0,'', "그래도 샹보르는, 르네상스가 남긴 가장 대담한 걸작으로 남았습니다.",
   "a gorgeous golden-hour hero shot of Chambord in full, its magnificent silhouette and fantastical roofscape standing bold and iconic against a luminous sky, grand and breathtaking.",
   "a majestic slow orbit that pulls back to a hero wide of the whole chateau at golden hour", ""),
 ('end','real','cont',10,0,'', "숲 위에 홀로 선 거대한 꿈. 샹보르는 오늘도 그 자리에 그대로 서 있습니다.",
   "a long, unhurried, lingering dusk shot: the colossal white chateau standing alone above the misty forest as warm golden light very slowly fades toward soft blue dusk, a few windows glowing, the camera drifting almost imperceptibly and then holding, letting the immense silhouette breathe and settle, quietly grand and cinematic.",
   "an almost-still, very slow drift that settles into a long hold on the lone chateau above the forest as dusk falls", ""),
]

CONT = (" The shot begins and ends on smooth, continuous camera motion with no abrupt start, freeze or hard stop, "
        "gentle easing, so it blends seamlessly into the neighbouring shots.")
def prompt_final(role,cls,tr,dur,dyn,eff,kr,desc,cam,anno):
    if dyn:
        return f"{DBASE[cls]} {desc} One continuous ~{dur}-second shot.{CONT}"
    return f"{BASE[cls]} {desc} SUBJECT: {SUBJECT} Camera: {cam} One continuous ~{dur}-second shot.{CONT}"

t=0; rows=[]
for i,s in enumerate(SHOTS):
    role,cls,tr,dur,dyn,eff,kr,desc,cam,anno = s
    rows.append({'id':i+1,'role':role,'cls':cls,'style_class':CLS_KO[cls],'transition':tr,'t':t,'dur':dur,
                 'dynamic':bool(dyn),'effect':eff,'sentence_kr':kr,'desc':desc,'camera':cam,
                 'anno_rendered':anno,'prompt_final':prompt_final(*s)})
    t += dur
TOTAL=t; mix=Counter(r['style_class'] for r in rows)

manifest = {
 'topic':TOPIC,
 'mode':'CLEAN-PLATE(숫자 미포함, 후처리 오버레이) · 4-skin · witty · beauty-first · 고증검증(deep-research/CMN)',
 'filter_score':{'대중인지도':2,'외관vs기능반전':2,'문제선명도':1,'뻔한해법실패':1,'반직관해결':2,
                 '작동과정명확성':1,'시각화가능성':2,'강한숫자':1,'공식자료충분':2,'현재성결말':2,'미모(가중)':3,
                 '총점':16,'판정':'미모 우선 채택'},
 'candidate_sentences_hit':['사냥 별궁이라기엔 궁전급','두 사람이 안 마주치는 이중나선','왕이 짓고도 거의 안 산(72일)','완성도 못 본 미완성 걸작'],
 'fact_pack_verified':{'착공':'1519, 프랑수아 1세, 사냥 별궁, 루아르 최대(✅ CMN/Britannica)',
   '이중나선':'중앙 이중나선 계단 — 두 나선이 열린 중심 돌며, 오르내리는 사람이 서로 보이나 계단에선 안 마주침(옥상서만 합류)(✅)',
   '방':'약 440실(✅ WHE 확인)',
   '왕 체류':'전해지기로 ~72일/42박, 32년 재위 중 극소(✅ but 72는 전통 수치)',
   '입지':'코송 강(루아르 아님) 늪지, 후대 운하화(✅)',
   '미완성':'1547 프랑수아1세 사망 시 미완성, 상주 아님(✅). 완성은 후대 루이14세',
   '삭제/주의':'다빈치 "설계"=DISPUTED(영감/전설만, 1519.5 사망) → 삭제 · 365굴뚝(하루하나)=전설(≈200개) → 삭제 · 84계단/800기둥=미검증 → 삭제 · 루아르 물길돌리기(다빈치설)=전설 → 삭제',
   '출처':'chambord.org(공식), britannica.com, worldhistory.org'},
 'note':'고증 검증 완료본. 미검증/전설 전부 삭제. 미모우선·4스킨·clean plate·위트·연속무빙. #11 걸작→#12 여운 엔딩.',
 'style_base':STYLE_REAL,'style_base_diorama':STYLE_DIORAMA,'style_base_xray':STYLE_XRAY,'style_base_blueprint':STYLE_BLUEPRINT,
 'subject':SUBJECT,'shots':rows,
}
json.dump(manifest, open(os.path.join(HERE,'manifest.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)

with open(os.path.join(HERE,'prompts.txt'),'w',encoding='utf-8') as f:
    f.write(f"# {TOPIC}\n# 고증검증 · CLEAN-PLATE · 4-스킨 · 위트 · {len(SHOTS)}컷 · {TOTAL}초\n\n")
    for r in rows:
        f.write(f"── #{r['id']:02d} {r['role']} · {r['t']}s→{r['t']+r['dur']}s · [{r['style_class']}]"
                + (f" · ⚡{r['effect']}" if r['dynamic'] else "") + "\n")
        f.write(f"  나레이션: {r['sentence_kr']}\n")
        if r['anno_rendered']: f.write(f"  오버레이(후처리): {r['anno_rendered']}\n")
        f.write(f"  프롬프트: {r['prompt_final']}\n\n")
with open(os.path.join(HERE,'script.md'),'w',encoding='utf-8') as f:
    f.write(f"# {TOPIC} — 대본 (고증검증·위트·미모우선)\n\n**전체 나레이션**\n\n")
    f.write(' '.join(r['sentence_kr'] for r in rows) + "\n\n| # | 구간 | 스킨 | 나레이션 |\n|---|---|---|---|\n")
    for r in rows:
        f.write(f"| {r['id']} | {r['t']}s→{r['t']+r['dur']}s | {r['style_class']}"
                + (f"·⚡{r['effect']}" if r['dynamic'] else "") + f" | {r['sentence_kr']} |\n")

ref = open(REF, encoding='utf-8').read()
style = re.search(r'<style>.*?</style>', ref, re.S).group(0)
script = re.search(r'<script>.*?</script>', ref, re.S).group(0)
ndyn = sum(1 for r in rows if r['dynamic'])
cards=[]
for r in rows:
    dyncls = ' dyn' if r['dynamic'] else ' '
    ph2 = '⚡DYNAMIC · 프롬프트→드롭' if r['dynamic'] else '프롬프트→드롭'
    dynspan = f'<span class="dyn">⚡ {html.escape(r["effect"])}</span>' if r['dynamic'] else ''
    if r['dynamic']: ovlabel, ovbody = '카메라/효과', html.escape(r['effect'])
    elif r['anno_rendered']: ovlabel, ovbody = '🎬 오버레이(후처리)', html.escape(r['anno_rendered'])
    else: ovlabel, ovbody = '🎬 오버레이(후처리)', '<i style="color:#4a515b">— (없음)</i>'
    t0,t1 = r['t'], r['t']+r['dur']
    cards.append(
f'''<article class="c{dyncls}">
<div class="slot empty{dyncls}"><div class="ph">#{r['id']:02d} · {r['role']} · {t0}s→{t1}s<br><span>{ph2}</span></div><input type="file" accept="video/*,image/*" onchange="drop(this)"><img></div>
<div class="meta">
<div class="hd"><b>{r['id']:02d}</b> <span class="role">{r['role']}</span> <span class="tr">{r['transition']}</span>
 <span class="cls" style="{CLS_STYLE[r['cls']]}">{r['style_class']}</span> {dynspan} <span class="dur">{t0}s→{t1}s</span></div>
<p class="kr">{html.escape(r['sentence_kr'])}</p>
<div class="ov"><b>{ovlabel}</b><br>{ovbody}</div>
<div class="prow"><button onclick="cp(this)">📋 프롬프트 복사</button></div>
<code class="p">{html.escape(r['prompt_final'])}</code>
</div></article>''')
sub = (f'<span class="dyn">⚡ DYNAMIC {ndyn}컷</span> · 4-스킨(실사 {mix["실사"]}·디오라마 {mix["디오라마"]}·X-ray {mix.get("X-ray",0)}·청사진 {mix.get("청사진",0)}) · 위트 · 미모우선 · <b style="color:#e4685c">클립엔 숫자 없음(후처리 오버레이)</b> · <b style="color:#8fd06f">고증검증</b>. '
       f'훅=왕이 짓고도 안 산 이중나선의 거대한 성. 프롬프트 복사→t2v→슬롯 드롭.')
gallery = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    f'<title>샹보르 성 — 프롬프트 갤러리 (t2v)</title>{style}</head><body><div class="wrap">\n'
    f'<h1>샹보르 성 <span style="color:var(--cyan)">t2v</span> ({len(SHOTS)}컷 · {TOTAL}초 · 고증검증)</h1>\n'
    f'<p class="sub">{sub}</p>\n'
    '<div class="bar"><button class="save" onclick="saveFolder()">📁 images 폴더에 바로 저장</button>'
    '<button class="save" onclick="saveDownload()">⬇️ shotNN 전부 다운로드</button>'
    '<span class="barhint">저장 규칙 <code>images/shot01.mp4</code> · 다음에 열면 자동으로 불러옵니다</span></div>\n'
    '<div class="grid">' + ''.join(cards) + f'</div></div>{script}</body></html>')
open(os.path.join(HERE,'gallery.html'),'w',encoding='utf-8').write(gallery)
print(f"생성 완료: {len(SHOTS)}컷 · {TOTAL}초 · DYNAMIC {ndyn}컷 · 스킨 {dict(mix)}")
