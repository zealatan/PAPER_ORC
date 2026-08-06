"""yield_badge — 슬롯 안에 QYLD 분배율 배지(큰 숫자 카운트업).

만화의 빈 슬롯(P['params']['slot']=[x0,y0,x1,y1], 1080 기준) '안에만' 그린다.
캐릭터/말풍선/제목 침범 금지 — 모든 좌표는 slot 안으로 clamp, 폰트는 슬롯 크기 비례.

구성(슬롯 중앙정렬):
  · 작은 라벨   '분배율'
  · 큰 숫자     '연 11.7%'  (0 → yield_pct, eOut 카운트업)
  · 작은 주의문 '※ 분배율 ≠ 수익률'
강조색 = 골드(달콤함). 약 2초 카운트업 후 최종프레임 hold.

데이터: P['income']['QYLD']['yield_pct'] (분배율 %).
renderAt(t_ms)는 t만으로 결정적(Math.random/Date.now 금지).
"""
import json

from lib.scene_common import html_skeleton, b64  # noqa: F401  (계약상 import)


GOLD = '#C8901A'        # 큰 숫자·강조(달콤한 골드)
GOLD_SOFT = '#E7C15A'   # 카드 테두리
INK = '#3f3f46'         # 라벨
WARN = '#a1a1aa'        # 주의문


def build(P):
    income = P['income']
    params = P.get('params') or {}
    slot = params['slot']
    x0, y0, x1, y1 = (float(v) for v in slot)

    yld = float(income['QYLD'].get('yield_pct') or 0.0)

    D = {
        'slot': [x0, y0, x1, y1],
        'yld': yld,
        'gold': GOLD, 'goldSoft': GOLD_SOFT, 'ink': INK, 'warn': WARN,
    }

    css = "#cv{position:absolute;inset:0;z-index:4}"
    body = '<canvas id="cv" width="1080" height="1080"></canvas>'

    js = P['helpers'] + '\nconst D=' + json.dumps(D, ensure_ascii=False) + ';\n' + _MAIN_JS
    return html_skeleton(P['bg'], css, body, js)


# renderAt(t): t(ms)만으로 결정적. ~2s 카운트업 eOut, 이후 hold.
_MAIN_JS = r'''
const g=document.getElementById('cv').getContext('2d');
const S=D.slot, SX0=S[0],SY0=S[1],SX1=S[2],SY1=S[3];
const SW=SX1-SX0, SH=SY1-SY0;
const CX=SX0+SW/2, CY=SY0+SH/2;
const YLD=D.yld;
const DUR=2000, DELAY=200;

// 슬롯 크기 비례 폰트/간격
const FBIG=cl(SH*0.26,26,150);   // 큰 숫자
const FLAB=cl(SH*0.085,12,40);   // '분배율'
const FWARN=cl(SH*0.062,10,30);  // 주의문
const GAP=cl(SH*0.04,6,26);      // 블록 간격
const RAD=Math.min(SW,SH)*0.06;

function rr(x,y,w,h,r){g.beginPath();g.roundRect(x,y,w,h,r);}
const ytxt=v=>'연 '+v.toFixed(1)+'%';

function draw(t){
  g.clearRect(0,0,1080,1080);

  // ── 카드 배경(달콤한 골드 톤) ──
  const app=c01(t/380), e=eOut(app);
  g.globalAlpha=app;
  const pad=cl(Math.min(SW,SH)*0.04,4,16);
  g.fillStyle='rgba(120,120,125,0.10)';
  rr(SX0+pad,SY0+pad,SW-2*pad,SH-2*pad,RAD); g.fill();
  g.lineWidth=Math.max(3,Math.min(SW,SH)*0.012); g.strokeStyle=D.goldSoft; g.stroke();
  g.globalAlpha=1;
  if(app<=0.01) return;

  // ── 카운트업 값 ──
  const k=eOut(c01((t-DELAY)/DUR));
  const cur=YLD*k;

  // 세 블록의 높이를 재서 세로 중앙정렬
  const hLab=FLAB, hBig=FBIG, hWarn=FWARN;
  const totH=hLab+GAP+hBig+GAP*0.9+hWarn;
  let cy=CY-totH/2;

  // 라벨 '분배율'
  g.textAlign='center'; g.textBaseline='top';
  g.fillStyle=D.ink; g.font='800 '+Math.round(FLAB)+'px sans-serif';
  g.fillText('분배율', CX, cy);
  cy+=hLab+GAP;

  // 큰 숫자(카운트업 중 살짝 팝)
  const pop=1+(1-c01((t-DELAY)/DUR))*0.06;
  g.save();
  g.translate(CX, cy+hBig*0.5);
  g.scale(pop,pop);
  g.textAlign='center'; g.textBaseline='middle';
  g.fillStyle=D.gold; let _bf=FBIG; g.font='900 '+Math.round(_bf)+'px sans-serif';
  var _tw=g.measureText(ytxt(cur)).width, _mw=SW*0.84;
  if(_tw>_mw){ _bf=_bf*_mw/_tw; g.font='900 '+Math.round(_bf)+'px sans-serif'; }
  g.fillText(ytxt(cur), 0, 0);
  g.restore();
  cy+=hBig+GAP*0.9;

  // 주의문 '※ 분배율 ≠ 수익률' (숫자 다 찬 뒤 페이드인)
  const wa=c01((t-(DELAY+DUR*0.7))/450);
  if(wa>0.01){
    g.globalAlpha=wa;
    g.textAlign='center'; g.textBaseline='top';
    g.fillStyle=D.warn; g.font='700 '+Math.round(FWARN)+'px sans-serif';
    g.fillText('※ 분배율 ≠ 수익률', CX, cy);
    g.globalAlpha=1;
  }
}
window.__renderAt=draw; draw(0);
'''