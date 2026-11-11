#!/usr/bin/env python3
"""Отдельное контентное превью текущей главной. Не изменяет корневую страницу или preview-audit.

python3 tools/preview_services/build.py
"""
import hashlib
import html
import json
import pathlib
import re
import shutil
import importlib.util
from urllib.parse import urljoin

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'preview-services'
PROD = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
GITHUB = 'https://sokolnikovalex1975.github.io/site06122026v1/'
SELF = GITHUB + 'preview-services/'
LICENSE = 'https://fp.rospotrebnadzor.ru/licen/?oper=search&numb_history=&numb=%D0%9B064-00111-77%2F01942445'
GROUPS = [
    ('01', 'Защита от вредителей', 'От отдельной задачи до постоянного наблюдения.', [
        ('pest-control', 'Пест-контроль по системе IPM', '#podhod',
         'Обследование, программа, точки контроля и регулярный мониторинг. Обработки по показаниям.'),
        ('deratizatsiya', 'Дератизация', 'deratizatsiya/',
         'Защита объекта от мышей и крыс, обследование путей проникновения и контроль активности.'),
        ('zashchita-gryzuny', 'Защита от проникновения грызунов', 'zashchita-ot-proniknoveniya-gryzunov/',
         'Герметизация проходок, защита дверей и ворот. Обследование, согласованный объём и фотофиксация.'),
        ('dezinsektsiya', 'Дезинсекция', 'dezinsektsiya/',
         'Работа с тараканами, клопами и другими насекомыми с учётом режима и назначения помещений.'),
    ]),
    ('02', 'Санитарные обработки', 'Помещения, оборудование и инженерные системы.', [
        ('dezinfektsiya', 'Дезинфекция', 'dezinfektsiya/',
         'Обеззараживание помещений, поверхностей и оборудования под задачу организации.'),
        ('ventilyatsiya', 'Очистка и дезинфекция вентиляции', 'ochistka-dezinfektsiya-ventilyatsii/',
         'Обследование системы, очистка и дезинфекция, документы по выполненным работам.'),
    ]),
    ('03', 'Документы и проверки', 'От оценки ситуации до документов и исследований.', [
        ('sanitarnyy-audit', 'Санитарный аудит', 'sanitarnyy-audit/',
         'Обследование объекта и документов, перечень несоответствий и план их устранения.'),
        ('ppk', 'Разработка ППК и ППК по ХАССП', 'razrabotka-ppk/',
         'Программа производственного контроля с учётом деятельности и особенностей объекта.'),
        ('rospotrebnadzor', 'Документы для Роспотребнадзора', 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/',
         'Перечень документов, проверочные списки и помощь в определении того, чего не хватает.'),
        ('laboratoriya', 'Лабораторные исследования', 'laboratornye-issledovaniya/',
         'Смывы, исследования воды и воздуха, инструментальные замеры под задачи контроля.'),
    ]),
]
FAQ_QUESTION = 'Какие услуги, кроме пест-контроля, можно заказать?'
FAQ_ANSWER = (
    'ПЕСТКОНТРОЛЬ Центр оказывает услуги дератизации, защиты от проникновения грызунов, дезинсекции и дезинфекции, очистки и дезинфекции вентиляции, '
    'санитарного аудита, разработки ППК и ППК по ХАССП, а также лабораторных исследований. '
    'Помогаем разобраться с документами для Роспотребнадзора: на сайте есть перечень и проверочные списки. '
    'Можно обратиться с одной задачей или обсудить несколько направлений для одного объекта. '
    'Состав работ, стоимость и условия согласуем отдельно по вашей заявке.'
)
ARROW = '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


