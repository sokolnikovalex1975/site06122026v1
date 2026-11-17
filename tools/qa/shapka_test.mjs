// Проверка 17.11.2026: компактная закреплённая шапка (решение владельца после разбора удобства 13.11.2026).
// Запуск: BASE=http://127.0.0.1:8090 node tools/qa/shapka_test.mjs   (по умолчанию — рабочий сайт)
// PKG=<папка pkg пакета> — подставить страницы (index.php), app.min.js, style.css и legal.css пакета вместо файлов сайта.
// QUICK=1 — без обхода всех страниц из sitemap.xml (только подробные проверки); PARTS=1,5 — только эти разделы;
// VERBOSE=1 — печатать строки сразу.
// Ожидание:
//  1. Компьютер и планшет (шире 760 px и выше 500 px): в начале страницы шапка в полный рост (clamp(68px, 6vw, 115px)
//     и линия 1 px), после 30 px прокрутки — компактная: 65 px (от 1281 px) или 61 px (761–1280 px), фон rgba(9,9,11,.94).
//     При чтении вниз, медленной прокрутке вверх (2 px за событие) и снова вниз шапка всегда видна.
//  2. Телефон (до 760 px) и низкое окно (до 500 px): компактная — 57 px; уходит после 48 px прокрутки вниз подряд
//     (если прокручено больше 400 px), дрожание ±6 px её не трогает, возвращается после 24 px медленной прокрутки вверх
//     (2 px за событие), в первых 120 px видна всегда; при открытом меню не уходит.
//  3. Элементы шапки не налезают друг на друга и не выходят за окно (320–1920 px), горизонтальной прокрутки нет —
//     в полный рост и компактная.
//  4. Выпадающий список (компьютер, компактная шапка): наведение открывает его через 0,15 с, а не сразу; панель
//     под шапкой и в пределах окна, при переходе мыши на панель не закрывается.
//  5. Фокус клавиатуры (Tab вглубь страницы) не уходит под шапку.
//  6. «Цена» в шапке: прокрутка к блоку за 0,8 с (не дольше 1,4 с вместе с запуском), шапка видна и компактная,
//     начало блока ниже шапки.
//  7. Закреплённые блоки страниц (оглавления, план «Схемы объекта» и др., position: sticky) не уходят под шапку.
//  8. «Уменьшение движения» — шапка меняет размер сразу, без анимации.
//  9. Все страницы sitemap.xml (компьютер 1440 и телефон 390): нет ошибок JavaScript и горизонтальной прокрутки,
//     шапка компактная после прокрутки, на компьютере не уходит, на телефоне уходит и возвращается.
// Счётчики в тесте не загружаются (запросы к Метрике, UIS и Radist обрываются). Код выхода 1, если есть нарушения.
import { chromium } from 'playwright';
import fs from 'fs';

