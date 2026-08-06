#!/usr/bin/env python3
"""demo_chenonceau 빌더 — 슈농소: 강 위에 아치로 지은 '여인들의 성' + 2차대전 탈출 다리.
   미모 우선 + 4-스킨 비주얼 문법 + 위트/대화체 톤 + 연속-무빙(부드러운 전환).
   BAKED(숫자만) · 한글=TTS · 갤러리 CSS/JS는 ../demo_montsaintmichel/gallery.html 재사용.
"""
import json, os, re, html
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
REF  = os.path.join(HERE, '..', 'demo_montsaintmichel', 'gallery.html')

TOPIC = '슈농소 성 — 강을 건너는 성, 여인들의 성 (Château de Chenonceau, 셰르 강 5아치 + 2차대전 탈출 다리)'
NUMS = "5, 60 m, 16C, 1940"
SUBJECT = ("Château de Chenonceau — an elegant white Renaissance château in the Loire Valley of France built right "
    "across the River Cher, its long two-storey gallery carried on a five-arched stone bridge spanning the water "
    "and mirrored in the river below; the 'Château des Dames' shaped by a succession of women, set among formal "
    "gardens and woods.")

# 클립엔 숫자/치수/라벨을 절대 굽지 않음 → 전부 후처리 오버레이. clean plate 지시.
CLEAN = (" Absolutely NO rendered text, numbers, digits, labels, dimension lines, callouts, counters, arrows-with-text "
    "or graphic annotations of any kind anywhere in the frame — a completely clean plate; all numeric graphics are "
    "added later as a separate post overlay. no watermark.")
STYLE_REAL = ("photorealistic cinematic drone footage with a subtle tilt-shift miniature feel, physically-based "
    "lighting, subtle film grain, soft cinematic color grade, vertical 9:16, Loire Valley France setting on the "
    "River Cher, an elegant white Renaissance château spanning the calm river on arches, mirror-still water "
    f"reflections, soft silvery-golden light, gardens and woods.{CLEAN}")
STYLE_DIORAMA = ("signature floating-diorama miniature cutaway: a rectangular slab of the River Cher with the "
    "château-bridge on it, cut out and floating in a WARM graduated amber-to-charcoal void, flat cut-sides "
    "exposing water and riverbed strata and the stone arches and piers under the water, warm low amber key light "
    "with soft golden fill and gentle rim glow, faint volumetric haze, portrait telephoto look, shallow depth of "
    f"field, photorealistic miniature render, warm cinematic color grade, vertical 9:16.{CLEAN}")
STYLE_XRAY = ("see-through x-ray / technical scan visualization, deep graduated navy-black void, the château-bridge "
    "and the river rendered as a glowing translucent cyan wireframe with x-ray layers revealing the stone arches "
    "and submerged piers standing in the riverbed beneath the water surface, a soft horizontal scan-line sweeping "
    f"through, holographic engineering feel, subtle film grain, cyan accents, vertical 9:16.{CLEAN}")
STYLE_BLUEPRINT = ("an architectural blueprint that morphs into photoreal reality, vertical 9:16. The shot BEGINS as "
    "a clean cyan-and-white line drawing of an arched bridge/gallery over a river on deep blueprint-blue paper with "
    "a faint grid — then a bright wipe sweeps across and it MORPHS into the real white stone structure over the "
    f"water with soft light.{CLEAN}")
DYN_REAL = f"photorealistic cinematic footage, soft cinematic color grade, vertical 9:16, Loire Valley River Cher setting.{CLEAN}"
DYN_DIORAMA = f"signature floating-diorama miniature, warm graduated amber-charcoal void, warm cinematic color grade, vertical 9:16.{CLEAN}"
DYN_XRAY = f"see-through x-ray / scan visualization, deep navy-black void, glowing translucent cyan wireframe revealing submerged bridge piers under the river, scan-line sweep, vertical 9:16.{CLEAN}"
DYN_BLUEPRINT = f"architectural blueprint morphing into a real white stone arched bridge over a river, blueprint-blue paper with grid, cyan line-drawing wiping into real stone, vertical 9:16.{CLEAN}"
BASE  = {'real':STYLE_REAL,'diorama':STYLE_DIORAMA,'xray':STYLE_XRAY,'blueprint':STYLE_BLUEPRINT}
DBASE = {'real':DYN_REAL,'diorama':DYN_DIORAMA,'xray':DYN_XRAY,'blueprint':DYN_BLUEPRINT}
CLS_KO   = {'real':'실사','diorama':'디오라마','xray':'X-ray','blueprint':'청사진'}
CLS_STYLE= {'real':'color:#8fd06f;border-color:#8fd06f55','diorama':'color:#e8a33d;border-color:#e8a33d55',
            'xray':'color:#5bd0ff;border-color:#5bd0ff55','blueprint':'color:#7aa2ff;border-color:#7aa2ff55'}

