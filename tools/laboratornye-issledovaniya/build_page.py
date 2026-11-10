#!/usr/bin/env python3
"""Сборка страницы «Лабораторные исследования» — laboratornye-issledovaniya/index.html (10.11.2026).

Подача — как «Лабораторный центр» ЭКОСЕТИ (https://ekoset.ru/laboratornyj-czentr-3): плитки 14 направлений
с ценой «от» и прайс по группам. Своё: расчёт (кнопка «+», количество, сумма в панели внизу экрана и в заявке),
примеры наборов по видам объектов, определение, «Коротко», порядок работы, FAQ и нормативная база.
Цены — прайс ЭКОСЕТИ + 100 ₽ (решение владельца 10.11.2026), данные — data.py.
Аттестат аккредитации, юрлицо лаборатории и срок выдачи протоколов на странице не указываем (решение владельца).

Шаблон — pishchevoe-proizvodstvo/index.html (шапка, меню, подвал, плавающие кнопки, анимации), как у «Разработки ППК».

    python3 tools/laboratornye-issledovaniya/build_page.py   # build_site.py запускает его сам
    python3 tools/site/build_site.py

Цели Метрики (113675622): заявка — «audit», как на всех страницах (app.js); «Отправить расчёт» — «lab_raschet»;
«Добавить набор в расчёт» — «lab_nabor»; первая позиция в расчёте — «lab_pozitsiya». Цели lab_* нужно создать
в Метрике (тип «JavaScript-событие»).
"""
import html as H
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
sys.path.insert(0, str(HERE))
import data as D  # noqa: E402

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
SLUG = 'laboratornye-issledovaniya/'
URL = SITE + SLUG
TITLE = 'Лабораторные исследования для бизнеса: смывы, воздух, вода, замеры — цены в Москве — ПЕСТКОНТРОЛЬ Центр'
NAME = 'Лабораторные исследования по программе производственного контроля'
CRUMB = 'Лабораторные исследования'
OG_TITLE = 'Лабораторные исследования по ППК: смывы, воздух, вода, продукция и замеры — цены и расчёт'
DESC = ('Лабораторный контроль по ППК от 2 600 ₽: смывы от 310 ₽, воздух от 300 ₽, вода, пищевые продукты, '
        'микроклимат, освещённость и шум, стерильность, почва, испытания продукции. Москва и область, прайс и расчёт онлайн.')
OG_ALT = 'Лаборант берёт смыв с разделочного стола на кухне ресторана'
DATE = '2026-11-10'
AUTHOR = {'@type': 'Person', 'name': 'Марианна Семерина', 'jobTitle': 'Санитарный врач'}
DEFINITION = ('Лабораторный контроль по программе производственного контроля — исследования и измерения, которые '
              'организация или ИП проводит на своём объекте по плану-графику ППК: смывы, пробы воздуха и воды, '
              'исследования сырья и продукции, замеры микроклимата, освещённости и шума. Номенклатуру, объём и '
              'периодичность определяют по виду деятельности и вредным факторам (СП 1.1.1058-01, п. 2.5).')

