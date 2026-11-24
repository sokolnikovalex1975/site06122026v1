// Картинки для соцсетей страниц статей «Пест-контроль по ISO 22000 и FSSC 22000» и «Лицензия на дезинфекцию» (1200×630).
//   node tools/materialy-stati/og.mjs     (из корня репозитория; нужен playwright)
// Шаблон карточки — общий с нормативной базой: tools/normativnaya-baza/og/og.html. Фото — make_images.py.
import { chromium } from '/home/user/node_modules/playwright/index.mjs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../..');
const tpl = path.join(root, 'tools/normativnaya-baza/og/og.html');
const cards = [
  { out: 'img/iso-og.jpg', photo: 'img/iso-hero.webp', ey: 'Материалы · сертификация пищевых производств',
    h1: 'Пест-контроль по ISO 22000 и FSSC 22000: <em>что проверяет аудитор</em>', ft: 'ГОСТ Р 54762-2011, FSSC 22000 версии 7, BRCGS и IFS' },
  { out: 'img/lic-og.jpg', photo: 'img/lic-hero.webp', ey: 'Материалы · выбор подрядчика',
    h1: 'Лицензия на дезинфекцию и дератизацию: <em>как проверить подрядчика</em>', ft: 'Реестр Роспотребнадзора, сроки и требования к исполнителю' },
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
