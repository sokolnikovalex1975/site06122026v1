#!/usr/bin/env python3
"""Сборка страницы «Санитарный аудит (СЭС-аудит)» — sanitarnyy-audit/index.html.

Шаблон — готовая отраслевая страница pishchevoe-proizvodstvo/index.html: из неё берутся шапка, мобильное меню,
подвал, плавающие кнопки, ранний скрипт и подключение анимаций, общие стили отраслевой страницы.
Своё у страницы: <head> (заголовок, описание, Open Graph, структурированные данные), стили page.css,
содержимое main.html и вопросы FAQ (список ниже — из него же собирается FAQPage).

Дальше страницу доводит общий конвейер сайта (бегущая строка, «Смотрите также», разметка анимаций, общее меню):

    python3 tools/sanitarnyy-audit/build_page.py
    python3 tools/site/build_site.py

Ссылки «Подробнее» на отраслевые страницы (метки <!--MORE:адрес:текст--> в main.html) ставятся, только если
такая страница есть в репозитории: в версии для Timeweb не появится ссылка на страницу, которой нет на сайте.

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
SLUG = 'sanitarnyy-audit/'
URL = SITE + SLUG
TITLE = 'Санитарный аудит (СЭС-аудит) в Москве и МО — ПЕСТКОНТРОЛЬ Центр'
NAME = 'Санитарный аудит (СЭС-аудит)'
OG_TITLE = 'Санитарный аудит (СЭС-аудит) предприятия в Москве и области'
DESC = ('Санитарный аудит (СЭС-аудит) в Москве и области по СанПиН 2026 года и проверочным листам Роспотребнадзора: '
        'смывы и пробы воздуха, акт с реестром нарушений и планом устранения. От 9 000 ₽.')
OG_ALT = 'Санитарный врач проверяет температуру в холодильнике на кухне ресторана'
DATE = '2026-11-06'
AUTHOR = {'@type': 'Person', 'name': 'Марианна Семерина', 'jobTitle': 'Санитарный врач'}
# фото в карточке автора иллюстративное (сгенерировано), поэтому image у Person не указываем

LICENSE_URL = 'https://fp.rospotrebnadzor.ru/licen/?oper=search&amp;numb_history=&amp;numb=&amp;firmget_name=&amp;ogrn_inn_nza=7714462211'
CGON_PPK = ('https://cgon.rospotrebnadzor.ru/biznesu/profilaktika-nadzor-uslsugi/profilakticheskie-meropriatiya/'
            'o-prinyatii-rospotrebnadzorom-normativno-pravovykh-aktov-/')
FAQ = [
    ('Что такое СЭС-аудит?',
     'Это добровольная проверка предприятия на соответствие санитарным нормам, которую проводит независимый специалист '
     'до прихода Роспотребнадзора. По итогам вы получаете акт с нарушениями и планом их устранения; штрафов '
     'и предписаний аудит не влечёт. Название осталось от санитарно-эпидемиологических станций (СЭС), функции которых '
     'сегодня выполняет Роспотребнадзор.'),
    ('Обязателен ли санитарный аудит?',
     'Нет. Обязателен производственный контроль: его проводят сами предприниматели и юридические лица (ст. 11 и 32 '
     'Федерального закона № 52-ФЗ). Аудит показывает, как этот контроль работает на деле.'),
    ('Чем санитарный аудит отличается от проверки Роспотребнадзора?',
     'Аудит проводит приглашённый специалист по вашему заказу, проверку — инспектор по основаниям 248-ФЗ. После аудита '
     'остаются акт и план устранения, после проверки — акт, а при нарушениях — предписание и протокол. Результаты '
     'аудита видит только заказчик.'),
    ('Сколько стоит санитарный аудит в Москве?',
     'От 9 000 ₽ за кафе без кухни до 20 000 ₽ и выше за пищевое производство; смывы и пробы воздуха входят '
     'в стоимость. Точную сумму называем после короткого разговора о площади и виде деятельности.'),
    ('Сколько длится аудит?',
     'Выезд занимает от 2 до 6 часов в зависимости от площади и числа зон, смену при этом не останавливаем. Акт '
     'с протоколами лабораторных исследований передаём через 3 рабочих дня.'),
    ('Какие документы подготовить к аудиту?',
     'Программу производственного контроля; договоры на вывоз отходов, дезинфекцию, дезинсекцию и дератизацию, стирку '
     'санитарной одежды и лабораторные исследования; личные медицинские книжки; журналы (температура холодильников, '
     'бракераж, здоровье персонала, пест-контроль); протоколы лабораторных исследований; документы ХАССП. Если '
     'чего-то нет, это тоже результат аудита.'),
    ('Нужно ли менять программу производственного контроля после 1 сентября 2026 года?',
     'Да, если она ссылается на отменённые СанПиН 2.3/2.4.3590-20, СП 2.3.6.3668-20, СП 2.1.3678-20 или '
     'СП 2.2.3670-20. С 1 сентября 2026 года действуют новые правила, и '
     f'<a href="{CGON_PPK}" target="_blank" rel="noopener">Центр гигиенического образования населения '
     'Роспотребнадзора</a> напоминает: «Не забудьте внести изменения в программу производственного контроля».'),
    ('Гарантируете, что проверка пройдёт без штрафов?',
     'Нет, и честный подрядчик такого не обещает: решение принимает инспектор, а проверка не ограничивается вопросами '
     'проверочного листа. Аудит снижает риск: нарушения, которые вы устранили заранее, инспектор уже не найдёт.'),
    ('Проверяете ли вы по проверочным листам Роспотребнадзора?',
     'Да. С октября 2026 года действуют новые формы (приказы Роспотребнадзора от 20.07.2026 № 578 и № 580): в листе '
     'для общепита 142 вопроса, для торговли пищевой продукцией — 181. Мы проходим лист вашего вида деятельности '
     'и добавляем требования, которые инспектор вправе проверить сверх него.'),
    ('Делаете ли вы лабораторные исследования?',
     'Да, смывы и пробы воздуха входят в стоимость аудита. Во время выезда отбираем смывы с рабочих поверхностей, '
     'оборудования, инвентаря и рук персонала и пробы воздуха в помещениях. Протоколы прикладываем к акту и сверяем '
     'с планом лабораторных исследований из вашей программы производственного контроля.'),
    ('Засчитывается ли стоимость аудита, если потом заключить договор на пест-контроль?',
     'Да. Если после аудита вы заключаете с нами договор на пест-контроль, стоимость аудита засчитываем в счёт оплаты '
     'обслуживания.'),
    ('Можно ли провести аудит сети магазинов или ресторанов?',
     'Да. Проверяем объекты по одному чек-листу и сводим результаты в общую таблицу, чтобы были видны нарушения, '
     'которые повторяются по всей сети.'),
    ('Работаете ли вы с частными лицами?',
     'Нет. Санитарный аудит проводим для организаций и ИП в Москве и Московской области.'),
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
        out.append(typo(t))
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
            '    <div class="head"><div class="eyebrow">Вопросы</div><h2>Вопросы <em>о санитарном аудите</em></h2></div>',
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
         'alternateName': ['СЭС-аудит', 'Санитарно-эпидемиологический аудит'],
         'serviceType': 'Санитарный аудит (СЭС-аудит) по СанПиН и проверочным листам Роспотребнадзора',
         'description': DESC, 'url': URL, 'provider': org,
         'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
         'audience': {'@type': 'BusinessAudience',
                      'audienceType': 'Рестораны и кафе, магазины и торговые сети, пищевые и фармацевтические производства, склады, гостиницы'},
         'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'RUB', 'lowPrice': 9000,
                    'description': 'Стоимость зависит от вида и площади объекта; смывы и пробы воздуха входят в стоимость аудита'}},
        {'@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE, 'description': DESC, 'inLanguage': 'ru',
         'datePublished': DATE, 'dateModified': DATE, 'author': AUTHOR,
         'about': {'@id': URL + '#service'},
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': SITE + 'img/san-hero.webp', 'width': 1920, 'height': 1072}},
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
    return f'<a class="sa-more" href="../{slug}/"><span>{text}</span> →</a>'


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
         f'<meta property="og:image" content="{SITE}img/san-og.jpg">\n'
         '<meta property="og:image:type" content="image/jpeg">\n'
         '<meta property="og:image:width" content="1200">\n'
         '<meta property="og:image:height" content="630">\n'
         f'<meta property="og:image:alt" content="{OG_ALT}">\n'
         '<meta name="twitter:card" content="summary_large_image">'),
        (r'<link rel="preload" href="\.\./img/food-hero\.webp"[^>]*>\n<link rel="preload" href="\.\./img/food-hero-mob\.webp"[^>]*>',
         '<link rel="preload" as="image" media="(min-width:761px)" imagesrcset="../img/san-hero-1440.webp 1440w, ../img/san-hero.webp 1920w" imagesizes="100vw" fetchpriority="high">\n'
         '<link rel="preload" as="image" media="(max-width:760px)" imagesrcset="../img/san-hero-mob-760.webp 760w, ../img/san-hero-mob.webp 1024w" imagesizes="100vw" fetchpriority="high">'),
    ]
    for pat, new in rep:
        head, n = re.subn(pat, lambda m: new, head, count=1)
        assert n == 1, 'шаблон: не найдено ' + pat
    assert 'food-hero' not in head, 'шаблон: осталась предзагрузка фото пищевой страницы'
    css = tpl[tpl.index('<style>') + 7:tpl.index('</style>')]
    css += '\n' + (HERE / 'page.css').read_text(encoding='utf-8').strip()

    # ---------------- шапка, меню (общее меню потом пересобирает tools/menu/apply_menu.py)
    top = tpl[tpl.index('</head>'):tpl.index('<main id="main"')]
    top = top.replace('<body class="d-page">', '<body class="d-page sa-page">', 1)
    assert 'sa-page' in top

    # ---------------- содержимое
    main = (HERE / 'main.html').read_text(encoding='utf-8')
    main = main.replace('<!--FAQ-->', faq_section())
    main = re.sub(r'<!--MORE:([a-z0-9-]+):([^>]*?)-->', more_link, main)
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
    # из скрипта шаблона берём только «Предпросмотр» (заглушка send.php вне рабочего домена):
    # самопроверки и схемы зон на этой странице нет
    page_js = cut(tpl, '<script>\n/* Предпросмотр', '</script>', after=True)
    pv = re.match(r'<script>\n(/\* Предпросмотр[^\n]*\*/\n\(function\(\)\{.*?\n?\}\)\(\);)', page_js, re.S)
    assert pv, 'шаблон: не найден скрипт предпросмотра'
    page_js = '<script>\n' + pv.group(1) + '\n</script>'
    # только загрузчик анимаций: скрипт формы пищевой страницы (unify.py) сюда не переносим — у аудита свои поля
    li = tpl.index('<script>\n  /* скрипты анимаций')
    loader = tpl[li:tpl.index('</script>', li) + len('</script>')] + '\n'
    form_js = ("<script>/* Форма: цель аудита, адрес, комментарий и страница — в поле msg, которое читает send.php */\n"
               "document.addEventListener('submit',function(ev){var f=ev.target;if(!f||f.id!=='form')return;var e=f.elements,"
               "g=e.goal.value||'не выбрана',a=e.address.value.trim()||'не указан',c=e.comment.value.trim();"
               "e.msg.value='Цель: '+g+'\\nАдрес: '+a+(c?'\\nКомментарий: '+c:'')+"
               "'\\nСтраница: Санитарный аудит (СЭС-аудит) (/sanitarnyy-audit/)';},true);</script>\n")

    html = (head + '<style>' + css + '</style>\n' + json_ld() + '\n' + top + main + bottom + page_js + '\n'
            + loader + form_js + '</body>\n</html>\n')
    out = ROOT / 'sanitarnyy-audit' / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print('ok', out.relative_to(ROOT), len(html) // 1024, 'КБ')


if __name__ == '__main__':
    main()
