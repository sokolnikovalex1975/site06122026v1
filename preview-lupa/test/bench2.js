// Замер кадров и процессора первого экрана (Chrome без видеоускорения). Сайт — с локального сервера BASE
// (по умолчанию http://127.0.0.1:8811/, из корня репозитория: python3 -m http.server 8811), страница — PAGE.
// Запуск: node bench.js <variant> <mode> <profile> [width] [height] [dpr] [mobile]
//  variant: cur | off | opt
//  mode:    idle | move | trace-idle | trace-move | shot
//  profile: norm (2 ядра, без замедления) | weak (1 ядро + замедление main-потока x4)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const BASE = process.env.BASE || 'http://127.0.0.1:8811/';
const SITE_HOST = new URL(BASE).host;
const SITE = BASE + (process.env.PAGE || '');
const BLOCK = [/yandex\./, /uiscom/, /comagic/, /radist/, /mc\.yandex/, /webvisor/];
const CACHE = path.join(__dirname, 'cache');
fs.mkdirSync(CACHE, { recursive: true });

const [variant = 'cur', mode = 'idle', profile = 'norm', W = '1920', H = '1080', DPR = '1', MOBILE = '0', DUR = '8'] = process.argv.slice(2);
const width = +W, height = +H, dpr = +DPR, mobile = MOBILE === '1', DURATION = +DUR * 1000;
const TAG = 'bench' + Date.now();

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function fetchWithRetry(url, headers) {
  let last;
  for (let i = 0; i < 8; i++) {
    try {
      const r = await fetch(url, { headers });
      if (r.status === 200) {
        const buf = Buffer.from(await r.arrayBuffer());
        return { status: 200, ct: r.headers.get('content-type') || '', buf };
      }
      last = 'HTTP ' + r.status;
    } catch (e) { last = String(e); }
    await sleep(1200);
  }
  throw new Error('fetch failed ' + url + ' ' + last);
}

