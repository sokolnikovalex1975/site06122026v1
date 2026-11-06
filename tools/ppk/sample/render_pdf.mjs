// Печать образца ППК: ppk.html → PDF (A4, колонтитулы Chromium) + PNG рисунков для DOCX.
// node render_pdf.mjs <dir> <out.pdf> [--figs]
import { chromium } from 'playwright';
import fs from 'fs';
const [,, dir, outPdf, figs] = process.argv;
const tpl = JSON.parse(fs.readFileSync(dir + '/templates.json', 'utf8'));
const b = await chromium.launch({ headless: true });
const pg = await b.newPage();
await pg.goto('file://' + dir + '/ppk.html', { waitUntil: 'load' });
await pg.evaluate(() => document.fonts.ready);
await pg.pdf({
  path: outPdf, format: 'A4', printBackground: true, preferCSSPageSize: true,
  displayHeaderFooter: true, headerTemplate: tpl.header, footerTemplate: tpl.footer,
  margin: { top: '20mm', bottom: '15mm', left: '17mm', right: '13mm' },
});
if (figs === '--figs') {
  for (const name of ['plan', 'flow']) {
    const p2 = await b.newPage({ deviceScaleFactor: 3.2, viewport: { width: 720, height: 1000 } });
    await p2.goto('file://' + dir + '/' + name + '.html', { waitUntil: 'load' });
    await p2.evaluate(() => document.fonts.ready);
    const el = await p2.$('#fig');
    await el.screenshot({ path: dir + '/' + name + '.png' });
    await p2.close();
  }
}
await b.close();
console.log('ok', outPdf);
