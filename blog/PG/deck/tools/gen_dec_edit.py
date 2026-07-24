#!/usr/bin/env python3
"""dec_pipeline.html(PG 24씬 지도) + dec_edit_page{N}.html 24개(페이지별 편집 임베드) 생성.
   흐름: dec_pipeline.html →(페이지 클릭)→ dec_edit_page{N}.html →(iframe)→ pg_v1.html?page=N&edit=1
   출력 위치: blog/architecture_docs/ (dec_pipeline.html 옆). iframe은 ../PG/deck/pg_v1.html 상대참조."""
from pathlib import Path
import html as _h, json

# ── 종목 자동 인식 (이 파일 위치 = <blog>/<STOCK>/deck/tools/gen_dec_edit.py) ──
#    폴더 복사(pg→pg)만 하면 STOCK·경로가 자동으로 새 종목에 맞춰짐.
SELF = Path(__file__).resolve()
STOCK_DIR = SELF.parent.parent.parent            # <blog>/<STOCK>
STOCK = STOCK_DIR.name                            # PG / PG / ...
PFX = STOCK.lower()                               # 덱 파일 접두사: pg / pg
ROOT = STOCK_DIR.parent                           # <blog>
ARCH = ROOT / "architecture_docs" / STOCK         # 종목별 편집 UI 출력 폴더
ARCH.mkdir(parents=True, exist_ok=True)
DECK_REL = f"../../{STOCK}/deck/{PFX}_v1.html"    # architecture_docs/<STOCK>/ 기준 상대경로
DECK_JSON = STOCK_DIR / "deck" / f"{PFX}_deck.json"
PLAN_JSON = STOCK_DIR / "spec" / "deck_plan.json"

# 씬별 자막(subLines) — 편집화면 우측 패널에 표시. 페이지 N = 씬 index N-1.
_deck = json.load(open(DECK_JSON, encoding="utf-8")) if DECK_JSON.exists() else {"scenes": []}
_scs = _deck["scenes"] if isinstance(_deck, dict) else _deck
def sublines(i):
    if 0 <= i < len(_scs):
        s = _scs[i]
        sl = s.get("subLines") or s.get("data", {}).get("subLines")
        if isinstance(sl, list):
            return [x for x in sl if str(x).strip()]
    return []

# (tpl, 제목, chip_class, chip_text)  — 순서 = 페이지 1..24 (덱 씬 0..23)
SCENES = [
    ("notice",      "유의사항 · 경고 화면",              "ti", "경고"),
    ("stmt",        "투자자 A · 영수증 (매달 $3천 인출)", "ta", "인물 A"),
    ("stmt",        "투자자 B · 통장 (매달 $1천)",        "tb", "인물 B"),
    ("enginechart", "26년 후 결과 — 같은 40만, 다른 소비", "tg", "그래프"),
    ("hero",        "49년 배당귀족 (골든아치)",           "ti", "정보"),
    ("menuboard",   "햄버거보다 부동산 (임대료·로열티)",  "ti", "정보"),
    ("checks",      "최신 근황 (Q1 2026)",               "tn", "뉴스"),
    ("sectint",     "1부 전환 · 물가 반영 파산 시나리오",  "tt", "전환화면"),
    ("enginechart", "2000년 은퇴 · 20만불",              "tg", "그래프"),
    ("enginechart", "2000년 은퇴 · 40만불",              "tg", "그래프"),
    ("enginechart", "2000년 은퇴 · 60만불",              "tg", "그래프"),
    ("enginechart", "2002년 은퇴 · 20만불",              "tg", "그래프"),
    ("enginechart", "2002년 은퇴 · 40만불",              "tg", "그래프"),
    ("enginechart", "2002년 은퇴 · 60만불",              "tg", "그래프"),
    ("sectint",     "2부 전환 · 두 투자자 (매수법)",      "tt", "전환화면"),
    ("drivethru",   "타이밍 투자자 (폭락 노림)",          "ta", "인물 A"),
    ("stampcard",   "적립 투자자 (시간을 믿는다)",        "tb", "인물 B"),
    ("enginechart", "PG 주가 · −30% 폭락 신호",         "tg", "그래프"),
    ("enginechart", "폭락 때만 몰아 투자",               "tg", "그래프"),
    ("enginechart", "매달 $1,000 적립식",               "tg", "그래프"),
    ("hbars2",      "폭락 타이밍 vs 매달 적립",          "tg", "그래프"),
    ("divbars",     "49년 연속 배당 인상",              "tg", "그래프"),
    ("quotebig",    "피터 린치 명언",                   "tq", "명언"),
    ("card",        "마무리 · 다음 종목 예고",           "to", "마무리"),
]
# 막(act): (마크, 제목, 부제, 색변수, 시작페이지, 끝페이지)
ACTS = [
    ("①", "후킹",                    "같은 종목, 다른 운명 — 궁금증 유발",    "var(--amber)", 1, 4),
    ("②", "종목 소개",               "이 종목이 뭐고 지금 어떤가",            "var(--blue)", 5, 7),
    ("③", "1부 · 파산 시나리오 백테스트", "얼마 있으면 / 얼마 쓰면 버티나·파산하나", "var(--red)", 8, 14),
    ("④", "2부 · 매수 방법 백테스트",  "타이밍 vs 적립, 뭐가 이기나",           "var(--green)", 15, 21),
    ("⑤", "마무리",                  "정리·명언·CTA",                        "var(--muted)", 22, 24),
]

