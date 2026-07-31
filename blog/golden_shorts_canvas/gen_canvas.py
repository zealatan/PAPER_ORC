#!/usr/bin/env python3
"""gen_canvas.py — 무한 캔버스 팬·줌 릴 생성기.

큰 흰 종이(월드)에 블록(제목/그래프/콜아웃)을 좌표로 배치 → 카메라가 시퀀스대로 팬·줌하며
하나씩 보여준다. 줌인(도착) 시 그 그래프의 선이 그려지는(드로우) 애니 + 끝값 라벨 등장.
카드/패널 없이 종이 위에 바로 그린다.

출력: out/canvas.html  (build_canvas.py 가 playwright로 녹화 → out/canvas.mp4)

■ 저작(핵심):
  - BLOCKS: 화면 요소 리스트. 각 dict = {id, x, y, w, html}. (h는 내용에 따라 자동)
  - SEQ:    카메라 순서. [{t: 블록id 또는 "ALL", hold: 정지 ms}, ...]
  - linechart(w,h,series,cols,ends): 선차트 SVG 문자열(class ln/dot/lab → 드로우/페이드 대상).
  - 블록에 그래프를 넣으면 그 블록 도착 시 .ln 이 dashoffset 애니로 그려짐.

■ 좌표계: 월드는 좌상단 원점(px). 카메라는 대상 블록 bbox+여백을 세로 1080×1920에 맞춰 fit.
"""
import os, json, base64

HERE = os.path.dirname(os.path.abspath(__file__))
BLOG = os.path.abspath(os.path.join(HERE, ".."))

_pb = open(os.path.join(HERE, "assets", "paper_b64.txt")).read().strip()
PAPER_URI = _pb if _pb.startswith("data:") else "data:image/jpeg;base64," + _pb
FONTSRC = "data:font/woff2;base64," + base64.b64encode(open(os.path.join(BLOG, "fonts", "PretendardVariable.woff2"), "rb").read()).decode()

SW, SH = 1080, 1920   # 세로 쇼츠 뷰포트


def linechart(w, h, series, cols, ends=None, ml=90, mr=160, mt=30, mb=60, dashed=None):
    """series=[[[x,y],...],...], cols=[색,...], ends=[끝라벨,...] → 종이 위 선차트 SVG.
    dashed=값 이면 그 y에 점선(원금선 등)."""
    xs = [p[0] for S in series for p in S]; ys = [p[1] for S in series for p in S]
    x0, x1, y1 = min(xs), max(xs), max(ys) * 1.08
    def X(x): return ml + (w - ml - mr) * (x - x0) / (x1 - x0)
    def Y(y): return mt + (h - mt - mb) * (1 - y / y1)
    s = '<line class="ax" x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="#c9c2b6" stroke-width="2"/>' % (ml, w - mr, Y(0), Y(0))
    if dashed is not None:
        s += '<line class="ax" x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="#b8b1a8" stroke-width="2.5" stroke-dasharray="8 6"/>' % (ml, w - mr, Y(dashed), Y(dashed))
    for i, S in enumerate(series):
        d = "M" + " L".join("%.1f,%.1f" % (X(p[0]), Y(p[1])) for p in S)
        s += '<path class="ln" d="%s" fill="none" stroke="%s" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>' % (d, cols[i])
        ex, ey = X(S[-1][0]), Y(S[-1][1])
        s += '<circle class="dot" cx="%.1f" cy="%.1f" r="9" fill="%s"/>' % (ex, ey, cols[i])
        if ends:
            s += '<text class="lab" x="%.1f" y="%.1f" font-size="38" font-weight="800" fill="%s">%s</text>' % (ex + 16, ey + 13, cols[i], ends[i])
    return '<svg viewBox="0 0 %d %d" style="display:block;width:100%%;height:auto" font-family="Pretendard,sans-serif">%s</svg>' % (w, h, s)


