/* ПЕСТКОНТРОЛЬ Центр — интерактив и анимации (GSAP + ScrollTrigger + Lenis, всё локально) */
(function () {
  'use strict';
  var html = document.documentElement;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var hasGSAP = !!(window.gsap && window.ScrollTrigger);
  /* скрипты подключаются после первой отрисовки; если они пришли позже страховки (4 с, класс anim-fail), страница уже
     показана целиком — анимации не запускаем, чтобы не прятать видимый текст повторно */
  var anim = hasGSAP && !reduce && !html.classList.contains('anim-fail');
  if (!anim) html.classList.add('anim-fail');
  html.classList.add('anim-ready');
  if (hasGSAP) gsap.registerPlugin(ScrollTrigger);

  /* ---------- текст кнопок для эффекта «прокрутки» надписи ---------- */
  $$('.btn-t').forEach(function (el) {
    el.setAttribute('data-t', el.textContent.trim());
    el.innerHTML = '<span>' + el.innerHTML + '</span>';
  });
  /* ссылки-заглушки не прыгают наверх */
  $$('a[data-todo]').forEach(function (a) { a.addEventListener('click', function (e) { e.preventDefault(); }); });
  /* ширина шкал риска для режимов без анимации */
  $$('.bar-f').forEach(function (b) { b.style.setProperty('--w', b.dataset.w + '%'); });

  /* ---------- плавный скролл ---------- */
  var lenis = null;
  if (window.Lenis && !reduce) {
    lenis = new Lenis({ lerp: 0.09, smoothWheel: true, wheelMultiplier: 1 });
    if (hasGSAP) {
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
      gsap.ticker.lagSmoothing(0);
    } else {
      var raf = function (t) { lenis.raf(t); requestAnimationFrame(raf); };
      requestAnimationFrame(raf);
    }
  }
  var scrollToEl = function (target, isTop) {
    /* начало блока — сразу под шапкой: раздел «переход к блоку по якорю» в конце файла (13.11.2026) */
    if (window.pcAnchor) return window.pcAnchor.go(target, isTop, lenis, reduce);
    if (lenis) lenis.scrollTo(isTop ? 0 : target, { offset: isTop ? 0 : -80, duration: 0.8, easing: function (t) { return 1 - Math.pow(1 - t, 4); } });
    else if (isTop) window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
    else target.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
  };

  /* ---------- меню ---------- */
  var hdr = $('#hdr'), burger = $('#burger'), mmenu = $('#mmenu'), menuOpen = false, mmReset = 0;
  /* раскрывающиеся пункты мобильного меню («Отрасли»): после закрытия меню возвращаются в исходное состояние */
  var mmGroups = $$('.mm-group');
  var setGroup = function (g, o) { g.classList.toggle('open', o); $('.mm-toggle', g).setAttribute('aria-expanded', o); };
  mmGroups.forEach(function (g) { $('.mm-toggle', g).addEventListener('click', function () { setGroup(g, !g.classList.contains('open')); }); });
  var setMenu = function (o) {
    clearTimeout(mmReset);
    if (o) { /* центр круга — по фактическому положению кнопки при любом масштабе */
      var r = burger.getBoundingClientRect();
      mmenu.style.setProperty('--mx', (r.left + r.width / 2) + 'px');
      mmenu.style.setProperty('--my', (r.top + r.height / 2) + 'px');
    } else mmReset = setTimeout(function () { mmGroups.forEach(function (g) { setGroup(g, g.hasAttribute('data-open')); }); }, 800);
    menuOpen = o;
    document.body.classList.toggle('menu-open', o);
    burger.setAttribute('aria-expanded', o);
    burger.setAttribute('aria-label', o ? 'Закрыть меню' : 'Открыть меню');
    hdr.classList.remove('hide');
    if (lenis) { o ? lenis.stop() : lenis.start(); }
  };
  burger.addEventListener('click', function () { setMenu(!menuOpen); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && menuOpen) setMenu(false); });
  $$('.mmenu > a, .mmenu .mm-toggle').forEach(function (a, i) { a.style.setProperty('--d', (0.15 + i * 0.045) + 's'); }); /* задержка только при открытии */

  /* выпадающий список «Отрасли» в шапке. Мышь: открывается наведением (CSS). Касание и клавиатура: щелчок по кнопке,
     Esc и щелчок вне списка закрывают, стрелка вниз переводит фокус на первый пункт */
  $$('.nav-dd').forEach(function (dd) {
    var btn = $('.nav-dd-btn', dd);
    var set = function (o) { dd.classList.toggle('open', o); btn.setAttribute('aria-expanded', o); };
    btn.addEventListener('click', function () {
      if (fine && dd.matches(':hover') && !dd.classList.contains('open') && !dd.classList.contains('nohover')) return; /* уже открыт наведением */
      set(!dd.classList.contains('open'));
    });
    dd.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { set(false); dd.classList.add('nohover'); btn.focus(); }
      else if (e.key === 'ArrowDown' && e.target === btn) { e.preventDefault(); set(true); var f = $('.nav-dd-panel a', dd); if (f) f.focus(); }
    });
    dd.addEventListener('focusout', function (e) { if (!dd.contains(e.relatedTarget)) set(false); });
    dd.addEventListener('mouseleave', function () { dd.classList.remove('nohover'); if (!dd.contains(document.activeElement)) set(false); });
    document.addEventListener('click', function (e) { if (!dd.contains(e.target)) set(false); });
    $$('.nav-dd-panel a', dd).forEach(function (a) { a.addEventListener('click', function () { set(false); dd.classList.add('nohover'); }); });
  });

  /* ---------- якоря ---------- */
  $$('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('href');
      if (id === '#') return;
      var t = id === '#top' ? document.body : $(id);
      if (!t) return;
      e.preventDefault();
      if (menuOpen) setMenu(false);
      scrollToEl(t, id === '#top');
      if (id === '#main') { t.focus({ preventScroll: true }); }
    });
  });

  /* ---------- шапка, прогресс, мобильная панель ----------
     Шапка (17.11.2026, решение владельца после разбора удобства 13.11). На компьютере и планшете она всегда на месте,
     после 30 px прокрутки — компактная (класс scrolled, style.css «компактная шапка»). На телефоне (до 760 px) и в низком
     окне (до 500 px) уходит после 48 px прокрутки вниз подряд, если страница прокручена дальше 400 px, и возвращается
     после 24 px прокрутки вверх с любой скоростью; в первых 120 px видна всегда. Счёт начинается заново при каждой смене
     направления — дрожание пальца шапку не дёргает. Было: на всех экранах шапка уезжала после 500 px и возвращалась,
     только если между двумя событиями прокрутки больше 4 px вверх, — при медленной прокрутке не возвращалась вовсе */
  var prog = $('#progress'), mbar = $('#mbar'), cta = $('#zayavka'), lastY = scrollY, run = 0;
  var awayMq = matchMedia('(max-width: 760px), (max-height: 500px)');
  var onScroll = function (y) {
    var d = y - lastY;
    lastY = y;
    hdr.classList.toggle('scrolled', y > 30);
    /* пока страница едет к блоку по якорю, шапка не прячется (класс hold — раздел «переход к блоку» в конце файла) */
    if (menuOpen || y < 120 || !awayMq.matches || hdr.classList.contains('hold')) { hdr.classList.remove('hide'); run = 0; }
    else if (d) {
      if ((d > 0) !== (run > 0)) run = 0;
      run += d;
      if (run > 48 && y > 400) hdr.classList.add('hide');
      else if (run < -24) hdr.classList.remove('hide');
    }
    var max = document.documentElement.scrollHeight - innerHeight;
    if (prog) prog.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, y / max) : 0) + ')';
    if (mbar) mbar.classList.toggle('show', y > innerHeight * 0.6 && (!cta || cta.getBoundingClientRect().top > innerHeight * 0.5));
  };
  addEventListener('scroll', function () { onScroll(scrollY); }, { passive: true });
  onScroll(scrollY);
  /* телефон повернули или окно стало шире 760 px — шапка снова на месте */
  var awayChange = function () { onScroll(scrollY); };
  if (awayMq.addEventListener) awayMq.addEventListener('change', awayChange); else if (awayMq.addListener) awayMq.addListener(awayChange);
  /* клавиатурный фокус внутри шапки — показать шапку */
  hdr.addEventListener('focusin', function () { hdr.classList.remove('hide'); run = 0; });

  /* ---------- плавающие мессенджеры: если UIS показал свою кнопку в том же углу, поднимаем наши над ней ----------
     Кнопку UIS (блок .comagic-c-buttons, скрытый — с классом comagic-widget--hidden) скрипт UIS добавляет после первого
     действия посетителя и показывает по своему расписанию. Наши кнопки сдвигаются свойством translate, без сдвига вёрстки. */
  var fab = $('.fab');
  if (fab && window.MutationObserver) {
    var uis = null;
    var fitFab = function () {
      var lift = 0;
      if (uis && !uis.classList.contains('comagic-widget--hidden')) {
        var r = uis.getBoundingClientRect(), f = fab.getBoundingClientRect();
        var bottom0 = innerHeight - parseFloat(getComputedStyle(fab).bottom), top0 = bottom0 - f.height;
        if (r.width && r.height && r.height < innerHeight * 0.6 && r.left < f.right && r.right > f.left && r.bottom > top0 - 14 && r.top < bottom0 + 14)
          lift = Math.ceil(bottom0 - r.top + 14);
      }
      fab.style.translate = lift > 0 ? '0 ' + (-lift) + 'px' : '';
    };
    var hookUis = function () {
      var el = $('.comagic-c-buttons');
      if (!el || uis) return;
      findUis.disconnect();
      uis = el;
      new MutationObserver(fitFab).observe(el, { attributes: true, attributeFilter: ['class', 'style'] });
      fitFab(); setTimeout(fitFab, 700);
    };
    var findUis = new MutationObserver(hookUis);
    findUis.observe(document.body, { childList: true, subtree: true });
    hookUis(); /* кнопка UIS могла появиться раньше, чем загрузился этот скрипт */
    addEventListener('resize', fitFab);
  }

  /* активный пункт меню: на главной подсвечиваются якоря шапки (и «Отрасли» у блока отраслей) по мере прокрутки.
     Ссылки на другие страницы не отслеживаются; текущая страница отмечена в HTML (aria-current) */
  var links = $$('.nav > a[href^="#"], .nav [data-spy]');
  var spyId = function (l) { return (l.getAttribute('data-spy') || l.getAttribute('href')).slice(1); };
  /* блок дошёл до середины экрана — подсветить его пункт (остальные погасить); ушёл из середины — погасить его пункт.
     Раньше подсветка гасла только у следующего отслеживаемого блока: «Цена» горела и у вопросов, и у формы (13.11.2026) */
  var so = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      links.forEach(function (l) {
        if (e.isIntersecting) l.classList.toggle('active', spyId(l) === e.target.id);
        else if (spyId(l) === e.target.id) l.classList.remove('active');
      });
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  links.forEach(function (l) { var s = document.getElementById(spyId(l)); if (s) so.observe(s); });
  if (links.length && $('#hero')) so.observe($('#hero'));

  /* ---------- FAQ ---------- */
  var refreshLater = (function () { var t; return function () { clearTimeout(t); t = setTimeout(function () { if (hasGSAP) ScrollTrigger.refresh(); }, 650); }; })();
  $$('.qa button').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var qa = btn.parentElement, open = !qa.classList.contains('open');
      qa.classList.toggle('open', open); btn.setAttribute('aria-expanded', open);
      refreshLater();
    });
  });
  var firstQa = $('.qa');
  if (firstQa) { firstQa.classList.add('open'); $('button', firstQa).setAttribute('aria-expanded', true); }

  /* ---------- форма ---------- */
  var form = $('#form'), ph = $('#phone'), submitBtn = $('#submitBtn');
  if (form && ph && submitBtn) {
  $$('.field').forEach(function (f, i) {
    var err = $('.ferr', f), inp = $('input,select,textarea', f);
    if (err && inp) { err.id = 'err-' + i; inp.setAttribute('aria-describedby', err.id); }
    if (inp) inp.addEventListener('input', function () { f.classList.remove('err'); inp.removeAttribute('aria-invalid'); });
    if (inp && inp.tagName === 'SELECT') inp.addEventListener('change', function () { f.classList.remove('err'); inp.removeAttribute('aria-invalid'); });
  });
  ph.addEventListener('focus', function () { if (!ph.value) ph.value = '+7 ('; });
  ph.addEventListener('blur', function () { if (ph.value.replace(/\D/g, '').length <= 1) ph.value = ''; });
  ph.addEventListener('input', function () {
    var d = ph.value.replace(/\D/g, '');
    if (d[0] === '8') d = '7' + d.slice(1);
    if (d[0] !== '7') d = '7' + d;
    d = d.slice(0, 11);
    var p = d.slice(1), s = '+7';
    if (p.length) s += ' (' + p.slice(0, 3);
    if (p.length >= 3) s += ')';
    if (p.length > 3) s += ' ' + p.slice(3, 6);
    if (p.length > 6) s += '-' + p.slice(6, 8);
    if (p.length > 8) s += '-' + p.slice(8, 10);
    ph.value = s;
  });
  var checks = {
    name: function (v) { return v.trim().length > 1; },
    phone: function (v) { return v.replace(/\D/g, '').length === 11; },
    email: function (v) { return !v.trim() || /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()); },
    type: function (v) { return !!v; }
  };
  /* отправка заявки: один запрос к send.php, цели — только после ответа сервера */
  /* превью на GitHub Pages: заявки никуда не отправляются, форма показывает успешную отправку */
  var DEMO = /\.github\.io$/i.test(location.hostname);
  var sending = false, FAIL_MSG = 'Не удалось отправить заявку. Попробуйте ещё раз или позвоните нам: +7 (495) 104-35-70.';
  /* после отправки — подтверждение на экране (17.11.2026): поля формы скрываются, форма становится короче, и без прокрутки
     «Заявка отправлена» уезжала выше края экрана — на компьютере целиком, посетитель видел только подвал */
  var sentOk = function () {
    form.classList.add('sent');
    refreshLater();
    var ok = $('.ok', form);
    if (!ok) return;
    var r = ok.getBoundingClientRect(), vh = innerHeight, top = (hdr ? hdr.getBoundingClientRect().height : 0) + 16;
    if (r.top < top || r.bottom > vh - 16) {
      var y = Math.max(0, Math.round(pageYOffset + r.top - Math.max(top, (vh - r.height) / 2)));
      if (lenis) lenis.scrollTo(y, { duration: reduce ? 0 : 0.9, immediate: reduce, force: true });
      else window.scrollTo({ top: y, behavior: reduce ? 'auto' : 'smooth' });
    }
    ok.setAttribute('tabindex', '-1');
    try { ok.focus({ preventScroll: true }); } catch (err) { /* старый браузер */ }
  };
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (sending) return;
    var ok = true, first = null;
    Object.keys(checks).forEach(function (n) {
      var el = form.elements[n], f = el.closest('.field'), bad = !checks[n](el.value);
      f.classList.remove('err');
      if (bad) { void f.offsetWidth; f.classList.add('err'); el.setAttribute('aria-invalid', 'true'); ok = false; first = first || el; }
      else el.removeAttribute('aria-invalid');
    });
    if (!ok) { first.focus(); return; }
    sending = true;
    submitBtn.disabled = true;
    submitBtn.classList.add('is-loading');
    if (DEMO) { setTimeout(sentOk, 700); return; }
    /* вид объекта: если подпись пункта отличается от значения для send.php («Медицинская организация» уходит
       как «Другое»), подпись попадает в комментарий заявки — если страница не добавила её сама */
    var fd = new FormData(form), ts = form.elements.type, to = ts && ts.options ? ts.options[ts.selectedIndex] : null;
    if (to && to.value && to.text !== to.value) {
      var mv = String(fd.get('msg') || '');
      if (mv.indexOf('Вид объекта: ') < 0) fd.set('msg', 'Вид объекта: ' + to.text + (mv ? '\n' + mv : ''));
    }
    /* серверная передача в UIS: передаём ID сессии UIS (если нет блокировщика), название формы и страницу */
    var uisSid = '';
    try {
      var cm = window.Comagic;
      if (cm && typeof cm.getSessionId === 'function') uisSid = cm.getSessionId() || '';
      if (!uisSid && cm && typeof cm.getCredentials === 'function') { var cr = cm.getCredentials(); uisSid = cr && cr.session_id ? cr.session_id : ''; }
      if (!/^\d+$/.test(String(uisSid))) uisSid = '';
    } catch (err) { uisSid = ''; }
    var h1 = $('h1'), fn = h1 ? h1.textContent.replace(/\s+/g, ' ').trim().replace(/\s*[.:]$/, '').slice(0, 100) : '';
    var prod = /^(www\.)?xn----itbbsflddbfpfdodg9d0f\.xn--p1ai$/i.test(location.hostname);
    fd.set('uis_session_id', String(uisSid));
    fd.set('form_name', 'Основная форма' + (fn ? ': ' + fn : ''));
    fd.set('page_url', (prod ? 'https://пестконтроль-центр.рф' : location.origin) + location.pathname);
    fetch('/send.php', { method: 'POST', body: fd, headers: { 'Accept': 'application/json' }, credentials: 'same-origin' })
      .then(function (res) {
        return res.text().then(function (txt) {
          var json = null;
          try { json = JSON.parse(txt); } catch (err) { /* ответ не JSON */ }
          if (!res.ok || !json || !json.success) {
            var er = new Error('send failed: ' + res.status);
            er.userMessage = json && json.message ? json.message : '';
            throw er;
          }
          return json;
        });
      })
      .then(function () {
        try { if (typeof ym === 'function') ym(113675622, 'reachGoal', 'audit'); } catch (err) { console.error('Яндекс Метрика:', err); }
        /* заявка в UIS отправляется сервером в send.php — клиентский Comagic.addOfflineRequest убран во избежание дублей */
        sentOk();
      })
      .catch(function (err) {
        console.error('Ошибка отправки формы:', err);
        sending = false;
        submitBtn.disabled = false;
        submitBtn.classList.remove('is-loading');
        alert(err && err.userMessage ? err.userMessage : FAIL_MSG);
      });
  });
  }

  /* ---------- фоновые картинки блоков: грузим при подходе к блоку ---------- */
  var lazyBgs = $$('.pests-bg,.cta-bg');
  if ('IntersectionObserver' in window) {
    var bgIO = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('bg-in'); bgIO.unobserve(e.target); } });
    }, { rootMargin: '150% 0px' });
    lazyBgs.forEach(function (b) { bgIO.observe(b); });
  } else lazyBgs.forEach(function (b) { b.classList.add('bg-in'); });

  /* ---------- бесконечные CSS-анимации блоков вне экрана — на паузу ---------- */
  if ('IntersectionObserver' in window) {
    var offIO = new IntersectionObserver(function (es) {
      es.forEach(function (e) { e.target.classList.toggle('anim-off', !e.isIntersecting); });
    });
    ['#hero', '#zadachi', '#podhod'].forEach(function (id) { var el = $(id); if (el) offIO.observe(el); });
  }

  if (!anim) return; /* дальше — только анимации */

  /* ================================================================ */
  var desk = matchMedia('(min-width: 1025px)').matches;
  var mobile = matchMedia('(max-width: 760px)').matches;

  /* ---------- облегчённый режим для слабых компьютеров (15.11.2026) ----------
     window.pcFx задаёт скрипт в <head> (общий для всех страниц): там же ?fx=lite / ?fx=full / ?fx=auto и решение, уже
     принятое на этом визите (sessionStorage pc-lowfx). Здесь — замер: через 3 с после загрузки 2 с считаются кадры
     (и потом, пока лупа догоняет мышь, — см. лупу ниже и лупу внутренних страниц, tools/site/fx.py). Меньше 40 в секунду
     (середина промежутков между кадрами длиннее 25 мс) — слабый компьютер или браузер без видеоускорения: pcFx.set ставит
     класс lowfx на <html> (style.css выключает лупу, «зерно», сканирующую линию, пульсации, матовое стекло) и вызывает
     pcFx.hooks: без параллакса, наклона и блика панели, нарисованный курсор — обычный. */
  var pcFx = window.pcFx || (window.pcFx = { mode: '', lite: false, hooks: [], set: function () {
    if (pcFx.lite) return;
    pcFx.lite = true;
    html.classList.add('lowfx');
    pcFx.hooks.forEach(function (f) { try { f(); } catch (e) { } });
  } });
  var fxProbe = function () {
    if (pcFx.lite || pcFx.mode === 'full' || pcFx.mode === 'lite') return;
    if (document.hidden) { setTimeout(fxProbe, 2000); return; }
    var ts = [], t0 = 0, hid = false, onVis = function () { hid = true; };
    document.addEventListener('visibilitychange', onVis);
    var step = function (t) {
      if (!t0) t0 = t;
      ts.push(t);
      if (t - t0 < 2000 && !hid) { requestAnimationFrame(step); return; }
      document.removeEventListener('visibilitychange', onVis);
      if (hid || document.hidden) { setTimeout(fxProbe, 2000); return; } /* вкладку прятали — замер не в счёт */
      var d = [];
      for (var i = 1; i < ts.length; i++) d.push(ts[i] - ts[i - 1]);
      d.sort(function (a, b) { return a - b; });
      var med = d.length ? d[d.length >> 1] : 1000;
      html.setAttribute('data-fps', Math.round(1000 / med));
      if (d.length < 20 || med > 25) pcFx.set(true);
    };
    requestAnimationFrame(step);
  };
  if (document.readyState === 'complete') setTimeout(fxProbe, 3000);
  else addEventListener('load', function () { setTimeout(fxProbe, 3000); });
  /* размытие (blur) при появлении — только на компьютерах с мышью: на телефонах и планшетах оно сильно грузит процессор */
  var richFx = fine && !mobile && !pcFx.lite;
  var fx = function (o, px) { if (richFx) o.filter = 'blur(' + px + 'px)'; return o; };

  /* ---------- разбивка текста на слова ---------- */
  function splitWords(el, plain) {
    var walk = function (node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var parts = n.textContent.split(/( +)/), frag = document.createDocumentFragment();
          parts.forEach(function (p) {
            if (!p) return;
            if (/^ +$/.test(p)) { frag.appendChild(document.createTextNode(' ')); return; }
            if (plain) { var s = document.createElement('span'); s.className = 'sw'; s.textContent = p; frag.appendChild(s); }
            else {
              var w = document.createElement('span'); w.className = 'w';
              var wi = document.createElement('span'); wi.className = 'wi'; wi.textContent = p;
              w.appendChild(wi); frag.appendChild(w);
            }
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1) walk(n);
      });
    };
    walk(el);
  }

  /* ---------- отложенная инициализация ----------
     Анимации блоков ниже первого экрана настраиваются отдельными короткими задачами после первого экрана:
     так основной поток не блокируется одной длинной задачей и заставка идёт плавно.
     Пока идёт заставка, прокрутка остановлена, а блоки до настройки скрыты стилями (style.css). */
  var later = [];
  var defer = function (fn) { later.push(fn); };
  var runLater = function () {
    var fn = later.shift();
    if (!fn) return;
    fn();
    if (later.length) setTimeout(runLater, 0);
  };

  /* ---------- курсор ----------
     На светлых объектах (белый план, лист документа, светлая картинка) курсор становится фиолетовым прицелом,
     на ссылке-документе — кругом с подписью (вариант В, выбран владельцем 11.11.2026). Светлый объект — по цвету фона
     ближайшего непрозрачного предка или по средней яркости картинки (считается один раз); вручную — data-cursor="light|dark".
     Кнопки .btn — всегда обычный курсор (при наведении они сами меняют цвет). */
  if (fine && !pcFx.lite) {
    html.classList.add('has-cursor');
    pcFx.hooks.push(function () { html.classList.remove('has-cursor'); }); /* облегчённый режим — обычный курсор */
    var cur = $('.cursor'), dot = $('.cursor-dot'), ring = $('.cursor-ring');
    var lbl = document.createElement('b');
    lbl.className = 'cursor-lbl';
    ring.appendChild(lbl);
    var cx = -100, cy = -100, rx = -100, ry = -100, lastT = null;
    var lightCache = new WeakMap(), imgCache = new WeakMap();
    var lum = function (r, g, b) { return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255; };
    var imgLight = function (im) {
      if (imgCache.has(im)) return imgCache.get(im);
      if (!im.complete || !im.naturalWidth) return false; /* не загрузилась — проверим при следующем наведении */
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
      cx = e.clientX; cy = e.clientY;
      dot.style.transform = 'translate3d(' + cx + 'px,' + cy + 'px,0)';
      var t = e.target;
      cur.classList.remove('hidden');
      if (t === lastT || !t.closest) return;
      lastT = t;
      cur.classList.toggle('link', !!t.closest('a,button,select,label,[role=button]'));
      cur.classList.toggle('text', !!t.closest('input,textarea'));
      var l = lightCache.has(t) ? lightCache.get(t) : isLight(t);
      if (t.tagName !== 'IMG' || imgCache.has(t)) lightCache.set(t, l);
      var d = l ? docLabel(t) : '';
      cur.classList.toggle('light', l);
      cur.classList.toggle('doc', !!d);
      if (d) lbl.textContent = d;
    }, { passive: true });
    addEventListener('scroll', function () { lastT = null; }, { passive: true });
    addEventListener('pointerdown', function () { cur.classList.add('down'); });
    addEventListener('pointerup', function () { cur.classList.remove('down'); });
    document.addEventListener('pointerleave', function () { cur.classList.add('hidden'); lastT = null; });
    gsap.ticker.add(function () {
      rx += (cx - rx) * 0.2; ry += (cy - ry) * 0.2;
      ring.style.transform = 'translate3d(' + rx.toFixed(1) + 'px,' + ry.toFixed(1) + 'px,0)';
    });
  }

  /* ---------- подсветка карточек за курсором ---------- */
  if (fine) {
    document.addEventListener('pointermove', function (e) {
      if (pcFx.lite) return;
      var c = e.target.closest && e.target.closest('.card,.form');
      if (!c) return;
      var r = c.getBoundingClientRect();
      c.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      c.style.setProperty('--my', (e.clientY - r.top) + 'px');
    }, { passive: true });
  }

  /* ---------- магнитные кнопки и наклон карточек ---------- */
  if (fine) {
    $$('[data-magnet]').forEach(function (el) {
      var xTo = gsap.quickTo(el, 'x', { duration: 0.6, ease: 'power3' }), yTo = gsap.quickTo(el, 'y', { duration: 0.6, ease: 'power3' });
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        xTo((e.clientX - r.left - r.width / 2) * 0.22); yTo((e.clientY - r.top - r.height / 2) * 0.35);
      });
      el.addEventListener('pointerleave', function () { xTo(0); yTo(0); });
    });
    $$('[data-tilt]').forEach(function (el) {
      gsap.set(el, { transformPerspective: 1100 });
      var rX = gsap.quickTo(el, 'rotationX', { duration: 0.9, ease: 'power3' }), rY = gsap.quickTo(el, 'rotationY', { duration: 0.9, ease: 'power3' });
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect(), px = (e.clientX - r.left) / r.width - 0.5, py = (e.clientY - r.top) / r.height - 0.5;
        rY(px * 7); rX(-py * 7);
      });
      el.addEventListener('pointerleave', function () { rX(0); rY(0); });
    });
  }

  /* ---------- первый экран: лупа инспектора, параллакс, наклон панели ----------
     Лупа (15.11.2026): светлое фото img/hero-lit.webp в круглой маске только сдвигается (transform) — браузер не
     перерисовывает фото. Кадры считаются, только пока круг догоняет мышь (та же плавность, что раньше); без мыши круг
     стоит на открытой части фото над панелью «Что покажет бесплатный аудит» и сам не ходит. Мышь ушла с первого экрана —
     круг плавно возвращается на место. Телефоны, планшеты и облегчённый режим — без лупы (фото заранее затемнено). */
  var hero = $('#hero'), media = $('#heroMedia'), lens = $('#heroLens'), panel = $('#panel');
  /* первый экран внутренних страниц: .d-hero (услуги, договор, материалы), .p-hero (раздел и журнал), .f-hero (отрасль) */
  var dHero = $('.d-hero') || $('.p-hero') || $('.f-hero'), dMedia = dHero ? $('.d-hero-media, .hero-media', dHero) : null;
  var lensShow = function () { };
  var initLens = function () {
    var img = lens.firstElementChild, src = lens.getAttribute('data-src');
    var W = 0, H = 0, r = 0, x = 0, y = 0, tx = 0, ty = 0, hx = 0, hy = 0;
    var raf = 0, last = 0, visible = true, follow = false, off = false, ready = false, want = false, dts = [];
    var home = function () {
      /* открытая часть фото: над панелью, когда она стоит справа от текста (шире 1280 px), иначе — справа вверху */
      var p = panel, px = 0, py = 0, el = p;
      if (p && matchMedia('(min-width: 1281px)').matches) {
        for (; el && el !== hero; el = el.offsetParent) { px += el.offsetLeft; py += el.offsetTop; }
      }
      if (p && el === hero) {
        var hdr = $('#hdr'), hh = hdr ? hdr.offsetHeight : 0;
        hx = px + p.offsetWidth / 2 - media.offsetLeft;
        hy = (hh + py) / 2 - media.offsetTop;
      } else { hx = W * 0.78; hy = H * 0.22; }
    };
    var apply = function () {
      /* круг и фото внутри — ровно навстречу друг другу: фото стоит на месте до долей пикселя */
      var X = Math.round((x - r) * 10) / 10, Y = Math.round((y - r) * 10) / 10;
      lens.style.transform = 'translate3d(' + X + 'px,' + Y + 'px,0)';
      img.style.transform = 'translate3d(' + -X + 'px,' + -Y + 'px,0)';
    };
    var size = function () {
      if (off) return;
      var cs = getComputedStyle(media); /* точный размер фото (offsetWidth/offsetHeight округляют до целых) */
      W = parseFloat(cs.width) || media.offsetWidth; H = parseFloat(cs.height) || media.offsetHeight;
      r = Math.round(Math.max(240, Math.min(400, innerWidth * 0.21)) * 0.72); /* как раньше: clamp(240px, 21vw, 400px) */
      lens.style.width = lens.style.height = 2 * r + 'px';
      img.style.width = W + 'px'; img.style.height = H + 'px';
      home();
      if (!follow) { tx = hx; ty = hy; if (!raf) { x = hx; y = hy; } }
      apply();
    };
    var tick = function (now) {
      raf = 0;
      if (off || !visible) return;
      var dt = last ? Math.min(Math.max(now - last, 0), 100) : 16.67;
      if (last && pcFx.mode !== 'full') {
        /* страховка и в движении: середина из 40 кадров длиннее 25 мс (меньше 40 кадров в секунду) — облегчённый режим */
        dts.push(now - last);
        if (dts.length >= 40) {
          dts.sort(function (a, b) { return a - b; });
          var med = dts[20]; dts = [];
          if (med > 25) { html.setAttribute('data-fps', Math.round(1000 / med)); pcFx.set(true); return; }
        }
      }
      last = now;
      var k = 1 - Math.pow(0.94, dt / 16.67);
      x += (tx - x) * k; y += (ty - y) * k;
      if (Math.abs(tx - x) < 0.3 && Math.abs(ty - y) < 0.3) { x = tx; y = ty; apply(); return; } /* догнал — кадры не нужны */
      apply();
      raf = requestAnimationFrame(tick);
    };
    var go = function () { if (!raf && !off && visible) { last = 0; raf = requestAnimationFrame(tick); } };
    var reveal = function () { if (ready && want && !off) lens.classList.add('on'); };
    hero.addEventListener('pointermove', function (e) {
      if (e.pointerType !== 'mouse' || off) return;
      var b = media.getBoundingClientRect();
      tx = (e.clientX - b.left) / b.width * W; ty = (e.clientY - b.top) / b.height * H;
      follow = true; go();
    }, { passive: true });
    hero.addEventListener('pointerleave', function () { if (off) return; follow = false; tx = hx; ty = hy; go(); });
    new IntersectionObserver(function (en) { visible = en[0].isIntersecting; if (visible) go(); }).observe(hero);
    if (window.ResizeObserver) new ResizeObserver(function () { size(); }).observe(media);
    addEventListener('resize', size);
    size();
    /* светлое фото — после загрузки страницы, чтобы не мешать первому экрану */
    var loadLit = function () {
      var im = new Image();
      im.onload = function () {
        var set = function () { img.style.backgroundImage = 'url("' + src + '")'; ready = true; reveal(); };
        if (im.decode) im.decode().then(set, set); else set();
      };
      im.src = src;
    };
    if (document.readyState === 'complete') loadLit(); else addEventListener('load', loadLit);
    pcFx.hooks.push(function () { off = true; if (raf) cancelAnimationFrame(raf); raf = 0; lens.classList.remove('on'); });
    return function () { want = true; reveal(); };
  };
  if (lens && media && hero) {
    if (fine && !mobile && !pcFx.lite) lensShow = initLens();
    if (fine && panel) {
      var mX = gsap.quickTo(media, 'x', { duration: 1.4, ease: 'power3' }), mY = gsap.quickTo(media, 'y', { duration: 1.4, ease: 'power3' });
      var pY = gsap.quickTo(panel, 'rotationY', { duration: 1.1, ease: 'power3' }), pX = gsap.quickTo(panel, 'rotationX', { duration: 1.1, ease: 'power3' });
      /* нули — явно: вход панели может ещё идти анимацией браузера (tools/site/hero_in.js), её промежуточное положение
         GSAP не должен принять за исходное */
      gsap.set(panel, { transformPerspective: 1200, x: 0, y: 0, rotationX: 0, rotationY: 0 });
      hero.addEventListener('pointermove', function (e) {
        if (pcFx.lite) return; /* облегчённый режим: без параллакса, наклона и блика панели */
        var px = e.clientX / innerWidth - 0.5, py = e.clientY / innerHeight - 0.5;
        mX(-px * 30); mY(-py * 20); pY(px * 9); pX(-py * 9);
        var r = panel.getBoundingClientRect();
        panel.style.setProperty('--gx', (e.clientX - r.left) + 'px'); panel.style.setProperty('--gy', (e.clientY - r.top) + 'px');
      });
      hero.addEventListener('pointerleave', function () { mX(0); mY(0); pX(0); pY(0); });
      pcFx.hooks.push(function () { mX(0); mY(0); pX(0); pY(0); });
    }
    /* уход первого экрана при прокрутке — только шире 1280 px, где панель «Что покажет бесплатный аудит» стоит рядом
       с текстом и видна целиком сразу. До 1280 px (телефоны, планшеты, небольшие ноутбуки) панель под текстом, её читают
       во время прокрутки — первый экран не гаснет и не уезжает (решение владельца 13.11.2026). При смене ширины окна
       gsap.matchMedia сам снимает и возвращает эффект. */
    gsap.matchMedia().add('(min-width: 1281px)', function () {
      gsap.timeline({ scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true } })
        .to(media, { yPercent: 14, scale: 1.1, ease: 'none' }, 0)
        .to('.hero .wrap', { y: -110, opacity: 0.1, ease: 'none' }, 0);
    });
  } else if (dHero && dMedia) {
    if (fine && desk) {
      var dmX = gsap.quickTo(dMedia, 'x', { duration: 1.4, ease: 'power3' }), dmY = gsap.quickTo(dMedia, 'y', { duration: 1.4, ease: 'power3' });
      dHero.addEventListener('pointermove', function (e) {
        if (pcFx.lite) return; /* облегчённый режим: без параллакса фото */
        var px = e.clientX / innerWidth - 0.5, py = e.clientY / innerHeight - 0.5;
        dmX(-px * 22); dmY(-py * 14);
      });
      dHero.addEventListener('pointerleave', function () { dmX(0); dmY(0); });
      pcFx.hooks.push(function () { dmX(0); dmY(0); });
    }
    if (desk) {
      gsap.timeline({ scrollTrigger: { trigger: dHero, start: 'top top', end: 'bottom top', scrub: true } })
        .to(dMedia, { yPercent: 10, scale: 1.07, ease: 'none' }, 0);
    }
    var fPanel = $('.f-check.panel');
    if (fine && fPanel) {
      fPanel.addEventListener('pointermove', function (e) {
        if (pcFx.lite) return;
        var r = fPanel.getBoundingClientRect();
        fPanel.style.setProperty('--gx', (e.clientX - r.left) + 'px'); fPanel.style.setProperty('--gy', (e.clientY - r.top) + 'px');
      });
    }
  }

  /* вход первого экрана. С 11.11.2026 его рисует встроенный скрипт сразу после разметки первого экрана
     (tools/site/hero_in.js, window.pcHero) — не дожидаясь этого файла, GSAP и счётчиков. Код ниже (heroIn и заставка)
     работает, только если встроенного скрипта нет или он не запустился (старый браузер без element.animate) */
  var pcHero = window.pcHero;
  var heroLines = $$('.hero h1 .ln>span');
  if (heroLines.length && !pcHero) gsap.set(heroLines, { y: 0, yPercent: 110, rotation: 3 });
  /* фото первого экрана — сразу в начальном масштабе входа (до скрипта его держит style.css), чтобы под уходящей
     заставкой оно не дёргалось из 1 в 1.12 */
  var heroImgs = dHero ? $$('.d-hero-img, .f-hero-img', dHero) : [];
  if (pcHero) { /* вход уже идёт или прошёл */ }
  else if (heroImgs.length) gsap.set(heroImgs, { scale: 1.12 });
  else if (hero && $('.hero-bg')) gsap.set('.hero-bg', { scale: 1.18 });
  function heroIn() {
    if (dHero) {
      /* внутренние страницы: тот же почерк, что у главной — строки заголовка поднимаются из-под маски,
         затем по очереди проявляются надзаголовок, отметки, текст и кнопки (элементы с data-h) */
      var dEyebrow = $('.eyebrow', dHero);
      if (dEyebrow) dEyebrow.classList.add('in');
      /* строка под маской (блочная) поднимается снизу; строка, которая на телефоне течёт в тексте (inline), — проявляется */
      var dLines = $$('h1 .ln>span', dHero);
      var tlD = gsap.timeline({ defaults: { ease: 'expo.out' } });
      var dImg = $$('.d-hero-img, .f-hero-img', dHero);
      if (dImg.length) tlD.fromTo(dImg, { scale: 1.12 }, { scale: 1, duration: 2.2, clearProps: 'transform' }, 0);
      dLines.forEach(function (l, i) {
        var at = 0.12 + i * 0.1;
        /* без clearProps: начальное положение строк задано в style.css, итоговое остаётся во встроенном стиле */
        if (getComputedStyle(l.parentNode).display !== 'inline') tlD.fromTo(l, { opacity: 1, y: 0, yPercent: 110, rotation: 3 }, { yPercent: 0, rotation: 0, duration: 1.3 }, at);
        else tlD.fromTo(l, { opacity: 0, y: 22 }, { opacity: 1, y: 0, duration: 1.1 }, at);
      });
      var dH = $$('[data-h]', dHero);
      if (dH.length) tlD.fromTo(dH, fx({ opacity: 0, y: 18 }, 6), fx({ opacity: 1, y: 0, duration: 1, stagger: 0.06, clearProps: 'filter,transform' }, 0), 0.26);
      var dStack = $$('.p-stack > a', dHero);
      if (dStack.length) tlD.fromTo(dStack, fx({ opacity: 0, y: 70 }, 8), fx({ opacity: 1, y: 0, duration: 1.5, stagger: 0.14, clearProps: 'filter,transform' }, 0), 0.3);
      return;
    }
    var tl = gsap.timeline({ defaults: { ease: 'expo.out' } });
    tl.fromTo('.hero-bg', { scale: 1.18 }, { scale: 1, duration: 2.6 }, 0)
      .add(lensShow, 2.65)
      .fromTo('.badge', fx({ opacity: 0, y: 20 }, 8), fx({ opacity: 1, y: 0, duration: 1.1 }, 0), 0.1)
      .to(heroLines, { yPercent: 0, rotation: 0, duration: 1.4, stagger: 0.11 }, 0.15)
      .fromTo('.lead', fx({ opacity: 0, y: 24 }, 8), fx({ opacity: 1, y: 0, duration: 1.2 }, 0), 0.4)
      .fromTo('.hero-ctas', { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 1.1 }, 0.5)
      .fromTo(panel, fx({ opacity: 0, x: 70, rotationY: -14 }, 10), fx({ opacity: 1, x: 0, rotationY: 0, duration: 1.6 }, 0), 0.3)
      .fromTo('.panel li', { opacity: 0, x: 24 }, { opacity: 1, x: 0, duration: 0.9, stagger: 0.08 }, 0.6)
      .fromTo('.scroll-cue', { opacity: 0 }, { opacity: 1, duration: 1 }, 1.1);
  }

  /* ---------- заставка ---------- */
  var intro = $('#intro');
  if (pcHero) {
    /* заставку и вход ведёт встроенный скрипт; здесь — только то, что требует GSAP и Lenis:
       лупа главной появляется после входа фото (2,6 с), плавный скролл ждёт подъёма заставки */
    var litStart = function () {
      if (dHero) return;
      /* лупа — после входа фото (2,6 с), иначе круг не совпадёт с фото, которое ещё уменьшается */
      setTimeout(lensShow, Math.max(0, pcHero.t0 + 2650 - performance.now()));
    };
    if (pcHero.t0 !== null) litStart();
    else document.addEventListener('pc:hero', litStart);
    if (intro && intro.parentNode) {
      if (lenis) lenis.stop();
      document.addEventListener('pc:intro', function () { if (lenis) lenis.start(); });
    }
  } else if (!intro || location.hash || html.classList.contains('no-intro')) {
    if (intro) intro.remove();
    heroIn();
  } else {
    /* логотип, надпись и полоса рисуются CSS-анимацией сразу при загрузке страницы (style.css),
       скрипт дожидается конца рисунка и поднимает заставку */
    if (lenis) lenis.stop();
    var lifted = false;
    var lift = function () {
      if (lifted) return;
      lifted = true;
      gsap.timeline({ onComplete: function () { intro.remove(); if (lenis) lenis.start(); } })
        .to(intro, { clipPath: 'inset(0% 0% 100% 0%)', duration: 0.75, ease: 'expo.inOut' })
        .add(heroIn, 0.3);
    };
    var bar = $('.intro-bar i', intro), barAnims = bar && bar.getAnimations ? bar.getAnimations() : [];
    if (barAnims.length) Promise.all(barAnims.map(function (a) { return a.finished; })).then(lift, lift);
    else setTimeout(lift, 900);
    setTimeout(lift, 1500); /* страховка, если вкладка была в фоне */
  }

  /* ---------- бегущая строка, реагирующая на скорость прокрутки ---------- */
  var track = $('#stripTrack');
  if (track) {
    var set1 = track.firstElementChild, sw = set1.offsetWidth, mx = 0, dir = 1, skew = 0, stripVisible = true;
    addEventListener('resize', function () { sw = set1.offsetWidth; });
    new IntersectionObserver(function (en) { stripVisible = en[0].isIntersecting; }).observe(track.parentElement);
    gsap.ticker.add(function (t, dt) {
      if (!stripVisible) return; /* строка вне экрана — не пересчитываем */
      var v = lenis ? lenis.velocity : 0;
      if (v > 0.4) dir = 1; else if (v < -0.4) dir = -1;
      mx -= (0.7 + Math.min(Math.abs(v) * 0.3, 12)) * dir * (dt / 16.7);
      if (mx <= -sw) mx += sw; if (mx > 0) mx -= sw;
      skew += (Math.max(-7, Math.min(7, -v * 0.4)) - skew) * 0.12;
      track.style.transform = 'translate3d(' + mx.toFixed(2) + 'px,0,0) skewX(' + skew.toFixed(2) + 'deg)';
    });
  }

  /* ---------- надзаголовки, заголовки, подзаголовки ---------- */
  defer(function () {
  /* все надзаголовки страницы (кроме первого экрана — он входит вместе с заголовком) */
  $$('[data-eyebrow], .eyebrow').forEach(function (el) {
    if (el.classList.contains('in') || (dHero && dHero.contains(el)) || (hero && !dHero && hero.contains(el) && !el.hasAttribute('data-eyebrow'))) return;
    ScrollTrigger.create({ trigger: el, start: 'top 90%', once: true, onEnter: function () { el.classList.add('in'); } });
  });
  $$('[data-split]').forEach(function (h) {
    splitWords(h);
    var ws = $$('.wi', h);
    gsap.set(ws, { yPercent: 118, rotation: 5 });
    h.style.visibility = 'visible';
    gsap.to(ws, { yPercent: 0, rotation: 0, duration: 1.25, ease: 'expo.out', stagger: 0.055, scrollTrigger: { trigger: h, start: 'top 88%', once: true } });
  });
  });
  defer(function () {
  /* панели самопроверки и другие .panel вне первого экрана главной проявляются так же, как блоки data-fade */
  $$('.panel').forEach(function (el) { if (el.id !== 'panel' && !el.hasAttribute('data-fade') && !el.closest('[data-group]')) el.setAttribute('data-fade', ''); });
  $$('[data-fade]').forEach(function (el) {
    gsap.fromTo(el, fx({ opacity: 0, y: 34 }, 8), fx({ opacity: 1, y: 0, duration: 1.3, ease: 'expo.out', scrollTrigger: { trigger: el, start: 'top 90%', once: true } }, 0));
  });
  /* на телефоне текст не приглушаем (закон владельца 17.11.2026: на телефоне ничего не затемнять) */
  var noDim = matchMedia('(max-width: 760px)').matches;
  $$('[data-scrub]').forEach(function (p) {
    splitWords(p, true);
    if (noDim) return;
    gsap.fromTo($$('.sw', p), { opacity: 0.14 }, { opacity: 1, stagger: 0.1, ease: 'none', scrollTrigger: { trigger: p, start: 'top 86%', end: 'bottom 52%', scrub: 0.6 } });
  });
  });

  /* ---------- группы карточек ---------- */
  var group = function (name) { return $$('[data-group="' + name + '"]'); };
  var onceST = function (trigger, fn, start) { ScrollTrigger.create({ trigger: trigger, start: start || 'top 85%', once: true, onEnter: fn }); };

  defer(function () {
  group('tasks').forEach(function (g) {
    var items = $$(':scope>*', g);
    gsap.set(items, { transformPerspective: 1200, transformOrigin: '50% 0%' });
    onceST(g, function () {
      gsap.fromTo(items, { opacity: 0, y: 90, rotationX: -28 }, { opacity: 1, y: 0, rotationX: 0, duration: 1.5, ease: 'expo.out', stagger: 0.13 });
    });
  });

  group('pests').forEach(function (g) {
    $$(':scope>*', g).forEach(function (card, i) {
      onceST(card, function () {
        var d = (i % 2) * 0.1;
        gsap.fromTo(card, { opacity: 0, y: 60, scale: 0.97 }, { opacity: 1, y: 0, scale: 1, duration: 1.3, ease: 'expo.out', delay: d });
        var pImg = $('.pest-img img', card);
        if (pImg) gsap.fromTo(pImg, { scale: 1.45, filter: 'grayscale(1) brightness(.6)' }, { scale: 1, filter: 'grayscale(0) brightness(1)', duration: 1.6, ease: 'expo.out', delay: d + 0.1, clearProps: 'filter' });
        var b = $('.bar-f', card);
        if (b) gsap.fromTo(b, { width: '0%' }, { width: b.dataset.w + '%', duration: 1.8, ease: 'expo.out', delay: d + 0.35 });
        setTimeout(function () { card.classList.add('scanned'); }, (d + 0.3) * 1000);
      }, 'top 88%');
    });
  });

  group('steps').forEach(function (g) {
    onceST(g, function () {
      gsap.fromTo($$(':scope>*', g), { opacity: 0, x: -50 }, { opacity: 1, x: 0, duration: 1.2, ease: 'expo.out', stagger: 0.1, clearProps: 'transform' });
    });
  });

  group('inds').forEach(function (g) {
    $$(':scope>*', g).forEach(function (card, i) {
      var img = $('.ind-img', card), pic = $('img', img);
      onceST(card, function () {
        var d = (i % (desk ? 3 : 2)) * 0.12;
        gsap.fromTo(card, { opacity: 0, y: 70 }, { opacity: 1, y: 0, duration: 1.4, ease: 'expo.out', delay: d });
        gsap.fromTo(img, { clipPath: 'inset(0% 0% 100% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.5, ease: 'expo.inOut', delay: d + 0.05 });
        gsap.fromTo(pic, { scale: 1.35 }, { scale: 1, duration: 2, ease: 'expo.out', delay: d + 0.05 });
      }, 'top 90%');
    });
  });

  group('docs').forEach(function (g) {
    var items = $$(':scope>*', g);
    onceST(g, function () {
      gsap.fromTo(items, { opacity: 0, y: 110, scale: 0.9, rotation: function (i) { return [-6, 3, 7, -4, 5, -7][i % 6]; } },
        { opacity: 1, y: 0, scale: 1, rotation: 0, duration: 1.4, ease: 'expo.out', stagger: 0.08 });
    }, 'top 82%');
  });

  group('kpis').forEach(function (g) {
    var items = $$(':scope>*', g);
    onceST(g, function () {
      gsap.fromTo(items, { opacity: 0, y: 50 }, { opacity: 1, y: 0, duration: 1.2, ease: 'expo.out', stagger: 0.1 });
      items.forEach(function (k, i) {
        setTimeout(function () { k.classList.add('lit'); }, 200 + i * 160);
        var b = $('b[data-count]', k);
        if (!b) return;
        var to = +b.dataset.count, suf = b.dataset.suf || '', o = { v: 0 };
        if (!to) return;
        gsap.to(o, { v: to, duration: 1.8, ease: 'expo.out', delay: 0.15 + i * 0.1, onUpdate: function () { b.textContent = Math.round(o.v) + suf; } });
      });
    });
  });

  group('cases').forEach(function (g) {
    $$(':scope>*', g).forEach(function (card, i) {
      var img = $('.case-img', card), pic = $('img', img);
      onceST(card, function () {
        var d = i * 0.12;
        gsap.fromTo(card, { opacity: 0, y: 70 }, { opacity: 1, y: 0, duration: 1.4, ease: 'expo.out', delay: d });
        gsap.fromTo(img, { clipPath: 'inset(0% 0% 100% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.5, ease: 'expo.inOut', delay: d });
        gsap.fromTo(pic, { scale: 1.3 }, { scale: 1, duration: 2, ease: 'expo.out', delay: d });
        gsap.fromTo($$('.case-k>div', card), { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 1, ease: 'expo.out', stagger: 0.1, delay: d + 0.6 });
      }, 'top 88%');
    });
  });

  /* универсальная группа карточек внутренних страниц: подъём с задержкой по колонкам; фото в карточке раскрывается шторкой */
  group('cards').forEach(function (g) {
    var items = $$(':scope>*', g), cols = Math.max(1, Math.round(g.offsetWidth / Math.max(1, items[0] ? items[0].offsetWidth : 1)));
    items.forEach(function (card, i) {
      if (card.hasAttribute('data-hin')) return; /* уже проявлена встроенным скриптом первого экрана (tools/site/hero_in.js) */
      var box = $('.ind-img, .d-obj-img, .d-kind-img, .d-swap-img, .pm-img, [data-reveal]', card), pic = box ? $('img', box) : null;
      onceST(card, function () {
        var d = (i % cols) * 0.1;
        gsap.fromTo(card, { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 1.3, ease: 'expo.out', delay: d, clearProps: 'transform' });
        if (box) gsap.fromTo(box, { clipPath: 'inset(0% 0% 100% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.4, ease: 'expo.inOut', delay: d + 0.05 });
        if (pic) gsap.fromTo(pic, { scale: 1.3 }, { scale: 1, duration: 1.9, ease: 'expo.out', delay: d + 0.05, clearProps: 'transform' });
      }, 'top 90%');
    });
  });
  /* строки сравнений и таблиц: выезжают слева по очереди */
  group('rows').forEach(function (g) {
    onceST(g, function () {
      gsap.fromTo($$(':scope>*', g), { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 1, ease: 'expo.out', stagger: 0.06, clearProps: 'transform' });
    }, 'top 88%');
  });
  /* фото отраслей вне блока «Отрасли» (карточки на внутренних страницах) — та же шторка, что и на главной */
  $$('.ind-img').forEach(function (box) {
    if (box.closest('[data-group="inds"]') || box.closest('[data-group="cards"]')) return;
    var pic = $('img', box);
    onceST(box, function () {
      gsap.fromTo(box, { clipPath: 'inset(0% 0% 100% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.5, ease: 'expo.inOut' });
      if (pic) gsap.fromTo(pic, { scale: 1.3 }, { scale: 1, duration: 2, ease: 'expo.out' });
    }, 'top 92%');
  });

  group('faq').forEach(function (g) {
    var items = $$(':scope>*', g);
    onceST(g, function () {
      gsap.fromTo(items, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 1.1, ease: 'expo.out', stagger: 0.08, clearProps: 'transform' });
    }, 'top 88%');
  });

  group('ctalist').forEach(function (g) {
    onceST(g, function () {
      gsap.fromTo($$(':scope>*', g), { opacity: 0, x: -24 }, { opacity: 1, x: 0, duration: 1, ease: 'expo.out', stagger: 0.1 });
    }, 'top 90%');
  });

  var formEl = $('[data-form]');
  if (formEl) onceST(formEl, function () {
    gsap.fromTo(formEl, fx({ opacity: 0, y: 70, rotationY: desk ? -10 : 0, transformPerspective: 1400 }, 12),
      fx({ opacity: 1, y: 0, rotationY: 0, duration: 1.6, ease: 'expo.out', clearProps: 'filter' }, 0));
    gsap.fromTo($$('.field', formEl), { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.9, ease: 'expo.out', stagger: 0.06, delay: 0.35, clearProps: 'transform' });
  }, 'top 88%');
  });

  /* ---------- параллакс изображений и фонов ---------- */
  defer(function () {
  $$('img[data-parallax]').forEach(function (img) {
    // фото с людьми (data-fp, tools/site/focal.js) — меньший ход ±3,5 %, чтобы голова не уходила за край (11.11.2026)
    var a = img.hasAttribute('data-fp') ? 3.5 : 6;
    gsap.fromTo(img, { yPercent: -a }, { yPercent: a, ease: 'none', scrollTrigger: { trigger: img.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } });
  });
  $$('[data-parallax-bg]').forEach(function (bg) {
    gsap.fromTo(bg, { yPercent: -8 }, { yPercent: 8, ease: 'none', scrollTrigger: { trigger: bg.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } });
  });
  });

  /* ---------- подход: цикл IPM управляется прокруткой ---------- */
  defer(function () {
  var steps = $$('.step'), nodes = $$('.node'), cProg = $('#cycleProg'), cArc = $('#cycleArc'), cLbl = $('#cycleStep'), curStep = -1;
  if (cLbl && cProg && cArc) {
    var setOn = function (i) {
      if (i === curStep) return; curStep = i;
      steps.forEach(function (s, j) { s.classList.toggle('on', j === i); });
      nodes.forEach(function (n, j) { n.classList.toggle('on', j === i); });
      cLbl.textContent = '0' + (i + 1) + ' / 04';
      gsap.fromTo(cLbl, { opacity: 0, y: 6 }, { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out' });
    };
    setOn(0);
    ScrollTrigger.create({
      trigger: desk ? '#podhod' : '#cycle', start: desk ? 'top 55%' : 'top 85%', end: desk ? 'bottom 75%' : 'bottom 30%', scrub: true,
      onUpdate: function (s) {
        var p = s.progress;
        cProg.style.strokeDashoffset = (100 - p * 100).toFixed(2);
        cArc.style.transform = 'rotate(' + (p * 540).toFixed(1) + 'deg)';
        if (desk) setOn(Math.min(3, Math.floor(p * 4)));
      }
    });
    if (!desk) {
      steps.forEach(function (s, i) {
        ScrollTrigger.create({ trigger: s, start: 'top 62%', end: 'bottom 62%', onToggle: function (st) { if (st.isActive) setOn(i); } });
      });
      var auto = null;
      ScrollTrigger.create({ trigger: '#cycle', start: 'top 80%', end: 'bottom 20%',
        onToggle: function (st) { clearInterval(auto); if (st.isActive) auto = setInterval(function () { setOn((curStep + 1) % 4); }, 1800); } });
    }
    steps.forEach(function (s, i) { s.addEventListener('pointerenter', function () { if (fine) setOn(i); }); });
  }

  /* ---------- этапы: линия, точки, раскрытие фото ---------- */
  var tlHead = $('#tlhead');
  if (tlHead && $('#tlprog')) {
    gsap.to('#tlprog', { scaleY: 1, ease: 'none', scrollTrigger: { trigger: '#tl', start: 'top 62%', end: 'bottom 62%', scrub: 0.5,
      onUpdate: function (s) { tlHead.style.top = (s.progress * 100).toFixed(2) + '%'; tlHead.style.opacity = s.progress > 0 && s.progress < 1 ? 1 : 0; } } });
    $$('.tl-row').forEach(function (row) {
      var flip = row.classList.contains('flip'), txt = $('.tl-txt', row), box = $('.tl-img', row), pic = $('img', box);
      var from = mobile ? 'inset(0% 0% 100% 0%)' : (flip ? 'inset(0% 0% 0% 100%)' : 'inset(0% 100% 0% 0%)');
      onceST(row, function () {
        row.classList.add('in');
        gsap.fromTo(txt, fx({ opacity: 0, x: mobile ? 0 : (flip ? 50 : -50), y: mobile ? 24 : 0 }, 8), fx({ opacity: 1, x: 0, y: 0, duration: 1.3, ease: 'expo.out', clearProps: 'filter' }, 0));
        gsap.fromTo(box, { clipPath: from }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.6, ease: 'expo.inOut' });
        gsap.fromTo(pic, { scale: 1.3 }, { scale: 1, duration: 2.2, ease: 'expo.out' });
      }, 'top 72%');
    });
  }

  /* ---------- заявка: свечение следует за курсором ---------- */
  var orb = $('#orb');
  if (orb && cta) {
    gsap.set(orb, { xPercent: -50, yPercent: -50, x: cta.offsetWidth * 0.5, y: cta.offsetHeight * 0.5 });
    if (fine) {
      var oX = gsap.quickTo(orb, 'x', { duration: 2.2, ease: 'power3' }), oY = gsap.quickTo(orb, 'y', { duration: 2.2, ease: 'power3' });
      cta.addEventListener('pointermove', function (e) { var r = cta.getBoundingClientRect(); oX(e.clientX - r.left); oY(e.clientY - r.top); });
      cta.addEventListener('pointerleave', function () { oX(cta.offsetWidth * 0.5); oY(cta.offsetHeight * 0.5); });
    } else {
      var orbTw = gsap.to(orb, { x: '+=' + Math.round(innerWidth * 0.15), y: '-=80', duration: 6, ease: 'sine.inOut', yoyo: true, repeat: -1, paused: true });
      ScrollTrigger.create({ trigger: cta, start: 'top bottom', end: 'bottom top', onToggle: function (st) { if (st.isActive) orbTw.play(); else orbTw.pause(); } });
    }
  }

  /* ---------- подвал ---------- */
  if ($('.ft>div')) gsap.fromTo('.ft>div', { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 1.1, ease: 'expo.out', stagger: 0.08, scrollTrigger: { trigger: 'footer', start: 'top 92%', once: true } });

  /* пересчёт после загрузки шрифтов и изображений (если они уже загрузились — сразу) */
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { ScrollTrigger.refresh(); });
  if (document.readyState === 'complete') ScrollTrigger.refresh();
  else addEventListener('load', function () { ScrollTrigger.refresh(); });
  });

  setTimeout(runLater, 0);
})();

/* ---------- переход к блоку по якорю: начало блока — сразу под шапкой (13.11.2026) ----------
   Запрос владельца 13.11.2026: пункт меню открывал блок не с заголовка — над ним оставалось пустое тёмное поле.
   Было: щелчок по ссылке на этой же странице ставил верх раздела на 176 px от верха окна (scroll-padding-top 96 px
   и поправка Lenis 80 px), переход с другой страницы — на 96 px, и к этому добавлялся собственный верхний отступ
   раздела (80–130 px). Подпись над заголовком стояла на 278 px от верха окна (компьютер 1440) и 241–257 px
   (телефон 390), шапка при прокрутке вниз уезжала — сверху оставалось пустое поле.
   Стало: у раздела (section) под шапку встаёт начало его содержимого — подпись над заголовком (на политике и
   согласии — заголовок раздела); у карточки, строки таблицы, заголовка — их верх. От верха окна — высота шапки и ещё
   20…32 px (так же scroll-padding-top и scroll-margin-top разделов в style.css и legal.css, чтобы браузер до запуска
   скриптов ставил страницу туда же). Пока страница едет к блоку, шапка не прячется: класс hold у #hdr читает раздел
   «шапка, прогресс…» выше; первое колесо, касание или клавиша посетителя возвращают обычное поведение шапки.
   - Щелчок по ссылке на этой же странице — window.pcAnchor.go (его вызывает раздел «якоря» выше): Lenis за 0,8 с
     (до 17.11.2026 — за 1,5 с), в конце — сверка положения; без Lenis — плавная прокрутка браузера, при «уменьшении
     движения» — сразу.
   - Шапка на месте прихода — компактная (style.css: --hdr-c и линия 1 px, 17.11.2026); в первых 30 px страницы —
     в полный рост (clamp(68px, 6vw, 115px) и линия 1 px).
   - Переход по ссылке с якорем с другой страницы (/#tseny, ../#podhod, ../#etapy, ../#vrediteli, ../#voprosy):
     браузер сразу ставит страницу на блок (style.css: html:has(:target) — без плавной прокрутки), а здесь положение
     держится, пока страница догружается: после загрузки страницы и шрифтов, после каждого пересчёта ScrollTrigger
     и при сдвиге прокрутки не посетителем — до первого действия посетителя (колесо, касание, клавиша, нажатие)
     и не дольше 2,5 с после загрузки. При «Назад» и обновлении страницы браузер сам возвращает прежнее место —
     тогда раздел ничего не делает.
   В app.min.js рабочего сайта этот раздел заменяет прежний «переход по ссылке с якорем с другой страницы»
   (tools/deploy/prepare-2026-11-13-zagolovok.py). */
(function () {
  var w = window, d = document, root = d.documentElement, hdr = d.getElementById('hdr'), holdT = 0, seq = 0;
  /* блок на месте прибытия — сразу целиком (17.11.2026): анимации появления, которые запустились по дороге, доводятся до
     конца. Раньше после «Бесплатный аудит» поля заявки 1,5–2 с были невидимы, после пункта меню карточки блока
     проявлялись уже на месте. Только одиночные анимации верхнего уровня на экране: циклы, анимации от прокрутки (scrub)
     и шкалы времени (вход первого экрана, заставка) не трогаются */
  var finish = function () {
    var g = w.gsap;
    if (!g || !g.globalTimeline) return;
    var vh = w.innerHeight;
    g.globalTimeline.getChildren(false, true, false).forEach(function (tw) {
      if (tw.progress() >= 1 || tw.repeat() || (tw.scrollTrigger && tw.scrollTrigger.vars && tw.scrollTrigger.vars.scrub)) return;
      var near = tw.targets().some(function (el) {
        if (!el || !el.getBoundingClientRect) return false;
        var r = el.getBoundingClientRect();
        return r.bottom > 0 && r.top < vh;
      });
      if (near) tw.progress(1);
    });
  };
  /* высота шапки с линией 1 px: компактной (после 30 px прокрутки, style.css: --hdr-c) или в полный рост */
  var hdrH = function (compact) {
    if (!hdr) return 0;
    var c = parseFloat(getComputedStyle(root).getPropertyValue('--hdr-c'));
    if (compact && c) return c + 1;
    return Math.min(115, Math.max(68, w.innerWidth * 0.06)) + 1;
  };
  /* куда прокрутить страницу, чтобы начало блока t встало сразу под шапкой. У раздела (section) начало — верх первого
     дочернего блока в потоке (.wrap с подписью и заголовком; у разделов политики — заголовок с его отступом сверху),
     фон и украшения (position: absolute) не в счёт; у карточки, строки таблицы, заголовка — их верх */
  var anchorY = function (t) {
    var top = t.getBoundingClientRect().top;
    if (t.tagName === 'SECTION') {
      var s = getComputedStyle(t), c = t.firstElementChild, k, r;
      top += (parseFloat(s.borderTopWidth) || 0) + (parseFloat(s.paddingTop) || 0);
      for (; c; c = c.nextElementSibling) {
        k = getComputedStyle(c).position; r = c.getBoundingClientRect();
        if (k !== 'absolute' && k !== 'fixed' && r.height) { top = r.top; break; }
      }
    }
    var gap = Math.min(32, Math.max(20, w.innerWidth * 0.022)), abs = top + w.pageYOffset;
    var y = abs - hdrH(true) - gap;
    if (y <= 30) y = abs - hdrH(false) - gap; /* у самого начала страницы шапка в полный рост */
    return Math.max(0, Math.min(Math.round(y), root.scrollHeight - w.innerHeight));
  };
  /* шапка не прячется, пока страница едет к блоку (ms — страховка: снять удержание не позже) */
  var hold = function (on, ms) {
    clearTimeout(holdT);
    if (!hdr) return;
    hdr.classList.toggle('hold', on);
    if (on) { hdr.classList.remove('hide'); if (ms) holdT = setTimeout(function () { hold(false); }, ms); }
  };
  var jump = function (y, smooth) {
    try { w.scrollTo({ top: y, left: 0, behavior: smooth ? 'smooth' : 'instant' }); } catch (e) { w.scrollTo(0, y); }
  };
  ['wheel', 'touchstart', 'keydown'].forEach(function (n) {
    w.addEventListener(n, function () { if (hdr && hdr.classList.contains('hold')) hold(false); }, { passive: true, capture: true });
  });
  var ease = function (k) { return 1 - Math.pow(1 - k, 4); };
  var go = function (t, isTop, lenis, reduce) {
    if (isTop) { if (lenis) lenis.scrollTo(0, { duration: 0.8, easing: ease }); else jump(0, !reduce); return; }
    var my = ++seq, fin = false;
    hold(true, 3000);
    var end = function () { /* сверка в конце: картинки и шрифты могли сдвинуть блок за время прокрутки */
      if (fin || my !== seq) return;
      fin = true;
      var y = anchorY(t);
      if (Math.abs(w.pageYOffset - y) >= 2) { if (lenis) lenis.scrollTo(y, { immediate: true }); else jump(y, false); }
      finish();
      setTimeout(finish, 300); /* анимации, запущенные сверкой положения и пересчётом ScrollTrigger */
      setTimeout(function () { if (my === seq) hold(false); }, 150);
    };
    if (lenis) { lenis.scrollTo(anchorY(t), { duration: 0.8, easing: ease, onComplete: end }); return; }
    jump(anchorY(t), !reduce);
    if (!reduce && 'onscrollend' in w) w.addEventListener('scrollend', end, { once: true });
    setTimeout(end, reduce ? 60 : 1600);
  };
  w.pcAnchor = { y: anchorY, go: go };

  /* переход по ссылке с якорем с другой страницы */
  var h = w.location.hash, t = null;
  if (!h || h.length < 2 || h === '#top') return;
  var nav = w.performance && performance.getEntriesByType ? performance.getEntriesByType('navigation')[0] : null;
  if (nav && nav.type && nav.type !== 'navigate') return;
  try { t = d.getElementById(decodeURIComponent(h.slice(1))); } catch (e) { t = null; }
  if (!t) return;
  var done = false, ST = w.ScrollTrigger && ScrollTrigger.addEventListener ? ScrollTrigger : null;
  var land = function () {
    if (done) return;
    var r = t.getBoundingClientRect();
    if (!r.width && !r.height) return; /* блок скрыт */
    var y = anchorY(t);
    if (Math.abs(w.pageYOffset - y) >= 2) jump(y, false);
  };
  var stop = function () {
    if (done) return;
    done = true;
    w.removeEventListener('scroll', land);
    hold(false);
  };
  ['wheel', 'touchstart', 'keydown', 'mousedown', 'pointerdown'].forEach(function (n) { w.addEventListener(n, stop, { passive: true, capture: true }); });
  var settle = function () {
    land();
    [300, 1000, 2000].forEach(function (ms) { setTimeout(land, ms); });
    [300, 1000].forEach(function (ms) { setTimeout(function () { if (!done) finish(); }, ms); }); /* блок — сразу целиком */
    setTimeout(stop, 2500);
  };
  hold(true);
  land();
  w.addEventListener('scroll', land, { passive: true });
  if (d.readyState === 'complete') settle(); else w.addEventListener('load', settle);
  if (d.fonts && d.fonts.ready) d.fonts.ready.then(land);
  if (ST) ST.addEventListener('refresh', land);
})();
