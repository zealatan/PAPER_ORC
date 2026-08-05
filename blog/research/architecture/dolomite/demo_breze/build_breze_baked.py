#!/usr/bin/env python3
"""demo_breze 빌더 — 브레제 성 '성 밑의 성'. 4-스킨 비주얼 문법 + 위트/대화체 톤.
   스킨 역할: real=실제세계·현장·감정 / diorama=따뜻한 부유 디오라마(물리 구조·단면·스케일, 시그니처)
             / xray=내부를 꿰뚫어 볼 때 / blueprint=발상·설계가 현실이 되는 순간.
   BAKED(숫자만): 숫자·치수선·화살표만 프롬프트에 구워 AI가 화면에 직접 렌더. 한글=TTS.
   갤러리 CSS/JS(업로드·저장·자동로드·복사폴백)는 ../demo_montsaintmichel/gallery.html 재사용.
"""
import json, os, re, html
HERE = os.path.dirname(os.path.abspath(__file__))
REF  = os.path.join(HERE, '..', 'demo_montsaintmichel', 'gallery.html')

TOPIC = '브레제 성 — 성 밑의 성 (Château de Brézé, 유럽 최심 해자·지하 요새)'
NUMS = "18 m, 1.5 km, 1 km, 9 m, 1448, 3x"
SUBJECT = ("Château de Brézé — an elegant pale tuffeau-limestone Renaissance château in the Loire Valley of France, "
    "ringed by the deepest dry moats in Europe (about 18 metres deep) and standing above a vast hidden underground "
    "fortress of galleries, rooms and defensive passages carved into the soft limestone bedrock — a 'château "
    "beneath the château' — surrounded by vineyards.")

_ANNO = f"Any rendered labels contain ONLY numbers, units and magnitude suffixes (e.g. {NUMS}), never words, sentences, captions or titles. no watermark."
STYLE_REAL = ("photorealistic cinematic drone footage with a subtle tilt-shift miniature feel, physically-based "
    "lighting, subtle film grain, warm cinematic color grade, vertical 9:16, Loire Valley France setting, an "
    "elegant pale tuffeau-limestone Renaissance château ringed by deep dry moats and vineyards under warm golden "
    "light. Presented with clean rendered infographic annotations composited over the scene: thin red and cyan "
    f"dimension lines with arrowheads and extension ticks, leader lines and rounded callout boxes. {_ANNO}")
STYLE_DIORAMA = ("signature floating-diorama miniature cutaway: a rectangular slab of the château and the rock "
    "beneath it cut out and floating in a WARM graduated amber-to-charcoal void, flat specimen cut-sides exposing "
    "pale tuffeau limestone strata and the hollow underground galleries, lit by a warm low amber key light with "
    "soft golden fill and gentle rim glow, faint volumetric haze and ambient occlusion, portrait telephoto look "
    "with shallow depth of field, photorealistic miniature render, warm cinematic color grade, vertical 9:16. "
    "Presented as a clean engineering technical drawing with crisp legible rendered annotations: thin cyan and "
    f"warm-amber dimension lines with arrowheads and extension ticks, leader lines to rounded callout boxes. {_ANNO}")
STYLE_XRAY = ("see-through x-ray / technical scan visualization, deep graduated navy-black void background, the "
    "château and everything beneath it rendered as a glowing translucent cyan wireframe with x-ray interior layers "
    "revealing the underground galleries, rooms and passages hidden below ground, a soft horizontal scan-line "
    "sweeping through, holographic engineering feel, physically-based glow, subtle film grain, muted palette with "
    f"cyan and red accents, vertical 9:16. {_ANNO}")
STYLE_BLUEPRINT = ("an engineering blueprint that morphs into photoreal reality, vertical 9:16. The shot BEGINS as a "
    "clean technical blueprint — crisp cyan and white line drawing on deep blueprint-blue paper with a faint grid, "
    "dimension lines and rounded callout boxes — then a bright wipe sweeps across and the blueprint MORPHS and "
    "fills into a photorealistic build with real pale stone and physically-based light, subtle film grain, warm "
    f"grade; the numeric annotations live in the blueprint layer and fade as the real build resolves. {_ANNO}")
