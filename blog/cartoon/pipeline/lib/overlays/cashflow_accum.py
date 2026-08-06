"""cashflow_accum — 슬롯 안에 '매달 분배금 누적'을 area/line으로 좌→우 reveal.

만화의 빈 슬롯 박스(P['params']['slot']=[x0,y0,x1,y1]) '안에만' 그린다.
캐릭터/말풍선/제목 침범 금지 — 폰트·패딩은 슬롯 크기에 비례.

레이아웃(슬롯 로컬):
  상단  : 헤더(QYLD 이름 · '매달 쌓이는 분배금') + 큰 카운터(0 → dist_cum_final '원').
  중단  : 배지 '누적 분배금 = 투입의 XX%'(dist_cum_final/invest) — 끝에 팝인.
  하단  : dist_cum(분배금 현금 누적) area/line 좌→우 reveal.
          매달 들어오는 '달콤함'을 초록(라인)+골드(면 그라디언트·코인닷)로 강조.

데이터: P['income']['QYLD']['dist_cum'] (누적 현금, 0에서 증가) · dist_cum_final · invest.
타임라인(≈3.5s): reveal(0.3~2.9s eOut) → 배지 팝인(2.95s~) → 최종프레임 hold.
renderAt(t_ms)는 t만으로 결정적(Math.random/Date.now 미사용).
스타일 톤: single_line.py(라인 reveal) · loss_counter.py(카운터) 참고.
"""
import json

from lib.scene_common import html_skeleton, b64  # noqa: F401  (계약상 import)


GREEN = '#16a34a'    # 라인 = 초록(매달 들어오는 달콤함)
GREEN_DK = '#15803d'
GOLD = '#f59e0b'     # 면/코인 = 골드
GOLD_DK = '#d97706'


def build(P):
    income = P['income']
    params = P.get('params') or {}

    slot = params['slot']
    x0, y0, x1, y1 = (int(round(float(v))) for v in slot)

    q = income['QYLD']
    invest = int(income.get('invest') or 0)

    dist = [int(v) for v in (q.get('dist_cum') or [])]
    dates = list(q.get('dates') or income.get('dates') or [])
    # dates/dist 길이 정합(짧은 쪽 기준)
    n = min(len(dist), len(dates)) if dates else len(dist)
    if not dates:
        dates = ['' for _ in range(len(dist))]
        n = len(dist)
    dist = dist[:n]
    dates = dates[:n]

    final = int(q.get('dist_cum_final') if q.get('dist_cum_final') is not None
                else (dist[-1] if dist else 0))
    # 투입 대비 누적 분배 비율(%)
    pct_final = int(round(final / invest * 100)) if invest else 0

    name = q.get('name') or 'QYLD'

    # 누적 기간(년)
    import datetime as _dt
    try:
        _y = (_dt.date.fromisoformat(income['asof']) - _dt.date.fromisoformat(income['buy_date'])).days / 365.25
        years = ('%.1f' % _y).rstrip('0').rstrip('.')
    except Exception:
        years = ''

    D = {
        'slot': [x0, y0, x1, y1],
        'dist': dist, 'dates': dates,
        'final': final, 'invest': invest, 'pctFinal': pct_final,
        'years': years,
        'name': name,
        'green': GREEN, 'greenDk': GREEN_DK, 'gold': GOLD, 'goldDk': GOLD_DK,
    }

    css = "#cv{position:absolute;inset:0;z-index:4}"
    body = '<canvas id="cv" width="1080" height="1080"></canvas>'

    js = P['helpers'] + '\nconst D=' + json.dumps(D, ensure_ascii=False) + ';\n' + _MAIN_JS
    return html_skeleton(P['bg'], css, body, js)


