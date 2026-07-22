import asyncio, pathlib
from playwright.async_api import async_playwright

URL = pathlib.Path("cocacola_v4.html").resolve().as_uri()

async def measure(pg):
    return await pg.evaluate("""() => {
      const s=document.querySelector('.frame .scene:not(.exit)')||document.querySelector('.frame .scene');
      if(!s) return null;
      const cls=[...s.querySelectorAll('[class*=tpl-]')].map(e=>e.className).join(' ')+' '+s.className;
      const tpl=(cls.match(/tpl-([a-z0-9]+)/)||[])[1]||'?';
      const t=s.querySelector('.btitle,.ntitle,.cmain');
      const fw=document.querySelector('.frame')?.clientWidth;
      if(!t) return {tpl,cls:null,px:null,cqw:null,txt:''};
      const px=parseFloat(getComputedStyle(t).fontSize);
      return {tpl,cls:t.className.split(' ')[0],px:Math.round(px*10)/10,cqw:Math.round(px/fw*1000)/10,txt:t.textContent.trim().slice(0,26)};
    }""")

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width":1280,"height":720})
        await pg.goto(URL)
        await pg.wait_for_timeout(2000)
        seen=[]
        for i in range(1,41):
            r = await measure(pg)
            if r:
                print(f"p{i:2d} {r['tpl']:11s} {str(r['cls']):8s} {str(r['px']):>7}px  {str(r['cqw']):>5}cqw  {r['txt']}")
            await pg.keyboard.press("ArrowRight")
            await pg.wait_for_timeout(700)
        await b.close()

asyncio.run(main())
