#!/usr/bin/env python3
"""
gen_pg_editor.py — PG 통합 쇼츠 에디터(pg_editor.html) 생성 · GOLDEN spec 반영본.

golden_shorts_accum.py 의 NEWRA(x축 이동 reelAnim)·CMAP·fire_payload·CSS 를 재사용해
4슬라이드(1=썸네일 편집가능 / 2·3·4=golden 그래프)를 조립한다.
출력: blog/golden_shorts_accum/golden_shorts_accum_editor.html

의존: golden_shorts_accum.py(같은 폴더, import), assets/assets.json, assets/paper_b64.txt, blog/fonts, pg_deck.json, pg_final.html
실행: python3 gen_pg_editor.py
"""
import json, os
import golden_shorts_accum as G   # NEWRA, CMAP, logo, rc_css, FONTSRC, paper_uri, sc, fire_payload, FIRE_SPECS

HERE = os.path.dirname(os.path.abspath(__file__))
assets = json.load(open(os.path.join(HERE, "assets", "assets.json")))
STOCK = os.environ.get("SHORTS_STOCK", "PG")   # PG(기본) | KTNG — 파이프라인 §0.5: 스펙 고정, 종목 입력만 교체

if STOCK == "PG":
    OUT     = os.path.join(HERE, "golden_shorts_accum_editor.html")
    TITLE   = "golden_shorts_accum_editor — PG 적립 쇼츠 에디터 (썸네일+적립vs폭락 3)"
    LOGO    = G.logo
    COMPANY = "프록터 앤 갬블 (PG)"
    LEGOUT  = ('<span class="lg"><span class="sw" style="background:#2b6cb0"></span>매달 적립식</span>'
               '<span class="lg"><span class="sw" style="background:#c2255c"></span>폭락 시 매수</span>')
    FIRES   = [{"hook": "%d. 적립식 vs <b>%d%% 하락매수</b>" % (i + 1, f["thr"]), "payload": f["payload"]}
               for i, f in enumerate(G.FIRES)]
    # 배투실 표준 썸네일(레퍼런스): 제품클러스터(y37)→브랜드로고(y54)→마젠타문구(y60)→흰문구(y66)
    THUMB_INIT = ("addImg(PRODUCTS,50,37,78,0);addImg(PGLOGO,50,54,15,0);"
                  "addText('5억으로 은퇴',50,60,7,'#d12e77',0);"
                  "addText('적정 생활비는?',50,66,7,'#ffffff',0);")
elif STOCK == "KTNG":
    OUT     = os.path.join(HERE, "golden_shorts_accum_KTNG.html")
    TITLE   = "golden_shorts_accum_KTNG — KT&G 통합 쇼츠 에디터 (썸네일+파이어 3)"
    LOGO    = ('<text x="100" y="62" text-anchor="middle" font-family="Pretendard,sans-serif" '
               'font-weight="900" font-size="58" fill="#e60012">KT&amp;G</text>')
    COMPANY = "케이티앤지 (KT&G)"
    LEGOUT  = ('<span class="lg"><span class="sw" style="background:#2b6cb0"></span>월 100만 인출</span>'
               '<span class="lg"><span class="sw" style="background:#d98f2b"></span>월 200만 인출</span>'
               '<span class="lg"><span class="sw" style="background:#c2255c"></span>월 300만 인출</span>')
    _kf = json.load(open(os.path.join(HERE, "assets", "ktng_fires.json")))
    FIRES = [{"hook": "%d. 은퇴원금 <b>%s</b>" % (i + 1, f["hook"]), "payload": f["payload"]}
             for i, f in enumerate(_kf)]
    # PG 기준 썸네일 구조: 제품클러스터(y37·사람이 KT&G 사진)→로고(y54)→마젠타문구(y60)→흰문구(y66)
    THUMB_INIT = ("addText('( KT&G 제품 사진은 사람이 추가 )',50,37,4.2,'#5a6472',0);"
                  "addText('KT&amp;G',50,54,5,'#e60012',0);"
                  "addText('6억으로 은퇴',50,60,7,'#d12e77',0);"
                  "addText('적정 생활비는?',50,66,7,'#ffffff',0);")
