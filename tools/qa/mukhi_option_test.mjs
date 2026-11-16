// Проверка 15.11.2026: пункт «Мухи или мелкие мушки» в формах заявки общепита (/restorany-i-kafe/, /dezinsektsiya/restorany-i-kafe/).
// Запуск: node tools/qa/mukhi_option_test.mjs   (по умолчанию — рабочий сайт; BASE=http://127.0.0.1:8090 — локальная копия)
// SHOTS=<папка> — снимки формы с выбранным пунктом.
// На компьютере 1440×900 и телефонах 390×844 и 360×740:
//   1. в поле ровно согласованные пункты, «Мухи или мелкие мушки» есть, «дрозофил» в пунктах нет;
//   2. выбранный пункт целиком помещается в закрытом поле (ширина текста меньше ширины поля без отступов и стрелки);
//   3. при отправке в заявку (поле msg) уходит строка «Задача: …» / «Что беспокоит: Мухи или мелкие мушки».
// Запрос к /send.php перехватывается в браузере и на сервер не уходит (заявка не создаётся); Метрика, UIS и Radist
// не загружаются. Итог — число нарушений; код выхода 1, если они есть.
import { chromium } from 'playwright';
import fs from 'fs';

const BASE = (process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai').replace(/\/$/, '');
const SHOTS = process.env.SHOTS || '';
const BLOCK = /mc\.yandex|uiscom|comagic|radist|yandex\.ru\/metrika|mc\.webvisor/;
const NEW = 'Мухи или мелкие мушки';
const PAGES = [
  ['/restorany-i-kafe/', 'Задача', ['Задача', 'Договор на регулярное обслуживание', 'Срочно: тараканы', 'Срочно: мыши или крысы',
    NEW, 'Подготовка к проверке', 'Открытие нового заведения']],
  ['/dezinsektsiya/restorany-i-kafe/', 'Что беспокоит', ['Что беспокоит', 'Тараканы', NEW, 'Муравьи', 'Моль или жуки на складе',
    'Нужен договор и журнал к проверке']],
];
const VP = [['компьютер 1440×900', 1440, 900, false], ['телефон 390×844', 390, 844, true], ['телефон 360×740', 360, 740, true]];

let bad = 0;
const fail = (m) => { bad++; console.log('НАРУШЕНИЕ', m); };
const browser = await chromium.launch();
for (const [path, label, want] of PAGES) {
  for (const [vpName, w, h, mobile] of VP) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, isMobile: mobile, hasTouch: mobile, deviceScaleFactor: mobile ? 2 : 1 });
    let posted = null;
    await ctx.route('**/*', (r) => {
      const u = r.request().url();
      if (BLOCK.test(u)) return r.abort();
      if (/\/send\.php(\?|$)/.test(u)) {
        posted = r.request().postData() || '';
        return r.fulfill({ status: 200, contentType: 'application/json; charset=utf-8', body: '{"success":true,"message":"test"}' });
      }
      return r.continue();
    });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    let ok = false;
    for (let k = 0; k < 5 && !ok; k++) {  // Timeweb из облака иногда отвечает ложным 502
      const res = await page.goto(BASE + path + '?qa=mukhi', { waitUntil: 'load', timeout: 60000 }).catch((e) => null);
      ok = !!res && res.status() === 200;
      if (!ok) await page.waitForTimeout(2000 + 2000 * k);
    }
    if (!ok) { fail(`${path} ${vpName}: страница не открылась`); await ctx.close(); continue; }
    const sel = page.locator('#f-task');
    const opts = await sel.locator('option').allTextContents();
    const norm = opts.map((t) => t.replace(/\u00a0/g, ' ').trim());
    if (JSON.stringify(norm) !== JSON.stringify(want)) fail(`${path} ${vpName}: пункты ${JSON.stringify(norm)}`);
    if (norm.some((t) => /дрозофил/i.test(t))) fail(`${path} ${vpName}: в пунктах осталось «дрозофилы»`);
    const aria = await page.locator('label[for="f-task"]').textContent();
    if ((aria || '').trim() !== label) fail(`${path} ${vpName}: подпись поля «${aria}»`);
    await sel.scrollIntoViewIfNeeded();
    await sel.selectOption({ label: opts[norm.indexOf(NEW)] });
    const fit = await sel.evaluate((el) => {
      const cs = getComputedStyle(el);
      const c = document.createElement('canvas').getContext('2d');
      c.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
      const text = el.options[el.selectedIndex].text;
      const textW = c.measureText(text).width;
      const boxW = el.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      return { text, textW: Math.round(textW), boxW: Math.round(boxW), selW: el.clientWidth, font: cs.fontSize };
    });
    if (!(fit.textW <= fit.boxW)) fail(`${path} ${vpName}: пункт не помещается — текст ${fit.textW} px, поле ${fit.boxW} px`);
    if (SHOTS) {
      fs.mkdirSync(SHOTS, { recursive: true });
      const box = page.locator('#form');
      await box.screenshot({ path: `${SHOTS}/${path.replace(/\//g, '_').replace(/^_|_$/g, '')}-${w}.png` }).catch(() => {});
    }
    // отправка: имя, телефон и пункт; запрос к send.php перехвачен в браузере
    await page.fill('#f-name', 'ТЕСТ — не звонить');
    await page.fill('#phone', '9990000000');
    await page.locator('#submitBtn').click();
    await page.waitForTimeout(2500);
    const want_row = `${label}: ${NEW}`;
    let msg = '';
    if (posted) {
      const m = posted.match(/name="msg"\r?\n\r?\n([\s\S]*?)\r?\n--/);
      msg = m ? m[1] : '';
    }
    if (!posted) fail(`${path} ${vpName}: форма не отправила запрос к send.php`);
    else if (!msg.split(/\r?\n/).map((s) => s.replace(/\u00a0/g, ' ')).includes(want_row)) fail(`${path} ${vpName}: в msg нет «${want_row}»: ${JSON.stringify(msg)}`);
    if (errors.length) fail(`${path} ${vpName}: ошибки JS ${errors.join('; ').slice(0, 200)}`);
    console.log(`${path} ${vpName}: пунктов ${norm.length}, «${fit.text.replace(/\u00a0/g, ' ')}» ${fit.textW}/${fit.boxW} px (шрифт ${fit.font}), msg: ${JSON.stringify(msg.split(/\r?\n/).filter((s) => s.startsWith(label + ':'))[0] || '')}`);
    await ctx.close();
  }
}
await browser.close();
console.log(bad ? `Нарушений: ${bad}` : 'Нарушений нет');
process.exit(bad ? 1 : 0);
