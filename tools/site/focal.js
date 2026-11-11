/* Кадрирование фото с людьми — правило владельца 11.11.2026: «не должно быть такого, что видны только части тела,
   должен быть виден весь человек». Голова не уходит за край кадра и под шапку сайта ни на одном экране.

   У каждой картинки с людьми в разметке есть data-fp="x0 y0 x1 y1 hx0 hy0 hx1 hy1" (доли ширины и высоты исходника):
   рамка всех людей в кадре и рамка их голов (из tools/site/focal_points.json, вставляет tools/site/focal_points.py).
   У <source> в <picture> — свой data-fp для своего файла. Для каждой картинки с object-fit: cover скрипт считает,
   какая часть исходника видна в рамке (с учётом обрезки родителем, фиксированной шапки над первым экраном и сдвига
   параллакса ±3,5 %), и ставит object-position так, чтобы:
     1) голова целиком в кадре с запасом сверху (важнее всего);
     2) человек целиком, если помещается, — по центру кадра; если не помещается — от головы вниз, сколько влезет.
   Меняется только object-position: раскладка страницы не сдвигается (CLS = 0). Пересчёт — при загрузке картинки,
   изменении размера окна и повороте экрана. Если на первом экране голова оказывается под фиксированной шапкой
   и поднять фото уже некуда, фото опускается под шапку (top: N px) — над ним остаётся тёмный фон шапки. Исходник этого файла — tools/site/focal.js; на страницы он попадает
   сжатым одной строкой <script id="focal-js"> сразу после первого экрана (до первой отрисовки фото).
*/
(function () {
  var W = window, D = document;
  function num(v) { return parseFloat(v) || 0; }
  function headerBottom() {
    var h = D.getElementById('hdr') || D.querySelector('header');
    if (!h) return 0;
    var cs = getComputedStyle(h);
    if (cs.position !== 'fixed' && cs.position !== 'sticky') return 0;
    return h.getBoundingClientRect().height + Math.max(0, num(cs.top));
  }
  function inSrcset(el, url) {
    var ss = (el.getAttribute('srcset') || el.getAttribute('src') || '').split(',');
    for (var i = 0; i < ss.length; i++) {
      var u = ss[i].trim().split(/\s+/)[0];
      if (u && url.indexOf(u.replace(/^(\.\.\/)+|^\.\//, '')) !== -1) return true;
    }
    return false;
  }
  // data-fp и размеры того файла, который сейчас показан
  function pick(img) {
    var cur = img.currentSrc || '', pic = img.parentElement, el = null;
    if (pic && pic.tagName === 'PICTURE') {
      var ss = pic.getElementsByTagName('source');
      for (var i = 0; i < ss.length && !el; i++) {
        var s = ss[i];
        if (cur ? inSrcset(s, cur) : (!s.media || W.matchMedia(s.media).matches)) el = s;
      }
    }
    if (!el) el = img;
    var fp = el.getAttribute('data-fp');
    if (!fp) return null;
    var nw = img.naturalWidth, nh = img.naturalHeight;
    if (!nw || !nh || (el !== img && !img.complete)) { nw = num(el.getAttribute('width')) || nw; nh = num(el.getAttribute('height')) || nh; }
    if (!nw || !nh) return null;
    var v = fp.split(/\s+/).map(num);
    return { s: v.slice(0, 4), h: v.slice(4, 8), nw: nw, nh: nh };
  }
  // сдвиг transform (параллакс gsap, масштаб интро) — считаем по раскладке без него
  function tr(img) {
    var t = getComputedStyle(img).transform;
    if (!t || t === 'none') return [0, 0];
    var m = t.match(/matrix\(([^)]+)\)/);
    if (!m) return [0, 0];
    var a = m[1].split(',');
    return [num(a[4]), num(a[5])];
  }
  function solve(lo, hi, subLo, subHi, center, prio) {
    // смещение off в [lo, hi]; если голова не помещается (lo > hi) — приоритет у верхней границы головы (prio)
    if (lo > hi) return prio;
    if (subLo <= subHi) return Math.min(hi, Math.max(lo, Math.min(subHi, Math.max(subLo, center))));
    return Math.min(hi, Math.max(lo, subLo));
  }
  var hb = 0;
  function fit(img, again) {
    if (getComputedStyle(img).objectFit !== 'cover') return;
    var f = pick(img);
    if (!f) return;
    if (!again && img.hasAttribute('data-fp-top')) { img.style.top = ''; img.removeAttribute('data-fp-top'); }
    var w = img.offsetWidth, h = img.offsetHeight;
    if (w < 2 || h < 2) return;
    var r = img.getBoundingClientRect(), t = tr(img);
    var left = r.left + r.width / 2 - t[0] - w / 2, top = r.top + r.height / 2 - t[1] - h / 2;
    var sc = Math.max(w / f.nw, h / f.nh), dw = f.nw * sc, dh = f.nh * sc;
    // видимая часть рамки картинки (обрезка родителями)
    var L = left, T = top, R = left + w, B = top + h, p = img.parentElement;
    while (p && p !== D.body) {
      var cs = getComputedStyle(p);
      if (cs.overflow !== 'visible' || cs.overflowX !== 'visible' || cs.overflowY !== 'visible') {
        var q = p.getBoundingClientRect();
        L = Math.max(L, q.left); T = Math.max(T, q.top); R = Math.min(R, q.right); B = Math.min(B, q.bottom);
      }
      p = p.parentElement;
    }
    var vx0 = L - left, vx1 = R - left, vy0 = T - top, vy1 = B - top;
    // фиксированная шапка над картинками первого экрана
    var pageTop = top + W.pageYOffset, under = pageTop < hb;
    if (under) vy0 = Math.max(vy0, hb - pageTop);
    if (vx1 - vx0 < 2 || vy1 - vy0 < 2) return;
    var m = img.hasAttribute('data-parallax') ? 0.037 * h : 0;  // ход параллакса ±3,5 % высоты (app.js)
    var pad = Math.max(6, 0.035 * h), padx = Math.max(4, 0.03 * w);
    var s = f.s, hd = f.h, maxY = Math.max(0, dh - h), maxX = Math.max(0, dw - w);
    // по вертикали: oy — на сколько картинка поднята вверх
    var hiY = hd[1] * dh - vy0 - m - pad, loY = hd[3] * dh - vy1 + m;
    var oy = solve(Math.max(0, loY), Math.min(maxY, hiY), s[3] * dh - vy1 + m, s[1] * dh - vy0 - m,
      (s[1] + s[3]) / 2 * dh - (vy0 + vy1) / 2, Math.min(maxY, Math.max(0, hiY)));
    var hiX = hd[0] * dw - vx0 - padx, loX = hd[2] * dw - vx1 + padx;
    var ox = solve(Math.max(0, loX), Math.min(maxX, hiX), s[2] * dw - vx1, s[0] * dw - vx0,
      (s[0] + s[2]) / 2 * dw - (vx0 + vx1) / 2, Math.min(maxX, Math.max(0, (hiX + loX) / 2)));
    var px = maxX > 0.5 ? ox / maxX * 100 : 50, py = maxY > 0.5 ? oy / maxY * 100 : 50;
    img.style.objectPosition = px.toFixed(2) + '% ' + py.toFixed(2) + '%';
    var head = hd[1] * dh - oy - vy0 - m;
    // голова под шапкой первого экрана и выше её не поднять: опускаем фото под шапку (сверху остаётся тёмный фон шапки)
    if (head < pad && under && !again && getComputedStyle(img).position === 'absolute') {
      var d = Math.min(Math.ceil(hb - pageTop), Math.ceil(pad - head));  // не ниже нижнего края шапки
      if (d > 0) {
        img.style.top = d + 'px';
        img.setAttribute('data-fp-top', d);
        return fit(img, true);
      }
    }
    // для проверки (tools/qa/people_crop_test.mjs): запас над головой в px, отрицательный — голову не уместить
    img.setAttribute('data-fp-head', Math.round(head));
  }
  function all() {
    hb = headerBottom();
    var list = D.querySelectorAll('img[data-fp], picture source[data-fp] ~ img');
    for (var i = 0; i < list.length; i++) fit(list[i]);
  }
  W.__focal = all;
  all();
  var t;
  function later() { clearTimeout(t); t = setTimeout(all, 120); }
  D.addEventListener('DOMContentLoaded', all);
  W.addEventListener('load', all);
  W.addEventListener('resize', later);
  W.addEventListener('orientationchange', later);
  D.addEventListener('load', function (e) { var el = e.target; if (el && el.tagName === 'IMG' && (el.hasAttribute('data-fp') || (el.parentElement && el.parentElement.tagName === 'PICTURE'))) fit(el); }, true);
})();