elif STOCK == "QQQ":
    OUT     = os.path.join(HERE, "golden_shorts_accum_QQQ.html")
    TITLE   = "golden_shorts_accum_QQQ — 나스닥100 QQQ 통합 쇼츠 에디터 (썸네일+파이어 3)"
    LOGO    = ('<text x="100" y="62" text-anchor="middle" font-family="Pretendard,sans-serif" '
               'font-weight="900" font-size="58" fill="#1b3660">QQQ</text>')
    COMPANY = "나스닥100 (QQQ)"
    LEGOUT  = ('<span class="lg"><span class="sw" style="background:#2b6cb0"></span>월 $1천 인출</span>'
               '<span class="lg"><span class="sw" style="background:#d98f2b"></span>월 $2천 인출</span>'
               '<span class="lg"><span class="sw" style="background:#c2255c"></span>월 $3천 인출</span>')
    _qf = json.load(open(os.path.join(HERE, "assets", "qqq_fires.json")))
    FIRES = [{"hook": "%d. 은퇴원금 <b>%s</b>" % (i + 1, f["hook"]), "payload": f["payload"]}
             for i, f in enumerate(_qf)]
    THUMB_INIT = ("addText('( 나스닥/종목 이미지는 사람이 추가 )',50,37,4,'#5a6472',0);"
                  "addText('QQQ',50,54,6,'#1b3660',0);"
                  "addText('5억으로 은퇴',50,60,7,'#d12e77',0);"
                  "addText('적정 생활비는?',50,66,7,'#ffffff',0);")
else:
    raise SystemExit("unknown SHORTS_STOCK: " + STOCK)

DATA_JS = ("var PRODUCTS=%s,BADGE=%s,PGLOGO=%s,MCDLOGO=%s,JNJLOGO=%s;\n"
           "var FIRES=%s;\nvar PACE=1.0;\n") % (
    json.dumps(assets["PRODUCTS"]), json.dumps(assets["BADGE"]), json.dumps(assets["PGLOGO"]),
    json.dumps(assets["MCDLOGO"]), json.dumps(assets["JNJLOGO"]), json.dumps(FIRES, ensure_ascii=False))

