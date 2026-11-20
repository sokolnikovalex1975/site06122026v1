/* Длинные блоки на телефоне (до 760 px) — команда владельца 20.11.2026 «Делай это на сайте» по решению «Мобильная
   версия — блоки с выбором и состав заявки» от 16.11.2026; сборка — tools/site/zayavka.py. Только внутренние страницы:
   у главной своя мобильная раскладка (tools/home-mobile, решение владельца 19.11.2026), этот скрипт на неё не ставится.

   Пять приёмов, вид — как на мобильной главной (лента со счётчиком «1 / 6», точками и стрелками; подвал разделами):
     1. лента со свайпом — карточки-анонсы, где порядок чтения не важен (связанные услуги, отрасли, вредители, образцы);
     2. раскрывающиеся пункты, первый открыт — термины, вопросы проверочных листов, разделы документов;
     3. «Показать ещё» после первых трёх пунктов — длинные шаги и списки;
     4. таблицы: короткие значения (цены, сроки) — компактной таблицей; длинные справочники — строки раскрываются по
        названию, первая открыта;
     5. подвал: разделы ссылок раскрываются по нажатию, контакты всегда открыты.
   Тексты не удаляются и не переписываются — всё остаётся в разметке страницы (для поисковиков и ИИ-ответов) и
   скрывается только визуально до нажатия. Блоки «Коротко» (#korotko), самопроверка и формы не меняются.
   Компьютер и планшет шире 760 px — без изменений: скрипт ничего не делает. */
