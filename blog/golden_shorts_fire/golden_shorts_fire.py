import json,re,base64,os
HERE=os.path.dirname(os.path.abspath(__file__))   # blog/golden_shorts_fire
BLOG=os.path.abspath(os.path.join(HERE,".."))  # blog
FONTSRC="data:font/woff2;base64,"+base64.b64encode(open(BLOG+"/fonts/PretendardVariable.woff2","rb").read()).decode()
SP=HERE   # 출력 HTML은 이 디렉터리에 생성
pf=open(BLOG+"/PG/deck/pg_final.html",encoding="utf-8").read()
logo=re.search(r'<svg class="rc-logo"[^>]*>(<path d="[^"]+"[^>]*/?>)</svg>',pf).group(1)
rc_css="\n".join(pf.splitlines()[1611:1634])

# ── 누적 고스트 애니메이션(accumAnim) ─────────────────────────────────────────
# 원금 5종을 순차로 그림. 완료분은 회색 고스트로 남고 새 원금이 위에 그려짐.
# x축=이전 최대범위까지 고정→그 뒤 확장 / y축=보이는 창 최대값 동적. 전멸=파산 스탬프·생존=생존 스탬프.
ACCUM=r"""
function accumAnim(root){
  var svg=root.querySelector('.rc-chart'); if(!svg) return;
  var cfg=JSON.parse(svg.getAttribute('data-rc'));
  var W=960,H=960,ML=64,MR=176,MT=132,MB=74,x0=2000,KRW=cfg.krw,P=cfg.principals,DUR=cfg.dur,HOLD=cfg.hold;
  var start=[],acc=0; for(var i=0;i<P.length;i++){start[i]=acc;acc+=DUR[i]+HOLD[i];} var INTRO=cfg.intro||0; var TOTAL=INTRO+acc;
  var endX=P.map(function(p){return p.lines.reduce(function(m,l){var e=l.pts[l.pts.length-1][0];return e>m?e:m;},x0+1);});
  var prevExt=[],mx=0; for(var i=0;i<P.length;i++){prevExt[i]=mx; if(endX[i]>mx)mx=endX[i];}
  var allDead=P.map(function(p){return p.lines.every(function(l){return !l.surv;});});
  var NS='http://www.w3.org/2000/svg';
  function mk(t,a){var e=document.createElementNS(NS,t);for(var k in a)e.setAttribute(k,a[k]);return e;}
  var ya=svg.querySelector('.rc-yaxis'),xa=svg.querySelector('.rc-xaxis'),lg=svg.querySelector('.rc-lines');
  var hl=svg.querySelector('.rc-hline'),hlb=svg.querySelector('.rc-hlab'),_bs=svg.querySelector('.rc-base');
  if(_bs){_bs.setAttribute('x1',ML);_bs.setAttribute('x2',W-MR);_bs.setAttribute('y1',H-MB);_bs.setAttribute('y2',H-MB);}
  var hookEl=root.parentNode.querySelector('.hook')||document.querySelector('.hook');
  var YMAX=1,Rx=x0+1;
  function X(y){return ML+(y-x0)/(Rx-x0)*(W-ML-MR);}
  function Y(v){return (H-MB)-v/YMAX*(H-MB-MT);}
  function nstep(r){var e=Math.pow(10,Math.floor(Math.log10(r))),f=r/e;var n=f<=1?1:f<=2?2:f<=5?5:10;return n*e;}
  function fmtY(v){return KRW?(v>=1e8?(v/1e8).toFixed(1).replace('.0','')+'억':Math.round(v/1e4).toLocaleString()+'만'):('$'+(Math.round(v/10000)*10000).toLocaleString());}
  function yearStep(s){return s<=7?1:s<=16?2:s<=35?5:10;}
  function clip(pts,R){var out=[];for(var i=0;i<pts.length;i++){if(pts[i][0]<=R){out.push(pts[i]);}else{if(out.length){var a=pts[i-1],b=pts[i],fr=(R-a[0])/(b[0]-a[0]);out.push([R,a[1]+(b[1]-a[1])*fr]);}break;}}if(!out.length)out=[pts[0]];return out;}
  // 스탬프(이중테두리) — 파산(라즈베리)·생존(녹색)
  function makeStamp(cx,cy,txt,col){var g=mk('g',{'class':'rc-stamp'});g.style.transformBox='fill-box';g.style.transformOrigin='center';g.style.display='none';g.style.pointerEvents='none';
    var w=296,h=130,o=mk('rect',{x:cx-w/2,y:cy-h/2,width:w,height:h,rx:20});o.style.fill='none';o.style.stroke=col;o.style.strokeWidth='6.5';
    var ii=mk('rect',{x:cx-w/2+13,y:cy-h/2+13,width:w-26,height:h-26,rx:13});ii.style.fill='none';ii.style.stroke=col;ii.style.strokeWidth='3';
    var tx=mk('text',{x:cx,y:cy});tx.setAttribute('text-anchor','middle');tx.setAttribute('dominant-baseline','central');tx.setAttribute('font-size','80');tx.setAttribute('font-weight','900');tx.setAttribute('letter-spacing','14');tx.style.fill=col;tx.textContent=txt;
    g.appendChild(o);g.appendChild(ii);g.appendChild(tx);svg.appendChild(g);return g;}
  var stampBust=makeStamp(520,520,'파산','#c2255c');   // 전멸 페이지
  // 생존 스탬프(녹색·2줄: 생활비 $X / 생존) — 생활비는 원금별로 갱신
  var stampSurv=mk('g',{'class':'rc-stamp'});stampSurv.style.transformBox='fill-box';stampSurv.style.transformOrigin='center';stampSurv.style.display='none';stampSurv.style.pointerEvents='none';
  (function(){var cx=460,cy=500,w=360,h=176,col='#2b8a3e';
    var o=mk('rect',{x:cx-w/2,y:cy-h/2,width:w,height:h,rx:22});o.style.fill='none';o.style.stroke=col;o.style.strokeWidth='6.5';
    var ii=mk('rect',{x:cx-w/2+13,y:cy-h/2+13,width:w-26,height:h-26,rx:14});ii.style.fill='none';ii.style.stroke=col;ii.style.strokeWidth='3';
    var e=mk('text',{x:cx,y:cy-40});e.setAttribute('text-anchor','middle');e.setAttribute('dominant-baseline','central');e.setAttribute('font-size','34');e.setAttribute('font-weight','800');e.style.fill=col;e.textContent='생활비';
    var t=mk('text',{x:cx,y:cy+33});t.setAttribute('text-anchor','middle');t.setAttribute('dominant-baseline','central');t.setAttribute('font-size','64');t.setAttribute('font-weight','900');t.setAttribute('letter-spacing','10');t.style.fill=col;t.textContent='생존';
    stampSurv.appendChild(o);stampSurv.appendChild(ii);stampSurv.appendChild(e);stampSurv.appendChild(t);stampSurv._exp=e;})();
  svg.appendChild(stampSurv);
  // 훅 스탬프: "생존 or 파산"(생존 녹색·or 회색·파산 빨강) — 인트로 전용
  var stampHook=mk('g',{'class':'rc-stamp'});stampHook.style.transformBox='fill-box';stampHook.style.transformOrigin='center';stampHook.style.display='none';stampHook.style.pointerEvents='none';
  (function(){var cx=480,cy=500,w=474,h=150;
    function tsp(tx,fl){var s=mk('tspan',{});s.style.fill=fl;s.textContent=tx;return s;}
    var o=mk('rect',{x:cx-w/2,y:cy-h/2,width:w,height:h,rx:20});o.style.fill='none';o.style.stroke='#3a4150';o.style.strokeWidth='6.5';
    var ii=mk('rect',{x:cx-w/2+13,y:cy-h/2+13,width:w-26,height:h-26,rx:13});ii.style.fill='none';ii.style.stroke='#3a4150';ii.style.strokeWidth='3';
    var t=mk('text',{x:cx,y:cy});t.setAttribute('text-anchor','middle');t.setAttribute('dominant-baseline','central');t.setAttribute('font-size','58');t.setAttribute('font-weight','900');t.setAttribute('letter-spacing','3');
    t.appendChild(tsp('생존','#2b8a3e'));t.appendChild(tsp(' or ','#8a929e'));t.appendChild(tsp('파산','#c2255c'));
    stampHook.appendChild(o);stampHook.appendChild(ii);stampHook.appendChild(t);})();
  svg.appendChild(stampHook);
  function draw(t){
    var intro=t<INTRO, i, lt, pr;
    if(intro){i=P.length-1;lt=DUR[i];pr=1;}   /* 훅: 마지막 원금 기준 전체 라인 표시 */
    else{var tt=t-INTRO;i=0;while(i<P.length-1&&tt>=start[i+1])i++;lt=tt-start[i];pr=lt<=DUR[i]?lt/DUR[i]:1;}
    var R=(x0+0.3)+pr*(endX[i]-(x0+0.3));
    Rx=Math.max(R,prevExt[i]);
    var vmax=P[i].hline?P[i].hline.v:0, ghosts=[], active=[];
    for(var g=0;g<i;g++){P[g].lines.forEach(function(l){ghosts.push(l);l.pts.forEach(function(q){if(q[1]>vmax)vmax=q[1];});});}
    P[i].lines.forEach(function(l){var a=clip(l.pts,R);active.push({l:l,arr:a});a.forEach(function(q){if(q[1]>vmax)vmax=q[1];});});
    YMAX=Math.max(vmax*1.15,1);
    lg.innerHTML='';ya.innerHTML='';xa.innerHTML='';
    var step=nstep(YMAX/4);
    for(var v=step;v<=YMAX+1;v+=step){if(P[i].hline&&Math.abs(v-P[i].hline.v)<step*0.25)continue;var yy=Y(v);ya.appendChild(mk('line',{x1:ML,y1:yy,x2:W-MR,y2:yy,'class':'ytick'}));var tx=mk('text',{x:ML+2,y:yy-7,'class':'rc-ax rc-al'});tx.setAttribute('font-size','27');tx.setAttribute('text-anchor','start');tx.textContent=fmtY(v);ya.appendChild(tx);}
    var span=Rx-x0,st=yearStep(span),first=Math.ceil(x0/st)*st;
    for(var yr=first;yr<=Rx+0.01;yr+=st){var t2=mk('text',{x:X(yr),y:H-MB+22,'class':'rc-ax rc-axx'});t2.textContent=String(yr);xa.appendChild(t2);}
    ghosts.forEach(function(l){var d='M'+l.pts.map(function(q){return X(q[0]).toFixed(1)+' '+Y(q[1]).toFixed(1);}).join(' L');var p=mk('path',{d:d,'class':'rc-ln'});p.style.stroke='#bdb8b0';p.style.strokeWidth='3';p.style.opacity=intro?'0.55':'0.7';lg.appendChild(p);
      if(l.surv&&!intro){var gp=l.pts[l.pts.length-1],gx=X(gp[0]),gy=Y(gp[1]);var gt=mk('text',{x:Math.min(gx+9,W-MR+2),y:gy+6,'class':'rc-lab'});gt.setAttribute('font-size','23');gt.setAttribute('text-anchor','start');gt.style.fill='#8a857c';gt.textContent=l.plab;lg.appendChild(gt);}});
    var _lab=[];
    active.forEach(function(o){var d='M'+o.arr.map(function(q){return X(q[0]).toFixed(1)+' '+Y(q[1]).toFixed(1);}).join(' L');var p=mk('path',{d:d,'class':'rc-ln'});p.style.stroke=intro?'#bdb8b0':o.l.c;p.style.strokeWidth=intro?'3':'4';if(intro)p.style.opacity='0.55';lg.appendChild(p);
      if(intro)return;   /* 훅: 점·라벨 없음(회색 미스터리) */
      var lp=o.arr[o.arr.length-1],ex=X(lp[0]),ey=Y(lp[1]);var dot=mk('circle',{cx:ex,cy:ey,r:4.5});dot.style.fill=o.l.c;lg.appendChild(dot);
      var ended=lp[0]>=o.l.pts[o.l.pts.length-1][0]-1e-6;
      var val=o.l.surv?fmtY(lp[1]):(ended?(KRW?'₩0':'$0'):fmtY(lp[1]));   /* 생존선=현재 가격 / 파산선=$0 */
      var tv=mk('text',{x:Math.min(ex+9,W-MR+2),y:ey+6,'class':'rc-lab rc-labv'});tv.setAttribute('font-size','23');tv.setAttribute('text-anchor','start');tv.style.fill=o.l.c;tv.textContent=val;lg.appendChild(tv);_lab.push({tv:tv,x:ex+9,y0:ey+6});});
    _lab.sort(function(a,b){return a.x-b.x;});var pxr=-1e9,row=0;for(var k=0;k<_lab.length;k++){var b=_lab[k];row=(b.x-pxr<92)?row+1:0;b.tv.setAttribute('y',b.y0-row*30);pxr=b.x;}
    if(intro){hl.style.display='none';hlb.style.opacity='0';}
    else{var hy=Y(P[i].hline.v);hl.style.display='';hl.setAttribute('x1',ML);hl.setAttribute('x2',W-MR);hl.setAttribute('y1',hy);hl.setAttribute('y2',hy);hlb.setAttribute('x',ML+4);hlb.setAttribute('y',hy-9);hlb.style.opacity='1';hlb.textContent=P[i].hline.label;}
    var stampG=allDead[i]?stampBust:stampSurv, stampOff=allDead[i]?stampSurv:stampBust;
    stampOff.style.display='none';
    if(!allDead[i]&&stampSurv._exp)stampSurv._exp.textContent='생활비 '+(P[i].survmo||'');
    if(!intro&&lt>DUR[i]){var sp=Math.max(0,Math.min(1,(lt-DUR[i])/450));var e3=1-Math.pow(1-sp,3);stampG.style.display='';stampG.style.opacity=Math.min(1,sp*1.8).toFixed(3);stampG.style.transform='rotate(-12deg) scale('+(1.55-0.55*e3).toFixed(3)+')';}
    else{stampG.style.display='none';}
    if(intro){var hsp=Math.min(1,t/300),he=1-Math.pow(1-hsp,3);stampHook.style.display='';stampHook.style.opacity=Math.min(1,hsp*1.6).toFixed(3);stampHook.style.transform='rotate(-9deg) scale('+(1.4-0.4*he).toFixed(3)+')';}
    else{stampHook.style.display='none';}
    if(hookEl)hookEl.innerHTML=intro?'30년 뒤, <b>살아남는 원금</b>은?':P[i].hook;
  }
  var t0=null;function run(ts){if(!svg.isConnected)return;if(t0===null)t0=ts;var t=ts-t0;if(t>TOTAL)t=TOTAL;draw(t);if(t<TOTAL)requestAnimationFrame(run);}
  draw(0);requestAnimationFrame(run);
}
"""

