/* «Состав заявки» — всё, что посетитель выбрал в блоках сайта, уходит менеджеру вместе с заявкой
   (команда владельца 20.11.2026 «Делай это на сайте» по решению «Мобильная версия — блоки с выбором и состав заявки»
   от 16.11.2026; сборка — tools/site/zayavka.py).

   * Блоки с выбором добавляют свой пункт: отметки самопроверки, папка документов со списком «Нет», лабораторный
     расчёт, расчёт по площади, схема объекта на главной. Хранение — sessionStorage «pc-zayavka-v1» (до закрытия
     вкладки, общий для всех страниц визита; в cookies и на сторонние сайты не передаётся).
   * Состав виден над полями основной формы («В заявку уже добавлено») и в шторке заявки; любой пункт убирается
     крестиком. При отправке основной формы текст состава дописывается в поле msg (событие formdata — app.js и тексты
     страниц не меняются), после ответа сервера состав очищается.
   * Телефон (до 760 px): кнопки блоков с выбором и нижняя кнопка открывают шторку заявки снизу — без затемнения
     страницы (ЗАКОН ВЛАДЕЛЬЦА 17.11.2026); нижняя кнопка — «Заявка N», когда в составе есть пункты. Шторка отправляет
     тот же /send.php (name, phone, type, msg); цель Метрики «audit» и заявка UIS — только после ответа сервера.
   * Компьютер: вид блоков и кнопок прежний, выбор записывается в состав и виден в форме.
   Без скрипта и в старом браузере всё работает как раньше: кнопки ведут к форме внизу страницы. */
