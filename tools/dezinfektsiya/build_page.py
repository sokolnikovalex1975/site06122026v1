#!/usr/bin/env python3
"""Страница «Дезинфекция для организаций» (/dezinfektsiya/) — зонтичная страница всех санитарных услуг.

Оболочка (head, шапка, меню, подвал, плавающие кнопки, подключение скриптов) берётся из готовой страницы
дезинсекции — так у новой страницы те же стили, меню, телефон и форма, что и у остальных.
Заменяются: мета-теги, предзагрузка фото первого экрана, структурированные данные, стили страницы,
содержимое <main> (tools/dezinfektsiya/main.html) и скрипт страницы (tools/dezinfektsiya/page.js).

Бегущую строку, «Смотрите также», атрибуты анимаций и меню добавляют общие скрипты сайта
(tools/site/unify.py и tools/menu/apply_menu.py) — скрипт запускается из tools/site/build_site.py.

Запуск из корня репозитория: python3 tools/dezinfektsiya/build_page.py
"""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
from typo import typo  # noqa: E402  неразрывные пробелы, как в остальных текстах сайта

SLUG = 'dezinfektsiya'
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
URL = SITE + SLUG + '/'
TITLE = 'Дезинфекция для организаций в Москве и области — ПЕСТКОНТРОЛЬ Центр'
DESC = ('Дезинфекция помещений для организаций в Москве и МО: профилактическая и заключительная, вентиляция, '
        'СЭС-аудит, дезинсекция, дератизация и IPM. Акты и журнал.')
OG_TITLE = 'Дезинфекция для организаций в Москве и области'
OG_ALT = 'Дезинфектор ПЕСТКОНТРОЛЬ Центр обрабатывает холодным туманом пустой цех пищевого производства'
MODIFIED = '2026-11-06'

ICONS = json.loads((ROOT / 'tools' / 'site' / 'icons.json').read_text(encoding='utf-8'))
_SVG = ('<svg aria-hidden="true" focusable="false" class="lucide lucide-{n}" xmlns="http://www.w3.org/2000/svg" '
        'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
        'stroke-linejoin="round" > {p} </svg>')
ICONS.update({  # иконки Lucide, которых нет в icons.json
    'lucide-building': _SVG.format(n='building-2', p=(
        '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z" /> <path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2" /> '
        '<path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2" /> <path d="M10 6h4" /> <path d="M10 10h4" /> '
        '<path d="M10 14h4" /> <path d="M10 18h4" />')),
    'lucide-wind': _SVG.format(n='wind', p=(
        '<path d="M12.8 19.6A2 2 0 1 0 14 16H2" /> <path d="M17.5 8a2.5 2.5 0 1 1 2 4H2" /> '
        '<path d="M9.8 4.4A2 2 0 1 1 11 8H2" />')),
    'lucide-bug': _SVG.format(n='bug', p=(
        '<path d="m8 2 1.88 1.88" /> <path d="M14.12 3.88 16 2" /> <path d="M9 7.13v-1a3.003 3.003 0 1 1 6 0v1" /> '
        '<path d="M12 20c-3.3 0-6-2.7-6-6v-3a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v3c0 3.3-2.7 6-6 6" /> <path d="M12 20v-9" /> '
        '<path d="M6.53 9C4.6 8.8 3 7.1 3 5" /> <path d="M6 13H2" /> <path d="M3 21c0-2.1 1.7-3.9 3.8-4" /> '
        '<path d="M20.97 5c0 2.1-1.6 3.8-3.5 4" /> <path d="M22 13h-4" /> <path d="M17.2 17c2.1.1 3.8 1.9 3.8 4" />')),
})

SANPIN = 'http://pravo.gov.ru/proxy/ips/?docbody=&amp;nd=602107773&amp;rdk=0'
CNTD = 'https://docs.cntd.ru/document/573660140/titles/6FESEN'
SP = 'http://publication.pravo.gov.ru/document/0001202606020088'
SP_TRADE = 'https://base.garant.ru/414329165/53f89421bbdaf741eb2d1ecc4ddb4c33/'
MR353 = 'https://www.garant.ru/products/ipo/prime/doc/410334925/'
LICPOS = 'https://39.rospotrebnadzor.ru/content/ob-utverzhdenii-polozheniya-o-licenzirovanii-deyatelnosti-po-okazaniyu-uslug-po-dezinfekcii'
LIC = 'https://fp.rospotrebnadzor.ru/licen/?oper=search&amp;numb_history=&amp;numb=&amp;firmget_name=&amp;ogrn_inn_nza=7714462211'
NEW6 = 'https://www.41.rospotrebnadzor.ru/content/s-1-sentyabrya-2026-goda-vstupayut-v-silu-shest-novyh-sanitarnyh-pravil'


