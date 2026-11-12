// Проверка: «Цена» (шапка, мобильное меню, подвал) и «Вопросы» (подвал) ведут к блокам этой же страницы (12.11.2026).
// Запуск: BASE=http://localhost:8090 node tools/qa/menu_anchors_test.mjs   (по умолчанию — рабочий сайт)
// Страницы — PAGES='/ /dezinsektsiya/'. Итог: JSON по каждой странице и экрану, в конце — число нарушений.
// Норма: адрес страницы не меняется (кроме политики и согласия — они ведут на прайс главной), верх блока после
// прокрутки — под шапкой (0…200 px от верха окна; на главной 176 px), мобильное меню закрывается, нет горизонтальной прокрутки и ошибок JS.
import { chromium } from 'playwright';
const BASE = process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai';
const PAGES = (process.env.PAGES || `/ /dezinsektsiya/ /deratizatsiya-i-dezinsektsiya/ /laboratornye-issledovaniya/analiz-vody/
/materialy/zhurnal-pest-kontrolya/ /materialy/ /restorany-i-kafe/ /privacy/`).trim().split(/\s+/);
const VP = [['компьютер 1440×900', 1440, 900, false], ['телефон 390×844', 390, 844, true]];
const WAIT = 2300; // плавная прокрутка Lenis — 1,5 с

const browser = await chromium.launch();
const out = [];
let bad = 0;
for (const [vn, w, h, mob] of VP) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob, deviceScaleFactor: 1 });
  await ctx.addInitScript(() => { try { sessionStorage.setItem('pc-intro', '1'); } catch (e) {} });
  await ctx.route(/mc\.yandex|uiscom|comagic|radist|yandex\.ru\/metrika|mc\.webvisor/, r => r.abort());
  for (const p of PAGES) {
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', e => errs.push(String(e).slice(0, 160)));
    const res = { vn, p, steps: [] };
    const where = async (href) => page.evaluate((href) => {
      const frag = href.split('#')[1];
      const el = document.getElementById(frag);
      const cena = [...document.querySelectorAll('.nav > a')].find(a => a.textContent.trim() === 'Цена');
      return { path: location.pathname, hash: location.hash, top: el ? Math.round(el.getBoundingClientRect().top) : null,
        active: cena ? cena.classList.contains('active') : null, docW: document.documentElement.scrollWidth, iw: innerWidth,
        menu: document.getElementById('burger')?.getAttribute('aria-expanded') };
    }, href);
    const step = async (name, locator, before) => {
      const a = page.locator(locator).first();
      const href = await a.getAttribute('href');
      if (before) await before();
      if (locator.startsWith('footer')) {
        // как посетитель: прокрутка до ссылки (колесо на компьютере, обычная прокрутка на телефоне), пауза, щелчок/касание
        // по координатам. Щелчок Playwright с автопрокруткой не годится: он жмёт раньше, чем Lenis узнаёт о прокрутке.
        if (!mob) { for (let i = 0; i < 90; i++) { await page.mouse.wheel(0, 700); await page.waitForTimeout(35); } }
        await page.waitForTimeout(1200);
        await a.evaluate(el => { const r = el.getBoundingClientRect(); if (r.top < 0 || r.bottom > innerHeight) window.scrollTo(0, r.top + scrollY - innerHeight / 2); });
        await page.waitForTimeout(1200);
        const b = await a.boundingBox();
        if (mob) await page.touchscreen.tap(b.x + b.width / 2, b.y + b.height / 2);
        else await page.mouse.click(b.x + b.width / 2, b.y + b.height / 2);
      } else await a.click();
      await page.waitForTimeout(WAIT);
      if (href.split('#')[0]) await page.waitForLoadState('load');
      const r = await where(href);
      const samePage = !href.split('#')[0];
      const ok = (samePage ? r.path === new URL(BASE + p).pathname : r.path !== new URL(BASE + p).pathname)
        && r.top !== null && r.top >= 0 && r.top <= 200 && r.docW <= r.iw && (r.menu === null || r.menu === 'false');
      if (!ok) bad++;
      res.steps.push({ name, href, ok, ...r });
      if (!samePage) { await page.goto(BASE + p, { waitUntil: 'load' }); await page.waitForTimeout(1200); }
    };
    try {
      await page.goto(BASE + p, { waitUntil: 'load', timeout: 60000 });
      await page.waitForTimeout(1500);
      if (!mob) await step('шапка «Цена»', '.nav > a:text-is("Цена")');
      else await step('мобильное меню «Цена»', '#mmenu a:text-is("Цена")', async () => {
        await page.click('#burger'); await page.waitForTimeout(900);
      });
      await step('подвал «Цена»', 'footer a:text-is("Цена")');
      await step('подвал «Вопросы»', 'footer a:text-is("Вопросы")');
    } catch (e) { bad++; res.err = String(e).slice(0, 200); }
    if (errs.length) { bad++; res.errs = errs; }
    out.push(res);
    await page.close();
  }
  await ctx.close();
}
await browser.close();
for (const r of out) {
  console.log(`${r.vn} ${r.p}${r.err ? ' ОШИБКА ' + r.err : ''}${r.errs ? ' JS: ' + r.errs.join(' | ') : ''}`);
  for (const s of r.steps) console.log(`  ${s.ok ? 'OK ' : 'НЕТ'} ${s.name}: ${s.href} → ${s.path}${s.hash}, верх блока ${s.top} px` +
    `${s.active !== null ? ', «Цена» подсвечена: ' + (s.active ? 'да' : 'нет') : ''}${s.menu !== null && s.menu !== undefined ? ', меню открыто: ' + s.menu : ''}`);
}
console.log(`Нарушений: ${bad}`);
process.exit(bad ? 1 : 0);
