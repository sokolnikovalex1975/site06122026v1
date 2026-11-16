/* Прототип варианта C: второстепенные блоки свёрнуты в раздел «Подробнее о работе» (раскрываются на месте) */
(function () {
  if (!matchMedia('(max-width:760px)').matches) return;
  var main = document.querySelector('main'); if (!main) return;
  var h = document.createElement('div');
  h.className = 'mc-fold-h';
  h.innerHTML = '<div class="wrap"><div class="eyebrow in">Подробнее о работе</div><p>Метод IPM, документы, вредители, типовые задачи и все услуги — раскройте нужный раздел.</p></div>';
  main.appendChild(h);
  ['podhod', 'dokumenty', 'vrediteli', 'usloviya', 'vse-uslugi'].forEach(function (id) {
    var s = document.getElementById(id); if (!s) return;
    var h2 = s.querySelector('h2'); if (!h2) return;
    var fh = h2.closest('.vu-head') || h2.closest('.head') || h2.parentElement;
    s.classList.add('mc-fold');
    fh.classList.add('mc-fh');
    fh.setAttribute('role', 'button'); fh.setAttribute('tabindex', '0'); fh.setAttribute('aria-expanded', 'false');
    fh.addEventListener('click', function () {
      var o = s.classList.toggle('open'); fh.setAttribute('aria-expanded', o);
      if (window.ScrollTrigger) ScrollTrigger.refresh();
    });
  });
  if (window.ScrollTrigger) ScrollTrigger.refresh();
})();
