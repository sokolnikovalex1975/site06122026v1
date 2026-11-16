// Самопроверка на телефоне и планшете (tools/site/samoproverka.py, решение владельца 17.11.2026).
//   BASE=http://127.0.0.1:8833 node tools/qa/samoproverka_test.mjs
//   OLD=http://127.0.0.1:8834  — плюс сравнение с прежней версией: на компьютере (от 1101 px) раскладка блока та же (±1 px),
//                                на телефоне и планшете — высота блока «было → стало» (в отчёте).
// Что проверяется на каждой странице с блоком #samoproverka и каждой ширине экрана:
//   * блок не шире экрана (прокрутка страницы из-за других блоков — предупреждение); кнопка и полоска счёта в пределах
//     карточки, текст кнопки не обрезан;
//   * до 1100 px: заголовок → счёт с полоской → пункты → подсказка → кнопка (кнопка ниже последнего пункта);
//     от 1101 px: подсказка и кнопка в левой колонке под счётом, пункты справа, полоски нет;
//   * до 600 px надпись «Заказать обследование» (где была «Заказать бесплатное обследование»), шире — прежняя;
//   * отрезков полоски столько же, сколько пунктов; после отметки 3 пунктов закрашено 3 и цифра 3; после всех — все;
//   * до 760 px: пока блок в середине экрана, нижняя панель «Позвонить / Обследование» убрана вниз за край экрана,
//     ниже блока — снова на экране.
// Отчёт — в OUT (по умолчанию samoproverka-report.json), в консоль — нарушения. Код выхода 1, если есть нарушения.
import { chromium } from 'playwright';
import fs from 'fs';

const BASE = process.env.BASE || 'http://127.0.0.1:8833';
const OLD = process.env.OLD || '';
const PAGES = (process.env.PAGES || [
  '/restorany-i-kafe/', '/gostinitsy/', '/pishchevoe-proizvodstvo/', '/deratizatsiya/', '/sklady-i-logistika/',
  '/magaziny-i-torgovye-seti/', '/biznes-tsentry-torgovye-tsentry-predpriyatiya/', '/farmatsevticheskie-proizvodstva/',
  '/ochistka-dezinfektsiya-ventilyatsii/', '/dezinsektsiya/', '/materialy/zhurnal-pest-kontrolya/',
  '/materialy/programma-pest-kontrolya/', '/materialy/pest-menedzhment-ili-razovaya-obrabotka/',
  '/zashchita-ot-proniknoveniya-gryzunov/',
].join(' ')).split(' ').filter(Boolean);
const WIDTHS = (process.env.WIDTHS || '320 360 375 390 430 600 601 768 820 1024 1100 1101 1280 1440 1920').split(' ').map(Number);
const FREE = 'Заказать бесплатное обследование', SHORT = 'Заказать обследование';

const measure = () => {
  const s = document.getElementById('samoproverka');
  if (!s) return null;
  const q = c => s.querySelector(c);
  const vis = el => !!el && getComputedStyle(el).display !== 'none' && el.getClientRects().length > 0;
  const R = el => { if (!vis(el)) return null; const r = el.getBoundingClientRect(); return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height }; };
  const btn = q('.f-check-f .btn') || q('.f-check .btn');
  const spans = [...btn.querySelectorAll('.btn-t')].filter(vis);
  return {
    vw: document.documentElement.clientWidth, sw: document.documentElement.scrollWidth,
    sec: R(s), panel: R(q('.f-check')), t: R(q('.f-check-t')), res: R(q('.f-check-res')), bar: R(q('.f-check-bar')),
    list: R(q('.f-check-list')), note: R(q('.f-check-note')), btn: R(btn),
    label: spans.map(e => e.getAttribute('data-t') || e.textContent.trim()).join(' | '),
    // текст надписи не шире своей рамки и рамка внутри кнопки (заливка кнопки ::before шире на 2 px — её не считаем)
    clipped: spans.some(e => { const r = e.getBoundingClientRect(), b = btn.getBoundingClientRect();
      return e.scrollWidth > e.clientWidth + 1 || r.left < b.left - 0.5 || r.right > b.right + 0.5; }),
    items: s.querySelectorAll('.f-check-list input[type=checkbox]').length,
    segs: q('.f-check-bar') ? q('.f-check-bar').children.length : 0,
    firstLi: R(q('.f-check-list li')), lastLi: R(q('.f-check-list li:last-child')),
    blockRight: Math.max(...[...s.querySelectorAll('*')].filter(vis).map(e => e.getBoundingClientRect().right)),
  };
};

