// Проверка превью «лёгкой лупы»: ошибки, 404, положение лупы, сравнение с главной при тех же положениях мыши,
// телефон, облегчённый режим. node preview_test.js [base]
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const BASE = process.argv[2] || 'http://127.0.0.1:8811/';
const OUT = path.join(__dirname, 'ptest'); fs.mkdirSync(OUT, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));
const FREEZE = `.grain,.cursor,.lupa-badge,.panel-scan{display:none!important}
.dot:before,.phone::after,.phone i:after,.scroll-cue i:after,.chip-y:before{animation:none!important}
html.has-cursor,html.has-cursor *{cursor:none!important}`;

async function open(browser, url, opts = {}) {
  const ctx = await browser.newContext(opts.mobile
    ? { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true }
    : { viewport: { width: opts.w || 1920, height: opts.h || 1080 } });
  await ctx.addInitScript(() => { try { sessionStorage.setItem('pc-intro', '1'); } catch (e) { } });
  if (opts.init) await ctx.addInitScript(opts.init);
  const page = await ctx.newPage();
  const log = { errors: [], failed: [], console: [] };
  page.on('pageerror', e => log.errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') log.console.push(m.type() + ': ' + m.text()); });
  page.on('requestfailed', r => log.failed.push(r.url() + ' ' + (r.failure() || {}).errorText));
  page.on('response', r => { if (r.status() >= 400) log.failed.push(r.status() + ' ' + r.url()); });
  await page.goto(url, { waitUntil: 'load' });
  return { ctx, page, log };
}

function diffPng(a, b, out) {
  // сравнение через Python (Pillow): средняя разница и доля заметно отличающихся точек
  const { execFileSync } = require('child_process');
  return JSON.parse(execFileSync('python3', ['-c', `
import sys, json
from PIL import Image, ImageChops
import numpy as np
A = np.asarray(Image.open(sys.argv[1]).convert('RGB'), dtype=np.int16); B = np.asarray(Image.open(sys.argv[2]).convert('RGB'), dtype=np.int16)
D = np.abs(A - B).max(axis=2)
Image.fromarray(np.clip(D * 8, 0, 255).astype(np.uint8)).save(sys.argv[3])
print(json.dumps({'mean': round(float(D.mean()), 3), 'p99': int(np.percentile(D, 99)), 'max': int(D.max()), 'over8': round(float((D > 8).mean() * 100), 3), 'over16': round(float((D > 16).mean() * 100), 3)}))
`, a, b, out]).toString());
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const res = {};
  // 1. полный режим: ошибки, лупа появилась, положение «дома»
  {
    const { ctx, page, log } = await open(browser, BASE + 'preview-lupa/?fx=full');
    await page.waitForFunction(() => document.documentElement.classList.contains('anim-ready'), null, { timeout: 15000 });
    await sleep(5000);
    res.full = await page.evaluate(() => {
      const l = document.getElementById('heroLens'), i = l && l.firstElementChild, cs = l && getComputedStyle(l);
      const r = l.getBoundingClientRect(), m = document.getElementById('heroMedia').getBoundingClientRect(), p = document.getElementById('panel').getBoundingClientRect();
      return { cls: document.documentElement.className, on: l.classList.contains('on'), opacity: cs.opacity, display: cs.display, w: r.width, h: r.height,
        center: [Math.round(r.left + r.width / 2), Math.round(r.top + r.height / 2)], img: i.style.backgroundImage, imgSize: [i.style.width, i.style.height],
        media: [Math.round(m.left), Math.round(m.top), Math.round(m.width), Math.round(m.height)], panel: [Math.round(p.left), Math.round(p.top), Math.round(p.width), Math.round(p.height)],
        fps: document.documentElement.getAttribute('data-fps'), badge: document.getElementById('lupaMode').textContent };
    });
    await page.screenshot({ path: path.join(OUT, 'full-home.png') });
    res.full.log = log;
    await ctx.close();
  }
  // 2. сравнение с главной: те же положения мыши, анимации остановлены
  const POS = [[1560, 215], [1500, 620], [430, 470], [1750, 900]];
  for (const [name, url] of [['root', BASE], ['prev', BASE + 'preview-lupa/?fx=full']]) {
    const { ctx, page, log } = await open(browser, url, { init: css => { document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s); }); } });
    await page.addStyleTag({ content: FREEZE });
    await sleep(5500);
    for (const [i, [x, y]] of POS.entries()) {
      await page.mouse.move(x - 40, y - 30); await page.mouse.move(x, y, { steps: 6 });
      await sleep(2200);
      await page.screenshot({ path: path.join(OUT, `cmp-${name}-${i}.png`) });
    }
    res['log_' + name] = log;
    await ctx.close();
  }
  res.cmp = POS.map((p, i) => ({ pos: p, ...diffPng(path.join(OUT, `cmp-root-${i}.png`), path.join(OUT, `cmp-prev-${i}.png`), path.join(OUT, `cmp-diff-${i}.png`)) }));
  // 3. телефон
  for (const [name, url] of [['root', BASE], ['prev', BASE + 'preview-lupa/']]) {
    const { ctx, page, log } = await open(browser, url, { mobile: true });
    await sleep(6000);
    await page.screenshot({ path: path.join(OUT, `mob-${name}.png`) });
    res['mob_' + name] = { log, st: await page.evaluate(() => { const l = document.getElementById('heroLens') || document.getElementById('heroLit'); return { cls: document.documentElement.className, lens: l && getComputedStyle(l).display, op: l && getComputedStyle(l).opacity, fps: document.documentElement.getAttribute('data-fps') }; }) };
    await ctx.close();
  }
  // 4. авто: в песочнице без видеокарты должен включиться облегчённый режим
  {
    const { ctx, page, log } = await open(browser, BASE + 'preview-lupa/');
    await page.waitForFunction(() => document.documentElement.hasAttribute('data-fps'), null, { timeout: 20000 }).catch(() => { });
    await sleep(500);
    res.auto = await page.evaluate(() => ({ cls: document.documentElement.className, fps: document.documentElement.getAttribute('data-fps'), lowfxStored: sessionStorage.getItem('pc-lowfx'), badge: document.getElementById('lupaMode').textContent,
      lens: getComputedStyle(document.getElementById('heroLens')).display, grain: getComputedStyle(document.querySelector('.grain')).display, cursor: document.documentElement.classList.contains('has-cursor') }));
    await page.screenshot({ path: path.join(OUT, 'auto.png') });
    // следующая страница визита: облегчённый режим сразу
    await page.goto(BASE + 'preview-lupa/', { waitUntil: 'load' });
    res.auto.second = await page.evaluate(() => document.documentElement.className);
    res.auto.log = log;
    await ctx.close();
  }
  // 5. ?fx=lite
  {
    const { ctx, page, log } = await open(browser, BASE + 'preview-lupa/?fx=lite');
    await sleep(4500);
    await page.mouse.move(1400, 500, { steps: 5 }); await sleep(800);
    res.lite = await page.evaluate(() => ({ cls: document.documentElement.className, badge: document.getElementById('lupaMode').textContent, panelBF: getComputedStyle(document.getElementById('panel')).backdropFilter,
      mediaTr: getComputedStyle(document.getElementById('heroMedia')).transform, litLoaded: performance.getEntriesByType('resource').some(e => /hero-lit/.test(e.name)) }));
    await page.screenshot({ path: path.join(OUT, 'lite.png') });
    res.lite.log = log;
    await ctx.close();
  }
  console.log(JSON.stringify(res, null, 1));
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