_HTML = """<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:'Pretendard';font-weight:100 900;src:url('{FONT}')}}
*{{margin:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;background:#000;overflow:hidden;font-family:'Pretendard',sans-serif}}
#world{{position:absolute;left:0;top:0;width:{WW}px;height:{WH}px;background:#f4f0e8 url('{PAPER}') center/cover;transform-origin:0 0}}
.block{{position:absolute;opacity:0;transition:opacity .55s ease}}
.block h2{{font-size:56px;font-weight:900;color:#1a1a1a;letter-spacing:-.02em}}
.block .s{{font-size:32px;color:#7a746a;font-weight:600;margin:6px 0 4px}}
.block h1{{font-size:140px;font-weight:900;color:#1a1a1a;letter-spacing:-.03em;line-height:1.04}}
.block h1 b,.hl{{color:#2b6cb0}}
.block p{{font-size:46px;color:#7a746a;font-weight:700;margin-top:26px}}
.big{{font-size:150px;font-weight:900;color:#2b6cb0;letter-spacing:-.02em}}
</style>
<div id="world">
{BLOCKS}
</div>
<script>
var SW={SW},SH={SH},WW={WW},WH={WH},SEQ={SEQ},MOVE={MOVE};
var world=document.getElementById('world');
document.querySelectorAll('.block').forEach(function(bl){{
 bl.querySelectorAll('.ln').forEach(function(p){{var L=p.getTotalLength();p.style.strokeDasharray=L;p.style.strokeDashoffset=L;p.style.transition='stroke-dashoffset 1.55s cubic-bezier(.4,0,.2,1)';}});
 bl.querySelectorAll('.dot,.lab').forEach(function(e){{e.style.opacity=0;e.style.transition='opacity .5s ease 1.05s';}});
}});
function reveal(id){{var bl=document.getElementById(id);if(!bl||bl.dataset.r)return;bl.dataset.r=1;bl.style.opacity=1;
 bl.querySelectorAll('.ln').forEach(function(p){{p.style.strokeDashoffset=0;}});
 bl.querySelectorAll('.dot,.lab').forEach(function(e){{e.style.opacity=1;}});}}
function lookAt(x,y,w,h,pad){{pad=pad||70;w+=pad*2;h+=pad*2;x-=pad;y-=pad;var s=Math.min(SW/w,SH/h);return {{s:s,tx:SW/2-s*(x+w/2),ty:SH/2-s*(y+h/2)}};}}
function target(k){{if(k==='ALL')return lookAt(0,0,WW,WH,140);var e=document.getElementById(k);return lookAt(e.offsetLeft,e.offsetTop,e.offsetWidth,e.offsetHeight,80);}}
function apply(v){{world.style.transform='translate('+v.tx+'px,'+v.ty+'px) scale('+v.s+')';}}
function ease(p){{return p<.5?2*p*p:1-Math.pow(-2*p+2,2)/2;}}
var i=0,t0=null,from=null,to=target(SEQ[0].t),phase='hold',holdEnd=0;
apply(to);reveal(SEQ[0].t);
function frame(ts){{if(t0===null){{t0=ts;holdEnd=ts+SEQ[0].hold;}}
 if(phase==='hold'){{if(ts>=holdEnd){{if(i>=SEQ.length-1){{window.__done=1;return;}}from=to;to=target(SEQ[i+1].t);phase='move';t0=ts;}}}}
 else{{var p=Math.min(1,(ts-t0)/MOVE),e=ease(p);apply({{s:from.s+(to.s-from.s)*e,tx:from.tx+(to.tx-from.tx)*e,ty:from.ty+(to.ty-from.ty)*e}});
   if(p>=1){{i++;phase='hold';holdEnd=ts+SEQ[i].hold;reveal(SEQ[i].t);}}}}
 requestAnimationFrame(frame);}}
requestAnimationFrame(frame);
</script>"""


def build(world_w, world_h, blocks_html, seq, move_ms=1450):
    """blocks_html=문자열(.block들), seq=[{t,hold}]. → 전체 HTML 문자열."""
    return _HTML.format(FONT=FONTSRC, PAPER=PAPER_URI, WW=world_w, WH=world_h,
                        BLOCKS=blocks_html, SW=SW, SH=SH, SEQ=json.dumps(seq), MOVE=move_ms)


def total_seconds(seq, move_ms=1450):
    return (sum(s["hold"] for s in seq) + move_ms * (len(seq) - 1)) / 1000.0


def block(bid, x, y, w, inner):
    return '<div class="block" id="%s" style="left:%dpx;top:%dpx;width:%dpx">%s</div>' % (bid, x, y, w, inner)


# ─────────────────────────────────────────────────────────────
# 예제 씬: QYLD 커버드콜 데모 (SHORTS_SCENE=qyld python3 gen_canvas.py)
# ─────────────────────────────────────────────────────────────
def scene_qyld():
    qq = json.load(open(os.path.join(HERE, "data", "qq_cmp.json")))
    fire = os.path.join(BLOG, "golden_shorts_fire", "assets", "spy_fires.json")
    spy = json.load(open(fire))[-1]["payload"]["lines"]
    COL = ["#2b6cb0", "#d98f2b", "#c2255c"]
    g1 = linechart(1560, 940, [qq["A"], qq["B"]], ["#d98f2b", "#2b6cb0"], ends=["$1.69M", "$2.66M"], dashed=qq["init"])
    g2 = linechart(1560, 940, [l["pts"] for l in spy], COL, ends=["$5.3M", "$3M", "$744K"])
    blocks = "\n".join([
        block("title", 300, 240, 1600, "<h1>은퇴 백테스트<br><b>커버드콜의 진실</b></h1><p>QYLD로 은퇴하면 벌어지는 일</p>"),
        block("c1", 260, 1180, 1560, '<h2>남는 배당, 어디에 재투자?</h2><div class="s">QYLD $100만 · 월$2천 · 11년</div>' + g1),
        block("c2", 2380, 560, 1560, '<h2>같은 기간 SPY라면</h2><div class="s">원금 $100만 · 2015 은퇴</div>' + g2),
        block("c3", 2620, 2050, 1200, '<div class="big">$2.66M</div><div class="s" style="font-size:44px;margin-top:10px">QYLD 배당 → QQQ 재투자<br>QYLD 재투자 대비 <b class="hl">+$97만</b></div>'),
    ])
    seq = [{"t": "title", "hold": 1600}, {"t": "c1", "hold": 2700}, {"t": "c2", "hold": 2700},
           {"t": "c3", "hold": 2100}, {"t": "ALL", "hold": 1700}]
    return 4400, 3000, blocks, seq


if __name__ == "__main__":
    scene = os.environ.get("SHORTS_SCENE", "qyld")
    ww, wh, blocks, seq = {"qyld": scene_qyld}[scene]()
    html = build(ww, wh, blocks, seq)
    out = os.path.join(HERE, "out", "canvas.html")
    open(out, "w", encoding="utf-8").write(html)
    print("wrote %s (scene=%s · world %dx%d · %.1fs)" % (out, scene, ww, wh, total_seconds(seq)))
