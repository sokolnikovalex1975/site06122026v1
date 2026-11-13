// Проверка 13.11.2026: вопросы внизу страницы — при открытии страницы развёрнут только первый, остальные свёрнуты.
// Запуск: BASE=http://127.0.0.1:8090 node tools/qa/faq_first_test.mjs   (по умолчанию — рабочий сайт)
// PKG=<папка pkg пакета> — подставить страницы пакета (index.php) вместо страниц сайта (проверка до выкладки).
// SHOTS=<папка> — снимки блока «Вопросы» (компьютер 1440 и телефон 390) для страниц из SHOT_PAGES (через пробел).
// Для каждой страницы из server/sitemap.xml (нет на сайте — пропуск), компьютер 1440×900 и телефон 390×844:
//   1. после загрузки у первого вопроса класс open, aria-expanded="true" и видимый ответ; у остальных — свёрнуты;
//   2. щелчок по второму вопросу раскрывает его, повторный — сворачивает (вопросы по-прежнему открываются);
//   3. ошибок JavaScript нет.
// Счётчики не загружаются (запросы к Метрике, UIS и Radist обрываются). Итог — число нарушений; код выхода 1, если есть.
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const BASE = (process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai').replace(/\/$/, '');
const PKG = process.env.PKG || '';
const SHOTS = process.env.SHOTS || '';
const SHOT_PAGES = (process.env.SHOT_PAGES || '').trim().split(/\s+/).filter(Boolean);
const ONLY = (process.env.PAGES || '').trim().split(/\s+/).filter(Boolean);
const BLOCK = /mc\.yandex|uiscom|comagic|radist|yandex\.ru\/metrika|mc\.webvisor/;
const SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/';
const sitemap = fs.readFileSync(path.join(ROOT, 'server/sitemap.xml'), 'utf8');
let PAGES = [...sitemap.matchAll(/<loc>([^<]*)<\/loc>/g)].map((m) => '/' + m[1].slice(SITE.length));
if (ONLY.length) PAGES = ONLY;
const VP = [['компьютер 1440×900', 'desktop', 1440, 900, false], ['телефон 390×844', 'mobile', 390, 844, true]];
const HIDE = '.hdr,.fab,.mbar,.progress,.cursor,.skip,.intro{visibility:hidden!important}';

const route = async (ctx) => {
  await ctx.route('**/*', (r) => {
    const u = r.request().url();
    if (BLOCK.test(u)) return r.abort();
    if (PKG && u.startsWith(BASE + '/')) {
      const p = decodeURI(u.slice(BASE.length + 1).split('?')[0].split('#')[0]);
      if ((p === '' || p.endsWith('/')) && fs.existsSync(`${PKG}/${p}index.php`))
        return r.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: fs.readFileSync(`${PKG}/${p}index.php`) });
    }
    return r.continue();
  });
};
const open = async (page, url) => {
  for (let k = 0; ; k++) {
    try { return await page.goto(url, { waitUntil: 'load', timeout: 90000 }); }
    catch (e) { if (k >= 3) throw e; await page.waitForTimeout(3000); }
  }
};
const state = (page) => page.evaluate(() => [...document.querySelectorAll('.qa')].map((q) => {
  const b = q.querySelector('button'), a = q.querySelector('.ans');
  return { open: q.classList.contains('open'), exp: b ? b.getAttribute('aria-expanded') : null,
    h: a ? Math.round(a.getBoundingClientRect().height) : 0 };
}));

if (SHOTS) fs.mkdirSync(SHOTS, { recursive: true });
const browser = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
let bad = 0, checked = 0;
for (const [vn, vk, w, h, mob] of VP) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob, deviceScaleFactor: SHOTS ? 2 : 1,
    userAgent: mob ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' : undefined });
  await ctx.addInitScript(() => { try { sessionStorage.setItem('pc-intro', '1'); } catch (e) {} });
  await route(ctx);
  for (const p of PAGES) {
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', (e) => errs.push(String(e).slice(0, 160)));
    let res;
    for (let k = 0; k < 3; k++) {
      res = await open(page, BASE + p);
      if (!res || res.status() === 404) break;
      await page.waitForFunction(() => !document.querySelector('.qa') || document.querySelector('.qa.open'), null, { timeout: 15000 }).catch(() => {});
      await page.waitForTimeout(1200);
      // Timeweb из облака иногда отвечает ложным 502 на style.css — страница без стилей; такую загрузку повторяем
      const styled = await page.evaluate(() => { const a = document.querySelector('.qa .ans'); return !a || getComputedStyle(a).display === 'grid'; });
      if (styled) break;
      console.log(`${vn}  ${p}  — стили не загрузились, повтор`);
    }
    if (!res || res.status() === 404) { console.log(`${vn}  ${p}  — нет на сайте (${res ? res.status() : '?'}), пропуск`); await page.close(); continue; }
    let s = await state(page);
    if (!s.length) { console.log(`${vn}  ${p}  — вопросов нет`); await page.close(); continue; }
    checked++;
    const why = [];
    if (!(s[0].open && s[0].exp === 'true' && s[0].h > 20)) why.push(`первый вопрос не развёрнут (${JSON.stringify(s[0])})`);
    const extra = s.map((x, i) => [x, i + 1]).filter(([x, i]) => i > 1 && (x.open || x.exp !== 'false' || x.h > 1)).map(([, i]) => i);
    if (extra.length) why.push(`развёрнуты и другие вопросы: ${extra.join(', ')} из ${s.length}`);
    if (s.length > 1) {
      const b2 = page.locator('.qa button').nth(1);
      await b2.scrollIntoViewIfNeeded();
      await page.waitForTimeout(400);
      if (mob) await b2.tap(); else await b2.click();
      await page.waitForTimeout(900);
      let s2 = (await state(page))[1];
      if (!(s2.open && s2.exp === 'true' && s2.h > 20)) why.push(`второй вопрос не раскрывается щелчком (${JSON.stringify(s2)})`);
      if (mob) await b2.tap(); else await b2.click();
      await page.waitForTimeout(900);
      s2 = (await state(page))[1];
      if (s2.open || s2.exp !== 'false' || s2.h > 1) why.push(`второй вопрос не сворачивается (${JSON.stringify(s2)})`);
    }
    if (errs.length) why.push('ошибки JS: ' + errs.join(' | '));
    console.log(`${why.length ? 'НАРУШЕНИЕ' : 'OK'}  ${vn}  ${p}  вопросов ${s.length}` + (why.length ? '  — ' + why.join('; ') : ''));
    if (why.length) bad++;
    if (SHOTS && SHOT_PAGES.includes(p)) {
      // снимок в состоянии сразу после загрузки: перезагрузка, прокрутка к блоку, ждём появления блока
      await open(page, BASE + p);
      await page.waitForFunction(() => document.querySelector('.qa.open'), null, { timeout: 15000 }).catch(() => {});
      await page.addStyleTag({ content: HIDE });
      const sec = page.locator('#voprosy');
      await sec.scrollIntoViewIfNeeded();
      await page.waitForTimeout(2500);
      await sec.evaluate((el) => window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 20));
      await page.waitForTimeout(1500);
      const name = p.replace(/^\/|\/$/g, '').replace(/\//g, '__') || 'home';
      await sec.screenshot({ path: `${SHOTS}/${name}--${vk}.png` });
    }
    await page.close();
  }
  await ctx.close();
}
await browser.close();
console.log(`\nСтраниц с вопросами проверено (по экранам): ${checked}; нарушений: ${bad}`);
process.exit(bad ? 1 : 0);
