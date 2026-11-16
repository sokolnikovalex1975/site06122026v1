// Проверка 17.11.2026: блок «Что видит камера в коробе» на странице вентиляции (tools/site/kamera-2026-11-17.md).
// Запуск: node tools/qa/kamera_test.mjs   (по умолчанию — рабочий сайт)
// PKG=<папка pkg пакета> — страница (ochistka-dezinfektsiya-ventilyatsii/index.php) и кадры (img/vent-kadr-*.webp)
// подставляются из пакета вместо файлов сайта (до выкладки).
// На компьютере 1440×900, ноутбуке 1180×800, планшете 768×1024 и телефонах 390×844, 360×780, 320×640:
//   1. подпись «Иллюстрация · что видит камера в коробе», старой «Схема · …» нет; в кадре 3 фото, холст и кнопка паузы;
//   2. долистали до блока — кадры загрузились (файлы vent-kadr-*), WebGL включился;
//   3. состояния меняются сами: «До работ» → «После очистки» → «После дезинфекции», подпись под кадром — своя;
//   4. щелчок по «До работ» — остановка на нём (пауза), кнопка в углу — снова пуск;
//   5. сдвигов страницы нет (layout-shift = 0), прокрутки вбок нет, блок в пределах экрана, ошибок JavaScript нет;
//   6. самопроверка и вопросы работают как раньше (скрипт страницы цел), коды счётчиков на странице есть.
// Отдельно (390 px): «уменьшить движение» — сами не меняются; без WebGL — плавная смена фото.
// Метрика, UIS и Radist не загружаются. Скриншоты блока — в OUT (по умолчанию /tmp/kamera-shots).
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const BASE = (process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai').replace(/\/$/, '');
const PKG = process.env.PKG || '';
const OUT = process.env.OUT || '/tmp/kamera-shots';
fs.mkdirSync(OUT, { recursive: true });
const PG = '/ochistka-dezinfektsiya-ventilyatsii/';
const BLOCK = /mc\.yandex|uiscom|comagic|radist|yandex\.ru\/metrika|mc\.webvisor/;
const LABEL = 'Иллюстрация · что видит камера в коробе';
const VPS = [['компьютер 1440×900', 1440, 900, false, 1], ['ноутбук 1180×800', 1180, 800, false, 1],
  ['планшет 768×1024', 768, 1024, true, 2], ['телефон 390×844', 390, 844, true, 3],
  ['телефон 360×780', 360, 780, true, 3], ['телефон 320×640', 320, 640, true, 2]];
let bad = 0;
const fail = (m) => { bad++; console.log('НАРУШЕНИЕ', m); };
const pkgPage = PKG ? path.join(PKG, 'ochistka-dezinfektsiya-ventilyatsii/index.php') : '';
if (PKG && !fs.existsSync(pkgPage)) throw new Error('нет страницы пакета: ' + pkgPage);

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });

async function open({ w, h, mobile, dpr, reduce = false, noGL = false }) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, isMobile: mobile, hasTouch: mobile,
    deviceScaleFactor: dpr, reducedMotion: reduce ? 'reduce' : 'no-preference' });
  await ctx.route('**/*', (r) => {
    const u = r.request().url();
    if (BLOCK.test(u)) return r.abort();
    const p = new URL(u).pathname;
    if (PKG && r.request().resourceType() === 'document' && p === PG) {
      return r.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: fs.readFileSync(pkgPage) });
    }
    const m = p.match(/^\/img\/(vent-kadr-[a-z0-9-]+\.webp)$/);
    if (PKG && m) return r.fulfill({ status: 200, contentType: 'image/webp', body: fs.readFileSync(path.join(PKG, 'img', m[1])) });
    return r.continue();
  });
  await ctx.addInitScript(({ noGL }) => {
    window.__ls = [];
    window.__lsSrc = [];
    new PerformanceObserver((l) => { for (const e of l.getEntries()) if (!e.hadRecentInput) { window.__ls.push(e.value);
      for (const x of e.sources || []) { const n = x.node; window.__lsSrc.push(n ? (n.id ? '#' + n.id : n.nodeName + (n.className && n.className.baseVal === undefined ? '.' + String(n.className).split(' ').join('.') : '')) + (n.closest && n.closest('#vduct') ? ' (в блоке)' : '') : '?'); } } })
      .observe({ type: 'layout-shift', buffered: true });
    if (noGL) { window.WebGLRenderingContext = undefined; }
  }, { noGL });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error' && !/ERR_FAILED|net::|Failed to load resource/.test(m.text())) errors.push(m.text()); });
  const resp = await page.goto(BASE + PG, { waitUntil: 'load', timeout: 90000 });
  const body = resp ? await resp.text() : '';
  // заставка сайта (#intro) закрывает экран первые секунды — ждём, пока уйдёт
  await page.waitForFunction(() => { const e = document.getElementById('intro'); if (!e || !e.isConnected) return true;
    const s = getComputedStyle(e); return s.display === 'none' || s.visibility === 'hidden' || +s.opacity === 0; }, null, { timeout: 20000 })
    .catch(() => errors.push('заставка #intro не ушла за 20 с'));
  return { ctx, page, errors, body };
}

