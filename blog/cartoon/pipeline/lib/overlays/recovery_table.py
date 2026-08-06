"""recovery_table — 슬롯 안에 '일시매수 vs 분할매수' 회복 스토리(라인+결과표).

만화의 빈 슬롯 박스(P['params']['slot']=[x0,y0,x1,y1]) '안에만' 그린다.
캐릭터/말풍선/제목 침범 금지 — 모든 좌표는 슬롯 로컬(캔버스=슬롯 크기).

레이아웃:
  상단 ~55% : 평가액 라인 2개(일시매수=빨강 / 분할매수=파랑) 좌→우 reveal,
              각 투입원금선(회색 점선) 참고. y·x축·범례는 슬롯 크기에 맞춰 컴팩트.
  하단 ~45% : 결과표 3×2
              행 = ['최종 자산','원금 회복','손실 기간']
              열 = ['일시매수','분할매수']
              값 = final_mult'배' · recover_m'개월' · loss_m'개월'
              셀 순차 페이드인.

타임라인(≈8s): 라인 reveal(0.3~4.3s) → 표 프레임(4.4s) → 값 셀 순차(4.6s~) → 최종 hold.

데이터: P['dca'] (data.build_dca 결과). renderAt(t_ms)는 결정적(Math.random/Date.now 금지).
스타일 톤: injection_backtest.py(라인+표) 참고.
"""
import json

from lib.scene_common import html_skeleton, b64  # noqa: F401  (계약상 import)


LUMP_COLOR = '#dc2626'   # 일시매수 = 빨강계열
DCA_COLOR = '#2563eb'    # 분할매수 = 파랑계열
PRIN_COLOR = '#9ca3af'   # 투입원금 = 회색 점선


def _fmt_mult(m):
    try:
        return ('%.2f배' % float(m))
    except (TypeError, ValueError):
        return '—'


def _fmt_mon(m):
    if m is None:
        return '—'
    try:
        return '%d개월' % int(m)
    except (TypeError, ValueError):
        return '—'


def build(P):
    dca = P['dca']
    params = P.get('params') or {}
    slot = params['slot']
    x0, y0, x1, y1 = (float(v) for v in slot)
    W = int(round(x1 - x0))
    H = int(round(y1 - y0))
    left = int(round(x0))
    top = int(round(y0))

    lump = dca['lump']
    dcav = dca['dca']
    name = dca['ticker']['name']

    # 결과표 값(포맷 완료 문자열) — 행 순서 = [최종자산, 원금회복, 손실기간]
    rows = [
        {'label': '최종 자산',
         'a': _fmt_mult(lump.get('final_mult')), 'b': _fmt_mult(dcav.get('final_mult'))},
        {'label': '원금 회복',
         'a': _fmt_mon(lump.get('recover_m')), 'b': _fmt_mon(dcav.get('recover_m'))},
        {'label': '손실 기간',
         'a': _fmt_mon(lump.get('loss_m')), 'b': _fmt_mon(dcav.get('loss_m'))},
    ]

    D = {
        'W': W, 'H': H,
        'name': name,
        'dates': dca['dates'],
        'lumpV': lump['value'], 'lumpI': lump['invested'],
        'dcaV': dcav['value'], 'dcaI': dcav['invested'],
        'lumpC': LUMP_COLOR, 'dcaC': DCA_COLOR, 'prinC': PRIN_COLOR,
        'rows': rows,
    }

    css = (
        f"#rt{{position:absolute;left:{left}px;top:{top}px;"
        f"width:{W}px;height:{H}px;z-index:3}}"
        "#rtcv{position:absolute;inset:0;width:100%;height:100%}"
    )
    body = (
        f'<div id="rt"><canvas id="rtcv" width="{W}" height="{H}"></canvas></div>'
    )

    js = (
        P['helpers']
        + '\nwindow.__RT=' + json.dumps(D, ensure_ascii=False) + ';\n'
        + _MAIN_JS
    )
    return html_skeleton(P['bg'], css, body, js)


