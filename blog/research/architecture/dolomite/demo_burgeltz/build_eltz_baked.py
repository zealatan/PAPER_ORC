#!/usr/bin/env python3
"""demo_burgeltz 빌더 — 대본/샷리스트(SHOTS) → manifest.json · gallery.html · prompts.txt · script.md 자동생성.
   BAKED(숫자만): 치수·숫자·화살표는 t2v 프롬프트에 구워 AI가 화면에 직접 렌더. 한글은 TTS 나레이션.
   갤러리 CSS/JS(영상 업로드·저장·자동불러오기)는 ../demo_montsaintmichel/gallery.html 에서 재사용.
   수정→재실행하면 전부 재생성. (rec/ 렌더 파이프라인은 별도 복사)
"""
import json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
REF  = os.path.join(HERE, '..', 'demo_montsaintmichel', 'gallery.html')  # CSS/JS 재사용 소스

TOPIC = '엘츠 성 — 세 가문의 수직 공동주택 (Burg Eltz, Ganerbenburg)'

SUBJECT = ("Burg Eltz — a medieval German castle: a tight cluster of about eight tall stone residential "
    "towers up to eight storeys high with steep grey slate roofs and half-timbered upper floors, packed "
    "closely together on a narrow 70-metre-high rock spur in a deep forested valley, encircled on three "
    "sides by the small Elzbach river, Eifel region near the Moselle.")

NUMS = "70 m, 8, 35 m, 100, 861 yr, 34, 1157, 1268, 1331"
STYLE_REAL = ("photorealistic cinematic drone footage with a subtle tilt-shift miniature feel, physically-based "
    "lighting, subtle film grain, muted desaturated cinematic color grade, vertical 9:16, German Eifel/Moselle "
    "forested valley setting, soft silver overcast daylight, deep green forest and grey slate stone palette. "
    "Presented with clean, crisp, legible rendered infographic annotations composited over the scene: thin red "
    "and cyan dimension lines with arrowheads and extension ticks, leader lines and rounded callout boxes, subtle "
    "documentary motion-graphics style. Any rendered labels contain ONLY numbers, units and magnitude suffixes "
    f"(e.g. {NUMS}), never words, sentences, captions or titles. no watermark.")
STYLE_DIORAMA = ("signature floating-diorama miniature cutaway: a rectangular slab of the forested rock spur and "
    "castle cut out and floating in a dark graduated grey void, flat specimen cut-sides exposing rock strata and "
    "foundation layers, a low angled key sun with soft fill light, faint volumetric haze and ambient occlusion, "
    "slow orbit with a portrait telephoto look and shallow depth of field, photorealistic miniature render, muted "
    "desaturated cinematic color grade, vertical 9:16. Presented as a clean engineering technical drawing with "
    "crisp, legible rendered annotations: thin cyan and red dimension lines with arrowheads and extension ticks, "
    "leader lines to rounded callout boxes, faint blueprint grid accents. Any rendered labels contain ONLY numbers, "
    f"units and magnitude suffixes (e.g. {NUMS}), never words, sentences, captions or titles. no watermark.")
DYN_REAL = ("photorealistic cinematic footage, muted desaturated color grade, vertical 9:16, German Eifel forested "
    "valley setting, no watermark.")
DYN_DIORAMA = "signature floating-diorama miniature, dark graduated grey void, muted desaturated color grade, vertical 9:16, no watermark."