const state = (page) => page.evaluate(() => {
  const vd = document.getElementById('vduct');
  const cap = [...vd.querySelectorAll('[data-cap]')].filter((c) => !c.hidden).map((c) => c.getAttribute('data-cap'));
  const pressed = [...vd.querySelectorAll('.v-seg button')].filter((b) => b.getAttribute('aria-pressed') === 'true').map((b) => b.getAttribute('data-s'));
  const on = [...vd.querySelectorAll('.vk-f.is-on')].map((i) => i.getAttribute('data-s'));
  return { s: vd.getAttribute('data-state'), cap, pressed, on, gl: vd.classList.contains('vk-gl-on'),
    paused: vd.classList.contains('vk-paused') };
});

async function toBlock(page) {
  await page.evaluate(() => document.getElementById('vduct').querySelector('.v-duct-art').scrollIntoView({ block: 'center' }));
  await page.waitForFunction(() => [...document.querySelectorAll('#vduct .vk-f')].every((i) => i.complete && i.naturalWidth > 0),
    null, { timeout: 30000 }).catch(() => null);
}

async function waitState(page, s, ms) {
  return page.waitForFunction((s) => document.getElementById('vduct').getAttribute('data-state') === s, s, { timeout: ms })
    .then(() => true, () => false);
}
// фото сменилось (переход WebGL закончился); программный WebGL песочницы медленный — ждём с запасом
async function waitPic(page, s, ms = 25000) {
  const t = Date.now();
  const ok = await page.waitForFunction((s) => { const on = document.querySelectorAll('#vduct .vk-f.is-on');
    return on.length === 1 && on[0].getAttribute('data-s') === s; }, s, { timeout: ms }).then(() => true, () => false);
  return ok ? Date.now() - t : -1;
}
const fps = (page) => page.evaluate(() => new Promise((res) => { let n = 0; const t0 = performance.now();
  const f = () => { n++; if (performance.now() - t0 < 1000) requestAnimationFrame(f); else res(Math.round(n * 1000 / (performance.now() - t0))); };
  requestAnimationFrame(f); }));

const shot = async (page, name) => {
  const el = page.locator('#vduct');
  await el.screenshot({ path: path.join(OUT, name + '.png') }).catch((e) => console.log('скриншот', name, String(e).slice(0, 80)));
};