async function cachedSiteResponse(url) {
  const key = crypto.createHash('sha1').update(url).digest('hex');
  const bin = path.join(CACHE, key + '.bin'), meta = path.join(CACHE, key + '.json');
  if (fs.existsSync(bin) && fs.existsSync(meta)) {
    return { ...JSON.parse(fs.readFileSync(meta, 'utf8')), buf: fs.readFileSync(bin) };
  }
  const r = await fetchWithRetry(url, { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36', 'Referer': SITE });
  fs.writeFileSync(bin, r.buf);
  fs.writeFileSync(meta, JSON.stringify({ status: r.status, ct: r.ct, url }));
  return r;
}

// ---------- CPU по процессам/потокам Chrome ----------
function listPids() {
  return fs.readdirSync('/proc').filter(d => /^\d+$/.test(d)).map(Number);
}
function readStat(p) {
  try {
    const s = fs.readFileSync(p, 'utf8');
    const r = s.lastIndexOf(')');
    const comm = s.slice(s.indexOf('(') + 1, r);
    const f = s.slice(r + 2).split(' ');
    return { comm, ppid: +f[1], ticks: (+f[11]) + (+f[12]) };
  } catch (e) { return null; }
}
function chromeTree(rootPid) {
  const all = listPids();
  const kids = {};
  for (const p of all) { const st = readStat('/proc/' + p + '/stat'); if (st) (kids[st.ppid] = kids[st.ppid] || []).push(p); }
  const out = []; const q = [rootPid];
  while (q.length) { const p = q.shift(); out.push(p); (kids[p] || []).forEach(k => q.push(k)); }
  return out;
}
function findRoot() {
  for (const p of listPids()) {
    try { const c = fs.readFileSync('/proc/' + p + '/cmdline', 'utf8'); if (c.includes(TAG) && !c.includes('--type=')) return p; } catch (e) { }
  }
  return null;
}
function procType(pid) {
  try {
    const c = fs.readFileSync('/proc/' + pid + '/cmdline', 'utf8');
    const m = c.match(/--type=([a-z-]+)/); return m ? m[1] : 'browser';
  } catch (e) { return '?'; }
}
function snapshot(rootPid) {
  const res = {};
  for (const pid of chromeTree(rootPid)) {
    const type = procType(pid);
    let tids = [];
    try { tids = fs.readdirSync('/proc/' + pid + '/task'); } catch (e) { }
    for (const t of tids) {
      const st = readStat('/proc/' + pid + '/task/' + t + '/stat'); if (!st) continue;
      let name = st.comm.replace(/\d+$/, '');
      const k = type + ':' + name;
      res[k] = (res[k] || 0) + st.ticks;
    }
  }
  return res;
}
function diff(a, b, secs) {
  const out = {}; let total = 0;
  for (const k of Object.keys(b)) { const d = (b[k] - (a[k] || 0)) / 100; if (d > 0.005) { out[k] = +(d / secs * 100).toFixed(1); total += d; } }
  return { total: +(total / secs * 100).toFixed(1), byThread: Object.fromEntries(Object.entries(out).sort((x, y) => y[1] - x[1]).slice(0, 12)) };
}

// ---------- оптимизированная «лупа» для варианта opt ----------
const OPT_CSS = `#heroLit{display:none!important}
.lens{position:absolute;left:0;top:0;width:calc(var(--lr)*2);height:calc(var(--lr)*2);pointer-events:none;will-change:transform,opacity;opacity:0;transition:opacity .5s;
-webkit-mask-image:radial-gradient(circle closest-side,#000 0%,rgba(0,0,0,.55) 62%,transparent 100%);mask-image:radial-gradient(circle closest-side,#000 0%,rgba(0,0,0,.55) 62%,transparent 100%);overflow:hidden;contain:strict}
.lens.on{opacity:1}
.lens-img{position:absolute;left:0;top:0;background:url(img/hero.webp) center/cover;will-change:transform;filter:grayscale(.05) brightness(1.05) contrast(1.05)}
@media (max-width:760px){.lens{display:none}}`;
function optScript() {
  // вставляется в страницу; только transform, без перерисовки; без «блуждания» в простое; на сенсорных экранах не работает
  var media = document.getElementById('heroMedia'), hero = document.getElementById('hero');
  if (!media || !hero || !matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  var lens = document.createElement('div'); lens.className = 'lens';
  var img = document.createElement('div'); img.className = 'lens-img'; lens.appendChild(img); media.appendChild(lens);
  var R = 0, mw = 0, mh = 0, x = 0, y = 0, tx = 0, ty = 0, raf = 0, visible = true;
  function size() {
    var r = media.getBoundingClientRect(); mw = r.width; mh = r.height;
    R = Math.round(Math.max(240, Math.min(400, innerWidth * 0.21)) * 0.72);
    lens.style.setProperty('--lr', R + 'px'); img.style.width = mw + 'px'; img.style.height = mh + 'px';
  }
  size(); addEventListener('resize', size);
  new IntersectionObserver(function (e) { visible = e[0].isIntersecting; }).observe(hero);
  function apply() {
    lens.style.transform = 'translate3d(' + (x - R).toFixed(1) + 'px,' + (y - R).toFixed(1) + 'px,0)';
    img.style.transform = 'translate3d(' + (R - x).toFixed(1) + 'px,' + (R - y).toFixed(1) + 'px,0)';
  }
  function tick() {
    raf = 0; x += (tx - x) * 0.18; y += (ty - y) * 0.18; apply();
    if (Math.abs(tx - x) > 0.5 || Math.abs(ty - y) > 0.5) raf = requestAnimationFrame(tick); // кадры только пока пятно догоняет мышь
  }
  hero.addEventListener('pointermove', function (e) {
    if (e.pointerType !== 'mouse' || !visible) return;
    var r = media.getBoundingClientRect(); tx = e.clientX - r.left; ty = e.clientY - r.top;
    if (!lens.classList.contains('on')) { x = tx; y = ty; apply(); lens.classList.add('on'); }
    if (!raf) raf = requestAnimationFrame(tick);
  }, { passive: true });
  hero.addEventListener('pointerleave', function () { lens.classList.remove('on'); });
}

(async () => {
  let execPath = chromium.executablePath();
  if (profile === 'weak') {
    const wrap = path.join(__dirname, 'chrome-1core.sh');
    fs.writeFileSync(wrap, '#!/bin/sh\nexec taskset -c 0 "' + execPath + '" "$@"\n'); fs.chmodSync(wrap, 0o755);
    execPath = wrap;
  }
  const browser = await chromium.launch({ executablePath: execPath, headless: true, args: ['--' + TAG, '--disable-background-timer-throttling', '--disable-renderer-backgrounding'] });
  const ctxOpts = mobile
    ? { viewport: { width, height }, deviceScaleFactor: dpr, isMobile: true, hasTouch: true, userAgent: 'Mozilla/5.0 (Linux; Android 13; SM-A145F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36' }
    : { viewport: { width, height }, deviceScaleFactor: dpr, userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36' };
  const context = await browser.newContext(ctxOpts);
  await context.route('**/*', async route => {
    const url = route.request().url(); let u; try { u = new URL(url); } catch (e) { return route.continue(); }
    if (u.protocol === 'data:' || u.protocol === 'blob:') return route.continue();
    if (u.host === SITE_HOST) return route.continue();
    if (BLOCK.some(re => re.test(u.host))) return route.abort();
    return route.abort(); // остальное стороннее тоже не грузим
  });
  await context.addInitScript(() => { try { sessionStorage.setItem('pc-intro', '1'); } catch (e) { } });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  if (variant === 'off') await context.addInitScript(() => { document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style'); s.textContent = '#heroLit,.fx-lit{display:none!important}'; document.head.appendChild(s); }); });
  const BARE_CSS = '#heroLit{display:none!important}.grain{display:none!important}.panel-scan,.dot:before,.phone i:after,.phone::after,.scroll-cue i:after{animation:none!important}';
  if (variant === 'nograin') await context.addInitScript(() => { document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style'); s.textContent = '#heroLit{display:none!important}.grain{display:none!important}'; document.head.appendChild(s); }); });
  if (variant === 'noscan') await context.addInitScript(() => { document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style'); s.textContent = '#heroLit{display:none!important}.panel-scan{animation:none!important}'; document.head.appendChild(s); }); });
  if (variant === 'bare') await context.addInitScript(css => { document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s); }); }, BARE_CSS);
  if (variant === 'opt2') await context.addInitScript(css => { document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style'); s.textContent = css + '.lens-img{filter:none!important}'; document.head.appendChild(s); }); }, OPT_CSS);
  if (variant === 'opt') await context.addInitScript(css => { document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s); }); }, OPT_CSS);

  await page.goto(SITE, { waitUntil: 'load', timeout: 120000 });
  // дождаться GSAP и включения эффекта
  await page.waitForFunction(() => document.documentElement.classList.contains('anim-ready') || document.documentElement.classList.contains('anim-fail'), null, { timeout: 30000 });
  if (variant === 'opt' || variant === 'opt2') await page.evaluate(optScript);
  await sleep(4500);
  if (process.env.WAITFX === '1') { await page.waitForFunction(() => document.documentElement.hasAttribute('data-fps') || document.documentElement.classList.contains('lowfx'), null, { timeout: 20000 }).catch(() => { }); await sleep(800); }
  const fxState = await page.evaluate(() => ({ cls: document.documentElement.className, fps: document.documentElement.getAttribute('data-fps') }));
  const state = await page.evaluate(() => {
    const l = document.getElementById('heroLit') || document.querySelector('.fx-lit'); const cs = l ? getComputedStyle(l) : null;
    return { animFail: document.documentElement.classList.contains('anim-fail'), gsap: !!window.gsap, hover: matchMedia('(hover: hover) and (pointer: fine)').matches,
      litOpacity: cs && cs.opacity, litDisplay: cs && cs.display, sx: l && l.style.getPropertyValue('--sx'), sr: l && l.style.getPropertyValue('--sr'),
      mediaBox: (() => { const el = document.getElementById('heroMedia') || document.querySelector('.fx-lit') || document.body; const r = el.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; })(),
      panelBox: (() => { const p = document.getElementById('panel'); if (!p) return null; const r = p.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; })() };
  });

  const cdp = await context.newCDPSession(page);
  await cdp.send('Performance.enable');
  if (profile === 'weak') await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });

  // in-page счётчик кадров
  await page.evaluate(() => {
    window.__fr = { t: [], on: false };
    const loop = (ts) => { if (window.__fr.on) window.__fr.t.push(ts); requestAnimationFrame(loop); }; requestAnimationFrame(loop);
    window.__loaf = []; try { new PerformanceObserver(l => l.getEntries().forEach(e => window.__loaf.push(e.duration))).observe({ type: 'long-animation-frame', buffered: false }); } catch (e) { }
  });

  const isTrace = mode.startsWith('trace');
  const moving = mode === 'move' || mode === 'trace-move';
  let stopMove = false;
  const mover = async () => {
    const t0 = Date.now();
    while (!stopMove) {
      const t = (Date.now() - t0) / 1000;
      const cx = width * 0.66 + width * 0.17 * Math.cos(t * 2.4), cy = height * 0.46 + height * 0.2 * Math.sin(t * 3.1);
      await page.mouse.move(cx, cy);
      await sleep(16);
    }
  };
  if (moving) { await page.mouse.move(width * 0.6, height * 0.5); await sleep(300); }

  const rootPid = findRoot();
  if (isTrace) await browser.startTracing(page, { path: path.join(__dirname, `trace-${variant}-${mode}-${profile}-${width}x${height}${mobile ? 'm' : ''}.json`), categories: ['devtools.timeline', 'disabled-by-default-devtools.timeline', 'disabled-by-default-devtools.timeline.frame', 'benchmark', 'cc', 'viz'] });
  const m0 = await cdp.send('Performance.getMetrics');
  const c0 = snapshot(rootPid); const w0 = Date.now();
  await page.evaluate(() => { window.__fr.on = true; window.__fr.t = []; window.__loaf = []; });
  let mv = null; if (moving) mv = mover();
  if (mode === 'scroll') { await page.mouse.move(width * 0.5, height * 0.5); mv = (async () => { const t0 = Date.now(); while (!stopMove && Date.now() - t0 < DURATION) { await page.mouse.wheel(0, 40); await sleep(100); } })(); }
  await sleep(isTrace ? 3000 : DURATION);
  stopMove = true; if (mv) await mv;
  const fr = await page.evaluate(() => { window.__fr.on = false; const t = window.__fr.t; const d = []; for (let i = 1; i < t.length; i++) d.push(t[i] - t[i - 1]); d.sort((a, b) => a - b);
    const span = t.length > 1 ? (t[t.length - 1] - t[0]) / 1000 : 0; return { frames: t.length, fps: span ? +(d.length / span).toFixed(1) : 0, p50: d.length ? +d[Math.floor(d.length * .5)].toFixed(1) : 0, p95: d.length ? +d[Math.floor(d.length * .95)].toFixed(1) : 0, over34: d.filter(x => x > 34).length, loaf: window.__loaf.length, loafMax: window.__loaf.length ? Math.round(Math.max.apply(null, window.__loaf)) : 0 }; });
  const secs = (Date.now() - w0) / 1000;
  const scrolled = await page.evaluate(() => Math.round(scrollY));
  const c1 = snapshot(rootPid);
  const m1 = await cdp.send('Performance.getMetrics');
  if (isTrace) await browser.stopTracing();
  const mm = (m, n) => (m.metrics.find(x => x.name === n) || {}).value || 0;
  const mainBusy = {};
  for (const n of ['TaskDuration', 'ScriptDuration', 'RecalcStyleDuration', 'LayoutDuration']) mainBusy[n] = +(((mm(m1, n) - mm(m0, n)) / secs) * 100).toFixed(1);
  const cpu = diff(c0, c1, secs);
  let shot = null;
  if (mode === 'shot') { shot = path.join(__dirname, `shot-${variant}-${width}x${height}${mobile ? 'm' : ''}.png`); await page.screenshot({ path: shot }); }
  console.log(JSON.stringify({ variant, page: process.env.PAGE || '', fx: fxState, mode, profile, viewport: `${width}x${height}@${dpr}${mobile ? ' mobile' : ''}`, secs: +secs.toFixed(1), state, frames: fr, scrolled, cpuTotalPct: cpu.total, mainThreadPct: mainBusy, threads: cpu.byThread, errors: errors.slice(0, 3) }));
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
