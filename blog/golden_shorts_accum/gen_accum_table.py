#!/usr/bin/env python3
"""
gen_accum_table.py — 적립 골든 5번째 페이지: CAGR/XIRR 결과 테이블(약 5초 정지).
golden_shorts_accum.py를 import해 폰트·종이·데이터(pg_accum.json) 재사용.
출력: golden_shorts_accum_table.html  (build 스크립트가 5초 정지 클립으로 합성)
실행: python3 gen_accum_table.py
"""
import os
import golden_shorts_accum as G   # FONTSRC, paper_uri, logo, FIRES(=pg_accum.json)

HERE = os.path.dirname(os.path.abspath(__file__))
F = G.FIRES
INVESTED = F[0]["invested"]
KRW = F[0].get("krw")
MONTHLY = F[0].get("monthly", 1)
def usd(v):
    return ("%s원" % format(int(round(v)), ",")) if KRW else ("$" + format(int(round(v)), ","))
def pct(x): return "%.1f%%" % (x * 100)

# 행: 매달 적립식(파랑) + 각 임계값 하락매수(라즈베리)
rows = [("매달 적립식", F[0]["steady"], "#2b6cb0", True)]
for f in F:
    rows.append(("%d%% 하락매수" % f["thr"], f["smart"], "#c2255c", False))

trs = ""
for name, s, col, steady in rows:
    cls = "steady" if steady else "smart"
    trs += ('<tr class="%s"><td class="nm"><span class="sw" style="background:%s"></span>%s</td>'
            '<td>%s</td><td>%s</td><td class="xr">%s</td></tr>\n'
            % (cls, col, name, usd(s["final"]), pct(s["cagr"]), pct(s["xirr"])))

HTML = """<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:'Pretendard';font-weight:100 900;src:url('{FONT}') format('woff2')}}
*{{margin:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;background:#000;font-family:'Pretendard',sans-serif;overflow:hidden;position:relative}}
.ttl{{position:absolute;left:0;right:0;top:15%;text-align:center;color:#fff;font-weight:900;font-size:46px;letter-spacing:-.02em}}
.ttl b{{color:#d12e77}}
.card{{position:absolute;left:5%;right:5%;top:26%;padding:34px 34px 26px;border-radius:24px;
  background:#fff url('{PAPER}') center/cover;box-shadow:0 20px 60px rgba(0,0,0,.5)}}
table{{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}}
th,td{{text-align:right;padding:16px 8px;font-size:28px;color:#1a1a1a}}
th{{font-size:18px;font-weight:700;color:#8a857c;border-bottom:2px solid rgba(0,0,0,.25)}}
td.nm,th.nm{{text-align:left;font-weight:800}}
td.nm{{font-size:27px}}
.sw{{display:inline-block;width:18px;height:18px;border-radius:5px;margin-right:12px;vertical-align:-2px}}
tr+tr td{{border-top:1px solid rgba(0,0,0,.12)}}
td.xr{{font-weight:900;color:#111}}
th.xr{{color:#111}}
tr.steady td{{background:rgba(43,108,176,.08)}}
.note{{margin-top:20px;text-align:center;font-size:17px;font-weight:500;color:#6b6560}}
</style>
<div class="ttl">적립식 vs 폭락매수 <b>결과</b></div>
<div class="card">
<table>
<thead><tr><th class="nm">전략</th><th>최종 평가액</th><th>CAGR</th><th class="xr">XIRR</th></tr></thead>
<tbody>
{ROWS}</tbody>
</table>
<div class="note">2000년~ 매달 {MON} 적립 · 배당 재투자 · 총 투입원금 {INV}</div>
</div>""".format(FONT=G.FONTSRC, PAPER=G.paper_uri, ROWS=trs, INV=usd(INVESTED), MON=usd(MONTHLY))

open(os.path.join(HERE, "golden_shorts_accum_table.html"), "w", encoding="utf-8").write(HTML)
print("wrote golden_shorts_accum_table.html")
