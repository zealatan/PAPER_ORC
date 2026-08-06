#!/usr/bin/env python3
"""stock_alert 프로젝트 전용 페이지 생성기 (gen_dec_edit.py 와 독립).

배투실 '주간 전고점 대비 낙폭 알림' 프로젝트의 대시보드 HTML을 생성한다.
- 출력: blog/architecture_docs/stock_alert/dec_pipeline.html  (이 파일 하나만 씀)
- 루트 인덱스(dec_pipeline.html)·gen_dec_edit.py 는 절대 건드리지 않는다.
- 유니버스 종목 수는 global_cup_suite 티커 CSV 에서 라이브로 읽는다(하드코딩 금지).
- 주간 스캔 결과가 있으면(data/weekN.json) 랭킹 표를 렌더, 없으면 '스캔 대기' 표시.

★ 편집 기능(내장): 우상단 '✏️ 편집' → 모든 텍스트 클릭 편집 + 박스 드래그 재배치.
  변경은 localStorage(KEY=stockalert_edit_v1) 저장 → 재빌드/새로고침해도 유지.
  3계층: gen_page.py(소스) · HTML(빌드 스냅샷) · localStorage(브라우저 편집본).
  구조를 바꾼 뒤 편집본이 이상하면 '🔄 초기화'로 localStorage 비우면 됨.

사용: python3 blog/stock_alert/gen_page.py
"""
from __future__ import annotations

import csv
import json
from html import escape as esc
from pathlib import Path

# ── 경로 ────────────────────────────────────────────────────────────────────────
SELF = Path(__file__).resolve()
PROJ = SELF.parent                                  # blog/stock_alert
BLOG = PROJ.parent                                  # blog
ROOT = BLOG.parent                                  # PAPER_ORC
DATA_DIR = PROJ / "data"                            # 주간 스캔 결과 JSON
TICKERS = ROOT / "global_cup_suite" / "data"        # 재사용 유니버스
OUT = BLOG / "architecture_docs" / "stock_alert" / "dec_pipeline.html"

ETF_CATS = ("ETF", "Covered Call ETF")


# ── 유니버스 집계 (라이브) ────────────────────────────────────────────────────────
def _rows(name: str) -> list[dict]:
    p = TICKERS / f"tickers_{name}.csv"
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def universe_counts() -> dict:
    stock, etf_total = {}, 0
    for key in ("us", "korea", "japan", "eu", "global"):
        r = _rows(key)
        stock[key] = sum(1 for x in r if x["category"].strip() == "Stock")
        etf_total += sum(1 for x in r if x["category"].strip() in ETF_CATS)
    return {"us": stock["us"], "korea": stock["korea"], "etf": etf_total}


def load_weeks() -> list[dict]:
    if not DATA_DIR.exists():
        return []
    weeks = []
    for p in sorted(DATA_DIR.glob("week*.json")):
        try:
            weeks.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            pass
    return weeks


# ── HTML 조각 ───────────────────────────────────────────────────────────────────
NAV = (
    '<nav style="font-family:ui-monospace,Consolas,monospace;font-size:12.5px;'
    'padding:9px 16px;background:#17282a;color:#cfd3d1;display:flex;gap:15px;'
    'flex-wrap:wrap;align-items:center;position:sticky;top:0;z-index:50;'
    'border-bottom:1px solid #2c4144">'
    '<span style="color:#c98a1a;font-weight:700;letter-spacing:.04em">배투실 문서</span>'
    '<a href="../dec_pipeline.html" style="color:#cfd3d1;text-decoration:none">◆ 종목 선택</a>'
    '<a href="../top_pipeline_standalone.html" style="color:#cfd3d1;text-decoration:none">파이프라인 허브</a>'
    '<a href="../production_manual.html" style="color:#cfd3d1;text-decoration:none">제작 매뉴얼</a>'
    '<a href="../research.html" style="color:#cfd3d1;text-decoration:none">리서치</a>'
    '<span style="color:#e8a33d;font-weight:700">STOCK_ALERT</span></nav>'
)

