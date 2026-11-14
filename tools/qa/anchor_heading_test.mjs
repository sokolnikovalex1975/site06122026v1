// Проверка 13.11.2026: переход к блоку по якорю — начало блока (подпись над заголовком) сразу под шапкой, шапка видна.
// Запуск: BASE=http://127.0.0.1:8090 node tools/qa/anchor_heading_test.mjs   (по умолчанию — рабочий сайт)
// PKG=<папка pkg пакета> — подставить страницы, app.min.js, style.css и legal.css пакета вместо файлов сайта.
// Ожидание: шапка видна, верх подписи над заголовком (у формы заявки — верх содержимого) ниже шапки на 20…32 px
// (min(32, max(20, 2,2 % ширины окна)), допуск 3 px). Было: шапка уезжала, подпись на 240–280 px от верха окна.
// 1. Щелчки на странице: меню шапки и выпадающие списки (компьютер), мобильное меню (телефон), подвал вверх по странице,
//    ссылка на форму. Во время прокрутки шапка не прячется; после первого колеса посетителя прячется как обычно.
// 2. Переход с другой страницы (/#podhod, /#tseny, /#etapy, /#vrediteli, /#voprosy): положение через 1, 2 и 3 с.
// 3. Без app.min.js (браузер сам, по style.css) — то же место, что со скриптом (нет скачка при запуске скриптов).
// 4. «Уменьшение движения» — сразу на место. 5. Политика: оглавление — заголовок раздела под шапкой (со скриптом и без).
// Счётчики не загружаются (запросы к Метрике, UIS и Radist обрываются). Итог — число нарушений; код выхода 1, если есть.
import { chromium } from 'playwright';
import fs from 'fs';

const BASE = (process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai').replace(/\/$/, '');
const PKG = process.env.PKG || '';
const BLOCK = /mc\.yandex|uiscom|comagic|radist|yandex\.ru\/metrika|mc\.webvisor/;
const VP = [['компьютер 1440×900', 1440, 900, false], ['телефон 390×844', 390, 844, true]];
const TOL = 3;
const ONLY = process.env.ONLY || ''; // часть адреса, текста ссылки или якоря — проверить только эти переходы
const CLICK = [
  // [страница, где ссылка: nav | dd | footer | cta, текст ссылки, якорь]
  ['/', 'nav', 'Цена', 'tseny'],
  ['/', 'nav', 'Метод IPM', 'podhod'],
  ['/', 'dd', 'Все отрасли', 'otrasli'],
  ['/', 'dd', 'Все услуги', 'vse-uslugi'],
  ['/', 'footer', 'Цена', 'tseny'],
  ['/dezinsektsiya/', 'nav', 'Цена', 'stoimost'],
  ['/laboratornye-issledovaniya/', 'nav', 'Цена', 'ceny'],
  ['/sanitarnyy-audit/', 'cta', '', 'zayavka'],
];
const LAND = [
  ['/dezinsektsiya/', 'nav', 'Метод IPM', 'podhod'],
  ['/privacy/', 'nav', 'Цена', 'tseny'],
  ['/deratizatsiya/', 'footer', 'Этапы работы', 'etapy'],
  ['/gostinitsy/', 'footer', 'Вредители', 'vrediteli'],
  ['/materialy/', 'footer', 'Вопросы', 'voprosy'],
];

const route = async (ctx, noJs) => {
  await ctx.route('**/*', (r) => {
    const u = r.request().url();
    if (BLOCK.test(u)) return r.abort();
    const path = u.startsWith(BASE + '/') ? decodeURI(u.slice(BASE.length + 1).split('?')[0].split('#')[0]) : null;
    if (noJs && path === 'app.min.js') return r.abort();
    if (PKG && path !== null) {
      if (['app.min.js', 'style.css', 'legal.css'].includes(path) && fs.existsSync(`${PKG}/${path}`)) return r.fulfill({ status: 200,
        body: fs.readFileSync(`${PKG}/${path}`), contentType: path.endsWith('.js') ? 'application/javascript; charset=utf-8' : 'text/css; charset=utf-8' });
      if ((path === '' || path.endsWith('/')) && fs.existsSync(`${PKG}/${path}index.php`))
        return r.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: fs.readFileSync(`${PKG}/${path}index.php`) });
    }
    return r.continue();
  });
};
const open = async (page, url) => {
  for (let k = 0; ; k++) {
    try { const res = await page.goto(url, { waitUntil: 'load', timeout: 90000 }); if (res && res.status() >= 500) throw new Error('HTTP ' + res.status()); return; }
    catch (e) { if (k >= 3) throw e; await page.waitForTimeout(3000); }
  }
};
// положение начала блока относительно низа шапки
const where = (page, id) => page.evaluate((id) => {
  const t = document.getElementById(id); if (!t) return null;
  const hdr = document.getElementById('hdr'), hr = hdr.getBoundingClientRect();
  const shown = !hdr.classList.contains('hide') && hr.bottom > 1;
  let top;
  if (t.classList.contains('cta')) top = Math.min(...[...t.querySelector('.wrap').children].map((c) => c.getBoundingClientRect().top));
  else if (t.classList.contains('l-sec')) top = t.querySelector('h2').getBoundingClientRect().top;
  else top = (t.querySelector('.eyebrow, h1, h2') || t).getBoundingClientRect().top;
  return { shown, gap: Math.round(top - hr.bottom), exp: Math.round(Math.min(32, Math.max(20, innerWidth * 0.022))), y: Math.round(scrollY),
    docW: document.documentElement.scrollWidth, iw: innerWidth };
}, id);
const okPos = (m) => m && m.shown && Math.abs(m.gap - m.exp) <= TOL && m.docW <= m.iw;
const fmt = (m) => m ? `${m.shown ? 'шапка видна' : 'ШАПКА СКРЫТА'}, под шапкой ${m.gap} px (нужно ${m.exp})` : 'блок не найден';

