// Проверка 19.11.2026: самопроверка → заявка (tools/site/samoproverka_forma.py, tools/site/samoproverka-forma-2026-11-19.md).
// Запуск: BASE=http://127.0.0.1:8765 node tools/qa/samoproverka_forma_test.mjs   (по умолчанию — рабочий сайт)
// PKG=<папка pkg пакета> — страницы пакета (index.php) и samoproverka-forma.min.js подставляются вместо файлов сайта.
// На 13 страницах, экраны 320×568, 390×844, 768×1024, 1024×768, 1440×900:
//   1. кнопка (.f-check-f) — под пунктами (в одну колонку) или в левой колонке рядом со списком (в две колонки),
//      под ней строка «Откроется короткая форма…»; прокрутки вбок нет, текст кнопки не обрезан;
//   2. кнопка открывает окно, страница не прыгает; окно целиком на экране; на телефоне страница за шторкой
//      не затемняется (ЗАКОН ВЛАДЕЛЬЦА 17.11.2026), на компьютере — затемнение;
//   3. в окне — число отметок и список пропущенных пунктов (на странице пест-менеджмента — отмеченных признаков),
//      типы объекта — как в основной форме, с тем же выбором;
//   4. пустая форма показывает ошибки; маска телефона; после отправки — «Заявка отправлена», в заявке (msg) — отметки
//      и адрес страницы, цель Метрики audit и заявка UIS с названием формы — после ответа сервера;
//   5. закрытие кнопкой «Вернуться к странице», Esc и щелчком мимо окна; фокус возвращается на кнопку;
//   6. на телефоне нижняя панель «Позвонить / Обследование» за краем экрана, пока кнопка на экране;
//   7. ошибка сервера — сообщение в окне с телефоном, кнопка снова активна; ошибок JavaScript нет.
// Заявки никуда не уходят: /send.php перехватывается тестом. Метрика, UIS и Radist не загружаются.
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const BASE = (process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai').replace(/\/$/, '');
const PKG = process.env.PKG || '';
const OUT = process.env.OUT || '/tmp/samoproverka-shots';
const ONLY = process.env.ONLY || '';
fs.mkdirSync(OUT, { recursive: true });
const BLOCK = /mc\.yandex|uiscom|comagic|radist|yandex\.ru\/metrika|mc\.webvisor/;
const PAGES = ['materialy/zhurnal-pest-kontrolya', 'materialy/programma-pest-kontrolya',
  'materialy/pest-menedzhment-ili-razovaya-obrabotka', 'deratizatsiya', 'dezinsektsiya',
  'ochistka-dezinfektsiya-ventilyatsii', 'pishchevoe-proizvodstvo', 'restorany-i-kafe', 'magaziny-i-torgovye-seti',
  'sklady-i-logistika', 'farmatsevticheskie-proizvodstva', 'gostinitsy',
  'biznes-tsentry-torgovye-tsentry-predpriyatiya'].filter((p) => !ONLY || p.includes(ONLY));
const VPS = (process.env.VPS || '320x568,390x844,768x1024,1024x768,1440x900').split(',').map((v) => v.split('x').map(Number));
let bad = 0;
const fail = (m) => { bad++; console.log('НАРУШЕНИЕ', m); };
const norm = (s) => String(s || '').replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();

const openBtn = async (p, mobile) => {
  const bb = await p.locator('#samoproverka [data-chk-open]').boundingBox();
  if (mobile) await p.touchscreen.tap(bb.x + bb.width / 2, bb.y + bb.height / 2);
  else await p.mouse.click(bb.x + bb.width / 2, bb.y + bb.height / 2);
};
const browser = await chromium.launch();
for (const page of PAGES) {
  for (const [W, H] of VPS) {
    const tag = `${page} ${W}×${H}`;
    const mobile = W <= 760;
    const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1,
      hasTouch: mobile, isMobile: mobile });
    const posts = [];
    await ctx.route(BLOCK, (r) => r.abort());
    await ctx.route('**/send.php', async (r) => {
      posts.push(r.request().postData() || '');
      await r.fulfill({ status: 200, contentType: 'application/json', body: '{"success":true}' });
    });
    // Timeweb из облака иногда отвечает ложным 502 — файлы сайта запрашиваются с повтором
    await ctx.route((u) => u.hostname === new URL(BASE).hostname && !u.pathname.endsWith('/send.php'), async (r) => {
      for (let k = 0; k < 6; k++) {
        try {
          const res = await r.fetch();
          if (res.status() < 500 || k === 5) return r.fulfill({ response: res });
        } catch (e) { if (k === 5) return r.abort(); }
        await new Promise((ok) => setTimeout(ok, 1500 + 1000 * k));
      }
    });
    if (PKG) {
      await ctx.route((u) => u.pathname === '/' + page + '/' || u.pathname.endsWith('/samoproverka-forma.min.js'), async (r) => {
        const u = new URL(r.request().url());
        const f = u.pathname.endsWith('.js') ? path.join(PKG, 'samoproverka-forma.min.js') : path.join(PKG, page, 'index.php');
        await r.fulfill({ status: 200, contentType: f.endsWith('.js') ? 'application/javascript' : 'text/html; charset=utf-8',
          body: fs.readFileSync(f) });
      });
    }
    const p = await ctx.newPage();
    const errs = [];
    p.on('pageerror', (e) => errs.push(e.message));
    await p.addInitScript(() => {
      window.__ym = []; window.__uis = [];
      window.ym = function () { window.__ym.push([].slice.call(arguments)); };
      window.Comagic = { addOfflineRequest: function (o) { window.__uis.push(o); } };
      try { sessionStorage.setItem('pc-intro', '1'); } catch (e) { /* нет */ }
    });
    await p.goto(`${BASE}/${page}/`, { waitUntil: 'load', timeout: 60000 });
    await p.waitForTimeout(2600);
    await p.evaluate(() => document.querySelector('#samoproverka').scrollIntoView({ block: 'start' }));
    await p.waitForTimeout(900);
    const lay = await p.evaluate(() => {
      const q = (s) => document.querySelector(s);
      const r = (el) => { const b = el.getBoundingClientRect(); return { l: b.left, r: b.right, t: b.top, b: b.bottom, w: b.width }; };
      const btn = q('#samoproverka [data-chk-open]');
      return { list: r(q('#samoproverka .f-check-list')), act: r(q('#samoproverka .f-check-f')), btn: r(btn),
        btnClip: (() => { const t = [...btn.querySelectorAll('.btn-t')].find((x) => x.getClientRects().length) || btn, a = t.getBoundingClientRect(), o = btn.getBoundingClientRect(); return t.scrollWidth > t.clientWidth + 1 || a.left < o.left - 1 || a.right > o.right + 1; })(), sw: document.scrollingElement.scrollWidth, iw: innerWidth,
        n: document.querySelectorAll('#samoproverka .f-check-list input').length, hint: !!q('#samoproverka .f-check-f .f-check-tip') };
    });
    const twoCol = lay.list.l > lay.act.r - 1;
    if (twoCol) {
      if (lay.act.t > lay.list.b) fail(`${tag}: в две колонки результат ниже списка`);
    } else if (lay.act.t < lay.list.b - 1) fail(`${tag}: в одну колонку результат не под списком`);
    if (mobile && twoCol) fail(`${tag}: на телефоне две колонки`);
    if (lay.sw > lay.iw + 1) fail(`${tag}: прокрутка вбок ${lay.sw} > ${lay.iw}`);
    if (lay.btnClip) fail(`${tag}: текст кнопки обрезан`);
    if (!lay.hint) fail(`${tag}: нет строки «Откроется короткая форма…»`);
    // отметить 1-й и 3-й пункты
    for (const i of [0, 2]) await p.locator('#samoproverka .f-check-list label').nth(i).click();
    // кнопка — в середине экрана, как у человека, который только что отметил пункты
    await p.evaluate(() => { const r = document.querySelector('#samoproverka [data-chk-open]').getBoundingClientRect(); scrollBy(0, r.top - innerHeight / 2); });
    await p.waitForTimeout(900);
    if (mobile) {
      const off = await p.evaluate(() => { const m = document.getElementById('mbar'); return !m || m.getBoundingClientRect().top >= innerHeight - 1; });
      if (!off) fail(`${tag}: нижняя панель не спряталась у кнопки`);
    }
    await p.screenshot({ path: `${OUT}/${page.replace(/\//g, '_')}_${W}_block.png` });
    const y0 = await p.evaluate(() => scrollY);
    await openBtn(p, mobile);
    await p.waitForTimeout(700);
    const dl = await p.evaluate(() => {
      const dlg = document.getElementById('chk-dlg'), box = dlg && dlg.querySelector('.chk-box');
      if (!dlg) return null;
      const b = box.getBoundingClientRect(), bd = getComputedStyle(dlg, '::backdrop');
      const mt = document.getElementById('f-type'), ct = document.getElementById('chk-type');
      return { open: dlg.open, y: scrollY, t: b.top, b: b.bottom, l: b.left, r: b.right, ih: innerHeight, iw: innerWidth,
        bg: bd.backgroundColor, bf: bd.backdropFilter || bd.webkitBackdropFilter || 'none',
        n: dlg.querySelector('#chk-dlg-n').textContent, of: dlg.querySelector('#chk-dlg-of').textContent,
        miss: dlg.querySelectorAll('#chk-dlg-miss li').length, missT: dlg.querySelector('#chk-dlg-miss-t').textContent,
        opts: ct.options.length, mopts: mt.options.length, tv: ct.value, mv: mt.value,
        legal: !!dlg.querySelector('.legal a[href*="soglasie"]'), title: dlg.querySelector('#chk-dlg-t').textContent,
        risk: document.getElementById('samoproverka').getAttribute('data-chk-mode') === 'risk',
        sw: document.scrollingElement.scrollWidth };
    });
    if (!dl || !dl.open) { fail(`${tag}: окно не открылось`); await ctx.close(); continue; }
    if (Math.abs(dl.y - y0) > 2) fail(`${tag}: страница прыгнула ${y0} → ${dl.y}`);
    if (dl.t < -1 || dl.l < -1 || dl.r > dl.iw + 1 || dl.b > dl.ih + 1) fail(`${tag}: окно не целиком на экране ${JSON.stringify([dl.t, dl.b, dl.l, dl.r])}`);
    const dim = !/rgba\(0, 0, 0, 0\)|transparent/.test(dl.bg) || dl.bf !== 'none';
    if (mobile && dim) fail(`${tag}: на телефоне страница за шторкой затемнена (${dl.bg}, ${dl.bf})`);
    if (!mobile && !dim) fail(`${tag}: на компьютере нет затемнения`);
    if (dl.n !== '2' || +dl.of !== lay.n) fail(`${tag}: в окне ${dl.n} из ${dl.of}, ожидалось 2 из ${lay.n}`);
    const wantMiss = dl.risk ? 2 : lay.n - 2;
    if (dl.miss !== wantMiss) fail(`${tag}: в списке окна ${dl.miss}, ожидалось ${wantMiss}`);
    if (dl.opts !== dl.mopts || dl.tv !== dl.mv) fail(`${tag}: типы объекта не как в основной форме`);
    if (!dl.legal) fail(`${tag}: нет строки о согласии`);
    if (dl.sw > dl.iw + 1) fail(`${tag}: прокрутка вбок при открытом окне`);
    await p.screenshot({ path: `${OUT}/${page.replace(/\//g, '_')}_${W}_dialog.png` });
    // пустая форма
    await p.locator('#chk-send').click();
    await p.waitForTimeout(300);
    const errsN = await p.evaluate(() => document.querySelectorAll('#chk-dlg .field.err').length);
    if (errsN < 2) fail(`${tag}: ошибок пустой формы ${errsN}`);
    await p.locator('#chk-name').fill('Тест Самопроверки');
    await p.locator('#chk-phone').click();
    await p.locator('#chk-phone').pressSequentially('9161234567');
    const phv = await p.locator('#chk-phone').inputValue();
    if (phv !== '+7 (916) 123-45-67') fail(`${tag}: маска телефона «${phv}»`);
    if (!(await p.locator('#chk-type').inputValue())) await p.locator('#chk-type').selectOption({ index: 1 });
    // первая отправка — ошибка сервера
    if (W === 390 || W === 1440) {
      await p.evaluate(() => { window.__fetch = window.fetch; window.fetch = () => Promise.resolve(new Response('{"success":false,"message":"Проверьте номер телефона."}', { status: 422, headers: { 'Content-Type': 'application/json' } })); });
      await p.locator('#chk-send').click();
      await p.waitForTimeout(500);
      const er = await p.evaluate(() => ({ shown: !document.getElementById('chk-err').hidden,
        tel: !!document.querySelector('#chk-err a[href="tel:+74951043570"]'), dis: document.getElementById('chk-send').disabled,
        t: document.getElementById('chk-err').textContent, goals: window.__ym.filter((x) => x[1] === 'reachGoal').length }));
      if (!er.shown || !er.tel || er.dis || er.goals) fail(`${tag}: ошибка сервера показана неверно ${JSON.stringify(er)}`);
      await p.evaluate(() => { window.fetch = window.__fetch; });
    }
    await p.locator('#chk-send').click();
    await p.waitForTimeout(1300);
    const ok = await p.evaluate(() => ({ ok: !document.querySelector('#chk-dlg .chk-ok').hidden,
      msg: document.querySelector('#chk-form [name=msg]').value, ym: window.__ym, uis: window.__uis }));
    if (!ok.ok) fail(`${tag}: нет «Заявка отправлена»`);
    const want = dl.risk ? 'Отмечено признаков риска: 2 из ' : 'Отмечено: 2 из ';
    if (!ok.msg.includes(want + lay.n) || !ok.msg.includes('Страница: ') || !ok.msg.startsWith('Заявка из самопроверки «'))
      fail(`${tag}: текст заявки: ${ok.msg}`);
    const viaServer = posts.length > 0;
    if (viaServer) {
      const body = posts[posts.length - 1];
      if (!body.includes('Тест Самопроверки') || !body.includes('+7 (916) 123-45-67')) fail(`${tag}: в запросе нет имени или телефона`);
    }
    if (!ok.ym.some((a) => a[0] === 113675622 && a[1] === 'reachGoal' && a[2] === 'audit')) fail(`${tag}: нет цели audit`);
    if (!ok.uis.some((o) => /^Самопроверка: /.test(o.form_name) && o.message === ok.msg)) fail(`${tag}: нет заявки UIS`);
    if (W === 390) console.log(`--- ${page}: ${viaServer ? 'запрос к send.php' : 'превью без запроса'}\n${ok.msg}\n`);
    await p.screenshot({ path: `${OUT}/${page.replace(/\//g, '_')}_${W}_ok.png` });
    await p.locator('#chk-dlg .chk-back').click();
    await p.waitForTimeout(400);
    const cl = await p.evaluate(() => ({ open: document.getElementById('chk-dlg').open,
      foc: document.activeElement && document.activeElement.hasAttribute('data-chk-open'),
      lock: document.documentElement.classList.contains('chk-lock') }));
    if (cl.open || !cl.foc || cl.lock) fail(`${tag}: закрытие после отправки ${JSON.stringify(cl)}`);
    // повторное открытие: пустая форма; Esc
    await openBtn(p, mobile);
    await p.waitForTimeout(500);
    const re = await p.evaluate(() => ({ name: document.getElementById('chk-name').value,
      ok: document.querySelector('#chk-dlg .chk-ok').hidden }));
    if (re.name || !re.ok) fail(`${tag}: повторное окно не пустое`);
    await p.keyboard.press('Escape');
    await p.waitForTimeout(400);
    if (await p.evaluate(() => document.getElementById('chk-dlg').open)) fail(`${tag}: Esc не закрыл окно`);
    // щелчок мимо окна
    await openBtn(p, mobile);
    await p.waitForTimeout(500);
    const bx = await p.evaluate(() => { const b = document.querySelector('#chk-dlg .chk-box').getBoundingClientRect(); return { t: b.top, l: b.left }; });
    if (bx.t > 20) await p.mouse.click(Math.max(5, bx.l + 10), Math.max(5, bx.t / 2));
    else await p.mouse.click(5, 5);
    await p.waitForTimeout(400);
    if (await p.evaluate(() => document.getElementById('chk-dlg').open)) fail(`${tag}: щелчок мимо окна не закрыл его`);
    const y1 = await p.evaluate(() => scrollY);
    if (Math.abs(y1 - y0) > 2) fail(`${tag}: после закрытия страница сдвинулась ${y0} → ${y1}`);
    if (errs.length) fail(`${tag}: ошибки JavaScript: ${errs.join(' | ')}`);
    await ctx.close();
  }
  console.log('OK', page);
}
await browser.close();
console.log(bad ? `Нарушений: ${bad}` : 'Нарушений нет');
process.exit(bad ? 1 : 0);
