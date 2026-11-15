#!/usr/bin/env python3
"""Главный запрос семантического ядра в H1 — утверждено владельцем 15.11.2026.

    python3 tools/site/h1_core.py            # правит страницы репозитория
    python3 tools/site/h1_core.py --check    # только проверка (код 1, если где-то прежний H1 или нет нового)

Решение владельца 15.11.2026: главный запрос семантического ядра страницы — в Title и H1, где его нет. Title —
TITLE_CORE в tools/site/meta_titles.py, H1 — здесь. Меняются только слова: разметка H1 та же (строки .ln с маской
и вход первого экрана, акцентный <em>, неразрывное <span class="nw">), поэтому анимация и стили прежние.

Что делает (шаг tools/site/build_site.py после meta_titles.py и перед tracking_laws.py; patch() применим и к живым
index.php с Timeweb): у каждой страницы из H1 прежний H1 целиком (готовая разметка после unify.py) заменяется новым.
Генераторы страниц (tools/*) пока дают прежний H1 — этот шаг идёт после них, поэтому сборка даёт новый. og:title,
headline и name в разметке, хлебные крошки и тексты не меняются. Повторный запуск ничего не меняет.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def typo(text):
    """Неразрывный пробел после слов из одной-двух букв (с, и, на, по) и «для», как типографика генераторов страниц."""
    return re.sub(r'(?<![\w<-])(\w{1,2}|для) (?=\w)', '\\1\u00a0', text)


def ln(text, em=False):
    text = typo(text)
    inner = '<em>%s</em>' % text if em else text
    return '<span class="ln"><span>%s</span></span>' % inner


def h1(*lines):
    return '<h1>' + ' '.join(lines) + '</h1>'


NW_PK = '<span class="nw">пест-контроля</span>'

H1 = {  # адрес страницы: (было, стало) — запрос ядра в комментарии
    'dezinfektsiya/': (  # дезинфекция помещений
        h1('<span class="ln d-ln1"><span>Дезинфекция</span></span>', ln('для организаций', em=True)),
        h1('<span class="ln d-ln1"><span>Дезинфекция помещений</span></span>', ln('для организаций', em=True))),
    'materialy/kak-berut-smyvy/': (  # метод смывов с поверхности
        h1(ln('Как берут смывы'), ln('с поверхностей и рук', em=True)),
        h1(ln('Метод смывов'), ln('с поверхности и рук', em=True))),
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/': (  # программа производственного контроля образец
        h1(ln('Программа'), ln('производственного'), ln('контроля по ХАССП:'), ln('раздел ' + NW_PK, em=True)),
        h1(ln('Образец программы'), ln('производственного'), ln('контроля по ХАССП:'), ln('раздел ' + NW_PK, em=True))),
    'laboratornye-issledovaniya/analiz-pishchevykh-produktov/': (  # испытания пищевой продукции
        h1(ln('Анализ пищевых продуктов'), ln('и готовых блюд', em=True)),
        h1(ln('Испытания пищевой продукции'), ln('и готовых блюд', em=True))),
    'laboratornye-issledovaniya/zamer-osveshchennosti/': (  # измерение освещённости
        h1(ln('Замер освещённости'), ln('на рабочих местах', em=True)),
        h1(ln('Измерение освещённости'), ln('на рабочих местах', em=True))),
    'materialy/skhema-tochek-pest-kontrolya/': (  # точки контроля грызунов
        h1(ln('Схема точек'), ln(NW_PK + ':'), ln('образец и правила', em=True)),
        h1(ln('Схема точек'), ln('контроля грызунов'), ln('и насекомых: образец', em=True))),
    'laboratornye-issledovaniya/analiz-smyvov/': (  # смывы на БГКП
        h1(ln('Анализ смывов'), ln('с поверхностей, оборудования и рук', em=True)),
        h1(ln('Анализ смывов'), ln('на БГКП с поверхностей и рук', em=True))),
    'materialy/zamer-osveshchennosti-i-mikroklimata/': (  # методика измерения освещённости на рабочих местах
        h1(ln('Как проходит замер'), ln('освещённости и микроклимата', em=True)),
        h1(ln('Методика измерения'), ln('освещённости на рабочих местах'), ln('и микроклимата', em=True))),
    'laboratornye-issledovaniya/kontrol-sterilizatorov/': (  # анализ на стерильность
        h1(ln('Контроль работы стерилизаторов'), ln('и стерильности инструментов', em=True)),
        h1(ln('Контроль работы стерилизаторов'), ln('и анализ на стерильность', em=True))),
    'materialy/programma-pest-kontrolya/': (  # программа пест-контроля пищевого предприятия: образец
        h1(ln('Программа'), ln(NW_PK), ln('на предприятии', em=True)),
        h1(ln('Образец программы'), ln(NW_PK), ln('пищевого предприятия', em=True))),
}


def patch(path, s):
    """path — адрес страницы от корня сайта ('dezinfektsiya/'), s — HTML страницы."""
    if path in H1:
        old, new = H1[path]
        s = s.replace(old, new)
    return s


def left(path, s):
    old, new = H1[path]
    return old in s or s.count(new) != 1


def main():
    check = '--check' in sys.argv[1:]
    changed, bad = [], []
    for path in sorted(H1):
        f = ROOT / path / 'index.html'
        s = f.read_text(encoding='utf-8')
        new = patch(path, s)
        assert patch(path, new) == new
        if check:
            if left(path, s):
                bad.append(path)
            continue
        assert not left(path, new), '%s: нет прежнего H1 в разметке страницы — сверьте H1 в h1_core.py' % path
        if new != s:
            f.write_text(new, encoding='utf-8')
            changed.append(path)
    if check:
        for path in bad:
            print('h1_core:', path, '— прежний H1 или нет нового')
        print('h1_core: страниц без H1 с запросом ядра:', len(bad))
        sys.exit(1 if bad else 0)
    print('h1_core: запрос ядра в H1 — изменено страниц:', len(changed))


if __name__ == '__main__':
    main()
