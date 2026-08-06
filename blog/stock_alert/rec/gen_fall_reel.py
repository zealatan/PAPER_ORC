#!/usr/bin/env python3
"""gen_fall_reel.py — 낙폭 4시장 테이블 통합 쇼츠(애니 HTML).
golden_shorts_fire 디자인 상속: 검정 배경·흰 종이질감 카드·Pretendard·마젠타 강조 타이틀·
빨강 낙폭·⚠️경고문·배투실 워터마크. + 모션(행 스태거 슬라이드인·낙폭% 카운트업·카드 전환).
페이지 = [통합 인트로] + 시장별 표 ×N.  → _fall_reel.html (playwright로 녹화, build_fall_reel.py).
사용: python3 rec/gen_fall_reel.py --week 31
"""
import argparse
import base64
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SA = os.path.dirname(HERE)                 # stock_alert/
BLOG = os.path.dirname(SA)                 # blog/
GF = os.path.join(BLOG, 'golden_shorts_fire')

FONTSRC = 'data:font/woff2;base64,' + base64.b64encode(
    open(os.path.join(BLOG, 'fonts', 'PretendardVariable.woff2'), 'rb').read()).decode()
_paper = open(os.path.join(GF, 'assets', 'paper_b64.txt')).read().strip()
PAPER = _paper if _paper.startswith('data:') else 'data:image/jpeg;base64,' + _paper
BADGE = json.load(open(os.path.join(GF, 'assets', 'assets.json'))).get('BADGE', '')
# 배투실 마크: 뜨개 마스코트 누끼본(있으면 이걸로 대체, 없으면 기존 배지)
_masc = os.path.join(SA, 'assets', 'shorts', 'mascot_knit.png')
MARK = ('data:image/png;base64,' + base64.b64encode(open(_masc, 'rb').read()).decode()) if os.path.exists(_masc) else BADGE
# 인트로/썸네일 카드(디자인 완성본 이미지). 있으면 이걸 인트로 페이지로 씀.
_thumb = os.path.join(SA, 'assets', 'shorts', 'thumb_fall_multi.png')
THUMB = ('data:image/png;base64,' + base64.b64encode(open(_thumb, 'rb').read()).decode()) if os.path.exists(_thumb) else ''
LOGO_DIR = os.path.join(SA, 'deck', 'logos')
_logo_cache = {}


def logo_uri(ticker):
    """티커→로고 data URI(deck/logos/<티커앞>.png). 없으면 None."""
    base = ticker.split('.')[0]
    for cand in (base, base.upper()):
        p = os.path.join(LOGO_DIR, cand + '.png')
        if os.path.exists(p):
            if p not in _logo_cache:
                _logo_cache[p] = 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
            return _logo_cache[p]
    return None

MK = {'미국': '미국 주식', '한국': '한국 주식', '유럽': '유럽 주식', 'ETF': 'ETF'}
FLAG = {'미국': '🇺🇸', '한국': '🇰🇷', '유럽': '🇪🇺', 'ETF': '📊'}
ORDER = ['미국', '한국', '유럽', 'ETF']
# 한국 종목 한글명(gen_table.KR_NAME 동기)
KR_NAME = {'005930': '삼성전자', '000660': 'SK하이닉스', '402340': 'SK스퀘어', '005380': '현대차',
           '009150': '삼성전기', '373220': 'LG에너지솔루션', '032830': '삼성생명', '028260': '삼성물산',
           '329180': 'HD현대중공업', '000270': '기아', '011070': 'LG이노텍', '006800': '미래에셋증권',
           '066570': 'LG전자', '064400': 'LG CNS', '950160': '코오롱티슈진', '010950': 'S-Oil',
           '078930': 'GS', '161390': '한국타이어', '012450': '한화에어로스페이스',
           '034020': '두산에너빌리티', '012330': '현대모비스',
           '005490': 'POSCO홀딩스', '010130': '고려아연', '051910': 'LG화학'}


def name_of(r):
    code = r['ticker'].split('.')[0]
    return KR_NAME.get(code, r['label'].split(' / ')[0])


