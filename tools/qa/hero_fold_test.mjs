// Проверка: кнопки первого экрана целиком видны (не ниже нижнего края и не шире экрана)
// Запуск: BASE=http://localhost:8090 node tools/qa/hero_fold_test.mjs (нужен playwright: npm i playwright)
// Размеры экрана — VP='[["имя",ширина,высота,mobile]]', страницы — PAGES='/ /restorany-i-kafe/'.
// Итог: JSON; кнопки первого экрана должны быть выше нижнего края (с учётом нижней панели) и не шире экрана.
import { chromium } from 'playwright';
const BASE = process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai';
const PAGES = (process.env.PAGES || `/
/dezinfektsiya/
/deratizatsiya/
/dezinsektsiya/
/deratizatsiya-i-dezinsektsiya/
/sanitarnyy-audit/
/razrabotka-ppk/
/dogovor-deratizatsiya-dezinsektsiya/
/ochistka-dezinfektsiya-ventilyatsii/
/pishchevoe-proizvodstvo/
/restorany-i-kafe/
/magaziny-i-torgovye-seti/
/gostinitsy/
/farmatsevticheskie-proizvodstva/
/sklady-i-logistika/
/biznes-tsentry-torgovye-tsentry-predpriyatiya/
/materialy/
/materialy/programma-pest-kontrolya/
/materialy/zhurnal-pest-kontrolya/
/materialy/pest-menedzhment-ili-razovaya-obrabotka/
/materialy/programma-proizvodstvennogo-kontrolya-haccp/
/normativnaya-baza/
/normativnaya-baza/proverochnye-listy/
/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/`).trim().split(/\s+/);
// [имя, ширина, высота видимой области, mobile]
const VP = (process.env.VP ? JSON.parse(process.env.VP) : [
 ['iPhone SE 320×480',320,480,true],['Android 360×640',360,640,true],['iPhone SE2 375×553',375,553,true],
 ['iPhone 13 390×664',390,664,true],['Android 412×780',412,780,true],['iPhone Pro Max 430×739',430,739,true],
 ['планшет 768×1024',768,1024,true],['планшет гориз. 1024×768',1024,768,true],
 ['ноутбук 1280×600',1280,600,false],['ноутбук 1366×657',1366,657,false],['ноутбук 1440×760',1440,760,false],
 ['ноутбук 1536×730',1536,730,false],['монитор 1920×947',1920,947,false],['телефон гориз. 844×390',844,390,true]]);
const browser = await chromium.launch();
const out = [];
for (const [vn,w,h,mob] of VP) {
  const ctx = await browser.newContext({viewport:{width:w,height:h},deviceScaleFactor:1,isMobile:mob,hasTouch:mob,reducedMotion:'no-preference'});
  await ctx.route(/mc\.yandex|uiscom|comagic|radist|yandex\.ru\/metrika|mc\.webvisor/, r=>r.abort());
  for (const p of PAGES) {
    const page = await ctx.newPage();
    try {
      await page.goto(BASE+p,{waitUntil:'load',timeout:60000});
      await page.waitForTimeout(3500);
      const r = await page.evaluate(()=>{
        const h1=document.querySelector('h1'); if(!h1) return {err:'no h1'};
        // ближайший предок-секция с кнопками
        let sec=h1; while(sec && sec!==document.body && !sec.querySelector('a.btn,button.btn')) sec=sec.parentElement;
        // кнопки: внутри секции h1, в первом блоке кнопок после h1
        const btns=[...sec.querySelectorAll('a.btn,button.btn')].filter(b=>{const r=b.getBoundingClientRect();const cs=getComputedStyle(b);return r.width>0&&r.height>0&&cs.visibility!=='hidden'&&!b.closest('header,nav,.mnav,.m-menu,form,dialog')});
        // берём только первую группу (первый родитель с кнопками)
        if(!btns.length) return {err:'no btns'};
        const grp=btns[0].parentElement; const g=btns.filter(b=>b.parentElement===grp);
        const rs=g.map(b=>{const r=b.getBoundingClientRect();return {t:b.innerText.trim().slice(0,40),top:Math.round(r.top+scrollY),bottom:Math.round(r.bottom+scrollY),left:Math.round(r.left),right:Math.round(r.right),sw:b.scrollWidth,cw:b.clientWidth}});
        const fixedBar=[...document.querySelectorAll('body *')].filter(e=>{const cs=getComputedStyle(e);if(cs.position!=='fixed'&&cs.position!=='sticky')return false;const r=e.getBoundingClientRect();return r.height>30&&r.top>innerHeight*0.6&&r.top<innerHeight&&r.width>innerWidth*0.5}).map(e=>Math.round(e.getBoundingClientRect().top));
        return {ih:innerHeight,iw:innerWidth,docW:document.documentElement.scrollWidth,btns:rs,bar:fixedBar.length?Math.min(...fixedBar):null,sy:scrollY};
      });
      out.push({vn,w,h,p,...r});
    } catch(e){ out.push({vn,w,h,p,err:String(e).slice(0,100)}); }
    await page.close();
  }
  await ctx.close();
}
await browser.close();
console.log(JSON.stringify(out));
