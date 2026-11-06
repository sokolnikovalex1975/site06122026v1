#!/usr/bin/env python3
"""Выкладка 06.11.2026: пункт «Дезинфекция для организаций» первым в меню «Услуги» — точечно, поверх файлов сайта.

Файлы на сайте и в main собраны разными выкладками (часть правок main ещё не выложена, часть правок сайта есть только там),
поэтому страницы целиком не заменяются. Скрипт берёт текущие файлы сайта и вставляет ровно три ссылки — в выпадающее меню
шапки (id="nav-uslugi"), в мобильное меню (id="mm-uslugi") и в колонку «Услуги» подвала. Разметка ссылок берётся
из сборки main (dist/timeweb) той же страницы, поэтому совпадает байт в байт с тем, что даёт tools/menu/apply_menu.py.
Заодно убирается задвоенная ссылка «Согласие на обработку данных» в нижней строке подвала (была на трёх страницах сайта).

Проверки: на страницах, где файл сайта совпадает со сборкой main без новой страницы, результат должен совпасть со сборкой
main с новой страницей байт в байт; на остальных — отличаться от файла сайта только тремя вставками (и снятым дублем).

Запуск: python3 tools/deploy/insert_dezinf_menu.py <папка с файлами сайта> <dist/timeweb> <папка результата>
"""
import pathlib
import re
import sys

LIVE, BUILD, OUT = (pathlib.Path(p) for p in sys.argv[1:4])
PAGES = [
    ('index.php', ''),
    ('deratizatsiya/index.php', '../'), ('dezinsektsiya/index.php', '../'), ('sanitarnyy-audit/index.php', '../'),
    ('ochistka-dezinfektsiya-ventilyatsii/index.php', '../'), ('dogovor-deratizatsiya-dezinsektsiya/index.php', '../'),
    ('pishchevoe-proizvodstvo/index.php', '../'), ('magaziny-i-torgovye-seti/index.php', '../'),
    ('restorany-i-kafe/index.php', '../'), ('sklady-i-logistika/index.php', '../'),
    ('farmatsevticheskie-proizvodstva/index.php', '../'), ('gostinitsy/index.php', '../'),
    ('materialy/index.php', '../'),
    ('materialy/programma-pest-kontrolya/index.php', '../../'), ('materialy/zhurnal-pest-kontrolya/index.php', '../../'),
    ('materialy/pest-menedzhment-ili-razovaya-obrabotka/index.php', '../../'),
    ('materialy/programma-proizvodstvennogo-kontrolya-haccp/index.php', '../../'),
    ('privacy/index.php', '../'), ('soglasie/index.php', '../'),
]
SAME = set(sys.argv[4].split(',')) if len(sys.argv) > 4 and sys.argv[4] else set()


def one(rx, s, what):
    m = list(re.finditer(rx, s, re.S))
    assert len(m) == 1, f'{what}: найдено {len(m)}'
    return m[0]


def snippets(b, root):
    """Три ссылки на новую страницу из сборки main (как их делает apply_menu.py)."""
    h = re.escape(f'<a href="{root}dezinfektsiya/">')
    nav = one(r'id="nav-uslugi">(' + h + r'.*?</a>)', b, 'шапка').group(1)
    mm = one(r'id="mm-uslugi"><div>(' + h + r'.*?</a>)', b, 'мобильное меню').group(1)
    ft = one(r'<h4>Услуги</h4><ul>(<li>' + h + r'.*?</a></li>)', b, 'подвал').group(1)
    return nav, mm, ft


def patch(s, root, nav, mm, ft):
    assert f'href="{root}dezinfektsiya/"' not in s, 'ссылка уже есть'
    m = one(r'<div class="nav-dd-panel" id="nav-uslugi">', s, 'шапка (сайт)')
    s = s[:m.end()] + nav + s[m.end():]
    m = one(r'<div class="mm-sub" id="mm-uslugi"><div>', s, 'мобильное меню (сайт)')
    s = s[:m.end()] + mm + s[m.end():]
    m = one(r'<div><h4>Услуги</h4><ul>', s, 'подвал (сайт)')
    s = s[:m.end()] + ft + s[m.end():]
    return dedup(s, root)


def dedup(s, root):
    """Задвоенная ссылка на согласие в нижней строке подвала (вторая — с неразрывным пробелом) → одна, как в main."""
    one_link = f'<a href="{root}soglasie/">Согласие на обработку данных</a>'
    return s.replace(one_link + f'<a href="{root}soglasie/">Согласие на\u00a0обработку данных</a>', one_link, 1)


ok = True
for f, root in PAGES:
    live = (LIVE / f).read_text(encoding='utf-8')
    build = (BUILD / f).read_text(encoding='utf-8')
    nav, mm, ft = snippets(build, root)
    new = patch(live, root, nav, mm, ft)
    # обратная проверка: без трёх вставок — файл сайта (с точностью до снятого дубля)
    back = new.replace(nav, '', 1).replace(mm, '', 1).replace(ft, '', 1)
    note = ''
    if back != live:
        assert back == dedup(live, root), f'{f}: лишние отличия'
        note = ' + снят дубль ссылки на согласие'
    if f in SAME:
        if new != build:
            ok = False
            print('ОШИБКА', f, 'не совпадает со сборкой main')
            continue
        note += ' = сборка main'
    (OUT / f).parent.mkdir(parents=True, exist_ok=True)
    (OUT / f).write_text(new, encoding='utf-8')
    print('ok', f, f'+{len(new.encode()) - len(live.encode())} байт' + note)
sys.exit(0 if ok else 1)
