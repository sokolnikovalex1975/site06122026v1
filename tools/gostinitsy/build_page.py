#!/usr/bin/env python3
"""Сборка страницы «Пест-контроль гостиниц и отелей» — gostinitsy/index.html.

Шаблон — готовая отраслевая страница pishchevoe-proizvodstvo/index.html: из неё берутся шапка, мобильное меню,
подвал, плавающие кнопки, ранний скрипт и подключение анимаций, общие стили отраслевой страницы.
Своё у страницы: <head> (заголовок, описание, Open Graph, структурированные данные), стили page.css,
содержимое main.html, схема зон zones.svg и вопросы FAQ (список ниже — из него же собирается FAQPage).

Дальше страницу доводит общий конвейер сайта (бегущая строка, «Смотрите также», разметка анимаций, общее меню):

    python3 tools/gostinitsy/build_page.py
    python3 tools/site/build_site.py

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
SLUG = 'gostinitsy/'
URL = SITE + SLUG
TITLE = 'Пест-контроль гостиниц и отелей в Москве и области — ПЕСТКОНТРОЛЬ Центр'
NAME = 'Пест-контроль гостиниц и отелей'
OG_TITLE = 'Пест-контроль гостиниц и отелей в Москве и области'
DESC = ('Пест-контроль гостиниц и отелей по СанПиН 3.3686-21: осмотр номеров 2 раза в месяц, обработка от клопов '
        'без гостей, журнал для проверки. Бесплатное обследование.')
OG_ALT = 'Специалист ПЕСТКОНТРОЛЬ Центра проверяет шов матраса в гостиничном номере'

LICENSE_URL = 'https://fp.rospotrebnadzor.ru/licen/?oper=search&amp;numb_history=&amp;numb=&amp;firmget_name=&amp;ogrn_inn_nza=7714462211'
FAQ = [
    ('Как часто нужно проводить дезинсекцию в гостинице?',
     'Гостиница — объект особого эпидемиологического значения: обследования на насекомых — не реже 2 раз в месяц, '
     'оценка заселённости грызунами — ежемесячно (пп. 98, 101, 110 СанПиН 3.3686-21). Обработки проводят по результатам '
     'обследований и при появлении вредителей.'),
    ('Что делать, если гость пожаловался на клопов?',
     'Переселить гостя в номер на другом этаже, снять номер с продажи, бельё отправить в прачечную в закрытом мешке '
     'и вызвать специалиста. Мы осмотрим номер и соседние — слева, справа, сверху и снизу, обработаем очаг '
     'и проведём контрольный осмотр через 10–14 дней.'),
    ('Нужно ли закрывать этаж или выселять соседей?',
     'Обычно нет. Выборочную дезинсекцию проводят в отдельных номерах, где нашли насекомых, в отсутствие людей '
     '(п. 127 СанПиН 3.3686-21). Соседние номера осматриваем и обрабатываем, если в них тоже есть находки.'),
    ('Когда номер можно вернуть в продажу?',
     'После проветривания по инструкции к средству и влажной уборки. Срок зависит от средства, поэтому называем его '
     'до начала работ.'),
    ('Сколько стоит обработка номера от клопов?',
     'Разовая обработка номера от клопов — от 3 500 ₽ за выезд: локализация очага, уничтожение клопов '
     'и акт выполненных работ. Абонентское обслуживание гостиницы считаем после бесплатного '
     'обследования; при переходе на годовой договор стоимость первой обработки учитываем в расчёте.'),
    ('Что проверяет Роспотребнадзор в гостинице по вредителям?',
     'По проверочному листу (приказ Роспотребнадзора от 20.07.2026 № 578): нет ли насекомых и грызунов, кто и как '
     'проводит обработки, соблюдается ли кратность обследований — 2 раза в месяц на насекомых и ежемесячно на грызунов, '
     'обследуются ли мусоросборные камеры и контейнерная площадка.'),
    ('Работаете ли вы ночью и без огласки?',
     'Да. Выезжаем без броской символики, ночью и в выходные — без наценки. Срочный выезд — в течение 3 часов '
     'по Москве и Московской области, 24/7.'),
    ('Проводите ли вы обучение горничных?',
     'Да. Инструктаж проводим на объекте: признаки клопов, порядок действий при находке и как не разнести насекомых '
     'с бельём по этажам.'),
    ('Чем пест-контроль отличается от разовой обработки?',
     'Разовая обработка убирает очаг. Пест-контроль — постоянная система: осмотры по графику, точки контроля, журнал '
     'и обучение персонала, чтобы очаг не повторился. Подробнее — в материале '
     '<a href="../materialy/pest-menedzhment-ili-razovaya-obrabotka/">«Пест-менеджмент или разовая обработка»</a>.'),
    ('Есть ли у вас лицензия?',
     'Да. С 1 марта 2025 года услуги дезинфекции, дезинсекции и дератизации лицензируются. У ООО «Центр '
     'дезинфекционных услуг» действующая лицензия № Л064-00111-77/01942445 — запись можно проверить в '
     f'<a href="{LICENSE_URL}" target="_blank" rel="noopener">реестре лицензий Роспотребнадзора</a>.'),
]

NW_RE = re.compile(r'(?<![\w>-])([А-Яа-яЁё]+-[А-Яа-яЁё]+)(?![\w-])')
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
        out.append(typo(NW_RE.sub(r'<span class="nw">\1</span>', part)))
    return ''.join(out)


def plain(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html)).replace('&amp;', '&').strip()


def faq_section():
    def qa(i, q, a):
        return (f'        <div class="card qa"><button aria-expanded="false" aria-controls="a{i}" id="q{i}"><span>{q}</span><span class="pm"></span></button>'
                f'<div class="ans" id="a{i}" role="region" aria-labelledby="q{i}"><div><p>{a}</p></div></div></div>')
    half = (len(FAQ) + 1) // 2
    cols = [FAQ[:half], FAQ[half:]]
    html = ['<section class="s" id="voprosy">', '  <div class="wrap">',
            '    <div class="head"><div class="eyebrow">Вопросы</div><h2>Вопросы <em>о пест-контроле гостиниц</em></h2></div>',
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
    graph = [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': NAME, 'item': URL}]},
        {'@type': 'Service', '@id': URL + '#service', 'name': NAME,
         'serviceType': 'Пест-контроль по системе IPM: дезинсекция и дератизация гостиниц (СанПиН 3.3686-21, СП 2.1.4284-26)',
         'description': DESC, 'url': URL, 'provider': org,
         'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
         'audience': {'@type': 'BusinessAudience', 'audienceType': 'Гостиницы, отели, апарт-отели, хостелы, базы отдыха'},
         'offers': {'@type': 'Offer', 'name': 'Разовая обработка номера', 'priceCurrency': 'RUB', 'price': 3500,
                    'priceSpecification': {'@type': 'UnitPriceSpecification', 'minPrice': 3500, 'priceCurrency': 'RUB', 'unitText': 'за выезд'}}},
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
         f'<meta property="og:image" content="{SITE}img/gost-og.jpg">\n'
         '<meta property="og:image:type" content="image/jpeg">\n'
         '<meta property="og:image:width" content="1200">\n'
         '<meta property="og:image:height" content="630">\n'
         f'<meta property="og:image:alt" content="{OG_ALT}">\n'
         '<meta name="twitter:card" content="summary_large_image">'),
        (r'<link rel="preload" href="\.\./img/food-hero\.webp"[^>]*>\n<link rel="preload" href="\.\./img/food-hero-mob\.webp"[^>]*>',
         '<link rel="preload" as="image" media="(min-width:761px)" imagesrcset="../img/gost-hero-1440.webp 1440w, ../img/gost-hero.webp 1920w" imagesizes="100vw" fetchpriority="high">\n'
         '<link rel="preload" as="image" media="(max-width:760px)" imagesrcset="../img/gost-hero-mob-760.webp 760w, ../img/gost-hero-mob.webp 1024w" imagesizes="100vw" fetchpriority="high">'),
    ]
    for pat, new in rep:
        head, n = re.subn(pat, lambda m: new, head, count=1)
        assert n == 1, 'шаблон: не найдено ' + pat
    css = tpl[tpl.index('<style>') + 7:tpl.index('</style>')]
    css += '\n' + (HERE / 'page.css').read_text(encoding='utf-8').strip()

    # ---------------- шапка, меню (общее меню потом пересобирает tools/menu/apply_menu.py)
    top = tpl[tpl.index('</head>'):tpl.index('<main id="main"')]
    top = top.replace('<body class="d-page">', '<body class="d-page g-page">', 1)
    assert 'g-page' in top

    # ---------------- содержимое
    main = (HERE / 'main.html').read_text(encoding='utf-8')
    main = main.replace('<!--FAQ-->', faq_section())
    main = typeset(main)
    # .ind h3 — flex-контейнер: текст со спаном .nw оборачиваем в один span, иначе части разъезжаются по gap
    main = re.sub(r'<h3>((?:(?!</h3>).)*?<span class="nw">(?:(?!</h3>).)*?)</h3>', r'<h3><span>\1</span></h3>', main)
    main = main.replace('<!--ZONES_SVG-->', (HERE / 'zones.svg').read_text(encoding='utf-8').strip())
    main = re.sub(r'<!--ICON:([a-z-]+)-->', lambda m: icons[m.group(1)], main)
    contacts = cut(tpl, '      <div class="cta-contacts"', '    </div>\n    <form', after=False)
    contacts = contacts.replace(' data-fade', '')
    main = main.replace('<!--CTA_CONTACTS-->\n', contacts.rstrip('\n') + '\n')
    assert '<!--' not in main.replace('<!-- ', ''), 'остались метки в main.html'

    # ---------------- подвал, плавающие кнопки, скрипты
    bottom = tpl[tpl.index('</main>') + len('</main>'):tpl.index('<script>\n/* Предпросмотр')]
    page_js = cut(tpl, '<script>\n/* Предпросмотр', '</script>', after=True)
    page_js = page_js.replace(
        "document.getElementById('chk-note').textContent=n===5?'Всё на месте — на обследовании проверим, как это работает на объекте.':'Чего-то не хватает — на бесплатном обследовании покажем, что добавить и в каком порядке.'",
        "document.getElementById('chk-note').textContent=n===5?'Всё на месте — на обследовании проверим, как это работает в номерах и на кухне.':'Чего-то не хватает — на бесплатном обследовании покажем, что добавить и в каком порядке.'")
    # только загрузчик анимаций: скрипт формы пищевой страницы (unify.py) сюда не переносим — у гостиниц свои поля
    li = tpl.index('<script>\n  /* скрипты анимаций')
    loader = tpl[li:tpl.index('</script>', li) + len('</script>')] + '\n'
    form_js = ("<script>/* Форма: номерной фонд, задача, комментарий и страница — в поле msg, которое читает send.php */\n"
               "document.addEventListener('submit',function(ev){var f=ev.target;if(!f||f.id!=='form')return;var e=f.elements,"
               "r=e.rooms.value||'не указан',t=e.task.value||'не выбрана',c=e.comment.value.trim();"
               "e.msg.value='Номерной фонд: '+r+'\\nЗадача: '+t+(c?'\\nКомментарий: '+c:'')+"
               "'\\nСтраница: Пест-контроль гостиниц и отелей (/gostinitsy/)';},true);</script>\n")

    html = (head + '<style>' + css + '</style>\n' + json_ld() + '\n' + top + main + bottom + page_js + '\n'
            + loader + form_js + '</body>\n</html>\n')
    out = ROOT / 'gostinitsy' / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print('ok', out.relative_to(ROOT), len(html) // 1024, 'КБ')


if __name__ == '__main__':
    main()
