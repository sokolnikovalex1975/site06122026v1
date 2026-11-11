// Хлебные крошки первого экрана на всех страницах (правило владельца 11.11.2026).
//
//   python3 -m http.server 8833          # в корне репозитория
//   node tools/qa/check_crumbs.mjs [BASE] # BASE по умолчанию http://localhost:8833/; можно адрес рабочего сайта
//
// Компьютер и планшет (1024×768, 1280×720, 1440×900, 1920×1080): крошки видны, стоят над заголовком H1,
// до ближайшей кнопки первого экрана (над ней или под ней) — не меньше 24 px.
// Телефон (360×740, 390×844, 768×1024, 900×1000): крошки скрыты или стоят ниже кнопок первого экрана
// (не меньше 24 px) — первый экран не занимают.
// Список страниц — tools/menu/apply_menu.PAGES. Код выхода 1, если есть нарушения.
// Playwright: переменная PW (по умолчанию /home/user/node_modules/playwright/index.mjs).
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const BASE = process.argv[2] || 'http://localhost:8833/';
const { chromium } = await import(process.env.PW || '/home/user/node_modules/playwright/index.mjs');
const pages = JSON.parse(execFileSync('python3', ['-c',
  "import sys,json;sys.path.insert(0,'tools/menu');import apply_menu as A;print(json.dumps([f[:-len('index.html')] for f,_,_ in A.PAGES]))"],
  { cwd: ROOT, encoding: 'utf-8' }));
const DESK = [[1024, 768], [1280, 720], [1440, 900], [1920, 1080]];
const MOB = [[360, 740], [390, 844], [768, 1024], [900, 1000]];
const MIN = 24;

const measure = () => {
  const vis = (e) => e && e.offsetParent !== null && e.getBoundingClientRect().height > 0;
  const c = [...document.querySelectorAll('#hero .d-crumbs,#hero .f-crumbs,main .d-crumbs,main .f-crumbs')].find(vis);
  const hero = document.querySelector('#hero') || document.querySelector('main section');
  const btns = hero ? [...hero.querySelectorAll('.btn')].filter(vis).map((e) => e.getBoundingClientRect()) : [];
  const h1 = document.querySelector('#hero h1, main h1');
  const r = { crumbs: !!c, h1Top: h1 ? Math.round(h1.getBoundingClientRect().top) : null,
    btnBottom: btns.length ? Math.round(Math.max(...btns.map((b) => b.bottom))) : null };
  if (!c) return r;
  const cb = c.getBoundingClientRect();
  r.top = Math.round(cb.top); r.bottom = Math.round(cb.bottom);
  let gap = null;
  for (const b of btns) {
    if (b.right < cb.left || b.left > cb.right) continue;  // кнопка в другой колонке
    const g = b.bottom <= cb.top ? cb.top - b.bottom : b.top >= cb.bottom ? b.top - cb.bottom : -1;
    if (gap === null || g < gap) gap = g;
  }
  r.gap = gap === null ? null : Math.round(gap);
  return r;
};

const b = await chromium.launch();
const bad = [];
let checked = 0;
for (const [mode, sizes] of [['desk', DESK], ['mob', MOB]]) {
  for (const [w, h] of sizes) {
    const ctx = await b.newContext({ viewport: { width: w, height: h } });
    for (const p of pages) {
      const pg = await ctx.newPage();
      try {
        await pg.goto(BASE + p, { waitUntil: 'networkidle', timeout: 45000 });
        await pg.waitForTimeout(1200);
        const r = await pg.evaluate(measure);
        checked++;
        const where = `${w}×${h} /${p}`;
        if (mode === 'desk') {
          if (!r.crumbs) continue;  // страница без крошек (главная)
          if (r.h1Top !== null && r.bottom > r.h1Top) bad.push(`${where}: крошки ниже заголовка (крошки ${r.top}, H1 ${r.h1Top})`);
          if (r.gap !== null && r.gap < MIN) bad.push(`${where}: до кнопки ${r.gap} px`);
        } else if (r.crumbs) {
          if (r.btnBottom === null || r.top < r.btnBottom + MIN) bad.push(`${where}: крошки на первом экране телефона (крошки ${r.top}, кнопки до ${r.btnBottom})`);
        }
      } catch (e) {
        bad.push(`${w}×${h} /${p}: ошибка ${e.message.slice(0, 80)}`);
      }
      await pg.close();
    }
    await ctx.close();
  }
}
await b.close();
console.log(`проверено: ${pages.length} страниц × ${DESK.length + MOB.length} размеров (${checked} замеров)`);
if (bad.length) { console.log('нарушения:\n  ' + bad.join('\n  ')); process.exit(1); }
console.log('крошки: на компьютере и планшете — над заголовком, до кнопок не меньше 24 px; на телефоне — скрыты или ниже кнопок');
