import asyncio, pathlib
from playwright.async_api import async_playwright
URL = pathlib.Path("cocacola_v4.html").resolve().as_uri()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":1280,"height":720})
        await pg.goto(URL); await pg.wait_for_timeout(1800)
        n=await pg.evaluate("document.querySelector('#dots').children.length")
        rows=[]
        for i in range(n):
            await pg.evaluate(f"document.querySelector('#dots').children[{i}].click()")
            await pg.wait_for_timeout(450)
            r=await pg.evaluate("""() => {
              const s=document.querySelector('.frame .scene:not(.exit)')||document.querySelector('.frame .scene');
              const t=s.querySelector('.btitle,.ntitle,.cmain');
              const cls=s.querySelector('[class*=tpl-]')?.className||s.className;
              return {tpl:(cls.match(/tpl-([a-z0-9]+)/)||[])[1],
                      cls:t?t.className.split(' ')[0]:null,
                      px:t?Math.round(parseFloat(getComputedStyle(t).fontSize)):null,
                      txt:t?t.textContent.trim().slice(0,22):''};
            }""")
            rows.append((i+1,r))
        for i,r in rows:
            mark='' if r['cls']!='btitle' else ('  <= 32?' if r['px']==32 else '  !!! %s'%r['px'])
            print(f"p{i:2d} {r['tpl']:11s} {str(r['cls']):8s} {str(r['px']):>5}px  {r['txt']}{mark}")
        await b.close()
asyncio.run(main())
