"""③ 씬 공통 계약(contract) — 오버레이가 지켜야 할 스켈레톤/헬퍼.

오버레이 모듈 규약:
    overlays/<type>.py 는 `def build(P) -> str` 를 노출한다.
    P = {
      'bg'       : 배경 패널 data URI (panel_n.png, 1080에 object-fit:contain),
      'panel_png': 패널 파일경로 (detect 용),
      'series'   : {key: series}  # data.build_series 결과
      'meta'     : meta dict,
      'params'   : 이 컷의 params,
      'assets'   : {logo_key: data URI, ...},
      'helpers'  : HELPERS_JS (공통 JS, <script>에 그대로 인라인),
    }
    반환 HTML은 반드시:
      - #stage(1080x1080) + 배경 <img id="bg" src=P['bg']>
      - window.__renderAt(t_ms) 정의(결정적: t만으로 상태 산출, Math.random/Date.now 금지)
      - 끝에서 window.__ready = true
"""
import base64


def b64(path, mime=None):
    if mime is None:
        mime = 'image/png' if path.lower().endswith('.png') else 'application/octet-stream'
    return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()


# 공통 JS 헬퍼(이징·포맷). 모든 오버레이가 P['helpers']로 인라인해서 사용.
HELPERS_JS = r'''
const cl=(x,a,b)=>Math.max(a,Math.min(b,x)), c01=x=>cl(x,0,1), lerp=(a,b,t)=>a+(b-a)*t;
const eOut=p=>1-Math.pow(1-p,3);
const eIO=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const eBack=p=>1+2.70158*Math.pow(p-1,3)+1.70158*Math.pow(p-1,2);
const ss=u=>{u=c01(u);return u*u*(3-2*u);};
const won=v=>{const s=v<0?'−':'';return s+Math.abs(v).toLocaleString('en-US');};
const man=v=>{const s=v<0?'−':'+';return s+Math.abs(Math.round(v/1e4))+'만';};
const pct=(v,base)=>(v>=base?'+':'−')+Math.abs(Math.round(v/base*100-100))+'%';
'''


def html_skeleton(bg_uri, css, body, js):
    """표준 씬 HTML 조립. css/body/js는 오버레이가 채운다."""
    return (
        '<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">'
        '<title>scene</title><style>'
        "html,body{margin:0;background:#fff;overflow:hidden}"
        "#stage{position:relative;width:1080px;height:1080px;overflow:hidden;background:#fff;"
        "font-family:'Pretendard','Malgun Gothic',system-ui,sans-serif}"
        "#bg{position:absolute;inset:0;width:1080px;height:1080px;object-fit:contain;z-index:0}"
        + css +
        '</style></head><body><div id="stage">'
        f'<img id="bg" src="{bg_uri}">'
        + body +
        '</div><script>'
        + js +
        '\nwindow.__ready=true;'
        '</script></body></html>'
    )
