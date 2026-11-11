#!/usr/bin/env python3
"""Сборка двух материалов о документах пест-контроля (с 11.11.2026, превью):

    materialy/akt-deratizatsii-i-dezinsektsii/index.html  — «Акт дератизации и дезинсекции: образец и что в нём указать»
        (akt.html; образец и бланк акта — те же PDF, что на странице «Документы для Роспотребнадзора», tools/akt)
    materialy/skhema-tochek-pest-kontrolya/index.html     — «Схема точек пест-контроля: образец и правила»
        (skhema.html; интерактивный план — skhema_data.py, PDF-образец — build_skhema.py)

Шаблон и сборка — как у раздела «Нормативная база»: функции tools/normativnaya-baza/build_pages.py (шапка, подвал, форма,
FAQ, типографика) на шаблоне пищевой отраслевой страницы. Свои у страниц: тексты, page.css, разметка Article с PDF,
крошки «Главная → Материалы → …», скрипт плана и цели Метрики на скачивание (akt_obrazets, akt_shablon — те же,
что на странице документов; skhema_obrazets — новая, создать в Метрике при выкладке).

    python3 tools/materialy-dokumenty/build_pages.py   # build_site.py запускает его сам
    python3 tools/site/build_site.py

Счётчики в репозиторий не кладутся — их добавляет tools/site/build_prod.py в версию для Timeweb.
"""
import importlib.util
import json
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import skhema_data as S  # noqa: E402

sys.path.insert(0, str(ROOT / 'tools' / 'akt'))
import build_akt as A  # noqa: E402  логотип, иконки и реквизиты бланка — как в PDF-образцах

# сборщик нормативной базы — тоже build_pages.py, поэтому загружаем его по пути, под другим именем
_spec = importlib.util.spec_from_file_location('nb_build_pages', ROOT / 'tools' / 'normativnaya-baza' / 'build_pages.py')
NB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(NB)

SITE = NB.SITE
# тип объекта: значения — только из send.php (ниже подпись пункта; «Другое» уходит с подписью в комментарии)
NB.SEND_TYPES |= {'Бизнес-центр или офисное здание', 'Торговый центр', 'Промышленное предприятие'}
TYPES = [('Пищевое производство', 'Пищевое производство'), ('Ресторан или кафе', 'Ресторан, кафе, столовая'),
         ('Магазин или торговая сеть', 'Магазин или торговая сеть'), ('Склад, логистика', 'Склад, логистика'),
         ('Фармацевтическое производство', 'Фармацевтическое производство'), ('Гостиница', 'Гостиница, отель'),
         ('Бизнес-центр или офисное здание', 'Бизнес-центр, офисное здание'), ('Торговый центр', 'Торговый центр'),
         ('Промышленное предприятие', 'Промышленное предприятие'), ('Другое', 'Медицинская организация'),
         ('Другое', 'Школа, детский сад'), ('Другое', 'Другое')]
AKT_PDF = 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/obrazets-akta-dezinsektsii-i-deratizatsii.pdf'
AKT_BLANK = 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/blank-akta-dezinsektsii-i-deratizatsii.pdf'
SK_PDF = 'materialy/skhema-tochek-pest-kontrolya/obrazets-skhemy-tochek-pest-kontrolya.pdf'

