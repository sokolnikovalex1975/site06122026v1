// Проверка: текст во flex-ссылках и подписях не разъезжается на колонки (замечание владельца 11.11.2026,
// «Подробнее о пест-контроле по GMP» на телефоне). Ищет flex/grid-элементы, где кусок текста соседствует со строчным
// тегом (span.nw, b, em…) — каждый такой кусок во flex становится отдельной колонкой.
// Запуск: BASE=http://localhost:8090 node tools/qa/flex_split_test.mjs  (нужен playwright: npm i playwright)
// Страницы — PAGES='/ /gostinitsy/' (по умолчанию все из server/sitemap.xml). Код 1 — есть нарушения.
import { chromium } from 'playwright';
import fs from 'fs';
const BASE = process.env.BASE || 'http://localhost:8090';
const SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai';
const PAGES = (process.env.PAGES || [...fs.readFileSync(new URL('../../server/sitemap.xml', import.meta.url), 'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1].replace(SITE, '')).join(' ')).trim().split(/\s+/);
const b = await chromium.launch(); const bad = [];
for (const [w, mob] of [[360, true], [390, true], [1440, false]]) {
  const ctx = await b.newContext({ viewport: { width: w, height: 800 }, isMobile: mob, reducedMotion: 'reduce' }); const p = await ctx.newPage();
  for (const pg of PAGES) {
    await p.goto(BASE + pg, { waitUntil: 'domcontentloaded' });
    const r = await p.evaluate(() => {
      const res = [];
      const inl = x => x && x.nodeType === 1 && !/^(svg|IMG|I)$/i.test(x.tagName) && x.textContent.trim() && (x.classList.contains('nw') || /^(B|STRONG|EM|A|NOBR|ABBR|U|SMALL|SUP|SUB|SPAN)$/.test(x.tagName));
      for (const el of document.querySelectorAll('body *')) {
        const cs = getComputedStyle(el);
        if (!/flex|grid/.test(cs.display) || /column/.test(cs.flexDirection) || el.closest('.strip-item, .nb-dot, .dzf-order')) continue;
        const kids = [...el.childNodes].filter(n => (n.nodeType === 3 && n.textContent.trim()) || n.nodeType === 1);
        const arrow = n => /^\s*[→←↗›»]+\s*$/.test(n.textContent);
        const hit = kids.some((n, i) => n.nodeType === 3 && !arrow(n) && ((inl(kids[i - 1]) && (/^\s/.test(n.textContent) || kids[i - 1].classList.contains('nw'))) || (inl(kids[i + 1]) && (/\s$/.test(n.textContent) || kids[i + 1].classList.contains('nw')))));
        // структурные пары «значок/номер + подпись» (.strip-item, .nb-dot, h3 с номером) — без пробела на стыке, не ошибка
        if (hit) res.push(el.className + ' :: ' + el.textContent.trim().replace(/\s+/g, ' ').slice(0, 70));
      }
      return res;
    });
    r.forEach(x => bad.push(`${w} ${pg} ${x}`));
  }
  await ctx.close();
}
await b.close();
const uniq = [...new Set(bad)];
uniq.forEach(x => console.log(x));
console.log(uniq.length ? `нарушений: ${uniq.length}` : 'ok: текст во flex-элементах не разбит');
process.exit(uniq.length ? 1 : 0);
