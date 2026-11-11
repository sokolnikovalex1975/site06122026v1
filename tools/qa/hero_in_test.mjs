// Вход первого экрана «до» (GSAP из app.js) и «после» (встроенный скрипт hero-in): кадры в одни и те же моменты,
// итоговое состояние первого экрана, ошибки, работа анимаций ниже по странице, страховка при медленных скриптах.
// node tools/qa/hero_in_test.mjs <base> <label> <pages.txt> [slowjs|nointro]   (кадры и result.json — в $OUT или /tmp/hero_in_test/<label>)
import { chromium } from 'playwright';
import fs from 'fs';
const base = process.argv[2], label = process.argv[3];
const pages = fs.readFileSync(process.argv[4], 'utf8').trim().split('\n').map(x => x === 'HOME' ? '' : x);
const slow = process.argv[5] === 'slowjs';   // GSAP/app.min.js приходят через 6 с — первый экран не должен их ждать
const nointro = process.argv[5] === 'nointro'; // второй просмотр за визит: заставки нет
const browser = await chromium.launch({ args: [
  '--host-resolver-rules=MAP app.uiscom.ru 127.0.0.1:8443, MAP tracker.comagic.ru 127.0.0.1:8443, MAP app.comagic.ru 127.0.0.1:8443',
  '--ignore-certificate-errors'] });
const dir = `${process.env.OUT || "/tmp/hero_in_test"}/${label}`; fs.mkdirSync(dir, { recursive: true });
const out = [];
const STATE = () => {
  const hero = document.querySelector('#hero');
  const els = hero ? [...hero.querySelectorAll('[data-h], h1 .ln>span, .p-stack>a, .badge, .lead, .hero-ctas')] : [];
  const pn = document.querySelector('#panel'); if (pn) els.push(pn);
  const hidden = els.filter(e => { const cs = getComputedStyle(e); const r = e.getBoundingClientRect();
    return r.width > 0 && (parseFloat(cs.opacity) < 0.99 || (cs.transform !== 'none' && !/^matrix\(1, 0, 0, 1, 0, 0\)$/.test(cs.transform) && !e.matches('.p-stack>a, #panel'))); })
    .map(e => (e.className || e.tagName) + ' op=' + getComputedStyle(e).opacity + ' tr=' + getComputedStyle(e).transform);
  const imgs = hero ? [...hero.querySelectorAll('.d-hero-img, .f-hero-img, .hero-bg')].map(e => getComputedStyle(e).transform) : [];
  return { cls: document.documentElement.className, pcHero: window.pcHero ? Math.round(window.pcHero.t0) : null,
    intro: !!document.querySelector('#intro'), hidden, imgs: [...new Set(imgs)], anims: document.getAnimations().filter(a => a.playState === 'running').length,
    lit: document.querySelector('#heroLit') ? getComputedStyle(document.querySelector('#heroLit')).opacity : null,
    fab: document.querySelector('.fab') ? getComputedStyle(document.querySelector('.fab')).opacity : null,
    lenis: document.documentElement.classList.contains('lenis-stopped') };
};
for (const p of pages) {
  for (const vw of [375, 1440]) {
    const mob = vw < 800;
    const ctx = await browser.newContext({ viewport: { width: vw, height: mob ? 740 : 900 }, deviceScaleFactor: 1, locale: 'ru-RU',
      isMobile: mob, hasTouch: mob,
      userAgent: mob ? 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36'
                     : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36' });
    const page = await ctx.newPage();
    if (nointro) await page.addInitScript(() => { try { sessionStorage.setItem('pc-intro', '1'); } catch (e) {} });
    if (slow) await page.route(/\/(vendor\/[a-zA-Z.]+\.js|app\.min\.js)/, async r => { await new Promise(res => setTimeout(res, 6000)); await r.continue(); });
    const errs = [];
    page.on('pageerror', e => errs.push('pageerror: ' + e.message.slice(0, 200)));
    page.on('console', m => { if (m.type() === 'error' && !/comagic|uiscom|ERR_CERT|favicon|net::ERR|mc\.yandex|radist/.test(m.text())) errs.push('console: ' + m.text().slice(0, 200)); });
    const name = (p.replace(/\//g, '_').replace(/^_|_$/g, '') || 'home') + '_' + vw;
    const t0 = Date.now();
    await page.goto(base + p, { waitUntil: 'commit', timeout: 90000 });
    const frames = {};
    for (const t of [400, 900, 1500, 2300, 3200]) {
      const wait = t - (Date.now() - t0); if (wait > 0) await page.waitForTimeout(wait);
      await page.screenshot({ path: `${dir}/${name}_${t}.png` });
      frames[t] = await page.evaluate(STATE);
    }
    await page.waitForTimeout(Math.max(0, (slow ? 8500 : 5000) - (Date.now() - t0)));
    const end = await page.evaluate(STATE);
    await page.screenshot({ path: `${dir}/${name}_end.png` });
    // ниже по странице: блоки data-fade / группы карточек проявляются при прокрутке (app.js)
    const below = await page.evaluate(async () => {
      const els = [...document.querySelectorAll('[data-fade], [data-group]>*')].slice(0, 6);
      if (!els.length) return 'нет блоков';
      els[0].scrollIntoView({ block: 'center' });
      await new Promise(r => setTimeout(r, 2200));
      return els.slice(0, 3).map(e => parseFloat(getComputedStyle(e).opacity).toFixed(2)).join(',');
    });
    out.push({ p, vw, errs, frames: Object.fromEntries(Object.entries(frames).map(([k, v]) => [k, { hidden: v.hidden.length, intro: v.intro, pc: v.pcHero }])), end, below });
    await ctx.close();
  }
}
await browser.close();
fs.writeFileSync(`${dir}/result.json`, JSON.stringify(out, null, 1));
for (const o of out) console.log([o.vw, o.p || '/', 'err=' + o.errs.length + (o.errs.length ? ' ' + o.errs[0] : ''),
  'hidden@400/900/1500/2300/3200=' + Object.values(o.frames).map(f => f.hidden).join('/'),
  'end.hidden=' + o.end.hidden.length + (o.end.hidden.length ? ' ' + o.end.hidden[0] : ''), 'imgs=' + o.end.imgs.join(';'),
  'intro=' + o.end.intro, 'lit=' + o.end.lit, 'fab=' + o.end.fab, 'lenisStopped=' + o.end.lenis, 'below=' + o.below,
  'cls=' + o.end.cls].join(' | '));
