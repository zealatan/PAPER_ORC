import json,re,base64,os
HERE=os.path.dirname(os.path.abspath(__file__))   # blog/golden_shorts_fire
BLOG=os.path.abspath(os.path.join(HERE,".."))  # blog
FONTSRC="data:font/woff2;base64,"+base64.b64encode(open(BLOG+"/fonts/PretendardVariable.woff2","rb").read()).decode()
SP=HERE   # 출력 HTML은 이 디렉터리에 생성
pf=open(BLOG+"/PG/deck/pg_final.html",encoding="utf-8").read()
logo=re.search(r'<svg class="rc-logo"[^>]*>(<path d="[^"]+"[^>]*/?>)</svg>',pf).group(1)
rc_css="\n".join(pf.splitlines()[1611:1634])

# ── 새 애니메이션: 디자인/DOM/클래스/색/폰트/라벨 전부 동일, x축 도메인만 시간에 따라 확장(재스케일) ──
NEWRA=r"""
function reelAnim(root){
  var svg=root.querySelector('.rc-chart'); if(!svg) return;
  var cfg; try{ cfg=JSON.parse(svg.getAttribute('data-rc')); }catch(e){ return; }
  var _vb=(svg.getAttribute('viewBox')||'0 0 960 540').split(/\s+/).map(Number),W=_vb[2],H=_vb[3];
  var ML=64,MR=cfg.yleft?176:150,MT=150,MB=66,x0=2000,YMAX=cfg.ymax,TIP=cfg.tip,YLX=cfg.yleft;
  var x1=cfg.lines.reduce(function(m,l){var e=l.pts[l.pts.length-1][0];return e>m?e:m;},x0+1);   /* 페이지별 끝점=마지막 데이터점(조기 전멸 페이지는 빈 미래로 슬라이드하지 않음) */
  var INIT=0.3;                              /* 시작 시 보이는 초기 창(년) — 2000년부터 시작 */
  var WIN=14;                                /* 슬라이딩 창 폭(년): R-WIN 이전(오래된) 데이터는 왼쪽으로 지나감 */
  function PADf(prog){return 1.4*(1-prog)+0.05;} /* 오른쪽 여유(년): 초반 넓게→끝에서 0 (마지막 프레임=기존 정적축과 동일) */
  function Xr(y,R,prog){var L=Math.max(x0,R-WIN);return ML+(y-L)/((R+PADf(prog))-L)*(W-ML-MR);}   /* 무빙슬라이드: 창 [L,R]이 오른쪽으로 흐름(오래된 데이터 왼쪽 이탈) */
  function Y(v){return (H-MB)-v/YMAX*(H-MB-MT);}
  function nstep(r){var e=Math.pow(10,Math.floor(Math.log10(r))),f=r/e;var n=f<=1?1:f<=2?2:f<=5?5:10;return n*e;}
  function fmt(v){if(cfg.krw){return v>=1e8?(v/1e8).toFixed(1)+'억':Math.round(v/1e4).toLocaleString()+'만';}return '$'+(Math.round(v/10000)*10000).toLocaleString();}
  var NS='http://www.w3.org/2000/svg';
  function mk(t,a){var e=document.createElementNS(NS,t);for(var k in a)e.setAttribute(k,a[k]);return e;}
  var ya=svg.querySelector('.rc-yaxis'),xa=svg.querySelector('.rc-xaxis'),lg=svg.querySelector('.rc-lines');
  xa.innerHTML='';lg.innerHTML='';
  function drawYAxis(){   /* y축 눈금/라벨 — 매 프레임 재생성(YMAX 동적) */
    ya.innerHTML='';
    var step=nstep(YMAX/4);
    for(var v=step;v<=YMAX+1;v+=step){
      if(cfg.hline&&Math.abs(v-cfg.hline.v)<step*0.25)continue;
      if(cfg.ylabelmin&&v<cfg.ylabelmin)continue;
      var y=Y(v);ya.appendChild(mk('line',{x1:ML,y1:y,x2:W-MR,y2:y,'class':'ytick'}));
      var t=mk('text',{x:ML+2,y:y-7,'class':'rc-ax rc-al'});t.setAttribute('text-anchor','start');t.setAttribute('font-size','18');
      t.textContent=cfg.krw?(v>=1e8?Math.round(v/1e8)+'억':Math.round(v/1e4).toLocaleString()+'만'):('$'+v.toLocaleString());ya.appendChild(t);
    }
  }
  var _bs=svg.querySelector('.rc-base');if(_bs){_bs.setAttribute('y1',H-MB);_bs.setAttribute('y2',H-MB);_bs.setAttribute('x1',ML);_bs.setAttribute('x2',W-MR);}
  var hl=svg.querySelector('.rc-hline'),hlb=svg.querySelector('.rc-hlab');
  var ELS=cfg.lines.map(function(l,_li){
    var p=mk('path',{'class':'rc-ln'});p.style.stroke=l.c;if(l.dash)p.style.strokeDasharray='2 5';
    var dot=mk('circle',{r:4.5});dot.style.fill=l.c;
    var tt=mk('text',{'class':'rc-lab rc-labt'});tt.style.fill=l.c;
    var tv=mk('text',{'class':'rc-lab rc-labv'});tv.style.fill=l.c;
    lg.appendChild(p);lg.appendChild(dot);lg.appendChild(tt);lg.appendChild(tv);
    return {p:p,dot:dot,tt:tt,tv:tv,l:l,li:_li,endX:l.pts[l.pts.length-1][0]};});
  var HLY=null;   /* 은퇴원금 라벨 충돌판정용 — draw()에서 매 프레임 갱신 */
  var _dep=ELS.filter(function(e){return !e.l.surv;}).map(function(e){return {e:e,x:e.endX};});
  _dep.forEach(function(d){d.e.side=_dep.some(function(o){return o!==d&&o.x>d.x&&o.x-d.x<5;})?'left':'right';});
  function yearStep(span){return span<=7?1:span<=16?2:span<=35?5:10;}
  function drawXAxis(R,prog){
    xa.innerHTML='';
    var L=Math.max(x0,R-WIN), span=R-L, st=yearStep(span), first=Math.ceil(L/st)*st;   /* 슬라이딩 창 [L,R] 라벨 — 오래된 연도는 왼쪽으로 이탈 */
    for(var yr=first; yr<=R+0.01; yr+=st){
      var t=mk('text',{x:Xr(yr,R,prog),y:H-MB+22,'class':'rc-ax rc-axx'});
      t.textContent=String(yr);
      xa.appendChild(t);
    }
  }
  function clipX(pts,R){
    if(R<=pts[0][0]) return {arr:[pts[0]],ex:pts[0][0],ey:pts[0][1],ended:false};
    var last=pts[pts.length-1];
    if(R>=last[0]) return {arr:pts,ex:last[0],ey:last[1],ended:true};
    for(var i=0;i<pts.length-1;i++){
      if(pts[i][0]<=R && R<pts[i+1][0]){
        var fr=(R-pts[i][0])/(pts[i+1][0]-pts[i][0]);
        var ey=pts[i][1]+(pts[i+1][1]-pts[i][1])*fr;
        var arr=pts.slice(0,i+1); arr.push([R,ey]);
        return {arr:arr,ex:R,ey:ey,ended:false};
      }
    }
    return {arr:pts,ex:last[0],ey:last[1],ended:true};
  }
  function draw(prog){
    var R=(x0+INIT)+prog*(x1-(x0+INIT));
    drawXAxis(R,prog);
    /* y축 동적 재스케일: 보이는 창 [_L,R]의 최대값(+은퇴원금 hline)으로 매 프레임 재계산 */
    var _L=Math.max(x0,R-WIN);
    var vmax=cfg.hline?cfg.hline.v:0;
    ELS.forEach(function(e){var rr=clipX(e.l.pts,R);rr.arr.forEach(function(q){if(q[0]>=_L-0.01&&q[1]>vmax)vmax=q[1];});if(rr.ey>vmax)vmax=rr.ey;});
    YMAX=Math.max(vmax*1.15,1);
    drawYAxis();
    if(cfg.hline){var hy=Y(cfg.hline.v);hl.style.display='';hl.setAttribute('y1',hy);hl.setAttribute('y2',hy);hlb.setAttribute('x',ML+4);hlb.setAttribute('y',hy-9);hlb.textContent=cfg.hline.label;HLY=hy;}else{hl.style.display='none';HLY=null;}
    var _hlhide=false;
    var _bank=[];   /* 파산(바닥선) 라벨 — 가로 겹침 회피용 수집 */
    ELS.forEach(function(e){
      var r=clipX(e.l.pts,R);
      if(r.ended&&!e.l.surv&&r.ex<_L){e.p.setAttribute('d','');e.dot.style.display='none';e.tv.textContent='';e.tt.textContent='';return;}   /* 파산점이 창밖 이탈 → 완전 숨김 */
      e.dot.style.display='';
      var ex=Xr(r.ex,R,prog),ey=Y(r.ey);
      var _a=r.arr,_a2=[];   /* 창 왼쪽(오래된) 구간 클립 — 경계 _L에서 보간 진입 */
      for(var _k=0;_k<_a.length;_k++){var q=_a[_k];
        if(q[0]>=_L){ if(_a2.length===0&&_k>0){var pv=_a[_k-1],fr=(_L-pv[0])/(q[0]-pv[0]);_a2.push([_L,pv[1]+(q[1]-pv[1])*fr]);} _a2.push(q); } }
      if(_a2.length===0)_a2=[_a[_a.length-1]];
      var d='M'+_a2.map(function(q){return Xr(q[0],R,prog).toFixed(1)+' '+Y(q[1]).toFixed(1);}).join(' L');
      e.p.setAttribute('d',d);e.dot.setAttribute('cx',ex);e.dot.setAttribute('cy',ey);
      var running=!(r.ended&&!e.l.surv);
      var val=running?fmt(r.ey):e.l.end;
      e.tt.textContent='';
      var _sd=e.side||'right';
      var lx=_sd==='left'?(ex-9):Math.min(ex+9,W-MR+2);
      e.tv.setAttribute('text-anchor',_sd==='left'?'end':'start');
      e.tv.setAttribute('x',lx);
      e.tv.setAttribute('y',ey+6);
      e.tv.setAttribute('font-size','15');
      e.tv.textContent=val;   /* 데이터 선 라벨은 항상 표시 */
      if(!running){_bank.push({tv:e.tv,x:lx,y0:ey+6});}   /* 파산 라벨(바닥선) 수집(좌·우 무관) */
      if(HLY!=null&&Math.abs(ey-HLY)<42&&lx>560&&lx<840) _hlhide=true;  /* 선 라벨과 겹치면 은퇴원금 라벨을 숨김 */
    });
    /* 파산 라벨 가로 겹침 회피: x가 가까운(<72) 라벨은 위로 20px씩 계단식 이동 */
    _bank.sort(function(a,b){return a.x-b.x;});
    var _pxr=-1e9,_row=0;
    for(var _bi=0;_bi<_bank.length;_bi++){var _b=_bank[_bi];_row=(_b.x-_pxr<72)?_row+1:0;_b.tv.setAttribute('y',_b.y0-_row*20);_pxr=_b.x;}
    if(hlb) hlb.style.opacity='1';  /* 좌측 y축 위치로 이동 → 우측 끝점값과 겹치지 않으므로 항상 표시 */
  }
  var DUR=10080*(typeof PACE!=='undefined'?PACE:1),start=null;   /* 2배+20% 느리게(4200→8400→10080) */
  function run(ts){if(!svg.isConnected)return;if(!start)start=ts;var p=Math.min(1,(ts-start)/DUR);draw(p);if(p<1)requestAnimationFrame(run);}
  draw(0);requestAnimationFrame(run);
}
"""

