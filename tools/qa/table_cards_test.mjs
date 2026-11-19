// Широкие таблицы на планшете — карточками (tools/site/table_cards.py, команда владельца 19.11.2026).
//   BASE=http://127.0.0.1:8833 [OLD=http://127.0.0.1:8834] node tools/qa/table_cards_test.mjs
// На каждой странице и ширине: страница не шире экрана, заголовки h2 в пределах своей колонки (как телефон: isMobile до 900 px — там прокрутка видна);
// таблицы .v-freq, .dz-methods и #sanpin .d-table на 601–760 px — карточки (шапка скрыта, ячейки блоками, подпись
// колонки над значением) в диапазоне правки (601–760 или 861–1040 px) и там, где страница сама складывает их в карточки,
// иначе — таблица в пределах своей колонки. С OLD: вне диапазона правки размеры этих таблиц и высота страницы те же (±1 px). Запросы к Метрике, UIS и Radist отменяются. Код выхода 1 при нарушениях.
import { chromium } from 'playwright';
const BASE = process.env.BASE || 'http://127.0.0.1:8833';
const OLD = process.env.OLD || '';
// страница: таблицы, до скольких px страница сама показывает их карточками (native), диапазон правки (cards)
const T = (sels, native, cards) => ({ sels, native, cards });
const ALL = {
  '/ochistka-dezinfektsiya-ventilyatsii/': T(['.v-freq'], 600, [601, 760]),
  '/dezinsektsiya/': T(['.dz-methods', '#sanpin .d-table'], 600, [601, 760]),
  '/dezinfektsiya/': T(['.dzf-kinds', '.dzf-freq'], 600, [601, 760]),
  '/laboratornye-issledovaniya/analiz-pishchevykh-produktov/': T(['.lbs-t'], 600, [601, 760]),
  '/laboratornye-issledovaniya/kontrol-sterilizatorov/': T(['.lbs-t'], 600, [601, 760]),
  '/laboratornye-issledovaniya/zamer-osveshchennosti/': T(['.lbs-t'], 600, [601, 760]),
  '/materialy/kontrol-raboty-sterilizatorov/': T(['.lbs-t'], 600, [601, 760]),
  '/materialy/programma-pest-kontrolya/': T(['.p-plan-table'], 860, [861, 980]),
  '/normativnaya-baza/': T(['.nb-docs'], 900, [901, 1000]),
  '/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/': T(['.dk-tbl'], 900, [901, 1040]),
};
// заголовки на 441–520 px на 5 % меньше — страница короче, это ожидаемо
const SHORTER = ['/dezinfektsiya/', '/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/'];
// ONLY=/dezinsektsiya/ — одна страница (например, повтор после ложного 502 Timeweb)
const PAGES = process.env.ONLY ? { [process.env.ONLY]: ALL[process.env.ONLY] } : ALL;
const WIDTHS = (process.env.WIDTHS || '320 375 430 445 450 480 505 560 600 601 620 640 660 670 690 700 720 744 760 761 768 800 820 860 861 880 900 901 920 940 960 980 981 1000 1001 1020 1040 1041 1060 1280 1440 1920').split(' ').map(Number);
const b = await chromium.launch();
const errors = [];
const measure = (sels) => ({ vw: document.documentElement.clientWidth, sw: document.documentElement.scrollWidth, H: document.documentElement.scrollHeight,
  t: sels.flatMap(s => [...document.querySelectorAll(s)].map((t, k) => [s + (k ? ' #' + (k + 1) : ''), t])).map(([s, t]) => { const r = t.getBoundingClientRect(); const td = t.querySelector('td');
    const par = t.parentElement.getBoundingClientRect();
    return { s, w: Math.round(r.width), h: Math.round(r.height), right: r.right, parRight: par.right,
      thead: getComputedStyle(t.querySelector('thead') || t).display, td: getComputedStyle(td).display,
      label: getComputedStyle(td, '::before').content }; }),
  // заголовки h2 не выходят за свою колонку (заголовок «Документы по дезинфекции» на 445–505 px выходил на 4–21 px)
  h2: [...document.querySelectorAll('main h2')].filter(h => h.getClientRects().length).map(h => { const hr = h.getBoundingClientRect().right;
    const over = Math.max(...[...h.querySelectorAll('*')].flatMap(e => [...e.getClientRects()].map(r => r.right)), hr) - hr;
    return over > 1 ? h.textContent.trim().slice(0, 50) + ' +' + Math.round(over) : ''; }).filter(Boolean) });