const tapOrClick = async (page, mob, a) => {
  const b = await a.boundingBox();
  if (!b) throw new Error('ссылка не видна');
  if (mob) await page.touchscreen.tap(b.x + b.width / 2, b.y + b.height / 2);
  else { await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2); await page.waitForTimeout(120); await page.mouse.click(b.x + b.width / 2, b.y + b.height / 2); }
};
const press = async (page, mob, kind, text) => {
  if (kind === 'footer') {
    const a = page.locator(`footer a:text-is("${text}")`).first();
    await a.evaluate((el) => window.scrollTo(0, el.getBoundingClientRect().top + scrollY - innerHeight / 2));
    await page.waitForTimeout(1500);
    return tapOrClick(page, mob, a);
  }
  if (kind === 'cta') { // видимая ссылка на форму: кнопка шапки или первого экрана, на телефоне — нижняя панель
    if (mob) { await page.evaluate(() => window.scrollTo(0, innerHeight * 1.2)); await page.waitForTimeout(1500); }
    const a = await page.evaluateHandle(() => [...document.querySelectorAll('a[href="#zayavka"]')].find((el) => {
      const r = el.getBoundingClientRect(), x = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
      return r.width && r.height && r.top >= 0 && r.bottom <= innerHeight && x && (x === el || el.contains(x));
    }) || null);
    if (!(await a.evaluate((x) => !!x))) throw new Error('нет видимой ссылки на форму');
    return tapOrClick(page, mob, a.asElement());
  }
  if (mob) {
    await page.locator('#burger').tap(); await page.waitForTimeout(900);
    const g = page.locator('.mm-group', { has: page.locator(`a:text-is("${text}")`) }).first();
    if (await g.count() && !(await g.evaluate((el) => el.classList.contains('open')))) { await g.locator('.mm-toggle').tap(); await page.waitForTimeout(500); }
    const a = page.locator(`#mmenu a:text-is("${text}")`).first();
    await a.scrollIntoViewIfNeeded(); await page.waitForTimeout(300);
    return tapOrClick(page, mob, a);
  }
  if (kind === 'dd') {
    const dd = page.locator('.nav-dd', { has: page.locator(`a:text-is("${text}")`) }).first();
    await dd.locator('.nav-dd-btn').hover(); await page.waitForTimeout(600);
    return tapOrClick(page, mob, dd.locator(`a:text-is("${text}")`).first());
  }
  return tapOrClick(page, mob, page.locator(`.nav > a:text-is("${text}")`).first());
};