AKT_FAQ = [
    ('Можно ли заказать акт без выезда на объект?',
     'Нет. Мы не продаём акты как документ: акт выдаём только после выезда специалиста и обследования объекта. '
     'В нём отражаем реальную ситуацию — что нашли, где и что рекомендуем. Акт без обследования не выдержит '
     'сверки с журналом и точками контроля на месте.'),
    ('Сколько стоит акт дератизации и дезинсекции?',
     'Акт по итогам обследования — 3 000 ₽, выезд специалиста входит в стоимость. Выезд обязателен: акт составляем по результатам '
     'осмотра помещений и территории. Если понадобится обработка, её рассчитаем отдельно.'),
    ('Есть ли утверждённая форма акта дезинсекции и дератизации?',
     'Нет. СанПиН 3.3686-21 не устанавливает единого бланка, форму согласуют в договоре. Чтобы акт подтвердил работу, '
     'в нём указывают дату и время, помещения, результаты обследования по точкам контроля, средство с номером СГР '
     'и концентрацией, исполнителя с номером лицензии и подписи обеих сторон.'),
    ('Как часто составляют акт?',
     'По каждому визиту: плановому обследованию, обработке по показаниям, внеплановому выезду. На объектах из п. 98 '
     'СанПиН 3.3686-21 — пищевых, торговых, гостиницах, медицинских и детских организациях — обследования на насекомых '
     'проводят не реже 2 раз в месяц (п. 101), поэтому актов в месяц не меньше двух.'),
    ('Можно ли оформить один акт за месяц?',
     'Сводный акт для бухгалтерии оформить можно, но каждый визит всё равно нужно подтвердить по дате — актом визита '
     'или записью в журнале пест-контроля. Один акт без дат визитов не показывает кратность обследований, которую '
     'проверяет инспектор.'),
    ('Нужно ли указывать в акте номер СГР средства?',
     'Да. Номер свидетельства о госрегистрации, действующее вещество и концентрация позволяют проверить, что средство '
     'зарегистрировано и применено по инструкции. Копии свидетельств и инструкций хранят в папке объекта.'),
    ('Кто подписывает акт со стороны заказчика?',
     'Работник, ответственный за пест-контроль или производственный контроль: менеджер по качеству, заведующий '
     'производством, администратор. Его удобно назначить приказом и указать в договоре — тогда подпись в акте '
     'не вызывает вопросов.'),
    ('Можно ли оформлять акты в электронном виде?',
     'Да. Первичный учётный документ можно составить в электронном виде и подписать электронными подписями '
     '(ч. 5 ст. 9 402-ФЗ). На объекте держите распечатку или доступ к системе электронного документооборота, '
     'чтобы показать акт инспектору сразу.'),
    ('Сколько хранить акты дезинсекции и дератизации?',
     'Как первичные учётные документы — не менее пяти лет после отчётного года (ч. 1 ст. 29 402-ФЗ). '
     'Храните их в папке объекта вместе с журналом, договором и схемой точек.'),
    ('Чем акт отличается от журнала пест-контроля?',
     'Журнал ведут на объекте постоянно: в нём записи по каждой точке за все визиты. Акт подводит итог одного визита '
     'и подтверждает объём работ для заказчика и бухгалтерии. Номер акта ставят в журнале рядом с записью визита.'),
]

SK_FAQ = [
    ('Обязательна ли схема точек пест-контроля?',
     'Если предприятие работает по ГОСТ Р 54762-2011 или проходит аудит FSSC 22000 и торговых сетей — да: п. 12.5 '
     'стандарта требует иметь план размещения датчиков обнаружения и ловушек. СанПиН отдельного документа не называет, '
     'но схема точек входит в программу пест-контроля и показывает инспектору, где и как вы контролируете вредителей.'),
    ('Кто составляет схему точек?',
     'Исполнитель по итогам первичного обследования объекта, заказчик её согласует. Если пест-контроль ведут '
     'своими силами — ответственный сотрудник предприятия.'),
    ('Как нумеровать точки контроля?',
     'Префикс типа устройства и порядковый номер: КИК-01, МЛ-10, ИМ-03. Номер не повторяется и совпадает на схеме, '
     'настенном указателе и в журнале. Номер снятой точки повторно не используют.'),
    ('Сколько точек нужно на объекте?',
     'Столько, сколько требует риск зон, а не формула. Плотнее — у входов, доков, складов сырья и мест сбора отходов. '
     'Ориентир для раскладки приманок в помещениях при дератизации — 3–5 точек на 100 м² (МР 3.5.3.0374-25). '
     'В образце хлебопекарного цеха на 1 850 м² — 30 точек в трёх контурах.'),
    ('Можно ли ставить станции с ядом внутри цеха?',
     'В помещениях с открытой пищевой продукцией используют ловушки и клеевые мониторы без родентицидов — этого '
     'ждут аудиторы ХАССП и торговых сетей, так работаем и мы. Станции с приманкой — запираемые и закреплённые, '
     'на территории и в зонах без продукции.'),
    ('Когда нужно обновлять схему?',
     'При каждом переносе, добавлении или снятии точки, после перепланировки и смены зон хранения. Изменение '
     'записывают в журнал, а схема получает новую редакцию с датой и подписями сторон.'),
    ('Где хранить схему точек?',
     'В папке объекта вместе с программой пест-контроля и журналом и у исполнителя; удобно иметь и электронную копию. '
     'На проверке схему сверяют с журналом и с точками на месте, поэтому на объекте должна быть действующая редакция.'),
]

