#!/usr/bin/env python3
"""Общее меню сайта (вариант 1 черновика «SEO/Главное меню — черновик v0», 29–30.10.2026).

Ставит одинаковые шапку (меню), мобильное меню и подвал на все страницы:
главную, «Договор на дератизацию и дезинсекцию» и «Пест-контроль на пищевом производстве».

    Отрасли ▾ · Договор · Метод IPM · Цена · Материалы

«Контакты» — только в подвале, пока не согласован адрес (решение 30.10.2026).
Ссылки — обычные <a href> прямо в HTML. С внутренних страниц якоря ведут на главную (../#podhod).
Телефон, ссылки Telegram/MAX, кнопки заявки и блок счётчиков не меняются.

Запуск из корня репозитория: python3 tools/menu/apply_menu.py
Пищевую страницу собирает tools/food/assemble.py — после него запустите этот скрипт ещё раз.
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
from typo import typo  # неразрывный пробел после коротких слов («и\u00a0отели»), как в остальных текстах сайта

# Услуги (выпадающий список «Услуги ▾» в шапке и раскрывающийся блок в мобильном меню)
USLUGI = [
    ('deratizatsiya', 'Дератизация для организаций'),
    ('dezinsektsiya', 'Дезинсекция для организаций'),
    ('dezinfektsiya', 'Дезинфекция для организаций'),
    ('dogovor-deratizatsiya-dezinsektsiya', 'Договор на обслуживание'),
]
# Отрасли — в порядке блока «Отрасли» на главной; адреса — из SEO-плана
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
MATERIALS = [  # слова через дефис не переносим (класс nw, как в остальных текстах сайта)
    ('materialy/programma-pest-kontrolya', 'Программа <span class="nw">пест-контроля</span>'),
    ('materialy/zhurnal-pest-kontrolya', 'Журнал <span class="nw">пест-контроля</span>'),
    ('materialy/tochki-kontrolya', 'Точки контроля вредителей'),
    ('materialy/pest-menedzhment-ili-razovaya-obrabotka', '<span class="nw">Пест-менеджмент</span> или разовая обработка'),
    ('materialy', 'Все материалы'),
]
SERVICE = [  # блоки главной
    ('etapy', 'Этапы работы'), ('podhod', 'Метод IPM'), ('vrediteli', 'Вредители'),
    ('dokumenty', 'Документы'), ('usloviya', 'Цена'), ('voprosy', 'Вопросы'),
]
CHEV = '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CHEV_M = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARR = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'

PAGES = [
    # файл, путь к корню, текущая страница
    ('index.html', '', ''),
    (DERAT + '/index.html', '../', DERAT),
    ('dezinsektsiya/index.html', '../', 'dezinsektsiya'),
    (DOGOVOR + '/index.html', '../', DOGOVOR),
    ('pishchevoe-proizvodstvo/index.html', '../', 'pishchevoe-proizvodstvo'),
    ('materialy/pest-menedzhment-ili-razovaya-obrabotka/index.html', '../../', 'materialy/pest-menedzhment-ili-razovaya-obrabotka'),
    ('materialy/index.html', '../', 'materialy'),
    ('materialy/programma-pest-kontrolya/index.html', '../../', 'materialy/programma-pest-kontrolya'),
    ('materialy/zhurnal-pest-kontrolya/index.html', '../../', 'materialy/zhurnal-pest-kontrolya'),
]


def page_link(root, cur, slug, text, cls=''):
    c = f' class="{cls}"' if cls else ''
    if slug == cur:
        return f'<a href="./"{c} aria-current="page">{text}</a>'
    return f'<a href="{root}{slug}/"{c}>{text}</a>'


def anchor(root, sid, text, cls=''):
    c = f' class="{cls}"' if cls else ''
    return f'<a href="{root}#{sid}"{c}>{text}</a>'


def build(root, cur, cta_mobile):
    home = root == ''
    in_usl = cur in ('deratizatsiya', 'dezinsektsiya', 'dezinfektsiya')
    in_ind = any(s == cur for s, _ in INDUSTRIES)
    in_mat = cur.startswith('materialy')
    # шапка: Услуги ▾ · Отрасли ▾ · Договор · Метод IPM · Цена · Материалы
    usl_items = ''.join(page_link(root, cur, s, t + ARR) for s, t in USLUGI)
    usl_items += anchor(root, 'podhod', '<span>Пест-контроль по системе IPM</span>' + ARR, 'nav-dd-all')
    usl_btn_cls = 'nav-dd-btn active' if in_usl else 'nav-dd-btn'
    dd_items = ''.join(page_link(root, cur, s, t + ARR) for s, t in INDUSTRIES)
    dd_items += anchor(root, 'otrasli', 'Все отрасли' + ARR, 'nav-dd-all')
    spy = ' data-spy="#otrasli"' if home else ''
    btn_cls = 'nav-dd-btn active' if in_ind else 'nav-dd-btn'
    mat_cls = ' class="active"' if in_mat else ''
    nav = (
        '<nav class="nav" aria-label="Основное меню">\n'
        f'      <div class="nav-dd"><button class="{usl_btn_cls}" type="button" aria-expanded="false" aria-controls="nav-uslugi">Услуги{CHEV}</button>'
        f'<div class="nav-dd-panel" id="nav-uslugi">{usl_items}</div></div>'
        f'<div class="nav-dd"><button class="{btn_cls}" type="button" aria-expanded="false" aria-controls="nav-otrasli"{spy}>Отрасли{CHEV}</button>'
        f'<div class="nav-dd-panel" id="nav-otrasli">{dd_items}</div></div>'
        + (f'<a href="./" class="active" aria-current="page">Договор</a>' if cur == DOGOVOR else f'<a href="{root}{DOGOVOR}/">Договор</a>')
        + anchor(root, 'podhod', 'Метод IPM') + anchor(root, 'usloviya', 'Цена')
        + (f'<a href="./" class="active" aria-current="page">Материалы</a>' if cur == 'materialy' else f'<a href="{root}materialy/"{mat_cls}>Материалы</a>') + '\n    </nav>'
    )
    # мобильное меню
    sub_usl = ''.join(page_link(root, cur, s, t) for s, t in USLUGI) + anchor(root, 'podhod', '<span class="nw">Пест-контроль</span> по системе IPM')
    opened_usl = ' open" data-open' if in_usl else '"'
    sub = ''.join(page_link(root, cur, s, t) for s, t in INDUSTRIES) + anchor(root, 'otrasli', 'Все отрасли')
    opened = ' open" data-open' if in_ind else '"'
    dog_text = 'Договор <small>на дератизацию и дезинсекцию</small>'
    mm = (
        '<nav class="mmenu" id="mmenu" aria-label="Мобильное меню">\n'
        f'  <div class="mm-group{opened_usl}><button class="mm-toggle" type="button" aria-expanded="{"true" if in_usl else "false"}" aria-controls="mm-uslugi">Услуги{CHEV_M}</button>'
        f'<div class="mm-sub" id="mm-uslugi"><div>{sub_usl}</div></div></div>'
        f'<div class="mm-group{opened}><button class="mm-toggle" type="button" aria-expanded="{"true" if in_ind else "false"}" aria-controls="mm-otrasli">Отрасли{CHEV_M}</button>'
        f'<div class="mm-sub" id="mm-otrasli"><div>{sub}</div></div></div>'
        + (f'<a href="./" aria-current="page">{dog_text}</a>' if cur == DOGOVOR else f'<a href="{root}{DOGOVOR}/">{dog_text}</a>')
        + anchor(root, 'podhod', 'Метод IPM') + anchor(root, 'usloviya', 'Цена')
        + (f'<a href="./" aria-current="page">Материалы</a>' if cur == 'materialy' else f'<a href="{root}materialy/">Материалы</a>') + '\n'
        f'  {cta_mobile}\n</nav>'
    )
    # подвал: колонки «Отрасли», «Обслуживание», «Материалы» (описание и «Контакты» остаются как были)
    li = lambda a: f'<li>{a}</li>'
    ft_ind = ''.join(li(page_link(root, cur, s, t)) for s, t in INDUSTRIES)
    derat_ft = (f'<a href="./" aria-current="page">Дератизация для организаций</a>' if cur == DERAT
                else f'<a href="{root}{DERAT}/">Дератизация для организаций</a>')
    dez_ft = (f'<a href="./" aria-current="page">Дезинсекция для организаций</a>' if cur == 'dezinsektsiya'
              else f'<a href="{root}dezinsektsiya/">Дезинсекция для организаций</a>')
    dog_ft = (f'<a href="./" aria-current="page">Договор на дератизацию и дезинсекцию</a>' if cur == DOGOVOR
              else f'<a href="{root}{DOGOVOR}/">Договор на дератизацию и дезинсекцию</a>')
    ft_srv = li(derat_ft) + li(dez_ft) + li(dog_ft) + ''.join(li(anchor(root, s, t)) for s, t in SERVICE)
    # подпись с вложенным <span class="nw"> оборачиваем в один <span>: на телефоне ссылки подвала — inline-flex,
    # и без обёртки пробел перед вложенным тегом пропал бы
    wrap = lambda t: f'<span>{t}</span>' if '<' in t else t
    ft_mat = ''.join(li(page_link(root, cur, s, wrap(t))) for s, t in MATERIALS)
    cols = (f'<div><h4>Отрасли</h4><ul>{ft_ind}</ul></div>\n'
            f'      <div><h4>Обслуживание</h4><ul>{ft_srv}</ul></div>\n'
            f'      <div><h4>Материалы</h4><ul>{ft_mat}</ul></div>')
    return nav, mm, cols


def sub1(pat, rep, s):
    out, n = re.subn(pat, lambda m: rep, s, count=1, flags=re.S)
    assert n == 1, pat
    return out


def main():
    for rel, root, cur in PAGES:
        f = ROOT / rel
        s = f.read_text(encoding='utf-8')
        cta = re.search(r'<nav class="mmenu"[^>]*>.*?(<a href="#zayavka" class="btn btn-w btn-lg">.*?</a>)\s*</nav>', s, re.S).group(1)
        nav, mm, cols = (typo(x) for x in build(root, cur, cta))
        s = sub1(r'<nav class="nav" aria-label="Основное меню">.*?</nav>', nav, s)
        s = sub1(r'<nav class="mmenu" id="mmenu" aria-label="Мобильное меню">.*?</nav>', mm, s)
        s = sub1(r'<div><h4>(?:Объекты|Отрасли)</h4>.*?(?=\n\s*<div><h4>Контакты</h4>)', cols, s)
        # нижняя строка подвала: ссылка на согласие рядом с политикой
        if 'soglasie/">Согласие' not in s:
            s, n = re.subn(r'(<div class="fb">.*?<a href="((?:\.\./)*)privacy/">Политика конфиденциальности</a>)',
                           lambda m: m.group(1) + f'<a href="{m.group(2)}soglasie/">Согласие на обработку данных</a>',
                           s, count=1, flags=re.S)
            assert n == 1, 'нет строки .fb с политикой'
        s = s.replace('</footer>\n</footer>', '</footer>')  # лишний закрывающий тег во внутренних страницах
        f.write_text(s, encoding='utf-8')
        print('ok', rel)


if __name__ == '__main__':
    main()