NAV = ('<nav data-tag="batusil-docnav" style="font-family:ui-monospace,Consolas,monospace;font-size:12.5px;'
       'padding:9px 16px;background:#17282a;color:#cfd3d1;display:flex;gap:15px;flex-wrap:wrap;align-items:center;'
       'position:sticky;top:0;z-index:9999;border-bottom:1px solid #2c4144">'
       '<span style="color:#c98a1a;font-weight:700;letter-spacing:.04em">배투실 문서</span>'
       '<a href="../top_pipeline_standalone.html" style="color:#cfd3d1;text-decoration:none">◆ 파이프라인 허브</a>'
       '<a href="../protocol.html" style="color:#cfd3d1;text-decoration:none">프로토콜</a>'
       '<a href="../production_manual.html" style="color:#cfd3d1;text-decoration:none">제작 매뉴얼</a>'
       f'<span style="color:#e8a33d;font-weight:700">덱 세부 · {STOCK}</span>'
       '<a href="../research.html" style="color:#cfd3d1;text-decoration:none">리서치</a>'
       '<a href="../handover.html" style="color:#cfd3d1;text-decoration:none">인수인계</a></nav>')

CSS = """:root{--ground:#f2ede2;--surface:#fbf8f1;--surface-2:#f4eee1;--line:#ddd4c3;--ink:#17282a;
--muted:#5c6d6b;--faint:#8a9694;--amber:#c98a1a;--blue:#2f6d8f;--red:#c0442e;--green:#3f7d4e;
--mono:ui-monospace,"SF Mono","Cascadia Mono",Consolas,monospace}
*{box-sizing:border-box}html{background:var(--ground)}
body{margin:0;color:var(--ink);font-family:"Pretendard","Apple SD Gothic Neo","Malgun Gothic",sans-serif;line-height:1.5;padding:0 20px 72px}
.wrap{max-width:900px;margin:0 auto}
.mast{padding:52px 0 8px}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.14em;color:var(--amber);text-transform:uppercase}
.eyebrow b{color:var(--ink)}
h1{font-size:clamp(26px,4vw,36px);font-weight:800;letter-spacing:-.02em;margin:10px 0 8px}
.sub{color:var(--muted);font-size:15px;margin:0;max-width:660px}
.sub code{font-family:var(--mono);font-size:13px;background:var(--surface-2);padding:1px 6px;border-radius:5px;color:var(--ink)}
.hint{margin:14px 0 0;font-size:13px;color:var(--green);background:color-mix(in srgb,var(--green) 9%,transparent);
border:1px solid color-mix(in srgb,var(--green) 26%,transparent);border-radius:9px;padding:9px 13px;max-width:660px}
.stats{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0 6px}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 16px;min-width:96px}
.stat b{display:block;font-family:var(--mono);font-size:24px;font-weight:800;line-height:1}
.stat span{font-size:12px;color:var(--muted)}
.legend{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 4px;font-size:12px;color:var(--muted)}
.act{margin:30px 0 0;border-left:3px solid var(--ac);padding-left:20px;position:relative}
.acth{display:flex;align-items:center;gap:14px;margin:0 0 14px}
.acmark{font-family:var(--mono);font-size:22px;font-weight:800;color:var(--ac);line-height:1;min-width:26px}
.acmeta{flex:1}.acmeta h2{font-size:18px;font-weight:800;margin:0;letter-spacing:-.01em}
.acmeta p{font-size:13px;color:var(--muted);margin:2px 0 0}
.acrng{font-family:var(--mono);font-size:12px;color:var(--faint);white-space:nowrap;
background:var(--surface-2);border:1px solid var(--line);border-radius:999px;padding:4px 10px}
.pgs{display:flex;flex-direction:column;gap:8px}
a.pg{display:flex;align-items:center;gap:12px;background:var(--surface);border:1px solid var(--line);
border-radius:11px;padding:11px 14px;transition:transform .12s,box-shadow .12s;text-decoration:none;color:inherit}
a.pg:hover{transform:translateX(3px);box-shadow:0 3px 12px rgba(23,40,42,.1);border-color:color-mix(in srgb,var(--ac) 45%,var(--line))}
.pn{font-family:var(--mono);font-size:14px;font-weight:800;color:var(--ac);min-width:26px;text-align:center;
background:color-mix(in srgb,var(--ac) 12%,transparent);border-radius:7px;padding:3px 0}
.pt{flex:1;font-size:15px;font-weight:600}
.edit{font-family:var(--mono);font-size:11px;color:var(--faint);opacity:0;transition:opacity .12s}
a.pg:hover .edit{opacity:1}
.chip{font-family:var(--mono);font-size:11.5px;font-weight:700;padding:4px 10px;border-radius:999px;white-space:nowrap;border:1px solid transparent}
.tg{color:var(--amber);background:color-mix(in srgb,var(--amber) 13%,transparent);border-color:color-mix(in srgb,var(--amber) 30%,transparent)}
.tv{color:var(--blue);background:color-mix(in srgb,var(--blue) 13%,transparent);border-color:color-mix(in srgb,var(--blue) 30%,transparent)}
.ta{color:var(--red);background:color-mix(in srgb,var(--red) 12%,transparent);border-color:color-mix(in srgb,var(--red) 30%,transparent)}
.tb{color:var(--green);background:color-mix(in srgb,var(--green) 13%,transparent);border-color:color-mix(in srgb,var(--green) 30%,transparent)}
.ti{color:var(--muted);background:var(--surface-2);border-color:var(--line)}
.tn{color:#8a5a1a;background:#f2e6cf;border-color:#e2cfa6}
.tt{color:var(--muted);background:var(--surface-2);border:1px dashed var(--line)}
.tq,.to,.tr{color:var(--faint);background:var(--surface-2);border-color:var(--line)}
.foot{margin-top:40px;padding-top:16px;border-top:1px solid var(--line);color:var(--faint);font-size:12.5px;font-family:var(--mono)}
@media(max-width:560px){.pt{font-size:14px}.acrng,.edit{display:none}}"""