AUTHOR = NB.AUTHOR
PAGES = [
    {
        'key': 'akt', 'src': 'akt.html', 'out': 'materialy/akt-deratizatsii-i-dezinsektsii/index.html',
        'slug': 'materialy/akt-deratizatsii-i-dezinsektsii/', 'root': '../../',
        'title': 'Акт дератизации и дезинсекции: образец и бланк, что указать',
        'og_title': 'Акт дератизации и дезинсекции: образец и что в нём указать',
        'desc': 'Что указать в акте дератизации и дезинсекции: реквизиты, средства с СГР, результаты по точкам, подписи. '
                'Образец и бланк PDF. Акт по вашему объекту — после обследования, 3 000 ₽ с выездом.',
        'h1': 'Акт дератизации и дезинсекции: образец и что в нём указать',
        'crumbs': [('Главная', ''), ('Материалы', 'materialy/'),
                   ('Акт дератизации и дезинсекции', 'materialy/akt-deratizatsii-i-dezinsektsii/')],
        'og_image': 'akt-og.jpg', 'og_alt': 'Акт дератизации и дезинсекции: образец и что в нём указать',
        'hero': 'akt-hero', 'hero_alt': 'Специалист по пест-контролю в синей форме показывает акт обследования менеджеру '
                                        'по качеству в хлебопекарном цехе, на столе станция контроля грызунов',
        'faq': AKT_FAQ, 'faq_h2': 'Вопросы <em>об акте дератизации и дезинсекции</em>', 'faq_open': True,
        'types': TYPES, 'name': 'Акт дератизации и дезинсекции',
        'need': ['Акт по итогам обследования', 'Договор на обслуживание с актами', 'Проверить акты и журнал подрядчика'],
        # услуга: акт выдаём только после выезда и обследования объекта (решение владельца 11.11.2026)
        'service': {'name': 'Обследование объекта с выдачей акта дератизации и дезинсекции', 'price': '3000',
                    'desc': 'Стоимость 3 000 ₽ включает выезд специалиста. Акт выдаём только после обследования объекта: в нём — реальная ситуация '
                            'на объекте, находки по точкам контроля и рекомендации. Документ без обследования не продаём.'},
        'comment_ph': 'Комментарий: адрес, площадь, когда удобен выезд',
        'date_published': '2026-11-11', 'date_modified': '2026-11-11',
        'docs': [('Образец акта обследования и выполненных работ по дезинсекции и дератизации', AKT_PDF),
                 ('Бланк акта обследования и выполненных работ по дезинсекции и дератизации', AKT_BLANK)],
        'about': ['Акт дезинсекции', 'Акт дератизации', 'Акт выполненных работ', 'Документы для Роспотребнадзора'],
    },
    {
        'key': 'skhema', 'src': 'skhema.html', 'out': 'materialy/skhema-tochek-pest-kontrolya/index.html',
        'slug': 'materialy/skhema-tochek-pest-kontrolya/', 'root': '../../',
        'title': 'Схема точек пест-контроля: образец план-схемы ТПК в PDF',
        'og_title': 'Схема точек пест-контроля: образец и правила',
        'desc': 'Как составить схему точек пест-контроля (план-схему ТПК): контуры защиты, нумерация, обозначения, '
                'обновление. Интерактивный образец на 30 точек и PDF.',
        'h1': 'Схема точек пест-контроля: образец и правила',
        'crumbs': [('Главная', ''), ('Материалы', 'materialy/'),
                   ('Схема точек пест-контроля', 'materialy/skhema-tochek-pest-kontrolya/')],
        'og_image': 'skhema-og.jpg', 'og_alt': 'Схема точек пест-контроля: образец и правила',
        'hero': 'skhema-hero', 'hero_alt': 'На складе с мешками муки специалист по пест-контролю проверяет станцию '
                                           'контроля грызунов у стены, менеджер по качеству сверяет её с план-схемой точек',
        'faq': SK_FAQ, 'faq_h2': 'Вопросы <em>о схеме точек</em>', 'faq_open': True,
        'types': TYPES, 'name': 'Схема точек пест-контроля',
        'need': ['Заказать схему точек для объекта', 'Проверить схему и журнал подрядчика', 'Договор на обслуживание'],
        'comment_ph': 'Комментарий: площадь, этажи, есть ли схема сейчас',
        'date_published': '2026-11-11', 'date_modified': '2026-11-11',
        'docs': [('Образец план-схемы точек пест-контроля (форма СТПК-01)', SK_PDF)],
        'about': ['Схема точек пест-контроля', 'План-схема ТПК', 'ГОСТ Р 54762-2011', 'Мониторинг вредителей'],
    },
]