const BASE = (process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai').replace(/\/$/, '');
const PKG = process.env.PKG || '';
const QUICK = !!process.env.QUICK;
const PARTS = (process.env.PARTS || '').split(',').filter(Boolean).map(Number);
const want = (n) => !PARTS.length || PARTS.includes(n);
const BLOCK = /mc\.yandex|uiscom|comagic|radist|yandex\.ru\/metrika|mc\.webvisor/;
const PAGES = ['/', '/deratizatsiya/', '/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/', '/privacy/'];

let bad = 0;
const lines = [];
const line = (ok, s) => { if (!ok) bad++; const t = `${ok ? 'OK ' : 'НЕТ'} ${s}`; lines.push(t); if (process.env.VERBOSE) console.log(t); };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const route = async (ctx) => {
  await ctx.route('**/*', (r) => {
    const u = r.request().url();
    if (BLOCK.test(u)) return r.abort();
    const path = u.startsWith(BASE + '/') ? decodeURI(u.slice(BASE.length + 1).split('?')[0].split('#')[0]) : null;
    if (PKG && path !== null) {
      if (['app.min.js', 'style.css', 'legal.css'].includes(path) && fs.existsSync(`${PKG}/${path}`)) return r.fulfill({ status: 200,
        body: fs.readFileSync(`${PKG}/${path}`), contentType: path.endsWith('.js') ? 'application/javascript; charset=utf-8' : 'text/css; charset=utf-8' });
      if ((path === '' || path.endsWith('/')) && fs.existsSync(`${PKG}/${path}index.php`))
        return r.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: fs.readFileSync(`${PKG}/${path}index.php`) });
    }
    return r.continue();
  });
};
const newCtx = async (browser, w, h, mob, extra = {}) => {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob, deviceScaleFactor: 1, ...extra });
  await ctx.addInitScript(() => { try { sessionStorage.setItem('pc-intro', '1'); } catch (e) {} });
  await route(ctx);
  return ctx;
};
const open = async (page, url) => {
  for (let k = 0; ; k++) {
    try { const res = await page.goto(url, { waitUntil: 'load', timeout: 90000 }); if (res && res.status() >= 500) throw new Error('HTTP ' + res.status()); return; }
    catch (e) { if (k >= 3) throw e; await sleep(3000); }
  }
};
const st = (page) => page.evaluate(() => {
  const h = document.getElementById('hdr'), r = h.getBoundingClientRect(), cs = getComputedStyle(h);
  return { y: Math.round(scrollY), hide: h.classList.contains('hide'), scrolled: h.classList.contains('scrolled'),
    top: Math.round(r.top), bottom: Math.round(r.bottom), hh: Math.round(r.height), bg: cs.backgroundColor,
    hc: parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--hdr-c')) || 0,
    docW: document.documentElement.scrollWidth, iw: innerWidth, ih: innerHeight };
});
// прокрутка «пальцем»: по шагу за кадр, у каждого шага своё событие scroll
const steps = (page, step, n) => page.evaluate(async ([step, n]) => {
  for (let i = 0; i < n; i++) { window.scrollBy({ top: step, left: 0, behavior: 'instant' }); await new Promise((r) => requestAnimationFrame(() => r())); }
  await new Promise((r) => setTimeout(r, 60));
}, [step, n]);
const fullH = (w) => Math.round(Math.min(115, Math.max(68, w * 0.06)) + 1);
const compactH = (w, h) => (w <= 760 ? 57 : w <= 1280 ? 61 : 65);
const away = (w, h) => w <= 760 || h <= 500;
const errsOf = (page) => { const errs = []; page.on('pageerror', (e) => errs.push(String(e).slice(0, 160))); return errs; };

// наложения в шапке: видимые элементы попарно не пересекаются, не выходят за окно и за шапку
const overlap = (page) => page.evaluate(() => {
  const hdr = document.getElementById('hdr'), hr = hdr.getBoundingClientRect();
  const els = [...hdr.querySelectorAll('.logo, .nav > a, .nav-dd-btn, .srch-btn, .phone, .hdr-right > .btn, #burger')].filter((el) => {
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
  });
  const probs = [];
  const name = (el) => (el.className && typeof el.className === 'string' ? el.className.split(' ')[0] : el.tagName) + (el.textContent.trim() ? '«' + el.textContent.trim().slice(0, 14) + '»' : '');
  els.forEach((a, i) => {
    const r = a.getBoundingClientRect();
    if (r.left < -0.5 || r.right > innerWidth + 0.5) probs.push(name(a) + ' за краем окна');
    if (r.top < hr.top - 1 || r.bottom > hr.bottom + 1) probs.push(name(a) + ' выше или ниже шапки');
    els.slice(i + 1).forEach((b) => {
      const q = b.getBoundingClientRect();
      if (a.contains(b) || b.contains(a)) return;
      if (r.left < q.right - 1 && q.left < r.right - 1 && r.top < q.bottom - 1 && q.top < r.bottom - 1) probs.push(name(a) + ' и ' + name(b) + ' налезают');
    });
  });
  return { n: els.length, probs, docW: document.documentElement.scrollWidth, iw: innerWidth, hh: Math.round(hr.height) };
});

const browser = await chromium.launch();

// ---------- 1, 2. поведение шапки при прокрутке ----------
const VP = [['компьютер 1920×1080', 1920, 1080, false], ['компьютер 1440×900', 1440, 900, false], ['ноутбук 1366×768', 1366, 768, false],
  ['ноутбук 1280×800', 1280, 800, false], ['планшет 1024×768', 1024, 768, true], ['планшет 768×1024', 768, 1024, true],
  ['телефон 390×844', 390, 844, true], ['телефон 320×568', 320, 568, true], ['телефон лёжа 844×390', 844, 390, true],
  ['окно 1440×480 (масштаб)', 1440, 480, false]];