async function load(base, pg, w) {
  const ctx = await b.newContext({ viewport: { width: w, height: w <= 600 ? 800 : 1024 }, isMobile: w < 900, hasTouch: w < 900, deviceScaleFactor: 1, reducedMotion: 'reduce' });
  await ctx.route(/mc\.yandex|uiscom|comagic|radist|googletagmanager/, r => r.abort());
  const p = await ctx.newPage();
  let ok = false;
  for (let i = 0; i < 4 && !ok; i++) { const r = await p.goto(base + pg, { waitUntil: 'load', timeout: 45000 }).catch(() => null); ok = !!r && r.status() === 200; }
  if (!ok) { await ctx.close(); return null; }
  await p.waitForTimeout(250);
  const m = await p.evaluate(measure, PAGES[pg].sels);
  await ctx.close();
  return m;
}
for (const pg of Object.keys(PAGES)) for (const w of WIDTHS) {
  const m = await load(BASE, pg, w);
  if (!m) { errors.push(`${w} ${pg} страница не открылась`); continue; }
  if (m.sw > m.vw) errors.push(`${w} ${pg} прокрутка вбок: ${m.sw} > ${m.vw}`);
  for (const h of m.h2) errors.push(`${w} ${pg} заголовок шире колонки: ${h}`);
  const cfg = PAGES[pg];
  const inFix = w >= cfg.cards[0] && w <= cfg.cards[1];
  for (const t of m.t) {
    const cards = w <= cfg.native || inFix;
    if (cards && (t.thead !== 'none' || t.td !== 'block' || t.label === 'none')) errors.push(`${w} ${pg} ${t.s}: не карточки`);
    if (!cards && t.td !== 'table-cell') errors.push(`${w} ${pg} ${t.s}: не таблица`);
    if (t.right > t.parRight + 1) errors.push(`${w} ${pg} ${t.s}: шире своей колонки (${Math.round(t.right)} > ${Math.round(t.parRight)})`);
  }
  let note = '';
  if (OLD && !inFix) {
    const o = await load(OLD, pg, w);
    if (o) { o.t.forEach((x, i) => { const n = m.t[i]; if (Math.abs(x.w - n.w) > 1 || Math.abs(x.h - n.h) > 1) errors.push(`${w} ${pg} ${n.s}: было ${x.w}×${x.h}, стало ${n.w}×${n.h}`); });
      // дезинфекция на 441–520 px: заголовок «Документы по дезинфекции» на 5 % меньше — страница короче, это ожидаемо
      if (Math.abs(o.H - m.H) > 1 && !(SHORTER.includes(pg) && w >= 441 && w <= 520)) errors.push(`${w} ${pg} высота страницы: было ${o.H}, стало ${m.H}`); note = ' = как было'; }
  }
  console.log(w, pg, m.sw <= m.vw ? 'без прокрутки' : 'ПРОКРУТКА', m.t.map(t => `${t.s} ${t.td === 'block' ? 'карточки' : 'таблица'} ${t.w}×${t.h}`).join('; ') + note);
}
await b.close();
errors.forEach(e => console.log('НАРУШЕНИЕ:', e));
console.log(`table_cards_test: страниц ${Object.keys(PAGES).length}, ширин ${WIDTHS.length}, нарушений ${errors.length}`);
process.exit(errors.length ? 1 : 0);
