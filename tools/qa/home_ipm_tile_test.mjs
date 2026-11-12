// Главная, блок цен #tseny: плитка «Пест-контроль по системе IPM» — текущая страница (предложение владельца 12.11.2026).
// Метка «Вы здесь», без ссылки на #podhod: нажатие не перебрасывает через «Этапы работы», фирменный курсор не в режиме ссылки.
//   python3 -m http.server 8090 --bind 127.0.0.1   (из корня репозитория)
//   BASE=http://127.0.0.1:8090/ node tools/qa/home_ipm_tile_test.mjs
import { chromium } from 'playwright';

const BASE = process.env.BASE || 'http://127.0.0.1:8090/';
const VIEWS = {
  'компьютер 1440': { viewport: { width: 1440, height: 900 } },
  'телефон 390': { viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true },
};
const browser = await chromium.launch();
let bad = 0;
for (const [name, opts] of Object.entries(VIEWS)) {
  const ctx = await browser.newContext(opts);
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  // счётчики в тесте не грузим, чтобы не портить статистику
  await page.route('**/*', r => (r.request().url().startsWith(BASE) ? r.continue() : r.abort()));
  await page.goto(BASE, { waitUntil: 'load' });
  await page.waitForTimeout(2500);
  const top = await page.evaluate(() => document.querySelector('#tseny').getBoundingClientRect().top + scrollY);
  if (opts.isMobile) await page.evaluate(t => scrollTo(0, t - 100), top);
  else for (let y = 0; y < top - 120; y += 600) { await page.mouse.wheel(0, 600); await page.waitForTimeout(120); }
  await page.waitForTimeout(2200);
  const t = await page.evaluate(() => {
    const sec = document.querySelector('#tseny'), el = sec.querySelector('.pr-cards > :first-child'), r = el.getBoundingClientRect();
    return { tag: el.tagName, current: el.getAttribute('aria-current'), label: (el.querySelector('.pr-here-g') || {}).textContent,
      self: sec.querySelectorAll('a[href="#podhod"]').length, links: sec.querySelectorAll('.pr-cards > a').length,
      overflow: document.documentElement.scrollWidth - innerWidth, x: r.x + r.width / 2, y: r.y + Math.min(r.height / 2, 300) };
  });
  let cursorLink = false;
  if (!opts.isMobile) {
    await page.mouse.move(t.x, t.y, { steps: 4 });
    await page.waitForTimeout(300);
    cursorLink = await page.evaluate(() => !!document.querySelector('.cursor.link'));
  }
  const y0 = await page.evaluate(() => scrollY);
  if (opts.isMobile) await page.touchscreen.tap(t.x, t.y); else await page.mouse.click(t.x, t.y);
  await page.waitForTimeout(2200);
  const jump = Math.round((await page.evaluate(() => scrollY)) - y0);
  const fails = [];
  if (t.tag !== 'DIV' || t.current !== 'page') fails.push(`плитка ${t.tag}, aria-current=${t.current}`);
  if (t.label !== 'Вы здесь') fails.push('нет зелёной метки «Вы здесь»');
  if (t.self) fails.push(`ссылок на #podhod в блоке цен: ${t.self}`);
  if (t.links !== 3) fails.push(`ссылок на остальные плитки: ${t.links} вместо 3`);
  if (cursorLink) fails.push('курсор над плиткой в режиме ссылки');
  if (Math.abs(jump) > 2) fails.push(`нажатие сдвинуло страницу на ${jump} px`);
  if (t.overflow > 0) fails.push(`горизонтальная прокрутка ${t.overflow} px`);
  if (errors.length) fails.push('ошибки JavaScript: ' + errors.join('; '));
  console.log(`${fails.length ? 'ОШИБКА' : 'OK'} — ${name}: ${fails.length ? fails.join('; ') : `плитка без ссылки, «Вы здесь», сдвиг при нажатии ${jump} px`}`);
  bad += fails.length;
  await ctx.close();
}
await browser.close();
process.exit(bad ? 1 : 0);
