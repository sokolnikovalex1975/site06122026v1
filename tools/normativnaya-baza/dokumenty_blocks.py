"""Генерируемые блоки страницы «Документы для Роспотребнадзора» (dokumenty.html).

Данные — data/dokumenty.json: выгрузка из content.py чек-листа PDF (папка проекта «Страница Документы для Роспотребнадзора»,
скрипт export_site_json.py). Таблицы страницы, конструктор и PDF собираются из одних данных и не расходятся.

Метки в dokumenty.html:
    <!--DK_GROUPS-->    восемь карточек групп (блок «Какие документы нужны»)
    <!--DK_PICK-->      кнопки видов объектов конструктора
    <!--DK_TABLES-->    восемь разделов с таблицами (группы 1–8) и пояснениями под ними
    <!--DK_OBJECTS-->   «Что добавить к общему списку» по видам объектов (вкладки / аккордеон)
    <!--DK_TIMELINE-->  «Что пересмотреть в папке в 2027 году»
    <!--DK_DATA-->      данные конструктора (JSON) для dokumenty.js
"""
import html
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DATA = json.loads((HERE / 'data' / 'dokumenty.json').read_text(encoding='utf-8'))
PDF = '@/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/chek-list-dokumentov-dlya-rospotrebnadzora.pdf'
# образец и бланк акта (форма АПК-01, tools/akt/build_akt.py) — карточка под таблицей «Акты» и ссылки в строках 3.2 и 3.4
AKT_PDF = '@/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/obrazets-akta-dezinsektsii-i-deratizatsii.pdf'
AKT_BLANK = '@/normativnaya-baza/dokumenty-dlya-rospotrebnadzora/blank-akta-dezinsektsii-i-deratizatsii.pdf'
# ссылки сайта в графе «Образец или услуга», которых нет в выгрузке data/dokumenty.json (подставляются, только если графа пуста)
LINK_EXTRA = {
    '3.2': '<a href="#obrazets-akta">Образец акта</a>',
    '3.4': '<a href="#obrazets-akta">Образец акта</a>, <a href="@/materialy/akt-deratizatsii-i-dezinsektsii/">что в нём указать</a>',  # страница акта — с 11.11.2026
}

