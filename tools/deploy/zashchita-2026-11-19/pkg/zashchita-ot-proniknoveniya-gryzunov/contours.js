const figure = document.getElementById('proof-contours');
if (figure) {
  const drawing = figure.querySelector('.proof-drawing');
  const controls = [...figure.querySelectorAll('[data-contour-button]')];
  const list = figure.querySelector('.proof-contour-list');
  const status = document.getElementById('proof-contour-status');
  const fine = window.matchMedia('(hover:hover) and (pointer:fine)');
  const labels = {
    '0': 'Показаны все три контура',
    '1': 'Контур 1: территория и подходы к зданию',
    '2': 'Контур 2: оболочка и уязвимые узлы здания',
    '3': 'Контур 3: внутренние помещения и связи между зонами'
  };
  // Закреплённый выбор (нажатие) и временный просмотр (наведение или фокус) разделены:
  // курсор, ушедший со списка, возвращает схему к закреплённому контуру.
  let pinned = '0', enterTimer = 0, leaveTimer = 0;
  const render = value => {
    if (!drawing || !Object.prototype.hasOwnProperty.call(labels, value)) return;
    if (drawing.dataset.contour === value) return;
    drawing.dataset.contour = value;
    controls.forEach(button => button.classList.toggle('is-preview', button.dataset.contourButton === value && value !== pinned));
  };
  const pin = value => {
    if (!Object.prototype.hasOwnProperty.call(labels, value)) return;
    clearTimeout(enterTimer); clearTimeout(leaveTimer);
    pinned = value;
    controls.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.contourButton === value)));
    drawing.dataset.contour = '';
    render(value);
    if (status) status.textContent = labels[value];
  };
  // Короткая пауза отсекает случайный пролёт курсора над списком, но остаётся заметно меньше 0,4 с.
  const preview = value => {
    clearTimeout(leaveTimer); clearTimeout(enterTimer);
    enterTimer = setTimeout(() => render(value), 90);
  };
  const restore = delay => {
    clearTimeout(enterTimer); clearTimeout(leaveTimer);
    leaveTimer = setTimeout(() => render(pinned), delay);
  };
  controls.forEach(button => {
    const value = button.dataset.contourButton;
    button.disabled = false;
    button.addEventListener('click', () => pin(value));
    button.addEventListener('pointerenter', event => { if (event.pointerType === 'mouse' && fine.matches) preview(value); });
    button.addEventListener('focus', () => { if (button.matches(':focus-visible')) { clearTimeout(leaveTimer); render(value); } });
    button.addEventListener('blur', () => restore(150));
  });
  if (list) list.addEventListener('pointerleave', event => { if (event.pointerType === 'mouse') restore(250); });
  const reset = figure.querySelector('[data-contour-button="0"]');
  if (reset) reset.hidden = false;
  const hint = document.getElementById('proof-contour-hint');
  if (hint) hint.textContent = fine.matches
    ? 'Наведите курсор на контур в списке — схема подсветит его, нажатие закрепит выбор. Часть кровли и стены условно снята.'
    : 'Выберите контур в списке. Часть кровли и стены условно снята, чтобы показать внутренние зоны.';
  pin('0');
}