def json_ld(p):
    """Article с документами PDF, крошки и FAQ — вместо разметки нормативной базы (её json_ld для этих страниц не подходит)."""
    url = SITE + p['slug']
    crumbs = {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + s} for i, (n, s) in enumerate(p['crumbs'])]}
    faq = {'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': NB.plain(a)}} for q, a in p['faq']]}
    image = {'@type': 'ImageObject', 'url': SITE + 'img/' + p['og_image'], 'width': 1200, 'height': 630}
    hero = {'@type': 'ImageObject', 'url': SITE + 'img/' + p['hero'] + '.webp', 'width': 1920, 'height': 1072,
            'caption': p['hero_alt']}
    docs = [{'@type': 'DigitalDocument', 'name': n, 'encodingFormat': 'application/pdf', 'inLanguage': 'ru',
             'url': SITE + u, 'publisher': {'@id': SITE + '#org'}} for n, u in p['docs']]
    page = {'@type': 'Article', '@id': url + '#article', 'headline': p['h1'], 'description': p['desc'],
            'inLanguage': 'ru', 'datePublished': p['date_published'], 'dateModified': p['date_modified'],
            'author': AUTHOR, 'publisher': {'@id': SITE + '#org'}, 'mainEntityOfPage': url, 'image': [hero, image],
            'about': p['about'], 'isPartOf': {'@type': 'CollectionPage', '@id': SITE + 'materialy/#webpage',
                                              'url': SITE + 'materialy/', 'name': 'Материалы о пест-контроле'},
            'hasPart': docs if len(docs) > 1 else docs[0]}
    graph = [NB.ORG, crumbs, page, faq]
    if p.get('service'):
        sv = p['service']
        graph.append({'@type': 'Service', '@id': url + '#service', 'name': sv['name'], 'description': sv['desc'],
                      'serviceType': 'Дератизация и дезинсекция', 'provider': {'@id': SITE + '#org'},
                      'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
                      'offers': {'@type': 'Offer', 'price': sv['price'], 'priceCurrency': 'RUB', 'url': url + '#zakazat',
                                 'availability': 'https://schema.org/InStock'}})
    return ('<script type="application/ld+json">'
            + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False) + '</script>')


def side_html():
    """Панель между планом и образцом PDF (вариант А «плотная сетка», выбран владельцем 11.11.2026): контуры — они же фильтр
    точек — и типы точек со значками тех же цветов, что на плане, и числом точек; карточка точки — внизу панели (в разметке)."""
    c = S.counts()
    short = {'К1': 'Территория', 'К2': 'Периметр', 'К3': 'Помещения'}
    note = {'К1': 'ограждение, отмостка, ТКО', 'К2': 'ворота, доки, входы', 'К3': 'цех, склады, АБК'}
    tshort = {'КИК': 'станция с приманкой', 'МЛ': 'ловушка механическая / клеевая', 'ИМ': 'клеевой монитор насекомых',
              'ИЛ': 'световая УФ-ловушка', 'ФЛ': 'феромонная ловушка'}
    rows = ['<button type="button" class="sk-f is-on" data-f="" aria-pressed="true"><span class="sk-sw" aria-hidden="true">'
            + ''.join(f'<i class="dt" style="background:{col}"></i>' for _, col in S.K.values()) + '</span>'
            f'<span class="sk-f-t"><b>Все точки</b></span><span class="sk-f-n">{len(S.POINTS)}</span></button>']
    for k, (n, col) in S.K.items():
        rows.append(f'<button type="button" class="sk-f" data-f="{k}" aria-pressed="false"><span class="sk-sw" aria-hidden="true">'
                    f'<i class="ln{" dot" if k == "К3" else ""}" style="border-color:{col}"></i></span>'
                    f'<span class="sk-f-t"><b>{k} · {short[k]}</b><small>{note[k]}</small></span><span class="sk-f-n">{c[k]}</span></button>')
    types = []
    for t, (name, kind) in S.T.items():
        icon = f'<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">{S.mark(kind, 12, 12, S.TC[t], 7)}</svg>'
        types.append(f'<li data-t="{t}"><span class="sk-ico">{icon}</span><span class="skg-ty"><b>{t}</b> — {tshort[t]}</span>'
                     f'<span class="skg-n">{sum(1 for x in S.POINTS if x[0].startswith(t + "-"))}</span></li>')
    return ('<div class="skg-grp"><p class="sk-side-h">Контуры защиты</p><div class="sk-fs" role="group" aria-label="Показать точки контура">'
            + ''.join(rows) + '</div></div>\n<div class="skg-grp"><p class="sk-side-h">Типы точек</p><ul class="sk-types">'
            + ''.join(types) + '</ul></div>')