# id, role, cls(real|diorama), transition, dur, dyn, effect, kr, desc, camera, anno
SHOTS = [
 (1,'hook','real','cut',5,0,'', "숲 속 바위 위에, 탑 여덟 개가 다닥다닥 붙은 성. 동화 같지만, 이건 한 사람의 성이 아닙니다.",
   "a low forest dawn shot rising through misty trees toward a distant cluster of tall stone towers crowded on a rock spur, then a smooth crane-up revealing the whole huddle of eight towers packed on the narrow rock above a river bend, fairy-tale silhouette, moody silver-green light.",
   "a slow drift rising through the mist then craning up to reveal the full tower cluster on the spur", ""),
 (3,'subject','real','cut',4,0,'', "독일 엘츠 성. 세 가문이 한 성에 함께 산, 중세의 공동주택입니다.",
   "a dramatic hero shot of Burg Eltz seen from across the valley, the dense stack of towers and gabled houses rising straight out of the wooded rock, river far below.",
   "a slow graceful orbit around the castle cluster, majestic and unhurried", ""),
 (4,'subject','real','cut',4,0,'', "왜 한 지붕 아래 세 집이 모여 살았을까요?",
   "a clean straight-down top-down aerial over the tightly packed roofs and tiny courtyards of the castle, showing many separate houses squeezed onto one small rock.",
   "a slow overhead descent toward the packed rooftops", "thin cyan brackets grouping three clustered roof blocks and a callout 3 (no words)"),
 (5,'cause','diorama','cut',5,0,'', "1268년, 삼형제가 성을 물려받아 셋으로 나눕니다. 세 집안, 각자 살 곳이 필요했죠.",
   "floating diorama of the single rock-top castle as a glowing cyan line splits its plan into three coloured ownership zones — one castle divided among three families who each need their own home.",
   "a slow orbit as the castle plan divides into three coloured zones", "a bold 1268 marker, three coloured zones split by a cyan line, and a callout 3 (numbers only)"),
 (6,'scale','real','cut',4,0,'', "그런데 성터는, 세 면이 강에 감긴 70미터 바위 하나뿐이었습니다.",
   "a sweeping aerial circling the tall narrow rock spur, the Elzbach river looping around three sides far below, sheer wooded cliffs dropping to the water.",
   "a dramatic orbit around the 70 m spur showing the river wrapping three sides", "a red vertical dimension line on the rock reading 70 m, cyan arrows on the river with a callout 3 (numbers only)"),
 (7,'fail','diorama','cut',5,0,'', "그럼 각자 딴 곳에 성을 지어 나가면 되지 않냐고요? 하지만 이 요충지를 버리면 방어가 흩어집니다.",
   "floating diorama: the strategic rock at a tight river bend commanding the valley; three small markers try to leave toward faraway empty forested hilltops and drift apart, weakening a defensive ring around the valley route.",
   "a slow orbit as the three markers scatter outward from the rock", "a red X over the scattered markers and a cyan control-radius ring (no text)"),
 (9,'fail','diorama','cut',4,0,'', "그럼 성을 옆으로 넓히면? 바위 끝이라 넓힐 땅이 없었습니다.",
   "floating cross-section slab of the rock spur: the castle footprint already covering the entire flat top, sheer cliffs dropping to the river on both sides, no ground left to build outward.",
   "a slow lateral truck across the cross-section showing cliffs on both edges", "red X marks off both cliff edges and a horizontal dimension bracket pinched to its limit (no text)"),
 (10,'flip','diorama','cut',5,1,'수평→수직 모프 + 수직 적층', "대신에, 묘수를 냅니다. 밖이 아니라 위로 — 한 성을 지분으로 쪼개, 각자 자기 몫을 쌓기로.",
   "HIGH-ENERGY, TIGHT FRAMING. Extreme close-up of the rock-top cross-section: a blocked horizontal expansion arrow hits the cliff edge and FLIPS ninety degrees to point straight UP; a glowing cyan wireframe rapidly stacks upward and SNAPS solid, and three colour-coded columns of houses rise vertically from their zones; hard punch-in, then a fast full 360-degree orbit around the carved section.", "", ""),
 (11,'solution','diorama','cont',5,1,'수직 증축 타임랩스', "세 가문은 자기 구역에 집과 탑을 올렸습니다. 500년 넘게 위로만 증축해, 탑이 여덟, 높이는 8층.",
   "HIGH-ENERGY construction TIME-LAPSE, tight on the rock top: stone houses and tall towers rapidly STACK and ASSEMBLE themselves floor by floor in three colour-coded zones, rising upward piece by piece, flying dust and kinetic building motion, the cluster growing denser and taller until it settles as a tight cluster while bold counters tick up to 8 towers and 8 floors and a vertical scale reads 35 m.", "", ""),
 (12,'scale','diorama','cut',4,0,'', "방 100칸을 좁은 바위에 욱여넣었습니다. 그것도 많은 방에 난방까지 되게.",
   "a cutaway of the packed towers revealing a honeycomb of about one hundred tiny rooms crammed inside, thin smoke rising from many chimneys on every roof.",
   "a slow push-in across the honeycomb of rooms", "a big callout 100 and small heat/chimney markers on many rooms (numbers only)"),
 (13,'solution','real','cont',4,0,'', "안뜰과 우물은 함께 썼습니다. 좁을수록, 공유가 답이었죠.",
   "an intimate shot inside the castle: half-timbered facades of the different family houses all facing one small shared inner courtyard with a single well, tight and cosy.",
   "a slow reveal panning across the shared inner courtyard and well", "cyan arrows pointing to one shared courtyard and well (no text)"),
 (14,'cause','real','cut',4,0,'', "세 면을 감은 강과 절벽은, 그대로 성벽이 됐습니다.",
   "a low cinematic aerial skimming along the Elzbach river as it wraps the base of the sheer cliff, then rising up the rock face to the towers, water as a natural moat.",
   "a low orbit following the river around the cliff base up to the towers", "cyan arrows tracing the river on three sides and a callout 3 (no text)"),
 (15,'fail','real','cut',5,1,'투석 공성 → 온존', "1331년, 대주교가 맞은편에 공성성을 짓고 돌을 퍼부었지만, 끝내 무력으로는 뚫지 못했습니다.",
   "DYNAMIC medieval siege: from an opposing forested hilltop a small stone siege-castle, trebuchets hurling heavy round stone balls that arc across the valley and SMASH against Burg Eltz's cliff and towers with dust and impacts; then the camera settles to reveal the castle standing completely intact and defiant, spent stone balls scattered harmlessly among the rocks below. a small bold 1331 marker.",
   "", ""),
 (16,'scale','diorama','cut',5,0,'', "그래서 엘츠 성은 861년, 34대 동안 한 번도 무너지지 않았죠.",
   "a floating exploded timeline study of the castle in a dark void with a long horizontal dimension line running beside it representing centuries, clean neutral studio, space for big numbers.",
   "a slow orbit around the long timeline dimension line", "a long dimension line reading 861 yr, a callout 34, and a small 1157 start marker (numbers only)"),
 (17,'end','real','cut',6,1,'외벽 클라임→하늘→골든아워', "세 집안의 욕심이 하나의 성이 되어, 여덟 개의 탑으로 오늘도 숲 위에 서 있습니다.",
   "DYNAMIC. Start LOW at the river and cliff base, the camera travels fast UP the towering stone wall of the packed towers past window after window and slate roof after slate roof, then CRANES and TILTS UP off the highest tower and transitions into a majestic golden-hour aerial orbit pulling back to a hero wide, the eight towers glowing warm above the green forest and looping river; a small summary strip reads only 70 m 8 861 yr (numerals and units only).",
   "", ""),
]

