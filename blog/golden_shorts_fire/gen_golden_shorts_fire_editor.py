#!/usr/bin/env python3
"""
gen_pg_editor.py — PG 통합 쇼츠 에디터(pg_editor.html) 생성 · GOLDEN spec 반영본.

golden_shorts_fire.py 의 NEWRA(x축 이동 reelAnim)·CMAP·fire_payload·CSS 를 재사용해
4슬라이드(1=썸네일 편집가능 / 2·3·4=golden 그래프)를 조립한다.
출력: blog/golden_shorts_fire/golden_shorts_fire_editor.html

의존: golden_shorts_fire.py(같은 폴더, import), assets/assets.json, assets/paper_b64.txt, blog/fonts, pg_deck.json, pg_final.html
실행: python3 gen_pg_editor.py
"""
import json, os, base64
import golden_shorts_fire as G   # NEWRA, CMAP, logo, rc_css, FONTSRC, paper_uri, sc, fire_payload, FIRE_SPECS

HERE = os.path.dirname(os.path.abspath(__file__))
assets = json.load(open(os.path.join(HERE, "assets", "assets.json")))
STOCK = os.environ.get("SHORTS_STOCK", "PG")   # PG(기본) | KTNG — 파이프라인 §0.5: 스펙 고정, 종목 입력만 교체

if STOCK == "PG":
    OUT     = os.path.join(HERE, "golden_shorts_fire_editor.html")
    TITLE   = "golden_shorts_fire_editor — PG 통합 쇼츠 에디터 (썸네일+누적그래프+테이블)"
    LOGO    = G.logo
    COMPANY = "프록터 앤 갬블 (PG)"
    LEGOUT  = ('<span class="lg"><span class="sw" style="background:#2b6cb0"></span>월 $1천 인출</span>'
               '<span class="lg"><span class="sw" style="background:#d98f2b"></span>월 $2천 인출</span>'
               '<span class="lg"><span class="sw" style="background:#c2255c"></span>월 $3천 인출</span>')
    FIRES   = [{"hook": "%d. 은퇴원금 <b>%s</b>" % (i + 1, f["hook"]), "payload": f["payload"]}
               for i, f in enumerate(G.FIRES)]
    # 배투실 표준 썸네일(레퍼런스): 제품클러스터(y37)→브랜드로고(y54)→마젠타문구(y60)→흰문구(y66)
    THUMB_INIT = ("addImg(PRODUCTS,50,37,78,0);addImg(PGLOGO,50,54,15,0);"
                  "addText('5억으로 은퇴',50,60,7,'#d12e77',0);"
                  "addText('적정 생활비는?',50,66,7,'#ffffff',0);")
elif STOCK == "KTNG":
    OUT     = os.path.join(HERE, "golden_shorts_fire_KTNG.html")
    TITLE   = "golden_shorts_fire_KTNG — KT&G 통합 쇼츠 에디터 (썸네일+누적그래프+테이블)"
    LOGO    = ('<text x="100" y="62" text-anchor="middle" font-family="Pretendard,sans-serif" '
               'font-weight="900" font-size="58" fill="#e60012">KT&amp;G</text>')
    COMPANY = "케이티앤지 (KT&G)"
    LEGOUT  = ('<span class="lg"><span class="sw" style="background:#2b6cb0"></span>월 100만 인출</span>'
               '<span class="lg"><span class="sw" style="background:#d98f2b"></span>월 200만 인출</span>'
               '<span class="lg"><span class="sw" style="background:#c2255c"></span>월 300만 인출</span>')
    _kf = json.load(open(os.path.join(HERE, "assets", "ktng_fires.json")))
    FIRES = [{"hook": "%d. 은퇴원금 <b>%s</b>" % (i + 1, f["hook"]), "payload": f["payload"]}
             for i, f in enumerate(_kf)]
    # PG 기준 썸네일 구조: 제품클러스터(y37·사람이 KT&G 사진)→로고(y54)→마젠타문구(y60)→흰문구(y66)
    THUMB_INIT = ("addText('( KT&G 제품 사진은 사람이 추가 )',50,37,4.2,'#5a6472',0);"
                  "addText('KT&amp;G',50,54,5,'#e60012',0);"
                  "addText('6억으로 은퇴',50,60,7,'#d12e77',0);"
                  "addText('적정 생활비는?',50,66,7,'#ffffff',0);")
elif STOCK == "SEC":
    OUT     = os.path.join(HERE, "golden_shorts_fire_SEC.html")
    TITLE   = "golden_shorts_fire_SEC — 삼성전자 통합 쇼츠 에디터 (썸네일+누적그래프+테이블)"
    LOGO    = ('<text x="100" y="62" text-anchor="middle" font-family="Pretendard,sans-serif" '
               'font-weight="900" font-size="48" fill="#1b3660">005930</text>')
    COMPANY = "\uc0bc\uc131\uc804\uc790 (005930)"
    LEGOUT  = ('<span class="lg"><span class="sw" style="background:#2b6cb0"></span>\uc6d4 100\ub9cc \uc778\ucd9c</span>'
               '<span class="lg"><span class="sw" style="background:#d98f2b"></span>\uc6d4 200\ub9cc \uc778\ucd9c</span>'
               '<span class="lg"><span class="sw" style="background:#c2255c"></span>\uc6d4 300\ub9cc \uc778\ucd9c</span>')
    _ef = json.load(open(os.path.join(HERE, "assets", "sec_fires.json")))
    FIRES = [{"hook": "%d. \uc740\ud1f4\uc6d0\uae08 <b>%s</b>" % (i + 1, f["hook"]), "payload": f["payload"]}
             for i, f in enumerate(_ef)]
    THUMB_INIT = ("addText('\uc0bc\uc131\uc804\uc790',50,54,6,'#1b3660',0);"
                  "addText('\uc0bc\uc131\uc804\uc790\ub85c \uc740\ud1f4',50,61,6.4,'#d12e77',0);"
                  "addText('\uc5bc\ub9c8 \uc788\uc5b4\uc57c \ud560\uae4c?',50,67,6.4,'#ffffff',0);")
