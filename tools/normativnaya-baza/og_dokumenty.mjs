// Картинка для соцсетей страницы «Документы для Роспотребнадзора»: img/dok-og.jpg (1200×630), стиль — как nb-og.jpg и pl-og.jpg.
// Запуск из корня репозитория: node tools/normativnaya-baza/og_dokumenty.mjs  (нужны playwright и img/dok-cover-720.webp)
import fs from 'fs';
import path from 'path';
import { chromium } from 'playwright';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const f = (p) => 'file://' + path.join(ROOT, p);
const html = `<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>
@font-face{font-family:Inter;font-weight:100 900;src:url(${f('fonts/inter-ru-wght-normal.woff2')})}
@font-face{font-family:Inter;font-style:italic;font-weight:100 900;src:url(${f('fonts/inter-ru-wght-italic.woff2')})}
*{box-sizing:border-box}
body{margin:0;width:1200px;height:630px;overflow:hidden;font-family:Inter;color:#fff;position:relative;
background:radial-gradient(760px 460px at 86% 6%,rgba(97,95,255,.26),transparent 66%),radial-gradient(700px 420px at 0% 100%,rgba(124,134,255,.08),transparent 60%),#09090b}
.brand{position:absolute;left:72px;top:64px;display:flex;align-items:center;gap:14px;font-weight:600;font-size:24px;letter-spacing:-.02em}
.brand small{font-size:13px;color:#7c86ff;letter-spacing:.14em;font-weight:500;margin-left:4px}
.k{position:absolute;left:72px;top:190px;display:flex;align-items:center;gap:14px;font-size:16px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#7c86ff}
.k::before{content:"";width:40px;height:2px;background:#7c86ff}
h1{position:absolute;left:72px;top:232px;width:700px;margin:0;font-weight:300;font-size:64px;line-height:1.06;letter-spacing:-.045em}
h1 em{font-style:italic;font-weight:600}
.foot{position:absolute;left:72px;right:72px;bottom:54px;display:flex;justify-content:space-between;font-size:20px;color:#a1a1aa}
.foot b{color:#fff;font-weight:600}
.doc{position:absolute;right:92px;top:92px;width:300px;border-radius:10px;transform:rotate(4deg);box-shadow:0 40px 90px rgba(0,0,0,.65),0 0 0 1px rgba(255,255,255,.08)}
</style></head><body>
<div class="brand"><svg width="48" height="48" viewBox="0 0 48 48"><circle cx="24" cy="24" r="23" fill="#09090b" stroke="rgba(255,255,255,.25)"/><g transform="translate(12 12)" fill="none" stroke-width="1.6" stroke-linejoin="round"><path d="M12 2.5l7.5 3v6c0 5-3.2 8.6-7.5 10-4.3-1.4-7.5-5-7.5-10v-6z" stroke="#fff"/><circle cx="12" cy="11.5" r="2.6" stroke="#7c86ff"/><path d="M12 6.2v2.7M12 14.1v2.7M6.8 11.5h2.6M14.6 11.5h2.6" stroke="#7c86ff"/></g></svg>ПЕСТКОНТРОЛЬ<small>ЦЕНТР</small></div>
<div class="k">Нормативная база · чек-лист PDF</div>
<h1>Документы для Роспотребнадзора: <em>полный перечень для&nbsp;проверки</em></h1>
<img class="doc" src="${f('img/dok-cover-720.webp')}" alt="">
<div class="foot"><span>41 общий документ и разделы для 8 видов объектов</span><b>пестконтроль-центр.рф</b></div>
</body></html>`;
const tmp = '/tmp/dok_og.html';
fs.writeFileSync(tmp, html);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
await p.goto('file://' + tmp);
await p.evaluate(() => document.fonts.ready);
await p.waitForTimeout(300);
await p.screenshot({ path: path.join(ROOT, 'img/dok-og.jpg'), type: 'jpeg', quality: 84 });
await b.close();
console.log('ok img/dok-og.jpg');
