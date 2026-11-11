// Картинки для соцсетей страниц «Акт дератизации и дезинсекции» и «Схема точек пест-контроля» (1200×630).
//   node tools/materialy-dokumenty/og.mjs     (из корня репозитория; нужен playwright)
// Шаблон карточки — общий с нормативной базой: tools/normativnaya-baza/og/og.html. Фото — make_images.py.
import { chromium } from '/home/user/node_modules/playwright/index.mjs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const tpl = path.join(root, 'tools/normativnaya-baza/og/og.html');
const cards = [
  { out: 'img/akt-og.jpg', photo: 'img/akt-hero.webp', ey: 'Материалы · образец и бланк PDF',
    h1: 'Акт дератизации и дезинсекции: <em>образец и что в нём указать</em>', ft: 'Реквизиты акта, ошибки и хранение' },
  { out: 'img/skhema-og.jpg', photo: 'img/skhema-hero.webp', ey: 'Материалы · образец PDF',
    h1: 'Схема точек пест-контроля: <em>образец и правила</em>', ft: 'Контуры защиты, нумерация и обозначения точек' },
];
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
for (const c of cards) {
  await page.goto('file://' + tpl);
  await page.evaluate(({ c, root }) => {
    document.getElementById('ph').src = 'file://' + root + '/' + c.photo;
    document.getElementById('ey').textContent = c.ey;
    document.getElementById('h1').innerHTML = c.h1.replace(/ (\S{1,2}) /g, ' $1\u00a0');
    document.getElementById('ft').textContent = c.ft;
  }, { c, root });
  await page.waitForFunction(() => document.getElementById('ph').complete && document.fonts.status === 'loaded');
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(root, c.out), type: 'jpeg', quality: 86 });
  console.log('ok', c.out);
}
await browser.close();
