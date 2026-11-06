#!/usr/bin/env python3
"""Сборка страницы /sklady-i-logistika/index.html — «Пест-контроль для складов и логистики» (06.11.2026).

python3 tools/sklady/assemble.py  ->  sklady-i-logistika/index.html (превью с noindex).
После сборки: python3 tools/site/build_site.py (анимации, «Смотрите также», меню, sitemap);
версия для Timeweb со счётчиками — python3 tools/site/build_prod.py.

Шаблон (head, шапка, интро, подвал, нижняя панель, скрипты и стили компонентов) берётся из страницы
«Дератизация для организаций» и сохраняется в template-deratizatsiya.html.
Содержимое: main.html (иконки — {{i:имя}} из icons.json), стили: extra.css, скрипт страницы: page.js.
Фото: tools/sklady/images.py (мастер-файлы хранятся в файлах проекта, не в репозитории).
Счётчики и колл-трекинг в превью не вставляются: их рабочий код — server/counters.html (не менять),
в версию для Timeweb его вставляет tools/site/build_prod.py.
"""
import json, pathlib, re, shutil, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
from typo import typo  # неразрывные пробелы после коротких слов, как в остальных текстах сайта

OUT = ROOT / 'sklady-i-logistika' / 'index.html'
PROD = pathlib.Path(sys.argv[sys.argv.index('--prod') + 1]) if '--prod' in sys.argv else None
DERAT = ROOT / 'deratizatsiya' / 'index.html'
if DERAT.exists():
    shutil.copy2(DERAT, HERE / 'template-deratizatsiya.html')
SRC = HERE / 'template-deratizatsiya.html'

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
URL = SITE + 'sklady-i-logistika/'
TITLE = 'Пест-контроль складов и логистических центров в Москве и МО — ПЕСТКОНТРОЛЬ Центр'
DESC = ('Пест-контроль склада, РЦ и фулфилмента в Москве и области: грызуны, насекомые и моль '
        'без остановки приёмки и отгрузки. Схема точек, журнал и акты для проверок и аудитов. От 4 500 ₽/мес.')
OG_TITLE = 'Пест-контроль складов и логистических центров в Москве и области — ПЕСТКОНТРОЛЬ Центр'
OG_DESC = ('Склады, РЦ, фулфилмент, холодильные и фармацевтические склады: контроль грызунов, насекомых '
           'и вредителей запасов по системе IPM, схема точек, журнал и отчёт по зонам. Обследование — 0 ₽.')
OG_ALT = ('Специалист ПЕСТКОНТРОЛЬ Центра проверяет феромонную ловушку на стеллаже и станцию контроля '
          'грызунов в распределительном центре')


def sub1(pat, rep, s, flags=re.S):
    out, n = re.subn(pat, lambda m: rep, s, count=1, flags=flags)
    assert n == 1, pat
    return out


s = SRC.read_text(encoding='utf-8')
main = (HERE / 'main.html').read_text(encoding='utf-8')
icons = json.loads((HERE / 'icons.json').read_text(encoding='utf-8'))
css = re.sub(r'\s*\n\s*', '', re.sub(r'/\*.*?\*/', '', (HERE / 'extra.css').read_text(encoding='utf-8'), flags=re.S).strip())
js = (HERE / 'page.js').read_text(encoding='utf-8').strip()

