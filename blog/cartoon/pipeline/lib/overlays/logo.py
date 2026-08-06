"""logo — 두 종목 로고를 얼굴 오른쪽에 세로 배치(팝인 + 은은한 플로팅).

레퍼런스: cartoon/scene_page1.html 의 흰 라운드카드(chip) + 종목색 테두리 +
eBack 팝인 + sin 상하 바빙을 파이썬 문자열 생성기로 포팅.
하드코딩 좌표 대신 detect.character_right_edge / bubble_bottom 로 캐릭터·말풍선을
피해 배치한다. 데이터(P['series'])는 쓰지 않는 순수 브랜딩 오버레이.

params:
  use    : 로고 key 리스트(기본 ['SEC','HYNIX'])
  layout : 'vertical'(기본)
  anchor : 'right_of_face'(기본)
"""
from lib.scene_common import html_skeleton, b64  # noqa: F401
from lib import detect, data  # noqa: F401

# 종목색 테두리(카드 외곽). 미지정 key는 회색.
BORDER = {
    'SEC':   '#1428A0',
    'HYNIX': '#E60012',
    'SKH':   '#E60012',
}
_DEF_BORDER = '#888'

# 카드 규격(레퍼런스와 동일 비율)
CARD_W, CARD_H = 270, 170
BORDER_W = 5


def _layout(P, keys):
    """detect 로 캐릭터·말풍선을 피해 각 카드 중심 (cx,cy) 리스트를 계산."""
    png = P['panel_png']
    try:
        char_r = detect.character_right_edge(png)
    except Exception:
        char_r = 0
    try:
        bub_b = detect.bubble_bottom(png)
    except Exception:
        bub_b = 0
    # 검출 실패 시 안전 기본값
    if not char_r:
        char_r = round(0.62 * 1080)
    if not bub_b:
        bub_b = round(0.30 * 1080)

    # 가로: 캐릭터 오른쪽 끝 ~ 스테이지 우측 사이 영역의 중앙에 카드 중심.
    left_margin, right_margin = 40, 30
    region_l = char_r + left_margin + CARD_W / 2
    region_r = 1080 - right_margin - CARD_W / 2
    cx = region_r if region_l > region_r else round((region_l + region_r) / 2)
    cx = max(round(CARD_W / 2 + 8), min(round(1080 - CARD_W / 2 - 8), round(cx)))

    # 세로: 말풍선 아래에서 시작해 카드들을 아래로 스택.
    n = len(keys)
    top_margin, bot_margin, gap = 40, 30, 26
    top = bub_b + top_margin
    span = n * CARD_H + (n - 1) * gap
    # 아래로 넘치면 위로 끌어올림(단, 상단 안전선 아래 유지)
    if top + span > 1080 - bot_margin:
        top = max(bub_b + 12, 1080 - bot_margin - span)
    cy0 = top + CARD_H / 2
    step = CARD_H + gap
    return [(cx, round(cy0 + i * step)) for i in range(n)]


def build(P):
    params = P.get('params') or {}
    want = params.get('use') or ['SEC', 'HYNIX']
    # 실제 에셋이 있는 key만
    keys = [k for k in want if k in P['assets']]
    if not keys:
        js = P['helpers'] + "window.__renderAt=function(t){};"
        return html_skeleton(P['bg'], "", "", js)

    centers = _layout(P, keys)

    # CSS: chip 기본 + key별 테두리색
    css = (
        ".chip{position:absolute;left:0;top:0;background:#fff;border-radius:28px;"
        "box-shadow:0 10px 26px rgba(0,0,0,.16);display:flex;align-items:center;"
        "justify-content:center;z-index:5;opacity:0;will-change:transform,opacity}"
        ".chip img{width:82%;height:82%;object-fit:contain}"
    )
    for k in keys:
        col = BORDER.get(k, _DEF_BORDER)
        css += (f"#c_{k}{{width:{CARD_W}px;height:{CARD_H}px;"
                f"border:{BORDER_W}px solid {col}}}")

    # body: chip DOM
    body = ""
    for k in keys:
        body += (f'<div class="chip" id="c_{k}">'
                 f'<img src="{P["assets"][k]}"></div>')

    # JS: 레퍼런스 place() 포팅(팝인 eBack + sin 바빙), t(ms)만으로 결정적.
    IN_DUR = 460      # 스케일/등장 램프(ms)
    OP_DUR = 240      # 페이드인(ms)
    STAGGER = 220     # 카드 간 등장 지연
    START = 200       # 첫 카드 등장 오프셋
    HALF_W, HALF_H = CARD_W / 2, CARD_H / 2

    # [id, cx, cy, t0]
    cards = []
    for i, (k, (cx, cy)) in enumerate(zip(keys, centers)):
        cards.append(f"['c_{k}',{cx},{cy},{START + i * STAGGER}]")
    cards_js = "[" + ",".join(cards) + "]"

    js = P['helpers'] + (
        f"const CARDS={cards_js};"
        f"const HW={HALF_W},HH={HALF_H};"
        f"const IN={IN_DUR},OP={OP_DUR};"
        "function place(el,cx,cy,rel){"
        "  if(rel<0){el.style.opacity=0;return;}"
        "  const p=c01(rel/IN), e=eBack(p);"
        "  const bob=rel>IN?Math.sin((rel-IN)/900)*5:0;"
        "  el.style.opacity=c01(rel/OP);"
        "  el.style.transform="
        "'translate('+(cx-HW)+'px,'+(cy-HH+bob)+'px) scale('+(0.6+0.4*e)+')';"
        "}"
        "window.__renderAt=function(t){"
        "  for(const c of CARDS){"
        "    const el=document.getElementById(c[0]);"
        "    if(el) place(el,c[1],c[2],t-c[3]);"
        "  }"
        "};"
        "window.__renderAt(0);"
    )
    return html_skeleton(P['bg'], css, body, js)