def esc(s): return _h.escape(str(s))

# ── dec_pipeline.html 생성 (인터랙티브: 이동·추가·삭제·수정) ──
# 초기 데이터(items): 막 헤더 + 페이지 카드 인터리브. ref = 덱 페이지(1-based).
default_items = []
for mark, atitle, asub, ac, p0, p1 in ACTS:
    default_items.append({"t": "act", "mark": mark, "title": atitle, "sub": asub, "color": ac})
    for n in range(p0, p1 + 1):
        tpl, title, cc, ct = SCENES[n - 1]
        default_items.append({"t": "pg", "title": title, "chip": cc, "ref": n})

# 현재 계획(items): deck_plan.json 있으면 그것(=덱에 반영된 최신 구성), 없으면 기본 24.
_planf = PLAN_JSON
items = default_items
if _planf.exists():
    try:
        _p = json.load(open(_planf, encoding="utf-8"))
        if isinstance(_p, list) and any(x.get("t") == "pg" for x in _p):
            items = _p
    except Exception:
        pass
pg_items = [it for it in items if it.get("t") == "pg"]
TOTAL = len(pg_items)

EDITOR_CSS = """
.tbar{position:sticky;top:41px;z-index:50;display:flex;gap:8px;flex-wrap:wrap;align-items:center;
margin:18px 0 10px;padding:10px 12px;background:var(--surface);border:1px solid var(--line);border-radius:12px}
.tbar button{font-family:inherit;font-size:13px;font-weight:700;color:var(--ink);background:var(--surface-2);
border:1px solid var(--line);border-radius:8px;padding:7px 12px;cursor:pointer;transition:.12s}
.tbar button:hover{background:#ece3d0;transform:translateY(-1px)}
.tbar .sp{flex:1}.tbar .muted{color:var(--muted);font-size:12px;font-family:var(--mono)}
.tbar button.warn{color:var(--red)}
.tbar button.apply{color:#fff;background:var(--green);border-color:var(--green);font-weight:800}
.tbar button.apply:hover{background:#356b43}
.tbar button.apply:disabled{opacity:.7}
#list{display:flex;flex-direction:column;gap:7px;margin-top:6px}
.row,.rowact{display:flex;align-items:center;gap:11px;border-radius:11px;padding:10px 13px;background:var(--surface);
border:1px solid var(--line);cursor:default}
.row.dragging,.rowact.dragging{opacity:.45;box-shadow:0 6px 20px rgba(23,40,42,.18)}
.rowact{--ac:var(--muted);background:transparent;border:0;border-left:3px solid var(--ac);border-radius:0;
padding:16px 13px 6px;margin-top:8px}
.grip{cursor:grab;color:var(--faint);font-size:15px;letter-spacing:-3px;user-select:none;flex:0 0 auto}
.grip:active{cursor:grabbing}
.amark{font-family:var(--mono);font-size:20px;font-weight:800;color:var(--ac)}
.ameta{flex:1}.atitle{font-size:18px;font-weight:800;outline:0}
.asub{font-size:13px;color:var(--muted);outline:0;margin-top:1px}
.pn{font-family:var(--mono);font-size:14px;font-weight:800;color:var(--ac,#c98a1a);min-width:28px;text-align:center;
background:color-mix(in srgb,var(--amber) 12%,transparent);border-radius:7px;padding:3px 0;flex:0 0 auto}
.pt{flex:1;font-size:15px;font-weight:600;outline:0;border-radius:5px;padding:2px 4px}
.pt:focus,.atitle:focus,.asub:focus{background:color-mix(in srgb,var(--amber) 10%,transparent);
box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--amber) 40%,transparent)}
.go{font-family:var(--mono);font-size:11.5px;font-weight:700;text-decoration:none;color:var(--blue);
border:1px solid color-mix(in srgb,var(--blue) 30%,transparent);border-radius:7px;padding:4px 9px;white-space:nowrap}
.go:hover{background:color-mix(in srgb,var(--blue) 12%,transparent)}
.go.off{color:var(--faint);border-color:var(--line);pointer-events:none}
select.chip{font-family:var(--mono);font-size:11.5px;font-weight:700;border-radius:999px;padding:4px 8px;cursor:pointer;
-webkit-appearance:none;appearance:none;text-align:center}
.del{border:0;background:transparent;color:var(--faint);font-size:19px;line-height:1;cursor:pointer;
padding:2px 6px;border-radius:6px;flex:0 0 auto}
.del:hover{color:var(--red);background:color-mix(in srgb,var(--red) 10%,transparent)}
.savenote{font-family:var(--mono);font-size:11.5px;color:var(--green)}
"""

