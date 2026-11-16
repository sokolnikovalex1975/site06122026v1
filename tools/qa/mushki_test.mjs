// Проверка 16.11.2026: «Мухи и мелкие мушки» вместо «Мухи и дрозофилы» и вид объекта без звёздочки в заявках со страниц ресторанов.
// Запуск: node tools/qa/mushki_test.mjs   (по умолчанию — рабочий сайт)
// PKG=<папка pkg пакета> — страницы пакета (index.php) подставляются вместо страниц сайта (проверка до выкладки).
// SHOTS=<папка> — снимки карточки «Мухи и мелкие мушки» и формы.
// Для 6 страниц на компьютере 1440×900 и телефонах 390×844, 360×740, 320×640:
//   1. в тексте страницы нет «Мухи и дрозофилы» / «мухи и дрозофилы», у фото нет такого alt;
//   2. заголовок «Мухи и мелкие мушки» (где он есть) виден, помещается в карточке, прокрутки вбок нет;
//   3. страницы ресторанов: в заявку уходит «Вид объекта: Ресторан или кафе» без звёздочки, тип объекта — «Ресторан или кафе»;
//      при другом пункте («Склад, логистика») строки «Вид объекта» нет, как и раньше;
//   4. ошибок JavaScript нет.
// Запрос к /send.php перехватывается в браузере и на сервер не уходит (заявка не создаётся); Метрика, UIS и Radist
// не загружаются. Итог — число нарушений; код выхода 1, если они есть.
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const BASE = (process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai').replace(/\/$/, '');
const PKG = process.env.PKG || '';
const SHOTS = process.env.SHOTS || '';
const BLOCK = /mc\.yandex|uiscom|comagic|radist|yandex\.ru\/metrika|mc\.webvisor/;
const PAGES = [
  { path: '/', heading: true },
  { path: '/restorany-i-kafe/', heading: true, form: true },
  { path: '/pishchevoe-proizvodstvo/', heading: true },
  { path: '/dezinsektsiya/', heading: true },
  { path: '/dezinsektsiya/restorany-i-kafe/', form: true },
  { path: '/deratizatsiya/restorany-i-kafe/', form: true },
];
const VPS = [['компьютер 1440×900', 1440, 900, false], ['телефон 390×844', 390, 844, true],
  ['телефон 360×740', 360, 740, true], ['телефон 320×640', 320, 640, true]];
const NEW = 'Мухи и мелкие мушки';
let bad = 0;
const fail = (m) => { bad++; console.log('НАРУШЕНИЕ', m); };

const browser = await chromium.launch();
for (const pg of PAGES) {
  for (const [vpName, w, h, mobile] of VPS) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, isMobile: mobile, hasTouch: mobile,
      deviceScaleFactor: mobile ? 2 : 1, reducedMotion: 'reduce' });
    let posted = null;
    await ctx.route('**/*', (r) => {
      const u = r.request().url();
      if (BLOCK.test(u)) return r.abort();
      if (/\/send\.php/.test(u)) {
        posted = r.request().postData() || '';
        return r.fulfill({ status: 200, contentType: 'application/json; charset=utf-8', body: '{"success":true,"message":"test"}' });
      }
      if (PKG && r.request().resourceType() === 'document' && new URL(u).pathname === pg.path) {
        const f = path.join(PKG, pg.path.replace(/^\//, ''), 'index.php');
        return r.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: fs.readFileSync(f) });
      }
      return r.continue();
    });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    let ok = false;
    for (let k = 0; k < 5 && !ok; k++) {  // Timeweb из облака иногда отвечает ложным 502
      const res = await page.goto(BASE + pg.path + '?qa=mushki', { waitUntil: 'load', timeout: 60000 }).catch(() => null);
      ok = !!res && res.status() === 200;
      if (!ok) await page.waitForTimeout(2000 + 2000 * k);
    }
    const where = `${pg.path} ${vpName}`;
    if (!ok) { fail(`${where}: страница не открылась`); await ctx.close(); continue; }
    await page.waitForTimeout(400);
    const info = await page.evaluate((NEW) => {
      const html = document.documentElement.outerHTML;
      const old = (html.match(/[Мм]ухи и(\s|&nbsp;|\u00a0)дрозофил/g) || []).length;
      const hs = [...document.querySelectorAll('h3')].filter((e) => e.textContent.replace(/\u00a0/g, ' ').trim() === NEW);
      const vw = document.documentElement.clientWidth;
      const r = hs.map((e) => {
        e.scrollIntoView({ block: 'center' });
        const card = e.closest('article, .card, .pest, li') || e.parentElement;
        const a = e.getBoundingClientRect(), c = card.getBoundingClientRect();
        const cs = getComputedStyle(e);
        return { w: Math.round(a.width), sw: e.scrollWidth, cw: e.clientWidth, lines: Math.round(a.height / (parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2)),
          inCard: a.left >= c.left - 1 && a.right <= c.right + 1, vis: a.width > 0 && a.height > 0 };
      });
      return { old, n: hs.length, r, hscroll: document.documentElement.scrollWidth > vw + 1 };
    }, NEW);
    if (info.old) fail(`${where}: «Мухи и дрозофилы» на странице — ${info.old}`);
    if (info.hscroll) fail(`${where}: прокрутка вбок`);
    if (pg.heading) {
      if (info.n !== 1) fail(`${where}: заголовков «${NEW}» — ${info.n}`);
      for (const x of info.r) {
        if (!x.vis) fail(`${where}: заголовок не виден`);
        if (!x.inCard || x.sw > x.cw + 1) fail(`${where}: заголовок выходит за карточку ${JSON.stringify(x)}`);
      }
    }
    if (SHOTS && info.n && (w === 1440 || w === 360)) {
      fs.mkdirSync(SHOTS, { recursive: true });
      const card = page.locator('h3', { hasText: NEW }).first().locator('xpath=ancestor::*[self::article or contains(@class,"card") or contains(@class,"pest")][1]');
      await card.scrollIntoViewIfNeeded().catch(() => {});
      await page.waitForTimeout(500);
      await card.screenshot({ path: `${SHOTS}/${pg.path.replace(/\//g, '_').replace(/^_|_$/g, '') || 'home'}-${w}.png` }).catch((e) => console.log('снимок:', String(e).slice(0, 80)));
    }
    let msgInfo = '';
    if (pg.form) {
      for (const choice of [null, 'Склад, логистика']) {
        posted = null;
        if (choice) {
          await page.reload({ waitUntil: 'load' }).catch(() => {});
          await page.waitForTimeout(300);
          await page.locator('#f-type').selectOption({ label: choice });
        }
        await page.locator('#form').scrollIntoViewIfNeeded();
        await page.fill('#f-name', 'ТЕСТ — не звонить');
        await page.fill('#phone', '9990000000');
        await page.locator('#submitBtn').click();
        await page.waitForTimeout(2500);
        if (!posted) { fail(`${where}: форма не отправила запрос к send.php (${choice || 'по умолчанию'})`); continue; }
        const field = (n) => { const m = posted.match(new RegExp('name="' + n + '"\\r?\\n\\r?\\n([\\s\\S]*?)\\r?\\n--')); return m ? m[1] : null; };
        const msg = field('msg') || '', type = field('type');
        const lines = msg.split(/\r?\n/);
        if (msg.includes('*')) fail(`${where}: звёздочка в заявке: ${JSON.stringify(msg)}`);
        if (!choice) {
          if (lines[0] !== 'Вид объекта: Ресторан или кафе') fail(`${where}: первая строка заявки ${JSON.stringify(lines[0])}`);
          if (lines.filter((s) => s.startsWith('Вид объекта:')).length !== 1) fail(`${where}: строк «Вид объекта» не одна`);
          if (type !== 'Ресторан или кафе') fail(`${where}: тип объекта ${JSON.stringify(type)}`);
          if (!lines.some((s) => s.startsWith('Страница: '))) fail(`${where}: нет строки «Страница»`);
          msgInfo = ` | msg: ${JSON.stringify(lines.join(' / '))}, type: ${type}`;
        } else {
          if (lines.some((s) => s.startsWith('Вид объекта:'))) fail(`${where}: «Вид объекта» при пункте «${choice}»`);
          if (type !== choice) fail(`${where}: тип объекта ${JSON.stringify(type)} при пункте «${choice}»`);
          msgInfo += ` | «${choice}»: ${JSON.stringify(lines[0])}, type: ${type}`;
        }
      }
      if (SHOTS && w === 360) {
        await page.reload({ waitUntil: 'load' }).catch(() => {});
        await page.locator('#form').scrollIntoViewIfNeeded();
        await page.waitForTimeout(600);
        await page.locator('#form').screenshot({ path: `${SHOTS}/${pg.path.replace(/\//g, '_').replace(/^_|_$/g, '')}-form-${w}.png` }).catch(() => {});
      }
    }
    if (errors.length) fail(`${where}: ошибки JS ${errors.join('; ').slice(0, 200)}`);
    console.log(`${where}: старых — ${info.old}, заголовок ${info.r.map((x) => x.w + ' px, строк ' + x.lines).join(', ') || '—'}${msgInfo}`);
    await ctx.close();
  }
}
await browser.close();
console.log(bad ? `Нарушений: ${bad}` : 'Нарушений нет');
process.exit(bad ? 1 : 0);