FAQ = [
    ('Что такое лабораторный контроль по ППК?',
     'Это исследования и замеры, которые предусмотрены планом-графиком вашей программы производственного контроля: '
     'смывы, пробы воздуха и воды, исследования продукции, микроклимат, освещённость и шум. Номенклатуру, объём и '
     'периодичность определяют по виду деятельности и вредным факторам (СП 1.1.1058-01, п. 2.5). Результаты — '
     'протоколы, которые хранят в папке производственного контроля.'),
    ('Сколько стоят лабораторные исследования?',
     'Лабораторный контроль по ППК — от 2&nbsp;600&nbsp;₽ за комплекс. Отдельно: смывы — от 310&nbsp;₽ за точку, '
     'микробиология воздуха — от 300&nbsp;₽, микробиологический анализ воды — от 2&nbsp;350&nbsp;₽, микроклимат и '
     'освещённость — от 350&nbsp;₽ за точку. Итог зависит от числа точек и показателей; соберите '
     '<a href="#ceny">расчёт в прайсе</a> — назовём точную сумму до начала работы.'),
    ('Как часто нужно делать смывы и другие исследования?',
     'С периодичностью, которая указана в вашей программе производственного контроля: её определяют по виду '
     'деятельности и факторам риска. Отдельные сроки установлены правилами: например, исследования на легионеллы в '
     'системах кондиционирования и увлажнения — не реже 2 раз в год (СанПиН 3.3686-21, п. 132), смывы в бассейне — '
     'не реже 1 раза в квартал (СП 2.1.4284-26, подп. 35 п. 73).'),
    ('Какие исследования нужны ресторану или кафе?',
     'Обычно — смывы с оборудования, инвентаря и рук персонала, микробиология воздуха, вода, готовые блюда, '
     'микроклимат и освещённость. Точный состав — по ППК на принципах ХАССП. Пример набора с ценой — в блоке '
     '<a href="#nabory">«Какие исследования нужны вашему объекту»</a>.'),
    ('Можно ли заменить замеры результатами спецоценки условий труда?',
     'Да. Для производственного контроля можно использовать результаты измерений специальной оценки условий труда, '
     'если они проведены не раньше чем за 6 месяцев (52-ФЗ, ст. 32, п. 1.1). Остальные исследования — смывы, '
     'воздух, вода, продукция — проводят по плану-графику ППК.'),
    ('Вы приезжаете на объект?',
     'Да. Специалист лаборатории приезжает в Москве и Московской области в согласованное время и сам отбирает пробы: '
     'смывы, воздух, воду, продукцию, проводит замеры на рабочих местах.'),
    ('Что делать, если нет программы производственного контроля?',
     'Сначала нужна программа: перечень исследований и точек отбора берут из её плана-графика. Мы '
     '<a href="../razrabotka-ppk/">разрабатываем ППК</a> — от 5&nbsp;900&nbsp;₽ за 1 рабочий день, ППК по ХАССП — '
     'от 19&nbsp;900&nbsp;₽ за 3 рабочих дня.'),
    ('Входят ли смывы в санитарный аудит?',
     'Да. В <a href="../sanitarnyy-audit/">санитарный аудит</a> входят смывы и пробы воздуха; стоимость аудита — '
     'от 9&nbsp;000&nbsp;₽, а если после аудита вы заключаете договор на пест-контроль, она засчитывается.'),
    ('Делаете ли вы анализ почвы и испытания продукции?',
     'Да. Анализ почвы — микробиологический, химический, радиологический, на плодородие и гранулометрический. '
     'Испытания продукции — пищевой продукции, косметики, детских товаров, одежды и текстиля, упаковки, мебели, '
     'СИЗ, бытовой техники, оборудования и медицинских изделий. Состав испытаний подбираем по виду продукции и '
     'задаче, для которой нужен протокол.'),
]


from textlib import typeset, plain, cut  # noqa: E402  как в tools/razrabotka-ppk/build_page.py


def rub(n):
    return f'{n:,}'.replace(',', '\u00a0') + '\u00a0₽'


def pr(it):
    return ('от\u00a0' if it[4] else '') + rub(D.price(it))


def gmin(g):
    return min(D.price(it) for it in g[4])


# Страницы направлений (11.11.2026, build_subpages.py): плитка такого направления ведёт на его страницу,
# остальные плитки раскрывают прайс, как раньше. Адреса — от страницы раздела.
TILE_PAGE = {
    'smyvy': 'analiz-smyvov/', 'voda': 'analiz-vody/', 'pishcha': 'analiz-pishchevykh-produktov/',
    'sterilizatory': 'kontrol-sterilizatorov/', 'sterilnost': 'kontrol-sterilizatorov/#sterilnost',
    'obluchateli': 'kontrol-sterilizatorov/#obluchateli',
}
# «Подробнее» внутри раскрытого прайса группы: страницы направлений и статьи «Материалов»
MORE = {
    'smyvy': [('analiz-smyvov/', 'Анализ смывов'), ('../materialy/kak-berut-smyvy/', 'Как берут смывы')],
    'vozduh': [('analiz-vozdukha-rabochey-zony/', 'Анализ воздуха рабочей зоны')],
    'voda': [('analiz-vody/', 'Анализ воды')],
    'pishcha': [('analiz-pishchevykh-produktov/', 'Анализ пищевых продуктов')],
    'faktory': [('izmerenie-mikroklimata/', 'Измерение микроклимата'), ('zamer-osveshchennosti/', 'Замер освещённости'),
                ('../materialy/zamer-osveshchennosti-i-mikroklimata/', 'Как проходят замеры')],
    'rabochie-mesta': [('izmerenie-mikroklimata/', 'Измерение микроклимата'), ('zamer-osveshchennosti/', 'Замер освещённости')],
    'sterilnost': [('kontrol-sterilizatorov/#sterilnost', 'Анализ на стерильность')],
    'sterilizatory': [('kontrol-sterilizatorov/', 'Контроль работы стерилизаторов'),
                      ('../materialy/kontrol-raboty-sterilizatorov/', 'Методы, периодичность, журнал')],
    'obluchateli': [('kontrol-sterilizatorov/#obluchateli', 'Бактерицидные облучатели')],
}
# Все страницы направлений — строка ссылок под плитками
DIRECTIONS = [('analiz-smyvov/', 'Анализ смывов'), ('izmerenie-mikroklimata/', 'Измерение микроклимата'),
              ('zamer-osveshchennosti/', 'Замер освещённости'), ('analiz-vozdukha-rabochey-zony/', 'Анализ воздуха рабочей зоны'),
              ('analiz-pishchevykh-produktov/', 'Анализ пищевых продуктов'), ('analiz-vody/', 'Анализ воды'),
              ('kontrol-sterilizatorov/', 'Контроль работы стерилизаторов')]
