#!/usr/bin/env python3
"""gen_fire_table.py — 파이어 골든 3페이지: 원금 × 월 인출 결과 매트릭스(약 5초 정지).
golden_shorts_fire.py를 import해 폰트·종이·데이터 재사용. accum 테이블 스타일.
직접 실행 → golden_shorts_fire_table.html. import 시 ROWS/MOS/NOTE 노출(에디터 재사용).
"""
import os, re
import golden_shorts_fire as G

HERE = os.path.dirname(os.path.abspath(__file__))
F = G.FIRES
KRW = bool(F[0]["payload"].get("krw"))
MOS = ["월 100만", "월 200만", "월 300만"] if KRW else ["월 $1천", "월 $2천", "월 $3천"]

def hnum(v):   # 원금 표기
    if KRW:
        return ("%.1f억" % (v / 1e8)).replace(".0", "") if v >= 1e8 else ("%d만" % round(v / 1e4))
    return "$" + format(int(round(v)), ",")

def cell(line):
    end = line.get("end", "")
    if line.get("surv"):
        return '<td class="ok">%s</td>' % re.sub(r"^생존\s*", "", end)
    m = re.search(r"'?(\d{2})", end)
    yr = ("'%s" % m.group(1)) if m else end
    return '<td class="ko">%s 파산</td>' % yr

ROWS = ""
for f in F:
    tds = "".join(cell(l) for l in f["payload"]["lines"])
    ROWS += '<tr><td class="pr">%s</td>%s</tr>\n' % (hnum(f["amt"]), tds)

_yr = int(F[0]["payload"].get("x0", 2000))
NOTE = "%d년 은퇴 · 물가반영 인출 · 세금 15%% · ✅=생존 최종액 / 파산=고갈 연도" % _yr

def table_html():   # 독립 페이지(1080×1920, px)
    return """<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:'Pretendard';font-weight:100 900;src:url('{FONT}') format('woff2')}}
*{{margin:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;background:#000;font-family:'Pretendard',sans-serif;overflow:hidden;position:relative}}
.ttl{{position:absolute;left:0;right:0;top:15%;text-align:center;color:#fff;font-weight:900;font-size:46px;letter-spacing:-.02em}}
.ttl b{{color:#d12e77}}
.card{{position:absolute;left:5%;right:5%;top:26%;padding:30px 26px 24px;border-radius:24px;
  background:#fff url('{PAPER}') center/cover;box-shadow:0 20px 60px rgba(0,0,0,.5)}}
table{{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}}
th,td{{text-align:center;padding:16px 6px;font-size:27px;color:#1a1a1a}}
th{{font-size:19px;font-weight:800;color:#8a857c;border-bottom:2px solid rgba(0,0,0,.25)}}
td.pr,th.pr{{text-align:left;font-weight:900;font-size:26px;color:#111}}
th.pr{{color:#8a857c;font-weight:800;font-size:19px}}
tr+tr td{{border-top:1px solid rgba(0,0,0,.12)}}
td.ok{{color:#2b8a3e;font-weight:900}}
td.ko{{color:#c2255c;font-weight:800}}
.note{{margin-top:18px;text-align:center;font-size:17px;font-weight:500;color:#6b6560}}
</style>
<div class="ttl">원금 × 월 인출 <b>결과</b></div>
<div class="card">
<table>
<thead><tr><th class="pr">은퇴원금</th><th>{M0}</th><th>{M1}</th><th>{M2}</th></tr></thead>
<tbody>
{ROWS}</tbody>
</table>
<div class="note">{NOTE}</div>
</div>""".format(FONT=G.FONTSRC, PAPER=G.paper_uri, ROWS=ROWS, M0=MOS[0], M1=MOS[1], M2=MOS[2], NOTE=NOTE)

if __name__ == "__main__":
    open(os.path.join(HERE, "golden_shorts_fire_table.html"), "w", encoding="utf-8").write(table_html())
    print("wrote golden_shorts_fire_table.html")
