#!/usr/bin/env python3
"""Сборка страницы «Разработка программы производственного контроля (ППК)» — razrabotka-ppk/index.html.

Услуга для объектов непищевого профиля (офисы, склады, гостиницы без пищеблока, магазины непродовольственных товаров,
производства непищевой продукции) — от 5 900 ₽. ППК по ХАССП для пищевых объектов — отдельная услуга и отдельная
страница /materialy/programma-proizvodstvennogo-kontrolya-haccp/ (от 19 900 ₽). Решение владельца — 08.11.2026.

Шаблон — готовая отраслевая страница pishchevoe-proizvodstvo/index.html (как у страницы санитарного аудита): из неё
берутся шапка, мобильное меню, подвал, плавающие кнопки, ранний скрипт и подключение анимаций, общие стили.
Своё у страницы: <head> (заголовок, описание, Open Graph, структурированные данные), стили page.css,
содержимое main.html и вопросы FAQ (список ниже — из него же собирается FAQPage).

Дальше страницу доводит общий конвейер сайта (бегущая строка, «Смотрите также», разметка анимаций, общее меню):

    python3 tools/razrabotka-ppk/build_page.py
    python3 tools/site/build_site.py

Ссылки «Подробнее» на отраслевые страницы (метки <!--MORE:адрес:текст--> в main.html) ставятся, только если
такая страница есть в репозитории.

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
HACCP_URL = SITE + 'materialy/programma-proizvodstvennogo-kontrolya-haccp/'
TITLE = 'Разработка программы производственного контроля (ППК) в Москве и МО — ПЕСТКОНТРОЛЬ Центр'
NAME = 'Разработка программы производственного контроля (ППК)'
CRUMB = 'Разработка ППК'
OG_TITLE = 'Разработка программы производственного контроля (ППК) — от 5 900 ₽'
DESC = ('Разработаем программу производственного контроля (ППК) для офиса, склада, гостиницы, магазина и другого '
        'объекта непищевого профиля по СП 1.1.1058-01 и санитарным правилам 2026 года. От 5 900 ₽.')
OG_ALT = 'Специалист ПЕСТКОНТРОЛЬ Центра и офис-менеджер сверяют программу производственного контроля и план помещений'
DATE = '2026-11-08'

CGON_PK = 'https://cgon.rospotrebnadzor.ru/biznesu/articles/proizvodstvennyy-kontrol/'
CGE48 = 'https://www.cge48.ru/nashi-uslugi/proizvodstvennyi-kontrol/kak_sostavit_programmu_plan_proizvodstvennogo_kontrolya.htm'
FAQ = [
    ('Что такое программа производственного контроля (ППК)?',
     'Внутренний документ организации или ИП, по которому она сама контролирует соблюдение санитарных правил: какие '
     'нормы относятся к объекту, кто отвечает за их соблюдение, какие лабораторные исследования и с какой '
     'периодичностью проводить, каким работникам нужны медосмотры и гигиеническое обучение, какие журналы вести '
     'и что делать при аварии. Программу составляют в произвольной форме по разделу 3 СП 1.1.1058-01, утверждает '
     'её руководитель.'),
    ('Нужна ли ППК офису или складу?',
     'Да. Производственный контроль обязаны вести организации и ИП, на чью деятельность распространяются санитарные '
     'правила (ст. 11 и 32 Федерального закона № 52-ФЗ, п. 2.1 СП 1.1.1058-01). В офисе и на складе это прежде всего '
     'условия труда — микроклимат и освещённость на рабочих местах по СП 2.2.4285-26, а также уборка, вывоз отходов, '
     'дезинсекция и дератизация помещений.'),
    ('Чем ППК отличается от ППК по ХАССП?',
     'ППК по ХАССП дополнительно содержит процедуры, которые ст. 10 ТР ТС 021/2011 требует от производителей пищевой '
     'продукции: анализ опасностей, критические контрольные точки, мониторинг и корректирующие действия. Такая '
     'программа нужна пищевым производствам, общепиту, магазинам с кулинарией или пекарней. Объектам непищевого '
     'профиля процедуры ХАССП не нужны — достаточно программы по СП 1.1.1058-01. Разработка ППК стоит от 5 900 ₽, '
     f'<a href="{HACCP_URL}">ППК по ХАССП</a> — от 19 900 ₽.'),
    ('Сколько стоит разработка ППК?',
     'От 5 900 ₽ для объекта непищевого профиля. Цена зависит от вида деятельности, числа помещений и площадок, '
     'числа должностей и объёма лабораторных исследований; точную стоимость называем после описания объекта '
     'и фиксируем в договоре. Программа по ХАССП для пищевого объекта — от 19 900 ₽.'),
    ('Нужно ли согласовывать ППК с Роспотребнадзором?',
     'Нет. Программу утверждает руководитель организации, ИП или уполномоченное лицо (СП 1.1.1058-01, п. 2.6), '
     'а Роспотребнадзор оценивает её при проверке. Исключение — программа производственного контроля качества '
     'и безопасности воды систем водоснабжения: её согласовывают с территориальным органом Роспотребнадзора '
     f'(<a href="{CGON_PK}" target="_blank" rel="noopener">разъяснение ЦГОН Роспотребнадзора</a>).'),
    ('Какой срок действия у ППК?',
     'Срок не ограничен (СП 1.1.1058-01, п. 2.6). Изменения и дополнения вносят при смене вида деятельности, '
     'технологии и других существенных изменениях. На практике программу обновляют и тогда, когда отменены '
     'санитарные правила, на которые она ссылается.'),
    ('Какой штраф за отсутствие ППК?',
     'Как правило, наказание назначают по ч. 1 ст. 6.3 КоАП РФ: для юрлиц — штраф 10 000–20 000 ₽ или '
     'приостановление деятельности до 90 суток, для ИП — 500–1 000 ₽ или приостановление до 90 суток, '
     'для должностных лиц — 500–1 000 ₽.'),
    ('Что нужно для разработки ППК?',
     'Вид деятельности и адрес, перечень помещений и их площади, список должностей и число работников, оборудование, '
     'договоры на вывоз отходов, дезинфекцию, дезинсекцию и дератизацию, обслуживание вентиляции. Если программа '
     'или протоколы лабораторных исследований уже есть — их тоже. Анкету присылаем после заявки.'),
    ('Нужно ли менять ППК после 1 сентября 2026 года?',
     'Да, если в ней остались ссылки на СП 2.1.3678-20 или СП 2.2.3670-20: с 1 сентября 2026 года вместо них '
     'действуют СП 2.1.4284-26 и СП 2.2.4285-26. Новую редакцию утверждает руководитель; действующую программу '
     'мы обновляем без разработки с нуля.'),
    ('Нужно ли включать в ППК дезинсекцию и дератизацию?',
     'Да. По п. 14 СП 2.1.4284-26 в помещениях не должно быть насекомых, грызунов и следов их жизнедеятельности, '
     'а обработки проводит организация, которая ведёт дезинфекционную деятельность. В программе записывают меры '
     'и периодичность обследований по СанПиН 3.3686-21 и ссылку на договор с исполнителем. ПЕСТКОНТРОЛЬ Центр '
     'работает по лицензии № Л064-00111-77/01942445.'),
    ('Можно ли составить ППК самостоятельно?',
     'Да: программу можно разработать своими силами или с привлечением специалистов '
     f'(<a href="{CGE48}" target="_blank" rel="noopener">разъяснение ФБУЗ «Центр гигиены и эпидемиологии '
     'в Липецкой области»</a>). К подрядчику обращаются, когда в штате нет специалиста, который знает санитарные '
     'правила вашего вида деятельности и требования к лабораторному контролю, или когда программу нужно быстро '
     'обновить под новые правила.'),
]

NW_RE = re.compile(r'(?<![\w>-])([А-Яа-яЁё]+-[А-Яа-яЁё]+)(?![\w-])')
# номера документов не разрываем на дефисе: «СанПиН 2.3/2.4.4282-26», «248-ФЗ», «ТР ТС 021/2011»
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
        t = typo(t)
        # суммы не разрываем: «19 900 ₽», «10 000–20 000 ₽»
        t = re.sub(r'(?<=\d) (?=\d{3}(?!\d))', '\u00a0', t)
        t = re.sub(r'(?<=\d) (?=₽)', '\u00a0', t)
        # обозначение документа не отрывается от номера: «СП 1.1.1058-01», «СанПиН 2.1.3684-21»
        t = re.sub(r'\b(СП|СанПиН|ГОСТ|МУК|МУ|МР) (?=\d|<span class="nw">\d)', '\\1\u00a0', t)
        out.append(t)
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
            '    <div class="head"><div class="eyebrow">Вопросы</div><h2>Вопросы <em>о программе производственного контроля</em></h2></div>',
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
            {'@type': 'ListItem', 'position': 2, 'name': CRUMB, 'item': URL}]},
        {'@type': 'Service', '@id': URL + '#service', 'name': NAME,
         'alternateName': ['Разработка ППК', 'Разработка программы производственного контроля'],
         'serviceType': 'Разработка программы производственного контроля по СП 1.1.1058-01',
         'description': DESC, 'url': URL, 'provider': org,
         'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
         'audience': {'@type': 'BusinessAudience',
                      'audienceType': 'Офисы, склады, гостиницы, магазины непродовольственных товаров, производства непищевой продукции'},
         'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'RUB', 'lowPrice': 5900,
                    'description': 'Стоимость зависит от вида деятельности, числа помещений и должностей и объёма лабораторных исследований'},
         'isRelatedTo': {'@type': 'Service', 'name': 'Разработка программы производственного контроля по ХАССП', 'url': HACCP_URL}},
        {'@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE, 'description': DESC, 'inLanguage': 'ru',
         'datePublished': DATE, 'dateModified': DATE,
         'about': {'@id': URL + '#service'},
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': SITE + 'img/rppk-hero.webp', 'width': 1920, 'height': 1072}},
        {'@type': 'FAQPage', '@id': URL + '#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in FAQ]},
    ]
    return '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False) + '</script>'


def cut(s, start, end, after=False):
    i = s.index(start)
    j = s.index(end, i)
    return s[i:j + (len(end) if after else 0)]


def more_link(m):
    slug, text = m.group(1), m.group(2)
    if not (ROOT / slug / 'index.html').exists():
        return ''  # отраслевой страницы нет в этой сборке — ссылку не ставим
    return f'<a class="rp-more" href="../{slug}/"><span>{text}</span> →</a>'


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
    # кнопка в шапке и в мобильном меню — заявка на ППК (бесплатно у компании только обследование по пест-контролю)
    top, n = re.subn(r'(<a href="#zayavka" class="btn btn-w btn-sm"[^>]*><span class="btn-t">)[^<]*(</span>)', r'\1Заказать ППК\2', top, count=1)
    assert n == 1, 'шаблон: нет кнопки заявки в шапке'
    top, n = re.subn(r'(<a href="#zayavka" class="btn btn-w btn-lg"><span class="btn-t">)[^<]*(</span></a>\n</nav>)', r'\1Заказать разработку ППК\2', top, count=1)
    assert n == 1, 'шаблон: нет кнопки заявки в мобильном меню'

    # ---------------- содержимое
    main = (HERE / 'main.html').read_text(encoding='utf-8')
    main = main.replace('<!--FAQ-->', faq_section())
    main = re.sub(r'<!--MORE:([a-z0-9-]+):([^>]*?)-->', more_link, main)
    main = typeset(main)
    main = re.sub(r'<!--ICON:([a-z-]+)-->', lambda m: icons[m.group(1)], main)
    contacts = cut(tpl, '      <div class="cta-contacts"', '    </div>\n    <form', after=False)
    contacts = contacts.replace(' data-fade', '')
    main = main.replace('<!--CTA_CONTACTS-->\n', contacts.rstrip('\n') + '\n')
    assert '<!--' not in main.replace('<!-- ', ''), 'остались метки в main.html'

    # ---------------- подвал, плавающие кнопки, скрипты
    bottom = tpl[tpl.index('</main>') + len('</main>'):tpl.index('<script>\n/* Предпросмотр')]
    # нижняя панель на телефоне: вместо «Обследование» (бесплатно только обследование по пест-контролю) — заказ ППК
    bottom, n = re.subn(r'(<a href="#zayavka" class="c2"><span>)[^<]*', r'\g<1>Заказать ППК', bottom)
    assert n == 1, 'шаблон: нет нижней панели на телефоне'
    # из скрипта шаблона берём только «Предпросмотр» (заглушка send.php вне рабочего домена):
    # самопроверки и схемы зон на этой странице нет
    page_js = cut(tpl, '<script>\n/* Предпросмотр', '</script>', after=True)
    pv = re.match(r'<script>\n(/\* Предпросмотр[^\n]*\*/\n\(function\(\)\{.*?\n?\}\)\(\);)', page_js, re.S)
    assert pv, 'шаблон: не найден скрипт предпросмотра'
    page_js = '<script>\n' + pv.group(1) + '\n</script>'
    # только загрузчик анимаций: скрипт формы пищевой страницы (unify.py) сюда не переносим — у аудита свои поля
    li = tpl.index('<script>\n  /* скрипты анимаций')
    loader = tpl[li:tpl.index('</script>', li) + len('</script>')] + '\n'
    form_js = ("<script>/* Форма: задача, адрес, комментарий и страница — в поле msg, которое читает send.php */\n"
               "document.addEventListener('submit',function(ev){var f=ev.target;if(!f||f.id!=='form')return;var e=f.elements,"
               "g=e.goal.value||'не выбрана',a=e.address.value.trim()||'не указан',c=e.comment.value.trim();"
               "e.msg.value='Задача: '+g+'\\nАдрес: '+a+(c?'\\nКомментарий: '+c:'')+"
               "'\\nСтраница: Разработка ППК (/razrabotka-ppk/)';},true);</script>\n")

    html = (head + '<style>' + css + '</style>\n' + json_ld() + '\n' + top + main + bottom + page_js + '\n'
            + loader + form_js + '</body>\n</html>\n')
    out = ROOT / 'razrabotka-ppk' / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print('ok', out.relative_to(ROOT), len(html) // 1024, 'КБ')


if __name__ == '__main__':
    main()
