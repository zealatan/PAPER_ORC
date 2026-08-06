"""checklist — 교훈 컷. params['items'](문자열 리스트)를 체크(✓) 순차 팝인.

레퍼런스 없음(신규). 배경 만화는 그대로 두고, 오버레이는 캐릭터 반대편(우측 여백)에
반투명 라운드 카드로 얹는다. 각 항목은 시차(stagger) 팝인 + 체크 원 채움 + ✓ 스트로크
드로우. params['ending'] 있으면 하단 중앙 배지 자막으로 마지막에 등장.

렌더는 t(ms)만으로 결정적(Math.random/Date.now 금지). 끝나면 최종 프레임 hold(c01 포화).

params:
  items  : list[str]   체크 항목(필수). 비면 오버레이 없음.
  ending : str|None     하단 자막 배지(선택).
  title  : str|None     카드 상단 소제목(선택).
  accent : str          체크/배지 강조색(기본 '#16a34a').
"""
import html as _html

from lib.scene_common import html_skeleton, b64  # noqa: F401
from lib import detect, data  # noqa: F401


def _layout(P, n, has_title, has_ending):
    """detect 로 캐릭터·말풍선을 피해 카드 박스(left,top,W,rowH,cs,fs)를 계산."""
    png = P['panel_png']
    try:
        char_r = detect.character_right_edge(png)
    except Exception:
        char_r = 0
    try:
        bub_b = detect.bubble_bottom(png)
    except Exception:
        bub_b = 0
    if not char_r:
        char_r = round(0.50 * 1080)
    if not bub_b:
        bub_b = round(0.28 * 1080)

    # 가로: 캐릭터 오른쪽 끝 + 여백 ~ 우측 여백. 최소 폭 보장.
    right = 1044
    left = max(char_r + 44, 504)
    left = min(left, 700)
    W = right - left
    if W < 340:
        W = 360
        left = right - W

    # 세로: 말풍선 아래에서 시작. 카드 높이는 항목 수에 맞춰 rowH 축소.
    pad = 30
    top = max(bub_b + 52, 250)
    top = min(top, 430)
    bottom_limit = 928 if has_ending else 1004
    fs_guess = 40
    title_h = round(fs_guess * 1.35) + 14 if has_title else 0
    avail = bottom_limit - top - 2 * pad - title_h
    rowH = avail / max(n, 1)
    rowH = max(58.0, min(118.0, rowH))
    cs = round(max(34, min(60, rowH * 0.58)))          # 체크 아이콘 크기
    fs = round(max(24, min(46, rowH * 0.40)))          # 항목 글자 크기
    return {
        'left': round(left), 'top': round(top), 'W': round(W),
        'pad': pad, 'rowH': round(rowH), 'cs': cs, 'fs': fs,
        'title_h': title_h,
    }


