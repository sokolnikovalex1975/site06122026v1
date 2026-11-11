#!/usr/bin/env python3
"""Общее меню сайта site06122026v1 (06.11.2026): шапка, мобильное меню и подвал на всех страницах.

    Услуги ▾ · Отрасли ▾ · Договор · Метод IPM · Цена · Материалы ▾
    (в «Услугах» с 06.11.2026 — очистка и дезинфекция вентиляции, с 08.11.2026 — «Разработка ППК» (/razrabotka-ppk/):
    одна страница услуги для ППК без ХАССП и ППК по ХАССП; страница образца ППК по ХАССП остаётся в «Материалах»)

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
    # с 11.11.2026 — первый пункт: главная (основная услуга сайта). На главной он отмечен как текущая страница
    # (href="./", aria-current) — услуга остаётся в общем списке. Заменил якорь «Пест-контроль по системе IPM» (#podhod):
    # тот же блок открывает пункт шапки «Метод IPM»
    ('', '<span class="nw">Пест-контроль</span> для бизнеса'),
    ('dezinfektsiya', 'Дезинфекция для организаций'),
    ('deratizatsiya', 'Дератизация для организаций'),
    ('dezinsektsiya', 'Дезинсекция для организаций'),
    ('deratizatsiya-i-dezinsektsiya', 'Дератизация и дезинсекция'),  # с 11.11.2026 — комплекс по одному договору
    ('sanitarnyy-audit', 'Санитарный аудит <span class="nw">(СЭС-аудит)</span>'),
    ('laboratornye-issledovaniya', 'Лабораторные исследования'),  # с 10.11.2026
    ('razrabotka-ppk', 'Разработка ППК'),  # с 08.11.2026 — ППК без ХАССП и по ХАССП на одной странице /razrabotka-ppk/
    ('normativnaya-baza/dokumenty-dlya-rospotrebnadzora', 'Документы для Роспотребнадзора'),
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
    ('biznes-tsentry-torgovye-tsentry-predpriyatiya', 'Бизнес-центры, ТЦ и предприятия'),  # с 11.11.2026 (tools/bctc)
]
# Подпункты отрасли (с 11.11.2026, решение владельца «найти место в меню, в верхнем и в нижнем»): страницы «услуга +
# сфера» стоят под своей отраслью — в шапке, мобильном меню и подвале, с отступом (класс nav-sub / ft-sub)
INDUSTRY_SUB = {
    'restorany-i-kafe': [('dezinsektsiya/restorany-i-kafe', 'Дезинсекция кафе и ресторанов'),
                         ('deratizatsiya/restorany-i-kafe', 'Дератизация ресторанов и кафе')],
}
DOGOVOR = 'dogovor-deratizatsiya-dezinsektsiya'
DERAT = 'deratizatsiya'
VENT = 'ochistka-dezinfektsiya-ventilyatsii'
SAN = 'sanitarnyy-audit'
RPPK = 'razrabotka-ppk'
LAB = 'laboratornye-issledovaniya'  # «Лабораторные исследования» (с 10.11.2026)
DD = 'deratizatsiya-i-dezinsektsiya'  # «Дератизация и дезинсекция для организаций» (с 11.11.2026)
MATERIALS = [  # слова через дефис не переносим (класс nw, как в остальных текстах сайта)
    ('normativnaya-baza', 'Нормативная база'),  # раздел «Нормативная база» (tools/normativnaya-baza)
    ('normativnaya-baza/dokumenty-dlya-rospotrebnadzora', 'Документы для Роспотребнадзора'),  # с 08.11.2026; в подвале — после «Проверочных листов»
    ('normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii', 'Оценка эффективности дератизации и дезинсекции'),  # с 11.11.2026
    ('materialy/programma-pest-kontrolya', 'Программа <span class="nw">пест-контроля</span>'),
    ('materialy/zhurnal-pest-kontrolya', 'Журнал <span class="nw">пест-контроля</span>'),
    ('materialy/skhema-tochek-pest-kontrolya', 'Схема точек <span class="nw">пест-контроля</span>'),  # с 11.11.2026
    ('materialy/akt-deratizatsii-i-dezinsektsii', 'Акт дератизации и дезинсекции'),  # с 11.11.2026
    ('materialy/pest-menedzhment-ili-razovaya-obrabotka', '<span class="nw">Пест-менеджмент</span> или разовая обработка'),
    ('materialy/programma-proizvodstvennogo-kontrolya-haccp', 'Программа производственного контроля по ХАССП'),
]
FOOTER_MAT_EXTRA = {  # в подвале под пунктом — ещё одна ссылка (в шапке её нет)
    'normativnaya-baza': ('normativnaya-baza/proverochnye-listy', 'Проверочные листы 2026'),
}
SERVICE = [  # блоки главной («Документы для проверок» → страница «Документы для Роспотребнадзора» в «Материалах», 08.11.2026)
    ('etapy', 'Этапы работы'), ('vrediteli', 'Вредители'),
    ('usloviya', 'Цена'), ('voprosy', 'Вопросы'),
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
    (DD + '/index.html', '../', DD),
    (VENT + '/index.html', '../', VENT),
    (SAN + '/index.html', '../', SAN),
    (RPPK + '/index.html', '../', RPPK),
    (LAB + '/index.html', '../', LAB),
    # страницы направлений раздела «Лабораторные исследования» (с 11.11.2026)
    (LAB + '/analiz-smyvov/index.html', '../../', LAB + '/analiz-smyvov'),
    (LAB + '/izmerenie-mikroklimata/index.html', '../../', LAB + '/izmerenie-mikroklimata'),
    (LAB + '/zamer-osveshchennosti/index.html', '../../', LAB + '/zamer-osveshchennosti'),
    (LAB + '/analiz-vozdukha-rabochey-zony/index.html', '../../', LAB + '/analiz-vozdukha-rabochey-zony'),
    (LAB + '/analiz-pishchevykh-produktov/index.html', '../../', LAB + '/analiz-pishchevykh-produktov'),
    (LAB + '/analiz-vody/index.html', '../../', LAB + '/analiz-vody'),
    (LAB + '/kontrol-sterilizatorov/index.html', '../../', LAB + '/kontrol-sterilizatorov'),
    (DOGOVOR + '/index.html', '../', DOGOVOR),
    # «Защита от проникновения грызунов» (11.11.2026, пока только GitHub): в «Услуги» меню не добавлена до выкладки на сайт
    ('zashchita-ot-proniknoveniya-gryzunov/index.html', '../', 'zashchita-ot-proniknoveniya-gryzunov'),
    # страницы «услуга + сфера» для общепита (tools/restorany-uslugi), с 11.11.2026 — в меню не добавляются
    ('dezinsektsiya/restorany-i-kafe/index.html', '../../', 'dezinsektsiya/restorany-i-kafe'),
    (DERAT + '/restorany-i-kafe/index.html', '../../', DERAT + '/restorany-i-kafe'),
    ('pishchevoe-proizvodstvo/index.html', '../', 'pishchevoe-proizvodstvo'),
    ('restorany-i-kafe/index.html', '../', 'restorany-i-kafe'),
    ('magaziny-i-torgovye-seti/index.html', '../', 'magaziny-i-torgovye-seti'),
    ('gostinitsy/index.html', '../', 'gostinitsy'),
    ('farmatsevticheskie-proizvodstva/index.html', '../', 'farmatsevticheskie-proizvodstva'),
    ('sklady-i-logistika/index.html', '../', 'sklady-i-logistika'),
    ('biznes-tsentry-torgovye-tsentry-predpriyatiya/index.html', '../', 'biznes-tsentry-torgovye-tsentry-predpriyatiya'),
    ('materialy/pest-menedzhment-ili-razovaya-obrabotka/index.html', '../../', 'materialy/pest-menedzhment-ili-razovaya-obrabotka'),
    ('materialy/index.html', '../', 'materialy'),
    ('materialy/programma-pest-kontrolya/index.html', '../../', 'materialy/programma-pest-kontrolya'),
    ('materialy/zhurnal-pest-kontrolya/index.html', '../../', 'materialy/zhurnal-pest-kontrolya'),
    # акт и схема точек (tools/materialy-dokumenty), с 11.11.2026 — в «Материалах» шапки, мобильного меню и подвала (MATERIALS)
    ('materialy/akt-deratizatsii-i-dezinsektsii/index.html', '../../', 'materialy/akt-deratizatsii-i-dezinsektsii'),
    ('materialy/skhema-tochek-pest-kontrolya/index.html', '../../', 'materialy/skhema-tochek-pest-kontrolya'),
    ('materialy/programma-proizvodstvennogo-kontrolya-haccp/index.html', '../../', 'materialy/programma-proizvodstvennogo-kontrolya-haccp'),
    # статьи о лабораторном контроле (с 11.11.2026)
    ('materialy/kak-berut-smyvy/index.html', '../../', 'materialy/kak-berut-smyvy'),
    ('materialy/zamer-osveshchennosti-i-mikroklimata/index.html', '../../', 'materialy/zamer-osveshchennosti-i-mikroklimata'),
    ('materialy/kontrol-raboty-sterilizatorov/index.html', '../../', 'materialy/kontrol-raboty-sterilizatorov'),
    ('normativnaya-baza/index.html', '../', 'normativnaya-baza'),
    ('normativnaya-baza/proverochnye-listy/index.html', '../../', 'normativnaya-baza/proverochnye-listy'),
    ('normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.html', '../../', 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora'),
    ('normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/index.html', '../../', 'normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii'),
]
LEGAL = [('privacy/index.html', '../', 'privacy'), ('soglasie/index.html', '../', 'soglasie')]


def page_link(root, cur, slug, text, cls=''):
    if slug.startswith('#'):  # карточка на главной
        return anchor(root, slug[1:], text, cls)
    c = f' class="{cls}"' if cls else ''
    if slug == cur:
        return f'<a href="./"{c} aria-current="page">{text}</a>'
    if slug == '':  # главная
        return f'<a href="{root or "./"}"{c}>{text}</a>'
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
    in_usl = cur != '' and cur in ('dezinfektsiya', DERAT, 'dezinsektsiya', DD, VENT, SAN, RPPK, LAB) or cur.startswith(LAB + '/') or cur.startswith('dezinsektsiya/') or cur.startswith(DERAT + '/')
    in_ind = any(s == cur for s, _ in INDUSTRIES)
    in_mat = cur.startswith('materialy') or cur.startswith('normativnaya-baza')
    # шапка: Услуги ▾ · Отрасли ▾ · Договор · Метод IPM · Цена · Материалы ▾
    usl_items = ''.join(page_link(root, cur, s, one(t) + ARR) for s, t in USLUGI)
    # «Все услуги» (с 11.11.2026) — блок #vse-uslugi перед заявкой (tools/site/services_block.py) на этой же странице;
    # на политике и согласии блока нет — ссылка ведёт к блоку на главной
    vu = (root + '#vse-uslugi') if cur in ('privacy', 'soglasie') else '#vse-uslugi'
    usl_items += f'<a href="{vu}" class="nav-dd-all">Все услуги{ARR}</a>'
    ind_items = ''.join(page_link(root, cur, s, t + ARR) + ''.join(page_link(root, cur, s2, t2 + ARR, 'nav-sub') for s2, t2 in INDUSTRY_SUB.get(s, []))
                        for s, t in INDUSTRIES)
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
    sub_usl = ''.join(page_link(root, cur, s, one(t)) for s, t in USLUGI) + f'<a href="{vu}">Все услуги</a>'
    sub_ind = ''.join(page_link(root, cur, s, t) + ''.join(page_link(root, cur, s2, t2, 'nav-sub') for s2, t2 in INDUSTRY_SUB.get(s, []))
                      for s, t in INDUSTRIES) + anchor(root, 'otrasli', 'Все отрасли')
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
              + ''.join(li(anchor(root, s, t)) for s, t in SERVICE))
    ft_ind = ''.join(li(page_link(root, cur, s, t)) + ''.join(f'<li class="ft-sub">{page_link(root, cur, s2, t2)}</li>' for s2, t2 in INDUSTRY_SUB.get(s, []))
                     for s, t in INDUSTRIES)
    ft_mat = ''.join(li(page_link(root, cur, s, wrap(t)))
                     + (li(page_link(root, cur, *FOOTER_MAT_EXTRA[s][:1], wrap(FOOTER_MAT_EXTRA[s][1]))) if s in FOOTER_MAT_EXTRA else '')
                     for s, t in MATERIALS) + li(page_link(root, cur, 'materialy', 'Все материалы'))
    cols = (f'<div><h4>Услуги</h4><ul>{ft_srv}</ul></div>\n'
            f'      <div><h4>Отрасли</h4><ul>{ft_ind}</ul></div>\n'
            f'      <div><h4>Материалы</h4><ul>{ft_mat}</ul></div>')
    return nav, mm, cols


def sub1(pat, rep, s):
    out, n = re.subn(pat, lambda m: rep, s, count=1, flags=re.S)
    assert n == 1, pat
    return out


# ---------------------------------------------------------------- поиск по сайту (tools/search)
# Лупа в шапке на всех страницах; по первому нажатию (или клавише «/») загружаются search.min.js и search-index.json.
# В <head> — только стили кнопки и загрузчик (около 1,5 КБ). Блок стоит перед <style data-fx> (tools/site/fx.py), если его нет —
# перед <style id="m-crumbs">, иначе перед </head>: так его место одинаково в сборке и в файлах с сайта
# (tools/deploy/patch-2026-11-08-poisk.py), хотя fx.py и mobile_crumbs.py переставляют свои блоки в конец <head>.
SEARCH_V = '20261108'  # версия search.min.js и search-index.json — та же, что V в tools/search/build_index.py
SRCH_BTN = ('<button class="srch-btn" type="button" data-srch aria-label="Поиск по сайту" aria-haspopup="dialog">'
            '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<path d="m20 20-3.6-3.6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>')
# Раскладка шапки с лупой (проверена на 320–2560 px по всем страницам, /home/user/qa/hdrfit2.mjs):
# от 761 px лупа без круга стоит вплотную к телефону, мессенджеры в шапке скрыты — Max и Telegram остаются
# в плавающих кнопках .fab справа внизу (на сайте шапка и раньше не вмещала их рядом с кнопкой на 1381–1800 px);
# до 900 px «ПЕСТКОНТРОЛЬ» и «Центр» в две строки; на телефонах кнопки 44 → 40 → 38 px.
SRCH_CSS = ('<style id="srch-st">/* лупа поиска в шапке и раскладка шапки с ней (tools/menu/apply_menu.py) */'
            '.srch-btn{flex:none;width:44px;height:44px;padding:0;border-radius:50%;display:grid;place-items:center;'
            'background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);color:#fff;cursor:pointer;'
            'transition:color .25s,border-color .3s,background .3s,transform .35s cubic-bezier(.16,1,.3,1)}'
            '.srch-btn:hover{border-color:#7c86ff;background:rgba(97,95,255,.2);transform:translateY(-2px)}'
            '.srch-btn:focus-visible{outline:2px solid #7c86ff;outline-offset:2px}'
            '.srch-btn svg{width:18px;height:18px;display:block}'
            '@media (min-width:761px){.hdr .wrap{gap:16px}.hdr .msg{display:none}'
            '.srch-btn{width:38px;height:38px;background:none;border-color:transparent;color:var(--t2);margin-right:calc(4px - clamp(14px,2vw,40px))}'
            '.srch-btn svg{width:20px;height:20px}'
            '.srch-btn:hover{color:#fff;background:rgba(255,255,255,.07);border-color:rgba(255,255,255,.1);transform:none}}'
            '@media (min-width:761px) and (max-width:1440px){.hdr-right{gap:18px}.srch-btn{margin-right:-14px}}'
            '@media (min-width:761px) and (max-width:1000px){.hdr-right{gap:12px}.srch-btn{margin-right:-8px}}'
            '@media (max-width:900px){.logo-txt{display:flex;flex-direction:column;align-items:flex-start}.logo-sub{margin:0}}'
            '@media (max-width:760px){.hdr .wrap{gap:12px}.hdr-right{gap:8px}}'
            '@media (max-width:400px){.hdr .wrap{gap:10px}.srch-btn{width:40px;height:40px}}'
            '@media (max-width:360px){.hdr .wrap{gap:8px}.hdr-right{gap:6px}.srch-btn,.phone i,.burger{width:38px;height:38px}}'
            '@media (max-width:340px){.logo-mark{display:none}.logo-sub{display:block}}'
            # подпункты отрасли (INDUSTRY_SUB): с отступом и чуть мельче
            '.nav-dd-panel a.nav-sub{padding:8px 14px 8px 30px;font-size:14px;color:var(--t3)}'
            '.nav-dd-panel a.nav-sub::before{content:"";position:absolute;left:16px;top:50%;width:7px;height:1px;background:var(--line2)}'
            '.nav-dd-panel a.nav-sub{position:relative}.nav-dd-panel a.nav-sub:hover,.nav-dd-panel a.nav-sub[aria-current]{color:#fff}'
            '.mm-sub a.nav-sub{padding-left:40px;font-size:16px;color:var(--t3)}'
            '.ft li.ft-sub{padding-left:14px;font-size:14px;position:relative}'
            '.ft li.ft-sub::before{content:"";position:absolute;left:0;top:50%;width:7px;height:1px;background:var(--line2)}</style>')
SRCH_JS = ('<script id="srch-js">/* поиск по сайту: движок и индекс загружаются по первому нажатию на лупу или «/» (tools/search) */'
           '(function(r,v){var d=document,ld=0,w=null;function go(o){if(window.PCSearch)return window.PCSearch.open(r,v,o);w=o;if(ld)return;ld=1;'
           'var s=d.createElement("script");s.src=r+"search.min.js?v="+v;s.async=true;s.onload=function(){window.PCSearch&&window.PCSearch.open(r,v,w)};'
           's.onerror=function(){ld=0};d.head.appendChild(s)}'
           'd.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest("[data-srch]");if(b){e.preventDefault();go({btn:b})}});'
           'd.addEventListener("keydown",function(e){if(e.key!=="/"||e.ctrlKey||e.metaKey||e.altKey)return;var t=e.target,n=t&&t.tagName;'
           'if(n==="INPUT"||n==="TEXTAREA"||n==="SELECT"||t.isContentEditable)return;e.preventDefault();go({})});'
           # переход из поиска к вопросу (#q3): когда app.js подключит FAQ, ответ раскрывается сам
           'if(/^#q\\d+$/.test(location.hash)){var c=0,t=setInterval(function(){var b=d.getElementById(location.hash.slice(1));'
           'if(b&&d.documentElement.classList.contains("anim-ready")){clearInterval(t);if(b.getAttribute("aria-expanded")==="false")b.click()}'
           'else if(++c>60)clearInterval(t)},150)}})("ROOT","' + SEARCH_V + '");</script>')
SRCH_HEAD_RE = re.compile(r'<style id="srch-st">.*?</style><script id="srch-js">.*?</script>\n', re.S)


def search_ui(s, root):
    """Лупа в шапке и блок поиска в <head>; повторный запуск заменяет прежний блок (можно применять к файлам с сайта)."""
    s = SRCH_HEAD_RE.sub('', s)
    block = SRCH_CSS + SRCH_JS.replace('"ROOT"', '"' + (root or './') + '"') + '\n'
    head = s[:s.index('</head>')]
    for mark in ('<style data-fx>', '<style id="m-crumbs">'):
        if mark in head:
            s = s.replace(mark, block + mark, 1)
            break
    else:
        assert s.count('</head>') == 1, 'не один </head>'
        s = s.replace('</head>', block + '</head>', 1)
    if 'class="srch-btn"' not in s:
        s, n = re.subn(r'(<div class="hdr-right">\n(\s*))', lambda m: m.group(1) + SRCH_BTN + '\n' + m.group(2), s, count=1)
        assert n == 1, 'нет .hdr-right в шапке'
    return s


def apply_page(s, root, cur):
    """Шапка, мобильное меню, подвал и поиск одной страницы (тот же код правит страницы, снятые с сайта)."""
    cta = re.search(r'<nav class="mmenu"[^>]*>.*?(<a href="(?:\.\./)*#zayavka" class="btn btn-w btn-lg">.*?</a>)\s*</nav>', s, re.S).group(1)
    nav, mm, cols = (typo(x) for x in build(root, cur, cta))
    s = sub1(r'<nav class="nav" aria-label="Основное меню">.*?</nav>', nav, s)
    s = sub1(r'<nav class="mmenu" id="mmenu" aria-label="Мобильное меню">.*?</nav>', mm, s)
    s = sub1(r'<div><h4>(?:Объекты|Отрасли|Услуги)</h4>.*?(?=\n\s*<div><h4>Контакты</h4>)', cols, s)
    return search_ui(s, root)


def main():
    for rel, root, cur in PAGES + LEGAL:
        f = ROOT / rel
        s = f.read_text(encoding='utf-8')
        s = apply_page(s, root, cur)
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
