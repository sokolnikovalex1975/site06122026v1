// Первый экран главной при прокрутке (13.11.2026): до 1280 px текст и панель «Что покажет бесплатный аудит» не гаснут
// и не уезжают, фото не двигается; на телефоне (до 760 px) от низа панели до бегущей строки 32 px. Шире 1280 px —
// прежний «уход первого экрана» (затемнение, сдвиг вверх, параллакс фото). В конце — смена ширины 1440 → 1200 → 1440.
// Запуск: BASE=http://127.0.0.1:8090 node tools/qa/hero_scroll_test.mjs   (по умолчанию — рабочий сайт; нужен playwright)
// VERSION=20261113ekran — проверить ещё и версию app.min.js на странице. Счётчики в тесте заблокированы.
// PKG=<папка пакета>/pkg — до выкладки: страницы, style.css и app.min.js рабочего сайта подменяются файлами пакета.
import { chromium } from 'playwright';
import { existsSync, readFileSync } from 'node:fs';

const BASE = (process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai').replace(/\/$/, '');
const VERSION = process.env.VERSION || '';
const PKG = process.env.PKG || '';
const TYPES = { php: 'text/html; charset=utf-8', css: 'text/css; charset=utf-8', js: 'application/javascript; charset=utf-8' };
const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1';
const SIZES = [[360, 800], [375, 667], [390, 844], [430, 932], [768, 1024], [820, 1180], [1024, 768], [1280, 800], [1440, 900], [1920, 1080]];

const browser = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
let bad = 0;

// Timeweb иногда отвечает облаку ложным 502 на vendor/gsap.min.js — тогда страница открывается заново (до 4 раз)
async function open(w, h, tries = 4) {
  const r = await open1(w, h);
  if (tries > 1 && !(await r.page.evaluate(() => !!window.gsap && !!window.ScrollTrigger))) {
    await r.ctx.close();
    return open(w, h, tries - 1);
  }
  return r;
}

async function open1(w, h) {
  const touch = w < 1025;
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: touch ? 3 : 1, isMobile: touch, hasTouch: touch, ...(touch ? { userAgent: UA } : {}) });
  const page = await ctx.newPage();
  await page.route(/mc\.yandex|uiscom|radist|yandex\.ru\/metrika/, r => r.abort());
  if (PKG) await page.route(u => u.href.startsWith(BASE + '/'), r => {
    const path = new URL(r.request().url()).pathname.replace(/^\//, '');
    const file = PKG + '/' + (path === '' || path.endsWith('/') ? path + 'index.php' : path);
    if (!existsSync(file)) return r.continue();
    return r.fulfill({ status: 200, contentType: TYPES[file.split('.').pop()], body: readFileSync(file) });
  });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  await page.goto(BASE + '/', { waitUntil: 'load' });
  await page.waitForFunction(() => !!window.gsap && !!window.ScrollTrigger, null, { timeout: 10000 }).catch(() => {});
  // заставка: пока она идёт, Lenis остановлен и прокрутки нет — ждём, пока её уберут, и вход первого экрана
  await page.waitForFunction(() => !document.getElementById('intro'), null, { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(2500);
  return { ctx, page, errors };
}

const probe = page => page.evaluate(() => {
  const w = getComputedStyle(document.querySelector('#hero .wrap'));
  const p = document.querySelector('#panel').getBoundingClientRect(), s = document.querySelector('.strip').getBoundingClientRect();
  return { y: Math.round(scrollY), op: +(+w.opacity).toFixed(2), tr: w.transform, media: getComputedStyle(document.querySelector('#heroMedia')).transform,
    gap: Math.round(s.top - p.bottom), hscroll: document.documentElement.scrollWidth > innerWidth,
    js: [...document.querySelectorAll('script')].map(x => x.src).filter(x => x.includes('app.min.js')) };
});

async function scrollTo(page, y) {
  await page.evaluate(v => window.scrollTo({ top: v, behavior: 'instant' }), y);
  await page.waitForTimeout(600);
  return probe(page);
}

for (const [w, h] of SIZES) {
  const { ctx, page, errors } = await open(w, h);
  const rows = [];
  for (const y of [0, Math.round(h * 0.5), Math.round(h * 0.9)]) rows.push(await scrollTo(page, y));
  const wide = w > 1280, phone = w <= 760;
  const still = rows.every(r => r.op === 1 && r.tr === 'none' && r.media === 'none');
  const gapsSame = rows.every(r => r.gap === rows[0].gap);
  let ok = !errors.length && rows.every(r => !r.hscroll);
  if (wide) ok = ok && rows[0].op === 1 && rows[1].op < 0.9 && rows[1].tr !== 'none' && rows[2].op < rows[1].op;
  else ok = ok && still && gapsSame && (!phone || rows[0].gap === 32);
  if (VERSION) ok = ok && rows[0].js.length > 0 && rows[0].js.every(s => s.endsWith('app.min.js?v=' + VERSION));
  if (!ok) bad++;
  console.log((ok ? 'OK  ' : 'BAD ') + `${w}x${h}`.padEnd(10) + (wide ? ' эффект ' : ' без эффекта ') +
    rows.map(r => `y${r.y}: яркость ${r.op}, сдвиг ${r.tr === 'none' ? 0 : r.tr.split(',')[5].trim().replace(')', '')}, фото ${r.media === 'none' ? 'стоит' : 'движется'}, отступ ${r.gap}`).join(' | ') +
    (errors.length ? ' ОШИБКИ JS: ' + errors.join('; ') : ''));
  await ctx.close();
}

// смена ширины окна: эффект снимается до 1280 px и возвращается шире
{
  const { ctx, page, errors } = await open(1440, 900);
  const a = await scrollTo(page, 450);
  await page.setViewportSize({ width: 1200, height: 900 }); await page.waitForTimeout(900);
  const b = await scrollTo(page, 450);
  await page.setViewportSize({ width: 1440, height: 900 }); await page.waitForTimeout(900);
  const c = await scrollTo(page, 451);
  const ok = !errors.length && a.op < 0.9 && b.op === 1 && b.tr === 'none' && b.media === 'none' && c.op < 0.9;
  if (!ok) bad++;
  console.log((ok ? 'OK  ' : 'BAD ') + 'смена ширины 1440 → 1200 → 1440: яркость ' + [a.op, b.op, c.op].join(' → ') + (errors.length ? ' ОШИБКИ JS: ' + errors.join('; ') : ''));
  await ctx.close();
}

await browser.close();
console.log('нарушений:', bad);
process.exit(bad ? 1 : 0);
