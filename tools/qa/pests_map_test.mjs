// Проверка фона блока «Вредители» — «Карта очагов» (12.11.2026) на 9 страницах, компьютер 1440 и телефон 390.
// Запуск: BASE=http://localhost:8090 node tools/qa/pests_map_test.mjs   (по умолчанию — рабочий сайт; нужен playwright)
// Счётчики в тесте заблокированы, чтобы не портить статистику. SHOTS=папка — снимки блока на главной и «Дератизации».
// Итог: строка на страницу и экран, в конце — число нарушений (фон не подгрузился, старая фактура, ошибки JS, прокрутка).
import { chromium } from 'playwright';
import fs from 'node:fs';

const BASE = (process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai').replace(/\/$/, '');
const SHOTS = process.env.SHOTS || '';
const PAGES = [
  ['/', '#vrediteli'], ['/deratizatsiya/', '#vidy'], ['/pishchevoe-proizvodstvo/', '#vrediteli'], ['/restorany-i-kafe/', '#vrediteli'],
  ['/magaziny-i-torgovye-seti/', '#vrediteli'], ['/gostinitsy/', '#vrediteli'], ['/farmatsevticheskie-proizvodstva/', '#vrediteli'],
  ['/sklady-i-logistika/', '#vrediteli-sklada'], ['/biznes-tsentry-torgovye-tsentry-predpriyatiya/', '#vrediteli'],
];
const DEVICES = {
  desktop: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 },
  mobile: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' },
};
if (SHOTS) fs.mkdirSync(SHOTS, { recursive: true });

const browser = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
let bad = 0;
for (const [dev, opts] of Object.entries(DEVICES)) {
  const ctx = await browser.newContext(opts);
  for (const [path, sel] of PAGES) {
    const page = await ctx.newPage();
    await page.route(/mc\.yandex|uiscom|radist|yandex\.ru\/metrika/, r => r.abort());
    const errors = [], svg = [], texture = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('response', r => { if (r.url().includes('pests-map.svg')) svg.push(r.status() + ' ' + (r.headers()['content-type'] || '')); });
    page.on('request', r => { if (r.url().includes('texture.webp')) texture.push(r.url()); });
    await page.goto(BASE + path, { waitUntil: 'load' });
    await page.waitForFunction(() => !!window.gsap, null, { timeout: 8000 }).catch(() => {});
    const top = await page.evaluate(s => document.querySelector(s).getBoundingClientRect().top + scrollY, sel);
    for (let y = 0; y < top - 100; y += 500) { await page.evaluate(v => scrollTo(0, v), y); await page.waitForTimeout(50); }
    await page.evaluate(v => scrollTo(0, v), top - 100);
    await page.waitForFunction(s => document.querySelector(s + ' .pests-bg').classList.contains('bg-in'), sel, { timeout: 6000 }).catch(() => {});
    await page.waitForTimeout(700);
    const st = await page.evaluate(s => {
      const sec = document.querySelector(s), bg = sec.querySelector('.pests-bg'), cs = getComputedStyle(bg);
      return { lazy: bg.classList.contains('bg-in'), map: cs.backgroundImage.includes('pests-map.svg'), glows: cs.backgroundImage.split('radial-gradient').length - 1,
        color: cs.backgroundColor, fade: getComputedStyle(sec, '::after').backgroundImage.startsWith('linear-gradient'),
        oldShade: getComputedStyle(sec, '::before').content !== 'none', hscroll: document.documentElement.scrollWidth > innerWidth };
    }, sel);
    const ok = st.lazy && st.map && st.glows === 2 && st.color === 'rgb(5, 5, 8)' && st.fade && !st.oldShade && !st.hscroll &&
      !errors.length && !texture.length && svg.length && svg.every(x => x.startsWith('200 image/svg+xml'));
    if (!ok) bad++;
    console.log((ok ? 'OK  ' : 'BAD ') + dev.padEnd(7) + ' ' + path.padEnd(48) + ' ' + JSON.stringify({ ...st, svg, texture: texture.length, errors }));
    if (SHOTS && (path === '/' || path === '/deratizatsiya/')) {
      await page.evaluate(s => { const e = document.querySelector(s); const h = e.querySelector('[data-eyebrow]') || e; scrollTo(0, h.getBoundingClientRect().top + scrollY - 100); }, sel);
      await page.waitForTimeout(1200);
      await page.screenshot({ path: `${SHOTS}/${dev}${path === '/' ? '-home' : '-deratizatsiya'}.png` });
    }
    await page.close();
  }
  await ctx.close();
}
await browser.close();
console.log('нарушений:', bad);
process.exit(bad ? 1 : 0);
