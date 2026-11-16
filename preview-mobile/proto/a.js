/* Прототип варианта A «Точечные исправления» */
(function () {
  if (!matchMedia('(max-width:760px)').matches) return;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* Схема: нажали зону на плане — описание зоны выезжает прямо под план */
  $$('#shema .hz-pan').forEach(function (p) {
    p.addEventListener('click', function (e) {
      var g = e.target.closest('.f-plan [data-z]'); if (!g) return;
      var li = $('.hz-zl li[data-z="' + g.getAttribute('data-z') + '"]', p); if (!li) return;
      setTimeout(function () {
        var plan = $('.f-plan', p).getBoundingClientRect(), r = li.getBoundingClientRect(), bottom = innerHeight - 96;
        /* при прокрутке вверх шапка появляется и план опускается под неё (top 76 px) — считаем от этого места */
        var d = r.top < plan.bottom + 8 ? r.top - (76 + plan.height) - 12 : (r.bottom > bottom ? r.bottom - bottom + 12 : 0);
        if (d) window.scrollBy({ top: d, behavior: 'smooth' });
      }, 30);
    });
  });

  /* Метод IPM: без самостоятельного вращения — круг показывает тот шаг, который читают */
  if (window.ScrollTrigger) ScrollTrigger.getAll().forEach(function (st) { if (st.trigger && st.trigger.id === 'cycle') st.kill(); });
  for (var k = 1; k < 3000; k++) clearInterval(k); /* только для прототипа: снять автопрокрутку круга */
  var steps = $$('#podhod .step'), prog = $('#cycleProg');
  var mo = new MutationObserver(function () {
    var i = steps.findIndex(function (s) { return s.classList.contains('on'); });
    if (prog && i >= 0) prog.style.strokeDashoffset = (100 - (i + 1) * 25).toFixed(2);
  });
  steps.forEach(function (s) { mo.observe(s, { attributes: true, attributeFilter: ['class'] }); });
  if (window.ScrollTrigger) ScrollTrigger.refresh();
})();
