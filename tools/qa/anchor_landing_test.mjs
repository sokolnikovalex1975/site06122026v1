// Проверка 13.11.2026: переход по ссылке с якорем с другой страницы и подсветка пунктов шапки.
// Запуск: BASE=http://127.0.0.1:8090 node tools/qa/anchor_landing_test.mjs   (по умолчанию — рабочий сайт)
// PKG=<папка pkg пакета> — подставить страницы, app.min.js и style.css пакета вместо файлов сайта (проверка до выкладки).
// 1. Переход: настоящий щелчок (касание) по ссылке «Метод IPM» в шапке, «Цена» на политике, «Этапы работы», «Вредители»,
//    «Вопросы» в подвале — на главной блок встаёт под шапку и держится там через 1, 2 и 3 с после загрузки. С 13.11.2026
//    (правка «начало блока сразу под шапкой», tools/qa/anchor_heading_test.mjs) шапка видна, подпись над заголовком блока —
//    на 20…32 px ниже шапки (допуск 3 px); до этой правки проверялся верх блока на 96 px от верха окна (80…130 px).
//    Раньше браузер не доезжал: 300…2500 px, на телефоне до блока не доходило вовсе.
// 2. Подсветка: прокрутка колесом через всю страницу (компьютер) — пункт шапки горит только пока его блок в полосе
//    45–50 % высоты окна. Раньше «Цена» горела до самого подвала.
// Счётчики не загружаются (запросы к Метрике, UIS и Radist обрываются). Итог — число нарушений; код выхода 1, если есть.
import { chromium } from 'playwright';
import fs from 'fs';

