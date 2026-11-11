#!/usr/bin/env python3
"""Сборка страницы «Пест-контроль бизнес-центров, торговых центров и промышленных предприятий» (11.11.2026).

    python3 tools/bctc/build_page.py                         → biznes-tsentry-torgovye-tsentry-predpriyatiya/index.html (превью)
    python3 tools/bctc/build_page.py --template F --out G    → то же из другого шаблона (файл страницы складов с сайта → index.php)

Шаблон — готовая страница «Склады и логистика» (после общего конвейера либо снятая с сайта): из неё берутся <head>,
общие стили отраслевой страницы, шапка, мобильное меню, подвал, плавающие кнопки, скрипты анимаций и — если шаблон
снят с сайта — блок счётчиков (Метрика 113675622, UIS, Radist), который не меняется ни на байт.
Своё у страницы: заголовок, описание, Open Graph, структурированные данные (BreadcrumbList, Service, FAQPage),
page.css, содержимое main.html со схемой zones.svg, вопросы FAQ (список ниже) и page.js.
Меню (шапка, мобильное меню, подвал) пересобирает tools/menu/apply_menu.py — страница в нём уже есть.

Страница пишется сразу в готовом виде (атрибуты анимаций, «Смотрите также», звёздочки в форме), общий конвейер
tools/site/build_site.py её не трогает: unify.py о ней не знает, остальные шаги повторно применимы.
Поле «Тип объекта» формы: обработчик заявок на сервере принимает фиксированный список значений, поэтому у всех
пунктов value="Другое", а выбранный вид объекта page.js пишет первой строкой сообщения (поле msg).
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
sys.path.insert(0, str(ROOT / 'tools' / 'menu'))
from typo import typo  # noqa: E402  неразрывные пробелы после коротких слов, как на остальных страницах
import apply_menu  # noqa: E402

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
SLUG = 'biznes-tsentry-torgovye-tsentry-predpriyatiya'
URL = SITE + SLUG + '/'
TPL_SLUG = 'sklady-i-logistika'
TITLE = 'Пест-контроль бизнес-центров, торговых центров и предприятий в Москве и МО — ПЕСТКОНТРОЛЬ Центр'
DESC = ('Дератизация и дезинсекция бизнес-центров, ТЦ, офисов и промышленных предприятий в Москве и области: '
        'защита кабельных трасс, паркингов и техэтажей, работы без остановки здания, журнал и акты для проверок. '
        'Обследование — 0 ₽.')
OG_TITLE = 'Пест-контроль бизнес-центров, ТЦ и промышленных предприятий в Москве и области — ПЕСТКОНТРОЛЬ Центр'
OG_DESC = ('Один договор на здание: паркинг, техэтажи, щитовые, мусорокамеры, фуд-корт и офисы. '
           'Схема точек, журнал, акты и сводный отчёт для управляющей компании.')
OG_ALT = ('Специалист ПЕСТКОНТРОЛЬ Центра проверяет станцию контроля грызунов у двери щитовой '
          'на техническом этаже бизнес-центра')
NAME = 'Пест-контроль бизнес-центров, торговых центров и промышленных предприятий'
LICENSE_URL = ('https://fp.rospotrebnadzor.ru/licen/?oper=search&amp;numb_history=&amp;numb=&amp;firmget_name=&amp;'
               'ogrn_inn_nza=7714462211')

FAQ = [
    ('Обязана ли управляющая компания проводить дератизацию и дезинсекцию?',
     'Да. Юрлица и ИП обеспечивают дезинсекцию и дератизацию на объектах, которые эксплуатируют (п. 88 СанПиН 3.3686-21), '
     'а в помещениях не должно быть насекомых, грызунов и следов их жизнедеятельности (п. 14 СП 2.1.4284-26).'),
    ('Как часто нужно проводить дератизацию и дезинсекцию в бизнес-центре или ТЦ?',
     'Обследования на насекомых — не реже 2 раз в месяц, оценка заселённости грызунами — каждый месяц '
     '(пп. 98, 101, 110 СанПиН 3.3686-21). Обработки проводят по результатам обследований. '
     'Мусорокамеры осматривают не реже раза в месяц.'),
    ('Как часто нужна дератизация на промышленном предприятии?',
     'Минимум по п. 101 СанПиН 3.3686-21 — обследование раз в месяц. Для столовой и складов пищевой продукции — '
     'не реже 2 раз в месяц и ежемесячная оценка по грызунам. Точную кратность по корпусам записываем в программе '
     'после обследования.'),
    ('Кто отвечает за вредителей — управляющая компания или арендатор?',
     'За общие зоны, технические помещения и территорию — тот, кто эксплуатирует здание. За арендованное помещение — '
     'арендатор. Границы указывают в договоре аренды; мы ведём общую схему, чтобы не оставалось ничьих зон.'),
    ('Можно ли проводить работы в рабочее время?',
     'Осмотры, клеевые мониторы, ловушки и гелевые приманки — да, они без запаха. Обработку распылением проводят '
     'в отсутствие работников и посетителей (п. 14 СП 2.1.4284-26): ночью или в выходной, без наценки.'),
    ('Чем грызуны опасны для инженерных систем?',
     'Крысы и мыши грызут изоляцию кабелей и утеплитель, ходят по кабельным трассам и шахтам. Итог — короткое замыкание, '
     'отказ слаботочных систем и остановка оборудования. Поэтому точки контроля ставим у вводов, в подвале '
     'и на техэтажах, а в щитовых — ловушки вместо приманок с ядом.'),
    ('Что делать, если в офисе увидели мышь или таракана?',
     'Сообщить управляющей компании или позвонить нам. По договору внеплановый выезд — в течение 3 часов, 24/7. '
     'Специалист ищет источник, ставит точки контроля и записывает меры в журнал.'),
    ('Какие документы получит управляющая компания?',
     'Договор, программу, схему точек контроля, журнал учёта, акт после каждого визита, СГР и инструкции на средства, '
     'сводный отчёт за месяц.'),
    ('Нужна ли подрядчику лицензия?',
     'Да. С 1 марта 2025 года услуги по дезинсекции и дератизации оказывают только по лицензии. Работы ведёт '
     'ООО «Центр дезинфекционных услуг», лицензия № <span class="nw">Л064-00111-77/01942445</span> — запись можно проверить в '
     f'<a href="{LICENSE_URL}" target="_blank" rel="noopener">реестре лицензий Роспотребнадзора</a>.'),
    ('Сколько стоит пест-контроль бизнес-центра или торгового центра?',
     'Стоимость считаем после бесплатного обследования: она зависит от площади технических зон, числа точек контроля '
     'и кратности визитов. Офис или помещение арендатора — от 3\u00a0500\u00a0₽ в месяц, разовая обработка — от 3\u00a0500\u00a0₽ за выезд.'),
    ('Обслуживаете ли вы рестораны и магазины арендаторов?',
     'Да, по отдельным программам: для них выше кратность обследований и свои требования к документам. Подробности — '
     'на страницах <a href="../restorany-i-kafe/">ресторанов и кафе</a>, '
     '<a href="../magaziny-i-torgovye-seti/">магазинов и торговых сетей</a>.'),
    ('Можно ли заключить один договор на несколько зданий?',
     'Да. Для управляющих компаний делаем единый договор, общий график визитов и сводный отчёт по всем объектам.'),
]
STRIP = [
    ('cable', 'Кабели и щитовые', 'под контролем'),
    ('building-2', 'Без остановки', 'работы здания'),
    ('file-signature', 'Один договор', 'на общие зоны и арендаторов'),
    ('chart-column', 'Сводный отчёт', 'для управляющей компании'),
    ('moon', 'Ночь и выходные', 'без наценки'),
    ('notebook-pen', 'Журнал и акт', 'после каждого визита'),
    ('clock', 'Выезд за 3 часа', 'по сигналу, 24/7'),
    ('badge-check', 'Лицензия', 'на дезинсекцию и дератизацию'),
]
ARR = ('<svg class="btn-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
       '<path d="M5 12h14M13 6l6 6-6 6"/></svg>')
ARR0 = ARR.replace(' class="btn-ic"', '')
A16 = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" '
       'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def sub1(pat, rep, s, flags=re.S):
    out, n = re.subn(pat, lambda m: rep, s, count=1, flags=flags)
    assert n == 1, 'шаблон: не найдено ' + pat
    return out


def plain(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html)).replace('&amp;', '&').replace('&nbsp;', ' ').replace('\xa0', ' ').strip()


def faq_section():
    def qa(i, q, a):
        return (f'        <div class="card qa">\n'
                f'          <button aria-expanded="false" aria-controls="a{i}" id="q{i}">{q}<span class="pm"></span></button>\n'
                f'          <div class="ans" id="a{i}" role="region" aria-labelledby="q{i}"><div><p>{a}</p></div></div>\n'
                f'        </div>')
    half = (len(FAQ) + 1) // 2
    out = ['<section class="s" id="voprosy">', '  <div class="wrap">', '    <div class="head">',
           '      <div class="eyebrow" data-eyebrow>Вопросы</div>',
           '      <h2 data-split>Вопросы о <span class="nw">пест-контроле</span> <em><span class="nw">бизнес-центров,</span> ТЦ и предприятий</em></h2>',
           '    </div>', '    <div class="faq">']
    n = 0
    for col in (FAQ[:half], FAQ[half:]):
        out.append('      <div class="faq-col" data-group="faq">')
        for q, a in col:
            n += 1
            out.append(qa(n, q, a))
        out.append('      </div>')
    out += ['    </div>', '  </div>', '</section>']
    return '\n'.join(out)


def offer(name, price, unit, code=None):
    spec = {'@type': 'UnitPriceSpecification', 'minPrice': price, 'priceCurrency': 'RUB', 'unitText': unit}
    if code:
        spec['unitCode'] = code
    return {'@type': 'Offer', 'name': name, 'priceCurrency': 'RUB', 'price': price, 'priceSpecification': spec}


def json_ld():
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': 'Отрасли', 'item': SITE + '#otrasli'},
            {'@type': 'ListItem', 'position': 3, 'name': 'Бизнес-центры, ТЦ и предприятия', 'item': URL}]},
        {'@type': 'Service', '@id': URL + '#service', 'name': NAME,
         'serviceType': 'Пест-контроль по системе IPM: дератизация и дезинсекция бизнес-центров, торговых центров, '
                        'офисов и промышленных предприятий (СанПиН 3.3686-21, СП 2.1.4284-26)',
         'description': DESC, 'url': URL,
         'provider': {'@type': 'Organization', '@id': SITE + '#org', 'name': 'ПЕСТКОНТРОЛЬ Центр',
                      'legalName': 'ООО «Центр дезинфекционных услуг»', 'url': SITE,
                      'telephone': '+7 495 104-35-70', 'email': 'b2b@pestcontrol-center.ru'},
         'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
         'audience': {'@type': 'BusinessAudience',
                      'audienceType': 'Управляющие компании, собственники и арендаторы бизнес-центров и торговых центров, '
                                      'промышленные предприятия, технопарки'},
         'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'RUB', 'lowPrice': 600, 'offerCount': 3},
         'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': 'Пест-контроль здания для юридических лиц', 'itemListElement': [
             offer('Пест-контроль офиса или помещения арендатора по договору', 3500, 'в месяц', 'MON'),
             offer('Разовая обработка при очаге', 3500, 'за выезд'),
             offer('Точки контроля: станции и ловушки с установкой и нумерацией', 600, 'за точку')]}},
        {'@type': 'FAQPage', '@id': URL + '#faq', 'mainEntity': [
            {'@type': 'Question', 'name': plain(q), 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}}
            for q, a in FAQ]},
    ]}
    return json.dumps(ld, ensure_ascii=False, separators=(',', ':'))


def build(tpl):
    """Страница из шаблона — готовой страницы складов (превью из репозитория или файл с сайта)."""
    icons = json.loads((HERE / 'icons.json').read_text(encoding='utf-8'))
    css = re.sub(r'\s*\n\s*', '', re.sub(r'/\*.*?\*/', '', (HERE / 'page.css').read_text(encoding='utf-8'), flags=re.S).strip())
    js = (HERE / 'page.js').read_text(encoding='utf-8').strip()
    s = tpl

    # 1. <head>: заголовок, описание, адрес, Open Graph, предзагрузка фото первого экрана
    s = sub1(r'<title>.*?</title>', f'<title>{TITLE}</title>', s)
    s = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s)
    assert s.count(SITE + TPL_SLUG + '/') >= 2
    s = s.replace(SITE + TPL_SLUG + '/', URL)
    s = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_TITLE}">', s)
    s = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{OG_DESC}">', s)
    assert s.count(SITE + 'img/sklady-og.jpg') == 1
    s = s.replace(SITE + 'img/sklady-og.jpg', SITE + 'img/bctc-og.jpg')
    s = sub1(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{OG_ALT}">', s)
    s = sub1(r'imagesrcset="\.\./img/sklad-hero-1440\.webp 1440w, \.\./img/sklad-hero\.webp 1920w"',
             'imagesrcset="../img/bctc-hero-1440.webp 1440w, ../img/bctc-hero.webp 1920w"', s)
    s = sub1(r'imagesrcset="\.\./img/sklad-hero-mob-760\.webp 760w, \.\./img/sklad-hero-mob\.webp 1024w"',
             'imagesrcset="../img/bctc-hero-mob-760.webp 760w, ../img/bctc-hero-mob.webp 1024w"', s)

    # 2. стили: общие стили отраслевой страницы (вместе с блоками складов, они здесь переиспользуются) + page.css
    m = re.search(r'<style>(.*?)</style>', s, re.S)
    s = s[:m.start()] + '<style>' + m.group(1).rstrip() + '\n' + css + '</style>' + s[m.end():]
    s = sub1(r'<body class="d-page">', '<body class="d-page b-page">', s)
    # фон блока заявки: вместо доков склада — паркинг с кабельными трассами
    for a, b in (('sklad-rampa.webp', 'bctc-cta.webp'), ('sklad-rampa-720.webp', 'bctc-cta-720.webp')):
        rule = '#zayavka .cta-bg{background-image:url(../img/' + a + ')}'
        assert s.count(rule) == 1, rule
        s = s.replace(rule, rule.replace(a, b))

    # 3. структурированные данные
    s = sub1(r'<script type="application/ld\+json">.*?</script>',
             f'<script type="application/ld+json">{json_ld()}</script>', s)

    # 4. содержимое
    msg = re.search(r'<div class="cta-contacts"[^>]*>\s*<a class="ph"[^>]*>[^<]*</a>\s*(<div class="msg">.*?</div>)\s*</div>',
                    s, re.S).group(1)
    main = (HERE / 'main.html').read_text(encoding='utf-8')
    strip = '\n'.join(f'      <div class="strip-item">{icons[i]}<b>{b}</b> {t}</div>' for i, b, t in STRIP)
    main = main.replace('{{strip}}', strip).replace('{{faq}}', faq_section())
    main = main.replace('{{zones}}', (HERE / 'zones.svg').read_text(encoding='utf-8').strip())
    main = re.sub(r'\{\{i:([a-z0-9-]+)\}\}', lambda mm: icons[mm.group(1)], main)
    main = main.replace('{{arr}}', ARR).replace('{{arr0}}', ARR0).replace('{{a16}}', A16).replace('{{msg}}', msg)
    assert '{{' not in main, 'остались метки в main.html'
    main = typo(main)
    s = sub1(r'<main id="main"[^>]*>.*?</main>', main.strip(), s)

    # 5. скрипт страницы вместо скрипта складов
    s = sub1(r'<script>\n/\* Предпросмотр: вне рабочего домена.*?</script>', '<script>\n' + js + '\n</script>', s)

    # 6. меню: шапка, мобильное меню и подвал с отметкой текущей страницы
    s = apply_menu.apply_page(s, '../', SLUG)

    for bad in ('sklad-hero', 'sklady-og', 'sklad-rampa', 'Склады и логистика (/', 'wtype'):
        assert bad not in s, 'от шаблона осталось: ' + bad
    assert s.count('<h1') == 1 and s.count('application/ld+json') == 1
    return s


def main():
    a = sys.argv[1:]
    tpl = pathlib.Path(a[a.index('--template') + 1]) if '--template' in a else ROOT / TPL_SLUG / 'index.html'
    out = pathlib.Path(a[a.index('--out') + 1]) if '--out' in a else ROOT / SLUG / 'index.html'
    html = build(tpl.read_text(encoding='utf-8'))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print('ok', out, len(html.encode('utf-8')) // 1024, 'КБ')


if __name__ == '__main__':
    main()