for (const [vpName, w, h, mobile, dpr] of VPS) {
  const where = `${vpName}${PKG ? ' (пакет)' : ''}`;
  const { ctx, page, errors, body } = await open({ w, h, mobile, dpr });
  const cnt = (re) => (body.match(re) || []).length;
  const codes = [cnt(/mc\.yandex\.ru\/metrika\/tag\.js\?id=113675622/g), cnt(/ym\(113675622, 'init'/g), cnt(/mc\.yandex\.ru\/watch\/113675622/g),
    cnt(/app\.uiscom\.ru\/static\/cs\.min\.js\?k=/g), cnt(/track\.radist\.me\/tracker\.min\.js/g)];
  if (codes.join() !== '1,1,1,1,1') fail(`${where}: коды счётчиков в странице (Метрика tag.js, init, noscript, UIS, Radist) ${codes}`);
  const st = await page.evaluate((LABEL) => {
    const norm = (s) => s.replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();
    const vd = document.getElementById('vduct');
    if (!vd) return { none: true };
    return { label: norm(vd.querySelector('.v-duct-k').textContent), old: /Схема · что видит/.test(norm(document.body.textContent)),
      imgs: vd.querySelectorAll('.v-duct-art .vk-f').length, canvas: !!vd.querySelector('.vk-gl'), play: !!vd.querySelector('.vk-play'),
      legend: vd.querySelector('.v-legend') && vd.querySelector('.v-legend').getAttribute('aria-label'),
      li: vd.querySelectorAll('.v-legend li').length, caps: vd.querySelectorAll('[data-cap]').length,
      lazy: [...vd.querySelectorAll('.vk-f')].every((i) => i.loading === 'lazy'),
      early: [...vd.querySelectorAll('.vk-f')].filter((i) => i.complete && i.naturalWidth > 0).length };
  }, LABEL);
  if (st.none) { fail(`${where}: нет блока #vduct`); await ctx.close(); continue; }
  if (st.label !== LABEL) fail(`${where}: подпись «${st.label}»`);
  if (st.old) fail(`${where}: осталась подпись «Схема · что видит…»`);
  if (st.imgs !== 3 || !st.canvas || !st.play) fail(`${where}: кадр ${JSON.stringify(st)}`);
  if (st.legend !== 'Что видно на кадре' || st.li !== 4 || st.caps !== 3) fail(`${where}: обозначения/подписи ${JSON.stringify(st)}`);
  if (!st.lazy) fail(`${where}: кадры без loading=lazy`);
  // самопроверка и вопросы (скрипт страницы цел)
  const resTxt = () => page.evaluate(() => { const r = document.querySelector('.f-check-res'); return r ? r.textContent : ''; });
  const r0 = await resTxt();
  await page.locator('.f-check-list label').first().click();
  await page.waitForTimeout(700);
  const r1 = await resTxt();
  await page.locator('.f-check-list label').first().click();
  await page.waitForTimeout(400);
  if (!r0 || r0 === r1) fail(`${where}: самопроверка не отвечает («${r0}» → «${r1}»)`);
  const misc = await page.evaluate(() => ({ qaOpen: document.querySelectorAll('.qa.open').length, qa: document.querySelectorAll('.qa').length }));
  if (misc.qa && misc.qaOpen < 1) fail(`${where}: вопросы — ни один не развёрнут`);
  await toBlock(page);
  const t0 = Date.now();
  const s0 = await state(page);
  const files = await page.evaluate(() => [...document.querySelectorAll('#vduct .vk-f')].map((i) => (i.currentSrc || '').split('/').pop()));
  if (!files.every((f) => /^vent-kadr-.+\.webp$/.test(f))) fail(`${where}: кадры не загрузились ${files}`);
  await page.waitForFunction(() => document.getElementById('vduct').classList.contains('vk-gl-on'), null, { timeout: 8000 }).catch(() => null);
  const gl = (await state(page)).gl;
  if (!gl) fail(`${where}: WebGL не включился`);
  if (s0.s !== 'do' || s0.cap.join() !== 'do' || s0.pressed.join() !== 'do') fail(`${where}: начало ${JSON.stringify(s0)}`);
  await shot(page, `${w}-1-do`);
  // щётка: середина перехода
  const toClean = await waitState(page, 'clean', 7000);
  if (!toClean) fail(`${where}: «После очистки» не наступило само`);
  const f1 = await fps(page);
  await page.waitForTimeout(600);
  await shot(page, `${w}-2-shchetka`);
  const s1 = await state(page);
  if (s1.cap.join() !== 'clean' || s1.pressed.join() !== 'clean') fail(`${where}: «После очистки» ${JSON.stringify(s1)}`);
  const brushMs = await waitPic(page, 'clean');
  if (brushMs < 0) fail(`${where}: фото «После очистки» не сменилось`);
  const toDez = await waitState(page, 'dez', 9000);
  if (!toDez) fail(`${where}: «После дезинфекции» не наступило само`);
  await page.waitForTimeout(1200);
  await shot(page, `${w}-3-tuman`);
  const mistMs = await waitPic(page, 'dez');
  const s2 = await state(page);
  if (mistMs < 0 || s2.cap.join() !== 'dez' || s2.on.join() !== 'dez') fail(`${where}: «После дезинфекции» ${JSON.stringify(s2)}`);
  await shot(page, `${w}-4-dez`);
  const cycle = ((Date.now() - t0) / 1000).toFixed(1);
  // закон «на телефоне ничего не затемнять»: кнопка паузы и убранное в «Что видно на кадре» (до 760 px)
  const law = await page.evaluate(() => {
    const lum = (c) => { const m = c.match(/[\d.]+/g).map(Number); return (0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2]) / 255; };
    const pb = getComputedStyle(document.querySelector('#vduct .vk-play')).backgroundColor;
    const gone = getComputedStyle(document.querySelector('#vduct .v-legend li>span')).color;
    const t2 = getComputedStyle(document.querySelector('#vduct figcaption')).color;
    return { pb: lum(pb), gone, t2, phone: matchMedia('(max-width:760px)').matches };
  });
  if (law.phone && law.pb < 0.6) fail(`${where}: на телефоне тёмная кнопка паузы поверх фото (${law.pb.toFixed(2)})`);
  if (law.phone && law.gone !== law.t2) fail(`${where}: на телефоне убранное приглушено (${law.gone} ≠ ${law.t2})`);
  // щелчок по «До работ» — остановка; переход назад снимаем, чтобы сверить яркость (на телефоне — без затемнения)
  const art = page.locator('#vduct .v-duct-art');
  await art.screenshot({ path: path.join(OUT, `${w}-art-dez.png`) }).catch(() => null);
  await page.locator('#vduct .v-seg button[data-s="do"]').click();
  for (const [i, ms] of [[1, 200], [2, 200], [3, 200]]) {
    await page.waitForTimeout(ms);
    await art.screenshot({ path: path.join(OUT, `${w}-art-back-${i}.png`) }).catch(() => null);
  }
  const backMs = await waitPic(page, 'do');
  await page.waitForTimeout(400);
  await art.screenshot({ path: path.join(OUT, `${w}-art-do.png`) }).catch(() => null);
  const s3 = await state(page);
  if (backMs < 0 || s3.s !== 'do' || !s3.paused || s3.on.join() !== 'do') fail(`${where}: щелчок «До работ» ${JSON.stringify(s3)}`);
  await page.waitForTimeout(3200);
  if ((await state(page)).s !== 'do') fail(`${where}: после щелчка смена не остановилась`);
  // кнопка в углу — пуск
  await page.locator('#vduct .vk-play').click();
  const resumed = await waitState(page, 'clean', 7000);
  if (!resumed || (await state(page)).paused) fail(`${where}: кнопка пуска не запустила смену`);
  const geo = await page.evaluate(() => {
    const vd = document.getElementById('vduct').getBoundingClientRect();
    const art = document.querySelector('#vduct .v-duct-art').getBoundingClientRect();
    return { hscroll: document.documentElement.scrollWidth > window.innerWidth + 1, left: vd.left, right: vd.right, vw: window.innerWidth,
      ratio: art.width / art.height, artH: Math.round(art.height), cls: window.__ls.reduce((a, b) => a + b, 0),
      inBlock: window.__lsSrc.filter((x) => x.includes('(в блоке)')), src: [...new Set(window.__lsSrc)].slice(0, 6) };
  });
  if (geo.hscroll) fail(`${where}: горизонтальная прокрутка`);
  if (geo.left < -0.5 || geo.right > geo.vw + 0.5) fail(`${where}: блок за краем экрана ${JSON.stringify(geo)}`);
  if (Math.abs(geo.ratio - 43 / 24) > 0.02) fail(`${where}: пропорции кадра ${geo.ratio.toFixed(3)}`);
  if (geo.inBlock.length) fail(`${where}: сдвиги внутри блока ${geo.inBlock.join(', ')}`);
  if (geo.cls > 0.01) fail(`${where}: сдвиг страницы ${geo.cls.toFixed(4)} (${geo.src.join(', ')})`);
  if (errors.length) fail(`${where}: ошибки JS ${errors.slice(0, 3).join(' | ')}`);
  console.log(`${where}: кадры ${files.join(', ')}; WebGL ${gl ? 'да' : 'нет'} (${f1} кадров/с в песочнице); ` +
    `до → дезинфекция ${cycle} с; кадр ${geo.artH} px; сдвиг ${geo.cls.toFixed(4)}${geo.cls ? ' (' + geo.src.join(', ') + ')' : ''}; до блока загружено кадров ${st.early}; самопроверка «${r0}» → «${r1}»`);
  await ctx.close();
}

