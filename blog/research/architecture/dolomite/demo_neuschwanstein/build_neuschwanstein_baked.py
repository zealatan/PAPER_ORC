#!/usr/bin/env python3
"""demo_neuschwanstein 빌더 — 노이슈반슈타인: 동화 껍데기 속 1880년대 최첨단, 왕이 못 누린 성.
   미모 우선 + 4-스킨(X-ray가 주인공) + 위트 + 연속-무빙 + CLEAN PLATE(숫자 없음, 후처리 오버레이).
   ※ deep-research/공식(Bayerische Schlösserverwaltung) 고증 반영:
     삭제 = "172일/11박" 체류 숫자(1차검증 실패) · 디즈니 영감설(1차검증 실패).
     scope = 강철골조는 '옥좌의 방'만. 확인 = 1869착공/1886미완성(200중14)/온풍난방·전층온수·자동변기·전기벨·3·4층전화/그로토·무대/7주후개방·연140만.
"""
import json, os, re, html
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
REF  = os.path.join(HERE, '..', 'demo_montsaintmichel', 'gallery.html')

TOPIC = '노이슈반슈타인 성 — 동화 껍데기 속 최첨단, 왕이 못 누린 성 (Schloss Neuschwanstein)'
SUBJECT = ("Schloss Neuschwanstein — an idealized Romanesque-Revival fairytale castle of pale grey-white limestone "
    "perched dramatically on a rugged rock crag high in the Bavarian Alps: tall slender towers with blue conical "
    "spires, a soaring multi-storey Palas keep, arched windows and battlements, and a lower red-brick gatehouse; "
    "set against snow-capped Alpine peaks, dark pine forests and the Alpsee lake below, the classic view from the "
    "Marienbrücke bridge over the Pöllat gorge waterfall.")

CLEAN = (" Absolutely NO rendered text, numbers, digits, labels, dimension lines, callouts, counters, arrows-with-text "
    "or graphic annotations of any kind anywhere in the frame — a completely clean plate; all numeric graphics are "
    "added later as a separate post overlay. no watermark.")
STYLE_REAL = ("photorealistic cinematic drone footage with a subtle tilt-shift miniature feel, physically-based "
    "lighting, subtle film grain, soft cinematic color grade, vertical 9:16, Bavarian Alps setting, a pale fairytale "
    "castle with blue-spired towers perched on a dramatic rock crag above forests and a lake, snow-capped peaks, "
    f"soft silvery-golden light.{CLEAN}")
STYLE_DIORAMA = ("signature floating-diorama miniature cutaway: a rectangular slab of the alpine rock crag with the "
    "fairytale castle on it, cut out and floating in a WARM graduated amber-to-charcoal void, flat cut-sides exposing "
    "rock and foundations, lit by a warm low amber key light with soft golden fill and gentle rim glow, faint "
    "volumetric haze, portrait telephoto look, shallow depth of field, photorealistic miniature render, warm "
    f"cinematic color grade, vertical 9:16.{CLEAN}")
STYLE_XRAY = ("see-through x-ray / technical scan visualization, deep graduated navy-black void, the medieval-looking "
    "castle rendered as a glowing translucent cyan wireframe with x-ray layers revealing the HIDDEN modern services "
    "behind the fairytale stone shell — hot-air heating ducts, running-water pipes, wiring and telephone lines "
    f"threading through every floor — a soft horizontal scan-line sweeping through, holographic feel, subtle film grain, cyan accents, vertical 9:16.{CLEAN}")
STYLE_BLUEPRINT = ("an architectural blueprint that morphs into photoreal reality, vertical 9:16. The shot BEGINS as "
    "a clean cyan-and-white line drawing on deep blueprint-blue paper with a faint grid, then a bright wipe sweeps "
    f"across and it MORPHS into the real structure with soft light.{CLEAN}")
