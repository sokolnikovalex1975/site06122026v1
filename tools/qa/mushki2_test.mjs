// Проверка 17.11.2026: «Мухи и мелкие мушки» в заголовках карточек вредителей страниц магазинов и бизнес-центров
// (tools/site/mushki2-2026-11-17.md).
// Запуск: node tools/qa/mushki2_test.mjs   (по умолчанию — рабочий сайт)
// PKG=<папка pkg пакета> — файлы пакета (index.php, search-index.json) подставляются вместо файлов сайта (до выкладки).
// Для каждой страницы на компьютере 1440×900 и телефоне 390×844:
//   1. заголовок карточки «Мухи и мелкие мушки» есть ровно один, старых заголовков нет;
//   2. заголовок и подпись зон помещаются в карточку (нет выхода за край и наложения), нет горизонтальной прокрутки;
//   3. поиск по сайту: в search-index.json у страницы в списке разделов — «Мухи и мелкие мушки», старых строк нет;
//   4. ошибок JavaScript нет.
// Метрика, UIS и Radist не загружаются. Скриншоты карточек — в OUT (по умолчанию /tmp/mushki2-shots).
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const BASE = (process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai').replace(/\/$/, '');
const PKG = process.env.PKG || '';
const OUT = process.env.OUT || '/tmp/mushki2-shots';
fs.mkdirSync(OUT, { recursive: true });
const BLOCK = /mc\.yandex|uiscom|comagic|radist|yandex\.ru\/metrika|mc\.webvisor/;
const NEW = 'Мухи и мелкие мушки';
const OLD = ['Дрозофилы и мухи', 'Мухи, дрозофилы, бабочницы'];
const PAGES = ['/magaziny-i-torgovye-seti/', '/biznes-tsentry-torgovye-tsentry-predpriyatiya/'];
const VPS = [['компьютер 1440×900', 1440, 900, false], ['телефон 390×844', 390, 844, true]];
let bad = 0;
const fail = (m) => { bad++; console.log('НАРУШЕНИЕ', m); };
const norm = (s) => s.replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();

const pkgFile = (p) => (PKG ? path.join(PKG, p) : '');
const browser = await chromium.launch();
for (const pg of PAGES) {
  const local = pkgFile(pg.replace(/^\//, '') + 'index.php');
  const useLocal = local && fs.existsSync(local);
  for (const [vpName, w, h, mobile] of VPS) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, isMobile: mobile, hasTouch: mobile,
      deviceScaleFactor: mobile ? 2 : 1, reducedMotion: 'reduce' });
    await ctx.route('**/*', (r) => {
      const u = r.request().url();
      if (BLOCK.test(u)) return r.abort();
      const p = new URL(u).pathname;
      if (useLocal && r.request().resourceType() === 'document' && p === pg) {
        return r.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: fs.readFileSync(local) });
      }
      if (PKG && p === '/search-index.json' && fs.existsSync(pkgFile('search-index.json'))) {
        return r.fulfill({ status: 200, contentType: 'application/json; charset=utf-8',
          body: fs.readFileSync(pkgFile('search-index.json')) });
      }
      return r.continue();
    });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    const where = `${pg} ${vpName}${useLocal ? ' (пакет)' : ''}`;
    await page.goto(BASE + pg, { waitUntil: 'load', timeout: 90000 });
    await page.waitForTimeout(800);
    const r = await page.evaluate(({ NEW, OLD }) => {
      const norm = (s) => s.replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();
      const hs = [...document.querySelectorAll('h1,h2,h3,h4')];
      const hit = hs.filter((x) => norm(x.textContent) === NEW);
      const old = hs.filter((x) => OLD.includes(norm(x.textContent))).length;
      let geo = null;
      if (hit.length === 1) {
        const h = hit[0];
        h.scrollIntoView({ block: 'center' });
        const card = h.closest('.pest-b') || h.parentElement;
        const head = h.parentElement;
        const lvl = head.querySelector('.lvl');
        const R = (e) => e.getBoundingClientRect();
        const c = R(card), hr = R(h), lr = lvl ? R(lvl) : null;
        const overlap = lr && !(hr.right <= lr.left + 0.5 || lr.right <= hr.left + 0.5 || hr.bottom <= lr.top + 0.5 || lr.bottom <= hr.top + 0.5);
        geo = { out: hr.left < c.left - 0.5 || hr.right > c.right + 0.5 || (lr && (lr.left < c.left - 0.5 || lr.right > c.right + 0.5)),
          overlap: !!overlap, scrollW: h.scrollWidth > h.clientWidth + 1, height: Math.round(hr.height) };
      }
      return { n: hit.length, old, geo, hscroll: document.documentElement.scrollWidth > window.innerWidth + 1 };
    }, { NEW, OLD });
    if (r.n !== 1) fail(`${where}: заголовков «${NEW}» — ${r.n}`);
    if (r.old) fail(`${where}: остались старые заголовки (${r.old})`);
    if (r.geo && (r.geo.out || r.geo.overlap || r.geo.scrollW)) fail(`${where}: вёрстка заголовка ${JSON.stringify(r.geo)}`);
    if (r.hscroll) fail(`${where}: горизонтальная прокрутка`);
    await page.waitForTimeout(300);
    const card = page.locator('h3', { hasText: 'мелкие мушки' }).first().locator('xpath=ancestor::*[contains(@class,"pest")][2]');
    const shot = path.join(OUT, pg.replace(/\//g, '_').replace(/^_|_$/g, '') + '-' + w + '.png');
    try { await card.screenshot({ path: shot }); } catch { await page.screenshot({ path: shot }); }
    if (errors.length) fail(`${where}: ошибки JavaScript: ${errors.join(' | ')}`);
    console.log(`${where}: заголовок 1, старых 0, высота заголовка ${r.geo && r.geo.height} px, скриншот ${shot}`);
    await ctx.close();
  }
}
// поиск по сайту
const si = PKG && fs.existsSync(pkgFile('search-index.json')) ? fs.readFileSync(pkgFile('search-index.json'), 'utf8')
  : await (await fetch(BASE + '/search-index.json', { cache: 'no-store' })).text();
const idx = JSON.parse(si);
for (const pg of PAGES) {
  const slug = pg.replace(/^\//, '');
  const rows = idx.i.filter((x) => x[0] === 'h' && x[1].startsWith(slug + '#') && /вредител|#vrediteli|#pests/i.test(x[1] + x[2]));
  const all = idx.i.filter((x) => x[1].startsWith(slug)).map((x) => norm(x.slice(2, 5).join(' '))).join(' ');
  if (!all.includes(NEW)) fail(`поиск ${pg}: нет «${NEW}»`);
  for (const o of OLD) if (all.includes(o)) fail(`поиск ${pg}: осталось «${o}»`);
  console.log(`поиск ${pg}: «${NEW}» есть, старых строк нет${rows.length ? '' : ''}`);
}
await browser.close();
console.log(bad ? `Нарушений: ${bad}` : 'Нарушений нет');
process.exit(bad ? 1 : 0);
