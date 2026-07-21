# -*- coding: utf-8 -*-
"""cocacola 덱 → supetv-1 스타일 스토리보드 + 대본(확장) 생성 · dur 재계산 + 덱 갱신."""
import json, sys, html, base64, pathlib, math
THUMBS = pathlib.Path("thumbs_sm")
def thumb_uri(i):
    p = THUMBS/f"s{i+1:02d}.png"
    if p.exists(): return "data:image/jpeg;base64,"+base64.b64encode(p.read_bytes()).decode()
    return None

DECK = sys.argv[1] if len(sys.argv)>1 else "cocacola_sb36.json"   # 최신 36씬(2_3_real 반영 + 닷컴카드)
d = json.load(open(DECK, encoding="utf-8"))
S = d["scenes"]

RATE = 5.0        # 자/s (공백 제외) — 편안한 나레이션 속도
BUF  = 1.3        # 씬당 호흡 버퍼(s)

# (대본, 배경, 요소[], fx[], 자료) — 확장 · 친근한 설명형(훅은 드라마틱)
SB = [
 ("", "다크 그라디언트", ["유의사항 카드"], ["페이드인"], "대사 없음 — 인트로 고지"),
 ("2000년, 코카콜라 하나로 은퇴한 두 사람이 있었습니다. 먼저 A. 은퇴자금은 60만 달러로, 셋 중 가장 넉넉했죠. 돈이 넉넉하니 매달 3천 달러씩 여유 있게 썼습니다. 이 정도면 평생 걱정 없겠지 했는데 — 2015년, 그의 계좌 잔고는 0. 파산하고 맙니다.", "트레이더 배경", ["A 인물카드","현금다발","스탯"], ["슬라이드인"], None),
 ("반대로 B. 은퇴자금은 40만 달러로, A의 3분의 2뿐이었죠. 대신 매달 딱 1천 달러씩만 아껴 쓰고, 배당은 한 푼도 안 빼고 전부 재투자했습니다.", "새싹 배경", ["B 인물카드","머니트리","스탯"], ["슬라이드인"], None),
 ("26년이 지난 지금, 두 사람은 과연 어떻게 살고 있을까요?", "얼음/소다 실사", ["전환 스크림"], ["디졸브"], None),
 ("본론에 들어가기 전에, 이 종목부터 짚고 갈까요. 전 세계에서 하루에만 22억 잔이 팔리는 회사입니다.", "자판기 실사", ["대형 숫자","라벨"], ["카운트업"], None),
 ("200개가 넘는 브랜드에, 워런 버핏이 평생 팔지 않은 종목 — 바로 코카콜라죠. 오늘은 이 코카콜라를 25년 백테스트로 낱낱이 파헤쳐 보겠습니다.", "콜라 따르는 실사", ["타이틀","코크 로고","칩(주가·증배·시총)"], ["로고팝"], None),
 ("먼저 2000년에 20만 달러로 은퇴했다고 해보죠. 물가 상승까지 반영하면, 매달 1천 달러씩만 빼 써도 2015년엔 잔고가 바닥납니다. 20만 달러로는 빠듯하다는 뜻이죠.", "차트 배경", ["라인차트","인출액 표","기준선"], ["드로우인"], "FIRE 엔진 · 물가 US CPI 연동 · 세율 15%"),
 ("그럼 40만 달러라면 어떨까요? 매달 1천 달러는 살아남아 71만 달러까지 늘어납니다. 하지만 2천 달러부터는 결국 파산이죠.", "차트 배경", ["라인차트","인출액 표"], ["드로우인"], "FIRE 엔진 · 물가 반영"),
 ("60만 달러여도 매달 3천 달러씩 쓰면 결국 무너집니다. 반대로 1천 달러만 썼다면 184만 달러까지 불어나죠. 얼마를 버느냐가 아니라, 얼마를 쓰느냐 — 그 차이가 이렇게까지 큽니다.", "차트 배경", ["라인차트","인출액 표"], ["드로우인","강조팝"], "FIRE 엔진 · 물가 반영"),
 ("그런데 여기엔 함정이 하나 있습니다. 2000년은 닷컴버블의 정점 — 거의 모든 자산이 비쌌던 시기였죠. 버블이 터지자 S&P500은 반토막, 나스닥은 78%, 시스코·야후 같은 테크주는 90% 넘게 무너졌습니다.", "닷컴 크래시 차트 클립(웹 실사)", ["S&P500 하락 라인","나스닥 라인","테크주 낙폭 표"], ["라인 드로우인"], "S&P500 −49% · 나스닥 −78% · 시스코 −89% · 야후 −97% · 노텔 −99%"),
 ("그래서 이번엔, 버블이 터진 뒤 저점이었던 2002년에 은퇴했다고 바꿔봤습니다. 같은 20만 달러인데, 무려 10년을 더 버팁니다.", "차트 배경", ["라인차트","인출액 표"], ["드로우인"], "FIRE 엔진 · 2002 시작 · 물가 반영"),
 ("40만 달러는 127만 달러로 불어나죠. 2000년에 시작한 것보다 훨씬 큰 결과입니다.", "차트 배경", ["라인차트"], ["드로우인"], "FIRE 엔진 · 2002 시작"),
 ("60만 달러라면 256만 달러까지 갑니다. 똑같은 종목, 똑같은 생활비인데 — 언제 들어갔느냐가 이렇게 운명을 가릅니다.", "차트 배경", ["라인차트"], ["드로우인"], "FIRE 엔진 · 2002 시작"),
 ("그렇다면 배당만으로 살려면 얼마가 필요할까요? 연 3만 달러를 받으려면 약 1만 4천 주, 시가로 약 118만 달러가 있어야 합니다.", "코인 실사", ["가로막대","주식수"], ["카운트업"], "현재 배당수익률 2.5% 기준"),
 ("결국 핵심은 하나죠. 이 회사가 앞으로도 배당을 꾸준히 줄 수 있느냐입니다.", "자판기 실사", ["전환 스크림"], ["디졸브"], None),
 ("코카콜라 매출의 절반 이상은 사실 북미 밖에서 나옵니다. 200개국에 고르게 퍼져 있어서, 한 지역이 흔들려도 전체는 잘 버티죠.", "보틀링 실사", ["세계지도","지역 핀"], ["핀팝"], "지역별 순매출 비중(개략)"),
 ("게다가 무려 64년 연속으로 배당을 올렸습니다. 오일쇼크도, 금융위기도, 코로나도 — 단 한 해도 거르지 않았죠.", "다크 배경", ["연도별 막대","증가곡선"], ["드로우인"], "1963~2026 분할조정 주당배당"),
 ("이 배당, 계속 줄 수 있을까요? 벌어들인 이익의 약 67% 정도를 배당으로 내주고 있어서, 부담스럽지 않은 안정적인 수준입니다.", "다크 배경", ["게이지","컵"], ["채움 애니"], "조정 EPS 대비 배당성향 · 2025 배당 88억$"),
 ("최근 실적도 탄탄합니다. 2026년 1분기 순매출 12.5억 달러, 영업이익률은 35%에 달하죠.", "트레이더 배경", ["KPI 타일 4"], ["팝인"], "2026년 1분기 · 전년 대비"),
 ("그리고 코카콜라는 콜라만 파는 회사가 아닙니다. 물, 주스, 커피까지 200개 브랜드를 갖고 있어서, 한 카테고리가 흔들려도 나머지가 받쳐주죠.", "소다 실사", ["4분할 그리드","제품 이미지"], ["순차 등장"], None),
 ("", "블루 소다 실사", ["전환 스크림"], ["디졸브"], "대사 없음 — 챕터 전환"),
 ("이번엔 은퇴 말고, 순수하게 투자만 했다면 어땠을까요? 2000년에 10만 달러를 넣고 그냥 뒀다면 26년 뒤 55만 달러. 이 중 16만 달러는 오직 배당 재투자가 만들어낸 몫입니다.", "다크 배경", ["가로막대","비교"], ["드로우인"], "일시불 · 배당 재투자 vs 미재투자"),
 ("10만 달러가 55만이 되기까지 — 주가 상승, 받은 배당, 그리고 그 배당을 다시 굴린 힘이 차곡차곡 쌓인 결과죠.", "다크 배경", ["워터폴 차트"], ["단계 등장"], "요인별 기여 · CAGR 6.7%"),
 ("가만히 들고만 있어도 배당은 눈덩이처럼 커집니다. 첫해 1천 달러였던 연 배당이, 재투자를 거치며 1만 1천 달러까지 불어나죠.", "다크 배경", ["누적 막대","기본+재투자"], ["드로우인"], "일시불 10만$ · 연 배당 수령액(엔진 실측)"),
 ("", "콜라캔 실사", ["전환 스크림"], ["디졸브"], "대사 없음 — 챕터 전환"),
 ("이번엔 이제 막 목돈을 모으기 시작한 투자자입니다. A는 쌀 때 사자 — 30% 폭락할 때만 몰아서 사기로 했죠.", "트레이더 배경", ["A 인물카드","현금 대기"], ["슬라이드인"], None),
 ("반면 B는 타이밍 같은 건 신경 쓰지 않습니다. 그냥 매달 꾸준히 사고, 배당은 전부 재투자하죠.", "새싹 배경", ["B 인물카드","적립"], ["슬라이드인"], None),
 ("", "레몬 소다 실사", ["전환 스크림"], ["디졸브"], "대사 없음 — 챕터 전환"),
 ("그런데 말이죠, 코카콜라가 30% 넘게 폭락한 건 2000년 이후로 딱 다섯 번뿐이었습니다. 생각보다 기회가 많지 않죠.", "차트 배경", ["주가 라인","폭락 별표","트리거선"], ["드로우인"], "global_cup 엔진 · KO 일봉"),
 ("그 다섯 번의 폭락만 노린 A는 118만 달러를 만듭니다. 현금을 아꼈다가 폭락에 몰아넣은 결과죠.", "차트 배경", ["라인차트","주식평가액 선","투입 계단"], ["드로우인"], "ko_smart 엔진 · 세율 15.4%"),
 ("그런데 타이밍 없이 매달 꼬박꼬박 산 B도 117만 달러. 거의 차이가 없습니다.", "차트 배경", ["라인차트","원금 점선"], ["드로우인"], "ko_smart 엔진 · 월말 매수"),
 ("완벽한 폭락 타이밍을 잡아도, 그냥 꾸준히 적립한 것과 겨우 1% 차이예요. 오히려 배당을 재투자하지 않았다면, 타이밍을 노린 쪽이 지고 맙니다.", "다크 배경", ["좌우 가로막대","비교"], ["드로우인"], "둘 다 원금 $319,000 동일"),
 ("그럼 최근에 시작했다면 어떨까요? 2020년부터 매달 1천 달러씩 6년 반을 부었다면, 원금 7만 9천 달러가 12만 달러로 늘어납니다. 배당까지 재투자하면 연 12.8%씩 불어난 셈이죠. 시작이 늦어도, 꾸준함은 여전히 통합니다.", "다크 배경", ["좌우 가로막대","적립 계단"], ["드로우인"], "2020.1~2026.7 매월 $1,000 DCA · XIRR 12.8%"),
 ("그래서 담기 전에 체크해 봅시다. 배당 성장은 최고 수준이지만, 성장성은 낮고 밸류에이션은 지금 좀 부담스러운 구간이죠.", "다크 배경", ["체크리스트 4","판정"], ["팝인"], None),
 ("위대한 기업을 적정한 가격에 사서, 아주 오래 보유하라. 워런 버핏의 이 한마디가, 코카콜라를 가장 잘 설명해 줍니다.", "건배 실사", ["대형 인용문","버핏 사진"], ["페이드"], None),
 ("오늘 영상이 도움이 되셨다면 구독과 좋아요, 알림 설정 부탁드려요. 다음엔 어떤 종목을 백테스트해볼까요? 댓글로 남겨주세요!", "건배 실사", ["CTA 타이틀","이모지 칩"], ["로고팝"], None),
]
assert len(SB)==len(S), f"{len(SB)} vs {len(S)}"

