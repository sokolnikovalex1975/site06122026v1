// Печать журнала: образец (как есть) и шаблон (тот же DOM с body.tpl) — листы совпадают геометрически.
import { chromium } from 'playwright';
const [,, dir] = process.argv;
const b = await chromium.launch({ headless: true });
const pg = await b.newPage();
await pg.goto('file://' + dir + '/journal.html');
await pg.evaluate(() => document.fonts.ready);
await pg.evaluate(() => {
  const mm = 96 / 25.4;
  document.querySelectorAll('table.fill').forEach(t => {
    const p = t.closest('.pg'), ft = p.querySelector('.ft');
    const rh = parseFloat(t.dataset.rh), tb = t.tBodies[0], num = t.dataset.num === '1';
    const ncols = t.querySelectorAll('colgroup col').length;
    const after = () => { let h = 0, e = t.nextElementSibling; while (e && e !== ft) { const cs = getComputedStyle(e); h += e.getBoundingClientRect().height + parseFloat(cs.marginTop) + parseFloat(cs.marginBottom); e = e.nextElementSibling; } return h; };
    for (let k = 0; k < 90; k++) {
      const room = ft.getBoundingClientRect().top - 2.2 * mm - after() - t.getBoundingClientRect().bottom;
      if (room < rh * mm + 0.5) break;
      const tr = document.createElement('tr');
      for (let i = 0; i < ncols; i++) { const td = document.createElement('td'); if (i === 0) td.style.height = rh + 'mm'; tr.appendChild(td); }
      if (num) { tr.cells[0].textContent = String(tb.rows.length + 1); tr.cells[0].className = 'num'; }
      if (t.classList.contains('mx')) for (let i = 2; i < 10; i++) tr.cells[i].className = 'v';
      tb.appendChild(tr);
    }
  });
});
const qa = await pg.evaluate(() => {
  const out = { pages: [], rows: [], slots: [] };
  document.querySelectorAll('.pg').forEach((p, i) => {
    const ft = p.querySelector('.ft'), prev = ft.previousElementSibling;
    out.pages.push([i + 1, Math.round(ft.getBoundingClientRect().top - prev.getBoundingClientRect().bottom), p.scrollHeight - p.clientHeight]);
    p.querySelectorAll('table.t').forEach((t, ti) => {
      const hs = [...t.tBodies[0].rows].map(r => r.getBoundingClientRect().height);
      if (!hs.length) return;
      const sorted = [...hs].sort((a, b) => a - b); const base = sorted[0];
      hs.forEach((h, ri) => { if (h > base + 0.6) out.rows.push([i + 1, ti, ri, +(h - base).toFixed(1), t.tBodies[0].rows[ri].innerText.slice(0, 60)]); });
    });
    p.querySelectorAll('.sl,.fld,.t-nobox').forEach(e => { if (e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1) out.slots.push([i + 1, e.className, e.innerText.slice(0, 50), e.scrollWidth - e.clientWidth, e.scrollHeight - e.clientHeight]); });
    p.querySelectorAll('td .ink').forEach(e => { const td = e.closest('td'); if (td.scrollWidth > td.clientWidth + 1) out.slots.push([i + 1, 'td-x', e.innerText.slice(0, 40), td.scrollWidth - td.clientWidth, 0]); });
  });
  out.fill = [...document.querySelectorAll('table.t')].map(t => t.tBodies[0].rows.length);
  return out;
});
console.log(JSON.stringify(qa));
await pg.pdf({ path: dir + '/obrazets.pdf', preferCSSPageSize: true, printBackground: true });
await pg.evaluate(() => document.body.classList.add('tpl'));
await pg.pdf({ path: dir + '/shablon.pdf', preferCSSPageSize: true, printBackground: true });
await b.close();
