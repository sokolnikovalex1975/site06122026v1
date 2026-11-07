// Печать акта (образец и бланк из одного HTML), чек-листа и картинки для соцсетей.
//   node render_akt.mjs pdf <dir>                         — dir/akt.html → akt.pdf и blank.pdf (body.tpl), dir/cheklist.html → ck.pdf
//   node render_akt.mjs og <dir> <img1> <img2> <out.jpg>  — картинка 1200×630 для og:image
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
  const pg2 = await b.newPage();
  await pg2.goto('file://' + dir + '/cheklist.html', { waitUntil: 'load' });
  await pg2.evaluate(() => document.fonts.ready);
  await pg2.waitForFunction(() => window.__done === true);
  const r2 = await qa(pg2);
  await pg2.pdf({ path: dir + '/ck.pdf', preferCSSPageSize: true, printBackground: true });
  console.log(JSON.stringify({ akt: r1, cheklist: r2 }));
} else if (mode === 'og') {
  const [img1, img2, out] = rest;
  const FONT = new URL('../../fonts/inter-ru-wght-normal.woff2', import.meta.url).href;
  const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  const html = `<html><head><style>
@font-face{font-family:Inter;font-weight:100 900;src:url(${FONT})}
body{margin:0;width:1200px;height:630px;overflow:hidden;background:radial-gradient(700px 420px at 80% 30%,rgba(124,134,255,.28),rgba(0,0,0,0) 70%),#000;font-family:Inter;color:#fff;position:relative}
.l{position:absolute;left:72px;top:70px;width:640px}
.brand{display:flex;align-items:center;gap:14px;font-weight:600;font-size:26px;letter-spacing:-.02em}
.brand small{font-size:14px;color:#7c86ff;letter-spacing:.12em;font-weight:500;margin-left:6px}
h1{font-weight:300;font-size:64px;line-height:1.04;letter-spacing:-.05em;margin:62px 0 0}
h1 em{font-style:normal;color:#7c86ff}
p{font-size:22px;color:#9f9fa9;margin:24px 0 0;line-height:1.4}
.tags{display:flex;gap:10px;margin-top:32px}.tags span{border:1px solid rgba(255,255,255,.18);border-radius:99px;padding:9px 16px;font-size:17px;color:#e4e4e7}
.tags span.y{background:#fdc700;color:#09090b;border-color:#fdc700;font-weight:600}
.d1,.d2{position:absolute;width:320px;border-radius:8px;box-shadow:0 30px 70px rgba(0,0,0,.6)}
.d2{right:60px;top:130px;transform:rotate(6deg);opacity:.92}
.d1{right:190px;top:72px;transform:rotate(-4deg)}
</style></head><body>
<div class="l"><div class="brand"><svg width="52" height="52" viewBox="0 0 48 48"><circle cx="24" cy="24" r="23" fill="#09090b" stroke="rgba(255,255,255,.25)"/><g transform="translate(12 12)" fill="none" stroke-width="1.6" stroke-linejoin="round"><path d="M12 2.5l7.5 3v6c0 5-3.2 8.6-7.5 10-4.3-1.4-7.5-5-7.5-10v-6z" stroke="#fff"/><circle cx="12" cy="11.5" r="2.6" stroke="#7c86ff"/><path d="M12 6.2v2.7M12 14.1v2.7M6.8 11.5h2.6M14.6 11.5h2.6" stroke="#7c86ff"/></g></svg>ПЕСТКОНТРОЛЬ<small>ЦЕНТР</small></div>
<h1>Документы<br>для <em>Роспотребнадзора</em></h1>
<p>Полный перечень к проверке: 8 групп, кто готовит,<br>сборщик папки для 14 типов объектов</p>
<div class="tags"><span class="y">Чек-лист PDF</span><span>Образец акта</span><span>2026</span></div></div>
<img class="d2" src="file://${img2}"><img class="d1" src="file://${img1}">
</body></html>`;
  fs.writeFileSync(dir + '/og.html', html);
  await p.goto('file://' + dir + '/og.html');
  await p.waitForTimeout(400);
  await p.screenshot({ path: out, type: 'jpeg', quality: 84 });
  console.log('og', out);
}
await b.close();