# заголовки H2 разделов: акцент курсивом, как на остальных страницах; тексты H2 — из согласованного черновика
H2 = {
    'programmy': 'Организационные документы <em>и программы</em>',
    'dogovory': 'Какие договоры нужны <em>для Роспотребнадзора</em>',
    'akty': 'Акты: <em>чем подтвердить, что работы выполнены</em>',
    'protokoly': 'Протоколы <em>лабораторных исследований</em>',
    'zhurnaly': 'Журналы <em>и графики</em>',
    'personal': 'Документы на персонал: <em>медкнижки, медосмотры, гигиеническая аттестация</em>',
    'ispolnitel': 'Документы исполнителя, <em>которые должны храниться у вас</em>',
    'produkciya': 'Документы на продукцию <em>и средства</em>',
}
# карточки «восемь групп»: что входит (согласованный текст блока 2)
GROUP_DESC = {
    'programmy': 'Учредительные документы, приказы об ответственных, программа производственного контроля, программа пест-контроля.',
    'dogovory': 'На дезинсекцию и дератизацию, лабораторные исследования, вывоз отходов, медосмотры, а по ситуации — на стирку, вентиляцию, ртутные лампы.',
    'akty': 'Обследований и обработок, мусорокамер и контейнерной площадки, работ по вентиляции.',
    'protokoly': 'Смывы, воздух, микроклимат и освещённость, вода, продукция, легионеллы. Все исследования делает наша лаборатория.',
    'zhurnaly': 'Пест-контроль, вентиляция, уборки, а в общепите и торговле — температура, влажность и осмотр работников.',
    'personal': 'Медкнижки, медосмотры, гигиеническая аттестация.',
    'ispolnitel': 'Лицензия, свидетельства о госрегистрации средств, инструкции.',
    'produkciya': 'Накладные, декларации, сертификаты, технологические карты.',
}
GROUP_SHORT = {  # подпись карточки: короче названия раздела
    'programmy': 'Организационные документы и программы', 'dogovory': 'Договоры', 'akty': 'Акты',
    'protokoly': 'Протоколы лабораторных исследований', 'zhurnaly': 'Журналы и графики', 'personal': 'Документы на персонал',
    'ispolnitel': 'Документы исполнителя', 'produkciya': 'Документы на продукцию и средства',
}
EXT = ' target="_blank" rel="noopener"'
U_LICREG = 'https://fp.rospotrebnadzor.ru/licen/'
U_SANPIN4282 = 'https://base.garant.ru/414329257/53f89421bbdaf741eb2d1ecc4ddb4c33/'
U_GIG229 = 'https://ppt.ru/news/medknijka/gigienicheskuyu-podgotovku-rabotnikov-razreshat-prohodit-samostoyatelno'
U_GIGPROEKT = 'https://cntd.ru/news/read/pravitelstvo-predlozilo-obnovit-poriadok-gigieniceskoi-podgotovki-rabotnikov'
# пояснения под таблицами (согласованный текст блоков 4–10)
AFTER = {
    'programmy': '<p class="nb-after">Программу производственного контроля и программу пест-контроля сверяют между собой: кратность обследований, зоны и исполнитель должны совпадать. Образцы обеих программ — в разделе <a href="@/materialy/">«Материалы»</a>.</p>',
    'dogovory': f'<p class="nb-after">Своими силами для собственных нужд дезинсекцию и дератизацию можно проводить без лицензии и без договора, но программа, журналы и учёт обследований всё равно нужны. Лицензию подрядчика проверяют в <a href="{U_LICREG}"{EXT}>реестре Роспотребнадзора</a>.</p>',
    'akty': ('<div class="card dk-akt"><h3 class="dk-akt-h">Что должно быть в акте дезинсекции и дератизации</h3>'
             '<p>Единой обязательной формы акта нет. Чтобы акт подтверждал работу на проверке, в нём указывают:</p><ul>'
             '<li>дату и время начала и окончания работ;</li><li>адрес и помещения, где проводили обследование или обработку;</li>'
             '<li>вид работ: обследование, профилактика, дезинсекция, дератизация;</li><li>вредителей и результаты обследования по точкам контроля;</li>'
             '<li>средство, номер свидетельства о госрегистрации, концентрацию и способ применения;</li>'
             '<li>меры безопасности и когда можно вернуться в помещения;</li>'
             '<li>исполнителя, номер его лицензии, подписи исполнителя и представителя объекта.</li></ul>'
             f'<p>В общепите время обработки особенно важно: во время дезинсекции и дератизации нельзя хранить и готовить продукцию, а распыляемые и рассыпаемые средства нельзя применять при посетителях и персонале (п. 45 <a href="{U_SANPIN4282}"{EXT}>СанПиН 2.3/2.4.4282-26</a>).</p></div>'
             # образец акта (с 08.11.2026): та же карточка, что у чек-листа PDF в блоке «Восемь групп»
             '<div class="card dk-pdfcard dk-aktcard" id="obrazets-akta">'
             f'<a class="dk-cover" href="{AKT_PDF}" download data-dl="akt" tabindex="-1" aria-hidden="true"><img src="@/img/akt-obrazets-p1-360.webp" '
             'srcset="@/img/akt-obrazets-p1-360.webp 360w, @/img/akt-obrazets-p1-720.webp 720w" sizes="(max-width:760px) 64px, 132px" '
             'width="360" height="509" alt="" loading="lazy" decoding="async"></a>'
             '<div class="dk-pdfcard-t"><p class="dk-pdfcard-k">Образец акта · PDF, 2 листа</p>'
             '<p>Так выглядит наш акт по каждому визиту: время работ, обследование по точкам контроля, средства с концентрацией и номером СГР, '
             'условия обработки, контроль эффективности и рекомендации — всё из списка выше. Данные заказчика в образце скрыты, бланк — та же форма без записей. '
             'Разбор реквизитов и частых ошибок — на странице <a href="@/materialy/akt-deratizatsii-i-dezinsektsii/">«Акт дератизации и дезинсекции»</a>.</p></div>'
             f'<div class="dk-aktcard-b"><a class="btn btn-w btn-lg" href="{AKT_PDF}" download data-dl="akt"><span class="btn-t">Скачать образец</span></a>'
             f'<a class="btn btn-o btn-lg" href="{AKT_BLANK}" download data-dl="akt-blank"><span class="btn-t">Бланк для печати</span></a></div></div>'),
    'protokoly': '<p class="nb-after">Все исследования из этой таблицы выполняет наша лаборатория: отбираем пробы на объекте и передаём протоколы. Цены и расчёт — на странице <a href="@/laboratornye-issledovaniya/">«Лабораторные исследования»</a>. Смывы и пробы воздуха входят и в <a href="@/sanitarnyy-audit/">санитарный аудит</a>.</p>',
    'personal': f'<p class="nb-after">Порядок гигиенической подготовки могут изменить. Законопроект, внесённый в Госдуму 07.10.2026, предлагает проходить её при поступлении на работу и затем раз в 5 лет, с самостоятельной подготовкой и электронной оценкой. Если закон примут, изменения вступят в силу с 01.09.2027, а пока действует приказ № 229 (<a href="{U_GIG229}"{EXT}>ppt.ru</a>, <a href="{U_GIGPROEKT}"{EXT}>Техэксперт</a>).</p>',
    'ispolnitel': '<p class="nb-after">Попросите подрядчика передать эти документы вместе с договором: без них инспектор не увидит, кто и чем обрабатывал объект.</p>',
}
# названия отраслевых страниц для ссылок из разделов по объектам
PAGE_NAMES = {
    '/pishchevoe-proizvodstvo/': 'Пест-контроль на пищевом производстве',
    '/restorany-i-kafe/': 'Пест-контроль ресторанов и кафе',
    '/magaziny-i-torgovye-seti/': 'Пест-контроль для магазинов и торговых сетей',
    '/sklady-i-logistika/': 'Пест-контроль для складов и логистики',
    '/farmatsevticheskie-proizvodstva/': 'Пест-контроль фармацевтического производства по GMP',
    '/gostinitsy/': 'Пест-контроль гостиниц и отелей',
}
OURS = '<span class="dk-ours" title="Делаем мы">●<span class="sr-only"> — делаем мы</span></span>'


