import { chromium } from 'playwright'; import fs from 'fs';
const BASE=process.env.BASE; const PAGES=[...fs.readFileSync(new URL('../../server/sitemap.xml', import.meta.url),'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)].map(m=>m[1].replace('https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai','')).join(' ').trim().split(/\s+/).filter(x=>!/privacy|soglasie/.test(x));
const b=await chromium.launch(); const out=[];
const ctx=await b.newContext({viewport:{width:320,height:640},isMobile:true,hasTouch:true,reducedMotion:'reduce'});
await ctx.route(/mc\.yandex|uiscom|comagic|radist/, r=>r.abort());
const p=await ctx.newPage(); p.on('pageerror',e=>out.push('JSERR '+p.url()+' '+e.message.slice(0,80)));
for (const pg of PAGES) {
  let ok=false; for(let k=0;k<6&&!ok;k++){ try{const r=await p.goto(BASE+pg,{waitUntil:'load',timeout:45000}); ok=r&&r.status()===200;}catch(e){} if(!ok) await p.waitForTimeout(3000);} if(!ok){out.push(pg+' LOADFAIL');continue;}
  const bt=p.locator('button[aria-controls="mmenu"], .burger').first(); try{ await bt.click({timeout:4000}); }catch(e){ out.push(pg+' noburger'); continue; }
  await p.waitForTimeout(900);
  for (const t of await p.locator('#mmenu button[aria-expanded="false"]').all()) { try{ await t.click({timeout:1000}); }catch(e){} }
  await p.waitForTimeout(500);
  const r=await p.evaluate(()=>{ const m=document.querySelector('#mmenu'); m.scrollTop=300; const h=document.querySelector('#hdr'); const hb=getComputedStyle(h).backgroundColor; return hb; });
  await p.waitForTimeout(800);
  const hb=await p.evaluate(()=>getComputedStyle(document.querySelector('#hdr')).backgroundColor);
  if (hb!=='rgb(0, 0, 0)') out.push(pg+' header bg '+hb);
}
await b.close(); console.log(out.length?out.join('\n'):'menu header ok on all pages');
