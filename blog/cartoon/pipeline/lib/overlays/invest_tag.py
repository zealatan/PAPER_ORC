"""invest_tag — 슬롯 안에 '투입(매수) 표시' 카드.

만화의 빈 슬롯 박스(P['params']['slot']=[x0,y0,x1,y1]) '안에만' 그린다.
캐릭터/말풍선/제목 침범 금지 — 카드는 슬롯 사각형을 채우고, 폰트·패딩은
슬롯 크기에 비례한다.

내용(정적에 가까운 페이드/팝인):
  · 상단 라벨  : '<QYLD.name> 매수'  (앞에 종목색 점)
  · 큰 금액    : P['income']['invest'] → '1,000만원'  (won 헬퍼)
  · 하단 칩    : '커버드콜 ETF'        (종목색 배경 pill)

애니메이션: 카드 전체가 중앙 기준 팝인(eBack) + 페이드, 이후 최종프레임 hold.
renderAt(t_ms)는 t만으로 결정적(Math.random/Date.now 미사용).
"""
import json

from lib.scene_common import html_skeleton, b64  # noqa: F401  (계약상 import)


def build(P):
    income = P['income']
    params = P.get('params') or {}

    slot = params['slot']
    x0, y0, x1, y1 = (int(round(float(v))) for v in slot)

    q = income['QYLD']
    D = {
        'slot': [x0, y0, x1, y1],
        'name': q.get('name', 'QYLD'),
        'color': q.get('color', '#dc2626'),
        'invest': int(income['invest']),
        'sub': '커버드콜 ETF',
    }

    css = "#cv{position:absolute;inset:0;z-index:4}"
    body = '<canvas id="cv" width="1080" height="1080"></canvas>'

    js = P['helpers'] + '\nconst D=' + json.dumps(D, ensure_ascii=False) + ';\n' + _MAIN_JS
    return html_skeleton(P['bg'], css, body, js)


# renderAt(t): t(ms)만 → 결정적. 팝인 ~500ms 후 hold.
_MAIN_JS = r'''
const g=document.getElementById('cv').getContext('2d');
const S=D.slot, SX0=S[0],SY0=S[1],SX1=S[2],SY1=S[3];
const SW=SX1-SX0, SH=SY1-SY0, CX=SX0+SW/2, CY=SY0+SH/2;
const COL=D.color;

// 슬롯 크기에 비례한 폰트/반경
const RAD=Math.min(SW,SH)*0.08;
const HF=cl(SH*0.115,13,42);          // 상단 라벨
const BF=cl(SH*0.24,22,96);           // 큰 금액
const SF=cl(SH*0.075,10,28);          // 하단 칩

// 금액 문자열: '1,000만원'
const AMT=won(Math.round(D.invest/1e4))+'만원';

function rr(x,y,w,h,r){g.beginPath();g.roundRect(x,y,w,h,r);}

function draw(t){
  g.clearRect(0,0,1080,1080);
  const app=c01(t/300);
  const k=c01(t/500);
  const sc=lerp(0.86,1,eBack(k));     // 중앙 기준 팝인(오버슈트)

  g.save();
  g.globalAlpha=app;
  g.translate(CX,CY); g.scale(sc,sc); g.translate(-CX,-CY);

  // ── 카드 배경 ──
  g.fillStyle='rgba(120,120,125,0.10)'; rr(SX0,SY0,SW,SH,RAD); g.fill();
  g.lineWidth=Math.max(2.5,SW*0.007); g.strokeStyle=COL; g.stroke();

  // ── 상단 라벨: 종목색 점 + '<name> 매수' (그룹 중앙정렬) ──
  const hdr=D.name+' 매수';
  g.font='800 '+Math.round(HF)+'px sans-serif';
  g.textAlign='left'; g.textBaseline='middle';
  const tw=g.measureText(hdr).width;
  const dotR=HF*0.30, gap=HF*0.42;
  const grpW=dotR*2+gap+tw, gx=CX-grpW/2, hy=SY0+SH*0.30;
  g.fillStyle=COL; g.beginPath(); g.arc(gx+dotR,hy,dotR,0,7); g.fill();
  g.fillStyle='#111'; g.fillText(hdr,gx+dotR*2+gap,hy+1);

  // ── 큰 금액 ──
  g.textAlign='center'; g.textBaseline='middle';
  g.fillStyle='#111'; g.font='900 '+Math.round(BF)+'px sans-serif';
  g.fillText(AMT,CX,SY0+SH*0.56);

  // ── 하단 칩: 종목색 pill + 흰 글씨 ──
  g.font='800 '+Math.round(SF)+'px sans-serif';
  const sw=g.measureText(D.sub).width;
  const padx=SF*0.85, ch=SF*1.9, cw=sw+padx*2, cyy=SY0+SH*0.80;
  g.fillStyle=COL; rr(CX-cw/2,cyy-ch/2,cw,ch,ch/2); g.fill();
  g.fillStyle='#fff'; g.textAlign='center'; g.textBaseline='middle';
  g.fillText(D.sub,CX,cyy+1);

  g.restore();
}
window.__renderAt=draw; draw(0);
'''