CLS_KO   = {'real':'실사', 'diorama':'디오라마'}
CLS_STYLE= {'real':'color:#8fd06f;border-color:#8fd06f55', 'diorama':'color:#3fb6c4;border-color:#3fb6c455'}

def prompt_final(s):
    _id,role,cls,tr,dur,dyn,eff,kr,desc,cam,anno = s
    if dyn:
        base = DYN_REAL if cls=='real' else DYN_DIORAMA
        return f"{base} {desc} One continuous ~{dur}-second shot."
    base = STYLE_REAL if cls=='real' else STYLE_DIORAMA
    p = f"{base} {desc}"
    if anno:
        p += f" Rendered numeric annotations in the image: {anno}."
    p += f" SUBJECT: {SUBJECT} Camera: {cam} One continuous ~{dur}-second shot."
    return p

# ---- 시간축 (id는 순번 자동부여 → 컷 병합/삭제 시 재번호 불필요) ----
t=0; rows=[]
for i,s in enumerate(SHOTS):
    _id,role,cls,tr,dur,dyn,eff,kr,desc,cam,anno = s
    rows.append({'id':i+1,'role':role,'style_class':CLS_KO[cls],'transition':tr,'t':t,'dur':dur,
                 'dynamic':bool(dyn),'effect':eff,'sentence_kr':kr,'desc':desc,'camera':cam,
                 'anno_rendered':anno,'prompt_final':prompt_final(s)})
    t += dur
TOTAL=t