CSS = (
    'body{margin:0;font-family:"Pretendard","Apple SD Gothic Neo",sans-serif;'
    'background:#f2ede2;color:#17282a;padding:0 20px}'
    '.wrap{max-width:820px;margin:0 auto;padding:44px 0 80px}'
    'section.box{margin:0 0 8px;border-radius:12px;padding:8px 10px}'
    '.eyebrow{font-family:ui-monospace,monospace;font-size:12px;color:#c98a1a;'
    'font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px}'
    'h1{font-size:31px;font-weight:800;margin:0 0 8px;letter-spacing:-.02em}'
    '.lede{color:#5c6d6b;margin:0 0 12px;font-size:15px;line-height:1.6}'
    'h2{font-size:15px;font-weight:800;margin:22px 0 12px;letter-spacing:-.01em;'
    'border-left:3px solid #c98a1a;padding-left:9px}'
    '.uni{display:flex;gap:10px;flex-wrap:wrap}'
    '.uni .c{flex:1;min-width:130px;background:#fbf8f1;border:1px solid #ddd4c3;'
    'border-radius:12px;padding:15px 17px}'
    '.uni .c .n{font-size:27px;font-weight:800;font-family:ui-monospace,monospace;color:#17282a}'
    '.uni .c .k{font-size:12.5px;color:#5c6d6b;margin-top:2px}'
    '.pipe{display:flex;gap:7px;flex-wrap:wrap;align-items:center;font-size:13px;color:#3d4f4d}'
    '.pipe .s{background:#fbf8f1;border:1px solid #ddd4c3;border-radius:8px;padding:7px 11px;position:relative}'
    '.pipe .s:not(:last-child){margin-right:16px}'
    '.pipe .s:not(:last-child)::after{content:"→";position:absolute;right:-14px;top:50%;'
    'transform:translateY(-50%);color:#c98a1a;font-weight:800}'
    '.plan{list-style:none;padding:6px 20px;margin:0;background:#fbf8f1;'
    'border:1px solid #ddd4c3;border-radius:12px}'
    '.plan li{margin:9px 0;font-size:14px;line-height:1.55}.plan b{color:#17282a}'
    'table{width:100%;border-collapse:collapse;font-size:13.5px;margin-top:4px}'
    'th,td{text-align:left;padding:8px 10px;border-bottom:1px solid #e4dcc9}'
    'th{color:#5c6d6b;font-weight:700;font-size:12px}'
    'td.dd{font-family:ui-monospace,monospace;font-weight:800;color:#c0392b;text-align:right}'
    '.week{background:#fbf8f1;border:1px solid #ddd4c3;border-radius:12px;padding:16px 20px;margin-bottom:14px}'
    '.badge{display:inline-block;font-family:ui-monospace,monospace;font-size:11px;'
    'font-weight:700;padding:2px 8px;border-radius:6px;background:#17282a;color:#f2ede2}'
    '.empty{color:#8a9694;font-size:13.5px;padding:14px 0}'
    '.foot{margin-top:40px;font-size:12px;color:#8a9694;line-height:1.6}'
    '.foot code{background:#f4eee1;padding:1px 6px;border-radius:5px}'
)

EDIT_CSS = (
    # 툴바
    '#ed{position:fixed;top:52px;right:18px;z-index:100;display:flex;gap:6px;align-items:center;'
    'font-family:ui-monospace,monospace;font-size:12.5px}'
    '#ed button{border:1px solid #c9bfa6;background:#fbf8f1;color:#17282a;border-radius:8px;'
    'padding:6px 10px;cursor:pointer;font-family:inherit;font-size:12.5px}'
    '#ed button:hover{border-color:#c98a1a}'
    '#ed button.on{background:#17282a;color:#f2ede2;border-color:#17282a}'
    '#ed .st{color:#8a9694;font-size:11.5px;min-width:52px}'
    # 편집 모드
    'body.editing [data-t]{outline:1px dashed #c9a24a;outline-offset:2px;border-radius:3px}'
    'body.editing [data-t]:focus{outline:2px solid #c98a1a;background:#fffef8}'
    'body.editing [data-box]{position:relative}'
    'body.editing .grip{display:inline-flex}'
    '.grip{display:none;position:absolute;top:4px;right:4px;width:22px;height:22px;'
    'align-items:center;justify-content:center;cursor:grab;color:#b0a488;'
    'background:#f4eee1;border:1px solid #ddd4c3;border-radius:6px;font-size:13px;z-index:5;user-select:none}'
    '.grip:active{cursor:grabbing}'
    'body.editing [data-box]:hover{box-shadow:0 0 0 1px #e0d3b0}'
    '.box-drag{opacity:.45}'
    '.zone-over{background:rgba(201,138,26,.06);border-radius:12px}'
    # 커스텀 텍스트 박스
    '.cust{background:#fff;border:1px dashed #c9a24a;padding:14px 16px;margin:8px 0}'
    '.ctext{min-height:1.4em;font-size:14px;line-height:1.6;color:#17282a;outline:none}'
    '.ctext:empty::before{content:"여기에 텍스트를 입력하세요…";color:#b7ab8e}'
    '.cdel{display:none;position:absolute;top:4px;right:30px;width:22px;height:22px;'
    'align-items:center;justify-content:center;cursor:pointer;color:#b0463a;background:#f7e9e6;'
    'border:1px solid #e2c3bd;border-radius:6px;font-size:12px;z-index:5}'
    'body.editing .cdel{display:inline-flex}'
)


