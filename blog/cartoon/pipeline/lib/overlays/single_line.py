"""single_line — 슬롯 안에 단일 종목 가격라인을 좌→우 reveal.

params:
  window       : [d0, d1] 실제 날짜(토큰 치환 완료). 이 구간 가격라인.
  color        : hex 라인색(없으면 P['dca']['ticker']['color']; down이면 빨강 폴백).
  label        : 헤더 라벨(예 'QQQ'; 없으면 ticker name).
  down         : bool. true면 하락 강조(빨강·배지 −xx%).
  slot         : [x0,y0,x1,y1] 이 사각형 '안에만' 그린다(필수). 캐릭터/말풍선 침범 금지.
  caption_slot : optional [x0,y0,x1,y1] 큰 낙폭 라벨 자리.
  caption      : optional 캡션 텍스트(없으면 P['dca']['lump']['mdd']로 '−xx.x%' 생성).

데이터 = data.price_line(P['dca']['ticker']['code'], window[0], window[1], base=100).
라인+헤드닷+시작대비 최종 수익%(우측 상단 배지). reveal ~2.5초 후 최종프레임 hold.
renderAt(t): t(ms)만으로 결정적(Math.random/Date.now 미사용).
"""
import json

from lib.scene_common import html_skeleton, b64  # noqa: F401  (계약상 import)
from lib import data


def build(P):
    params = P.get('params') or {}
    if P.get('dca'):
        tk = P['dca']['ticker']
    elif P.get('income'):
        q = P['income']['QYLD']
        tk = {'code': params.get('code') or q.get('code', 'QYLD'),
              'name': q.get('name', 'QYLD'), 'color': q.get('color', '#dc2626')}
    else:
        tk = {'code': params.get('code', 'QYLD'), 'name': params.get('label', ''), 'color': '#2563eb'}

    slot = params['slot']
    x0, y0, x1, y1 = (int(v) for v in slot)
    win = params['window']
    d0, d1 = win[0], win[1]

    down = bool(params.get('down'))
    color = params.get('color') or ('#dc2626' if down else tk.get('color', '#2563eb'))
    label = params.get('label') or tk.get('name', '')

    pl = data.price_line(tk['code'], d0, d1, base=100)
    dates = pl['dates']
    value = pl['value']

    cap_slot = params.get('caption_slot')
    caption = params.get('caption')
    if caption is None:
        _dca = P.get('dca')
        mdd = (_dca.get('lump', {}).get('mdd') if _dca
               else (P.get('income') or {}).get('QYLD', {}).get('mdd'))
        if mdd is not None:
            caption = '−' + ('%.1f' % abs(float(mdd))) + '%'

    D = {
        'dates': dates, 'value': value, 'color': color, 'label': label,
        'down': down, 'slot': [x0, y0, x1, y1],
        'capSlot': list(map(int, cap_slot)) if cap_slot else None,
        'caption': caption,
    }

    css = "#cv{position:absolute;inset:0;z-index:4}"
    body = '<canvas id="cv" width="1080" height="1080"></canvas>'

    js = P['helpers'] + '\nconst D=' + json.dumps(D, ensure_ascii=False) + ';\n' + _MAIN_JS
    return html_skeleton(P['bg'], css, body, js)


