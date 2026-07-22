import asyncio, pathlib
from playwright.async_api import async_playwright
URL = pathlib.Path("cocacola_v4.html").resolve().as_uri()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":1280,"height":720})
        await pg.goto(URL); await pg.wait_for_timeout(1800)
        ndots=await pg.evaluate("document.querySelector('#dots').children.length")
        await pg.evaluate("document.querySelector('#dots').children[25].click()")  # p26
        await pg.wait_for_timeout(2500)
        info=await pg.evaluate("""() => {
          const s=document.querySelector('.frame .scene:not(.exit)')||document.querySelector('.frame .scene');
          const t=s.querySelector('.btitle');
          return {
            tpl:(s.querySelector('[class*=tpl-]')?.className||'').match(/tpl-([a-z0-9]+)/)?.[1],
            title:t?t.textContent.trim():null,
            titlePx: t?Math.round(parseFloat(getComputedStyle(t).fontSize)):null,
            lines: s.querySelectorAll('.eline').length,
            legends:[...s.querySelectorAll('.eleg')].map(e=>e.textContent.trim()),
            endlabs:[...s.querySelectorAll('.eend')].map(e=>e.textContent.trim()),
            hline: s.querySelector('.eguide')?.textContent.trim(),
            anno: s.querySelector('.anno')?.textContent.trim().slice(0,60),
          };
        }""")
        print("dots:", ndots)
        print(info)
        await pg.screenshot(path="fire_slide_p26.png")
        print("screenshot -> fire_slide_p26.png")
        await b.close()
asyncio.run(main())
