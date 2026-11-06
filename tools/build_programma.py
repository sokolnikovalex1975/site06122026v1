#!/usr/bin/env python3
"""Генератор страницы /materialy/programma-pest-kontrolya/ и разводящей /materialy/ для превью pestcontrol-center-menu-V1-30102026."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
from typo import typo

CANONICAL_BASE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai'
PAGE_URL = f'{CANONICAL_BASE}/materialy/programma-pest-kontrolya/'
TITLE = 'Программа пест-контроля: образец и шаблон для предприятия — ПЕСТКОНТРОЛЬ Центр'
DESC = 'Образец программы пест-контроля на предприятии: скачать PDF и шаблон Word, форма из 7 разделов, пример заполнения плана мероприятий и расчёта пест-риска по ХАССП и СанПиН 3.3686-21.'
OG_TITLE = 'Программа пест-контроля: образец PDF, шаблон Word и пример заполнения'
OG_IMAGE_ALT = 'Специалист по пест-контролю и инженер по качеству сверяют программу и план-схему точек контроля в цехе'

FAQS = [
    (
        'Обязательна ли отдельная программа пест-контроля, если уже есть ППК и договор на дератизацию?',
        'В общей программе производственного контроля (ППК) борьбе с вредителями обычно отведена одна строка с кратностью обработок. Для пищевых производств, складов, торговых сетей и общепита, работающих по принципам ХАССП (ТР ТС 021/2011, ГОСТ Р ИСО 22000-2019, FSSC 22000), этого недостаточно: раздел 12 ГОСТ Р 54762-2011 требует документированной программы с перечнем целевых видов, оценкой пест-риска по зонам, картой пронумерованных точек контроля, пороговыми лимитами и анализом трендов.'
    ),
    (
        'Кто имеет право разрабатывать и подписывать программу пест-контроля?',
        'Программу разрабатывает профильный специалист службы пест-контроля (пест-менеджер, врач-дезинфектолог или биолог со специальной подготовкой) от организации, имеющей действующую лицензию Роспотребнадзора на дезинфекцию, дезинсекцию и дератизацию (обязательна с 1 марта 2025 года). Документ подписывается двумя сторонами — исполнителем и ответственным представителем заказчика.'
    ),
    (
        'Где скачать образец программы пест-контроля и можно ли его использовать?',
        'На этой странице образец программы пест-контроля можно скачать бесплатно — в PDF и как шаблон Word (DOCX). Он обезличен и показывает форму документа: паспорт объекта, целевые виды вредителей, расчёт пест-риска, план-схему точек, план мероприятий, реестр средств и подписи сторон. Для проверки Роспотребнадзора или аудита торговой сети шаблон заполняют по реальному объекту: без обследования, привязки к помещениям и номеров точек на схеме он остаётся формальной бумагой.'
    ),
    (
        'Есть ли шаблон программы пест-контроля в Word, чтобы заполнить самостоятельно?',
        'Да, рядом с PDF есть шаблон в формате DOCX с теми же разделами и приложениями; поля для заполнения отмечены подчёркиванием. Паспорт объекта и сведения об ответственных предприятие может внести само. Оценку пест-риска, план-схему точек, пороги численности и перечень средств заполняет специалист по пест-контролю после осмотра — этого ждут аудиторы ХАССП и стандарты IPM.'
    ),
    (
        'Чем программа пест-контроля по системе IPM отличается от графика обработок по договору ДДД?',
        'Обычный график ДДД фиксирует только даты приезда дезинфектора для раскладки приманки или опрыскивания. Программа по системе IPM (интегрированного пест-менеджмента) управляет риском: связывает инженерную герметизацию здания, санитарные обязанности персонала, нетоксичный мониторинг внутри цехов, количественные пороги численности и применение пестицидов строго по показаниям.'
    ),
    (
        'Как часто нужно пересматривать и обновлять программу пест-контроля?',
        'Плановая ревизия проводится не реже 1 раза в год вместе с анализом системы ХАССП со стороны руководства. Внепланово программа и план-схема точек обновляются при перепланировке или реконструкции цехов, запуске новых линий, смене сырья, а также при выявлении нового вида вредителя или устойчивом росте отлова в критических точках.'
    ),
    (
        'Какие документы входят в папку объекта вместе с программой пест-контроля?',
        'В рабочую папку входят: (1) утверждённая программа с оценкой пест-риска и планом мероприятий; (2) договор на обслуживание и копия лицензии Роспотребнадзора № Л064-00111-77/01942445; (3) сведения о квалификации специалистов; (4) цветные план-схемы здания и территории с точками контроля; (5) объектовый журнал осмотров ТПК и акты работ; (6) реестр средств с копиями СГР, инструкциями и паспортами безопасности; (7) ежемесячные отчёты с трендами и предписаниями.'
    ),
    (
        'Чем программа пест-контроля отличается от журнала пест-контроля?',
        'Программа — документ планирования: что, где, какими средствами и как часто контролируется, кто отвечает и какие пороги численности допустимы. Журнал пест-контроля — документ учёта: при каждом визите в нём фиксируют состояние каждой пронумерованной точки, найденных вредителей и следы, расход приманки и выполненные работы. Форму журнала утверждают в программе, а записи в журнале подтверждают, что программа выполняется.'
    ),
    (
        'Сколько времени занимает разработка программы и нужно ли платить за неё отдельно?',
        'Обследование объекта занимает 1–3 часа. Проект договора с расчётом точек и структурой программы мы направляем в течение 1 часа после осмотра, а выезд на установку и маркировку оборудования возможен от 3 часов. При заключении абонентского договора разработка программы, схемы точек и журналов входит в запуск обслуживания.'
    ),
]

SCHEMA_GRAPH = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{CANONICAL_BASE}/"},
                {"@type": "ListItem", "position": 2, "name": "Материалы", "item": f"{CANONICAL_BASE}/materialy/"},
                {"@type": "ListItem", "position": 3, "name": "Программа пест-контроля на предприятии", "item": PAGE_URL},
            ],
        },
        {
            "@type": "TechArticle",
            "headline": "Программа пест-контроля на предприятии: образец, форма и шаблон с примером заполнения",
            "image": f"{CANONICAL_BASE}/img/programma-og.jpg",
            "description": DESC,
            "inLanguage": "ru-RU",
            "mainEntityOfPage": PAGE_URL,
            "datePublished": "2026-11-06",
            "dateModified": "2026-11-06",
            "author": {
                "@type": "Organization",
                "name": "Методический отдел ПЕСТКОНТРОЛЬ Центр",
                "url": f"{CANONICAL_BASE}/"
            },
            "publisher": {
                "@type": "Organization",
                "name": "ПЕСТКОНТРОЛЬ Центр",
                "url": f"{CANONICAL_BASE}/",
                "telephone": "+7-495-104-35-70",
                "email": "b2b@pestcontrol-center.ru"
            }
        },
        {
            "@type": "DigitalDocument",
            "name": "Образец программы пест-контроля на предприятии (PDF, 6 страниц)",
            "encodingFormat": "application/pdf",
            "url": PAGE_URL + "obrazets-programmy-pest-kontrolya.pdf",
            "inLanguage": "ru-RU",
            "publisher": {"@type": "Organization", "name": "ПЕСТКОНТРОЛЬ Центр"}
        },
        {
            "@type": "DigitalDocument",
            "name": "Шаблон программы пест-контроля в Word (DOCX)",
            "encodingFormat": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "url": PAGE_URL + "shablon-programmy-pest-kontrolya.docx",
            "inLanguage": "ru-RU",
            "publisher": {"@type": "Organization", "name": "ПЕСТКОНТРОЛЬ Центр"}
        },
        {
            "@type": "Service",
            "name": "Разработка и внедрение программы пест-контроля на предприятии",
            "serviceType": "Пест-контроль и пест-менеджмент по системе IPM и ХАССП",
            "provider": {
                "@type": "Organization",
                "name": "ПЕСТКОНТРОЛЬ Центр",
                "url": f"{CANONICAL_BASE}/",
                "telephone": "+7-495-104-35-70"
            },
            "areaServed": [
                {"@type": "City", "name": "Москва"},
                {"@type": "AdministrativeArea", "name": "Московская область"}
            ]
        },
        {
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a}
                }
                for q, a in FAQS
            ]
        }
    ]
}

EXTRA_CSS = """
html{scroll-behavior:auto}
.d-page .s{padding:clamp(64px,7vw,128px) 0;border-top:1px solid var(--line)}
.d-crumbs{font-size:14px;color:var(--t3);display:flex;flex-wrap:wrap;gap:8px;margin:0 0 clamp(20px,2.4vw,32px)}
.d-crumbs a{color:var(--t2)}
.d-crumbs a:hover{color:var(--t1)}
.p-hero{position:relative;overflow:hidden;padding:calc(clamp(68px,6vw,115px) + 28px) 0 clamp(56px,6vw,108px);background:radial-gradient(900px 480px at 85% 22%,rgba(124,134,255,.14),rgba(9,9,11,0) 70%)}
.p-hero-grid{display:grid;grid-template-columns:minmax(0,1.08fr) minmax(0,.92fr);gap:clamp(28px,4vw,68px);align-items:start}
.p-hero h1{font-size:clamp(38px,4.2vw,76px);line-height:1.08;letter-spacing:-.05em;font-weight:300;margin:16px 0 0}
.p-hero h1 .ln{display:block;padding:0 .08em .08em 0;margin-bottom:-.08em}
.p-hero h1 .ln>span{display:inline-block}
.p-def{font-size:clamp(16px,1.18vw,20px);line-height:1.62;color:var(--t2);margin:24px 0 0;max-width:660px}
.p-def strong{color:var(--t1);font-weight:500}
.d-ticks{list-style:none;padding:0;margin:24px 0 0;display:grid;gap:12px}
.d-ticks li{position:relative;padding-left:30px;line-height:1.52;color:var(--t1)}
.d-ticks li::before{content:"";position:absolute;left:2px;top:.45em;width:13px;height:7px;border-left:2px solid var(--acc);border-bottom:2px solid var(--acc);transform:rotate(-45deg)}
.d-btns{display:flex;flex-wrap:wrap;gap:12px;margin-top:28px}
.p-doc-card{background:linear-gradient(180deg,rgba(24,24,29,.92),rgba(14,14,18,.96));border:1px solid var(--line2);border-top:2px solid var(--acc);border-radius:var(--r);padding:clamp(22px,2.4vw,34px);box-shadow:0 24px 60px rgba(0,0,0,.45)}
.p-doc-top{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-bottom:16px;border-bottom:1px solid var(--line)}
.p-doc-tag{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--acc);font-weight:500}
.p-doc-badge{font-size:12px;color:var(--yel);background:rgba(253,199,0,.1);border:1px solid rgba(253,199,0,.3);padding:4px 10px;border-radius:99px;white-space:nowrap}
.p-doc-title{font-size:clamp(19px,1.4vw,24px);font-weight:400;letter-spacing:-.02em;margin:16px 0 6px;color:var(--t1)}
.p-doc-sub{font-size:14px;color:var(--t3);margin:0 0 18px;line-height:1.5}
.p-doc-toc{list-style:none;padding:0;margin:0;display:grid;gap:8px}
.p-doc-toc li a{display:grid;grid-template-columns:32px minmax(0,1fr) auto;align-items:center;gap:10px;padding:10px 12px;border-radius:10px;background:rgba(255,255,255,.025);border:1px solid var(--line);color:var(--t2);font-size:14px;line-height:1.35;transition:border-color .2s,color .2s,background .2s}
.p-doc-toc li a:hover{border-color:var(--acc);color:var(--t1);background:rgba(124,134,255,.08)}
.p-doc-toc b{font-family:var(--mono,monospace);font-size:12px;color:var(--acc);font-weight:500}
.p-doc-toc i{font-style:normal;color:var(--t3);font-size:13px}
.p-doc-meta{margin-top:18px;padding-top:16px;border-top:1px solid var(--line);display:grid;gap:8px;font-size:13px;color:var(--t2);line-height:1.5}
.p-doc-meta span{color:var(--t3)}
.p-doc-meta a{color:var(--acc);text-decoration:underline;text-underline-offset:3px}
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
.f-check-list label{display:flex;gap:16px;align-items:flex-start;padding:16px 4px;cursor:pointer;font-size:clamp(15px,1.08vw,18px);line-height:1.48;color:var(--t2);transition:color .25s}
.f-check-list label:hover{color:var(--t1)}
.f-check-list input{appearance:none;-webkit-appearance:none;flex:none;width:24px;height:24px;margin:2px 0 0;border-radius:7px;border:1.4px solid var(--line2);background:rgba(255,255,255,.03) center/14px no-repeat;cursor:pointer;transition:background-color .25s,border-color .25s}
.f-check-list input:checked{background-color:var(--acc2);border-color:var(--acc);background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 14 14'%3E%3Cpath d='M2.5 7.5l3 3 6-7' fill='none' stroke='%23fff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")}
.f-check-list input:focus-visible{outline:2px solid var(--acc);outline-offset:3px}
.f-check-list input:checked+span{color:var(--t1)}
.f-check-list strong{color:var(--t1);font-weight:500}
.d-cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.d-card{background:var(--card);border:1px solid var(--line2);border-radius:var(--r);padding:clamp(22px,2vw,32px)}
.d-card h3{font-size:clamp(19px,1.4vw,24px);font-weight:400;letter-spacing:-.02em;margin:0 0 12px}
.d-card p{color:var(--t2);line-height:1.6;margin:0}
.d-card .f-num{font-size:clamp(24px,2.1vw,38px);line-height:1.1;letter-spacing:-.03em;font-weight:300;color:var(--acc);margin:0 0 14px}
.f-req .d-card{border-top:2px solid rgba(124,134,255,.45)}
.d-note{color:var(--t2);margin:24px 0 0;line-height:1.6}
.d-strong{color:var(--t1);font-size:clamp(17px,1.25vw,21px)}
.d-table{width:100%;border-collapse:collapse;border:1px solid var(--line2);border-radius:var(--r);overflow:hidden;background:var(--card);margin-top:28px}
.d-table th,.d-table td{padding:16px 20px;text-align:left;border-bottom:1px solid var(--line);line-height:1.52;vertical-align:top;font-size:15px}
.d-table th{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--t3);font-weight:500;background:rgba(255,255,255,.02)}
.d-table tr:last-child td{border-bottom:0}
.d-table td:first-child{color:var(--t1);font-weight:500}
.d-table td:not(:first-child){color:var(--t2)}
.d-vs td:first-child{color:var(--t2);font-weight:400}
.d-vs td:nth-child(2){color:var(--t2)}
.d-vs td:last-child,.d-vs th:last-child{background:rgba(124,134,255,.07);color:var(--t1)}
.p-secs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.p-sec{background:var(--card);border:1px solid var(--line2);border-radius:var(--r);padding:clamp(22px,2.2vw,32px);display:flex;flex-direction:column;justify-content:space-between}
.p-sec-wide{grid-column:1/-1;border-top:2px solid var(--acc)}
.p-sec-top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px}
.p-sec-num{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--acc);font-weight:500;padding:4px 10px;border-radius:99px;background:rgba(124,134,255,.1);border:1px solid rgba(124,134,255,.28)}
.p-sec-who{font-size:12px;color:var(--t3)}
.p-sec h3{font-size:clamp(19px,1.4vw,24px);font-weight:400;letter-spacing:-.02em;margin:0 0 12px;color:var(--t1)}
.p-sec p{color:var(--t2);line-height:1.62;margin:0;font-size:15px}
.p-sec ul{margin:12px 0 0;padding-left:18px;color:var(--t2);display:grid;gap:6px;font-size:14px;line-height:1.55}
.p-sec li strong{color:var(--t1);font-weight:500}
.p-formula{background:linear-gradient(135deg,rgba(124,134,255,.13),rgba(24,24,29,.92));border:1px solid rgba(124,134,255,.4);border-radius:var(--r);padding:clamp(24px,2.8vw,40px);margin-bottom:24px}
.p-formula-lbl{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--acc);margin-bottom:12px;display:block}
.p-formula-eq{font-size:clamp(20px,2vw,32px);font-weight:300;letter-spacing:-.02em;color:var(--t1);line-height:1.3;margin:0 0 20px}
.p-formula-eq em{font-style:normal;color:var(--yel);font-weight:400}
.p-formula-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.p-fcard{background:rgba(9,9,11,.65);border:1px solid var(--line2);border-radius:12px;padding:18px}
.p-fcard b{display:block;color:var(--t1);font-weight:500;margin-bottom:6px;font-size:15px}
.p-fcard span{color:var(--t2);font-size:14px;line-height:1.55;display:block}
.d-cols2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:16px}
.p-prp-card{border-top:2px solid var(--acc)}
.p-oprp-card{border-top:2px solid var(--yel)}
.p-badge-inline{display:inline-block;font-size:12px;letter-spacing:.06em;text-transform:uppercase;padding:3px 9px;border-radius:6px;margin-bottom:10px}
.p-b-acc{background:rgba(124,134,255,.14);color:var(--acc)}
.p-b-yel{background:rgba(253,199,0,.14);color:var(--yel)}
.p-plan-table th,.p-plan-table td{padding:14px 16px;font-size:14px}
.p-code{display:inline-block;font-family:var(--mono,monospace);font-size:12px;color:var(--acc);background:rgba(124,134,255,.12);border:1px solid rgba(124,134,255,.3);padding:2px 7px;border-radius:6px;margin-bottom:4px}
.p-risk-hi{color:var(--yel);font-weight:500}
.p-risk-cr{color:#fda4af;font-weight:500}
.p-risk-md{color:#93c5fd;font-weight:500}
.p-sample-box{display:grid;grid-template-columns:280px minmax(0,1fr);gap:clamp(24px,3.2vw,44px);align-items:center;background:linear-gradient(135deg,rgba(124,134,255,.1),rgba(24,24,29,.95));border:1px solid rgba(124,134,255,.35);border-radius:var(--r);padding:clamp(22px,2.8vw,38px);margin-bottom:28px}
.d-doc-prev{display:block;max-width:280px;border-radius:12px;overflow:hidden;border:1px solid var(--line2);background:#fff;box-shadow:0 18px 44px rgba(0,0,0,.45);transition:border-color .2s,transform .2s}
.d-doc-prev:hover{border-color:var(--acc);transform:translateY(-2px)}
.d-doc-prev img{display:block;width:100%;height:auto}
.p-sample-copy h3{font-size:clamp(20px,1.6vw,28px);font-weight:400;letter-spacing:-.02em;margin:0 0 12px;color:var(--t1)}
.p-sample-copy p{color:var(--t2);line-height:1.6;margin:0 0 16px;font-size:15px}
.p-sample-pages{list-style:none;padding:0;margin:0 0 22px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px 18px;font-size:14px;color:var(--t2)}
.p-sample-pages li{position:relative;padding-left:22px;line-height:1.45}
.p-sample-pages li::before{content:"";position:absolute;left:2px;top:.45em;width:10px;height:5px;border-left:2px solid var(--acc);border-bottom:2px solid var(--acc);transform:rotate(-45deg)}
.p-sample-pages b{color:var(--t1);font-weight:500}
.p-sample-actions{display:flex;flex-wrap:wrap;align-items:center;gap:14px}
.p-sample-meta{font-size:13px;color:var(--t3)}
.p-duties{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}
.p-duty-box{background:var(--card);border:1px solid var(--line2);border-radius:var(--r);padding:clamp(24px,2.4vw,36px)}
.p-duty-box.isp{border-top:2px solid var(--acc)}
.p-duty-box.zak{border-top:2px solid var(--yel)}
.p-duty-box h3{font-size:clamp(20px,1.5vw,26px);font-weight:400;margin:0 0 8px}
.p-duty-lead{color:var(--t3);font-size:14px;margin:0 0 20px;line-height:1.5}
.p-duty-list{list-style:none;padding:0;margin:0;display:grid;gap:14px}
.p-duty-list li{position:relative;padding-left:28px;color:var(--t2);line-height:1.55;font-size:15px}
.p-duty-list li strong{color:var(--t1);font-weight:500}
.p-duty-box.isp .p-duty-list li::before{content:"";position:absolute;left:2px;top:.48em;width:12px;height:6px;border-left:2px solid var(--acc);border-bottom:2px solid var(--acc);transform:rotate(-45deg)}
.p-duty-box.zak .p-duty-list li::before{content:"";position:absolute;left:4px;top:.55em;width:8px;height:8px;border-radius:50%;background:var(--yel)}
.d-steps{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;counter-reset:st}
.d-steps li{background:var(--card);border:1px solid var(--line2);border-top:2px solid var(--acc);border-radius:var(--r);padding:24px;counter-increment:st}
.d-steps li::before{content:"0" counter(st);display:block;font-size:13px;letter-spacing:.08em;color:var(--acc);margin-bottom:14px}
.d-steps b{display:block;font-size:19px;font-weight:400;margin-bottom:8px;color:var(--t1)}
.d-steps span{display:block;color:var(--t2);line-height:1.55;font-size:15px}
.d-chips{list-style:none;padding:0;margin:24px 0 0;display:flex;flex-wrap:wrap;gap:10px}
.d-chips a{display:inline-flex;align-items:center;gap:8px;padding:12px 18px;border:1px solid var(--line2);border-radius:99px;background:var(--card);color:var(--t1);font-size:14px;transition:border-color .2s,background .2s}
.d-chips a:hover{border-color:var(--acc);background:rgba(124,134,255,.08)}
.d-hero{position:relative;overflow:hidden;padding:calc(clamp(68px,6vw,115px) + 20px) 0 clamp(64px,7vw,116px);min-height:clamp(640px,52vw,860px);display:flex;align-items:center}
.d-hero .wrap{width:100%;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(28px,4vw,80px);align-items:center}
.d-hero-copy>*:not(.d-hero-media){position:relative;z-index:1}
.d-hero-media{position:absolute;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.d-hero-media::before{content:"";position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(0,0,0,.95) 0%,rgba(0,0,0,.86) 38%,rgba(0,0,0,.3) 55%,rgba(0,0,0,0) 66%),linear-gradient(180deg,#000 0,rgba(0,0,0,.55) 90px,rgba(0,0,0,0) 260px),linear-gradient(0deg,#000 0,rgba(0,0,0,0) 20%)}
.d-hero-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:100% 50%}
.d-hero h1{font-size:clamp(38px,4.1vw,76px);line-height:1.1;letter-spacing:-.055em;font-weight:300;margin:18px 0 0}
.d-hero h1 .ln{display:block;padding:0 .08em .08em 0;margin-bottom:-.08em}
.d-hero h1 .ln>span{display:inline-block}
.d-hero .p-def{margin-top:22px}
.p-hero-note{margin:14px 0 0;font-size:13px;color:var(--t3)}
.p-hero-note a{color:var(--t2);text-decoration:underline;text-underline-offset:3px}
.p-toc{border-top:1px solid var(--line);background:rgba(255,255,255,.015)}
.p-toc .wrap{display:flex;align-items:center;gap:10px;padding-top:16px;padding-bottom:16px;overflow-x:auto;scrollbar-width:none}
.p-toc .wrap::-webkit-scrollbar{display:none}
.p-toc b{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--t3);font-weight:500;white-space:nowrap;margin-right:4px}
.p-toc a{flex:0 0 auto;white-space:nowrap;padding:9px 14px;border:1px solid var(--line2);border-radius:99px;color:var(--t2);font-size:14px;transition:border-color .2s,color .2s}
.p-toc a:hover{border-color:var(--acc);color:var(--t1)}
.p-obr{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:clamp(24px,3.4vw,56px);align-items:start}
.p-obr-pages{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.p-obr-page{display:block;color:var(--t2);font-size:13px;line-height:1.4}
.p-obr-page span{display:block;border-radius:10px;overflow:hidden;border:1px solid var(--line2);background:#fff;box-shadow:0 14px 36px rgba(0,0,0,.45);transition:border-color .2s,transform .2s;margin-bottom:10px}
.p-obr-page img{display:block;width:100%;height:auto;aspect-ratio:720/1018}
.p-obr-page:hover span{border-color:var(--acc);transform:translateY(-2px)}
.p-obr-page b{display:block;color:var(--t1);font-weight:500}
.p-obr-info{background:var(--card);border:1px solid var(--line2);border-top:2px solid var(--acc);border-radius:var(--r);padding:clamp(22px,2.4vw,34px)}
.p-obr-info h3{font-size:clamp(19px,1.4vw,24px);font-weight:400;letter-spacing:-.02em;margin:0 0 14px;color:var(--t1)}
.p-obr-list{list-style:none;padding:0;margin:0 0 22px;display:grid;gap:10px;counter-reset:pg}
.p-obr-list li{display:grid;grid-template-columns:52px minmax(0,1fr);gap:10px;color:var(--t2);font-size:14px;line-height:1.5}
.p-obr-list li b{font-family:var(--mono,monospace);font-size:12px;color:var(--acc);font-weight:500;padding-top:2px}
.p-obr-btns{display:flex;flex-wrap:wrap;gap:12px}
.p-obr-meta{margin:14px 0 0;font-size:13px;color:var(--t3);line-height:1.5}
.p-obr-meta a{color:var(--t2);text-decoration:underline;text-underline-offset:3px}
.p-fig{margin:0;border-radius:var(--r);overflow:hidden;border:1px solid var(--line2);background:var(--card)}
.p-fig img{display:block;width:100%;height:auto;aspect-ratio:3/2;object-fit:cover}
.p-fig figcaption{padding:12px 16px;font-size:13px;color:var(--t3);line-height:1.5;border-top:1px solid var(--line)}
.p-fig-wide{margin:0 0 24px}
.p-fig-wide img{aspect-ratio:21/8;object-position:50% 60%}
.p-fill{display:grid;grid-template-columns:minmax(0,.95fr) minmax(0,1.05fr);gap:clamp(24px,3.4vw,56px);align-items:start}
.p-fill-steps{list-style:none;padding:0;margin:0;display:grid;gap:12px;counter-reset:fs}
.p-fill-steps li{position:relative;background:var(--card);border:1px solid var(--line2);border-radius:var(--r);padding:18px 20px 18px 64px;counter-increment:fs}
.p-fill-steps li::before{content:counter(fs);position:absolute;left:18px;top:16px;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;color:var(--acc);background:rgba(124,134,255,.12);border:1px solid rgba(124,134,255,.35)}
.p-fill-steps li>b{display:block;color:var(--t1);font-weight:500;font-size:16px;margin-bottom:4px}
.p-fill-steps li>span{display:block;color:var(--t2);font-size:14px;line-height:1.55}
.p-fill-side{position:sticky;top:96px;display:grid;gap:16px}
@media (max-width:1180px){.d-hero{min-height:0}.d-hero .wrap{grid-template-columns:minmax(0,.82fr) minmax(0,1.18fr)}.d-hero .btn-lg{height:52px;padding:0 22px;font-size:15px}}
@media (max-width:1100px){.p-obr,.p-fill{grid-template-columns:minmax(0,1fr)}.p-fill-side{position:static}}
@media (max-width:860px){
  .d-hero{display:block;min-height:0;padding:calc(clamp(68px,6vw,115px) + 20px) 0 clamp(36px,6vw,56px)}
  .d-hero .wrap{grid-template-columns:minmax(0,1fr)}
  .d-hero-copy{display:flex;flex-direction:column}
  .d-hero .eyebrow{display:none}
  .d-hero h1{order:1;font-size:clamp(28px,7.8vw,34px);line-height:1.08;margin:0}
  .d-hero h1 .ln{display:inline}
  .d-hero-media{order:2;position:relative;inset:auto;aspect-ratio:16/9;margin:18px calc(var(--pad) * -1) 0}
  .d-hero-media::before{display:none}
  .d-hero-img{height:100%;min-height:0}
  .d-hero .d-btns{order:3;margin-top:20px;gap:10px}
  .d-hero .p-hero-note{order:4}
  .d-hero .d-ticks{order:5;margin:22px 0 0;gap:9px;font-size:15px}
  .d-hero .p-def{order:6;margin:18px 0 0;font-size:15px;line-height:1.5}
  .d-hero .d-crumbs{order:7;margin:18px 0 0;font-size:11px;line-height:1.2;gap:6px;flex-wrap:nowrap;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;opacity:1;color:#8b8b93}
  .d-hero .d-crumbs a,.d-hero .d-crumbs span{color:#8b8b93}
  .p-toc .wrap{padding-top:12px;padding-bottom:12px}
  .p-toc a{padding:8px 12px;font-size:13px}
  .p-obr-pages{gap:10px}
  .p-obr-page{font-size:12px}
  .p-fig-wide img{aspect-ratio:4/3}
  .p-fill-steps li{padding:16px 16px 16px 58px}
  .p-fill-steps li::before{left:14px}
}
@media (max-width:600px){.p-obr-btns .btn{width:100%;white-space:normal;text-align:center;line-height:1.25}.p-obr-page b{font-size:12px}.p-obr-page small{display:none}}
@media (max-width:1100px){
  .p-hero-grid,.f-check-in,.p-duties{grid-template-columns:minmax(0,1fr)}
  .p-formula-grid{grid-template-columns:minmax(0,1fr)}
  .d-steps{grid-template-columns:repeat(2,minmax(0,1fr))}
}
@media (max-width:900px){
  .hdr{background:rgba(0,0,0,.72);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border-color:var(--line)}
  .d-cards,.p-secs,.d-cols2,.p-sample-box,.p-sample-pages{grid-template-columns:minmax(0,1fr)}
  .d-doc-prev{margin:0 auto;max-width:240px}
}
@media (max-width:860px){
  .p-hero{padding:76px 0 36px}
  .p-hero-copy{display:flex;flex-direction:column}
  .p-hero-copy .eyebrow{order:1;font-size:11px}
  .p-hero-copy h1{order:2;font-size:clamp(30px,8vw,40px);line-height:1.06;margin-top:8px}
  .p-hero-copy .p-def{order:3;font-size:14px;line-height:1.48;margin-top:12px}
  .p-hero-copy .d-btns{order:4;margin-top:14px}
  .p-hero-copy .p-btn-sec{display:none}
  .p-hero-copy .d-ticks{order:5;margin-top:14px;gap:8px;font-size:14px}
  .p-hero-copy .d-ticks li{line-height:1.42;padding-left:26px}
  .p-hero-copy .d-crumbs{order:6;margin:14px 0 0;font-size:11px;line-height:1.3;gap:5px;color:rgba(255,255,255,.38);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .p-hero-copy .d-crumbs a{color:rgba(255,255,255,.46)}
  .d-table,.d-table tbody,.d-table tr,.d-table td{display:block;width:100%}
  .d-table thead{display:none}
  .d-table tr{padding:16px 18px;border-bottom:1px solid var(--line)}
  .d-table td{padding:6px 0;border:0}
  .d-table td::before{content:attr(data-l);display:block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--t3);margin-bottom:2px}
  .d-vs td:last-child{padding:10px 12px;border-radius:8px;margin-top:6px}
}
@media (max-width:600px){
  .d-steps{grid-template-columns:minmax(0,1fr)}
  .d-btns .btn,.f-check .btn{width:100%;white-space:normal;text-align:center;line-height:1.25}
  .d-page .btn-lg{padding:0 16px}
  .f-check-in{padding:24px 20px}
}
@media (max-width:400px){
  .hdr .wrap{gap:10px}.hdr-right{gap:8px}.logo{gap:8px}.logo-mark{width:34px;height:34px}.logo-name{font-size:15px}.phone i,.burger{width:40px;height:40px}
}
@media (max-width:340px){.logo-sub{display:none}}
@media (max-width:480px){#submitBtn{padding:0 18px;gap:10px}#submitBtn .btn-t{white-space:normal;text-align:center;line-height:1.2}}
""".strip()

def build_faq_html():
    col1, col2 = [], []
    for idx, (q, a) in enumerate(FAQS, 1):
        card = (
            f'<div class="card qa">'
            f'<button aria-expanded="false" aria-controls="a{idx}" id="q{idx}">{q}<span class="pm"></span></button>'
            f'<div class="ans" id="a{idx}" role="region" aria-labelledby="q{idx}"><div><p>{a}</p></div></div>'
            f'</div>'
        )
        if idx <= (len(FAQS) + 1) // 2:
            col1.append(card)
        else:
            col2.append(card)
    return f'<div class="faq"><div class="faq-col">{"".join(col1)}</div><div class="faq-col">{"".join(col2)}</div></div>'

MAIN_HTML = f"""
<section class="d-hero" id="hero">
  <div class="wrap">
    <div class="d-hero-copy">
      <nav class="d-crumbs" aria-label="Навигационная цепочка"><a href="../../">Главная</a><span aria-hidden="true">→</span><a href="../">Материалы</a><span aria-hidden="true">→</span><span aria-current="page">Программа пест-контроля</span></nav>
      <div class="eyebrow">Материалы · Образец, форма и шаблон документа</div>
      <h1><span class="ln"><span>Программа</span></span> <span class="ln"><span><span class="nw">пест-контроля</span></span></span> <span class="ln"><span><em>на предприятии</em></span></span></h1>
      <div class="d-hero-media"><picture><source media="(max-width:860px)" srcset="../../img/programma-hero-mob-760.webp 760w, ../../img/programma-hero-mob.webp 1024w" sizes="100vw" width="1024" height="576"><img class="d-hero-img" src="../../img/programma-hero.webp" srcset="../../img/programma-hero-1440.webp 1440w, ../../img/programma-hero.webp 1920w" sizes="100vw" width="1920" height="1072" alt="Специалист по пест-контролю и инженер по качеству сверяют программу пест-контроля и план-схему точек в цехе пищевого производства" fetchpriority="high" decoding="async"></picture></div>
      <p class="p-def"><strong>Программа пест-контроля</strong> — рабочий документ системы IPM и плана ХАССП: целевые вредители объекта, оценка пест-риска по зонам, схема пронумерованных точек контроля (ТПК), пороги численности и обязанности предприятия и лицензированной службы.</p>
      <ul class="d-ticks">
        <li>Бесплатный образец программы пест-контроля — PDF на 6 страниц и шаблон Word для заполнения</li>
        <li>Форма из 7 разделов по СанПиН 3.3686-21, ТР ТС 021/2011 и ГОСТ Р 54762-2011 (FSSC 22000)</li>
        <li>Пример заполнения плана мероприятий по 6 зонам и разработка программы под ваш объект</li>
      </ul>
      <div class="d-btns">
        <a href="obrazets-programmy-pest-kontrolya.pdf" class="btn btn-w btn-lg" target="_blank" rel="noopener"><span class="btn-t">Скачать образец, PDF</span></a>
        <a href="#zayavka" class="btn btn-o btn-lg"><span class="btn-t">Заказать разработку программы</span></a>
      </div>
      <p class="p-hero-note">Есть <a href="shablon-programmy-pest-kontrolya.docx" download>шаблон программы в Word (DOCX)</a> · обезличенный образец ПЕСТКОНТРОЛЬ Центра</p>
    </div>
    <div aria-hidden="true"></div>
  </div>
</section>

<nav class="p-toc" aria-label="Содержание страницы">
  <div class="wrap">
    <b>Содержание</b>
    <a href="#obrazets">Образец PDF и шаблон Word</a>
    <a href="#razdely">Форма: 7 разделов</a>
    <a href="#kak-zapolnit">Как заполнить шаблон</a>
    <a href="#metodika">Расчёт пест-риска</a>
    <a href="#plan">Пример плана мероприятий</a>
    <a href="#otvetstvennost">Обязанности сторон</a>
    <a href="#kontrol">Журнал и отчёты</a>
    <a href="#razrabotka">Разработка и цена</a>
    <a href="#voprosy">Вопросы</a>
  </div>
</nav>

<section class="s" id="obrazets">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Образец · форма · шаблон</div>
      <h2>Образец программы <span class="nw">пест-контроля</span>: <em>скачать PDF и шаблон Word</em></h2>
      <p class="sub">Обезличенный образец рабочей программы ПЕСТКОНТРОЛЬ Центра для пищевого производства, склада, магазина или ресторана. Показывает, как выглядит заполненная форма: титул с грифами утверждения, паспорт объекта, расчёт пест-риска, план мероприятий по зонам, реестр средств и подписи сторон.</p>
    </div>
    <div class="p-obr">
      <div class="p-obr-pages">
        <a class="p-obr-page" href="obrazets-programmy-pest-kontrolya.pdf" target="_blank" rel="noopener"><span><img src="../../img/programma-sample-p1-360.webp" srcset="../../img/programma-sample-p1-240.webp 240w, ../../img/programma-sample-p1-360.webp 360w, ../../img/programma-sample-p1-720.webp 720w" sizes="(max-width:600px) 28vw, 200px" width="360" height="509" loading="lazy" decoding="async" alt="Образец программы пест-контроля, страница 1: титульный лист, нормативная база и паспорт объекта"></span><b>Стр. 1</b><small>Титул и паспорт объекта</small></a>
        <a class="p-obr-page" href="obrazets-programmy-pest-kontrolya.pdf#page=3" target="_blank" rel="noopener"><span><img src="../../img/programma-sample-p3-360.webp" srcset="../../img/programma-sample-p3-240.webp 240w, ../../img/programma-sample-p3-360.webp 360w, ../../img/programma-sample-p3-720.webp 720w" sizes="(max-width:600px) 28vw, 200px" width="360" height="509" loading="lazy" decoding="async" alt="Образец программы пест-контроля, страница 3: пример плана мероприятий по зонам объекта"></span><b>Стр. 3</b><small>План мероприятий по зонам</small></a>
        <a class="p-obr-page" href="obrazets-programmy-pest-kontrolya.pdf#page=5" target="_blank" rel="noopener"><span><img src="../../img/programma-sample-p5-360.webp" srcset="../../img/programma-sample-p5-240.webp 240w, ../../img/programma-sample-p5-360.webp 360w, ../../img/programma-sample-p5-720.webp 720w" sizes="(max-width:600px) 28vw, 200px" width="360" height="509" loading="lazy" decoding="async" alt="Образец программы пест-контроля, страница 5: реестр разрешённых средств и оборудования"></span><b>Стр. 5</b><small>Реестр средств с СГР</small></a>
      </div>
      <div class="p-obr-info">
        <h3>Что внутри образца программы</h3>
        <ol class="p-obr-list">
          <li><b>Стр. 1</b><span>Грифы «Утверждаю» и «Согласовано», нормативная база, паспорт объекта и ответственные</span></li>
          <li><b>Стр. 2</b><span>Целевые виды вредителей до рода и вида, формула пест-риска, ПОПМ и ПРПО, 3 контура защиты</span></li>
          <li><b>Стр. 3</b><span>Приложение № 1 — пример заполнения плана мероприятий по 6 зонам (A_1…F_6)</span></li>
          <li><b>Стр. 4</b><span>Обязательные мероприятия службы пест-контроля и предприятия</span></li>
          <li><b>Стр. 5</b><span>Приложение № 2 — реестр разрешённых средств, ловушек и правила безопасности</span></li>
          <li><b>Стр. 6</b><span>Уровни контроля, журнал и отчёты, порядок пересмотра, подписи сторон</span></li>
        </ol>
        <div class="p-obr-btns">
          <a href="obrazets-programmy-pest-kontrolya.pdf" class="btn btn-w btn-lg" target="_blank" rel="noopener"><span class="btn-t">Скачать образец, PDF</span></a>
          <a href="shablon-programmy-pest-kontrolya.docx" class="btn btn-o btn-lg" download><span class="btn-t">Шаблон Word, DOCX</span></a>
        </div>
        <p class="p-obr-meta">PDF — 6 страниц, 145 КБ; DOCX — те же разделы с полями для заполнения. Структура плана мероприятий — по методике НЧНОУ «Институт <span class="nw">пест-менеджмента</span>» (<a href="https://ipm.moscow/pest-hazard-assessment" target="_blank" rel="noopener noreferrer">ipm.moscow</a>).</p>
      </div>
    </div>
  </div>
</section>

<section class="f-checks" id="samoproverka" aria-labelledby="chk-t">
  <div class="wrap">
    <div class="panel f-check">
      <div class="panel-scan" aria-hidden="true"></div>
      <div class="f-check-in">
        <div class="f-check-l">
          <div class="eyebrow">Экспресс-проверка документа</div>
          <h2 id="chk-t" class="f-check-t">Пройдёт ли ваша программа <span class="nw">пест-контроля</span> аудит</h2>
          <p class="f-check-res"><b id="chk-n">0</b> из 5</p>
          <p class="f-check-note" id="chk-note" aria-live="polite">Отметьте пункты, которые уже выполнены в вашей папке пест-контроля. Если чего-то не хватает — на бесплатном обследовании покажем, что доработать до проверки.</p>
          <a href="#zayavka" class="btn btn-w btn-lg"><span class="btn-t">Проверить папку на объекте</span></a>
        </div>
        <ul class="f-check-list">
          <li><label><input type="checkbox"><span><strong>Рассчитан пест-риск по зонам:</strong> для каждого цеха, склада и территории определена категория риска и заданы пороговые лимиты численности</span></label></li>
          <li><label><input type="checkbox"><span><strong>Закреплена двусторонняя ответственность:</strong> приказом назначен ответственный от предприятия и указан пест-менеджер лицензированного подрядчика</span></label></li>
          <li><label><input type="checkbox"><span><strong>План-схема совпадает с цехом:</strong> номера и типы КИК, живоловок, клеевых мониторов и УФ-ламп на чертеже на 100% соответствуют факту</span></label></li>
          <li><label><input type="checkbox"><span><strong>Средства разделены по контурам:</strong> родентициды — строго снаружи здания, внутри цехов — ловушки без яда, приложены действующие СГР и паспорта безопасности</span></label></li>
          <li><label><input type="checkbox"><span><strong>Прописаны корректирующие меры и тренды:</strong> есть регламент действий при превышении порога, срок выезда по сигналу и ежемесячный анализ динамики</span></label></li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="s" id="trebovaniya">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Нормативные требования и аудиты</div>
      <h2>Почему образец нельзя просто <em>скачать и подписать</em></h2>
      <p class="sub">Образец показывает форму документа, но инспектор Роспотребнадзора и аудитор торговой сети сверяют программу с реальным цехом. Общие фразы «проводить обработку раз в месяц» без оценки риска, пронумерованных точек и пороговых уровней фиксируются как критическое несоответствие.</p>
    </div>
    <div class="d-cards f-req">
      <article class="d-card">
        <p class="f-num">СанПиН 3.3686-21</p>
        <h3>Пункты 98, 101, 108–111</h3>
        <p>Обязывает юрлиц проводить регулярные обследования, профилактические и истребительные меры. На пищевых и торговых объектах контроль насекомых — не реже 2 раз в месяц, по грызунам — ежемесячная оценка.</p>
      </article>
      <article class="d-card">
        <p class="f-num">ТР ТС 021/2011</p>
        <h3>Статьи 10 и 14 · ГОСТ Р ИСО 22000</h3>
        <p>Требует внедрения процедур ХАССП, инженерной защиты производственных помещений от проникновения грызунов, насекомых и птиц, а также документального подтверждения мониторинга в контрольных точках.</p>
      </article>
      <article class="d-card">
        <p class="f-num">Раздел 12 ГОСТ</p>
        <h3>ГОСТ Р 54762-2011 / ISO/TS 22002-1</h3>
        <p>Базовый стандарт предварительных программ (ПОПМ / PRP) для FSSC 22000: назначенный ответственный, документированная программа, целевые вредители, карта детекторов, защита сырья от пестицидов и анализ трендов.</p>
      </article>
    </div>
    <table class="d-table d-vs">
      <thead>
        <tr>
          <th scope="col">Критерий проверки</th>
          <th scope="col">Шаблон без обследования или формальная ППК</th>
          <th scope="col">Рабочая программа ПЕСТКОНТРОЛЬ Центра</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td data-l="Критерий проверки">Привязка к зданию и потокам сырья</td>
          <td data-l="Скачанный шаблон">Общий текст без учёта рамп, ворот, вентиляции, температурных зон и маршрутов движения продукта</td>
          <td data-l="Рабочая программа">Составляется после очного обследования строений и территории с разбивкой на 3 контура защиты и зоны риска</td>
        </tr>
        <tr>
          <td data-l="Критерий проверки">Перечень целевых вредителей</td>
          <td data-l="Скачанный шаблон">Абстрактная запись «грызуны и бытовые насекомые»</td>
          <td data-l="Рабочая программа">Точный видовой состав до рода и вида под специфику сырья, тары и прилегающей территории</td>
        </tr>
        <tr>
          <td data-l="Критерий проверки">Связь с системой ХАССП</td>
          <td data-l="Скачанный шаблон">Отдельная папка, не связанная с анализом опасностей предприятия</td>
          <td data-l="Рабочая программа">Чёткое разделение постоянных мер ПОПМ (PRP) без остановки цеха и операционных мер ПРПО при превышении порога</td>
        </tr>
        <tr>
          <td data-l="Критерий проверки">Точки пест-контроля (ТПК) и лимиты</td>
          <td data-l="Скачанный шаблон">Нет привязки к типам ловушек и допустимым порогам численности</td>
          <td data-l="Рабочая программа">Сквозная нумерация КИК, живоловок, клеевых мониторов и УФ-ламп с критическими лимитами по каждой зоне</td>
        </tr>
        <tr>
          <td data-l="Критерий проверки">Обязанности служб предприятия</td>
          <td data-l="Скачанный шаблон">Вся ответственность формально переложена на приходящего дезинфектора</td>
          <td data-l="Рабочая программа">Прописан регламент для служб Заказчика: герметизация (пест-пруфинг), санитарный режим, входной контроль партий</td>
        </tr>
      </tbody>
    </table>
  </div>
</section>

<section class="s" id="razdely">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Структура документа</div>
      <h2>Форма программы <span class="nw">пест-контроля</span>: <em>7 обязательных разделов</em></h2>
      <p class="sub">Мы формируем программу на основе санитарного законодательства РФ и отраслевых стандартов пест-менеджмента (СТО 55003215.001-2023 и СТО 55003215.001-2015 НЧНОУ «Институт пест-менеджмента»).</p>
    </div>
    <div class="p-secs">
      <article class="p-sec">
        <div>
          <div class="p-sec-top"><span class="p-sec-num">Раздел 01</span><span class="p-sec-who">Проверяют: РПН, аудитор ХАССП</span></div>
          <h3>Паспорт объекта, стороны и распределение ответственности</h3>
          <p>Перечень адресов, корпусов и площадей, номер лицензии ДДД исполнителя. Закрепляются два ответственных лица: <strong>представитель Заказчика</strong> (координирует работы, допуск и выполнение санитарно-технических предписаний) и <strong>пест-менеджер Исполнителя</strong> (оценивает качество работы техников, проверяет документацию и ведёт переговоры со службами объекта).</p>
        </div>
      </article>
      <article class="p-sec">
        <div>
          <div class="p-sec-top"><span class="p-sec-num">Раздел 02</span><span class="p-sec-who">Проверяют: аудиторы FSSC 22000, сетей</span></div>
          <h3>Перечень целевых (проблемных) биологических видов</h3>
          <p>Классификация вредителей, несущих медицинский, хозяйственный или репутационный риск для предприятия:</p>
          <ul>
            <li><strong>Грызуны:</strong> серая крыса (<em>Rattus norvegicus</em>), чёрная крыса (<em>Rattus rattus</em>), домовая мышь (<em>Mus musculus</em>), полёвки;</li>
            <li><strong>Бытовые членистоногие:</strong> тараканы (<em>Blattidae</em>), муравьи (<em>Formicidae</em>), мухи, дрозофилы, бабочницы, чешуйницы;</li>
            <li><strong>Вредители запасов и сырья:</strong> огнёвки, пищевая моль, хрущаки, долгоносики, мукоеды, кожееды, точильщики;</li>
            <li><strong>Случайно проникающие виды и птицы:</strong> насекомые, летящие на свет и запах, синантропные птицы на рампах и кровле.</li>
          </ul>
        </div>
      </article>
      <article class="p-sec">
        <div>
          <div class="p-sec-top"><span class="p-sec-num">Раздел 03</span><span class="p-sec-who">Проверяют: орган сертификации, служба качества</span></div>
          <h3>Оценка пест-опасности и расчёт пест-риска по зонам</h3>
          <p>Анализ вероятности захода и размножения вредителей в каждом подразделении (территория, рампа, склад сырья, цех, моечная, упаковка) с учётом ёмкости среды обитания, внешних факторов и защищённости здания. Каждой зоне присваивается индекс пест-риска, определяющий плотность точек и частоту обходов.</p>
        </div>
      </article>
      <article class="p-sec">
        <div>
          <div class="p-sec-top"><span class="p-sec-num">Раздел 04</span><span class="p-sec-who">Проверяют: все инспекторы при обходе цеха</span></div>
          <h3>План-схема контуров защиты и точек пест-контроля (ТПК)</h3>
          <p>Цветные схемы территории и этажей с местами размещения контрольно-истребительных контейнеров (КИК), механических живоловок, клеевых и феромонных мониторов, следовых площадок и инсектицидных УФ-ловушек. Описывается порядок настенной маркировки, сигнальных лент и сезонного уплотнения точек.</p>
        </div>
      </article>
      <article class="p-sec">
        <div>
          <div class="p-sec-top"><span class="p-sec-num">Раздел 05</span><span class="p-sec-who">Проверяют: группа ХАССП, технолог</span></div>
          <h3>Пороговые уровни (лимиты) и программы ПОПМ / ПРПО</h3>
          <p>Количественные критерии допустимой численности по каждой зоне (например, 0 грызунов и 0 тараканов в зоне открытого продукта) и алгоритм действий при превышении лимита: от уплотнения мониторинга и ревизии партии до запуска истребительных мер ПРПО в санитарное окно.</p>
        </div>
      </article>
      <article class="p-sec">
        <div>
          <div class="p-sec-top"><span class="p-sec-num">Раздел 06</span><span class="p-sec-who">Проверяют: санитарный врач, Роспотребнадзор</span></div>
          <h3>Реестр разрешённых средств с СГР и правила безопасности</h3>
          <p>Перечень родентицидов, инсектицидов, репеллентов и клеевых средств с номерами свидетельств о госрегистрации (СГР), действующими веществами, дозировками и разрешёнными зонами применения. Включает схему ротации препаратов против резистентности и регламент охраны труда.</p>
        </div>
      </article>
      <article class="p-sec p-sec-wide">
        <div>
          <div class="p-sec-top"><span class="p-sec-num">Раздел 07</span><span class="p-sec-who">Проверяют: руководство, аудиторы торговых сетей и сертификации</span></div>
          <h3>Регламент мониторинга, обслуживания оборудования, отчётности и анализа трендов</h3>
          <p>График плановых и инспекционных обследований, порядок перезарядки, мойки и дезинфекции станций контроля (не реже 1 раза в месяц), правила выемки и утилизации павших особей, формы объектовых журналов и структура ежемесячного аналитического отчёта с оценкой эффективности и санитарно-техническими предписаниями.</p>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="s" id="kak-zapolnit">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Пример заполнения</div>
      <h2>Как заполнить шаблон <span class="nw">программы</span>: <em>шесть шагов</em></h2>
      <p class="sub">Так составляется программа <span class="nw">пест-контроля</span> на предприятии — в том же порядке, что и в шаблоне Word. Пример заполненной матрицы мероприятий — на странице 3 образца.</p>
    </div>
    <div class="p-fill">
      <ol class="p-fill-steps">
        <li><b>Паспорт объекта и ответственные</b><span>Адрес, площади зданий и территории, число ворот, цехов и складов. Приказом назначается ответственный от предприятия, в программе указывается <span class="nw">пест-менеджер</span> подрядчика и номер его лицензии.</span></li>
        <li><b>Целевые виды вредителей</b><span>По результатам осмотра и опроса персонала — до рода и вида: какие грызуны, насекомые, вредители запасов и птицы реально угрожают продукту и зданию.</span></li>
        <li><b>Зоны и расчёт <span class="nw">пест-риска</span></b><span>Каждому подразделению присваивается код (A_1, B_2…) и индекс риска R = P × D. От него зависят плотность точек и частота обходов.</span></li>
        <li><b>План-схема точек контроля</b><span>На поэтажный план и план территории наносятся КИК, живоловки, клеевые и феромонные ловушки, УФ-лампы — по трём контурам, со сквозной нумерацией и легендой.</span></li>
        <li><b>Пороги и план мероприятий</b><span>В матрицу Приложения № 1 вписываются допустимый уровень численности по зоне, мероприятия, ответственные с обеих сторон, периодичность и номер отчётной формы.</span></li>
        <li><b>Реестр средств, утверждение, папка</b><span>В Приложение № 2 вносятся средства с номерами СГР и зоны применения. Программу утверждает руководитель предприятия, согласует служба <span class="nw">пест-контроля</span>; документ кладут в папку ХАССП.</span></li>
      </ol>
      <div class="p-fill-side">
        <figure class="p-fig"><img src="../../img/programma-plan-skhema-720.webp" srcset="../../img/programma-plan-skhema-720.webp 720w, ../../img/programma-plan-skhema.webp 1200w" sizes="(max-width:1100px) 100vw, 45vw" width="1200" height="800" loading="lazy" decoding="async" alt="План-схема точек пест-контроля: три контура защиты и пронумерованные точки на плане предприятия"><figcaption>План-схема точек к программе: внешний контур территории, периметр здания и внутренние помещения — каждая точка с номером.</figcaption></figure>
        <div class="p-obr-btns"><a href="shablon-programmy-pest-kontrolya.docx" class="btn btn-w btn-lg" download><span class="btn-t">Скачать шаблон Word</span></a><a href="#zayavka" class="btn btn-o btn-lg"><span class="btn-t">Заполнить со специалистом</span></a></div>
      </div>
    </div>
  </div>
</section>

<section class="s" id="metodika">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Методология IPM и ХАССП</div>
      <h2>Как рассчитывается <em>пест-риск</em> и разделяются ПОПМ и ПРПО</h2>
      <p class="sub">На сертификационном аудите ISO 22000 или FSSC 22000 недостаточно показать расставленные ловушки — нужно обосновать, почему в этой зоне выбран именно такой тип контроля и частота проверок.</p>
    </div>
    <div class="p-formula">
      <span class="p-formula-lbl">Формула оценки риска (по СТО 55003215.001-2015 «Процедуры управления пест-риском на предприятии»)</span>
      <p class="p-formula-eq">Пест-риск = <em>Пест-опасность (0…1)</em> × <em>Вероятность ущерба (0…1)</em></p>
      <div class="p-formula-grid">
        <div class="p-fcard">
          <b>1. Пест-опасность (0…1)</b>
          <span>Вероятность появления и выживания вредителей на объекте. Оценивается по внешнему окружению, потоку входящих грузов, ёмкости среды обитания (доступ к корму, воде, теплу), герметичности здания и дисциплине персонала.</span>
        </div>
        <div class="p-fcard">
          <b>2. Вероятность ущерба (0…1)</b>
          <span>Тяжесть медицинских, хозяйственных и репутационных последствий при появлении вредителя: от порчи упаковки на рампе до контаминации открытого продукта, возврата партии сетью или штрафа Роспотребнадзора.</span>
        </div>
        <div class="p-fcard">
          <b>3. Управляющее решение</b>
          <span>Чем выше произведение двух показателей в конкретной зоне, тем плотнее шаг установки точек пест-контроля (ТПК), жёстче критический порог и выше частота плановых и инспекционных проверок.</span>
        </div>
      </div>
    </div>
    <div class="d-cols2">
      <article class="d-card p-prp-card">
        <span class="p-badge-inline p-b-acc">Базовый контур · Работает постоянно</span>
        <h3>ПОПМ (PRP) — Программа обязательных предварительных мероприятий</h3>
        <p>Составляется на основе первичного анализа опасностей и действует непрерывно без остановки производства. Включает инженерно-технические барьеры (сетки, уплотнители, закрытые двери), санитарный режим, наружные приманочные станции КИК по периметру и инструментальный мониторинг нетоксичными ловушками внутри цехов и складов.</p>
      </article>
      <article class="d-card p-oprp-card">
        <span class="p-badge-inline p-b-yel">Дополнительный контур · По показаниям мониторинга</span>
        <h3>ПРПО (OPRP) — Производственная программа предварительных мероприятий</h3>
        <p>Включается для устранения конкретной выявленной опасности, когда отлов на точках контроля превысил допустимый порог. Истребительные обработки инсектицидами или фогация внутри производственных помещений в рамках ПРПО проводятся только как крайняя мера, при полной остановке участка в санитарное окно и с последующей мойкой линий.</p>
      </article>
    </div>
  </div>
</section>

<section class="s" id="plan">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Пример из рабочей документации</div>
      <h2>Пример плана мероприятий <em>в программе <span class="nw">пест-контроля</span></em></h2>
      <p class="sub">Фрагмент Приложения № 1 из образца: шесть типовых зон предприятия с целевыми видами, порогами, точками контроля и ответственными. Для вашего объекта таблица составляется после бесплатного обследования с привязкой к реальным помещениям и номерам точек на схеме.</p>
    </div>
    <table class="d-table p-plan-table">
      <thead>
        <tr>
          <th scope="col">Подразделение (код)</th>
          <th scope="col">Целевые виды вредителей</th>
          <th scope="col">Пест-риск и порог</th>
          <th scope="col">Мероприятия и точки ТПК</th>
          <th scope="col">Ответственные</th>
          <th scope="col">Сроки и отчёт</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td data-l="Подразделение (код)"><span class="p-code">A_1</span><br>Прилегающая территория и площадка ТКО</td>
          <td data-l="Целевые виды вредителей">Серая крыса (<em>Rattus norvegicus</em>), домовая мышь (<em>Mus musculus</em>), полёвки (<em>Microtus spp.</em>), мухи</td>
          <td data-l="Пест-риск и порог"><span class="p-risk-hi">Высокий (0,64)</span><br>Порог: 0 жилых нор; поедаемость приманки &gt; 20% — уплотнение КИК</td>
          <td data-l="Мероприятия и точки ТПК">Закрытые антивандальные КИК с родентицидными блоками на стержнях вдоль забора и у ТКО; дезинсекция мусоросборников; покос травы и вывоз отходов</td>
          <td data-l="Ответственные">Заказчик: нач. АХО.<br>Исполнитель: пест-менеджер, дезинфектор</td>
          <td data-l="Сроки и отчёт">Обход — 2 раза в месяц; мойка КИК — 1 раз в месяц.<br>Отчёт <code>Ф-ТПК-1</code></td>
        </tr>
        <tr>
          <td data-l="Подразделение (код)"><span class="p-code">B_2</span><br>Погрузочная рампа, доки и тамбуры</td>
          <td data-l="Целевые виды вредителей">Серая и чёрная крыса (<em>Rattus spp.</em>), домовая мышь, мухи (<em>Musca domestica</em>), осы</td>
          <td data-l="Пест-риск и порог"><span class="p-risk-hi">Высокий (0,72)</span><br>Порог: 0 грызунов в тамбуре; &gt; 15 насекомых/нед. на УФ-лампу — ревизия ворот</td>
          <td data-l="Мероприятия и точки ТПК">Контур КИК снаружи у доков; механические живоловки и клеевые туннели внутри у ворот; инсектицидные УФ-ловушки; проверка уплотнителей и завес</td>
          <td data-l="Ответственные">Заказчик: зав. складом.<br>Исполнитель: пест-менеджер</td>
          <td data-l="Сроки и отчёт">Плановый осмотр — 2 раза в месяц; замена экранов УФ-ламп при заполнении &gt; 50%.<br>Отчёт <code>Ф-ТПК-2</code></td>
        </tr>
        <tr>
          <td data-l="Подразделение (код)"><span class="p-code">C_3</span><br>Склад сырья, упаковки и готовой продукции</td>
          <td data-l="Целевые виды вредителей">Домовая мышь (<em>Mus musculus</em>), пищевая моль и огнёвки (<em>Pyralidae</em>), хрущаки, мукоеды</td>
          <td data-l="Пест-риск и порог"><span class="p-risk-hi">Высокий (0,70)</span><br>Порог: 0 грызунов и погрызов; &gt; 2 особей огнёвки в ловушке — ревизия партии</td>
          <td data-l="Мероприятия и точки ТПК">Без ядов: многоместные живоловки и клеевые мониторы с шагом 6–12 м; феромонные ловушки на вредителей запасов; входной осмотр паллет от поставщиков</td>
          <td data-l="Ответственные">Заказчик: кладовщик, служба качества.<br>Исполнитель: пест-менеджер</td>
          <td data-l="Сроки и отчёт">Мониторинг — 2–4 раза в месяц; ежемесячная оценка.<br>Отчёт <code>Ф-ТПК-3</code></td>
        </tr>
        <tr>
          <td data-l="Подразделение (код)"><span class="p-code">D_4</span><br>Производственный цех, линии и фасовка</td>
          <td data-l="Целевые виды вредителей">Тараканы (<em>Blattella germanica</em>), муравьи (<em>Formicidae</em>), мухи, дрозофилы, мышь домовая</td>
          <td data-l="Пест-риск и порог"><span class="p-risk-cr">Критический (0,85)</span><br>Порог: 0 особей грызунов и тараканов (нулевая терпимость у продукта)</td>
          <td data-l="Мероприятия и точки ТПК">ПОПМ: клеевые мониторы в защитных корпусах и УФ-ловушки с небьющимися лампами. ПРПО (при очаге): точечное нанесение геля или обработка в санитарное окно</td>
          <td data-l="Ответственные">Заказчик: гл. технолог, инженер ХАССП.<br>Исполнитель: пест-менеджер</td>
          <td data-l="Сроки и отчёт">Осмотр ТПК — не реже 2 раз в месяц; выезд по сигналу — за 3 часа.<br>Отчёт <code>Ф-ТПК-4</code></td>
        </tr>
        <tr>
          <td data-l="Подразделение (код)"><span class="p-code">E_5</span><br>Моечная, трапы, санузлы и бытовые зоны</td>
          <td data-l="Целевые виды вредителей">Тараканы, плодовые мушки (<em>Drosophila spp.</em>), бабочницы (<em>Psychodidae</em>), чешуйницы</td>
          <td data-l="Пест-риск и порог"><span class="p-risk-hi">Средний / Высокий (0,55)</span><br>Порог: &gt; 1 особи таракана или выплод в трапе — зачистка и барьер</td>
          <td data-l="Мероприятия и точки ТПК">Клеевые мониторы под мойками, у стояков и кабель-каналов; контроль гидрозатворов и чистоты трапов; гелевые приманки с СГР в закрытых точках</td>
          <td data-l="Ответственные">Заказчик: мастер смены, клининг.<br>Исполнитель: дезинфектор</td>
          <td data-l="Сроки и отчёт">Осмотр — 2 раза в месяц; устранение протечек и жира за 3–7 дней.<br>Отчёт <code>Ф-ТПК-5</code></td>
        </tr>
        <tr>
          <td data-l="Подразделение (код)"><span class="p-code">F_6</span><br>Техподполье, венткамеры, кабель-каналы и кровля</td>
          <td data-l="Целевые виды вредителей">Серая и чёрная крыса (<em>Rattus spp.</em>), комары (<em>Culex pipiens</em>), сизый голубь (<em>Columba livia</em>)</td>
          <td data-l="Пест-риск и порог"><span class="p-risk-md">Средний (0,45)</span><br>Порог: 0 следов крыс у кабельных вводов; 0 гнёзд птиц на рампах</td>
          <td data-l="Мероприятия и точки ТПК">Закрытые КИК во влажных техподпольях; проверка сеток с ячейкой не более 5×5 мм на вентшахтах и продухах; защита карнизов рамп от птиц</td>
          <td data-l="Ответственные">Заказчик: гл. инженер.<br>Исполнитель: пест-менеджер</td>
          <td data-l="Сроки и отчёт">Плановая проверка — 1–2 раза в месяц.<br>Отчёт <code>Ф-ТПК-6</code></td>
        </tr>
      </tbody>
    </table>
    <p class="d-note">Методическая основа структуры плана мероприятий: СТО 55003215.001-2023 и СТО 55003215.001-2015 НЧНОУ «Институт пест-менеджмента» (<a href="https://ipm.moscow/pest-hazard-assessment" target="_blank" rel="noopener noreferrer">ipm.moscow</a>), адаптированные под договорной регламент ПЕСТКОНТРОЛЬ Центра.</p>
  </div>
</section>

<section class="s" id="otvetstvennost">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Регламент взаимодействия сторон</div>
      <h2>Что в программе делает <em>служба <span class="nw">пест-контроля</span></em>, а что — предприятие</h2>
      <p class="sub">Аудиторы FSSC 22000 и торговых сетей проверяют не только акты подрядчика, но и выполнение предприятием своих санитарно-технических обязанностей. В рабочей программе эти перечни разделены.</p>
    </div>
    <figure class="p-fig p-fig-wide"><img src="../../img/programma-kik-rampa-720.webp" srcset="../../img/programma-kik-rampa-720.webp 720w, ../../img/programma-kik-rampa.webp 1200w" sizes="100vw" width="1200" height="800" loading="lazy" decoding="async" alt="Специалист по пест-контролю проверяет контрольно-истребительный контейнер у погрузочной рампы и вносит данные в планшет"><figcaption>Плановый обход внешнего контура: специалист открывает контейнер КИК у рампы и сразу вносит состояние точки в журнал.</figcaption></figure>
    <div class="p-duties">
      <div class="p-duty-box isp">
        <h3>Мероприятия ПЕСТКОНТРОЛЬ Центра (Исполнитель)</h3>
        <p class="p-duty-lead">Работы выполняют <span class="nw">пест-менеджеры</span> и дезинфекторы с профильной подготовкой по дезинфектологии:</p>
        <ul class="p-duty-list">
          <li><strong>Обследование и анкетирование:</strong> визуальный и инструментальный осмотр помещений и территории, выявление троп, нор, следов и мест захода вредителей, опрос инженерных и производственных смен.</li>
          <li><strong>Оснащение и маркировка ТПК:</strong> установка следовых и клеевых площадок, живоловок, УФ-ламп и контейнеров КИК с сигнальными лентами и настенными указателями, ведение актуальной план-схемы.</li>
          <li><strong>Плановые обходы и учёт:</strong> регулярная проверка всех точек контроля по графику, видовая идентификация и регистрация состояния каждой точки и активности вредителей.</li>
          <li><strong>Санитарное обслуживание оборудования:</strong> перезарядка приманок, замена клеевых пластин, сборка и мойка, чистка и дезинфекция контейнеров и ловушек <strong>не реже 1 раза в месяц</strong>.</li>
          <li><strong>Выемка и утилизация:</strong> изъятие отловленных вредителей и вывоз павших грызунов специализированным транспортом.</li>
          <li><strong>Целевые обработки средствами с СГР:</strong> барьерные и истребительные обработки поверхностей, зон ТКО и очагов строго разрешёнными препаратами с передачей копий СГР и инструкций.</li>
          <li><strong>Письменные предписания с фото:</strong> подготовка отчётов для инженерной и санитарной служб Заказчика с фотографиями дефектов герметичности и приоритетными сроками устранения (3 / 7 / 14 дней).</li>
        </ul>
      </div>
      <div class="p-duty-box zak">
        <h3>Мероприятия предприятия (Заказчик по программе ПОПМ)</h3>
        <p class="p-duty-lead">Внутренние превентивные условия, которые координирует назначенный представитель Заказчика:</p>
        <ul class="p-duty-list">
          <li><strong>Благоустройство территории:</strong> своевременное скашивание травы, подрезка кроны деревьев на высоту не ниже 0,5 м над землёй, отказ от высадки растений, образующих кормовые семена у корпусов.</li>
          <li><strong>Удаление отходов и оборотной тары:</strong> ежедневный вывоз мусора и пищевых отходов, плотно закрытые контейнеры ТКО, немедленный вывоз освободившихся паллет, картона и строительных материалов после ремонта.</li>
          <li><strong>Входной контроль поставок:</strong> осмотр каждой партии сырья, упаковки и готовой продукции при приёмке на склад; документирование находок и немедленное оповещение поставщика и службы пест-контроля.</li>
          <li><strong>Устранение источников влаги:</strong> оперативный ремонт протечек труб, устранение конденсата на потолках и стенах, удаление стоячей воды в приямках, раковинах и канализационных трапах.</li>
          <li><strong>Санитарный режим и герметизация контура:</strong> регулярная мойка помещений и оборудования, запрет на хранение пищи в личных шкафчиках, закрытые двери, сетки на окнах и вентиляции, исправные тепловые завесы и своевременная замена УФ-ламп по сроку службы.</li>
          <li><strong>Сохранность и доступность ТПК:</strong> обеспечение доступа специалиста во все зоны при визите и инструктаж персонала, чтобы ловушки не заставляли паллетами и не сбивали при уборке.</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="s" id="kontrol">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Многоуровневый контроль и отчётность</div>
      <h2>Журнал <span class="nw">пест-контроля</span> и отчёты <em>в составе программы</em></h2>
      <p class="sub">Программа определяет, что и как записывается: журнал <span class="nw">пест-контроля</span> (учёт осмотров точек), акты применения средств и аналитический отчёт. Выполнение программы проверяют на четырёх уровнях.</p>
    </div>
    <ol class="d-steps">
      <li><b>Внутренний производственный</b><span>Руководитель службы пест-контроля проверяет работу дезинфекторов на объекте, соблюдение методик и точность записей по каждой точке.</span></li>
      <li><b>Текущий контроль Заказчика</b><span>Менеджер по качеству или санитарный врач принимает результаты каждого визита, сверяет показания точек и получает санитарные предписания.</span></li>
      <li><b>Инспекционный контроль ХАССП</b><span>Инспекционная группа предприятия оценивает динамику численности за месяц и проверяет устранение инженерных замечаний в срок.</span></li>
      <li><b>Внешний надзор и аудит</b><span>Независимую проверку папки и территории проводят органы Роспотребнадзора, аудиторы сертификации и инспекторы торговых сетей.</span></li>
    </ol>
    <div class="d-cards" style="margin-top:20px">
      <article class="d-card">
        <span class="p-badge-inline p-b-acc">Форма 1 · При каждом визите</span>
        <h3>Журнал <span class="nw">пест-контроля</span>: осмотр точек ТПК</h3>
        <p>При каждом визите по каждой пронумерованной точке записывают дату, номер и тип устройства, его состояние и доступность, вид и число вредителей или следов (помёт, погрызы, оотеки), поедаемость приманки, замену клеевой пластины и подпись специалиста.</p>
      </article>
      <article class="d-card">
        <span class="p-badge-inline p-b-acc">Форма 2 · При применении средств</span>
        <h3>Отчёты о средствах пест-контроля и акты</h3>
        <p>Указываются торговые наименования пестицидов и нетоксичных средств, номера СГР, действующие вещества, дозировки, конкретные места и методы нанесения, целевой вредитель и точное время проведения работ.</p>
      </article>
      <article class="d-card">
        <span class="p-badge-inline p-b-yel">Форма 3 · Ежемесячно и по итогам аудита</span>
        <h3>Итоговый аналитический отчёт с трендами</h3>
        <p>Обобщает данные визуального и инструментального осмотра и опроса персонала. Содержит тренды по критическим точкам, рекомендации по участкам со сроками исполнения и факты снижения эффективности ловушек по вине персонала.</p>
      </article>
    </div>
  </div>
</section>

<section class="s" id="razrabotka">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Порядок запуска и стоимость</div>
      <h2>Как мы разрабатываем программу <em>для вашего объекта</em></h2>
      <p class="sub">Образец и шаблон на этой странице — бесплатно и для ориентира. Рабочую программу под ваш объект составляем после осмотра: она входит в запуск регулярного обслуживания по договору.</p>
    </div>
    <table class="d-table">
      <thead>
        <tr>
          <th scope="col">Тип объекта</th>
          <th scope="col">Что входит в программу и абонентское ведение</th>
          <th scope="col">Ориентир стоимости</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td data-l="Тип объекта">Кафе, ресторан, пищеблок</td>
          <td data-l="Что входит">Программа пест-контроля для ХАССП и ППК, схема ТПК, контроль грызунов и насекомых (1–2 визита в месяц), журнал и акты</td>
          <td data-l="Ориентир стоимости">от 3 500 ₽/мес</td>
        </tr>
        <tr>
          <td data-l="Тип объекта">Магазин, супермаркет</td>
          <td data-l="Что входит">Программа и схема точек по залу, складу и дебаркадеру, 1–2 визита в месяц, полный комплект документов с СГР</td>
          <td data-l="Ориентир стоимости">от 3 500 ₽/мес</td>
        </tr>
        <tr>
          <td data-l="Тип объекта">Склад до 1 000 м²</td>
          <td data-l="Что входит">Оценка пест-риска, программа и схема контуров защиты (периметр, доки, хранение), плановый мониторинг и отчётность</td>
          <td data-l="Ориентир стоимости">от 4 500 ₽/мес</td>
        </tr>
        <tr>
          <td data-l="Тип объекта">Пищевое производство, РЦ, завод</td>
          <td data-l="Что входит">Развёрнутая программа ПОПМ / ПРПО под FSSC 22000, ISO 22000 и сети, многоконтурная схема ТПК, анализ трендов и предписания</td>
          <td data-l="Ориентир стоимости">после бесплатного выезда</td>
        </tr>
      </tbody>
    </table>
    <div class="d-cols2">
      <div class="d-card">
        <h3>Сроки подготовки и запуска</h3>
        <p>Выезд пест-менеджера и первичное обследование — бесплатно. Проект договора со структурой программы и расчётом точек направляем в течение 1 часа после осмотра. Старт работ на объекте — от 3 часов, внеплановый выезд по сигналу — в течение 3 часов.</p>
      </div>
      <div class="d-card">
        <h3>Переход от другого подрядчика без разрыва</h3>
        <p>Проводим ревизию действующей программы, схемы точек и журналов прежнего исполнителя, устраняем замечания под актуальные нормы СанПиН 3.3686-21 и запускаем обслуживание с даты окончания старого договора. Работаем с НДС и без НДС, по ЭДО и на бумаге.</p>
      </div>
    </div>
    <ul class="d-chips">
      <li><a href="../../dogovor-deratizatsiya-dezinsektsiya/">Условия и образец договора на обслуживание →</a></li>
      <li><a href="../../pishchevoe-proizvodstvo/">Пест-контроль на пищевом производстве →</a></li>
      <li><a href="../pest-menedzhment-ili-razovaya-obrabotka/">Пест&#8209;менеджмент или разовая обработка →</a></li>
      <li><a href="../../#dokumenty">Документы и отчётность на главной →</a></li>
    </ul>
  </div>
</section>

<section class="s" id="voprosy">
  <div class="wrap">
    <div class="head">
      <div class="eyebrow">Частые вопросы</div>
      <h2>Вопросы <em>о программе <span class="nw">пест-контроля</span></em></h2>
    </div>
    {build_faq_html()}
  </div>
</section>
"""

def build_page():
    tpl = (ROOT / 'dogovor-deratizatsiya-dezinsektsiya' / 'index.html').read_text(encoding='utf-8')
    # Replace paths from ../ to ../../
    s = tpl.replace('href="../', 'href="../../').replace('src="../', 'src="../../').replace('srcset="../', 'srcset="../../')
    # Remove hero image preloads from dogovor
    s = re.sub(r'<link rel="preload"[^>]*dogovor-hero[^>]*>\n?', '', s)
    s = s.replace('<link rel="preload" href="../../fonts/inter-ru-wght-normal.woff2" as="font" type="font/woff2" crossorigin>',
        '<link rel="preload" href="../../fonts/inter-ru-wght-normal.woff2" as="font" type="font/woff2" crossorigin>\n'
        '<link rel="preload" as="image" media="(min-width:861px)" imagesrcset="../../img/programma-hero-1440.webp 1440w, ../../img/programma-hero.webp 1920w" imagesizes="100vw" fetchpriority="high">\n'
        '<link rel="preload" as="image" media="(max-width:860px)" imagesrcset="../../img/programma-hero-mob-760.webp 760w, ../../img/programma-hero-mob.webp 1024w" imagesizes="100vw" fetchpriority="high">')
    s = s.replace(f'{CANONICAL_BASE}/img/dogovor-og.jpg', f'{CANONICAL_BASE}/img/programma-og.jpg')
    s = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + OG_IMAGE_ALT, s)
    # Meta tags
    s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, flags=re.S)
    s = re.sub(r'(<meta name="description" content=")[^"]*', r'\g<1>' + DESC, s)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*', r'\g<1>' + DESC, s)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + OG_TITLE, s)
    s = s.replace('https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/dogovor-deratizatsiya-dezinsektsiya/', PAGE_URL)
    # Replace style block
    s = re.sub(r'<style>.*?</style>', f'<style>{EXTRA_CSS}</style>', s, flags=re.S)
    # Replace JSON-LD block
    json_ld = json.dumps(SCHEMA_GRAPH, ensure_ascii=False, separators=(',', ':'))
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', f'<script type="application/ld+json">{json_ld}</script>', s, flags=re.S)
    # Header CTA button
    s = re.sub(r'(<a href="#zayavka" class="btn btn-w btn-sm"[^>]*><span class="btn-t">)[^<]*', r'\g<1>Заказать программу', s)
    # Mobile menu CTA
    s = re.sub(r'(<nav class="mmenu"[^>]*>.*?<a href="#zayavka" class="btn btn-w btn-lg"><span class="btn-t">)[^<]*', r'\g<1>Заказать разработку программы', s, flags=re.S)
    # Main content before #zayavka
    main_typed = typo(MAIN_HTML.strip())
    s = re.sub(r'(<main id="main" tabindex="-1">).*?(<section class="cta" id="zayavka">)', lambda m: m.group(1) + '\n' + main_typed + '\n\n' + m.group(2), s, flags=re.S)
    # Customize #zayavka section
    cta_heading = typo('Получите программу <span class="nw">пест-контроля</span> <em>и схему точек под ваш объект</em>')
    cta_sub = typo('Бесплатно приедем на предприятие в Москве или Московской области, проведём оценку пест-риска, проверим текущую папку документов и подготовим проект договора с программой за 1 час.')
    s = re.sub(
        r'(<section class="cta" id="zayavka">.*?<h2>).*?(</h2>\s*<p class="sub">).*?(</p>)',
        lambda m: m.group(1) + cta_heading + m.group(2) + cta_sub + m.group(3),
        s,
        flags=re.S
    )
    s = s.replace('<h3>Заявка на проект договора</h3>', '<h3>Заявка на разработку программы</h3>')
    s = s.replace(
        '<option value="" selected>Что нужно</option><option>Дератизация</option><option>Дезинсекция</option><option>Комплекс: дератизация и дезинсекция</option>',
        '<option value="" selected>Какая задача стоит</option><option>Разработать программу с нуля и запустить обслуживание</option><option>Подготовить папку к аудиту ХАССП / FSSC 22000 / торговой сети</option><option>Проверить и обновить программу от прежнего подрядчика</option>'
    )
    s = re.sub(r'(<button type="submit" class="btn btn-w btn-lg" id="submitBtn"><span class="btn-t">)[^<]*', r'\g<1>Получить программу', s)
    s = re.sub(r'(<a href="#zayavka" class="c2"><span>)[^<]*', r'\g<1>Обследование', s)

    # Inline script for checklist + form message + preview guard
    inline_js = """<script>
(function(){if(/^(www\\.)?xn----itbbsflddbfpfdodg9d0f\\.xn--p1ai$/i.test(location.hostname))return;var f=window.fetch;window.fetch=function(u){if(typeof u==='string'&&u.indexOf('send.php')>-1)return new Promise(function(r){setTimeout(function(){r(new Response('{"success":true}',{status:200,headers:{'Content-Type':'application/json'}}))},500)});return f.apply(this,arguments)};document.addEventListener('DOMContentLoaded',function(){var p=document.querySelector('.form .fs');if(p)p.textContent='Предпросмотр: заявка никуда не отправляется'})})();
document.addEventListener('change',function(e){if(!e.target.closest('.f-check-list'))return;var n=0;document.querySelectorAll('.f-check-list input').forEach(function(i){n+=i.checked?1:0});document.getElementById('chk-n').textContent=n;document.querySelector('.f-check-res').classList.toggle('full',n===5);document.getElementById('chk-note').textContent=n===5?'Все 5 пунктов отмечены — на бесплатном обследовании проверим, как программа и точки контроля работают в цехах.':'Отмечено '+n+' из 5 — на бесплатном обследовании проверим папку и покажем, какие разделы и схемы доработать к проверке.'});
(function(){var f=document.getElementById('form');if(!f)return;f.addEventListener('submit',function(){var e=f.elements,s=e.service.value||'не выбрано',a=e.address.value.trim()||'не указан';e.msg.value='Задача: '+s+'\\nАдрес объекта: '+a+'\\nСтраница: Программа пест-контроля (/materialy/programma-pest-kontrolya/)';});})();
</script>"""
    s = re.sub(r'<script>\(function\(\)\{var f=document\.getElementById\(\'form\'\).*?</script>', lambda m: inline_js, s, flags=re.S)

    out_dir = ROOT / 'materialy' / 'programma-pest-kontrolya'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / 'index.html'
    out_file.write_text(s, encoding='utf-8')
    print('Built:', out_file, len(s))

    # Also build /materialy/index.html hub page so breadcrumbs & header link "Материалы" work cleanly
    hub_url = f'{CANONICAL_BASE}/materialy/'
    hub_title = 'Материалы о пест-контроле для предприятий — ПЕСТКОНТРОЛЬ Центр'
    hub_desc = 'Практические руководства и образцы документов по системе IPM и ХАССП для предприятий Москвы и области: программа пест-контроля, журналы учёта, точки контроля.'
    hub_main = typo("""
<section class="p-hero" id="hero">
  <div class="wrap">
    <nav class="d-crumbs" aria-label="Навигационная цепочка"><a href="../">Главная</a><span aria-hidden="true">→</span><span aria-current="page">Материалы</span></nav>
    <div class="eyebrow">Экспертный раздел · Документация и практика IPM</div>
    <h1><span class="ln"><span>Материалы о <span class="nw">пест-контроле</span></span></span> <span class="ln"><span><em>для предприятий</em></span></span></h1>
    <p class="p-def">Разбираем требования СанПиН 3.3686-21, ТР ТС 021/2011, ГОСТ Р 54762-2011 (FSSC 22000) и стандартов IPM: как устроена рабочая документация для проверок Роспотребнадзора и аудитов торговых сетей.</p>
    <div class="p-secs" style="margin-top:36px">
      <article class="p-sec p-sec-wide">
        <div>
          <div class="p-sec-top"><span class="p-sec-num">Материал 01 · Опубликован в превью</span><span class="p-sec-who">СанПиН 3.3686-21 · ГОСТ Р 54762-2011 · СТО 55003215.001-2023</span></div>
          <h3><a href="./programma-pest-kontrolya/" style="color:var(--t1)">Программа пест-контроля на предприятии: образец PDF, шаблон Word и пример заполнения</a></h3>
          <p>Из каких 7 разделов состоит рабочая программа пест-контроля для плана ХАССП, как рассчитывается индекс пест-риска, чем отличаются программы ПОПМ (PRP) и ПРПО (OPRP), образец таблицы мероприятий по 5 зонам и разделение обязанностей между подрядчиком и Заказчиком.</p>
          <div class="d-btns" style="margin-top:20px"><a href="./programma-pest-kontrolya/" class="btn btn-w btn-lg"><span class="btn-t">Читать материал и смотреть образец</span></a></div>
        </div>
      </article>
      <article class="p-sec">
        <div>
          <div class="p-sec-top"><span class="p-sec-num">Материал 02 · Опубликован в превью</span><span class="p-sec-who">Сравнение подходов</span></div>
          <h3><a href="./pest-menedzhment-ili-razovaya-obrabotka/" style="color:var(--t1)"><span class="nw">Пест-менеджмент</span> или разовая обработка</a></h3>
          <p>Чем системный <span class="nw">пест-контроль</span> по IPM отличается от дезинсекции и дератизации по вызову и когда предприятию хватит одного выезда.</p>
        </div>
      </article>
      <article class="p-sec">
        <div>
          <div class="p-sec-top"><span class="p-sec-num">Материал 03 · В плане</span><span class="p-sec-who">Документы и учёт</span></div>
          <h3>Журнал пест-контроля: что записывать и образец заполнения</h3>
          <p>Как вести объектовый журнал осмотров точек контроля и учёта численности грызунов и насекомых без замечаний со стороны инспектора и аудитора сети.</p>
        </div>
      </article>
      <article class="p-sec">
        <div>
          <div class="p-sec-top"><span class="p-sec-num">Материал 04 · В плане</span><span class="p-sec-who">Мониторинг вредителей</span></div>
          <h3>Точки контроля вредителей (ТПК) на предприятии</h3>
          <p>Виды станций мониторинга (КИК, живоловки, клеевые туннели, феромонные и УФ-ловушки), правила нумерации, маркировки и нанесения на план-схему.</p>
        </div>
      </article>
    </div>
  </div>
</section>
""".strip())
    hs = s.replace('href="../../', 'href="../').replace('src="../../', 'src="../').replace('srcset="../../', 'srcset="../')
    hs = re.sub(r'<title>.*?</title>', f'<title>{hub_title}</title>', hs, flags=re.S)
    hs = re.sub(r'(<meta name="description" content=")[^"]*', r'\g<1>' + hub_desc, hs)
    hs = re.sub(r'(<meta property="og:description" content=")[^"]*', r'\g<1>' + hub_desc, hs)
    hs = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + hub_title, hs)
    hs = hs.replace(PAGE_URL, hub_url)
    hs = re.sub(r'(<main id="main" tabindex="-1">).*?(<section class="cta" id="zayavka">)', lambda m: m.group(1) + '\n' + hub_main + '\n\n' + m.group(2), hs, flags=re.S)
    hub_file = ROOT / 'materialy' / 'index.html'
    hub_file.write_text(hs, encoding='utf-8')
    print('Built:', hub_file, len(hs))

if __name__ == '__main__':
    build_page()
