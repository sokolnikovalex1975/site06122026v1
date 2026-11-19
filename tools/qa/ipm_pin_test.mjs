// Главная, блок IPM (#podhod): круг «цикл визита» закреплён на компьютере, пока прокручиваются шаги (tools/site/ipm_pin.py).
//   python3 -m http.server 8090 --bind 127.0.0.1   (из корня репозитория)
//   node tools/qa/ipm_pin_test.mjs  → по каждому экрану: «сдвиг прокрутки: верх круга / активный шаг / заполнение кольца»
// Компьютер: верх круга не меняется ~1000 px прокрутки, шаг 0→3, заполнение 100→0. Планшет и телефон — как раньше.
import { chromium } from 'playwright';
const BASE='http://127.0.0.1:8090/';
const b=await chromium.launch();
const views=[['d1440',{viewport:{width:1440,height:900}}],['d1280',{viewport:{width:1280,height:720}}],['d1920',{viewport:{width:1920,height:1080}}],['t900',{viewport:{width:900,height:1200},hasTouch:true}],['m390',{viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true}]];
for (const [n,o] of views){
 const p=await (await b.newContext(o)).newPage();
 const errs=[]; p.on('pageerror',e=>errs.push(e.message));
 await p.route('**/*', r => (r.request().url().startsWith(BASE) ? r.continue() : r.abort()));
 await p.goto(BASE,{waitUntil:'load'}); await p.waitForTimeout(2500);
 const y0=await p.evaluate(()=>document.querySelector('#podhod').getBoundingClientRect().top+scrollY);
 const out=[];
 for(let k=0;k<=24;k++){
   const y=y0-200+k*90;
   await p.evaluate(y=>window.scrollTo(0,y),y); await p.waitForTimeout(o.isMobile?300:450);
   const st=await p.evaluate(()=>{const c=document.querySelector('#cycle').getBoundingClientRect();return {ct:Math.round(c.top),on:[...document.querySelectorAll('#podhod .step')].findIndex(s=>s.classList.contains('on')),lbl:document.getElementById('cycleNum').textContent,off:document.getElementById('cycleProg').style.strokeDashoffset,pad:getComputedStyle(document.querySelector('.appr')).getPropertyValue('--pin-pad')}});
   out.push(`${y-y0}:${st.ct}/${st.on}/${st.off}`);
   if(n.startsWith('d1440') && k%3==0) await p.screenshot({path:`/tmp/ipm-pin-${n}-${k}.png`});
   if(n==='m390' && k%6==0) await p.screenshot({path:`/tmp/ipm-pin-${n}-${k}.png`});
 }
 console.log(n, errs.join('|')||'no errors'); console.log(out.join('  '));
}
await b.close();
