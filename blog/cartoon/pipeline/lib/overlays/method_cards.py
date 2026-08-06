"""method_cards — 두 매수 방식 카드 안에 투입액 카운터.

만화의 빈 슬롯 두 곳(params.slot_lump / params.slot_dca)에 각각 카드를 그린다.
  · lump 카드(빨강 톤) = P['dca']['total'] 을 '한 번에' 0→total 빠르게 카운트업.
  · dca  카드(파랑 톤) = 같은 total 을 dca_months 회에 걸쳐 계단식으로 누적.
각 카드 안: 큰 금액(만 단위) + 작은 방식설명 + 진행 표시(pill/pips).
좌표는 1080×1080 기준, 반드시 slot 사각형 [x0,y0,x1,y1] 안에만 그린다.
renderAt(t): t(ms)만으로 결정적. 끝나면 최종프레임 hold.
"""
import json

from lib.scene_common import html_skeleton, b64  # noqa: F401  (계약상 import)


def _clamp_slot(s):
    """slot 을 1080 스테이지 안으로 clamp + 정규화 [x0,y0,x1,y1]."""
    x0, y0, x1, y1 = [float(v) for v in s]
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    x0 = max(0.0, min(x0, 1080.0)); x1 = max(0.0, min(x1, 1080.0))
    y0 = max(0.0, min(y0, 1080.0)); y1 = max(0.0, min(y1, 1080.0))
    return [x0, y0, x1, y1]


def build(P):
    params = P.get('params') or {}
    dca = P['dca']
    total = int(dca['total'])
    months = int(dca.get('dca_months', 6)) or 6

    slot_lump = _clamp_slot(params.get('slot_lump') or [80, 360, 520, 720])
    slot_dca = _clamp_slot(params.get('slot_dca') or [560, 360, 1000, 720])

    D = {
        'SL': slot_lump,
        'SD': slot_dca,
        'TOTAL': total,
        'M': months,
        'lab': {
            'lumpT': '일시매수',          # 일시매수
            'lumpS': '한 번에 전액',  # 한 번에 전액
            'dcaT': '분할매수',           # 분할매수
            'dcaS': str(months) + '개월 분할',  # N개월 분할
            'unit': '만',                             # 만
            'gaewol': '개월',                     # 개월
        },
    }

    css = "#cv{position:absolute;inset:0;width:1080px;height:1080px;z-index:2}"
    body = '<canvas id="cv" width="1080" height="1080"></canvas>'

    js = P['helpers'] + '\nwindow.__P=' + json.dumps(D, ensure_ascii=False) + ';\n' + _MAIN_JS
    return html_skeleton(P['bg'], css, body, js)