// «уменьшить движение» и без WebGL — телефон 390
{
  const { ctx, page, errors } = await open({ w: 390, h: 844, mobile: true, dpr: 3, reduce: true });
  await toBlock(page);
  await page.waitForTimeout(7000);
  const s = await state(page);
  if (s.s !== 'do' || !s.paused) fail(`уменьшить движение: смена пошла сама ${JSON.stringify(s)}`);
  await page.locator('#vduct .v-seg button[data-s="clean"]').click();
  await page.waitForTimeout(1500);
  const s2 = await state(page);
  if (s2.s !== 'clean' || s2.on.join() !== 'clean') fail(`уменьшить движение: щелчок ${JSON.stringify(s2)}`);
  if (errors.length) fail(`уменьшить движение: ошибки JS ${errors.join(' | ')}`);
  console.log('уменьшить движение (390): сами не меняются, щелчок —', s2.s);
  await ctx.close();
}
{
  const { ctx, page, errors } = await open({ w: 390, h: 844, mobile: true, dpr: 3, noGL: true });
  await toBlock(page);
  const ok = await waitState(page, 'clean', 7000);
  await page.waitForTimeout(1500);
  const s = await state(page);
  if (!ok || s.gl || s.on.join() !== 'clean') fail(`без WebGL: ${JSON.stringify(s)}`);
  await shot(page, '390-nogl-clean');
  if (errors.length) fail(`без WebGL: ошибки JS ${errors.join(' | ')}`);
  console.log('без WebGL (390): плавная смена фото —', s.s);
  await ctx.close();
}
await browser.close();
console.log(bad ? `Нарушений: ${bad}` : 'Нарушений нет');
process.exit(bad ? 1 : 0);