# renderAt(t): t(ms)만 → 결정적. reveal ~2.5s eOut, 이후 hold.
_MAIN_JS = r'''
const g=document.getElementById('cv').getContext('2d');
const S=D.slot, SX0=S[0],SY0=S[1],SX1=S[2],SY1=S[3];
const SW=SX1-SX0, SH=SY1-SY0;
const VAL=D.value, DAT=D.dates, N=VAL.length, NX=Math.max(1,N-1);
const COL=D.color, DOWN=D.down;
const REVEAL=2500;

// 슬롯 크기에 맞춘 폰트/패딩
const F=cl(SH*0.052,12,26);
const PL=Math.max(F*2.2,SW*0.11), PR=Math.max(F*0.8,SW*0.05);
const PT=Math.max(F*2.4,SH*0.22), PB=Math.max(F*1.6,SH*0.13);
const px0=SX0+PL, px1=SX1-PR, py0=SY0+PT, py1=SY1-PB;

// y 범위(시작기준선 100 포함)
let lo=100,hi=100;
for(const v of VAL){if(v<lo)lo=v; if(v>hi)hi=v;}
const _pad=(hi-lo)*0.08||1; const VMIN=lo-_pad, VMAX=hi+_pad;

const X=i=>px0+(px1-px0)*(i/NX);
const Y=v=>py1-(py1-py0)*((v-VMIN)/((VMAX-VMIN)||1));
function rr(x,y,w,h,r){g.beginPath();g.roundRect(x,y,w,h,r);}
const pctTxt=v=>{const d=Math.round(v-100);return (d>=0?'+':'−')+Math.abs(d)+'%';};
const xlab=i=>{i=cl(Math.round(i),0,N-1);return DAT.length?DAT[i].slice(2,7).replace('-','.'):'';};

function draw(t){
  const k=eOut(c01(t/REVEAL));
  g.clearRect(0,0,1080,1080);
  if(N<2)return;

  // 카드 배경 — 골든 표준: 회색 10% 패널(테두리 제거)
  g.fillStyle='rgba(120,120,125,0.10)'; rr(SX0,SY0,SW,SH,Math.min(20,SW*0.05)); g.fill();

  // 헤더 라벨
  g.textAlign='left'; g.textBaseline='alphabetic';
  g.fillStyle=COL; g.beginPath(); g.arc(SX0+PL*0.55,SY0+PT*0.5,F*0.42,0,7); g.fill();
  g.fillStyle='#111'; g.font='800 '+Math.round(F*1.05)+'px sans-serif';
  g.fillText(D.label,SX0+PL*0.55+F*0.7,SY0+PT*0.5+F*0.38);

  // y 그리드 + 라벨
  g.textAlign='right'; g.textBaseline='middle'; g.font='800 '+Math.round(F*0.62)+'px sans-serif';
  for(let s=0;s<=2;s++){const v=VMIN+(VMAX-VMIN)*s/2, y=Y(v);
    g.strokeStyle='#f1f1f4'; g.lineWidth=1; g.beginPath(); g.moveTo(px0,y); g.lineTo(px1,y); g.stroke();
    g.fillStyle='#9ca3af'; g.fillText(pctTxt(v),px0-6,y);}

  // 시작 기준선(100) 점선
  const yb=Y(100);
  g.setLineDash([6,6]); g.strokeStyle='#d4d4d8'; g.lineWidth=1.5;
  g.beginPath(); g.moveTo(px0,yb); g.lineTo(px1,yb); g.stroke(); g.setLineDash([]);

  // x 라벨
  g.textAlign='center'; g.textBaseline='top'; g.fillStyle='#9ca3af'; g.font='800 '+Math.round(F*0.6)+'px sans-serif';
  for(const i of [0,(NX/2),NX]) g.fillText(xlab(i),X(i),py1+6);

  // 라인 좌→우 reveal(분수 진행)
  const fpos=NX*k, li=Math.floor(fpos), fr=fpos-li;
  g.beginPath(); g.moveTo(X(0),Y(VAL[0]));
  for(let i=1;i<=li;i++) g.lineTo(X(i),Y(VAL[i]));
  let hx=X(li), hy=Y(VAL[li]), hv=VAL[li];
  if(li<NX && fr>0){hv=VAL[li]+(VAL[li+1]-VAL[li])*fr; hx=X(li+fr); hy=Y(hv); g.lineTo(hx,hy);}
  g.lineWidth=Math.max(3,F*0.22); g.lineJoin='round'; g.lineCap='round';
  g.strokeStyle=DOWN?'#dc2626':COL; g.stroke();

  // 헤드닷
  g.beginPath(); g.arc(hx,hy,Math.max(5,F*0.32),0,7); g.fillStyle=DOWN?'#dc2626':COL; g.fill();
  g.beginPath(); g.arc(hx,hy,Math.max(2.5,F*0.16),0,7); g.fillStyle='#fff'; g.fill();

  // 우측 상단 수익% 배지
  const pv=Math.round(hv-100);
  const btxt=(DOWN||pv<0?'−':'+')+Math.abs(pv)+'%';
  const bc=(DOWN||pv<0)?'#dc2626':'#16a34a';
  g.font='900 '+Math.round(F*0.9)+'px sans-serif';
  const bw=g.measureText(btxt).width+F*0.9, bh=F*1.5;
  const bx=px1-bw, by=SY0+PT*0.5-bh/2;
  g.fillStyle=bc; rr(bx,by,bw,bh,bh*0.32); g.fill();
  g.fillStyle='#fff'; g.textAlign='center'; g.textBaseline='middle';
  g.fillText(btxt,bx+bw/2,by+bh/2+1);

  // 캡션(큰 낙폭 라벨)
  if(D.capSlot && D.caption){
    const C=D.capSlot, cw=C[2]-C[0], ch=C[3]-C[1];
    const a=c01((t-1600)/700); if(a>0.01){
      g.globalAlpha=a;
      const cf=cl(ch*0.5,20,120);
      g.fillStyle=DOWN?'#dc2626':'#111'; g.font='900 '+Math.round(cf)+'px sans-serif';
      g.textAlign='center'; g.textBaseline='middle';
      g.fillText(D.caption,C[0]+cw/2,C[1]+ch/2);
      g.globalAlpha=1;
    }
  }
}
window.__renderAt=draw; draw(0);
'''