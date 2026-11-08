/* Тестовая страница: никакой отправки, cookie-трекинга и записи в local/sessionStorage. */
(function () {
  'use strict';
  var toggle = document.getElementById('preview-notes');
  toggle.addEventListener('click', function () {
    var show = toggle.getAttribute('aria-pressed') !== 'true';
    toggle.setAttribute('aria-pressed', String(show));
    toggle.textContent = show ? 'Скрыть изменения' : 'Показать изменения';
    document.body.classList.toggle('show-review-notes', show);
  });

  var form = document.getElementById('form');
  var result = document.getElementById('preview-form-result');
  var reset = document.getElementById('preview-reset');
  var consent = form.elements.consent;
  var validators = {
    name: function (s) { return s.trim().length > 1; },
    phone: function (s) { return /^7\d{10}$/.test(s.replace(/\D/g, '')); },
    email: function (s) { return !s.trim() || /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(s.trim()); },
    type: function (s) { return !!s; }
  };
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    var first = null;
    Object.keys(validators).forEach(function (key) {
      var input = form.elements[key];
      var bad = !validators[key](input.value);
      input.closest('.field').classList.toggle('err', bad);
      input.setAttribute('aria-invalid', String(bad));
      if (bad && !first) first = input;
    });
    consent.closest('.consent').classList.toggle('invalid', !consent.checked);
    consent.setAttribute('aria-invalid', String(!consent.checked));
    result.classList.remove('ok');
    if (first) {
      result.textContent = 'Проверьте имя, телефон и тип объекта. Заполненные поля остаются только в этой вкладке.';
      first.focus();
      return;
    }
    if (!consent.checked) {
      result.textContent = 'Подтвердите отдельное согласие на обработку данных.';
      consent.focus();
      return;
    }
    result.classList.add('ok');
    result.textContent = 'Поля заполнены корректно.\nЭто тестовая версия: заявка никуда не отправлена, данные не сохранены.';
    reset.hidden = false;
    result.focus();
  }, true);
  form.querySelector('[data-preview-fields]').disabled = false;
  reset.addEventListener('click', function () {
    form.reset();
    form.querySelectorAll('.err').forEach(function (el) { el.classList.remove('err'); });
    form.querySelectorAll('[aria-invalid]').forEach(function (el) { el.removeAttribute('aria-invalid'); });
    consent.closest('.consent').classList.remove('invalid');
    result.textContent = '';
    result.classList.remove('ok');
    reset.hidden = true;
    form.elements.name.focus();
  });

  var fab = document.querySelector('.fab');
  if (fab) {
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'preview-msg-toggle';
    button.setAttribute('aria-expanded', 'false');
    button.setAttribute('aria-label', 'Показать мессенджеры');
    button.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8v.5Z"/></svg>';
    fab.appendChild(button);
    button.addEventListener('click', function () {
      var open = !fab.classList.contains('is-open');
      fab.classList.toggle('is-open', open);
      button.setAttribute('aria-expanded', String(open));
      button.setAttribute('aria-label', open ? 'Скрыть мессенджеры' : 'Показать мессенджеры');
    });
    new IntersectionObserver(function (entries) {
      document.body.classList.toggle('preview-at-form', entries[0].isIntersecting);
    }, { threshold: .05 }).observe(form);
  }
})();
