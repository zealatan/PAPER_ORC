"""two_line_compare — 슬롯 안에 QYLD vs SPY 2선 비교 라인차트.

만화의 빈 슬롯 박스(P['params']['slot']=[x0,y0,x1,y1], 1080 기준) '안에만' 그린다.
캐릭터/말풍선/제목 침범 금지 — 라인·축·라벨·범례 모두 슬롯 좌표 안으로 clamp.

params:
  slot   : [x0,y0,x1,y1]  (필수) 이 사각형 안에만 그림.
  source : 'total'(배당재투자 평가액, 기본) | 'price'(분배제외 가격평가액).
           둘 다 invest 시작. total → y축·끝라벨=배수(×N), duration 길게(8s).
           price → y축·끝라벨=수익률(%).
  title  : 상단 표기(없으면 'QYLD vs SPY').

데이터: P['income'] (EP3). QYLD=빨강(#dc2626), SPY=파랑(#2563eb).
좌→우 reveal, y축 배수/% 눈금, x축 연도, 각 선 끝에 최종 배수(×2.23)/수익률 라벨, 범례.
SPY가 크게 앞서는 걸 시각적으로 보여준다.
renderAt(t_ms): t만으로 결정적(Math.random/Date.now 금지). 끝나면 최종프레임 hold.
"""
import json

from lib.scene_common import html_skeleton, b64  # noqa: F401  (계약상 import)


QYLD_COLOR = '#dc2626'   # 빨강
SPY_COLOR = '#2563eb'    # 파랑


def build(P):
    income = P['income']
    params = P.get('params') or {}

    slot = params['slot']
    x0, y0, x1, y1 = (int(v) for v in slot)

    source = params.get('source', 'total')
    if source not in ('total', 'price'):
        source = 'total'
    mode = 'mult' if source == 'total' else 'pct'

    q = income['QYLD']
    s = income['SPY']
    invest = int(income['invest'])
    dates = income['dates']

    qa = q.get(source) or q['total']
    sa = s.get(source) or s['total']

    # 공통 거래일 축 — 짧은 쪽에 맞춤
    N = min(len(dates), len(qa), len(sa))
    dates = dates[:N]
    qa = [int(v) for v in qa[:N]]
    sa = [int(v) for v in sa[:N]]

    q_name = q.get('name', 'QYLD')
    s_name = s.get('name', 'SPY')
    q_col = q.get('color') or QYLD_COLOR
    s_col = s.get('color') or SPY_COLOR

    title = params.get('title') or ('%s vs %s' % (q_name, s_name))

    # 끝라벨: 표(compare_table)와 동일하게 income 사전계산값 사용 → 수치 통일
    def _wan(v):
        return '{:,}만원'.format(int(round(v / 1e4)))

    def _pct(v):
        n = int(round(float(v)))
        return ('+' if n >= 0 else '−') + str(abs(n)) + '%'

    def _ends(t):
        if mode == 'mult':
            m = float(t.get('total_mult'))
            return ('×%.2f' % m), _wan(m * invest)
        pc = t.get('price_chg')
        return _pct(pc), _wan(invest * (1 + float(pc) / 100.0))

    aMain, aSub = _ends(q)
    bMain, bSub = _ends(s)

    D = {
        'slot': [x0, y0, x1, y1],
        'mode': mode,
        'title': title,
        'dates': dates,
        'invest': invest,
        'A': {'name': q_name, 'color': q_col, 'val': qa, 'endMain': aMain, 'endSub': aSub},  # QYLD
        'B': {'name': s_name, 'color': s_col, 'val': sa, 'endMain': bMain, 'endSub': bSub},   # SPY
        'reveal': 8000 if source == 'total' else 5000,
    }

    css = "#cv{position:absolute;inset:0;z-index:4}"
    body = '<canvas id="cv" width="1080" height="1080"></canvas>'

    js = P['helpers'] + '\nconst D=' + json.dumps(D, ensure_ascii=False) + ';\n' + _MAIN_JS
    return html_skeleton(P['bg'], css, body, js)


