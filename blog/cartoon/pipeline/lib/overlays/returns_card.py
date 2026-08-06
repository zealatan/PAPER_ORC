"""returns_card — 실제 수익 카드(카운트업).

scene_page3.html 포팅: 흰 카드가 배경의 가짜 '+xx%' 초록 텍스트(green_bbox)를 덮고,
종목별 dot + 이름 + 수익%가 buy_date→asof 실제 성과로 카운트업. 평가금액(만원)도 동시 증가.

params:
    use : [series_key, ...]   # 표시할 종목(생략 시 P['series'] 전체)
    asof: 'YYYY-MM-DD'         # 성과 종료일(빌더가 'asof' 토큰을 치환)
"""
import json

from lib.scene_common import html_skeleton
from lib import detect, data


def build(P):
    series = P['series']
    meta = P['meta']
    params = P['params'] or {}

    keys = params.get('use') or list(series.keys())
    asof = params.get('asof') or meta['asof']
    buy = meta['buy_date']

    # ── 각 종목: buy_date→asof 구간 마지막 평가액으로 수익/평가금액 산출 ──
    rows = []
    for k in keys:
        s = series.get(k)
        if s is None:
            continue
        w = data.window(s, buy, asof)
        rows.append({
            'name': w['name'],
            'color': w['color'],
            'inv': w['invest'],          # 시작 원금(=100만 리베이스)
            'final': w['value'][-1],     # 마지막 평가액
        })
    n = max(1, len(rows))
    start_man = round(rows[0]['inv'] / 10000) if rows else 100

    # ── 헤더 날짜(M/D) ──
    try:
        y, mo, dy = asof.split('-')
        hd_date = f'{int(mo)}/{int(dy)}'
    except Exception:
        hd_date = asof

    # ── 카드 크기(행 수에 맞춰 동적) ──
    W = 404
    ROW_TOP0, ROW_GAP, SUB_DY = 66, 84, 44
    H = ROW_TOP0 + (n - 1) * ROW_GAP + SUB_DY + 30 + 12

    # ── 배치: green_bbox('+xx%') 중심을 덮되, 말풍선/캐릭터/무대 경계 회피 ──
    cx, cy = 768, 464  # 폴백(레퍼런스 카드 중심 근사)
    top_lim, left_lim = 8, 8
    try:
        gb = detect.green_bbox(P['panel_png'])
        if gb:
            cx, cy = gb['cx'], gb['cy']
    except Exception:
        pass
    try:
        bb = detect.bubble_bottom(P['panel_png'])
        if bb:
            top_lim = max(top_lim, bb + 8)
    except Exception:
        pass
    try:
        ce = detect.character_right_edge(P['panel_png'])
        if ce:
            left_lim = max(left_lim, ce + 8)
    except Exception:
        pass
    left = min(max(round(cx - W / 2), left_lim), 1080 - W - 8)
    top = min(max(round(cy - H / 2), top_lim), 1080 - H - 8)

    # ── CSS ──
    css = (
        f"#card{{position:absolute;left:{left}px;top:{top}px;width:{W}px;height:{H}px;"
        "background:#fff;border:3px solid #111;border-radius:22px;"
        "box-shadow:0 8px 26px rgba(0,0,0,.14);opacity:0;transform-origin:center}"
        "#hd{position:absolute;left:24px;top:16px;font:800 24px 'Pretendard';color:#111}"
        ".row{position:absolute;left:24px;display:flex;align-items:center;gap:12px}"
        ".dot{width:22px;height:22px;border-radius:6px;flex:0 0 auto}"
        ".nm{font:800 30px 'Pretendard';color:#111}"
        ".pc{font:900 52px 'Pretendard';letter-spacing:-1px}"
        ".sub{position:absolute;left:60px;font:700 20px 'Pretendard';color:#71717a}"
    )

    # ── BODY ──
    parts = [f'<div id="card"><div id="hd">{hd_date} · 실제 수익</div>']
    for i, r in enumerate(rows):
        rt = ROW_TOP0 + i * ROW_GAP
        st = rt + SUB_DY
        col = r['color']
        parts.append(
            f'<div class="row" style="top:{rt}px">'
            f'<span class="dot" style="background:{col}"></span>'
            f'<span class="nm">{r["name"]}</span>'
            f'<span class="pc" id="pc{i}" style="color:{col}">+0%</span></div>'
            f'<div class="sub" style="top:{st}px">{start_man}만 → '
            f'<span id="v{i}">{start_man}</span>만</div>'
        )
    parts.append('</div>')
    body = ''.join(parts)

    # ── JS(결정적 renderAt) ──
    DATA = json.dumps([{'inv': r['inv'], 'final': r['final']} for r in rows])
    js = P['helpers'] + (
        "const __D=" + DATA + ";"
        "const __card=document.getElementById('card');"
        "function renderAt(t){"
        "  const app=c01(t/300);"
        "  __card.style.opacity=app;"
        "  __card.style.transform='scale('+(0.94+0.06*app)+')';"
        "  const e=eOut(c01((t-250)/1500));"
        "  for(let i=0;i<__D.length;i++){"
        "    const d=__D[i], cur=d.inv+(d.final-d.inv)*e;"
        "    const sg=cur>=d.inv?'+':'−';"
        "    document.getElementById('pc'+i).textContent=sg+Math.abs(Math.round(cur/d.inv*100-100))+'%';"
        "    document.getElementById('v'+i).textContent=Math.round(cur/10000);"
        "  }"
        "}"
        "window.__renderAt=renderAt; renderAt(0);"
    )

    return html_skeleton(P['bg'], css, body, js)