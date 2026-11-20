// Проверка «Состава заявки» и длинных блоков: node zv_test.mjs [all|flow|desk] (BASE=http://localhost:8080)
import { chromium, devices } from 'playwright';
const BASE = process.env.BASE || 'http://localhost:8080';
const mode = process.argv[2] || 'all';
const PAGES = ['/', '/dezinfektsiya/', '/deratizatsiya/', '/zashchita-ot-proniknoveniya-gryzunov/', '/dezinsektsiya/', '/deratizatsiya-i-dezinsektsiya/', '/dogovor-deratizatsiya-dezinsektsiya/',
  '/sanitarnyy-audit/', '/razrabotka-ppk/', '/laboratornye-issledovaniya/', '/ochistka-dezinfektsiya-ventilyatsii/', '/pishchevoe-proizvodstvo/', '/restorany-i-kafe/',
  '/magaziny-i-torgovye-seti/', '/gostinitsy/', '/farmatsevticheskie-proizvodstva/', '/sklady-i-logistika/', '/biznes-tsentry-torgovye-tsentry-predpriyatiya/', '/materialy/',
  '/materialy/programma-pest-kontrolya/', '/materialy/zhurnal-pest-kontrolya/', '/materialy/pest-menedzhment-ili-razovaya-obrabotka/', '/materialy/programma-proizvodstvennogo-kontrolya-haccp/',
  '/normativnaya-baza/', '/normativnaya-baza/proverochnye-listy/', '/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/', '/normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/',
  '/materialy/akt-deratizatsii-i-dezinsektsii/', '/materialy/skhema-tochek-pest-kontrolya/', '/dezinsektsiya/restorany-i-kafe/', '/deratizatsiya/restorany-i-kafe/',
  '/laboratornye-issledovaniya/analiz-smyvov/', '/laboratornye-issledovaniya/izmerenie-mikroklimata/', '/laboratornye-issledovaniya/zamer-osveshchennosti/',
  '/laboratornye-issledovaniya/analiz-vozdukha-rabochey-zony/', '/laboratornye-issledovaniya/analiz-pishchevykh-produktov/', '/laboratornye-issledovaniya/analiz-vody/',
  '/laboratornye-issledovaniya/kontrol-sterilizatorov/', '/materialy/kak-berut-smyvy/', '/materialy/zamer-osveshchennosti-i-mikroklimata/', '/materialy/kontrol-raboty-sterilizatorov/'];
const host = new URL(BASE).host;
async function ctxFor(browser, w, h) {
  const mob = w < 800;
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1, isMobile: mob, hasTouch: mob,
    userAgent: mob ? devices['iPhone 13'].userAgent : undefined, reducedMotion: 'reduce', locale: 'ru-RU' });
  await ctx.route(u => !u.host.endsWith(host.split(':')[0]) && u.host !== host, r => r.abort());
  // заявки никуда не уходят: send.php отвечает сам тест
  await ctx.route(u => u.pathname.endsWith('/send.php'), r => r.fulfill({ status: 200, contentType: 'application/json', body: '{"success":true}' }));
  return ctx;
}
const CAP = () => {
  window.__sent = [];
  const f0 = window.fetch;
  window.fetch = function (u, o) {
    if (String(u).indexOf('send.php') > -1) {
      const obj = {}; for (const [k, v] of o.body.entries()) obj[k] = v; window.__sent.push(obj);
      return new Promise(r => setTimeout(() => r(new Response('{"success":true}', { status: 200, headers: { 'Content-Type': 'application/json' } })), 200));
    }
    return f0.apply(this, arguments);
  };
};
async function go(ctx, p) {
  const page = await ctx.newPage();
  page.__err = [];
  page.on('pageerror', e => page.__err.push(String(e.message)));
  page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|ERR_FAILED|net::/.test(m.text())) page.__err.push(m.text()); });
  for (let t = 0; ; t++) {
    try { const r = await page.goto(BASE + p, { waitUntil: 'load', timeout: 60000 }); if (!r || r.status() < 500) break; } catch (e) { if (t > 6) throw e; }
    if (t > 6) break;
    await page.waitForTimeout(3000);
  }
  await page.waitForTimeout(1200);
  await page.evaluate(CAP);
  return page;
}
const browser = await chromium.launch();
let fails = 0;
const bad = (...a) => { fails++; console.log('НАРУШЕНИЕ', ...a); };