DYN_REAL = f"photorealistic cinematic footage, soft cinematic color grade, vertical 9:16, Bavarian Alps setting.{CLEAN}"
DYN_DIORAMA = f"signature floating-diorama miniature, warm graduated amber-charcoal void, warm cinematic color grade, vertical 9:16.{CLEAN}"
DYN_XRAY = f"see-through x-ray / scan visualization, deep navy-black void, glowing translucent cyan wireframe revealing hidden heating ducts, water pipes and wiring behind a fairytale castle shell, scan-line sweep, vertical 9:16.{CLEAN}"
DYN_BLUEPRINT = f"architectural blueprint morphing into a real ornate hall over a hidden steel framework, blueprint-blue paper with grid, cyan line-drawing wiping into real interior, vertical 9:16.{CLEAN}"
BASE  = {'real':STYLE_REAL,'diorama':STYLE_DIORAMA,'xray':STYLE_XRAY,'blueprint':STYLE_BLUEPRINT}
DBASE = {'real':DYN_REAL,'diorama':DYN_DIORAMA,'xray':DYN_XRAY,'blueprint':DYN_BLUEPRINT}
CLS_KO   = {'real':'실사','diorama':'디오라마','xray':'X-ray','blueprint':'청사진'}
CLS_STYLE= {'real':'color:#8fd06f;border-color:#8fd06f55','diorama':'color:#e8a33d;border-color:#e8a33d55',
            'xray':'color:#5bd0ff;border-color:#5bd0ff55','blueprint':'color:#7aa2ff;border-color:#7aa2ff55'}