# ── dur 재계산: 대본 길이에 맞춰 확장(무대사는 원본 유지) ──
newdurs=[]
for i,s in enumerate(S):
    orig=s.get("dur",5000)
    script=SB[i][0]
    if script:
        chars=len(script.replace(" ",""))
        need=int(math.ceil((chars/RATE+BUF)))*1000
        nd=max(orig, need)
    else:
        nd=orig
    newdurs.append(nd)
    S[i]["dur"]=nd   # 덱에도 반영

def fmt(ms):
    s=ms//1000; return f"00:{s//60:02d}:{s%60:02d}"
durs=newdurs; total=sum(durs); maxd=max(durs)
starts=[]; acc=0
for x in durs: starts.append(acc); acc+=x

def esc(t): return html.escape(t)
cards=[]
for i,(s,(script,bg,els,fxs,src)) in enumerate(zip(S,SB)):
    dur=durs[i]; start=starts[i]
    chars=len(script.replace(" ","")); rate=chars/(dur/1000) if script else 0
    hot=" hot" if rate>=6.5 else ""; quiet=" quiet" if not script else ""
    dat=s.get("data",{})
    title=(dat.get('title') or dat.get('main') or dat.get('eyebrow') or dat.get('num') or dat.get('kick') or dat.get('quote') or '')
    if isinstance(title,str) and title.startswith('data:'): title=''
    title=title.replace('{{coke}}','').replace('|',' · ').strip(' —')
    turi=thumb_uri(i)
    if turi:
        thumb=f'<div class="thumb"><img loading="lazy" alt="씬 {i+1:02d}" src="{turi}"><span class="thnum">{i+1:02d}</span></div>'
    else:
        thumb=f'<div class="thumb ph"><div class="phnum">{i+1:02d}</div><div class="phttl">{esc(title) if title else "전환/인터루드"}</div><div class="phtpl">{s["tpl"]}</div></div>'
    header=(f'<header><span class="num">{i+1:02d}</span>'
            f'<span class="tc">{fmt(start)} <em>&rarr;</em> {fmt(start+dur)}</span>'
            f'<span class="dur">{dur/1000:.1f}s</span>'
            + (f'<span class="rate{hot}" title="발화 속도(공백 제외)">{rate:.1f}자/s</span>' if script else '')
            + f'<span class="durbar"><i style="width:{dur/maxd*100:.1f}%"></i></span></header>')
    sc=(f'<p class="script">{esc(script)}</p>' if script else f'<p class="script mute">{esc(src or "대사 없음")}</p>')
    tags='<div class="tags"><span class="chip bg" title="배경">'+esc(bg)+'</span>'
    for e in els: tags+=f'<span class="chip el" title="요소">{esc(e)}</span>'
    for f in fxs: tags+=f'<span class="chip fx" title="액션">{esc(f)}</span>'
    tags+='</div>'
    srcl=f'<p class="srcline"><b>자료</b> {esc(src)}</p>' if (src and script) else ''
    cards.append(f'<article class="card{quiet}" id="s{i+1}">{thumb}<div class="info">{header}{sc}{tags}{srcl}</div></article>')

