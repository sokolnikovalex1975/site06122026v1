/* Только проверка полей во вложенном приложении. Сетевых запросов и хранения нет. */
(function () {
  var form = document.getElementById('form');
  var fields = form.querySelector('[data-proof-fields]');
  fields.disabled = false;
  var checks = {
    name: function (v) { return v.trim().length > 1; },
    phone: function (v) { return /^7\d{10}$/.test(v.replace(/\D/g, '')); },
    type: function (v) { return !!v; }
  };
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var first = null;
    Object.keys(checks).forEach(function (key) {
      var field = form.elements[key], bad = !checks[key](field.value);
      field.closest('.field').classList.toggle('err', bad);
      if (bad) { field.setAttribute('aria-invalid', 'true'); first = first || field; }
      else field.removeAttribute('aria-invalid');
    });
    if (first) { first.focus(); return; }
    form.classList.add('sent');
    form.querySelector('.ok h3').textContent = 'Проверка заполнения завершена';
    form.querySelector('.ok p').textContent = 'Это тестовая версия. Заявка никуда не отправлена, данные не сохранены.';
  }, true);
})();