elif STOCK == "MO":
    OUT     = os.path.join(HERE, "golden_shorts_fire_MO.html")
    TITLE   = "golden_shorts_fire_MO — 알트리아 통합 쇼츠 에디터 (썸네일+누적그래프+테이블)"
    LOGO    = ('<text x="100" y="62" text-anchor="middle" font-family="Pretendard,sans-serif" '
               'font-weight="900" font-size="52" fill="#1b3660">MO</text>')
    COMPANY = "\uc54c\ud2b8\ub9ac\uc544 (MO)"
    LEGOUT  = ('<span class="lg"><span class="sw" style="background:#2b6cb0"></span>\uc6d4 $1\ucc9c \uc778\ucd9c</span>'
               '<span class="lg"><span class="sw" style="background:#d98f2b"></span>\uc6d4 $2\ucc9c \uc778\ucd9c</span>'
               '<span class="lg"><span class="sw" style="background:#c2255c"></span>\uc6d4 $3\ucc9c \uc778\ucd9c</span>')
    _mf = json.load(open(os.path.join(HERE, "assets", "mo_fires.json")))
    FIRES = [{"hook": "%d. \uc740\ud1f4\uc6d0\uae08 <b>%s</b>" % (i + 1, f["hook"]), "payload": f["payload"]}
             for i, f in enumerate(_mf)]
    THUMB_INIT = ("addText('MO',50,54,6,'#1b3660',0);"
                  "addText('\uc54c\ud2b8\ub9ac\uc544\ub85c \uc740\ud1f4',50,61,6.4,'#d12e77',0);"
                  "addText('\uc5bc\ub9c8 \uc788\uc5b4\uc57c \ud560\uae4c?',50,67,6.4,'#ffffff',0);")
elif STOCK == "AAPL":
    OUT     = os.path.join(HERE, "golden_shorts_fire_AAPL.html")
    TITLE   = "golden_shorts_fire_AAPL — 애플 통합 쇼츠 에디터 (썸네일+누적그래프+테이블)"
    LOGO    = ('<path fill="#000" d="M788.1 340.9c-5.8 4.5-108.2 62.2-108.2 190.5 0 148.4 130.3 200.9 134.2 202.2-.6 3.2-20.7 71.9-68.7 141.9-42.8 61.6-87.5 123.1-155.5 123.1s-85.5-39.5-164-39.5c-76.5 0-103.7 40.8-165.9 40.8s-105.6-57-155.5-127C46.7 790.7 0 663 0 541.8c0-194.4 126.4-297.5 250.8-297.5 66.1 0 121.2 43.4 162.7 43.4 39.5 0 101.1-46 176.3-46 28.5 0 130.9 2.6 198.3 99.2zm-234-181.5c31.1-36.9 53.1-88.1 53.1-139.3 0-7.1-.6-14.3-1.9-20.1-50.6 1.9-110.8 33.7-147.1 75.8-28.5 32.4-55.1 83.6-55.1 135.5 0 7.8 1.3 15.6 1.9 18.1 3.2.6 8.4 1.3 13.6 1.3 45.4 0 102.5-30.4 135.5-71.2z"/>')
    COMPANY = "애플 (AAPL)"
    LEGOUT  = ('<span class="lg"><span class="sw" style="background:#2b6cb0"></span>월 $1천 인출</span>'
               '<span class="lg"><span class="sw" style="background:#d98f2b"></span>월 $2천 인출</span>'
               '<span class="lg"><span class="sw" style="background:#c2255c"></span>월 $3천 인출</span>')
    _af = json.load(open(os.path.join(HERE, "assets", "aapl_fires.json")))
    FIRES = [{"hook": "%d. 은퇴원금 <b>%s</b>" % (i + 1, f["hook"]), "payload": f["payload"]}
             for i, f in enumerate(_af)]
    THUMB_INIT = ("addText('AAPL',50,54,6,'#1b3660',0);"
                  "addText('애플로 은퇴',50,61,6.4,'#d12e77',0);"
                  "addText('얼마 있어야 할까?',50,67,6.4,'#ffffff',0);")