# renderAt(t): t(ms)만으로 결정적. 끝나면 최종프레임 hold.
_MAIN_JS = r'''
const D=window.__RT;
const W=D.W, H=D.H, sc=W/500;
const g=document.getElementById('rtcv').getContext('2d');
const AV=D.lumpV, BV=D.dcaV, AI=D.lumpI, BI=D.dcaI;
const N=D.dates.length, NX=Math.max(1,N-1);
const R=(px)=>px*sc;

// ── y축 범위(두 평가액+두 원금 포함) ──
let vmax=-1e18, vmin=1e18;
for(const arr of [AV,BV,AI,BI]) for(const v of arr){ if(v>vmax)vmax=v; if(v<vmin)vmin=v; }
vmax*=1.04; vmin*=0.97; if(vmax<=vmin) vmax=vmin+1;

// ── 영역 분할: 상단 55% 차트 / 하단 45% 표 ──
const CH=H*0.55;
const PADL=R(46), PADR=R(12), PADT=R(38), PADB=R(26);
const cW=W-PADL-PADR, cH=CH-PADT-PADB;
const X=i=>PADL+cW*(i/NX);
const Y=v=>PADT+cH*(1-(v-vmin)/(vmax-vmin));

const mm=v=>Math.round(v/1e4).toLocaleString('en-US')+'만';
const mdlab=i=>{const p=D.dates[cl(Math.round(i),0,N-1)].slice(5).split('-');return (+p[0])+'.'+(+p[1]);};

function chartGrid(){
  // y 눈금 3개
  g.textAlign='right'; g.textBaseline='middle';
  g.font='800 '+R(13)+'px sans-serif';
  for(let k=0;k<=2;k++){
    const v=vmin+(vmax-vmin)*k/2, y=Y(v);
    g.strokeStyle='#eef0f3'; g.lineWidth=1;
    g.beginPath(); g.moveTo(PADL,y); g.lineTo(W-PADR,y); g.stroke();
    g.fillStyle='#666'; g.fillText(mm(v),PADL-R(5),y);
  }
  // x 눈금(시작·중간·끝)
  g.textAlign='center'; g.textBaseline='top'; g.fillStyle='#71717a';
  g.font='800 '+R(13)+'px sans-serif';
  for(const i of [0,(NX/2)|0,NX]) g.fillText(mdlab(i),X(i),CH-PADB+R(6));
}

function legend(){
  g.textBaseline='alphabetic'; g.textAlign='left';
  g.font='800 '+R(15)+'px sans-serif';
  let lx=PADL; const cy=R(20), r=R(6);
  const items=[['일시매수',D.lumpC],['분할매수',D.dcaC]];
  for(const [lab,col] of items){
    g.fillStyle=col; g.beginPath(); g.arc(lx+r,cy,r,0,7); g.fill();
    g.fillStyle='#111'; g.fillText(lab,lx+2*r+R(6),cy+R(5));
    lx+=2*r+R(6)+g.measureText(lab).width+R(20);
  }
}

function prinLine(arr,li,c){
  g.setLineDash([R(6),R(5)]); g.strokeStyle=c; g.lineWidth=R(2);
  g.beginPath(); g.moveTo(X(0),Y(arr[0]));
  for(let i=1;i<=li;i++) g.lineTo(X(i),Y(arr[i]));
  g.stroke(); g.setLineDash([]);
}

function valLine(arr,li,c,frac){
  g.strokeStyle=c; g.lineWidth=R(4.5); g.lineJoin='round'; g.lineCap='round';
  g.beginPath(); g.moveTo(X(0),Y(arr[0]));
  for(let i=1;i<=li;i++) g.lineTo(X(i),Y(arr[i]));
  // 소수 구간 보간
  if(li<NX && frac>0){ const a=arr[li], b=arr[li+1];
    g.lineTo(X(li+frac),Y(a+(b-a)*frac)); }
  g.stroke();
  const hx=X(li+ (li<NX?frac:0)), hv=(li<NX?arr[li]+(arr[li+1]-arr[li])*frac:arr[li]);
  const hy=Y(hv);
  g.beginPath(); g.arc(hx,hy,R(6),0,7); g.fillStyle=c; g.fill();
  g.beginPath(); g.arc(hx,hy,R(3),0,7); g.fillStyle='#fff'; g.fill();
}

function drawChart(k){
  chartGrid(); legend();
  const prog=(NX)*k, li=Math.min(NX,Math.floor(prog)), frac=cl(prog-li,0,1);
  // 원금선(회색 점선) — 참고, 값선 아래
  prinLine(AI,li,D.prinC);
  prinLine(BI,li,D.prinC);
  // 값선: 분할(파랑) 먼저 → 일시(빨강) 위
  valLine(BV,li,D.dcaC,frac);
  valLine(AV,li,D.lumpC,frac);
}

// ── 결과표 ──
const TT=CH+R(6);                 // table top
const LBLW=(W)*0.34;              // 행 라벨 열 폭
const colW=(W-LBLW)/2;
const nR=D.rows.length;           // 3
const rowsTop=TT+R(30);           // 헤더 아래
const rowH=(H-rowsTop-R(6))/nR;
const colX=[LBLW+colW*0.5, LBLW+colW*1.5];  // 값 열 중심
const colC=[D.lumpC,D.dcaC];
const colHd=['일시매수','분할매수'];

function drawTableFrame(a){
  if(a<=0) return;
  g.globalAlpha=a;
  // 외곽/구분선
  g.strokeStyle='#d4d4d8'; g.lineWidth=R(1.4);
  g.beginPath(); g.moveTo(0,TT+R(28)); g.lineTo(W,TT+R(28)); g.stroke(); // 헤더 하단
  for(let r=1;r<nR;r++){ const y=rowsTop+rowH*r; g.strokeStyle='#eceef1'; g.lineWidth=R(1);
    g.beginPath(); g.moveTo(0,y); g.lineTo(W,y); g.stroke(); }
  g.strokeStyle='#e6e8eb'; g.lineWidth=R(1);
  g.beginPath(); g.moveTo(LBLW,TT); g.lineTo(LBLW,H); g.stroke();
  g.beginPath(); g.moveTo(LBLW+colW,TT); g.lineTo(LBLW+colW,H); g.stroke();
  // 헤더
  g.textBaseline='middle'; g.textAlign='center';
  g.font='800 '+R(17)+'px sans-serif';
  for(let c=0;c<2;c++){ g.fillStyle=colC[c]; g.fillText(colHd[c],colX[c],TT+R(14)); }
  // 행 라벨
  g.textAlign='left'; g.fillStyle='#3f3f46'; g.font='700 '+R(16)+'px sans-serif';
  for(let r=0;r<nR;r++) g.fillText(D.rows[r].label,R(8),rowsTop+rowH*(r+0.5));
  g.globalAlpha=1;
}

function drawCells(t){
  const T0=4600, STEP=300, DUR=380;
  g.textAlign='center'; g.textBaseline='middle';
  g.font='900 '+R(22)+'px sans-serif';
  for(let r=0;r<nR;r++){
    const row=D.rows[r], vals=[row.a,row.b];
    for(let c=0;c<2;c++){
      const idx=r*2+c, a=c01((t-(T0+idx*STEP))/DUR);
      if(a<=0) continue;
      g.globalAlpha=a; g.fillStyle=colC[c];
      const yy=rowsTop+rowH*(r+0.5);
      const pop=1+(1-a)*0.10;   // 살짝 팝
      g.save(); g.translate(colX[c],yy); g.scale(pop,pop);
      g.fillText(vals[c],0,0); g.restore();
    }
  }
  g.globalAlpha=1;
}

function renderAt(t){
  g.clearRect(0,0,W,H);
  const k=eOut(c01((t-300)/4000));
  drawChart(k);
  drawTableFrame(c01((t-4400)/400));
  drawCells(t);
}
window.__renderAt=renderAt; renderAt(0);
'''