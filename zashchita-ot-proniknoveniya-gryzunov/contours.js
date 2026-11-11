const figure = document.getElementById('proof-contours');
if (figure) {
  const drawing = figure.querySelector('.proof-drawing');
  const controls = [...figure.querySelectorAll('[data-contour-button]')];
  const status = document.getElementById('proof-contour-status');
  const labels = {
    '0': 'Показаны все три контура',
    '1': 'Контур 1: территория и подходы к зданию',
    '2': 'Контур 2: оболочка и уязвимые узлы здания',
    '3': 'Контур 3: внутренние помещения и связи между зонами'
  };
  const select = value => {
    if (!drawing || !Object.prototype.hasOwnProperty.call(labels, value)) return;
    drawing.dataset.contour = value;
    controls.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.contourButton === value)));
    if (status) status.textContent = labels[value];
  };
  controls.forEach(button => {
    button.disabled = false;
    button.addEventListener('click', () => select(button.dataset.contourButton));
  });
  const reset = figure.querySelector('[data-contour-button="0"]');
  if (reset) reset.hidden = false;
  const hint = document.getElementById('proof-contour-hint');
  if (hint) hint.textContent = 'Выберите контур в списке. Часть кровли и стены условно снята, чтобы показать внутренние зоны.';
  select('0');
}
