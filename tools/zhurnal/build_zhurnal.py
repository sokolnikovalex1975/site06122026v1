#!/usr/bin/env python3
"""v2: страница /materialy/zhurnal-pest-kontrolya/ (образец заполнения и шаблон-бланк журнала пест-контроля, оба PDF и совпадают лист в лист) и карточка в /materialy/.
Запуск: python3 build_zhurnal_v1.py <ROOT репозитория>
Шаблон оформления — dogovor-deratizatsiya-dezinsektsiya/index.html (общие шапка, меню, подвал, форма заявки, скрипты)."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
from typo import typo  # noqa: E402

CANONICAL_BASE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai'
PAGE_URL = f'{CANONICAL_BASE}/materialy/zhurnal-pest-kontrolya/'
TITLE = 'Журнал пест-контроля: образец, бланк и шаблон — ПЕСТКОНТРОЛЬ Центр'
DESC = 'Образец заполнения журнала пест-контроля и шаблон-бланк для печати в PDF. Форма из 9 разделов по СанПиН 3.3686-21 и ХАССП: точки контроля, осмотр ловушек, предписания.'
OG_TITLE = 'Журнал пест-контроля: образец заполнения и шаблон в PDF'
OG_ALT = 'Образец заполнения и шаблон журнала пест-контроля ПЕСТКОНТРОЛЬ Центр: титульные листы'
F_SAMPLE = 'obrazets-zhurnala-pest-kontrolya.pdf'
F_TEMPLATE = 'shablon-zhurnala-pest-kontrolya.pdf'
V = '20261106j'

SANPIN_URL = 'http://pravo.gov.ru/proxy/ips/?docbody=&nd=602107773'

FAQS = [
    ('Есть ли утверждённая форма журнала пест-контроля?',
     'Единой государственной формы нет. СанПиН 3.3686-21 требует учитывать численность вредителей, контролировать эффективность истребительных мероприятий и вести производственный контроль за их объёмом и качеством (пп. 82, 99, 114), а форму записей определяет программа пест-контроля объекта и договор с подрядчиком. Поэтому журнал разных компаний выглядит по-разному. Наша форма из 9 разделов закрывает и требования санитарных правил, и то, что смотрят аудиторы ХАССП, ISO 22000 и FSSC 22000.'),
    ('Где скачать образец, бланк и шаблон журнала пест-контроля?',
     'На этой странице, бесплатно и без регистрации, два PDF-файла: образец заполнения на 10 листов (журнал пекарни за сентябрь–октябрь) и шаблон — тот же журнал без записей, он же бланк для печати. Файлы совпадают лист в лист, поэтому свой журнал удобно заполнять, глядя в образец. Листы визитов, поточечного осмотра и предписаний печатайте в нужном количестве, а номера листов проставьте при прошивке.'),
    ('Журнал пест-контроля и журнал учёта дератизации и дезинсекции — это одно и то же?',
     'По смыслу да, но журнал пест-контроля шире. Простой журнал учёта дератизации и дезинсекции фиксирует выезды и обработки. Журнал пест-контроля дополнительно ведёт мониторинг вредителей по каждой точке контроля, учёт насекомых по видам, предписания и анализ тенденций — это нужно для ХАССП и аудитов. Ведомость визитов в нашей форме (раздел 4) одновременно служит журналом учёта дератизации и дезинсекции.'),
    ('Кто должен заполнять журнал пест-контроля — сотрудник предприятия или подрядчик?',
     'Результаты осмотров точек контроля, применённые средства и замечания вносит специалист подрядной организации в день визита. Ответственный сотрудник предприятия подписывает визит, отмечает выполнение предписаний и следит за сигнальным листом, куда персонал записывает наблюдения между визитами.'),
    ('Как часто нужно делать записи в журнале пест-контроля?',
     'Запись делается при каждом плановом и внеплановом визите. Для объектов из пункта 98 СанПиН 3.3686-21 — пищевая промышленность, общественное питание, хранение и реализация пищевой продукции, гостиницы, медицинские организации и другие — плановые обследования на насекомых проводятся не реже 2 раз в месяц (п. 101), а дератизация — по результатам ежемесячной оценки (п. 110). Внутренние стандарты сетей и аудиторов могут требовать чаще.'),
    ('Нужно ли прошивать, нумеровать и заверять журнал печатью?',
     'Прямого требования в санитарных правилах нет, но для бумажного журнала это обычная практика: листы нумеруют, журнал прошнуровывают, а на последней странице делают заверительную надпись с числом листов, подписями и печатями сторон. Так видно, что листы не заменяли и не вклеивали задним числом.'),
    ('Чем журнал пест-контроля отличается от акта выполненных работ?',
     'Акт подтверждает конкретный выезд: перечень работ, расход средств, основание для оплаты, в том числе по ЭДО. Журнал хранится на объекте и показывает непрерывную историю каждой точки контроля из месяца в месяц, предписания и их выполнение. Номера актов указываются в ведомости визитов журнала, поэтому документы легко сверить.'),
    ('Можно ли вести журнал пест-контроля в электронном виде?',
     'Санитарные правила не запрещают электронный учёт, а для учёта дезинфекции прямо допускают программные продукты (п. 94 СанПиН 3.3686-21). На практике на объекте держат бумажный журнал с подписями, а электронный отчёт с фото и трендами получает служба качества. Если ваш стандарт или торговая сеть принимает только электронные записи, проверьте, что в них видны дата, автор и подтверждение Заказчика.'),
    ('Что писать в журнале, если точка контроля заставлена паллетами или повреждена?',
     'Пустую клетку оставлять нельзя. В поточечном листе ставится код «Д» — нет доступа — или «Р» — повреждена и заменена, а в лист предписаний вносится причина и срок: например, освободить проход вдоль стены. На следующем визите отмечается, восстановлен ли доступ.'),
    ('Сколько хранить заполненные журналы пест-контроля?',
     'Единый срок в санитарных правилах не установлен: его задаёт внутренний порядок предприятия, программа пест-контроля или требования сети. Часто журналы, акты и план-схемы хранят не меньше трёхлетнего цикла сертификации системы пищевой безопасности, чтобы на ресертификационном аудите была видна история.'),
    ('Можно ли заказать у вас только оформление журнала без обслуживания?',
     'Нет. Мы не заполняем журналы без фактической работы на объекте. Образец и шаблон журнала можно бесплатно скачать на этой странице, а рабочий журнал со схемой точек, программой и полным комплектом документов мы заводим и ведём по договору после бесплатного обследования.'),
]

SCHEMA_GRAPH = {
    '@context': 'https://schema.org',
    '@graph': [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': f'{CANONICAL_BASE}/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Материалы', 'item': f'{CANONICAL_BASE}/materialy/'},
            {'@type': 'ListItem', 'position': 3, 'name': 'Журнал пест-контроля', 'item': PAGE_URL}]},
        {'@type': 'TechArticle', '@id': PAGE_URL + '#article', 'headline': OG_TITLE, 'description': DESC, 'inLanguage': 'ru-RU',
         'mainEntityOfPage': PAGE_URL, 'datePublished': '2026-11-06', 'dateModified': '2026-11-06',
         'image': f'{CANONICAL_BASE}/img/zhurnal-og.jpg',
         'about': ['журнал пест-контроля', 'дератизация', 'дезинсекция', 'ХАССП'],
         'author': {'@type': 'Organization', 'name': 'ПЕСТКОНТРОЛЬ Центр', 'url': f'{CANONICAL_BASE}/'},
         'publisher': {'@type': 'Organization', 'name': 'ПЕСТКОНТРОЛЬ Центр', 'legalName': 'ООО «Центр дезинфекционных услуг»', 'taxID': '7714462211',
                       'url': f'{CANONICAL_BASE}/', 'telephone': '+7-495-104-35-70', 'email': 'b2b@pestcontrol-center.ru',
                       'logo': {'@type': 'ImageObject', 'url': f'{CANONICAL_BASE}/img/zhurnal-og.jpg'}},
         'hasPart': [
             {'@type': 'DigitalDocument', 'name': 'Образец заполнения журнала пест-контроля (PDF, 10 листов)', 'encodingFormat': 'application/pdf', 'url': PAGE_URL + F_SAMPLE, 'inLanguage': 'ru-RU'},
             {'@type': 'DigitalDocument', 'name': 'Шаблон (бланк) журнала пест-контроля для печати (PDF, 10 листов)', 'encodingFormat': 'application/pdf', 'url': PAGE_URL + F_TEMPLATE, 'inLanguage': 'ru-RU'}]},
        {'@type': 'Service', 'name': 'Ведение журнала и документации пест-контроля по договору', 'serviceType': 'Пест-контроль, дератизация и дезинсекция для организаций по системе IPM и ХАССП',
         'provider': {'@type': 'Organization', 'name': 'ПЕСТКОНТРОЛЬ Центр', 'url': f'{CANONICAL_BASE}/', 'telephone': '+7-495-104-35-70'},
         'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}]},
        {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQS]},
    ],
}

EXTRA_CSS = """
html{scroll-behavior:auto}
.d-page .s{padding:clamp(64px,7vw,128px) 0;border-top:1px solid var(--line)}
.d-crumbs{font-size:14px;color:var(--t3);display:flex;flex-wrap:wrap;gap:8px;margin:0 0 clamp(20px,2.4vw,32px)}
.d-crumbs a{color:var(--t2)}
.d-crumbs a:hover{color:var(--t1)}
.p-hero{position:relative;overflow:hidden;padding:calc(clamp(68px,6vw,115px) + 28px) 0 clamp(56px,6vw,100px);background:radial-gradient(900px 520px at 82% 30%,rgba(124,134,255,.16),rgba(9,9,11,0) 70%)}
.p-hero-grid{display:grid;grid-template-columns:minmax(0,1.12fr) minmax(0,.88fr);gap:clamp(28px,4vw,72px);align-items:center}
.p-hero h1{font-size:clamp(38px,4.1vw,74px);line-height:1.06;letter-spacing:-.05em;font-weight:300;margin:16px 0 0}
.p-hero h1 .ln{display:block;padding:0 .08em .08em 0;margin-bottom:-.08em}
.p-hero h1 .ln>span{display:inline-block}
.p-def{font-size:clamp(16px,1.18vw,20px);line-height:1.62;color:var(--t2);margin:24px 0 0;max-width:660px}
.p-def strong{color:var(--t1);font-weight:500}
.d-ticks{list-style:none;padding:0;margin:24px 0 0;display:grid;gap:12px}
.d-ticks li{position:relative;padding-left:30px;line-height:1.52;color:var(--t1)}
.d-ticks li::before{content:"";position:absolute;left:2px;top:.45em;width:13px;height:7px;border-left:2px solid var(--acc);border-bottom:2px solid var(--acc);transform:rotate(-45deg)}
.d-btns{display:flex;flex-wrap:wrap;gap:12px;margin-top:28px}
.p-files{display:none;flex-wrap:wrap;gap:8px 18px;margin-top:16px;font-size:14px;color:var(--t3)}
.p-files a{color:var(--t2);text-decoration:underline;text-decoration-color:rgba(124,134,255,.5);text-underline-offset:4px}
.p-files a:hover{color:var(--t1)}
.p-stack{position:relative;justify-self:center;width:min(100%,430px);aspect-ratio:430/560}
.p-stack a{position:absolute;display:block;border-radius:10px;overflow:hidden;background:#fff;box-shadow:0 30px 70px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.08);transition:transform .5s var(--ease)}
.p-stack img{display:block;width:100%;height:auto}
.p-stack .s1{left:0;top:0;width:78%;z-index:2;transform:rotate(-2.5deg)}
.p-stack .s2{right:0;top:9%;width:70%;z-index:1;transform:rotate(4deg);opacity:.92}
.p-stack a:hover{transform:rotate(0) translateY(-4px)}
.p-stack-cap{position:absolute;left:4%;bottom:0;z-index:3;display:flex;gap:8px;flex-wrap:wrap}
.p-chip{font-size:12px;letter-spacing:.04em;padding:6px 11px;border-radius:99px;background:rgba(9,9,11,.86);border:1px solid var(--line2);color:var(--t1);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
.p-chip.y{background:var(--yel);border-color:var(--yel);color:#09090b;font-weight:600}
.p-toc{display:flex;flex-wrap:wrap;gap:8px;margin:clamp(28px,3vw,44px) 0 0;padding:0;list-style:none}
.p-toc a{display:inline-flex;gap:8px;align-items:center;padding:9px 14px;border:1px solid var(--line2);border-radius:99px;font-size:13.5px;color:var(--t2);background:rgba(255,255,255,.02);transition:border-color .2s,color .2s}
.p-toc a:hover{border-color:var(--acc);color:var(--t1)}
.p-toc b{font-family:var(--mono,monospace);font-size:11px;color:var(--acc);font-weight:500}
.p-dl{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.p-dl-card{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line2);border-radius:var(--r);overflow:hidden}
.p-dl-card.main{border-color:rgba(253,199,0,.45)}
.p-dl-img{display:block;background:linear-gradient(180deg,rgba(124,134,255,.1),rgba(124,134,255,0));padding:22px 22px 0;height:250px;overflow:hidden;border-bottom:1px solid var(--line2)}
.p-dl-img img{display:block;width:76%;max-width:260px;height:auto;margin:0 auto;border-radius:6px 6px 0 0;box-shadow:0 18px 40px rgba(0,0,0,.5);transition:transform .4s var(--ease)}
.p-dl-card:hover .p-dl-img img{transform:translateY(-4px)}
.p-dl-body{padding:clamp(20px,1.8vw,28px);display:flex;flex-direction:column;gap:10px;flex:1}
.p-dl-meta{display:flex;gap:8px;flex-wrap:wrap;font-size:12px;color:var(--t3);letter-spacing:.04em}
.p-dl-meta span{padding:3px 9px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid var(--line)}
.p-dl-meta span.f{color:var(--acc);border-color:rgba(124,134,255,.35)}
.p-dl-card h3{font-size:clamp(19px,1.4vw,23px);font-weight:400;letter-spacing:-.02em;margin:0}
.p-dl-card p{color:var(--t2);line-height:1.58;margin:0;font-size:15px}
.p-dl-card .btn{margin-top:auto;align-self:flex-start}
.f-checks{position:relative;padding:0 0 clamp(56px,6vw,110px)}
.f-check.panel{max-width:none}
.f-check-in{position:relative;z-index:1;display:grid;grid-template-columns:minmax(0,.88fr) minmax(0,1.12fr);gap:clamp(24px,4vw,72px);padding:clamp(24px,3vw,48px)}
.f-check-t{font-size:clamp(26px,2.5vw,44px);line-height:1.1;letter-spacing:-.04em;font-weight:300;margin:0}
.f-check-res{margin:20px 0 10px;color:var(--t2);font-size:15px}
.f-check-res b{font-size:clamp(38px,3.2vw,60px);font-weight:300;letter-spacing:-.04em;color:var(--acc);margin-right:6px;line-height:1;transition:color .3s}
.f-check-res.full b{color:var(--grn)}
.f-check-note{color:var(--t2);line-height:1.6;margin:0 0 24px;max-width:460px}
.f-check-list{list-style:none;margin:0;padding:0;display:grid;align-content:center;border-top:1px solid var(--line)}
.f-check-list li{border-bottom:1px solid var(--line)}
.f-check-list label{display:flex;gap:16px;align-items:flex-start;padding:15px 4px;cursor:pointer;font-size:clamp(15px,1.05vw,17.5px);line-height:1.46;color:var(--t2);transition:color .25s}
.f-check-list label:hover{color:var(--t1)}
.f-check-list input{appearance:none;-webkit-appearance:none;flex:none;width:24px;height:24px;margin:2px 0 0;border-radius:7px;border:1.4px solid var(--line2);background:rgba(255,255,255,.03) center/14px no-repeat;cursor:pointer;transition:background-color .25s,border-color .25s}
.f-check-list input:checked{background-color:var(--acc2);border-color:var(--acc);background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 14 14'%3E%3Cpath d='M2.5 7.5l3 3 6-7' fill='none' stroke='%23fff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")}
.f-check-list input:focus-visible{outline:2px solid var(--acc);outline-offset:3px}
.f-check-list input:checked+span{color:var(--t1)}
.f-check-list strong{color:var(--t1);font-weight:500}
.d-cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.d-cards.c4{grid-template-columns:repeat(4,minmax(0,1fr))}
.d-card{background:var(--card);border:1px solid var(--line2);border-radius:var(--r);padding:clamp(22px,2vw,32px)}
.d-card h3{font-size:clamp(19px,1.4vw,24px);font-weight:400;letter-spacing:-.02em;margin:0 0 12px}
.d-card p{color:var(--t2);line-height:1.6;margin:0}
.d-card p+p{margin-top:10px}
.d-card .f-num{font-size:clamp(20px,1.7vw,30px);line-height:1.1;letter-spacing:-.03em;font-weight:300;color:var(--acc);margin:0 0 14px}
.d-card a{color:var(--acc);text-decoration:underline;text-underline-offset:3px}
.f-req .d-card{border-top:2px solid rgba(124,134,255,.45)}
.d-split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,400px);gap:clamp(28px,4vw,72px);align-items:start}
.d-terms{list-style:none;counter-reset:t;padding:0;margin:0;border-top:1px solid var(--line2)}
.d-terms li{display:grid;grid-template-columns:44px minmax(0,.36fr) minmax(0,1fr);gap:16px;padding:18px 0;border-bottom:1px solid var(--line2);line-height:1.55}
.d-terms li::before{counter-increment:t;content:counter(t);color:var(--acc);font-family:var(--mono,monospace);font-size:13px}
.d-terms b{font-weight:500;color:var(--t1)}
.d-terms span{color:var(--t2)}
.d-terms span i{font-style:normal;color:var(--t3)}
.d-doc{display:grid;gap:14px;position:sticky;top:110px}
.d-doc-prev{display:block;border-radius:12px;overflow:hidden;border:1px solid var(--line2);background:#fff;box-shadow:0 18px 44px rgba(0,0,0,.45);transition:border-color .2s,transform .2s}
.d-doc-prev:hover{border-color:var(--acc);transform:translateY(-2px)}
.d-doc-prev img{display:block;width:100%;height:auto}
.d-small{font-size:13px;color:var(--t3);margin:0;line-height:1.5}
.d-tw{overflow-x:auto;-webkit-overflow-scrolling:touch;margin-top:24px;border:1px solid var(--line2);border-radius:var(--r);background:var(--card)}
.d-table{width:100%;border-collapse:collapse}
.d-table th,.d-table td{padding:14px 16px;text-align:left;border-bottom:1px solid var(--line);line-height:1.5;vertical-align:top;font-size:14.5px}
.d-table th{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--t3);font-weight:500;background:rgba(255,255,255,.02)}
.d-table tr:last-child td{border-bottom:0}
.d-table td:first-child{color:var(--t1);font-weight:500}
.d-table td:not(:first-child){color:var(--t2)}
.mx-t{min-width:760px}
.mx-t th,.mx-t td{text-align:center;padding:11px 10px;font-size:14px}
.mx-t th:first-child,.mx-t td:first-child,.mx-t th:nth-child(2),.mx-t td:nth-child(2){text-align:left}
.mx-t td.v{font-family:var(--mono,monospace);color:var(--t1)}
.mx-t td.hl{background:rgba(253,199,0,.12);color:var(--yel)}
.mx-t td.cr{background:rgba(253,164,175,.12);color:#fda4af}
.mx-t td.na{color:var(--t3)}
.p-legend{display:flex;flex-wrap:wrap;gap:8px 18px;margin:16px 0 0;padding:0;list-style:none;font-size:14px;color:var(--t2)}
.p-legend b{display:inline-block;min-width:30px;text-align:center;font-family:var(--mono,monospace);font-weight:500;color:var(--acc);border:1px solid rgba(124,134,255,.35);border-radius:6px;padding:1px 6px;margin-right:6px}
.p-subhead{font-size:clamp(20px,1.55vw,26px);font-weight:400;letter-spacing:-.02em;margin:44px 0 6px;color:var(--t1)}
.p-subhead.first{margin-top:8px}
.p-scroll{display:none;margin-top:14px}
.p-sublead{color:var(--t3);font-size:14px;margin:0;line-height:1.5}
.p-code{display:inline-block;font-family:var(--mono,monospace);font-size:12px;color:var(--acc);background:rgba(124,134,255,.12);border:1px solid rgba(124,134,255,.3);padding:2px 7px;border-radius:6px}
.p-ok{color:#34d399;font-weight:500}
.p-wip{color:var(--yel);font-weight:500}
.p-steps{list-style:none;counter-reset:st;margin:0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.p-steps li{counter-increment:st;position:relative;background:var(--card);border:1px solid var(--line2);border-radius:var(--r);padding:clamp(22px,2vw,30px) clamp(22px,2vw,30px) clamp(22px,2vw,30px) 76px}
.p-steps li::before{content:counter(st,decimal-leading-zero);position:absolute;left:24px;top:22px;font-family:var(--mono,monospace);font-size:14px;color:var(--acc);border:1px solid rgba(124,134,255,.4);border-radius:8px;padding:4px 7px}
.p-steps h3{font-size:clamp(18px,1.3vw,21px);font-weight:400;letter-spacing:-.02em;margin:0 0 8px}
.p-steps p{color:var(--t2);line-height:1.6;margin:0;font-size:15px}
.p-secs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.p-sec{background:var(--card);border:1px solid var(--line2);border-radius:var(--r);padding:clamp(22px,2.2vw,32px)}
.p-sec-top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px}
.p-sec-num{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--yel);font-weight:500;padding:4px 10px;border-radius:99px;background:rgba(253,199,0,.1);border:1px solid rgba(253,199,0,.28)}
.p-sec-who{font-size:12px;color:var(--t3);text-align:right}
.p-sec h3{font-size:clamp(18px,1.35vw,22px);font-weight:400;letter-spacing:-.02em;margin:0 0 10px;color:var(--t1)}
.p-sec h3 a,.p-sec h2 a{color:var(--t1)}
.p-sec h2.p-sec-h{font-size:clamp(18px,1.35vw,22px);font-weight:400;letter-spacing:-.02em;line-height:1.3;margin:0 0 10px;color:var(--t1)}
.p-sec h3 a:hover,.p-sec h2 a:hover{color:var(--acc)}
.p-sec p{color:var(--t2);line-height:1.6;margin:0;font-size:15px}
.p-sec .d-btns{margin-top:20px}
.p-obj{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}
.p-obj .d-card h3{font-size:clamp(18px,1.3vw,21px)}
.p-obj ul{list-style:none;padding:0;margin:14px 0 0;display:grid;gap:8px}
.p-obj li{position:relative;padding-left:18px;color:var(--t2);font-size:14.5px;line-height:1.5}
.p-obj li::before{content:"";position:absolute;left:2px;top:.6em;width:6px;height:6px;border-radius:50%;background:var(--acc)}
.d-cols2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:16px}
.d-chips{list-style:none;padding:0;margin:24px 0 0;display:flex;flex-wrap:wrap;gap:10px}
.d-chips a{display:inline-flex;align-items:center;gap:8px;padding:12px 18px;border:1px solid var(--line2);border-radius:99px;background:var(--card);color:var(--t1);font-size:14px;transition:border-color .2s,background .2s}
.d-chips a:hover{border-color:var(--acc);background:rgba(124,134,255,.08)}
.p-note{margin-top:24px;padding:18px 22px;border-left:2px solid var(--yel);background:rgba(253,199,0,.05);border-radius:0 12px 12px 0;color:var(--t2);line-height:1.6}
.p-note b{color:var(--t1);font-weight:500}
@media (max-width:1180px){.p-obj,.d-cards.c4{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:1100px){
  .p-hero-grid,.f-check-in,.d-split{grid-template-columns:minmax(0,1fr)}
  .d-doc{position:static;max-width:520px}
  .p-stack{width:min(100%,380px)}
}
@media (max-width:900px){
  .hdr{background:rgba(0,0,0,.72);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border-color:var(--line)}
  .d-cards,.p-secs,.d-cols2,.p-dl,.p-steps{grid-template-columns:minmax(0,1fr)}
  .p-dl-img{height:220px}
}
@media (max-width:860px){
  .p-hero{padding:76px 0 36px}
  .p-hero-copy{display:flex;flex-direction:column}
  .p-hero-copy .eyebrow{order:1;font-size:11px}
  .p-hero-copy h1{order:2;font-size:clamp(30px,8vw,40px);line-height:1.06;margin-top:8px}
  .p-hero-copy .p-def{order:3;font-size:14px;line-height:1.48;margin-top:12px}
  .p-hero-copy .d-btns{order:4;margin-top:14px}
  .p-hero-copy .p-files{display:flex;order:5;margin-top:12px;font-size:13px}
  .p-hero-copy .d-ticks{order:6;margin-top:14px;gap:8px;font-size:14px}
  .p-hero-copy .d-ticks li{line-height:1.42;padding-left:26px}
  .p-hero-copy .d-crumbs{order:7;margin:14px 0 0;font-size:11px;line-height:1.3;gap:5px;color:rgba(255,255,255,.38);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .p-hero-copy .d-crumbs a{color:rgba(255,255,255,.46)}
  .p-hero-copy .p-btn-sec{display:none}
  .p-stack{width:min(86%,320px);margin-top:8px}
  .p-toc{display:none}
  .p-scroll{display:block}
  .p-scroll+.d-tw{margin-top:8px}
  .d-terms li{grid-template-columns:30px minmax(0,1fr);gap:6px 12px}
  .d-terms span{grid-column:2}
  .p-obj,.d-cards.c4{grid-template-columns:minmax(0,1fr)}
  .p-steps li{padding-left:22px;padding-top:62px}
  .p-steps li::before{left:22px;top:20px}
  .d-table.st,.d-table.st tbody,.d-table.st tr,.d-table.st td{display:block;width:100%}
  .d-table.st thead{display:none}
  .d-table.st tr{padding:16px 18px;border-bottom:1px solid var(--line)}
  .d-table.st td{padding:6px 0;border:0}
  .d-table.st td::before{content:attr(data-l);display:block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--t3);margin-bottom:2px}
}
@media (max-width:600px){
  .d-btns .btn,.f-check .btn,.d-doc .btn,.p-dl-card .btn{width:100%;white-space:normal;text-align:center;line-height:1.25}
  .d-page .btn-lg{padding:0 16px}
  .f-check-in{padding:24px 20px}
  .p-dl-img{height:200px}
}
@media (max-width:400px){
  .hdr .wrap{gap:10px}.hdr-right{gap:8px}.logo{gap:8px}.logo-mark{width:34px;height:34px}.logo-name{font-size:15px}.phone i,.burger{width:40px;height:40px}
}
@media (max-width:340px){.logo-sub{display:none}}
""".strip()


def build_faq_html():
    mid = (len(FAQS) + 1) // 2
    out = ['<div class="faq">']
    idx = 1
    for col in (FAQS[:mid], FAQS[mid:]):
        out.append('<div class="faq-col">')
        for q, a in col:
            out.append(f'<div class="card qa"><button aria-expanded="false" aria-controls="a{idx}" id="q{idx}">{q}<span class="pm"></span></button>'
                       f'<div class="ans" id="a{idx}" role="region" aria-labelledby="q{idx}"><div><p>{a}</p></div></div></div>')
            idx += 1
        out.append('</div>')
    out.append('</div>')
    return ''.join(out)


IMG = '../../img/'

MX_ROWS = [
    ('КИК-03', 'Площадка ТКО', ['П25/З', 'П10', '0', '—', '0'], {0: 'hl'}),
    ('КИК-05', 'Отмостка восточной стены', ['0', 'П50/З', 'П20/З', '—', 'П5'], {1: 'cr'}),
    ('МЛ-04', 'Экспедиция, у ворот № 2', ['0', 'Д', '0', '—', '0'], {1: 'hl'}),
    ('МЛ-10', 'Склад сырья, стеллаж А-2', ['0', '0', '0', 'М1/З', '0'], {3: 'cr'}),
    ('ИМ-03', 'Моечное отделение цеха', ['0', '0/З', 'Н2', '—', '0/З'], {2: 'cr'}),
    ('ИЛ-01', 'Экспедиция, над входом из цеха', ['Н14', 'Н11/З', 'Н7', '—', 'Н4/З'], {}),
    ('ФЛ-01', 'Склад муки, стеллаж Б-1', ['Н2', 'Н1', '0', '0', '0'], {0: 'hl'}),
]


def mx_table():
    head = '<tr><th scope="col">№ ТПК</th><th scope="col">Место установки</th>' + ''.join(
        f'<th scope="col">{d}</th>' for d in ['16.09', '30.09', '14.10', '21.10 <span class="nw">(внепл.)</span>', '28.10']) + '</tr>'
    rows = ''
    for code, place, vals, hl in MX_ROWS:
        tds = ''
        for i, v in enumerate(vals):
            cls = 'v' + (' ' + hl[i] if i in hl else '') + (' na' if v == '—' else '')
            tds += f'<td class="{cls}">{v}</td>'
        rows += f'<tr><td><span class="p-code">{code}</span></td><td>{place}</td>{tds}</tr>'
    return f'<p class="d-small p-scroll">Таблицу можно прокрутить вправо →</p><div class="d-tw"><table class="d-table mx-t"><thead>{head}</thead><tbody>{rows}</tbody></table></div>'


MAIN_HTML = f"""
<section class="p-hero" id="hero">
  <div class="wrap">
    <div class="p-hero-grid">
      <div class="p-hero-copy">
        <nav class="d-crumbs" aria-label="Навигационная цепочка"><a href="../../">Главная</a><span aria-hidden="true">→</span><a href="../">Материалы</a><span aria-hidden="true">→</span><span aria-current="page">Журнал пест-контроля</span></nav>
        <div class="eyebrow">Материалы · Документы IPM и ХАССП</div>
        <h1><span class="ln"><span>Журнал <span class="nw">пест-контроля:</span></span></span> <span class="ln"><span>образец заполнения,</span></span> <span class="ln"><span><em>бланк и шаблон</em></span></span></h1>
        <p class="p-def"><strong>Журнал пест-контроля</strong> — рабочий документ объекта, где по каждой пронумерованной точке контроля записывают результат осмотра, применённые средства, находки вредителей и выполнение предписаний. Ниже — готовая форма из 9 разделов: образец заполнения на примере пекарни и шаблон-бланк для печати. Оба файла в PDF и совпадают лист в лист.</p>
        <div class="d-btns">
          <a href="{F_SAMPLE}" class="btn btn-w btn-lg" target="_blank" rel="noopener" data-dl="obrazets"><span class="btn-t">Скачать образец заполнения, PDF</span></a>
          <a href="{F_TEMPLATE}" class="btn btn-o btn-lg p-btn-sec" target="_blank" rel="noopener" data-dl="shablon"><span class="btn-t">Скачать шаблон, PDF</span></a>
        </div>
        <p class="p-files"><a href="{F_TEMPLATE}" target="_blank" rel="noopener" data-dl="shablon">Шаблон журнала для печати, PDF</a></p>
        <ul class="d-ticks">
          <li>Образец и шаблон совпадают лист в лист — свой журнал удобно заполнять по образцу</li>
          <li>Учитывает СанПиН 3.3686-21 и то, что смотрят аудиторы ХАССП, ISO 22000 и FSSC 22000</li>
          <li>Рабочий журнал заводим и ведём на объекте с первого визита по договору</li>
        </ul>
      </div>
      <div class="p-stack" aria-label="Страницы образца журнала">
        <a href="{F_SAMPLE}" class="s1" target="_blank" rel="noopener" aria-label="Открыть образец журнала пест-контроля, PDF"><img src="{IMG}zhurnal-obrazets-p1-360.webp" srcset="{IMG}zhurnal-obrazets-p1-360.webp 360w, {IMG}zhurnal-obrazets-p1-720.webp 720w" sizes="(max-width:860px) 260px, 340px" width="360" height="509" decoding="async" alt="Титульный лист образца журнала пест-контроля ПЕСТКОНТРОЛЬ Центр с реквизитами исполнителя и составом разделов"></a>
        <a href="{F_SAMPLE}" class="s2" target="_blank" rel="noopener" tabindex="-1" aria-hidden="true"><img src="{IMG}zhurnal-obrazets-p8-360.webp" srcset="{IMG}zhurnal-obrazets-p8-360.webp 360w, {IMG}zhurnal-obrazets-p8-720.webp 720w" sizes="(max-width:860px) 230px, 300px" width="360" height="509" loading="lazy" decoding="async" alt=""></a>
        <div class="p-stack-cap"><span class="p-chip y">Образец заполнения</span><span class="p-chip">10 листов · 9 разделов</span></div>
      </div>
    </div>
    <ol class="p-toc" aria-label="Содержание страницы">
      <li><a href="#skachat"><b>01</b>Скачать образец и шаблон</a></li>
      <li><a href="#forma"><b>02</b>Форма: 9 разделов</a></li>
      <li><a href="#obrazets"><b>03</b>Образец заполнения</a></li>
      <li><a href="#kak-vesti"><b>04</b>Как вести журнал</a></li>
      <li><a href="#obekty"><b>05</b>Ресторан, склад, производство</a></li>
      <li><a href="#oshibki"><b>06</b>Ошибки</a></li>
      <li><a href="#normy"><b>07</b>Нормативная база</a></li>
      <li><a href="#voprosy"><b>08</b>Вопросы</a></li>
    </ol>
  </div>
</section>

<section class="s" id="skachat">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Бесплатно, без регистрации</div>
      <h2>Скачать журнал <span class="nw">пест-контроля:</span> <em>образец, бланк и шаблон</em></h2>
      <p class="sub">Два файла одной формы, совпадают лист в лист. Образец показывает, как выглядят правильные записи за два месяца работы. Шаблон — тот же журнал без записей: его печатают и заполняют от руки.</p>
    </div>
    <div class="p-dl">
      <article class="p-dl-card main">
        <a class="p-dl-img" href="{F_SAMPLE}" target="_blank" rel="noopener" tabindex="-1" aria-hidden="true"><img src="{IMG}zhurnal-obrazets-p1-360.webp" srcset="{IMG}zhurnal-obrazets-p1-360.webp 360w, {IMG}zhurnal-obrazets-p1-720.webp 720w" sizes="260px" width="360" height="509" loading="lazy" decoding="async" alt=""></a>
        <div class="p-dl-body">
          <div class="p-dl-meta"><span class="f">PDF</span><span>10 листов</span><span>A4</span></div>
          <h3>Образец заполнения журнала <span class="nw">пест-контроля</span></h3>
          <p>Заполненный журнал пекарни за сентябрь–октябрь: 30 точек контроля, поточечные отметки, находки грызунов и тараканов, предписания и их выполнение, сигналы персонала, сводка за месяц.</p>
          <a href="{F_SAMPLE}" class="btn btn-w btn-lg" target="_blank" rel="noopener" data-dl="obrazets"><span class="btn-t">Скачать образец, PDF</span></a>
        </div>
      </article>
      <article class="p-dl-card">
        <a class="p-dl-img" href="{F_TEMPLATE}" target="_blank" rel="noopener" tabindex="-1" aria-hidden="true"><img src="{IMG}zhurnal-shablon-p1-360.webp" srcset="{IMG}zhurnal-shablon-p1-360.webp 360w, {IMG}zhurnal-shablon-p1-720.webp 720w" sizes="260px" width="360" height="509" loading="lazy" decoding="async" alt=""></a>
        <div class="p-dl-body">
          <div class="p-dl-meta"><span class="f">PDF</span><span>10 листов</span><span>для печати</span></div>
          <h3>Шаблон и бланк журнала <span class="nw">пест-контроля</span></h3>
          <p>Тот же журнал из 9 разделов без записей, с разлинованными таблицами. Листы визитов, поточечного осмотра и предписаний распечатайте в нужном количестве, затем пронумеруйте и прошнуруйте журнал.</p>
          <a href="{F_TEMPLATE}" class="btn btn-o btn-lg" target="_blank" rel="noopener" data-dl="shablon"><span class="btn-t">Скачать шаблон, PDF</span></a>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="f-checks" id="samoproverka" aria-labelledby="chk-t">
  <div class="wrap">
    <div class="panel f-check">
      <div class="panel-scan" aria-hidden="true"></div>
      <div class="f-check-in">
        <div class="f-check-l">
          <div class="eyebrow">Проверка за 2 минуты</div>
          <h2 id="chk-t" class="f-check-t">Пройдёт ли ваш журнал <span class="nw">пест-контроля</span> проверку</h2>
          <p class="f-check-res"><b id="chk-n">0</b> из 6</p>
          <p class="f-check-note" id="chk-note" aria-live="polite">Отметьте, что уже есть в вашем журнале. Если чего-то не хватает — на бесплатном обследовании сверим журнал, схему и точки на объекте и покажем, что исправить до проверки.</p>
          <a href="#zayavka" class="btn btn-w btn-lg"><span class="btn-t">Проверить журнал на объекте</span></a>
        </div>
        <ul class="f-check-list">
          <li><label><input type="checkbox"><span><strong>Титульный лист заполнен:</strong> объект и адрес, номер договора, реквизиты и лицензия подрядчика, ответственные с обеих сторон, дата начала журнала</span></label></li>
          <li><label><input type="checkbox"><span><strong>Учёт по каждой точке:</strong> запись идёт по номеру точки контроля с план-схемы, а не одной строкой «обработка проведена»</span></label></li>
          <li><label><input type="checkbox"><span><strong>Нет пустых клеток:</strong> при отсутствии находок стоит «0», при отсутствии доступа — отметка и причина</span></label></li>
          <li><label><input type="checkbox"><span><strong>Средства с номерами СГР:</strong> наименование, действующее вещество, место применения и расход по каждому визиту</span></label></li>
          <li><label><input type="checkbox"><span><strong>Предписания закрыты:</strong> у каждого замечания есть ответственный, срок, отметка о выполнении и проверка подрядчиком</span></label></li>
          <li><label><input type="checkbox"><span><strong>Всё сходится:</strong> даты визитов совпадают с актами, номера точек — со схемой и указателями на стенах</span></label></li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="s" id="forma">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Структура документа</div>
      <h2>Форма журнала <span class="nw">пест-контроля:</span> <em>9 разделов и их графы</em></h2>
      <p class="sub">Так устроен бланк ПЕСТКОНТРОЛЬ Центра. В одном документе — журнал учёта дератизации и дезинсекции, журнал мониторинга вредителей и лист осмотра ловушек. Каждый раздел отвечает на вопрос проверяющего: что за объект, где стоят точки, чем работали, что нашли и что сделали.</p>
    </div>
    <div class="d-split">
      <ol class="d-terms">
        <li><b>Титульный лист и паспорт объекта</b><span>Объект, адрес, площади, зоны защиты, целевые вредители, кратность визитов, ответственные и контакты, график плановых визитов. <i>Реквизиты исполнителя и лицензия — на титуле.</i></span></li>
        <li><b>Реестр точек <span class="nw">пест-контроля</span> (ТПК)</b><span>№ точки, тип устройства, контур, место по план-схеме, дата установки, порог. <i>Отдельная таблица — изменения расстановки.</i></span></li>
        <li><b>Перечень средств и материалов</b><span>Наименование и форма, действующее вещество, СГР или декларация, где и как применяется, ограничения. <i>Подписи согласования обеих сторон.</i></span></li>
        <li><b>Ведомость визитов и расхода</b><span>Дата и время, вид визита, выполненные работы и результаты, средства и расход, № акта, подписи специалиста и Заказчика.</span></li>
        <li><b>Поточечный лист осмотра ТПК</b><span>Чек-лист осмотра ловушек: матрица «точка × дата визита» с кодами: 0, П%, М/К, С, Н, З, Д, Р. <i>Лист на 30 точек и 8 визитов.</i></span></li>
        <li><b>Учёт насекомых по видам</b><span>Дата, точка, вид и стадия, число особей, оценка к порогу, принятые меры. Вывод специалиста о динамике.</span></li>
        <li><b>Замечания и корректирующие действия</b><span>Что выявлено и почему это риск, рекомендация, ответственный и срок, отметка Заказчика о выполнении, проверка подрядчиком.</span></li>
        <li><b>Сигнальный лист и инструктажи</b><span>Что и где персонал увидел между визитами, кто сообщил и кому, отметка подрядчика. Учёт инструктажей сотрудников.</span></li>
        <li><b>Ежемесячная сводка и заверительная надпись</b><span>Визиты, число осмотров, активность грызунов и насекомых, предписания выдано/закрыто, оценка риска. Заверение листов подписями и печатями.</span></li>
      </ol>
      <div class="d-doc">
        <a href="{F_SAMPLE}" class="d-doc-prev" target="_blank" rel="noopener" aria-label="Открыть образец журнала пест-контроля, PDF"><img src="{IMG}zhurnal-obrazets-p6-480.webp" srcset="{IMG}zhurnal-obrazets-p6-480.webp 480w, {IMG}zhurnal-obrazets-p6-960.webp 960w" sizes="(max-width:1100px) 92vw, 400px" width="480" height="679" loading="lazy" decoding="async" alt="Поточечный лист осмотра 30 точек пест-контроля за 6 визитов с кодами отметок — лист 6 образца журнала"></a>
        <p class="d-small">Раздел 5 образца: поточечный лист осмотра. Маркером: жёлтым — достигнут порог, красным — превышение или отлов внутри здания.</p>
        <a href="{F_TEMPLATE}" class="btn btn-o btn-lg" target="_blank" rel="noopener" data-dl="shablon"><span class="btn-t">Скачать шаблон, PDF</span></a>
      </div>
    </div>
  </div>
</section>

<section class="s" id="obrazets">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Пример из образца</div>
      <h2>Образец заполнения журнала <em><span class="nw">пест-контроля</span></em></h2>
      <p class="sub">Фрагменты журнала пекарни: 30 точек контроля, визиты 2 раза в месяц, один внеплановый выезд по сигналу персонала. Видно не только находки, но и «нули», замены приманки и закрытые предписания.</p>
    </div>
    <h3 class="p-subhead first">Поточечный лист: 7 точек из 30 за пять визитов</h3>
    <p class="p-sublead">Каждая клетка — результат осмотра точки на конкретном визите. Через «/» — что сделал специалист.</p>
    {mx_table()}
    <ul class="p-legend">
      <li><b>0</b>находок нет</li><li><b>П25</b>съедено 25 % приманки</li><li><b>М1</b>отлов: 1 мышь</li><li><b>Н2</b>2 насекомых на клеевой поверхности</li><li><b>З</b>замена приманки или пластины</li><li><b>Д</b>нет доступа к точке</li><li><b>—</b>не входила во внеплановый визит</li>
    </ul>
    <h3 class="p-subhead">Лист предписаний: от находки до проверки</h3>
    <p class="p-sublead">Именно эту таблицу аудитор ХАССП смотрит, чтобы понять, работают ли корректирующие действия.</p>
    <div class="d-tw">
      <table class="d-table st">
        <thead><tr><th scope="col">№ и дата</th><th scope="col">Точка</th><th scope="col">Что выявлено</th><th scope="col">Рекомендация</th><th scope="col">Срок</th><th scope="col">Результат</th></tr></thead>
        <tbody>
          <tr><td data-l="№ и дата">№ 4 · 30.09</td><td data-l="Точка"><span class="p-code">КИК-05</span></td><td data-l="Что выявлено">2 норы у отмостки, строительный мусор</td><td data-l="Рекомендация">Засыпать и утрамбовать норы, вывезти мусор</td><td data-l="Срок">АХО, до 07.10</td><td data-l="Результат"><span class="p-ok">Выполнено 06.10.</span> На 14.10 новых нор нет, поедаемость снизилась с 50 до 20 %, к 28.10 — 5 %</td></tr>
          <tr><td data-l="№ и дата">№ 6 · 14.10</td><td data-l="Точка"><span class="p-code">ИМ-03</span></td><td data-l="Что выявлено">Рыжий таракан, 2 особи; отслоение герметика за моечной ванной, влага</td><td data-l="Рекомендация">Санобработка за ванной, герметизация шва; точечная обработка гелем</td><td data-l="Срок">Нач. цеха, до 21.10</td><td data-l="Результат"><span class="p-ok">Выполнено 20.10.</span> Контроль 28.10 — 0 особей, обработка эффективна</td></tr>
          <tr><td data-l="№ и дата">№ 7 · 21.10</td><td data-l="Точка"><span class="p-code">МЛ-10</span></td><td data-l="Что выявлено">Отлов мыши после сигнала кладовщика; ввод кабеля в стене не загерметизирован</td><td data-l="Рекомендация">Заделать отверстие металлической сеткой и герметиком</td><td data-l="Срок">Гл. инженер, до 28.10</td><td data-l="Результат"><span class="p-ok">Выполнено 27.10.</span> На 28.10 в МЛ-10 — 0</td></tr>
          <tr><td data-l="№ и дата">№ 8 · 28.10</td><td data-l="Точка"><span class="p-code">КИК-03</span></td><td data-l="Что выявлено">Крышки контейнеров ТКО не закрываются</td><td data-l="Рекомендация">Заменить контейнеры или крышки, держать закрытыми</td><td data-l="Срок">АХО, до 11.11</td><td data-l="Результат"><span class="p-wip">В работе</span> — проверка на визите 11.11</td></tr>
        </tbody>
      </table>
    </div>
    <div class="d-btns"><a href="{F_SAMPLE}" class="btn btn-w btn-lg" target="_blank" rel="noopener" data-dl="obrazets"><span class="btn-t">Открыть весь образец, 10 листов</span></a></div>
  </div>
</section>

<section class="s" id="kak-vesti">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Порядок записей</div>
      <h2>Как вести журнал <span class="nw">пест-контроля:</span> <em>6 правил</em></h2>
      <p class="sub">Правила напечатаны и на втором листе бланка, чтобы их видели все, кто открывает журнал.</p>
    </div>
    <ol class="p-steps">
      <li><h3>Запись — в день визита, на объекте</h3><p>Специалист заполняет журнал до ухода с объекта, представитель Заказчика подписывает визит. Записи «по памяти» через неделю — первое, что замечают проверяющие.</p></li>
      <li><h3>Каждая точка — под своим номером</h3><p>Номер в журнале совпадает с план-схемой и указателем на стене. Если точку перенесли, это отмечают в таблице изменений расстановки и обновляют схему.</p></li>
      <li><h3>Ноль — тоже результат</h3><p>«0» значит: точку осмотрели, находок нет. Пустая клетка читается как пропущенный осмотр. Нет доступа — код «Д» и запись в лист предписаний.</p></li>
      <li><h3>Средство — по перечню и с расходом</h3><p>Указывают номер средства из согласованного перечня, место и расход. Родентициды — только в запираемых станциях на территории, не в помещениях с открытой продукцией.</p></li>
      <li><h3>Находка — сразу в предписание</h3><p>Нора, щель под воротами, просыпи, влага: причина записывается с ответственным и сроком. Закрывают запись только после проверки на следующем визите.</p></li>
      <li><h3>Исправления — открыто</h3><p>Зачеркнуть одной линией, рядом верная запись, дата и подпись. Корректор, подчистки и вклеенные листы делают журнал недостоверным.</p></li>
    </ol>
  </div>
</section>

<section class="s" id="obekty">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Под тип объекта</div>
      <h2>Журнал <span class="nw">пест-контроля</span> для ресторана, склада <em>и пищевого производства</em></h2>
      <p class="sub">Форма одна, меняются набор точек, зоны и то, на что смотрит проверяющий. Все эти объекты входят в перечень пункта 98 СанПиН 3.3686-21, поэтому обследования на насекомых — не реже 2 раз в месяц.</p>
    </div>
    <div class="p-obj">
      <article class="d-card"><h3>Ресторан, кафе, столовая</h3><p>Компактный журнал на 10–20 точек: кухня, моечная, склад продуктов, зона приёма товара, мусорная площадка.</p><ul><li>Клеевые мониторы у моек и оборудования</li><li>Механические ловушки в подсобных помещениях</li><li>Сигнальный лист для поваров и вечерней смены</li></ul></article>
      <article class="d-card"><h3>Магазин и супермаркет</h3><p>Отдельные зоны для торгового зала, склада и дебаркадера: здесь вредители чаще всего приходят с товаром.</p><ul><li>Станции по периметру и у ворот приёмки</li><li>Феромонные ловушки у бакалеи</li><li>Отчёт по форме торговой сети</li></ul></article>
      <article class="d-card"><h3>Склад и распределительный центр</h3><p>Много точек по периметру здания и вдоль стен, где стоят паллеты: важно отмечать доступ к каждой.</p><ul><li>Код «Д» и предписание при заставленной точке</li><li>Контроль уплотнителей ворот и доков</li><li>Изменения расстановки после перепланировки</li></ul></article>
      <article class="d-card"><h3>Пищевое производство</h3><p>Журнал как часть системы ХАССП: пороги из программы <span class="nw">пест-контроля,</span> анализ тенденций, корректирующие действия.</p><ul><li>Контуры защиты: территория, периметр, цеха</li><li>Световые ловушки с учётом по видам</li><li>Ежемесячная сводка для службы качества</li></ul></article>
    </div>
  </div>
</section>

<section class="s" id="oshibki">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Что не проходит проверку</div>
      <h2>Ошибки в журнале <span class="nw">пест-контроля,</span> <em>которые находят на проверках</em></h2>
      <p class="sub">Проверяющий сверяет журнал со схемой точек, указателями на стенах и актами. Вот что чаще всего не сходится.</p>
    </div>
    <div class="p-secs">
      <article class="p-sec"><div class="p-sec-top"><span class="p-sec-num">Ошибка 01</span><span class="p-sec-who">Аудит ХАССП, торговая сеть</span></div><h3>Одна строка «обработка проведена»</h3><p>Если на объекте 30 точек контроля, по каждой должен быть виден результат. Общая фраза не показывает, что и где осматривали.</p></article>
      <article class="p-sec"><div class="p-sec-top"><span class="p-sec-num">Ошибка 02</span><span class="p-sec-who">ISO 22000, FSSC 22000</span></div><h3>Записаны только находки</h3><p>Пустые клетки читаются как пропущенный осмотр. «0» по каждой точке подтверждает, что специалист её проверил по графику.</p></article>
      <article class="p-sec"><div class="p-sec-top"><span class="p-sec-num">Ошибка 03</span><span class="p-sec-who">Обход цеха и склада</span></div><h3>Номера не совпадают со схемой</h3><p>Ловушку убрали при ремонте, а в журнале она по-прежнему «исправна». На обходе выборочную сверку точек со схемой делают почти всегда. Как вести схему и её редакции — на странице <a href="../skhema-tochek-pest-kontrolya/">схемы точек <span class="nw">пест-контроля</span></a>.</p></article>
      <article class="p-sec"><div class="p-sec-top"><span class="p-sec-num">Ошибка 04</span><span class="p-sec-who">Роспотребнадзор</span></div><h3>Нет названий, СГР и расхода</h3><p>«Разложена приманка» — не запись. Нужны наименование средства, действующее вещество, номер свидетельства о госрегистрации, место и расход.</p></article>
      <article class="p-sec"><div class="p-sec-top"><span class="p-sec-num">Ошибка 05</span><span class="p-sec-who">Служба качества</span></div><h3>Предписания без отметок о выполнении</h3><p>Одна и та же щель у ворот из месяца в месяц и пустая графа выполнения показывают, что корректирующие действия не работают.</p></article>
      <article class="p-sec"><div class="p-sec-top"><span class="p-sec-num">Ошибка 06</span><span class="p-sec-who">Любая проверка</span></div><h3>Журнал «восстановлен» перед проверкой</h3><p>Одна ручка, одинаковый почерк и даты, которые не совпадают с актами и пропусками охраны, выдают записи задним числом.</p></article>
    </div>
  </div>
</section>

<section class="s" id="normy">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Нормативная база</div>
      <h2>Что требует закон, <em>а что — стандарт пищевой безопасности</em></h2>
      <p class="sub">Единого утверждённого бланка журнала <span class="nw">пест-контроля</span> нет. Требования к содержанию записей складываются из санитарных правил, методических рекомендаций и стандартов, по которым работает предприятие.</p>
    </div>
    <div class="d-cards c4 f-req">
      <article class="d-card"><p class="f-num">СанПиН 3.3686-21</p><h3>Раздел III, пп. 98–124</h3><p>Перечень объектов особого эпидемиологического значения (п. 98), обследования на насекомых не реже 2 раз в месяц (п. 101), дератизация по ежемесячной оценке (п. 110), контроль эффективности (п. 114).</p><p><a href="{SANPIN_URL}" target="_blank" rel="noopener noreferrer">Текст на pravo.gov.ru</a></p></article>
      <article class="d-card"><p class="f-num">МР 3.5.3.0374-25</p><h3>Дератизация</h3><p>Методические рекомендации Роспотребнадзора 2025 года по организации и проведению дератизационных мероприятий: обследование, учёт численности грызунов, оценка эффективности.</p></article>
      <article class="d-card"><p class="f-num">ТР ТС 021/2011</p><h3>Статья 10</h3><p>Процедуры на принципах ХАССП на пищевом производстве, в том числе меры, которые не дают грызунам и насекомым попасть в производственные помещения.</p></article>
      <article class="d-card"><p class="f-num">ГОСТ Р 54762-2011</p><h3>Раздел 12</h3><p>Борьба с вредителями в программах предварительных требований: документированная программа, схема точек, записи мониторинга, анализ и корректирующие действия.</p></article>
    </div>
    <p class="p-note"><b>Что это значит для журнала.</b> Санитарные правила требуют учитывать численность вредителей, оценивать эффективность мер и вести производственный контроль за дезинфекционными работами (пп. 82, 99, 114). Форму записей вы выбираете сами — но проверяющий должен увидеть по ней каждую точку, каждый визит и каждое закрытое замечание. Сроки и критерии учёта до и после обработки — в разборе <a href="../../normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/" style="color:var(--acc);text-decoration:underline;text-underline-offset:3px">«Как оценивают эффективность дератизации и дезинсекции»</a>.</p>
  </div>
</section>

<section class="s" id="svyazka">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Папка пест-контроля</div>
      <h2>Журнал проверяют <em>вместе со всей папкой объекта</em></h2>
      <p class="sub">Рядом с журналом кладут договор, программу, план-схему и акты и сверяют даты, номера точек и названия средств. По договору мы ведём всю папку.</p>
    </div>
    <div class="d-tw">
      <table class="d-table st">
        <thead><tr><th scope="col">Документ</th><th scope="col">Что сверяют с журналом</th></tr></thead>
        <tbody>
          <tr><td data-l="Документ"><a href="../../dogovor-deratizatsiya-dezinsektsiya/" style="color:var(--acc);text-decoration:underline;text-underline-offset:3px">Договор на дератизацию и дезинсекцию</a></td><td data-l="Что сверяют">Адрес и площади объекта, кратность визитов, реквизиты и лицензия подрядчика на титуле журнала</td></tr>
          <tr><td data-l="Документ"><a href="../programma-pest-kontrolya/" style="color:var(--acc);text-decoration:underline;text-underline-offset:3px">Программа <span class="nw">пест-контроля</span></a></td><td data-l="Что сверяют">Целевые вредители, частота осмотров и пороги в реестре точек и поточечном листе</td></tr>
          <tr><td data-l="Документ">План-схема точек контроля</td><td data-l="Что сверяют">Количество, типы и нумерация точек, изменения расстановки</td></tr>
          <tr><td data-l="Документ">Акты и ежемесячный отчёт</td><td data-l="Что сверяют">Номер акта по каждому визиту в ведомости, анализ тенденций и закрытые предписания</td></tr>
        </tbody>
      </table>
    </div>
    <h3 class="p-subhead">Сколько стоит обслуживание с ведением журнала</h3>
    <div class="d-tw">
      <table class="d-table st">
        <thead><tr><th scope="col">Объект</th><th scope="col">Что входит</th><th scope="col">Ориентир</th></tr></thead>
        <tbody>
          <tr><td data-l="Объект">Кафе, ресторан, столовая</td><td data-l="Что входит">Контроль грызунов и насекомых, схема точек, объектовый журнал, копии СГР и акты</td><td data-l="Ориентир">от 3 500 ₽/мес</td></tr>
          <tr><td data-l="Объект">Магазин, супермаркет</td><td data-l="Что входит">Торговый зал, склад и дебаркадер, поточечный журнал, отчётность для сети</td><td data-l="Ориентир">от 3 500 ₽/мес</td></tr>
          <tr><td data-l="Объект">Склад до 1 000 м²</td><td data-l="Что входит">Периметр, доки и зоны хранения, журнал осмотров и предписаний</td><td data-l="Ориентир">от 4 500 ₽/мес</td></tr>
          <tr><td data-l="Объект">Пищевое производство</td><td data-l="Что входит">Программа, схема, поточечный учёт, анализ тенденций для ХАССП, ЭДО</td><td data-l="Ориентир">после бесплатного выезда</td></tr>
        </tbody>
      </table>
    </div>
    <div class="d-cols2">
      <div class="d-card"><h3>Журнал с первого визита</h3><p>Обследование объекта бесплатно. Проект договора с программой и расчётом присылаем в течение 1 часа после осмотра. На первом визите маркируем точки, передаём план-схему и заведённый журнал.</p></div>
      <div class="d-card"><h3>Смена подрядчика без пробела</h3><p>Принимаем объект с даты окончания прежнего договора: проверяем старые точки, обновляем схему и открываем новый журнал без перерыва в истории осмотров. Работаем с НДС и без НДС, по ЭДО и на бумаге.</p></div>
    </div>
    <ul class="d-chips">
      <li><a href="../../dogovor-deratizatsiya-dezinsektsiya/">Договор на дератизацию и дезинсекцию →</a></li>
      <li><a href="../programma-pest-kontrolya/">Программа пест-контроля: образец и шаблон →</a></li>
      <li><a href="../pest-menedzhment-ili-razovaya-obrabotka/">Пест-менеджмент или разовая обработка →</a></li>
      <li><a href="../../pishchevoe-proizvodstvo/">Пест-контроль на пищевом производстве →</a></li>
    </ul>
  </div>
</section>

<section class="s" id="voprosy">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Частые вопросы</div>
      <h2>Вопросы <em>о журнале <span class="nw">пест-контроля</span></em></h2>
    </div>
    {build_faq_html()}
  </div>
</section>
"""


def must_replace(s, old, new, count=1):
    assert old in s, f'Не найдено в шаблоне: {old[:90]}'
    return s.replace(old, new, count)


def build_page():
    tpl = (ROOT / 'dogovor-deratizatsiya-dezinsektsiya' / 'index.html').read_text(encoding='utf-8')
    s = tpl.replace('href="../', 'href="../../').replace('src="../', 'src="../../').replace('srcset="../', 'srcset="../../')
    s = re.sub(r'(imagesrcset|content)="\.\./', r'\1="../../', s)
    n0 = len(re.findall(r'<link rel="preload" as="image"[^>]*dogovor-hero[^>]*>', s))
    assert n0 == 2, n0
    s = re.sub(r'<link rel="preload" as="image"[^>]*dogovor-hero[^>]*>\n?', '', s)
    s = must_replace(s, '<link rel="preload" href="../../fonts/inter-ru-wght-normal.woff2" as="font" type="font/woff2" crossorigin>',
                     '<link rel="preload" href="../../fonts/inter-ru-wght-normal.woff2" as="font" type="font/woff2" crossorigin>\n'
                     '<link rel="preload" as="image" media="(min-width:861px)" imagesrcset="../../img/zhurnal-obrazets-p1-360.webp 360w, ../../img/zhurnal-obrazets-p1-720.webp 720w" imagesizes="340px" fetchpriority="high">')
    s, n = re.subn(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, flags=re.S); assert n == 1
    s, n = re.subn(r'(<meta name="description" content=")[^"]*', r'\g<1>' + DESC, s); assert n == 1
    s, n = re.subn(r'(<meta property="og:description" content=")[^"]*', r'\g<1>' + DESC, s); assert n == 1
    s, n = re.subn(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + OG_TITLE, s); assert n == 1
    s, n = re.subn(r'(<meta property="og:image" content=")[^"]*', r'\g<1>' + f'{CANONICAL_BASE}/img/zhurnal-og.jpg', s); assert n == 1
    s, n = re.subn(r'(<meta property="og:image:alt" content=")[^"]*', r'\g<1>' + OG_ALT, s); assert n == 1
    s, n = re.subn(r'(<meta property="og:type" content=")[^"]*', r'\g<1>article', s); assert n == 1
    assert 'name="robots" content="noindex' in s
    s = s.replace(f'{CANONICAL_BASE}/dogovor-deratizatsiya-dezinsektsiya/', PAGE_URL)
    s, n = re.subn(r'<style>.*?</style>', lambda m: f'<style>{EXTRA_CSS}</style>', s, count=1, flags=re.S); assert n == 1
    json_ld = json.dumps(SCHEMA_GRAPH, ensure_ascii=False, separators=(',', ':'))
    s, n = re.subn(r'<script type="application/ld\+json">.*?</script>', lambda m: f'<script type="application/ld+json">{json_ld}</script>', s, flags=re.S); assert n == 1
    # меню и подвал
    s = must_replace(s, '<a href="./" class="active" aria-current="page">Договор</a>', '<a href="../../dogovor-deratizatsiya-dezinsektsiya/">Договор</a>')
    s = s.replace('<a href="../../materialy/">Материалы</a>', '<a href="../../materialy/" class="active">Материалы</a>', 1)
    s = must_replace(s, '<a href="./" aria-current="page">Договор <small>', '<a href="../../dogovor-deratizatsiya-dezinsektsiya/">Договор <small>')
    s = re.sub(r'<li><a href="\./" aria-current="page">Договор на', '<li><a href="../../dogovor-deratizatsiya-dezinsektsiya/">Договор на', s)
    s = must_replace(s, '<li><a href="../../materialy/zhurnal-pest-kontrolya/"><span>Журнал', '<li><a href="./" aria-current="page"><span>Журнал')
    assert 'aria-current="page"' in s
    s, n = re.subn(r'(<a href="#zayavka" class="btn btn-w btn-sm"[^>]*><span class="btn-t">)[^<]*', r'\g<1>Проверить журнал', s); assert n == 1
    s, n = re.subn(r'(<nav class="mmenu"[^>]*>.*?<a href="#zayavka" class="btn btn-w btn-lg"><span class="btn-t">)[^<]*', r'\g<1>Бесплатное обследование', s, flags=re.S)
    main_typed = typo(MAIN_HTML.strip())
    s, n = re.subn(r'(<main id="main" tabindex="-1">).*?(<section class="cta" id="zayavka">)', lambda m: m.group(1) + '\n' + main_typed + '\n\n' + m.group(2), s, flags=re.S); assert n == 1
    cta_heading = typo('Проверим журнал <span class="nw">пест-контроля</span> <em>и заведём рабочий на вашем объекте</em>')
    cta_sub = typo('Бесплатно приедем на объект в Москве или области, сверим точки контроля, схему и журнал с требованиями СанПиН 3.3686-21 и ХАССП и пришлём проект договора с расчётом в течение 1 часа после осмотра.')
    s, n = re.subn(r'(<section class="cta" id="zayavka">.*?<h2>).*?(</h2>\s*<p class="sub">).*?(</p>)', lambda m: m.group(1) + cta_heading + m.group(2) + cta_sub + m.group(3), s, flags=re.S); assert n == 1
    s = must_replace(s, '<h3>Заявка на проект договора</h3>', '<h3>Заявка на бесплатное обследование</h3>')
    s, n = re.subn(r'<option value="" selected>Что нужно</option>(<option>[^<]*</option>)+',
                   '<option value="" selected>Какая задача</option><option>Пест-контроль с ведением журнала по договору</option><option>Проверить журнал и папку перед проверкой или аудитом</option><option>Сменить подрядчика без перерыва в журнале</option>', s); assert n == 1
    s, n = re.subn(r'(<button type="submit" class="btn btn-w btn-lg" id="submitBtn"><span class="btn-t">)[^<]*', r'\g<1>Заказать бесплатное обследование', s); assert n == 1
    s, n = re.subn(r'(<a href="#zayavka" class="c2"><span>)[^<]*', r'\g<1>Обследование', s); assert n == 1
    inline_js = """<script>
(function(){if(/^(www\\.)?xn----itbbsflddbfpfdodg9d0f\\.xn--p1ai$/i.test(location.hostname))return;var f=window.fetch;window.fetch=function(u){if(typeof u==='string'&&u.indexOf('send.php')>-1)return new Promise(function(r){setTimeout(function(){r(new Response('{"success":true}',{status:200,headers:{'Content-Type':'application/json'}}))},500)});return f.apply(this,arguments)};document.addEventListener('DOMContentLoaded',function(){var p=document.querySelector('.form .fs');if(p)p.textContent='Предпросмотр: заявка никуда не отправляется'})})();
document.addEventListener('change',function(e){if(!e.target.closest('.f-check-list'))return;var n=0;document.querySelectorAll('.f-check-list input').forEach(function(i){n+=i.checked?1:0});document.getElementById('chk-n').textContent=n;document.querySelector('.f-check-res').classList.toggle('full',n===6);document.getElementById('chk-note').textContent=n===6?'Все 6 пунктов на месте. На бесплатном обследовании проверим, совпадает ли журнал с точками в цехах и на складе.':'Отмечено '+n+' из 6. На бесплатном обследовании сверим журнал и схему и покажем, что исправить до проверки.'});
document.addEventListener('click',function(e){var a=e.target.closest('[data-dl]');if(!a)return;try{if(window.ym)ym(113675622,'reachGoal','zhurnal_'+a.getAttribute('data-dl'))}catch(_){}});
(function(){var f=document.getElementById('form');if(!f)return;f.addEventListener('submit',function(){var e=f.elements,s=e.service.value||'не выбрано',a=e.address.value.trim()||'не указан';e.msg.value='Задача: '+s+'\\nАдрес объекта: '+a+'\\nСтраница: Журнал пест-контроля (/materialy/zhurnal-pest-kontrolya/)';});})();
</script>"""
    s, n = re.subn(r"<script>\(function\(\)\{var f=document\.getElementById\('form'\).*?</script>", lambda m: inline_js, s, flags=re.S); assert n == 1
    out_dir = ROOT / 'materialy' / 'zhurnal-pest-kontrolya'
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'index.html').write_text(s, encoding='utf-8')
    print('Built page', len(s))
    return s


def build_hub(page):
    hub_url = f'{CANONICAL_BASE}/materialy/'
    hub_title = 'Материалы о пест-контроле для предприятий — ПЕСТКОНТРОЛЬ Центр'
    hub_desc = 'Руководства и образцы документов по пест-контролю для предприятий Москвы и области: журнал пест-контроля с образцом и бланком, пест-менеджмент или разовая обработка.'
    hub_main = typo(f"""
<section class="p-hero" id="hero">
  <div class="wrap">
    <nav class="d-crumbs" aria-label="Навигационная цепочка"><a href="../">Главная</a><span aria-hidden="true">→</span><span aria-current="page">Материалы</span></nav>
    <div class="eyebrow">Документы и практика IPM</div>
    <h1><span class="ln"><span>Материалы о <span class="nw">пест-контроле</span></span></span> <span class="ln"><span><em>для предприятий</em></span></span></h1>
    <p class="p-def">Разбираем, как устроены документы и работа по <span class="nw">пест-контролю</span> на пищевых производствах, складах, в ресторанах и магазинах: что требует СанПиН 3.3686-21, что смотрят аудиторы ХАССП, ISO 22000 и FSSC 22000.</p>
    <div class="p-secs" style="margin-top:36px">
      <article class="p-sec">
        <div class="p-sec-top"><span class="p-sec-num">Образец · бланк · шаблон</span><span class="p-sec-who">PDF</span></div>
        <h2 class="p-sec-h"><a href="./zhurnal-pest-kontrolya/">Журнал <span class="nw">пест-контроля:</span> образец заполнения, бланк и шаблон</a></h2>
        <p>Форма из 9 разделов: реестр точек контроля, поточечный лист осмотра, учёт насекомых, предписания, сигнальный лист персонала. Образец заполнения и шаблон-бланк на 10 листов, совпадают лист в лист.</p>
        <div class="d-btns"><a href="./zhurnal-pest-kontrolya/" class="btn btn-w btn-lg"><span class="btn-t">Открыть журнал и образец</span></a></div>
      </article>
      <article class="p-sec">
        <div class="p-sec-top"><span class="p-sec-num">Сравнение подходов</span><span class="p-sec-who">IPM</span></div>
        <h2 class="p-sec-h"><a href="./pest-menedzhment-ili-razovaya-obrabotka/"><span class="nw">Пест-менеджмент</span> или разовая обработка: в чём разница</a></h2>
        <p>Почему разовые выезды не заменяют постоянный контроль и чем отличаются результат, документы и стоимость для предприятия.</p>
        <div class="d-btns"><a href="./pest-menedzhment-ili-razovaya-obrabotka/" class="btn btn-o btn-lg"><span class="btn-t">Открыть материал</span></a></div>
      </article>
      <article class="p-sec">
        <div class="p-sec-top"><span class="p-sec-num">Готовится</span><span class="p-sec-who">ХАССП</span></div>
        <h2 class="p-sec-h">Программа <span class="nw">пест-контроля</span> на предприятии</h2>
        <p>Из каких разделов состоит программа, как оценивают <span class="nw">пест-риск</span> по зонам и как программа связана с журналом и схемой точек.</p>
      </article>
      <article class="p-sec">
        <div class="p-sec-top"><span class="p-sec-num">Готовится</span><span class="p-sec-who">Мониторинг</span></div>
        <h2 class="p-sec-h">Точки контроля вредителей на предприятии</h2>
        <p>Виды станций и ловушек, нумерация, маркировка и план-схема размещения.</p>
      </article>
    </div>
  </div>
</section>
""".strip())
    hs = page.replace('href="../../', 'href="../').replace('src="../../', 'src="../').replace('srcset="../../', 'srcset="../')
    hs = re.sub(r'(imagesrcset|content)="\.\./\.\./', r'\1="../', hs)
    hs = re.sub(r'<link rel="preload" as="image"[^>]*zhurnal-obrazets[^>]*>\n?', '', hs)
    hs = re.sub(r'<title>.*?</title>', f'<title>{hub_title}</title>', hs, flags=re.S)
    hs = re.sub(r'(<meta name="description" content=")[^"]*', r'\g<1>' + hub_desc, hs)
    hs = re.sub(r'(<meta property="og:description" content=")[^"]*', r'\g<1>' + hub_desc, hs)
    hs = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + hub_title, hs)
    hs = re.sub(r'(<meta property="og:type" content=")[^"]*', r'\g<1>website', hs)
    hs = hs.replace(PAGE_URL, hub_url)
    hub_ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': f'{CANONICAL_BASE}/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Материалы', 'item': hub_url}]},
        {'@type': 'CollectionPage', 'name': hub_title, 'description': hub_desc, 'url': hub_url, 'inLanguage': 'ru-RU',
         'hasPart': [{'@type': 'TechArticle', 'name': OG_TITLE, 'url': PAGE_URL},
                     {'@type': 'Article', 'name': 'Пест-менеджмент или разовая обработка', 'url': f'{CANONICAL_BASE}/materialy/pest-menedzhment-ili-razovaya-obrabotka/'}]}]}
    hs = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">' + json.dumps(hub_ld, ensure_ascii=False, separators=(',', ':')) + '</script>', hs, flags=re.S)
    hs = hs.replace('<li><a href="./" aria-current="page"><span>Журнал', '<li><a href="./zhurnal-pest-kontrolya/"><span>Журнал')
    hs = hs.replace('href="../materialy/zhurnal-pest-kontrolya/"', 'href="./zhurnal-pest-kontrolya/"')
    hs = hs.replace('<li><a href="../materialy/">Все материалы</a></li>', '<li><a href="./" aria-current="page">Все материалы</a></li>')
    hs = re.sub(r'(<main id="main" tabindex="-1">).*?(<section class="cta" id="zayavka">)', lambda m: m.group(1) + '\n' + hub_main + '\n\n' + m.group(2), hs, flags=re.S)
    hs = hs.replace("Страница: Журнал пест-контроля (/materialy/zhurnal-pest-kontrolya/)", "Страница: Материалы (/materialy/)")
    hs = hs.replace('<a href="#zayavka" class="btn btn-w btn-sm" data-magnet><span class="btn-t">Проверить журнал', '<a href="#zayavka" class="btn btn-w btn-sm" data-magnet><span class="btn-t">Обследование')
    (ROOT / 'materialy' / 'index.html').write_text(hs, encoding='utf-8')
    print('Built hub', len(hs))


def patch_hub():
    hub = ROOT / 'materialy' / 'index.html'
    h = hub.read_text(encoding='utf-8')
    k = h.find('href="./zhurnal-pest-kontrolya/"')
    assert k > 0, 'карточка журнала в разводящей не найдена'
    st = h.rfind('<article', 0, k); en = h.find('</article>', k) + len('</article>')
    class _M:
        def start(self): return st
        def end(self): return en
    old = _M()
    new = typo('''<article class="p-sec">
        <div>
          <div class="p-sec-top"><span class="p-sec-num">Материал 03 · Опубликован в превью</span><span class="p-sec-who">Образец и шаблон · PDF</span></div>
          <h3><a href="./zhurnal-pest-kontrolya/" style="color:var(--t1)">Журнал <span class="nw">пест-контроля:</span> образец заполнения, бланк и шаблон</a></h3>
          <p>Форма из 9 разделов: реестр точек контроля, поточечный лист осмотра ловушек, учёт насекомых, предписания и сигнальный лист персонала. Образец заполнения и шаблон-бланк на 10 листов, совпадают лист в лист.</p>
          <div class="d-btns" style="margin-top:20px"><a href="./zhurnal-pest-kontrolya/" class="btn btn-o btn-lg"><span class="btn-t">Открыть журнал и образец</span></a></div>
        </div>
      </article>''')
    h = h[:old.start()] + new + h[old.end():]
    hub.write_text(h, encoding='utf-8')
    print('Patched hub')


if __name__ == '__main__':
    build_page()
    if '--hub-new' in sys.argv:
        build_hub(build_page())
    else:
        patch_hub()
