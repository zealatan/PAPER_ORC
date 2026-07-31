#!/usr/bin/env python3
"""prep_fire.py — 파이어 누적 그래프(그대로)를 캔버스 iframe용으로 준비.

golden_shorts_fire 로 <stock> 그래프 생성 → out/<stock>_fire.html 로 복사 → autorun 스크립트 추가.
※ iframe은 file:// 교차출처라 부모(canvas)에서 accumAnim 호출이 막힌다 → 그래프가 **스스로**
   폰트 로드 후 accumAnim 을 실행하도록 autorun 을 붙인다. (fire_block 이 이 파일을 로드해 재생.)

사용: SHORTS_STOCK=QYLD python3 prep_fire.py
"""
import os, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
FIRE = os.path.abspath(os.path.join(HERE, "..", "golden_shorts_fire"))
STOCK = os.environ.get("SHORTS_STOCK", "QYLD")

subprocess.run(["python3", "golden_shorts_fire.py"], cwd=FIRE, check=True,
               env={**os.environ, "SHORTS_STOCK": STOCK})
src = os.path.join(FIRE, "golden_shorts_fire_1.html")
dst = os.path.join(HERE, "out", "%s_fire.html" % STOCK.lower())
shutil.copy(src, dst)

s = open(dst, encoding="utf-8").read()
if "__AUTORUN__" not in s:
    s += ('\n<!--__AUTORUN__--><script>document.fonts.ready.then(function(){'
          'requestAnimationFrame(function(){requestAnimationFrame(function(){'
          'accumAnim(document.querySelector(".graphbox"));});});});</script>')
    open(dst, "w", encoding="utf-8").write(s)
print("wrote %s (%s 파이어 그래프 + autorun)" % (dst, STOCK))
