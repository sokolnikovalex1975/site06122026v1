/* Самопроверка → заявка (решение владельца 19.11.2026, tools/site/samoproverka_forma.py).
   Блок «Самопроверка» (#samoproverka, раскладка — tools/site/samoproverka.py): человек отмечает пункты, под списком —
   подсказка и кнопка. Кнопка
   (data-chk-open) открывает короткую форму: на компьютере — окно по центру, на телефоне — шторка снизу без затемнения
   страницы (ЗАКОН ВЛАДЕЛЬЦА 17.11.2026: на телефоне ничего не затемнять). В заявку уходит результат: какие пункты
   отмечены и какие нет. Отправка — тот же /send.php, что у основной формы (имя, телефон, тип объекта, комментарий msg);
   цель Метрики «audit» и заявка в UIS — только после ответа сервера. Без скрипта или в очень старом браузере кнопка —
   обычная ссылка на основную форму внизу страницы. Основная форма и app.js не меняются: щелчок по кнопке перехватывается
   на этапе погружения, до прокрутки к #zayavka. */
(function () {
  'use strict';
  var d = document, w = window, html = d.documentElement;
  var sec = d.getElementById('samoproverka');
  if (!sec || !sec.querySelector('[data-chk-open]')) return;
  var probe = d.createElement('dialog');
  if (typeof probe.showModal !== 'function') return; /* очень старый браузер: ссылка ведёт к основной форме */

  var $ = function (s, r) { return (r || d).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); };
  var norm = function (s) { return String(s || '').replace(/\s+/g, ' ').trim(); };
  var esc = function (s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); };
  var fine = w.matchMedia && w.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var phoneView = function () { return w.matchMedia && w.matchMedia('(max-width: 760px)').matches; };
  var risk = sec.getAttribute('data-chk-mode') === 'risk';
  var DEMO = /\.github\.io$/i.test(location.hostname); /* превью на GitHub Pages: заявки никуда не уходят */
  var PROD = /^(www\.)?xn----itbbsflddbfpfdodg9d0f\.xn--p1ai$/i.test(location.hostname);
  var pageUrl = (PROD ? 'https://пестконтроль-центр.рф' : location.origin) + location.pathname;
  var title = norm(($('#chk-t') || sec).textContent);
  var name = sec.getAttribute('data-chk-name') || 'самопроверка';
  var mainForm = d.getElementById('form'), mainType = d.getElementById('f-type');
  var legal = mainForm && $('.legal', mainForm);

  var X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>';
  var dlg = d.createElement('dialog');
  dlg.className = 'chk-dlg';
  dlg.id = 'chk-dlg';
  dlg.setAttribute('aria-labelledby', 'chk-dlg-t');
  dlg.setAttribute('data-lenis-prevent', '');
  dlg.innerHTML =
    '<form class="chk-box" id="chk-form" novalidate tabindex="-1">' +
      '<button type="button" class="chk-x" data-chk-close aria-label="Закрыть форму">' + X + '</button>' +
      '<div class="chk-body">' +
        '<p class="chk-kicker">Ваш результат</p>' +
        '<div class="chk-sum">' +
          '<p class="chk-score"><b id="chk-dlg-n">0</b> из <span id="chk-dlg-of">0</span> <span class="chk-score-l">' + (risk ? 'признаков риска' : 'на месте') + '</span></p>' +
          '<div class="chk-bar" id="chk-dlg-bar" aria-hidden="true"></div>' +
          '<p class="chk-miss-t" id="chk-dlg-miss-t"></p>' +
          '<ul class="chk-miss" id="chk-dlg-miss"></ul>' +
        '</div>' +
        '<h3 id="chk-dlg-t">' + esc(sec.getAttribute('data-chk-title') || 'Бесплатное обследование объекта') + '</h3>' +
        '<p class="chk-lead">' + esc(sec.getAttribute('data-chk-lead') || '') + '</p>' +
        '<div class="chk-fg">' +
          '<div class="field"><label class="sr-only" for="chk-name">Ваше имя</label><input id="chk-name" name="name" placeholder="Ваше имя *" required autocomplete="name" maxlength="150"><small class="ferr">Укажите имя</small></div>' +
          '<div class="field"><label class="sr-only" for="chk-phone">Телефон</label><input id="chk-phone" name="phone" type="tel" inputmode="tel" placeholder="+7 (___) ___-__-__ *" required autocomplete="tel"><small class="ferr">Укажите телефон полностью</small></div>' +
          '<div class="field"><label class="sr-only" for="chk-type">Тип объекта</label><select id="chk-type" name="type" required><option value="" disabled selected>Тип объекта *</option></select><small class="ferr">Выберите тип объекта</small></div>' +
        '</div>' +
        '<input type="hidden" name="msg" value="">' +
        '<button type="submit" class="btn btn-w btn-lg chk-send" id="chk-send"><span class="btn-t">Отправить заявку</span><i class="spin" aria-hidden="true"></i></button>' +
        '<p class="chk-err" id="chk-err" role="alert" hidden><span id="chk-err-t">Не удалось отправить заявку.</span> Попробуйте ещё раз или позвоните: <a href="tel:+74951043570">+7 (495) 104-35-70</a></p>' +
      '</div>' +
      '<div class="chk-ok" role="status" aria-live="polite" hidden>' +
        '<svg class="ok-ic" viewBox="0 0 52 52" aria-hidden="true"><circle cx="26" cy="26" r="24" fill="none"/><path fill="none" d="M15 27l7 7 15-16"/></svg>' +
        '<h3>Заявка отправлена</h3>' +
        '<p>Перезвоним в ближайшее рабочее время, чтобы согласовать день выезда. Ваши отметки уже в заявке — специалист увидит, на что посмотреть в первую очередь.</p>' +
        '<button type="button" class="btn btn-o chk-back" data-chk-close><span class="btn-t">Вернуться к странице</span></button>' +
      '</div>' +
    '</form>';
  /* согласие и политика — та же строка, что под основной формой (с её ссылками) */
  if (legal) $('.chk-send', dlg).insertAdjacentElement('afterend', legal.cloneNode(true));
  ($('main') || d.body).insertAdjacentElement('afterend', dlg);

  var form = $('#chk-form', dlg), ph = $('#chk-phone', dlg), type = $('#chk-type', dlg);
  var send = $('#chk-send', dlg), err = $('#chk-err', dlg), errT = $('#chk-err-t', dlg);
  var sending = false, opener = null;
  /* типы объекта — как в основной форме этой страницы (их принимает send.php), с тем же выбором по умолчанию */
  if (mainType) { type.innerHTML = mainType.innerHTML; type.value = mainType.value; }

  /* пункты: короткое название — текст в <strong> без двоеточия, иначе весь текст пункта */
  var items = function () {
    return $$('.f-check-list li', sec).map(function (li) {
      var cb = $('input[type=checkbox]', li), st = $('strong', li);
      return { t: norm((st || li).textContent).replace(/[\s:.]+$/, ''), on: !!(cb && cb.checked) };
    });
  };
  var fill = function () {
    var it = items(), on = it.filter(function (x) { return x.on; }), off = it.filter(function (x) { return !x.on; });
    var score = $('.chk-score', dlg), mt = $('#chk-dlg-miss-t', dlg), ml = $('#chk-dlg-miss', dlg), list = risk ? on : off;
    $('#chk-dlg-n', dlg).textContent = on.length;
    $('#chk-dlg-of', dlg).textContent = it.length;
    score.classList.toggle('full', !risk && it.length > 0 && !off.length);
    score.classList.toggle('risk', risk && on.length > 0);
    $('#chk-dlg-bar', dlg).innerHTML = it.map(function (x) { return x.on ? '<i class="on"></i>' : '<i></i>'; }).join('');
    ml.innerHTML = '';
    if (risk) {
      mt.textContent = on.length ? 'Отмечены признаки:' : 'Признаков риска не отмечено — на осмотре подтвердим, хватит ли разовой обработки.';
    } else if (!on.length) {
      mt.textContent = 'Отметок нет — на обследовании пройдём все ' + it.length + ' пунктов.';
    } else if (!off.length) {
      mt.textContent = 'Все пункты на месте — на обследовании проверим, как это работает на объекте.';
    } else {
      mt.textContent = 'Не хватает:';
    }
    if (risk ? on.length : (on.length && off.length)) {
      list.forEach(function (x) { var li = d.createElement('li'); li.textContent = x.t; ml.appendChild(li); });
    }
    ml.hidden = !ml.children.length;
    return { it: it, on: on, off: off };
  };
  var message = function (s) {
    var join = function (a) { return a.length ? a.map(function (x) { return x.t; }).join('; ') : '—'; };
    var lines = ['Заявка из самопроверки «' + title + '»'];
    if (risk) {
      lines.push('Отмечено признаков риска: ' + s.on.length + ' из ' + s.it.length);
      lines.push('Отмечены: ' + join(s.on));
      lines.push('Не отмечены: ' + join(s.off));
    } else {
      lines.push('Отмечено: ' + s.on.length + ' из ' + s.it.length);
      lines.push('Есть: ' + join(s.on));
      lines.push('Не отмечено: ' + join(s.off));
    }
    /* как у основной формы: если подпись пункта отличается от значения для send.php, подпись — в комментарий */
    var o = type.options[type.selectedIndex], ot = o ? norm(o.text).replace(/\s*\*$/, '') : '';
    if (o && o.value && ot !== o.value) lines.push('Вид объекта: ' + ot);
    lines.push('Страница: ' + pageUrl);
    return lines.join('\n').slice(0, 2900);
  };

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

  /* телефон: шторка над экранной клавиатурой (iPhone не уменьшает окно, когда она открыта) */
  var vv = w.visualViewport;
  var fit = function () {
    if (!vv || !dlg.open) return;
    if (!phoneView()) { dlg.style.marginBottom = ''; form.style.maxHeight = ''; return; }
    var kb = Math.max(0, w.innerHeight - vv.height - vv.offsetTop);
    dlg.style.marginBottom = kb > 40 ? kb + 'px' : '';
    form.style.maxHeight = kb > 40 ? Math.max(240, vv.height - 10) + 'px' : '';
  };
  if (vv) { vv.addEventListener('resize', fit); vv.addEventListener('scroll', fit); }
  form.addEventListener('focusin', function (e) {
    if (!phoneView() || !/^(INPUT|SELECT)$/.test(e.target.tagName)) return;
    setTimeout(function () { try { e.target.scrollIntoView({ block: 'center', behavior: 'smooth' }); } catch (x) { /* старый браузер */ } }, 320);
  });

  var close = function () { if (dlg.open) dlg.close(); };
  var open = function (btn) {
    opener = btn;
    fill();
    if (!type.value && mainType && mainType.value) type.value = mainType.value;
    dlg.showModal();
    html.classList.add('chk-lock');
    fit();
    /* на компьютере — сразу в поле имени; на телефоне клавиатуру не открываем, чтобы был виден результат */
    var t = fine && !form.classList.contains('sent') ? $('#chk-name', dlg) : form;
    try { t.focus({ preventScroll: true }); } catch (x) { t.focus(); }
    form.scrollTop = 0;
  };
  dlg.addEventListener('close', function () {
    html.classList.remove('chk-lock');
    dlg.style.marginBottom = '';
    form.style.maxHeight = '';
    if (form.classList.contains('sent')) {
      /* после отправки окно снова открывается с пустой формой */
      form.classList.remove('sent');
      $('.chk-ok', dlg).hidden = true;
      form.reset();
      if (mainType) type.value = mainType.value;
      sending = false;
      send.disabled = false;
      send.classList.remove('is-loading');
    }
    if (opener) { try { opener.focus({ preventScroll: true }); } catch (x) { /* нет фокуса */ } }
  });
  /* перехват до обработчиков app.js: кнопка открывает форму, а не прокручивает к #zayavka */
  w.addEventListener('click', function (e) {
    var b = e.target && e.target.closest ? e.target.closest('[data-chk-open]') : null;
    if (!b || !sec.contains(b)) return;
    e.preventDefault();
    e.stopPropagation();
    open(b);
  }, true);
  $$('[data-chk-close]', dlg).forEach(function (b) { b.addEventListener('click', close); });
  dlg.addEventListener('click', function (e) { if (e.target === dlg) close(); }); /* щелчок мимо окна */

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (sending) return;
    var els = form.elements, ok = true, first = null;
    [['name', function (v) { return v.trim().length > 1; }],
     ['phone', function (v) { return v.replace(/\D/g, '').length === 11; }],
     ['type', function (v) { return !!v; }]].forEach(function (c) {
      var el = els[c[0]], f = el.closest('.field'), bad = !c[1](el.value);
      f.classList.remove('err');
      if (bad) { void f.offsetWidth; f.classList.add('err'); el.setAttribute('aria-invalid', 'true'); ok = false; first = first || el; }
      else el.removeAttribute('aria-invalid');
    });
    if (!ok) { first.focus(); return; }
    var msg = message(fill());
    els.msg.value = msg;
    sending = true;
    send.disabled = true;
    send.classList.add('is-loading');
    err.hidden = true;
    var done = function () {
      form.classList.add('sent');
      $('.chk-ok', dlg).hidden = false;
      form.scrollTop = 0;
      var back = $('.chk-back', dlg);
      try { back.focus({ preventScroll: true }); } catch (x) { back.focus(); }
    };
    if (DEMO) { setTimeout(done, 700); return; }
    fetch('/send.php', { method: 'POST', body: new FormData(form), headers: { 'Accept': 'application/json' }, credentials: 'same-origin' })
      .then(function (res) {
        return res.text().then(function (txt) {
          var json = null;
          try { json = JSON.parse(txt); } catch (x) { /* ответ не JSON */ }
          if (!res.ok || !json || !json.success) {
            var er = new Error('send failed: ' + res.status);
            er.userMessage = json && json.message ? json.message : '';
            throw er;
          }
          return json;
        });
      })
      .then(function () {
        try { if (typeof w.ym === 'function') w.ym(113675622, 'reachGoal', 'audit', { form: 'samoproverka' }); } catch (x) { console.error('Яндекс Метрика:', x); }
        try {
          if (typeof w.Comagic !== 'undefined' && typeof w.Comagic.addOfflineRequest === 'function') {
            w.Comagic.addOfflineRequest({ name: els.name.value.trim(), phone: els.phone.value.trim(), message: msg, form_name: 'Самопроверка: ' + name });
          }
        } catch (x) { console.error('UIS:', x); }
        done();
      })
      .catch(function (x) {
        console.error('Ошибка отправки самопроверки:', x);
        sending = false;
        send.disabled = false;
        send.classList.remove('is-loading');
        errT.textContent = x && x.userMessage ? x.userMessage : 'Не удалось отправить заявку.';
        err.hidden = false;
      });
  });

})();
