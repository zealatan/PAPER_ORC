"""compare_table — 슬롯 안에 QYLD vs SPY 비교표(분배율 함정 강조).

만화의 빈 슬롯 박스(P['params']['slot']=[x0,y0,x1,y1]) '안에만' 그린다.
캐릭터/말풍선/제목 침범 금지 — 모든 좌표는 슬롯 로컬(캔버스=슬롯 크기).

레이아웃(3행 × 2열 표):
  헤더 열 = ['QYLD'(빨강 톤), 'SPY'(파랑 톤)]
  행       = ['총수익','가격 변화','분배율']
  값       = total_mult'배' · price_chg'%'(부호) · yield_pct'%'
             (SPY 분배율 데이터 없으면 '낮음')
  셀 순차 페이드인(행→열).
  하단 한 줄 카피: '분배율은 수익률이 아니다'.

타임라인(≈4s): 프레임(0.2~0.6s) → 셀 순차(0.9s~) → 하단 카피(3.2s~) → 최종 hold.

데이터: P['income'] (EP3). renderAt(t_ms)는 결정적(Math.random/Date.now 금지).
스타일 톤: recovery_table.py(표부) 참고.
"""
import json

from lib.scene_common import html_skeleton, b64  # noqa: F401  (계약상 import)


QYLD_COLOR = '#dc2626'   # QYLD = 빨강계열
SPY_COLOR = '#2563eb'    # SPY  = 파랑계열


def _fmt_mult(m):
    try:
        return ('%.2f배' % float(m))
    except (TypeError, ValueError):
        return '—'


def _fmt_pct_signed(v):
    if v is None:
        return '—'
    try:
        n = int(round(float(v)))
    except (TypeError, ValueError):
        return '—'
    return ('+' if n >= 0 else '−') + str(abs(n)) + '%'


def _fmt_yield(v):
    if v is None:
        return None
    try:
        return ('%.1f%%' % float(v))
    except (TypeError, ValueError):
        return None


def build(P):
    income = P['income']
    params = P.get('params') or {}
    slot = params['slot']
    x0, y0, x1, y1 = (float(v) for v in slot)
    W = int(round(x1 - x0))
    H = int(round(y1 - y0))
    left = int(round(x0))
    top = int(round(y0))

    q = income['QYLD']
    s = income['SPY']
    qC = q.get('color') or QYLD_COLOR
    sC = s.get('color') or SPY_COLOR
    qName = q.get('name') or 'QYLD'
    sName = s.get('name') or 'SPY'

    # SPY 분배율은 원자료가 없으면 '낮음'
    spy_yield = _fmt_yield(s.get('yield_pct'))
    if spy_yield is None:
        spy_yield = '낮음'

    inv = income['invest']

    def wan(v):
        return '{:,}만원'.format(int(round(v / 1e4)))

    qTot = q.get('total_mult', 1) * inv
    sTot = s.get('total_mult', 1) * inv
    dist = q.get('dist_cum_final', 0)

    story = params.get('story')
    if story == 'drawdown':
        # 하락장 비교(총수익·최대낙폭·분배금)
        rows = [
            {'label': '총수익', 'a': _fmt_pct_signed(q.get('ret_pct')),
             'b': _fmt_pct_signed(s.get('ret_pct'))},
            {'label': '최대낙폭', 'a': _fmt_pct_signed(q.get('mdd')),
             'b': _fmt_pct_signed(s.get('mdd'))},
            {'label': '분배금', 'a': wan(dist), 'b': '거의 없음'},
        ]
        footer = '투입 ' + wan(inv) + ' · 방패는 아니지만 완충'
    else:
        # 기본(EP3): 최종잔고·가격변화·분배금누적·분배율
        rows = [
            {'label': '최종 잔고', 'a': wan(qTot), 'b': wan(sTot),
             'aSub': _fmt_mult(q.get('total_mult')), 'bSub': _fmt_mult(s.get('total_mult'))},
            {'label': '가격 변화', 'a': _fmt_pct_signed(q.get('price_chg')),
             'b': _fmt_pct_signed(s.get('price_chg'))},
            {'label': '분배금 누적', 'a': wan(dist), 'b': '—'},
            {'label': '분배율', 'a': _fmt_yield(q.get('yield_pct')) or '—', 'b': spy_yield},
        ]
        footer = '투입 ' + wan(inv) + ' · 분배율 ≠ 수익률'

    D = {
        'W': W, 'H': H,
        'rows': rows,
        'invest': wan(inv),
        'colHd': [qName, sName],
        'colC': [qC, sC],
        'footer': footer,
    }

    css = (
        f"#ct{{position:absolute;left:{left}px;top:{top}px;"
        f"width:{W}px;height:{H}px;z-index:3}}"
        "#ctcv{position:absolute;inset:0;width:100%;height:100%}"
    )
    body = (
        f'<div id="ct"><canvas id="ctcv" width="{W}" height="{H}"></canvas></div>'
    )

    js = (
        P['helpers']
        + '\nwindow.__CT=' + json.dumps(D, ensure_ascii=False) + ';\n'
        + _MAIN_JS
    )
    return html_skeleton(P['bg'], css, body, js)


