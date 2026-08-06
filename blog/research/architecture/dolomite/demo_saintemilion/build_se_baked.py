#!/usr/bin/env python3
"""demo_saintemilion 빌더 — 대본/샷리스트(SHOTS) → manifest.json · gallery.html · prompts.txt · script.md.
   BAKED(숫자만): 치수·숫자·화살표는 t2v 프롬프트에 구워 AI가 화면에 직접 렌더. 한글은 TTS.
   갤러리 CSS/JS(영상 업로드·저장·자동로드·복사폴백)는 ../demo_montsaintmichel/gallery.html 재사용.
"""
import json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
REF  = os.path.join(HERE, '..', 'demo_montsaintmichel', 'gallery.html')

TOPIC = '생떼밀리옹 — 마을을 판 구멍이 지하교회·와인셀러가 되다 (Saint-Émilion)'

SUBJECT = ("Saint-Émilion — a medieval hilltop wine village in south-west France near Bordeaux, honey-coloured "
    "limestone houses and a tall bell tower on a plateau above rolling vineyards, sitting on top of a vast "
    "underground network of quarried limestone galleries; beneath the town is Europe's largest monolithic church "
    "carved entirely out of a single limestone rock, and the tunnels are now used as wine cellars.")

NUMS = "200 km, 80 ha, 4500 t, 15, 12C, 1"
STYLE_REAL = ("photorealistic cinematic drone footage with a subtle tilt-shift miniature feel, physically-based "
    "lighting, subtle film grain, muted desaturated cinematic color grade, vertical 9:16, south-west France "
    "Bordeaux wine-country setting, warm honey-limestone village and green vineyards under soft golden light. "
    "Presented with clean, crisp, legible rendered infographic annotations composited over the scene: thin red "
    "and cyan dimension lines with arrowheads and extension ticks, leader lines and rounded callout boxes, subtle "
    "documentary motion-graphics style. Any rendered labels contain ONLY numbers, units and magnitude suffixes "
    f"(e.g. {NUMS}), never words, sentences, captions or titles. no watermark.")
STYLE_DIORAMA = ("signature floating-diorama miniature cutaway: a rectangular slab of the limestone plateau and "
    "hilltop village cut out and floating in a dark graduated grey void, flat specimen cut-sides exposing pale "
    "limestone strata and the hollow quarried galleries beneath, a low angled key sun with soft fill light, faint "
    "volumetric haze and ambient occlusion, slow orbit with a portrait telephoto look and shallow depth of field, "
    "photorealistic miniature render, muted desaturated cinematic color grade, vertical 9:16. Presented as a clean "
    "engineering technical drawing with crisp, legible rendered annotations: thin cyan and red dimension lines with "
    "arrowheads and extension ticks, leader lines to rounded callout boxes, faint blueprint grid accents. Any "
    f"rendered labels contain ONLY numbers, units and magnitude suffixes (e.g. {NUMS}), never words, sentences, "
    "captions or titles. no watermark.")
DYN_REAL = "photorealistic cinematic footage, muted desaturated color grade, vertical 9:16, Bordeaux wine-country setting, no watermark."
DYN_DIORAMA = "signature floating-diorama miniature, dark graduated grey void, muted desaturated color grade, vertical 9:16, no watermark."