# скрипт плана: фильтр по контуру и карточка точки из реестра; цели Метрики на скачивание PDF
PLAN_JS = """(function(){var P=%s,K=%s,T=%s,C=%s,root=document.getElementById('skPlan'),info=document.getElementById('skInfo');
if(!root||!info)return;var pts=[].slice.call(root.querySelectorAll('.sk-pt')),sel=null;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function show(i){var p=P[i],k=K[p[1]],c=C[p[0].split('-')[0]];if(sel)sel.classList.remove('is-sel');sel=pts[i];sel.classList.add('is-sel');
info.innerHTML='<div class="sk-info-g"><b class="sk-info-c" style="color:'+c+'">'+esc(p[0])+'</b><span class="sk-info-t">'+esc(T[p[0].split('-')[0]])+'</span>'
+'<span class="sk-info-k" style="color:'+k[2]+'">'+esc(p[1])+' · '+esc(k[0])+'</span><span class="sk-info-p">'+esc(p[2])+'</span>'
+'<span class="sk-info-th">Порог: '+esc(p[3])+'</span></div>';}
pts.forEach(function(g,i){g.addEventListener('click',function(){show(i);});
g.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();show(i);}});});
var fs=[].slice.call(document.querySelectorAll('.sk-f')),pin='',tIn=0,tOut=0,fine=window.matchMedia('(hover:hover) and (pointer:fine)');
function fv(el){try{return el.matches(':focus-visible');}catch(_){return true;}}
function dim(test){root.classList.toggle('is-filt',!!test);pts.forEach(function(g){g.classList.toggle('is-dim',!!test&&!test(g));});}
function byK(f){return f?function(g){return g.getAttribute('data-k')===f;}:null;}
function byT(t){return function(g){return P[+g.getAttribute('data-i')][0].split('-')[0]===t;};}
function look(test){clearTimeout(tOut);clearTimeout(tIn);tIn=setTimeout(function(){dim(test);},90);}
function back(d){clearTimeout(tIn);clearTimeout(tOut);tOut=setTimeout(function(){dim(byK(pin));},d);}
fs.forEach(function(b){var f=b.getAttribute('data-f');
b.addEventListener('click',function(){clearTimeout(tIn);clearTimeout(tOut);pin=f;
fs.forEach(function(x){var on=x===b;x.classList.toggle('is-on',on);x.setAttribute('aria-pressed',on?'true':'false');});dim(byK(f));});
b.addEventListener('pointerenter',function(e){if(e.pointerType==='mouse'&&fine.matches)look(byK(f));});
b.addEventListener('focus',function(){if(fv(b)){clearTimeout(tOut);clearTimeout(tIn);dim(byK(f));}});
b.addEventListener('blur',function(){back(150);});});
[].forEach.call(document.querySelectorAll('.sk-types li[data-t]'),function(li){var t=li.getAttribute('data-t');
li.addEventListener('pointerenter',function(e){if(e.pointerType==='mouse'&&fine.matches)look(byT(t));});});
[].forEach.call(document.querySelectorAll('.sk-fs,.sk-types'),function(g){g.addEventListener('pointerleave',function(e){if(e.pointerType==='mouse')back(250);});});})();"""
GOALS_JS = ("document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('[data-dl]');if(!a)return;"
            "var g={'akt':'akt_obrazets','akt-blank':'akt_shablon','skhema':'skhema_obrazets'}[a.getAttribute('data-dl')];"
            "if(g)try{if(typeof ym==='function')ym(113675622,'reachGoal',g);}catch(_){}});")


def plan_js():
    def thr_text(t):  # как в реестре PDF: КИК — доля съеденной приманки, ИЛ и ФЛ — особей за 14 суток, остальные — любая находка
        if t == '0':
            return '0 — меры при любой находке'
        if t.endswith('%'):
            return t + ' съеденной приманки'
        num = int(t.split(' / ')[0])
        word = 'особь' if num % 10 == 1 and num % 100 != 11 else 'особи' if num % 10 in (2, 3, 4) and num % 100 not in (12, 13, 14) else 'особей'
        return f'{num}\u00a0{word} за\u00a0' + t.split(' / ')[1]
    pts = [[c, k, place, thr_text(thr)] for c, k, place, thr, *_ in S.POINTS]
    short = {'К1': 'территория', 'К2': 'периметр здания', 'К3': 'помещения'}
    ks = {k: [short[k], None, c] for k, (n, c) in S.K.items()}
    ks['К1'][2], ks['К2'][2], ks['К3'][2] = '#4ade80', '#94a3b8', '#7ca5ff'  # светлее — на тёмном фоне карточки
    ts = {t: n for t, (n, _) in S.T.items()}
    tc = {'КИК': '#f87171', 'МЛ': '#a78bfa', 'ИМ': '#2dd4bf', 'ИЛ': '#fbbf24', 'ФЛ': '#f472b6'}  # цвета типов S.TC, светлее
    return PLAN_JS % tuple(json.dumps(x, ensure_ascii=False) for x in (pts, ks, ts, tc))