hint = ('<div class="hint">💡 <b>페이지 카드를 드래그해 순서 변경</b> · 제목 클릭해 수정 · <b>×</b> 삭제 · '
        '상단 <b>+ 페이지 / + 막</b>으로 추가 · <b>✎ 덱 Np</b>를 누르면 실제 덱 편집화면. '
        '모든 변경은 자동 저장되며 <b>⤓ JSON</b>으로 내보낼 수 있습니다.</div>')
mast = (NAV + '<div class="wrap"><header class="mast">'
        '<div class="eyebrow">배투실 · 영상 파이프라인 · <b>3 덱 생성 (PG)</b></div>'
        '<h1>덱 페이지 편집 지도 — PG</h1>'
        '<p class="sub"><code>pg_final.html</code> 엔진 + <code>spec</code>·<code>story</code>로 채운 씬 구성. '
        '카드를 편집·재배치하며 덱 페이지를 계획/수정한다.</p>' + hint +
        '<div class="stats">'
        '<div class="stat"><b id="cnt">0</b><span>총 페이지</span></div>'
        '<div class="stat"><b id="cntc">0</b><span>차트/그래프</span></div>'
        '<div class="stat"><b id="cnta">0</b><span>막(act)</span></div></div>'
        '</header>'
        '<div class="tbar">'
        '<button id="addpg">+ 페이지</button><button id="addact">+ 막</button>'
        '<span class="sp"></span><span class="savenote" id="note">자동 저장됨 ✓</span>'
        '<button id="apply" class="apply">🚀 덱에 반영</button>'
        '<button id="exp">⤓ JSON</button><button id="imp">⤒ 불러오기</button>'
        '<button id="rst" class="warn">↺ 원본으로</button>'
        '<input type="file" id="impf" accept="application/json" hidden>'
        '</div>'
        '<div id="list"></div>'
        '<div class="foot">배투실 파이프라인 → 덱 페이지 편집 · '
        'dec_pipeline → dec_edit_page{N} → pg_v1.html?page=N&amp;edit=1 · 변경은 localStorage 저장</div></div>')

