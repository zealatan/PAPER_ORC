"""cover_chart — 만화 위 작은 카드에 2선 라인차트를 그려 '가짜 그래프'를 덮는다.

params:
  use    : [keyA, keyB]  # P['series']의 종목 키 2개 (없으면 앞 2개)
  window : [d0, d1]      # 실제날짜(토큰 치환 완료). 없으면 [buy_date, asof]

각 종목 data.window(series[key], d0, d1)로 value 계산(둘 다 100만 시작).
공유 y축(둘의 max). 범례+수익%. 라인 좌→우 reveal(t).
카드 위치·크기는 detect.green_bbox(panel_png)를 덮도록(없으면 우측중앙).
scene_cover.html 레퍼런스 비주얼/애니 포팅.
"""
import json

from lib.scene_common import html_skeleton, b64  # noqa: F401  (계약상 import)
from lib import detect, data


def build(P):
    series = P['series']
    meta = P['meta']
    params = P.get('params') or {}

    # ── 종목 2개 결정 ──────────────────────────────────────────────
    use = params.get('use') or list(series.keys())[:2]
    ka, kb = use[0], use[1]
    sa, sb = series[ka], series[kb]

    # ── 창(window) 날짜 ────────────────────────────────────────────
    win = params.get('window') or [meta['buy_date'], meta['asof']]
    d0, d1 = win[0], win[1]

    wa = data.window(sa, d0, d1)
    wb = data.window(sb, d0, d1)

    # 두 종목은 같은 거래일 축(build_series가 공통축) → 짧은 쪽에 맞춤
    N = min(len(wa['dates']), len(wa['value']),
            len(wb['dates']), len(wb['value']))
    dates = wa['dates'][:N]
    A = wa['value'][:N]
    B = wb['value'][:N]
    invest = wa['invest']

    ca = sa['color']
    cb = sb['color']
    na = sa['name']
    nb = sb['name']

    # ── 카드 위치·크기: green_bbox(가짜 +xx%)를 덮도록 ────────────
    bb = detect.green_bbox(P['panel_png'])
    MINW, MINH = 456, 388
    if bb:
        pad = 30
        x0, x1 = bb['x0'] - pad, bb['x1'] + pad
        y0, y1 = bb['y0'] - pad, bb['y1'] + pad
        w = max(MINW, x1 - x0)
        h = max(MINH, y1 - y0)
        left = bb['cx'] - w / 2.0
        top = bb['cy'] - h / 2.0
    else:
        left, top, w, h = 548, 548, MINW, MINH
    # 스테이지(1080) 안으로 clamp
    w = int(min(w, 1080))
    h = int(min(h, 1080))
    left = int(max(0, min(left, 1080 - w)))
    top = int(max(0, min(top, 1080 - h)))

    header = '%s vs %s · 실제' % (na, nb)

    # ── CSS (레퍼런스 포팅) ───────────────────────────────────────
    css = (
        "#card{position:absolute;background:#fff;border:3px solid #111;"
        "border-radius:22px;box-shadow:0 8px 26px rgba(0,0,0,.12);overflow:hidden;z-index:5}"
        "#hd{position:absolute;left:24px;top:16px;font:800 25px 'Pretendard',sans-serif;color:#111}"
        ".lg{position:absolute;left:24px;display:flex;align-items:center;gap:9px;"
        "font:800 27px 'Pretendard',sans-serif}"
        "#lg0{top:52px}#lg1{top:88px}"
        ".dot{width:20px;height:20px;border-radius:6px}"
        "#cv{position:absolute;inset:0}"
    )

    # ── BODY ──────────────────────────────────────────────────────
    body = (
        '<div id="card" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">'
        '<div id="hd">%s</div>'
        '<div class="lg" id="lg0"><span class="dot" style="background:%s"></span>'
        '<span style="color:#111">%s</span>'
        '<span id="p0" style="color:%s">+0%%</span></div>'
        '<div class="lg" id="lg1"><span class="dot" style="background:%s"></span>'
        '<span style="color:#111">%s</span>'
        '<span id="p1" style="color:%s">+0%%</span></div>'
        '<canvas id="cv" width="%d" height="%d"></canvas>'
        '</div>'
    ) % (left, top, w, h, header, ca, na, ca, cb, nb, cb, w, h)

    # ── JS ────────────────────────────────────────────────────────
    D = {'dates': dates, 'invest': invest, 'A': A, 'B': B, 'ca': ca, 'cb': cb}
    js = P['helpers'] + (
        "const D=" + json.dumps(D, ensure_ascii=False) + ";\n"
        "const dates=D.dates, invest=D.invest, A=D.A, B=D.B, N=dates.length;\n"
        "const g=document.getElementById('cv').getContext('2d');\n"
        "const p0=document.getElementById('p0'),p1=document.getElementById('p1');\n"
        "const W=" + str(w) + ", Hh=" + str(h) + ", NX=Math.max(1,N-1);\n"
        "const PADL=58,PADR=20,PADT=136,PADB=50;\n"
        "const vmax=Math.max(Math.max.apply(0,A),Math.max.apply(0,B))*1.04;\n"
        "const vmin=Math.min(Math.min.apply(0,A),Math.min.apply(0,B),invest)*0.97;\n"
        "const X=i=>PADL+(W-PADL-PADR)*(i/NX);\n"
        "const Y=v=>PADT+(Hh-PADT-PADB)*(1-(v-vmin)/(vmax-vmin||1));\n"
        "function grid(){\n"
        "  g.clearRect(0,0,W,Hh);\n"
        "  g.textAlign='right';g.textBaseline='middle';g.font='800 16px sans-serif';g.fillStyle='#333';\n"
        "  for(let t=0;t<=2;t++){const v=vmin+(vmax-vmin)*t/2,y=Y(v);g.strokeStyle='#f0f0f0';g.lineWidth=1;g.beginPath();g.moveTo(PADL,y);g.lineTo(W-PADR,y);g.stroke();g.fillText((v/10000).toFixed(0)+'만',PADL-6,y);}\n"
        "  g.textAlign='center';g.textBaseline='top';\n"
        "  for(let t=0;t<=2;t++){const i=Math.round(NX*t/2),x=X(i);g.fillText(dates[i].slice(5).replace('-','.'),x,Hh-PADB+8);}\n"
        "  const yb=Y(invest);g.strokeStyle='#d4d4d8';g.lineWidth=1.5;g.setLineDash([6,6]);g.beginPath();g.moveTo(PADL,yb);g.lineTo(W-PADR,yb);g.stroke();g.setLineDash([]);\n"
        "}\n"
        "function line(arr,color,k){const li=Math.min(N-1,Math.floor((N-1)*k));\n"
        "  g.beginPath();g.moveTo(X(0),Y(arr[0]));for(let i=1;i<=li;i++)g.lineTo(X(i),Y(arr[i]));\n"
        "  g.lineWidth=5;g.lineJoin='round';g.strokeStyle=color;g.stroke();\n"
        "  const cx=X(li),cy=Y(arr[li]);g.beginPath();g.arc(cx,cy,7,0,7);g.fillStyle=color;g.fill();g.beginPath();g.arc(cx,cy,3.5,0,7);g.fillStyle='#fff';g.fill();\n"
        "  return arr[li];}\n"
        "function draw(k){grid();\n"
        "  const vb=line(B,D.cb,k), va=line(A,D.ca,k);\n"
        "  p0.textContent=(va>=invest?'+':'')+(va/invest*100-100).toFixed(0)+'%';\n"
        "  p1.textContent=(vb>=invest?'+':'')+(vb/invest*100-100).toFixed(0)+'%';}\n"
        "window.__renderAt=function(t){draw(c01(eOut(c01(t/2600))));};\n"
        "draw(0);\n"
    )

    return html_skeleton(P['bg'], css, body, js)