# role, cls(real|diorama), transition, dur, dyn, effect, kr, desc, camera, anno
SHOTS = [
 ('hook','real','cut',4,1,'지도→드론 다이브 줌', "프랑스 남서부, 보르도 동쪽 언덕 위 와인 마을입니다.",
   "DYNAMIC opening establisher: start on a clean minimal stylized map of France (soft grey landmass, no text labels of any kind) as a single glowing cyan location pin drops onto the Bordeaux region in the south-west; then a fast Google-Earth-style DIVE ZOOM plunges down out of the map through a thin cloud layer and resolves into a real cinematic drone view swooping fast over rolling green vineyards toward a honey-coloured limestone hilltop village crowned by a bell tower. no words anywhere.", "", ""),
 ('hook','real','cut',3,0,'', "예쁜 돌집 마을 같지만, 진짜 이야기는 발밑에 있습니다.",
   "a low golden drone glide skimming just over the honey-limestone rooftops and the tall bell tower of the village, then tilting downward toward the ground as if about to descend beneath it.",
   "a low glide over the rooftops then a downward tilt hinting at the world underground", ""),
 ('subject','real','cut',5,0,'', "생떼밀리옹. 이 마을 발밑엔 200km 지하 미로가 뚫려 있습니다.",
   "a majestic full 360-degree orbit sweeping right around the hilltop village at golden hour, honey-limestone walls and the bell tower glowing with warm rim-light, long shadows, vineyards spreading below.",
   "a slow cinematic full 360-degree orbit around the whole hilltop village, majestic, beautiful low golden-hour light", "a callout reading only 200 km (numbers only)"),
 ('cause','diorama','cut',3,0,'', "이 언덕은, 통째로 하나의 석회암 덩어리입니다.",
   "a floating diorama slab of the pale limestone plateau under the little village, homogeneous cream-coloured stone strata exposed on the clean cut sides, solid and massive.",
   "a slow orbit around the solid limestone slab", ""),
 ('cause','real','cut',4,0,'', "마을을 지을 돌을, 바로 발밑에서 캐냈습니다.",
   "an underground gallery lit by warm lamplight where workers cut and haul large pale limestone blocks, the same creamy stone that builds the village above, chisels and stacked blocks.",
   "a slow handheld move through the quarry gallery following a cut block", ""),
 ('cause','diorama','cut',6,0,'', "돌을 파낼수록, 지하엔 80헥타르 빈 공간이 남았죠.",
   "a dramatic clean vertical cross-section of the plateau: the little village and its bell tower sitting ON TOP, and directly beneath them a vast hollow honeycomb maze of quarried galleries eaten out of the same pale stone, the emptiness spreading wide under the town, crisp engineering-drawing clarity.",
   "a slow crane-down revealing the cross-section from the village on top down into the vast hollow galleries below", "a callout 80 ha on the hollow void and a total reading 200 km (numbers only)"),
 ('flip','diorama','cut',5,1,'바위 카브다운 + 360° 오빗', "그 구멍을 메우기는커녕 — 하나의 바위를 위에서 파내려가, 유럽 최대 지하 교회를 만들었습니다.",
   "HIGH-ENERGY: a single massive block of pale limestone CARVES OPEN from the top downward, columns, arches and a great vaulted nave rapidly hollowing out of the solid rock to form a huge underground church all cut from ONE rock; glowing cyan wireframe snaps to stone, hard punch-in, then a fast full 360-degree orbit around the carved cavern-church.", "", ""),
 ('scale','real','cut',5,0,'', "종탑은 땅 위에, 본당은 통째로 땅 밑에. 돌 하나를 파낸 겁니다.",
   "a clean cutaway showing the tall stone bell tower standing on the surface directly above the enormous vaulted church carved into the rock below, one continuous piece of pale limestone, tiny figures for scale inside the underground nave.",
   "a slow vertical truck linking the surface bell tower down to the underground nave in one move", "a callout 1 on the single rock and a vertical leader line from the bell tower down to the church (numbers only)"),
 ('solution','real','cut',5,1,'셀러로 하강 다이브', "그리고 남은 빈 공간은, 와인 저장고가 됐습니다.",
   "DYNAMIC continuous descent: the camera drops from a gallery mouth and DIVES down into a candle-lit limestone tunnel lined on both sides with oak wine barrels and dusty bottles aging in the pale stone, cool and still, motes of dust in the light beams.", "", ""),
 ('solution','real','cont',4,0,'', "빛도 진동도 없고, 일 년 내내 서늘하고 축축하죠. 완벽한 조건입니다.",
   "an intimate shot deep inside the barrel-lined limestone cellar, no daylight, glassy still air, faint condensation on the pale walls, rows of bottles under soft lamplight.",
   "a slow reveal gliding along the rows of aging barrels and bottles", "cyan markers indicating constant low temperature and high humidity (no text)"),
 ('fail','diorama','cut',4,0,'', "그런데 위가 무거우면, 아래 빈 공간이 짓눌립니다. 종탑만 4500톤.",
   "a floating cross-section: the heavy stone bell tower on top pressing straight down with bold red load arrows into the hollow galleries beneath, the thin rock roof of the caverns starting to strain, a sense of dangerous weight over emptiness.",
   "a slow push-in onto the pressing weight over the void", "a bold red load arrow reading 4500 t pressing down onto the hollow galleries (numbers only)"),
 ('fail','diorama','cut',6,0,'', "기둥을 세워 떠받쳤지만, 천장에 균열. 범인은 무게가 아니라 — 스며든 지하수였죠.",
   "a floating cross-section: extra stone support pillars are added holding up the cavern roof, yet fine cracks still spread across the vault; then a reveal of blue water seeping down through the pale limestone along the cracks as the true culprit, glowing blue infiltration lines tracing the water path.",
   "a slow lateral truck across the cracked vault, then a push-in following the blue water seeping in", "a red X over the weight arrow and blue water-infiltration lines running to the cracks (no text)"),
 ('solution','real','cut',4,0,'', "그래서 15개월간 문을 닫고, 물길을 잡고 보강했습니다.",
   "restoration work inside the underground church, scaffolding and drainage channels being installed, workers reinforcing the pale stone vault, careful and technical, work lamps.",
   "a slow overhead tracking move across the restoration work", "a callout reading only 15 (numbers only)"),
 ('scale','diorama','cut',5,0,'', "마을을 판 그 구멍이 — 교회가 되고, 와인을 익힙니다.",
   "the full money cross-section, complete and clean: the village and bell tower on top, and beneath, the great carved church and the barrel-lined wine cellars filling the hollow galleries, all one continuous pale limestone body, the church zone and cellar zone gently colour-coded.",
   "a slow orbit around the complete top-to-bottom cross-section", "a summary strip reading only 200 km   80 ha (numerals and units only, no words)"),
 ('end','real','cut',6,1,'지하 와인→지상 종탑 클라임→골든아워', "땅속 와인부터 하늘의 종탑까지, 모두 같은 돌 하나입니다.",
   "DYNAMIC finale: start deep in the candle-lit wine cellar, the camera CLIMBS fast UP through the pale rock, sweeping up past the vaulted underground church, then BURSTS up out of the ground beside the bell tower and CRANES up into a golden-hour sky over the hilltop village and vineyards — a rising underground-to-sky transition; a small summary strip reads only 200 km 80 ha (numerals and units only).", "", ""),
]

