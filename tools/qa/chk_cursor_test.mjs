// Курсор над чекбоксами и вариантами ответа (tools/site/chk_cursor.py, вариант А, 20.11.2026).
//   python3 -m http.server 8765  (в корне репозитория), затем: node tools/qa/chk_cursor_test.mjs [база]
// Компьютер 1440×900 (мышь): над каждым видимым чекбоксом самопроверки и вариантом опросного листа ППК системный курсор
// скрыт (cursor:none), фирменное кольцо видно (opacity 1); над текстом пункта — то же; квадрат подсвечен (box-shadow).
// В облегчённом режиме (?fx=lite) — обычная рука. Поля для текста по-прежнему с курсором text. Телефон 390×844 (касание): класса has-cursor нет, у пунктов нет подсветки,
// размеры блока самопроверки — как без строки chk-cur. Запросы к сторонним адресам (счётчики) отменяются.
// Пакет Timeweb: PREVIEW=0 PKG=tools/deploy/chk-cursor-2026-11-20/pkg node tools/qa/chk_cursor_test.mjs https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai
import { chromium } from 'playwright';
const BASE = (process.argv[2] || 'http://localhost:8765').replace(/\/$/, '');
const PAGES = ['biznes-tsentry-torgovye-tsentry-predpriyatiya', 'deratizatsiya', 'dezinsektsiya', 'farmatsevticheskie-proizvodstva',
  'gostinitsy', 'magaziny-i-torgovye-seti', 'materialy/pest-menedzhment-ili-razovaya-obrabotka', 'materialy/programma-pest-kontrolya',
  'materialy/zhurnal-pest-kontrolya', 'ochistka-dezinfektsiya-ventilyatsii', 'pishchevoe-proizvodstvo', 'restorany-i-kafe',
  'sklady-i-logistika', 'zashchita-ot-proniknoveniya-gryzunov', 'razrabotka-ppk#oprosnyy-online',
  ...(process.env.PREVIEW === '0' ? [] : ['preview-kamera-ventilyatsii'])]; // preview-services/zashchita… — старое превью без нарисованного курсора (там обычная рука)