elif STOCK == "SPY":
    OUT     = os.path.join(HERE, "golden_shorts_fire_SPY.html")
    TITLE   = "golden_shorts_fire_SPY — S&P 500 통합 쇼츠 에디터 (썸네일+누적그래프+테이블)"
    LOGO    = ('<text x="100" y="62" text-anchor="middle" font-family="Pretendard,sans-serif" '
               'font-weight="900" font-size="52" fill="#1b3660">SPY</text>')
    COMPANY = "S&P 500 \u00b7 SPDR"
    LEGOUT  = ('<span class="lg"><span class="sw" style="background:#2b6cb0"></span>\uc6d4 $1\ucc9c \uc778\ucd9c</span>'
               '<span class="lg"><span class="sw" style="background:#d98f2b"></span>\uc6d4 $2\ucc9c \uc778\ucd9c</span>'
               '<span class="lg"><span class="sw" style="background:#c2255c"></span>\uc6d4 $3\ucc9c \uc778\ucd9c</span>')
    _yf2 = json.load(open(os.path.join(HERE, "assets", "spy_fires.json")))
    FIRES = [{"hook": "%d. \uc740\ud1f4\uc6d0\uae08 <b>%s</b>" % (i + 1, f["hook"]), "payload": f["payload"]}
             for i, f in enumerate(_yf2)]
    THUMB_INIT = ("addText('SPY',50,54,6,'#1b3660',0);"
                  "addText('S&P500\ub85c \uc740\ud1f4',50,61,6.4,'#d12e77',0);"
                  "addText('\uc5bc\ub9c8 \uc788\uc5b4\uc57c \ud560\uae4c?',50,67,6.4,'#ffffff',0);")
elif STOCK == "SCHD":
    OUT     = os.path.join(HERE, "golden_shorts_fire_SCHD.html")
    TITLE   = "golden_shorts_fire_SCHD — SCHD 미국배당 통합 쇼츠 에디터 (썸네일+누적그래프+테이블)"
    LOGO    = ('<text x="100" y="62" text-anchor="middle" font-family="Pretendard,sans-serif" '
               'font-weight="900" font-size="52" fill="#1b3660">SCHD</text>')
    COMPANY = "SCHD \u00b7 \uc288\uc65d \ubbf8\uad6d\ubc30\ub2f9"
    HDRTITLE_SCHD = "\ubbf8\uad6d\ubc30\ub2f9 \ub2e4\uc6b0\uc874\uc2a4100"
    LEGOUT  = ('<span class="lg"><span class="sw" style="background:#2b6cb0"></span>\uc6d4 $1\ucc9c \uc778\ucd9c</span>'
               '<span class="lg"><span class="sw" style="background:#d98f2b"></span>\uc6d4 $2\ucc9c \uc778\ucd9c</span>'
               '<span class="lg"><span class="sw" style="background:#c2255c"></span>\uc6d4 $3\ucc9c \uc778\ucd9c</span>')
    _sf = json.load(open(os.path.join(HERE, "assets", "schd_fires.json")))
    FIRES = [{"hook": "%d. \uc740\ud1f4\uc6d0\uae08 <b>%s</b>" % (i + 1, f["hook"]), "payload": f["payload"]}
             for i, f in enumerate(_sf)]
    THUMB_INIT = ("addText('SCHD',50,54,6,'#1b3660',0);"
                  "addText('\ubbf8\uad6d\ubc30\ub2f9\ub85c \uc740\ud1f4',50,61,6.4,'#d12e77',0);"
                  "addText('\uc5bc\ub9c8 \uc788\uc5b4\uc57c \ud560\uae4c?',50,67,6.4,'#ffffff',0);")
elif STOCK == "QQQ":
    OUT     = os.path.join(HERE, "golden_shorts_fire_QQQ.html")
    TITLE   = "golden_shorts_fire_QQQ — 나스닥100 QQQ 통합 쇼츠 에디터 (썸네일+누적그래프+테이블)"
    # QQQ는 ETF라 회사 로고가 없음 → 운용사 Invesco 공식 로고로 대체(비디오 헤더와 동일)
    _qlogo  = "data:image/png;base64," + base64.b64encode(open(os.path.join(HERE, "assets", "qqq_logo.png"), "rb").read()).decode()
    LOGO    = '<image href="%s" x="0" y="0" width="1280" height="1089"/>' % _qlogo
    COMPANY = "나스닥100 (QQQ) · 운용 Invesco"
    LEGOUT  = ('<span class="lg"><span class="sw" style="background:#2b6cb0"></span>월 $1천 인출</span>'
               '<span class="lg"><span class="sw" style="background:#d98f2b"></span>월 $2천 인출</span>'
               '<span class="lg"><span class="sw" style="background:#c2255c"></span>월 $3천 인출</span>')
    _qf = json.load(open(os.path.join(HERE, "assets", "qqq_fires.json")))
    FIRES = [{"hook": "%d. 은퇴원금 <b>%s</b>" % (i + 1, f["hook"]), "payload": f["payload"]}
             for i, f in enumerate(_qf)]
    # 썸네일: 상단(제품/차트 이미지)은 사람이 import로 추가 · Invesco 로고 + 문구
    THUMB_INIT = ("var QLOGO=%s;addImg(QLOGO,50,52,16,0);"
                  "addText('나스닥 QQQ로 은퇴',50,61,6.4,'#d12e77',0);"
                  "addText('얼마 있어야 할까?',50,67,6.4,'#ffffff',0);") % json.dumps(_qlogo)
else:
    raise SystemExit("unknown SHORTS_STOCK: " + STOCK)

# 로고 viewBox(이미지 로고는 원본 비율) — 편집기 헤더 svg
LOGOVB = {"QQQ": "0 0 1280 1089", "AAPL": "0 0 814 1000"}.get(STOCK, "0 0 200 87.021")
HDRTITLE = {"QQQ": "QQQ 나스닥 100", "KTNG": "KT&amp;G 케이티앤지", "SCHD": "미국배당 다우존스100", "SPY": "S&P 500 지수", "MO": "알트리아", "SEC": "삼성전자", "AAPL": "애플"}.get(STOCK, "PG 프록터앤갬블")

