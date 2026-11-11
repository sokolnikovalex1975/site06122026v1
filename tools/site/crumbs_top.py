#!/usr/bin/env python3
"""Хлебные крошки первого экрана на компьютере и планшете — вверху, над заголовком (решение владельца 11.11.2026).

    python3 tools/site/crumbs_top.py            — правка страниц превью (index.html в репозитории)

Ошибка: правило tools/site/hero_fold.py (кнопки первого экрана видны целиком) на ширине от 861 px раскладывает блоки
первого экрана .d-hero по порядку и знало только крошки .d-crumbs. Крошки .f-crumbs внутри .d-hero (нормативная база,
проверочные листы, документы для Роспотребнадзора, оценка эффективности, акт, схема точек) получали порядок 6
и вставали сразу под кнопки — вплотную (0 px) или с отступом 18–24 px. Владелец: «Не должно быть так».
Теперь:
  * hero_fold.py: #hero.d-hero .d-hero-copy>:is(.d-crumbs,.f-crumbs){order:0} — любые крошки идут первыми;
  * tools/normativnaya-baza/page.css (до 1180 px): у крошек больше нет order:7 (были в самом низу, под подписью
    автора), отступ — снизу 18 px, до заголовка;
  * tools/materialy-dokumenty/page.css: убран отступ 24 px над крошками (был нужен, пока крошки стояли под кнопками).
На телефоне (до 900 px) крошки по-прежнему скрыты правилом m-crumbs (tools/site/mobile_crumbs.py): правило владельца —
на телефоне крошки только внизу первого экрана или ниже и только если нужны для SEO; BreadcrumbList и ссылки в HTML
остаются. Тексты и порядок в HTML не меняются.
Та же функция apply() — для точечной правки страниц, снятых с сайта (tools/deploy/prepare-2026-11-11-crumbs.py).
Проверка на всех страницах: node tools/qa/check_crumbs.mjs.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SKIP = {'.git', 'tools', 'dist', 'server', 'node_modules', 'preview-audit'}
EDITS = [
    ('#hero.d-hero .d-hero-copy>.d-crumbs{order:0}', '#hero.d-hero .d-hero-copy>:is(.d-crumbs,.f-crumbs){order:0}'),  # в странице блок hero-fold — одной строкой
    ('  .nb-hero .f-crumbs{order:7;margin:18px 0 0}\n', '  .nb-hero .f-crumbs{margin:0 0 18px}\n'),
    ('/* с 11.11.2026: крошки под кнопками первого экрана — с отступом; блок «Заказать акт» (услуга, 3 000 ₽) */\n'
     '@media (min-width:861px){.md-hero .d-hero-copy>.f-crumbs{margin-top:24px}}\n',
     '/* блок «Заказать акт» (услуга, 3 000 ₽); крошки первого экрана — вверху, над заголовком (tools/site/hero_fold.py, 11.11.2026) */\n'),
]


def apply(s):
    """Правки страницы; каждая — не больше одного раза, повторный запуск ничего не меняет. → (страница, число правок)."""
    n = 0
    for old, new in EDITS:
        c = s.count(old)
        assert c <= 1, f'«{old[:50]}» — вхождений {c}'
        if c:
            s = s.replace(old, new)
            n += 1
    return s, n


def main():
    for f in sorted(ROOT.rglob('index.html')):
        if SKIP & set(f.relative_to(ROOT).parts):
            continue
        s = f.read_text(encoding='utf-8')
        new, n = apply(s)
        if n:
            f.write_text(new, encoding='utf-8')
            print(f'{f.relative_to(ROOT)}: правок {n}')


if __name__ == '__main__':
    main()