def build(P):
    params = P.get('params') or {}
    items = [str(x) for x in (params.get('items') or []) if str(x).strip()]
    ending = params.get('ending')
    title = params.get('title')
    accent = params.get('accent') or '#16a34a'

    if not items:
        js = P['helpers'] + "window.__renderAt=function(t){};"
        return html_skeleton(P['bg'], "", "", js)

    n = len(items)
    L = _layout(P, n, bool(title), bool(ending))
    left, top, W = L['left'], L['top'], L['W']
    pad, rowH, cs, fs = L['pad'], L['rowH'], L['cs'], L['fs']
    ttl_fs = round(fs * 0.68)

    # ── CSS ─────────────────────────────────────────────────────────────
    css = (
        f"#ck{{position:absolute;left:{left}px;top:{top}px;width:{W}px;"
        f"box-sizing:border-box;padding:{pad}px {pad}px {pad - 4}px;"
        "background:rgba(255,255,255,.86);border-radius:30px;"
        "box-shadow:0 14px 34px rgba(0,0,0,.18);"
        "-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px);"
        "z-index:6;opacity:0;will-change:opacity}"
        f".ckrow{{display:flex;align-items:center;gap:16px;min-height:{rowH}px;"
        "opacity:0;will-change:transform,opacity}"
        ".ckrow svg{flex:0 0 auto;display:block}"
        f".cktx{{font-weight:800;color:#1f2937;line-height:1.14;"
        f"letter-spacing:-.5px;font-size:{fs}px}}"
    )
    if title:
        css += (
            f"#ckttl{{font-size:{ttl_fs}px;font-weight:900;color:{accent};"
            "letter-spacing:-.5px;margin-bottom:12px;opacity:.95}"
        )
    if ending:
        css += (
            "#ckend{position:absolute;left:50%;bottom:64px;transform:translateX(-50%);"
            f"background:{accent};color:#fff;font-weight:900;font-size:{round(fs * 0.92)}px;"
            "letter-spacing:-.5px;padding:20px 42px;border-radius:999px;"
            "box-shadow:0 12px 30px rgba(0,0,0,.28);white-space:nowrap;"
            "z-index:7;opacity:0;will-change:transform,opacity}"
        )

    # ── BODY(항목 DOM은 파이썬에서 확정 생성) ─────────────────────────────
    rows = ""
    for i, it in enumerate(items):
        rows += (
            f'<div class="ckrow" id="ck{i}">'
            f'<svg width="{cs}" height="{cs}" viewBox="0 0 40 40">'
            f'<circle id="ci{i}" cx="20" cy="20" r="18" fill="{accent}" '
            f'fill-opacity="0" stroke="{accent}" stroke-width="2.4"/>'
            f'<path id="cp{i}" d="M11.5 20.6 l5.6 5.6 l11.6 -13.8" fill="none" '
            f'stroke="#fff" stroke-width="4.4" stroke-linecap="round" '
            f'stroke-linejoin="round" pathLength="1" stroke-dasharray="1" '
            f'stroke-dashoffset="1"/>'
            f'</svg>'
            f'<span class="cktx" id="ctx{i}">{_html.escape(it)}</span>'
            f'</div>'
        )
    ttl_html = (f'<div id="ckttl">{_html.escape(str(title))}</div>' if title else '')
    body = f'<div id="ck">{ttl_html}{rows}</div>'
    if ending:
        body += f'<div id="ckend">{_html.escape(str(ending))}</div>'

    # ── JS(결정적 renderAt) ──────────────────────────────────────────────
    START = 260      # 첫 항목 등장 오프셋(ms)
    STAG = 520       # 항목 간 지연
    POP = 460        # 등장 램프
    CD = 360         # ✓ 드로우 시간
    js = P['helpers'] + (
        f"const N={n},START={START},STAG={STAG},POP={POP},CD={CD};"
        f"const HAS_END={'true' if ending else 'false'};"
        "const $=id=>document.getElementById(id);"
        "function ra(t){"
        "  $('ck').style.opacity=c01(t/300).toFixed(3);"
        "  for(let i=0;i<N;i++){"
        "    const ts=START+i*STAG, rel=t-ts;"
        "    const p=c01(rel/POP), e=eOut(p);"
        "    const sc=(0.86+0.14*eBack(p<1?p:1));"
        "    const row=$('ck'+i);"
        "    row.style.opacity=p.toFixed(3);"
        "    row.style.transform="
        "      'translateX('+((1-e)*46).toFixed(1)+'px) scale('+sc.toFixed(3)+')';"
        "    const fo=c01((rel-100)/220);"
        "    $('ci'+i).setAttribute('fill-opacity',fo.toFixed(3));"
        "    const cd=c01((rel-150)/CD);"
        "    $('cp'+i).setAttribute('stroke-dashoffset',(1-cd).toFixed(3));"
        "  }"
        "  if(HAS_END){"
        "    const te=START+N*STAG+300, pe=c01((t-te)/POP);"
        "    const end=$('ckend');"
        "    end.style.opacity=pe.toFixed(3);"
        "    const ye=(1-eOut(pe))*34, es=(0.8+0.2*eBack(pe<1?pe:1));"
        "    end.style.transform="
        "      'translateX(-50%) translateY('+ye.toFixed(1)+'px) scale('+es.toFixed(3)+')';"
        "  }"
        "}"
        "window.__renderAt=ra;"
        "ra(0);"
    )
    return html_skeleton(P['bg'], css, body, js)