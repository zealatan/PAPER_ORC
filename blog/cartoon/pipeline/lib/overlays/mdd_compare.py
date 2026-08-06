"""mdd_compare — 슬롯을 좌/우로 나눠 일시매수 vs 분할매수 '2022 저점 최대낙폭'을 비교.

P['dca']['lump']['mdd'] / P['dca']['dca']['mdd'] (둘 다 음수 %) 를
0→값 카운트다운(eOut)하며 큰 빨강 %로 표시. 분할이 덜 빠졌음을
막대 길이(|mdd| 비례)+색농도(주황=완화)+'완화' 배지로 강조.
좌표·폰트는 P['params']['slot']=[x0,y0,x1,y1] 사각형 안에만.
"""
import json

from lib.scene_common import html_skeleton, b64  # noqa: F401 (계약상 import)


def build(P):
    params = P.get('params') or {}

    slot = params.get('slot') or [300, 300, 780, 780]
    x0, y0, x1, y1 = [int(v) for v in slot]

    if P.get('dca'):
        dca = P['dca']
        lump_mdd = float(dca['lump']['mdd'])   # 좌(더 깊은 낙폭)
        dca_mdd = float(dca['dca']['mdd'])      # 우(완화)
        lump_label = params.get('lump_label', '일시매수')
        dca_label = params.get('dca_label', '분할매수')
    else:
        # income 모드: 좌=벤치마크(더 깊음), 우=종목(완화)
        inc = P['income']
        a, b = inc['QYLD'], inc['SPY']
        lump_mdd = float(b['mdd']); lump_label = b.get('name', '시장')
        dca_mdd = float(a['mdd']);  dca_label = a.get('name', 'QYLD')

    D = {
        'slot': [x0, y0, x1, y1],
        'lumpMDD': lump_mdd,
        'dcaMDD': dca_mdd,
        'title': params.get('title', '2022 저점 최대낙폭'),
        'lumpLabel': params.get('lump_label', lump_label),
        'dcaLabel': params.get('dca_label', dca_label),
    }

    css = "#cv{position:absolute;inset:0;z-index:2}"
    body = '<canvas id="cv" width="1080" height="1080"></canvas>'

    js = P['helpers'] + '\nconst D=' + json.dumps(D, ensure_ascii=False) + ';\n' + _MAIN_JS
    return html_skeleton(P['bg'], css, body, js)


# renderAt(t): t(ms)만으로 결정적. Math.random/Date.now 미사용. 끝나면 최종프레임 hold.
_MAIN_JS = r'''
const S=D.slot, X0=S[0], Y0=S[1], X1=S[2], Y1=S[3];
const W=X1-X0, H=Y1-Y0, XM=(X0+X1)/2;
const g=document.getElementById('cv').getContext('2d');
const LM=D.lumpMDD, DM=D.dcaMDD;
const MAXMAG=Math.max(Math.abs(LM),Math.abs(DM))||1;
const RED='#dc2626', ORANGE='#f97316';
function fmtPct(v){return (v<=0?'−':'+')+Math.abs(v).toFixed(1)+'%';}
function col(cx, mdd, label, p, isDCA){
  const color=isDCA?ORANGE:RED;
  // 칸 라벨
  g.textAlign='center';g.textBaseline='alphabetic';
  g.fillStyle='#3f3f46';g.font='800 '+Math.round(cl(H*0.085,14,40))+'px sans-serif';
  g.fillText(label, cx, Y0+H*0.31);
  // 큰 빨강 % (카운트다운)
  const cur=mdd*p;
  const pf=Math.round(cl(Math.min(H*0.215,(W/2)*0.30),22,150));
  g.fillStyle=color;g.font='900 '+pf+'px sans-serif';
  g.fillText(fmtPct(cur), cx, Y0+H*0.54);
  // 아래로 자라는 막대(|mdd| 비례) — 분할은 짧고 옅게
  const barTop=Y0+H*0.61, barBot=Y1-H*0.11, barMax=barBot-barTop;
  const bw=Math.round(cl(W*0.16,26,88));
  const bh=barMax*(Math.abs(mdd)/MAXMAG)*p;
  g.fillStyle=isDCA?'rgba(249,115,22,.82)':'rgba(220,38,38,.92)';
  g.beginPath();g.roundRect(cx-bw/2, barTop, bw, Math.max(0.01,bh), 7);g.fill();
}
function renderAt(t){
  g.clearRect(0,0,1080,1080);
  // 상단 작은 제목
  const ta=c01(t/380);
  g.globalAlpha=ta;g.textAlign='center';g.textBaseline='alphabetic';
  g.fillStyle='#18181b';g.font='800 '+Math.round(cl(H*0.072,12,34))+'px sans-serif';
  g.fillText(D.title, XM, Y0+H*0.115);
  g.globalAlpha=1;
  // 중앙 분할선
  g.strokeStyle='#e4e4e7';g.lineWidth=2;
  g.beginPath();g.moveTo(XM,Y0+H*0.22);g.lineTo(XM,Y1-H*0.06);g.stroke();
  // 카운트다운 진행(eOut)
  const p=eOut(c01((t-450)/1800));
  col(X0+W*0.25, LM, D.lumpLabel, p, false);
  col(X0+W*0.75, DM, D.dcaLabel, p, true);
  // 완화(gap) 배지 — 분할 칸, 카운트 종료 후 등장
  const gap=Math.abs(LM)-Math.abs(DM);
  if(t>2350 && gap>0.05){
    const ba=eOut(c01((t-2350)/380));
    const cx=X0+W*0.75, cy=Y1-H*0.028;
    const fs=Math.round(cl(H*0.052,10,24));
    g.globalAlpha=ba;
    g.font='800 '+fs+'px sans-serif';
    const txt='낙폭 '+gap.toFixed(1)+'%p 완화';
    const tw=g.measureText(txt).width, pad=fs*0.7;
    const bw2=tw+pad*2, bh2=fs*1.8;
    g.fillStyle='rgba(22,163,74,.14)';
    g.beginPath();g.roundRect(cx-bw2/2, cy-bh2/2, bw2, bh2, bh2/2);g.fill();
    g.fillStyle='#16a34a';g.textAlign='center';g.textBaseline='middle';
    g.fillText(txt, cx, cy);
    g.globalAlpha=1;
  }
}
window.__renderAt=renderAt; renderAt(0);
'''