JS = r"""
<script>
const CHIPS={tg:'그래프',tv:'영상',tt:'전환화면',ta:'인물 A',tb:'인물 B',ti:'정보',tn:'뉴스',tq:'명언',to:'마무리'};
const COLORS=[['var(--amber)','앰버'],['var(--blue)','블루'],['var(--red)','레드'],['var(--green)','그린'],['var(--muted)','그레이']];
const DEFAULT=__DATA__;
const LS='decPipeline_%%PFX%%_v1';
const $=s=>document.querySelector(s);
const esc=s=>String(s==null?'':s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
let items;
try{items=JSON.parse(localStorage.getItem(LS))}catch(e){items=null}
if(!Array.isArray(items)||!items.length) items=JSON.parse(JSON.stringify(DEFAULT));
function save(){localStorage.setItem(LS,JSON.stringify(items));flash();}
let ft; function flash(){const n=$('#note');n.textContent='저장됨 ✓';n.style.opacity='1';clearTimeout(ft);ft=setTimeout(()=>n.style.opacity='.4',900);}
function render(){
  const box=$('#list'); box.innerHTML='';
  let pn=0,cc=0,ac=0;
  items.forEach((it,idx)=>{
    if(it.t==='act'){ ac++;
      const el=document.createElement('div'); el.className='rowact'; el.draggable=true; el.dataset.i=idx;
      el.style.setProperty('--ac',it.color||'var(--muted)');
      el.innerHTML=`<span class="grip" title="드래그">⋮⋮</span><span class="amark">${esc(it.mark||'◆')}</span>
        <div class="ameta"><div class="atitle" contenteditable spellcheck="false">${esc(it.title)}</div>
        <div class="asub" contenteditable spellcheck="false">${esc(it.sub||'')}</div></div>
        <button class="del" data-k="act" title="막 삭제">×</button>`;
      box.appendChild(el);
    } else { pn++; if(it.chip==='tg')cc++;
      const el=document.createElement('div'); el.className='row'; el.draggable=true; el.dataset.i=idx;
      const go=`<a class="go" href="dec_edit_page${pn}.html" title="덱 ${pn}p 편집(덱에 반영 후)">✎ 덱 ${String(pn).padStart(2,'0')}p</a>`;
      const opts=Object.keys(CHIPS).map(k=>`<option value="${k}"${k===it.chip?' selected':''}>${CHIPS[k]}</option>`).join('');
      el.innerHTML=`<span class="grip" title="드래그">⋮⋮</span><span class="pn">${String(pn).padStart(2,'0')}</span>
        <span class="pt" contenteditable spellcheck="false">${esc(it.title)}</span>${go}
        <select class="chip ${it.chip} csel" title="유형">${opts}</select>
        <button class="del" data-k="pg" title="페이지 삭제">×</button>`;
      box.appendChild(el);
    }
  });
  $('#cnt').textContent=pn; $('#cntc').textContent=cc; $('#cnta').textContent=ac;
}
// 인라인 편집 (위임)
const list=$('#list');
list.addEventListener('focusout',e=>{
  const row=e.target.closest('[data-i]'); if(!row)return; const it=items[+row.dataset.i]; if(!it)return;
  if(e.target.classList.contains('pt')||e.target.classList.contains('atitle')) it.title=e.target.textContent.trim();
  else if(e.target.classList.contains('asub')) it.sub=e.target.textContent.trim();
  save();
});
list.addEventListener('keydown',e=>{ if(e.key==='Enter'&&e.target.isContentEditable){e.preventDefault();e.target.blur();} });
list.addEventListener('change',e=>{
  if(e.target.classList.contains('csel')){ const row=e.target.closest('[data-i]'); items[+row.dataset.i].chip=e.target.value; save(); render(); }
});
list.addEventListener('click',e=>{
  if(e.target.classList.contains('del')){ const row=e.target.closest('[data-i]'); const it=items[+row.dataset.i];
    const nm=it.t==='act'?`막 "${it.title}"`:`페이지 "${it.title}"`;
    if(confirm(nm+' 삭제할까요?')){ items.splice(+row.dataset.i,1); save(); render(); } }
});
// 드래그 재배치
list.addEventListener('dragstart',e=>{ const r=e.target.closest('[data-i]'); if(r){r.classList.add('dragging'); e.dataTransfer.effectAllowed='move';} });
list.addEventListener('dragend',()=>{ const d=list.querySelector('.dragging'); if(d)d.classList.remove('dragging');
  items=[...list.children].map(el=>items[+el.dataset.i]); save(); render(); });
list.addEventListener('dragover',e=>{ e.preventDefault(); const d=list.querySelector('.dragging'); if(!d)return;
  const els=[...list.querySelectorAll('[data-i]:not(.dragging)')];
  let after=null,best=-Infinity;
  for(const c of els){ const b=c.getBoundingClientRect(); const off=e.clientY-b.top-b.height/2; if(off<0&&off>best){best=off;after=c;} }
  if(after==null)list.appendChild(d); else list.insertBefore(d,after);
});
// 툴바
$('#addpg').onclick=()=>{ items.push({t:'pg',title:'새 페이지',chip:'ti',ref:null}); save(); render();
  list.lastElementChild.querySelector('.pt').focus(); };
$('#addact').onclick=()=>{ items.push({t:'act',mark:'◆',title:'새 막',sub:'설명',color:'var(--muted)'}); save(); render(); };
$('#exp').onclick=()=>{ const b=new Blob([JSON.stringify(items,null,2)],{type:'application/json'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(b); a.download='dec_pipeline_plan.json'; a.click(); URL.revokeObjectURL(a.href); };
$('#imp').onclick=()=>$('#impf').click();
$('#impf').onchange=e=>{ const f=e.target.files[0]; if(!f)return; const r=new FileReader();
  r.onload=()=>{ try{ const j=JSON.parse(r.result); if(Array.isArray(j)){items=j;save();render();} else alert('배열 JSON이 아닙니다'); }catch(x){alert('JSON 파싱 실패: '+x.message);} };
  r.readAsText(f); e.target.value=''; };
$('#rst').onclick=()=>{ if(confirm('편집 내용을 버리고 현재 덱 구성으로 되돌릴까요?')){ items=JSON.parse(JSON.stringify(DEFAULT)); save(); render(); } };
$('#apply').onclick=()=>{
  if(!confirm('현재 구성을 실제 덱에 반영할까요?\n재정렬·추가·삭제가 pg_v1.html에 적용되고 편집 페이지가 재생성됩니다.')) return;
  const btn=$('#apply'); btn.disabled=true; btn.textContent='반영 중…(재굽기)';
  fetch('/api/save-pipeline',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({stock:'%%STOCK%%',items})})
   .then(r=>r.json()).then(r=>{
     if(r&&r.ok){ btn.textContent='✅ 반영 완료'; localStorage.removeItem(LS); setTimeout(()=>location.reload(),1000); }
     else { btn.textContent='⚠ 실패'; btn.disabled=false; alert('반영 실패:\n'+JSON.stringify(r,null,1)); }
   }).catch(e=>{ btn.textContent='⚠ 오류'; btn.disabled=false; alert('네트워크 오류: '+e.message+'\n(edit_server.py로 띄웠는지 확인)'); });
};
render();
</script>"""