def _market_table(name: str, rows: list[dict]) -> str:
    body = "".join(
        f'<tr><td>{i+1}</td><td>{esc(str(r.get("label", r.get("ticker", ""))))}</td>'
        f'<td class="dd">{r.get("drawdown_pct", 0):.1f}%</td></tr>'
        for i, r in enumerate(rows)
    )
    return (f'<h2 data-t>{esc(name)}</h2><table><tr><th>#</th><th>종목</th>'
            f'<th style="text-align:right">전고점 대비</th></tr>{body}</table>')


def _weeks_html(weeks: list[dict]) -> str:
    if not weeks:
        return ('<div class="empty" data-t>아직 스캔 결과가 없습니다. '
                '<code>data/week1.json</code> 이 생성되면 여기에 시장별 낙폭 랭킹이 표시됩니다.</div>')
    out = []
    for w in reversed(weeks):
        wk, dt = esc(str(w.get("week", "?"))), esc(str(w.get("date", "")))
        tables = "".join(_market_table(nm, rows) for nm, rows in w.get("markets", {}).items())
        out.append(f'<div class="week" data-box="wk-{wk}"><span class="grip">⠿</span>'
                   f'<span class="badge">week {wk}</span> '
                   f'<span style="color:#5c6d6b;font-size:12.5px"> · {dt}</span>{tables}</div>')
    return f'<div data-zone="weeks">{"".join(out)}</div>'


def _sec(box: str, inner: str) -> str:
    """드래그 가능한 섹션 박스."""
    return f'<section class="box" data-box="{box}"><span class="grip">⠿</span>{inner}</section>'