def docs_word(n):
    """«41 документ», «44 документа», «49 документов»."""
    if n % 10 == 1 and n % 100 != 11:
        return 'документ'
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return 'документа'
    return 'документов'


def esc(s):
    return html.escape(s, quote=False)


def groups_cards():
    out = []
    for g in DATA['groups']:
        k = g['key']
        out.append(f'      <a class="card dk-g" href="#{k}"><span class="dk-g-n">{g["n"]:02d}</span>'
                   f'<b>{esc(GROUP_SHORT[k])}</b><span class="dk-g-d">{esc(GROUP_DESC[k])}</span>'
                   f'<span class="dk-g-c">{len(g["items"])} пунктов →</span></a>')
    return '\n'.join(out)


def pick_buttons():
    out = []
    for o in DATA['objects']:
        out.append(f'<button type="button" class="dk-pick" data-obj="{o["code"]}" data-slug="{o["slug"]}" aria-pressed="false">'
                   f'<span>{esc(o["name"])}</span><small>{o["count"]}</small></button>')
    return '\n        '.join(out)


def table(g):
    rows = []
    for it in g['items']:
        if not it['link_html'] and it['id'] in LINK_EXTRA:
            it = dict(it, link_html=LINK_EXTRA[it['id']])
        num = it['id'] + (OURS if it['ours'] else '')
        doc = f'<b>{esc(it["title"])}</b>' + (f'<span class="dk-note">{esc(it["note"])}</span>' if it['note'] else '')
        rows.append(f'        <tr id="p{it["id"].replace(".", "-")}"><td data-l="№" class="dk-n">{num}</td><td data-l="Документ">{doc}</td>'
                    f'<td data-l="Кто готовит">{esc(it["who"])}</td><td data-l="Основание">{it["basis_html"]}</td>'
                    f'<td data-l="Для кого">{esc(it["for_whom"])}</td>'
                    + (f'<td data-l="Образец или услуга">{it["link_html"]}</td></tr>' if it['link_html']
                       else '<td data-l="Образец или услуга" class="dk-0">—</td></tr>'))  # dk-0: на телефоне строку без ссылки не показываем
    return ('    <div class="dk-tw"><table class="d-table nb-tbl dk-tbl">\n'
            '      <thead><tr><th scope="col">№</th><th scope="col">Документ</th><th scope="col">Кто готовит</th>'
            '<th scope="col">Основание</th><th scope="col">Для кого</th><th scope="col">Образец или услуга</th></tr></thead>\n'
            '      <tbody>\n' + '\n'.join(rows) + '\n      </tbody>\n    </table></div>')


