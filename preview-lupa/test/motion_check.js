// Слабый ноутбук: в покое замер показывает норму, при движении мыши (1 ядро, замедление x4) должен включиться
// облегчённый режим. node motion_check.js [base]
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const BASE = process.argv[2] || 'http://127.0.0.1:8811/';
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const wrap = path.join(__dirname, 'chrome-1core.sh'); /* Chrome на одном ядре */
  fs.writeFileSync(wrap, '#!/bin/sh\nexec taskset -c 0 "' + chromium.executablePath() + '" "$@"\n'); fs.chmodSync(wrap, 0o755);
  const browser = await chromium.launch({ executablePath: wrap });
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 768 } });
  await ctx.addInitScript(() => { try { sessionStorage.setItem('pc-intro', '1'); } catch (e) { } });
  const page = await ctx.newPage(); const errs = []; page.on('pageerror', e => errs.push(String(e)));
  await page.goto(BASE + 'preview-lupa/', { waitUntil: 'load' });
  await page.waitForFunction(() => document.documentElement.hasAttribute('data-fps') || document.documentElement.classList.contains('lowfx'), null, { timeout: 20000 });
  console.log('after probe:', await page.evaluate(() => [document.documentElement.className, document.documentElement.getAttribute('data-fps')]));
  const cdp = await ctx.newCDPSession(page); await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
  const t0 = Date.now(); let switched = null;
  while (Date.now() - t0 < 12000) {
    const t = (Date.now() - t0) / 1000;
    await page.mouse.move(1366 * 0.66 + 230 * Math.cos(t * 2.4), 768 * 0.46 + 150 * Math.sin(t * 3.1));
    await sleep(16);
    if (!switched && await page.evaluate(() => document.documentElement.classList.contains('lowfx'))) switched = ((Date.now() - t0) / 1000).toFixed(1);
  }
  console.log('switched to lowfx after', switched, 's of movement;', await page.evaluate(() => [document.documentElement.className, document.documentElement.getAttribute('data-fps'), document.getElementById('lupaMode').textContent]), errs);
  await browser.close();
})();
