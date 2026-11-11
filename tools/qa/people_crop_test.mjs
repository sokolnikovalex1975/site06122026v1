// Проверка кадрирования фото с людьми (правило владельца 11.11.2026: голова не обрезана, человек виден целиком).
// Для каждой картинки с data-fp на каждой странице и экране считает по фактической раскладке:
//   head — запас над головой в px до верхнего края видимой части (с учётом шапки над первым экраном и параллакса);
//   side — запас от головы до боковых краёв, px;  body — какая доля высоты людей видна (1 = целиком).
// Запуск: BASE=http://localhost:8090 node tools/qa/people_crop_test.mjs > crop.json   (нужен playwright)
// PAGES='/ /gostinitsy/' — выбранные страницы; VP='[["m390",390,664,true]]' — экраны.
// Итог в stderr: строки с head < 4 px или side < 0 — голова у края или обрезана. Код 1, если такие есть.
import { chromium } from 'playwright';
import fs from 'fs';
const BASE = process.env.BASE || 'http://localhost:8090';
const SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai';
const PAGES = (process.env.PAGES || [...fs.readFileSync(new URL('../../server/sitemap.xml', import.meta.url), 'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1].replace(SITE, '')).join(' ')).trim().split(/\s+/);
const VPS = JSON.parse(process.env.VP || JSON.stringify([
  ['m320', 320, 480, true], ['m360', 360, 640, true], ['m375', 375, 553, true], ['m390', 390, 664, true], ['m390t', 390, 750, true],
  ['m430', 430, 740, true], ['t768', 768, 950, true], ['t1024', 1024, 700, true], ['d1280', 1280, 680, false], ['d1440', 1440, 800, false],
  ['d1920', 1920, 960, false], ['d2560', 2560, 1300, false]]));
const rows = [];
const b = await chromium.launch();
for (const [name, w, h, mob] of VPS) {
  const ctx = await b.newContext({ viewport: { width: w, height: h }, isMobile: mob, hasTouch: mob });
  const p = await ctx.newPage();
  for (const pg of PAGES) {
    try { await p.goto(BASE + pg, { waitUntil: 'load', timeout: 40000 }); } catch (e) { console.error('fail', pg); continue; }
    await p.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 500) { scrollTo(0, y); await new Promise(r => setTimeout(r, 40)); } scrollTo(0, 0); await new Promise(r => setTimeout(r, 300)); await Promise.race([Promise.all(document.getAnimations().filter(a => a.effect && a.effect.getTiming().iterations !== Infinity).map(a => a.finished.catch(() => 0))), new Promise(r => setTimeout(r, 3000))]); });  // вход первого экрана (hero_in.js) должен закончиться
    const r = await p.evaluate(() => {
      const out = [];
      const hdr = document.getElementById('hdr'); const hb = hdr && getComputedStyle(hdr).position === 'fixed' ? hdr.getBoundingClientRect().height : 0;
      const imgs = [...document.querySelectorAll('img')].filter(i => i.hasAttribute('data-fp') || (i.parentElement.tagName === 'PICTURE' && i.parentElement.querySelector('source[data-fp]')));
      for (const img of imgs) {
        if (img.classList.contains('fx-lit-img')) continue;
        const cs = getComputedStyle(img); if (cs.objectFit !== 'cover' || cs.display === 'none' || cs.visibility === 'hidden') continue;
        let el = img; const cur = img.currentSrc;
        const pic = img.parentElement; if (pic.tagName === 'PICTURE') for (const s of pic.querySelectorAll('source')) { if ((s.getAttribute('srcset') || '').split(',').some(u => cur.includes(u.trim().split(/\s+/)[0].replace(/^(\.\.\/)+|^\.\//, '')))) { el = s; break; } }
        const fp = el.getAttribute('data-fp'); if (!fp) continue;
        const v = fp.split(/\s+/).map(Number), S = v.slice(0, 4), H = v.slice(4, 8);
        const nw = img.naturalWidth, nh = img.naturalHeight; if (!nw) continue;
        const rc = img.getBoundingClientRect(); const W = rc.width, Hh = rc.height; if (W < 80 || Hh < 60) continue;
        const t = cs.transform; const sh = t && t !== 'none' ? parseFloat(t.match(/matrix\(([^)]+)\)/)[1].split(',')[5]) : 0;
        const top = rc.top - sh;
        let L = rc.left, T = top, R = rc.right, B = top + Hh, q = img.parentElement;
        while (q && q !== document.body) { const c = getComputedStyle(q); if (c.overflow !== 'visible' || c.overflowX !== 'visible' || c.overflowY !== 'visible') { const z = q.getBoundingClientRect(); L = Math.max(L, z.left); T = Math.max(T, z.top); R = Math.min(R, z.right); B = Math.min(B, z.bottom); } q = q.parentElement; }
        let vy0 = T - top, vy1 = B - top; const vx0 = L - rc.left, vx1 = R - rc.left;
        if (top + scrollY < hb) vy0 = Math.max(vy0, hb - (top + scrollY));
        if (vy1 - vy0 < 20 || vx1 - vx0 < 20) continue;
        const sc = Math.max(W / nw, Hh / nh), dw = nw * sc, dh = nh * sc;
        const [px, py] = cs.objectPosition.split(' ').map(s => parseFloat(s) / 100);
        const ox = (dw - W) * px, oy = (dh - Hh) * py;
        const m = img.hasAttribute('data-parallax') ? 0.035 * Hh : 0;
        const head = Math.round(H[1] * dh - oy - vy0 - m);
        const side = Math.round(Math.min(H[0] * dw - ox - vx0, vx1 - (H[2] * dw - ox)));
        const sTop = Math.max(S[1] * dh - oy, vy0 + m), sBot = Math.min(S[3] * dh - oy, vy1 - m);
        const body = +Math.max(0, (sBot - sTop) / ((S[3] - S[1]) * dh)).toFixed(2);
        out.push({ src: cur.split('/').pop().split('?')[0], head, side, body, box: [Math.round(W), Math.round(Hh)], vis: Math.round(vy1 - vy0), pos: cs.objectPosition, hero: !!img.closest('#hero') });
      }
      return out;
    });
    r.forEach(x => rows.push({ vp: name, page: pg, ...x }));
  }
  await ctx.close();
}
await b.close();
process.stdout.write(JSON.stringify(rows, null, 1));
const bad = rows.filter(x => x.head < 4 || x.side < 0);
for (const x of bad) console.error(`${x.vp} ${x.page} ${x.src}: голова ${x.head}px, сбоку ${x.side}px, видно людей ${Math.round(x.body * 100)}%`);
console.error(bad.length ? `проблем: ${bad.length} из ${rows.length}` : `ok: ${rows.length} фото — головы в кадре`);
process.exit(bad.length ? 1 : 0);