for (const [vn, w, h, mob] of want(1) ? VP : []) {
  const ctx = await newCtx(browser, w, h, mob);
  for (const path of (w === 1440 && h === 900) || w === 390 ? PAGES : PAGES.slice(0, 2)) {
    const page = await ctx.newPage(); const errs = errsOf(page);
    try {
      await open(page, BASE + path); await sleep(1500);
      const t0 = await st(page);
      const notes = [];
      let ok = !t0.scrolled && !t0.hide && t0.top === 0 && Math.abs(t0.hh - fullH(w)) <= 1;
      notes.push(`в начале ${t0.hh} px${ok ? '' : ' (нужно ' + fullH(w) + ', видна)'}`);
      if (!away(w, h)) {
        // колесо: вниз 3000 px, медленно вверх 80 px, снова вниз
        await page.mouse.move(w / 2, h / 2);
        for (let i = 0; i < 30; i++) { await page.mouse.wheel(0, 100); await sleep(40); }
        await sleep(900);
        const a = await st(page);
        for (let i = 0; i < 40; i++) { await page.mouse.wheel(0, -2); await sleep(16); }
        await sleep(600);
        const b = await st(page);
        for (let i = 0; i < 10; i++) { await page.mouse.wheel(0, 100); await sleep(40); }
        await sleep(900);
        const c = await st(page);
        const okA = [a, b, c].every((m) => m.scrolled && !m.hide && m.top === 0 && m.hh === compactH(w, h)) && a.y > 1500;
        const okBg = a.bg.replace(/\s/g, '') === 'rgba(9,9,11,0.94)' || a.bg.replace(/\s/g, '') === 'rgba(0,0,0,0.92)'; // lowfx — #000000eb
        ok = ok && okA && okBg;
        notes.push(`после прокрутки ${a.hh} px (нужно ${compactH(w, h)}), видна: вниз ${!a.hide && a.top === 0 ? 'да' : 'НЕТ'}, медленно вверх ${!b.hide && b.top === 0 ? 'да' : 'НЕТ'}, снова вниз ${!c.hide && c.top === 0 ? 'да' : 'НЕТ'}; фон ${a.bg}`);
      } else {
        // палец: вниз до 300 px — видна; до 500 px — уходит; дрожание ±6 — не возвращается; 22 px вверх — нет; 26 px — да
        await steps(page, 10, 30); const a = await st(page);
        await steps(page, 10, 20); await sleep(450); const b = await st(page);
        for (let i = 0; i < 10; i++) { await steps(page, -6, 1); await steps(page, 6, 1); }
        const c = await st(page);
        await steps(page, -2, 11); const d = await st(page);
        await steps(page, -2, 2); await sleep(450); const e = await st(page);
        for (let i = 0; i < 10; i++) { await steps(page, 6, 1); await steps(page, -6, 1); }
        const f = await st(page);
        await steps(page, 10, 4); const g = await st(page);
        await steps(page, 10, 2); const g2 = await st(page);
        await page.evaluate(() => window.scrollTo({ top: 100, behavior: 'instant' })); await sleep(100);
        await steps(page, 1, 15); const k = await st(page);
        const okS = a.y >= 290 && !a.hide && a.scrolled && a.hh === compactH(w, h) && b.hide && b.bottom <= 0 && c.hide && d.hide && !e.hide && e.top === 0 &&
          !f.hide && !g.hide && g2.hide && !k.hide;
        ok = ok && okS;
        notes.push(`компактная ${a.hh} px (нужно ${compactH(w, h)}); вниз до ${b.y}: ${b.hide && b.bottom <= 0 ? 'ушла' : 'НЕ УШЛА'}; дрожание: ${c.hide ? 'не вернулась' : 'ВЕРНУЛАСЬ'};` +
          ` вверх 22 px: ${d.hide ? 'нет' : 'ВЕРНУЛАСЬ РАНО'}, 26 px: ${!e.hide && e.top === 0 ? 'вернулась' : 'НЕ ВЕРНУЛАСЬ'}; дрожание у видимой: ${f.hide ? 'УШЛА' : 'на месте'};` +
          ` вниз 40 px: ${g.hide ? 'УШЛА РАНО' : 'на месте'}, 60 px: ${g2.hide ? 'ушла' : 'НЕ УШЛА'}; у начала (${k.y} px): ${k.hide ? 'СКРЫТА' : 'видна'}`);
        if (w <= 760 && path === '/') { // меню открыто — шапка на месте
          await page.evaluate(() => window.scrollTo({ top: 2000, behavior: 'instant' })); await sleep(300);
          await steps(page, -30, 1); await sleep(400);
          await page.locator('#burger').tap(); await sleep(700);
          await steps(page, 15, 10); await sleep(300);
          const m = await st(page);
          await page.locator('#burger').tap(); await sleep(900);
          ok = ok && !m.hide && m.top === 0;
          notes.push(`меню открыто: шапка ${!m.hide && m.top === 0 ? 'на месте' : 'УШЛА'}`);
        }
      }
      const end = await st(page);
      ok = ok && !errs.length && end.docW <= end.iw;
      line(ok, `${vn} ${path}: ${notes.join('; ')}${end.docW > end.iw ? '; ГОРИЗОНТАЛЬНАЯ ПРОКРУТКА ' + end.docW : ''}${errs.length ? '; JS: ' + errs.join(' | ') : ''}`);
    } catch (e) { line(false, `${vn} ${path}: ${String(e).slice(0, 200)}`); }
    await page.close();
  }
  await ctx.close();
}