const only = process.env.ONLY ? PAGES.filter(p => p.includes(process.env.ONLY)) : PAGES;
const host = new URL(BASE).host;
const b = await chromium.launch();
const bad = []; let n = 0;
async function open(ctx, slug, q = '?fx=full') {
  const p = await ctx.newPage();
  await p.route(r => new URL(r).host !== host, r => r.abort());
  if (process.env.PKG) { // страницы пакета Timeweb вместо страниц сайта: PKG=<папка pkg>, база — рабочий сайт
    const fs = await import('fs');
    await p.route(r => { const u = new URL(r); return u.host === host && /\/$/.test(u.pathname); }, async r => {
      const f = process.env.PKG + decodeURI(new URL(r.request().url()).pathname) + 'index.php';
      if (!fs.existsSync(f)) return r.continue();
      await r.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: fs.readFileSync(f) });
    });
  }
  const [path, hash] = slug.split('#');
  for (let i = 0; i < 6; i++) {
    const r = await p.goto(BASE + '/' + path + '/' + q + (hash ? '#' + hash : ''), { waitUntil: 'domcontentloaded', timeout: 90000 }).catch(() => null);
    if (r && r.status() === 200) {
      await p.waitForTimeout(2500);
      // ложные 502 Timeweb из облака бывают и на app.min.js — тогда курсор не включается: открыть заново
      const ok = q !== '?fx=full' || ctx._mobile || await p.evaluate(() => document.documentElement.classList.contains('has-cursor'));
      if (ok) break;
    }
    if (i === 5) throw new Error(slug + ': не открылась');
    await p.waitForTimeout(3000);
  }
  await p.addStyleTag({ content: '[data-fade],.panel{opacity:1!important;transform:none!important}' });
  return p;
}
const state = (p, x, y) => p.evaluate(([x, y]) => {
  const t = document.elementFromPoint(x, y), ring = document.querySelector('.cursor-ring');
  const inp = t && (t.closest('label') || t).querySelector ? ((t.closest('label') || t).querySelector('input') || t) : t;
  return { tag: t && t.tagName, native: t && getComputedStyle(t).cursor, ring: ring && getComputedStyle(ring).opacity,
    shadow: inp && getComputedStyle(inp).boxShadow };
}, [x, y]);
for (const slug of only) try {
  // компьютер
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const p = await open(ctx, slug);
  if (!(await p.evaluate(() => document.documentElement.classList.contains('has-cursor')))) bad.push(slug + ': нет has-cursor');
  const els = await p.$$('.f-check-list input, .rp-chip>input');
  let k = 0;
  for (const el of els) {
    if (!(await el.evaluate(e => !!e.offsetParent && e.getBoundingClientRect().width > 0))) continue;
    await el.evaluate(e => e.scrollIntoView({ block: 'center' }));
    await p.waitForTimeout(80);
    const bx = await el.boundingBox();
    const pts = [[bx.x + bx.width / 2, bx.y + bx.height / 2, 'квадрат']];
    const txt = await el.evaluateHandle(e => e.closest('.f-check-list') ? e.closest('label').querySelector('span') : null);
    const tb = txt.asElement() ? await txt.asElement().boundingBox() : null;
    if (tb) pts.push([tb.x + Math.min(60, tb.width / 2), tb.y + Math.min(10, tb.height / 2), 'текст']);
    for (const [x, y, what] of pts) {
      await p.mouse.move(x - 30, y - 20); await p.mouse.move(x, y, { steps: 4 }); await p.waitForTimeout(420);
      const s = await state(p, x, y); n++;
      const isChk = slug.indexOf('razrabotka') < 0;
      if (s.native !== 'none' || s.ring !== '1' || (isChk && what === 'квадрат' && s.shadow === 'none'))
        bad.push(`${slug} #${k} ${what}: курсор ${s.native}, кольцо ${s.ring}, подсветка ${s.shadow}`);
    }
    k++;
  }
  const field = await p.$('form input[type=tel], form input[type=text], form textarea');
  if (field && await field.evaluate(e => !!e.offsetParent)) {
    const c = await field.evaluate(e => getComputedStyle(e).cursor);
    if (c !== 'text') bad.push(slug + ': поле для текста с курсором ' + c);
  }
  console.log(`${slug}: компьютер — ${k} пунктов`);
  await ctx.close();
  // облегчённый режим (?fx=lite, сам включается при просадке кадров): нарисованного курсора нет — обычная рука, не «палочка»
  const lc = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const l = await open(lc, slug, '?fx=lite');
  const lr = await l.evaluate(() => [...document.querySelectorAll('.f-check-list input,.rp-chip>input')].map(e => getComputedStyle(e).cursor));
  if (!lr.length || lr.some(c => c !== 'pointer')) bad.push(slug + ': облегчённый режим: ' + [...new Set(lr)].join(','));
  await lc.close();
  // телефон
  if (slug.indexOf('razrabotka') < 0) {
    const m = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 }); m._mobile = true;
    const q = await open(m, slug);
    const r = await q.evaluate(() => {
      const box = () => { const e = document.querySelector('.f-check'); const r = e.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; };
      const a = box(), sh = getComputedStyle(document.querySelector('.f-check-list input')).boxShadow;
      document.getElementById('chk-cur')?.remove(); const z = box();
      return { cur: document.documentElement.classList.contains('has-cursor'), a, z, sh };
    });
    if (r.cur || r.a.join() !== r.z.join() || r.sh !== 'none') bad.push(`${slug}: телефон ${JSON.stringify(r)}`);
    await m.close();
  }
} catch (e) { bad.push(slug + ': ' + e.message.split('\n')[0]); }
await b.close();
console.log(`проверок: ${n}, нарушений: ${bad.length}`);
bad.forEach(x => console.log('  ' + x));
process.exit(bad.length ? 1 : 0);