# role, cls, transition, dur, dyn, effect, kr, desc, camera, anno
SHOTS = [
 ('hook','real','cut',5,1,'지도→드론 다이브 줌 + 다리 리빌', "프랑스 루아르, 셰르 강 위에 하얀 성이 떠 있습니다. 근데 자세히 보면 이 성, 강을 건너고 있어요. 성이 아니라 다리죠.",
   "DYNAMIC opening: start on a clean minimal stylized map of France (soft grey, no text) as a glowing cyan pin drops onto the Loire Valley; a fast Google-Earth-style DIVE ZOOM plunges down through soft clouds into a real cinematic drone view gliding low over a calm river toward an elegant white chateau that seems to float, then the camera slides alongside to reveal it stands on stone arches right across the river with water flowing beneath it, more bridge than castle. no words anywhere.", "", ""),
 ('subject','real','cut',5,0,'', "슈농소 성. 강 위에 아치를 놓고 올라선, '여인들의 성'이에요.",
   "a majestic full 360-degree orbit at soft golden hour around the chateau spanning the River Cher, the long gallery carried on graceful arches, mirror-still reflection doubling it on the water.",
   "a slow cinematic 360-degree orbit around the chateau on the river, beautiful soft golden light", ""),
 ('cause','diorama','cut',4,0,'', "사실 이 자리엔 원래, 강물을 받아 돌던 물레방아가 있었어요.",
   "a warm floating-diorama miniature of an old fortified stone water mill sitting on stone piers in the river, its little wooden wheel slowly turning in the flowing current, the small mill modelled on a floating cut slab with riverbed strata exposed on the sides.",
   "a slow orbit around the miniature old water mill and its turning wheel", ""),
 ('solution','blueprint','cut',6,1,'기초→다리 도면→실물 모프', "원래는 강가 물레방앗간 자리. 앙리 2세의 연인 디안이, 그 돌기초 위로 강을 가로지르는 다리를 놓습니다.",
   "DYNAMIC blueprint-to-real: over an old fortified mill's stone foundations standing in the river, a clean architectural blueprint of a five-arched stone bridge draws itself on blueprint-blue paper, then a bright wipe MORPHS it into the real white stone arched bridge spanning the River Cher, water flowing through the arches.", "", ""),
 ('scale','xray','cut',5,0,'', "아치 다섯 개가, 강물 속 교각을 딛고 성 전체를 떠받칩니다.",
   "an x-ray see-through of the chateau-bridge and the river, the water turned translucent to reveal the five stone arches and their submerged piers planted firmly in the riverbed, glowing cyan wireframe holding up the whole structure.",
   "a slow x-ray glide along the bridge revealing the five arches and their submerged piers", "[오버레이] 아치 5개 · 수중 교각 리더선"),
 ('scale','diorama','cut',5,0,'', "게다가 다리 기둥 속엔 — 강물 바로 위에 주방까지 숨겨 넣었어요.",
   "a warm floating-diorama cutaway of one massive bridge pier standing in the river, the near side sliced open to reveal the chateau's kitchens built inside the pier right at water level — a domed oven, a butcher's block and hanging copper pots with tiny figures at work — warm amber lighting, riverbed strata exposed on the cut sides of the floating slab.",
   "a slow orbit into the sliced-open pier revealing the kitchens inside at water level", "[오버레이] 교각 내부 주방 마커"),
 ('solution','blueprint','cut',5,1,'갤러리 증축 모프', "왕이 죽자 왕비 카트린이 디안을 쫓아내고, 그 다리 위에 2층 갤러리를 올리죠.",
   "DYNAMIC blueprint-to-real: on top of the existing five-arched bridge, a blueprint of a long elegant two-storey gallery draws itself and then MORPHS into the real white stone gallery rising over the water, completing the chateau that crosses the river.", "", ""),
 ('scale','real','cut',5,0,'', "그렇게 완성된 물 위의 긴 회랑. 강물에 그대로 한 번 더 비칩니다.",
   "a beautiful soft golden-hour shot of the long two-storey gallery stretching across the River Cher, perfectly mirrored in the glassy water below, symmetrical and dreamlike, the long white stone gallery over the river.",
   "a slow glide down the length of the gallery with its full reflection on the water", "[오버레이] 갤러리 길이 60 m 치수선"),
 ('subject','real','cut',4,0,'', "세운 것도, 넓힌 것도, 지킨 것도 모두 여인들. 그래서 '여인들의 성'이에요.",
   "an elegant aerial gliding over the chateau and its two famous formal gardens on either bank, warm and graceful, a sense of many hands having shaped it over centuries.",
   "a slow graceful aerial over the chateau and its symmetrical gardens", ""),
 ('subject','real','cut',4,0,'', "성 양옆 정원은 또 어떻고요. 손질된 화단이 강까지 곧게 이어집니다.",
   "a beautiful ground-level immersive glide along the central path of the blooming formal French parterre garden, geometric flowerbeds and clipped box hedges and bright flowers in warm golden light leading the eye straight toward the white chateau and the river beyond.",
   "a low smooth glide down the garden's central path toward the chateau", ""),
 ('cause','diorama','cut',6,0,'', "2차대전엔 이 강이 경계선이 됩니다. 갤러리 이쪽 끝은 자유 프랑스, 저쪽 끝은 나치 점령지였죠.",
   "a warm floating-diorama of the chateau-bridge over the river with a stark glowing line running right down the middle of the river beneath it, one bank tinted as free territory and the other as occupied, the long gallery straddling the divide between two worlds.",
   "a slow orbit as a glowing demarcation line lights up down the river under the bridge", "[오버레이] 1940 · 강 경계선(빨강)"),
 ('solution','real','cut',6,0,'', "관리인은 순찰이 뜸한 틈에 문을 열어, 수백 명을 이 회랑으로 몰래 건넸습니다. 강을 건너는 다리가, 자유로 건너는 다리가 된 거죠.",
   "a tense, moving night-into-dawn scene: a caretaker quietly unlocks the gallery doors while patrols are away and shadowy refugees slip across the long gallery over the dark river from the occupied bank toward freedom, hushed and dramatic, soft moonlight giving way to hopeful dawn on the water.",
   "a slow careful move following silhouettes crossing the gallery over the river as dawn breaks", ""),
 ('scale','real','cut',6,1,'강 위 상승→골든아워', "해 질 무렵, 슈농소는 강과 하늘 사이에 조용히 걸립니다.",
   "DYNAMIC climactic rise: the camera lifts from the water level up the arches and gallery, then CRANES and pulls back into a golden-hour sky as the whole chateau-bridge sits mirrored on the River Cher far below among the gardens — a soaring rising hero move at dusk.", "", ""),
 ('end','real','cont',10,0,'', "성을 놓은 여인들도, 강을 건넌 사람들도 이제는 없습니다. 그래도 슈농소는, 오늘도 셰르 강 위에 조용히 떠 있죠.",
   "a long, unhurried, lingering night-dusk shot: the white chateau-bridge mirrored perfectly on the utterly still River Cher, thin mist drifting low over the water, a single warm light glowing in the long gallery, the camera drifting almost imperceptibly and then holding, letting the scene breathe and settle, quietly emotional and cinematic, a gentle sense of time passing.",
   "an almost-still, very slow drift that settles into a long hold on the mirrored chateau, letting it linger", ""),
]