if (mode === 'all' || mode === 'pages') {
  for (const [w, h] of (process.env.WH ? JSON.parse(process.env.WH) : [[390, 844], [320, 568]])) {
    const ctx = await ctxFor(browser, w, h);
    for (const p of PAGES) {
      const page = await go(ctx, p);
      const r = await page.evaluate(async () => {
        for (let y = 0; y < document.documentElement.scrollHeight; y += 600) { scrollTo(0, y); await new Promise(r => setTimeout(r, 15)); }
        scrollTo(0, 0);
        const c = s => document.querySelectorAll(s).length;
        // элементы, выходящие за правый край экрана (кроме лент, у которых прокрутка своя)
        const over = [];
        document.querySelectorAll('main *, footer *').forEach(el => {
          if (el.closest('.mb-lane, .hm-track, .zv-chips, [aria-hidden=true], .sr-only, svg')) return;
          const r = el.getBoundingClientRect();
          if (!(r.width && r.right > innerWidth + 1) || getComputedStyle(el).position === 'fixed') return;
          for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
            const cs = getComputedStyle(a);
            if (cs.overflowX !== 'visible' && a.getBoundingClientRect().right <= innerWidth + 1) return;
          }
          over.push((el.className && String(el.className).slice(0, 40)) || el.tagName);
        });
        return { sw: document.documentElement.scrollWidth, iw: innerWidth, pcz: !!window.PCZ, lane: c('.mb-lane'), acc: c('.mb-acc'), more: c('.mb-more'), tbl: c('table.mb-tbl'), tacc: c('table.mb-tacc'), ft: c('.mb-ft'), h: document.documentElement.scrollHeight, over: over.slice(0, 5), on: over.length };
      });
      if (r.sw > r.iw) bad(w, p, 'прокрутка вбок', r.sw);
      if (!r.pcz) bad(w, p, 'нет PCZ');
      if (page.__err.length) bad(w, p, 'ошибки JS', page.__err.slice(0, 3));
      if (r.on) bad(w, p, 'за краем', r.on, r.over);
      console.log(w, p, 'лент', r.lane, 'раскр', r.acc, 'ещё', r.more, 'табл', r.tbl, '/', r.tacc, 'подвал', r.ft, 'экранов', (r.h / h).toFixed(1));
      await page.close();
    }
    await ctx.close();
  }
}