# renderAt(t): t(ms)만으로 결정적. 끝나면 최종프레임 hold.
_MAIN_JS = r'''
const D=window.__CT;
const W=D.W, H=D.H, sc=W/500;
const g=document.getElementById('ctcv').getContext('2d');
const R=(px)=>px*sc;
const nR=D.rows.length;                 // 3
const colC=D.colC, colHd=D.colHd;

// ── 영역 분할: 표 본체 / 하단 카피 ──
const footH=R(30);
const tTop=R(4);
const tBot=H-footH-R(8);
const LBLW=W*0.32;                      // 행 라벨 열 폭
const colW=(W-LBLW)/2;
const hdH=(tBot-tTop)*0.24;             // 헤더 밴드 높이
const rowsTop=tTop+hdH;
const rowH=(tBot-rowsTop)/nR;
const colX0=LBLW, colX1=LBLW+colW;
const colX=[colX0+colW*0.5, colX1+colW*0.5];   // 값 열 중심

// 열 톤 배경(연한 빨강/파랑)
function hexA(hex,a){
  const h=hex.replace('#',''); const r=parseInt(h.slice(0,2),16),
    gg=parseInt(h.slice(2,4),16), b=parseInt(h.slice(4,6),16);
  return 'rgba('+r+','+gg+','+b+','+a+')';
}

function drawFrame(a){
  if(a<=0) return;
  g.globalAlpha=a;
  // 열 톤 배경(헤더~본체)
  g.fillStyle=hexA(colC[0],0.06); g.fillRect(colX0,tTop,colW,tBot-tTop);
  g.fillStyle=hexA(colC[1],0.06); g.fillRect(colX1,tTop,colW,tBot-tTop);
  // 헤더 밴드 살짝 진하게
  g.fillStyle=hexA(colC[0],0.12); g.fillRect(colX0,tTop,colW,hdH);
  g.fillStyle=hexA(colC[1],0.12); g.fillRect(colX1,tTop,colW,hdH);
  // 헤더 하단 구분선
  g.strokeStyle='#d4d4d8'; g.lineWidth=R(1.4);
  g.beginPath(); g.moveTo(0,rowsTop); g.lineTo(W,rowsTop); g.stroke();
  // 행 구분선
  for(let r=1;r<nR;r++){ const y=rowsTop+rowH*r;
    g.strokeStyle='#eceef1'; g.lineWidth=R(1);
    g.beginPath(); g.moveTo(0,y); g.lineTo(W,y); g.stroke(); }
  // 열 세로선
  g.strokeStyle='#e6e8eb'; g.lineWidth=R(1);
  g.beginPath(); g.moveTo(colX0,tTop); g.lineTo(colX0,tBot); g.stroke();
  g.beginPath(); g.moveTo(colX1,tTop); g.lineTo(colX1,tBot); g.stroke();
  // 헤더 텍스트(열 이름 = 컬러)
  g.textBaseline='middle'; g.textAlign='center';
  g.font='900 '+R(23)+'px sans-serif';
  for(let c=0;c<2;c++){ g.fillStyle=colC[c]; g.fillText(colHd[c],colX[c],tTop+hdH*0.5); }
  // 행 라벨
  g.textAlign='left'; g.fillStyle='#3f3f46'; g.font='800 '+R(18)+'px sans-serif';
  for(let r=0;r<nR;r++) g.fillText(D.rows[r].label,R(8),rowsTop+rowH*(r+0.5));
  g.globalAlpha=1;
}

function drawCells(t){
  const T0=850, STEP=260, DUR=360;
  g.textAlign='center';
  for(let r=0;r<nR;r++){
    const row=D.rows[r], vals=[row.a,row.b], subs=[row.aSub,row.bSub];
    for(let c=0;c<2;c++){
      const idx=r*2+c, a=c01((t-(T0+idx*STEP))/DUR);
      if(a<=0) continue;
      const hasSub=!!subs[c];
      const yy=rowsTop+rowH*(r+0.5);
      const pop=1+(1-a)*0.10;
      g.save(); g.translate(colX[c],yy); g.scale(pop,pop);
      g.globalAlpha=a; g.fillStyle=colC[c];
      g.textBaseline=hasSub?'alphabetic':'middle';
      g.font='900 '+R(hasSub?23:26)+'px sans-serif';
      g.fillText(vals[c],0,hasSub?-R(2):0);
      if(hasSub){ g.textBaseline='top'; g.font='800 '+R(15)+'px sans-serif'; g.globalAlpha=a*0.85;
        g.fillText(subs[c],0,R(3)); }
      g.restore();
    }
  }
  g.globalAlpha=1;
}

function drawFooter(t){
  const a=c01((t-3200)/450);
  if(a<=0) return;
  g.globalAlpha=a;
  const fy=tBot+footH*0.5+R(4);
  g.textAlign='center'; g.textBaseline='middle';
  g.fillStyle='#111'; g.font='800 '+R(18)+'px sans-serif';
  const rise=(1-a)*R(6);
  g.fillText(D.footer,W/2,fy+rise);
  g.globalAlpha=1;
}

function renderAt(t){
  g.clearRect(0,0,W,H);
  drawFrame(c01((t-200)/400));
  drawCells(t);
  drawFooter(t);
}
window.__renderAt=renderAt; renderAt(0);
'''