# role, cls, transition, dur, dyn, effect, kr, desc, camera, anno
SHOTS = [
 ('hook','real','cut',5,1,'지도→드론 다이브 줌 + 산 위 성 리빌', "독일 바이에른 알프스, 산꼭대기에 동화 속 성이 하나 서 있어요.",
   "DYNAMIC opening: start on a clean minimal stylized map of Germany (soft grey, no text) as a glowing cyan pin drops onto Bavaria; a fast Google-Earth-style DIVE ZOOM plunges down through clouds into a real cinematic drone view soaring over snow-capped Alps toward a pale fairytale castle with blue-spired towers perched on a dramatic rock crag above dark forests and a lake. no words anywhere.", "", ""),
 ('subject','real','cut',5,0,'', "노이슈반슈타인. 세상에서 가장 유명한 '동화 성'이죠.",
   "a majestic full 360-degree orbit at soft golden hour around the pale fairytale castle on its crag, blue conical spires and slender towers glowing, snow-capped Alpine peaks and the lake spreading below.",
   "a slow cinematic 360-degree orbit around the castle on its alpine crag", ""),
 ('hook','real','cut',4,0,'', "완벽한 중세 기사의 성 같죠? 근데 지어진 건 1869년. 속은 당대 최첨단이었어요.",
   "a sweeping low shot rising along the castle's Romanesque towers, battlements and arched windows against the mountains, conveying a perfect medieval look, bright soft daylight.",
   "a slow rise along the towers conveying the medieval look before the twist", "[오버레이] 1869 착공"),
 ('cause','diorama','cut',5,1,'성 조립 타임랩스', "루트비히 2세가, 바그너 오페라 속 세계를 현실로 옮기려 산꼭대기에 짓기 시작합니다.",
   "HIGH-ENERGY warm floating-diorama construction TIME-LAPSE: on the rocky alpine crag, the fairytale castle rapidly ASSEMBLES itself stone by stone and tower by tower, blue-spired towers rising one after another in quick succession, kinetic building motion, a dreamy theatrical operatic quality as a stage fantasy is built into a real mountain, warm amber lighting.", "", ""),
 ('solution','xray','cut',5,1,'중세 껍데기 속 숨은 기술 스캔', "그런데 중세 돌벽을 투시하면 — 온풍 중앙난방에, 층마다 흐르는 수돗물.",
   "DYNAMIC x-ray reveal: the medieval stone walls of the castle turn translucent as a bright scan-line sweeps through, revealing hidden glowing cyan hot-air heating ducts and running-water pipes threading through every floor behind the fairytale shell.", "", ""),
 ('solution','xray','cut',5,1,'배선·전화 스캔업', "자동으로 물 내려가는 변기, 하인 부르는 전기 벨, 심지어 위층엔 전화기까지 있었죠.",
   "DYNAMIC x-ray scan climbing UPWARD through the castle, hidden modern systems glowing to life floor by floor — automatic-flushing toilets, electric servant call-bell wiring, and telephone lines on the upper floors — all cyan wireframe threading through the stone as the scan-line rises.", "", ""),
 ('solution','blueprint','cut',5,1,'옥좌의 방 강철 골조 모프', "가장 화려한 옥좌의 방은, 겉은 중세지만 속은 강철 골조로 떠받쳤어요.",
   "DYNAMIC blueprint-to-real: a blueprint of a hidden steel/iron framework draws itself inside the Throne Hall, then a bright wipe MORPHS it into the real lavish Byzantine-style throne hall whose ornate walls are clad in plaster over the concealed steel skeleton.", "", ""),
 ('scale','real','cut',5,0,'', "황금빛 옥좌의 방과, 벽마다 바그너 오페라로 가득한 방들.",
   "a beautiful real interior of the lavish golden Byzantine-style throne hall and rooms whose walls are covered with paintings of Wagner's operas, rich glowing colours, chandelier and candlelight, breathtaking.",
   "a slow reveal gliding across the golden throne hall and opera-painted walls", ""),
 ('solution','diorama','cut',5,0,'', "인공 종유석 동굴에 색색 전등과 폭포까지. 성이라기보단, 거대한 무대 세트였어요.",
   "a warm floating-diorama cutaway showing the theatrical artificial dripstone grotto tucked inside the castle — coloured electric lights and a little waterfall — and a small stage, the whole interior arranged like an opera set rather than a fortress.",
   "a slow orbit into the artificial grotto and stage set inside the castle", ""),
 ('fail','real','cut',5,0,'', "이렇게까지 지어놓고 — 정작 왕은, 완공도 못 본 채 잠깐 머물다 떠납니다.",
   "a wide melancholic golden shot of the vast castle with a lonely royal silhouette at a high window, overwhelming grandeur barely ever used, soft mist over the Alps.",
   "a slow high aerial drifting past the lonely castle, a sense of grandeur unused", ""),
 ('end','diorama','cut',5,0,'', "1886년 루트비히는 의문의 죽음을 맞고, 성은 200개 방 중 겨우 열댓 개만 완성된 채 멈춥니다.",
   "a warm floating-diorama cross-section of the castle showing only a handful of finished ornate rooms among many bare, unfinished ones and a still-scaffolded tower, the building frozen mid-construction, the light dimming.",
   "a slow orbit around the cross-section of finished vs unfinished rooms as the light dims", "[오버레이] 1886 · 200실 중 14"),
 ('scale','real','cut',5,0,'', "그런데 죽은 지 7주 만에 성이 열리고 — 지금은 해마다 140만 명이 찾는, 세계 최고의 성이 됐죠.",
   "a gorgeous golden-hour hero shot of Neuschwanstein seen from the classic Marienbruecke viewpoint over the gorge, the iconic fairytale silhouette against luminous mountains, tiny visitors for scale, breathtaking.",
   "a majestic slow reveal of the iconic castle from the classic bridge viewpoint at golden hour", "[오버레이] 연 140만"),
 ('end','real','cont',10,0,'', "왕의 외로운 꿈이었던 성이, 이제는 모두의 동화가 됐습니다. 알프스 위에, 오늘도 그대로.",
   "a long, unhurried, lingering dusk shot: the pale fairytale castle on its crag above the misty alpine forest as warm golden light very slowly fades toward soft blue dusk, a few windows glowing, the camera drifting almost imperceptibly and then holding, letting the lonely dream-castle breathe and settle, quietly emotional and cinematic.",
   "an almost-still, very slow drift that settles into a long hold on the fairytale castle above the misty Alps as dusk falls", ""),
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
 'mode':'CLEAN-PLATE(숫자 미포함, 후처리 오버레이) · 4-skin(X-ray 주인공) · witty · beauty-first · 고증검증(deep-research/공식)',
 'filter_score':{'대중인지도':2,'외관vs기능반전':2,'문제선명도':1,'뻔한해법실패':1,'반직관해결':2,
                 '작동과정명확성':2,'시각화가능성':2,'강한숫자':1,'공식자료충분':2,'현재성결말':2,'미모(가중)':3,
                 '총점':18,'판정':'즉시 제작 후보'},
 'candidate_sentences_hit':['겉은 중세, 속은 1880년대 최첨단','성이 아니라 거대한 무대 세트','왕이 짓고도 완공/거주 못 함','옥좌의 방=중세 외피+강철 골조'],
 'fact_pack_verified':{'착공/미완성':'초석 1869.9.5(부지작업 1868 여름), 1886.6.13 사망 시 미완성 — 200여 실 중 ~14실만 완성, Bower·사각탑 1892 완성, 성채(keep)+예배당 미착공(✅ 공식)',
   '숨은기술':'온풍(calorifère) 중앙난방·전층 온수(주방 냉온수)·자동 물내림 변기·전기(배터리) 하인 호출벨·3·4층 전화·현대식 주방·음식 리프트(✅ 공식 interior)',
   '강철골조':'옥좌의 방=이미 선 Palas에 삽입한 강철(獨:철) 골조 위 회벽 마감 + 산업용 강철 창틀. ★성 전체 강철 아님(scope)',
   '무대/그로토':'탄호이저 인공 그로토(색전등·폭포·무지개기계)·바그너 오페라 방·무대 세트(✅)',
   '개방/방문객':'1886.8.1(사후 ~7주) 유료 개방, 이후 누적 1억3천만+, 연 ~140만(✅)',
   '삭제(검증실패)':'"172일/11박" 체류 정확수치 → 삭제(숫자 없이 "잠깐") · 디즈니 잠자는숲속공주 성 영감설 → 삭제',
   '출처':'neuschwanstein.de·schloesser.bayern.de(공식), en.wikipedia.org, britannica.com'},
 'note':'고증 검증본. 미검증(172일·디즈니) 삭제, 강철골조 옥좌의방으로 scope. X-ray가 주인공(동화껍데기 속 최신공학). 미모우선·clean plate·위트.',
 'style_base':STYLE_REAL,'style_base_diorama':STYLE_DIORAMA,'style_base_xray':STYLE_XRAY,'style_base_blueprint':STYLE_BLUEPRINT,
 'subject':SUBJECT,'shots':rows,
}
json.dump(manifest, open(os.path.join(HERE,'manifest.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)

with open(os.path.join(HERE,'prompts.txt'),'w',encoding='utf-8') as f:
    f.write(f"# {TOPIC}\n# 고증검증 · CLEAN-PLATE · 4-스킨(X-ray 주인공) · 위트 · {len(SHOTS)}컷 · {TOTAL}초\n\n")
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
sub = (f'<span class="dyn">⚡ DYNAMIC {ndyn}컷</span> · 4-스킨(실사 {mix["실사"]}·디오라마 {mix["디오라마"]}·<b style="color:#5bd0ff">X-ray {mix.get("X-ray",0)}</b>·청사진 {mix.get("청사진",0)}) · 위트 · 미모우선 · <b style="color:#e4685c">클립엔 숫자 없음</b> · <b style="color:#8fd06f">고증검증</b>. '
       f'훅=동화 껍데기 속 1880년대 최첨단. 프롬프트 복사→t2v→슬롯 드롭.')
gallery = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    f'<title>노이슈반슈타인 성 — 프롬프트 갤러리 (t2v)</title>{style}</head><body><div class="wrap">\n'
    f'<h1>노이슈반슈타인 성 <span style="color:var(--cyan)">t2v</span> ({len(SHOTS)}컷 · {TOTAL}초 · 고증검증)</h1>\n'
    f'<p class="sub">{sub}</p>\n'
    '<div class="bar"><button class="save" onclick="saveFolder()">📁 images 폴더에 바로 저장</button>'
    '<button class="save" onclick="saveDownload()">⬇️ shotNN 전부 다운로드</button>'
    '<span class="barhint">저장 규칙 <code>images/shot01.mp4</code> · 다음에 열면 자동으로 불러옵니다</span></div>\n'
    '<div class="grid">' + ''.join(cards) + f'</div></div>{script}</body></html>')
open(os.path.join(HERE,'gallery.html'),'w',encoding='utf-8').write(gallery)
print(f"생성 완료: {len(SHOTS)}컷 · {TOTAL}초 · DYNAMIC {ndyn}컷 · 스킨 {dict(mix)}")
