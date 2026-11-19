import { chromium } from 'playwright';
import fs from 'fs';
const SITE='https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/';
const P='/home/user/workspace/site06122026v1/tools/deploy/ipm-pin-2026-11-19/pkg/';
const b=await chromium.launch();
for (const [url,file] of [['', 'index.php'],['deratizatsiya/','deratizatsiya/index.php']]){
 for (const [n,o] of [['d1440',{viewport:{width:1440,height:900}}],['m390',{viewport:{width:390,height:844},isMobile:true,hasTouch:true}]]){
  const p=await (await b.newContext(o)).newPage(); const errs=[];
  p.on('pageerror',e=>errs.push(e.message));
  await p.route('**/*', r=>{const u=r.request().url();
    if(/mc\.yandex|comagic|uiscom|radist|metrika/i.test(u)) return r.abort();
    if(u.startsWith(SITE)) return r.continue(); return r.abort();});
  for(let t=0;t<6;t++){try{await p.goto(SITE+url,{waitUntil:'load',timeout:60000});break;}catch(e){await p.waitForTimeout(3000);}} await p.waitForTimeout(2500);
  const y0=await p.evaluate(()=>document.querySelector('#podhod').getBoundingClientRect().top+scrollY);
  const out=[];
  for(let k=0;k<=14;k++){ await p.evaluate(y=>scrollTo(0,y),y0-100+k*100); await p.waitForTimeout(400);
   out.push(await p.evaluate(()=>{const c=document.querySelector('#cycle').getBoundingClientRect();return Math.round(c.top)+'/'+[...document.querySelectorAll('#podhod .step')].findIndex(s=>s.classList.contains('on'))}));}
  const wide=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
  console.log(url||'/', n, errs.length?errs.join('|'):'no errors', 'hscroll:',wide, out.join(' '));
 }}
await b.close();
