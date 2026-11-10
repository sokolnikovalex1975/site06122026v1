/* На GitHub Pages и локально не отправляем заявки и не вызываем производственные интеграции. */
(function () {
  if (/^(www\.)?xn----itbbsflddbfpfdodg9d0f\.xn--p1ai$/i.test(location.hostname)) return;
  var originalFetch = window.fetch;
  window.fetch = function (url) {
    if (typeof url === 'string' && url.indexOf('send.php') > -1) {
      return Promise.resolve(new Response('{"success":true}', {
        status: 200, headers: {'Content-Type': 'application/json'}
      }));
    }
    return originalFetch.apply(this, arguments);
  };
  document.addEventListener('DOMContentLoaded', function () {
    var hint = document.querySelector('.form .fs');
    if (hint) hint.textContent = 'Предпросмотр: заявка никуда не отправляется';
  });
})();

/* Самопроверка отмечает выполненные действия, но не диагностирует объект. */
document.addEventListener('change', function (event) {
  if (!event.target.closest('.f-check-list')) return;
  var inputs = document.querySelectorAll('.f-check-list input');
  var n = Array.prototype.filter.call(inputs, function (input) { return input.checked; }).length;
  document.getElementById('chk-n').textContent = n;
  document.querySelector('.f-check-res').classList.toggle('full', n === inputs.length);
  document.getElementById('chk-note').textContent = n === inputs.length
    ? 'Все проверки отмечены. Это не подтверждение непроницаемости здания: специалист уточнит состояние и доступность участков.'
    : 'Отмечено ' + n + ' из ' + inputs.length + '. Список поможет обсудить обследование; неотмеченные пункты не означают, что на объекте есть грызуны.';
});

/* Схема полей и общий обработчик app.min.js сохранены. Меняется только тема заявки. */
(function () {
  var form = document.getElementById('form');
  if (!form) return;
  form.addEventListener('submit', function () {
    var fields = form.elements;
    fields.msg.value = 'Задача: ' + (fields.service.value || 'Защита от проникновения грызунов')
      + '\nАдрес объекта: ' + (fields.address.value.trim() || 'не указан')
      + '\nСтраница: Защита от проникновения грызунов (/zashchita-ot-proniknoveniya-gryzunov/)';
  });
})();
