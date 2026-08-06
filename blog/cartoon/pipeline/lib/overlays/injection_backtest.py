"""injection_backtest — 만화 위 여백 카드에 백테스트 애니(상승→추매 스텝→하락).

레퍼런스: cartoon/scene_page5.html 의 캔버스 로직을 파라미터 생성기로 포팅.
데이터는 하드코딩이 아니라 P['series']/P['meta']/P['params']에서 계산한다.

params:
  use     : 카드에 그릴 series 키 리스트(예: ["SEC","HYNIX"])
  end     : 그래프 끝 날짜(YYYY-MM-DD) — buy_date~end 로 각 series 슬라이스
  x_split : 0.5~0.55, 추매 전/후 x축 배분(기본 0.52). XM=X0+x_split*(X1-X0)

카드 위치: detect 로 캐릭터 오른쪽아래 여백(character_right_edge / bubble_bottom)에 배치.
동적 y축(2e6→종목최댓값·~17e6), 원금선(init→INV) 계단, 손실밴드/색전환, 손실 배지.
"""
import json
import math

from lib.scene_common import html_skeleton
from lib import detect


# 카드 내부 캔버스 규격(레퍼런스와 동일)
CARD_W, CARD_H = 540, 452


def _nice_step(top, n=3):
    """0..top 사이 눈금 간격을 1/2/5×10^k 중에서 고른다."""
    if top <= 0:
        return 1
    raw = top / n
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 5, 10):
        if m * mag >= raw:
            return int(m * mag)
    return int(10 * mag)


def _slice_end(series, end):
    """series 를 [0 .. end] 구간으로 자른 value/dates 반환(inj_idx 유지)."""
    dates = series['dates']
    i1 = max((i for i, d in enumerate(dates) if d <= end), default=len(dates) - 1)
    return dates[:i1 + 1], series['value'][:i1 + 1]


def _recalc_redfrom(value, inj_idx, INV):
    """추매 후 마지막까지 원금(INV) 지속 하회하는 시작 idx(잘린 구간 기준)."""
    n = len(value)
    if inj_idx is None:
        return n
    k = n
    for i in range(n - 1, inj_idx, -1):
        if value[i] < INV:
            k = i
        else:
            break
    return k