DATA_JS = ("var PRODUCTS=%s,BADGE=%s,PGLOGO=%s,MCDLOGO=%s,JNJLOGO=%s;\n"
           "var FIRES=%s;\nvar ACCUM=%s;\nvar PACE=1.0;\n") % (
    json.dumps(assets["PRODUCTS"]), json.dumps(assets["BADGE"]), json.dumps(assets["PGLOGO"]),
    json.dumps(assets["MCDLOGO"]), json.dumps(assets["JNJLOGO"]), json.dumps(FIRES, ensure_ascii=False),
    json.dumps(G.ACCUM_DATA, ensure_ascii=False))

HTML = r'''<!doctype html><html lang=ko><head><meta charset=utf-8>
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>__TITLE__</title>
<style>
@font-face{font-family:'Pretendard';font-weight:100 900;font-style:normal;font-display:swap;src:url('__FONTSRC__') format('woff2')}
*{margin:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{background:#0b0e13;font-family:'Pretendard','Noto Sans KR',sans-serif;display:flex;flex-direction:column;align-items:center;min-height:100vh;padding:8px;color:#e9eef6}
.bar{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;padding:7px;position:sticky;top:0;z-index:50;background:#0b0e13;width:100%;max-width:1180px}
.bar button,.bar label{font:inherit;font-size:13px;font-weight:800;color:#e9eef6;background:#243040;border:1px solid #38465a;border-radius:9px;padding:8px 10px;cursor:pointer;display:inline-flex;align-items:center;gap:5px}
.bar button:active{background:#2f3f54}.bar button.on{background:#1d5fa8;border-color:#2f7be6}
.bar .sep{width:1px;background:#38465a;margin:2px 3px}
.bar input[type=color]{width:30px;height:28px;padding:0;border:none;border-radius:7px;background:none;cursor:pointer}
.bar .dim{opacity:.35;pointer-events:none}
#prev,#next{background:#22304a}#play{background:#6ea8ff;color:#0a0f18}#rmode{background:#7a5a2a}
#saveJson{background:#2e8b57}#loadJson{background:#3a4f8a}#save{background:#1d7a3f;border-color:#2aa15a}
.pdots{display:flex;gap:6px;align-items:center;margin:0 3px}.pdot{width:9px;height:9px;border-radius:50%;background:#2c3a52;cursor:pointer}.pdot.act{background:#6ea8ff}
.nb{display:flex;gap:4px;align-items:center;background:#111a28;padding:4px 8px;border-radius:8px;font-size:12px;font-weight:700}
.nb input{width:48px;font:inherit;background:#0a0f18;color:#fff;border:1px solid #2c3a52;border-radius:5px;padding:3px 5px;text-align:center}
.nb.dim{opacity:.35;pointer-events:none}
#hint{color:#8a97ad;font-size:11.5px;margin:1px 0 5px;text-align:center}
.stagewrap{width:100%;max-width:min(94vw,430px)}
.stage{position:relative;width:100%;aspect-ratio:9/16;background:#000;border-radius:12px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,.5);touch-action:none;container-type:size}
/* --- thumb_editor 요소 --- */
.el{position:absolute;transform:translate(-50%,-50%);cursor:grab;touch-action:none;z-index:10}
.el.sel{outline:2px dashed #49c6ff;outline-offset:3px}
.el.tb{color:#fff;font-weight:900;line-height:1.12;letter-spacing:-.02em;white-space:pre;text-align:center;text-shadow:0 3px 14px rgba(0,0,0,.6);padding:2px 6px}
.el.tb.outlined{-webkit-text-stroke:0.5cqw #000;paint-order:stroke fill;text-shadow:none}
.el.tb.editing{cursor:text;outline:2px solid #49c6ff}
.el.img img{display:block;width:100%;height:auto;pointer-events:none}
.el.tb b{color:#d12e77}   /* GOLDEN: 훅 강조=마젠타 */
#guide{position:absolute;inset:0;pointer-events:none;z-index:9998;display:none}#guide.on{display:block}
#guide .grid{position:absolute;inset:0;background-image:repeating-linear-gradient(0deg,rgba(255,255,255,.13) 0 1px,transparent 1px 10%),repeating-linear-gradient(90deg,rgba(255,255,255,.13) 0 1px,transparent 1px 10%)}
#guide .cx{position:absolute;left:50%;top:0;bottom:0;width:0;border-left:1px dashed rgba(0,229,255,.75)}
#guide .cy{position:absolute;top:50%;left:0;right:0;height:0;border-top:1px dashed rgba(0,229,255,.75)}
/* --- 차트 배경(그래프 슬라이드) --- */
.reelbg{position:absolute;inset:0;background:#000;z-index:1;display:none;container-type:size}
.graphbox{position:absolute;left:0;right:0;top:22%;aspect-ratio:1.125/1;container-type:size}
.reelbg .tophdr{position:absolute;top:14%;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:2.4cqw;z-index:6}
.reelbg .btsmark{position:absolute;top:28.5%;right:8%;width:6.5%;opacity:.85;z-index:7}
.reelbg .toplogo{height:9.6cqw;width:auto;filter:brightness(0) invert(1)}
.reelbg .toptitle{color:#fff;font-weight:900;font-size:5.2cqw;letter-spacing:-.02em;white-space:nowrap}
__RCCSS__
/* ===== GOLDEN 그래프 스펙 (golden_shorts_fire.py 와 동일 유지) ===== */
.tpl-reel{border-radius:0;background:transparent}.tpl-reel .rc-alL{text-anchor:end}
.tpl-reel .rc-card{left:0;right:0;top:0;bottom:0;border-radius:0;background:#fff url('__PAPER__') center/cover}
.tpl-reel .rc-card::before{display:none}
.tpl-reel .rc-chd{left:6.67cqw;top:3cqw;gap:2.4cqw}   /* 로고+문구 y축 정렬(업로드 잘림 방지) */
.tpl-reel .rc-logo{height:6.8cqw}   /* 헤더 2배 */
.tpl-reel .rc-ln{stroke-width:3.4}
.tpl-reel .rc-ax{font-size:27px;font-weight:400;fill:#000}
.tpl-reel .ytick{stroke:rgba(0,0,0,.22)}
.tpl-reel .rc-hlab{font-size:40px;font-weight:700;fill:#333;text-anchor:start}
.tpl-reel .rc-hline{stroke-width:2.8;stroke:#555}
.tpl-reel .rc-labv{font-size:27px;font-weight:600}
.tpl-reel .rc-base{stroke:#000}
.tpl-reel .rc-tk{font-weight:600;color:#111;font-size:4cqw}.tpl-reel .rc-per{font-weight:400;color:#111;font-size:2.6cqw}   /* 헤더 2배 */
.tpl-reel,.tpl-reel *,.rc-chart text{font-family:'Pretendard','Noto Sans KR',sans-serif!important}
/* 훅(누적 애니가 원금별 갱신) */
.reelbg .hook{position:absolute;left:0;right:0;top:80%;text-align:center;color:#fff;font-weight:900;font-size:7cqw;letter-spacing:-.02em;z-index:6}.reelbg .hook b{color:#d12e77}   /* 그래프 카드 바로 아래 */
/* 범례: 그래프 밖(카드 위) */
.legout{position:absolute;left:0;right:0;top:24.5%;display:flex;justify-content:center;gap:4.5cqw;z-index:5}
.legout .lg{display:flex;align-items:center;gap:1.1cqw;color:#333;font-weight:700;font-size:3cqw}
.legout .sw{width:2.8cqw;height:2.8cqw;border-radius:.4cqw}
/* --- 테이블 배경(3페이지) --- */
.tablebg{position:absolute;inset:0;background:#000;z-index:1;display:none;container-type:size}
.tablebg .ttl{position:absolute;left:0;right:0;top:15%;text-align:center;color:#fff;font-weight:900;font-size:4.3cqw;letter-spacing:-.02em}.tablebg .ttl b{color:#d12e77}
.tablebg .card{position:absolute;left:5%;right:5%;top:26%;padding:2.8cqw 2.4cqw 2.2cqw;border-radius:2.2cqw;background:#fff url('__PAPER__') center/cover;box-shadow:0 20px 60px rgba(0,0,0,.5)}
.tablebg table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
.tablebg th,.tablebg td{text-align:center;padding:1.5cqw .6cqw;font-size:2.5cqw;color:#1a1a1a}
.tablebg th{font-size:2.5cqw;font-weight:800;color:#8a857c;border-bottom:.2cqw solid rgba(0,0,0,.25)}
.tablebg td.pr,.tablebg th.pr{text-align:left;font-weight:900;font-size:2.4cqw;color:#111}
.tablebg th.pr{color:#8a857c;font-weight:800;font-size:2.4cqw}
.tablebg tr+tr td{border-top:.1cqw solid rgba(0,0,0,.12)}
.tablebg td.ok{color:#2b8a3e;font-weight:900}
.tablebg td.ko{color:#c2255c;font-weight:800}
.tablebg .note{margin-top:1.7cqw;text-align:center;font-size:1.57cqw;font-weight:500;color:#6b6560}
.tablebg .disc{position:absolute;left:6%;right:6%;top:55.5%;text-align:center;font-size:3cqw;font-weight:700;color:#c68a7f;line-height:1.4}
/* --- clean 렌더 모드: 편집 UI 전부 숨김 --- */
body.render .bar,body.render #hint{display:none}
body.render .el.sel{outline:none}
body.render #guide{display:none!important}
</style></head><body>
<div class="bar" id="bar">
  <button id="prev">◀</button><div class="pdots"></div><button id="next">▶</button>
  <button id="play">⏸ 재생</button>
  <span class="sep"></span>
  <button id="addText">➕텍스트</button><button id="addBadge">🐻배투실</button><button id="addPG">🅿️P&amp;G</button>
  <button id="addProd">📦제품</button><button id="importBtn">🖼임포트</button><input type="file" id="fileIn" accept="image/*" style="display:none">
  <span class="sep"></span>
  <label id="colWrap" class="dim">색<input type="color" id="col" value="#ffffff"></label>
  <button id="outline" class="dim">🔲외곽선</button><button id="minus" class="dim">−</button><button id="plus" class="dim">＋</button>
  <button id="front" class="dim">▲앞</button><button id="del" class="dim">🗑</button>
  <span class="sep"></span>
  <span class="nb dim" id="nbSel">선택 X<input type="number" id="nx" step="0.5">Y<input type="number" id="ny" step="0.5">크기<input type="number" id="ns" step="0.5">색<input type="color" id="nc"></span>
  <span class="sep"></span>
  <button id="guideBtn">📐가이드</button><button id="rmode">👁 렌더</button>
  <button id="saveJson">⬇JSON</button><button id="loadJson">⬆JSON</button><input type="file" id="jsonf" accept="application/json,.json" style="display:none">
  <button id="save">💾PNG</button>
</div>
<div id="hint">탭=선택·드래그=이동 · 숫자박스=정밀 X/Y/크기/색 · 텍스트더블탭=수정 · 👁렌더=편집UI 숨김 · 슬라이드마다 요소 따로</div>
<div class="stagewrap"><div class="stage" id="stage">
  <div class="reelbg">
    <div class="tophdr"><svg class="toplogo" viewBox="__LOGOVB__">__LOGO__</svg><span class="toptitle">__HDRTITLE__</span></div>
    <div class="graphbox"><div class="zoom tpl-reel">
      <div class="rc-title"></div>
      <div class="rc-card">
        <svg class="rc-chart" viewBox="0 0 960 960" preserveAspectRatio="xMidYMid meet" data-rc="">
          <g class="rc-yaxis"></g><g class="rc-xaxis"></g>
          <line class="rc-base"/><line class="rc-hline" x1="70" x2="780" style="display:none"/><text class="rc-hlab" x="780"></text>
          <g class="rc-lines"></g></svg>
      </div></div></div>
    <div class="legout">__LEGOUT__</div>
    <img class="btsmark" src="__BADGE__" alt="">
  </div>
  <div class="tablebg"><div class="ttl">원금 × 월 인출 <b>결과</b></div>
    <div class="card"><table>
      <thead><tr><th class="pr">은퇴원금</th><th>__M0__</th><th>__M1__</th><th>__M2__</th></tr></thead>
      <tbody>__TROWS__</tbody></table>
      <div class="note">__TNOTE__</div></div>
      <div class="disc">__TDISC__</div></div>
  <div id="guide"><div class="grid"></div><div class="cx"></div><div class="cy"></div></div>
</div></div>
<script>
__DATA__
__REELANIM__
/* ============ 통합 에디터 엔진 ============ */
var stage=document.getElementById('stage'), reelbg=stage.querySelector('.reelbg');
var svg=stage.querySelector('.rc-chart');
var sel=null, z=10, cur=0, NSLIDE=3;   /* 0=썸네일 · 1=누적그래프 · 2=테이블 */
function gid(id){return document.getElementById(id);}
function rgb2hex(c){var m=c.match(/\d+/g);if(!m)return '#ffffff';return '#'+m.slice(0,3).map(function(x){return ('0'+parseInt(x).toString(16)).slice(-2);}).join('');}
function isTb(el){return el&&el.classList.contains('tb');}
function elSize(el){return parseFloat(isTb(el)?el.style.fontSize:el.style.width)||(isTb(el)?9:30);}
function setToolState(){var on=!!sel,tb=isTb(sel);
  ['minus','plus','front','del'].forEach(function(id){gid(id).classList.toggle('dim',!on);});
  gid('colWrap').classList.toggle('dim',!tb);gid('outline').classList.toggle('dim',!tb);
  gid('nbSel').classList.toggle('dim',!on);
  if(on){gid('nx').value=(parseFloat(sel.style.left)||50).toFixed(1);gid('ny').value=(parseFloat(sel.style.top)||50).toFixed(1);gid('ns').value=elSize(sel).toFixed(1);
    if(tb){var hx=rgb2hex(getComputedStyle(sel).color);gid('col').value=hx;gid('nc').value=hx;gid('outline').classList.toggle('on',sel.classList.contains('outlined'));}}
}
function select(el){if(sel)sel.classList.remove('sel');sel=el;if(el)el.classList.add('sel');setToolState();}
stage.addEventListener('pointerdown',function(e){if(e.target===stage||e.target===reelbg||e.target.id==='guide'||(e.target.parentNode&&e.target.parentNode.id==='guide'))select(null);});
function pct(el){return {l:parseFloat(el.style.left)||50,t:parseFloat(el.style.top)||50};}
function makeDrag(el){
  el.addEventListener('pointerdown',function(e){
    if(el.classList.contains('editing'))return; e.stopPropagation();select(el);
    var rect=stage.getBoundingClientRect(),p=pct(el),ox=p.l,oy=p.t,sx=e.clientX,sy=e.clientY;
    el.setPointerCapture(e.pointerId);el.style.cursor='grabbing';
    function mv(ev){var dx=(ev.clientX-sx)/rect.width*100,dy=(ev.clientY-sy)/rect.height*100;el.style.left=(ox+dx)+'%';el.style.top=(oy+dy)+'%';gid('nx').value=(ox+dx).toFixed(1);gid('ny').value=(oy+dy).toFixed(1);}
    function up(ev){try{el.releasePointerCapture(e.pointerId);}catch(_){}el.style.cursor='grab';el.removeEventListener('pointermove',mv);el.removeEventListener('pointerup',up);}
    el.addEventListener('pointermove',mv);el.addEventListener('pointerup',up);});
  if(isTb(el)){var last=0;el.addEventListener('pointerup',function(){var now=Date.now();if(now-last<350)edit(el);last=now;});}}
function edit(el){el.classList.add('editing');el.contentEditable=true;el.focus();
  var r=document.createRange();r.selectNodeContents(el);var s=getSelection();s.removeAllRanges();s.addRange(r);
  el.addEventListener('blur',function h(){el.classList.remove('editing');el.contentEditable=false;el.removeEventListener('blur',h);});}
function addText(txt,left,top,size,color,slide){var el=document.createElement('div');el.className='el tb';el.innerHTML=(txt==null?'텍스트':txt);
  el.dataset.s=(slide==null?cur:slide);el.style.left=(left||50)+'%';el.style.top=(top||50)+'%';el.style.fontSize=(size||9)+'cqw';el.style.color=color||'#fff';el.style.zIndex=++z;
  stage.appendChild(el);makeDrag(el);applyVis(el);return el;}
function addImg(src,left,top,w,slide){var el=document.createElement('div');el.className='el img';
  el.dataset.s=(slide==null?cur:slide);el.style.left=(left||50)+'%';el.style.top=(top||50)+'%';el.style.width=(w||30)+'cqw';el.style.zIndex=++z;
  var img=document.createElement('img');img.src=src;el.appendChild(img);stage.appendChild(el);makeDrag(el);applyVis(el);return el;}
function applyVis(el){el.style.display=(+el.dataset.s===cur)?'':'none';}
/* 툴바 */
gid('addText').onclick=function(){var e=addText('새 텍스트',50,50,9,'#fff');select(e);};
gid('addBadge').onclick=function(){select(addImg(BADGE,86,7,22));};
gid('addPG').onclick=function(){select(addImg(PGLOGO,50,70,30));};
gid('addProd').onclick=function(){select(addImg(PRODUCTS,50,45,96));};
gid('importBtn').onclick=function(){gid('fileIn').click();};
gid('fileIn').onchange=function(e){var f=e.target.files&&e.target.files[0];if(!f)return;var r=new FileReader();r.onload=function(){select(addImg(r.result,50,45,70));};r.readAsDataURL(f);this.value='';};
gid('del').onclick=function(){if(sel){sel.remove();select(null);}};
gid('front').onclick=function(){if(sel)sel.style.zIndex=++z;};
gid('col').oninput=function(){if(isTb(sel)){sel.style.color=this.value;gid('nc').value=this.value;}};
gid('outline').onclick=function(){if(isTb(sel)){sel.classList.toggle('outlined');setToolState();}};
gid('guideBtn').onclick=function(){var g=gid('guide');g.classList.toggle('on');this.classList.toggle('on',g.classList.contains('on'));};
function resize(f){if(!sel)return;if(isTb(sel)){var s=parseFloat(sel.style.fontSize)||9;sel.style.fontSize=Math.max(3,s*f)+'cqw';}else{var w=parseFloat(sel.style.width)||30;sel.style.width=Math.max(6,w*f)+'cqw';}gid('ns').value=elSize(sel).toFixed(1);}
gid('plus').onclick=function(){resize(1.1);};gid('minus').onclick=function(){resize(1/1.1);};
/* 숫자박스 → 선택요소 */
gid('nx').oninput=function(){if(sel)sel.style.left=this.value+'%';};
gid('ny').oninput=function(){if(sel)sel.style.top=this.value+'%';};
gid('ns').oninput=function(){if(!sel)return;if(isTb(sel))sel.style.fontSize=this.value+'cqw';else sel.style.width=this.value+'cqw';};
gid('nc').oninput=function(){if(isTb(sel)){sel.style.color=this.value;gid('col').value=this.value;}};
/* PNG (요소만 · 썸네일용) */
gid('save').onclick=function(){
  var W=1080,H=1920,cv=document.createElement('canvas');cv.width=W;cv.height=H;var ctx=cv.getContext('2d');
  ctx.fillStyle='#000';ctx.fillRect(0,0,W,H);
  var els=[].slice.call(stage.querySelectorAll('.el')).filter(function(e){return +e.dataset.s===cur;});
  els.sort(function(a,b){return (parseInt(a.style.zIndex)||0)-(parseInt(b.style.zIndex)||0);});
  var was=sel;if(sel)sel.classList.remove('sel');
  els.forEach(function(el){var cx=(parseFloat(el.style.left)||50)/100*W,cy=(parseFloat(el.style.top)||50)/100*H;
    if(el.classList.contains('img')){var img=el.querySelector('img');var w=(parseFloat(el.style.width)||30)/100*W;var rr=img.getBoundingClientRect();var ratio=(rr.width?rr.height/rr.width:0.5);var h=w*ratio;try{ctx.drawImage(img,cx-w/2,cy-h/2,w,h);}catch(e){}}
    else{var fs=(parseFloat(el.style.fontSize)||9)/100*W;ctx.font="900 "+fs+"px 'Pretendard','Noto Sans KR',sans-serif";ctx.textAlign='center';ctx.textBaseline='middle';var lines=(el.innerText||'').split('\n');var lh=fs*1.12;var y0=cy-(lines.length-1)*lh/2;lines.forEach(function(ln,i){var yy=y0+i*lh;if(el.classList.contains('outlined')){ctx.lineWidth=fs*0.16;ctx.strokeStyle='#000';ctx.lineJoin='round';ctx.strokeText(ln,cx,yy);}ctx.fillStyle=el.style.color||'#fff';ctx.fillText(ln,cx,yy);});}});
  if(was)was.classList.add('sel');
  var a=document.createElement('a');a.download='pg_slide'+cur+'.png';a.href=cv.toDataURL('image/png');a.click();};
/* ============ 슬라이드 / 시퀀스 (GOLDEN 타이밍) ============ */
var auto=false,timer=null,THUMB_HOLD=1250,TABLE_HOLD=5000;
var ACCUM_TOTAL=(ACCUM.intro||0)+ACCUM.dur.reduce(function(a,b){return a+b;},0)+ACCUM.hold.reduce(function(a,b){return a+b;},0)+Math.max(0,ACCUM.dur.length-1)*(ACCUM.trans||0);
(function(){var pd=document.querySelector('.pdots');for(var i=0;i<NSLIDE;i++){var d=document.createElement('span');d.className='pdot';(function(k){d.onclick=function(){auto=false;setPlayBtn();showSlide(k);};})(i);pd.appendChild(d);}})();
function dots(){document.querySelectorAll('.pdot').forEach(function(d,k){d.classList.toggle('act',k===cur);});}
var tablebg=stage.querySelector('.tablebg');
function showSlide(i){cur=(i+NSLIDE)%NSLIDE;
  stage.querySelectorAll('.el').forEach(function(e){e.style.display=(+e.dataset.s===cur)?'':'none';});
  select(null);dots();if(timer)clearTimeout(timer);
  reelbg.style.display='none';tablebg.style.display='none';
  if(cur===0){if(auto)timer=setTimeout(function(){showSlide(1);},THUMB_HOLD);return;}   /* 썸네일 */
  if(cur===1){reelbg.style.display='block';svg.setAttribute('data-rc',JSON.stringify(ACCUM));accumAnim(reelbg);
    if(auto)timer=setTimeout(function(){showSlide(2);},ACCUM_TOTAL+400);return;}          /* 누적 그래프 */
  tablebg.style.display='block';                                                          /* 결과 테이블 */
  if(auto)timer=setTimeout(function(){showSlide(0);},TABLE_HOLD);}
function setPlayBtn(){gid('play').textContent=auto?'⏸ 재생':'▶ 재생';}
gid('prev').onclick=function(){auto=false;setPlayBtn();showSlide(cur-1);};
gid('next').onclick=function(){auto=false;setPlayBtn();showSlide(cur+1);};
gid('play').onclick=function(){auto=!auto;setPlayBtn();if(auto)showSlide(cur);else if(timer)clearTimeout(timer);};
/* clean 렌더 모드 */
gid('rmode').onclick=function(){var on=document.body.classList.toggle('render');this.classList.toggle('on',on);if(on)select(null);};
/* ============ JSON 저장/불러오기 ============ */
function serEl(el){return {s:+el.dataset.s,tb:isTb(el),x:el.style.left,y:el.style.top,size:isTb(el)?el.style.fontSize:el.style.width,z:el.style.zIndex,
  html:isTb(el)?el.innerHTML:'',src:isTb(el)?'':el.querySelector('img').src,color:isTb(el)?el.style.color:'',outlined:el.classList.contains('outlined')};}
gid('saveJson').onclick=function(){
  var els=[].slice.call(stage.querySelectorAll('.el')).map(serEl);
  var data={v:2,cur:cur,z:z,els:els};
  var a=document.createElement('a');a.download='pg_editor_layout.json';a.href=URL.createObjectURL(new Blob([JSON.stringify(data)],{type:'application/json'}));document.body.appendChild(a);a.click();a.remove();};
gid('loadJson').onclick=function(){gid('jsonf').click();};
gid('jsonf').onchange=function(e){var f=e.target.files&&e.target.files[0];if(!f)return;var r=new FileReader();r.onload=function(){try{var d=JSON.parse(r.result);
  stage.querySelectorAll('.el').forEach(function(el){el.remove();});z=d.z||10;
  (d.els||[]).forEach(function(o){var el;if(o.tb){el=addText(o.html,parseFloat(o.x),parseFloat(o.y),parseFloat(o.size),o.color,o.s);if(o.outlined)el.classList.add('outlined');}else{el=addImg(o.src,parseFloat(o.x),parseFloat(o.y),parseFloat(o.size),o.s);}el.style.zIndex=o.z;});
  auto=false;setPlayBtn();showSlide(typeof d.cur==='number'?d.cur:0);
  }catch(err){alert('불러오기 실패: '+err.message);}};r.readAsText(f);this.value='';};
/* ============ 초기 배치 (GOLDEN) ============ */
/* 슬라이드0 = 썸네일(편집가능·종목별 내용) */
__THUMB_INIT__
/* 슬라이드1 훅은 accumAnim이 원금별로 자동 갱신(편집 요소 아님) */
select(null);
(document.fonts?document.fonts.ready:Promise.resolve()).then(function(){showSlide(0);});
</script></body></html>'''

import gen_fire_table as T   # ROWS/MOS/NOTE 재사용(3페이지 테이블)
out = (HTML.replace('__RCCSS__', G.rc_css).replace('__LOGOVB__', LOGOVB).replace('__LOGO__', LOGO)
           .replace('__DATA__', DATA_JS).replace('__REELANIM__', G.ACCUM)
           .replace('__FONTSRC__', G.FONTSRC).replace('__PAPER__', G.paper_uri)
           .replace('__TITLE__', TITLE).replace('__COMPANY__', COMPANY)
           .replace('__LEGOUT__', LEGOUT).replace('__THUMB_INIT__', THUMB_INIT).replace('__HDRTITLE__', HDRTITLE)
           .replace('__M0__', T.MOS[0]).replace('__M1__', T.MOS[1]).replace('__M2__', T.MOS[2])
           .replace('__TROWS__', T.ROWS).replace('__TNOTE__', T.NOTE).replace('__TDISC__', T.DISC)
           .replace('__BADGE__', assets['BADGE']))
open(OUT, "w", encoding="utf-8").write(out)
print("wrote", OUT, "(STOCK=%s)" % STOCK, round(len(out) / 1024), "KB")
