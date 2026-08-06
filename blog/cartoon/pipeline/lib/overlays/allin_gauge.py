"""allin_gauge — ALL IN 팻말 위 여백에 듀얼 게이지 HUD.

레퍼런스: cartoon/scene_page4.html 를 파이썬 문자열 생성기로 포팅.
어두운 라운드 카드 안에 두 종목 로고 + 각각의 트랙/필 게이지가 meta['add']원
(=추매액 each, 예 1,000만)까지 eOut 카운트업. 완료 시 카운트가 골드로,
로고 펄스 + 화이트 플래시로 강조. 마지막에 합계 배지(2*add)가 팝인.

배경 팻말(우측중앙 대략 x585-905, y646-864)은 가리지 않고 카드는 그 위(y<646)에
배치한다. red_bbox 로 팻말을 검출해 카드를 자동으로 팻말 바로 위에 앉히고,
bubble_bottom 으로 상단 말풍선을 피한다. 검출 실패 시 레퍼런스 좌표로 폴백.

하드코딩 데이터 대신:
    - 게이지 목표액 = meta['add'] (각 게이지 +add), 합계 = 2*add
    - 날짜칩       = meta['inj_date']
    - 로고         = P['assets'][key], 색상 = series[key]['color']

params:
    anchor    : 'above_sign'(기본) — 팻말 위 배치
    sum_badge : bool(기본 True)     — 합계 배지 표시 여부
    use       : [series_key, ...]    — 게이지에 쓸 종목(기본 series 전체 앞 2개)
"""
from lib.scene_common import html_skeleton, b64  # noqa: F401
from lib import detect, data  # noqa: F401


# 레퍼런스 좌표(1080 기준). dy 만큼 세로 이동해 팻말 위에 정렬.
_BASE = {
    'card': 452, 'lg1': 492, 'lg2': 560,
    't1': 522, 't2': 596, 'c1': 498, 'c2': 568,
    'st1': 508, 'st2': 582, 'sum': 428,
}
_CARD_H = 176
_SIGN_TOP = 646     # 팻말 상단(폴백)
_GAP = 18           # 카드 하단 ~ 팻말 상단 여백


def _dy(P):
    """red_bbox 로 ALL IN 팻말을 찾아 카드를 그 위에 정렬하기 위한 세로 오프셋."""
    png = P['panel_png']
    sign_top = _SIGN_TOP
    try:
        bb = detect.red_bbox(png)
        # 우측중앙 팻말 영역 안에 있을 때만 신뢰
        if bb and 460 < bb['cx'] < 1000 and 540 < bb['cy'] < 940:
            sign_top = bb['y0']
    except Exception:
        pass
    card_top = sign_top - _GAP - _CARD_H
    dy = card_top - _BASE['card']
    # 상단 말풍선 침범 방지
    top_lim = 120
    try:
        bubb = detect.bubble_bottom(png)
        if bubb:
            top_lim = max(top_lim, bubb + 12)
    except Exception:
        pass
    lo = top_lim - _BASE['card']
    hi = 160
    return int(max(lo, min(hi, dy)))


