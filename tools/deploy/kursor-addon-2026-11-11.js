/* Курсор «Фирменный прицел» (вариант В, решение владельца 11.11.2026) — дополнение к app.min.js сайта на Timeweb.
   На сайте app.min.js собран из версии app.js с «входом первого экрана» (v=20261111hero), которой нет в репозитории,
   поэтому новый раздел курсора из app.js не встраивается в него, а дописывается в конец этим блоком: курсор app.min.js
   двигает точку и кольцо как раньше, блок добавляет классы light / doc и подпись «Скачать PDF» / «Открыть» (стили —
   style.css), а точкам плана и [role=button] — состояние ссылки. Логика та же, что в разделе «курсор» app.js. */
(function () {
  if (!window.matchMedia || !matchMedia('(hover:hover) and (pointer:fine)').matches) return;
  var cur = document.querySelector('.cursor'), ring = document.querySelector('.cursor-ring');
  if (!cur || !ring) return;
  var lbl = document.createElement('b');
  lbl.className = 'cursor-lbl';
  ring.appendChild(lbl);
  var lastT = null, hot = false, lightCache = new WeakMap(), imgCache = new WeakMap();
  var lum = function (r, g, b) { return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255; };
  var imgLight = function (im) {
    if (imgCache.has(im)) return imgCache.get(im);
    if (!im.complete || !im.naturalWidth) return false;
    var v = false;
    try {
      var c = document.createElement('canvas'); c.width = c.height = 8;
      var x = c.getContext('2d'); x.drawImage(im, 0, 0, 8, 8);
      var d = x.getImageData(0, 0, 8, 8).data, s = 0;
      for (var i = 0; i < d.length; i += 4) s += lum(d[i], d[i + 1], d[i + 2]);
      v = s / 64 > 0.62;
    } catch (_) { v = false; }
    imgCache.set(im, v);
    return v;
  };
  var isLight = function (el) {
    for (var n = el, k = 0; n && n.nodeType === 1 && k < 14; n = n.parentElement, k++) {
      var m = n.getAttribute('data-cursor');
      if (m === 'light') return true;
      if (m === 'dark') return false;
      if (n.classList.contains('btn')) return false;
      if (n.tagName === 'IMG') return imgLight(n);
      var p = getComputedStyle(n).backgroundColor.match(/[\d.]+/g);
      if (p && (p.length < 4 || +p[3] > 0.5)) return lum(+p[0], +p[1], +p[2]) > 0.62;
    }
    return false;
  };
  var docLabel = function (t) {
    var a = t.closest('a[href]');
    if (!a || a.classList.contains('btn')) return '';
    if (a.hasAttribute('download') || /\.pdf($|[?#])/i.test(a.getAttribute('href'))) return 'Скачать PDF';
    return a.querySelector('img') ? 'Открыть' : '';
  };
  addEventListener('pointermove', function (e) {
    var t = e.target;
    if (!t.closest) return;
    /* курсор app.min.js на каждом движении ставит link только для a, button, select, label — точкам плана добавляем после него */
    hot = !!t.closest('[role=button]');
    if (hot) requestAnimationFrame(function () { if (hot) cur.classList.add('link'); });
    if (t === lastT) return;
    lastT = t;
    var l = lightCache.has(t) ? lightCache.get(t) : isLight(t);
    if (t.tagName !== 'IMG' || imgCache.has(t)) lightCache.set(t, l);
    var d = l ? docLabel(t) : '';
    cur.classList.toggle('light', l);
    cur.classList.toggle('doc', !!d);
    if (d) lbl.textContent = d;
  }, { passive: true });
  addEventListener('scroll', function () { lastT = null; }, { passive: true });
  document.addEventListener('pointerleave', function () { lastT = null; });
})();
