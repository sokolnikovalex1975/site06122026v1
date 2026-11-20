#!/usr/bin/env python3
"""Кнопки заявки на странице «Разработка ППК» (/razrabotka-ppk/) — без обещания выезда (20.11.2026).

Замечание владельца 20.11.2026: в шапке страницы ППК стоит «Бесплатный выезд», но ППК разрабатываем дистанционно —
после получения заполненного опросного листа. «Бесплатный выезд» относится только к работам, где нужно участие
специалистов на объекте (аудит или предварительный осмотр). Решение владельца: «Делай первый вариант».

Три точные замены (ссылка #zayavka, классы и цели Метрики не меняются — только текст):
  1. кнопка в шапке (от 761 px):      «Бесплатный выезд»                  → «Рассчитать ППК»;
  2. кнопка мобильного меню:           «Заказать бесплатное обследование»  → «Рассчитать стоимость ППК»;
  3. нижняя панель телефона (#mbar):   «Обследование»                      → «Рассчитать ППК».
Те же слова, что у главной кнопки первого экрана («Рассчитать стоимость ППК») и кнопок карточек цен («Рассчитать ППК»).

    python3 tools/site/ppk_knopka.py      → применяет к razrabotka-ppk/index.html (повторный запуск ничего не меняет)

Сборка страницы (tools/razrabotka-ppk/build_page.py) вызывает fix() сама; tools/menu/apply_menu.py сохраняет
кнопку мобильного меню такой, какая она в странице.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
PAGE = ROOT / 'razrabotka-ppk' / 'index.html'

REPL = [
    ('<a href="#zayavka" class="btn btn-w btn-sm" data-magnet><span class="btn-t">Бесплатный выезд</span></a>',
     '<a href="#zayavka" class="btn btn-w btn-sm" data-magnet><span class="btn-t">Рассчитать ППК</span></a>'),
    ('<a href="#zayavka" class="btn btn-w btn-lg"><span class="btn-t">Заказать бесплатное обследование</span></a>',
     '<a href="#zayavka" class="btn btn-w btn-lg"><span class="btn-t">Рассчитать стоимость ППК</span></a>'),
    ('<a href="#zayavka" class="c2"><span>Обследование</span></a>',
     '<a href="#zayavka" class="c2"><span>Рассчитать ППК</span></a>'),
]


def fix(s):
    """Возвращает страницу с новыми подписями; уже исправленную страницу не меняет."""
    for old, new in REPL:
        if new in s and old not in s:
            continue
        assert s.count(old) == 1, 'ppk_knopka: «%s» найдено %d раз' % (old[:70], s.count(old))
        s = s.replace(old, new)
    return s


if __name__ == '__main__':
    old = PAGE.read_text(encoding='utf-8')
    new = fix(old)
    assert fix(new) == new
    if new != old:
        PAGE.write_text(new, encoding='utf-8')
    print('ppk_knopka:', 'изменено' if new != old else 'без изменений', PAGE.relative_to(ROOT))
