#!/usr/bin/env python3
"""Сборка раздела «Нормативная база»: две страницы.

    normativnaya-baza/index.html                    — хаб «СанПиН и требования к дезинсекции и дератизации» (hub.html)
    normativnaya-baza/proverochnye-listy/index.html — «Проверочные листы Роспотребнадзора 2026» (listy.html)
    normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.html — «Документы для Роспотребнадзора» (dokumenty.html;
        перечень, «Соберите папку» и «По типам объектов» — из dokumenty_data.py, стили dokumenty.css, скрипт dokumenty.js)

Шаблон — готовая отраслевая страница pishchevoe-proizvodstvo/index.html (как у санитарного аудита): из неё берутся
<head> без заголовков, шапка, мобильное меню, подвал, плавающие кнопки, ранний скрипт и загрузчик анимаций, общие стили.
Своё у страниц: заголовок, описание, Open Graph, структурированные данные, стили page.css, содержимое и вопросы FAQ.
Вторая страница лежит на уровень глубже, поэтому относительные пути шаблона '../' в ней становятся '../../'.

Метки в hub.html и listy.html:
    @/                     — корень сайта (../ или ../../)
    <!--FAQ-->             — блок вопросов (из списков FAQ ниже, из них же FAQPage)
    <!--TIMELINE-->        — хроника изменений (прошедшие даты — серым, по дате DATE)
    <!--ROADMAP-->         — дорожная карта норм 2025–2027 над хроникой (метка «Сегодня» — по дате посетителя, см. ROAD_JS)
    <!--HERO_PHOTO-->      — фото первого экрана (img/<hero>.webp, мастер-файлы и нарезка — make_images.py)
    <!--OBJ:адрес:текст--> — название объекта; ссылка, только если такая страница есть в репозитории
    <!--INDLINKS-->        — строка ссылок на отраслевые страницы (только существующие)
    <!--FORM_FIELDS-->     — поля формы; тип объекта — только значения, которые принимает send.php
    <!--CTA_CONTACTS-->, <!--ICON:имя-->, LICENSE_URL — как на странице санитарного аудита
                             (иконки — tools/site/icons.json и свои иконки раздела icons-nb.json)
    <!--DK_SHORT-->, <!--DK_TYPES-->, <!--DK_GROUPS-->, <!--DK_OBJECTS-->, CHECKLIST_PDF — страница документов (dokumenty_data.py)

Дальше страницы доводит общий конвейер сайта (бегущая строка, «Смотрите также», разметка анимаций, общее меню):

    python3 tools/normativnaya-baza/build_pages.py   # build_site.py запускает его сам
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
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import dokumenty_data as DK  # noqa: E402  перечень документов для проверки Роспотребнадзора (третья страница раздела)

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
DATE = '2026-11-06'  # дата сверки норм; при публикации в другой день поменяйте datePublished в PAGES
DK_DATE = '2026-11-08'  # страница «Документы для Роспотребнадзора»: опубликована 08.11.2026 (нормы и перечни сверены 06–07.11.2026)
SEARCH_V = '20261107'  # версия search.min.js и search-index.json (поиск по сайту, tools/search) — меняйте при их обновлении
AUTHOR = {'@type': 'Person', 'name': 'Марианна Семерина', 'jobTitle': 'Санитарный врач'}
# фото в карточке автора иллюстративное (сгенерировано), поэтому image у Person не указываем
ORG = {'@type': 'Organization', '@id': SITE + '#org', 'name': 'ПЕСТКОНТРОЛЬ Центр',
       'legalName': 'ООО «Центр дезинфекционных услуг»', 'url': SITE,
       'telephone': '+7 495 104-35-70', 'email': 'b2b@pestcontrol-center.ru'}
LICENSE_URL = 'https://fp.rospotrebnadzor.ru/licen/?oper=search&amp;numb_history=&amp;numb=&amp;firmget_name=&amp;ogrn_inn_nza=7714462211'

HUB_FAQ = [
    ('Какой документ главный по дезинсекции и дератизации в 2026 году?',
     'СанПиН 3.3686-21 «Санитарно-эпидемиологические требования по профилактике инфекционных болезней», раздел III. '
     'Он действует до 1 сентября 2027 года. Отраслевые требования содержатся в правилах 2026 года для общепита, торговли '
     'и помещений, а для пищевых производств — ещё и в ТР ТС 021/2011.'),
    ('Обязательна ли дератизация для организаций и ИП?',
     'Да. Юридические лица и ИП обеспечивают дезинсекцию и дератизацию на своих объектах — сами или через '
     'специализированную организацию (п. 88 СанПиН 3.3686-21). Это не обязательно ежемесячная раскладка родентицидов: '
     'дератизация включает обследование, профилактику и истребительные мероприятия по результатам оценки (пп. 108–110).'),
    ('Как часто проводить дезинсекцию и дератизацию на предприятии?',
     'Зависит от объекта. На объектах особого эпидемиологического значения — пищевых и торговых, в гостиницах, '
     'медицинских и детских организациях — обследования на насекомых проводят не реже 2 раз в месяц, на других объектах — '
     'раз в месяц (п. 101 СанПиН 3.3686-21). Заселённость грызунами на объектах особого эпидемиологического значения '
     'оценивают ежемесячно, а дератизацию проводят по результатам оценки (п. 110). Обработки назначают по результатам '
     'обследований.'),
    ('Что такое объекты особого эпидемиологического значения?',
     'Это объекты из перечня в п. 98 СанПиН 3.3686-21. Среди них организации пищевой промышленности и общественного '
     'питания, организации, которые хранят и продают пищевую продукцию, гостиницы и общежития, медицинские, '
     'санаторно-курортные и детские образовательные организации, вокзалы, аэропорты и объекты транспорта. Перечень '
     'широкий: в него входят также здания, предназначенные для постоянного или временного пребывания людей, и объекты '
     'коммунально-бытового назначения. Их обследуют на насекомых не реже 2 раз в месяц, а дератизацию проводят '
     'по результатам ежемесячной оценки.'),
    ('Нужна ли подрядчику лицензия и можно ли проводить обработки своими силами?',
     'С 1 марта 2025 года услуги по дезинфекции, дезинсекции и дератизации оказывают только по лицензии. Если организация '
     'работает для собственных нужд, лицензия ей не нужна. При этом в проверочных листах для гостиниц, аптек, спортивных '
     'объектов, бань и магазинов непродовольственных товаров есть вопрос, проводит ли обработки «организация, '
     'осуществляющая дезинфекционную деятельность».'),
    ('Действует ли СП 3.5.3.3223-14?',
     'Нет. СП 3.5.3.3223-14 о дератизации утратили силу 1 сентября 2021 года, их требования вошли в раздел III '
     'СанПиН 3.3686-21. Тогда же утратил силу СанПиН 3.5.2.3472-17 о дезинсекции. Если программа или договор '
     'ссылаются на эти документы, ссылки нужно обновить.'),
    ('Можно ли оставить в программе производственного контроля ссылки на старые СП и СанПиН?',
     'Лучше обновить. Правила 2020–2021 годов для общепита, торговли и помещений заменены с 1 сентября 2026 года, '
     'а СП 3.5.3.3223-14 и СанПиН 3.5.2.3472-17 не действуют с 2021 года. Ссылки на отменённые документы показывают '
     'инспектору и аудитору, что программу давно не пересматривали.'),
    ('Что будет после 1 сентября 2027 года?',
     'В этот день заканчивается срок действия СанПиН 3.3686-21. Изменения, подготовленные в марте 2026 года, раздел '
     'о дезинсекции и дератизации не затрагивают. Мы отслеживаем проекты и обновим эту страницу и образцы документов, '
     'как только новые правила будут опубликованы.'),
    ('Где найти официальные тексты документов?',
     'На портале официального опубликования publication.pravo.gov.ru и в системе pravo.gov.ru. Ссылки на каждый '
     'документ — в таблицах выше и в списке источников.'),
]

LISTY_FAQ = [
    ('С какого числа действуют новые проверочные листы Роспотребнадзора?',
     'Приказ № 578 — с 4 октября 2026 года, приказ № 580 — с 5 октября 2026 года. Они заменили приказ № 18 '
     'от 20.01.2022 и приказ № 808 от 24.12.2021.'),
    ('Может ли инспектор проверять то, чего нет в проверочном листе?',
     'Да. В п. 2 обоих приказов сказано, что плановый рейдовый осмотр и выездная проверка не ограничиваются вопросами '
     'из форм.'),
    ('Как часто нужно обследовать объект на насекомых?',
     'Объекты особого эпидемиологического значения — не реже 2 раз в месяц, другие объекты — раз в месяц, очаги '
     'инфекционных заболеваний — раз в неделю (п. 101 СанПиН 3.3686-21).'),
    ('Нужно ли проводить дератизацию каждый месяц?',
     'На объектах особого эпидемиологического значения раз в месяц обязательна оценка заселённости грызунами. '
     'Истребительные мероприятия проводят по её результатам (п. 110 СанПиН 3.3686-21).'),
    ('Можно ли проводить дезинсекцию и дератизацию своими силами?',
     'Лицензия не нужна, если работы выполняют для собственных нужд. Но в листах для гостиниц, аптек, магазинов '
     'непродовольственных товаров, спортивных объектов и бань спрашивают, проводит ли обработки «организация, '
     'осуществляющая дезинфекционную деятельность». Для мест массового пребывания людей это прямо установлено '
     'п. 130 СанПиН 3.3686-21.'),
    ('Что спрашивают о вредителях при проверке общепита?',
     'В листе для общепита (приказ № 580, приложение 2) четыре таких вопроса: дезинсекция и дератизация в составе '
     'производственного контроля на принципах ХАССП (вопрос 11), отсутствие насекомых, грызунов, синантропных птиц '
     'и животных (58), запрет хранить и готовить продукцию во время обработок (108) и запрет распыляемых '
     'и рассыпаемых средств при посетителях и персонале (109).'),
    ('Что спрашивают о вредителях при проверке магазина продуктов?',
     'В листе для торговли пищевой продукцией (приказ № 580, приложение 1) пять таких вопросов: защита продукции '
     'от грызунов и насекомых при перевозке (58), хранение сыпучих продуктов в помещениях, не заражённых амбарными '
     'вредителями (89), дератизация площадки накопления отходов (138), запрет присутствия насекомых и грызунов (153) '
     'и дезинсекция, дератизация и инженерная защита зданий (155).'),
    ('Есть ли проверочный лист для пищевого производства?',
     'В приказах № 578 и № 580 отдельной формы нет. На производстве оценивают процедуры ХАССП по ТР ТС 021/2011, '
     'в том числе периодичность и проведение дезинсекции и дератизации (ст. 10 ч. 3 п. 10).'),
    ('Применяют ли проверочные листы при профилактическом визите?',
     'Приказы утверждают формы для плановых рейдовых осмотров и выездных проверок. О профилактическом визите — '
     'на <a href="@/sanitarnyy-audit/">странице санитарного аудита</a>.'),
    ('Где взять полный текст проверочных листов?',
     'Официальная публикация приказа № 580 — на publication.pravo.gov.ru. Тексты всех форм обоих приказов есть '
     'в системе «Гарант», ссылки — в таблице «Какие вопросы зададут на вашем объекте» и в источниках.'),
]

GARANT_PROJ = 'https://www.garant.ru/products/ipo/prime/doc/56948554/'
CNTD_PROJ = 'https://cntd.ru/news/read/rospotrebnadzor-planiruet-aktualizirovat-sanitarnye-pravila-k-vode-vozduxu-pocvam-ziliu-otxodam'
TIMELINE = [  # (дата ISO, как показать, что происходит, что сделать)
    ('2026-09-01', '01.09.2026', 'Вступили в силу правила для общепита, торговли, помещений и условий труда',
     'Обновить ссылки в программе производственного контроля и программе пест-контроля'),
    ('2026-10-04', '04–05.10.2026', 'Начали применяться новые проверочные листы',
     'Пройти вопросы своей формы — <a href="@/normativnaya-baza/proverochnye-listy/">разбор проверочных листов</a>'),
    ('2026-10-05', '05.10.2026', 'Вступила в силу редакция СанПиН 2.1.3684-21 от 10.09.2026', ''),
    ('2027-03-01', '01.03.2027', 'Заканчивается срок СанПиН 2.1.3684-21. В июле 2026 года разработан проект замены '
     f'(<a href="{CNTD_PROJ}" target="_blank" rel="noopener">Техэксперт</a>)',
     'После утверждения сверить ссылки в программах и договоре'),
    ('2027-09-01', '01.09.2027', 'Заканчивается срок СанПиН 3.3686-21. Изменения, подготовленные в марте 2026 года, '
     f'раздел о дезинсекции и дератизации не затрагивают (<a href="{GARANT_PROJ}" target="_blank" rel="noopener">Гарант</a>)',
     'Мы отслеживаем проекты и обновим эту страницу и образцы документов после публикации новых правил'),
    ('2030-09-01', '01.09.2030', 'Заканчивается срок формы программы производственного контроля для исполнителей '
     '(приказ № 415)', ''),
]

IN, OUT = 'https://schema.org/InForce', 'https://schema.org/NotInForce'
LAWS = [  # документы хаба для разметки ItemList (Legislation)
    ('Федеральный закон № 52-ФЗ', 'О санитарно-эпидемиологическом благополучии населения', '1999-03-30', IN, None,
     'https://base.garant.ru/483424596/7a69fb6632f5876efd3160114758a106/'),
    ('СанПиН 3.3686-21', 'Санитарно-эпидемиологические требования по профилактике инфекционных болезней', '2021-01-28', IN,
     '2027-09-01', 'http://pravo.gov.ru/proxy/ips/?docbody=&nd=602107773'),
    ('СанПиН 2.1.3684-21', 'Санитарно-эпидемиологические требования к содержанию территорий городских и сельских поселений, '
     'к водным объектам, питьевой воде и питьевому водоснабжению, атмосферному воздуху, почвам, жилым помещениям, '
     'эксплуатации производственных, общественных помещений, организации и проведению санитарно-противоэпидемических '
     '(профилактических) мероприятий', '2021-01-28', IN, '2027-03-01',
     'http://pravo.gov.ru/proxy/ips/?doc_itself=&backlink=1&nd=602024221&page=1&rdk=3'),
    ('СанПиН 2.3/2.4.4282-26', 'Санитарные правила для общественного питания', None, IN, None,
     'https://www.garant.ru/products/ipo/prime/doc/414229257/'),
    ('СП 2.3.6.4281-26', 'Санитарные правила для торговли пищевой продукцией и рынков', None, IN, None,
     'https://cgon.rospotrebnadzor.ru/biznesu/articles/novye-sanitarnye-pravila-dlya-torgovykh-obektov-i-rynkov-realizuyushchikh-pishchevuyu-produktsiyu/'),
    ('СП 2.1.4284-26', 'Санитарные правила для эксплуатации помещений и оказания услуг', None, IN, None,
     'https://www.consultant.ru/law/hotdocs/94328.html'),
    ('Приказ Роспотребнадзора № 578', 'Об утверждении форм проверочных листов (31 форма)', '2026-07-20', IN, None,
     'https://base.garant.ru/414956074/'),
    ('Приказ Роспотребнадзора № 580', 'Об утверждении форм проверочных листов (6 форм)', '2026-07-20', IN, None,
     'http://publication.pravo.gov.ru/document/0001202609240001'),
    ('Федеральный закон № 99-ФЗ', 'О лицензировании отдельных видов деятельности', '2011-05-04', IN, None,
     'https://cgon.rospotrebnadzor.ru/biznesu/profilaktika-nadzor-uslsugi/nadzornie-meropriatiya/litsenzirovanie-dezinfektsionnoy-deyatelnosti/'),
    ('Приказ Роспотребнадзора № 415', 'Форма программы производственного контроля для организаций, оказывающих услуги '
     'по дезинфекции, дезинсекции и дератизации', '2024-05-30', IN, '2030-09-01',
     'http://www.pravo.gov.ru/proxy/ips/?docbody=&prevDoc=602107773&backlink=1&nd=607119571&rdk='),
    ('МР 3.5.3.0374-25', 'Дератизация. Организация и проведение дератизационных мероприятий', '2025-04-28', IN, None,
     'https://legalacts.ru/doc/mr-3530374-25-353-deratizatsija-organizatsija-i-provedenie-deratizatsionnykh-meroprijatii/'),
    ('ТР ТС 021/2011', 'О безопасности пищевой продукции', '2011-12-09', IN, None, 'https://docs.cntd.ru/document/902320560'),
    ('ГОСТ Р 51705.1-2024', 'Управление качеством и безопасностью пищевых продуктов на основе принципов ХАССП. '
     'Общие требования', None, IN, None, 'https://base.garant.ru/409077162/'),
    ('ГОСТ Р 54762-2011', 'Программы предварительных требований по безопасности пищевой продукции. Часть 1', None, IN, None,
     'https://base.garant.ru/70754062/'),
    ('СП 3.5.3.3223-14', 'Санитарно-эпидемиологические требования к организации и проведению дератизационных мероприятий',
     None, OUT, '2021-09-01', 'https://docs.cntd.ru/document/420223924'),
    ('СанПиН 3.5.2.3472-17', 'Санитарно-эпидемиологические требования к организации и проведению дезинсекционных '
     'мероприятий', None, OUT, '2021-09-01', 'https://www.normacs.ru/Doclist/doc/15NM.html'),
]

ROADMAP = [  # (дата ISO, как показать, что происходит, подпись сверху или снизу оси, место на оси в %)
    ('2025-03-01', '01.03.2025', 'Услуги по дезинсекции и дератизации — только по лицензии', 'up', 6),
    ('2026-09-01', '01.09.2026', 'Новые правила для общепита, торговли, помещений и условий труда', 'down', 22),
    ('2026-10-04', '04–05.10.2026', 'Начали применяться новые проверочные листы', 'up', 38),
    ('2026-10-05', '05.10.2026', 'Новая редакция СанПиН 2.1.3684-21', 'down', 51),
    ('2027-03-01', '01.03.2027', 'Заканчивается срок СанПиН 2.1.3684-21', 'up', 72),
    ('2027-09-01', '01.09.2027', 'Заканчивается срок СанПиН 3.3686-21', 'down', 90),
]

TYPES_HUB = [('Пищевое производство', 'Пищевое производство'), ('Ресторан или кафе', 'Ресторан или кафе'),
             ('Магазин или торговая сеть', 'Магазин продуктов'), ('Склад, логистика', 'Склад'),
             ('Гостиница', 'Гостиница'), ('Другое', 'Медицинская организация'), ('Другое', 'Другое')]
TYPES_LISTY = [('Ресторан или кафе', 'Ресторан или кафе'), ('Магазин или торговая сеть', 'Магазин продуктов'),
               ('Склад, логистика', 'Склад'), ('Пищевое производство', 'Пищевое производство'),
               ('Гостиница', 'Гостиница'), ('Другое', 'Медицинская организация'), ('Другое', 'Аптека'),
               ('Другое', 'Другое')]
TYPES_DOC = [(send, lab) for _, lab, send, _ in DK.OBJECTS] + [('Другое', 'Другое')]
SEND_TYPES = {'Пищевое производство', 'Фармацевтическое производство', 'Ресторан или кафе', 'Гостиница',
              'Магазин или торговая сеть', 'Склад, логистика', 'Элеватор, комбикормовый завод', 'Другое'}  # как в send.php

PAGES = [
    {
        'src': 'hub.html', 'out': 'normativnaya-baza/index.html', 'slug': 'normativnaya-baza/', 'root': '../',
        'title': 'СанПиН по дезинсекции и дератизации 2026: требования и периодичность',
        'og_title': 'СанПиН и требования к дезинсекции и дератизации в 2026 году',
        'desc': 'Какие СанПиН и нормативные документы действуют для дезинсекции и дератизации в 2026 году: '
                'периодичность, лицензия, ХАССП, сроки и отменённые документы.',
        'h1': 'СанПиН и требования к дезинсекции и дератизации: что действует в 2026 году',
        'crumbs': [('Главная', ''), ('Нормативная база', 'normativnaya-baza/')],
        'og_image': 'nb-og.jpg', 'og_alt': 'СанПиН и требования к дезинсекции и дератизации в 2026 году',
        'hero': 'nb-hero', 'hero_alt': 'Санитарный врач в белом халате и голубых перчатках листает папку с нормативными '
                                        'документами в производственном помещении; на стене — ловушка для летающих насекомых',
        'faq': HUB_FAQ, 'faq_h2': 'Вопросы <em>о нормативных требованиях</em>',
        'types': TYPES_HUB, 'name': 'Нормативная база', 'comment_ph': 'Комментарий: вид деятельности, площадь, ближайшая проверка',
        'date_published': DATE,
    },
    {
        'src': 'listy.html', 'out': 'normativnaya-baza/proverochnye-listy/index.html',
        'slug': 'normativnaya-baza/proverochnye-listy/', 'root': '../../',
        'title': 'Проверочные листы Роспотребнадзора 2026: дезинсекция и дератизация',
        'og_title': 'Проверочные листы Роспотребнадзора 2026: вопросы о дезинсекции и дератизации',
        'desc': 'Вопросы о насекомых и грызунах в проверочных листах (чек-листах) Роспотребнадзора по приказам № 578 '
                'и № 580: где они есть, нормы СанПиН и документы для ответа.',
        'h1': 'Проверочные листы Роспотребнадзора 2026: вопросы о дезинсекции и дератизации',
        'crumbs': [('Главная', ''), ('Нормативная база', 'normativnaya-baza/'),
                   ('Проверочные листы 2026', 'normativnaya-baza/proverochnye-listy/')],
        'og_image': 'pl-og.jpg', 'og_alt': 'Проверочные листы Роспотребнадзора 2026: вопросы о дезинсекции и дератизации',
        'hero': 'pl-hero', 'hero_alt': 'Менеджер по качеству отмечает пункты проверочного листа, специалист по пест-контролю '
                                        'показывает на пронумерованный контейнер для мониторинга грызунов на складе',
        'faq': LISTY_FAQ, 'faq_h2': 'Вопросы <em>о проверочных листах</em>',
        'types': TYPES_LISTY, 'name': 'Проверочные листы 2026', 'comment_ph': 'Комментарий: вид деятельности, дата проверки, что смущает',
        'date_published': DATE,
    },
    {
        'src': 'dokumenty.html', 'out': 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.html',
        'slug': 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/', 'root': '../../',
        'title': 'Документы для Роспотребнадзора: перечень для проверки в 2026 году',
        'og_title': 'Документы для Роспотребнадзора: полный перечень для проверки',
        'desc': 'Какие документы нужны для проверки Роспотребнадзора: договоры, акты, протоколы лабораторных исследований, '
                'журналы и ППК. Перечень по типам объектов и чек-лист PDF. Москва и область.',
        'h1': 'Документы для Роспотребнадзора: полный перечень для проверки',
        'crumbs': [('Главная', ''), ('Нормативная база', 'normativnaya-baza/'),
                   ('Документы для Роспотребнадзора', 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/')],
        'og_image': 'dk-og.jpg', 'og_alt': 'Документы для Роспотребнадзора: полный перечень для проверки',
        'hero': 'dk-hero', 'hero_alt': 'Управляющая кафе листает папку документов к проверке Роспотребнадзора, специалист '
                                        'по пест-контролю в перчатках показывает ручкой на акт; за ними — стеллаж с папками',
        'faq': DK.FAQ, 'faq_h2': 'Вопросы <em>о документах для проверки</em>',
        'types': TYPES_DOC, 'name': 'Документы для Роспотребнадзора',
        'comment_ph': 'Комментарий: вид деятельности, каких документов не хватает, когда проверка',
        'date_published': DK_DATE, 'date_modified': DK_DATE, 'css': 'dokumenty.css', 'js': 'dokumenty.js', 'body_cls': 'dk-page',
    },
]

# короткое слово перед словом через дефис входит в тот же span: «к\u00a0пест-контролю» не разрывается и в анимации заголовков
NW_RE = re.compile(r'(?<![\w>-])((?:[А-Яа-яЁё]{1,3}\u00a0)?[А-Яа-яЁё]+-[А-Яа-яЁё]+)(?![\w-])')
# номера документов не разрываем на дефисе: «СанПиН 2.3/2.4.4282-26», «248-ФЗ», «ТР ТС 021/2011»
CODE_RE = re.compile(r'(?<![\w/.-])((?:\d+[./])*\d+-(?:\d+|ФЗ)(?:[-/]\d+)*)(?![\w-])')
TRTS_RE = re.compile(r'ТР[ \u00a0]ТС[ \u00a0](\d{3}/\d{4})')
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
        # сначала неразрывные пробелы (пока в тексте нет тегов: «к» перед словом через дефис не повиснет), потом nw
        t = typo(part)
        # длинные слова («санитарно-эпидемиологическое») могут переноситься на дефисе, иначе не помещаются на 320 px
        t = NW_RE.sub(lambda m: m.group(1) if len(m.group(1)) > 18 else '<span class="nw">' + m.group(1) + '</span>', t)
        t = CODE_RE.sub(r'<span class="nw">\1</span>', t)
        t = TRTS_RE.sub(lambda m: '<span class="nw">ТР\u00a0ТС\u00a0' + m.group(1) + '</span>', t)
        out.append(t)
    return ''.join(out)


def plain(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html)).replace('&amp;', '&').replace('\u00a0', ' ').strip()


def cut(s, start, end, after=False):
    i = s.index(start)
    j = s.index(end, i)
    return s[i:j + (len(end) if after else 0)]


def deeper(s):
    """Относительные пути шаблона ('../') для страницы на уровень глубже."""
    return re.sub(r'(?<=["\'(,\s])\.\./', '../../', s)


def faq_section(faq, h2):
    def qa(i, q, a):
        return (f'        <div class="card qa"><button aria-expanded="false" aria-controls="a{i}" id="q{i}"><span>{q}</span><span class="pm"></span></button>'
                f'<div class="ans" id="a{i}" role="region" aria-labelledby="q{i}"><div><p>{a}</p></div></div></div>')
    half = (len(faq) + 1) // 2
    html = ['<section class="s" id="voprosy">', '  <div class="wrap">',
            f'    <div class="head"><div class="eyebrow">Вопросы</div><h2>{h2}</h2></div>',
            '    <div class="faq">']
    n = 0
    for col in (faq[:half], faq[half:]):
        html.append('      <div class="faq-col">')
        for q, a in col:
            n += 1
            html.append(qa(n, q, a))
        html.append('      </div>')
    html += ['    </div>', '  </div>', '</section>']
    return '\n'.join(html)


def timeline_html():
    rows = []
    for iso, shown, what, todo in TIMELINE:
        cls = 'is-past' if iso <= DATE else 'is-next'
        todo_html = f'<span class="nb-tl-k">Что сделать</span>{todo}' if todo else ''
        rows.append(f'      <li class="{cls}"><time class="nb-tl-d" datetime="{iso}">{shown}</time>'
                    f'<p class="nb-tl-w">{what}</p><p class="nb-tl-a">{todo_html}</p></li>')
    return '\n'.join(rows)


def hero_photo(p):
    """<picture> первого экрана, как на странице программы пест-контроля: на телефоне (до 860 px) кадр 4:3."""
    n = p['hero']
    return (f'<div class="d-hero-media"><picture><source media="(max-width:860px)" '
            f'srcset="@/img/{n}-mob-760.webp 760w, @/img/{n}-mob.webp 1024w" sizes="100vw" width="1024" height="768">'
            f'<img class="d-hero-img" src="@/img/{n}.webp" srcset="@/img/{n}-1440.webp 1440w, @/img/{n}.webp 1920w" '
            f'sizes="100vw" width="1920" height="1072" alt="{p["hero_alt"]}" fetchpriority="high" decoding="async">'
            '</picture></div>')


def hero_preload(p):
    n = p['hero']
    return (f'<link rel="preload" as="image" media="(min-width:861px)" imagesrcset="../img/{n}-1440.webp 1440w, '
            f'../img/{n}.webp 1920w" imagesizes="100vw" fetchpriority="high">\n'
            f'<link rel="preload" as="image" media="(max-width:860px)" imagesrcset="../img/{n}-mob-760.webp 760w, '
            f'../img/{n}-mob.webp 1024w" imagesizes="100vw" fetchpriority="high">\n')


def road_now(today):
    """Место метки «Сегодня» на оси и её порядок в вертикальной карте (телефон). Тот же расчёт — в ROAD_JS."""
    ds = [r[0] for r in ROADMAP]
    xs = [r[4] for r in ROADMAP]
    i = sum(d <= today for d in ds)
    if i == 0:
        return max(1, xs[0] - 4), -1
    if i == len(ds):
        return min(99, xs[-1] + 4), 2 * len(ds)
    import datetime
    f = lambda d: datetime.date.fromisoformat(d).toordinal()  # noqa: E731
    k = (f(today) - f(ds[i - 1])) / (f(ds[i]) - f(ds[i - 1]))
    return round(xs[i - 1] + (xs[i] - xs[i - 1]) * k, 1), 2 * i - 1


def roadmap_html():
    x, order = road_now(DATE)
    pts = []
    for k, (iso, shown, what, side, pos) in enumerate(ROADMAP):
        state = 'is-past' if iso <= DATE else 'is-next'
        pts.append(f'        <li class="nb-road-pt is-{side} {state}" data-d="{iso}" style="--x:{pos}%;--o:{2 * k}">'
                   f'<time datetime="{iso}">{shown}</time><span>{what}</span></li>')
    shown = '.'.join(reversed(DATE.split('-')))
    return '\n'.join([
        '    <figure class="nb-fig nb-road-fig">',
        '      <figcaption class="nb-fig-head"><span class="nb-fig-t">Дорожная карта норм <em>2025–2027</em></span>'
        '<span class="nb-fig-d">Серым — то, что уже действует, цветом — предстоящие сроки.</span></figcaption>',
        '      <ol class="nb-road" id="nbRoad">',
        f'        <li class="nb-road-axis" aria-hidden="true"><i class="nb-road-fill" style="width:{x}%"></i></li>',
        *pts,
        f'        <li class="nb-road-now" aria-hidden="true" style="--x:{x}%;--o:{order}"><span>Сверка норм · {shown}</span></li>',
        '      </ol>',
        '    </figure>'])


# метка «Сегодня» и цвет событий — по дате посетителя (без скрипта — по дате сверки DATE, как в хронике)
ROAD_JS = ("<script>/* Дорожная карта и хроника: прошедшее — серым, метка «Сегодня» — по сегодняшней дате */\n"
           "(function(){var r=document.getElementById('nbRoad');if(!r)return;var t=new Date(),d=new Date(t.getFullYear(),t.getMonth(),t.getDate()),"
           "P=function(s){var a=s.split('-');return new Date(+a[0],a[1]-1,+a[2]);},pts=[].slice.call(r.querySelectorAll('[data-d]')),"
           "ds=pts.map(function(p){return P(p.getAttribute('data-d'));}),xs=pts.map(function(p){return parseFloat(p.style.getPropertyValue('--x'));}),"
           "i=0,x,o;while(i<ds.length&&ds[i]<=d)i++;"
           "if(i===0){x=Math.max(1,xs[0]-4);o=-1;}else if(i===ds.length){x=Math.min(99,xs[i-1]+4);o=2*i;}"
           "else{x=xs[i-1]+(xs[i]-xs[i-1])*(d-ds[i-1])/(ds[i]-ds[i-1]);o=2*i-1;}"
           "pts.forEach(function(p,k){p.classList.toggle('is-past',ds[k]<=d);p.classList.toggle('is-next',ds[k]>d);});"
           "var n=r.querySelector('.nb-road-now'),z=function(v){return(v<10?'0':'')+v;};"
           "n.style.setProperty('--x',x.toFixed(1)+'%');n.style.setProperty('--o',o);"
           "n.firstChild.textContent='Сегодня · '+z(d.getDate())+'.'+z(d.getMonth()+1)+'.'+d.getFullYear();"
           "r.querySelector('.nb-road-fill').style.width=x.toFixed(1)+'%';"
           "[].forEach.call(document.querySelectorAll('.nb-tl li'),function(li){var m=li.querySelector('time');if(!m)return;"
           "var e=P(m.getAttribute('datetime'));li.classList.toggle('is-past',e<=d);li.classList.toggle('is-next',e>d);});})();</script>\n")


def form_fields(p):
    for value, _ in p['types']:
        assert value in SEND_TYPES, 'send.php не примет тип объекта: ' + value
    opts = ''.join(f'<option value="{v}">{t}</option>' if v != t else f'<option>{t}</option>' for v, t in p['types'])
    return '\n'.join([
        '<div class="field"><label class="sr-only" for="f-name">Ваше имя</label><input id="f-name" name="name" placeholder="Ваше имя" required autocomplete="name"><small class="ferr">Укажите имя</small></div>',
        '<div class="field"><label class="sr-only" for="phone">Телефон</label><input name="phone" id="phone" type="tel" inputmode="tel" placeholder="+7 (___) ___-__-__" required autocomplete="tel"><small class="ferr">Укажите телефон полностью</small></div>',
        '<div class="field full"><label class="sr-only" for="f-company">Компания</label><input id="f-company" name="company" placeholder="Компания (необязательно)" autocomplete="organization"></div>',
        f'<div class="field full"><label class="sr-only" for="f-type">Вид объекта</label><select id="f-type" name="type" required><option value="" selected>Вид объекта</option>{opts}</select><small class="ferr">Выберите вид объекта</small></div>',
        f'<div class="field full"><label class="sr-only" for="f-msg">Комментарий</label><textarea id="f-msg" name="comment" placeholder="{p["comment_ph"]}"></textarea></div>',
        '<input type="hidden" name="msg" value="">',
        '<div class="field" hidden><input type="hidden" name="email" value=""></div>',
        f'<input type="hidden" name="page" value="{p["name"]}">',
    ])


def form_js(p):
    # Вид объекта — текст выбранного пункта: «Медицинская организация» и «Аптека» уходят в send.php как «Другое»,
    # а в письмо попадает то, что выбрал посетитель
    return ("<script>/* Форма: вид объекта, комментарий и страница — в поле msg, которое читает send.php */\n"
            "document.addEventListener('submit',function(ev){var f=ev.target;if(!f||f.id!=='form')return;var e=f.elements,"
            "s=e.type,o=s&&s.selectedIndex>0?s.options[s.selectedIndex].text:'не выбран',c=e.comment.value.trim();"
            "e.msg.value='Вид объекта: '+o+(c?'\\nКомментарий: '+c:'')+"
            f"'\\nСтраница: {p['name']} (/{p['slug']})';}},true);</script>\n")


def json_ld(p):
    url = SITE + p['slug']
    crumbs = {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + s} for i, (n, s) in enumerate(p['crumbs'])]}
    faq = {'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in p['faq']]}
    image = {'@type': 'ImageObject', 'url': SITE + 'img/' + p['og_image'], 'width': 1200, 'height': 630}
    hero = {'@type': 'ImageObject', 'url': SITE + 'img/' + p['hero'] + '.webp', 'width': 1920, 'height': 1072,
            'caption': p['hero_alt']}
    if p['src'] == 'hub.html':
        items = []
        for i, (ident, name, date, force, expires, link) in enumerate(LAWS):
            law = {'@type': 'Legislation', 'position': i + 1, 'legislationIdentifier': ident, 'name': name,
                   'legislationJurisdiction': 'RU', 'legislationLegalForce': force, 'url': link}
            if date:
                law['legislationDate'] = date
            if expires:
                law['expires'] = expires
            items.append(law)
        page = {'@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': p['h1'], 'headline': p['h1'],
                'description': p['desc'], 'inLanguage': 'ru', 'datePublished': p['date_published'], 'dateModified': DATE,
                'author': AUTHOR, 'publisher': {'@id': SITE + '#org'}, 'primaryImageOfPage': hero, 'image': [hero, image],
                'about': ['Дезинсекция', 'Дератизация', 'СанПиН 3.3686-21', 'Проверочные листы Роспотребнадзора'],
                'mainEntity': {'@type': 'ItemList', 'name': 'Документы о дезинсекции и дератизации',
                               'numberOfItems': len(items), 'itemListElement': items}}
    elif p['src'] == 'dokumenty.html':
        page = {'@type': 'Article', '@id': url + '#article', 'headline': p['h1'], 'description': p['desc'],
                'inLanguage': 'ru', 'datePublished': p['date_published'], 'dateModified': p['date_modified'],
                'author': AUTHOR, 'publisher': {'@id': SITE + '#org'}, 'mainEntityOfPage': url, 'image': [hero, image],
                'about': ['Проверка Роспотребнадзора', 'Документы для проверки', 'Производственный контроль',
                          'Дезинсекция', 'Дератизация'],
                'hasPart': [{'@type': 'DigitalDocument', 'name': 'Образец акта обследования и выполненных работ по дезинсекции '
                             'и дератизации', 'encodingFormat': 'application/pdf', 'url': url + DK.AKT_PDF},
                            {'@type': 'DigitalDocument', 'name': 'Бланк акта обследования и выполненных работ по дезинсекции '
                             'и дератизации', 'encodingFormat': 'application/pdf', 'url': url + DK.AKT_BLANK},
                            {'@type': 'DigitalDocument', 'name': 'Чек-лист документов для проверки Роспотребнадзора',
                             'encodingFormat': 'application/pdf', 'url': url + DK.CHECKLIST_PDF}],
                'isPartOf': {'@id': SITE + 'normativnaya-baza/#webpage'}}
    else:
        page = {'@type': 'Article', '@id': url + '#article', 'headline': p['h1'], 'description': p['desc'],
                'inLanguage': 'ru', 'datePublished': p['date_published'], 'dateModified': DATE, 'author': AUTHOR,
                'publisher': {'@id': SITE + '#org'}, 'mainEntityOfPage': url, 'image': [hero, image],
                'about': [{'@type': 'Legislation', 'legislationIdentifier': 'Приказ Роспотребнадзора № 578',
                           'legislationDate': '2026-07-20', 'legislationLegalForce': IN, 'url': 'https://base.garant.ru/414956074/'},
                          {'@type': 'Legislation', 'legislationIdentifier': 'Приказ Роспотребнадзора № 580',
                           'legislationDate': '2026-07-20', 'legislationLegalForce': IN,
                           'url': 'http://publication.pravo.gov.ru/document/0001202609240001'}],
                'isPartOf': {'@id': SITE + 'normativnaya-baza/#webpage'}}
    graph = [ORG, crumbs, page, faq]
    return ('<script type="application/ld+json">'
            + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False) + '</script>')


def obj_link(root):
    def f(m):
        slug, text = m.group(1), m.group(2)
        if (ROOT / slug / 'index.html').exists():
            return f'<a href="{root}{slug}/">{text}</a>'
        return text
    return f


IND = [('restorany-i-kafe', 'рестораны и кафе'), ('magaziny-i-torgovye-seti', 'магазины и сети'),
       ('gostinitsy', 'гостиницы'), ('pishchevoe-proizvodstvo', 'пищевые производства'), ('sklady-i-logistika', 'склады')]


def ind_links(root):
    links = [f'<a href="{root}{s}/">{t}</a>' for s, t in IND if (ROOT / s / 'index.html').exists()]
    return (' Подробнее о вашей отрасли: ' + ' · '.join(links) + '.') if links else ''


# ---------------------------------------------------------------- страница «Документы для Роспотребнадзора»
OBJ_LABEL = {code: lab for code, lab, _, _ in DK.OBJECTS}
OBJ_GEN = {code: gen for code, _, _, gen in DK.OBJECTS}


def dk_short():
    li = ''.join(f'      <li class="card"><a href="#{gid}"><span class="dk-n">{n}</span><b>{title}</b><span>{short}</span></a></li>\n'
                 for gid, n, title, short in DK.GROUPS)
    return '    <ol class="dk-short">\n' + li + '    </ol>'


def dk_types():
    def chips(objs):
        return ''.join(f'<label class="dk-chip"><input type="radio" name="dk-obekt" value="{c}"><span>{lab}</span></label>'
                       for c, lab, _, _ in objs)
    main, other = DK.OBJECTS[:DK.MAIN_OBJECTS], DK.OBJECTS[DK.MAIN_OBJECTS:]
    return (f'        <div class="dk-chips">{chips(main)}</div>\n'
            f'        <p class="dk-types-k">Другой объект — типы из проверочных листов</p>\n'
            f'        <div class="dk-chips">{chips(other)}</div>')


def dk_for(obj):
    if obj == DK.ALL:
        return ''
    names = [OBJ_LABEL[o] for o in obj]
    return '<span class="dk-for">Для объектов: ' + ', '.join(n[0].lower() + n[1:] if not n.startswith(('ППК',)) else n for n in names) + '</span>'


def dk_row(rw):
    who = rw['who']
    badge = f'<span class="dk-who{" dk-who-my" if who == "my" else ""}">{DK.WHO[who]}</span>'
    who_t = rw['who_text']
    who_html = badge + (f'<span class="dk-who-t">{who_t}</span>' if who_t != DK.WHO[who] else '')
    note = f'<span class="dk-note">{rw["note"]}</span>' if rw['note'] else ''
    sample = rw['sample'] or '—'
    obj = ' '.join(rw['obj'])
    return (f'        <tr id="d-{rw["id"]}" data-obj="{obj}" data-who="{who}" data-kw="{rw["kw"]}">'
            f'<td data-l="Документ"><b class="dk-doc">{rw["name"]}</b>{note}{dk_for(rw["obj"])}</td>'
            f'<td data-l="Кто готовит">{who_html}</td>'
            f'<td data-l="Основание">{rw["basis"]}</td>'
            f'<td data-l="Образец или услуга">{sample}</td></tr>')


AKT_CARD = (
    '    <div class="card dk-akt">\n'
    f'      <a class="dk-akt-prev" href="{DK.AKT_PDF}" data-goal="akt_obrazets" aria-label="Образец акта, PDF">'
    '<img src="@/img/akt-obrazets-p1-360.webp" srcset="@/img/akt-obrazets-p1-360.webp 360w, @/img/akt-obrazets-p1-720.webp 720w" '
    'sizes="(max-width:760px) 240px, 200px" width="360" height="509" loading="lazy" decoding="async" '
    'alt="Первая страница образца акта обследования и выполненных работ по дезинсекции и дератизации"></a>\n'
    '      <div><span class="nb-link-k">Образец · PDF, 2 страницы</span>\n'
    '        <h4>Акт обследования и выполненных работ по дезинсекции и дератизации</h4>\n'
    '        <p>Результаты обследования по точкам контроля, выполненные работы со средством, номером свидетельства '
    'о госрегистрации, концентрацией и способом, контроль эффективности прежней обработки (п. 99 СанПиН 3.3686-21), '
    'рекомендации и подписи сторон. Бланк — тот же акт без записей, лист в лист.</p>\n'
    f'        <div class="d-btns"><a class="btn btn-w" href="{DK.AKT_PDF}" download data-goal="akt_obrazets">'
    '<span class="btn-t">Образец заполнения (PDF)</span></a>'
    f'<a class="btn btn-o" href="{DK.AKT_BLANK}" download data-goal="akt_shablon"><span class="btn-t">Бланк акта (PDF)</span></a></div>\n'
    '      </div>\n'
    '    </div>')


def dk_groups():
    out = []
    for gid, n, title, _ in DK.GROUPS:
        rows = [rw for rw in DK.ROWS if rw['g'] == gid]
        assert rows, gid
        html = [f'    <div class="dk-g" id="{gid}">',
                f'    <h3 class="dk-g-h"><span class="dk-n">{n}</span>{title}</h3>']
        if gid == 'produktsiya':
            html.append('    <p class="dk-g-p">Это не наша услуга — группа нужна для полноты папки на пищевых объектах, '
                        'в школах и салонах.</p>')
        html += ['    <table class="d-table nb-tbl dk-tbl">',
                 '      <thead><tr><th scope="col">Документ</th><th scope="col">Кто готовит</th><th scope="col">Основание</th>'
                 '<th scope="col">Образец или услуга</th></tr></thead>',
                 '      <tbody>'] + [dk_row(rw) for rw in rows] + ['      </tbody>', '    </table>']
        if gid == 'akty':
            html.append(AKT_CARD)
        html.append('    </div>')
        out.append('\n'.join(html))
    ids = [rw['id'] for rw in DK.ROWS]
    assert len(ids) == len(set(ids)), 'повторяются id строк перечня'
    for rw in DK.ROWS:
        assert rw['obj'] == DK.ALL or all(o in OBJ_LABEL for o in rw['obj']), rw['id']
    return '\n'.join(out)


def dk_objects():
    rows = []
    for code, lab, _, _ in DK.OBJECTS:
        form, url, qn, cat, add = DK.KITS[code]
        if url:
            sheet = f'<a href="{url}" target="_blank" rel="noopener">{form}</a>' + (f'<br>вопросы о вредителях: <b class="nb-val">{qn}</b>' if qn else '')
        else:
            sheet = form[0].upper() + form[1:]
        extra = (f' Раздел официального перечня — «{cat}».' if cat else '')
        rows.append(f'        <tr id="o-{code}" data-obekt="{code}"><td data-l="Объект"><b>{lab}</b>'
                    f'<a class="dk-go" href="?obekt={code}#papka">Собрать папку →</a></td>'
                    f'<td data-l="Проверочный лист">{sheet}</td><td data-l="Что добавить">{add}{extra}</td></tr>')
    return ('    <table class="d-table nb-tbl dk-obj">\n'
            '      <thead><tr><th scope="col">Объект</th><th scope="col">Проверочный лист</th><th scope="col">Что добавить к общему списку</th></tr></thead>\n'
            '      <tbody>\n' + '\n'.join(rows) + '\n      </tbody>\n    </table>')


def dk_js(root):
    import subprocess
    src = (HERE / 'dokumenty.js').read_text(encoding='utf-8').replace('__ROOT__', root).replace('__V__', SEARCH_V)
    try:
        r = subprocess.run(['npx', '--yes', 'esbuild@0.24.2', '--minify', '--target=es2015', '--charset=utf8', '--loader=js'],
                           input=src, capture_output=True, text=True, cwd=ROOT, timeout=120)
        if r.returncode == 0 and r.stdout.strip():
            return '<script>/* Документы для Роспотребнадзора: сборщик папки, поиск по перечню (tools/normativnaya-baza/dokumenty.js) */\n' + r.stdout.strip() + '</script>\n'
    except Exception:
        pass
    sys.exit('esbuild: не удалось сжать dokumenty.js')


def build(p, tpl, icons):
    root = p['root']
    url = SITE + p['slug']
    # ---------------- <head>
    head = tpl[:tpl.index('<style>')]
    og_img = SITE + 'img/' + p['og_image']
    rep = [
        (r'<title>[^<]*</title>', f'<title>{p["title"]}</title>'),
        (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{p["desc"]}">'),
        (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">'),
        (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">'),
        (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{p["og_title"]}">'),
        (r'<meta property="og:description" content="[^"]*">',
         f'<meta property="og:description" content="{p["desc"]}">\n'
         f'<meta property="og:image" content="{og_img}">\n'
         '<meta property="og:image:type" content="image/jpeg">\n'
         '<meta property="og:image:width" content="1200">\n'
         '<meta property="og:image:height" content="630">\n'
         f'<meta property="og:image:alt" content="{p["og_alt"]}">\n'
         '<meta name="twitter:card" content="summary_large_image">'),
        (r'<meta property="og:type" content="[^"]*">', '<meta property="og:type" content="article">'),
        # вместо фото пищевой страницы — предзагрузка своего фото первого экрана (компьютер и телефон)
        (r'<link rel="preload" href="\.\./img/food-hero\.webp"[^>]*>\n<link rel="preload" href="\.\./img/food-hero-mob\.webp"[^>]*>\n?',
         hero_preload(p)),
    ]
    for pat, new in rep:
        head, n = re.subn(pat, lambda m: new, head, count=1)
        if pat.startswith('<meta property="og:type"') and n == 0:
            continue  # в шаблоне может не быть og:type
        assert n == 1, 'шаблон: не найдено ' + pat
    assert 'food-hero' not in head and 'og:image" content="' + og_img in head and p['hero'] + '-mob-760.webp' in head
    css = tpl[tpl.index('<style>') + 7:tpl.index('</style>')]
    css += '\n' + (HERE / 'page.css').read_text(encoding='utf-8').strip()
    if p.get('css'):
        css += '\n' + (HERE / p['css']).read_text(encoding='utf-8').strip()

    # ---------------- шапка, меню (общее меню потом пересобирает tools/menu/apply_menu.py)
    top = tpl[tpl.index('</head>'):tpl.index('<main id="main"')]
    top = top.replace('<body class="d-page">', '<body class="d-page nb-page' + (' ' + p['body_cls'] if p.get('body_cls') else '') + '">', 1)
    assert 'nb-page' in top

    # ---------------- подвал, плавающие кнопки, скрипты
    bottom = tpl[tpl.index('</main>') + len('</main>'):tpl.index('<script>\n/* Предпросмотр')]
    page_js = cut(tpl, '<script>\n/* Предпросмотр', '</script>', after=True)
    pv = re.match(r'<script>\n(/\* Предпросмотр[^\n]*\*/\n\(function\(\)\{.*?\n?\}\)\(\);)', page_js, re.S)
    assert pv, 'шаблон: не найден скрипт предпросмотра'
    page_js = '<script>\n' + pv.group(1) + '\n</script>'
    li = tpl.index('<script>\n  /* скрипты анимаций')
    loader = tpl[li:tpl.index('</script>', li) + len('</script>')] + '\n'
    contacts = cut(tpl, '      <div class="cta-contacts"', '    </div>\n    <form', after=False).replace(' data-fade', '')
    if root != '../':
        head, top, bottom, page_js, loader, contacts = (deeper(x) for x in (head, top, bottom, page_js, loader, contacts))

    # ---------------- содержимое
    main = (HERE / p['src']).read_text(encoding='utf-8')
    main = main.replace('<!--FAQ-->', faq_section(p['faq'], p['faq_h2']))
    main = main.replace('<!--TIMELINE-->', timeline_html())
    main = main.replace('<!--ROADMAP-->', roadmap_html())
    main = main.replace('<!--HERO_PHOTO-->', hero_photo(p))
    main = main.replace('<!--FORM_FIELDS-->', form_fields(p))
    main = re.sub(r'<!--OBJ:([a-z0-9-]+):([^>]*?)-->', obj_link('@/'), main)
    main = main.replace('<!--INDLINKS-->', ind_links('@/'))
    if p['src'] == 'dokumenty.html':
        main = (main.replace('<!--DK_SHORT-->', dk_short()).replace('<!--DK_TYPES-->', dk_types())
                .replace('<!--DK_GROUPS-->', dk_groups()).replace('<!--DK_OBJECTS-->', dk_objects())
                .replace('href="CHECKLIST_PDF"', f'href="{DK.CHECKLIST_PDF}"'))
    main = typeset(main)
    main = main.replace('href="LICENSE_URL"', f'href="{LICENSE_URL}"')
    main = re.sub(r'<!--ICON:([a-z-]+)-->', lambda m: icons[m.group(1)], main)
    main = main.replace('<!--CTA_CONTACTS-->\n', contacts.rstrip('\n') + '\n')
    main = main.replace('"@/', '"' + root).replace(' @/', ' ' + root)
    assert '@/' not in main, 'остались метки @/ в ' + p['src']
    assert '<!--' not in main.replace('<!-- ', ''), 'остались метки в ' + p['src']
    assert 'LICENSE_URL' not in main

    extra_js = dk_js(root) if p.get('js') else ''
    html = (head + '<style>' + css + '</style>\n' + json_ld(p).replace('"@/', '"' + root) + '\n' + top + main + bottom
            + page_js + '\n' + loader + form_js(p) + (ROAD_JS if 'id="nbRoad"' in main else '') + extra_js
            + '</body>\n</html>\n')
    out = ROOT / p['out']
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print('ok', out.relative_to(ROOT), len(html) // 1024, 'КБ')


def main():
    tpl = (ROOT / 'pishchevoe-proizvodstvo' / 'index.html').read_text(encoding='utf-8')
    icons = json.loads((ROOT / 'tools' / 'site' / 'icons.json').read_text(encoding='utf-8'))
    icons.update(json.loads((HERE / 'icons-nb.json').read_text(encoding='utf-8')))  # иконки, которых нет в общем наборе
    for p in PAGES:
        build(p, tpl, icons)


if __name__ == '__main__':
    main()
