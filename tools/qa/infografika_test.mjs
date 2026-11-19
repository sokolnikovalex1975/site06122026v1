// Инфографика в стиле лаборатории (tools/site/infografika.py, команда владельца 19.11.2026).
//   BASE=http://127.0.0.1:8080 [SHOTS=папка] [WIDTHS="390 700 1440"] [TRIES=3] node tools/qa/infografika_test.mjs [/путь/ ...]
// TRIES — попыток открыть страницу: рабочий сайт отвечает облачным адресам ложным 502 примерно на половину запросов
// (из Москвы и Германии в это время 200 — check-host.net, 19.11.2026), для рабочего сайта ставить TRIES=8.
// На каждой странице и ширине: страница не шире экрана; строка <style id="ig"> на месте; каждая иконка ig-*.webp и
// lab-*.webp в блоках загрузилась (naturalWidth > 0), видна, размер на экране не больше файла (без размытия ×1);
// на телефоне (до 760 px) у иконок и их блоков нет затемнения (opacity 1, без brightness/фильтров затемнения) —
// закон владельца 17.11.2026; сдвиги вёрстки (CLS) при загрузке и прокрутке не больше 0,02. С SHOTS — снимки блоков.
// Иконки в скрытой вкладке (hidden) не проверяются.
// Запросы к Метрике, UIS и Radist отменяются. Код выхода 1 при нарушениях.
import { chromium } from 'playwright';
import fs from 'fs';
const BASE = process.env.BASE || 'http://127.0.0.1:8080';
const SHOTS = process.env.SHOTS || '';
const WIDTHS = (process.env.WIDTHS || '390 700 1440').split(' ').map(Number);
const TRIES = Number(process.env.TRIES || 3);
const ALL = ['/', '/dezinfektsiya/', '/deratizatsiya/', '/zashchita-ot-proniknoveniya-gryzunov/', '/dezinsektsiya/',
  '/deratizatsiya-i-dezinsektsiya/', '/dogovor-deratizatsiya-dezinsektsiya/', '/sanitarnyy-audit/', '/razrabotka-ppk/',
  '/laboratornye-issledovaniya/', '/ochistka-dezinfektsiya-ventilyatsii/', '/pishchevoe-proizvodstvo/', '/restorany-i-kafe/',
  '/magaziny-i-torgovye-seti/', '/gostinitsy/', '/farmatsevticheskie-proizvodstva/', '/sklady-i-logistika/',
  '/biznes-tsentry-torgovye-tsentry-predpriyatiya/', '/materialy/', '/materialy/programma-pest-kontrolya/',
  '/materialy/zhurnal-pest-kontrolya/', '/materialy/pest-menedzhment-ili-razovaya-obrabotka/',
  '/materialy/programma-proizvodstvennogo-kontrolya-haccp/', '/normativnaya-baza/', '/normativnaya-baza/proverochnye-listy/',
  '/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/', '/normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/',
  '/materialy/akt-deratizatsii-i-dezinsektsii/', '/materialy/skhema-tochek-pest-kontrolya/', '/dezinsektsiya/restorany-i-kafe/',
  '/deratizatsiya/restorany-i-kafe/', '/laboratornye-issledovaniya/analiz-smyvov/', '/laboratornye-issledovaniya/izmerenie-mikroklimata/',
  '/laboratornye-issledovaniya/zamer-osveshchennosti/', '/laboratornye-issledovaniya/analiz-vozdukha-rabochey-zony/',
  '/laboratornye-issledovaniya/analiz-pishchevykh-produktov/', '/laboratornye-issledovaniya/analiz-vody/',
  '/laboratornye-issledovaniya/kontrol-sterilizatorov/', '/materialy/kak-berut-smyvy/', '/materialy/zamer-osveshchennosti-i-mikroklimata/',
  '/materialy/kontrol-raboty-sterilizatorov/'];
const PAGES = process.argv.slice(2).length ? process.argv.slice(2) : ALL;
// блоки для снимков: селектор контейнера
const BLOCKS = { '01-vse-uslugi': '.s-vu .vu-grid', '02-tseny': '.s-pr .pr-cards', '02-drugie': '.s-pr .pr-more',
  '03-shagi': '.ig-steps, .proof-steps.ig-cards', '04-dokumenty': '.docs', '05-sostav': '.v-parts', '06-sa': '.sa-inds',
  '06-otrasli': '.dzf-inds, .v-inds', '06-obekty': '.rp-obj', '07-papka': 'table:has(.ig-row)', '08-krug': '.cycle',
  '09-vrediteli': '.pests', '10-gruppy': '.dk-gs' };
