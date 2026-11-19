#!/usr/bin/env python3
"""Курсор над чекбоксами и вариантами ответа — фирменное кольцо вместо «палочки» для текста (вариант А, 20.11.2026).

    python3 tools/site/chk_cursor.py            # правит страницы репозитория
    python3 tools/site/chk_cursor.py --check    # только проверка, код 1, если нужно поправить

Замечание владельца 19.11.2026: при наведении мыши на чекбокс появляется курсор-«палочка» (I-beam) — непонятно, что
пункт можно нажать. Выбор владельца 20.11.2026: «Делай вариант А».

Причина: в общем блоке курсора style.css правило `html.has-cursor input{cursor:text}` действует на все input, в том числе
на чекбоксы и переключатели, а курсор app.js ставит над любым input класс text и прячет фирменное кольцо. Затронуто:
  * самопроверка `.f-check-list` — 14 страниц на сайте (+ превью): над квадратом «палочка», кольца нет, над текстом
    пункта — системная рука и кольцо одновременно;
  * опросный лист «Разработка ППК» `.rp-chip` (70 вариантов): «палочка» на всей кнопке варианта.

Вариант А: над пунктом самопроверки и кнопкой варианта — фирменное кольцо, как на ссылках и кнопках сайта (системный
курсор скрыт); квадрат подсвечивается фиолетовой рамкой и бледной галочкой-подсказкой, текст пункта становится ярче;
у варианта ответа подсвечивается кружок или квадратик. Только стили, одна строка <style id="chk-cur"> перед </head> на
страницах с этими блоками: style.css, app.min.js, тексты, счётчики, телефон и почта не меняются.
  * Кольцо: app.js ставит над чекбоксом классы link и text (text прячет кольцо) — правило с :has() возвращает кольцо,
    пока мышь над чекбоксом или вариантом. В браузерах без :has() вместо скрытого курсора — обычная рука.
  * Подсветка — только для мыши (@media (hover:hover) and (pointer:fine)); на телефонах ничего не меняется.
  * Ничего не затемняется (закон владельца 17.11.2026).
Проверка в браузере: node tools/qa/chk_cursor_test.mjs.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
OLD = re.compile(r'<style id="chk-cur">.*?</style>\n?', re.S)
MARKS = ('class="f-check-list', 'class="rp-chip"')
CHECK_SVG = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 14 14'%3E%3Cpath "
             "d='M2.5 7.5l3 3 6-7' fill='none' stroke='%23a5abff' stroke-opacity='.6' stroke-width='2' "
             "stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E\")")
HOT = 'html.has-cursor .f-check-list input,html.has-cursor .f-check-list label,html.has-cursor .rp-chip>input'
CSS = (HOT + '{cursor:none}'
       'html.has-cursor:has(.f-check-list input:hover,.rp-chip>input:hover) .cursor.text .cursor-ring{opacity:1}'
       '@supports not selector(:has(*)){' + HOT + '{cursor:pointer}}'
       '@media (hover:hover) and (pointer:fine){'
       '.f-check-list label:hover input{box-shadow:0 0 0 4px rgba(124,134,255,.14)}'
       '.f-check-list label:hover input:not(:checked){border-color:rgba(124,134,255,.8);'
       'background-color:rgba(124,134,255,.12);background-image:' + CHECK_SVG + '}'
       '.f-check-list label:hover input:checked{border-color:#a5abff;box-shadow:0 0 0 4px rgba(124,134,255,.18)}'
       '.f-check-list label:hover>span{color:var(--t1)}'
       '.rp-chip:hover>span::before{border-color:var(--acc);background:rgba(124,134,255,.22)}'
       '}')
LINE = ('<style id="chk-cur">/* курсор над чекбоксами и вариантами ответа — фирменное кольцо и подсветка квадрата'
        ' (tools/site/chk_cursor.py, вариант А, 20.11.2026) */' + CSS + '</style>\n')


def needs(s):
    return any(m in s for m in MARKS)


def apply(s):
    s = OLD.sub('', s)
    if not needs(s):
        return s
    assert s.count('</head>') == 1, '</head> не один раз'
    return s.replace('</head>', LINE + '</head>')


def pages():
    skip = ('tools', 'dist', 'node_modules', 'vendor', '.git')
    return sorted(p for p in ROOT.rglob('index.html') if not set(p.relative_to(ROOT).parts) & set(skip))


def main():
    check = '--check' in sys.argv
    bad = 0
    for p in pages():
        s = p.read_text(encoding='utf-8')
        new = apply(s)
        if new != s:
            bad += 1
            print(('НУЖНО: ' if check else 'ПРАВКА: ') + str(p.relative_to(ROOT)))
            if not check:
                p.write_text(new, encoding='utf-8')
    print('страниц с чекбоксами: %d' % sum(needs(p.read_text(encoding='utf-8')) for p in pages()))
    sys.exit(1 if check and bad else 0)


if __name__ == '__main__':
    main()