pipe = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>덱 페이지 편집 지도 — PG · 배투실</title><style>' + CSS + EDITOR_CSS + '</style></head><body>'
        + mast + JS.replace('__DATA__', json.dumps(items, ensure_ascii=False))
                   .replace('%%STOCK%%', STOCK).replace('%%PFX%%', PFX) + '</body></html>')
(ARCH / "dec_pipeline.html").write_text(pipe, encoding="utf-8")
print(f"[{STOCK}] ✓ {ARCH}/dec_pipeline.html ({len(pipe)//1024}KB · 인터랙티브)")

# ── dec_edit_page{N}.html 24개 생성 ──
EDIT_CSS = ("*{box-sizing:border-box}html,body{margin:0;height:100%}"
            "body{display:flex;flex-direction:column;font-family:'Pretendard','Apple SD Gothic Neo',sans-serif;background:#17282a}"
            ".bar{display:flex;align-items:center;gap:12px;padding:9px 15px;background:#17282a;color:#cfd3d1;"
            "font-size:13px;border-bottom:1px solid #2c4144;flex:0 0 auto}"
            ".bar a{color:#cfd3d1;text-decoration:none;padding:5px 11px;border-radius:7px;border:1px solid #2c4144;white-space:nowrap}"
            ".bar a:hover{background:#22383b}.bar a.home{color:#e8a33d;border-color:#5a4420}"
            ".bar .ttl{flex:1;font-weight:700;color:#fbf8f1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}"
            ".bar .pn{font-family:ui-monospace,monospace;color:#e8a33d;font-weight:800}"
            ".bar .nav{display:flex;gap:7px}.bar a.off{opacity:.32;pointer-events:none}"
            ".bar button{font-family:inherit;font-size:13px;font-weight:700;color:#cfd3d1;background:#22383b;"
            "border:1px solid #2c4144;border-radius:7px;padding:5px 11px;cursor:pointer;white-space:nowrap}"
            ".bar button:hover{background:#2c4a4e}.bar button:disabled{opacity:.6;cursor:default}"
            ".bar button.save{color:#bfe3c4;border-color:#2f5a3a}.bar button.reload{color:#e8cfa0;border-color:#5a4420}"
            # 본문 = 위 iframe(영상) + 아래 자막패널 (세로 배치)
            ".work{flex:1 1 auto;display:flex;flex-direction:column;min-height:0}"
            "iframe{flex:1 1 auto;width:100%;border:0;background:#0d0d0d;min-height:0}"
            ".subs{flex:0 0 auto;max-height:32vh;background:#f4efe3;color:#1a2b2d;overflow-y:auto;padding:12px 22px;border-top:1px solid #2c4144;display:flex;flex-direction:column;gap:8px}"
            ".subs .hd{display:flex;align-items:center;gap:12px;flex-wrap:wrap}"
            ".subs .lns{display:flex;flex-direction:column;gap:6px}"
            ".subs .svbtn{font:inherit;font-size:12.5px;font-weight:700;color:#bfe3c4;background:#22383b;"
            "border:1px solid #2f5a3a;border-radius:7px;padding:5px 12px;cursor:pointer}"
            ".subs .svbtn:hover{background:#2c4a4e}.subs .svbtn:disabled{opacity:.6}"
            ".subs h3{margin:0 0 4px;font-family:ui-monospace,monospace;font-size:12px;letter-spacing:.12em;"
            "color:#8a5a1a;text-transform:uppercase}"
            ".subs .cap{margin:0 0 14px;font-size:12.5px;color:#5c6d6b}"
            ".subs .ln{font-size:16px;line-height:1.5;font-weight:600;color:#17282a;border-left:3px solid #c98a1a;"
            "padding:6px 10px 6px 12px;border-radius:0 6px 6px 0;background:#fbf6ea;outline:none;cursor:text}"
            ".subs .ln:focus{background:#fff;box-shadow:inset 0 0 0 2px #c98a1a}"
            ".subs .ln:empty:before{content:'(빈 줄)';color:#b7ae9c}"
            ".subs .none{color:#8a9694;font-size:15px;font-style:italic}"
            "@media(max-width:820px){.work{flex-direction:column}.subs{flex:0 0 auto;max-height:38vh;border-left:0;border-top:1px solid #2c4144}}")