(function () {
  'use strict';
  var d = document, w = window, html = d.documentElement;
  var K = 'pc-zayavka-v1';
  var $ = function (s, r) { return (r || d).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); };
  var norm = function (s) { return String(s || '').replace(/[\s\u00a0]+/g, ' ').trim(); };
  var txt = function (el) { return el ? norm(el.textContent) : ''; };
  var esc = function (s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); };
  var mq = w.matchMedia ? w.matchMedia('(max-width: 760px)') : null;
  var MOB = function () { return !!(mq && mq.matches); };
  var fine = w.matchMedia && w.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var DEMO = /\.github\.io$/i.test(location.hostname); /* превью на GitHub Pages: заявки никуда не уходят */
  var PROD = /^(www\.)?xn----itbbsflddbfpfdodg9d0f\.xn--p1ai$/i.test(location.hostname);
  var path = location.pathname;
  var pageUrl = (PROD ? 'https://пестконтроль-центр.рф' : location.origin) + path;
  var PAGE = { n: txt($('h1')).replace(/\s*[.:]$/, '').slice(0, 120), p: path };
  var goal = function (g, p) { try { if (typeof w.ym === 'function') w.ym(113675622, 'reachGoal', g, p); } catch (x) { console.error('Яндекс Метрика:', x); } };

  /* ---------- хранилище ---------- */
  var st = { e: {} };
  try { st = JSON.parse(sessionStorage.getItem(K)) || st; } catch (x) { /* нет доступа к хранилищу */ }
  if (!st || typeof st.e !== 'object' || !st.e) st = { e: {} };
  var hooks = {}, subs = [];
  var save = function () {
    try { sessionStorage.setItem(K, JSON.stringify(st)); } catch (x) { /* приватный режим */ }
    subs.forEach(function (f) { try { f(); } catch (x) { console.error(x); } });
  };
  var list = function (except) {
    except = except || [];
    return Object.keys(st.e).filter(function (k) { return except.indexOf(k) < 0; })
      .map(function (k) { return [k, st.e[k]]; }).sort(function (a, b) { return (a[1].ts || 0) - (b[1].ts || 0); });
  };
  var put = function (key, e, quiet) {
    var old = st.e[key];
    e.ts = old && old.ts ? old.ts : Date.now();
    e.page = e.page || PAGE;
    st.e[key] = e;
    save();
    if (!old && !quiet) toast('Добавлено в заявку');
  };
  var del = function (key) {
    if (!st.e[key]) return;
    delete st.e[key];
    save();
    if (hooks[key]) { try { hooks[key](); } catch (x) { console.error(x); } }
  };
  var clear = function () { st.e = {}; save(); };

  /* текст для менеджера: поле msg (send.php — до 3 000 знаков вместе с текстом страницы) и message в UIS */
  var text = function (limit, except) {
    var es = list(except);
    if (!es.length) return '';
    limit = Math.max(200, limit || 2400);
    var per = Math.floor((limit - 30) / es.length);
    var out = 'Состав заявки (' + es.length + '):';
    es.forEach(function (x, i) {
      var e = x[1], ls = e.l || [], part = '\n' + (i + 1) + ') ' + e.t + (e.s ? ' — ' + e.s : ''), k;
      if (e.page && e.page.p !== path) part += '\n   (страница: ' + e.page.n + ', ' + e.page.p + ')';
      for (k = 0; k < ls.length; k++) {
        var line = '\n   ' + (ls[k].p ? ls[k].p + ': ' : '') + ls[k].t;
        if ((part + line).length > per - 16) { part += '\n   и ещё ' + (ls.length - k); break; }
        part += line;
      }
      out += part.slice(0, per);
    });
    return out.slice(0, limit);
  };

  /* ---------- значки и список состава ---------- */
  var SV = function (p) { return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + p + '</svg>'; };
  var ICO = {
    chk: SV('<path d="m5 12 4.5 4.5L19 7"/>'),
    lab: SV('<path d="M9 3h6M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2.2h12.4a1.5 1.5 0 0 0 1.3-2.2L14 9V3"/>'),
    doc: SV('<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>'),
    area: SV('<path d="M4 20V4h16v16z"/><path d="M4 9h5M15 4v5M4 15h4M12 20v-4"/>'),
    map: SV('<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>')
  };
  var X = SV('<path d="M6 6l12 12M18 6 6 18"/>');
  var itemsHtml = function (max, except) {
    return list(except).map(function (x) {
      var k = x[0], e = x[1], ls = e.l || [], more = ls.length > max ? ls.length - max : 0;
      return '<li class="zv-e" data-k="' + esc(k) + '"><p class="zv-e-t"><i>' + (ICO[e.ico] || ICO.chk) + '</i><span>' + esc(e.t) + '</span></p>' +
        (e.s ? '<p class="zv-e-s">' + esc(e.s) + '</p>' : '') +
        (ls.length ? '<ul class="zv-e-l">' + ls.slice(0, max).map(function (l) {
          return '<li class="' + esc(l.c || '') + '">' + (l.p ? esc(l.p) + ': ' : '') + esc(l.t) + '</li>';
        }).join('') + (more ? '<li class="zv-more">и ещё ' + more + '</li>' : '') + '</ul>' : '') +
        (e.page && e.page.p !== path ? '<p class="zv-e-p">Со страницы «' + esc(e.page.n) + '»</p>' : '') +
        '<button type="button" class="zv-e-x" aria-label="Убрать из заявки: ' + esc(e.t) + '">' + X + '</button></li>';
    }).join('');
  };
  d.addEventListener('click', function (ev) {
    var b = ev.target && ev.target.closest ? ev.target.closest('.zv-e-x') : null;
    if (!b) return;
    ev.preventDefault();
    var li = b.closest('.zv-e');
    if (li) del(li.getAttribute('data-k'));
  });

  /* подсказка «Добавлено в заявку» (телефон) */
  var toastEl = null, toastT = 0;
  var toast = function (t) {
    if (!MOB()) return;
    if (!toastEl) {
      toastEl = d.createElement('div');
      toastEl.className = 'zv-toast';
      toastEl.setAttribute('role', 'status');
      d.body.appendChild(toastEl);
    }
    toastEl.textContent = t;
    toastEl.classList.add('on');
    clearTimeout(toastT);
    toastT = setTimeout(function () { toastEl.classList.remove('on'); }, 2400);
  };

  w.PCZ = { put: put, del: del, clear: clear, list: list, text: text, html: itemsHtml, on: function (f) { subs.push(f); }, open: function () { return openSheet.apply(null, arguments); } };

  var mainForm = d.getElementById('form'), mainType = mainForm ? mainForm.elements.type : null;

  /* ---------- основная форма: состав над полями и в комментарии заявки ---------- */
  var fbox = null;
  /* блоки, которые страница сама пишет в комментарий: лабораторный расчёт (скрипт прайса), список конструктора
     документов (кнопка «Отправить список» заполняет комментарий) — второй раз не добавляем */
  var selfKeys = function () {
    var out = [];
    if (w.LB) out.push('lab');
    var c = mainForm && mainForm.elements.comment;
    if (c && /\nНет \(\d+\):/.test('\n' + c.value)) out.push('dok');
    return out;
  };
  if (mainForm) {
    fbox = d.createElement('div');
    fbox.className = 'zv-f';
    fbox.hidden = true;
    fbox.innerHTML = '<p class="zv-lbl">В заявку уже добавлено</p><ul class="zv-sost"></ul><p class="zv-f-n">Менеджер увидит это вместе с вашими контактами</p>';
    var fa = $('.fs', mainForm) || $('h3', mainForm);
    if (fa) fa.insertAdjacentElement('afterend', fbox); else mainForm.insertBefore(fbox, mainForm.firstChild);
    mainForm.addEventListener('formdata', function (e) {
      if (!list().length) return;
      var fd = e.formData, cur = String(fd.get('msg') || ''), room = 2900 - cur.length - 1;
      var add = room > 160 ? text(room, selfKeys()) : '';
      if (add) fd.set('msg', (cur ? cur + '\n' : '') + add);
    });
    /* после ответа сервера app.js ставит форме класс sent — заявка ушла, состав больше не нужен */
    if (w.MutationObserver) {
      new MutationObserver(function () { if (mainForm.classList.contains('sent') && list().length) clear(); })
        .observe(mainForm, { attributes: true, attributeFilter: ['class'] });
    }
  }
  var renderForm = function () {
    if (!fbox) return;
    var n = list().length;
    fbox.hidden = !n;
    $('ul', fbox).innerHTML = n ? itemsHtml(2) : '';
  };

  /* ---------- шторка заявки (телефон) ---------- */
  var probe = d.createElement('dialog'), canDlg = typeof probe.showModal === 'function';
  var dlg = null, sForm = null, sending = false, opener = null, ctxName = '';
  var TITLES = {
    lab: ['Оформим лабораторный расчёт', 'Перезвоним в рабочее время, уточним объект и сроки и пришлём точную смету.'],
    dok: ['Поможем собрать папку документов', 'Перезвоним в рабочее время: подскажем, чего не хватает, и согласуем бесплатный выезд.'],
    area: ['Точная цена после осмотра', 'Перезвоним в рабочее время, уточним площадь и согласуем бесплатный выезд.'],
    shema: ['Схема точек для вашего объекта', 'Перезвоним в рабочее время и согласуем бесплатный выезд: специалист осмотрит объект и составит схему.'],
    def: ['Бесплатное обследование объекта', 'Перезвоним в рабочее время и согласуем день выезда в Москве или области.']
  };
  var build = function () {
    dlg = d.createElement('dialog');
    dlg.className = 'chk-dlg zv-dlg';
    dlg.id = 'zv-dlg';
    dlg.setAttribute('aria-labelledby', 'zv-t');
    dlg.setAttribute('data-lenis-prevent', '');
    dlg.innerHTML =
      '<form class="chk-box" id="zv-form" novalidate tabindex="-1">' +
        '<button type="button" class="chk-x" data-zv-close aria-label="Закрыть форму">' + X + '</button>' +
        '<div class="chk-body">' +
          '<p class="chk-kicker">Ваша заявка</p>' +
          '<div class="zv-sw"><ul class="zv-sost" id="zv-list"></ul></div>' +
          '<h3 id="zv-t"></h3>' +
          '<p class="chk-lead" id="zv-lead"></p>' +
          '<div class="chk-fg">' +
            '<div class="field"><label class="sr-only" for="zv-name">Ваше имя</label><input id="zv-name" name="name" placeholder="Ваше имя *" required autocomplete="name" maxlength="150"><small class="ferr">Укажите имя</small></div>' +
            '<div class="field"><label class="sr-only" for="zv-phone">Телефон</label><input id="zv-phone" name="phone" type="tel" inputmode="tel" placeholder="+7 (___) ___-__-__ *" required autocomplete="tel"><small class="ferr">Укажите телефон полностью</small></div>' +
            '<div class="field"><label class="sr-only" for="zv-type">Тип объекта</label><select id="zv-type" name="type" required><option value="" disabled selected>Тип объекта *</option><option>Другое</option></select><small class="ferr">Выберите тип объекта</small></div>' +
          '</div>' +
          '<input type="hidden" name="msg" value="">' +
          '<button type="submit" class="btn btn-w btn-lg chk-send" id="zv-send"><span class="btn-t">Отправить заявку</span><i class="spin" aria-hidden="true"></i></button>' +
          '<p class="chk-err" id="zv-err" role="alert" hidden><span id="zv-err-t">Не удалось отправить заявку.</span> Попробуйте ещё раз или позвоните: <a href="tel:+74951043570">+7 (495) 104-35-70</a></p>' +
        '</div>' +
        '<div class="chk-ok" role="status" aria-live="polite" hidden>' +
          '<svg class="ok-ic" viewBox="0 0 52 52" aria-hidden="true"><circle cx="26" cy="26" r="24" fill="none"/><path fill="none" d="M15 27l7 7 15-16"/></svg>' +
          '<h3>Заявка отправлена</h3>' +
          '<p>Перезвоним в ближайшее рабочее время, чтобы согласовать день выезда. Всё, что вы выбрали, уже в заявке.</p>' +
          '<button type="button" class="btn btn-o chk-back" data-zv-close><span class="btn-t">Вернуться к странице</span></button>' +
        '</div>' +
      '</form>';
    var legal = mainForm && $('.legal', mainForm);
    if (legal) $('#zv-send', dlg).insertAdjacentElement('afterend', legal.cloneNode(true));
    ($('main') || d.body).insertAdjacentElement('afterend', dlg);
    sForm = $('#zv-form', dlg);
    var type = $('#zv-type', dlg), ph = $('#zv-phone', dlg);
    if (mainType && mainType.tagName === 'SELECT') { type.innerHTML = mainType.innerHTML; type.value = mainType.value; }
    /* телефон: та же маска, что в основной форме */
    ph.addEventListener('focus', function () { if (!ph.value) ph.value = '+7 ('; });
    ph.addEventListener('blur', function () { if (ph.value.replace(/\D/g, '').length <= 1) ph.value = ''; });
    ph.addEventListener('input', function () {
      var v = ph.value.replace(/\D/g, '');
      if (v[0] === '8') v = '7' + v.slice(1);
      if (v[0] !== '7') v = '7' + v;
      v = v.slice(0, 11);
      var p = v.slice(1), s = '+7';
      if (p.length) s += ' (' + p.slice(0, 3);
      if (p.length >= 3) s += ')';
      if (p.length > 3) s += ' ' + p.slice(3, 6);
      if (p.length > 6) s += '-' + p.slice(6, 8);
      if (p.length > 8) s += '-' + p.slice(8, 10);
      ph.value = s;
    });
    $$('.field', dlg).forEach(function (f) {
      var inp = $('input,select', f);
      inp.addEventListener(inp.tagName === 'SELECT' ? 'change' : 'input', function () { f.classList.remove('err'); inp.removeAttribute('aria-invalid'); });
    });
    /* шторка над экранной клавиатурой (iPhone не уменьшает окно, когда она открыта) */
    var vv = w.visualViewport;
    var fit = function () {
      if (!vv || !dlg.open) return;
      if (!MOB()) { dlg.style.marginBottom = ''; sForm.style.maxHeight = ''; return; }
      var kb = Math.max(0, w.innerHeight - vv.height - vv.offsetTop);
      dlg.style.marginBottom = kb > 40 ? kb + 'px' : '';
      sForm.style.maxHeight = kb > 40 ? Math.max(240, vv.height - 10) + 'px' : '';
    };
    dlg._fit = fit;
    if (vv) { vv.addEventListener('resize', fit); vv.addEventListener('scroll', fit); }
    sForm.addEventListener('focusin', function (e) {
      if (!MOB() || !/^(INPUT|SELECT)$/.test(e.target.tagName)) return;
      setTimeout(function () { try { e.target.scrollIntoView({ block: 'center', behavior: 'smooth' }); } catch (x) { /* старый браузер */ } }, 320);
    });
    $$('[data-zv-close]', dlg).forEach(function (b) { b.addEventListener('click', function () { if (dlg.open) dlg.close(); }); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); }); /* нажатие мимо шторки */
    dlg.addEventListener('close', function () {
      html.classList.remove('chk-lock');
      setTimeout(renderCtx, 0);
      dlg.style.marginBottom = '';
      sForm.style.maxHeight = '';
      if (sForm.classList.contains('sent')) {
        sForm.classList.remove('sent');
        $('.chk-ok', dlg).hidden = true;
        sForm.reset();
        if (mainType) type.value = mainType.value;
        sending = false;
        $('#zv-send', dlg).disabled = false;
        $('#zv-send', dlg).classList.remove('is-loading');
      }
      if (opener) { try { opener.focus({ preventScroll: true }); } catch (x) { /* нет фокуса */ } }
    });
    sForm.addEventListener('submit', submit);
  };
  var renderSheet = function () {
    if (!dlg) return;
    var n = list().length;
    $('.chk-kicker', dlg).textContent = n ? 'Состав заявки' : 'Ваша заявка';
    $('.zv-sw', dlg).hidden = !n;
    $('#zv-list', dlg).innerHTML = n ? itemsHtml(3) : '';
  };
  /* тип объекта: по подписи пункта (без « *»), по значению или по началу подписи */
  var pickType = function (sel, hint) {
    if (!sel || !hint) return false;
    var h = norm(hint).replace(/\s*\*$/, '').toLowerCase(), opts = $$('option', sel), i, o, t;
    for (i = 0; i < opts.length; i++) {
      o = opts[i]; t = norm(o.text).replace(/\s*\*$/, '').toLowerCase();
      if (o.value && (t === h || o.value.toLowerCase() === h)) { sel.value = o.value; return true; }
    }
    return false;
  };
  var openSheet = function (ctx, hint, btn) {
    if (!canDlg) return false;
    if (!dlg) build();
    ctxName = ctx || 'def';
    var tl = TITLES[ctxName] || TITLES.def;
    $('#zv-t', dlg).textContent = tl[0];
    $('#zv-lead', dlg).textContent = tl[1];
    renderSheet();
    var type = $('#zv-type', dlg);
    if (!pickType(type, hint) && !type.value && mainType && mainType.value) type.value = mainType.value;
    opener = btn || d.activeElement;
    if (!dlg.open) dlg.showModal();
    html.classList.add('chk-lock');
    renderCtx();
    if (dlg._fit) dlg._fit();
    var t = fine && !sForm.classList.contains('sent') ? $('#zv-name', dlg) : sForm;
    try { t.focus({ preventScroll: true }); } catch (x) { t.focus(); }
    sForm.scrollTop = 0;
    return true;
  };
  var message = function () {
    var type = $('#zv-type', dlg), o = type.options[type.selectedIndex], ot = o ? norm(o.text).replace(/\s*\*$/, '') : '';
    var lines = ['Заявка из шторки на телефоне'];
    var tail = [];
    if (o && o.value && ot !== o.value) tail.push('Вид объекта: ' + ot);
    tail.push('Страница: ' + pageUrl);
    var room = 2900 - lines[0].length - tail.join('\n').length - 4;
    var sost = text(room);
    if (sost) lines.push(sost);
    return lines.concat(tail).join('\n').slice(0, 2950);
  };
  var submit = function (e) {
    e.preventDefault();
    if (sending) return;
    var els = sForm.elements, ok = true, first = null, send = $('#zv-send', dlg), err = $('#zv-err', dlg);
    [['name', function (v) { return v.trim().length > 1; }],
     ['phone', function (v) { return v.replace(/\D/g, '').length === 11; }],
     ['type', function (v) { return !!v; }]].forEach(function (c) {
      var el = els[c[0]], f = el.closest('.field'), bad = !c[1](el.value);
      f.classList.remove('err');
      if (bad) { void f.offsetWidth; f.classList.add('err'); el.setAttribute('aria-invalid', 'true'); ok = false; first = first || el; }
      else el.removeAttribute('aria-invalid');
    });
    if (!ok) { first.focus(); return; }
    var msg = message();
    els.msg.value = msg;
    sending = true;
    send.disabled = true;
    send.classList.add('is-loading');
    err.hidden = true;
    var done = function () {
      sForm.classList.add('sent');
      $('.chk-ok', dlg).hidden = false;
      sForm.scrollTop = 0;
      clear();
      var back = $('.chk-back', dlg);
      try { back.focus({ preventScroll: true }); } catch (x) { back.focus(); }
    };
    if (DEMO) { setTimeout(done, 700); return; }
    var name = els.name.value.trim(), phone = els.phone.value.trim();
    fetch('/send.php', { method: 'POST', body: new FormData(sForm), headers: { 'Accept': 'application/json' }, credentials: 'same-origin' })
      .then(function (res) {
        return res.text().then(function (t) {
          var json = null;
          try { json = JSON.parse(t); } catch (x) { /* ответ не JSON */ }
          if (!res.ok || !json || !json.success) {
            var er = new Error('send failed: ' + res.status);
            er.userMessage = json && json.message ? json.message : '';
            throw er;
          }
          return json;
        });
      })
      .then(function () {
        goal('audit', { form: 'zayavka' });
        try {
          if (typeof w.Comagic !== 'undefined' && typeof w.Comagic.addOfflineRequest === 'function') {
            w.Comagic.addOfflineRequest({ name: name, phone: phone, message: msg, form_name: 'Заявка с телефона: ' + PAGE.n.slice(0, 80) });
          }
        } catch (x) { console.error('UIS:', x); }
        done();
      })
      .catch(function (x) {
        console.error('Ошибка отправки заявки:', x);
        sending = false;
        send.disabled = false;
        send.classList.remove('is-loading');
        $('#zv-err-t', dlg).textContent = x && x.userMessage ? x.userMessage : 'Не удалось отправить заявку.';
        err.hidden = false;
      });
  };

  /* ---------- нижняя панель: «Заявка N», нажатие — шторка ---------- */
  var mbar = d.getElementById('mbar'), c2 = mbar ? $('.c2', mbar) : null, c2html = c2 ? c2.innerHTML : '';
  var renderBar = function () {
    if (!c2) return;
    var n = list().length;
    c2.innerHTML = n ? '<span>Заявка</span><b class="zv-badge">' + n + '</b>' : c2html;
    c2.setAttribute('aria-label', n ? 'Заявка: в составе ' + n : norm(c2.textContent));
  };
  /* перехват на этапе погружения — до обработчиков якорей app.js */
  var own = function (sel, fn) {
    w.addEventListener('click', function (e) {
      if (!MOB() || !canDlg || e.button) return;
      var b = e.target && e.target.closest ? e.target.closest(sel) : null;
      if (!b) return;
      e.preventDefault();
      e.stopPropagation();
      fn(b);
    }, true);
  };
  if (c2) own('#mbar .c2', function (b) { openSheet('def', '', b); });

  /* ---------- панель блока (телефон): документы и лаборатория ---------- */
  var pcbar = null, ctx = null, cta = d.getElementById('zayavka');
  var renderCtx = function () {
    var on = false;
    if (ctx && MOB() && !(dlg && dlg.open)) {
      var i = ctx.info();
      var r = ctx.el.getBoundingClientRect(), vh = w.innerHeight;
      var inView = ctx.always || (r.top < vh * 0.75 && r.bottom > vh * 0.4);
      var formIn = cta && cta.getBoundingClientRect().top < vh * 0.6;
      if (i && inView && !formIn) {
        if (!pcbar) {
          pcbar = d.createElement('div');
          pcbar.className = 'zv-bar';
          pcbar.innerHTML = '<p class="zv-bar-t"><b></b><span></span></p><button type="button" class="btn btn-w zv-bar-b"><span class="btn-t"></span></button>';
          d.body.appendChild(pcbar);
          $('button', pcbar).addEventListener('click', function () { if (pcbar._go) pcbar._go(this); });
        }
        on = true;
        $('b', pcbar).textContent = i.b;
        $('span', pcbar).textContent = i.s;
        $('.btn-t', pcbar).textContent = i.btn;
        pcbar._go = i.go;
      }
    }
    if (pcbar) pcbar.classList.toggle('show', on);
    if (mbar) mbar.classList.toggle('zv-hide', on);
  };
  var rq = 0;
  w.addEventListener('scroll', function () { if (!rq) rq = requestAnimationFrame(function () { rq = 0; renderCtx(); }); }, { passive: true });
  w.addEventListener('resize', renderCtx);

  subs.push(renderBar, renderForm, renderSheet, renderCtx);

  /* ================= блоки с выбором ================= */

  /* 1. Самопроверка (13 страниц): отметки — в составе; кнопка блока открывает своё окно (samoproverka-forma.js),
     в нём тоже виден весь состав */
  var chk = d.getElementById('samoproverka');
  if (chk && $('.f-check-list', chk)) {
    var cKey = 'chk:' + path, quietChk = false;
    var cTitle = txt($('#chk-t', chk) || $('.f-check-t', chk) || $('h2', chk));
    var risk = chk.getAttribute('data-chk-mode') === 'risk';
    var cItems = function () {
      return $$('.f-check-list li', chk).map(function (li) {
        var cb = $('input[type=checkbox]', li), sg = $('strong', li);
        return { t: txt(sg || li).replace(/[\s:.]+$/, ''), on: !!(cb && cb.checked), cb: cb };
      });
    };
    var cEntry = function () {
      var it = cItems(), on = it.filter(function (x) { return x.on; }), off = it.filter(function (x) { return !x.on; });
      return {
        ico: 'chk', t: 'Самопроверка: ' + cTitle,
        s: risk ? 'признаков риска ' + on.length + ' из ' + it.length : on.length + ' из ' + it.length + ' на месте',
        l: risk ? on.map(function (x) { return { c: 'n', p: 'Есть', t: x.t }; }) : off.map(function (x) { return { c: 'n', p: 'Нет', t: x.t }; })
      };
    };
    chk.addEventListener('change', function (e) {
      if (quietChk || !e.target.closest('.f-check-list')) return;
      put(cKey, cEntry(), true);
      toast(risk ? 'Отметки добавлены в заявку' : 'Результат добавлен в заявку');
    });
    /* после возврата на страницу в той же вкладке — отметки из состава снова в блоке */
    if (st.e[cKey] && !cItems().some(function (x) { return x.on; })) {
      var keep = st.e[cKey].l || [], names = keep.map(function (l) { return l.t; });
      quietChk = true;
      cItems().forEach(function (x) { if (x.cb) x.cb.checked = risk ? names.indexOf(x.t) > -1 : names.indexOf(x.t) < 0; });
      var c0 = $('.f-check-list input', chk);
      if (c0) c0.dispatchEvent(new Event('change', { bubbles: true }));
      quietChk = false;
    }
    /* страница без своего окна самопроверки: кнопка блока на телефоне открывает шторку заявки */
    if (!$('[data-chk-open]', chk)) {
      own('#samoproverka a[href="#zayavka"]', function (b) { put(cKey, cEntry(), true); openSheet('def', '', b); });
    }
    hooks[cKey] = function () {
      quietChk = true;
      cItems().forEach(function (x) { if (x.cb) x.cb.checked = false; });
      var c1 = $('.f-check-list input', chk);
      if (c1) c1.dispatchEvent(new Event('change', { bubbles: true }));
      quietChk = false;
    };
  }

  /* 2. Конструктор «Соберите папку» (документы для Роспотребнадзора) */
  var dk = d.getElementById('konstruktor');
  if (dk) {
    var dkObjs = function () { return $$('.dk-pick[aria-pressed="true"]', dk).map(function (b) { return txt($('span', b) || b); }); };
    var dkCount = function () {
      var rows = $$('.dk-row', dk), m = 0, no = [];
      rows.forEach(function (r) { var p = $('[aria-pressed="true"]', r); if (p) { m++; if (p.getAttribute('data-v') === 'n') no.push(r); } });
      return { all: rows.length, m: m, no: no };
    };
    var dkName = function (r) {
      var t = $('.dk-row-t', r), sm = t ? $('small', t) : null, s = txt(t);
      if (sm) s = norm(s.replace(txt(sm), ''));
      return norm(txt($('.dk-row-n', r)) + ' ' + s);
    };
    var dkEntry = function () {
      var o = dkObjs(), c = dkCount();
      if (!o.length) return null;
      return {
        ico: 'doc', t: 'Папка документов: ' + o.join(', '),
        s: 'отмечено ' + c.m + ' из ' + c.all + (c.no.length ? ', нет — ' + c.no.length : ''),
        l: c.no.map(function (r) { return { c: 'n', p: 'Нет', t: dkName(r) }; }), hint: o[0]
      };
    };
    var dkSync = function () { var e = dkEntry(); if (e && dkCount().m) put('dok', e); };
    var gOpen = {};
    var dkDecorate = function () {
      if (!MOB()) return;
      var picks = $('.dk-picks', dk), any = dkObjs().length;
      if (picks && !$('.zv-picks-ed', picks)) {
        var ed = d.createElement('button');
        ed.type = 'button'; ed.className = 'zv-picks-ed'; ed.textContent = 'Изменить вид объекта';
        picks.appendChild(ed);
        ed.addEventListener('click', function () { picks._unfold = true; picks.classList.remove('zv-fold'); });
      }
      if (picks) picks.classList.toggle('zv-fold', !!any && !picks._unfold);
      $$('.dk-lg', dk).forEach(function (g, i) {
        var h = $('h3', g);
        if (!h) return;
        var rows = $$('.dk-row', g), m = 0, n = 0;
        rows.forEach(function (r) { var p = $('[aria-pressed="true"]', r); if (p) { m++; if (p.getAttribute('data-v') === 'n') n++; } });
        var gc = $('.zv-gc', h);
        if (!gc) { gc = d.createElement('span'); gc.className = 'zv-gc'; h.appendChild(gc); }
        var gcH = m + '/' + rows.length + (n ? ' · <b>нет ' + n + '</b>' : '');
        if (gc.innerHTML !== gcH) gc.innerHTML = gcH;
        if (gOpen[i] === undefined) gOpen[i] = i === 0;
        g.classList.toggle('zv-open', !!gOpen[i]);
        if (!h._zv) {
          h._zv = 1;
          h.setAttribute('role', 'button');
          h.setAttribute('tabindex', '0');
          var tg = function () { gOpen[i] = !gOpen[i]; g.classList.toggle('zv-open', gOpen[i]); h.setAttribute('aria-expanded', gOpen[i] ? 'true' : 'false'); };
          h.addEventListener('click', tg);
          h.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); tg(); } });
        }
        h.setAttribute('aria-expanded', gOpen[i] ? 'true' : 'false');
      });
    };
    if (w.MutationObserver) {
      var mo = new MutationObserver(function () { mo.disconnect(); dkDecorate(); mo.observe(dk, { childList: true, subtree: true }); });
      mo.observe(dk, { childList: true, subtree: true });
    }
    dk.addEventListener('click', function (e) {
      var pk = e.target.closest && e.target.closest('.dk-pick');
      if (pk) { var ps = $('.dk-picks', dk); if (ps) ps._unfold = false; }
      setTimeout(function () {
        dkDecorate();
        if (e.target.closest && e.target.closest('.dk-seg button, .dk-pick')) dkSync();
        renderCtx();
      }, 0);
    });
    var dkGo = function (b) {
      var en = dkEntry();
      if (en) put('dok', en, true);
      goal('dokumenty_spisok');
      openSheet('dok', en ? en.hint : '', b);
    };
    own('#dk-send', dkGo);
    ctx = {
      el: dk,
      info: function () {
        var o = dkObjs();
        if (!o.length) return null;
        var c = dkCount();
        return { b: 'Отмечено ' + c.m + ' из ' + c.all, s: c.no.length ? 'Нет: ' + c.no.length + ' — уйдут в заявку' : 'Отмечайте «Есть» и «Нет»', btn: 'Отправить', go: dkGo };
      }
    };
    dkDecorate();
    hooks.dok = function () { };
  }

  /* 3. Лабораторный расчёт: прайс с «+» и наборы (скрипт страницы хранит расчёт в sessionStorage «lb-calc») */
  var LB = w.LB;
  if (LB) {
    var rub = function (n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '\u00a0') + '\u00a0₽'; };
    var plural = function (n, a, b, c) { var m = n % 10, h = n % 100; return n + ' ' + (m === 1 && h !== 11 ? a : m >= 2 && m <= 4 && (h < 12 || h > 14) ? b : c); };
    var labRead = function () { var S = {}; try { S = JSON.parse(sessionStorage.getItem('lb-calc')) || {}; } catch (x) { /* нет хранилища */ } return S; };
    var labSig = '';
    var labSync = function () {
      var S = labRead(), ks = Object.keys(S).filter(function (k) { return LB[k] && S[k] > 0; });
      var sig = JSON.stringify(ks.map(function (k) { return [k, S[k]]; }));
      if (sig === labSig) return;
      labSig = sig;
      if (!ks.length) { if (st.e.lab) { delete st.e.lab; save(); } return; }
      var sum = 0;
      ks.forEach(function (k) { sum += LB[k][2] * S[k]; });
      put('lab', {
        ico: 'lab', t: 'Лабораторный расчёт', s: plural(ks.length, 'позиция', 'позиции', 'позиций') + ', от ' + rub(sum),
        l: ks.map(function (k) { return { t: LB[k][0] + ': ' + S[k] + ' × ' + (LB[k][3] ? 'от ' : '') + rub(LB[k][2]) }; })
      });
    };
    ['click', 'change', 'keyup'].forEach(function (ev) { d.addEventListener(ev, function () { setTimeout(labSync, 0); }); });
    labSync();
    hooks.lab = function () { labSig = ''; var c = d.getElementById('lb-bar-clear'); if (c) c.click(); };
    var labGo = function (b) { labSync(); goal('lab_raschet'); openSheet('lab', '', b); };
    own('#lb-bar-go', labGo);
    if (!ctx) {
      ctx = {
        el: $('#ceny') || d.body, always: true,
        info: function () { var e = st.e.lab; return e ? { b: e.s, s: 'Расчёт уйдёт вместе с заявкой', btn: 'Оформить', go: labGo } : null; }
      };
      html.classList.add('zv-lab');
    }
    /* наборы по видам объектов: на телефоне — кнопки видов объекта и одна карточка */
    var sets = $('.lb-sets'), setsCards = sets ? $$('.lb-set', sets) : [];
    if (sets && setsCards.length > 2 && MOB()) {
      var chips = d.createElement('div');
      chips.className = 'zv-chips';
      chips.setAttribute('role', 'group');
      chips.setAttribute('aria-label', 'Вид объекта');
      chips.innerHTML = setsCards.map(function (c, i) { return '<button type="button" aria-pressed="' + (i === 0) + '">' + esc(txt($('.lb-set-n', c)) || ('Набор ' + (i + 1))) + '</button>'; }).join('');
      sets.parentNode.insertBefore(chips, sets);
      sets.classList.add('zv-setpick');
      setsCards[0].classList.add('zv-cur');
      chips.addEventListener('click', function (e) {
        var b = e.target.closest('button');
        if (!b) return;
        var i = $$('button', chips).indexOf(b);
        $$('button', chips).forEach(function (x, j) { x.setAttribute('aria-pressed', j === i ? 'true' : 'false'); });
        setsCards.forEach(function (c, j) { c.classList.toggle('zv-cur', j === i); });
        if (w.ScrollTrigger) w.ScrollTrigger.refresh();
      });
    }
  }

  /* 4. Цена по площади (дезинсекция и дератизация кафе и ресторанов) */
  var area = d.getElementById('rk-area');
  if (area) {
    var aKey = 'area:' + path, ts = d.getElementById('tseny');
    var svc = /дератизац/i.test(PAGE.n) ? 'дератизация' : /дезинсекц/i.test(PAGE.n) ? 'дезинсекция' : 'обработка';
    var aEntry = function () {
      return { ico: 'area', t: 'Расчёт по площади: ' + svc, s: area.value + ' м²: разово ' + txt(d.getElementById('rk-c-o')) + ', по договору ' + txt(d.getElementById('rk-c-m')) + ' в месяц', l: [] };
    };
    var bandRows = function () { var tb = $('.rk-ptbl', ts || d); return tb ? $$('tbody tr', tb) : []; };
    var hl = function () {
      var v = +area.value, rows = bandRows();
      rows.forEach(function (tr) {
        var nums = (txt(tr.cells[0]).match(/\d[\d\s]*/g) || []).map(function (x) { return +x.replace(/\s/g, ''); });
        var lo = 0, hi = 1e9, t0 = txt(tr.cells[0]);
        if (!nums.length) { lo = 1e9; } else if (/^до/i.test(t0)) hi = nums[0]; else if (/^(от|свыше|более|больше)/i.test(t0)) lo = nums[0] + (/^от/i.test(t0) ? 0 : 1); else if (nums.length > 1) { lo = nums[0] + 1; hi = nums[1]; } else { lo = hi = nums[0]; }
        tr.classList.toggle('zv-cur', v >= lo && v <= hi);
      });
    };
    area.addEventListener('change', function () { put(aKey, aEntry()); hl(); });
    area.addEventListener('input', hl);
    own('#rk-c-go', function (b) { put(aKey, aEntry(), true); openSheet('area', 'Ресторан или кафе', b); });
    hl();
  }

  /* 5. «Схема объекта» на главной: отрасль — в составе, тип объекта подставлен */
  var shema = d.getElementById('shema');
  if (shema) {
    var MAPT = { food: 'Пищевое производство', rest: 'Ресторан или кафе', sklad: 'Склад, логистика', bc: 'Бизнес-центр или офисное здание' };
    own('#shema a[href="#zayavka"]', function (b) {
      var tab = $('[role="tab"][aria-selected="true"]', shema), id = tab ? (tab.getAttribute('data-o') || tab.id.replace('hz-t-', '')) : '';
      put('shema', { ico: 'map', t: 'Схема объекта: ' + (txt(tab ? $('b', tab) || tab : null) || 'объект'), s: 'нужна схема точек контроля для своего объекта', l: [] }, true);
      openSheet('shema', MAPT[id] || '', b);
    });
  }

  renderBar(); renderForm(); renderCtx();
  if (mq && mq.addEventListener) mq.addEventListener('change', renderCtx);
})();
