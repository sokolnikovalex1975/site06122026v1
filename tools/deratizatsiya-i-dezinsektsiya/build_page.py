#!/usr/bin/env python3
"""Сборка страницы «Дератизация и дезинсекция для организаций» — deratizatsiya-i-dezinsektsiya/index.html (11.11.2026).

Комплекс дератизации и дезинсекции по одному договору: от 4 900 ₽/мес для любого типа объекта (решение владельца
10.11.2026). Тексты — черновик, согласованный владельцем («Страница Дератизация и дезинсекция/Черновик контента v0.md»
в файлах проекта); семантика — Keys.so, 10.11.2026. Страница не повторяет блоки /deratizatsiya/, /dezinsektsiya/ и
договора: на ней «Коротко», выбор «комплекс или одна услуга», цены комплекса со сравнением, график на год по сезонам,
один комплект документов, блок для закупок, ссылка на дезинфекцию, вопросы и заявка.

Шаблон — pishchevoe-proizvodstvo/index.html (шапка, меню, подвал, плавающие кнопки, анимации), как у «Лабораторных
исследований» и «Разработки ППК».

    python3 tools/deratizatsiya-i-dezinsektsiya/build_page.py   # build_site.py запускает его сам
    python3 tools/site/build_site.py

Цель Метрики (113675622) — «audit» после отправки заявки, как на всех страницах (app.js). Тип объекта — значения,
которые принимает send.php; площадь, «Что нужно» и адрес страницы уходят в поле msg (скрипт страницы).
Кнопка «Запросить коммерческое предложение» выбирает в форме «КП для закупки».
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
sys.path.insert(0, str(HERE))
from textlib import typeset, plain, cut  # noqa: E402

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
SLUG = 'deratizatsiya-i-dezinsektsiya/'
URL = SITE + SLUG
TITLE = 'Дератизация и дезинсекция в Москве — цены для юридических лиц — ПЕСТКОНТРОЛЬ Центр'
NAME = 'Дератизация и дезинсекция для организаций'
CRUMB = 'Дератизация и дезинсекция'
OG_TITLE = 'Дератизация и дезинсекция для организаций — комплекс от 4 900 ₽/мес'
DESC = ('Дезинсекция и дератизация для организаций в Москве и области: комплекс от 4 900 ₽/мес, общий график визитов, '
        'акты и журнал. Цены для юрлиц, документы для закупок.')
OG_ALT = 'Специалист проверяет контейнер для грызунов в складском помещении ресторана, рядом ловушка для насекомых'
DATE = '2026-11-11'
PRICE = 4900
LIC = 'https://fp.rospotrebnadzor.ru/licen/?oper=search&amp;numb_history=&amp;numb=&amp;firmget_name=&amp;ogrn_inn_nza=7714462211'
SANPIN = 'http://pravo.gov.ru/proxy/ips/?docbody=&amp;nd=602107773'
ARR = ('<svg class="dd-arr" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" '
       'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')

FAQ = [
    ('Чем дератизация отличается от дезинсекции?',
     'Дератизация — меры против грызунов, дезинсекция — против насекомых и других членистоногих. У них разные методы '
     'и оборудование, но на одном объекте обе услуги можно вести по одному договору и графику.'),
    ('Как часто нужно проводить дератизацию и дезинсекцию?',
     'На объектах особого эпидемиологического значения — пищевых производствах, в общепите, торговле продуктами, '
     'гостиницах — обследования на насекомых проводят не реже 2 раз в месяц, а дератизацию — по результатам '
     'ежемесячной оценки (пп. 101 и 110 СанПиН 3.3686-21). Для остальных объектов кратность определяем после '
     'обследования и закрепляем в графике.'),
    ('Можно ли заключить один договор на дератизацию и дезинсекцию?',
     'Да. В договоре обе услуги, общий график и одна ежемесячная оплата. Образец договора — на странице '
     '<a href="../dogovor-deratizatsiya-dezinsektsiya/">договора на дератизацию и дезинсекцию</a>.'),
    ('Сколько стоит дератизация и дезинсекция для юридических лиц?',
     'Комплекс — от 4&nbsp;900&nbsp;₽ в месяц. Точную цену называем после бесплатного выезда: она зависит от площади, '
     'числа зон и точек контроля, кратности визитов.'),
    ('Какие организации проводят дератизацию и дезинсекцию?',
     'С 1 марта 2025 года эти услуги оказывают только по лицензии. Наша лицензия — № Л064-00111-77/01942445, её можно '
     f'проверить в <a href="{LIC}" target="_blank" rel="noopener">реестре Роспотребнадзора</a>.'),
    ('Работаете ли вы в Московской области?',
     'Да. Выезд и расчёт по Москве и Московской области бесплатны.'),
    ('Какой код ОКПД 2 указать в закупке?',
     '81.29.11.000 «Услуги по дезинфекции, дезинсекции и дератизации».'),
]

# график на год: сезон, подпись, месяцы (короткое имя, полное), в каких месяцах усиленный контроль (грызуны, насекомые)
YEAR = [
    ('vesna', 'Весна', 'осмотр периметра после зимы, подготовка к сезону летающих насекомых',
     [('Мар', 'март', 1, 0), ('Апр', 'апрель', 0, 0), ('Май', 'май', 0, 1)]),
    ('leto', 'Лето', 'больше мух и муравьёв — усиливаем контроль у входов, площадок для отходов и в зонах приёмки',
     [('Июн', 'июнь', 0, 1), ('Июл', 'июль', 0, 1), ('Авг', 'август', 0, 1)]),
    ('osen', 'Осень', 'грызуны ищут укрытие в зданиях — проверяем ворота, рампы и проходы коммуникаций',
     [('Сен', 'сентябрь', 1, 0), ('Окт', 'октябрь', 1, 0), ('Ноя', 'ноябрь', 1, 0)]),
    ('zima', 'Зима', 'контроль внутренних зон, складов и подвальных помещений',
     [('Дек', 'декабрь', 0, 0), ('Янв', 'январь', 0, 0), ('Фев', 'февраль', 0, 0)]),
]

TYPE_SELECT = ('<div class="field full"><label class="sr-only" for="f-type">Тип объекта</label><select id="f-type" name="type" required>'
               '<option value="" selected>Тип объекта</option><option>Ресторан или кафе</option><option>Магазин или торговая сеть</option>'
               '<option>Склад, логистика</option><option>Пищевое производство</option><option>Фармацевтическое производство</option>'
               '<option>Гостиница</option><option>Другое</option>'
               '</select><small class="ferr">Выберите тип объекта</small></div>')

PAGE_JS = (
    "<script>/* Форма: площадь, «Что нужно» и страница — в поле msg, которое читает send.php;"
    " кнопка «Запросить коммерческое предложение» выбирает в форме «КП для закупки» */\n"
    "(function(d){var f=d.getElementById('form');if(!f)return;"
    "d.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-goal]');"
    "if(a&&f.elements.goal)f.elements.goal.value=a.getAttribute('data-goal');});"
    "d.addEventListener('submit',function(ev){if(ev.target!==f)return;var e=f.elements,a=e.area.value.trim(),g=e.goal.value;"
    "e.msg.value='Тип объекта: '+(e.type.value||'не выбран')+(a?'\\nПлощадь: '+a+' м²':'')+'\\nЧто нужно: '+(g||'не выбрано')"
    "+'\\nСтраница: Дератизация и дезинсекция (/deratizatsiya-i-dezinsektsiya/)';},true);})(document);</script>\n"
)


def year_html():
    def dots(n, on, cls):
        return ''.join(f'<i class="dd-dot {cls}{" on" if on else ""}"></i>' for _ in range(n))

    out = ['    <div class="dd-year">']
    for code, name, note, months in YEAR:
        head = ''.join(f'<th scope="col"><abbr title="{full}">{short}</abbr></th>' for short, full, _, _ in months)
        rr = ''.join(f'<td>{dots(1, r, "dd-r")}<span class="sr-only">{full}: оценка{", усиленный контроль" if r else ""}</span></td>'
                     for short, full, r, _ in months)
        ii = ''.join(f'<td>{dots(2, i, "dd-i")}<span class="sr-only">{full}: 2 обследования{", усиленный контроль" if i else ""}</span></td>'
                     for short, full, _, i in months)
        out.append(f'      <div class="card dd-ssn dd-ssn-{code}"><p class="dd-ssn-h"><b>{name}</b></p>'
                   f'<table class="dd-ssn-t"><caption class="sr-only">{name}: пример графика визитов</caption>'
                   f'<thead><tr><td></td>{head}</tr></thead><tbody>'
                   f'<tr><th scope="row">Грызуны</th>{rr}</tr><tr><th scope="row">Насекомые</th>{ii}</tr></tbody></table>'
                   f'<p class="dd-ssn-n">{note[0].upper() + note[1:]}.</p></div>')
    out.append('    </div>')
    out.append('    <p class="dd-leg"><span><i class="dd-dot dd-r"></i>Грызуны — оценка раз в месяц</span>'
               '<span><i class="dd-dot dd-i"></i><i class="dd-dot dd-i"></i>Насекомые — обследования не реже 2 раз в месяц</span>'
               '<span><i class="dd-dot dd-r on"></i><i class="dd-dot dd-i on"></i>Усиленный контроль в сезон</span></p>')
    return '\n'.join(out)


def faq_section():
    def qa(i, q, a):
        # развёрнут только первый вопрос, остальные свёрнуты (решение владельца 13.11.2026, tools/site/faq_first.py)
        cls, exp = (' open', 'true') if i == 1 else ('', 'false')
        return (f'        <div class="card qa{cls}"><button aria-expanded="{exp}" aria-controls="a{i}" id="q{i}"><span>{q}</span><span class="pm"></span></button>'
                f'<div class="ans" id="a{i}" role="region" aria-labelledby="q{i}"><div><p>{a}</p></div></div></div>')
    half = (len(FAQ) + 1) // 2
    html = ['<section class="s" id="voprosy">', '  <div class="wrap">',
            '    <div class="head"><div class="eyebrow">Вопросы</div><h2>Вопросы о <em>дератизации и дезинсекции</em></h2></div>',
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


def json_ld():
    org = {'@type': 'Organization', '@id': SITE + '#org', 'name': 'ПЕСТКОНТРОЛЬ Центр',
           'legalName': 'ООО «Центр дезинфекционных услуг»', 'url': SITE,
           'telephone': '+7 495 104-35-70', 'email': 'b2b@pestcontrol-center.ru'}
    month = {'@type': 'UnitPriceSpecification', 'minPrice': PRICE, 'priceCurrency': 'RUB', 'unitText': 'в месяц', 'unitCode': 'MON'}
    objects = ['Кафе, ресторан, столовая', 'Магазин, торговая сеть', 'Склад и логистика', 'Пищевое и фармацевтическое производство']
    graph = [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': CRUMB, 'item': URL}]},
        {'@type': 'Service', '@id': URL + '#service', 'name': NAME,
         'alternateName': ['Дезинсекция и дератизация для организаций', 'Комплекс дератизации и дезинсекции',
                           'Оказание услуг по дератизации и дезинсекции'],
         'serviceType': 'Дератизация и дезинсекция', 'description': DESC, 'url': URL, 'provider': org,
         'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
         'audience': {'@type': 'BusinessAudience', 'audienceType': 'Организации и предприятия'},
         'offers': {'@type': 'Offer', 'name': 'Комплекс дератизации и дезинсекции', 'priceCurrency': 'RUB', 'price': PRICE,
                    'priceSpecification': month},
         'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': 'Цены на комплекс дератизации и дезинсекции', 'itemListElement': [
             {'@type': 'Offer', 'name': f'{o}: дератизация и дезинсекция', 'priceCurrency': 'RUB', 'price': PRICE,
              'priceSpecification': month} for o in objects]}},
        {'@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE, 'description': DESC, 'inLanguage': 'ru',
         'datePublished': DATE, 'dateModified': DATE,
         'about': [{'@id': URL + '#service'}, {'@id': URL + '#derat'}, {'@id': URL + '#dezins'}],
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': SITE + 'img/dd-hero.webp', 'width': 1920, 'height': 1072}},
        {'@type': 'DefinedTerm', '@id': URL + '#derat', 'name': 'Дератизация',
         'description': 'Защита от грызунов: крыс и мышей.'},
        {'@type': 'DefinedTerm', '@id': URL + '#dezins', 'name': 'Дезинсекция',
         'description': 'Защита от насекомых: тараканов, мух, муравьёв, моли и других.'},
        {'@type': 'FAQPage', '@id': URL + '#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in FAQ]},
    ]
    return '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False) + '</script>'


def main():
    tpl = (ROOT / 'pishchevoe-proizvodstvo' / 'index.html').read_text(encoding='utf-8')
    icons = json.loads((ROOT / 'tools' / 'site' / 'icons.json').read_text(encoding='utf-8'))
    icons['arr'] = ARR

    head = tpl[:tpl.index('<style>')]
    rep = [
        (r'<title>[^<]*</title>', f'<title>{TITLE}</title>'),
        (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">'),
        (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">'),
        (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">'),
        (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_TITLE}">'),
        (r'<meta property="og:description" content="[^"]*">',
         f'<meta property="og:description" content="{DESC}">\n'
         f'<meta property="og:image" content="{SITE}img/dd-og.jpg">\n'
         '<meta property="og:image:type" content="image/jpeg">\n'
         '<meta property="og:image:width" content="1200">\n'
         '<meta property="og:image:height" content="630">\n'
         f'<meta property="og:image:alt" content="{OG_ALT}">\n'
         '<meta name="twitter:card" content="summary_large_image">'),
        (r'<link rel="preload" href="\.\./img/food-hero\.webp"[^>]*>\n<link rel="preload" href="\.\./img/food-hero-mob\.webp"[^>]*>',
         '<link rel="preload" as="image" media="(min-width:761px)" imagesrcset="../img/dd-hero-1440.webp 1440w, ../img/dd-hero.webp 1920w" imagesizes="100vw" fetchpriority="high">\n'
         '<link rel="preload" as="image" media="(max-width:760px)" imagesrcset="../img/dd-hero-mob-760.webp 760w, ../img/dd-hero-mob.webp 1024w" imagesizes="100vw" fetchpriority="high">'),
    ]
    for pat, new in rep:
        head, n = re.subn(pat, lambda m: new, head, count=1)
        assert n == 1, 'шаблон: не найдено ' + pat
    assert 'food-hero' not in head
    css = tpl[tpl.index('<style>') + 7:tpl.index('</style>')]
    css += '\n' + (HERE / 'page.css').read_text(encoding='utf-8').strip()

    top = tpl[tpl.index('</head>'):tpl.index('<main id="main"')]
    top = top.replace('<body class="d-page">', '<body class="d-page dd-page">', 1)
    assert 'dd-page' in top

    main = (HERE / 'main.html').read_text(encoding='utf-8')
    main = main.replace('<!--YEAR-->', year_html()).replace('<!--FAQ-->', faq_section()).replace('<!--TYPE_SELECT-->', TYPE_SELECT)
    main = main.replace('href="https://fp.rospotrebnadzor.ru/licen/"', f'href="{LIC}"')
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

    html = (head + '<style>' + css + '</style>\n' + json_ld() + '\n' + top + main + bottom + page_js + '\n'
            + loader + PAGE_JS + '</body>\n</html>\n')
    out = ROOT / SLUG / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print('ok', out.relative_to(ROOT), len(html) // 1024, 'КБ')


if __name__ == '__main__':
    main()