(function () {
  'use strict';
  var mq = window.matchMedia && matchMedia('(max-width:760px)');
  if (!mq || !mq.matches) return;
  var d = document;
  var $ = function (s, r) { return (r || d).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); };
  var txt = function (el) { return el ? el.textContent.replace(/[\s\u00a0]+/g, ' ').trim() : ''; };
  var SKIP = '#korotko, #samoproverka, #zayavka, form, dialog, .mm, header, .mb-lane';
  var refresh = function () { if (window.ScrollTrigger) try { ScrollTrigger.refresh(); } catch (x) { /* нет анимаций */ } };
  var vis = function (g) { return [].filter.call(g.children, function (k) { return k.offsetParent !== null && !/^(SCRIPT|STYLE|TEMPLATE)$/.test(k.tagName); }); };
  var ARR = function (p) { return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="' + p + '"/></svg>'; };
  var seq = 0;
  var tog = function (head, box, cls, first) {
    head.setAttribute('role', 'button');
    head.setAttribute('tabindex', '0');
    var set = function (o) { box.classList.toggle(cls, o); head.setAttribute('aria-expanded', o ? 'true' : 'false'); };
    set(!!first);
    var go = function (e) { if (e.target.closest && e.target.closest('a')) return; set(!box.classList.contains(cls)); refresh(); };
    head.addEventListener('click', go);
    head.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(e); } });
  };

  /* 1. Лента со свайпом */
  var LANE = ['.rel-grid', '.pr-cards', '.rk-pcs', '.pests', '.inds', '.v-inds', '.dzf-inds', '.d-objs', '.dzf-svc', '.w-cards4',
    '.md-kinds', '.rk-xs', '.ph-tasks', '.cases', '.lb-with', '.pm-links-grid', '.nb-links', '.nb-objs', '.g-quiet', '.k-facts',
    '.md-facts', '.nb-five', '.dk-we', '.k-errs', '.sa-when', '.tasks'];
  var SMALL = /(^|\s)(rel-grid|nb-links|nb-objs|pm-links-grid)(\s|$)/;
  $$(LANE.join(',')).forEach(function (g) {
    if (g.closest(SKIP)) return;
    var kids = vis(g);
    if (kids.length < 3) return;
    g.classList.add('mb-lane');
    if (SMALL.test(g.className)) g.classList.add('mb-lane-s');
    g.setAttribute('tabindex', '-1');
    var n = kids.length, nav = d.createElement('div');
    nav.className = 'mb-nav';
    nav.innerHTML = '<span class="mb-count" aria-live="polite"><b>1</b> / ' + n + '</span>' +
      (n <= 8 ? '<span class="mb-dots" aria-hidden="true">' + kids.map(function (_, i) { return '<i' + (i ? '' : ' class="on"') + '></i>'; }).join('') + '</span>' : '') +
      '<span class="mb-arr"><button type="button" aria-label="Назад" disabled>' + ARR('M15 18l-6-6 6-6') + '</button>' +
      '<button type="button" aria-label="Дальше">' + ARR('M9 18l6-6-6-6') + '</button></span>';
    g.insertAdjacentElement('afterend', nav);
    var cur = 0, btn = $$('button', nav), dots = $$('.mb-dots i', nav), num = $('.mb-count b', nav);
    var pad = function () { return parseFloat(getComputedStyle(g).paddingLeft) || 0; };
    var go = function (i) {
      i = Math.max(0, Math.min(n - 1, i));
      g.scrollTo({ left: kids[i].getBoundingClientRect().left - g.getBoundingClientRect().left + g.scrollLeft - pad(), behavior: 'smooth' });
    };
    var upd = function () {
      var best = 0, bd = 1e9, gl = g.getBoundingClientRect().left + pad();
      kids.forEach(function (k, i) { var x = Math.abs(k.getBoundingClientRect().left - gl); if (x < bd) { bd = x; best = i; } });
      if (g.scrollLeft + g.clientWidth >= g.scrollWidth - 4) best = n - 1;
      if (best === cur) return;
      cur = best;
      num.textContent = best + 1;
      dots.forEach(function (o, i) { o.classList.toggle('on', i === best); });
      btn[0].disabled = best === 0;
      btn[1].disabled = best === n - 1;
    };
    var raf = 0;
    g.addEventListener('scroll', function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(upd); }, { passive: true });
    btn[0].addEventListener('click', function () { go(cur - 1); });
    btn[1].addEventListener('click', function () { go(cur + 1); });
    kids.forEach(function (k, i) { k.addEventListener('focusin', function () { if (i !== cur) go(i); }); });
  });

  /* 2. Раскрывающиеся пункты: у каждого пункта первым идёт заголовок */
  $$('ol.d-terms, .nb-qs, .p-secs, .p-duties, .pm-scen-grid').forEach(function (g) {
    if (g.closest(SKIP)) return;
    var kids = vis(g);
    if (kids.length < 2) return;
    g.classList.add('mb-acc');
    kids.forEach(function (k, i) {
      var h = k.firstElementChild;
      if (!h || h === k.lastElementChild) return;
      k.classList.add('mb-acc-i');
      tog(h, k, 'mb-open', i === 0);
    });
  });

  /* 3. «Показать ещё»: пошаговые списки длиннее 4 пунктов */
  $$('.d-steps, .d-cards, .p-steps, .g-steps, .p-fill-steps, .f-zlist').forEach(function (g) {
    if (g.classList.contains('mb-lane') || g.closest(SKIP + ', .mb-lane')) return;
    var kids = vis(g);
    if (kids.length < 5) return;
    kids.slice(3).forEach(function (k) { k.classList.add('mb-more-h'); });
    g.classList.add('mb-more');
    g.id = g.id || 'mb-more-' + (++seq);
    var b = d.createElement('button');
    b.type = 'button';
    b.className = 'mb-more-b';
    b.setAttribute('aria-controls', g.id);
    b.setAttribute('aria-expanded', 'false');
    b.textContent = 'Показать ещё ' + (kids.length - 3);
    g.insertAdjacentElement('afterend', b);
    b.addEventListener('click', function () { g.classList.remove('mb-more'); b.remove(); refresh(); });
  });

  /* 4. Таблицы */
  $$('table.d-table').forEach(function (t) {
    if (t.classList.contains('lb-tbl') || t.closest(SKIP + ', .lb-g, details, #ceny')) return;
    var rows = $$('tbody tr', t), heads = $$('thead th', t).length, cols = heads || (rows[0] ? rows[0].children.length : 0);
    if (cols < 2 || !rows.length) return;
    var len = function (r, c) { return r.children[c] ? txt(r.children[c]).length : 0; };
    var ok = cols <= 4, c, ls, avg, mx;
    for (c = 1; ok && c < cols; c++) {
      ls = rows.map(function (r) { return len(r, c); });
      avg = ls.reduce(function (a, b) { return a + b; }, 0) / ls.length;
      mx = Math.max.apply(null, ls);
      if (cols === 2 ? (avg > 34 || mx > 60) : (avg > 16 || mx > 24)) ok = false;
    }
    if (ok) {
      /* короткие значения (цены, сроки) — компактной таблицей; числа и сроки не переносятся */
      t.classList.add('mb-tbl');
      for (c = 1; c < cols; c++) {
        mx = Math.max.apply(null, rows.map(function (r) { return len(r, c); }));
        if (mx <= 14) rows.forEach(function (r) { if (r.children[c]) r.children[c].classList.add('mb-nw'); });
      }
      return;
    }
    /* длинный справочник: строка раскрывается, видно первое содержательное поле */
    if (heads >= 2 && rows.length >= 4 && t.getBoundingClientRect().height > 800) {
      t.classList.add('mb-tacc');
      var bare = function (cell) { var x = cell.cloneNode(true); $$('.sr-only', x).forEach(function (s) { s.parentNode.removeChild(s); }); return txt(x); };
      rows.forEach(function (r, i) {
        var cells = [].slice.call(r.children), k, head = null;
        for (k = 0; k < cells.length; k++) {
          cells[k].classList.add('mb-keep');
          if (!/^[\d.]*\s*[●•*]?$/.test(bare(cells[k]))) { cells[k].classList.add('mb-keep-l'); head = cells[k]; break; }
        }
        if (head) tog(head, r, 'mb-open', i === 0);
      });
    }
  });
  var rk = $('.rk-ptbl');
  if (rk) rk.classList.add('mb-tbl');

  /* 5. Подвал: разделы со ссылками раскрываются по нажатию; контакты всегда открыты (как на мобильной главной) */
  $$('footer .ft>div').forEach(function (col, n) {
    var h = $('h4', col), ul = $('ul', col);
    if (!h || !ul || /Контакт/.test(h.textContent)) return;
    ul.id = ul.id || 'mb-ft-' + n;
    col.classList.add('mb-fa');
    var b = d.createElement('button');
    b.type = 'button';
    b.className = 'mb-fa-b';
    b.setAttribute('aria-expanded', 'false');
    b.setAttribute('aria-controls', ul.id);
    b.textContent = h.textContent;
    h.textContent = '';
    h.appendChild(b);
    b.addEventListener('click', function () {
      var o = col.classList.toggle('open');
      b.setAttribute('aria-expanded', o ? 'true' : 'false');
      refresh();
    });
  });
  var ft = $('footer .ft');
  if (ft && $('.mb-fa', ft)) ft.classList.add('mb-ft');
  d.documentElement.classList.add('mb-on');
  refresh();
})();