CSS="""@font-face{font-family:'Pretendard';font-weight:100 900;src:url('%s') format('woff2')}
*{margin:0;box-sizing:border-box}body{width:1080px;height:1920px;background:#000;font-family:'Pretendard',sans-serif;position:relative;overflow:hidden}
.graphbox{position:absolute;left:0;right:0;top:50%%;transform:translateY(-50%%);aspect-ratio:1.78/1;container-type:size}
%s
.tpl-reel{background:transparent}
.tpl-reel .rc-card{left:0;right:0;top:0;bottom:0;border-radius:0;background:#fff url('%s') center/cover}
.tpl-reel .rc-card::before{display:none}.tpl-reel .rc-alL{text-anchor:end}
.tpl-reel .rc-chd{left:6.67cqw}   /* 로고+문구를 그래프 y축(ML=64→6.67cqw)에 정렬, 업로드 잘림 방지 */
.tpl-reel .rc-ln{stroke-width:3.4}.tpl-reel .rc-ax{font-size:18px;font-weight:400;fill:#000}
.tpl-reel .ytick{stroke:rgba(0,0,0,.22)}
.tpl-reel .rc-hlab{font-size:18px;font-weight:700;fill:#333;text-anchor:start}.tpl-reel .rc-hline{stroke-width:2.8;stroke:#555}
.tpl-reel .rc-labv{font-size:18px;font-weight:600}.tpl-reel .rc-base{stroke:#000}
.tpl-reel .rc-tk{font-weight:600;color:#111}.tpl-reel .rc-per{font-weight:400;color:#111}
.tpl-reel,.tpl-reel *,.rc-chart text,.legout,.legout *{font-family:'Pretendard',sans-serif!important}
.hook{position:absolute;left:0;right:0;top:20%%;text-align:center;color:#fff;font-weight:900;font-size:7cqw;letter-spacing:-.02em}.hook b{color:#d12e77}
.legout{position:absolute;left:0;right:0;top:28%%;display:flex;justify-content:center;gap:4.5cqw;z-index:5}
.legout .lg{display:flex;align-items:center;gap:1.1cqw;color:#e8e6e0;font-weight:500;font-size:3cqw}
.legout .sw{width:2.8cqw;height:2.8cqw;border-radius:.4cqw}"""