ARR = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" '
       'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def more_nav(links, label='Подробнее', key='Подробнее'):
    a = ''.join(f'<a href="{h}"><span>{t}</span>{ARR}</a>' for h, t in links)
    return f'<nav class="more" aria-label="{label}"><span class="more-k">{key}</span>{a}</nav>'


def tiles(icons):
    out = ['    <div class="lb-tiles">']
    for code, name, ico, desc, its in D.GROUPS:
        img = (f'<img class="lb-tile-ic" src="../img/lab-i-{code}.webp" width="96" height="96" alt="" loading="lazy" decoding="async">')
        low = rub(gmin((code, name, ico, desc, its)))
        if code in TILE_PAGE:
            out.append(f'      <a class="card lb-tile lb-tile-pg" href="{TILE_PAGE[code]}">{img}'
                       f'<b>{name}</b><span class="lb-tile-d">{desc}</span><span class="lb-tile-p">от {low}{ARR}</span></a>')
        else:
            out.append(f'      <a class="card lb-tile" href="#g-{code}" data-open="{code}">{img}'
                       f'<b>{name}</b><span class="lb-tile-d">{desc}</span><span class="lb-tile-p">от {low}</span></a>')
    out.append('    </div>')
    out.append('    ' + more_nav(DIRECTIONS, 'Страницы направлений', 'Подробно о направлениях'))
    return '\n'.join(out)


OPEN = {'ppk', 'smyvy', 'vozduh'}


def prices(icons):
    out = ['    <div class="lb-price">']
    for code, name, ico, desc, its in D.GROUPS:
        op = ' open' if code in OPEN else ''
        n = len(its)
        cnt = f'{n} позиц' + ('ия' if n % 10 == 1 and n % 100 != 11 else 'ии' if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else 'ий')
        out.append(f'      <details class="lb-grp" id="g-{code}"{op}><summary><span class="lb-grp-ic">{icons[ico]}</span>'
                   f'<span class="lb-grp-n">{name}</span><span class="lb-grp-c">{cnt} · от {rub(min(D.price(i) for i in its))}</span><span class="pm" aria-hidden="true"></span></summary>')
        out.append('        <table class="d-table lb-tbl"><thead><tr><th scope="col">Услуга</th><th scope="col">Единица</th><th scope="col">Цена</th><th scope="col"><span class="sr-only">Расчёт</span></th></tr></thead><tbody>')
        for it in its:
            iid, iname, unit = it[0], it[1], it[2]
            out.append(f'          <tr data-id="{iid}"><td data-l="Услуга" class="lb-tn">{iname}</td><td data-l="Единица" class="lb-tu">{unit}</td>'
                       f'<td data-l="Цена" class="lb-tp">{pr(it)}</td><td class="lb-tc"><button type="button" class="lb-add" data-add="{iid}" '
                       f'aria-label="Добавить в расчёт: {H.escape(iname)}"><span aria-hidden="true">+</span></button></td></tr>')
        out.append('        </tbody></table>')
        if code in MORE:
            out.append('        ' + more_nav(MORE[code]))
        out.append('      </details>')
    out.append('    </div>')
    return '\n'.join(out)


