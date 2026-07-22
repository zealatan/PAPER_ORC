import asyncio, pathlib
from playwright.async_api import async_playwright
URL = pathlib.Path("cocacola_v4.html").resolve().as_uri()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":1280,"height":720})
        await pg.goto(URL); await pg.wait_for_timeout(2000)
        info=await pg.evaluate("""() => {
          const dots=document.querySelector('#dots');
          return {
            dotsChildren: dots? dots.children.length : 'no #dots',
            dotTag: dots&&dots.children[0]? dots.children[0].tagName+'.'+dots.children[0].className : null,
            sceneCount: document.querySelectorAll('.frame .scene').length,
            hasGoto: typeof window.go+'/'+typeof window.goto+'/'+typeof window.show,
          };
        }""")
        print(info)
        # jump to 17th scene (enginechart crash, idx16) via dot click
        await pg.evaluate("document.querySelector('#dots').children[16]?.click()")
        await pg.wait_for_timeout(1500)
        r=await pg.evaluate("""() => {
          const s=document.querySelector('.frame .scene:not(.exit)');
          const t=s.querySelector('.btitle,.ntitle,.cmain');
          const fw=document.querySelector('.frame').clientWidth;
          const cls=s.querySelector('[class*=tpl-]')?.className||s.className;
          return {tpl:(cls.match(/tpl-([a-z0-9]+)/)||[])[1], title:t?t.textContent.trim().slice(0,30):null,
                  px:t?parseFloat(getComputedStyle(t).fontSize):null, fw, cqw:t?Math.round(parseFloat(getComputedStyle(t).fontSize)/fw*1000)/10:null};
        }""")
        print("dot16 ->", r)
        await b.close()
asyncio.run(main())