# 1. Метаданные, Open Graph, предзагрузка адаптивного Hero
s = sub1(r'<title>.*?</title>', f'<title>{TITLE}</title>', s)
s = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s)
s = s.replace(SITE + 'deratizatsiya/', URL)
s = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_TITLE}">', s)
s = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{OG_DESC}">', s)
s = s.replace(SITE + 'img/deratizatsiya-og.jpg', SITE + 'img/sklady-og.jpg')
s = sub1(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{OG_ALT}">', s)
s = sub1(r'imagesrcset="\.\./img/derat-hero-v1-1440\.webp 1440w, \.\./img/derat-hero-v1\.webp 1920w"',
         'imagesrcset="../img/sklad-hero-1440.webp 1440w, ../img/sklad-hero.webp 1920w"', s)
s = sub1(r'imagesrcset="\.\./img/derat-hero-v1-mob-760\.webp 760w, \.\./img/derat-hero-v1-mob\.webp 1024w"',
         'imagesrcset="../img/sklad-hero-mob-760.webp 760w, ../img/sklad-hero-mob.webp 1024w"', s)

# 2. Стили: компоненты страницы дератизации + дополнения склада
m = re.search(r'<style>(.*?)</style>', s, re.S)
base_css = m.group(1).rstrip()
s = s[:m.start()] + '<style>' + base_css + '\n' + css + '</style>' + s[m.end():]

# 3. Schema.org: BreadcrumbList + Service с ценами + FAQPage
qa_pairs = re.findall(
    r'<div class="card qa">\s*<button[^>]*>(.*?)<span class="pm"></span></button>\s*'
    r'<div class="ans"[^>]*><div><p>(.*?)</p></div></div>', main, flags=re.S)
assert len(qa_pairs) == 10, f'FAQ: {len(qa_pairs)}'
clean = lambda h: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', h).replace('&nbsp;', ' ').replace('&amp;', '&')).strip()


def offer(name, price, unit, code=None):
    spec = {'@type': 'UnitPriceSpecification', 'minPrice': price, 'priceCurrency': 'RUB', 'unitText': unit}
    if code:
        spec['unitCode'] = code
    return {'@type': 'Offer', 'name': name, 'priceCurrency': 'RUB', 'price': price, 'priceSpecification': spec}


ld = {'@context': 'https://schema.org', '@graph': [
    {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE},
        {'@type': 'ListItem', 'position': 2, 'name': 'Отрасли', 'item': SITE + '#otrasli'},
        {'@type': 'ListItem', 'position': 3, 'name': 'Склады и логистика', 'item': URL}]},
    {'@type': 'Service', '@id': URL + '#service',
     'name': 'Пест-контроль складов и логистических центров',
     'serviceType': 'Пест-контроль по системе IPM: дератизация, дезинсекция и мониторинг вредителей запасов на складах',
     'description': DESC, 'url': URL,
     'provider': {'@type': 'Organization', '@id': SITE + '#org', 'name': 'ПЕСТКОНТРОЛЬ Центр',
                  'legalName': 'ООО «Центр дезинфекционных услуг»', 'url': SITE,
                  'telephone': '+7 495 104-35-70', 'email': 'b2b@pestcontrol-center.ru'},
     'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
     'audience': {'@type': 'BusinessAudience', 'audienceType': 'Склады, распределительные центры, логистические операторы, фулфилмент'},
     'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'RUB', 'lowPrice': 600, 'offerCount': 4},
     'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': 'Пест-контроль склада для юридических лиц', 'itemListElement': [
         offer('Дератизация склада до 1 000 м² по договору', 4500, 'в месяц', 'MON'),
         offer('Плановая дезинсекция склада по договору', 4500, 'в месяц', 'MON'),
         offer('Разовая истребительная обработка склада', 3500, 'за выезд'),
         offer('Контейнеры КИК и ловушки для оснащения склада', 600, 'за точку')]}},
    {'@type': 'FAQPage', '@id': URL + '#faq', 'mainEntity': [
        {'@type': 'Question', 'name': clean(q), 'acceptedAnswer': {'@type': 'Answer', 'text': clean(a)}}
        for q, a in qa_pairs]},
]}
ld_json = json.dumps(ld, ensure_ascii=False, separators=(',', ':'))
s = sub1(r'<script type="application/ld\+json">.*?</script>', f'<script type="application/ld+json">{ld_json}</script>', s)

# 4. Основное содержимое: иконки, мессенджеры из шаблона, типографика
msg = re.search(r'<div class="cta-contacts"[^>]*>\s*<a class="ph"[^>]*>[^<]*</a>\s*(<div class="msg">.*?</div>)\s*</div>', s, re.S).group(1)
body = re.sub(r'\{\{i:([a-z0-9-]+)\}\}', lambda m: icons[m.group(1)], main)
body = body.replace('{{msg}}', msg)
assert '{{' not in body, 'не заменены метки'
body = typo(body)
s = sub1(r'<main id="main"[^>]*>.*?</main>', body.strip(), s)

# 5. Скрипт страницы вместо скрипта дератизации (переключатель Hero не нужен)
s = sub1(r'<script>\n/\* Предпросмотр: вне рабочего домена.*?</script>', '<script>\n' + js + '\n</script>', s)

# 6. Нижняя панель и кнопка в шапке без изменений; aria-current расставит tools/menu/apply_menu.py
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(s, encoding='utf-8')
print('ok', OUT.relative_to(ROOT), len(s))
if PROD:
    p = s.replace('<meta name="robots" content="noindex, nofollow"><!-- только в версии для предпросмотра на GitHub Pages: копия не индексируется -->\n', '')
    assert 'noindex' not in p
    PROD.parent.mkdir(parents=True, exist_ok=True)
    PROD.write_text(p, encoding='utf-8')
    print('ok prod', PROD)