def a(href, text):
    return f'<a href="{href}" target="_blank" rel="noopener noreferrer">{text}</a>'


# Вопросы: (вопрос, ответ в HTML). В разметку FAQPage идёт тот же текст без тегов.
FAQ = [
    ('Что такое дезинфекция простыми словами?',
     'Это уничтожение или удаление возбудителей инфекций — бактерий, вирусов, грибов и их спор — на поверхностях, '
     'оборудовании, в воздухе и вентиляции. Цель — прервать путь, по которому инфекция переходит от источника '
     f'к человеку (п. 40 {a(SANPIN, "СанПиН 3.3686-21")}).'),
    ('Чем дезинфекция отличается от дезинсекции и дератизации?',
     'Дезинфекция направлена на микроорганизмы, дезинсекция — на насекомых и других членистоногих, дератизация — '
     'на грызунов. В санитарных правилах все три вида работ объединены понятием «дезинфекционная деятельность» '
     f'({a(CNTD, "пп. 79–80 СанПиН 3.3686-21")}), а лицензия Роспотребнадзора выдаётся сразу на все три.'),
    ('Какие виды дезинфекции бывают?',
     'Профилактическая — постоянно, когда заболевших нет. Очаговая — при выявлении инфекции: текущая, пока заболевший '
     'находится на месте, и заключительная — после его изоляции, госпитализации или выздоровления, в том числе '
     'по месту работы (пп. 41, 80 СанПиН 3.3686-21). Отдельно проводят внеплановую дезинфекцию после аварий '
     'и по замечаниям производственного контроля.'),
    ('Как часто организации нужно проводить дезинфекцию?',
     'Кратность задаёт программа производственного контроля с учётом правил для вашего типа объекта. Например, '
     f'в торговле — уборка всех помещений с дезсредствами 1 раз в месяц (п. 75 {a(SP_TRADE, "СП 2.3.6.4281-26")}), '
     f'в гостиницах — дезинфекция заселённых номеров ежедневно и после каждого выезда (п. 84 {a(SP, "СП 2.1.4284-26")}), '
     'централизованная вентиляция — не реже 1 раза в год (п. 132 СанПиН 3.3686-21).'),
    ('Нужна ли подрядчику лицензия на дезинфекцию?',
     'Да. С 1 марта 2025 года услуги по дезинфекции, дезинсекции и дератизации без лицензии Роспотребнадзора '
     f'оказывать нельзя ({a(LICPOS, "постановление Правительства РФ от 20.03.2024 № 337")}). Лицензия не нужна, '
     'если организация проводит работы своими силами для собственных нужд. У ООО «Центр дезинфекционных услуг» '
     f'действующая лицензия № Л064-00111-77/01942445, её можно проверить в {a(LIC, "реестре Роспотребнадзора")}.'),
    ('Можно ли проводить дезинфекцию своими силами?',
     'Ежедневную уборку с дезсредствами ваш персонал проводит сам — для многих объектов этого прямо требуют '
     'санитарные правила. Для собственных нужд лицензия не нужна. Но полноценные дезинфекционные работы, по п. 89 '
     'СанПиН 3.3686-21, проводит персонал организаций, у которых дезинфекционная деятельность указана '
     'в учредительных документах, а заключительную дезинфекцию при ряде инфекций — только специализированные '
     'организации.'),
    ('Нужно ли останавливать работу на время дезинфекции?',
     'Обычно нет. Работы планируем на ночь, выходные или санитарный день. Если инструкция к средству требует '
     'отсутствия людей, заранее сообщаем время выдержки и проветривания. Ночные и выходные окна — без наценки.'),
    ('Какие документы выдаются после дезинфекции?',
     'Акт выполненных работ с зонами, площадью, средством, концентрацией, способом и экспозицией; запись в журнале '
     'объекта; копии разрешительных документов и инструкций на средства; копия лицензии. При заказе лабораторного '
     'контроля — протоколы аккредитованной лаборатории.'),
    ('Что делать, если у сотрудника выявили инфекцию?',
     'Выполнить предписания Роспотребнадзора и организовать заключительную дезинфекцию помещений, где работал '
     'заболевший, после его изоляции или госпитализации (п. 41 СанПиН 3.3686-21). На пищевом производстве это '
     f'и основание для внеплановой санитарной обработки (п. 3.1 {a(MR353, "МР 3.5.0353-24")}). Выезжаем в течение '
     '3 часов и подбираем режим под возбудитель.'),
    ('Как часто дезинфицировать вентиляцию и кондиционеры?',
     'Централизованные системы вентиляции и кондиционирования — не реже 1 раза в год. Централизованные системы '
     'кондиционирования и увлажнения в офисах, гостиницах, торговле, на производстве и транспорте исследуют '
     'на легионеллы не реже 2 раз в год, кроме сплит-систем и установок малой мощности без увлажнения (п. 132 '
     'СанПиН 3.3686-21). Подробнее — на странице <a href="../ochistka-dezinfektsiya-ventilyatsii/">об очистке '
     'и дезинфекции вентиляции</a>.'),
    ('Какие санитарные правила изменились с 1 сентября 2026 года?',
     'Вступили в силу шесть новых правил: СП 2.1.4284-26 (вместо СП 2.1.3678-20), СП 2.3.6.4281-26 (вместо '
     'СП 2.3.6.3668-20), СанПиН 2.3/2.4.4282-26 (вместо СанПиН 2.3/2.4.3590-20), а также СП 2.2.4285-26, '
     f'СП 2.4.2.4283-26 и СП 2.5.4286-26 ({a(NEW6, "сообщение Роспотребнадзора")}). Требования к дезинфекционной '
     'деятельности по-прежнему в СанПиН 3.3686-21.'),
    ('Сколько стоит дезинфекция для организаций?',
     'Ориентиры: дезинфекция помещений — от 9 ₽ за м², дезинфекция воздуховодов — от 45 ₽ за погонный метр, '
     'санитарный аудит — от 9 000 ₽, комплексное обслуживание по договору — от 3 500 ₽ в месяц. Осмотр и расчёт '
     'бесплатны, точную стоимость фиксируем в договоре.'),
]