HTML = r'''<!doctype html><html lang=ko><head><meta charset=utf-8>
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>__TITLE__</title>
<style>
@font-face{font-family:'Pretendard';font-weight:100 900;font-style:normal;font-display:swap;src:url('__FONTSRC__') format('woff2')}
*{margin:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{background:#0b0e13;font-family:'Pretendard','Noto Sans KR',sans-serif;display:flex;flex-direction:column;align-items:center;min-height:100vh;padding:8px;color:#e9eef6}
.bar{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;padding:7px;position:sticky;top:0;z-index:50;background:#0b0e13;width:100%;max-width:1180px}
.bar button,.bar label{font:inherit;font-size:13px;font-weight:800;color:#e9eef6;background:#243040;border:1px solid #38465a;border-radius:9px;padding:8px 10px;cursor:pointer;display:inline-flex;align-items:center;gap:5px}
.bar button:active{background:#2f3f54}.bar button.on{background:#1d5fa8;border-color:#2f7be6}
.bar .sep{width:1px;background:#38465a;margin:2px 3px}
.bar input[type=color]{width:30px;height:28px;padding:0;border:none;border-radius:7px;background:none;cursor:pointer}
.bar .dim{opacity:.35;pointer-events:none}
#prev,#next{background:#22304a}#play{background:#6ea8ff;color:#0a0f18}#rmode{background:#7a5a2a}
#saveJson{background:#2e8b57}#loadJson{background:#3a4f8a}#save{background:#1d7a3f;border-color:#2aa15a}
.pdots{display:flex;gap:6px;align-items:center;margin:0 3px}.pdot{width:9px;height:9px;border-radius:50%;background:#2c3a52;cursor:pointer}.pdot.act{background:#6ea8ff}
.nb{display:flex;gap:4px;align-items:center;background:#111a28;padding:4px 8px;border-radius:8px;font-size:12px;font-weight:700}
.nb input{width:48px;font:inherit;background:#0a0f18;color:#fff;border:1px solid #2c3a52;border-radius:5px;padding:3px 5px;text-align:center}
.nb.dim{opacity:.35;pointer-events:none}
#hint{color:#8a97ad;font-size:11.5px;margin:1px 0 5px;text-align:center}
.stagewrap{width:100%;max-width:min(94vw,430px)}
.stage{position:relative;width:100%;aspect-ratio:9/16;background:#000;border-radius:12px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,.5);touch-action:none;container-type:size}
/* --- thumb_editor 요소 --- */
.el{position:absolute;transform:translate(-50%,-50%);cursor:grab;touch-action:none;z-index:10}
.el.sel{outline:2px dashed #49c6ff;outline-offset:3px}
.el.tb{color:#fff;font-weight:900;line-height:1.12;letter-spacing:-.02em;white-space:pre;text-align:center;text-shadow:0 3px 14px rgba(0,0,0,.6);padding:2px 6px}
.el.tb.outlined{-webkit-text-stroke:0.5cqw #000;paint-order:stroke fill;text-shadow:none}
.el.tb.editing{cursor:text;outline:2px solid #49c6ff}
.el.img img{display:block;width:100%;height:auto;pointer-events:none}
.el.tb b{color:#d12e77}   /* GOLDEN: 훅 강조=마젠타 */
#guide{position:absolute;inset:0;pointer-events:none;z-index:9998;display:none}#guide.on{display:block}
#guide .grid{position:absolute;inset:0;background-image:repeating-linear-gradient(0deg,rgba(255,255,255,.13) 0 1px,transparent 1px 10%),repeating-linear-gradient(90deg,rgba(255,255,255,.13) 0 1px,transparent 1px 10%)}
#guide .cx{position:absolute;left:50%;top:0;bottom:0;width:0;border-left:1px dashed rgba(0,229,255,.75)}
#guide .cy{position:absolute;top:50%;left:0;right:0;height:0;border-top:1px dashed rgba(0,229,255,.75)}
/* --- 결과 테이블(5p·정지) --- */
.tablebg{position:absolute;inset:0;background:#000;z-index:1;display:none}
.tablebg .tbl-ttl{position:absolute;left:0;right:0;top:15%;text-align:center;color:#fff;font-weight:900;font-size:4.3cqw;letter-spacing:-.02em;font-family:'Pretendard',sans-serif}
.tablebg .tbl-ttl b{color:#d12e77}
.tablebg .tbl-card{position:absolute;left:5%;right:5%;top:26%;padding:3.1cqw 3.1cqw 2.4cqw;border-radius:2.2cqw;background:#fff url('__PAPER__') center/cover;box-shadow:0 1.8cqw 5cqw rgba(0,0,0,.5)}
.tablebg table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums;font-family:'Pretendard',sans-serif}
.tablebg th,.tablebg td{text-align:right;padding:1.5cqw .7cqw;font-size:2.6cqw;color:#1a1a1a}
.tablebg th{font-size:1.7cqw;font-weight:700;color:#8a857c;border-bottom:.2cqw solid rgba(0,0,0,.25)}
.tablebg td.nm,.tablebg th.nm{text-align:left;font-weight:800}
.tablebg td.nm{font-size:2.5cqw}
.tablebg .sw{display:inline-block;width:1.7cqw;height:1.7cqw;border-radius:.5cqw;margin-right:1.1cqw;vertical-align:-.2cqw}
.tablebg tr+tr td{border-top:.09cqw solid rgba(0,0,0,.12)}
.tablebg td.xr{font-weight:900;color:#111}.tablebg th.xr{color:#111}
.tablebg tr.steady td{background:rgba(43,108,176,.08)}
.tablebg .tbl-note{margin-top:1.8cqw;text-align:center;font-size:1.6cqw;font-weight:500;color:#6b6560}
/* --- 차트 배경(그래프 슬라이드) --- */
.reelbg{position:absolute;inset:0;background:#000;z-index:1;display:none}
.graphbox{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);aspect-ratio:1.78/1;container-type:size}
__RCCSS__
/* ===== GOLDEN 그래프 스펙 (golden_shorts_accum.py 와 동일 유지) ===== */
.tpl-reel{border-radius:0;background:transparent}.tpl-reel .rc-alL{text-anchor:end}
.tpl-reel .rc-card{left:0;right:0;top:0;bottom:0;border-radius:0;background:#fff url('__PAPER__') center/cover}
.tpl-reel .rc-card::before{display:none}
.tpl-reel .rc-chd{left:6.67cqw}   /* 로고+문구 y축 정렬(업로드 잘림 방지) */
.tpl-reel .rc-ln{stroke-width:3.4}
.tpl-reel .rc-ax{font-size:18px;font-weight:400;fill:#000}
.tpl-reel .ytick{stroke:rgba(0,0,0,.22)}
.tpl-reel .rc-hlab{font-size:18px;font-weight:700;fill:#333;text-anchor:start}
.tpl-reel .rc-hline{stroke-width:2.8;stroke:#555}
.tpl-reel .rc-labv{font-size:18px;font-weight:600}
.tpl-reel .rc-base{stroke:#000}
.tpl-reel .rc-tk{font-weight:600;color:#111}.tpl-reel .rc-per{font-weight:400;color:#111}
.tpl-reel,.tpl-reel *,.rc-chart text{font-family:'Pretendard','Noto Sans KR',sans-serif!important}
/* 범례: 그래프 밖(카드 위) */
.legout{position:absolute;left:0;right:0;top:28%;display:flex;justify-content:center;gap:4.5cqw;z-index:5}
.legout .lg{display:flex;align-items:center;gap:1.1cqw;color:#e8e6e0;font-weight:500;font-size:3cqw}
.legout .sw{width:2.8cqw;height:2.8cqw;border-radius:.4cqw}
/* --- clean 렌더 모드: 편집 UI 전부 숨김 --- */
body.render .bar,body.render #hint{display:none}
body.render .el.sel{outline:none}
body.render #guide{display:none!important}
</style></head><body>
<div class="bar" id="bar">
  <button id="prev">◀</button><div class="pdots"></div><button id="next">▶</button>
  <button id="play">⏸ 재생</button>
  <span class="sep"></span>
  <button id="addText">➕텍스트</button><button id="addBadge">🐻배투실</button><button id="addPG">🅿️P&amp;G</button>
  <button id="addProd">📦제품</button><button id="importBtn">🖼임포트</button><input type="file" id="fileIn" accept="image/*" style="display:none">
  <span class="sep"></span>
  <label id="colWrap" class="dim">색<input type="color" id="col" value="#ffffff"></label>
  <button id="outline" class="dim">🔲외곽선</button><button id="minus" class="dim">−</button><button id="plus" class="dim">＋</button>
  <button id="front" class="dim">▲앞</button><button id="del" class="dim">🗑</button>
  <span class="sep"></span>
  <span class="nb dim" id="nbSel">선택 X<input type="number" id="nx" step="0.5">Y<input type="number" id="ny" step="0.5">크기<input type="number" id="ns" step="0.5">색<input type="color" id="nc"></span>
  <span class="sep"></span>
  <button id="guideBtn">📐가이드</button><button id="rmode">👁 렌더</button>
  <button id="saveJson">⬇JSON</button><button id="loadJson">⬆JSON</button><input type="file" id="jsonf" accept="application/json,.json" style="display:none">
  <button id="save">💾PNG</button>
</div>
<div id="hint">탭=선택·드래그=이동 · 숫자박스=정밀 X/Y/크기/색 · 텍스트더블탭=수정 · 👁렌더=편집UI 숨김 · 슬라이드마다 요소 따로</div>
<div class="stagewrap"><div class="stage" id="stage">
  <div class="reelbg">
    <div class="graphbox"><div class="zoom tpl-reel">
      <div class="rc-title"></div>
      <div class="rc-card">
        <div class="rc-chd"><svg class="rc-logo" viewBox="0 0 200 87.021">__LOGO__</svg>
          <div class="rc-txt"><div class="rc-tk">__COMPANY__</div><div class="rc-per">2000년~ 매달 적립 · 배당 재투자</div></div></div>
        <svg class="rc-chart" viewBox="0 0 960 540" preserveAspectRatio="xMidYMid meet" data-rc="">
          <g class="rc-yaxis"></g><g class="rc-xaxis"></g>
          <line class="rc-base"/><line class="rc-hline" x1="70" x2="780" style="display:none"/><text class="rc-hlab" x="780"></text>
          <g class="rc-lines"></g></svg>
      </div></div></div>
    <div class="legout">__LEGOUT__</div>
  </div>
  <div class="tablebg">
    <div class="tbl-ttl">적립식 vs 폭락매수 <b>결과</b></div>
    <div class="tbl-card">
      <table>
      <thead><tr><th class="nm">전략</th><th>최종 평가액</th><th>CAGR</th><th class="xr">XIRR</th></tr></thead>
      <tbody>__TABLE_ROWS__</tbody>
      </table>
      <div class="tbl-note">2000년~ 매달 __MON__ 적립 · 배당 재투자 · 총 투입원금 __INV__</div>
    </div>
  </div>
  <div id="guide"><div class="grid"></div><div class="cx"></div><div class="cy"></div></div>
</div></div>
<script>
__DATA__
__REELANIM__
/* ============ 통합 에디터 엔진 ============ */
var stage=document.getElementById('stage'), reelbg=stage.querySelector('.reelbg'), tablebg=stage.querySelector('.tablebg');
var svg=stage.querySelector('.rc-chart');
var sel=null, z=10, cur=0, NSLIDE=FIRES.length+2;   /* 썸네일 + 그래프N + 테이블 */
function gid(id){return document.getElementById(id);}
function rgb2hex(c){var m=c.match(/\d+/g);if(!m)return '#ffffff';return '#'+m.slice(0,3).map(function(x){return ('0'+parseInt(x).toString(16)).slice(-2);}).join('');}
function isTb(el){return el&&el.classList.contains('tb');}
function elSize(el){return parseFloat(isTb(el)?el.style.fontSize:el.style.width)||(isTb(el)?9:30);}
function setToolState(){var on=!!sel,tb=isTb(sel);
  ['minus','plus','front','del'].forEach(function(id){gid(id).classList.toggle('dim',!on);});
  gid('colWrap').classList.toggle('dim',!tb);gid('outline').classList.toggle('dim',!tb);
  gid('nbSel').classList.toggle('dim',!on);
  if(on){gid('nx').value=(parseFloat(sel.style.left)||50).toFixed(1);gid('ny').value=(parseFloat(sel.style.top)||50).toFixed(1);gid('ns').value=elSize(sel).toFixed(1);
    if(tb){var hx=rgb2hex(getComputedStyle(sel).color);gid('col').value=hx;gid('nc').value=hx;gid('outline').classList.toggle('on',sel.classList.contains('outlined'));}}
}
function select(el){if(sel)sel.classList.remove('sel');sel=el;if(el)el.classList.add('sel');setToolState();}
stage.addEventListener('pointerdown',function(e){if(e.target===stage||e.target===reelbg||e.target.id==='guide'||(e.target.parentNode&&e.target.parentNode.id==='guide'))select(null);});
function pct(el){return {l:parseFloat(el.style.left)||50,t:parseFloat(el.style.top)||50};}
function makeDrag(el){
  el.addEventListener('pointerdown',function(e){
    if(el.classList.contains('editing'))return; e.stopPropagation();select(el);
    var rect=stage.getBoundingClientRect(),p=pct(el),ox=p.l,oy=p.t,sx=e.clientX,sy=e.clientY;
    el.setPointerCapture(e.pointerId);el.style.cursor='grabbing';
    function mv(ev){var dx=(ev.clientX-sx)/rect.width*100,dy=(ev.clientY-sy)/rect.height*100;el.style.left=(ox+dx)+'%';el.style.top=(oy+dy)+'%';gid('nx').value=(ox+dx).toFixed(1);gid('ny').value=(oy+dy).toFixed(1);}
    function up(ev){try{el.releasePointerCapture(e.pointerId);}catch(_){}el.style.cursor='grab';el.removeEventListener('pointermove',mv);el.removeEventListener('pointerup',up);}
    el.addEventListener('pointermove',mv);el.addEventListener('pointerup',up);});
  if(isTb(el)){var last=0;el.addEventListener('pointerup',function(){var now=Date.now();if(now-last<350)edit(el);last=now;});}}
function edit(el){el.classList.add('editing');el.contentEditable=true;el.focus();
  var r=document.createRange();r.selectNodeContents(el);var s=getSelection();s.removeAllRanges();s.addRange(r);
  el.addEventListener('blur',function h(){el.classList.remove('editing');el.contentEditable=false;el.removeEventListener('blur',h);});}
function addText(txt,left,top,size,color,slide){var el=document.createElement('div');el.className='el tb';el.innerHTML=(txt==null?'텍스트':txt);
  el.dataset.s=(slide==null?cur:slide);el.style.left=(left||50)+'%';el.style.top=(top||50)+'%';el.style.fontSize=(size||9)+'cqw';el.style.color=color||'#fff';el.style.zIndex=++z;
  stage.appendChild(el);makeDrag(el);applyVis(el);return el;}
function addImg(src,left,top,w,slide){var el=document.createElement('div');el.className='el img';
  el.dataset.s=(slide==null?cur:slide);el.style.left=(left||50)+'%';el.style.top=(top||50)+'%';el.style.width=(w||30)+'cqw';el.style.zIndex=++z;
  var img=document.createElement('img');img.src=src;el.appendChild(img);stage.appendChild(el);makeDrag(el);applyVis(el);return el;}
function applyVis(el){el.style.display=(+el.dataset.s===cur)?'':'none';}
/* 툴바 */
gid('addText').onclick=function(){var e=addText('새 텍스트',50,50,9,'#fff');select(e);};
gid('addBadge').onclick=function(){select(addImg(BADGE,86,7,22));};
gid('addPG').onclick=function(){select(addImg(PGLOGO,50,70,30));};
gid('addProd').onclick=function(){select(addImg(PRODUCTS,50,45,96));};
gid('importBtn').onclick=function(){gid('fileIn').click();};
gid('fileIn').onchange=function(e){var f=e.target.files&&e.target.files[0];if(!f)return;var r=new FileReader();r.onload=function(){select(addImg(r.result,50,45,70));};r.readAsDataURL(f);this.value='';};
gid('del').onclick=function(){if(sel){sel.remove();select(null);}};
gid('front').onclick=function(){if(sel)sel.style.zIndex=++z;};
gid('col').oninput=function(){if(isTb(sel)){sel.style.color=this.value;gid('nc').value=this.value;}};
gid('outline').onclick=function(){if(isTb(sel)){sel.classList.toggle('outlined');setToolState();}};
gid('guideBtn').onclick=function(){var g=gid('guide');g.classList.toggle('on');this.classList.toggle('on',g.classList.contains('on'));};
function resize(f){if(!sel)return;if(isTb(sel)){var s=parseFloat(sel.style.fontSize)||9;sel.style.fontSize=Math.max(3,s*f)+'cqw';}else{var w=parseFloat(sel.style.width)||30;sel.style.width=Math.max(6,w*f)+'cqw';}gid('ns').value=elSize(sel).toFixed(1);}
gid('plus').onclick=function(){resize(1.1);};gid('minus').onclick=function(){resize(1/1.1);};
/* 숫자박스 → 선택요소 */
gid('nx').oninput=function(){if(sel)sel.style.left=this.value+'%';};
gid('ny').oninput=function(){if(sel)sel.style.top=this.value+'%';};
gid('ns').oninput=function(){if(!sel)return;if(isTb(sel))sel.style.fontSize=this.value+'cqw';else sel.style.width=this.value+'cqw';};
gid('nc').oninput=function(){if(isTb(sel)){sel.style.color=this.value;gid('col').value=this.value;}};
/* PNG (요소만 · 썸네일용) */
gid('save').onclick=function(){
  var W=1080,H=1920,cv=document.createElement('canvas');cv.width=W;cv.height=H;var ctx=cv.getContext('2d');
  ctx.fillStyle='#000';ctx.fillRect(0,0,W,H);
  var els=[].slice.call(stage.querySelectorAll('.el')).filter(function(e){return +e.dataset.s===cur;});
  els.sort(function(a,b){return (parseInt(a.style.zIndex)||0)-(parseInt(b.style.zIndex)||0);});
  var was=sel;if(sel)sel.classList.remove('sel');
  els.forEach(function(el){var cx=(parseFloat(el.style.left)||50)/100*W,cy=(parseFloat(el.style.top)||50)/100*H;
    if(el.classList.contains('img')){var img=el.querySelector('img');var w=(parseFloat(el.style.width)||30)/100*W;var rr=img.getBoundingClientRect();var ratio=(rr.width?rr.height/rr.width:0.5);var h=w*ratio;try{ctx.drawImage(img,cx-w/2,cy-h/2,w,h);}catch(e){}}
    else{var fs=(parseFloat(el.style.fontSize)||9)/100*W;ctx.font="900 "+fs+"px 'Pretendard','Noto Sans KR',sans-serif";ctx.textAlign='center';ctx.textBaseline='middle';var lines=(el.innerText||'').split('\n');var lh=fs*1.12;var y0=cy-(lines.length-1)*lh/2;lines.forEach(function(ln,i){var yy=y0+i*lh;if(el.classList.contains('outlined')){ctx.lineWidth=fs*0.16;ctx.strokeStyle='#000';ctx.lineJoin='round';ctx.strokeText(ln,cx,yy);}ctx.fillStyle=el.style.color||'#fff';ctx.fillText(ln,cx,yy);});}});
  if(was)was.classList.add('sel');
  var a=document.createElement('a');a.download='pg_slide'+cur+'.png';a.href=cv.toDataURL('image/png');a.click();};
/* ============ 슬라이드 / 시퀀스 (GOLDEN 타이밍) ============ */
var auto=false,timer=null,DUR=10080*PACE,HOLD=700,THUMB_HOLD=1250,TABLE_HOLD=5000;
(function(){var pd=document.querySelector('.pdots');for(var i=0;i<NSLIDE;i++){var d=document.createElement('span');d.className='pdot';(function(k){d.onclick=function(){auto=false;setPlayBtn();showSlide(k);};})(i);pd.appendChild(d);}})();
function dots(){document.querySelectorAll('.pdot').forEach(function(d,k){d.classList.toggle('act',k===cur);});}
function showSlide(i){cur=(i+NSLIDE)%NSLIDE;
  stage.querySelectorAll('.el').forEach(function(e){e.style.display=(+e.dataset.s===cur)?'':'none';});
  select(null);dots();if(timer)clearTimeout(timer);
  var LAST=NSLIDE-1;   /* 마지막 = 결과 테이블 */
  if(cur===0){reelbg.style.display='none';tablebg.style.display='none';if(auto)timer=setTimeout(function(){showSlide(1);},THUMB_HOLD);return;}
  if(cur===LAST){reelbg.style.display='none';tablebg.style.display='block';if(auto)timer=setTimeout(function(){showSlide(0);},TABLE_HOLD);return;}
  tablebg.style.display='none';reelbg.style.display='block';var f=FIRES[cur-1];f.payload.yleft=true;
  svg.setAttribute('data-rc',JSON.stringify(f.payload));reelAnim(reelbg);
  if(auto)timer=setTimeout(function(){showSlide(cur+1);},DUR+HOLD);}
function setPlayBtn(){gid('play').textContent=auto?'⏸ 재생':'▶ 재생';}
gid('prev').onclick=function(){auto=false;setPlayBtn();showSlide(cur-1);};
gid('next').onclick=function(){auto=false;setPlayBtn();showSlide(cur+1);};
gid('play').onclick=function(){auto=!auto;setPlayBtn();if(auto)showSlide(cur);else if(timer)clearTimeout(timer);};
/* clean 렌더 모드 */
gid('rmode').onclick=function(){var on=document.body.classList.toggle('render');this.classList.toggle('on',on);if(on)select(null);};
/* ============ JSON 저장/불러오기 ============ */
function serEl(el){return {s:+el.dataset.s,tb:isTb(el),x:el.style.left,y:el.style.top,size:isTb(el)?el.style.fontSize:el.style.width,z:el.style.zIndex,
  html:isTb(el)?el.innerHTML:'',src:isTb(el)?'':el.querySelector('img').src,color:isTb(el)?el.style.color:'',outlined:el.classList.contains('outlined')};}
gid('saveJson').onclick=function(){
  var els=[].slice.call(stage.querySelectorAll('.el')).map(serEl);
  var data={v:2,cur:cur,z:z,els:els};
  var a=document.createElement('a');a.download='pg_editor_layout.json';a.href=URL.createObjectURL(new Blob([JSON.stringify(data)],{type:'application/json'}));document.body.appendChild(a);a.click();a.remove();};
gid('loadJson').onclick=function(){gid('jsonf').click();};
gid('jsonf').onchange=function(e){var f=e.target.files&&e.target.files[0];if(!f)return;var r=new FileReader();r.onload=function(){try{var d=JSON.parse(r.result);
  stage.querySelectorAll('.el').forEach(function(el){el.remove();});z=d.z||10;
  (d.els||[]).forEach(function(o){var el;if(o.tb){el=addText(o.html,parseFloat(o.x),parseFloat(o.y),parseFloat(o.size),o.color,o.s);if(o.outlined)el.classList.add('outlined');}else{el=addImg(o.src,parseFloat(o.x),parseFloat(o.y),parseFloat(o.size),o.s);}el.style.zIndex=o.z;});
  auto=false;setPlayBtn();showSlide(typeof d.cur==='number'?d.cur:0);
  }catch(err){alert('불러오기 실패: '+err.message);}};r.readAsText(f);this.value='';};
/* ============ 초기 배치 (GOLDEN) ============ */
/* 슬라이드0 = 썸네일(편집가능·종목별 내용) */
__THUMB_INIT__
/* 슬라이드1~3 = golden 번호 훅(상단·금액 마젠타) */
FIRES.forEach(function(f,i){addText(f.hook,50,20,7,'#ffffff',i+1);});
select(null);
(document.fonts?document.fonts.ready:Promise.resolve()).then(function(){showSlide(0);});
</script></body></html>'''

