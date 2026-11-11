// NODE_PATH=/tmp/pw/node_modules node tools/qa/bctc_types.cjs <production-page.php> <output-dir>
// Serve the unchanged site's assets through routing; POSTs go to local PHP with fake PHPMailer.
// No actual website request and no real email is sent by this test.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), assert = require('assert');
const ROOT = path.resolve(__dirname, '../..');
const PAGE = path.resolve(process.argv[2]), OUT = path.resolve(process.argv[3]);
const ORIGIN = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai';
const SLUG = 'biznes-tsentry-torgovye-tsentry-predpriyatiya';
const TYPES = ['Бизнес-центр или офисное здание','Офис арендатора','Торговый центр','Промышленное предприятие','Несколько объектов'];
const MIME = {'.html':'text/html; charset=utf-8','.php':'text/html; charset=utf-8','.css':'text/css','.js':'application/javascript','.woff2':'font/woff2','.webp':'image/webp','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg'};
fs.mkdirSync(OUT,{recursive:true});
(async()=>{
  const browser = await chromium.launch({executablePath:process.env.HOME+'/.cache/ms-playwright/chromium-1217/chrome-linux64/chrome'});
  try {
    for (const width of [375,1440]) {
      const ctx = await browser.newContext({viewport:{width,height:width===375?740:900}});
      const errors=[],payloads=[];
      await ctx.route('**/*',async route=>{
        const req=route.request(),url=new URL(req.url());
        if(url.origin!==ORIGIN) return route.fulfill({status:200,body:''});
        if(url.pathname==='/send.php') {
          assert.equal(req.method(),'POST');
          const data=req.postDataBuffer().toString();
          const t=data.match(/name="type"\r\n\r\n([^\r]+)/)[1];
          payloads.push(t);
          const response=await route.fetch({url:'http://127.0.0.1:8899/send.php',headers:{...req.headers(),origin:'http://127.0.0.1:8899',host:'127.0.0.1:8899'}});
          assert.equal(response.status(),200);
          assert.equal((await response.json()).success,true);
          const mail=JSON.parse(fs.readFileSync('/home/user/workspace/bctc-types/fixture/mail.json','utf8'));
          assert(mail.html.includes('<b>Тип объекта:</b> '+t+'</p>'));
          assert(mail.text.includes('Тип объекта: '+t+'\n'));
          return route.fulfill({response});
        }
        let p=decodeURIComponent(url.pathname);
        let file=p===`/${SLUG}/`?PAGE:path.join(ROOT,p.endsWith('/')?p+'index.html':p);
        if(!fs.existsSync(file)) return route.fulfill({status:404,body:'Not found'});
        return route.fulfill({status:200,contentType:MIME[path.extname(file)]||'application/octet-stream',body:fs.readFileSync(file)});
      });
      const pg=await ctx.newPage();
      pg.on('pageerror',e=>errors.push(String(e)));
      await pg.goto(ORIGIN+'/'+SLUG+'/');
      await pg.locator('#hero .btn').first().click();
      await pg.locator('#form').scrollIntoViewIfNeeded();
      await pg.locator('#form button[type=submit]').click();
      assert(await pg.locator('#form [aria-invalid=true]').count()>0);
      assert.equal(payloads.length,0);
      await pg.screenshot({path:path.join(OUT,`form-${width}.png`)});
      for (const t of TYPES) {
        await pg.reload();
        const f=pg.locator('#form');
        await f.locator('[name=name]').fill('Тестовая проверка');
        await f.locator('[name=phone]').pressSequentially('9991234567');
        await f.locator('[name=company]').fill('Проверка без отправки реального письма');
        await f.locator('[name=address]').fill('100 м²');
        await f.locator('[name=problem]').fill('Проверка типа объекта');
        await f.locator('[name=type]').selectOption({value:t});
        await f.locator('button[type=submit]').click();
        await pg.locator('#form.sent').waitFor();
        assert.equal(payloads.at(-1),t);
      }
      await pg.reload();
      const checkbox=pg.locator('.f-check-list input').first();
      await checkbox.check();
      await pg.waitForFunction(()=>document.querySelector('#chk-n').textContent==='1');
      await checkbox.uncheck();
      await pg.waitForFunction(()=>document.querySelector('#chk-n').textContent==='0');
      const faq=pg.locator('.qa button').first();
      await faq.click(); assert.equal(await faq.getAttribute('aria-expanded'),'false'); // first FAQ is open initially
      await faq.click(); assert.equal(await faq.getAttribute('aria-expanded'),'true');
      await pg.evaluate(()=>window.scrollTo(0,0));
      if(width===375) {
        await pg.locator('[aria-controls="mmenu"]').click();
        const toggle=pg.locator('[aria-controls="mm-otrasli"]');
        if(await toggle.getAttribute('aria-expanded')!=='true') await toggle.click();
        await pg.locator('#mm-otrasli a[href="../sklady-i-logistika/"]').click();
      } else {
        await pg.locator('[aria-controls="nav-otrasli"]').click();
        await pg.locator('#nav-otrasli a[href="../sklady-i-logistika/"]').click();
      }
      await pg.waitForURL('**/sklady-i-logistika/');
      assert((await pg.locator('h1').innerText()).includes('склад'));
      assert.equal(errors.length,0,errors.join(';'));
      await pg.goto(ORIGIN+'/'+SLUG+'/');
      assert(await pg.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
      console.log(`PASS ${width}px: 5 form→PHP→HTML/text mail types, validation, success UI, FAQ, checklist, navigation; no JS errors/overflow`);
      await ctx.close();
    }
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