CLS_KO   = {'real':'실사', 'diorama':'디오라마'}
CLS_STYLE= {'real':'color:#8fd06f;border-color:#8fd06f55', 'diorama':'color:#3fb6c4;border-color:#3fb6c455'}

def prompt_final(role,cls,tr,dur,dyn,eff,kr,desc,cam,anno):
    if dyn:
        base = DYN_REAL if cls=='real' else DYN_DIORAMA
        return f"{base} {desc} One continuous ~{dur}-second shot."
    base = STYLE_REAL if cls=='real' else STYLE_DIORAMA
    p = f"{base} {desc}"
    if anno: p += f" Rendered numeric annotations in the image: {anno}."
    p += f" SUBJECT: {SUBJECT} Camera: {cam} One continuous ~{dur}-second shot."
    return p

t=0; rows=[]
for i,s in enumerate(SHOTS):
    role,cls,tr,dur,dyn,eff,kr,desc,cam,anno = s
    rows.append({'id':i+1,'role':role,'style_class':CLS_KO[cls],'transition':tr,'t':t,'dur':dur,
                 'dynamic':bool(dyn),'effect':eff,'sentence_kr':kr,'desc':desc,'camera':cam,
                 'anno_rendered':anno,'prompt_final':prompt_final(*s)})
    t += dur
TOTAL=t