DYN_REAL = "photorealistic cinematic footage, warm color grade, vertical 9:16, Loire Valley France setting, no watermark."
DYN_DIORAMA = "signature floating-diorama miniature, warm graduated amber-charcoal void, warm cinematic color grade, vertical 9:16, no watermark."
DYN_XRAY = "see-through x-ray / scan visualization, deep navy-black void, glowing translucent cyan wireframe revealing hidden underground structure, scan-line sweep, vertical 9:16, no watermark."
DYN_BLUEPRINT = "engineering blueprint morphing into photoreal reality, blueprint-blue paper with grid, cyan line-drawing wiping into real pale stone, vertical 9:16, no watermark."
BASE  = {'real':STYLE_REAL,'diorama':STYLE_DIORAMA,'xray':STYLE_XRAY,'blueprint':STYLE_BLUEPRINT}
DBASE = {'real':DYN_REAL,'diorama':DYN_DIORAMA,'xray':DYN_XRAY,'blueprint':DYN_BLUEPRINT}
CLS_KO   = {'real':'실사','diorama':'디오라마','xray':'X-ray','blueprint':'청사진'}
CLS_STYLE= {'real':'color:#8fd06f;border-color:#8fd06f55','diorama':'color:#e8a33d;border-color:#e8a33d55',
            'xray':'color:#5bd0ff;border-color:#5bd0ff55','blueprint':'color:#7aa2ff;border-color:#7aa2ff55'}