# услуги для OfferCatalog: (название, адрес относительно корня сайта)
CATALOG = [
    ('Профилактическая дезинфекция', SLUG + '/#vidy'),
    ('Заключительная дезинфекция', SLUG + '/#zaklyuchitelnaya'),
    ('Очистка и дезинфекция вентиляции', 'ochistka-dezinfektsiya-ventilyatsii/'),
    ('Дезинсекция для организаций', 'dezinsektsiya/'),
    ('Дератизация для организаций', 'deratizatsiya/'),
    ('Санитарный аудит (СЭС-аудит)', 'sanitarnyy-audit/'),
    ('Пест-контроль по системе IPM', '#podhod'),
    ('Договор на обслуживание', 'dogovor-deratizatsiya-dezinsektsiya/'),
]


def plain(h):
    return html.unescape(re.sub(r'<[^>]+>', '', h)).replace('\xa0', ' ')


def faq_items(lo, hi):
    out = []
    for i in range(lo, hi + 1):
        q, ans = FAQ[i]
        n = i + 1
        first = i == 0
        out.append(
            f'        <div class="card qa{" open" if first else ""}"><button aria-expanded="{"true" if first else "false"}" '
            f'aria-controls="a{n}" id="q{n}">{q}<span class="pm"></span></button><div class="ans" id="a{n}" role="region" '
            f'aria-labelledby="q{n}"{" style=\"height:auto\"" if first else ""}><div><p>{ans}</p></div></div></div>')
    return '\n'.join(out)


def provider_from(shell):
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', shell, re.S):
        d = json.loads(m.group(1))
        for g in d.get('@graph', [d]):
            if g.get('@type') == 'Service' and 'provider' in g:
                return g['provider']
    raise SystemExit('в оболочке нет Service.provider')


def ld_json(provider):
    graph = [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': 'Дезинфекция для организаций', 'item': URL}]},
        {'@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE, 'description': DESC,
         'inLanguage': 'ru', 'dateModified': MODIFIED, 'about': {'@id': URL + '#service'},
         'publisher': {'@type': 'Organization', 'name': provider.get('name', 'ПЕСТКОНТРОЛЬ Центр')}},
        {'@type': 'Service', '@id': URL + '#service', 'name': 'Дезинфекция для организаций',
         'serviceType': 'Дезинфекция помещений, оборудования и воздуха; комплекс дезинфекционных услуг', 'url': URL,
         'description': ('Профилактическая и заключительная дезинфекция помещений, оборудования и воздуха для '
                         'организаций в Москве и Московской области по СанПиН 3.3686-21, а также весь комплекс '
                         'дезинфекционных услуг: дезинсекция, дератизация, очистка и дезинфекция вентиляции, '
                         'санитарный аудит и пест-контроль по системе IPM.'),
         'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
         'audience': {'@type': 'BusinessAudience', 'name': 'Юридические лица и ИП'},
         'provider': provider,
         'hasOfferCatalog': {'@type': 'OfferCatalog', 'name': 'Дезинфекционные услуги для организаций',
                             'itemListElement': [{'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': n, 'url': SITE + u}}
                                                 for n, u in CATALOG]},
         'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'RUB', 'lowPrice': '9',
                    'description': 'Ориентиры: дезинфекция помещений от 9 ₽ за м², дезинфекция воздуховодов от 45 ₽ '
                                   'за м. п., санитарный аудит от 9 000 ₽, обслуживание по договору от 3 500 ₽ в месяц; '
                                   'осмотр и расчёт — 0 ₽'}},
        {'@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(ans)}} for q, ans in FAQ]},
    ]
    return ('<script type="application/ld+json">'
            + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False) + '</script>')