const b = await chromium.launch();
const errors = [];
let shots = 0;
for (const pg of PAGES) for (const w of WIDTHS) {
  const mob = w <= 760;
  const ctx = await b.newContext({ viewport: { width: w, height: mob ? 844 : 900 }, isMobile: w < 900, hasTouch: w < 900,
    deviceScaleFactor: SHOTS && mob ? 2 : 1, reducedMotion: 'reduce' });
  await ctx.route(/mc\.yandex|uiscom|comagic|radist|googletagmanager/, r => r.abort());
  const p = await ctx.newPage();
  await p.addInitScript(() => { window.__cls = 0; new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({ type: 'layout-shift', buffered: true }); });
  let ok = false;
  for (let i = 0; i < TRIES && !ok; i++) { const r = await p.goto(BASE + pg, { waitUntil: 'load', timeout: 45000 }).catch(() => null); ok = !!r && r.status() === 200; }
  if (!ok) { errors.push(`${w} ${pg}: страница не открылась`); await ctx.close(); continue; }
  const H = await p.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < H; y += 600) { await p.evaluate(yy => window.scrollTo(0, yy), y); await p.waitForTimeout(40); }
  await p.evaluate(() => Promise.race([Promise.all([...document.images].filter(i => /\/(ig|lab)-/.test(i.src)).map(i => { i.loading = 'eager'; return i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; }); })), new Promise(r => setTimeout(r, 8000))]));
  await p.waitForTimeout(300);
  const m = await p.evaluate((mob) => {
    const out = { vw: document.documentElement.clientWidth, sw: document.documentElement.scrollWidth, style: !!document.getElementById('ig'), cls: window.__cls, bad: [] };
    const sel = '.s-vu .vu-ic img, .ig-pr, .ig-prm, .ig-step-ic, .docs .doc .ico img, .ig-v, .sa-inds .sa-ico img, .ig-ind, .rp-ico img, .ig-row>img, .cycle .node>i img, .pest-img.ig-pi img, .ig-g';
    const imgs = [...document.querySelectorAll(sel)].filter(i => !i.closest('[hidden]'));  // вкладка «Нашли вредителей» скрыта до выбора
    out.n = imgs.length;
    for (const i of imgs) {
      const r = i.getBoundingClientRect();
      const name = i.getAttribute('src').split('/').pop();
      if (!i.complete || !i.naturalWidth) out.bad.push(name + ': не загрузилась');
      else if (r.width < 20 || r.height < 20) out.bad.push(name + `: не видна (${Math.round(r.width)}×${Math.round(r.height)})`);
      else if (r.width > i.naturalWidth + 0.5) out.bad.push(name + `: шире файла (${Math.round(r.width)} > ${i.naturalWidth})`);
      if (mob) {
        for (let e = i; e && e !== document.body; e = e.parentElement) {
          const cs = getComputedStyle(e);
          if (parseFloat(cs.opacity) < 1 || /brightness|contrast|grayscale|opacity/.test(cs.filter)) { out.bad.push(name + ': затемнение у ' + (e.className || e.tagName)); break; }
        }
      }
    }
    return out;
  }, mob);
  if (m.sw > m.vw) errors.push(`${w} ${pg}: прокрутка вбок ${m.sw} > ${m.vw}`);
  if (!m.style) errors.push(`${w} ${pg}: нет <style id="ig">`);
  if (!m.n) errors.push(`${w} ${pg}: нет иконок`);
  if (m.cls > 0.02) errors.push(`${w} ${pg}: CLS ${m.cls.toFixed(3)}`);
  for (const x of [...new Set(m.bad)]) errors.push(`${w} ${pg}: ${x}`);
  console.log(`${w} ${pg}: иконок ${m.n}, CLS ${m.cls.toFixed(3)}${m.bad.length ? ', замечаний ' + m.bad.length : ''}`);
  if (SHOTS) {
    await p.addStyleTag({ content: '*{animation:none!important;transition:none!important}[data-fade],[data-split],[data-group]>*{opacity:1!important;transform:none!important;filter:none!important}' });
    fs.mkdirSync(SHOTS, { recursive: true });
    for (const [id, s] of Object.entries(BLOCKS)) {
      const els = await p.$$(s);
      for (const [k, el] of els.entries()) {
        const box = await el.boundingBox();
        if (!box || box.height < 10) continue;
        await el.scrollIntoViewIfNeeded();
        await p.waitForTimeout(150);
        const name = `${(pg.replace(/\//g, '_').replace(/^_|_$/g, '') || 'glavnaya')}__${id}${els.length > 1 ? '-' + (k + 1) : ''}__${w}.png`;
        await el.screenshot({ path: `${SHOTS}/${name}` }).catch(e => errors.push(`${w} ${pg} ${id}: снимок ${e.message}`));
        shots++;
      }
    }
  }
  await ctx.close();
}
await b.close();
console.log(errors.length ? `ЗАМЕЧАНИЯ (${errors.length}):\n` + errors.join('\n') : `OK: страниц ${PAGES.length}, ширин ${WIDTHS.length}, без замечаний${SHOTS ? ', снимков ' + shots : ''}`);
process.exit(errors.length ? 1 : 0);