# ── 결과 테이블(5p) 데이터: G.FIRES(pg_accum.json)의 steady/smart XIRR·CAGR·최종액 ──
_Fd = G.FIRES
_krw = _Fd[0].get("krw"); _mon = _Fd[0].get("monthly", 1000); _inv = _Fd[0].get("invested", 0)
def _money(v): return (format(int(round(v)), ",") + "원") if _krw else ("$" + format(int(round(v)), ","))
def _pct(x): return "%.1f%%" % (x * 100)
if _Fd and "steady" in _Fd[0]:
    _s = _Fd[0]["steady"]
    _rows = ('<tr class="steady"><td class="nm"><span class="sw" style="background:#2b6cb0"></span>매달 적립식</td>'
             '<td>%s</td><td>%s</td><td class="xr">%s</td></tr>' % (_money(_s["final"]), _pct(_s["cagr"]), _pct(_s["xirr"])))
    for _f in _Fd:
        _m = _f["smart"]
        _rows += ('<tr class="smart"><td class="nm"><span class="sw" style="background:#c2255c"></span>%d%% 하락매수</td>'
                  '<td>%s</td><td>%s</td><td class="xr">%s</td></tr>' % (_f["thr"], _money(_m["final"]), _pct(_m["cagr"]), _pct(_m["xirr"])))
else:
    _rows = ""

out = (HTML.replace('__RCCSS__', G.rc_css).replace('__LOGO__', LOGO)
           .replace('__DATA__', DATA_JS).replace('__REELANIM__', G.NEWRA)
           .replace('__FONTSRC__', G.FONTSRC).replace('__PAPER__', G.paper_uri)
           .replace('__TITLE__', TITLE).replace('__COMPANY__', COMPANY)
           .replace('__LEGOUT__', LEGOUT).replace('__THUMB_INIT__', THUMB_INIT)
           .replace('__TABLE_ROWS__', _rows).replace('__MON__', _money(_mon)).replace('__INV__', _money(_inv)))
open(OUT, "w", encoding="utf-8").write(out)
print("wrote", OUT, "(STOCK=%s)" % STOCK, round(len(out) / 1024), "KB")
