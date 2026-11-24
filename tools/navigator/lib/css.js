/* nv.css = стили прототипа (src/prototype.css) с приставкой nv- и областью .nv + дополнения для сайта (src/extra.css) */
'use strict';
const fs = require('fs'), path = require('path');
const DROP = /(^|[\s,>+~(])(html|body|main)\b|\.(top|top-in|top-tel|logo|logo-mark|logo-name|logo-sub|logo-txt|product|tabs|tabs-in|skip|wrap|foot|foot-in|foot-h|boot|is-home|crumbs|form|ok-box|err)(?![\w-])/;
function sel(s) {
  return s.split(',').map(x => x.trim()).filter(x => x && !DROP.test(x)).map(x => {
    if (x === ':root') return '.nv';
    return '.nv ' + x.replace(/\.([a-zA-Z_][\w-]*)/g, '.nv-$1');
  }).join(',');
}
function walk(css) {            // правила верхнего уровня и вложенные в @media
  let out = '', i = 0;
  while (i < css.length) {
    const o = css.indexOf('{', i); if (o < 0) break;
    const head = css.slice(i, o).replace(/\/\*[\s\S]*?\*\//g, '').trim();
    let d = 1, j = o + 1;
    while (j < css.length && d) { if (css[j] === '{') d++; else if (css[j] === '}') d--; j++; }
    const body = css.slice(o + 1, j - 1);
    if (head.indexOf('@font-face') === 0) { /* шрифт уже подключён сайтом */ }
    else if (head[0] === '@') { const inner = walk(body); if (inner) out += head + '{' + inner + '}\n'; }
    else { const s = sel(head); if (s) out += s + '{' + body.trim() + '}\n'; }
    i = j;
  }
  return out;
}
exports.build = function () {
  const proto = fs.readFileSync(path.join(__dirname, '..', 'src', 'prototype.css'), 'utf8');
  const extra = fs.readFileSync(path.join(__dirname, '..', 'src', 'extra.css'), 'utf8');
  return '/* Санитарный навигатор: стили раздела. Собирается tools/navigator/build.js — правьте src/prototype.css и src/extra.css */\n' + walk(proto) + extra;
};
