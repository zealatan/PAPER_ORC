#!/usr/bin/env python3
"""top_pipeline_standalone.html의 .stage 박스들을 이동·추가·삭제·수정 가능하게 만드는 편집기 주입.
   기존 HTML은 그대로, </body> 앞에 <style>+<script> 삽입. 재실행해도 중복 안 되게 마커 체크."""
from pathlib import Path

import re
F = Path(__file__).resolve().parent.parent / "architecture_docs" / "top_pipeline_standalone.html"
MARK = "/*__STAGE_EDITOR__*/"
h = F.read_text(encoding="utf-8")
# 기존 주입 있으면 제거 후 재주입(재실행 가능)
h = re.sub(r"\n?<style>/\*__STAGE_EDITOR__\*/.*?</script>\n?", "", h, flags=re.S)

INJECT = """
<style>""" + MARK + """
.tp-tools{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:2px 0 16px}
.tp-tools button{font:inherit;font-size:12.5px;font-weight:700;color:var(--ink);background:var(--card,#fbf8f1);
  border:1px solid var(--line);border-radius:8px;padding:7px 12px;cursor:pointer;transition:.12s}
.tp-tools button:hover{filter:brightness(.96);transform:translateY(-1px)}
.tp-tools button.warn{color:var(--red,#c0442e)}
.tp-tools .sp{flex:1}
.tp-tools #tp-note{font-size:11px;color:var(--faint,#8a9694);font-family:var(--mono)}
.stages .stage .st-grip{position:absolute;right:96px;top:7px;cursor:grab;color:var(--faint);font-size:14px;
  letter-spacing:-3px;user-select:none;opacity:0;transition:opacity .12s;z-index:4}
.stages .stage:hover .st-grip{opacity:.7}
.stages .stage .st-grip:active{cursor:grabbing}
.stages .stage .st-link{position:absolute;right:62px;top:6px;border:0;background:transparent;font-size:13px;
  cursor:pointer;opacity:0;transition:opacity .12s;z-index:4;padding:0 3px}
.stages .stage:hover .st-link{opacity:.6}.stages .stage .st-link.on{opacity:1}
.stages .stage .st-ag{position:absolute;right:38px;top:6px;border:0;background:transparent;font-size:14px;
  cursor:pointer;opacity:0;transition:opacity .12s;z-index:4;padding:0 3px}
.stages .stage:hover .st-ag{opacity:.65}.stages .stage .st-ag.on{opacity:1;filter:none}
.stages .stage .st-del{position:absolute;right:8px;top:4px;border:0;background:var(--ground);color:var(--faint);
  font-size:17px;line-height:1;cursor:pointer;border-radius:6px;padding:1px 6px;opacity:0;transition:opacity .12s;z-index:4}
.stages .stage:hover .st-del{opacity:1}.stages .stage .st-del:hover{color:var(--red,#c0442e);background:color-mix(in srgb,var(--red,#c0442e) 12%,var(--ground))}
.stages .stage.dragging{opacity:.4}
.stages .stage [contenteditable]:focus{outline:2px solid color-mix(in srgb,var(--gold,#c98a1a) 55%,transparent);
  outline-offset:2px;border-radius:4px}
</style>
<script>
(function(){
  var box=document.querySelector('.stages'); if(!box) return;
  var LS='topPipeStages_v2';   // v2: 스테이지 링크(declink) 보존 반영 — 옛 캐시 무시하고 재파싱
  var esc=function(s){return String(s==null?'':s).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});};
  function parseDefault(){
    return [].map.call(box.querySelectorAll('.stage'), function(s){
      var b=s.querySelector('.badge'), bc='b-built';
      if(b){[].forEach.call(b.classList,function(c){ if(c.indexOf('b-')===0) bc=c; });}
      var g=function(sel){var e=s.querySelector(sel);return e?e.textContent.trim():'';};
      var nameEl=s.querySelector('.name'), la=nameEl?nameEl.querySelector('a[href]'):null;
      return {agentic:s.classList.contains('agentic'),
              name:(la?la.textContent.trim():g('.name')), link:(la?la.getAttribute('href'):null),
              tool:g('.tool'), reads:g('.rw .r'), writes:g('.rw .w'),
              badge:b?b.textContent.trim():'', badgeCls:bc};
    });
  }
  var DEFAULT=parseDefault(), model=null;
  try{ model=JSON.parse(localStorage.getItem(LS)); }catch(e){}
  if(!(model&&model.length)) model=JSON.parse(JSON.stringify(DEFAULT));
  var noteT;
  function flash(){var n=document.getElementById('tp-note'); if(!n)return; n.textContent='저장됨 ✓'; n.style.opacity=1;
    clearTimeout(noteT); noteT=setTimeout(function(){n.style.opacity=.45;},900);}
  function save(){ localStorage.setItem(LS, JSON.stringify(model)); flash(); }
  function render(){
    box.innerHTML='';
    model.forEach(function(st,i){
      var el=document.createElement('div');
      el.className='stage'+(st.agentic?' agentic':''); el.draggable=true; el.dataset.i=i;
      el.innerHTML=(st.agentic?'<span class="agent-tag">multi-agent</span>':'')
        +'<div class="no">'+(i+1)+'</div><div class="body">'
        +'<div class="name"><span class="st-name" contenteditable spellcheck="false">'+esc(st.name)+'</span>'
        +(st.link?' <a class="declink" href="'+esc(st.link)+'" target="_top" style="font-size:12px;font-weight:700;color:var(--amber,#c98a1a);text-decoration:none;white-space:nowrap">↗ 열기</a>':'')+'</div>'
        +'<div class="tool" contenteditable spellcheck="false">'+esc(st.tool)+'</div>'
        +'<div class="rw"><span class="r" contenteditable spellcheck="false">'+esc(st.reads)+'</span>'
        +'<span class="w" contenteditable spellcheck="false">'+esc(st.writes)+'</span></div>'
        +'</div><span class="badge '+esc(st.badgeCls)+'" contenteditable spellcheck="false">'+esc(st.badge)+'</span>'
        +'<span class="st-grip" title="드래그로 이동">⋮⋮</span>'
        +'<button class="st-ag'+(st.agentic?' on':'')+'" title="multi-agent 토글">🤖</button>'
        +'<button class="st-link'+(st.link?' on':'')+'" title="'+(st.link?('링크: '+esc(st.link)):'링크 설정')+'">🔗</button>'
        +'<button class="st-del" title="스테이지 삭제">×</button>';
      box.appendChild(el);
    });
  }
  // 툴바
  var tools=document.createElement('div'); tools.className='tp-tools';
  tools.innerHTML='<b style="font-size:12.5px;color:var(--gold,#c98a1a)">스테이지 편집</b>'
    +'<button id="tp-add">+ 스테이지</button>'
    +'<span class="sp"></span><span id="tp-note">자동 저장됨 ✓</span>'
    +'<button id="tp-exp">⤓ JSON</button><button id="tp-rst" class="warn">↺ 원본</button>';
  var pipe=box.closest('.pipe')||box;           // .pipe(grid) 바깥 위에 삽입 — grid 안 깨짐
  pipe.parentNode.insertBefore(tools, pipe);
  // 인라인 편집
  box.addEventListener('focusout', function(e){
    var el=e.target.closest && e.target.closest('.stage'); if(!el)return; var st=model[+el.dataset.i]; if(!st)return;
    var t=e.target, v=t.textContent.trim();
    if(t.classList.contains('st-name'))st.name=v; else if(t.classList.contains('tool'))st.tool=v;
    else if(t.classList.contains('r'))st.reads=v; else if(t.classList.contains('w'))st.writes=v;
    else if(t.classList.contains('badge'))st.badge=v; else return;
    save();
  });
  box.addEventListener('keydown', function(e){ if(e.key==='Enter'&&e.target.isContentEditable){e.preventDefault();e.target.blur();} });
  box.addEventListener('click', function(e){
    var el=e.target.closest && e.target.closest('.stage'); if(!el)return; var i=+el.dataset.i;
    if(e.target.classList.contains('st-del')){ if(confirm('이 스테이지를 삭제할까요?\\n"'+(model[i].name||'')+'"')){ model.splice(i,1); save(); render(); } }
    else if(e.target.classList.contains('st-ag')){ model[i].agentic=!model[i].agentic; save(); render(); }
    else if(e.target.classList.contains('st-link')){ var u=prompt('이 스테이지가 열 링크 URL (비우면 제거):', model[i].link||''); if(u!==null){ model[i].link=(u.trim()||null); save(); render(); } }
  });
  // 드래그 재배치
  box.addEventListener('dragstart', function(e){ var el=e.target.closest && e.target.closest('.stage'); if(el){el.classList.add('dragging'); e.dataTransfer.effectAllowed='move';} });
  box.addEventListener('dragend', function(){ var d=box.querySelector('.dragging'); if(d)d.classList.remove('dragging');
    model=[].map.call(box.children, function(el){return model[+el.dataset.i];}); save(); render(); });
  box.addEventListener('dragover', function(e){ e.preventDefault(); var d=box.querySelector('.dragging'); if(!d)return;
    var els=[].slice.call(box.querySelectorAll('.stage:not(.dragging)')), after=null, best=-Infinity;
    els.forEach(function(c){ var b=c.getBoundingClientRect(), off=e.clientY-b.top-b.height/2; if(off<0&&off>best){best=off;after=c;} });
    if(after==null)box.appendChild(d); else box.insertBefore(d,after); });
  // 툴바 동작
  document.getElementById('tp-add').onclick=function(){ model.push({agentic:false,name:'새 스테이지',tool:'도구·설명',reads:'reads',writes:'writes',badge:'신규',badgeCls:'b-new'}); save(); render();
    var last=box.lastElementChild; if(last){var n=last.querySelector('.name'); if(n)n.focus();} };
  document.getElementById('tp-rst').onclick=function(){ if(confirm('편집 내용을 버리고 원본 스테이지로 되돌릴까요?')){ model=JSON.parse(JSON.stringify(DEFAULT)); save(); render(); } };
  document.getElementById('tp-exp').onclick=function(){ var b=new Blob([JSON.stringify(model,null,2)],{type:'application/json'});
    var a=document.createElement('a'); a.href=URL.createObjectURL(b); a.download='top_pipeline_stages.json'; a.click(); URL.revokeObjectURL(a.href); };
  render();
})();
</script>
"""

h = h.replace("</body></html>", INJECT + "</body></html>", 1)
F.write_text(h, encoding="utf-8")
print(f"주입 완료 ({len(INJECT)} chars) → {F.name} ({len(h)} bytes)")
