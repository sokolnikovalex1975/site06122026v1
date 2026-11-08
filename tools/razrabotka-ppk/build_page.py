#!/usr/bin/env python3
"""Сборка страницы «Разработка программы производственного контроля (ППК)» — razrabotka-ppk/index.html.
Одна страница услуги для двух программ: ППК (от 5 900 ₽, 1 рабочий день) и ППК по ХАССП для объектов, где
изготавливают пищевую продукцию (от 19 900 ₽, 3 рабочих дня). Образец ППК по ХАССП — отдельная страница
materialy/programma-proizvodstvennogo-kontrolya-haccp/ (решение владельца 08.11.2026).

Шаблон — готовая отраслевая страница pishchevoe-proizvodstvo/index.html: из неё берутся шапка, мобильное меню,
подвал, плавающие кнопки, ранний скрипт и подключение анимаций, общие стили отраслевой страницы.
Своё у страницы: <head> (заголовок, описание, Open Graph, структурированные данные), стили page.css,
содержимое main.html и вопросы FAQ (список ниже — из него же собирается FAQPage).

Дальше страницу доводит общий конвейер сайта (бегущая строка, «Смотрите также», разметка анимаций, общее меню):

    python3 tools/razrabotka-ppk/build_page.py
    python3 tools/site/build_site.py

Опросный лист заказчика (блок #oprosnyy-list, онлайн-форма и два PDF) собирается из tools/razrabotka-ppk/oprosnyy:
content.py — вопросы, build_pdf.py — PDF, block.py — блок и форма (метка <!--OPROSNYY--> в main.html).

Цели Метрики: заявка — «audit», как на всех страницах (app.js); клик по образцу ППК — «ppk_obrazets»,
как на странице образца ППК (атрибут data-dl="obrazets"). Опросный лист (08.11.2026): отправлен онлайн —
«audit» и «ppk_oprosnyy_send», скачан PDF — «ppk_oprosnyy_ppk» и «ppk_oprosnyy_haccp» (data-dl).
Счётчики (Метрика, UIS, Radist) в репозиторий не кладутся — их добавляет tools/site/build_prod.py
в версию для Timeweb, как и на остальных страницах.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
sys.path.insert(0, str(HERE / 'oprosnyy'))
from typo import typo  # noqa: E402  неразрывные пробелы после коротких слов, как на остальных страницах
import block as oprosnyy  # noqa: E402  опросный лист заказчика: блок на странице и онлайн-форма
from content import PROGRAMS as OL_PROGRAMS  # noqa: E402

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
SLUG = 'razrabotka-ppk/'
URL = SITE + SLUG
TITLE = 'Разработка программы производственного контроля (ППК) и ППК по ХАССП в Москве — ПЕСТКОНТРОЛЬ Центр'
NAME = 'Разработка программы производственного контроля (ППК)'
CRUMB = 'Разработка ППК'
OG_TITLE = 'Разработка ППК и ППК по ХАССП — программа производственного контроля под ваш объект'
DESC = ('Разработка ППК под ваш объект: от 5 900 ₽ за 1 рабочий день, ППК по ХАССП для общепита и пищевых '
        'производств — от 19 900 ₽ за 3 рабочих дня. Нормы 2026 года, план-график исследований, приказ и журналы.')
OG_ALT = 'Специалист и владелец пекарни изучают распечатанную программу производственного контроля'
DATE = '2026-11-08'
AUTHOR = {'@type': 'Person', 'name': 'Марианна Семерина', 'jobTitle': 'Санитарный врач'}
# фото в карточке автора иллюстративное (сгенерировано), поэтому image у Person не указываем
DEFINITION = ('Программа производственного контроля (ППК) — внутренний документ организации или индивидуального '
              'предпринимателя, по которому они сами контролируют соблюдение санитарных правил на своём объекте: '
              'действующие нормы, ответственные, лабораторные исследования, медосмотры, журналы и действия при авариях. '
              'Требования к программе установлены СП 1.1.1058-01. Если на объекте изготавливают пищевую продукцию, '
              'в программу входят процедуры на принципах ХАССП — такую программу называют ППК по ХАССП.')

LICENSE_URL = 'https://fp.rospotrebnadzor.ru/licen/?oper=search&amp;numb_history=&amp;numb=&amp;firmget_name=&amp;ogrn_inn_nza=7714462211'
SP1058 = 'https://13.rospotrebnadzor.ru/sites/default/files/1.1.1058-01.rtf'
FAQ = [
    ('Сколько стоит разработка ППК?',
     'ППК — от 5&nbsp;900&nbsp;₽, ППК по ХАССП — от 19&nbsp;900&nbsp;₽. Точная сумма зависит от вида деятельности, '
     'площади, числа помещений и сотрудников, а для ППК по ХАССП — ещё и от числа технологических процессов; '
     'называем её до начала работы. Для сети считаем по количеству и типам объектов.'),
    ('Сколько времени занимает разработка ППК?',
     'ППК — 1 рабочий день, ППК по ХАССП — 3 рабочих дня. Срок считаем с момента, когда получили сведения '
     'об объекте — заполненный <a href="#oprosnyy-list">опросный лист</a>, а если нужен выезд — после выезда. '
     'Для сети объектов срок называем при расчёте.'),
    ('Что нужно для разработки ППК?',
     'Сведения об объекте: реквизиты и адрес, виды деятельности, площадь и помещения, персонал по должностям, '
     'водоснабжение, канализация и вентиляция, оборудование, отходы, договоры на дезинсекцию и дератизацию и '
     'с лабораторией, действующая программа и предписания, если были. Всё это собрано в '
     '<a href="#oprosnyy-list">опросном листе заказчика</a> — его можно заполнить онлайн на этой странице или в PDF. '
     'Из документов пригодятся план помещений, штатное расписание и перечень оборудования, но начать можно и без них.'),
    ('Какие сведения нужны для ППК по ХАССП?',
     'Всё, что для ППК, и сведения о продукции и технологии: ассортимент или меню, объём выпуска, основное сырьё, '
     'сроки годности и хранение, операции от приёмки сырья до выдачи, тепловая обработка и охлаждение, цеха, '
     'холодильное оборудование и действующие документы ХАССП. По ним составляют блок-схемы процессов и определяют '
     'критические контрольные точки (ТР ТС 021/2011, ст. 10–11). В опросном листе это разделы 5 и 6.'),
    ('Нужно ли согласовывать ППК с Роспотребнадзором?',
     'Нет. По СП 1.1.1058-01 программу утверждает руководитель организации, ИП или уполномоченное лицо (п. 2.6), '
     'согласование с Роспотребнадзором не предусмотрено. При проверке инспектор смотрит и саму программу, '
     'и документы о её выполнении.'),
    ('Сколько действует ППК и когда её обновлять?',
     'Срок действия не ограничен (СП 1.1.1058-01, п. 2.6). Изменения вносят при смене вида деятельности, технологии '
     'и других существенных изменениях, а также когда отменены правила, на которые программа ссылается: с 1 сентября '
     '2026 года это затронуло общепит, торговлю пищевой продукцией и объекты услуг.'),
    ('Нужна ли ППК индивидуальному предпринимателю?',
     'Да. Программу составляет и юридическое лицо, и индивидуальный предприниматель — до начала деятельности '
     '(СП 1.1.1058-01, п. 2.6).'),
    ('Кто отвечает за ППК, если её разработали вы?',
     'За организацию и выполнение производственного контроля отвечает сама организация или ИП (СП 1.1.1058-01, '
     'п. 2.7). Мы отвечаем за содержание документа: состав по разделу 3, действующие нормы и соответствие программы '
     'вашему объекту.'),
    ('Чем ППК отличается от ППК по ХАССП?',
     'ППК по ХАССП — это ППК по СП 1.1.1058-01, в которую включены процедуры на принципах ХАССП: опасные факторы, '
     'критические контрольные точки и их пределы, мониторинг и действия при отклонениях (ТР ТС 021/2011, ст. 11, '
     'ч. 3). Такая программа нужна всем, кто изготавливает пищевую продукцию: производствам, ресторанам, кафе, '
     'кулинариям. Офису, складу или магазину без собственного производства достаточно ППК.'),
    ('Какая ППК нужна продуктовому магазину или складу продуктов?',
     'Если магазин или склад только хранит и продаёт готовую продукцию, достаточно ППК — от 5&nbsp;900&nbsp;₽ '
     'за 1 рабочий день. Если в магазине есть своя кулинария, пекарня или другое изготовление пищевой продукции, '
     'нужна ППК по ХАССП (ТР ТС 021/2011, ст. 10–11).'),
    ('Входят ли лабораторные исследования в разработку ППК?',
     'В разработку входит план-график исследований: что, где и как часто исследовать. Сами исследования проводит '
     'организация или аккредитованная лаборатория (СП 1.1.1058-01, п. 2.5), в стоимость разработки они не входят. '
     'Измерения недавней специальной оценки условий труда можно использовать, если они проведены не раньше чем '
     'за шесть месяцев (ст. 32 Федерального закона № 52-ФЗ, п. 1.1).'),
    ('Можно ли разработать ППК без выезда на объект?',
     'Да, ППК обычно разрабатываем по <a href="#oprosnyy-list">опросному листу</a>, планировке и фотографиям помещений. '
     'Для ППК по ХАССП нужно разобрать '
     'технологические процессы, поэтому нужен ли выезд специалиста, согласуем при расчёте.'),
    ('Нужна ли отдельная ППК для каждого объекта сети?',
     'Программа должна описывать конкретный объект: его помещения, точки отбора проб и ответственных '
     '(СП 1.1.1058-01, раздел 3). Для сети мы делаем общую часть и приложения по каждому объекту — так программу '
     'проще обновлять сразу для всех.'),
    ('Что будет, если ППК нет?',
     'Отсутствие программы — нарушение обязанности вести производственный контроль (ст. 11 и 32 Федерального закона '
     '№ 52-ФЗ). Штрафы за санитарные нарушения по КоАП собраны в таблице на странице '
     '<a href="../sanitarnyy-audit/#shtrafy">санитарного аудита</a>.'),
]

NW_RE = re.compile(r'(?<![\w>-])([А-Яа-яЁё]+-[А-Яа-яЁё]+)(?![\w-])')
# номера документов не разрываем на дефисе: «СанПиН 2.3/2.4.4282-26», «52-ФЗ», «ТР ТС 021/2011»
CODE_RE = re.compile(r'(?<![\w/.-])((?:\d+[./])*\d+-(?:\d+|ФЗ)(?:[-/]\d+)*)(?![\w-])')
TRTS_RE = re.compile(r'ТР ТС (\d{3}/\d{4})')
DOC_RE = re.compile(r'\b(СП|СанПиН|ГОСТ|МУК|МУ|МР) (?=\d|<span class="nw">\d)')
SKIP = {'svg', 'script', 'style', 'option', 'textarea', 'title', 'select'}
VOID = {'img', 'input', 'br', 'source', 'meta', 'link', 'hr'}


def typeset(html):
    """Типографика только в тексте: неразрывные пробелы и слова через дефис без переноса (класс nw).
    Атрибуты, svg, option и скрипты не трогаем."""
    out, stack = [], []
    for part in re.split(r'(<[^>]+>)', html):
        if part.startswith('<'):
            m = re.match(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)', part)
            if m:
                tag, closing = m.group(2).lower(), m.group(1) == '/'
                if tag in SKIP and tag not in VOID and not part.endswith('/>'):
                    if closing:
                        if stack and stack[-1] == tag:
                            stack.pop()
                    else:
                        stack.append(tag)
            out.append(part)
            continue
        if stack or not part.strip():
            out.append(part)
            continue
        t = NW_RE.sub(r'<span class="nw">\1</span>', part)
        t = CODE_RE.sub(r'<span class="nw">\1</span>', t)
        t = TRTS_RE.sub(r'<span class="nw">ТР ТС \1</span>', t)
        t = typo(t)
        # обозначение документа не отрывается от номера: «СП 1.1.1058-01», «СанПиН 2.3/2.4.4282-26»
        t = DOC_RE.sub('\\1\u00a0', t)
        out.append(t)
    return ''.join(out)


def plain(html):
    t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html))
    return t.replace('&nbsp;', ' ').replace('\u00a0', ' ').replace('&amp;', '&').strip()


def faq_section():
    def qa(i, q, a):
        return (f'        <div class="card qa"><button aria-expanded="false" aria-controls="a{i}" id="q{i}"><span>{q}</span><span class="pm"></span></button>'
                f'<div class="ans" id="a{i}" role="region" aria-labelledby="q{i}"><div><p>{a}</p></div></div></div>')
    half = (len(FAQ) + 1) // 2
    cols = [FAQ[:half], FAQ[half:]]
    html = ['<section class="s" id="voprosy">', '  <div class="wrap">',
            '    <div class="head"><div class="eyebrow">Вопросы</div><h2>Вопросы о разработке <em>ППК и ППК по ХАССП</em></h2></div>',
            '    <div class="faq">']
    n = 0
    for col in cols:
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
    term = {'@type': 'DefinedTerm', '@id': URL + '#ppk', 'name': 'Программа производственного контроля',
            'alternateName': ['ППК', 'План производственного контроля'], 'description': DEFINITION,
            'subjectOf': {'@type': 'CreativeWork', 'name': 'СП 1.1.1058-01', 'url': SP1058}}
    graph = [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': CRUMB, 'item': URL}]},
        {'@type': 'Service', '@id': URL + '#service', 'name': NAME,
         'alternateName': ['Разработка ППК', 'Разработка ППК по ХАССП', 'Разработка плана производственного контроля'],
         'serviceType': 'Разработка программы производственного контроля по СП 1.1.1058-01, в том числе с процедурами ХАССП',
         'description': DESC, 'url': URL, 'provider': org,
         'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
         'audience': {'@type': 'BusinessAudience',
                      'audienceType': ('Офисы, склады, магазины и торговые сети, гостиницы, рестораны и кафе, '
                                       'пищевые и фармацевтические производства')},
         'offers': [
             {'@type': 'Offer', 'name': 'Разработка ППК',
              'priceSpecification': {'@type': 'PriceSpecification', 'minPrice': 5900, 'priceCurrency': 'RUB'},
              'description': ('Для объектов, где не изготавливают пищевую продукцию: офисы, склады, магазины без '
                              'собственного производства, гостиницы без ресторана. Срок — 1 рабочий день после '
                              'получения сведений об объекте (опросный лист заказчика); лабораторные исследования '
                              'в стоимость не входят')},
             {'@type': 'Offer', 'name': 'Разработка ППК по ХАССП',
              'priceSpecification': {'@type': 'PriceSpecification', 'minPrice': 19900, 'priceCurrency': 'RUB'},
              'description': ('Для пищевых производств, ресторанов и кафе, магазинов с кулинарией или пекарней: ППК '
                              'с процедурами ХАССП. Срок — 3 рабочих дня после получения сведений об объекте '
                              '(опросный лист заказчика с разделами о продукции и технологии); лабораторные '
                              'исследования в стоимость не входят')}]},
        {'@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE, 'description': DESC, 'inLanguage': 'ru',
         'datePublished': DATE, 'dateModified': DATE, 'author': AUTHOR,
         'about': [{'@id': URL + '#service'}, {'@id': URL + '#ppk'}],
         'hasPart': [{'@id': URL + '#oprosnyy-' + k} for k in OL_PROGRAMS],
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': SITE + 'img/rppk-hero.webp', 'width': 1920, 'height': 1072}},
        term,
        *[{'@type': 'DigitalDocument', '@id': URL + '#oprosnyy-' + k, 'name': P['title'], 'url': URL + P['file'],
           'encodingFormat': 'application/pdf', 'inLanguage': 'ru', 'datePublished': DATE,
           'description': ('Опросный лист заказчика: сведения об объекте, по которым разрабатываем '
                           + P['short'] + (' — с разделами о продукции и технологических процессах' if k == 'haccp' else '')
                           + '. Заполняется онлайн на странице или в PDF.'),
           'publisher': {'@id': SITE + '#org'}, 'isPartOf': {'@id': URL + '#webpage'}} for k, P in OL_PROGRAMS.items()],
        {'@type': 'FAQPage', '@id': URL + '#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in FAQ]},
    ]
    return '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False) + '</script>'


def cut(s, start, end, after=False):
    i = s.index(start)
    j = s.index(end, i)
    return s[i:j + (len(end) if after else 0)]


def main():
    tpl = (ROOT / 'pishchevoe-proizvodstvo' / 'index.html').read_text(encoding='utf-8')
    icons = json.loads((ROOT / 'tools' / 'site' / 'icons.json').read_text(encoding='utf-8'))

    # ---------------- <head>
    head = tpl[:tpl.index('<style>')]
    rep = [
        (r'<title>[^<]*</title>', f'<title>{TITLE}</title>'),
        (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">'),
        (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">'),
        (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">'),
        (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_TITLE}">'),
        (r'<meta property="og:description" content="[^"]*">',
         f'<meta property="og:description" content="{DESC}">\n'
         f'<meta property="og:image" content="{SITE}img/rppk-og.jpg">\n'
         '<meta property="og:image:type" content="image/jpeg">\n'
         '<meta property="og:image:width" content="1200">\n'
         '<meta property="og:image:height" content="630">\n'
         f'<meta property="og:image:alt" content="{OG_ALT}">\n'
         '<meta name="twitter:card" content="summary_large_image">'),
        (r'<link rel="preload" href="\.\./img/food-hero\.webp"[^>]*>\n<link rel="preload" href="\.\./img/food-hero-mob\.webp"[^>]*>',
         '<link rel="preload" as="image" media="(min-width:761px)" imagesrcset="../img/rppk-hero-1440.webp 1440w, ../img/rppk-hero.webp 1920w" imagesizes="100vw" fetchpriority="high">\n'
         '<link rel="preload" as="image" media="(max-width:760px)" imagesrcset="../img/rppk-hero-mob-760.webp 760w, ../img/rppk-hero-mob.webp 1024w" imagesizes="100vw" fetchpriority="high">'),
    ]
    for pat, new in rep:
        head, n = re.subn(pat, lambda m: new, head, count=1)
        assert n == 1, 'шаблон: не найдено ' + pat
    assert 'food-hero' not in head, 'шаблон: осталась предзагрузка фото пищевой страницы'
    css = tpl[tpl.index('<style>') + 7:tpl.index('</style>')]
    css += '\n' + (HERE / 'page.css').read_text(encoding='utf-8').strip()

    # ---------------- шапка, меню (общее меню потом пересобирает tools/menu/apply_menu.py)
    top = tpl[tpl.index('</head>'):tpl.index('<main id="main"')]
    top = top.replace('<body class="d-page">', '<body class="d-page rp-page">', 1)
    assert 'rp-page' in top

    # ---------------- содержимое
    main = (HERE / 'main.html').read_text(encoding='utf-8')
    main = main.replace('<!--FAQ-->', faq_section())
    main = main.replace('<!--OPROSNYY-->\n', oprosnyy.section_html())
    main = typeset(main)
    main = main.replace('href="LICENSE_URL"', f'href="{LICENSE_URL}"')
    main = re.sub(r'<!--ICON:([a-z-]+)-->', lambda m: icons[m.group(1)], main)
    contacts = cut(tpl, '      <div class="cta-contacts"', '    </div>\n    <form', after=False)
    contacts = contacts.replace(' data-fade', '')
    main = main.replace('<!--CTA_CONTACTS-->\n', contacts.rstrip('\n') + '\n')
    assert '<!--' not in main.replace('<!-- ', ''), 'остались метки в main.html'
    assert 'LICENSE_URL' not in main

    # ---------------- подвал, плавающие кнопки, скрипты
    bottom = tpl[tpl.index('</main>') + len('</main>'):tpl.index('<script>\n/* Предпросмотр')]
    # из скрипта шаблона берём только «Предпросмотр» (заглушка send.php вне рабочего домена)
    page_js = cut(tpl, '<script>\n/* Предпросмотр', '</script>', after=True)
    pv = re.match(r'<script>\n(/\* Предпросмотр[^\n]*\*/\n\(function\(\)\{.*?\n?\}\)\(\);)', page_js, re.S)
    assert pv, 'шаблон: не найден скрипт предпросмотра'
    page_js = '<script>\n' + pv.group(1) + '\n</script>'
    # только загрузчик анимаций: скрипт формы пищевой страницы (unify.py) сюда не переносим — у страницы свои поля
    li = tpl.index('<script>\n  /* скрипты анимаций')
    loader = tpl[li:tpl.index('</script>', li) + len('</script>')] + '\n'
    form_js = ("<script>/* Форма: что нужно, адрес, комментарий и страница — в поле msg, которое читает send.php;\n"
               "   «Офис или бытовые услуги» уходит на сервер как «Другое» (список send.php), название вида — в msg */\n"
               "document.addEventListener('submit',function(ev){var f=ev.target;if(!f||f.id!=='form')return;var e=f.elements,"
               "g=e.goal.value||'не выбрано',a=e.address.value.trim()||'не указан',c=e.comment.value.trim(),"
               "o=e.type.options[e.type.selectedIndex],k=o&&o.value&&o.text!==o.value?'Вид объекта: '+o.text+'\\n':'';"
               "e.msg.value=k+'Что нужно: '+g+'\\nАдрес: '+a+(c?'\\nКомментарий: '+c:'')+"
               "'\\nСтраница: Разработка ППК (/razrabotka-ppk/)';},true);\n"
               "/* кнопки в карточках цен сразу выбирают в форме «Что нужно» */\n"
               "document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-goal]');if(!b)return;"
               "var g=document.getElementById('f-goal');if(g)g.value=b.getAttribute('data-goal');});\n"
               "/* клик по образцу ППК — цель Метрики ppk_obrazets, как на странице образца */\n"
               "document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-dl]');if(!a)return;"
               "try{if(window.ym)ym(113675622,'reachGoal','ppk_'+a.getAttribute('data-dl'))}catch(_){}});</script>\n"
               + oprosnyy.FORM_JS)

    html = (head + '<style>' + css + '</style>\n' + json_ld() + '\n' + top + main + bottom + page_js + '\n'
            + loader + form_js + '</body>\n</html>\n')
    out = ROOT / 'razrabotka-ppk' / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print('ok', out.relative_to(ROOT), len(html) // 1024, 'КБ')


if __name__ == '__main__':
    main()