def build(P):
    meta = P['meta']
    params = P['params'] or {}
    use = params.get('use') or list(P['series'].keys())
    end = params.get('end') or meta['asof']
    x_split = float(params.get('x_split', 0.52))

    INJ = meta['inj_idx']
    INV = meta['INV']
    ADD = meta['add']
    INIT = meta['invest_each']
    inj_date = meta.get('inj_date') or ''

    # ── 각 series 를 end 까지 슬라이스 + redFrom 재계산 ──
    ser = []
    sub_dates = None
    for k in use:
        s = P['series'][k]
        d_sub, v_sub = _slice_end(s, end)
        if sub_dates is None:
            sub_dates = d_sub
        rf = _recalc_redfrom(v_sub, INJ, INV)
        ser.append({
            'name': s['name'], 'color': s['color'],
            'value': v_sub, 'redFrom': rf, 'final': v_sub[-1],
        })
    if sub_dates is None:
        sub_dates = []
    N = len(sub_dates)

    # ── 동적 y축: 하단 앵커 2e6(추매 전 스케일) → 상단=종목 최댓값 여유 ──
    y_init = 2_000_000
    peak = max((max(s['value']) for s in ser), default=INV)
    y_top = int(math.ceil(peak * 1.45 / 1e6) * 1e6)
    y_top = max(y_top, INV + 2_000_000, y_init + 1_000_000)

    # 큰 눈금(상단 스케일) / 작은 눈금(하단 스케일)
    step = _nice_step(y_top)
    large_marks = list(range(0, int(y_top), step))
    small_marks = [0, y_init // 2, y_init]

    # 추매 월/일(헤더용)
    inj_md = ''
    if inj_date:
        mo, da = inj_date.split('-')[1:]
        inj_md = f'{int(mo)}/{int(da)}'

    # ── 카드 배치: 캐릭터 오른쪽 + 말풍선 아래 여백(우하단) ──
    png = P['panel_png']
    cre = detect.character_right_edge(png) or 0
    bub = detect.bubble_bottom(png) or 0
    L = min(max(cre + 11, 0), 1080 - CARD_W)
    T = min(max(bub + 7, 0), 1080 - CARD_H)

    # ── JS 로 넘길 결정적 데이터 ──
    D = {
        'dates': sub_dates, 'INJ': INJ, 'N': N,
        'INV': INV, 'ADD': ADD, 'INIT': INIT,
        'x_split': x_split, 'y_init': y_init, 'y_top': y_top,
        'small_marks': small_marks, 'large_marks': large_marks,
        'inj_md': inj_md, 'ser': ser,
    }

    css = (
        f"#card{{position:absolute;left:{L}px;top:{T}px;width:{CARD_W}px;height:{CARD_H}px;"
        "background:#fff;border:3px solid #111;border-radius:22px;"
        "box-shadow:0 10px 30px rgba(0,0,0,.16);overflow:hidden;z-index:2}"
        "#cv{position:absolute;inset:0}"
    )
    body = f'<div id="card"><canvas id="cv" width="{CARD_W}" height="{CARD_H}"></canvas></div>'

    js = P['helpers'] + '\nwindow.__P=' + json.dumps(D, ensure_ascii=False) + ';\n' + _MAIN_JS
    return html_skeleton(P['bg'], css, body, js)


# renderAt(t): t(ms)만으로 결정적. Math.random/Date.now 미사용. 끝나면 최종프레임 hold.
_MAIN_JS = r'''
const D=window.__P, SER=D.ser;
const g=document.getElementById('cv').getContext('2d');
const W=540,Hc=452, X0=60,X1=514,Y0=96,Y1=400;
const INJ=D.INJ, N=D.N, INV=D.INV, ADD=D.ADD, INIT=D.INIT;
const Y_INIT=D.y_init, Y_TOP=D.y_top;
const XM=X0+D.x_split*(X1-X0);
const hasInj=(INJ!==null&&INJ!==undefined&&INJ>0&&INJ<N-1);
const IJ=hasInj?INJ:(N-1);
const Xof=i=> (i<=IJ ? X0+(IJ>0?(i/IJ):0)*(XM-X0) : XM+((i-IJ)/((N-1-IJ)||1))*(X1-XM));
function Ymax(t){return t<3400?Y_INIT:(t>4600?Y_TOP:lerp(Y_INIT,Y_TOP,ss((t-3400)/1200)));}
const PY=(v,t)=>Y1-(v/Ymax(t))*(Y1-Y0);
const md=k=>{k=cl(Math.round(k),0,N-1);const p=D.dates[k].slice(5).split('-');return (+p[0])+'.'+(+p[1]);};
function ptsA(v){const a=[];for(let i=0;i<=IJ;i++)a.push({i,v:v[i]});return a;}
function ptsB(v){const a=[{i:IJ,v:v[IJ]+ADD}];for(let i=IJ+1;i<N;i++)a.push({i,v:v[i]});return a;}
function seg(a,b,t,c){g.beginPath();g.moveTo(Xof(a.i),PY(a.v,t));g.lineTo(Xof(b.i),PY(b.v,t));g.strokeStyle=c;g.lineWidth=4;g.lineJoin='round';g.lineCap='round';g.stroke();}
function poly(pts,fi,t,brand,rf){let h=pts[0];
  for(let k=0;k+1<pts.length;k++){if(k+1>fi){const f=fi-k;if(f<=0)break;const a=pts[k],b=pts[k+1],m={i:a.i+(b.i-a.i)*f,v:a.v+(b.v-a.v)*f};seg(a,m,t,(b.i>=rf)?'#dc2626':brand);h=m;break;}
    const a=pts[k],b=pts[k+1];seg(a,b,t,(b.i>=rf&&b.v<INV)?'#dc2626':brand);h=b;}return h;}
function band(pts,fi,t,inv,rf){for(let k=0;k+1<pts.length&&k+1<=fi;k++){const a=pts[k],b=pts[k+1];
  if(b.i>=rf&&a.v<inv&&b.v<inv){g.beginPath();g.moveTo(Xof(a.i),PY(a.v,t));g.lineTo(Xof(b.i),PY(b.v,t));g.lineTo(Xof(b.i),PY(inv,t));g.lineTo(Xof(a.i),PY(inv,t));g.closePath();g.fillStyle='rgba(220,38,38,.18)';g.fill();}}}
function dot(h,c){if(!h)return;g.beginPath();g.arc(Xof(h.i),PY(h.v,t_g),6,0,7);g.fillStyle=c;g.fill();g.beginPath();g.arc(Xof(h.i),PY(h.v,t_g),3,0,7);g.fillStyle='#fff';g.fill();}
let t_g=0;
function renderAt(t){
  t_g=t;
  g.clearRect(0,0,W,Hc);
  const zp=c01((t-3400)/1200), invLevel=lerp(INIT,INV,zp);
  // header
  g.fillStyle='#111';g.font='800 24px sans-serif';g.textAlign='left';g.textBaseline='alphabetic';
  g.fillText((D.inj_md?D.inj_md+' ':'')+'고점 추매 백테스트',20,36);
  // legend
  let lx=24;
  g.textBaseline='alphabetic';
  for(const s of SER){g.fillStyle=s.color;g.beginPath();g.arc(lx,58,8,0,7);g.fill();
    g.fillStyle='#111';g.font='700 18px sans-serif';g.textAlign='left';g.fillText(s.name,lx+14,64);
    lx+=14+g.measureText(s.name).width+26;}
  g.strokeStyle='#e4e4e7';g.lineWidth=1;g.strokeRect(X0,Y0,X1-X0,Y1-Y0);
  // y ticks — 하단(작은)↔상단(큰) 크로스페이드
  const aA=c01(1-(Ymax(t)-Y_INIT)/((Y_TOP-Y_INIT)||1)*1.3),aB=1-aA;
  g.textAlign='right';g.textBaseline='middle';g.font='800 15px sans-serif';
  if(aA>0.02){g.globalAlpha=aA;g.fillStyle='#333';for(const m of D.small_marks){const y=PY(m,t);if(y<Y0-3||y>Y1+3)continue;g.fillText(Math.round(m/1e4)+'만',X0-6,y);}}
  if(aB>0.02){g.globalAlpha=aB;g.fillStyle='#333';for(const m of D.large_marks){const y=PY(m,t);if(y<Y0-3)continue;g.fillText(Math.round(m/1e4)+'만',X0-6,y);}}
  g.globalAlpha=1;
  // x ticks
  g.textAlign='center';g.textBaseline='top';g.fillStyle='#52525b';g.font='800 15px sans-serif';
  const xt=hasInj?[0,IJ,N-1]:[0,N-1];
  for(const i of xt) g.fillText(md(i),Xof(i),Y1+8);
  // principal step line
  g.setLineDash([7,6]);g.strokeStyle='#9ca3af';g.lineWidth=2;g.beginPath();g.moveTo(X0,PY(invLevel,t));g.lineTo(X1,PY(invLevel,t));g.stroke();g.setLineDash([]);
  g.fillStyle='#9ca3af';g.textAlign='left';g.font='700 14px sans-serif';g.textBaseline='bottom';
  g.fillText((zp>0.5?'투입원금 ':'원금 ')+won(Math.round((zp>0.5?INV:INIT)/1e4))+'만',X0+4,PY(invLevel,t)-4);
  // draw progress
  const fiA=eIO(c01((t-600)/2400))*IJ, fiB=eIO(c01((t-4600)/2600))*((N-1-IJ)||0);
  // loss bands (under everything)
  if(hasInj&&t>4600){for(const s of SER) band(ptsB(s.value),fiB,t,invLevel,s.redFrom);}
  // phase A lines (draw reversed → SER[0] on top)
  const rA=t<3400?fiA:IJ;
  for(let k=SER.length-1;k>=0;k--) poly(ptsA(SER[k].value),rA,t,SER[k].color,9999);
  // injection step + phase B
  const heads=SER.map(()=>null);
  if(hasInj&&t>=3400){
    for(let k=SER.length-1;k>=0;k--){const s=SER[k],pre=s.value[IJ],post=pre+ADD;
      g.strokeStyle=s.color;g.lineWidth=4;g.beginPath();g.moveTo(Xof(IJ),PY(pre,t));g.lineTo(Xof(IJ),PY(lerp(pre,post,zp),t));g.stroke();
      if(t>4600) heads[k]=poly(ptsB(s.value),fiB,t,s.color,s.redFrom);
      else heads[k]={i:IJ,v:lerp(pre,post,zp)};}
  }
  // dots
  if(hasInj&&t<3400&&SER.length){const li=cl(Math.round(fiA),0,IJ);dot({i:fiA,v:SER[0].value[li]},SER[0].color);}
  else if(!hasInj&&SER.length){const li=cl(Math.round(fiA),0,N-1);dot({i:fiA,v:SER[0].value[li]},SER[0].color);}
  for(let k=SER.length-1;k>=0;k--) dot(heads[k],SER[k].color);
  // injection marker
  if(hasInj&&t>3000){g.globalAlpha=c01((t-3000)/400);g.setLineDash([5,5]);g.strokeStyle='#111';g.lineWidth=1.5;g.beginPath();g.moveTo(Xof(IJ),Y0);g.lineTo(Xof(IJ),Y1);g.stroke();g.setLineDash([]);
    g.fillStyle='#111';g.textAlign='center';g.font='800 16px sans-serif';g.textBaseline='bottom';g.fillText(md(IJ)+' 추매',Xof(IJ),Y0-4);g.globalAlpha=1;}
  // loss badges
  if(t>7000){const a=eBack(c01((t-7000)/400));
    function lb(x,y,txt){g.save();g.translate(x,y);g.scale(a,a);g.fillStyle='#dc2626';g.font='900 18px sans-serif';const w=g.measureText(txt).width+20;
      g.beginPath();g.roundRect(-w/2,-17,w,34,10);g.fill();g.fillStyle='#fff';g.textAlign='center';g.textBaseline='middle';g.fillText(txt,0,0);g.restore();}
    for(let k=0;k<SER.length;k++){const s=SER[k];if(s.final>=INV)continue;
      const dy=(k%2===0)?34:-34;
      lb(Xof(N-1)-92,PY(s.value[N-1],t)+dy,s.name+' −'+won(Math.round((INV-s.final)/1e4))+'만');}
  }
}
window.__renderAt=renderAt; renderAt(0);
'''