# role, cls, transition, dur, dyn, effect, kr, desc, camera, anno
SHOTS = [
 ('hook','real','cut',4,1,'지도→드론 다이브 줌', "프랑스 루아르 밸리, 포도밭 한복판. 우아한 르네상스 성이 서 있습니다.",
   "DYNAMIC opening: start on a clean minimal stylized map of France (soft grey landmass, no text labels) as a glowing cyan location pin drops onto the Loire Valley; then a fast Google-Earth-style DIVE ZOOM plunges down through a thin cloud layer into a real cinematic drone view swooping over vineyards toward an elegant pale-stone Renaissance château ringed by deep dry moats. no words anywhere.", "", ""),
 ('hook','real','cut',3,0,'', "그림 같죠? 근데 이 성, 진짜배기는 발밑에 숨어 있습니다.",
   "a low warm drone glide skimming over the elegant château's pale facades and slate roofs, then tilting downward toward the ground and the deep dry moat as if about to descend beneath it.",
   "a low glide over the château then a downward tilt hinting at the world underground", ""),
 ('subject','real','cut',5,0,'', "브레제 성. 별명이 아예 '성 밑의 성'이에요.",
   "a majestic full 360-degree orbit sweeping right around the château at golden hour, pale tuffeau walls and towers glowing with warm rim-light, the deep dry moat wrapping the base, vineyards spreading beyond.",
   "a slow cinematic full 360-degree orbit around the whole château, beautiful golden-hour light", ""),
 ('subject','real','cut',4,0,'', "먼저 이 해자. 성을 빙 두른 마른 도랑인데 — 이게 유럽에서 제일 깊습니다.",
   "a dramatic aerial that drops straight down into the vast dry stone moat encircling the château, sheer pale limestone walls towering on both sides, tiny visitors far below for scale.",
   "a fast vertical drone descent (ZOOM DOWN) plunging into the deep dry moat", "a red vertical dimension line reading 18 m down the moat wall (numbers only)"),
 ('scale','diorama','cut',5,0,'', "보통 성 해자는 3에서 6미터. 근데 브레제는 무려 18미터, 세 배가 넘죠.",
   "a warm floating-diorama cross-section slab of the château and its dry moat, the deep moat cut about three times deeper than a faint ghost outline of a typical shallow moat placed beside it for comparison, pale limestone strata on the cut faces.",
   "a slow orbit around the cross-section comparing the deep moat to a typical shallow one", "a red dimension line reading 18 m on the deep moat, a faint ghost outline marked 3–6 m, and a callout 3x (numbers only)"),
 ('cause','blueprint','cut',4,0,'', "비결은 이 땅이에요. 무른 석회암이라, 파고 또 파기 딱 좋았거든요.",
   "a blueprint section of the soft tuffeau limestone bedrock that morphs into real carved stone, chisels cutting easily into the pale rock and blocks being removed, showing how readily the ground could be dug.",
   "a slow push-in as the blueprint of the bedrock wipes into real carved stone", "cyan hatching marking the soft limestone layer (numbers only)"),
 ('flip','xray','cut',6,1,'지하 성 스캔 리빌', "그렇게 파 내려간 지하에는 — 지상 성보다 더 거대한 '지하 성'이 통째로 들어앉았습니다. 길이만 1.5km.",
   "DYNAMIC x-ray reveal: the elegant château above turns translucent as a bright scan-line sweeps DOWNWARD through the ground, revealing beneath it a vast glowing cyan wireframe network of underground galleries, rooms and passages far larger than the château above — an entire hidden fortress under the castle; the camera cranes down into the revealed network as a bold 1.5 km counter lights up.", "", ""),
 ('solution','diorama','cut',5,0,'', "땅속 9미터에 마구간·주방은 기본. 빵 굽는 제빵소에, 누에 키우는 방까지 있었어요.",
   "a warm floating-diorama cutaway of the underground level about 9 metres down, little rooms carved into the pale limestone — stables, a kitchen, a bakery with a domed oven, and a silkworm-rearing room — warm lamplight and tiny figures at work.",
   "a slow orbit across the row of carved underground rooms", "a depth dimension line reading 9 m and small numeric callouts on the rooms (numbers only)"),
 ('scale','diorama','cut',4,0,'', "게다가 이 와인 압착실은, 프랑스에서 손꼽는 크기랍니다.",
   "a warm floating-diorama cutaway of an enormous underground wine-press hall carved in pale stone, a giant old wooden press dwarfing tiny figures, oak barrels stacked in the adjacent galleries.",
   "a slow push-in on the giant underground wine press", "a bracket callout on the huge press hall (numbers only)"),
 ('solution','xray','cut',5,0,'', "1km 넘는 방어 통로에, 공성 때 귀족이 숨어 살던 지하 거처까지. 완벽한 지하 요새였죠.",
   "an x-ray see-through of the château and its moat revealing the long defensive galleries snaking over a kilometre through the rock, plus elegant carved underground apartments where the nobility could live during a siege, all as glowing translucent cyan wireframe.",
   "a slow x-ray glide following the defensive galleries deep through the rock", "a length callout reading 1 km on the galleries (numbers only)"),
 ('solution','blueprint','cut',5,1,'도개교·방어 작동 모프', "적이 쳐들어오면? 다리를 걷어 올리고, 18미터 절벽 해자 앞에서 그냥 막혀버립니다.",
   "DYNAMIC blueprint-to-real: a technical blueprint of the drawbridge over the deep dry moat draws itself, then MORPHS to real as the bridge lifts and an attacker is stopped dead at the edge of the sheer 18-metre moat wall; the defensive galleries glow to life below.", "", ""),
 ('fail','real','cut',5,0,'', "근데 반전. 이렇게 철벽으로 지어놨는데, 브레제 성은 역사상 단 한 번도 공격받은 적이 없어요. 그 방어터널, 실전에선 한 번도 못 써봤죠.",
   "a serene wide golden-hour drone shot of the peaceful, untouched château and its empty deep moat, calm vineyards all around, an air of gentle irony that nothing ever attacked this perfect fortress.",
   "a slow calm orbit over the peaceful never-besieged château", ""),
 ('solution','real','cont',4,0,'', "대신 그 서늘한 지하는 지금, 최고의 와인 저장고가 됐습니다.",
   "inside the cool underground stone cellars today, long rows of oak barrels and dusty bottles of Loire wine aging in the pale limestone galleries, soft lamplight and drifting dust motes.",
   "a slow reveal gliding along the barrels aging deep underground", ""),
 ('scale','diorama','cut',5,0,'', "위는 우아한 성, 아래는 숨은 요새. 돌덩이 하나에, 성이 둘인 셈이죠.",
   "the full warm floating-diorama money cross-section, complete: the elegant Renaissance château on top and directly beneath it the vast underground fortress of galleries, rooms and cellars filling the rock — one continuous limestone body holding two castles, the upper château and the lower fortress gently distinguished.",
   "a slow orbit around the complete top-and-bottom cross-section", "a summary strip reading only 18 m   1.5 km (numerals and units only, no words)"),
 ('end','real','cut',6,1,'지하→지상 클라임→골든아워', "성 밑의 성, 브레제. 진짜 이야기는 늘, 발밑에 있었습니다.",
   "DYNAMIC finale: start deep in the underground wine cellars, the camera CLIMBS fast UP through the pale rock past the galleries, BURSTS up out of the ground into the château courtyard and CRANES up into a golden-hour sky over the château and vineyards — a rising underground-to-sky transition; a small summary strip reads only 18 m 1.5 km (numerals and units only).", "", ""),
]