CSS = """:root{--bg:#16181d;--panel:#1e2127;--line:#2b2f37;--ink:#e6e8ec;--mute:#8b919c;--amber:#e8a33d;--amber-dim:#8a6526;--coke:#e61a27}
html{background:var(--bg);scroll-behavior:smooth}
body{font-family:"Pretendard Variable",Pretendard,"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif;color:var(--ink);line-height:1.7;margin:0;padding:0 20px 80px}
.wrap{max-width:960px;margin:0 auto}
.masthead{padding:56px 0 28px}
.eyebrow{font-family:ui-monospace,"SF Mono",Consolas,monospace;font-size:12px;letter-spacing:.18em;color:var(--coke);text-transform:uppercase}
h1{font-size:clamp(24px,4vw,34px);font-weight:800;letter-spacing:-.02em;margin:10px 0 6px;text-wrap:balance}
.sub{color:var(--mute);font-size:14.5px;margin:0}.sub b{color:var(--ink);font-weight:600}
.meta{display:flex;gap:28px;margin-top:22px;flex-wrap:wrap}
.meta div{display:flex;flex-direction:column;gap:2px}
.meta dt{font-size:11.5px;color:var(--mute);letter-spacing:.08em}
.meta dd{margin:0;font-size:20px;font-weight:700;font-variant-numeric:tabular-nums;font-family:ui-monospace,Consolas,monospace}
.kbdhint{color:#565c66;font-size:11px;margin-top:8px;font-family:ui-monospace,Consolas,monospace;letter-spacing:.06em}
.tlbox{position:sticky;top:0;z-index:5;background:linear-gradient(var(--bg) 78%,transparent);padding:14px 0 18px}
.tllabel{font-size:11px;color:var(--mute);letter-spacing:.12em;margin-bottom:6px;font-family:ui-monospace,Consolas,monospace;display:flex;justify-content:space-between}
.timeline{display:flex;gap:2px;height:26px;border-radius:4px;overflow:hidden;align-items:flex-end}
.seg{flex-basis:0;flex-grow:var(--g,1);min-width:3px;background:var(--panel);position:relative;height:100%}
.seg span{position:absolute;inset:auto 0 0 0;background:var(--amber-dim)}
.seg:hover,.seg:focus-visible{background:#2a2e36;outline:none}
.seg:hover span,.seg:focus-visible span{background:var(--amber)}
.list{display:flex;flex-direction:column;gap:14px;margin-top:26px}
.card{display:grid;grid-template-columns:300px 1fr;gap:0;background:var(--panel);border:1px solid var(--line);border-radius:6px;overflow:hidden;scroll-margin-top:78px}
.thumb{background:#000;aspect-ratio:16/9;position:relative}
.thumb img{width:100%;height:100%;object-fit:cover;display:block}
.thnum{position:absolute;left:8px;top:7px;font-family:ui-monospace,Consolas,monospace;font-size:12px;font-weight:700;color:#fff;background:rgba(0,0,0,.55);padding:1px 7px;border-radius:3px;font-variant-numeric:tabular-nums}
.thumb.ph{display:flex;flex-direction:column;justify-content:center;padding:14px 16px;background:radial-gradient(120% 120% at 0 0,#242832,#15171c)}
.phnum{font-family:ui-monospace,Consolas,monospace;font-size:13px;color:var(--coke);font-weight:700}
.phttl{font-size:14px;font-weight:700;margin-top:4px;line-height:1.35}
.phtpl{margin-top:auto;font-family:ui-monospace,Consolas,monospace;font-size:10.5px;color:var(--mute);letter-spacing:.08em;text-transform:uppercase}
.info{padding:16px 22px 18px;min-width:0}
.info header{display:flex;align-items:center;gap:14px;margin-bottom:8px;flex-wrap:wrap}
.num{font-family:ui-monospace,Consolas,monospace;font-size:22px;font-weight:700;color:var(--coke);font-variant-numeric:tabular-nums}
.tc{font-family:ui-monospace,Consolas,monospace;font-size:13px;color:var(--mute);font-variant-numeric:tabular-nums}
.tc em{font-style:normal;color:#565c66}
.dur{font-family:ui-monospace,Consolas,monospace;font-size:13px;color:var(--ink);font-variant-numeric:tabular-nums}
.durbar{flex:1;min-width:60px;height:3px;background:var(--line);border-radius:2px;overflow:hidden}
.durbar i{display:block;height:100%;background:var(--amber-dim)}
.rate{font-family:ui-monospace,Consolas,monospace;font-size:11.5px;color:var(--mute);border:1px solid var(--line);border-radius:3px;padding:1px 7px;font-variant-numeric:tabular-nums;white-space:nowrap}
.rate.hot{color:var(--amber);border-color:var(--amber-dim)}
.script{margin:0;font-size:14.5px;max-width:66ch;color:#c9cdd4}
.script.mute{color:#565c66;font-style:italic}
.card.quiet{opacity:.6}.card.quiet:hover{opacity:.9}
.card.kfocus{border-color:var(--coke);box-shadow:0 0 0 1px var(--amber-dim)}
.tags{display:flex;flex-wrap:wrap;gap:5px;margin-top:10px}
.chip{font-size:11px;line-height:1;padding:4px 9px;border-radius:11px;border:1px solid var(--line);color:var(--mute);white-space:nowrap}
.chip.bg{color:#8fa8c8;border-color:#31405a;background:rgba(63,101,158,.08)}
.chip.fx{color:var(--amber);border-color:var(--amber-dim);background:rgba(232,163,61,.07)}
.chip.fx::before{content:"\\25B6 ";font-size:8px;vertical-align:1px}
.srcline{margin-top:8px;font-size:12px;line-height:1.55;color:#79a8d9;border-left:2px solid #2c4258;padding-left:9px}
.srcline b{color:#9fc3e8;font-weight:600}
@media(max-width:720px){.card{grid-template-columns:1fr}}"""

