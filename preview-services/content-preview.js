/* Демонстрация нового контента. Ни отправки, ни счётчиков, ни постоянного хранения. */
(function () {
  'use strict';
  var notes = document.getElementById('content-notes');
  notes.addEventListener('click', function () {
    var show = notes.getAttribute('aria-pressed') !== 'true';
    notes.setAttribute('aria-pressed', String(show));
    notes.textContent = show ? 'Скрыть отметки' : 'Показать новое';
    document.body.classList.toggle('show-content-notes', show);
  });
  var form = document.getElementById('form');
  var result = document.getElementById('content-form-result');
  var reset = document.getElementById('content-form-reset');
  var checks = {
    name: function (v) { return v.trim().length > 1; },
    phone: function (v) { return /^7\d{10}$/.test(v.replace(/\D/g, '')); },
    email: function (v) { return !v.trim() || /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()); },
    type: function (v) { return !!v; }
  };
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    e.stopImmediatePropagation();
    var first = null;
    Object.keys(checks).forEach(function (key) {
      var input = form.elements[key], bad = !checks[key](input.value);
      input.closest('.field').classList.toggle('err', bad);
      input.setAttribute('aria-invalid', String(bad));
      if (bad && !first) first = input;
    });
    result.classList.remove('is-valid');
    if (first) {
      result.textContent = 'Проверьте отмеченные поля. Обязательны имя, телефон и тип объекта.';
      first.focus();
      return;
    }
    result.classList.add('is-valid');
    result.textContent = 'Поля заполнены корректно.\nЭто тестовая версия: заявка никуда не отправлена, данные не сохранены.';
    reset.hidden = false;
    result.focus();
  }, true);
  form.querySelector('[data-content-fields]').disabled = false;
  reset.addEventListener('click', function () {
    form.reset();
    form.querySelectorAll('.err').forEach(function (el) { el.classList.remove('err'); });
    form.querySelectorAll('[aria-invalid]').forEach(function (el) { el.removeAttribute('aria-invalid'); });
    result.textContent = '';
    result.classList.remove('is-valid');
    reset.hidden = true;
    form.elements.name.focus();
  });
  new IntersectionObserver(function (entries) {
    document.body.classList.toggle('content-at-form', entries[0].isIntersecting);
  }, { threshold: .03 }).observe(form);
  new IntersectionObserver(function (entries) {
    document.body.classList.toggle('content-at-services', entries[0].isIntersecting);
  }, { threshold: .01 }).observe(document.getElementById('all-services'));
})();