CSS="""@font-face{font-family:'Pretendard';font-weight:100 900;src:url('%s') format('woff2')}
*{margin:0;box-sizing:border-box}body{width:1080px;height:1920px;background:#000;font-family:'Pretendard',sans-serif;position:relative;overflow:hidden}
.graphbox{position:absolute;left:0;right:0;top:50%%;transform:translateY(-50%%);aspect-ratio:1/1;container-type:size}
.toplogo{position:absolute;top:14%%;left:50%%;transform:translateX(-50%%);height:132px;width:auto;filter:brightness(0) invert(1)}   /* 상단 Invesco 로고(흰색) */
%s
.tpl-reel{background:transparent}
.tpl-reel .rc-card{left:0;right:0;top:0;bottom:0;border-radius:0;background:#fff url('%s') center/cover}
.tpl-reel .rc-card::before{display:none}.tpl-reel .rc-alL{text-anchor:end}
.tpl-reel .rc-chd{left:6.67cqw;top:3cqw;gap:2.4cqw}   /* 로고+문구를 그래프 y축(ML=64→6.67cqw)에 정렬, 업로드 잘림 방지 */
.tpl-reel .rc-logo{height:6.8cqw}   /* 헤더 2배(3.4→6.8cqw) */
.tpl-reel .rc-ln{stroke-width:3.4}.tpl-reel .rc-ax{font-size:27px;font-weight:400;fill:#000}
.tpl-reel .ytick{stroke:rgba(0,0,0,.22)}
.tpl-reel .rc-hlab{font-size:27px;font-weight:700;fill:#333;text-anchor:start}.tpl-reel .rc-hline{stroke-width:2.8;stroke:#555}
.tpl-reel .rc-labv{font-size:27px;font-weight:600}.tpl-reel .rc-base{stroke:#000}
.tpl-reel .rc-tk{font-weight:600;color:#111;font-size:4cqw}.tpl-reel .rc-per{font-weight:400;color:#111;font-size:2.6cqw}   /* 헤더 2배 */
.tpl-reel,.tpl-reel *,.rc-chart text,.legout,.legout *{font-family:'Pretendard',sans-serif!important}
.hook{position:absolute;left:0;right:0;top:80%%;text-align:center;color:#fff;font-weight:900;font-size:7cqw;letter-spacing:-.02em}.hook b{color:#d12e77}   /* 그래프 카드 바로 아래 */
.legout{position:absolute;left:0;right:0;top:24.5%%;display:flex;justify-content:center;gap:4.5cqw;z-index:5}
.legout .lg{display:flex;align-items:center;gap:1.1cqw;color:#333;font-weight:700;font-size:3cqw}
.legout .sw{width:2.8cqw;height:2.8cqw;border-radius:.4cqw}"""

