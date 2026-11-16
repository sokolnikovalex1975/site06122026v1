// Проверка 17.11.2026: вид объекта без звёздочки в заявках с отраслевых страниц (гостиницы, магазины, пищевое производство,
// склады, фармпроизводства) и, для сравнения, с трёх страниц ресторанов (правка 16.11.2026).
// Запуск: node tools/qa/zvezdochka_test.mjs   (по умолчанию — рабочий сайт)
// PKG=<папка pkg пакета> — страницы пакета (index.php) подставляются вместо страниц сайта (проверка до выкладки).
// Для каждой страницы на компьютере 1440×900 и телефоне 390×844:
//   1. пункт по умолчанию: первая строка заявки — «Вид объекта: <подпись без звёздочки>», такая строка одна, звёздочек нет,
//      строки страницы («Страница: …») на месте, тип объекта для send.php — значение пункта;
//   2. другой пункт: если подпись равна значению — строки «Вид объекта» нет; если отличается — она одна, с подписью пункта;
//   3. ошибок JavaScript нет.
// Запрос к /send.php перехватывается в браузере и на сервер не уходит (заявка не создаётся); Метрика, UIS и Radist
// не загружаются. Итог — число нарушений; код выхода 1, если они есть.
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const BASE = (process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai').replace(/\/$/, '');
const PKG = process.env.PKG || '';
const BLOCK = /mc\.yandex|uiscom|comagic|radist|yandex\.ru\/metrika|mc\.webvisor/;
const PAGES = [
  // страница, подпись по умолчанию без звёздочки, значение, другой пункт (подпись без неразрывных пробелов; выбирается по
  // значению из OTHER_VALUE или по самой подписи), ждём ли для него «Вид объекта»
  ['/gostinitsy/', 'Гостиница', 'Гостиница', 'Другое', false],
  ['/magaziny-i-torgovye-seti/', 'Магазин или торговая сеть', 'Магазин или торговая сеть', 'Другое', false],
  ['/pishchevoe-proizvodstvo/', 'Пищевое производство', 'Пищевое производство', 'Другое', false],
  ['/sklady-i-logistika/', 'Склад, логистика', 'Склад, логистика', 'Другое', false],
  ['/farmatsevticheskie-proizvodstva/', 'Фармпроизводство', 'Фармацевтическое производство', 'Склад или дистрибьютор лекарств', true],
  ['/restorany-i-kafe/', 'Ресторан или кафе', 'Ресторан или кафе', 'Склад, логистика', false],
  ['/dezinsektsiya/restorany-i-kafe/', 'Ресторан или кафе', 'Ресторан или кафе', 'Склад, логистика', false],
  ['/deratizatsiya/restorany-i-kafe/', 'Ресторан или кафе', 'Ресторан или кафе', 'Склад, логистика', false],
];
const OTHER_VALUE = { 'Склад или дистрибьютор лекарств': 'Склад, логистика' };
const VPS = [['компьютер 1440×900', 1440, 900, false], ['телефон 390×844', 390, 844, true]];
let bad = 0;
const fail = (m) => { bad++; console.log('НАРУШЕНИЕ', m); };

const browser = await chromium.launch();
for (const [pg, label, value, other, otherLine] of PAGES) {
  const local = PKG && fs.existsSync(path.join(PKG, pg.replace(/^\//, ''), 'index.php'));
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
      if (local && r.request().resourceType() === 'document' && new URL(u).pathname === pg) {
        return r.fulfill({ status: 200, contentType: 'text/html; charset=utf-8',
          body: fs.readFileSync(path.join(PKG, pg.replace(/^\//, ''), 'index.php')) });
      }
      return r.continue();
    });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    const where = `${pg} ${vpName}${local ? ' (пакет)' : ''}`;
    const out = [];
    for (const choice of [null, other]) {
      let ok = false;
      for (let k = 0; k < 5 && !ok; k++) {  // Timeweb из облака иногда отвечает ложным 502
        const res = await page.goto(BASE + pg + '?qa=zvezdochka', { waitUntil: 'load', timeout: 60000 }).catch(() => null);
        ok = !!res && res.status() === 200;
        if (!ok) await page.waitForTimeout(2000 + 2000 * k);
      }
      if (!ok) { fail(`${where}: страница не открылась`); break; }
      await page.waitForTimeout(300);
      posted = null;
      if (choice) await page.locator('#f-type').selectOption({ value: OTHER_VALUE[choice] || choice });
      await page.locator('#form').scrollIntoViewIfNeeded();
      await page.fill('#f-name', 'ТЕСТ — не звонить');
      await page.fill('#phone', '9990000000');
      await page.locator('#submitBtn').click();
      await page.waitForTimeout(2500);
      if (!posted) { fail(`${where}: форма не отправила запрос к send.php (${choice || 'по умолчанию'})`); continue; }
      const field = (n) => { const m = posted.match(new RegExp('name="' + n + '"\\r?\\n\\r?\\n([\\s\\S]*?)\\r?\\n--')); return m ? m[1] : null; };
      const msg = field('msg') || '', type = field('type');
      const lines = msg.split(/\r?\n/), vid = lines.filter((s) => s.startsWith('Вид объекта:'));
      if (msg.includes('*')) fail(`${where}: звёздочка в заявке: ${JSON.stringify(msg)}`);
      if (!lines.some((s) => /^Страница: /.test(s))) fail(`${where}: нет строки «Страница» (${choice || 'по умолчанию'})`);
      if (!choice) {
        if (lines[0] !== 'Вид объекта: ' + label || vid.length !== 1) fail(`${where}: заявка ${JSON.stringify(lines)}`);
        if (type !== value) fail(`${where}: тип объекта ${JSON.stringify(type)}`);
      } else if (otherLine) {
        if (lines[0] !== 'Вид объекта: ' + other || vid.length !== 1) fail(`${where}: «${other}»: ${JSON.stringify(lines)}`);
      } else if (vid.length) fail(`${where}: «Вид объекта» при пункте «${other}»`);
      out.push(`${choice ? '«' + choice + '»' : 'по умолчанию'}: ${JSON.stringify(lines[0])}, type: ${type}`);
    }
    if (errors.length) fail(`${where}: ошибки JS ${errors.join('; ').slice(0, 200)}`);
    console.log(`${where}: ${out.join(' | ')}`);
    await ctx.close();
  }
}
await browser.close();
console.log(bad ? `Нарушений: ${bad}` : 'Нарушений нет');
process.exit(bad ? 1 : 0);