// ---------- 3. наложения в шапке ----------
for (const [w, mob] of want(3) ? [[320, true], [360, true], [390, true], [414, true], [768, true], [1024, true], [1280, false], [1281, false], [1366, false], [1440, false], [1600, false], [1920, false]] : []) {
  const ctx = await newCtx(browser, w, 900, mob);
  for (const path of ['/', '/deratizatsiya/']) {
    const page = await ctx.newPage(); const errs = errsOf(page);
    try {
      await open(page, BASE + path); await sleep(1200);
      const a = await overlap(page);
      await page.evaluate(() => window.scrollTo({ top: 600, behavior: 'instant' })); await sleep(700);
      const b = await overlap(page);
      const ok = !a.probs.length && !b.probs.length && a.docW <= a.iw && b.docW <= b.iw && !errs.length && b.hh === compactH(w, 900);
      line(ok, `${w} px ${path}: элементов шапки ${a.n}/${b.n}, в полный рост ${a.hh} px ${a.probs.length ? a.probs.join(', ') : 'без наложений'}, компактная ${b.hh} px ${b.probs.length ? b.probs.join(', ') : 'без наложений'}` +
        `${Math.max(a.docW, b.docW) > w ? '; ГОРИЗОНТАЛЬНАЯ ПРОКРУТКА' : ''}${errs.length ? '; JS: ' + errs.join(' | ') : ''}`);
    } catch (e) { line(false, `${w} px ${path}: ${String(e).slice(0, 200)}`); }
    await page.close();
  }
  await ctx.close();
}