# 누적 그래프 1장(연속). hook은 accumAnim이 원금별로 갱신. data-rc=ACCUM_DATA.
TMPL="""<!doctype html><meta charset=utf-8><style>%s</style>
<svg class="toplogo" viewBox="__LOGOVB__">__LOGO__</svg>
<div class="graphbox"><div class="zoom tpl-reel"><div class="rc-title"></div>
<div class="rc-card">
<svg class="rc-chart" viewBox="0 0 960 960" preserveAspectRatio="xMidYMid meet" data-rc='%s'>
<g class="rc-yaxis"></g><g class="rc-xaxis"></g><line class="rc-base"/><line class="rc-hline" x1="70" x2="780" style="display:none"/><text class="rc-hlab" x="780"></text><g class="rc-lines"></g></svg>
</div></div></div>
<div class="hook"></div>
<div class="legout">__LEGEND__</div>
<script>%s</script>"""

# paper texture base64 (재사용)
paper_b64=open(HERE+"/assets/paper_b64.txt").read().strip()
paper_uri="data:image/jpeg;base64,"+paper_b64 if not paper_b64.startswith("data:") else paper_b64

CSS_F=CSS%(FONTSRC,rc_css,paper_uri)
CMAP={"#1f6fe0":"#2b6cb0","#e0821c":"#d98f2b","#e01e37":"#c2255c"}