# 클립이 앞뒤 컷과 매끄럽게 이어지도록 하는 연속-무빙 지시(모든 컷 공통)
CONT = (" The shot begins and ends on smooth, continuous camera motion with no abrupt start, freeze or hard stop, "
        "gentle easing, so it blends seamlessly into the neighbouring shots.")
def prompt_final(role,cls,tr,dur,dyn,eff,kr,desc,cam,anno):
    if dyn:
        return f"{DBASE[cls]} {desc} One continuous ~{dur}-second shot.{CONT}"
    p = f"{BASE[cls]} {desc}"
    if anno: p += f" Rendered numeric annotations in the image: {anno}."
    p += f" SUBJECT: {SUBJECT} Camera: {cam} One continuous ~{dur}-second shot.{CONT}"
    return p

t=0; rows=[]
for i,s in enumerate(SHOTS):
    role,cls,tr,dur,dyn,eff,kr,desc,cam,anno = s
    rows.append({'id':i+1,'role':role,'cls':cls,'style_class':CLS_KO[cls],'transition':tr,'t':t,'dur':dur,
                 'dynamic':bool(dyn),'effect':eff,'sentence_kr':kr,'desc':desc,'camera':cam,
                 'anno_rendered':anno,'prompt_final':prompt_final(*s)})
    t += dur
TOTAL=t