manifest = {
 'topic':TOPIC,
 'mode':'baked-numbersonly(AI-rendered numeric annotations, no captions)',
 'filter_score':{'대중인지도':2,'외관vs기능반전':2,'문제선명도':2,'뻔한해법실패':1,'반직관해결':2,
                 '작동과정명확성':2,'시각화가능성':2,'강한숫자':2,'공식자료충분':2,'현재성결말':2,
                 '총점':19,'판정':'즉시 제작 후보(17~20)'},
 'candidate_sentences_hit':['골칫거리(구멍)를 없애지 않고 그대로 이용했다',
                            '장애물(빈 공간)을 재료·자산으로 바꿨다',
                            '지상 구조보다 지하에 숨은 구조가 더 크다',
                            '겉은 마을, 속은 텅 빈 벌집',
                            '진짜 원인은 무게가 아니라 물이었다(오답 태우기)'],
 'fact_pack':{'교회':'유럽 최대 모놀리식(단일암) 지하 교회, 하나의 석회암을 위에서 파 조성, 12세기 초',
   '지하갤러리':'약 80헥타르, 누적 약 200km 미로. 19세기까지 채석해 마을·리부른·보르도 일부 건설',
   '붕괴위험':'종탑 약 4500톤이 균열 원인으로 지목됐으나, 실제 원인은 지하수 침투. 안전상 카메라만 투입 조사',
   '보수':'금 발견으로 교회 약 15개월 폐쇄·보강',
   '와인셀러':'지하 공동을 셀러로 사용 — 무광·항온·고습·무진동 이상적 숙성 조건',
   '출처':'connexionfrance.com, bordeaux-tourism.co.uk, decanterchina.com(Anson)'},
 'note':'BAKED(숫자만): 숫자·치수선·화살표만 프롬프트에 구워 AI가 이미지에 직접 렌더. 단어 라벨/한글 자막 없음. 한글=TTS. 훅=마을을 판 구멍이 지하교회·와인셀러가 됐다 + 붕괴 오답(무게→실은 지하수).',
 'style_base':STYLE_REAL,'style_base_diorama':STYLE_DIORAMA,'subject':SUBJECT,
 'shots':rows,
}
json.dump(manifest, open(os.path.join(HERE,'manifest.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)

with open(os.path.join(HERE,'prompts.txt'),'w',encoding='utf-8') as f:
    f.write(f"# {TOPIC}\n# BAKED(숫자만) · {len(SHOTS)}컷 · {TOTAL}초\n\n")
    for r in rows:
        f.write(f"── #{r['id']:02d} {r['role']} · {r['t']}s→{r['t']+r['dur']}s · {r['style_class']}"
                + (f" · ⚡{r['effect']}" if r['dynamic'] else "") + "\n")
        f.write(f"  나레이션: {r['sentence_kr']}\n")
        if r['anno_rendered']: f.write(f"  숫자그래픽: {r['anno_rendered']}\n")
        f.write(f"  프롬프트: {r['prompt_final']}\n\n")
with open(os.path.join(HERE,'script.md'),'w',encoding='utf-8') as f:
    f.write(f"# {TOPIC} — 대본\n\n**전체 나레이션**\n\n")
    f.write(' '.join(r['sentence_kr'] for r in rows) + "\n\n**컷 표**\n\n| # | 구간 | 길이 | 스타일 | 나레이션 |\n|---|---|---|---|---|\n")
    for r in rows:
        f.write(f"| {r['id']} | {r['t']}s→{r['t']+r['dur']}s | {r['dur']}s | {r['style_class']}"
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
    elif r['anno_rendered']: ovlabel, ovbody = '렌더 숫자그래픽', html.escape(r['anno_rendered'])
    else: ovlabel, ovbody = '렌더 숫자그래픽', '<i style="color:#4a515b">—</i>'
    clsstyle = CLS_STYLE['real' if r['style_class']=='실사' else 'diorama']
    t0,t1 = r['t'], r['t']+r['dur']
    cards.append(
f'''<article class="c{dyncls}">
<div class="slot empty{dyncls}"><div class="ph">#{r['id']:02d} · {r['role']} · {t0}s→{t1}s<br><span>{ph2}</span></div><input type="file" accept="video/*,image/*" onchange="drop(this)"><img></div>
<div class="meta">
<div class="hd"><b>{r['id']:02d}</b> <span class="role">{r['role']}</span> <span class="tr">{r['transition']}</span>
 <span class="cls" style="{clsstyle}">{r['style_class']}</span> {dynspan} <span class="dur">{t0}s→{t1}s</span></div>
<p class="kr">{html.escape(r['sentence_kr'])}</p>
<div class="ov"><b>{ovlabel}</b><br>{ovbody}</div>
<div class="prow"><button onclick="cp(this)">📋 프롬프트 복사</button></div>
<code class="p">{html.escape(r['prompt_final'])}</code>
</div></article>''')
sub = (f'<span class="dyn">⚡ DYNAMIC {ndyn}컷</span> + BAKED(숫자만). 훅=마을을 판 구멍이 지하교회·와인셀러가 되다. '
       f'프롬프트 복사→t2v(Veo/Kling)→슬롯 드롭. 영상 저장→images/shotNN.mp4 자동 로드.')
gallery = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    f'<title>생떼밀리옹 — 프롬프트 갤러리 (t2v)</title>{style}</head><body><div class="wrap">\n'
    f'<h1>생떼밀리옹 <span style="color:var(--cyan)">t2v</span> ({len(SHOTS)}컷 · {TOTAL}초)</h1>\n'
    f'<p class="sub">{sub}</p>\n'
    '<div class="bar"><button class="save" onclick="saveFolder()">📁 images 폴더에 바로 저장</button>'
    '<button class="save" onclick="saveDownload()">⬇️ shotNN 전부 다운로드</button>'
    '<span class="barhint">저장 규칙 <code>images/shot01.mp4</code> · 다음에 열면 자동으로 불러옵니다</span></div>\n'
    '<div class="grid">' + ''.join(cards) + f'</div></div>{script}</body></html>')
open(os.path.join(HERE,'gallery.html'),'w',encoding='utf-8').write(gallery)
print(f"생성 완료: {len(SHOTS)}컷 · {TOTAL}초 · DYNAMIC {ndyn}컷")
print("  manifest.json · prompts.txt · script.md · gallery.html")