const browser = await chromium.launch();
const errors = [], warns = [], report = [];
const bad = (w, pg, msg) => { errors.push(`${w} ${pg} ${msg}`); };

async function open(ctx, url) {
  const p = await ctx.newPage();
  const jsErr = [];
  p.on('pageerror', e => jsErr.push(String(e)));
  await p.goto(url, { waitUntil: 'load', timeout: 45000 });
  await p.waitForTimeout(250);
  return { p, jsErr };
}

for (const w of WIDTHS) {
  const h = w <= 600 ? 800 : w <= 1100 ? 1024 : 900;
  const opts = { viewport: { width: w, height: h }, isMobile: w < 900, hasTouch: w < 900, deviceScaleFactor: 1, reducedMotion: 'reduce' };
  const ctx = await browser.newContext(opts);
  await ctx.route(/mc\.yandex|uiscom|comagic|radist|googletagmanager/, r => r.abort());
  const octx = OLD ? await browser.newContext(opts) : null;
  if (octx) await octx.route(/mc\.yandex|uiscom|comagic|radist|googletagmanager/, r => r.abort());
  for (const pg of PAGES) {
    let p, jsErr;
    try { ({ p, jsErr } = await open(ctx, BASE + pg)); } catch (e) { bad(w, pg, 'LOADFAIL ' + e.message); continue; }
    const m = await p.evaluate(measure);
    if (!m) { bad(w, pg, 'нет блока #samoproverka'); await p.close(); continue; }
    const row = { w, pg, h: Math.round(m.sec.h), panelH: Math.round(m.panel.h), label: m.label };
    if (m.blockRight > m.vw + 1) bad(w, pg, `блок шире экрана: ${Math.round(m.blockRight)} > ${m.vw}`);
    if (m.sw > m.vw + 1) warns.push(`${w} ${pg} горизонтальная прокрутка страницы ${m.sw} > ${m.vw} (не из блока самопроверки)`);
    if (m.btn.x < m.panel.x - 0.5 || m.btn.x + m.btn.w > m.panel.x + m.panel.w + 0.5) bad(w, pg, 'кнопка выходит за карточку');
    if (m.clipped) bad(w, pg, 'текст кнопки обрезан');
    if (m.segs !== m.items) bad(w, pg, `отрезков ${m.segs}, пунктов ${m.items}`);
    const orig = m.label === SHORT || m.label === FREE ? FREE : m.label;
    if (w <= 600 && orig === FREE && m.label !== SHORT) bad(w, pg, `надпись «${m.label}» вместо «${SHORT}»`);
    if (w > 600 && m.label === SHORT) bad(w, pg, `надпись «${SHORT}» шире 600 px`);
    if (w <= 1100) {
      if (!m.bar) bad(w, pg, 'нет полоски счёта');
      else if (m.bar.x + m.bar.w > m.panel.x + m.panel.w + 0.5) bad(w, pg, 'полоска выходит за карточку');
      if (m.list.y < m.res.y + m.res.h - 0.5) bad(w, pg, 'пункты выше счёта');
      if (m.note.y < m.list.y + m.list.h - 0.5) bad(w, pg, 'подсказка выше конца списка');
      if (m.btn.y < m.note.y + m.note.h - 0.5) bad(w, pg, 'кнопка выше подсказки');
      if (w <= 600 && Math.abs(m.btn.w - (m.list.w)) > 1) bad(w, pg, `кнопка не во всю ширину (${m.btn.w} / ${m.list.w})`);
      if (w <= 600 && m.btn.h < 51.5) bad(w, pg, `кнопка ниже 52 px (${m.btn.h})`);
      row.btnH = Math.round(m.btn.h); row.liH = Math.round(m.firstLi.h);
    } else {
      if (m.bar) bad(w, pg, 'полоска видна на компьютере');
      if (m.btn.x + m.btn.w > m.list.x) bad(w, pg, 'кнопка не в левой колонке');
      if (m.btn.y < m.res.y + m.res.h) bad(w, pg, 'кнопка выше счёта');
    }
    if (OLD) {
      const { p: op } = await open(octx, OLD + pg);
      const o = await op.evaluate(() => {
        const s = document.getElementById('samoproverka'); const q = c => s.querySelector(c);
        const R = el => { const r = el.getBoundingClientRect(); return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height }; };
        return { sec: R(s), panel: R(q('.f-check')), t: R(q('.f-check-t')), res: R(q('.f-check-res')), list: R(q('.f-check-list')),
          note: R(q('.f-check-note')), btn: R(q('.f-check .btn')), label: q('.f-check .btn-t').getAttribute('data-t') };
      });
      row.oldH = Math.round(o.sec.h); row.oldPanelH = Math.round(o.panel.h);
      if (w > 1100) {
        for (const k of ['sec', 'panel', 't', 'res', 'list', 'note', 'btn'])
          for (const d of ['x', 'y', 'w', 'h'])
            if (Math.abs(o[k][d] - m[k][d]) > 1) bad(w, pg, `компьютер: ${k}.${d} было ${o[k][d].toFixed(1)}, стало ${m[k][d].toFixed(1)}`);
        if (o.label !== m.label) bad(w, pg, `компьютер: надпись «${m.label}», была «${o.label}»`);
      }
      await op.close();
    }
    // отметки и полоска — на одной ширине телефона, планшета и компьютера
    if ([375, 768, 1440].includes(w)) {
      const st = await p.evaluate(async () => {
        const s = document.getElementById('samoproverka'), cb = [...s.querySelectorAll('.f-check-list input')];
        const read = () => ({ n: (s.querySelector('.f-check-res b') || {}).textContent, on: s.querySelectorAll('.f-check-bar i.on').length,
          cls: s.querySelector('.f-check-res').className });
        const wait = () => new Promise(r => setTimeout(r, 60));
        for (const c of cb.slice(0, 3)) c.click();
        await wait(); const a = read();
        for (const c of cb.slice(3)) c.click();
        await wait(); const b = read();
        for (const c of cb) c.click();
        await wait(); const z = read();
        return { a, b, z, total: cb.length };
      });
      row.clicks = st;
      if (String(st.a.n) !== '3' || st.a.on !== 3) bad(w, pg, `после 3 отметок: цифра ${st.a.n}, отрезков ${st.a.on}`);
      if (String(st.b.n) !== String(st.total) || st.b.on !== st.total) bad(w, pg, `после всех отметок: цифра ${st.b.n}, отрезков ${st.b.on}`);
      if (String(st.z.n) !== '0' || st.z.on !== 0) bad(w, pg, `после снятия отметок: цифра ${st.z.n}, отрезков ${st.z.on}`);
    }
    // нижняя панель на телефоне
    if (w <= 760 && [320, 375, 430].includes(w)) {
      const mb = await p.evaluate(async () => {
        const s = document.querySelector('#samoproverka .f-check'), bar = document.getElementById('mbar');
        const at = async y => { scrollTo(0, y); await new Promise(r => setTimeout(r, 900)); const r = bar.getBoundingClientRect();
          return { on: document.documentElement.classList.contains('f-check-on'), show: bar.classList.contains('show'), top: Math.round(r.top), ih: innerHeight }; };
        const r = s.getBoundingClientRect(), top = r.top + scrollY;
        const mid = await at(top + r.height / 2 - innerHeight / 2);
        const btn = await at(top + r.height - innerHeight + 40);  // кнопка блока у нижнего края экрана
        const after = await at(top + r.height + 40);  // блок ушёл вверх за край экрана
        return { mid, btn, after };
      });
      row.mbar = mb;
      if (!mb.mid.on || mb.mid.top < mb.mid.ih) bad(w, pg, `панель видна, когда блок в середине экрана (${JSON.stringify(mb.mid)})`);
      if (!mb.btn.on || mb.btn.top < mb.btn.ih) bad(w, pg, `панель закрывает кнопку блока (${JSON.stringify(mb.btn)})`);
      if (mb.after.on) bad(w, pg, 'класс f-check-on остался ниже блока');
      if (mb.after.show && mb.after.top >= mb.after.ih) bad(w, pg, 'панель не вернулась ниже блока');
    }
    if (jsErr.length) bad(w, pg, 'ошибки JS: ' + jsErr.join('; '));
    report.push(row);
    await p.close();
  }
  await ctx.close();
  if (octx) await octx.close();
}
await browser.close();
fs.writeFileSync(process.env.OUT || 'samoproverka-report.json', JSON.stringify({ base: BASE, old: OLD, errors, warns, report }, null, 1));
for (const e of warns) console.log('предупреждение:', e);
for (const e of errors) console.log(e);
console.log(`samoproverka_test: страниц ${PAGES.length}, ширин ${WIDTHS.length}, нарушений ${errors.length}`);
process.exit(errors.length ? 1 : 0);