const BASE = (process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai').replace(/\/$/, '');
const PKG = process.env.PKG || '';
const BLOCK = /mc\.yandex|uiscom|comagic|radist|yandex\.ru\/metrika|mc\.webvisor/;
const LAND = [
  // [страница, где ссылка, текст ссылки, якорь на главной]
  ['/dezinsektsiya/', 'header', 'Метод IPM', 'podhod'],
  ['/privacy/', 'header', 'Цена', 'tseny'],
  ['/deratizatsiya/', 'footer', 'Этапы работы', 'etapy'],
  ['/gostinitsy/', 'footer', 'Вредители', 'vrediteli'],
  ['/materialy/', 'footer', 'Вопросы', 'voprosy'],
];
const SPY = (process.env.SPY || '/ /dezinsektsiya/ /gostinitsy/').trim().split(/\s+/);
const VP = [['компьютер 1440×900', 1440, 900, false], ['телефон 390×844', 390, 844, true]];

const route = async (ctx) => {
  await ctx.route('**/*', (r) => {
    const u = r.request().url();
    if (BLOCK.test(u)) return r.abort();
    if (PKG && u.startsWith(BASE + '/')) {
      const path = decodeURI(u.slice(BASE.length + 1).split('?')[0].split('#')[0]);
      if (path === 'app.min.js' || path === 'style.css') return r.fulfill({ status: 200, body: fs.readFileSync(`${PKG}/${path}`),
        contentType: path.endsWith('.js') ? 'application/javascript; charset=utf-8' : 'text/css; charset=utf-8' });
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

const browser = await chromium.launch();
let bad = 0;
const lines = [];
for (const [vn, w, h, mob] of VP) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob, deviceScaleFactor: 1 });
  await ctx.addInitScript(() => { try { sessionStorage.setItem('pc-intro', '1'); } catch (e) {} });
  await route(ctx);
  for (const [from, where, text, id] of LAND) {
    if (mob && where === 'header') continue; // на телефоне ссылки шапки — в мобильном меню, проверяются подвалом
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', (e) => errs.push(String(e).slice(0, 160)));
    let msg = '';
    try {
      await open(page, BASE + from);
      await page.waitForTimeout(1500);
      const a = page.locator(`${where === 'header' ? '.nav > a' : 'footer a'}:text-is("${text}")`).first();
      const href = await a.getAttribute('href');
      if (where === 'footer') { // как посетитель: прокрутка к подвалу, пауза, щелчок по координатам
        await a.evaluate((el) => window.scrollTo(0, el.getBoundingClientRect().top + scrollY - innerHeight / 2));
        await page.waitForTimeout(1500);
      }
      const b = await a.boundingBox();
      await Promise.all([page.waitForURL((u) => u.hash === '#' + id, { timeout: 60000 }),
        mob ? page.touchscreen.tap(b.x + b.width / 2, b.y + b.height / 2) : page.mouse.click(b.x + b.width / 2, b.y + b.height / 2)]);
      await page.waitForLoadState('load');
      const tops = [];
      let exp = 0;
      for (const t of [1000, 1000, 1000]) {
        await page.waitForTimeout(t);
        const m = await page.evaluate((id) => {
          const el = document.getElementById(id), hdr = document.getElementById('hdr'); if (!el || !hdr) return null;
          const hb = hdr.getBoundingClientRect().bottom, head = el.querySelector('.eyebrow, h1, h2') || el;
          return { gap: hdr.classList.contains('hide') ? null : Math.round(head.getBoundingClientRect().top - hb), exp: Math.round(Math.min(32, Math.max(20, innerWidth * 0.022))) };
        }, id);
        exp = m ? m.exp : exp;
        tops.push(m ? m.gap : null);
      }
      const path = new URL(page.url()).pathname;
      const ok = path === '/' && tops.every((t) => t !== null && Math.abs(t - exp) <= 3) && !errs.length;
      if (!ok) bad++;
      msg = `${ok ? 'OK ' : 'НЕТ'} ${vn} ${from} ${where === 'header' ? 'шапка' : 'подвал'} «${text}» (${href}) → ${path}#${id}: подпись блока ниже шапки на ${tops.map((t) => t === null ? 'шапка скрыта' : t).join(' / ')} px (нужно ${exp})${errs.length ? ' JS: ' + errs.join(' | ') : ''}`;
    } catch (e) { bad++; msg = `НЕТ ${vn} ${from} «${text}»: ${String(e).slice(0, 200)}`; }
    lines.push(msg);
    await page.close();
  }
  if (!mob) {
    for (const p of SPY) {
      const page = await ctx.newPage();
      const errs = [];
      page.on('pageerror', (e) => errs.push(String(e).slice(0, 160)));
      let sticky = 0, steps = 0, lit = new Set();
      try {
        await open(page, BASE + p);
        await page.waitForTimeout(2500);
        await page.mouse.move(w / 2, h / 2);
        for (let i = 0; i < 90; i++) {
          const st = await page.evaluate(() => {
            const links = [...document.querySelectorAll('.nav > a[href^="#"], .nav [data-spy]')];
            const sid = (l) => (l.getAttribute('data-spy') || l.getAttribute('href')).slice(1);
            const b0 = innerHeight * 0.45, b1 = innerHeight * 0.5, exp = [], act = [];
            for (const l of links) {
              const s = document.getElementById(sid(l)); if (!s) continue;
              const r = s.getBoundingClientRect();
              if (r.bottom > b0 && r.top < b1) exp.push(l.textContent.trim());
              if (l.classList.contains('active')) act.push(l.textContent.trim());
            }
            return { y: scrollY, max: document.documentElement.scrollHeight - innerHeight, exp, act };
          });
          steps++;
          st.act.forEach((x) => lit.add(x));
          if (st.act.some((x) => !st.exp.includes(x))) sticky++;
          if (st.y >= st.max - 2) break;
          await page.mouse.wheel(0, 450);
          await page.waitForTimeout(900);
        }
      } catch (e) { errs.push(String(e).slice(0, 200)); }
      const ok = !sticky && steps > 10 && lit.has('Цена') && !errs.length;
      if (!ok) bad++;
      lines.push(`${ok ? 'OK ' : 'НЕТ'} ${vn} ${p} подсветка шапки при прокрутке: шагов ${steps}, лишняя подсветка ${sticky}, горели: ${[...lit].join(', ') || '—'}${errs.length ? ' ОШИБКИ: ' + errs.join(' | ') : ''}`);
      await page.close();
    }
  }
  await ctx.close();
}
await browser.close();
console.log(lines.join('\n'));
console.log(`Нарушений: ${bad}`);
process.exit(bad ? 1 : 0);