# 파이어 데이터(원금 5종) — 엔진 산출(gen_fires.py). 편집기·테이블 생성기도 재사용.
_STOCK=os.environ.get("SHORTS_STOCK","PG")
_PREF={"PG":"pg","QQQ":"qqq","KTNG":"ktng"}.get(_STOCK,"pg")
FIRES=json.load(open(HERE+"/assets/%s_fires.json"%_PREF))   # [{amt, hook(순수 금액), payload}]
_KRW=bool(FIRES[0]["payload"].get("krw"))

# 종목별 헤더(로고·회사·부제)
SUB="2000년 은퇴 · 물가반영 · 월 인출액별"
if _STOCK=="QQQ":
    _qlg="data:image/png;base64,"+base64.b64encode(open(HERE+"/assets/qqq_logo.png","rb").read()).decode()
    LOGO='<image href="%s" x="0" y="0" width="1280" height="1089"/>'%_qlg; LOGOVB="0 0 1280 1089"; COMPANY="나스닥100 (QQQ) · 운용 Invesco"
elif _STOCK=="KTNG":
    LOGO=logo; LOGOVB="0 0 200 87.021"; COMPANY="KT&G (033780)"
else:
    LOGO=logo; LOGOVB="0 0 200 87.021"; COMPANY="프록터 앤 갬블 (PG)"