for n in range(1, TOTAL + 1):
    it = pg_items[n - 1]
    title = it.get("title", "")
    tpl = _scs[n - 1]["tpl"] if n - 1 < len(_scs) else (it.get("chip") or "")
    sl = sublines(n - 1)
    _scene = (it.get("ref") or n) - 1          # narration_final 키 = 원본 씬 인덱스(sid-1=ref-1)
    subs = ("".join(f'<div class="ln" contenteditable="true">{esc(x)}</div>' for x in sl) if sl
            else '<div class="none">이 페이지는 내레이션(자막)이 없습니다.</div>')
    doc = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{n}p 편집 · {esc(title)}</title><style>' + EDIT_CSS + '</style></head><body>'
           '<div class="bar">'
           '<a class="home" href="dec_pipeline.html">← 파이프라인</a>'
           f'<span class="ttl"><span class="pn">{n:02d}p</span> · {esc(title)} '
           f'<span style="color:#7f8f8d;font-weight:400">[{esc(tpl)}]</span></span>'
           '<button class="save" id="bsave" title="이 편집을 소스에 저장하고 덱을 다시 굽는다">💾 저장(영구)</button>'
           '<button class="reload" id="breload" title="localStorage 비우고 최신 구운 버전 로드">🔄 최신본</button>'
           '<span class="nav">'
           f'<a class="{("off" if n==1 else "")}" href="dec_edit_page{n-1}.html">◀ 이전</a>'
           f'<a class="{("off" if n==TOTAL else "")}" href="dec_edit_page{n+1}.html">다음 ▶</a>'
           '</span></div>'
           '<div class="work">'
           f'<iframe src="{DECK_REL}?page={n}&edit=1&stock={STOCK}" title="deck page {n}"></iframe>'
           f'<aside class="subs"><div class="hd"><h3>자막 · {n:02d}p</h3>'
           f'<span class="cap">문장을 직접 고치고 →</span>'
           f'<button class="svbtn" id="subsave">💾 자막 저장</button></div>'
           f'<div class="lns">{subs}</div></aside>'
           '</div>'
           '<script>'
           'var fr=document.querySelector("iframe"),bs=document.getElementById("bsave"),br=document.getElementById("breload");'
           'bs.onclick=function(){var w=fr.contentWindow;'
           'if(!w||!w.__pipelineSave){alert("덱이 아직 로드되지 않았습니다. 잠시 후 다시.");return;}'
           'bs.disabled=true;bs.textContent="저장 중…";'
           'w.__pipelineSave().then(function(r){bs.textContent=(r&&r.ok)?"✅ 저장+재굽기 완료":"⚠ 실패(콘솔확인)";'
           'if(!(r&&r.ok))console.warn("save-deck",r);'
           'setTimeout(function(){bs.textContent="💾 저장(영구)";bs.disabled=false;},2400);})'
           '.catch(function(e){bs.textContent="⚠ 오류";bs.disabled=false;console.error(e);});};'
           'br.onclick=function(){var w=fr.contentWindow;if(w&&w.__pipelineReload)w.__pipelineReload();else fr.src=fr.src;};'
           'var sv=document.getElementById("subsave");'
           'if(sv)sv.onclick=function(){'
           'var L=[].map.call(document.querySelectorAll(".subs .ln"),function(d){return d.textContent.replace(/\\s+/g," ").trim();}).filter(Boolean);'
           'sv.disabled=true;sv.textContent="저장 중…(재굽기)";'
           'fetch("/api/save-subs",{method:"POST",headers:{"Content-Type":"application/json"},'
           f'body:JSON.stringify({{stock:"{STOCK}",scene:{_scene},lines:L}})}})'
           '.then(function(r){return r.json();}).then(function(r){'
           'sv.textContent=(r&&r.ok)?"✅ 저장+재굽기 완료":"⚠ 실패(콘솔)";if(!(r&&r.ok))console.warn("save-subs",r);'
           'if(r&&r.ok)setTimeout(function(){fr.src=fr.src;},700);'
           'setTimeout(function(){sv.textContent="💾 자막 저장";sv.disabled=false;},2600);})'
           '.catch(function(e){sv.textContent="⚠ 오류";sv.disabled=false;console.error(e);});};'
           '</script>'
           '</body></html>')
    (ARCH / f"dec_edit_page{n}.html").write_text(doc, encoding="utf-8")