if (mode === 'all' || mode === 'flow') {
  const ctx = await ctxFor(browser, 390, 844);
  // 1. самопроверка ресторанов: отметки → состав, нижняя кнопка «Заявка 1»
  let page = await go(ctx, '/restorany-i-kafe/');
  await page.evaluate(() => { const l = document.querySelectorAll('#samoproverka .f-check-list input'); l[0].click(); l[2].click(); });
  let s = await page.evaluate(() => ({ n: PCZ.list().length, e: PCZ.list()[0] && PCZ.list()[0][1], bar: document.querySelector('#mbar .c2').textContent.trim() }));
  console.log('самопроверка →', JSON.stringify(s));
  if (s.n !== 1 || !/2 из 5/.test(s.e.s) || s.bar !== 'Заявка1') bad('самопроверка не в составе', s);
  // основная форма: состав над полями и в msg
  await page.evaluate(() => document.getElementById('zayavka').scrollIntoView());
  await page.waitForTimeout(400);
  const fbox = await page.evaluate(() => { const b = document.querySelector('#form .zv-f'); return b && !b.hidden ? b.textContent.replace(/\s+/g, ' ').slice(0, 160) : null; });
  console.log('форма: ', fbox);
  if (!fbox) bad('нет состава в основной форме');
  await page.fill('#f-name', 'Тест Тестов');
  await page.click('#phone'); await page.keyboard.type('9991234567');
  await page.click('#form button[type=submit]');
  await page.waitForTimeout(1500);
  s = await page.evaluate(() => ({ sent: window.__sent, left: PCZ.list().length, cls: document.getElementById('form').className }));
  console.log('основная форма msg:\n' + (s.sent[0] ? s.sent[0].msg : '—'));
  if (!s.sent[0] || !/Состав заявки \(1\)/.test(s.sent[0].msg) || !/Нет: /.test(s.sent[0].msg) || !/Страница: Пест-контроль ресторанов/.test(s.sent[0].msg)) bad('msg основной формы', s.sent[0]);
  if (s.left) bad('состав не очищен после отправки');
  await page.close();

  // 2. цена по площади → состав; шторка с другой страницы
  page = await go(ctx, '/dezinsektsiya/restorany-i-kafe/');
  await page.evaluate(() => { const a = document.getElementById('rk-area'); a.value = 240; a.dispatchEvent(new Event('input', { bubbles: true })); a.dispatchEvent(new Event('change', { bubbles: true })); });
  s = await page.evaluate(() => ({ e: PCZ.list().map(x => x[1].t + ' — ' + x[1].s), cur: [...document.querySelectorAll('.rk-ptbl tr.zv-cur')].map(t => t.textContent.trim().slice(0, 30)) }));
  console.log('площадь →', JSON.stringify(s));
  if (!s.e.length || !s.cur.length) bad('площадь', s);
  await page.evaluate(() => document.getElementById('rk-c-go').scrollIntoView({ block: 'center' }));
  await page.click('#rk-c-go');
  await page.waitForTimeout(600);
  s = await page.evaluate(() => { const d = document.getElementById('zv-dlg'); return { open: d && d.open, t: d && d.querySelector('#zv-t').textContent, list: d && d.querySelectorAll('#zv-list>li').length, type: d && d.querySelector('#zv-type').value, y: scrollY }; });
  console.log('шторка площади →', JSON.stringify(s));
  if (!s.open || s.list !== 1 || s.type !== 'Ресторан или кафе') bad('шторка площади', s);
  await page.screenshot({ path: '/home/user/work/zv/flow-area-sheet.png' });
  await page.keyboard.press('Escape');

  // 3. лабораторный расчёт → панель «Оформить» → шторка
  await page.goto(BASE + '/laboratornye-issledovaniya/', { waitUntil: 'load' }); await page.waitForTimeout(1200); await page.evaluate(CAP);
  await page.evaluate(() => { const b = document.querySelector('[data-add]'); b.scrollIntoView({ block: 'center' }); b.click(); });
  await page.waitForTimeout(500);
  s = await page.evaluate(() => ({ e: PCZ.list().map(x => x[0] + ':' + x[1].s), bar: document.querySelector('.zv-bar.show') ? document.querySelector('.zv-bar').textContent : null, lb: getComputedStyle(document.querySelector('.lb-bar') || document.body).display, chips: document.querySelectorAll('.zv-chips button').length }));
  console.log('лаборатория →', JSON.stringify(s));
  if (!s.bar || s.e.length !== 2) bad('лаборатория', s);
  await page.screenshot({ path: '/home/user/work/zv/flow-lab-bar.png' });
  await page.click('.zv-bar button');
  await page.waitForTimeout(600);
  s = await page.evaluate(() => { const d = document.getElementById('zv-dlg'); return { open: d && d.open, list: d && d.querySelectorAll('#zv-list>li').length }; });
  if (!s.open || s.list !== 2) bad('шторка лаборатории', s);
  await page.screenshot({ path: '/home/user/work/zv/flow-lab-sheet.png' });
  // отправка из шторки
  await page.fill('#zv-name', 'Иван');
  await page.click('#zv-phone'); await page.keyboard.type('9161112233');
  await page.selectOption('#zv-type', { index: 1 });
  await page.click('#zv-send');
  await page.waitForTimeout(1200);
  s = await page.evaluate(() => ({ sent: window.__sent, ok: !document.querySelector('#zv-dlg .chk-ok').hidden, left: PCZ.list().length }));
  console.log('шторка msg:\n' + (s.sent[0] ? s.sent[0].msg : '—'), '\nполя', s.sent[0] && [s.sent[0].name, s.sent[0].phone, s.sent[0].type]);
  if (!s.ok || !s.sent[0] || !/Состав заявки \(2\)/.test(s.sent[0].msg) || s.left) bad('отправка шторки', s);
  await page.screenshot({ path: '/home/user/work/zv/flow-sent.png' });
  await page.close();

  // 4. документы для Роспотребнадзора
  page = await go(ctx, '/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/');
  await page.evaluate(() => { const b = document.querySelectorAll('#konstruktor .dk-pick')[1]; b.scrollIntoView({ block: 'center' }); b.click(); });
  await page.waitForTimeout(500);
  await page.evaluate(() => { document.querySelectorAll('#konstruktor .dk-row').forEach((r, i) => { const b = r.querySelector('.dk-seg button[data-v=' + (i % 3 ? 'y' : 'n') + ']'); if (b && i < 12) b.click(); }); });
  await page.waitForTimeout(500);
  s = await page.evaluate(() => ({ e: PCZ.list().map(x => x[1].t + ' — ' + x[1].s + ' / ' + (x[1].l || []).length), h: document.getElementById('konstruktor').getBoundingClientRect().height, bar: document.querySelector('.zv-bar.show') ? document.querySelector('.zv-bar').textContent : null, fold: !!document.querySelector('.dk-picks.zv-fold') }));
  console.log('документы →', JSON.stringify(s));
  if (!s.e.length || !s.fold) bad('документы', s);
  await page.screenshot({ path: '/home/user/work/zv/flow-dok.png' });
  await page.evaluate(() => document.getElementById('dk-send').scrollIntoView({ block: 'center' }));
  await page.click('#dk-send');
  await page.waitForTimeout(600);
  s = await page.evaluate(() => { const d = document.getElementById('zv-dlg'); return { open: d && d.open, type: d && d.querySelector('#zv-type').value }; });
  console.log('шторка документов →', JSON.stringify(s));
  if (!s.open) bad('шторка документов', s);
  await page.close();

  // 5. главная: схема объекта
  page = await go(ctx, '/');
  await page.evaluate(() => { document.getElementById('hz-t-rest').click(); });
  await page.evaluate(() => document.querySelector('#shema a[href="#zayavka"]').scrollIntoView({ block: 'center' }));
  await page.waitForTimeout(300);
  await page.click('#shema a[href="#zayavka"]');
  await page.waitForTimeout(600);
  s = await page.evaluate(() => { const d = document.getElementById('zv-dlg'); return { open: d && d.open, type: d && d.querySelector('#zv-type').value, e: PCZ.list().map(x => x[1].t) }; });
  console.log('схема →', JSON.stringify(s));
  if (!s.open || s.type !== 'Ресторан или кафе') bad('схема', s);
  await page.screenshot({ path: '/home/user/work/zv/flow-shema.png' });
  await page.keyboard.press('Escape');
  // нижняя кнопка
  await page.evaluate(() => scrollTo(0, 3000));
  await page.waitForTimeout(500);
  await page.click('#mbar .c2');
  await page.waitForTimeout(500);
  s = await page.evaluate(() => ({ open: document.getElementById('zv-dlg').open, bar: document.querySelector('#mbar .c2').textContent.trim() }));
  if (!s.open) bad('нижняя кнопка', s);
  await page.close();

  // 6. самопроверка: окно показывает остальной состав, msg содержит его
  page = await go(ctx, '/deratizatsiya/');
  await page.evaluate(() => { PCZ.put('lab', { ico: 'lab', t: 'Лабораторный расчёт', s: '2 позиции, от 5 000 ₽', l: [{ t: 'Смывы: 5 × от 500 ₽' }] }, true); document.querySelector('#samoproverka .f-check-list input').click(); });
  await page.evaluate(() => document.querySelector('[data-chk-open]').scrollIntoView({ block: 'center' }));
  await page.click('[data-chk-open]');
  await page.waitForTimeout(600);
  s = await page.evaluate(() => ({ also: !document.querySelector('#chk-dlg .zv-also').hidden, n: document.querySelectorAll('#chk-dlg-also>li').length }));
  if (!s.also || s.n !== 1) bad('самопроверка: нет остального состава', s);
  await page.screenshot({ path: '/home/user/work/zv/flow-chk.png' });
  await page.fill('#chk-name', 'Пётр');
  await page.click('#chk-phone'); await page.keyboard.type('9031234567');
  await page.evaluate(() => { const t = document.getElementById('chk-type'); if (!t.value) { t.selectedIndex = 1; t.dispatchEvent(new Event('change')); } });
  await page.click('#chk-send');
  await page.waitForTimeout(1200);
  s = await page.evaluate(() => ({ sent: window.__sent, left: PCZ.list().length }));
  console.log('самопроверка msg:\n' + (s.sent[0] ? s.sent[0].msg : '—'));
  if (!s.sent[0] || !/Лабораторный расчёт/.test(s.sent[0].msg) || s.left) bad('самопроверка msg', s);
  if (page.__err.length) bad('ошибки', page.__err);
  await page.close();
  await ctx.close();
}