# 범례(월 인출 3종) — 통화별
if _KRW:
    _LG=[("#2b6cb0","월 100만 인출"),("#d98f2b","월 200만 인출"),("#c2255c","월 300만 인출")]
else:
    _LG=[("#2b6cb0","월 $1천 인출"),("#d98f2b","월 $2천 인출"),("#c2255c","월 $3천 인출")]
LEGEND="".join('<span class="lg"><span class="sw" style="background:%s"></span>%s</span>'%(c,t) for c,t in _LG)

# ── 누적 그래프 데이터(원금별: 생존시 최대인출 1선만, 전멸시 3선 전부) ──
MOAMT=["100만원","200만원","300만원"] if _KRW else ["$1,000","$2,000","$3,000"]   # 월 인출액(생존 스탬프용)
def _plab(v):   # 원금 컴팩트 표기(고스트 라벨)
    if _KRW: return ("%.0f억"%(v/1e8)) if v>=1e8 else ("%d만"%round(v/1e4))
    return ("$%dM"%round(v/1e6)) if v>=1e6 else ("$%dK"%round(v/1e3))

def build_principals():
    ps=[]
    for idx,f in enumerate(FIRES):
        lines=f["payload"]["lines"]                                # 순서: 월1천·2천·3천(오름차순)
        survs=[j for j,l in enumerate(lines) if l.get("surv")]
        # 모든 인출선 전부 그림(생존선+높은인출 파산선). 생존선만 고스트에 원금 라벨(plab).
        out=[{"c":l["c"],"surv":l.get("surv",False),"pts":l["pts"],
              "plab":(_plab(f["amt"]) if l.get("surv") else "")} for l in lines]
        ps.append({"hook":"%d. 은퇴원금 <b>%s</b>"%(idx+1,f["hook"]),
                   "hline":f["payload"]["hline"],"lines":out,
                   "survmo":(MOAMT[max(survs)] if survs else "")})   # 생존 스탬프 생활비=최대 생존 인출
    return ps

