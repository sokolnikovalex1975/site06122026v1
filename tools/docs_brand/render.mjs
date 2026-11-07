// Печать фирменных элементов документов (Playwright / Chromium).
//   node render.mjs header <in.html> <out.pdf> [<out.png>]  — PDF размером ровно с шапку (.hd или .rh) и PNG 600 dpi для Word
//   node render.mjs page <in.html> <out.pdf> <w_mm> <h_mm>   — PDF одной страницы заданного размера (водяной знак)
//   node render.mjs doc <in.html> <out.pdf>                  — документ A4 без полей, с фоном (программа пест-контроля:
//                                                              те же настройки печати, что у генератора образца)
import { chromium } from 'playwright';

const [,, mode, inHtml, outPdf, a4, a5] = process.argv;
const b = await chromium.launch({ headless: true });
if (mode === 'header') {
  const pg = await b.newPage({ deviceScaleFactor: 600 / 96 });
  await pg.goto('file://' + inHtml, { waitUntil: 'load' });
  await pg.evaluate(() => document.fonts.ready);
  const box = await pg.evaluate(() => {
    const r = document.querySelector('.hd, .rh').getBoundingClientRect();
    return { w: r.width, h: r.height };
  });
  const mm = (px) => (px * 25.4 / 96);
  await pg.pdf({ path: outPdf, width: mm(box.w).toFixed(3) + 'mm', height: (mm(box.h) + 0.05).toFixed(3) + 'mm',
                 printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  if (a4) await (await pg.$('.hd, .rh')).screenshot({ path: a4, omitBackground: true });
  console.log(JSON.stringify({ w_mm: +mm(box.w).toFixed(3), h_mm: +mm(box.h).toFixed(3) }));
} else if (mode === 'page') {
  const pg = await b.newPage();
  await pg.goto('file://' + inHtml, { waitUntil: 'load' });
  await pg.pdf({ path: outPdf, width: a4 + 'mm', height: a5 + 'mm', printBackground: true,
                 margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  console.log('ok', outPdf);
} else if (mode === 'doc') {
  const pg = await b.newPage();
  await pg.goto('file://' + inHtml, { waitUntil: 'networkidle' });
  await pg.evaluateHandle('document.fonts.ready');
  await pg.emulateMedia({ media: 'print' });
  await pg.pdf({ path: outPdf, format: 'A4', printBackground: true,
                 margin: { top: '0mm', right: '0mm', bottom: '0mm', left: '0mm' } });
  console.log('ok', outPdf);
}
await b.close();
