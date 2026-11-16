/* Прототип: общие мобильные правки (варианты A и B) */
(function () {
  if (!matchMedia('(max-width:760px)').matches) return;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };


  /* Вопросы: первые 5 видны, остальные — по кнопке */
  var qs = $$('#voprosy .qa');
  if (qs.length > 5) {
    qs.slice(5).forEach(function (q) { q.classList.add('mc-hide'); });
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'mc-more-btn';
    b.textContent = 'Показать все вопросы (' + qs.length + ')';
    b.addEventListener('click', function () { qs.forEach(function (q) { q.classList.remove('mc-hide'); }); b.remove(); });
    $('#voprosy .faq').after(b);
  }

  /* Подвал: колонки со ссылками — раскрывающиеся списки */
  $$('footer .ft>div').forEach(function (d) {
    var h = $('h4', d), ul = $('ul', d);
    if (!h || !ul || /Контакты/.test(h.textContent)) return;
    d.classList.add('mc-acc');
    h.setAttribute('role', 'button'); h.setAttribute('tabindex', '0'); h.setAttribute('aria-expanded', 'false');
    h.addEventListener('click', function () { var o = d.classList.toggle('open'); h.setAttribute('aria-expanded', o); });
  });
})();