manifest = {
 'topic':TOPIC,
 'mode':'baked-numbersonly(AI-rendered numeric annotations, no captions) · 4-skin(real/diorama-warm/xray/blueprint) · witty tone',
 'filter_score':{'대중인지도':1,'외관vs기능반전':2,'문제선명도':2,'뻔한해법실패':1,'반직관해결':2,
                 '작동과정명확성':2,'시각화가능성':2,'강한숫자':2,'공식자료충분':2,'현재성결말':2,
                 '총점':18,'판정':'즉시 제작 후보(17~20)'},
 'candidate_sentences_hit':['지상 구조보다 지하에 숨은 구조가 더 크다','겉은 우아한 성, 속은 지하 요새',
                            '골칫거리 대신 자연(무른 석회암)을 재료로','철벽을 지었지만 한 번도 안 쓰였다(오답/아이러니)'],
 'fact_pack':{'해자':'유럽 최심 건식 해자 약 18m(일반 3~6m의 3배+). 1448~15C 채굴, 16C 확장',
   '지하요새':'"château sous le château"(성 밑의 성). 지하 갤러리 약 1.5km(관람 약 1km), 깊이 9m',
   '지하시설':'마구간·주방(중세), 17C 지하 제빵소·누에방(magnanerie), 배럴 저장고, 프랑스 최대급 와인 압착실, 1km+ 방어 갤러리, 공성용 귀족 지하 거처, 채광정(light wells)',
   '방어':'무른 tuffeau 석회암에 굴착. 방어 완비했으나 역사상 한 번도 공격받지 않아 실전 미검증',
   '현재':'지금도 지하에서 Saumur 와인 숙성·생산(Vignobles Colbert)',
   '출처':'chateaudebreze.com, france.fr, journee-mondiale.com, ancient-origins.net'},
 'note':'4-스킨 비주얼 문법: real=현장/감정, diorama(warm)=구조·단면·스케일(시그니처), xray=내부 투시, blueprint=발상→실물. 위트/대화체 톤. 한글=TTS, 숫자만 baked.',
 'style_base':STYLE_REAL,'style_base_diorama':STYLE_DIORAMA,'style_base_xray':STYLE_XRAY,'style_base_blueprint':STYLE_BLUEPRINT,
 'subject':SUBJECT,'shots':rows,
}
json.dump(manifest, open(os.path.join(HERE,'manifest.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)

with open(os.path.join(HERE,'prompts.txt'),'w',encoding='utf-8') as f:
    f.write(f"# {TOPIC}\n# 4-스킨 · BAKED(숫자만) · 위트톤 · {len(SHOTS)}컷 · {TOTAL}초\n\n")
    for r in rows:
        f.write(f"── #{r['id']:02d} {r['role']} · {r['t']}s→{r['t']+r['dur']}s · [{r['style_class']}]"
                + (f" · ⚡{r['effect']}" if r['dynamic'] else "") + "\n")
        f.write(f"  나레이션: {r['sentence_kr']}\n")
        if r['anno_rendered']: f.write(f"  숫자그래픽: {r['anno_rendered']}\n")
        f.write(f"  프롬프트: {r['prompt_final']}\n\n")
with open(os.path.join(HERE,'script.md'),'w',encoding='utf-8') as f:
    f.write(f"# {TOPIC} — 대본 (위트/대화체)\n\n**전체 나레이션**\n\n")
    f.write(' '.join(r['sentence_kr'] for r in rows) + "\n\n**컷 표 (스킨)**\n\n| # | 구간 | 스킨 | 나레이션 |\n|---|---|---|---|\n")
    for r in rows:
        f.write(f"| {r['id']} | {r['t']}s→{r['t']+r['dur']}s | {r['style_class']}"
                + (f"·⚡{r['effect']}" if r['dynamic'] else "") + f" | {r['sentence_kr']} |\n")

ref = open(REF, encoding='utf-8').read()
style = re.search(r'<style>.*?</style>', ref, re.S).group(0)
script = re.search(r'<script>.*?</script>', ref, re.S).group(0)
ndyn = sum(1 for r in rows if r['dynamic'])
from collections import Counter
mix = Counter(r['style_class'] for r in rows)
cards=[]
for r in rows:
    dyncls = ' dyn' if r['dynamic'] else ' '
    ph2 = '⚡DYNAMIC · 프롬프트→드롭' if r['dynamic'] else '프롬프트→드롭'
    dynspan = f'<span class="dyn">⚡ {html.escape(r["effect"])}</span>' if r['dynamic'] else ''
    if r['dynamic']: ovlabel, ovbody = '카메라/효과', html.escape(r['effect'])
    elif r['anno_rendered']: ovlabel, ovbody = '렌더 숫자그래픽', html.escape(r['anno_rendered'])
    else: ovlabel, ovbody = '렌더 숫자그래픽', '<i style="color:#4a515b">—</i>'
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
sub = (f'<span class="dyn">⚡ DYNAMIC {ndyn}컷</span> · 4-스킨 문법(실사 {mix["실사"]} · 디오라마 {mix["디오라마"]} · X-ray {mix["X-ray"]} · 청사진 {mix["청사진"]}) · 위트톤. '
       f'훅=성 밑의 성. 프롬프트 복사→t2v→슬롯 드롭. 영상 저장→images/shotNN.mp4 자동 로드.')
gallery = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    f'<title>브레제 성 — 프롬프트 갤러리 (t2v)</title>{style}</head><body><div class="wrap">\n'
    f'<h1>브레제 성 <span style="color:var(--cyan)">t2v</span> ({len(SHOTS)}컷 · {TOTAL}초 · 4-스킨)</h1>\n'
    f'<p class="sub">{sub}</p>\n'
    '<div class="bar"><button class="save" onclick="saveFolder()">📁 images 폴더에 바로 저장</button>'
    '<button class="save" onclick="saveDownload()">⬇️ shotNN 전부 다운로드</button>'
    '<span class="barhint">저장 규칙 <code>images/shot01.mp4</code> · 다음에 열면 자동으로 불러옵니다</span></div>\n'
    '<div class="grid">' + ''.join(cards) + f'</div></div>{script}</body></html>')
open(os.path.join(HERE,'gallery.html'),'w',encoding='utf-8').write(gallery)
print(f"생성 완료: {len(SHOTS)}컷 · {TOTAL}초 · DYNAMIC {ndyn}컷 · 스킨 {dict(mix)}")