ACCUM_DATA={"krw":_KRW,"principals":build_principals(),
            "dur":[4500,5500,8000,7000,9000],"hold":[1100,1100,700,700,2200],
            "intro":3000}   # 썸네일 직후: 전체 라인 회색 훅(3초·생존 or 파산 스탬프) → 이후 누적으로 전개
ACCUM_TOTAL_MS=ACCUM_DATA.get("intro",0)+sum(ACCUM_DATA["dur"])+sum(ACCUM_DATA["hold"])   # build 녹화 길이 참조

if __name__=="__main__":   # 직접 실행 시에만 쇼츠 HTML 생성(모듈 import 시 부작용 없음)
    _hdr=(TMPL.replace("__LOGOVB__",LOGOVB).replace("__LOGO__",LOGO)
              .replace("__COMPANY__",COMPANY).replace("__SUB__",SUB).replace("__LEGEND__",LEGEND))
    data=json.dumps(ACCUM_DATA,ensure_ascii=False).replace("'","&#39;")
    html=_hdr%(CSS_F,data,ACCUM)
    open("%s/golden_shorts_fire_1.html"%SP,"w").write(html)
    print("wrote golden_shorts_fire_1.html (누적 고스트 · 원금 %d종 · %.1fs)"%(len(FIRES),ACCUM_TOTAL_MS/1000))
