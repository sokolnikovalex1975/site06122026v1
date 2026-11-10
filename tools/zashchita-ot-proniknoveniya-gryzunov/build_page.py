#!/usr/bin/env python3
"""Новая страница услуги на актуальном шаблоне сайта, без редизайна.

Сборка: python3 tools/zashchita-ot-proniknoveniya-gryzunov/build_page.py
Публикация этой задачи ограничена GitHub. build_prod.py лишь проверяет будущую
совместимость с Timeweb и сам ничего не выгружает.
"""
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
from typo import typo
import unify
import mobile_crumbs
import hero_fold
import required_marks
import table_inset

SLUG = 'zashchita-ot-proniknoveniya-gryzunov'
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
URL = SITE + SLUG + '/'
NAME = 'Защита от проникновения грызунов'
TITLE = 'Защита от проникновения грызунов в Москве | ПЕСТКОНТРОЛЬ'
DESC = ('Защита от проникновения грызунов в Москве и МО: обследование, герметизация '
        'проходок, защита ворот и дверей, фотоотчёт. Расчёт после осмотра объекта.')
OUT = ROOT / SLUG / 'index.html'
COUNTERS_HASH = '3c4a1e15f773b49bbde7e69f5f8168aaa1c51f22a1d3dc338798e53be47fb652'


def replace_once(pattern, replacement, text):
    text, n = re.subn(pattern, lambda _: replacement, text, count=1, flags=re.S)
    assert n == 1, pattern
    return text


def clean(markup):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', markup))).strip()