# renderAt(t): t(ms)만 → 결정적. reveal eOut, 이후 hold.
_MAIN_JS = r'''
const g=document.getElementById('cv').getContext('2d');
const S=D.slot, SX0=S[0],SY0=S[1],SX1=S[2],SY1=S[3];
const SW=SX1-SX0, SH=SY1-SY0;
const V=D.dist, DAT=D.dates, N=V.length, NX=Math.max(1,N-1);
const GREEN=D.green, GREENDK=D.greenDk, GOLD=D.gold, GOLDDK=D.goldDk;

const REVEAL_ST=300, REVEAL_DUR=2600;   // reveal 0.3~2.9s
const BADGE_ST=2950, BADGE_DUR=420;     // 배지 팝인

// 슬롯 크기에 비례한 폰트/패딩
const F=cl(SH*0.05,12,26);
const CF=cl(SH*0.15,26,84);             // 큰 카운터
const PL=Math.max(F*2.6,SW*0.13), PR=Math.max(F*0.8,SW*0.05);

// 세로 구획(슬롯 로컬 비율)
const headY = SY0+SH*0.11;              // 헤더 baseline
const cntY  = SY0+SH*0.30;              // 카운터 center
const badgeY= SY0+SH*0.455;             // 배지 center
const chTop = SY0+SH*0.56;              // 차트 상단
const chBot = SY1-Math.max(F*1.5,SH*0.10);
const px0=SX0+PL, px1=SX1-PR;

// y 범위: 0 ~ final(패딩)
let hi=D.final; for(const v of V) if(v>hi) hi=v;
if(hi<=0) hi=1;
const VMAX=hi*1.10, VMIN=0;

const X=i=>px0+(px1-px0)*(i/NX);
const Y=v=>chBot-(chBot-chTop)*((v-VMIN)/((VMAX-VMIN)||1));
function rr(x,y,w,h,r){g.beginPath();g.roundRect(x,y,w,h,r);}
const mlab=i=>{i=cl(Math.round(i),0,N-1);const s=DAT[i]||'';return s?s.slice(2,7).replace('-','.'):'';};

function draw(t){
  g.clearRect(0,0,1080,1080);
  if(N<1) return;
  const k=eOut(c01((t-REVEAL_ST)/REVEAL_DUR));

  // ── 카드 배경 ──
  g.fillStyle='rgba(120,120,125,0.10)'; rr(SX0,SY0,SW,SH,Math.min(22,SW*0.05)); g.fill();
  g.lineWidth=3; g.strokeStyle=GREEN; g.stroke();

  // ── 헤더: 초록 닷 + 이름 + 부제 ──
  g.textAlign='left'; g.textBaseline='alphabetic';
  g.fillStyle=GREEN; g.beginPath(); g.arc(SX0+PL*0.42,headY-F*0.32,F*0.40,0,7); g.fill();
  g.fillStyle='#111'; g.font='800 '+Math.round(F*1.02)+'px sans-serif';
  g.fillText(D.name,SX0+PL*0.42+F*0.72,headY);
  const nw=g.measureText(D.name).width;
  g.fillStyle='#71717a'; g.font='800 '+Math.round(F*0.72)+'px sans-serif';
  g.fillText('· 매달 쌓이는 분배금',SX0+PL*0.42+F*0.72+nw+F*0.5,headY);

  // ── reveal 진행(분수) ──
  const fpos=NX*k, li=cl(Math.floor(fpos),0,NX), fr=cl(fpos-li,0,1);
  let hx=X(li), hv=V[li];
  if(li<NX && fr>0){ hv=V[li]+(V[li+1]-V[li])*fr; hx=X(li+fr); }
  const hy=Y(hv);

  // ── area(골드 그라디언트) ──
  const grd=g.createLinearGradient(0,chTop,0,chBot);
  grd.addColorStop(0,'rgba(245,158,11,0.30)');
  grd.addColorStop(1,'rgba(22,163,74,0.05)');
  g.beginPath(); g.moveTo(X(0),Y(0));
  g.lineTo(X(0),Y(V[0]));
  for(let i=1;i<=li;i++) g.lineTo(X(i),Y(V[i]));
  if(li<NX && fr>0) g.lineTo(hx,hy);
  g.lineTo(hx,Y(0)); g.closePath();
  g.fillStyle=grd; g.fill();

  // ── 기준선(0) ──
  g.strokeStyle='#e5e7eb'; g.lineWidth=1.5;
  g.beginPath(); g.moveTo(px0,Y(0)); g.lineTo(px1,Y(0)); g.stroke();

  // ── 라인(초록) ──
  g.beginPath(); g.moveTo(X(0),Y(V[0]));
  for(let i=1;i<=li;i++) g.lineTo(X(i),Y(V[i]));
  if(li<NX && fr>0) g.lineTo(hx,hy);
  g.lineWidth=Math.max(3.5,F*0.24); g.lineJoin='round'; g.lineCap='round';
  g.strokeStyle=GREEN; g.stroke();

  // ── 매달 코인닷(골드) — 이미 지나온 달 ──
  const cr=cl((px1-px0)/Math.max(NX,1)*0.16, 2, F*0.22);
  for(let i=0;i<=li;i++){
    g.beginPath(); g.arc(X(i),Y(V[i]),cr,0,7); g.fillStyle=GOLD; g.fill();
  }

  // ── 헤드닷(골드) ──
  g.beginPath(); g.arc(hx,hy,Math.max(5,F*0.34),0,7); g.fillStyle=GOLDDK; g.fill();
  g.beginPath(); g.arc(hx,hy,Math.max(2.5,F*0.17),0,7); g.fillStyle='#fff'; g.fill();

  // ── y 눈금(0 / final) — 컴팩트 ──
  g.textAlign='right'; g.textBaseline='middle'; g.font='800 '+Math.round(F*0.6)+'px sans-serif';
  g.fillStyle='#9ca3af';
  g.fillText('0',px0-F*0.3,Y(0));
  g.fillText(Math.round(D.final/1e4).toLocaleString('en-US')+'만',px0-F*0.3,Y(D.final));

  // ── x 라벨(시작/중간/끝) ──
  g.textAlign='center'; g.textBaseline='top'; g.fillStyle='#9ca3af';
  g.font='800 '+Math.round(F*0.58)+'px sans-serif';
  for(const i of [0,(NX/2),NX]){ const s=mlab(i); if(s) g.fillText(s,X(i),chBot+F*0.35); }

  // ── 큰 카운터(0 → head value) — 카드 폭에 맞춤 ──
  const cur=Math.round(hv);
  const _t=won(cur)+'원';
  g.textAlign='center'; g.textBaseline='middle';
  let _cf=CF; g.font='900 '+Math.round(_cf)+'px sans-serif';
  const _mw=SW-2*Math.max(F*1.0,SW*0.06);
  const _tw=g.measureText(_t).width;
  if(_tw>_mw){ _cf=_cf*_mw/_tw; g.font='900 '+Math.round(_cf)+'px sans-serif'; }
  g.fillStyle=GREENDK;
  g.fillText(_t,SX0+SW/2,cntY);

  // ── 기간 강조: 큰 '12.6년' (바운스) + 작은 서브 ──
  const ba=c01((t-BADGE_ST)/BADGE_DUR);
  if(ba>0.01 && D.years){
    const e=eBack(ba), sc=0.5+0.5*e;
    const yf=cl(SH*0.135,24,66);
    g.save(); g.translate(SX0+SW/2,badgeY); g.scale(sc,sc);
    g.textAlign='center'; g.textBaseline='middle';
    g.lineWidth=Math.max(4,yf*0.16); g.strokeStyle='#fff'; g.lineJoin='round';
    g.font='900 '+Math.round(yf)+'px sans-serif';
    g.strokeText(D.years+'년',0,0); g.fillStyle=GOLDDK; g.fillText(D.years+'년',0,0);
    g.restore();
  }
  // 서브: '동안 모은 분배금 = 투입의 XX%'
  const sa=c01((t-(BADGE_ST+280))/420);
  if(sa>0.01){
    g.globalAlpha=sa;
    const sf=cl(SH*0.05,11,26);
    g.textAlign='center'; g.textBaseline='top';
    g.font='800 '+Math.round(sf)+'px sans-serif'; g.fillStyle=GOLDDK;
    g.fillText('동안 모은 분배금 = 투입의 '+D.pctFinal+'%',SX0+SW/2,badgeY+cl(SH*0.085,18,44));
    g.globalAlpha=1;
  }
}
window.__renderAt=draw; draw(0);
'''