def sets():
    byid = {it[0]: it for _, it in D.items()}
    out = ['    <div class="lb-sets">']
    for code, name, desc, lst in D.SETS:
        total = sum(D.price(byid[i]) * q for i, q in lst)
        li = ''.join(f'<li><span>{byid[i][1]}</span><span class="lb-set-q">{q}&nbsp;×&nbsp;{rub(D.price(byid[i]))}</span></li>' for i, q in lst)
        payload = H.escape(json.dumps(lst, ensure_ascii=False), quote=True)
        out.append(f'      <div class="card lb-set"><p class="lb-set-n">{name}</p><p class="lb-set-d">{desc}</p><ul class="lb-set-l">{li}</ul>'
                   f'<p class="lb-set-t">Пример: от {rub(total)}</p><div class="lb-set-f"><button type="button" class="btn btn-o btn-sm lb-set-b" data-set="{payload}">'
                   f'<span class="btn-t">Добавить набор в расчёт</span></button><span class="lb-set-ok" aria-live="polite"></span></div></div>')
    out.append('    </div>')
    return '\n'.join(out)


def faq_section():
    def qa(i, q, a):
        return (f'        <div class="card qa"><button aria-expanded="false" aria-controls="a{i}" id="q{i}"><span>{q}</span><span class="pm"></span></button>'
                f'<div class="ans" id="a{i}" role="region" aria-labelledby="q{i}"><div><p>{a}</p></div></div></div>')
    half = (len(FAQ) + 1) // 2
    html = ['<section class="s" id="voprosy">', '  <div class="wrap">',
            '    <div class="head"><div class="eyebrow">Вопросы</div><h2>Вопросы о <em>лабораторных исследованиях</em></h2></div>',
            '    <div class="faq">']
    n = 0
    for col in (FAQ[:half], FAQ[half:]):
        html.append('      <div class="faq-col">')
        for q, a in col:
            n += 1
            html.append(qa(n, q, a))
        html.append('      </div>')
    html += ['    </div>', '  </div>', '</section>']
    return '\n'.join(html)


TYPE_SELECT = ('<div class="field full"><label class="sr-only" for="f-type">Вид объекта</label><select id="f-type" name="type" required>'
               '<option value="" selected>Вид объекта</option><option>Ресторан или кафе</option><option>Магазин или торговая сеть</option>'
               '<option>Пищевое производство</option><option>Склад, логистика</option><option>Гостиница</option>'
               '<option value="Другое">Медицинская организация</option><option value="Другое">Салон красоты</option>'
               '<option value="Другое">Бассейн, фитнес</option><option value="Другое">Школа, детский сад</option>'
               '<option value="Другое">Офис, бизнес-центр</option><option>Фармацевтическое производство</option><option>Другое</option>'
               '</select><small class="ferr">Выберите вид объекта</small></div>')


