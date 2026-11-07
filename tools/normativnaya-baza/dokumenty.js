/* «Документы для Роспотребнадзора»: сборщик папки по типу объекта, поиск по перечню, цели Метрики.
   Данные берутся из таблиц страницы (строки tr[id^="d-"] с data-obj и data-who, таблица «По типам объектов»),
   поэтому перечень правится в одном месте — tools/normativnaya-baza/dokumenty_data.py. __ROOT__ и __V__ подставляет сборка. */
(function () {
  'use strict';
  var d = document, ROOT = '__ROOT__', V = '__V__';
  var tool = d.querySelector('[data-dk-tool]');
  if (!tool) return;
  var rows = [].slice.call(d.querySelectorAll('.dk-tbl tbody tr[id^="d-"]'));
  var groups = [].slice.call(d.querySelectorAll('.dk-g'));
  var kitBox = d.getElementById('dk-kit'), bar = d.getElementById('dk-bar'), cnt = d.getElementById('dk-count');
  var form = d.getElementById('form');
  var cur = null;

  function goal(name, params) {
    try { if (window.ym) window.ym(113675622, 'reachGoal', name, params || undefined); } catch (e) {}
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function chip(code) { return tool.querySelector('input[name="dk-obekt"][value="' + code + '"]'); }
  function label(code) { var i = chip(code); return i ? i.parentNode.textContent.replace(/\s+/g, ' ').trim() : ''; }
  function rowName(tr) { var b = tr.querySelector('.dk-doc'); return b ? b.textContent.replace(/\s+/g, ' ').trim() : ''; }
  function rowWho(tr) {
    var w = tr.querySelector('.dk-who-t') || tr.querySelector('.dk-who');
    return w ? w.textContent.replace(/\s+/g, ' ').trim() : '';
  }
  function forObj(tr, code) {
    var o = (tr.getAttribute('data-obj') || 'all').split(' ');
    return o.indexOf('all') > -1 || o.indexOf(code) > -1;
  }

  // ---------------------------------------------------------------- сборщик папки
  function render(code) {
    cur = code;
    var kit = d.getElementById('o-' + code);
    var head = '<div class="dk-kit-head"><h3>' + esc(label(code)) + '</h3>';
    if (kit) {
      var c = kit.cells;
      head += '<p><b>Проверочный лист:</b> ' + c[1].innerHTML + '</p><p>' + c[2].innerHTML + '</p>';
    }
    head += '</div>';
    var html = head, total = 0;
    groups.forEach(function (g) {
      var items = rows.filter(function (tr) { return g.contains(tr) && forObj(tr, code); });
      if (!items.length) return;
      var h = g.querySelector('.dk-g-h');
      html += '<div class="dk-kit-g"><p class="dk-kit-gh">' + h.innerHTML + '</p><ul class="dk-items">';
      items.forEach(function (tr) {
        total++;
        var my = tr.getAttribute('data-who') === 'my' ? '<span class="dk-my">готовим мы</span>' : '';
        html += '<li><label class="dk-item"><input type="checkbox" value="' + tr.id + '"><span><b>' + esc(rowName(tr)) + my +
          '</b><small>' + esc(rowWho(tr)) + ' · <a href="#' + tr.id + '">подробнее</a></small></span></label></li>';
      });
      html += '</ul></div>';
    });
    kitBox.innerHTML = html;
    bar.hidden = false;
    update();
  }
  function boxes() { return [].slice.call(kitBox.querySelectorAll('input[type=checkbox]')); }
  function update() {
    var all = boxes(), have = all.filter(function (b) { return b.checked; }).length, miss = all.length - have;
    all.forEach(function (b) { b.closest('.dk-item').classList.toggle('is-have', b.checked); });
    cnt.innerHTML = 'Есть <b>' + have + '</b> из ' + all.length + ' · не хватает <b>' + miss + '</b>';
  }
  tool.addEventListener('change', function (e) {
    var t = e.target;
    if (t.name === 'dk-obekt') {
      render(t.value);
      try { history.replaceState(null, '', location.pathname + '?obekt=' + t.value + '#papka'); } catch (_) {}
    } else if (t.type === 'checkbox') update();
  });
  d.getElementById('dk-send').addEventListener('click', function () {
    if (!cur || !form) return;
    var all = boxes(), miss = all.filter(function (b) { return !b.checked; });
    var names = miss.map(function (b) { return '— ' + rowName(d.getElementById(b.value)); });
    var e = form.elements, sel = e.type, want = label(cur), i;
    if (sel) {
      for (i = 0; i < sel.options.length; i++) if (sel.options[i].text === want) { sel.selectedIndex = i; break; }
      sel.dispatchEvent(new Event('change', { bubbles: true }));
    }
    if (e.comment) {
      e.comment.value = 'Сборщик папки: ' + want + '. Есть ' + (all.length - miss.length) + ' из ' + all.length + '.' +
        (names.length ? '\nНе хватает (' + names.length + '):\n' + names.join('\n') : '\nВсе документы из списка есть — прошу сверить.');
    }
    goal('dokumenty_spisok', { obekt: cur, net: miss.length });
    var z = d.getElementById('zayavka');
    if (z) z.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setTimeout(function () { var n = e.name; if (n) try { n.focus({ preventScroll: true }); } catch (_) { n.focus(); } }, 600);
  });

  // ---------------------------------------------------------------- переходы с параметрами: ?obekt= и ?q=
  var qs = {};
  location.search.replace(/^\?/, '').split('&').forEach(function (p) {
    var kv = p.split('=');
    if (kv[0]) { try { qs[kv[0]] = decodeURIComponent((kv[1] || '').replace(/\+/g, ' ')); } catch (_) {} }
  });
  if (qs.obekt && chip(qs.obekt)) { chip(qs.obekt).checked = true; render(qs.obekt); }
  if (qs.q && form && form.elements.comment && !form.elements.comment.value) {
    form.elements.comment.value = 'Ищу документ: ' + qs.q.slice(0, 200);
  }

  // ---------------------------------------------------------------- поиск по перечню (движок поиска сайта, грузится при первом вводе)
  var q = d.getElementById('dk-q'), qx = d.getElementById('dk-q-x'), st = d.getElementById('dk-q-st');
  var engine = null, waiting = [], loading = false, timer = 0, sent = '';
  function withEngine(cb) {
    if (engine) return cb(engine);
    waiting.push(cb);
    if (loading) return;
    loading = true;
    var s = d.createElement('script');
    s.src = ROOT + 'search.min.js?v=' + V;
    s.async = true;
    s.onload = function () { engine = window.PCSearch && window.PCSearch.engine; var w = waiting; waiting = []; w.forEach(function (f) { if (engine) f(engine); }); };
    d.head.appendChild(s);
  }
  function reset() {
    rows.forEach(function (tr) { tr.hidden = false; });
    groups.forEach(function (g) { g.hidden = false; });
    st.textContent = '';
    qx.hidden = true;
  }
  function filter() {
    var v = q.value.trim();
    qx.hidden = !v;
    if (v.length < 2) { reset(); return; }
    withEngine(function (E) {
      var P = E.parse(v);
      if (!P.groups.length) { reset(); return; }
      var n = 0;
      rows.forEach(function (tr) {
        if (!tr._t) tr._t = E.tokens(tr.textContent + ' ' + (tr.getAttribute('data-kw') || ''));
        var ok = E.matchAll(tr._t, P.groups);
        tr.hidden = !ok;
        if (ok) n++;
      });
      groups.forEach(function (g) { g.hidden = !g.querySelector('tbody tr[id^="d-"]:not([hidden])'); });
      var fixed = P.fixed ? ' Искали «' + esc(P.fixed) + '».' : '';
      st.innerHTML = n ? 'Найдено документов: ' + n + '.' + fixed
        : 'В перечне ничего не нашлось.' + fixed + ' <a href="#zayavka" data-dk-ask>Спросите санитарного врача</a> — подскажем, какой документ нужен.';
      clearTimeout(timer);
      timer = setTimeout(function () {
        if (sent === v) return;
        sent = v;
        goal(n ? 'poisk' : 'poisk_net', { query: v.slice(0, 100), count: n, place: 'perechen' });
      }, 1500);
    });
  }
  q.addEventListener('input', filter);
  q.addEventListener('focus', function () { withEngine(function () {}); }, { once: true });
  q.addEventListener('keydown', function (e) { if (e.key === 'Escape') { q.value = ''; filter(); } });
  qx.addEventListener('click', function () { q.value = ''; filter(); q.focus(); });
  st.addEventListener('click', function (e) {
    if (!e.target.closest('[data-dk-ask]') || !form || !form.elements.comment) return;
    if (!form.elements.comment.value) form.elements.comment.value = 'Ищу документ: ' + q.value.trim().slice(0, 200);
  });

  // переход к строке перечня по ссылке (#d-…), например из поиска по сайту: строка ненадолго подсвечивается
  var hl = location.hash && /^#d-[a-z0-9-]+$/.test(location.hash) && d.getElementById(location.hash.slice(1));
  if (hl) { hl.classList.add('dk-hl'); setTimeout(function () { hl.classList.remove('dk-hl'); }, 2400); }

  // ---------------------------------------------------------------- скачивания: чек-лист, образец и бланк акта
  d.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('[data-goal]');
    if (a) goal(a.getAttribute('data-goal'));
  });
})();
