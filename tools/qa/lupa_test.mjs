// «Лёгкая лупа» и облегчённый режим (15.11.2026). Все страницы на компьютере (1440×900, мышь) и телефоне (390×844):
// ошибки, лупа появилась, круг нужного размера, копия фото стоит ровно на фото (рамка, кадрирование, файл), фото
// приглушено только под лупой, круг идёт за мышью и возвращается на место, на телефоне лупы и приглушения нет.
// Затем — облегчённый режим вручную (?fx=lite) и по замеру кадров (процессор замедлен в 8 раз), совпадение точек
// под лупой (в лупу ставится то же приглушённое фото — снимки с лупой и без неё должны совпасть).
//   BASE=http://127.0.0.1:8811 node tools/qa/lupa_test.mjs pages.txt      (по умолчанию — рабочий сайт; HOME — главная)
//   PKG=<папка пакета>/pkg — до выкладки: файлы рабочего сайта подменяются файлами пакета. Счётчики заблокированы.
// Итог — $OUT/result.json (по умолчанию /tmp/lupa_test), код выхода 1 при ошибках.
import { chromium } from 'playwright';
import { existsSync, readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';

const BASE = (process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai').replace(/\/$/, '');
const PKG = process.env.PKG || '';
const OUT = process.env.OUT || '/tmp/lupa_test';
mkdirSync(OUT, { recursive: true });
const PAGES = readFileSync(process.argv[2], 'utf8').trim().split('\n').map(x => (x.trim() === 'HOME' ? '' : x.trim()));
const ALIGN = (process.env.ALIGN || 'HOME,deratizatsiya/,deratizatsiya/restorany-i-kafe/,ochistka-dezinfektsiya-ventilyatsii/')
  .split(',').filter(Boolean).map(x => (x === 'HOME' ? '' : x));
const TYPES = { php: 'text/html; charset=utf-8', html: 'text/html; charset=utf-8', css: 'text/css; charset=utf-8',
  js: 'application/javascript; charset=utf-8', webp: 'image/webp' };
const UA_M = 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36';
const FREEZE = '.grain,.cursor,.panel-scan{display:none!important}' +
  '.dot:before,.phone::after,.phone i:after,.scroll-cue i:after,.chip-y:before{animation:none!important}' +
  '.strip{visibility:hidden!important}';  /* бегущая строка движется скриптом — на снимках её нет */
const sleep = ms => new Promise(r => setTimeout(r, ms));
// CACHE=<папка> (с PKG): файлы рабочего сайта, которых нет в пакете, скачиваются один раз (Timeweb отвечает облаку
// медленно и иногда ложным 502) и дальше отдаются с диска; страницы и файлы пакета — всегда из пакета
const CACHE = process.env.CACHE || '';
if (CACHE) mkdirSync(CACHE, { recursive: true });
async function cached(url) {
  const key = createHash('sha1').update(url).digest('hex'), bin = CACHE + '/' + key + '.bin', meta = CACHE + '/' + key + '.json';
  if (existsSync(bin) && existsSync(meta)) return { status: 200, contentType: JSON.parse(readFileSync(meta, 'utf8')).ct, body: readFileSync(bin) };
  for (let i = 0; i < 10; i++) {
    try {
      const res = await fetch(url, { signal: AbortSignal.timeout(20000),
        headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36' } });
      if (res.status === 200) {
        const body = Buffer.from(await res.arrayBuffer()), ct = res.headers.get('content-type') || 'application/octet-stream';
        writeFileSync(bin, body); writeFileSync(meta, JSON.stringify({ url, ct }));
        return { status: 200, contentType: ct, body };
      }
      if (res.status < 500) return null;
    } catch (e) { }
    await sleep(1500 + 1000 * i);
  }
  return null;
}
const browser = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
const result = { base: BASE, pkg: PKG, pages: [], align: [], lowfx: [], bad: [] };
const bad = (where, what) => { result.bad.push(where + ': ' + what); console.log('ОШИБКА', where + ':', what); };

async function open(path, { mobile = false, query = '', w = 1440, h = 900, cpu = 0, intro = false, burn = 0 } = {}) {
  const ctx = await browser.newContext(mobile
    ? { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, userAgent: UA_M, locale: 'ru-RU' }
    : { viewport: { width: w, height: h }, deviceScaleFactor: 1, locale: 'ru-RU' });
  if (!intro) await ctx.addInitScript(() => { try { sessionStorage.setItem('pc-intro', '1'); } catch (e) { } });
  // «слабый компьютер»: после загрузки каждый кадр занят burn мс (замедление процессора в DevTools кадры почти не
  // растягивает, если странице в покое нечего считать, — а замер должен сработать там, где кадры действительно длинные)
  if (burn) await ctx.addInitScript(ms => {
    const f = () => { const t = performance.now(); while (performance.now() - t < ms) { } requestAnimationFrame(f); };
    addEventListener('load', () => requestAnimationFrame(f));
  }, burn);
  const page = await ctx.newPage();
  await page.route(/mc\.yandex|uiscom|comagic|radist|yandex\.ru\/metrika/, r => r.abort());
  if (PKG) await page.route(u => u.href.startsWith(BASE + '/'), async r => {
    const p = decodeURIComponent(new URL(r.request().url()).pathname.replace(/^\//, ''));
    const file = PKG + '/' + (p === '' || p.endsWith('/') ? p + 'index.php' : p);
    if (existsSync(file)) return r.fulfill({ status: 200, contentType: TYPES[file.split('.').pop()] || 'application/octet-stream', body: readFileSync(file) });
    if (!CACHE) return r.continue();
    const c = await cached(r.request().url());  // прочие файлы рабочего сайта — один раз, дальше с диска
    return c ? r.fulfill(c) : r.continue();
  });
  if (cpu) { const s = await ctx.newCDPSession(page); await s.send('Emulation.setCPUThrottlingRate', { rate: cpu }); }
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + String(e).slice(0, 300)));
  page.on('response', r => { if (r.status() >= 400 && r.url().startsWith(BASE)) errors.push(r.status() + ' ' + r.url()); });
  for (let k = 0; k < 4; k++) {  // Timeweb иногда отвечает облаку ложным 502 — тогда страница открывается заново
    errors.length = 0;
    try { await page.goto(BASE + '/' + path + query, { waitUntil: 'load', timeout: 60000 }); }
    catch (e) {
      // страница ошибки Timeweb (ложный 502 облаку) сама перезагружается — дождаться её перезагрузки
      const again = /interrupted by another navigation/.test(String(e)) &&
        await page.waitForLoadState('load', { timeout: 60000 }).then(() => page.evaluate(() => !!document.getElementById('hdr')), () => false).catch(() => false);
      if (!again) { if (k === 3) throw e; errors.push('502 goto: ' + String(e).slice(0, 80)); continue; }
    }
    await page.waitForFunction(() => document.documentElement.classList.contains('anim-ready') ||
      document.documentElement.classList.contains('anim-fail'), null, { timeout: 15000 }).catch(() => {});
    await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {});  // все скрипты загружены
    if (!errors.some(e => /^50\d /.test(e))) break;
  }
  return { ctx, page, errors };
}

const STATE = () => {
  const h = document.documentElement, hero = document.getElementById('hero');
  const lens = document.getElementById('heroLens') || document.getElementById('vLit') || document.querySelector('#hero .fx-lit');
  const out = { cls: h.className, fps: h.getAttribute('data-fps'), cursor: h.classList.contains('has-cursor'), gsap: !!window.gsap,
    hscroll: h.scrollWidth > innerWidth + 1, lens: null, align: null, baseFilter: null, heroBg: null,
    hdrBlur: (() => { const x = document.getElementById('hdr'); return x ? getComputedStyle(x).backdropFilter : null; })() };
  const bg = document.querySelector('.hero-bg');
  if (bg) out.heroBg = getComputedStyle(bg).backgroundImage.replace(/^.*\//, '').replace(/["')]+$/, '');
  if (hero) {
    const im = hero.querySelector('.d-hero-media>picture>img, .hero-media>picture>img');
    if (im) out.baseFilter = getComputedStyle(im).filter;
  }
  if (lens) {
    const r = lens.getBoundingClientRect(), cs = getComputedStyle(lens);
    out.lens = { id: lens.id || lens.className, display: cs.display, op: +(+cs.opacity).toFixed(2),
      on: lens.classList.contains('on') || !!(hero && (hero.classList.contains('fx-lit-on') || hero.classList.contains('v-lit-on'))),
      w: Math.round(r.width), h: Math.round(r.height), c: [Math.round(r.left + r.width / 2), Math.round(r.top + r.height / 2)] };
    if (lens.id !== 'heroLens') {
      const media = lens.parentNode, pic = [...media.children].find(c => c.tagName === 'PICTURE');
      const base = pic && pic.querySelector('img'), copy = lens.querySelector('img');
      if (base && copy) {
        const a = base.getBoundingClientRect(), b = copy.getBoundingClientRect();
        out.align = { d: +Math.max(Math.abs(a.left - b.left), Math.abs(a.top - b.top), Math.abs(a.width - b.width), Math.abs(a.height - b.height)).toFixed(2),
          pos: [getComputedStyle(base).objectPosition, getComputedStyle(copy).objectPosition],
          top: [getComputedStyle(base).top, getComputedStyle(copy).top], src: base.currentSrc === copy.currentSrc && !!base.currentSrc,
          w: Math.round(a.width) };
      }
    }
  }
  return out;
};

const R = w => 2 * Math.round(Math.max(240, Math.min(400, w * 0.21)) * 0.72);

// ---------------------------------------------------------------- 1. все страницы: компьютер и телефон
for (const path of PAGES) {
  const name = path || 'главная';
  const row = { page: name };
  // компьютер с мышью, полный режим
  {
    const { ctx, page, errors } = await open(path, { query: '?fx=full' });
    await sleep(6000);  // лупа внутренних страниц включается со входом первого экрана, страховка — через 5 с
    // страница без входа первого экрана (класс anim-fail в разметке) — лупа по страховке через 5 с и 2 с проявления
    await page.waitForFunction(() => { const l = document.getElementById('heroLens') || document.getElementById('vLit') ||
      document.querySelector('#hero .fx-lit'); return !l || +getComputedStyle(l).opacity > 0.97; }, null, { timeout: 4000 }).catch(() => {});
    const st = await page.evaluate(STATE);
    row.desk = st;
    if (errors.length) bad(name + ' компьютер', errors.join(' | '));
    if (st.hscroll) bad(name + ' компьютер', 'горизонтальная прокрутка');
    if (!st.cursor && st.gsap) bad(name + ' компьютер', 'нет нарисованного курсора');  // юридические страницы — без анимаций
    if (/\blowfx\b/.test(st.cls)) bad(name + ' компьютер', 'облегчённый режим при ?fx=full');
    if (st.lens) {
      if (st.lens.display === 'none' || !st.lens.on || st.lens.op < 0.95) bad(name + ' компьютер', 'лупа не появилась: ' + JSON.stringify(st.lens));
      if (st.lens.w !== R(1440) || st.lens.h !== R(1440)) bad(name + ' компьютер', 'размер лупы ' + st.lens.w + '×' + st.lens.h);
      if (st.align) {
        if (st.align.d > 0.5 || st.align.pos[0] !== st.align.pos[1] || st.align.top[0] !== st.align.top[1] || !st.align.src)
          bad(name + ' компьютер', 'копия фото не на месте фото: ' + JSON.stringify(st.align));
        if (!/grayscale/.test(st.baseFilter || '')) bad(name + ' компьютер', 'фото под лупой не приглушено: ' + st.baseFilter);
      }
      if (st.lens.id === 'heroLens' && st.heroBg !== 'hero-dim.webp') bad(name, 'фото главной ' + st.heroBg);
      // мышь над фото — круг идёт за ней; ушла с первого экрана — возвращается на место
      const home = st.lens.c;
      const target = [Math.round(1440 * 0.82), Math.round(900 * 0.42)];
      await page.mouse.move(target[0] - 60, target[1] - 40);
      await page.mouse.move(target[0], target[1], { steps: 8 });
      await sleep(2200);
      const st2 = await page.evaluate(STATE);
      const dx = Math.abs(st2.lens.c[0] - target[0]), dy = Math.abs(st2.lens.c[1] - target[1]);
      row.follow = { target, c: st2.lens.c, align: st2.align };
      if (dx > 32 || dy > 32) bad(name + ' компьютер', 'круг не дошёл до мыши: ' + JSON.stringify(row.follow));
      if (st2.align && st2.align.d > 0.5) bad(name + ' компьютер', 'после движения копия фото сдвинулась: ' + JSON.stringify(st2.align));
      await page.mouse.move(720, 12, { steps: 4 });  // на шапку — мышь ушла с первого экрана
      await sleep(3000);
      const st3 = await page.evaluate(STATE);
      row.back = { home, c: st3.lens.c };
      if (Math.abs(st3.lens.c[0] - home[0]) > 32 || Math.abs(st3.lens.c[1] - home[1]) > 32) bad(name + ' компьютер', 'круг не вернулся: ' + JSON.stringify(row.back));
    }
    await ctx.close();
  }
  // телефон
  {
    const { ctx, page, errors } = await open(path, { mobile: true });
    await sleep(3500);
    const st = await page.evaluate(STATE);
    row.mob = st;
    if (errors.length) bad(name + ' телефон', errors.join(' | '));
    if (st.hscroll) bad(name + ' телефон', 'горизонтальная прокрутка');
    if (st.cursor) bad(name + ' телефон', 'нарисованный курсор на телефоне');
    if (st.lens && st.lens.display !== 'none') bad(name + ' телефон', 'лупа на телефоне: ' + JSON.stringify(st.lens));
    if (st.lens && st.lens.id !== 'heroLens' && st.baseFilter !== 'none') bad(name + ' телефон', 'фото приглушено без лупы: ' + st.baseFilter);
    if (st.heroBg && st.heroBg !== 'hero-m-dim.webp') bad(name + ' телефон', 'фото главной ' + st.heroBg);
    await ctx.close();
  }
  result.pages.push(row);
  console.log(name, 'ок' + (result.bad.length ? ' (ошибок всего: ' + result.bad.length + ')' : ''));
}

// ---------------------------------------------------------------- 2. облегчённый режим
for (const path of ['', 'deratizatsiya/', 'ochistka-dezinfektsiya-ventilyatsii/'].filter(p => PAGES.includes(p))) {
  const name = path || 'главная';
  {
    const { ctx, page, errors } = await open(path, { query: '?fx=lite' });
    await sleep(4000);
    const st = await page.evaluate(STATE);
    const stored = await page.evaluate(() => sessionStorage.getItem('pc-lowfx'));
    result.lowfx.push({ page: name, mode: 'lite', st, stored });
    if (errors.length) bad(name + ' ?fx=lite', errors.join(' | '));
    if (!/\blowfx\b/.test(st.cls)) bad(name + ' ?fx=lite', 'нет класса lowfx');
    if (st.cursor) bad(name + ' ?fx=lite', 'нарисованный курсор');
    if (st.lens && (st.lens.display !== 'none' || st.lens.on)) bad(name + ' ?fx=lite', 'лупа: ' + JSON.stringify(st.lens));
    if (st.baseFilter && st.baseFilter !== 'none') bad(name + ' ?fx=lite', 'фото приглушено: ' + st.baseFilter);
    if (st.hdrBlur && st.hdrBlur !== 'none') bad(name + ' ?fx=lite', 'матовое стекло шапки: ' + st.hdrBlur);
    // переход на другую страницу того же визита без ?fx — режим помнится? (?fx=lite не запоминается — только авто)
    await ctx.close();
  }
  {
    // замер кадров на «слабом компьютере»: каждый кадр занят 40 мс — через 3 с после загрузки 2 с замера, середина
    // промежутков длиннее 25 мс (меньше 40 кадров в секунду) — облегчённый режим, и он помнится до конца визита
    const { ctx, page, errors } = await open(path, { burn: 40 });
    await sleep(9000);
    const st = await page.evaluate(STATE);
    const stored = await page.evaluate(() => sessionStorage.getItem('pc-lowfx'));
    result.lowfx.push({ page: name, mode: 'weak', st, stored });
    if (errors.length) bad(name + ' замер', errors.join(' | '));
    if (!/\blowfx\b/.test(st.cls) || stored !== '1') bad(name + ' замер', 'облегчённый режим не включился: ' + st.cls + ' fps=' + st.fps);
    if (st.lens && (st.lens.display !== 'none' || st.lens.on)) bad(name + ' замер', 'лупа осталась: ' + JSON.stringify(st.lens));
    if (st.cursor) bad(name + ' замер', 'нарисованный курсор остался');
    // следующая страница того же визита — сразу облегчённая, без нового замера
    if (path !== 'deratizatsiya/') {
      await page.goto(BASE + '/deratizatsiya/', { waitUntil: 'load', timeout: 60000 });
      await sleep(1500);
      const st2 = await page.evaluate(STATE);
      if (!/\blowfx\b/.test(st2.cls)) bad(name + ' замер', 'на следующей странице визита облегчённого режима нет: ' + st2.cls);
    }
    await ctx.close();
  }
  {
    // процессор замедлен в 8 раз (DevTools): решение должно совпасть с замером — меньше 40 кадров в секунду → облегчённый
    const { ctx, page, errors } = await open(path, { cpu: 8 });
    await page.evaluate(() => sessionStorage.removeItem('pc-lowfx'));
    await sleep(9000);
    const st = await page.evaluate(STATE);
    result.lowfx.push({ page: name, mode: 'cpu8', st });
    if (errors.length) bad(name + ' ЦП×8', errors.join(' | '));
    const lite = /\blowfx\b/.test(st.cls), fps = +st.fps;
    if (!st.fps) bad(name + ' ЦП×8', 'замер не прошёл');
    else if (lite ? fps > 40 : fps < 40) bad(name + ' ЦП×8', 'решение не совпало с замером: fps=' + fps + ', облегчённый ' + lite);
    if (lite && st.lens && (st.lens.display !== 'none' || st.lens.on)) bad(name + ' ЦП×8', 'лупа осталась: ' + JSON.stringify(st.lens));
    console.log(name, 'ЦП×8:', fps, 'кадров/с,', lite ? 'облегчённый режим' : 'полный режим');
    await ctx.close();
  }
}

// ---------------------------------------------------------------- 3. совпадение точек под лупой
function diff(a, b) {
  return JSON.parse(execFileSync('python3', ['-c', `
import sys, json
from PIL import Image
import numpy as np
A = np.asarray(Image.open(sys.argv[1]).convert('RGB'), dtype=np.int16); B = np.asarray(Image.open(sys.argv[2]).convert('RGB'), dtype=np.int16)
D = np.abs(A - B).max(axis=2)
print(json.dumps({'mean': round(float(D.mean()), 3), 'p99': int(np.percentile(D, 99)), 'max': int(D.max()), 'over8': round(float((D > 8).mean() * 100), 3)}))
`, a, b]).toString());
}
for (const path of ALIGN.filter(p => PAGES.includes(p))) {
  for (const [w, h] of [[1440, 900], [1920, 1080], [1280, 800]]) {
    const name = (path || 'главная') + ' ' + w + '×' + h;
    const { ctx, page, errors } = await open(path, { query: '?fx=full', w, h });
    await page.addStyleTag({ content: FREEZE + '.fx-lit img,.v-lit .d-hero-img{filter:grayscale(.3) brightness(.56)!important}' +
      '#hero :is(.d-hero-media,.hero-media)>picture>img{transition:none!important}' });
    await sleep(5000);
    await page.evaluate(() => { const i = document.querySelector('.hero-lens-img'); if (i) i.style.backgroundImage = 'url("img/hero-dim.webp")'; });
    await sleep(600);
    for (const [label, pos, scroll] of [['на месте', null, 0], ['мышь', [w * 0.8, h * 0.3], 0], ['край', [w - 6, h * 0.55], 0], ['прокрутка', [w * 0.7, h * 0.35], 260]]) {
      if (pos) { await page.mouse.move(pos[0] - 30, pos[1] - 20); await page.mouse.move(pos[0], pos[1], { steps: 5 }); }
      if (scroll) { await page.mouse.wheel(0, scroll); await sleep(1600); }
      await sleep(2400);
      const a = `${OUT}/al-${(path || 'home').replace(/\W+/g, '_')}-${w}-${label.replace(/\s/g, '_')}-on.png`, b = a.replace('-on.png', '-off.png');
      await page.screenshot({ path: a });
      const st = await page.evaluate(() => {
        const l = document.getElementById('heroLens') || document.getElementById('vLit') || document.querySelector('#hero .fx-lit');
        const r = l.getBoundingClientRect(), op = getComputedStyle(l).opacity;
        l.style.visibility = 'hidden';
        return { op, c: [Math.round(r.left + r.width / 2), Math.round(r.top + r.height / 2)], y: Math.round(scrollY) };
      });
      await sleep(200);
      await page.screenshot({ path: b });
      await page.evaluate(() => { const l = document.getElementById('heroLens') || document.getElementById('vLit') || document.querySelector('#hero .fx-lit'); l.style.visibility = ''; });
      const d = diff(a, b);
      result.align.push({ page: name, label, ...st, ...d });
      if (+st.op < 0.95) bad(name + ' ' + label, 'лупа не видна при сравнении: ' + st.op);
      if (d.mean > 1.2 || d.over8 > 0.5) bad(name + ' ' + label, 'точки под лупой не совпадают: ' + JSON.stringify(d));
    }
    if (errors.length) bad(name + ' совпадение', errors.join(' | '));
    await ctx.close();
  }
}

writeFileSync(OUT + '/result.json', JSON.stringify(result, null, 1));
console.log(result.bad.length ? 'ОШИБОК: ' + result.bad.length : 'OK: ' + PAGES.length + ' страниц, лупа и облегчённый режим по плану');
await browser.close();
process.exit(result.bad.length ? 1 : 0);