if (mode === 'all' || mode === 'desk') {
  const ctx = await ctxFor(browser, 1440, 900);
  for (const p of ['/', '/restorany-i-kafe/', '/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/', '/laboratornye-issledovaniya/', '/dezinsektsiya/restorany-i-kafe/', '/materialy/zhurnal-pest-kontrolya/']) {
    const page = await go(ctx, p);
    const r = await page.evaluate(() => ({ mb: document.querySelectorAll('[class*="mb-"]').length, sw: document.documentElement.scrollWidth, iw: innerWidth, bar: !!document.querySelector('.zv-bar.show') }));
    if (r.mb || r.sw > r.iw || r.bar || page.__err.length) bad('компьютер', p, r, page.__err);
    console.log('1440', p, JSON.stringify(r));
    await page.close();
  }
  // самопроверка на компьютере: состав в форме
  const page = await go(ctx, '/restorany-i-kafe/');
  await page.evaluate(() => document.querySelector('#samoproverka .f-check-list input').click());
  await page.click('#rk-c-go').catch(() => {});
  const r = await page.evaluate(() => ({ n: PCZ.list().length, box: !document.querySelector('#form .zv-f').hidden }));
  if (r.n !== 1 || !r.box) bad('компьютер: состав в форме', r);
  await page.evaluate(() => document.getElementById('zayavka').scrollIntoView());
  await page.waitForTimeout(800);
  await page.screenshot({ path: '/home/user/work/zv/desk-form.png' });
  await page.close();
  await ctx.close();
}
await browser.close();
console.log(fails ? 'НАРУШЕНИЙ: ' + fails : 'НАРУШЕНИЙ НЕТ');
