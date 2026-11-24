/* Санитарный навигатор: поведение страниц раздела. Без зависимостей. */
(function () {
  'use strict';
  var d = document;
  function $(s, r) { return (r || d).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); }
  function norm(s) { return String(s).toLowerCase().replace(/ё/g, 'е'); }
  function pl(n, f) { var a = Math.abs(n) % 100, b = a % 10; return a > 10 && a < 20 ? f[2] : b > 1 && b < 5 ? f[1] : b === 1 ? f[0] : f[2]; }
  function nq(n) { return n + '\u00a0' + pl(n, ['вопрос', 'вопроса', 'вопросов']); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function param(k) { var m = new RegExp('[?&]' + k + '=([^&#]*)').exec(location.search); if (!m) return ''; try { return decodeURIComponent(m[1].replace(/\+/g, ' ')); } catch (e) { return m[1]; } }
  var root = $('[data-nv]'), kind = root ? root.getAttribute('data-nv') : '';

  /* сообщение внизу экрана */
  var toastEl, toastT;
  function toast(t) {
    if (!toastEl) { toastEl = d.createElement('div'); toastEl.className = 'nv-toast'; toastEl.setAttribute('role', 'status'); toastEl.setAttribute('aria-live', 'polite'); ($('.nv') || d.body).appendChild(toastEl); }
    toastEl.textContent = t; toastEl.classList.add('nv-on'); clearTimeout(toastT);
    toastT = setTimeout(function () { toastEl.classList.remove('nv-on'); }, Math.min(7000, 2200 + t.length * 45));
  }
  function copyText(text, okMsg) {
    function fallback() {
      var ta = d.createElement('textarea'); ta.value = text; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;left:-9999px;top:0';
      d.body.appendChild(ta); ta.select(); var ok = false; try { ok = d.execCommand('copy'); } catch (e) { } d.body.removeChild(ta);
      toast(ok ? okMsg : 'Не удалось скопировать — используйте кнопку «Скачать»');
    }
    try { if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function () { toast(okMsg); }, fallback); else fallback(); } catch (e) { fallback(); }
  }
  function download(name, text) {
    try {
      var url = URL.createObjectURL(new Blob(['\ufeff' + text], { type: 'text/plain;charset=utf-8' }));
      var a = d.createElement('a'); a.href = url; a.download = name; d.body.appendChild(a); a.click();
      setTimeout(function () { d.body.removeChild(a); URL.revokeObjectURL(url); }, 500);
      toast('Файл подготовлен: ' + name);
    } catch (e) { toast('Не удалось сохранить файл — используйте «Скопировать список»'); }
  }
  /* отметки хранятся в браузере; если хранилище недоступно — до закрытия страницы */
  var mem = {};
  function load(k) { try { return JSON.parse(localStorage.getItem(k) || '{}') || {}; } catch (e) { return mem[k] || {}; } }
  function save(k, v) { mem[k] = v; try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { } }

  /* на телефоне лента разделов прокручивается — активный раздел должен быть виден */
  var tabs = $('.nv-tabs'), curTab = tabs && $('[aria-current="page"]', tabs);
  if (curTab && tabs.scrollWidth > tabs.clientWidth) tabs.scrollLeft = Math.max(0, curTab.offsetLeft - tabs.offsetLeft - (tabs.clientWidth - curTab.offsetWidth) / 2);

  /* «Показать все»: строки уже есть в разметке, они только скрыты */
  d.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-more]'); if (!b) return;
    var sec = b.closest('section') || b.parentNode;
    $$('[data-rows] > [hidden]', sec).forEach(function (r) { r.hidden = false; });
    b.remove();
  });

  /* строка поиска: переход на страницу поиска с запросом */
  $$('form.nv-find, form.nv-top-search').forEach(function (f) {
    if (f.id === 'sFind') return;
    f.addEventListener('submit', function (e) {
      e.preventDefault(); var v = f.elements.q.value.trim(); if (!v) { f.elements.q.focus(); return; }
      location.href = f.getAttribute('action') + '?q=' + encodeURIComponent(v);
    });
  });

  /* роли на главной */
  $$('.nv-role-tab').forEach(function (b) {
    b.addEventListener('click', function () {
      $$('.nv-role-tab').forEach(function (x) { x.setAttribute('aria-selected', x === b); });
      $$('.nv-role-p').forEach(function (p) { p.hidden = p.id !== b.getAttribute('aria-controls'); });
    });
  });

  /* список объектов: быстрый поиск по названию */
  if (kind === 'objects') {
    $('#objF').addEventListener('input', function () {
      var v = norm(this.value.trim()), any = false;
      $$('.nv-grp', root).forEach(function (g) {
        var n = 0;
        $$('.nv-obj', g).forEach(function (a) { var ok = !v || norm(a.getAttribute('data-k')).indexOf(v) >= 0; a.hidden = !ok; if (ok) n++; });
        g.hidden = !n; if (n) any = true;
      });
      $('#objNone').hidden = any;
    });
  }

  /* тема: выбор объекта */
  if (kind === 'theme') {
    var tSel = $('#tObj', root);
    var tApply = function () {
      var v = tSel.value;
      $$('#tList > .nv-qsec', root).forEach(function (s) {
        var on = !v || s.getAttribute('data-f') === v; s.hidden = !on;
        if (on && v) { $$('[data-rows] > [hidden]', s).forEach(function (r) { r.hidden = false; }); var m = $('[data-more]', s); if (m) m.remove(); }
      });
    };
    tSel.addEventListener('change', tApply);
    var o0 = param('o'); if (o0 && $('option[value="' + o0 + '"]', tSel)) { tSel.value = o0; tApply(); }
  }

  /* периодичность: выбор объекта и выгрузка графика */
  if (kind === 'per') {
    var pSel = $('#pObj', root);
    var pApply = function () {
      var v = pSel.value, any = false;
      $$('.nv-bucket', root).forEach(function (b) {
        var rows = $$('[data-rows] > .nv-q', b), n = 0, more = $('[data-more]', b);
        rows.forEach(function (r, i) { var ok = !v || r.getAttribute('data-f') === v; if (ok) n++; r.hidden = !ok || (!v && !!more && n > 5); });
        if (v && more) more.hidden = true; else if (more) more.hidden = false;
        b.hidden = !n; if (n) any = true;
        var c = $('.nv-bucket-h span', b); if (c) c.textContent = nq(n);
      });
      $('#pNone').hidden = any;
    };
    pSel.addEventListener('change', pApply);
    var s0 = param('o'); if (s0) { var op = $('option[data-slug="' + s0 + '"]', pSel); if (op) { pSel.value = op.value; pApply(); } }
    $('#pCopy').addEventListener('click', function () {
      var v = pSel.value, out = ['График обязательных работ' + (v ? ': ' + pSel.options[pSel.selectedIndex].text.replace(/ — \d+$/, '') : ''), ''];
      $$('.nv-bucket', root).forEach(function (b) {
        if (b.hidden) return;
        out.push($('h2', b).textContent.toUpperCase());
        $$('[data-rows] > .nv-q', b).forEach(function (r) {
          if (v && r.getAttribute('data-f') !== v) return;
          var per = $('.nv-per', r), obj = $('.nv-tag-l', r), cite = $('.nv-cite', r);
          out.push('— ' + (per ? per.textContent + ': ' : '') + $('.nv-q-t', r).textContent.replace(/^\s*[\d.]+\s*/, '') + (v || !obj ? '' : ' [' + obj.textContent + ']') + (cite ? ' (' + cite.textContent + ')' : ''));
        });
        out.push('');
      });
      copyText(out.join('\n'), 'График скопирован');
    });
  }

  /* реестр документов: поиск, вид, статус */
  if (kind === 'docs') {
    var rows = $$('#dList > a', root).map(function (a) { return { el: a, st: a.getAttribute('data-st'), g: a.getAttribute('data-g'), s: norm($('.nv-doc-s', a).textContent), h: norm(a.textContent + ' ' + (a.getAttribute('data-x') || '')) }; });
    var st = { q: param('q'), st: 'all', g: 'all' }, list = $('#dList');
    var dDraw = function () {
      var toks = norm(st.q).replace(/[«»"“”(),;:!?№]/g, ' ').split(/\s+/).filter(function (w) { return w && w !== 'п' && w !== 'ст'; });
      var cnt = {}, shown = 0, exact = [];
      rows.forEach(function (r) {
        var base = (st.g === 'all' || r.g === st.g) && toks.every(function (t) { return r.h.indexOf(t) >= 0; });
        if (base) { cnt.all = (cnt.all || 0) + 1; cnt[r.st] = (cnt[r.st] || 0) + 1; }
        var on = base && (st.st === 'all' || r.st === st.st); r.el.hidden = !on; if (on) { shown++; if (toks.length && toks.every(function (t) { return r.s.indexOf(t) >= 0; })) exact.push(r.el); }
      });
      exact.reverse().forEach(function (el) { list.insertBefore(el, list.firstChild); });      // совпадение с самим обозначением — выше
      $$('#dSt .nv-chip', root).forEach(function (b) { b.querySelector('b').textContent = cnt[b.getAttribute('data-st')] || 0; b.setAttribute('aria-pressed', b.getAttribute('data-st') === st.st); });
      $('#dNone').hidden = !!shown;
    };
    var tm; $('#dF').value = st.q;
    $('#dF').addEventListener('input', function () { var v = this.value; clearTimeout(tm); tm = setTimeout(function () { st.q = v; dDraw(); }, 140); });
    $('#dG').addEventListener('change', function () { st.g = this.value; dDraw(); });
    $('#dSt').addEventListener('click', function (e) { var b = e.target.closest('[data-st]'); if (b) { st.st = b.getAttribute('data-st'); dDraw(); } });
    if (st.q) dDraw();
  }

  /* объект: отметки, группировка, отбор, выгрузка */
  if (kind === 'object') {
    var DATA = JSON.parse($('#nv-data').textContent), KEY = 'nv:chk:' + DATA.fid;
    var qlist = $('#qlist'), all = $$('.nv-q', qlist).sort(function (a, b) { return a.getAttribute('data-i') - b.getAttribute('data-i'); });
    var chk = load(KEY), S = { mode: 'theme', only: false, text: '', doc: null };
    var dp = param('doc'); if (dp && DATA.docs[dp]) S.doc = dp;
    all.forEach(function (r) { var i = r.getAttribute('data-i'); if (chk[i]) { r.classList.add('nv-done'); $('input', r).checked = true; } });
    var keyOf = function (r) { return +r.getAttribute(S.mode === 'theme' ? 'data-t' : S.mode === 'sec' ? 'data-s' : 'data-p'); };
    var nameOf = function (k) { return S.mode === 'theme' ? DATA.themes[k] : S.mode === 'sec' ? (DATA.secs[k] || 'Вопросы листа') : DATA.buckets[k]; };
    var visible = function (r, skipDone) {
      var i = r.getAttribute('data-i');
      if ((S.only || skipDone) && chk[i]) return false;
      if (S.doc != null && (' ' + (r.getAttribute('data-d') || '') + ' ').indexOf(' ' + S.doc + ' ') < 0) return false;
      if (S.mode === 'per' && +r.getAttribute('data-p') < 0) return false;
      if (S.text && norm(r.textContent).indexOf(S.text) < 0) return false;
      return true;
    };
    var groups = function (skipDone) {
      var gs = [], map = {};
      all.forEach(function (r) { if (!visible(r, skipDone)) return; var k = keyOf(r); if (!(k in map)) { map[k] = { key: k, items: [] }; gs.push(map[k]); } map[k].items.push(r); });
      if (S.mode !== 'sec') gs.sort(function (a, b) { return a.key - b.key; });
      return gs;
    };
    var prog = function () {
      var n = 0; for (var k in chk) if (chk[k]) n++;
      $('#prT').textContent = 'Отмечено ' + n + ' из ' + all.length; $('#prB').style.width = (100 * n / all.length) + '%'; $('#resetBtn').hidden = !n;
    };
    var draw = function () {
      var gs = groups(), frag = d.createDocumentFragment(), jump = '';
      gs.forEach(function (g, gi) {
        var sec = d.createElement('section'); sec.className = 'nv-qsec'; sec.id = 'g' + gi;
        sec.innerHTML = '<div class="nv-qsec-h"><h2>' + esc(nameOf(g.key)) + '</h2><span>' + nq(g.items.length) + '</span></div>';
        g.items.forEach(function (r) { sec.appendChild(r); }); frag.appendChild(sec);
        jump += '<a href="#g' + gi + '"><span>' + esc(nameOf(g.key)) + '</span><i>' + g.items.length + '</i></a>';
      });
      qlist.textContent = '';
      if (gs.length) qlist.appendChild(frag); else qlist.innerHTML = '<p class="nv-empty">По этим условиям вопросов нет. Измените фильтр.</p>';
      $('#jump').innerHTML = jump; $('#jumpP').hidden = !gs.length;
      root.setAttribute('data-mode', S.mode);
      $$('.nv-seg button', root).forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-mode') === S.mode); });
      var note = $('#docNote');
      if (S.doc != null) { note.hidden = false; note.innerHTML = 'Показаны только вопросы со ссылкой на ' + esc(DATA.docs[S.doc]) + '. <a class="nv-link" href="' + location.pathname + '">Показать все вопросы</a>'; } else note.hidden = true;
      prog();
    };
    var qtext = function (r) { return $('.nv-q-t', r).textContent.replace(/^\s*([\d.]+)\.\s*/, '$1. '); };
    var asText = function () {
      var done = [], n = 0;
      all.forEach(function (r) { if (chk[r.getAttribute('data-i')]) done.push($('.nv-n', r).textContent.replace(/\.$/, '')); });
      var out = [DATA.name + ' — вопросы проверочного листа', 'Приказ Роспотребнадзора № ' + DATA.order + ', приложение № ' + DATA.app + '. ' + DATA.url];
      if (S.doc != null) out.push('Отбор: только вопросы со ссылкой на ' + DATA.docs[S.doc] + '.');
      if (S.mode === 'per') out.push('Отбор: только требования с периодичностью.');
      if (S.text) out.push('Отбор по слову: «' + S.text + '».');
      var body = [];
      groups(true).forEach(function (g) {
        body.push(nameOf(g.key).toUpperCase());
        g.items.forEach(function (r) {
          n++; body.push(qtext(r));
          var c = $('.nv-cite', r), p = $('.nv-per', r);
          body.push('   Основание: ' + (c ? c.textContent : 'в листе не указано'));
          if (p) body.push('   Периодичность: ' + p.textContent);
        });
        body.push('');
      });
      if (done.length) out.push('Без отметки: ' + n + '. Отмечено как выполненное: ' + done.length + ' из ' + all.length + '.');
      out.push(''); out = out.concat(n ? body : ['В этом списке не осталось вопросов без отметки.', '']);
      if (done.length) out.push('Отмечены как выполненные: № ' + done.join(', ') + '.');
      out.push('Санитарный навигатор. Сверка статусов документов: ' + DATA.checked + '. ' + location.href.split('?')[0].split('#')[0]);
      return { text: out.join('\n'), n: n, done: done.length };
    };
    $$('.nv-seg button', root).forEach(function (b) { b.addEventListener('click', function () { S.mode = b.getAttribute('data-mode'); draw(); }); });
    var tq; $('#qF').addEventListener('input', function () { var v = this.value; clearTimeout(tq); tq = setTimeout(function () { S.text = norm(v.trim()); draw(); }, 140); });
    $('#onlyBtn').addEventListener('click', function () { S.only = !S.only; this.setAttribute('aria-pressed', S.only); draw(); });
    $('#resetBtn').addEventListener('click', function () { chk = {}; save(KEY, chk); all.forEach(function (r) { r.classList.remove('nv-done'); $('input', r).checked = false; }); draw(); });
    $('#copyBtn').addEventListener('click', function () { var x = asText(); copyText(x.text, 'Скопировано: ' + nq(x.n) + (x.done ? ' без отметки' : '')); });
    $('#dlBtn').addEventListener('click', function () { var x = asText(); download(DATA.name.replace(/[^\wа-яё]+/gi, '_') + '_вопросы_проверки.txt', x.text); });
    qlist.addEventListener('change', function (e) {
      var r = e.target.closest('.nv-q'); if (!r) return;
      var i = r.getAttribute('data-i'); if (e.target.checked) chk[i] = 1; else delete chk[i];
      save(KEY, chk); r.classList.toggle('nv-done', e.target.checked); prog();
      if (S.only && e.target.checked) draw();
    });
    if (S.doc != null) draw(); else prog();
  }
})();