CONT = (" The shot begins and ends on smooth, continuous camera motion with no abrupt start, freeze or hard stop, "
        "gentle easing, so it blends seamlessly into the neighbouring shots.")
def prompt_final(role,cls,tr,dur,dyn,eff,kr,desc,cam,anno):
    if dyn:
        return f"{DBASE[cls]} {desc} One continuous ~{dur}-second shot.{CONT}"
    p = f"{BASE[cls]} {desc}"
    # anno(수치)는 프롬프트에 넣지 않음 — 후처리 오버레이용 메모로만 보관
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
mix = Counter(r['style_class'] for r in rows)

manifest = {
 'topic':TOPIC,
 'mode':'CLEAN-PLATE(클립에 숫자 미포함, 수치는 후처리 오버레이) · 4-skin(real/diorama-warm/xray/blueprint) · witty tone · beauty-first',
 'filter_score':{'대중인지도':2,'외관vs기능반전':2,'문제선명도':1,'뻔한해법실패':1,'반직관해결':2,
                 '작동과정명확성':1,'시각화가능성':2,'강한숫자':1,'공식자료충분':2,'현재성결말':2,'미모(가중)':3,
                 '총점':16,'판정':'미모 우선 채택(미모+반전+드라마)'},
 'candidate_sentences_hit':['성이 아니라 강을 건너는 다리','자연(강)을 딛고 그 위에 지었다',
                            '건너는 다리가 자유로 건너는 다리가 됐다','세운 것도 지킨 것도 여인들'],
 'fact_pack':{'구조':'옛 물레방앗간 돌기초 위에 건립, 셰르 강을 가로지르는 5아치 다리. 건축가 Philibert de l\'Orme',
   '디안→카트린':'앙리2세가 연인 Diane de Poitiers에게 하사→디안이 강 위 다리 축조. 왕 사후 왕비 Catherine de Médicis가 디안을 Chaumont로 내쫓고 다리 위 2층 갤러리 증축',
   '여인들의 성':'Château des Dames — Katherine Briçonnet·Diane·Catherine·Louise·Mme Dupin 등 여러 여인이 짓고 지킴',
   '2차대전':'셰르 강=점령지/자유지역 경계선. 갤러리 한쪽=자유 프랑스, 반대쪽=나치 점령. 관리인 Simone Meunier가 순찰 틈에 갤러리 문 열어 수백 명(유대인·주민·레지스탕스) 탈출 도움',
   '출처':'worldhistory.org, masterclass.com, castlesworld.com, thefunambulist.net'},
 'note':'미모 우선. 4-스킨: real=미모/여인들/2차대전 드라마, diorama=물레방앗간 기초·경계선, blueprint=다리·갤러리 건립, xray=강물 속 아치·교각. 위트톤·연속무빙·숫자만 baked.',
 'style_base':STYLE_REAL,'style_base_diorama':STYLE_DIORAMA,'style_base_xray':STYLE_XRAY,'style_base_blueprint':STYLE_BLUEPRINT,
 'subject':SUBJECT,'shots':rows,
}
json.dump(manifest, open(os.path.join(HERE,'manifest.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)

with open(os.path.join(HERE,'prompts.txt'),'w',encoding='utf-8') as f:
    f.write(f"# {TOPIC}\n# 미모우선 · 4-스킨 · BAKED(숫자만) · 위트톤 · {len(SHOTS)}컷 · {TOTAL}초\n\n")
    for r in rows:
        f.write(f"── #{r['id']:02d} {r['role']} · {r['t']}s→{r['t']+r['dur']}s · [{r['style_class']}]"
                + (f" · ⚡{r['effect']}" if r['dynamic'] else "") + "\n")
        f.write(f"  나레이션: {r['sentence_kr']}\n")
        if r['anno_rendered']: f.write(f"  숫자그래픽: {r['anno_rendered']}\n")
        f.write(f"  프롬프트: {r['prompt_final']}\n\n")
with open(os.path.join(HERE,'script.md'),'w',encoding='utf-8') as f:
    f.write(f"# {TOPIC} — 대본 (위트/대화체, 미모 우선)\n\n**전체 나레이션**\n\n")
    f.write(' '.join(r['sentence_kr'] for r in rows) + "\n\n**컷 표 (스킨)**\n\n| # | 구간 | 스킨 | 나레이션 |\n|---|---|---|---|\n")
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
sub = (f'<span class="dyn">⚡ DYNAMIC {ndyn}컷</span> · 4-스킨(실사 {mix["실사"]}·디오라마 {mix["디오라마"]}·X-ray {mix["X-ray"]}·청사진 {mix["청사진"]}) · 위트톤 · 미모우선 · <b style="color:#e4685c">클립엔 숫자 없음(후처리 오버레이)</b>. '
       f'훅=강을 건너는 성·여인들의 성·2차대전 탈출 다리. 프롬프트 복사→t2v→슬롯 드롭.')
gallery = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    f'<title>슈농소 성 — 프롬프트 갤러리 (t2v)</title>{style}</head><body><div class="wrap">\n'
    f'<h1>슈농소 성 <span style="color:var(--cyan)">t2v</span> ({len(SHOTS)}컷 · {TOTAL}초 · 4-스킨)</h1>\n'
    f'<p class="sub">{sub}</p>\n'
    '<div class="bar"><button class="save" onclick="saveFolder()">📁 images 폴더에 바로 저장</button>'
    '<button class="save" onclick="saveDownload()">⬇️ shotNN 전부 다운로드</button>'
    '<span class="barhint">저장 규칙 <code>images/shot01.mp4</code> · 다음에 열면 자동으로 불러옵니다</span></div>\n'
    '<div class="grid">' + ''.join(cards) + f'</div></div>{script}</body></html>')
open(os.path.join(HERE,'gallery.html'),'w',encoding='utf-8').write(gallery)
print(f"생성 완료: {len(SHOTS)}컷 · {TOTAL}초 · DYNAMIC {ndyn}컷 · 스킨 {dict(mix)}")
