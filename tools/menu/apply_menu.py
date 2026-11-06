#!/usr/bin/env python3
"""Общее меню сайта site06122026v1 (06.11.2026): шапка, мобильное меню и подвал на всех страницах.

    Услуги ▾ · Отрасли ▾ · Договор · Метод IPM · Цена · Материалы ▾
    (в «Услугах» с 06.11.2026 — очистка и дезинфекция вентиляции)

В меню — только готовые страницы сайта. Отрасли без своей страницы ведут к карточке отрасли на главной
(якоря #otrasl-…), у пищевых и фармацевтических производств, магазинов и торговых сетей, гостиниц — свои страницы. «Контакты» — только в подвале.
Ссылки — обычные <a href> прямо в HTML. С внутренних страниц якоря ведут на главную (../#podhod).
Телефон, ссылки Telegram/MAX, кнопки заявки и блок счётчиков не меняются.
Страницы документов (политика, согласие) получают ту же шапку и тот же подвал.

Запуск из корня репозитория: python3 tools/menu/apply_menu.py (или общий tools/site/build_site.py).
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
from typo import typo  # неразрывный пробел после коротких слов («и\u00a0отели»), как в остальных текстах сайта

# Услуги (выпадающий список «Услуги ▾» в шапке и раскрывающийся блок в мобильном меню)
USLUGI = [
    ('dezinfektsiya', 'Дезинфекция для организаций'),
    ('deratizatsiya', 'Дератизация для организаций'),
    ('dezinsektsiya', 'Дезинсекция для организаций'),
    ('sanitarnyy-audit', 'Санитарный аудит <span class="nw">(СЭС-аудит)</span>'),
    ('ochistka-dezinfektsiya-ventilyatsii', 'Очистка и дезинфекция вентиляции'),
    ('dogovor-deratizatsiya-dezinsektsiya', 'Договор на обслуживание'),
]
# Отрасли — в порядке блока «Отрасли» на главной. Адрес со знаком # — карточка отрасли на главной (своей страницы пока нет)
INDUSTRIES = [
    ('pishchevoe-proizvodstvo', 'Пищевые производства'),
    ('magaziny-i-torgovye-seti', 'Магазины и торговые сети'),
    ('restorany-i-kafe', 'Рестораны и кафе'),
    ('sklady-i-logistika', 'Склады и логистика'),
    ('farmatsevticheskie-proizvodstva', 'Фармацевтические производства'),
    ('gostinitsy', 'Гостиницы и отели'),
]
DOGOVOR = 'dogovor-deratizatsiya-dezinsektsiya'
DERAT = 'deratizatsiya'
VENT = 'ochistka-dezinfektsiya-ventilyatsii'
SAN = 'sanitarnyy-audit'
MATERIALS = [  # слова через дефис не переносим (класс nw, как в остальных текстах сайта)
    ('materialy/programma-pest-kontrolya', 'Программа <span class="nw">пест-контроля</span>'),
    ('materialy/zhurnal-pest-kontrolya', 'Журнал <span class="nw">пест-контроля</span>'),
    ('materialy/pest-menedzhment-ili-razovaya-obrabotka', '<span class="nw">Пест-менеджмент</span> или разовая обработка'),
    ('materialy/programma-proizvodstvennogo-kontrolya-haccp', 'Программа производственного контроля по ХАССП'),
]
SERVICE = [  # блоки главной
    ('etapy', 'Этапы работы'), ('vrediteli', 'Вредители'),
    ('dokumenty', 'Документы для проверок'), ('usloviya', 'Цена'), ('voprosy', 'Вопросы'),
]
CHEV = '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CHEV_M = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARR = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'

PAGES = [
    # файл, путь к корню, текущая страница
    ('index.html', '', ''),
    ('dezinfektsiya/index.html', '../', 'dezinfektsiya'),
    (DERAT + '/index.html', '../', DERAT),
    ('dezinsektsiya/index.html', '../', 'dezinsektsiya'),
    (VENT + '/index.html', '../', VENT),
    (SAN + '/index.html', '../', SAN),
    (DOGOVOR + '/index.html', '../', DOGOVOR),
    ('pishchevoe-proizvodstvo/index.html', '../', 'pishchevoe-proizvodstvo'),
    ('restorany-i-kafe/index.html', '../', 'restorany-i-kafe'),
    ('magaziny-i-torgovye-seti/index.html', '../', 'magaziny-i-torgovye-seti'),
    ('gostinitsy/index.html', '../', 'gostinitsy'),
    ('farmatsevticheskie-proizvodstva/index.html', '../', 'farmatsevticheskie-proizvodstva'),
    ('sklady-i-logistika/index.html', '../', 'sklady-i-logistika'),
    ('materialy/pest-menedzhment-ili-razovaya-obrabotka/index.html', '../../', 'materialy/pest-menedzhment-ili-razovaya-obrabotka'),
    ('materialy/index.html', '../', 'materialy'),
    ('materialy/programma-pest-kontrolya/index.html', '../../', 'materialy/programma-pest-kontrolya'),
    ('materialy/zhurnal-pest-kontrolya/index.html', '../../', 'materialy/zhurnal-pest-kontrolya'),
    ('materialy/programma-proizvodstvennogo-kontrolya-haccp/index.html', '../../', 'materialy/programma-proizvodstvennogo-kontrolya-haccp'),
]
LEGAL = [('privacy/index.html', '../', 'privacy'), ('soglasie/index.html', '../', 'soglasie')]


def page_link(root, cur, slug, text, cls=''):
    if slug.startswith('#'):  # карточка на главной
        return anchor(root, slug[1:], text, cls)
    c = f' class="{cls}"' if cls else ''
    if slug == cur:
        return f'<a href="./"{c} aria-current="page">{text}</a>'
    return f'<a href="{root}{slug}/"{c}>{text}</a>'


def anchor(root, sid, text, cls=''):
    c = f' class="{cls}"' if cls else ''
    return f'<a href="{root}#{sid}"{c}>{text}</a>'


def dropdown(key, label, items, active, spy=''):
    btn_cls = 'nav-dd-btn active' if active else 'nav-dd-btn'
    return (f'<div class="nav-dd"><button class="{btn_cls}" type="button" aria-expanded="false" aria-controls="nav-{key}"{spy}>{label}{CHEV}</button>'
            f'<div class="nav-dd-panel" id="nav-{key}">{items}</div></div>')


def mm_group(key, label, items, opened):
    cls = ' open" data-open' if opened else '"'
    return (f'<div class="mm-group{cls}><button class="mm-toggle" type="button" aria-expanded="{"true" if opened else "false"}" aria-controls="mm-{key}">{label}{CHEV_M}</button>'
            f'<div class="mm-sub" id="mm-{key}"><div>{items}</div></div></div>')


def one(t):
    """Подпись с вложенным тегом (<span class="nw">) — одним элементом: пункты списков — flex, иначе слова разъедутся."""
    return f'<span>{t}</span>' if '<' in t else t


def build(root, cur, cta_mobile):
    home = root == ''
    in_usl = cur in ('dezinfektsiya', DERAT, 'dezinsektsiya', VENT, SAN)
    in_ind = any(s == cur for s, _ in INDUSTRIES)
    in_mat = cur.startswith('materialy')
    # шапка: Услуги ▾ · Отрасли ▾ · Договор · Метод IPM · Цена · Материалы ▾
    usl_items = ''.join(page_link(root, cur, s, one(t) + ARR) for s, t in USLUGI)
    usl_items += anchor(root, 'podhod', '<span>Пест-контроль по системе IPM</span>' + ARR, 'nav-dd-all')
    ind_items = ''.join(page_link(root, cur, s, t + ARR) for s, t in INDUSTRIES)
    ind_items += anchor(root, 'otrasli', 'Все отрасли' + ARR, 'nav-dd-all')
    mat_items = ''.join(page_link(root, cur, s, one(t) + ARR) for s, t in MATERIALS)
    mat_items += page_link(root, cur, 'materialy', 'Все материалы' + ARR, 'nav-dd-all')
    spy = ' data-spy="#otrasli"' if home else ''
    nav = (
        '<nav class="nav" aria-label="Основное меню">\n      '
        + dropdown('uslugi', 'Услуги', usl_items, in_usl)
        + dropdown('otrasli', 'Отрасли', ind_items, in_ind, spy)
        + (f'<a href="./" class="active" aria-current="page">Договор</a>' if cur == DOGOVOR else f'<a href="{root}{DOGOVOR}/">Договор</a>')
        + anchor(root, 'podhod', 'Метод IPM') + anchor(root, 'usloviya', 'Цена')
        + dropdown('materialy', 'Материалы', mat_items, in_mat) + '\n    </nav>'
    )
    # мобильное меню
    sub_usl = ''.join(page_link(root, cur, s, one(t)) for s, t in USLUGI) + anchor(root, 'podhod', '<span class="nw">Пест-контроль</span> по системе IPM')
    sub_ind = ''.join(page_link(root, cur, s, t) for s, t in INDUSTRIES) + anchor(root, 'otrasli', 'Все отрасли')
    sub_mat = ''.join(page_link(root, cur, s, one(t)) for s, t in MATERIALS) + page_link(root, cur, 'materialy', 'Все материалы')
    dog_text = 'Договор <small>на дератизацию и дезинсекцию</small>'
    mm = (
        '<nav class="mmenu" id="mmenu" aria-label="Мобильное меню">\n  '
        + mm_group('uslugi', 'Услуги', sub_usl, in_usl)
        + mm_group('otrasli', 'Отрасли', sub_ind, in_ind)
        + (f'<a href="./" aria-current="page">{dog_text}</a>' if cur == DOGOVOR else f'<a href="{root}{DOGOVOR}/">{dog_text}</a>')
        + anchor(root, 'podhod', 'Метод IPM') + anchor(root, 'usloviya', 'Цена')
        + mm_group('materialy', 'Материалы', sub_mat, in_mat) + '\n'
        f'  {cta_mobile}\n</nav>'
    )
    # подвал: колонки «Услуги», «Отрасли», «Материалы» (описание и «Контакты» остаются как были)
    li = lambda a: f'<li>{a}</li>'
    # подпись с вложенным <span class="nw"> оборачиваем в один <span>: на телефоне ссылки подвала — inline-flex,
    # и без обёртки пробел перед вложенным тегом пропал бы
    wrap = lambda t: f'<span>{t}</span>' if '<' in t else t
    ft_srv = (''.join(li(page_link(root, cur, s, wrap(t) if s != DOGOVOR else 'Договор на дератизацию и дезинсекцию')) for s, t in USLUGI)
              + li(anchor(root, 'podhod', wrap('<span class="nw">Пест-контроль</span> по системе IPM')))
              + ''.join(li(anchor(root, s, t)) for s, t in SERVICE))
    ft_ind = ''.join(li(page_link(root, cur, s, t)) for s, t in INDUSTRIES)
    ft_mat = ''.join(li(page_link(root, cur, s, wrap(t))) for s, t in MATERIALS) + li(page_link(root, cur, 'materialy', 'Все материалы'))
    cols = (f'<div><h4>Услуги</h4><ul>{ft_srv}</ul></div>\n'
            f'      <div><h4>Отрасли</h4><ul>{ft_ind}</ul></div>\n'
            f'      <div><h4>Материалы</h4><ul>{ft_mat}</ul></div>')
    return nav, mm, cols


def sub1(pat, rep, s):
    out, n = re.subn(pat, lambda m: rep, s, count=1, flags=re.S)
    assert n == 1, pat
    return out


def main():
    for rel, root, cur in PAGES + LEGAL:
        f = ROOT / rel
        s = f.read_text(encoding='utf-8')
        cta = re.search(r'<nav class="mmenu"[^>]*>.*?(<a href="(?:\.\./)*#zayavka" class="btn btn-w btn-lg">.*?</a>)\s*</nav>', s, re.S).group(1)
        nav, mm, cols = (typo(x) for x in build(root, cur, cta))
        s = sub1(r'<nav class="nav" aria-label="Основное меню">.*?</nav>', nav, s)
        s = sub1(r'<nav class="mmenu" id="mmenu" aria-label="Мобильное меню">.*?</nav>', mm, s)
        s = sub1(r'<div><h4>(?:Объекты|Отрасли|Услуги)</h4>.*?(?=\n\s*<div><h4>Контакты</h4>)', cols, s)
        # нижняя строка подвала: ссылка на согласие рядом с политикой
        if not re.search('Согласие на[ \u00a0]обработку данных</a>', s):  # с неразрывным пробелом тоже
            s, n = re.subn(r'(<div class="fb">.*?<a href="((?:\.\./)*)privacy/">Политика конфиденциальности</a>)',
                           lambda m: m.group(1) + f'<a href="{m.group(2)}soglasie/">Согласие на обработку данных</a>',
                           s, count=1, flags=re.S)
            assert n == 1, 'нет строки .fb с политикой'
        s = s.replace('</footer>\n</footer>', '</footer>')  # лишний закрывающий тег во внутренних страницах
        f.write_text(s, encoding='utf-8')
        print('ok', rel)


if __name__ == '__main__':
    main()