segbar="".join(f'<a class="seg" style="--g:{durs[i]}" href="#s{i+1}" title="{i+1:02d}"><span style="height:{min(100,20+durs[i]/maxd*80):.0f}%"></span></a>' for i in range(len(S)))
JS = """<script>const cards=[...document.querySelectorAll('.card')];let ci=-1;
function focus(n){if(ci>=0)cards[ci].classList.remove('kfocus');ci=Math.max(0,Math.min(cards.length-1,n));cards[ci].classList.add('kfocus');cards[ci].scrollIntoView({behavior:'smooth',block:'center'});}
addEventListener('keydown',e=>{if(e.key==='ArrowRight'){e.preventDefault();focus(ci+1)}if(e.key==='ArrowLeft'){e.preventDefault();focus(ci-1)}});</script>"""
avg=total/len(S)/1000
OUT=f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>코카콜라, 시간이 만든 복리 — 스토리보드 — {len(S)}씬</title><style>{CSS}</style></head><body>
<div class="wrap"><header class="masthead">
<div class="eyebrow">Storyboard · cocacola · KO 25년 배당 백테스트</div>
<h1>코카콜라, 시간이 만든 복리 — 워런 버핏의 영원한 종목</h1>
<p class="sub">머니 리서치 · <b>{len(S)}씬</b> 페이지별 대본 + 컷 구성 · 친근한 설명형</p>
<dl class="meta"><div><dt>총 길이</dt><dd>{fmt(total)[3:]}</dd></div><div><dt>씬</dt><dd>{len(S)}</dd></div>
<div><dt>평균 씬 길이</dt><dd>{avg:.1f}s</dd></div><div><dt>종목</dt><dd>KO</dd></div></dl>
<p class="kbdhint">&larr;/&rarr; 키로 이전·다음 씬 이동</p></header>
<nav class="tlbox" aria-label="씬 타임라인"><div class="tllabel"><span>TIMELINE — 폭은 씬 길이 비례 · 클릭하면 이동</span><span>00:00 &rarr; {fmt(total)[3:]}</span></div>
<div class="timeline">{segbar}</div></nav>
<main class="list">{''.join(cards)}</main></div>{JS}</body></html>"""
open("cocacola-storyboard-sb.html","w",encoding="utf-8").write(OUT)
# 확장된 dur 반영한 덱 저장
json.dump(d, open("cocacola_final36.json","w",encoding="utf-8"), ensure_ascii=False)
print(f"→ 스토리보드 {len(S)}씬 · 총 {fmt(total)[3:]} · 평균 {avg:.1f}s · dur확장 덱→cocacola_final.json")