def json_ld():
    org = {'@type': 'Organization', '@id': SITE + '#org', 'name': 'ПЕСТКОНТРОЛЬ Центр',
           'legalName': 'ООО «Центр дезинфекционных услуг»', 'url': SITE,
           'telephone': '+7 495 104-35-70', 'email': 'b2b@pestcontrol-center.ru'}
    catalog = {'@type': 'OfferCatalog', 'name': 'Цены на лабораторные исследования', 'itemListElement': [
        {'@type': 'OfferCatalog', 'name': g[1], 'itemListElement': [
            {'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': it[1]},
             'priceSpecification': {'@type': 'UnitPriceSpecification', ('minPrice' if it[4] else 'price'): D.price(it),
                                    'priceCurrency': 'RUB', 'unitText': it[2]}} for it in g[4]]} for g in D.GROUPS]}
    graph = [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': CRUMB, 'item': URL}]},
        {'@type': 'Service', '@id': URL + '#service', 'name': NAME,
         'alternateName': ['Лабораторный контроль по ППК', 'Анализ смывов', 'Анализ воды', 'Анализ воздуха', 'Замеры микроклимата и освещённости'],
         'serviceType': 'Лабораторные исследования и измерения по программе производственного контроля',
         'description': DESC, 'url': URL, 'provider': org,
         'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
         'hasOfferCatalog': catalog},
        {'@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE, 'description': DESC, 'inLanguage': 'ru',
         'datePublished': DATE, 'dateModified': DATE, 'author': AUTHOR, 'about': [{'@id': URL + '#service'}, {'@id': URL + '#term'}],
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': SITE + 'img/lab-hero.webp', 'width': 1920, 'height': 1072}},
        {'@type': 'DefinedTerm', '@id': URL + '#term', 'name': 'Лабораторный контроль по программе производственного контроля',
         'description': DEFINITION},
        {'@type': 'FAQPage', '@id': URL + '#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in FAQ]},
    ]
    return '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False) + '</script>'


def calc_data():
    return {it[0]: [it[1], it[2], D.price(it), 1 if it[4] else 0] for _, it in D.items()}


def main():
    tpl = (ROOT / 'pishchevoe-proizvodstvo' / 'index.html').read_text(encoding='utf-8')
    icons = json.loads((ROOT / 'tools' / 'site' / 'icons.json').read_text(encoding='utf-8'))
    icons.update(json.loads((HERE / 'icons-lab.json').read_text(encoding='utf-8')))

    head = tpl[:tpl.index('<style>')]
    rep = [
        (r'<title>[^<]*</title>', f'<title>{TITLE}</title>'),
        (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">'),
        (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">'),
        (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">'),
        (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_TITLE}">'),
        (r'<meta property="og:description" content="[^"]*">',
         f'<meta property="og:description" content="{DESC}">\n'
         f'<meta property="og:image" content="{SITE}img/lab-og.jpg">\n'
         '<meta property="og:image:type" content="image/jpeg">\n'
         '<meta property="og:image:width" content="1200">\n'
         '<meta property="og:image:height" content="630">\n'
         f'<meta property="og:image:alt" content="{OG_ALT}">\n'
         '<meta name="twitter:card" content="summary_large_image">'),
        (r'<link rel="preload" href="\.\./img/food-hero\.webp"[^>]*>\n<link rel="preload" href="\.\./img/food-hero-mob\.webp"[^>]*>',
         '<link rel="preload" as="image" media="(min-width:761px)" imagesrcset="../img/lab-hero-1440.webp 1440w, ../img/lab-hero.webp 1920w" imagesizes="100vw" fetchpriority="high">\n'
         '<link rel="preload" as="image" media="(max-width:760px)" imagesrcset="../img/lab-hero-mob-760.webp 760w, ../img/lab-hero-mob.webp 1024w" imagesizes="100vw" fetchpriority="high">'),
    ]
    for pat, new in rep:
        head, n = re.subn(pat, lambda m: new, head, count=1)
        assert n == 1, 'шаблон: не найдено ' + pat
    assert 'food-hero' not in head
    css = tpl[tpl.index('<style>') + 7:tpl.index('</style>')]
    css += '\n' + (HERE / 'page.css').read_text(encoding='utf-8').strip()

    top = tpl[tpl.index('</head>'):tpl.index('<main id="main"')]
    top = top.replace('<body class="d-page">', '<body class="d-page lb-page">', 1)
    assert 'lb-page' in top

    main = (HERE / 'main.html').read_text(encoding='utf-8')
    main = main.replace('<!--TILES-->', tiles(icons)).replace('<!--PRICES-->', prices(icons)).replace('<!--SETS-->', sets())
    main = main.replace('<!--FAQ-->', faq_section()).replace('<!--TYPE_SELECT-->', TYPE_SELECT)
    main = typeset(main)
    main = re.sub(r'<!--ICON:([a-z0-9-]+)-->', lambda m: icons[m.group(1)], main)
    contacts = cut(tpl, '      <div class="cta-contacts"', '    </div>\n    <form', after=False).replace(' data-fade', '')
    main = main.replace('<!--CTA_CONTACTS-->\n', contacts.rstrip('\n') + '\n')
    assert '<!--' not in main.replace('<!-- ', ''), 'остались метки в main.html'

    bottom = tpl[tpl.index('</main>') + len('</main>'):tpl.index('<script>\n/* Предпросмотр')]
    page_js = cut(tpl, '<script>\n/* Предпросмотр', '</script>', after=True)
    pv = re.match(r'<script>\n(/\* Предпросмотр[^\n]*\*/\n\(function\(\)\{.*?\n?\}\)\(\);)', page_js, re.S)
    assert pv, 'шаблон: не найден скрипт предпросмотра'
    page_js = '<script>\n' + pv.group(1) + '\n</script>'
    li = tpl.index('<script>\n  /* скрипты анимаций')
    loader = tpl[li:tpl.index('</script>', li) + len('</script>')] + '\n'
    calc_js = ('<script>window.LB=' + json.dumps(calc_data(), ensure_ascii=False, separators=(',', ':')) + ';\n'
               + (HERE / 'calc.js').read_text(encoding='utf-8').strip() + '</script>\n')

    html = (head + '<style>' + css + '</style>\n' + json_ld() + '\n' + top + main + bottom + page_js + '\n'
            + loader + calc_js + '</body>\n</html>\n')
    out = ROOT / 'laboratornye-issledovaniya' / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print('ok', out.relative_to(ROOT), len(html) // 1024, 'КБ')


if __name__ == '__main__':
    main()
