#!/usr/bin/env python3
"""Хлебные крошки на телефоне — правило владельца сайта для всех страниц.

    python3 tools/site/mobile_crumbs.py

Крошки на мобильной версии показываются, только если они реально нужны для SEO; если нужны — минимально заметные
и только после первого экрана или в самом его низу. На этом сайте для SEO они на телефоне не нужны ни на одной странице:
цепочка для поиска передаётся разметкой BreadcrumbList (JSON-LD), а ссылки крошек остаются в HTML-коде страницы
и видны на компьютере (поисковые роботы читают HTML целиком, мобильная индексация учитывает скрытые стилями блоки).
Поэтому до 900 px (телефоны в обеих ориентациях и узкие планшеты) блок .d-crumbs / .f-crumbs скрыт.

Скрипт вставляет (или обновляет) одну строку <style id="m-crumbs"> перед </head> на каждой странице с крошками.
Запускается из tools/site/build_site.py после tools/menu/apply_menu.py.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SKIP = {'.git', 'tools', 'dist', 'server', 'node_modules'}
RULE = ('<style id="m-crumbs">/* крошки на телефоне не показываем: для SEO хватает BreadcrumbList и ссылок в HTML */'
        '@media (max-width:900px){.d-crumbs,.f-crumbs{display:none!important}}</style>')
HAS_CRUMBS = re.compile(r'<nav[^>]*class="[^"]*\b(?:d|f)-crumbs\b')
OLD = re.compile(r'<style id="m-crumbs">.*?</style>\n?', re.S)


def apply(s):
    """Вставить правило в одну страницу (тот же код используется для точечной правки страниц с сайта)."""
    if not HAS_CRUMBS.search(s):
        return s, False
    s = OLD.sub('', s)
    if s.count('</head>') != 1:
        raise SystemExit('ошибка: на странице не один </head>')
    return s.replace('</head>', RULE + '\n</head>', 1), True


def main():
    n = 0
    for f in sorted(ROOT.rglob('index.html')):
        if SKIP & set(f.relative_to(ROOT).parts):
            continue
        s = f.read_text(encoding='utf-8')
        new, ok = apply(s)
        if ok:
            n += 1
            if new != s:
                f.write_text(new, encoding='utf-8')
    print(f'крошки на телефоне скрыты: {n} страниц')


if __name__ == '__main__':
    main()