// ---------- 4. выпадающий список, 5. фокус, 6. «Цена», 7. закреплённые блоки — компьютер 1440×900 ----------
{
  const ctx = await newCtx(browser, 1440, 900, false);
  // 4
  for (const path of want(4) ? ['/', '/deratizatsiya/'] : []) {
    const page = await ctx.newPage(); const errs = errsOf(page);
    try {
      await open(page, BASE + path); await sleep(1200);
      await page.evaluate(() => window.scrollTo({ top: 1200, behavior: 'instant' })); await sleep(700);
      const btn = page.locator('.nav-dd-btn').first();
      const bb = await btn.boundingBox();
      await page.mouse.move(bb.x + bb.width / 2, bb.y + bb.height / 2);
      const vis = () => page.evaluate(() => { const p = document.querySelector('.nav-dd .nav-dd-panel'), s = getComputedStyle(p), r = p.getBoundingClientRect(), h = document.getElementById('hdr').getBoundingClientRect();
        return { v: s.visibility === 'visible' && parseFloat(s.opacity) > 0.5, top: Math.round(r.top), bottom: Math.round(r.bottom), left: Math.round(r.left), right: Math.round(r.right), hb: Math.round(h.bottom) }; });
      await sleep(60); const early = await vis();
      await sleep(600); const late = await vis();
      // мышь вниз на панель — список не закрывается
      await page.mouse.move(bb.x + bb.width / 2, late.top + 30, { steps: 8 }); await sleep(400);
      const inPanel = await vis();
      await page.mouse.move(700, 600); await sleep(800);
      const closed = await vis();
      const ok = !early.v && late.v && inPanel.v && !closed.v && late.top >= late.hb - 8 && late.bottom <= 900 && late.left >= 0 && late.right <= 1440 && !errs.length;
      line(ok, `1440 ${path} список «Услуги» в компактной шапке: через 0,06 с ${early.v ? 'УЖЕ ОТКРЫТ' : 'ещё закрыт'}, через 0,66 с ${late.v ? 'открыт' : 'НЕ ОТКРЫТ'}` +
        ` (верх панели ${late.top}, низ шапки ${late.hb}), мышь на панели — ${inPanel.v ? 'открыт' : 'ЗАКРЫЛСЯ'}, мышь ушла — ${closed.v ? 'НЕ ЗАКРЫЛСЯ' : 'закрыт'}${errs.length ? '; JS: ' + errs.join(' | ') : ''}`);
    } catch (e) { line(false, `1440 ${path} список: ${String(e).slice(0, 200)}`); }
    await page.close();
  }
  // 5
  for (const path of want(5) ? ['/deratizatsiya/', '/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/'] : []) {
    const page = await ctx.newPage(); const errs = errsOf(page);
    try {
      await open(page, BASE + path); await sleep(1200);
      let hidden = 0, checked = 0, worst = '';
      for (let i = 0; i < 90; i++) {
        await page.keyboard.press('Tab'); await sleep(i < 10 ? 40 : 90);
        const r = await page.evaluate(() => {
          const el = document.activeElement, hdr = document.getElementById('hdr');
          if (!el || el === document.body || hdr.contains(el) || el.closest('#mmenu')) return null;
          const q = el.getBoundingClientRect(), h = hdr.getBoundingClientRect();
          if (!q.width && !q.height) return null;
          const s = getComputedStyle(el); if (s.visibility === 'hidden') return null;
          return { top: q.top, bottom: q.bottom, hb: h.bottom, ht: h.top, txt: (el.textContent || el.getAttribute('aria-label') || el.tagName).trim().slice(0, 30) };
        });
        if (!r) continue;
        await sleep(450); // плавная прокрутка браузера к элементу
        // под шапкой — если в точках элемента сверху лежит шапка (ссылка «Перейти к содержанию» — поверх шапки, это верно)
        const q = await page.evaluate(() => {
          const el = document.activeElement, hdr = document.getElementById('hdr'), r = el.getBoundingClientRect();
          const xs = [r.left + 4, r.left + r.width / 2, r.right - 4].map((x) => Math.min(innerWidth - 1, Math.max(0, x)));
          const ys = [r.top + 2, r.top + r.height / 2, r.bottom - 2].filter((y) => y >= 0 && y < innerHeight);
          let seen = 0, under = 0;
          for (const x of xs) for (const y of ys) { const t = document.elementFromPoint(x, y); if (!t) continue; if (t === el || el.contains(t)) seen++; else if (hdr.contains(t)) under++; }
          return { seen, under };
        });
        checked++;
        if (!q.seen && q.under) { hidden++; worst = worst || r.txt; } // целиком под шапкой
      }
      line(hidden === 0 && checked > 20 && !errs.length, `1440 ${path} Tab: проверено ${checked} элементов, целиком под шапкой — ${hidden}${worst ? ' (например «' + worst + '»)' : ''}${errs.length ? '; JS: ' + errs.join(' | ') : ''}`);
    } catch (e) { line(false, `1440 ${path} Tab: ${String(e).slice(0, 200)}`); }
    await page.close();
  }
  // 6
  for (const [path, id] of want(6) ? [['/', 'tseny'], ['/deratizatsiya/', 'stoimost']] : []) {
    const page = await ctx.newPage(); const errs = errsOf(page);
    try {
      await open(page, BASE + path); await sleep(1500);
      const a = page.locator(`.nav > a[href="#${id}"]`).first();
      if (!(await a.count())) { line(true, `1440 ${path}: нет «Цены» с #${id} — пропуск`); await page.close(); continue; }
      const b = await a.boundingBox();
      await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2); await sleep(150);
      const t0 = Date.now();
      await page.mouse.click(b.x + b.width / 2, b.y + b.height / 2);
      let last = -1, still = 0, tEnd = 0;
      for (let i = 0; i < 80; i++) {
        await sleep(40);
        const y = await page.evaluate(() => scrollY);
        if (Math.abs(y - last) < 1 && y > 300) { if (++still >= 4 && !tEnd) { tEnd = Date.now() - t0 - 160; break; } } else still = 0;
        last = y;
      }
      await sleep(400);
      const m = await page.evaluate((id) => { const t = document.getElementById(id), h = document.getElementById('hdr').getBoundingClientRect(); const r = (t.querySelector('.eyebrow, h2') || t).getBoundingClientRect();
        return { hb: Math.round(h.bottom), hh: Math.round(h.height), hide: document.getElementById('hdr').classList.contains('hide'), top: Math.round(r.top) }; }, id);
      const ok = tEnd > 0 && tEnd <= 1400 && !m.hide && m.hh === 65 && m.top >= m.hb && !errs.length;
      line(ok, `1440 ${path} «Цена» → #${id}: прокрутка ${tEnd ? (tEnd / 1000).toFixed(2) + ' с' : 'НЕ ЗАКОНЧИЛАСЬ'}, шапка ${m.hide ? 'СКРЫТА' : 'видна'} ${m.hh} px, заголовок блока на ${m.top} px (низ шапки ${m.hb})${errs.length ? '; JS: ' + errs.join(' | ') : ''}`);
    } catch (e) { line(false, `1440 ${path} «Цена»: ${String(e).slice(0, 200)}`); }
    await page.close();
  }
  await ctx.close();
}
// 7. закреплённые блоки: на всех страницах с position: sticky — компьютер 1440 и 1280
for (const [w, h] of want(7) ? [[1440, 900], [1280, 800], [1920, 1080]] : []) {
  const ctx = await newCtx(browser, w, h, false);
  const list = ['/', '/normativnaya-baza/', '/normativnaya-baza/proverochnye-listy/', '/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/',
    '/normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/', '/materialy/programma-pest-kontrolya/', '/materialy/zhurnal-pest-kontrolya/',
    '/razrabotka-ppk/', '/materialy/skhema-tochek-pest-kontrolya/', '/materialy/akt-deratizatsii-i-dezinsektsii/', '/sanitarnyy-audit/'];
  for (const path of list) {
    const page = await ctx.newPage(); const errs = errsOf(page);
    try {
      await open(page, BASE + path); await sleep(1200);
      const n = await page.evaluate(() => { const a = [...document.querySelectorAll('body *')].filter((el) => { const s = getComputedStyle(el); return s.position === 'sticky' && s.top !== 'auto' && el.getBoundingClientRect().height > 0; });
        a.forEach((el, i) => el.setAttribute('data-sticky-test', i)); return a.length; });
      const res = [];
      for (let i = 0; i < n; i++) {
        const r = await page.evaluate(async (i) => {
          const el = document.querySelector(`[data-sticky-test="${i}"]`), p = el.parentElement, pr = p.getBoundingClientRect();
          if (pr.height < el.offsetHeight + 200) return null; // негде залипать
          window.scrollTo({ top: pr.top + scrollY + Math.min(500, (pr.height - el.offsetHeight) / 2), behavior: 'instant' });
          await new Promise((r) => setTimeout(r, 700));
          const q = el.getBoundingClientRect(), h = document.getElementById('hdr').getBoundingClientRect();
          return { cls: (el.className || el.tagName).toString().split(' ')[0], top: Math.round(q.top), hb: Math.round(h.bottom), stuck: Math.abs(q.top - parseFloat(getComputedStyle(el).top)) < 2, hide: document.getElementById('hdr').classList.contains('hide') };
        }, i);
        if (r) res.push(r);
      }
      const badOnes = res.filter((r) => r.stuck && (r.hide || r.top < r.hb));
      if (res.length) line(!badOnes.length && !errs.length, `${w}×${h} ${path}: закреплённых блоков ${res.length} (${res.map((r) => r.cls + ' ' + r.top + ' px' + (r.stuck ? '' : ' не залип')).join(', ')}), низ шапки ${res[0].hb} px` +
        `${badOnes.length ? '; ПОД ШАПКОЙ: ' + badOnes.map((r) => r.cls).join(', ') : ''}${errs.length ? '; JS: ' + errs.join(' | ') : ''}`);
    } catch (e) { line(false, `${w} ${path} закреплённые блоки: ${String(e).slice(0, 200)}`); }
    await page.close();
  }
  await ctx.close();
}

