import { chromium } from 'playwright';
import fs from 'fs';
const BASE = process.env.BASE || 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai';
const PAGES = (process.env.PAGES || [...fs.readFileSync(new URL('../../server/sitemap.xml', import.meta.url), 'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1].replace('https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai', '')).join(' ') + ' /privacy/ /soglasie/').trim().split(/\s+/);
const WIDTHS = (process.env.WIDTHS || '320 360 375 390 414 768').split(' ').map(Number);
const CSS = process.env.CSS ? fs.readFileSync(process.env.CSS,'utf8') : '';
const b = await chromium.launch(); const out = [];
for (const w of WIDTHS) {
  const ctx = await b.newContext({ viewport: { width: w, height: 800 }, isMobile: w < 900, hasTouch: w<900, deviceScaleFactor: 2, reducedMotion: 'reduce' });
  await ctx.route(/mc\.yandex|uiscom|comagic|radist/, r => r.abort());
  const p = await ctx.newPage();
  for (const pg of PAGES) {
    try { await p.goto(BASE + pg, { waitUntil: 'load', timeout: 45000 }); } catch(e) { out.push(`${w} ${pg} LOADFAIL`); continue; }
    if (CSS) await p.addStyleTag({ content: CSS });
    await p.waitForTimeout(300);
    const r = await p.evaluate(() => {
      const res = []; const vw = document.documentElement.clientWidth;
      if (document.documentElement.scrollWidth > vw + 1) res.push('HSCROLL doc ' + document.documentElement.scrollWidth);
      const vis = el => { const cs = getComputedStyle(el); return cs.display !== 'none' && cs.visibility !== 'hidden' && el.getClientRects().length; };
      const inScroll = el => { for (let a = el.parentElement; a; a = a.parentElement) { const o = getComputedStyle(a).overflowX; if (/auto|scroll/.test(o) && a.scrollWidth > a.clientWidth + 1) return true; } return false; };
      const skip = el => el.closest('.marquee, .strip, .ticker, [aria-hidden="true"], .m-menu, .mnav, nav[hidden], .srch, dialog, .lens, #heroLens, .tbl-wrap, .table-wrap, [class*="scroll"], .d-dd, .dd');
      const inl = x => x && x.nodeType === 1 && !/^(svg|IMG|I)$/i.test(x.tagName) && x.textContent.trim() && (x.classList.contains('nw') || /^(B|STRONG|EM|A|NOBR|ABBR|U|SMALL|SUP|SUB|SPAN)$/.test(x.tagName));
      for (const el of document.querySelectorAll('body *')) {
        if (!vis(el) || skip(el) || inScroll(el)) continue;
        const cs = getComputedStyle(el);
        const txt = el.textContent.trim().replace(/\s+/g,' ').slice(0,60);
        const id = el.tagName.toLowerCase() + (el.className && typeof el.className==='string' ? '.'+el.className.trim().split(/\s+/).join('.') : '');
        // flex split
        if (/flex|grid/.test(cs.display) && !/column/.test(cs.flexDirection) && !el.closest('.strip-item, .nb-dot, .dzf-order')) {
          const kids = [...el.childNodes].filter(n => (n.nodeType === 3 && n.textContent.trim()) || n.nodeType === 1);
          const arrow = n => /^\s*[→←↗›»]+\s*$/.test(n.textContent);
          if (kids.some((n, i) => n.nodeType === 3 && !arrow(n) && ((inl(kids[i - 1]) && (/^\s/.test(n.textContent) || kids[i - 1].classList.contains('nw'))) || (inl(kids[i + 1]) && (/\s$/.test(n.textContent) || kids[i + 1].classList.contains('nw'))))))
            res.push('FLEXSPLIT ' + id + ' :: ' + txt);
        }
        // clipped content
        if (/hidden|clip/.test(cs.overflowX) && el.scrollWidth > el.clientWidth + 2 && txt && !/^(IMG|PICTURE|VIDEO|svg)$/i.test(el.tagName)) {
          // ignore if overflow is due to images only
          const hasTextOverflow = [...el.querySelectorAll('*')].concat([el]).some(c => { if (!c.childNodes) return false; for (const n of c.childNodes) if (n.nodeType===3 && n.textContent.trim()) { const rg = document.createRange(); rg.selectNodeContents(n); for (const rc of rg.getClientRects()) { const er = el.getBoundingClientRect(); if (rc.right > er.right + 1 || rc.left < er.left - 1) return true; } } return false; });
          if (hasTextOverflow) res.push('CLIP ' + id + ' :: ' + txt + ` (${el.scrollWidth}>${el.clientWidth})`);
        }
        // text outside viewport
        for (const n of el.childNodes) if (n.nodeType===3 && n.textContent.trim()) { const rg = document.createRange(); rg.selectNodeContents(n); for (const rc of rg.getClientRects()) if (rc.width && (rc.right > vw + 1 || rc.left < -1)) { res.push('OUTVW ' + id + ' :: ' + txt + ` (${Math.round(rc.left)}..${Math.round(rc.right)})`); break; } }
      }
      return [...new Set(res)];
    });
    r.forEach(x => out.push(`${w} ${pg} ${x}`));
  }
  await ctx.close();
}
await b.close();
fs.writeFileSync(process.env.OUT || 'report.txt', out.join('\n'));
console.log(out.length);