def rows_html(rows, show_logo):
    out = []
    for i, r in enumerate(rows):
        dd = abs(r.get('drawdown_pct', 0))
        lg = ''
        if show_logo:
            uri = logo_uri(r['ticker'])
            img = f'<img src="{uri}">' if uri else ''
            lg = f'<td class="lg">{img}</td>'
        out.append(
            f'<tr style="--i:{i}"><td class="rk">{i+1}</td>{lg}'
            f'<td class="nm">{name_of(r)}</td>'
            f'<td class="dd" data-v="{dd:.1f}">▼0.0%</td></tr>')
    return '\n'.join(out)


def section_html(market, rows, week, page, total):
    n = len(rows)
    show_logo = market != 'ETF'          # ETF는 로고 없음(운용사 로고 무의미)
    logo_th = '<th class="lg"></th>' if show_logo else ''
    return f'''<section class="pg" data-mk="{market}">
  <div class="ttl"><span class="flag">{FLAG[market]}</span> {MK[market]} <b>하락</b> TOP{n}</div>
  <div class="card">
    <table>
      <thead><tr><th class="rk">#</th>{logo_th}<th class="nm">종목</th><th class="dd">전고점比</th></tr></thead>
      <tbody>
{rows_html(rows, show_logo)}
      </tbody>
    </table>
    <div class="note">전고점 대비 낙폭 · 2026년 week {week}</div>
  </div>
  <div class="pageind"><b>{page}</b> / {total}</div>
  <img class="bts" src="{MARK}" alt="">
</section>'''