def blank_html():
    """План на фирменном бланке ПЕСТКОНТРОЛЬ Центра — шапка и подвал как у PDF-образца (форма СТПК-01, tools/akt/build_akt.py)."""
    co = A.CO
    return ('<div class="skb">'
            '<div class="skb-wm" aria-hidden="true">пестконтроль-центр.рф</div>'
            f'<div class="skb-hd"><div class="skb-brand">{A.LOGO}<div><p class="skb-bn">ПЕСТКОНТРОЛЬ<small>ЦЕНТР</small></p>'
            '<p class="skb-bt">Пест-контроль для организаций · IPM / ХАССП</p></div></div>'
            f'<div class="skb-ct"><span>{A.IC_PHONE}<b>{co["phone"]}</b></span><span>{A.IC_GLOBE}<b>{co["site"]}</b></span></div></div>'
            '<div class="skb-meta"><span>Схема №&nbsp;<i>ПК-0917/26-С</i></span><span>Объект <i>Хлебопекарный цех, г.&nbsp;о.&nbsp;Химки</i></span>'
            '<span class="skb-badge">Образец заполнения</span><span class="skb-form">Форма СТПК-01 · ред.&nbsp;11.2026</span></div>'
            '<div class="skb-title"><div><p class="skb-ey">Пест-контроль · ГОСТ Р&nbsp;54762-2011, п.&nbsp;12.5</p>'
            '<p class="skb-h">План-схема</p><p class="skb-sub">точек пест-контроля (ТПК) объекта · приложение 1 к журналу пест-контроля №&nbsp;ПК-0917/26</p></div>'
            '<p class="skb-red">ред. <i>2 · 21.10.2026</i></p></div>'
            '<div class="skb-plan" id="skPlan"><!--SK_SVG--></div>'
            f'<div class="skb-ft"><b>ПЕСТКОНТРОЛЬ Центр</b> · {co["legal"]} · Лицензия Роспотребнадзора {co["lic"]} · {co["phone"]} · {co["site"]}</div>'
            '</div>')


def main():
    tpl = (ROOT / 'pishchevoe-proizvodstvo' / 'index.html').read_text(encoding='utf-8')
    icons = json.loads((ROOT / 'tools' / 'site' / 'icons.json').read_text(encoding='utf-8'))
    icons.update(json.loads((ROOT / 'tools' / 'normativnaya-baza' / 'icons-nb.json').read_text(encoding='utf-8')))
    NB.json_ld = json_ld  # своя разметка Article вместо разметки нормативной базы
    css = (HERE / 'page.css').read_text(encoding='utf-8').strip()
    with tempfile.TemporaryDirectory() as tmp:
        for p in PAGES:
            src = (HERE / p['src']).read_text(encoding='utf-8')
            if p['key'] == 'skhema':
                src = src.replace('<!--SK_PLAN-->', blank_html().replace('<!--SK_SVG-->', S.plan_svg(web=True))).replace('<!--SK_SIDE-->', side_html())
            f = pathlib.Path(tmp) / p['src']
            f.write_text(src, encoding='utf-8')
            q = dict(p, src=str(f))
            NB.build(q, tpl, icons)
            out = ROOT / p['out']
            s = out.read_text(encoding='utf-8')
            marker = '</style>\n<script type="application/ld+json">'
            assert s.count(marker) == 1, 'не найден конец стилей'
            s = s.replace(marker, '\n' + css + marker, 1)
            js = GOALS_JS + (plan_js() if p['key'] == 'skhema' else '')
            assert s.endswith('</body>\n</html>\n')
            s = s[:-len('</body>\n</html>\n')] + '<script>' + js + '</script>\n</body>\n</html>\n'
            out.write_text(s, encoding='utf-8')
            print('  + стили и скрипт страницы', p['key'])


if __name__ == '__main__':
    main()