# renderAt(t): 결정적. Math.random/Date.now 미사용.
_MAIN_JS = r'''
const D=window.__P, SL=D.SL, SD=D.SD, TOTAL=D.TOTAL, M=D.M, LAB=D.lab;
const g=document.getElementById('cv').getContext('2d');

// 톤(빨강=일시 / 파랑=분할)
const TL={bg:'#fff5f5',bd:'#dc2626',tx:'#dc2626',dim:'rgba(220,38,38,.22)'};
const TD={bg:'#eff6ff',bd:'#2563eb',tx:'#2563eb',dim:'rgba(37,99,235,.22)'};

// 타이밍(ms)
const APP=450;            // 카드 등장(페이드+상승)
const LS=520, LD=760;     // lump: 0→total 카운트업
const DS=520, SD_STEP=520;// dca : 스텝 간격

const m2=v=>Math.round(v/1e4).toLocaleString('en-US')+LAB.unit;

function roundRect(x,y,w,h,r){g.beginPath();g.roundRect(x,y,w,h,r);}

// pips: dca 는 월별 칸, lump 는 진행 pill
function pips(x0,y0,w,h,tn,filled,total){
  const cy=y0+h*0.68;
  const pw=w*0.088, gap=w*0.030, tw=total*pw+(total-1)*gap;
  let px=x0+(w-tw)/2, ph=Math.max(7,h*0.055), r=ph/2;
  for(let i=0;i<total;i++){
    g.fillStyle=(i<filled)?tn.bd:tn.dim;
    roundRect(px,cy-ph/2,pw,ph,r);g.fill();
    px+=pw+gap;
  }
}
function pill(x0,y0,w,h,tn,frac){
  const cy=y0+h*0.68, pw=w*0.62, ph=Math.max(8,h*0.058), r=ph/2;
  const px=x0+(w-pw)/2;
  g.fillStyle=tn.dim;roundRect(px,cy-ph/2,pw,ph,r);g.fill();
  const fw=Math.max(ph, pw*c01(frac));
  g.fillStyle=tn.bd;roundRect(px,cy-ph/2,fw,ph,r);g.fill();
}

// 카드 한 장(bigText 는 큰 금액, popS 는 스텝 팝 스케일)
function card(s,tn,rise,alpha,title,bigText,sub,popS,drawProg){
  const x0=s[0],y0=s[1],x1=s[2],y1=s[3],w=x1-x0,h=y1-y0;
  if(w<8||h<8)return;
  g.save();g.globalAlpha=alpha;g.translate(0,rise);
  // 배경 + 테두리
  roundRect(x0,y0,w,h,Math.min(30,h*0.14));g.fillStyle=tn.bg;g.fill();
  g.lineWidth=Math.max(3,w*0.012);g.strokeStyle=tn.bd;g.stroke();
  g.textAlign='center';
  // 제목(작게, 상단)
  const tF=Math.max(15,Math.min(w*0.11,h*0.13));
  g.textBaseline='middle';g.fillStyle=tn.bd;g.font='800 '+tF+'px sans-serif';
  g.fillText(title,x0+w/2,y0+h*0.185);
  // 큰 금액(중앙) — pop 스케일 적용
  const bF=Math.max(30,Math.min(w*0.20,h*0.30));
  const bx=x0+w/2, by=y0+h*0.45;
  g.save();g.translate(bx,by);g.scale(popS,popS);
  g.fillStyle=tn.tx;g.font='900 '+bF+'px sans-serif';g.textBaseline='middle';
  g.fillText(bigText,0,0);g.restore();
  // 진행 표시(pill/pips)
  drawProg(x0,y0,w,h,tn);
  // 작은 방식설명(하단)
  const sF=Math.max(13,Math.min(w*0.062,h*0.085));
  g.fillStyle='#52525b';g.font='700 '+sF+'px sans-serif';g.textBaseline='middle';
  g.fillText(sub,x0+w/2,y0+h*0.855);
  g.restore();
}

function renderAt(t){
  g.clearRect(0,0,1080,1080);
  const app=c01(t/APP), e=eOut(app), rise=(1-e)*22, al=app;

  // ── lump: 한 번에 0→total ─────────────────────────────
  const lk=eOut(c01((t-LS)/LD));
  const lcur=Math.round(TOTAL*lk);
  card(SL,TL,rise,al,LAB.lumpT,m2(lcur),LAB.lumpS,1,
    (x0,y0,w,h,tn)=>pill(x0,y0,w,h,tn,lk));

  // ── dca: total 을 M회 계단식 누적 ────────────────────
  const sf=(t-DS)/SD_STEP;
  let si=Math.floor(sf); if(si<0)si=0; if(si>M)si=M;
  const dcur=Math.round(TOTAL*si/M);
  const f=sf-Math.floor(sf);
  const pop=(sf>0&&si>=1)?0.15*Math.exp(-9*Math.max(0,f)):0;
  const dsub=(si<M)?(si+'/'+M+LAB.gaewol):LAB.dcaS;
  card(SD,TD,rise,al,LAB.dcaT,m2(dcur),dsub,1+pop,
    (x0,y0,w,h,tn)=>pips(x0,y0,w,h,tn,si,M));
}
window.__renderAt=renderAt; renderAt(0);
'''