TMPL="""<!doctype html><meta charset=utf-8><style>%s</style>
<div class="graphbox"><div class="zoom tpl-reel"><div class="rc-title"></div>
<div class="rc-card"><div class="rc-chd"><svg class="rc-logo" viewBox="__LOGOVB__">__LOGO__</svg>
<div class="rc-txt"><div class="rc-tk">__COMPANY__</div><div class="rc-per">__SUB__</div></div></div>
<svg class="rc-chart" viewBox="0 0 960 540" preserveAspectRatio="xMidYMid meet" data-rc='%s'>
<g class="rc-yaxis"></g><g class="rc-xaxis"></g><line class="rc-base"/><line class="rc-hline" x1="70" x2="780" style="display:none"/><text class="rc-hlab" x="780"></text><g class="rc-lines"></g></svg>
</div></div></div>
<div class="hook">%s 은퇴원금 <b>%s</b></div>
<div class="legout">__LEGEND__</div>
<script>var PACE=1;%s;(document.fonts?document.fonts.ready:Promise.resolve()).then(function(){reelAnim(document.querySelector('.graphbox'));});</script>"""

# paper texture base64 (재사용)
paper_b64=open(HERE+"/assets/paper_b64.txt").read().strip()
paper_uri="data:image/jpeg;base64,"+paper_b64 if not paper_b64.startswith("data:") else paper_b64

