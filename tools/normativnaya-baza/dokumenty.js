/* «Документы для Роспотребнадзора»: конструктор «Соберите папку», вкладки «По видам объектов», цели Метрики.
   Данные — <script id="dk-data"> (из data/dokumenty.json). Отметки — только в localStorage браузера (ключ pkc-dokumenty-v1). */
(function () {
  var el = document.getElementById('dk-data');
  if (!el) return;
  var D;
  try { D = JSON.parse(el.textContent); } catch (e) { return; }
  var KEY = 'pkc-dokumenty-v1', LABEL = { y: 'Есть', n: 'Нет', x: 'Не нужно' };
  // вид объекта в форме: текст пункта списка (значение для send.php подставляет сама форма)
  var FORM_TYPE = { pp: 'Пищевое производство', ob: 'Ресторан, кафе, столовая', tr: 'Магазин, торговая сеть', sk: 'Склад пищевой продукции',
    fa: 'Фармацевтическое производство', go: 'Гостиница, хостел', us: 'Салон красоты, бытовые услуги', dr: 'Другой объект' };
  var NAME = {}, SLUG = {};
  D.o.forEach(function (o) { NAME[o[0]] = o[1]; SLUG[o[2]] = o[0]; });
  var st = { o: [], m: {} };
  try { var s0 = JSON.parse(localStorage.getItem(KEY) || 'null'); if (s0 && s0.o && s0.m) st = s0; } catch (e) {}
  var q = /[?&]obekt=([a-z-]+)/.exec(location.search);
  if (q && SLUG[q[1]]) st.o = [SLUG[q[1]]];
  st.o = st.o.filter(function (c) { return NAME[c]; });

  function save() { try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {} }
  function goal(id) { try { if (typeof ym === 'function') ym(113675622, 'reachGoal', id); } catch (e) {} }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  // пункт: [номер, название, кто готовит, группа, объекты (0 — все), условие (1 — для всех, {код: текст} — для части), делаем мы]
  function applies(it) {
    if (!st.o.length) return [];
    return it[4] === 0 ? st.o.slice() : st.o.filter(function (c) { return it[4].indexOf(c) >= 0; });
  }
  function optional(it, codes) {
    if (it[5] === 1) return true;
    if (it[5] && typeof it[5] === 'object') return codes.every(function (c) { return it[5][c]; });
    return false;
  }
  function current() {
    var out = [];
    D.i.forEach(function (it) { var c = applies(it); if (c.length) out.push({ it: it, opt: optional(it, c) }); });
    return out;
  }

  var list = document.getElementById('dk-list'), bar = document.getElementById('dk-bar'), cnt = document.getElementById('dk-count');
  var mini = document.getElementById('dk-mini');  // телефон: счётчик внизу экрана, пока идёт список (сама панель — после списка)
  var empty = list ? list.innerHTML : '';
  var picks = [].slice.call(document.querySelectorAll('.dk-pick'));

  // высота конструктора меняется на тысячи пикселей: пересчитываем точки запуска анимаций появления (GSAP ScrollTrigger)
  var rt;
  function relayout() {
    clearTimeout(rt);
    rt = setTimeout(function () { try { if (window.ScrollTrigger) window.ScrollTrigger.refresh(); } catch (e) {} }, 350);
  }

  function render() {
    picks.forEach(function (b) { b.setAttribute('aria-pressed', st.o.indexOf(b.getAttribute('data-obj')) >= 0 ? 'true' : 'false'); });
    if (!list) return;
    var rows = current();
    relayout();
    if (!rows.length) { list.innerHTML = empty; bar.hidden = true; if (mini) mini.hidden = true; return; }
    var h = '', g = 0;
    rows.forEach(function (r) {
      var it = r.it, v = st.m[it[0]];
      if (v === 'x' && !r.opt) v = undefined;
      if (it[3] !== g) {
        if (g) h += '</div>';
        g = it[3];
        h += '<div class="dk-lg"><h3><span>' + g + '</span>' + esc(D.g[g - 1][1]) + '</h3>';
      }
      h += '<div class="dk-row' + (v ? ' is-' + v : '') + '" data-id="' + it[0] + '"><span class="dk-row-n">' + it[0] + '</span>' +
        '<span class="dk-row-t">' + esc(it[1]) + '<small>' + esc(it[2]) + (it[6] ? ' · ●' : '') + '</small></span><span class="dk-seg" role="group" aria-label="' + esc(it[1]) + '">';
      ['y', 'n'].concat(r.opt ? ['x'] : []).forEach(function (k) {
        h += '<button type="button" data-v="' + k + '" aria-pressed="' + (v === k ? 'true' : 'false') + '">' + LABEL[k] + '</button>';
      });
      h += '</span></div>';
    });
    list.innerHTML = h + '</div>';
    bar.hidden = false;
    if (mini) mini.hidden = false;
    count(rows);
  }
  function count(rows) {
    rows = rows || current();
    var done = 0, miss = 0;
    rows.forEach(function (r) { var v = st.m[r.it[0]]; if (v === 'x' && !r.opt) v = 0; if (v) done++; if (v === 'n') miss++; });
    cnt.innerHTML = 'Отмечено <b>' + done + '</b> из <b>' + rows.length + '</b>' + (miss ? ' · <span class="dk-miss">не хватает ' + miss + '</span>' : '');
    if (mini) mini.innerHTML = '<span class="dk-mini-t">' + cnt.innerHTML + '</span><span class="dk-mini-go" aria-hidden="true">↓</span>';
  }
  if (mini) mini.addEventListener('click', function () { bar.scrollIntoView({ block: 'center' }); });

  picks.forEach(function (b) {
    b.addEventListener('click', function () {
      var c = b.getAttribute('data-obj'), i = st.o.indexOf(c);
      if (i >= 0) st.o.splice(i, 1); else st.o.push(c);
      save(); render();
      if (st.o.length) showTab(st.o[st.o.length - 1]);
    });
  });
  if (list) list.addEventListener('click', function (e) {
    var b = e.target.closest('.dk-seg button');
    if (!b) return;
    var row = b.closest('.dk-row'), id = row.getAttribute('data-id'), v = b.getAttribute('data-v');
    if (st.m[id] === v) delete st.m[id]; else st.m[id] = v;
    save();
    [].forEach.call(row.querySelectorAll('.dk-seg button'), function (x) { x.setAttribute('aria-pressed', st.m[id] === x.getAttribute('data-v') ? 'true' : 'false'); });
    row.className = 'dk-row' + (st.m[id] ? ' is-' + st.m[id] : '');
    count();
  });

  function summary() {
    var rows = current(), no = [], left = [];
    rows.forEach(function (r) {
      var v = st.m[r.it[0]];
      if (v === 'n') no.push(r.it[0] + ' ' + r.it[1]);
      else if (!v || (v === 'x' && !r.opt)) left.push(r.it[0]);
    });
    return 'Список из конструктора «Документы для Роспотребнадзора»\nВид объекта: ' + st.o.map(function (c) { return NAME[c]; }).join(', ') +
      '\nНет (' + no.length + '): ' + (no.length ? no.join('; ') : '—') +
      (left.length ? '\nНе отмечено: ' + left.length + ' из ' + rows.length : '');
  }
  var send = document.getElementById('dk-send');
  if (send) send.addEventListener('click', function () {
    var f = document.getElementById('form');
    if (!f) return;
    var t = f.elements.type, m = f.elements.comment, want = FORM_TYPE[st.o[0]];
    if (t && want) [].forEach.call(t.options, function (o, i) { if (o.text === want) t.selectedIndex = i; });
    if (m) m.value = summary();
    goal('dokumenty_spisok');
    // к форме — тем же плавным переходом, что и ссылки «#zayavka» на странице (app.js); без него — обычный переход
    var a = document.querySelector('a[href="#zayavka"]'), z = document.getElementById('zayavka');
    if (a) a.click(); else if (z) z.scrollIntoView();
    // на компьютере курсор сразу в поле имени; на телефоне клавиатуру не открываем
    if (window.matchMedia && matchMedia('(pointer:fine)').matches) setTimeout(function () {
      var n = f.elements.name;
      if (n) try { n.focus({ preventScroll: true }); } catch (e) { n.focus(); }
    }, 1600);
  });
  var pr = document.getElementById('dk-print');
  if (pr) pr.addEventListener('click', function () {
    var rows = current(), h = '<h1>Документы для Роспотребнадзора</h1><p>Вид объекта: ' + esc(st.o.map(function (c) { return NAME[c]; }).join(', ')) +
      ' · ' + new Date().toLocaleDateString('ru-RU') + ' · пестконтроль-центр.рф</p>', g = 0;
    rows.forEach(function (r) {
      var it = r.it, v = st.m[it[0]];
      if (v === 'x' && !r.opt) v = 0;
      if (it[3] !== g) { if (g) h += '</table>'; g = it[3]; h += '<h2>' + g + '. ' + esc(D.g[g - 1][1]) + '</h2><table>'; }
      h += '<tr><td>' + it[0] + '</td><td>' + esc(it[1]) + '</td><td>' + esc(it[2]) + '</td><td>' + (v ? LABEL[v] : '☐ Есть ☐ Нет') + '</td></tr>';
    });
    var a = document.getElementById('dk-print-area') || document.body.appendChild(document.createElement('div'));
    a.id = 'dk-print-area';
    a.innerHTML = h + '</table>';
    document.body.classList.add('dk-printing');
    goal('dokumenty_spisok');
    window.print();
  });
  window.addEventListener('afterprint', function () { document.body.classList.remove('dk-printing'); });
  document.addEventListener('click', function (e) { if (e.target.closest('[data-dl="pdf"]')) goal('dokumenty_pdf'); });

  // вкладки «По видам объектов» (на телефоне — обычный аккордеон <details>)
  var tabs = [].slice.call(document.querySelectorAll('.dk-tab')), panels = [].slice.call(document.querySelectorAll('.dk-o'));
  function showTab(c) {
    if (!panels.length) return;
    tabs.forEach(function (t) { t.setAttribute('aria-selected', t.getAttribute('data-obj') === c ? 'true' : 'false'); t.tabIndex = t.getAttribute('data-obj') === c ? 0 : -1; });
    panels.forEach(function (p) { p.open = p.getAttribute('data-obj') === c; });  // на телефоне — раскрыт раздел выбранного объекта
  }
  tabs.forEach(function (t, i) {
    t.tabIndex = t.getAttribute('aria-selected') === 'true' ? 0 : -1;
    t.addEventListener('click', function () { showTab(t.getAttribute('data-obj')); });
    t.addEventListener('keydown', function (e) {
      var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!d) return;
      var n = tabs[(i + d + tabs.length) % tabs.length];
      n.focus(); showTab(n.getAttribute('data-obj'));
    });
  });

  render();
  if (st.o.length) showTab(st.o[0]);
})();
