#!/usr/bin/env python3
"""Страница «Дезинфекция автотранспорта» (/dezinfektsiya/avtotransport/), 20.11.2026.

Запрос владельца 20.11.2026: «Нужно сделать страницу дезинфекции автотранспорта» и «Сразу делай контент-страницу
с учётом SEO-оптимизации, с учётом поисковых запросов. Подбери сразу фразы через KEYSO». Ответы владельца на чек-лист:
цена — от 900 ₽ за машину; кузов моет клиент; бланк журнала на машину — бесплатно и наклейка в кабину с датой
следующей обработки; ночью и в выходные без наценки, срочный выезд за 3 часа; время — «просто напиши 15 минут»
(без деления по типам кузова); удаление запаха — отдельной услугой; образец акта PDF — сразу; меню и ссылки — в том же
пакете. Тексты — «Страница Дезинфекция автотранспорта/Тексты страницы v0.md» в файлах проекта с этими решениями.
Ключевые фразы — Keys.so, база «Яндекс, Москва» (H1, Title, подзаголовки H2 и вопросы FAQ).

Оболочка (head, шапка, меню, подвал, нижняя панель, скрипты) — готовая страница дезинсекции, как у
tools/dezinfektsiya/build_page.py; страница на втором уровне, поэтому пути оболочки '../' → '../../' (deeper()).
Заменяются: мета-теги, предзагрузка фото первого экрана, JSON-LD, стили страницы (extra.css), <main> (main.html,
корень сайта — метка '@/') и скрипт страницы (page.js). Бегущую строку, «Смотрите также», анимации, меню, блок
«Все услуги», самопроверку с формой и счётчики добавляют общие шаги tools/site/build_site.py.

Форма: send.php принимает только name, company, phone, email, type и msg. У всех пунктов «Тип транспорта» значение
«Другое» (есть в списке send.php), подпись пункта, число машин, задача, адрес и страница уходят в msg (page.js).

Запуск из корня репозитория: python3 tools/avtotransport/build_page.py (build_site.py запускает его сам).
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

SLUG = 'dezinfektsiya/avtotransport'
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
URL = SITE + SLUG + '/'
TITLE = 'Дезинфекция автотранспорта и санобработка кузова в Москве — от 900 ₽'
DESC = ('Дезинфекция грузового транспорта, автобусов и такси в Москве и МО: санобработка кузова рефрижератора '
        'за 15 минут, акт на каждую машину. От 900 ₽.')
OG_TITLE = 'Дезинфекция автотранспорта для перевозчиков и автопарков'
OG_DESC = ('Фургоны, рефрижераторы, фуры, автобусы, такси: 15 минут на машину, ночью и в выходные без наценки, '
           'акт с госномером. Что заменило санпаспорт и как часто нужна обработка.')
HERO_ALT = ('Специалист в комбинезоне, полумаске и перчатках обрабатывает дезинфицирующим раствором стенку кузова '
            'рефрижератора с открытыми задними дверями')
MODIFIED = '2026-11-20'
PDF_SAMPLE = 'obrazets-akta-dezinfektsii-avtotransporta.pdf'  # tools/avtotransport/build_akt.py
PDF_BLANK = 'blank-akta-dezinfektsii-avtotransporta.pdf'

L = {  # официальные тексты норм и реестр лицензий
    'trts021': 'https://www.consultant.ru/document/cons_doc_LAW_124768/5b4fff74f40802408d8d577ce4926f8f91c42c41/',
    'trts034': 'https://docs.cntd.ru/document/499050564/titles/8P40LT',
    'sanpin3686': 'http://pravo.gov.ru/proxy/ips/?docbody=&amp;nd=602107773&amp;rdk=0',
    'sanpin3684': 'http://pravo.gov.ru/proxy/ips/?docbody=&amp;nd=602024221',
    'sp4281': 'https://www.consultant.ru/document/cons_doc_LAW_535840/82653e94116167666a396abd1a10b355543195ea/',
    'sp1066': ('https://www.kontur-extern.ru/info/normativ/document/9/'
               '109093-postanovlenie-glavnogo-gosudarstvennogo-sanitarnogo-vracha-rf-ot-07-09-2001-n-23'),
    'mr0372': 'https://base.garant.ru/411918432/',
    'mr0354': 'https://www.consultant.ru/document/cons_doc_LAW_487757/4cc2da5d98dbf0805255325a729188519f781168/',
    'pasport': 'https://www.consultant.ru/law/podborki/sanitarnyj_pasport_na_transport/',
    'pp337': ('https://39.rospotrebnadzor.ru/content/'
              'ob-utverzhdenii-polozheniya-o-licenzirovanii-deyatelnosti-po-okazaniyu-uslug-po-dezinfekcii'),
    'lic': ('https://fp.rospotrebnadzor.ru/licen/?oper=search&amp;numb_history=&amp;numb=&amp;firmget_name=&amp;'
            'ogrn_inn_nza=7714462211'),
}

ICONS = json.loads((ROOT / 'tools' / 'site' / 'icons.json').read_text(encoding='utf-8'))
_SVG = ('<svg aria-hidden="true" focusable="false" class="lucide lucide-{n}" xmlns="http://www.w3.org/2000/svg" '
        'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
        'stroke-linejoin="round" > {p} </svg>')
ICONS.update({  # иконки Lucide, которых нет в icons.json
    'avt-truck': _SVG.format(n='truck', p=(
        '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2" /> <path d="M15 18H9" /> '
        '<path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14" /> '
        '<circle cx="17" cy="18" r="2" /> <circle cx="7" cy="18" r="2" />')),
    'avt-snow': _SVG.format(n='snowflake', p=(
        '<line x1="2" x2="22" y1="12" y2="12" /> <line x1="12" x2="12" y1="2" y2="22" /> <path d="m20 16-4-4 4-4" /> '
        '<path d="m4 8 4 4-4 4" /> <path d="m16 4-4 4-4-4" /> <path d="m8 20 4-4 4 4" />')),
    'avt-container': _SVG.format(n='container', p=(
        '<path d="M22 7.7c0-.6-.4-1.2-.8-1.5l-6.3-3.9a1.72 1.72 0 0 0-1.7 0l-10.3 6c-.5.2-.9.8-.9 1.4v6.6c0 .5.4 1.2.8 '
        '1.5l6.3 3.9a1.72 1.72 0 0 0 1.7 0l10.3-6c.5-.3.9-1 .9-1.5Z" /> <path d="M10 21.9V14L2.1 9.1" /> '
        '<path d="m10 14 11.9-6.9" /> <path d="M14 19.8v-8.1" /> <path d="M18 17.5V9.4" />')),
    'avt-beef': _SVG.format(n='beef', p=(
        '<circle cx="12.5" cy="8.5" r="2.5" /> <path d="M12.5 2a6.5 6.5 0 0 0-6.22 4.6c-1.1 3.13-.78 3.9-3.18 6.08A3 3 0 '
        '0 0 5 18c4 0 8.4-1.8 11.4-4.3A6.5 6.5 0 0 0 12.5 2Z" /> <path d="m18.5 6 2.19 4.5a6.48 6.48 0 0 1 .31 2 6.49 '
        '6.49 0 0 1-2.6 5.2C15.4 20.2 11 22 7 22a3 3 0 0 1-2.68-1.66L2.4 16.5" />')),
    'avt-bus': _SVG.format(n='bus', p=(
        '<path d="M8 6v6" /> <path d="M15 6v6" /> <path d="M2 12h19.6" /> <path d="M18 18h3s.5-1.7.8-2.8c.1-.4.2-.8.2-1.2 '
        '0-.4-.1-.8-.2-1.2l-1.4-5C20.1 6.8 19.1 6 18 6H4a2 2 0 0 0-2 2v10h3" /> <circle cx="7" cy="18" r="2" /> '
        '<path d="M9 18h5" /> <circle cx="16" cy="18" r="2" />')),
    'avt-taxi': _SVG.format(n='car-taxi-front', p=(
        '<path d="M10 2h4" /> <path d="m21 8-2 2-1.5-3.7A2 2 0 0 0 15.646 5H8.4a2 2 0 0 0-1.903 1.257L5 10 3 8" /> '
        '<path d="M7 14h.01" /> <path d="M17 14h.01" /> <rect width="18" height="8" x="3" y="10" rx="2" /> '
        '<path d="M5 18v2" /> <path d="M19 18v2" />')),
    'avt-trash': _SVG.format(n='trash-2', p=(
        '<path d="M3 6h18" /> <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" /> <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" /> '
        '<line x1="10" x2="10" y1="11" y2="17" /> <line x1="14" x2="14" y1="11" y2="17" />')),
    'avt-bio': _SVG.format(n='biohazard', p=(
        '<circle cx="12" cy="11.9" r="2" /> <path d="M6.7 3.4c-.9 2.5 0 5.2 2.2 6.7C6.5 9 3.7 9.6 2 11.6" /> '
        '<path d="m8.9 10.1 1.4.8" /> <path d="M17.3 3.4c.9 2.5 0 5.2-2.2 6.7 2.4-1.2 5.2-.6 6.9 1.5" /> '
        '<path d="m15.1 10.1-1.4.8" /> <path d="M16.7 20.8c-2.6-.4-4.6-2.6-4.7-5.3-.2 2.6-2.1 4.8-4.7 5.2" /> '
        '<path d="M12 13.9v1.6" /> <path d="M13.5 5.4c-1-.2-2-.2-3 0" /> <path d="M17 16.4c.7-.7 1.2-1.6 1.5-2.5" /> '
        '<path d="M5.5 13.9c.3.9.8 1.8 1.5 2.5" />')),
    'avt-sticker': _SVG.format(n='sticker', p=(
        '<path d="M15.5 3H5a2 2 0 0 0-2 2v14c0 1.1.9 2 2 2h14a2 2 0 0 0 2-2V8.5L15.5 3Z" /> <path d="M14 3v4a2 2 0 0 0 2 2h4" /> '
        '<path d="M8 13h.01" /> <path d="M16 13h.01" /> <path d="M10 16s.8 1 2 1c1.3 0 2-1 2-1" />')),
})


def a(key, text):
    return f'<a href="{L[key]}" target="_blank" rel="noopener noreferrer">{text}</a>'


# Вопросы: (вопрос, ответ в HTML). В разметку FAQPage идёт тот же текст без тегов. Формулировки вопросов —
# по запросам Keys.so («нужен ли санитарный паспорт на машину для перевозки продуктов», «должны ли грузовые отделения
# транспортных средств и контейнеры подвергаться регулярной очистке», «сколько действует санобработка грузового
# транспорта», «какой должна быть конструкция грузовых отделений», «какие медицинские документы должен иметь экспедитор»).
FAQ = [
    ('Нужен ли санитарный паспорт на машину для перевозки продуктов?',
     'Нет. Требование отменено с 21 октября 2011 года Федеральным законом от 19.07.2011 № 248-ФЗ, Роспотребнадзор '
     f'подтвердил это письмом от 31.10.2011 № 01/13750-1-32 ({a("pasport", "подборка КонсультантПлюс")}). '
     'Санобработку машины подтверждают договор с исполнителем и акт на каждую обработку.'),
    ('Должны ли грузовые отделения транспортных средств и контейнеры подвергаться регулярной очистке, мойке, дезинфекции?',
     'Да. Это прямое требование технического регламента: регулярно и с такой периодичностью, чтобы кузов и контейнеры '
     'не стали источником загрязнения продукции. Внутренние поверхности моют водой, которая соответствует требованиям '
     f'к питьевой ({a("trts021", "ТР ТС 021/2011, ст. 17, п. 6")}).'),
    ('Как часто проводится санитарная обработка транспорта для перевозки пищевых продуктов?',
     f'Для мяса — после каждой перевозки ({a("trts034", "ТР ТС 034/2013, п. 101")}). Для остальной продукции частоту '
     'устанавливает перевозчик в программе производственного контроля. Ориентир из методических рекомендаций '
     f'Роспотребнадзора — мойка ежедневно, дезинфекция ежемесячно ({a("mr0372", "МР 3.5.0372-25, п. 10.3")}).'),
    ('Сколько действует санобработка грузового транспорта?',
     'Срока действия у акта санитарной обработки автомобиля нет: он подтверждает, что машину обработали в конкретный день. Актуальность определяет '
     'ваш график — при ежемесячной дезинфекции нужен акт текущего месяца, для мяса — акт после каждой перевозки. '
     'Дату следующей обработки пишем в акте и на наклейке в кабине.'),
    ('Какой должна быть конструкция грузовых отделений транспортных средств и контейнеров?',
     'Такой, чтобы защищать продукцию от загрязнения, грызунов и насекомых и позволять очистку, мойку и дезинфекцию; '
     f'внутренняя поверхность — из моющихся и нетоксичных материалов ({a("trts021", "ТР ТС 021/2011, ст. 17, пп. 3, 5")}). '
     'Надорванный уплотнитель, щели в обшивке и забитые трапы отмечаем в акте как замечание.'),
    ('Какие средства применяются для дезинфекции автотранспорта?',
     'Только зарегистрированные средства III–IV класса опасности по инструкции к ним '
     f'({a("sanpin3686", "СанПиН 3.3686-21, п. 131")}), разрешённые для транспорта и поверхностей, которые контактируют '
     'с пищевой продукцией. При плесени — средство с фунгицидным действием. Название, номер госрегистрации '
     'и концентрацию указываем в акте.'),
    ('Нужна ли лицензия на дезинфекцию автотранспорта?',
     'Да. Начиная с 01.03.2025 дезинфекцию для заказчиков выполняют только по лицензии Роспотребнадзора '
     f'({a("pp337", "постановление Правительства РФ от 20.03.2024 № 337")}). '
     f'Наша лицензия — № Л064-00111-77/01942445, запись о ней есть в {a("lic", "реестре Роспотребнадзора")}.'),
    ('Сколько длится обработка и когда можно загружать машину?',
     '15 минут работы на машину. Затем выдержка по инструкции средства, смыв, если инструкция его требует, '
     'и проветривание. Время до загрузки называем заранее, чтобы рейс не сдвинулся.'),
    ('Можно ли дезинфицировать рефрижератор при минусовой температуре?',
     'Промёрзший кузов без отогрева не обрабатываем: на стене ниже нуля раствор замерзает и не действует. Установку '
     'выключают заранее, наледь убирают, кузов прогревается до плюсовой температуры — затем мойка и дезинфекция. '
     'Средство с режимом для минусовых температур применяем, только если такой режим записан в его зарегистрированной '
     'инструкции.'),
    ('Как убрать запах из кузова после рыбы и мяса?',
     'Найти и убрать источник: остатки продукции в стыках, трапах и уплотнителях. Затем мойка, дезинфекция и обработка '
     'средством от запахов с проветриванием. Если запах впитался в уплотнитель или пол, без замены детали он вернётся. '
     'Удаление запаха — отдельная услуга, цена по расчёту.'),
    ('Какие медицинские документы должен иметь экспедитор при перевозке пищевых продуктов?',
     'Личную медицинскую книжку с отметками о предварительном и периодических медосмотрах: их проходят все, кто '
     'контактирует с продукцией при перевозке, включая водителя-экспедитора и грузчиков '
     f'({a("trts021", "ТР ТС 021/2011, ст. 17, п. 10")}). Нужна и санитарная одежда. Санитарной книжки у самой машины '
     'законодательство не предусматривает.'),
    ('Есть ли особые условия для мусоровозов и транспорта медицинских отходов?',
     'Да. Мусоровозы и ассенизационные машины моют с дезинфекцией не реже 1 раза в 10 суток '
     f'({a("sanpin3684", "СанПиН 2.1.3684-21, пп. 16, 26")}). Транспорт медицинских отходов — только '
     'специализированный: для класса А мытьё, дезинфекция и дезинсекция не реже 1 раза в неделю, для классов Б и В — '
     'после каждой перевозки (пп. 203, 204, 207). Такие машины обрабатываем по запросу.'),
]


def plain(h):
    return html.unescape(re.sub(r'<[^>]+>', '', h)).replace('\xa0', ' ')


def faq_items(lo, hi):
    out = []
    for i in range(lo, hi + 1):
        q, ans = FAQ[i]
        n = i + 1
        first = i == 0  # развёрнут только первый вопрос (решение владельца 13.11.2026, tools/site/faq_first.py)
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


AUTHOR = {'@type': 'Person', 'name': 'Марианна Семерина', 'jobTitle': 'Санитарный врач'}


def ld_json(provider):
    docs = [
        {'@type': 'DigitalDocument', '@id': URL + '#akt-obrazets', 'name': 'Образец акта дезинфекции автотранспорта',
         'url': URL + PDF_SAMPLE, 'encodingFormat': 'application/pdf', 'inLanguage': 'ru'},
        {'@type': 'DigitalDocument', '@id': URL + '#akt-blank', 'name': 'Бланк акта санобработки транспортного средства',
         'url': URL + PDF_BLANK, 'encodingFormat': 'application/pdf', 'inLanguage': 'ru'},
    ]
    graph = [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': 'Дезинфекция для организаций', 'item': SITE + 'dezinfektsiya/'},
            {'@type': 'ListItem', 'position': 3, 'name': 'Дезинфекция автотранспорта', 'item': URL}]},
        {'@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE, 'description': DESC,
         'inLanguage': 'ru', 'dateModified': MODIFIED, 'about': {'@id': URL + '#service'}, 'author': AUTHOR,
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': SITE + 'img/avto-hero.webp', 'caption': HERO_ALT},
         'hasPart': [{'@id': d['@id']} for d in docs],
         'publisher': {'@type': 'Organization', 'name': provider.get('name', 'ПЕСТКОНТРОЛЬ Центр')}},
        {'@type': 'Service', '@id': URL + '#service', 'name': 'Дезинфекция автотранспорта',
         'serviceType': 'Дезинфекция и санитарная обработка транспортных средств', 'url': URL,
         'description': ('Дезинфекция кузовов фургонов, изотерм и рефрижераторов, фур и полуприцепов, салонов автобусов, '
                         'такси и каршеринга на стоянке заказчика в Москве и Московской области: 15 минут на машину, '
                         'акт с госномером, журнал и наклейка в кабину. Мусоровозы и транспорт медицинских отходов — '
                         'по запросу.'),
         'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
         'audience': {'@type': 'BusinessAudience', 'name': 'Юридические лица и ИП'},
         'provider': provider,
         'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'RUB', 'lowPrice': '900',
                    'description': ('Дезинфекция автотранспорта от 900 ₽ за машину; расчёт по списку машин — 0 ₽; '
                                    'удаление запаха — по расчёту; '
                                    'ночные и выходные окна без наценки')}},
        *docs,
        {'@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(ans)}} for q, ans in FAQ]},
    ]
    return ('<script type="application/ld+json">'
            + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False) + '</script>')


def sub1(pat, rep, s, flags=re.S):
    out, n = re.subn(pat, lambda m: rep, s, count=1, flags=flags)
    assert n == 1, pat
    return out


def deeper(s):
    """Относительные пути оболочки ('../') для страницы на уровень глубже (как в tools/restorany-uslugi)."""
    return re.sub(r'(?<=["\'(,\s])\.\./', '../../', s)


def build_main():
    main = (HERE / 'main.html').read_text(encoding='utf-8')
    main = main.replace('{{faq:0-6}}', faq_items(0, 6)).replace('{{faq:7-11}}', faq_items(7, 11))
    main = re.sub(r'\{\{a:([a-z0-9]+)\|([^}]+)\}\}', lambda m: a(m.group(1), m.group(2)), main)
    main = re.sub(r'\{\{ico:([a-z0-9-]+)\}\}', lambda m: ICONS[m.group(1)], main)
    assert '{{' not in main, 'остались заготовки в main.html'
    # телефон и почта — в том же виде, что и на других страницах (подмена номера колл-трекинга UIS)
    main = main.replace('+7 (495) 104-35-70', '\u2063PHONE\u2063')
    main = typo(main).replace('\u2063PHONE\u2063', '+7 (495) 104-35-70')
    # шифры документов и номер лицензии не разрываем переносом: «СанПиН 3.3686-21», «ТР ТС 021/2011», «Л064-00111-77/01942445»
    code = re.compile(r'(?<![\w.])((?:(?:СанПиН|СП|МР|Р)[ \xa0])?(?:\d+(?:\.\d+)+(?:/\d+(?:\.\d+)+)?-\d{2})'
                      r'|ТР[ \xa0]ТС[ \xa0]\d{3}/\d{4}|Л064-00111-77/01942445|[Пп]ест-контрол\w*)(?![\w-])')
    parts = re.split(r'(<[^>]+>)', main)
    main = ''.join(p if p.startswith('<') else code.sub(r'<span class="nw">\1</span>', p) for p in parts)
    # надзаголовок — flex-контейнер: текст и шифр документа держим в одном элементе
    main = re.sub(r'(<div class="eyebrow">)((?:(?!</div>).)*?<span class="nw">(?:(?!</div>).)*?)(</div>)',
                  r'\1<span>\2</span>\3', main)
    main = main.replace('"@/', '"../../').replace(' @/', ' ../../')
    assert '@/' not in main, 'остались метки @/'
    return main.strip()


def main():
    shell = (ROOT / 'dezinsektsiya' / 'index.html').read_text(encoding='utf-8')
    provider = provider_from(shell)
    s = deeper(shell)
    # --- head
    s = sub1(r'<title>.*?</title>', f'<title>{TITLE}</title>', s)
    s = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESC}">', s)
    s = sub1(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">', s)
    s = sub1(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">', s)
    s = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{OG_TITLE}">', s)
    s = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{OG_DESC}">', s)
    s = sub1(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{SITE}img/avto-og.jpg">', s)
    s = sub1(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{HERO_ALT}">', s)
    s = sub1(r'<link rel="preload" as="image" media="\(min-width:861px\)" imagesrcset="[^"]*"',
             '<link rel="preload" as="image" media="(min-width:861px)" imagesrcset="../../img/avto-hero-1440.webp 1440w, '
             '../../img/avto-hero.webp 1920w"', s)
    s = sub1(r'<link rel="preload" as="image" media="\(max-width:860px\)" imagesrcset="[^"]*"',
             '<link rel="preload" as="image" media="(max-width:860px)" imagesrcset="../../img/avto-hero-mob-760.webp 760w, '
             '../../img/avto-hero-mob.webp 1024w"', s)
    s = sub1(r'<script type="application/ld\+json">.*?</script>', ld_json(provider), s)
    # стили: общие блоки страниц услуг (как у дезинсекции) + блоки этой страницы
    extra = (HERE / 'extra.css').read_text(encoding='utf-8')
    extra = re.sub(r'/\*.*?\*/', '', extra, flags=re.S)
    extra = re.sub(r'\s*\n\s*', '', extra)
    m = re.search(r'<style>(.*?)</style>', s, re.S)
    s = s[:m.end(1)] + '\n' + extra + '\n' + s[m.end(1):]
    s = sub1(r'<body class="d-page">', '<body class="d-page avt-page">', s)
    # --- main
    s = sub1(r'<main id="main" tabindex="-1">.*?</main>', build_main(), s)
    # --- скрипт страницы (предпросмотр, самопроверка, схема кузова, фон блока заявки, форма)
    js = (HERE / 'page.js').read_text(encoding='utf-8').strip()
    s = sub1(r'<script>\n/\* Предпросмотр: вне рабочего домена.*?</script>', '<script>\n' + js + '\n</script>', s)
    assert 'dez-hero' not in s and 'dez-og' not in s, 'остались фото страницы дезинсекции'
    # меню и подвал перестроит apply_menu.py (текущая страница — эта)
    out = ROOT / SLUG / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(s, encoding='utf-8')
    print('ok', out.relative_to(ROOT), len(s), 'байт')


if __name__ == '__main__':
    main()