# ── 편집 스크립트 (localStorage 기반) ────────────────────────────────────────────
EDIT_JS = r"""<div id="ed">
  <span class="st" id="edst"></span>
  <button id="edadd" title="빈 텍스트 박스 추가">➕ 텍스트</button>
  <button id="edtog">✏️ 편집</button>
  <button id="edexp" title="편집본 JSON 내보내기">⤓ JSON</button>
  <button id="edrst" title="localStorage 비우고 원본으로">🔄 초기화</button>
</div>
<script>(function(){
  var KEY='stockalert_edit_v1';
  var body=document.body, editing=false, dragEl=null;
  var $=function(s){return document.querySelector(s);};
  function all(s){return Array.prototype.slice.call(document.querySelectorAll(s));}
  function texts(){return all('[data-t]');}
  function boxes(){return all('[data-box]');}
  function zones(){return all('[data-zone]');}
  function load(){try{return JSON.parse(localStorage.getItem(KEY))||{}}catch(e){return {}}}
  var stEl=$('#edst'),t0;
  function save(s){localStorage.setItem(KEY,JSON.stringify(s));stEl.textContent='저장됨';clearTimeout(t0);t0=setTimeout(function(){stEl.textContent='';},1200);}
  // 안정 키: 생성 텍스트([data-t])에만 문서순 인덱스 부여 (커스텀 .ctext 는 제외)
  function keyTexts(){texts().forEach(function(el,i){el.setAttribute('data-tk','t'+i);});}
  // ── 수집 ──
  function collectText(){var m={};texts().forEach(function(el){m[el.getAttribute('data-tk')]=el.innerHTML;});return m;}
  function collectOrder(){var o={};zones().forEach(function(z){
    o[z.getAttribute('data-zone')]=all2(z,':scope > [data-box]').map(function(el){return el.getAttribute('data-box');});});return o;}
  function collectCustom(){return all('[data-custom]').map(function(el){
    return {id:el.getAttribute('data-box'),zone:el.parentNode.getAttribute('data-zone'),text:el.querySelector('.ctext').innerHTML};});}
  function all2(root,s){return Array.prototype.slice.call(root.querySelectorAll(s));}
  function persist(){var s=load();s.text=collectText();s.order=collectOrder();s.custom=collectCustom();save(s);}
  // ── 드래그 ──
  function afterEl(z,y){var els=all2(z,':scope > [data-box]:not(.box-drag)'),best=null,bo=-Infinity;
    els.forEach(function(el){var b=el.getBoundingClientRect(),off=y-b.top-b.height/2;if(off<0&&off>bo){bo=off;best=el;}});return best;}
  function wireBox(box){
    var g=box.querySelector(':scope > .grip');
    if(g)g.addEventListener('mousedown',function(){box.setAttribute('draggable','true');});
    box.addEventListener('dragstart',function(e){dragEl=box;box.classList.add('box-drag');if(e.dataTransfer)e.dataTransfer.effectAllowed='move';});
    box.addEventListener('dragend',function(){box.classList.remove('box-drag');box.removeAttribute('draggable');
      all('.zone-over').forEach(function(z){z.classList.remove('zone-over');});if(dragEl){dragEl=null;persist();}});
  }
  function wireZone(z){
    z.addEventListener('dragover',function(e){if(!dragEl||dragEl.parentNode!==z)return;e.preventDefault();
      z.classList.add('zone-over');var a=afterEl(z,e.clientY);if(a==null)z.appendChild(dragEl);else z.insertBefore(dragEl,a);});
    z.addEventListener('dragleave',function(){z.classList.remove('zone-over');});
  }
  function wireText(el){el.addEventListener('blur',function(){if(editing)persist();});}
  // ── 커스텀 텍스트 박스 ──
  function makeCustom(id,text){
    var s=document.createElement('section');
    s.className='box cust';s.setAttribute('data-box',id);s.setAttribute('data-custom','');
    s.innerHTML='<span class="grip">⠿</span><button class="cdel" title="박스 삭제">✕</button><div class="ctext"></div>';
    s.querySelector('.ctext').innerHTML=text||'';
    wireBox(s);
    var ct=s.querySelector('.ctext');
    ct.contentEditable=editing?'true':'false';
    ct.addEventListener('blur',function(){if(editing)persist();});
    s.querySelector('.cdel').addEventListener('click',function(){if(confirm('이 텍스트 박스를 삭제할까요?')){s.remove();persist();}});
    return s;
  }
  function addCustom(){
    if(!editing)toggle(true);
    var z=$('[data-zone="root"]');
    var id='cust-'+Date.now()+'-'+Math.floor(Math.random()*1000);
    var s=makeCustom(id,'');z.appendChild(s);
    var ct=s.querySelector('.ctext');ct.contentEditable='true';ct.focus();persist();
  }
  // ── 저장본 적용 ──
  function apply(){
    var s=load();
    if(s.custom){s.custom.forEach(function(c){var z=$('[data-zone="'+c.zone+'"]')||$('[data-zone="root"]');
      if(z&&!$('[data-box="'+c.id+'"]'))z.appendChild(makeCustom(c.id,c.text));});}
    keyTexts();
    if(s.text){texts().forEach(function(el){var v=s.text[el.getAttribute('data-tk')];if(v!=null)el.innerHTML=v;});}
    if(s.order){zones().forEach(function(z){var zn=z.getAttribute('data-zone'),ord=s.order[zn];if(!ord)return;
      ord.forEach(function(bk){var el=z.querySelector(':scope > [data-box="'+bk+'"]');if(el)z.appendChild(el);});});}
  }
  // ── 편집 토글 ──
  function toggle(force){
    editing=(force!=null)?force:!editing;body.classList.toggle('editing',editing);
    var tg=$('#edtog');tg.classList.toggle('on',editing);tg.textContent=editing?'✓ 편집중':'✏️ 편집';
    texts().forEach(function(el){el.contentEditable=editing?'true':'false';});
    all('.ctext').forEach(function(el){el.contentEditable=editing?'true':'false';});
  }
  // ── init ──
  boxes().forEach(wireBox);
  zones().forEach(wireZone);
  texts().forEach(wireText);
  apply();
  $('#edtog').addEventListener('click',function(){toggle();});
  $('#edadd').addEventListener('click',addCustom);
  $('#edrst').addEventListener('click',function(){if(confirm('localStorage 편집본을 비우고 원본으로 되돌립니다.')){localStorage.removeItem(KEY);location.reload();}});
  $('#edexp').addEventListener('click',function(){var b=new Blob([JSON.stringify(load(),null,1)],{type:'application/json'}),
    a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='stock_alert_edits.json';a.click();URL.revokeObjectURL(a.href);});
})();</script>"""


