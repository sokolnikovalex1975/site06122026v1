/* Вход первого экрана — сразу после его разметки, не дожидаясь GSAP, app.min.js и счётчиков (с 11.11.2026).
   Встраивается на каждую страницу сразу после </section> первого экрана (id="hero") шагом tools/site/hero_in.py.

   Зачем: счётчики (Метрика, UIS, Radist) по закону владельца грузятся сразу вместе со страницей и делят сеть
   и процессор со скриптами анимаций. Пока вход первого экрана запускал app.js (GSAP), текст первого экрана
   на телефоне появлялся на 1–4 с позже (LCP 3,5–4,1 с). Теперь тот же рисунок входа рисует Web Animations API
   браузера, а app.js видит window.pcHero и первый экран не трогает. Счётчики этот скрипт не трогает.

   Рисунок тот же, что был в app.js (heroIn): строки заголовка поднимаются из-под маски (на телефоне строка, которая
   течёт в тексте, проявляется), затем по очереди проявляются надзаголовок, элементы data-h, стопка листов, фото
   уменьшается из 1.12 в 1; на главной — заставка поднимается после рисунка логотипа, затем бейдж, строки, текст,
   кнопки, панель аудита и её пункты. Размытие при появлении — только на компьютерах с мышью (как в app.js).

   Начальные состояния (скрыто) по-прежнему задаёт style.css; класс hero-in на <html> снимает их, а каждое появление —
   анимация с fill: 'backwards' (до своего старта держит начальное состояние). Появления начинаются с непрозрачности
   0,01 (глазом не отличить от 0) — так LCP отмечается при отрисовке, а не в конце появления. При заставке появления
   создаются сразу и стоят на паузе в начальном кадре; через 0,3 с после начала подъёма заставки они запускаются. Без element.animate, при
   prefers-reduced-motion и после страховки anim-fail скрипт ничего не делает — тогда, как раньше, работает app.js. */