def catalog():
    groups = []
    for number, title, subtitle, services in GROUPS:
        links = ''.join(
            f'<li><a class="service-link" data-service="{key}" href="{href}">'
            f'<span class="service-link-title">{name}{ARROW}</span><span class="service-link-desc">{desc}</span></a></li>'
            for key, name, href, desc in services
        )
        extra = (
            '<a class="service-contract" data-service="dogovor" href="dogovor-deratizatsiya-dezinsektsiya/">'
            'Договор на дератизацию и дезинсекцию ' + ARROW + '</a>'
        ) if number == '01' else ''
        groups.append(
            f'<article class="card service-group"><div class="service-group-top">'
            f'<span class="service-number">{number}</span><h3>{title}</h3></div>'
            f'<p class="service-group-sub">{subtitle}</p><ul>{links}</ul>{extra}</article>'
        )
    return '''
<section class="s services-s" id="all-services" aria-labelledby="services-title">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Услуги для бизнеса <span class="content-mark">Новый блок</span></div>
      <h2 id="services-title">Все услуги <em>для вашего объекта</em></h2>
      <p class="sub">От защиты от вредителей до лабораторных исследований и документов.
      Можно заказать одну услугу или подобрать несколько направлений под задачи предприятия.</p>
    </div>
    <div class="service-groups">''' + ''.join(groups) + '''</div>
    <div class="company-scope" id="about-company">
      <div><div class="eyebrow">О компании</div><h3>Санитарные задачи<br><em>в одном окне</em></h3></div>
      <div class="company-scope-text">
        <p>ПЕСТКОНТРОЛЬ Центр работает с организациями Москвы и Московской области: пищевыми и фармацевтическими
        производствами, магазинами, ресторанами, складами и гостиницами. Основное направление: пест-контроль
        и пест-менеджмент по системе IPM. Также оказываем услуги санитарной обработки, лабораторных исследований
        и разработки документов производственного контроля.</p>
        <p>С одной задачи можно начать, а связанные вопросы обсудить с той же командой. Например, обследование
        помогает определить, какие обработки, исследования и документы нужны объекту. Состав и условия работ
        согласуем до их начала.</p>
        <a class="company-license" href="''' + LICENSE.replace('&', '&amp;') + '''" target="_blank" rel="noopener">
          Лицензия на дезинфекцию, дезинсекцию и дератизацию: Л064-00111-77/01942445 ''' + ARROW + '''</a>
      </div>
    </div>
  </div>
</section>
'''


def normalize_links(s):
    def anchor(m):
        tag = m.group(0)
        href = re.search(r'href="([^"]*)"', tag)
        if not href:
            return tag
        value = href.group(1)
        if value and not re.match(r'^(#|https?:|tel:|mailto:|data:)', value):
            tag = tag.replace('href="' + value + '"', 'href="' + urljoin(GITHUB, value) + '"')
        return tag
    return re.sub(r'<a\b[^>]*>', anchor, s)


