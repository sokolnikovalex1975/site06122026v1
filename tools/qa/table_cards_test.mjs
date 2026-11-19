// Широкие таблицы на планшете — карточками (tools/site/table_cards.py, команда владельца 19.11.2026).
//   BASE=http://127.0.0.1:8833 [OLD=http://127.0.0.1:8834] node tools/qa/table_cards_test.mjs
// На каждой странице и ширине: страница не шире экрана (как телефон: isMobile до 900 px — там прокрутка видна);
// таблицы .v-freq, .dz-methods и #sanpin .d-table на 601–760 px — карточки (шапка скрыта, ячейки блоками, подпись
// колонки над значением), от 761 px — таблица в пределах своей колонки. С OLD: до 600 px и от 761 px размеры этих таблиц
// и высота страницы те же (±1 px). Запросы к Метрике, UIS и Radist отменяются. Код выхода 1 при нарушениях.
import { chromium } from 'playwright';
const BASE = process.env.BASE || 'http://127.0.0.1:8833';
const OLD = process.env.OLD || '';
const ALL = { '/ochistka-dezinfektsiya-ventilyatsii/': ['.v-freq'], '/dezinsektsiya/': ['.dz-methods', '#sanpin .d-table'] };
// ONLY=/dezinsektsiya/ — одна страница (например, повтор после ложного 502 Timeweb)
const PAGES = process.env.ONLY ? { [process.env.ONLY]: ALL[process.env.ONLY] } : ALL;
const WIDTHS = (process.env.WIDTHS || '320 375 430 560 600 601 620 640 660 670 690 700 720 744 760 761 768 800 820 900 1024 1280 1440 1920').split(' ').map(Number);
const b = await chromium.launch();
const errors = [];
const measure = (sels) => ({ vw: document.documentElement.clientWidth, sw: document.documentElement.scrollWidth, H: document.documentElement.scrollHeight,
  t: sels.map(s => { const t = document.querySelector(s); const r = t.getBoundingClientRect(); const td = t.querySelector('td');
    const par = t.parentElement.getBoundingClientRect();
    return { s, w: Math.round(r.width), h: Math.round(r.height), right: r.right, parRight: par.right,
      thead: getComputedStyle(t.querySelector('thead') || t).display, td: getComputedStyle(td).display,
      label: getComputedStyle(td, '::before').content }; }) });
async function load(base, pg, w) {
  const ctx = await b.newContext({ viewport: { width: w, height: w <= 600 ? 800 : 1024 }, isMobile: w < 900, hasTouch: w < 900, deviceScaleFactor: 1, reducedMotion: 'reduce' });
  await ctx.route(/mc\.yandex|uiscom|comagic|radist|googletagmanager/, r => r.abort());
  const p = await ctx.newPage();
  let ok = false;
  for (let i = 0; i < 4 && !ok; i++) { const r = await p.goto(base + pg, { waitUntil: 'load', timeout: 45000 }).catch(() => null); ok = !!r && r.status() === 200; }
  if (!ok) { await ctx.close(); return null; }
  await p.waitForTimeout(250);
  const m = await p.evaluate(measure, PAGES[pg]);
  await ctx.close();
  return m;
}
for (const pg of Object.keys(PAGES)) for (const w of WIDTHS) {
  const m = await load(BASE, pg, w);
  if (!m) { errors.push(`${w} ${pg} страница не открылась`); continue; }
  if (m.sw > m.vw) errors.push(`${w} ${pg} прокрутка вбок: ${m.sw} > ${m.vw}`);
  for (const t of m.t) {
    const cards = w >= 601 && w <= 760;
    if (cards && (t.thead !== 'none' || t.td !== 'block' || t.label === 'none')) errors.push(`${w} ${pg} ${t.s}: не карточки`);
    if (w > 760 && t.td !== 'table-cell') errors.push(`${w} ${pg} ${t.s}: не таблица`);
    if (t.right > t.parRight + 1) errors.push(`${w} ${pg} ${t.s}: шире своей колонки (${Math.round(t.right)} > ${Math.round(t.parRight)})`);
  }
  let note = '';
  if (OLD && (w <= 600 || w > 760)) {
    const o = await load(OLD, pg, w);
    if (o) { o.t.forEach((x, i) => { const n = m.t[i]; if (Math.abs(x.w - n.w) > 1 || Math.abs(x.h - n.h) > 1) errors.push(`${w} ${pg} ${n.s}: было ${x.w}×${x.h}, стало ${n.w}×${n.h}`); });
      if (Math.abs(o.H - m.H) > 1) errors.push(`${w} ${pg} высота страницы: было ${o.H}, стало ${m.H}`); note = ' = как было'; }
  }
  console.log(w, pg, m.sw <= m.vw ? 'без прокрутки' : 'ПРОКРУТКА', m.t.map(t => `${t.s} ${t.td === 'block' ? 'карточки' : 'таблица'} ${t.w}×${t.h}`).join('; ') + note);
}
await b.close();
errors.forEach(e => console.log('НАРУШЕНИЕ:', e));
console.log(`table_cards_test: страниц ${Object.keys(PAGES).length}, ширин ${WIDTHS.length}, нарушений ${errors.length}`);
process.exit(errors.length ? 1 : 0);