(function (d, w) {
  var html = d.documentElement;
  if (!html.classList.contains('js') || html.classList.contains('anim-fail') || !html.animate ||
      w.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return [].slice.call((c || d).querySelectorAll(s)); };
  var hero = $('#hero'), dHero = $('.d-hero') || $('.p-hero') || $('.f-hero');
  if (!hero) return;
  var fine = w.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var richFx = fine && !w.matchMedia('(max-width: 760px)').matches;
  var OUT = 'cubic-bezier(.19,1,.22,1)', IN_OUT = 'cubic-bezier(.87,0,.13,1)'; /* expo.out и expo.inOut GSAP */
  /* появления начинаются с непрозрачности 0,01, а не 0: глазом разницы нет, но браузер считает элемент отрисованным
     сразу и отмечает LCP в момент отрисовки (у анимации из 0 — только в её конце, на 1–1,5 с позже) */
  var O = 0.01;
  var st = w.pcHero = { t0: null }; /* t0 — начало входа (performance.now()), его ждёт app.js для «фонаря» главной */

  /* все появления создаются сразу и копятся в anims: при заставке они стоят на паузе в начальном кадре до её подъёма */
  var anims = [];
  function go(el, from, to, dur, at) {
    if (el) anims.push(el.animate([from, to], { duration: dur * 1000, delay: at * 1000, easing: OUT, fill: 'backwards' }));
  }
  function fx(o, px) { if (richFx) o.filter = 'blur(' + px + 'px)'; return o; }
  function fire(name) { var e = d.createEvent('Event'); e.initEvent(name, false, false); d.dispatchEvent(e); }

  var prepared = false, eyebrow = dHero && $('.eyebrow', dHero);
  function prep() { /* создать все появления первого экрана (в начальном кадре) */
    if (prepared) return;
    prepared = true;
    html.classList.add('hero-in');
    if (dHero) {
      $$('.d-hero-img, .f-hero-img', dHero).forEach(function (im) {
        go(im, { transform: 'scale(1.12)' }, { transform: 'scale(1)' }, 2.2, 0);
      });
      $$('h1 .ln>span', dHero).forEach(function (l, i) {
        var at = 0.12 + i * 0.1;
        if (getComputedStyle(l.parentNode).display !== 'inline') {
          go(l, { transform: 'translate(0,110%) rotate(3deg)' }, { transform: 'translate(0,0) rotate(0deg)' }, 1.3, at);
        } else {
          go(l, { opacity: O, transform: 'translate(0,22px)' }, { opacity: 1, transform: 'translate(0,0)' }, 1.1, at);
        }
      });
      $$('[data-h]', dHero).forEach(function (el, i) {
        go(el, fx({ opacity: O, transform: 'translate(0,18px)' }, 6), fx({ opacity: 1, transform: 'translate(0,0)' }, 0), 1, 0.26 + i * 0.06);
      });
      /* у листов в стопке свой поворот в style.css — сдвигаем отдельным свойством translate, поворот не трогаем */
      $$('.p-stack > a', dHero).forEach(function (el, i) {
        go(el, fx({ opacity: O, translate: '0 70px' }, 8), fx({ opacity: 1, translate: '0 0' }, 0), 1.5, 0.3 + i * 0.14);
      });
    } else {
      $$('.hero-bg, .hero-lit', hero).forEach(function (el) {
        go(el, { transform: 'scale(1.18)' }, { transform: 'scale(1)' }, 2.6, 0);
      });
      go($('.badge', hero), fx({ opacity: O, transform: 'translate(0,20px)' }, 8), fx({ opacity: 1, transform: 'translate(0,0)' }, 0), 1.1, 0.1);
      $$('h1 .ln>span', hero).forEach(function (l, i) {
        go(l, { transform: 'translate(0,110%) rotate(3deg)' }, { transform: 'translate(0,0) rotate(0deg)' }, 1.4, 0.15 + i * 0.11);
      });
      go($('.lead', hero), fx({ opacity: O, transform: 'translate(0,24px)' }, 8), fx({ opacity: 1, transform: 'translate(0,0)' }, 0), 1.2, 0.4);
      go($('.hero-ctas', hero), { opacity: O, transform: 'translate(0,24px)' }, { opacity: 1, transform: 'translate(0,0)' }, 1.1, 0.5);
      var panel = $('#panel');
      if (panel) {
        var p = fine ? 'perspective(1200px) ' : ''; /* как gsap.set(panel, {transformPerspective: 1200}) в app.js */
        go(panel, fx({ opacity: O, transform: p + 'translate(70px,0) rotateY(-14deg)' }, 10),
          fx({ opacity: 1, transform: p + 'translate(0,0) rotateY(0deg)' }, 0), 1.6, 0.3);
        $$('li', panel).forEach(function (li, i) {
          go(li, { opacity: O, transform: 'translate(24px,0)' }, { opacity: 1, transform: 'translate(0,0)' }, 0.9, 0.6 + i * 0.08);
        });
      }
      go($('.scroll-cue', hero), { opacity: O }, { opacity: 1 }, 1, 1.1);
    }
  }
  /* карточки [data-group="cards"] внутри первого экрана (хаб «Материалы»), которые видны сразу (верх выше 90% высоты
     окна, как start: 'top 90%' в app.js): проявляются сразу, тем же рисунком, что в app.js (непрозрачность и подъём на
     60 px, 1,3 с, сдвиг 0,1 с по колонкам), не дожидаясь GSAP. Отмечаются data-hin — app.js их пропускает.
     Карточки с фото и карточки ниже — как раньше, через app.js при прокрутке. */
  function cardsIn() {
    if (!dHero) return;
    var vh = w.innerHeight || html.clientHeight;
    $$('[data-group="cards"]', dHero).forEach(function (g) {
      var items = [].slice.call(g.children);
      if (!items.length) return;
      var cols = Math.max(1, Math.round(g.offsetWidth / Math.max(1, items[0].offsetWidth)));
      items.forEach(function (card, i) {
        if (card.getBoundingClientRect().top > vh * 0.9) return;
        if ($('.ind-img, .d-obj-img, .d-kind-img, .d-swap-img, .pm-img, [data-reveal]', card)) return;
        card.setAttribute('data-hin', '');
        card.animate([{ opacity: O, transform: 'translate(0,60px)' }, { opacity: 1, transform: 'translate(0,0)' }],
          { duration: 1300, delay: (i % cols) * 100, easing: OUT, fill: 'backwards' });
      });
    });
  }
  function heroIn() { /* запустить вход первого экрана */
    if (st.t0 !== null) return;
    prep();
    st.t0 = w.performance.now();
    if (eyebrow) eyebrow.classList.add('in');
    anims.forEach(function (a) { if (a.playState === 'paused') a.play(); });
    fire('pc:hero');
  }

  /* заставка главной: логотип, надпись и полоса рисуются CSS сразу; после рисунка заставка поднимается,
     через 0,3 с начинается вход первого экрана; после подъёма заставка удаляется (app.js включает плавный скролл) */
  var intro = $('#intro');
  if (!intro || w.location.hash || html.classList.contains('no-intro')) {
    if (intro) intro.parentNode.removeChild(intro);
    heroIn();
    cardsIn();
    return;
  }
  /* пока рисуется заставка, первый экран под ней уже стоит в начальном кадре входа (появления на паузе);
     карточки проявляются сразу — как раньше, когда app.js успевал их показать ещё под заставкой */
  prep();
  anims.forEach(function (a) { a.pause(); });
  cardsIn();
  var lifted = false;
  var lift = function () {
    if (lifted) return;
    lifted = true;
    var an = intro.animate([{ clipPath: 'inset(0% 0% 0% 0%)' }, { clipPath: 'inset(0% 0% 100% 0%)' }],
      { duration: 750, easing: IN_OUT, fill: 'forwards' });
    var done = function () {
      if (!intro.parentNode) return;
      intro.parentNode.removeChild(intro);
      st.introDone = true;
      fire('pc:intro');
    };
    an.onfinish = done;
    setTimeout(heroIn, 300);
    setTimeout(done, 2500); /* страховка, если вкладка была в фоне */
  };
  var bar = $('.intro-bar i', intro), barAnims = bar && bar.getAnimations ? bar.getAnimations() : [];
  if (barAnims.length) Promise.all(barAnims.map(function (a) { return a.finished; })).then(lift, lift);
  else setTimeout(lift, 900);
  setTimeout(lift, 1500); /* страховка, если вкладка была в фоне */
})(document, window);
