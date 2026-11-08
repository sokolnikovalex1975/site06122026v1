// Печать опросного листа (Playwright / Chromium): раскладка блоков по листам A4 и PDF.
//   node render_pdf.mjs <in.html> <out.pdf>   → в stdout JSON: {pages, overflow: [...]}
// Блоки из #src переносятся на листы по порядку; таблица вопросов делится по строкам, на новом листе
// заголовок раздела повторяется с пометкой «продолжение»; заголовок не остаётся внизу листа без вопросов.
import { chromium } from 'playwright';

const [,, inHtml, outPdf] = process.argv;
const b = await chromium.launch({ headless: true });
const pg = await b.newPage();
await pg.goto('file://' + inHtml, { waitUntil: 'load' });
await pg.evaluate(() => document.fonts.ready);
const qa = await pg.evaluate(() => {
  const src = document.getElementById('src');
  const pages = document.getElementById('pages');
  const T = (id) => document.getElementById(id).content.firstElementChild.cloneNode(true);
  const list = [];
  let cur = null;
  const newPage = () => {
    const p = document.createElement('section');
    p.className = 'pg';
    p.appendChild(T('t-wm'));
    p.appendChild(list.length ? T('t-rh') : T('t-hd'));
    const bd = document.createElement('div');
    bd.className = 'bd';
    p.appendChild(bd);
    p.appendChild(T('t-ft'));
    pages.appendChild(p);
    list.push(p);
    cur = bd;
  };
  const fits = () => cur.scrollHeight <= cur.clientHeight + 0.5;
  const startTable = (blk) => {
    const el = blk.cloneNode(false);
    el.appendChild(blk.querySelector('colgroup').cloneNode(true));
    const tb = document.createElement('tbody');
    el.appendChild(tb);
    cur.appendChild(el);
    return { el, tb };
  };
  const contHead = (h) => {
    const c = h.cloneNode(true);
    c.classList.add('cont');
    const why = c.querySelector('.why');
    if (why) why.remove();
    c.querySelector('h2').insertAdjacentHTML('beforeend', '<small>продолжение</small>');
    return c;
  };
  newPage();
  let lastHead = null;
  for (const blk of [...src.children]) {
    if (blk.tagName === 'TABLE') {
      let t = startTable(blk);
      for (const r of [...blk.tBodies[0].rows]) {
        t.tb.appendChild(r);
        if (fits()) continue;
        t.tb.removeChild(r);
        if (!t.tb.rows.length) {
          t.el.remove();
          const h = cur.lastElementChild;
          const moveHead = h && h.classList.contains('sh');
          if (moveHead) h.remove();
          newPage();
          if (moveHead) cur.appendChild(h);
        } else {
          newPage();
          if (lastHead) cur.appendChild(contHead(lastHead));
        }
        t = startTable(blk);
        t.tb.appendChild(r);
      }
    } else {
      cur.appendChild(blk);
      if (blk.classList.contains('sh')) lastHead = blk;
      if (!fits() && cur.children.length > 1) {
        cur.removeChild(blk);
        newPage();
        cur.appendChild(blk);
      }
    }
  }
  src.remove();
  const overflow = [];
  list.forEach((p, i) => {
    p.querySelector('.pi').textContent = String(i + 1);
    p.querySelector('.pc').textContent = String(list.length);
    const bd = p.querySelector('.bd');
    if (bd.scrollHeight > bd.clientHeight + 1) overflow.push([i + 1, bd.scrollHeight - bd.clientHeight]);
  });
  const room = list.map((p) => {
    const bd = p.querySelector('.bd');
    const last = bd.lastElementChild;
    return last ? Math.round((bd.getBoundingClientRect().bottom - last.getBoundingClientRect().bottom) * 25.4 / 96) : 0;
  });
  return { pages: list.length, overflow, room_mm: room };
});
await pg.pdf({ path: outPdf, preferCSSPageSize: true, printBackground: true });
console.log(JSON.stringify(qa));
await b.close();
