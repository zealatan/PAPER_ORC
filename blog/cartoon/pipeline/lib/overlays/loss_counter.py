"""④ 오버레이: loss_counter — 현재 손실 카운트다운 카드.

레퍼런스 cartoon/scene_page7.html 를 파이썬 문자열 생성기로 포팅.
하드코딩 데이터(L) 대신 P['series']/P['meta']에서 총손실·총투입·총평가와
종목별 브레이크다운을 계산한다. 카드는 detect.red_bbox 로 검출한
빨강 '손실 -x,xxx,xxx' 텍스트를 덮도록 배치(없으면 레퍼런스 좌표 폴백).
"""
import json

from lib.scene_common import html_skeleton, b64  # noqa: F401
from lib import detect, data  # noqa: F401


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def build(P):
    series = P['series']
    meta = P['meta']
    params = P.get('params') or {}

    # ── 집계: 총투입/총평가/총손실 + 종목별 브레이크다운 ────────────
    inv_tot = sum(int(s['invested']) for s in series.values())
    val_tot = sum(int(s['final']) for s in series.values())
    loss = val_tot - inv_tot  # 손실이면 음수

    items = []
    for s in series.values():
        items.append({
            'name': s['name'],
            'color': s['color'],
            'loss': int(s['final']) - int(s['invested']),
        })

    asof = meta.get('asof', P.get('params', {}).get('asof', ''))

    # ── 카드 크기(브레이크다운 행수에 따라 높이 가변) ───────────────
    CW = int(params.get('card_w', 468))
    n = len(items)
    rows = max(1, (n + 1) // 2)          # 2열 배치
    CH = 176 + rows * 34 + 26            # rows=1 → 236 (레퍼런스와 동일)

    # ── 배치: 빨강 손실 텍스트를 덮도록 red_bbox 중심에 정렬 ────────
    left, top = 548, 700                 # 레퍼런스 폴백 좌표
    try:
        rb = detect.red_bbox(P['panel_png'])
    except Exception:
        rb = None
    if rb:
        left = _clamp(rb['cx'] - CW // 2, 8, 1080 - CW - 8)
        top = _clamp(rb['cy'] - CH // 2, 8, 1080 - CH - 8)

    L = {'asof': asof, 'invTot': inv_tot, 'valTot': val_tot,
         'loss': loss, 'items': items}
    Ljson = json.dumps(L, ensure_ascii=False)

    css = (
        f"#card{{position:absolute;left:{left}px;top:{top}px;width:{CW}px;height:{CH}px;"
        "background:#fff;border:3px solid #dc2626;border-radius:20px;"
        "box-shadow:0 10px 28px rgba(220,38,38,.18);z-index:2}"
        "#cv{position:absolute;inset:0}"
        "#flash{position:absolute;inset:0;background:#dc2626;opacity:0;z-index:3;"
        "pointer-events:none;mix-blend-mode:multiply}"
    )

    body = (
        f'<div id="card"><canvas id="cv" width="{CW}" height="{CH}"></canvas></div>'
        '<div id="flash"></div>'
    )

    js = P['helpers'] + (
        "\nconst L=" + Ljson + ";"
        "\nconst CW=" + str(CW) + ",CH=" + str(CH) + ";"
        "\nconst g=document.getElementById('cv').getContext('2d');"
        "\nconst card=document.getElementById('card'),flash=document.getElementById('flash');"
        "\nconst m2=v=>Math.round(v/1e4).toLocaleString('en-US')+'\\uB9CC';"
        "\nfunction draw(t){"
        "\n  g.clearRect(0,0,CW,CH);"
        "\n  g.textAlign='left';g.textBaseline='alphabetic';"
        "\n  g.fillStyle='#71717a';g.font='800 20px sans-serif';"
        "\n  g.fillText('\\uC190\\uC2E4 \\u00B7 '+L.asof,24,38);"
        "\n  const k=eOut(c01((t-600)/2000));"
        "\n  const cur=Math.round(L.loss*k);"
        "\n  g.fillStyle='#dc2626';g.font='900 52px sans-serif';g.textAlign='center';"
        "\n  g.fillText(won(cur)+'\\uC6D0',CW/2,104);"
        "\n  const val=Math.round(L.invTot+L.loss*k);"
        "\n  g.fillStyle='#52525b';g.font='700 19px sans-serif';g.textAlign='center';"
        "\n  g.fillText('\\uD22C\\uC785 '+m2(L.invTot)+' \\u2192 \\uD3C9\\uAC00 '+m2(val),CW/2,146);"
        "\n  const ba=c01((t-2600)/400);g.globalAlpha=ba;"
        "\n  for(let i=0;i<L.items.length;i++){"
        "\n    const it=L.items[i],col=i%2,row=(i/2)|0;"
        "\n    const dx=96+col*172,dy=190+row*34;"
        "\n    g.fillStyle=it.color;g.beginPath();g.arc(dx,dy,8,0,7);g.fill();"
        "\n    g.textAlign='left';g.textBaseline='alphabetic';"
        "\n    const nm=it.name+' ';"
        "\n    g.fillStyle='#111';g.font='800 22px sans-serif';"
        "\n    g.fillText(nm,dx+16,dy+7);"
        "\n    const nw=g.measureText(nm).width;"
        "\n    g.fillStyle='#dc2626';"
        "\n    g.fillText(man(it.loss),dx+16+nw,dy+7);"
        "\n  }"
        "\n  g.globalAlpha=1;"
        "\n}"
        "\nfunction renderAt(t){"
        "\n  const app=c01(t/450),e=eOut(app);card.style.opacity=app;"
        "\n  let sx=0,sy=0;const d=(t-2600)/1000;"
        "\n  if(d>=0&&d<0.5){const a=6*Math.exp(-8*d)*Math.sin(60*d);sx=a;sy=a*0.5;}"
        "\n  card.style.transform='translate('+sx+'px,'+((1-e)*24+sy)+'px)';"
        "\n  flash.style.opacity=(t>=2600&&t<2760)?Math.sin((t-2600)/160*Math.PI)*0.25:0;"
        "\n  draw(t);"
        "\n}"
        "\nwindow.__renderAt=renderAt;renderAt(0);"
    )

    return html_skeleton(P['bg'], css, body, js)