# 페이지 수가 줄었으면 잉여 편집파일 제거
for _f in ARCH.glob("dec_edit_page*.html"):
    try:
        _num = int(_f.stem.replace("dec_edit_page", ""))
        if _num > TOTAL:
            _f.unlink()
    except ValueError:
        pass
print(f"[{STOCK}] ✓ dec_edit_page1..{TOTAL}.html ({TOTAL}개) → {ARCH}")

# ── 루트 종목 선택 인덱스(architecture_docs/dec_pipeline.html) — 공유문서 nav 링크 대상 ──
#    현재 존재하는 모든 <STOCK>/dec_pipeline.html을 스캔 → 자동 포함(PG 추가 시 다음 실행에 반영).
_stocks = sorted(p.parent.name for p in (ROOT / "architecture_docs").glob("*/dec_pipeline.html"))
_cards = "".join(
    f'<a class="sc" href="{esc(s)}/dec_pipeline.html"><b>{esc(s)}</b>'
    f'<span>덱 페이지 편집 →</span></a>' for s in _stocks)
_idx = ('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>덱 편집 — 종목 선택 · 배투실</title><style>'
        'body{margin:0;font-family:"Pretendard","Apple SD Gothic Neo",sans-serif;background:#f2ede2;color:#17282a;padding:0 20px}'
        '.wrap{max-width:720px;margin:0 auto;padding:52px 0 72px}'
        'h1{font-size:30px;font-weight:800;margin:0 0 6px;letter-spacing:-.02em}.sub{color:#5c6d6b;margin:0 0 24px}'
        '.grid{display:flex;flex-direction:column;gap:10px}'
        'a.sc{display:flex;align-items:baseline;gap:14px;background:#fbf8f1;border:1px solid #ddd4c3;border-radius:12px;'
        'padding:16px 18px;text-decoration:none;color:inherit;transition:.12s}'
        'a.sc:hover{transform:translateX(3px);box-shadow:0 3px 12px rgba(23,40,42,.1);border-color:#c98a1a}'
        'a.sc b{font-size:19px;font-family:ui-monospace,monospace;color:#c98a1a}a.sc span{color:#5c6d6b;font-size:13px}'
        '.foot{margin-top:26px;font-size:12.5px;color:#8a9694}.foot code{background:#f4eee1;padding:1px 6px;border-radius:5px}'
        '</style></head><body>' + NAV.replace('../', '') + '<div class="wrap">'
        '<h1>덱 편집 — 종목 선택</h1><p class="sub">편집할 종목을 고르세요. 종목별 편집 지도가 열립니다.</p>'
        f'<div class="grid">{_cards or "<p>생성된 종목 없음.</p>"}</div>'
        '<div class="foot">각 종목 UI = <code>&lt;STOCK&gt;/deck/tools/gen_dec_edit.py</code> 실행으로 생성 · '
        f'현재: {", ".join(_stocks) or "없음"}</div></div></body></html>')
(ROOT / "architecture_docs" / "dec_pipeline.html").write_text(_idx, encoding="utf-8")
print(f"✓ architecture_docs/dec_pipeline.html (종목 선택 인덱스: {', '.join(_stocks)})")