def tables():
    out = []
    for g in DATA['groups']:
        k = g['key']
        out.append(f'<section class="s dk-sec" id="{k}">\n  <div class="wrap">\n'
                   f'    <div class="head"><div class="eyebrow">Группа {g["n"]} из 8</div><h2>{H2[k]}</h2>'
                   f'<p class="sub">{esc(g["lead"])}</p></div>\n'
                   + table(g) + '\n' + (('    ' + AFTER[k] + '\n') if k in AFTER else '') + '  </div>\n</section>\n')
    return '\n'.join(out)


def objects():
    by_id = {it['id']: it for g in DATA['groups'] for it in g['items']}
    tabs, panels = [], []
    for i, o in enumerate(DATA['objects']):
        c = o['code']
        tabs.append(f'<button type="button" role="tab" class="dk-tab" id="dk-tab-{c}" aria-controls="obj-{c}" '
                    f'aria-selected="{"true" if i == 0 else "false"}" data-obj="{c}">{esc(o["name"])}</button>')
        if o['extra']:
            lis = []
            for pid in o['extra']:
                it = by_id[pid]
                cond = it['cond_for'].get(c) or it['cond']
                lis.append(f'<li><a href="#p{pid.replace(".", "-")}" class="dk-x-n">{pid}</a> {esc(it["title"])}'
                           + (f' <span class="dk-x-c">({esc(cond)})</span>' if cond else '') + '</li>')
            add = f'<ul class="dk-x">{"".join(lis)}</ul>'
        else:
            add = '<p class="dk-x-none">Ничего — подходит общий список.</p>'
        imp = ''.join(f'<li>{esc(x)}</li>' for x in o['important'])
        page = (f'<p class="dk-o-page"><a href="@{o["page"]}">{esc(PAGE_NAMES.get(o["page"], o["name"]))} →</a></p>'
                if o['page'] else '')
        panels.append(
            f'      <details class="dk-o" id="obj-{c}" data-obj="{c}"{" open" if i == 0 else ""}>'
            f'<summary>{esc(o["name"])}<small>{o["count"]} {docs_word(o["count"])}</small></summary>'
            f'<div class="dk-o-b" role="tabpanel" aria-labelledby="dk-tab-{c}">'
            f'<div class="dk-o-col"><p class="dk-o-k">Добавьте к общему списку</p>{add}'
            f'<p class="dk-o-k">Проверочный лист</p><p class="dk-o-cl">{esc(o["checklist"])}</p></div>'
            f'<div class="dk-o-col"><p class="dk-o-k">Что важно</p><ul class="dk-imp">{imp}</ul>{page}</div>'
            f'</div></details>')
    return ('    <div class="dk-objs" data-dk-tabs>\n      <div class="dk-tabs" role="tablist" aria-label="Вид объекта">'
            + ''.join(tabs) + '</div>\n' + '\n'.join(panels) + '\n    </div>')


def timeline():
    rows = []
    for d in DATA['deadlines']:
        rows.append(f'      <li class="is-next"><span class="nb-tl-d">{esc(d["date"])}</span><p class="nb-tl-w">{esc(d["text"])}</p>'
                    f'<p class="nb-tl-a"><span class="nb-tl-k">Источник</span><a href="{html.escape(d["src_url"])}"{EXT}>{esc(d["src_name"])}</a></p></li>')
    return '\n'.join(rows)


def builder_data():
    """Компактные данные конструктора: группы и пункты (номер, название, кто готовит, для каких объектов, условие)."""
    groups = [[g['n'], g['title']] for g in DATA['groups']]
    items = []
    for g in DATA['groups']:
        for it in g['items']:
            obj = 0 if it['obj'] == 'all' else it['obj']
            opt = 1 if it['cond'] else (it['cond_for'] if it['cond_for'] else 0)
            items.append([it['id'], it['title'], it['who'], g['n'], obj, opt, 1 if it['ours'] else 0])
    objs = [[o['code'], o['name'], o['slug']] for o in DATA['objects']]
    return json.dumps({'g': groups, 'i': items, 'o': objs}, ensure_ascii=False, separators=(',', ':'))


def render(main):
    main = main.replace('<!--DK_GROUPS-->', groups_cards())
    main = main.replace('<!--DK_PICK-->', pick_buttons())
    main = main.replace('<!--DK_TABLES-->', tables())
    main = main.replace('<!--DK_OBJECTS-->', objects())
    main = main.replace('<!--DK_TIMELINE-->', timeline())
    main = main.replace('DK_PDF', PDF)
    return main
