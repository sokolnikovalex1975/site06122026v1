// Картинки для соцсетей раздела «Нормативная база»: img/nb-og.jpg и img/pl-og.jpg (1200×630).
//   node tools/normativnaya-baza/og/render.mjs          (из корня репозитория; нужен playwright)
// Фото — img/nb-hero.webp и img/pl-hero.webp (их делает make_images.py), тексты — ниже.
import { chromium } from '/home/user/node_modules/playwright/index.mjs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const cards = [
  { out: 'img/nb-og.jpg', photo: 'img/nb-hero.webp', ey: 'Нормативная база · проверено 06.11.2026',
    h1: 'СанПиН и требования к дезинсекции и дератизации: <em>что действует в 2026 году</em>',
    ft: 'Документы, сроки, периодичность, лицензия' },
  { out: 'img/pl-og.jpg', photo: 'img/pl-hero.webp', ey: 'Нормативная база · приказы № 578 и № 580',
    h1: 'Проверочные листы Роспотребнадзора 2026: <em>вопросы о дезинсекции и дератизации</em>',
    ft: 'Вопросы по видам объектов и документы для ответа' },
];
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
for (const c of cards) {
  await page.goto('file://' + path.join(here, 'og.html'));
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