const browser = await chromium.launch();
let bad = 0;
const lines = [];
const line = (ok, s) => { if (!ok) bad++; lines.push(`${ok ? 'OK ' : 'НЕТ'} ${s}`); };
for (const [vn, w, h, mob] of VP) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob, deviceScaleFactor: 1 });
  await ctx.addInitScript(() => { try { sessionStorage.setItem('pc-intro', '1'); } catch (e) {} });
  await route(ctx, false);
  // 1. щелчки на странице
  for (const [from, kind, text, id] of CLICK) {
    if (ONLY && !(from + text + id).includes(ONLY)) continue;
    const page = await ctx.newPage();
    const errs = []; page.on('pageerror', (e) => errs.push(String(e).slice(0, 160)));
    try {
      await open(page, BASE + from); await page.waitForTimeout(2000);
      await press(page, mob, kind, text);
      const during = [];
      for (const t of [300, 500]) { await page.waitForTimeout(t); during.push((await where(page, id)).shown); }
      await page.waitForTimeout(2000);
      const m = await where(page, id);
      let restored = 'не проверялось';
      if (!mob) { // первое колесо посетителя — шапка снова прячется при прокрутке вниз
        await page.mouse.move(w / 2, h / 2); await page.mouse.wheel(0, 500); await page.waitForTimeout(900);
        restored = (await where(page, id)).shown ? 'НЕ спряталась' : 'спряталась';
      }
      const ok = okPos(m) && during.every(Boolean) && (mob || restored === 'спряталась') && !errs.length && new URL(page.url()).pathname === from;
      line(ok, `${vn} ${from} ${kind} «${text || 'заявка'}» → #${id}: ${fmt(m)}; во время прокрутки шапка ${during.every(Boolean) ? 'видна' : 'ПРЯТАЛАСЬ'}` +
        `${mob ? '' : '; колесо вниз — шапка ' + restored}${errs.length ? '; JS: ' + errs.join(' | ') : ''}`);
    } catch (e) { line(false, `${vn} ${from} «${text}»: ${String(e).slice(0, 200)}`); }
    await page.close();
  }
  // 2. переход с другой страницы
  for (const [from, kind, text, id] of LAND) {
    if (ONLY && !(from + text + id).includes(ONLY)) continue;
    const page = await ctx.newPage();
    const errs = []; page.on('pageerror', (e) => errs.push(String(e).slice(0, 160)));
    try {
      await open(page, BASE + from); await page.waitForTimeout(1500);
      await Promise.all([page.waitForURL((u) => u.hash === '#' + id, { timeout: 60000 }), press(page, mob, kind, text)]);
      await page.waitForLoadState('load');
      const ms = [];
      for (const t of [1000, 1000, 1000]) { await page.waitForTimeout(t); ms.push(await where(page, id)); }
      const ok = ms.every(okPos) && !errs.length && new URL(page.url()).pathname === '/';
      line(ok, `${vn} ${from} ${kind} «${text}» → /#${id}: через 1/2/3 с ${ms.map((m) => m ? m.gap : '—').join(' / ')} px под шапкой` +
        ` (нужно ${ms[0] ? ms[0].exp : '?'}), шапка ${ms.every((m) => m && m.shown) ? 'видна' : 'СКРЫТА'}${errs.length ? '; JS: ' + errs.join(' | ') : ''}`);
    } catch (e) { line(false, `${vn} ${from} «${text}» → /#${id}: ${String(e).slice(0, 200)}`); }
    await page.close();
  }
  // политика и согласие: app.min.js без Lenis — щелчок по оглавлению, заголовок раздела под шапкой
  if (!ONLY || ONLY === 'privacy') {
    const page = await ctx.newPage();
    const errs = []; page.on('pageerror', (e) => errs.push(String(e).slice(0, 160)));
    try {
      await open(page, BASE + '/privacy/'); await page.waitForTimeout(1000);
      const a = page.locator('.l-toc a').nth(5);
      const id = (await a.getAttribute('href')).replace(/^.*#/, '');
      await a.scrollIntoViewIfNeeded(); await page.waitForTimeout(400);
      await tapOrClick(page, mob, a); await page.waitForTimeout(2200);
      const m = await where(page, id);
      line(okPos(m) && !errs.length, `${vn} политика со скриптом, оглавление → #${id}: ${fmt(m)}${errs.length ? '; JS: ' + errs.join(' | ') : ''}`);
    } catch (e) { line(false, `${vn} политика со скриптом: ${String(e).slice(0, 200)}`); }
    await page.close();
  }
  await ctx.close();
  // 3. без app.min.js: браузер ставит блок сам (style.css), место — то же
  const ctx2 = await browser.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob, deviceScaleFactor: 1 });
  await ctx2.addInitScript(() => { try { sessionStorage.setItem('pc-intro', '1'); } catch (e) {} });
  await route(ctx2, true);
  for (const id of ['podhod', 'tseny', 'voprosy']) {
    const page = await ctx2.newPage();
    try {
      await open(page, BASE + '/#' + id); await page.waitForTimeout(1500);
      const m = await where(page, id);
      line(m && Math.abs(m.gap - m.exp) <= 4, `${vn} без скриптов /#${id}: ${fmt(m)}`);
    } catch (e) { line(false, `${vn} без скриптов /#${id}: ${String(e).slice(0, 200)}`); }
    await page.close();
  }
  // 5. политика: оглавление (на политике и согласии нет app.min.js — только style.css и legal.css)
  {
    const page = await ctx2.newPage();
    try {
      await open(page, BASE + '/privacy/'); await page.waitForTimeout(1000);
      const a = page.locator('.l-toc a').nth(3);
      const id = (await a.getAttribute('href')).replace(/^.*#/, '');
      await a.scrollIntoViewIfNeeded(); await page.waitForTimeout(400);
      await tapOrClick(page, mob, a); await page.waitForTimeout(1800);
      const m = await where(page, id);
      line(m && Math.abs(m.gap - m.exp) <= 4, `${vn} политика, оглавление → #${id}: ${fmt(m)}`);
    } catch (e) { line(false, `${vn} политика, оглавление: ${String(e).slice(0, 200)}`); }
    await page.close();
  }
  await ctx2.close();
}
// 4. «уменьшение движения»
{
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  await route(ctx, false);
  const page = await ctx.newPage();
  const errs = []; page.on('pageerror', (e) => errs.push(String(e).slice(0, 160)));
  try {
    await open(page, BASE + '/'); await page.waitForTimeout(1500);
    await press(page, false, 'nav', 'Цена'); await page.waitForTimeout(400);
    const m = await where(page, 'tseny');
    line(okPos(m) && !errs.length, `компьютер, уменьшение движения: «Цена» → #tseny через 0,4 с: ${fmt(m)}${errs.length ? '; JS: ' + errs.join(' | ') : ''}`);
  } catch (e) { line(false, `уменьшение движения: ${String(e).slice(0, 200)}`); }
  await ctx.close();
}
await browser.close();
console.log(lines.join('\n'));
console.log(`Нарушений: ${bad}`);
process.exit(bad ? 1 : 0);
