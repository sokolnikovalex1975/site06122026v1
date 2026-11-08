// Печать акта: образец и бланк из одного HTML.
//   node render_akt.mjs pdf <dir>  — dir/akt.html → akt.pdf и blank.pdf (body.tpl)
import fs from 'fs';
import { chromium } from 'playwright';

const [,, mode, dir, ...rest] = process.argv;
const b = await chromium.launch({ headless: true });

async function qa(pg) {
  return pg.evaluate(() => {
    const out = { pages: [], over: [] };
    document.querySelectorAll('.pg').forEach((p, i) => {
      const ft = p.querySelector('.ft'), prev = ft.previousElementSibling;
      out.pages.push([i + 1, Math.round((ft.getBoundingClientRect().top - prev.getBoundingClientRect().bottom) * 25.4 / 96), p.scrollHeight - p.clientHeight]);
      p.querySelectorAll('.sl,.fld,.a-nobox').forEach(e => {
        if (e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1) out.over.push([i + 1, e.className, e.innerText.slice(0, 60)]);
      });
      p.querySelectorAll('td').forEach(td => { if (td.scrollWidth > td.clientWidth + 1) out.over.push([i + 1, 'td', td.innerText.slice(0, 60)]); });
    });
    return out;
  });
}

if (mode === 'pdf') {
  const pg = await b.newPage();
  await pg.goto('file://' + dir + '/akt.html', { waitUntil: 'load' });
  await pg.evaluate(() => document.fonts.ready);
  const r1 = await qa(pg);
  await pg.pdf({ path: dir + '/akt.pdf', preferCSSPageSize: true, printBackground: true });
  await pg.evaluate(() => document.body.classList.add('tpl'));
  await pg.pdf({ path: dir + '/blank.pdf', preferCSSPageSize: true, printBackground: true });
  await pg.screenshot({ path: dir + '/blank-p1.png', clip: { x: 0, y: 0, width: 794, height: 1123 } });
  await pg.evaluate(() => document.body.classList.remove('tpl'));
  await pg.setViewportSize({ width: 794, height: 1123 });
  console.log(JSON.stringify({ akt: r1 }));
}
await b.close();