CSS_F=CSS%(FONTSRC,rc_css,paper_uri)
CMAP={"#1f6fe0":"#2b6cb0","#e0821c":"#d98f2b","#e01e37":"#c2255c"}

# 파이어 데이터(원금 5종) — 엔진 산출(gen_fires.py). 편집기 생성기도 G.FIRES 재사용.
_STOCK=os.environ.get("SHORTS_STOCK","PG")
_PREF={"PG":"pg","QQQ":"qqq","KTNG":"ktng"}.get(_STOCK,"pg")
FIRES=json.load(open(HERE+"/assets/%s_fires.json"%_PREF))   # [{amt, hook(순수 금액), payload}]
_KRW=bool(FIRES[0]["payload"].get("krw"))

# 종목별 헤더(로고·회사·부제) — 편집기 브랜치와 동일 값
SUB="2000년 은퇴 · 물가반영 · 월 인출액별"
if _STOCK=="QQQ":
    _qlg="data:image/png;base64,"+base64.b64encode(open(HERE+"/assets/qqq_logo.png","rb").read()).decode()
    LOGO='<image href="%s" x="0" y="0" width="1280" height="1089"/>'%_qlg; LOGOVB="0 0 1280 1089"; COMPANY="나스닥100 (QQQ) · 운용 Invesco"
elif _STOCK=="KTNG":
    LOGO=logo; LOGOVB="0 0 200 87.021"; COMPANY="KT&G (033780)"   # 편집기와 동일(로고 미보유 시 PG 자리 대체)
else:
    LOGO=logo; LOGOVB="0 0 200 87.021"; COMPANY="프록터 앤 갬블 (PG)"

# 범례(월 인출 3종) — 통화별
if _KRW:
    _LG=[("#2b6cb0","월 100만 인출"),("#d98f2b","월 200만 인출"),("#c2255c","월 300만 인출")]
else:
    _LG=[("#2b6cb0","월 $1천 인출"),("#d98f2b","월 $2천 인출"),("#c2255c","월 $3천 인출")]
LEGEND="".join('<span class="lg"><span class="sw" style="background:%s"></span>%s</span>'%(c,t) for c,t in _LG)

if __name__=="__main__":   # 직접 실행 시에만 쇼츠 HTML 생성(모듈 import 시 부작용 없음)
    _hdr=(TMPL.replace("__LOGOVB__",LOGOVB).replace("__LOGO__",LOGO)
              .replace("__COMPANY__",COMPANY).replace("__SUB__",SUB).replace("__LEGEND__",LEGEND))
    for n,f in enumerate(FIRES,1):
        payload=json.dumps(f["payload"],ensure_ascii=False)
        html=_hdr%(CSS_F,payload.replace("'","&#39;"),"%d."%n,f["hook"],NEWRA)
        open("%s/golden_shorts_fire_%d.html"%(SP,n),"w").write(html)
        print("wrote golden_shorts_fire_%d.html (%s)"%(n,f["hook"]))