def build_html(data, week):
    if THUMB:                              # 디자인 완성본 썸네일을 인트로로
        intro = f'<section class="pg intro"><img class="thumb" src="{THUMB}"></section>'
    else:                                  # 폴백: 생성 인트로
        intro = f'''<section class="pg intro">
  <div class="flags">{''.join(f'<span>{FLAG[m]}</span>' for m in ORDER)}</div>
  <div class="ihook">이번 주</div>
  <div class="ibig"><b>하락</b> TOP <span class="femoji">📉</span></div>
  <div class="isub">미국 · 한국 · 유럽 · ETF</div>
  <div class="iweek">2026년 week {week}</div>
</section>'''
    markets = [m for m in ORDER if data['markets'].get(m)]
    total = len(markets)
    sections = [intro]
    for idx, m in enumerate(markets):
        sections.append(section_html(m, data['markets'][m], week, idx + 1, total))

    return r'''<!doctype html><meta charset=utf-8><title>fall reel</title>
<style>
@font-face{font-family:'Pretendard';font-weight:100 900;src:url('__FONT__') format('woff2')}
*{margin:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;background:#000;overflow:hidden}
body{font-family:'Pretendard',sans-serif;position:relative}
.pg{position:absolute;inset:0;opacity:0;visibility:hidden}
.pg.on{opacity:1;visibility:visible}
/* ── 페이지 전환 ── */
.pg{transition:opacity .5s ease}
.pg .card{transition:transform .55s cubic-bezier(.16,1,.3,1),opacity .5s ease;transform:translateY(30px);opacity:0}
.pg .ttl{transition:transform .5s cubic-bezier(.16,1,.3,1),opacity .45s ease;transform:translateY(-22px);opacity:0}
.pg .pageind{transition:opacity .5s ease .15s;opacity:0}
.pg.on .card{transform:translateY(0);opacity:1}
.pg.on .ttl{transform:translateY(0);opacity:1}
.pg.on .pageind{opacity:1}
/* ── 타이틀 ── */
.ttl{position:absolute;left:0;right:0;top:8.5%;text-align:center;color:#fff;font-weight:900;font-size:52px;letter-spacing:-.02em}
.ttl b{color:#d12e77}
.ttl .flag{font-size:48px;vertical-align:-2px}
/* ── 카드(종이) ── */
.card{position:absolute;left:5%;right:5%;top:16%;padding:34px 30px 26px;border-radius:26px;
  background:#fff url('__PAPER__') center/cover;box-shadow:0 22px 60px rgba(0,0,0,.55)}
table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
th,td{padding:13px 8px;font-size:33px;color:#1a1a1a;text-align:left}
th{font-size:26px;font-weight:800;color:#8a857c;border-bottom:2px solid rgba(0,0,0,.22);padding-bottom:16px}
td.rk,th.rk{width:74px;text-align:center;font-weight:900;color:#c2255c}
th.rk{color:#8a857c;font-weight:800}
td.nm{font-weight:800;color:#141414;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:520px}
td.dd,th.dd{text-align:right;font-weight:900;color:#c2255c;white-space:nowrap}
th.dd{color:#8a857c;font-weight:800}
td.lg,th.lg{width:118px;padding-left:2px;padding-right:6px}
td.lg img{height:46px;max-width:104px;object-fit:contain;vertical-align:middle;display:block}
tr+tr td{border-top:1px solid rgba(0,0,0,.10)}
tbody td{opacity:0;transform:translateY(18px)}
.pg.on tbody tr td{transition:opacity .5s ease,transform .55s cubic-bezier(.16,1,.3,1);
  transition-delay:calc(.42s + var(--i)*.065s)}
.pg.on tbody tr td{opacity:1;transform:translateY(0)}
.note{margin-top:20px;text-align:center;font-size:19px;font-weight:600;color:#6b6560}
.pageind{position:absolute;left:0;right:0;bottom:13%;text-align:center;font-size:44px;font-weight:800;color:#7d7871;letter-spacing:.02em}
.pageind b{color:#fff;font-weight:900}
.bts{position:absolute;top:7.4%;right:6%;height:132px;width:auto;opacity:.96;filter:drop-shadow(0 3px 6px rgba(0,0,0,.45))}
/* ── 인트로 ── */
.thumb{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}
.intro{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px}
.intro>*{opacity:0;transform:translateY(26px);transition:opacity .5s ease,transform .6s cubic-bezier(.16,1,.3,1)}
.intro.on>*{opacity:1;transform:translateY(0)}
.intro.on .flags{transition-delay:.05s}
.intro.on .ihook{transition-delay:.35s}
.intro.on .ibig{transition-delay:.5s}
.intro.on .isub{transition-delay:.85s}
.intro.on .iweek{transition-delay:1.05s}
.flags{font-size:132px;letter-spacing:14px;margin-bottom:24px}
.ihook{color:#eee;font-weight:800;font-size:70px}
.ibig{color:#fff;font-weight:900;font-size:150px;letter-spacing:-.02em;line-height:1.05}
.ibig b{color:#d12e77}
.ibig .femoji{font-size:110px;vertical-align:-6px}
.isub{color:#eee;font-weight:700;font-size:58px;margin-top:14px}
.iweek{color:#ffd83d;font-weight:800;font-size:52px;margin-top:6px}
</style>
<div id="stage">
__SECTIONS__
</div>
<script>
const PG=[...document.querySelectorAll('.pg')];
const INTRO_MS=2600, MK_MS=8700, FADE=500;   // 표당 ≈1.7s 애니(행 스태거+카운트업) + 7.0s 정지(읽는시간)
function countUp(sec){
  sec.querySelectorAll('tbody .dd').forEach(td=>{
    if(!('v' in td.dataset))return;
    const fin=parseFloat(td.dataset.v); if(isNaN(fin))return;
    const idx=+td.closest('tr').style.getPropertyValue('--i')||0;
    const t0=performance.now()+420+idx*65, dur=680;
    function tick(now){
      const p=Math.min(1,Math.max(0,(now-t0)/dur));
      const e=1-Math.pow(1-p,3);
      td.textContent='▼'+(fin*e).toFixed(1)+'%';
      if(p<1)requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  });
}
window.REEL_MS=INTRO_MS+MK_MS*(PG.length-1)+600;
window.startReel=function(){
  let t=0;
  PG.forEach((pg,k)=>{
    const dur=(k===0)?INTRO_MS:MK_MS;
    setTimeout(()=>{ pg.classList.add('on'); if(!pg.classList.contains('intro'))countUp(pg); }, t);
    // 마지막 페이지는 끝까지 유지
    if(k<PG.length-1) setTimeout(()=>pg.classList.remove('on'), t+dur);
    t+=dur;
  });
};
</script>'''.replace('__FONT__', FONTSRC).replace('__PAPER__', PAPER).replace(
        '__SECTIONS__', '\n'.join(sections))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--week', type=int, required=True)
    ap.add_argument('--out')
    a = ap.parse_args()
    data = json.load(open(os.path.join(SA, 'data', f'fall_week{a.week}.json'), encoding='utf-8'))
    html = build_html(data, a.week)
    out = a.out or os.path.join(SA, '_fall_reel.html')
    open(out, 'w', encoding='utf-8').write(html)
    print('wrote', out, f'({len(html)//1024}KB)')


if __name__ == '__main__':
    main()
