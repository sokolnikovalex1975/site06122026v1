// Совпадение лупы с фото: вместо светлого фото в лупу ставится то же затемнённое — снимок с лупой и без неё должен
// совпасть точка в точку при любом положении мыши, прокрутке, параллаксе и размере окна. Плюс первый визит с заставкой.
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const BASE = process.argv[2] || 'http://127.0.0.1:8811/';
const OUT = path.join(__dirname, 'ptest'); fs.mkdirSync(OUT, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));
const { execFileSync } = require('child_process');
const FREEZE = `.grain,.cursor,.lupa-badge,.panel-scan{display:none!important}
.dot:before,.phone::after,.phone i:after,.scroll-cue i:after,.chip-y:before{animation:none!important}`;
function diff(a, b) {
  return JSON.parse(execFileSync('python3', ['-c', `
import sys, json
from PIL import Image
import numpy as np
A = np.asarray(Image.open(sys.argv[1]).convert('RGB'), dtype=np.int16); B = np.asarray(Image.open(sys.argv[2]).convert('RGB'), dtype=np.int16)
D = np.abs(A - B).max(axis=2)
print(json.dumps({'mean': round(float(D.mean()), 3), 'max': int(D.max()), 'over4': round(float((D > 4).mean() * 100), 3)}))
`, a, b]).toString());
}
(async () => {
  const browser = await chromium.launch({ headless: true });
  const res = [];
  for (const [w, h] of [[1920, 1080], [1366, 768], [2560, 1440], [1280, 800]]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h } });
    await ctx.addInitScript(() => { try { sessionStorage.setItem('pc-intro', '1'); } catch (e) { } });
    const page = await ctx.newPage(); const errs = []; page.on('pageerror', e => errs.push(String(e)));
    await page.goto(BASE + 'preview-lupa/?fx=full', { waitUntil: 'load' });
    await page.addStyleTag({ content: FREEZE });
    await sleep(5500);
    await page.evaluate(() => { document.querySelector('.hero-lens-img').style.backgroundImage = 'url("img/hero-dim.webp")'; });
    await sleep(500);
    const cases = [['дом', null, 0], ['мышь', [w * 0.8, h * 0.3], 0], ['край', [w - 5, h * 0.5], 0], ['прокрутка', [w * 0.7, h * 0.35], 300]];
    for (const [name, pos, scroll] of cases) {
      if (pos) { await page.mouse.move(pos[0] - 30, pos[1] - 20); await page.mouse.move(pos[0], pos[1], { steps: 5 }); }
      if (scroll) { await page.mouse.wheel(0, scroll); await sleep(1800); }
      await sleep(2300);
      const a = path.join(OUT, `al-${w}-${name}-on.png`), b = path.join(OUT, `al-${w}-${name}-off.png`);
      await page.screenshot({ path: a });
      const st = await page.evaluate(() => { const l = document.getElementById('heroLens'); const r = l.getBoundingClientRect(); l.style.visibility = 'hidden'; return { on: l.classList.contains('on'), op: getComputedStyle(l).opacity, c: [Math.round(r.left + r.width / 2), Math.round(r.top + r.height / 2)], y: Math.round(scrollY), mt: getComputedStyle(document.getElementById('heroMedia')).transform }; });
      await sleep(150);
      await page.screenshot({ path: b });
      await page.evaluate(() => { document.getElementById('heroLens').style.visibility = ''; });
      res.push({ vp: w + 'x' + h, name, ...st, ...diff(a, b) });
    }
    if (errs.length) res.push({ vp: w + 'x' + h, errs });
    await ctx.close();
  }
  // первый визит с заставкой: когда появляется лупа
  {
    const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
    const page = await ctx.newPage(); const errs = []; page.on('pageerror', e => errs.push(String(e)));
    await page.goto(BASE + 'preview-lupa/?fx=full', { waitUntil: 'load' });
    const tl = [];
    for (let i = 0; i < 14; i++) {
      tl.push(await page.evaluate(() => { const l = document.getElementById('heroLens'); return { t: Math.round(performance.now()), intro: !!document.getElementById('intro'), t0: window.pcHero && window.pcHero.t0 && Math.round(window.pcHero.t0), on: l.classList.contains('on'), op: (+getComputedStyle(l).opacity).toFixed(2), bg: getComputedStyle(document.querySelector('.hero-bg')).transform }; }));
      await sleep(500);
    }
    res.push({ intro: tl, errs });
    await ctx.close();
  }
  console.log(JSON.stringify(res, null, 1));
  await browser.close();
})().catch(e => { console.error('FATAL', e); process.exit(1); });
