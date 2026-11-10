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
    if (lenis) lenis.scrollTo(isTop ? 0 : target, { offset: isTop ? 0 : -80, duration: 1.5, easing: function (t) { return 1 - Math.pow(1 - t, 4); } });
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

  /* ---------- шапка, прогресс, мобильная панель ---------- */
  var prog = $('#progress'), mbar = $('#mbar'), cta = $('#zayavka'), lastY = 0;
  var onScroll = function (y) {
    hdr.classList.toggle('scrolled', y > 30);
    if (!menuOpen) {
      if (y > lastY + 4 && y > 500) hdr.classList.add('hide');
      else if (y < lastY - 4 || y < 200) hdr.classList.remove('hide');
    }
    lastY = y;
    var max = document.documentElement.scrollHeight - innerHeight;
    if (prog) prog.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, y / max) : 0) + ')';
    if (mbar) mbar.classList.toggle('show', y > innerHeight * 0.6 && (!cta || cta.getBoundingClientRect().top > innerHeight * 0.5));
  };
  addEventListener('scroll', function () { onScroll(scrollY); }, { passive: true });
  onScroll(scrollY);
  /* клавиатурный фокус внутри шапки — показать шапку */
  hdr.addEventListener('focusin', function () { hdr.classList.remove('hide'); });

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
  var so = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (e.isIntersecting) links.forEach(function (l) { l.classList.toggle('active', spyId(l) === e.target.id); });
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
  /* Отправка намеренно отсутствует: preview.js выполняет только локальную проверку. */

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

})();