# ── 빌드 ────────────────────────────────────────────────────────────────────────
def build() -> str:
    u = universe_counts()
    weeks = load_weeks()

    header = _sec("header",
        '<div class="eyebrow" data-t>배투실 · 영상 파이프라인 · 신규 프로젝트</div>'
        '<h1 data-t>STOCK_ALERT — 주간 전고점 대비 낙폭 알림</h1>'
        '<p class="lede" data-t>매주 미국주식·한국주식·ETF 통합 유니버스를 스캔해 '
        '전고점에서 가장 많이 무너진 종목을 랭킹으로 알려주는 정기 콘텐츠. 롱폼 + 쇼츠로 제작한다.</p>')

    universe = _sec("universe",
        '<h2 data-t>유니버스 (라이브)</h2><div class="uni" data-zone="uni">'
        f'<div class="c" data-box="uni-us"><span class="grip">⠿</span>'
        f'<div class="n" data-t>{u["us"]}</div><div class="k" data-t>🇺🇸 미국 주식</div></div>'
        f'<div class="c" data-box="uni-kr"><span class="grip">⠿</span>'
        f'<div class="n" data-t>{u["korea"]}</div><div class="k" data-t>🇰🇷 한국 주식</div></div>'
        f'<div class="c" data-box="uni-etf"><span class="grip">⠿</span>'
        f'<div class="n" data-t>{u["etf"]}</div><div class="k" data-t>📊 ETF (전체)</div></div></div>')

    steps = [
        "주간 스캔<br>scan_market ×3", "낙폭 랭킹<br>TOP N", "뉴스 큐레이션<br>왜 떨어졌나",
        "카운트다운 덱", "더빙·렌더", "롱폼 + 쇼츠",
    ]
    pipe_items = "".join(
        f'<span class="s" data-box="p{i}"><span class="grip">⠿</span><span data-t>{s}</span></span>'
        for i, s in enumerate(steps))
    pipeline = _sec("pipeline",
        '<h2 data-t>파이프라인</h2>'
        f'<div class="pipe" data-zone="pipe">{pipe_items}</div>')

    plan_items = [
        "<b>컨셉</b> — 매주 전고점 대비 낙폭이 큰 종목을 미국·한국·ETF 통합 유니버스에서 랭킹",
        "<b>포맷</b> — 롱폼 1편 + 쇼츠 2~3편 (3시장 통합 1영상)",
        "<b>앵글</b> — 낙폭 랭킹 중심(단순). 각 종목: 낙폭 −X% · 전고점→현재 차트 · 한 줄 이유",
        "<b>전고점 정의</b> — 마지막 ZigZag 전저점 이후 최고가(스윙고점, ATH 아님) · threshold 15%(trigger %와 별개)",
    ]
    plan_li = "".join(
        f'<li data-box="plan{i}"><span class="grip">⠿</span><span data-t>{s}</span></li>'
        for i, s in enumerate(plan_items))
    plan = _sec("plan",
        '<h2 data-t>확정 기획</h2>'
        f'<ul class="plan" data-zone="plan">{plan_li}</ul>')

    weeks_sec = _sec("weeks",
        f'<h2 data-t>주간 리포트</h2>{_weeks_html(weeks)}')

    return (
        '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>STOCK_ALERT — 주간 전고점 낙폭 알림 · 배투실</title>'
        f'<style>{CSS}{EDIT_CSS}</style></head><body>{NAV}{EDIT_JS_TOOLBAR}'
        f'<div class="wrap"><div data-zone="root">{header}{universe}{pipeline}{plan}{weeks_sec}</div>'
        '<div class="foot" data-t>이 페이지 = <code>blog/stock_alert/gen_page.py</code> 실행으로 생성 '
        '(gen_dec_edit.py 와 독립). 편집(✏️)은 localStorage 저장 · 재빌드해도 유지 · 이상하면 🔄 초기화.</div>'
        f'</div>{EDIT_JS_SCRIPT}</body></html>'
    )


# EDIT_JS 를 툴바(상단)와 스크립트(하단)로 분리 배치
_split = EDIT_JS.split("<script>", 1)
EDIT_JS_TOOLBAR = _split[0]
EDIT_JS_SCRIPT = "<script>" + _split[1]


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    html = build()
    OUT.write_text(html, encoding="utf-8")
    u = universe_counts()
    print(f"✓ {OUT.relative_to(BLOG)} ({len(html)//1024}KB · "
          f"유니버스 미국 {u['us']}·한국 {u['korea']}·ETF {u['etf']} · "
          f"주간 {len(load_weeks())}건 · 편집 내장)")


if __name__ == "__main__":
    main()