# renderAt(t): t(ms)만 → 결정적. 좌→우 reveal(eOut), 이후 hold.
_MAIN_JS = r'''
const g=document.getElementById('cv').getContext('2d');
const S=D.slot, SX0=S[0],SY0=S[1],SX1=S[2],SY1=S[3];
const SW=SX1-SX0, SH=SY1-SY0;
const INV=D.invest, DAT=D.dates, N=DAT.length, NX=Math.max(1,N-1);
const A=D.A, B=D.B, MODE=D.mode, REVEAL=D.reveal;

// 슬롯 크기 비례 폰트/패딩
const F=cl(SH*0.072,15,38);
const wan=v=>Math.round(v/1e4).toLocaleString('en-US')+'만원';
const PL=Math.max(F*3.0,SW*0.13), PR=Math.max(F*3.4,SW*0.15);
const PT=Math.max(F*3.6,SH*0.24), PB=Math.max(F*1.9,SH*0.13);
const px0=SX0+PL, px1=SX1-PR, py0=SY0+PT, py1=SY1-PB;

// y 범위(invest·두 선 모두 포함)
let lo=INV,hi=INV;
for(const v of A.val){if(v<lo)lo=v; if(v>hi)hi=v;}
for(const v of B.val){if(v<lo)lo=v; if(v>hi)hi=v;}
const _pad=(hi-lo)*0.08||1; const VMIN=lo-_pad, VMAX=hi+_pad;

const X=i=>px0+(px1-px0)*(i/NX);
const Y=v=>py1-(py1-py0)*((v-VMIN)/((VMAX-VMIN)||1));
function rr(x,y,w,h,r){g.beginPath();g.roundRect(x,y,w,h,r);}

// 배수/수익률 라벨 포맷
const yLab=v=>{ if(MODE==='mult'){ return '×'+(v/INV).toFixed(1); }
  const d=Math.round(v/INV*100-100); return (d>=0?'+':'−')+Math.abs(d)+'%'; };
const endLab=v=>{ if(MODE==='mult'){ return '×'+(v/INV).toFixed(2); }
  const d=Math.round(v/INV*100-100); return (d>=0?'+':'−')+Math.abs(d)+'%'; };
const yr=i=>{ i=cl(Math.round(i),0,N-1); return DAT.length?DAT[i].slice(0,4):''; };

function drawLine(item,k){
  const arr=item.val, col=item.color;
  const fpos=NX*k, li=Math.floor(fpos), fr=fpos-li;
  g.beginPath(); g.moveTo(X(0),Y(arr[0]));
  for(let i=1;i<=li;i++) g.lineTo(X(i),Y(arr[i]));
  let hx=X(li), hy=Y(arr[li]), hv=arr[li];
  if(li<NX && fr>0){ hv=arr[li]+(arr[li+1]-arr[li])*fr; hx=X(li+fr); hy=Y(hv); g.lineTo(hx,hy); }
  g.lineWidth=Math.max(3,F*0.22); g.lineJoin='round'; g.lineCap='round';
  g.strokeStyle=col; g.stroke();
  // 헤드닷
  g.beginPath(); g.arc(hx,hy,Math.max(5,F*0.32),0,7); g.fillStyle=col; g.fill();
  g.beginPath(); g.arc(hx,hy,Math.max(2.5,F*0.16),0,7); g.fillStyle='#fff'; g.fill();
  return {hx,hy,hv};
}

function endLabel(hx,hy,item){
  const col=item.color, main=item.endMain, sub=item.endSub;
  g.font='900 '+Math.round(F*0.98)+'px sans-serif'; const tw=g.measureText(main).width;
  g.font='800 '+Math.round(F*0.72)+'px sans-serif'; const sw=g.measureText(sub).width;
  const bw=Math.max(tw,sw);
  let tx=hx+F*0.6; if(tx+bw>SX1-4){ tx=hx-F*0.6-bw; }
  let ty=cl(hy,SY0+F*1.6,SY1-F*1.4);
  g.textAlign='left'; g.lineWidth=Math.max(3,F*0.3); g.strokeStyle='#fff'; g.lineJoin='round';
  // 배수/% (위)
  g.textBaseline='bottom'; g.font='900 '+Math.round(F*0.98)+'px sans-serif';
  g.strokeText(main,tx,ty); g.fillStyle=col; g.fillText(main,tx,ty);
  // 금액 (아래)
  g.textBaseline='top'; g.font='800 '+Math.round(F*0.72)+'px sans-serif';
  g.strokeText(sub,tx,ty+Math.round(F*0.15)); g.fillStyle=col; g.fillText(sub,tx,ty+Math.round(F*0.15));
}

function draw(t){
  const k=eOut(c01(t/REVEAL));
  g.clearRect(0,0,1080,1080);
  if(N<2)return;

  // 카드 배경(회색 10% 패널, 테두리 없음)
  g.fillStyle='rgba(120,120,125,0.10)'; rr(SX0,SY0,SW,SH,Math.min(20,SW*0.05)); g.fill();

  // 제목(상단 중앙)
  g.textAlign='center'; g.textBaseline='alphabetic';
  g.fillStyle='#111'; g.font='900 '+Math.round(F*1.02)+'px sans-serif';
  g.fillText(D.title,(SX0+SX1)/2,SY0+F*1.4);

  // 범례(제목 아래, 중앙)
  g.font='800 '+Math.round(F*0.72)+'px sans-serif';
  g.textBaseline='middle';
  const items=[A,B]; const ly=SY0+PT-F*0.9;
  let totW=0; const gap=F*1.1, dotR=F*0.34;
  for(const it of items){ totW+=dotR*2+F*0.5+g.measureText(it.name).width+gap; }
  totW-=gap;
  let lx=(SX0+SX1)/2-totW/2;
  for(const it of items){
    g.fillStyle=it.color; g.beginPath(); g.arc(lx+dotR,ly,dotR,0,7); g.fill();
    g.fillStyle='#111'; g.textAlign='left';
    g.fillText(it.name,lx+dotR*2+F*0.5,ly+1);
    lx+=dotR*2+F*0.5+g.measureText(it.name).width+gap;
  }

  // y 그리드 + 라벨(배수/%)
  g.textAlign='right'; g.textBaseline='middle'; g.font='800 '+Math.round(F*0.68)+'px sans-serif';
  for(let sI=0;sI<=2;sI++){ const v=VMIN+(VMAX-VMIN)*sI/2, y=Y(v);
    g.strokeStyle='#f1f1f4'; g.lineWidth=1; g.beginPath(); g.moveTo(px0,y); g.lineTo(px1,y); g.stroke();
    g.fillStyle='#9ca3af'; g.fillText(yLab(v),px0-6,y); }

  // 원금(invest) 기준선 점선
  const yb=Y(INV);
  g.setLineDash([6,6]); g.strokeStyle='#d4d4d8'; g.lineWidth=1.5;
  g.beginPath(); g.moveTo(px0,yb); g.lineTo(px1,yb); g.stroke(); g.setLineDash([]);

  // x 연도 라벨
  g.textAlign='center'; g.textBaseline='top'; g.fillStyle='#9ca3af'; g.font='800 '+Math.round(F*0.64)+'px sans-serif';
  for(const i of [0,(NX/2),NX]) g.fillText(yr(i),X(i),py1+6);

  // 라인 좌→우 reveal — QYLD(빨강) 먼저, SPY(파랑) 위(승자 강조)
  const ha=drawLine(A,k);
  const hb=drawLine(B,k);
  // 끝 라벨(각 선 최종 배수/수익률) — income 사전계산값
  endLabel(ha.hx,ha.hy,A);
  endLabel(hb.hx,hb.hy,B);
}
window.__renderAt=draw; draw(0);
'''