def schema():
    offer_groups = []
    for _, title, _, services in GROUPS:
        offers = []
        for key, name, href, desc in services:
            offers.append({
                '@type': 'Offer',
                'itemOffered': {
                    '@type': 'Service', '@id': PROD + '#service-' + key, 'name': name,
                    'description': desc, 'url': urljoin(PROD, href), 'provider': {'@id': PROD + '#organization'},
                    'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
                },
            })
        offer_groups.append({'@type': 'OfferCatalog', 'name': title, 'itemListElement': offers})
    data = {
        '@context': 'https://schema.org',
        '@graph': [
            {
                '@type': 'Organization', '@id': PROD + '#organization', 'name': 'ПЕСТКОНТРОЛЬ Центр',
                'url': PROD, 'telephone': '+7-495-104-35-70', 'email': 'b2b@pestcontrol-center.ru',
                'description': 'Пест-контроль и санитарные услуги для организаций Москвы и Московской области: защита от вредителей, обработки, лабораторные исследования и документы производственного контроля.',
                'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
                'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': 'Услуги для бизнеса', 'itemListElement': offer_groups},
            },
            {
                '@type': 'FAQPage', '@id': PROD + '#company-services-faq',
                'mainEntity': [{'@type': 'Question', 'name': FAQ_QUESTION, 'acceptedAnswer': {'@type': 'Answer', 'text': FAQ_ANSWER}}],
            },
        ],
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    s = (ROOT / 'index.html').read_text(encoding='utf-8')
    original = s
    # Превью без интро, хранилища, производственных обработчиков и счётчиков.
    # Статичный fallback задаём сразу, чтобы общий интерактив не перестраивал все разделы после первого кадра.
    s = s.replace('<html lang="ru">', '<html lang="ru" class="anim-fail anim-ready no-intro">', 1)
    s, count = re.subn(r'<script>\s*/\* начальные состояния анимаций.*?</script>\s*', '', s, count=1, flags=re.S)
    assert count == 1
    s, count = re.subn(r'<script>\s*/\* скрипты анимаций.*?</script>', '<script src="interactions.js" defer></script>\n<script src="content-preview.js" defer></script>', s, count=1, flags=re.S)
    assert count == 1
    s = s.replace('</head>', '<link rel="stylesheet" href="content-preview.css">\n' + schema() + '\n</head>', 1)
    s = s.replace('noindex, nofollow', 'noindex, nofollow, noarchive', 1)
    s = s.replace('<body>', '''<body>
<div class="content-toolbar" role="region" aria-label="Контентное превью">
  <span>Тестовая главная<span class="toolbar-extra">: только дополнение контентом</span></span>
  <a href="#all-services">Все услуги</a>
  <button id="content-notes" type="button" aria-pressed="false">Показать новое</button>
</div>''', 1)
    hero_end = s.index('    </div>\n    <aside class="panel"', s.index('<div class="hero-copy"'))
    s = s[:hero_end] + (
        '      <p class="hero-scope"><span class="content-mark">Новая строка</span>'
        'Не только пест-контроль: обработки, лаборатория и документы для бизнеса. '
        '<a href="#all-services">Все услуги компании ' + ARROW + '</a></p>\n'
    ) + s[hero_end:]
    insert = s.index('<!-- ============', s.index('id="zadachi"'))
    s = s[:insert] + catalog() + '\n' + s[insert:]
    faq = (
        '<div class="card qa service-faq"><button aria-expanded="false" aria-controls="a-services" id="q-services">'
        + FAQ_QUESTION + '<span class="content-mark">Новый вопрос</span><span class="pm"></span></button>'
        '<div class="ans" id="a-services" role="region" aria-labelledby="q-services"><div><p>'
        + FAQ_ANSWER + ' <a href="#all-services">Посмотреть все услуги</a>.</p></div></div></div>\n'
    )
    s = s.replace('<div class="faq-col" data-group="faq">', '<div class="faq-col" data-group="faq">\n' + faq, 1)
    s = s.replace('Обработки на\u00a0всех трёх объектах уже проводили.', 'Обработки на\u00a0всех трёх объектах уже проводили до\u00a0нас.', 1)

    # Оставляем привычный внешний вид формы, но исключаем любую реальную отправку.
    def demo_form(m):
        f = m.group(0)
        f = f.replace('novalidate data-form', 'novalidate data-form action="#content-form-result" method="post"', 1)
        f = f.replace('<div class="fbody">', '<div class="fbody"><fieldset data-content-fields disabled><legend class="sr-only">Демонстрационная заявка</legend>', 1)
        f = f.replace('Заполнение займёт меньше минуты', 'Тестовая форма: данные не отправляются и не сохраняются', 1)
        f = f.replace('Отправить заявку</span>', 'Проверить заполнение</span>', 1)
        f, n = re.subn(r'\s*<div class="ok"[^>]*>.*?</div>(?=\s*</form>)', '', f, count=1, flags=re.S)
        assert n == 1
        f, n = re.subn(
            r'</div>\s*</form>$',
            '</fieldset><p class="content-form-result" id="content-form-result" role="status" aria-live="polite" tabindex="-1"></p>'
            '<button class="content-form-reset" id="content-form-reset" type="button" hidden>Очистить тестовые данные</button>'
            '<noscript>Без JavaScript тестовая форма недоступна. Заявки не отправляются.</noscript></div></form>',
            f, count=1,
        )
        assert n == 1
        return f
    s, count = re.subn(r'<form\b[^>]*>.*?</form>', demo_form, s, count=1, flags=re.S)
    assert count == 1
    s = normalize_links(s)
    # Новая услуга доступна также внутри прикреплённого превью. Остальные адреса не меняем.
    s = s.replace('href="' + GITHUB + 'zashchita-ot-proniknoveniya-gryzunov/"',
                  'href="zashchita-ot-proniknoveniya-gryzunov/index.html"')
    (OUT / 'index.html').write_text(s, encoding='utf-8')
    (OUT / '.nojekyll').touch()
    shutil.copy2(ROOT / 'preview-audit/interactions.js', OUT / 'interactions.js')
    shutil.copy2(ROOT / 'search.min.js', OUT / 'search.min.js')
    idx = json.loads((ROOT / 'search-index.json').read_text())
    for entry in idx.get('p', []):
        if len(entry) > 1:
            entry[1] = urljoin(SELF if not entry[1] or entry[1].startswith('#') else GITHUB, entry[1])
    for entry in idx.get('i', []):
        if len(entry) > 1:
            entry[1] = urljoin(SELF if not entry[1] or entry[1].startswith('#') else GITHUB, entry[1])
    (OUT / 'search-index.json').write_text(json.dumps(idx, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    paths = set(re.findall(r'(?:img|fonts)/[A-Za-z0-9_.-]+\.(?:webp|woff2)', s))
    for path in paths:
        dest = OUT / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, dest)
    forbidden = ['mc.yandex.ru', 'track.radist.me', 'app.uiscom.ru/static/', 'sessionStorage', 'localStorage', "fetch('/send.php"]
    assert not any(word in s for word in forbidden)
    assert (ROOT / 'index.html').read_text() == original
    module_path = ROOT / 'tools/zashchita-ot-proniknoveniya-gryzunov/build_preview.py'
    if (ROOT / 'zashchita-ot-proniknoveniya-gryzunov/index.html').exists():
        spec = importlib.util.spec_from_file_location('proof_preview', module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.build()
    print('Built', OUT, '| original SHA256:', hashlib.sha256(original.encode()).hexdigest(), '| copied assets:', len(paths))


if __name__ == '__main__':
    main()
