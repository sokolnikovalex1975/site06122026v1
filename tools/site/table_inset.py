#!/usr/bin/env python3
"""Отступ текста в таблицах от края — правило владельца сайта для всех страниц (10.11.2026).

    python3 tools/site/table_inset.py

Замечание владельца: «в таблицах типа прайс-листов текст приклеен к левой вертикальной линии — так не должно быть».
В общем стиле .d-table у ячеек отступ 16px 20px 16px 0: слева ноль. В открытых таблицах это почти незаметно, а там,
где таблица стоит в карточке с рамкой или фоном, текст прилипает к линии. Правило даёт первой колонке отступ слева,
последней — справа, одинаковый на всех страницах, когда таблица выглядит таблицей — шире 900 px. До 900 px большинство таблиц сайта
складываются в карточки со своим внутренним отступом (проверено в браузере 10.11.2026 на 610–1180 px) — их не трогаем.

Скрипт вставляет (или обновляет) одну строку <style id="t-inset"> перед </head> на каждой странице с таблицей .d-table.
Запускается из tools/site/build_site.py после tools/site/mobile_crumbs.py.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SKIP = {'.git', 'tools', 'dist', 'server', 'node_modules'}
PAD = 'clamp(16px,1.5vw,24px)'


def rule():
    css = (f'@media (min-width:901px){{.d-table tr>:first-child{{padding-left:{PAD}}}'
           f'.d-table tr>:last-child{{padding-right:{PAD}}}}}')
    return ('<style id="t-inset">/* таблицы: текст не прижимается к краю — отступ первой и последней колонки */'
            + css + '</style>')


HAS_TABLE = re.compile(r'<table[^>]*class="[^"]*\bd-table\b')
OLD = re.compile(r'<style id="t-inset">.*?</style>\n?', re.S)


def apply(s):
    if not HAS_TABLE.search(s):
        return s, False
    s = OLD.sub('', s)
    if s.count('</head>') != 1:
        raise SystemExit('ошибка: на странице не один </head>')
    return s.replace('</head>', rule() + '\n</head>', 1), True


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
    print(f'отступ в таблицах: {n} страниц')


if __name__ == '__main__':
    main()