def build():
    import hashlib
    assert hashlib.sha256((ROOT / 'server/counters.html').read_bytes()).hexdigest() == COUNTERS_HASH
    template = (ROOT / 'deratizatsiya/index.html').read_text(encoding='utf-8')
    main = (HERE / 'main.html').read_text(encoding='utf-8')
    hero = re.search(r'<div class="d-hero-media".*?</div>\s*</div>', template, re.S).group(0)
    contacts = re.search(r'<div class="cta-contacts".*?</div>\s*</div>', template, re.S).group(0)
    form = re.search(r'<form class="form".*?</form>', template, re.S).group(0)
    form = replace_once(r'<h3>.*?</h3>', '<h3>Заявка на защиту от грызунов</h3>', form)
    form = form.replace('Заказать бесплатное обследование', 'Обследовать объект')
    form = replace_once(
        r'(<select id="f-service".*?</select>)',
        '<select id="f-service" name="service"><option selected>Защита от проникновения грызунов</option>'
        '<option>Обследование путей проникновения</option><option>Устранение инженерных замечаний</option>'
        '<option>Защита и дератизация объекта</option></select>', form)
    form = form.replace('согласовать день бесплатного обследования объекта', 'уточнить задачу и согласовать обследование объекта')
    check = unify.ICONS['lucide-circle-check']
    strip = unify.strip_html('Инженерная защита от грызунов', [
        ('lucide-scan-search', 'Обследование', 'доступных участков'),
        ('lucide-notebook-pen', 'Фотофиксация', 'дефектов здания'),
        ('lucide-shield-check', 'Защита', 'дверей, ворот и вводов'),
        ('lucide-clipboard-check', 'Смета', 'до начала работ'),
        ('lucide-map-pinned', 'Контроль', 'выполненных участков'),
    ])
    for key, value in {
        'hero-media': hero, 'contacts': contacts, 'form': form, 'check': check,
        'strip': strip, 'related': unify.related_html('../', ['derat', 'sklady', 'prog', 'san'])
    }.items():
        main = main.replace('{{' + key + '}}', value)
    assert '{{' not in main
    main = typo(main)
    s = replace_once(r'<main id="main"[^>]*>.*?</main>', main.strip(), template)
    s = replace_once(r'<title>.*?</title>', '<title>' + TITLE + '</title>', s)
    s = replace_once(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + DESC + '">', s)
    for attr in ['canonical', 'og:url']:
        if attr == 'canonical':
            s = replace_once(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="' + URL + '">', s)
        else:
            s = replace_once(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="' + URL + '">', s)
    s = replace_once(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="' + TITLE + '">', s)
    s = replace_once(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="' + DESC + '">', s)
    s = s.replace('<body class="d-page">', '<body class="d-page proof-page">', 1)
    assert 'proof-page' in s
    # Сохраняем общие компоненты; добавляем только локальную раскладку текстовых блоков.
    css = re.sub(r'/\*.*?\*/', '', (HERE / 'page.css').read_text(), flags=re.S)
    css = re.sub(r'\s*\n\s*', '', css).strip()
    s = s.replace('</head>', '<style id="proof-page-css">' + css + '</style>\n</head>', 1)
    s = s.replace('</head>', '<noscript><style>.proof-page .qa .ans{grid-template-rows:1fr;opacity:1}.proof-page #form{display:none}</style></noscript>\n</head>', 1)
    # На новой странице дератизация в меню — соседняя услуга, не текущая страница.
    s = s.replace('href="./" aria-current="page"', 'href="../deratizatsiya/"')
    s = s.replace('href="../deratizatsiya/" aria-current="page"', 'href="../deratizatsiya/"')
    # Удаляем только старый локальный скрипт дератизации; общий обработчик, FX и loader сохранены.
    script = (HERE / 'page.js').read_text(encoding='utf-8').strip()
    s = replace_once(r'<script>\s*/\* Предпросмотр: вне рабочего домена.*?</script>', '<script>\n' + script + '\n</script>', s)
    pairs = re.findall(
        r'<div class="card qa"><button[^>]*>(.*?)<span class="pm"></span></button>'
        r'<div class="ans"[^>]*><div><p>(.*?)</p></div></div></div>', main, flags=re.S)
    assert len(pairs) == 8, len(pairs)
    graph = {
        '@context': 'https://schema.org',
        '@graph': [
            {'@type': 'Organization', '@id': SITE + '#organization', 'name': 'ПЕСТКОНТРОЛЬ Центр',
             'url': SITE, 'telephone': '+7-495-104-35-70', 'email': 'b2b@pestcontrol-center.ru'},
            {'@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE,
             'description': DESC, 'inLanguage': 'ru-RU', 'mainEntity': {'@id': URL + '#service'}},
            {'@type': 'Service', '@id': URL + '#service', 'name': NAME, 'url': URL,
             'serviceType': 'Инженерно-техническая защита зданий от проникновения крыс и мышей',
             'description': DESC, 'provider': {'@id': SITE + '#organization'},
             'areaServed': [{'@type': 'City', 'name': 'Москва'},
                            {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
             'audience': {'@type': 'BusinessAudience', 'audienceType': 'Юридические лица и индивидуальные предприниматели'}},
            {'@type': 'BreadcrumbList', '@id': URL + '#breadcrumbs', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE},
                {'@type': 'ListItem', 'position': 2, 'name': 'Дератизация', 'item': SITE + 'deratizatsiya/'},
                {'@type': 'ListItem', 'position': 3, 'name': NAME, 'item': URL}]},
            {'@type': 'FAQPage', '@id': URL + '#faq', 'mainEntity': [
                {'@type': 'Question', 'name': clean(q), 'acceptedAnswer': {'@type': 'Answer', 'text': clean(a)}}
                for q, a in pairs]},
        ]
    }
    s = replace_once(r'<script type="application/ld\+json">.*?</script>',
                     '<script type="application/ld+json">' + json.dumps(graph, ensure_ascii=False, separators=(',', ':')) + '</script>', s)
    assert 'noindex, nofollow' in s and 'ym(113675622' not in s
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(s, encoding='utf-8')
    unify.process_inner(str(OUT.relative_to(ROOT)), unify.PAGES[str(OUT.relative_to(ROOT))])
    # Тот же порядок локальных правил, что и в общей сборке сайта.
    s = OUT.read_text(encoding='utf-8')
    s, _ = mobile_crumbs.apply(s)
    s, _ = table_inset.apply(s)
    s, _ = hero_fold.apply(s)
    s, _, _ = required_marks.apply(s)
    # Сохраняем существующий ind-links после остальных общих правил без изменения его содержимого.
    ind_rule = re.search(r'<style id="ind-links">.*?</style>\n?', s, re.S)
    if ind_rule:
        s = s[:ind_rule.start()] + s[ind_rule.end():]
        s = s.replace('</head>', ind_rule.group(0).rstrip() + '\n</head>', 1)
    OUT.write_text(s, encoding='utf-8')
    print('ok', OUT.relative_to(ROOT), len(s), 'символов; title', len(TITLE), '; description', len(DESC))


if __name__ == '__main__':
    build()
