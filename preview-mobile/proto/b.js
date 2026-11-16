/* Прототип варианта B «Мобильная перекомпоновка» */
(function () {
  if (!matchMedia('(max-width:760px)').matches) return;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var ARR = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>';
  var ARR2 = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>';

  /* Лента карточек: свайп, счётчик, точки, стрелки. onChange(i) — когда в центре новая карточка */
  function strip(track, onChange, itemSel) {
    if (!track) return null;
    var items = Array.prototype.slice.call(track.children).filter(function (x) { return !itemSel || x.matches(itemSel); });
    track.classList.add('mc-track');
    var nav = document.createElement('div');
    nav.className = 'mc-nav';
    nav.innerHTML = '<span class="mc-count"><b>1</b> / ' + items.length + '</span>' +
      '<span class="mc-dots">' + items.map(function (_, i) { return '<i' + (i ? '' : ' class="on"') + '></i>'; }).join('') + '</span>' +
      '<span class="mc-arr"><button type="button" aria-label="Назад" disabled>' + ARR + '</button><button type="button" aria-label="Дальше">' + ARR2 + '</button></span>';
    track.after(nav);
    var cur = 0, b = $$('button', nav);
    function go(i, smooth) {
      i = Math.max(0, Math.min(items.length - 1, i));
      var it = items[i];
      track.scrollTo({ left: it.offsetLeft - (track.clientWidth - it.offsetWidth) / 2, behavior: smooth === false ? 'auto' : 'smooth' });
    }
    function upd() {
      var c = track.scrollLeft + track.clientWidth / 2, best = 0, bd = 1e9;
      items.forEach(function (it, i) { var d = Math.abs(it.offsetLeft + it.offsetWidth / 2 - c); if (d < bd) { bd = d; best = i; } });
      if (best === cur) return;
      cur = best;
      $('b', nav).textContent = best + 1;
      $$('.mc-dots i', nav).forEach(function (d, i) { d.classList.toggle('on', i === best); });
      b[0].disabled = best === 0; b[1].disabled = best === items.length - 1;
      if (onChange) onChange(best, items[best]);
    }
    track.addEventListener('scroll', function () { cancelAnimationFrame(track._mc); track._mc = requestAnimationFrame(upd); }, { passive: true });
    b[0].addEventListener('click', function () { go(cur - 1); });
    b[1].addEventListener('click', function () { go(cur + 1); });
    return { go: go, items: items, nav: nav, get cur() { return cur; } };
  }

  /* После нажатия: если карточка с результатом ушла под нижнюю панель — чуть докручиваем страницу,
     но так, чтобы то, на что нажали (план, круг), осталось на экране */
  function reveal(box, keep) {
    setTimeout(function () {
      var r = box.getBoundingClientRect(), k = keep.getBoundingClientRect(), lim = innerHeight - 84;
      if (r.bottom <= lim) return;
      var d = Math.min(r.bottom - lim + 8, k.top - 12);
      if (d > 0) window.scrollBy({ top: d, behavior: 'smooth' });
    }, 60);
  }

  /* Ситуации, отрасли, типовые задачи — ленты */
  strip($('#zadachi .tasks'));
  strip($('#otrasli .inds'));
  strip($('#usloviya .cases'));
  strip($('#etapy #tl'), null, '.tl-row');

  /* Схема объекта: свайп по карточкам зон ↔ подсветка зоны на плане */
  $$('#shema .hz-pan').forEach(function (p) {
    var ol = $('.hz-zl', p);
    var lg = $('.f-legend', p); if (lg) p.appendChild(lg); /* условные обозначения — под карточкой зоны */
    var setZone = function (z) {
      $$('.f-plan [data-z]', p).forEach(function (g) { g.classList.toggle('on', g.getAttribute('data-z') === z); });
      $$('.hz-zl li', p).forEach(function (l) { l.classList.toggle('on', l.getAttribute('data-z') === z); });
    };
    var s = strip(ol, function (i, li) { setZone(li.getAttribute('data-z')); });
    if (s) ol.before(s.nav); /* счётчик и стрелки — между планом и карточкой, всегда на экране */
    p.addEventListener('click', function (e) {
      var g = e.target.closest('.f-plan [data-z]'), li = e.target.closest('.hz-zl li');
      var z = g ? g.getAttribute('data-z') : li ? li.getAttribute('data-z') : null;
      if (!z || !s) return;
      var i = s.items.findIndex(function (x) { return x.getAttribute('data-z') === z; });
      if (i >= 0) s.go(i);
      if (g) reveal(ol, $('.f-plan', p));
    });
  });
  /* при смене типа объекта лента новой схемы встаёт на первую зону */
  $$('#shema .hz-tab').forEach(function (t) {
    t.addEventListener('click', function () {
      var p = document.getElementById('hz-p-' + t.dataset.o), ol = p && $('.hz-zl', p);
      if (ol) setTimeout(function () { ol.scrollLeft = 0; }, 0);
    });
  });

  /* Метод IPM: шаги — лента под кругом; свайп или нажатие на узел круга меняет шаг, круг всегда на экране */
  var steps = $('#podhod .steps'), nodes = $$('#cycle .node'), lbl = $('#cycleStep'), prog = $('#cycleProg');
  if (steps && nodes.length) {
    if (window.ScrollTrigger) ScrollTrigger.getAll().forEach(function (st) {
      var t = st.trigger;
      if (t && (t.id === 'cycle' || (t.classList && t.classList.contains('step')))) st.kill();
    });
    for (var k = 1; k < 3000; k++) clearInterval(k); /* только для прототипа: снять автопрокрутку круга */
    var setStep = function (i) {
      $$('.step', steps).forEach(function (s, j) { s.classList.toggle('on', j === i); });
      nodes.forEach(function (n, j) { n.classList.toggle('on', j === i); });
      if (lbl) lbl.textContent = '0' + (i + 1) + ' / 04';
      if (prog) prog.style.strokeDashoffset = (100 - (i + 1) * 25).toFixed(2);
    };
    var ss = strip(steps, function (i) { setStep(i); });
    setStep(0);
    nodes.forEach(function (n, i) { n.addEventListener('click', function () { ss.go(i); reveal(steps, $('#cycle')); }); });
  }

  /* Вредители: подробности раскрываются в той же карточке */
  $$('#vrediteli .pest').forEach(function (c) {
    var pm = document.createElement('span'); pm.className = 'mc-pm'; pm.setAttribute('aria-hidden', 'true');
    c.appendChild(pm);
    c.setAttribute('role', 'button'); c.setAttribute('tabindex', '0'); c.setAttribute('aria-expanded', 'false');
    c.addEventListener('click', function () { var o = c.classList.toggle('open'); c.setAttribute('aria-expanded', o); });
  });

  /* Все услуги: группы раскрываются по нажатию */
  $$('#vse-uslugi .vu-g').forEach(function (g) {
    var t = $('.vu-gt', g); if (!t) return;
    t.setAttribute('role', 'button'); t.setAttribute('tabindex', '0');
    t.addEventListener('click', function () { g.classList.toggle('open'); });
  });

  if (window.ScrollTrigger) ScrollTrigger.refresh();
})();