// ---------- 8. «уменьшение движения» ----------
if (want(8)) {
  const ctx = await newCtx(browser, 1440, 900, false, { reducedMotion: 'reduce' });
  const page = await ctx.newPage(); const errs = errsOf(page);
  try {
    await open(page, BASE + '/deratizatsiya/'); await sleep(1200);
    await page.evaluate(() => window.scrollTo({ top: 400, behavior: 'instant' })); await sleep(80);
    const m = await st(page);
    const tr = await page.evaluate(() => getComputedStyle(document.querySelector('#hdr .wrap')).transitionDuration);
    line(m.hh === 65 && !errs.length, `1440 уменьшение движения: через 0,08 с после прокрутки шапка ${m.hh} px (нужно 65), длительность смены размера ${tr}${errs.length ? '; JS: ' + errs.join(' | ') : ''}`);
  } catch (e) { line(false, `уменьшение движения: ${String(e).slice(0, 200)}`); }
  await ctx.close();
}

// ---------- 9. все страницы sitemap.xml ----------
if (!QUICK && want(9)) {
  let paths = [];
  try {
    const xml = PKG && fs.existsSync(`${PKG}/sitemap.xml`) ? fs.readFileSync(`${PKG}/sitemap.xml`, 'utf8')
      : await (await fetch(BASE + '/sitemap.xml')).text();
    paths = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => new URL(m[1]).pathname);
  } catch (e) { line(false, 'sitemap.xml: ' + String(e).slice(0, 120)); }
  if (fs.existsSync('server/sitemap.xml') && !paths.length) paths = [...fs.readFileSync('server/sitemap.xml', 'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => new URL(m[1]).pathname);
  paths.push('/privacy/', '/soglasie/');
  for (const [vn, w, h, mob] of [['1440', 1440, 900, false], ['390', 390, 844, true]]) {
    const ctx = await newCtx(browser, w, h, mob);
    let okN = 0;
    for (const path of paths) {
      const page = await ctx.newPage(); const errs = errsOf(page);
      try {
        await open(page, BASE + path); await sleep(900);
        const t0 = await st(page);
        let ok = !t0.scrolled && !t0.hide && Math.abs(t0.hh - fullH(w)) <= 1, note = '';
        if (!mob) {
          await page.mouse.move(w / 2, h / 2);
          for (let i = 0; i < 20; i++) { await page.mouse.wheel(0, 120); await sleep(30); }
          await sleep(900);
          const a = await st(page);
          for (let i = 0; i < 20; i++) { await page.mouse.wheel(0, -3); await sleep(16); }
          await sleep(400);
          const b = await st(page);
          ok = ok && a.scrolled && !a.hide && a.top === 0 && a.hh === 65 && !b.hide && b.top === 0;
          note = `вниз ${a.y} px: ${a.hh} px, ${a.hide || a.top ? 'СКРЫТА' : 'видна'}; медленно вверх: ${b.hide || b.top ? 'СКРЫТА' : 'видна'}`;
        } else {
          await steps(page, 12, 60); await sleep(450); const a = await st(page);
          await steps(page, -2, 14); await sleep(450); const b = await st(page);
          ok = ok && a.hide && a.bottom <= 0 && !b.hide && b.top === 0 && b.hh === 57;
          note = `вниз ${a.y} px: ${a.hide && a.bottom <= 0 ? 'ушла' : 'НЕ УШЛА'}; вверх 28 px: ${!b.hide && b.top === 0 ? 'вернулась ' + b.hh + ' px' : 'НЕ ВЕРНУЛАСЬ'}`;
        }
        const e = await st(page);
        ok = ok && e.docW <= e.iw && !errs.length;
        if (ok) okN++;
        else line(false, `${vn} ${path}: в начале ${t0.hh} px; ${note}${e.docW > e.iw ? '; ГОРИЗОНТАЛЬНАЯ ПРОКРУТКА ' + e.docW : ''}${errs.length ? '; JS: ' + errs.join(' | ') : ''}`);
      } catch (e) { line(false, `${vn} ${path}: ${String(e).slice(0, 200)}`); }
      await page.close();
    }
    line(okN === paths.length, `${vn} px, все страницы: ${okN}/${paths.length} без замечаний`);
    await ctx.close();
  }
}

await browser.close();
console.log(lines.join('\n'));
console.log(bad ? `Нарушений: ${bad}` : 'Нарушений нет');
process.exit(bad ? 1 : 0);