# ---- manifest.json ----
manifest = {
 'topic':TOPIC,
 'mode':'baked-numbersonly(AI-rendered numeric annotations, no captions)',
 'filter_score':{'대중인지도':1,'외관vs기능반전':2,'문제선명도':1,'뻔한해법실패':1,'반직관해결':2,
                 '작동과정명확성':1,'시각화가능성':2,'강한숫자':2,'공식자료충분':2,'현재성결말':2,
                 '총점':16,'판정':'조사 후 제작(14~16)'},
 'candidate_sentences_hit':['더 크게 만드는 대신 여러 개로 나눴다 / 위로 쌓았다',
                            '밖으로 넓히는 대신 지분으로 쪼개 수직 증축',
                            '자연의 힘(강·절벽)을 성벽으로 이용',
                            '떠나지 않고 한 성을 공유'],
 'fact_pack':{'최초기록':'1157 (Rudolf von Eltz, Barbarossa 기증문서 증인)',
   'Ganerbenburg분할':'1268 삼형제 분할 → 3가문(Kempenich 금사자·Rübenach 은사자·Rodendorf 물소뿔)',
   '바위':'70m 스퍼, 3면 Elzbach 강, 해발 320m','탑':'약 8기, 30~40m','층':'최대 8층',
   '방':'100칸+, 전부 난방 가능(중세에 드묾)','거주':'약 100명','건축기간':'500년+ (1472~1661)',
   '공성':'1331~36 엘츠 반목, 대주교 Balduin이 Trutzeltz 공성성 축조·투석 → 함락 실패(1333 항복·1336 강화, 성 온존)',
   '세습':'약 861년·34대(2018 기준) 동일 가문','파괴':'무력 함락·파괴 없음(아이펠 3개 성 중 하나)',
   '지폐':'구 500 도이치마르크 도안(1961~1995)','출처':'burg-eltz.de, en.wikipedia.org/wiki/Eltz_Castle'},
 'note':'BAKED(숫자만): 숫자·치수선·화살표만 프롬프트에 구워 AI가 이미지에 직접 렌더. 단어 라벨/한글 자막 없음. 한글 나레이션=TTS. A안=공동소유 수직 공동주택(왜 이렇게 생겼나)+방어 보강.',
 'style_base':STYLE_REAL,'style_base_diorama':STYLE_DIORAMA,'subject':SUBJECT,
 'shots':rows,
}
json.dump(manifest, open(os.path.join(HERE,'manifest.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- prompts.txt / script.md ----
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

# ---- gallery.html (CSS/JS는 몽생미셸본 재사용) ----
ref = open(REF, encoding='utf-8').read()
style = re.search(r'<style>.*?</style>', ref, re.S).group(0)
script = re.search(r'<script>.*?</script>', ref, re.S).group(0)

ndyn = sum(1 for r in rows if r['dynamic'])
cards=[]
for r in rows:
    dyncls = ' dyn' if r['dynamic'] else ' '
    dynslot = ' dyn' if r['dynamic'] else ' '
    ph2 = '⚡DYNAMIC · 프롬프트→드롭' if r['dynamic'] else '프롬프트→드롭'
    dynspan = f'<span class="dyn">⚡ {html.escape(r["effect"])}</span>' if r['dynamic'] else ''
    if r['dynamic']:
        ovlabel, ovbody = '카메라/효과', html.escape(r['effect'])
    elif r['anno_rendered']:
        ovlabel, ovbody = '렌더 숫자그래픽', html.escape(r['anno_rendered'])
    else:
        ovlabel, ovbody = '렌더 숫자그래픽', '<i style="color:#4a515b">—</i>'
    clsstyle = CLS_STYLE['real' if r['style_class']=='실사' else 'diorama']
    t0,t1 = r['t'], r['t']+r['dur']
    cards.append(
f'''<article class="c{dyncls}">
<div class="slot empty{dynslot}"><div class="ph">#{r['id']:02d} · {r['role']} · {t0}s→{t1}s<br><span>{ph2}</span></div><input type="file" accept="video/*,image/*" onchange="drop(this)"><img></div>
<div class="meta">
<div class="hd"><b>{r['id']:02d}</b> <span class="role">{r['role']}</span> <span class="tr">{r['transition']}</span>
 <span class="cls" style="{clsstyle}">{r['style_class']}</span> {dynspan} <span class="dur">{t0}s→{t1}s</span></div>
<p class="kr">{html.escape(r['sentence_kr'])}</p>
<div class="ov"><b>{ovlabel}</b><br>{ovbody}</div>
<div class="prow"><button onclick="cp(this)">📋 프롬프트 복사</button></div>
<code class="p">{html.escape(r['prompt_final'])}</code>
</div></article>''')

sub = (f'<span class="dyn">⚡ DYNAMIC {ndyn}컷</span> + BAKED(숫자만). A안=공동소유 수직 공동주택. '
       f'프롬프트 복사→t2v(Veo/Kling)→슬롯 드롭. 영상 저장→images/shotNN.mp4 자동 로드.')
gallery = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8">'
    f'<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    f'<title>엘츠 성 — 프롬프트 갤러리 (t2v)</title>{style}</head><body><div class="wrap">\n'
    f'<h1>엘츠 성 <span style="color:var(--cyan)">t2v</span> ({len(SHOTS)}컷 · {TOTAL}초)</h1>\n'
    f'<p class="sub">{sub}</p>\n'
    f'<div class="bar"><button class="save" onclick="saveFolder()">📁 images 폴더에 바로 저장</button>'
    f'<button class="save" onclick="saveDownload()">⬇️ shotNN 전부 다운로드</button>'
    f'<span class="barhint">저장 규칙 <code>images/shot01.mp4</code> · 다음에 열면 자동으로 불러옵니다</span></div>\n'
    f'<div class="grid">' + ''.join(cards) + f'</div></div>{script}</body></html>')
open(os.path.join(HERE,'gallery.html'),'w',encoding='utf-8').write(gallery)

print(f"생성 완료: {len(SHOTS)}컷 · {TOTAL}초 · DYNAMIC {ndyn}컷")
print("  manifest.json · prompts.txt · script.md · gallery.html")
