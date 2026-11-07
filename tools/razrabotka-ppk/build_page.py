#!/usr/bin/env python3
"""Сборка страницы «Разработка программы производственного контроля (ППК)» — razrabotka-ppk/index.html.

Шаблон — готовая отраслевая страница pishchevoe-proizvodstvo/index.html: из неё берутся шапка, мобильное меню,
подвал, плавающие кнопки, ранний скрипт и подключение анимаций, общие стили отраслевой страницы.
Своё у страницы: <head> (заголовок, описание, Open Graph, структурированные данные), стили page.css,
содержимое main.html и вопросы FAQ (список ниже — из него же собирается FAQPage).

Дальше страницу доводит общий конвейер сайта (бегущая строка, «Смотрите также», разметка анимаций, общее меню):

    python3 tools/razrabotka-ppk/build_page.py
    python3 tools/site/build_site.py

Цели Метрики: заявка — «audit», как на всех страницах (app.js); клик по образцу ППК — «ppk_obrazets»,
как на странице образца ППК (атрибут data-dl="obrazets"). Новых целей нет.
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
from typo import typo  # noqa: E402  неразрывные пробелы после коротких слов, как на остальных страницах

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
SLUG = 'razrabotka-ppk/'
URL = SITE + SLUG
TITLE = 'Разработка программы производственного контроля (ППК) в Москве — ПЕСТКОНТРОЛЬ Центр'
NAME = 'Разработка программы производственного контроля (ППК)'
CRUMB = 'Разработка ППК'
OG_TITLE = 'Разработка ППК — программа производственного контроля под ваш объект'
DESC = ('Разработка ППК под ваш объект от 5 900 ₽ за 1 рабочий день: нормы 2026 года, план-график лабораторных '
        'исследований, ХАССП для пищевых объектов, приказ и формы журналов. Москва и область.')
OG_ALT = 'Специалист и владелец пекарни изучают распечатанную программу производственного контроля'
DATE = '2026-11-08'
AUTHOR = {'@type': 'Person', 'name': 'Марианна Семерина', 'jobTitle': 'Санитарный врач'}
# фото в карточке автора иллюстративное (сгенерировано), поэтому image у Person не указываем
DEFINITION = ('Программа производственного контроля (ППК) — внутренний документ организации или индивидуального '
              'предпринимателя, по которому они сами контролируют соблюдение санитарных правил на своём объекте: '
              'действующие нормы, ответственные, лабораторные исследования, медосмотры, журналы и действия при авариях. '
              'Требования к программе установлены СП 1.1.1058-01.')

LICENSE_URL = 'https://fp.rospotrebnadzor.ru/licen/?oper=search&amp;numb_history=&amp;numb=&amp;firmget_name=&amp;ogrn_inn_nza=7714462211'
SP1058 = 'https://13.rospotrebnadzor.ru/sites/default/files/1.1.1058-01.rtf'
FAQ = [
    ('Сколько стоит разработка ППК?',
     'От 5&nbsp;900&nbsp;₽ — это цена для небольшого объекта: кафе, кофейни или магазина. Для ресторана, склада, '
     'гостиницы и производства стоимость зависит от площади, числа помещений и сотрудников и от того, нужны ли '
     'процедуры ХАССП; сумму называем до начала работы. Для сети считаем по количеству и типам объектов.'),
    ('Сколько времени занимает разработка ППК?',
     '1 рабочий день после того, как мы получили сведения об объекте. Для производства с процедурами ХАССП '
     'и для сети объектов срок называем при расчёте.'),
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
    ('Чем ППК отличается от ХАССП?',
     'ППК охватывает все санитарные требования к объекту, а ХАССП — систему управления безопасностью пищевой '
     'продукции: опасные факторы, критические контрольные точки, пределы и корректирующие действия. На пищевых '
     'объектах процедуры ХАССП входят в ППК: ТР ТС 021/2011 требует определять контролируемые этапы технологических '
     'операций в программах производственного контроля (ст. 10, ч. 3, п. 3).'),
    ('Входят ли лабораторные исследования в разработку ППК?',
     'В разработку входит план-график исследований: что, где и как часто исследовать. Сами исследования проводит '
     'организация или аккредитованная лаборатория (СП 1.1.1058-01, п. 2.5), в стоимость разработки они не входят. '
     'Измерения недавней специальной оценки условий труда можно использовать, если они проведены не раньше чем '
     'за шесть месяцев (ст. 32 Федерального закона № 52-ФЗ, п. 1.1).'),
    ('Можно ли разработать ППК без выезда на объект?',
     'Да. Для небольших объектов обычно достаточно анкеты, планировки и фотографий помещений. Нужен ли выезд '
     'специалиста, решаем при расчёте: на производстве с процедурами ХАССП без осмотра не обойтись.'),
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
        out.append(typo(t))
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
            '    <div class="head"><div class="eyebrow">Вопросы</div><h2>Вопросы <em>о разработке ППК</em></h2></div>',
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
         'alternateName': ['Разработка ППК', 'Разработка плана производственного контроля'],
         'serviceType': 'Разработка программы производственного контроля по СП 1.1.1058-01',
         'description': DESC, 'url': URL, 'provider': org,
         'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
         'audience': {'@type': 'BusinessAudience',
                      'audienceType': 'Рестораны и кафе, магазины и торговые сети, пищевые и фармацевтические производства, склады, гостиницы'},
         'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'RUB', 'lowPrice': 5900,
                    'description': ('Цена зависит от вида деятельности, площади и числа помещений, численности персонала '
                                    'и процедур ХАССП; срок — 1 рабочий день после получения сведений об объекте; '
                                    'лабораторные исследования в стоимость не входят')}},
        {'@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE, 'description': DESC, 'inLanguage': 'ru',
         'datePublished': DATE, 'dateModified': DATE, 'author': AUTHOR,
         'about': [{'@id': URL + '#service'}, {'@id': URL + '#ppk'}],
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': SITE + 'img/rppk-hero.webp', 'width': 1920, 'height': 1072}},
        term,
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
    form_js = ("<script>/* Форма: что нужно, адрес, комментарий и страница — в поле msg, которое читает send.php */\n"
               "document.addEventListener('submit',function(ev){var f=ev.target;if(!f||f.id!=='form')return;var e=f.elements,"
               "g=e.goal.value||'не выбрано',a=e.address.value.trim()||'не указан',c=e.comment.value.trim();"
               "e.msg.value='Что нужно: '+g+'\\nАдрес: '+a+(c?'\\nКомментарий: '+c:'')+"
               "'\\nСтраница: Разработка ППК (/razrabotka-ppk/)';},true);\n"
               "/* клик по образцу ППК — цель Метрики ppk_obrazets, как на странице образца */\n"
               "document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-dl]');if(!a)return;"
               "try{if(window.ym)ym(113675622,'reachGoal','ppk_'+a.getAttribute('data-dl'))}catch(_){}});</script>\n")

    html = (head + '<style>' + css + '</style>\n' + json_ld() + '\n' + top + main + bottom + page_js + '\n'
            + loader + form_js + '</body>\n</html>\n')
    out = ROOT / 'razrabotka-ppk' / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print('ok', out.relative_to(ROOT), len(html) // 1024, 'КБ')


if __name__ == '__main__':
    main()
