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
        'desc': 'Что указать в акте дератизации и дезинсекции, чтобы он подтвердил работу на проверке: реквизиты, '
                'средства с СГР, результаты по точкам, подписи. Образец и бланк PDF.',
        'h1': 'Акт дератизации и дезинсекции: образец и что в нём указать',
        'crumbs': [('Главная', ''), ('Материалы', 'materialy/'),
                   ('Акт дератизации и дезинсекции', 'materialy/akt-deratizatsii-i-dezinsektsii/')],
        'og_image': 'akt-og.jpg', 'og_alt': 'Акт дератизации и дезинсекции: образец и что в нём указать',
        'hero': 'akt-hero', 'hero_alt': 'Специалист по пест-контролю в синей форме передаёт акт на планшете менеджеру '
                                        'по качеству, она подписывает его в хлебопекарном цехе',
        'faq': AKT_FAQ, 'faq_h2': 'Вопросы <em>об акте дератизации и дезинсекции</em>', 'faq_open': True,
        'types': TYPES, 'name': 'Акт дератизации и дезинсекции',
        'need': ['Договор на обслуживание с актами', 'Проверить акты и журнал подрядчика', 'Разовая обработка с актом'],
        'comment_ph': 'Комментарий: площадь, вредители, кто сейчас обслуживает',
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
        'need': ['Составить схему точек для объекта', 'Проверить схему и журнал подрядчика', 'Договор на обслуживание'],
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
    return ('<script type="application/ld+json">'
            + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False) + '</script>')


def legend_html():
    cont = ''.join(f'<span><i class="ln{" dot" if k == "К3" else ""}" style="border-color:{c}"></i>{k} — {n.lower() if k != "К2" else "периметр здания"}</span>'
                   for k, (n, c) in S.K.items())
    types = ''.join(f'<span>{svg.replace("#3f3f46", "currentColor")}<b>{t}</b>&nbsp;— {n[0].lower() + n[1:]}</span>'
                    for t, n, svg in S.legend_items())
    return cont + types


# скрипт плана: фильтр по контуру и карточка точки из реестра; цели Метрики на скачивание PDF
PLAN_JS = """(function(){var P=%s,K=%s,T=%s,root=document.getElementById('skPlan'),info=document.getElementById('skInfo');
if(!root||!info)return;var pts=[].slice.call(root.querySelectorAll('.sk-pt')),sel=null;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function show(i){var p=P[i],k=K[p[1]];if(sel)sel.classList.remove('is-sel');sel=pts[i];sel.classList.add('is-sel');
info.innerHTML='<div class="sk-info-g"><b class="sk-info-c" style="color:'+k[2]+'">'+esc(p[0])+'</b><span class="sk-info-t">'+esc(T[p[0].split('-')[0]])+'</span>'
+'<span class="sk-info-k" style="color:'+k[2]+'">'+esc(p[1])+' · '+esc(k[0])+'</span><span class="sk-info-p">'+esc(p[2])+'</span>'
+'<span class="sk-info-th">Порог: '+esc(p[3])+'</span></div>';}
pts.forEach(function(g,i){g.addEventListener('click',function(){show(i);});
g.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();show(i);}});});
[].forEach.call(document.querySelectorAll('.sk-f'),function(b){b.addEventListener('click',function(){var f=b.getAttribute('data-f');
[].forEach.call(document.querySelectorAll('.sk-f'),function(x){var on=x===b;x.classList.toggle('is-on',on);x.setAttribute('aria-pressed',on?'true':'false');});
pts.forEach(function(g){g.classList.toggle('is-dim',!!f&&g.getAttribute('data-k')!==f);});});});})();"""
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
    ks['К1'][2], ks['К2'][2], ks['К3'][2] = '#4ade80', '#fb923c', '#7ca5ff'  # светлее — на тёмном фоне карточки
    ts = {t: n for t, (n, _) in S.T.items()}
    return PLAN_JS % tuple(json.dumps(x, ensure_ascii=False) for x in (pts, ks, ts))


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
                src = src.replace('<!--SK_PLAN-->', S.plan_svg(web=True)).replace('<!--SK_LEGEND-->', legend_html())
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
