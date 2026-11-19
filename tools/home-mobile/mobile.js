/* Главная на телефоне (до 760 px), решение владельца 19.11.2026: отрасли — лента со свайпом и счётчиком, подвал —
   разделы раскрываются по нажатию (вариант B). Только главная: <script id="hm-js"> ставит tools/home-mobile/build.py.
   Ссылки и тексты остаются в разметке страницы; на компьютере скрипт ничего не делает. */
(function () {
  var mq = window.matchMedia && matchMedia('(max-width:760px)');
  if (!mq || !mq.matches) return;
  var d = document;
  var $ = function (s, r) { return (r || d).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); };
  var ARR = function (p) { return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="' + p + '"/></svg>'; };

  /* Отрасли: лента карточек — свайп, счётчик «1 / 6», точки и стрелки */
  var track = $('#otrasli .inds');
  if (track) {
    var items = $$('#otrasli .inds>.ind');
    if (items.length > 1) {
      track.classList.add('hm-track');
      track.setAttribute('tabindex', '-1');
      var nav = d.createElement('div');
      nav.className = 'hm-nav';
      nav.innerHTML = '<span class="hm-count" aria-live="polite"><b>1</b> / ' + items.length + '</span>' +
        '<span class="hm-dots" aria-hidden="true">' + items.map(function (_, i) { return '<i' + (i ? '' : ' class="on"') + '></i>'; }).join('') + '</span>' +
        '<span class="hm-arr"><button type="button" aria-label="Предыдущая отрасль" disabled>' + ARR('M15 18l-6-6 6-6') + '</button>' +
        '<button type="button" aria-label="Следующая отрасль">' + ARR('M9 18l6-6-6-6') + '</button></span>';
      track.parentNode.insertBefore(nav, track.nextSibling);
      var cur = 0, btn = $$('button', nav), dots = $$('.hm-dots i', nav), num = $('.hm-count b', nav);
      var go = function (i) {
        i = Math.max(0, Math.min(items.length - 1, i));
        var it = items[i];
        track.scrollTo({ left: it.offsetLeft - (track.clientWidth - it.offsetWidth) / 2, behavior: 'smooth' });
      };
      var upd = function () {
        var c = track.scrollLeft + track.clientWidth / 2, best = 0, bd = 1e9;
        items.forEach(function (it, i) { var x = Math.abs(it.offsetLeft + it.offsetWidth / 2 - c); if (x < bd) { bd = x; best = i; } });
        if (best === cur) return;
        cur = best;
        num.textContent = best + 1;
        dots.forEach(function (o, i) { o.classList.toggle('on', i === best); });
        btn[0].disabled = best === 0; btn[1].disabled = best === items.length - 1;
      };
      var raf = 0;
      track.addEventListener('scroll', function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(upd); }, { passive: true });
      btn[0].addEventListener('click', function () { go(cur - 1); });
      btn[1].addEventListener('click', function () { go(cur + 1); });
      /* фокус клавиатуры на ссылке карточки — лента встаёт на эту карточку */
      items.forEach(function (it, i) { it.addEventListener('focusin', function () { if (i !== cur) go(i); }); });
    }
  }

  /* Подвал: колонки со ссылками — раскрывающиеся разделы; контакты всегда открыты */
  $$('footer .ft>div').forEach(function (col, n) {
    var h = $('h4', col), ul = $('ul', col);
    if (!h || !ul || /Контакты/.test(h.textContent)) return;
    var id = 'hm-ft-' + n;
    ul.id = ul.id || id;
    col.classList.add('hm-acc');
    var b = d.createElement('button');
    b.type = 'button'; b.className = 'hm-acc-b';
    b.setAttribute('aria-expanded', 'false'); b.setAttribute('aria-controls', ul.id);
    b.textContent = h.textContent;
    h.textContent = ''; h.appendChild(b);
    b.addEventListener('click', function () {
      var o = col.classList.toggle('open');
      b.setAttribute('aria-expanded', o ? 'true' : 'false');
      if (window.ScrollTrigger) ScrollTrigger.refresh();
    });
  });
})();