def sub1(pat, rep, s, flags=re.S):
    out, n = re.subn(pat, lambda m: rep, s, count=1, flags=flags)
    assert n == 1, pat
    return out


def main():
    shell = (ROOT / 'dezinsektsiya' / 'index.html').read_text(encoding='utf-8')
    s = shell
    # --- head
    s = sub1(r'<title>.*?</title>', f'<title>{TITLE}</title>', s)
    s = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s)
    s = sub1(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">', s)
    s = sub1(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">', s)
    s = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_TITLE}">', s)
    s = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{DESC}">', s)
    s = sub1(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{SITE}img/dezinf-og.jpg">', s)
    s = sub1(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{OG_ALT}">', s)
    s = s.replace('../img/dez-hero-1440.webp 1440w, ../img/dez-hero.webp 1920w', '../img/dezinf-hero-1440.webp 1440w, ../img/dezinf-hero.webp 1920w')
    s = s.replace('../img/dez-hero-mob-760.webp 760w, ../img/dez-hero-mob.webp 1024w', '../img/dezinf-hero-mob-760.webp 760w, ../img/dezinf-hero-mob.webp 1024w')
    s = sub1(r'<script type="application/ld\+json">.*?</script>', ld_json(provider_from(shell)), s)
    # стили: общие блоки страниц услуг (как у дезинсекции) + блоки этой страницы
    extra = (HERE / 'extra.css').read_text(encoding='utf-8')
    extra = re.sub(r'/\*.*?\*/', '', extra, flags=re.S)
    extra = re.sub(r'\s*\n\s*', '', extra)
    m = re.search(r'<style>(.*?)</style>', s, re.S)
    s = s[:m.end(1)] + '\n' + extra + '\n' + s[m.end(1):]
    # --- main
    main = (HERE / 'main.html').read_text(encoding='utf-8')
    main = main.replace('{{faq:0-5}}', faq_items(0, 5)).replace('{{faq:6-11}}', faq_items(6, 11))
    main = re.sub(r'\{\{ico:([a-z0-9-]+)\}\}', lambda mm: ICONS[mm.group(1)], main)
    assert '{{' not in main, 'остались заготовки в main.html'
    # телефон оставляем в том же виде, что и на других страницах (подмена номера колл-трекинга UIS)
    main = main.replace('+7 (495) 104-35-70', '\u2063PHONE\u2063')
    main = typo(main).replace('\u2063PHONE\u2063', '+7 (495) 104-35-70')
    # шифры документов (вместе с «СП», «СанПиН», «МР», «Р») и номер лицензии не разрываем переносом: «СП 2.1.4284-26», «Л064-00111-77/01942445»
    code = re.compile(r'(?<![\w.])((?:(?:СанПиН|СП|МР|Р)[ \xa0])?(?:\d+(?:\.\d+)+(?:/\d+(?:\.\d+)+)?-\d{2})|Л064-00111-77/01942445|[Пп]ест-контрол\w*)(?![\w-])')
    parts = re.split(r'(<[^>]+>)', main)
    main = ''.join(p if p.startswith('<') else code.sub(r'<span class="nw">\1</span>', p) for p in parts)
    s = sub1(r'<main id="main" tabindex="-1">.*?</main>', main.strip(), s)
    # --- скрипт страницы (предпросмотр, фон блока заявки, форма)
    js = (HERE / 'page.js').read_text(encoding='utf-8').strip()
    s = sub1(r'<script>\n/\* Предпросмотр: вне рабочего домена.*?</script>', '<script>\n' + js + '\n</script>', s)
    # меню и подвал перестроит apply_menu.py (текущая страница — эта)
    out = ROOT / SLUG / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(s, encoding='utf-8')
    print('ok', out.relative_to(ROOT), len(s), 'байт')


if __name__ == '__main__':
    main()