def build(P):
    series = P['series']
    meta = P['meta']
    params = P['params'] or {}
    assets = P.get('assets') or {}

    keys = (params.get('use') or list(series.keys()))[:2]
    add = int(meta.get('add') or 0)
    man_add = int(round(add / 10000))            # 만 단위 목표(예 1000)
    sum_man = 2 * man_add
    sum_badge = params.get('sum_badge', True)

    # 날짜칩: inj_date(추매일) → YYYY.MM.DD
    inj = meta.get('inj_date') or meta.get('asof') or ''
    date_dot = inj.replace('-', '.') if inj else ''

    # 종목별 색상/로고
    def col(i):
        k = keys[i] if i < len(keys) else None
        s = series.get(k) if k else None
        return (s or {}).get('color', '#3B5BDB' if i == 0 else '#E60012')

    def logo_uri(i):
        if i >= len(keys):
            return None
        k = keys[i]
        s = series.get(k) or {}
        return assets.get(k) or assets.get(s.get('code'))

    def logo_name(i):
        if i >= len(keys):
            return ''
        s = series.get(keys[i]) or {}
        return s.get('name', keys[i])

    dy = _dy(P)
    Y = {k: v + dy for k, v in _BASE.items()}

    col1, col2 = col(0), col(1)

    # ── CSS(레퍼런스 포팅; #stage/#bg 는 스켈레톤 제공) ──
    css = (
        "#hud{position:absolute;inset:0;z-index:3}"
        f"#card{{position:absolute;left:556px;top:{Y['card']}px;width:410px;height:176px;"
        "border-radius:20px;background:rgba(15,23,42,0.93);border:2px solid #D4A017;"
        "box-shadow:0 8px 26px rgba(0,0,0,.28);opacity:0}"
        ".lg{position:absolute;height:34px;width:auto;max-width:172px;object-fit:contain;"
        "object-position:left center;z-index:4;opacity:0}"
        ".lgt{position:absolute;height:34px;line-height:34px;font-weight:900;font-size:26px;"
        "white-space:nowrap;z-index:4;opacity:0}"
        f"#lg1{{left:576px;top:{Y['lg1']}px}}#lg2{{left:576px;top:{Y['lg2']}px}}"
        ".trk{position:absolute;height:20px;border-radius:10px;background:rgba(255,255,255,.14);"
        "left:576px;width:230px;opacity:0}"
        f"#t1{{top:{Y['t1']}px}}#t2{{top:{Y['t2']}px}}"
        ".fill{position:absolute;height:20px;border-radius:10px;left:576px;width:0;opacity:0}"
        f"#f1{{top:{Y['t1']}px;background:{col1}}}"
        f"#f2{{top:{Y['t2']}px;background:{col2}}}"
        ".cnt{position:absolute;left:788px;width:172px;text-align:right;color:#fff;"
        "font-weight:900;font-size:28px;opacity:0}"
        f"#c1{{top:{Y['c1']}px}}#c2{{top:{Y['c2']}px}}"
        "#sum{position:absolute;left:761px;top:%dpx;transform:translate(-50%%,-50%%) scale(0);"
        "background:#FFCF3D;color:#1a1a1a;font-weight:900;font-size:26px;padding:6px 16px;"
        "border-radius:999px;box-shadow:0 6px 16px rgba(0,0,0,.25);z-index:5}" % Y['sum'] +
        "#date{position:absolute;left:815px;top:32px;background:#1a1a1a;color:#fff;"
        "border:2px solid #FFCF3D;border-radius:12px;padding:10px 16px;font-weight:800;"
        "font-size:26px;opacity:0;z-index:5}"
        "#flash{position:absolute;inset:0;background:#fff;opacity:0;z-index:8;pointer-events:none}"
    )

    # ── BODY ──
    def logo_el(i, lid, color):
        uri = logo_uri(i)
        if i >= len(keys):
            return ''
        if uri:
            return f'<img class="lg" id="{lid}" src="{uri}">'
        return (f'<div class="lgt" id="{lid}" style="left:576px;'
                f'top:{Y[lid]}px;color:{color}">{logo_name(i)}</div>')

    body_parts = []
    if date_dot:
        body_parts.append(f'<div id="date">{date_dot} · 증액</div>')
    body_parts.append('<div id="hud"><div id="card"></div>')
    body_parts.append(logo_el(0, 'lg1', col1))
    if len(keys) > 1:
        body_parts.append(logo_el(1, 'lg2', col2))
    body_parts.append('<div class="trk" id="t1"></div><div class="fill" id="f1"></div>')
    body_parts.append('<div class="cnt" id="c1">+0만</div>')
    if len(keys) > 1:
        body_parts.append('<div class="trk" id="t2"></div><div class="fill" id="f2"></div>')
        body_parts.append('<div class="cnt" id="c2">+0만</div>')
    body_parts.append('</div>')
    if sum_badge:
        body_parts.append(f'<div id="sum">합계 +{sum_man:,}만원</div>')
    body_parts.append('<div id="flash"></div>')
    body = ''.join(body_parts)

    # ── JS(결정적 renderAt; helpers 의 cl/c01/eOut/eBack 재사용) ──
    dual = 'true' if len(keys) > 1 else 'false'
    sumjs = ('true' if sum_badge else 'false')
    js = P['helpers'] + (
        "const E=id=>document.getElementById(id);"
        "const MAN=" + str(man_add) + ", DUAL=" + dual + ", SUM=" + sumjs + ";"
        "function gauge(fill,cnt,t,t0){"
        "  if(!fill||!cnt) return 0;"
        "  const p=eOut(c01((t-t0)/1600));"
        "  fill.style.width=(230*p)+'px';"
        "  const v=Math.round(MAN*p);"
        "  cnt.textContent='+'+v.toLocaleString('en-US')+'만';"
        "  cnt.style.color=p>=1?'#FFCF3D':'#fff';"
        "  return p;"
        "}"
        "function renderAt(t){"
        "  const bg=E('bg'); if(bg) bg.style.opacity=c01(t/300);"
        "  {const d=E('date'); if(d){const p=c01(t/450),e=eBack(p);"
        "     d.style.opacity=p; d.style.transform='translateY('+(-40*(1-e))+'px)';}}"
        "  {const p=c01((t-300)/400),e=eOut(p),card=E('card');"
        "   if(card){card.style.transform='translateY('+(-30*(1-e))+'px)';card.style.opacity=p;}"
        "   const ap=c01((t-400)/300);"
        "   ['lg1','lg2','t1','t2','f1','f2','c1','c2'].forEach(id=>{const el=E(id);if(el)el.style.opacity=ap;});}"
        "  const p1=gauge(E('f1'),E('c1'),t,900);"
        "  const p2=DUAL?gauge(E('f2'),E('c2'),t,1300):1;"
        "  {const l1=E('lg1');if(l1)l1.style.transform=p1>=1?"
        "     ('scale('+(1+0.08*Math.max(0,Math.sin((t-2500)/120))*Math.exp(-(t-2500)/300))+')'):'';}"
        "  {const l2=E('lg2');if(l2)l2.style.transform=p2>=1?"
        "     ('scale('+(1+0.08*Math.max(0,Math.sin((t-2900)/120))*Math.exp(-(t-2900)/300))+')'):'';}"
        "  {let a=0;const tbs=DUAL?[2500,2900]:[2500];"
        "   for(const tb of tbs){const d=t-tb;if(d>=0&&d<=130)a=Math.max(a,Math.sin(d/130*Math.PI)*0.3);}"
        "   const fl=E('flash');if(fl)fl.style.opacity=a;}"
        "  {const s=E('sum');if(s&&SUM){const p=c01((t-3000)/320),e=eBack(p);"
        "     s.style.transform='translate(-50%,-50%) scale('+e+')';}}"
        "}"
        "window.__renderAt=renderAt; renderAt(0);"
    )

    return html_skeleton(P['bg'], css, body, js)