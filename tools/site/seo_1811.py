#!/usr/bin/env python3
"""SEO-правки по аудиту 17.11.2026 — разрешены владельцем 18.11.2026 в 13:53 МСК, выкладка 22.11.2026.

    python3 tools/site/seo_1811.py            # правит страницы репозитория
    python3 tools/site/seo_1811.py --check    # только проверка (код 1, если где-то правки нет)

Решение владельца 18.11.2026 по пакетам проекта «СЕО Пестконтроль-центр» (seo-agent/drafts/2026-11-17-*.md):
«правки выложить на сайт: Title и H1 из PR #1 12 страниц под запросы ядра и title главной; внутренние ссылки —
10 пунктов лаборатории в подвале и 21 ссылка в тексте; технические правки — переадресации, index.php, lastmod,
разметка, og:image, 404», шесть текстовых блоков — «вноси на сайт». Title и H1 12 страниц — шаги meta_titles.py
(TITLE_CORE) и h1_core.py, на Timeweb опубликованы 19.11.2026 в 15:20 МСК (пакет title-h1-2026-11-19); здесь — всё
остальное, что меняется в самих страницах:

  * title главной: «Пест-контроль предприятий по системе IPM — ПЕСТКОНТРОЛЬ Центр» (и name в разметке WebPage);
  * подвал всех страниц: 7 подпунктов лаборатории в колонке «Услуги» (после «Лабораторные исследования», оформление
    подпунктов ft-sub, как у ресторанов в «Отраслях») и 3 лабораторных материала в колонке «Материалы» (перед «Все
    материалы»); ссылки относительные, на своей странице — «./» и aria-current="page", как у остальных пунктов;
  * 21 ссылка в тексте шести страниц: ссылками становятся слова, которые уже стоят на странице;
  * шесть текстовых блоков — текст дословно из seo-agent/drafts/2026-11-17-text-blocks.md;
  * разметка: @graph (Service, FAQPage, BreadcrumbList) у пищевого производства вместо одной цепочки, символ
    неразрывного пробела вместо &nbsp; в разметке ресторанов, новый вопрос — и в FAQPage анализа воды;
  * og:image (+ type, width, height, alt и twitter:card) у главной, пищевого производства и статьи «Пест-менеджмент или
    разовая обработка»; у главной ещё og:url. Картинки 1200×630 — img/home-og.jpg, img/pishchevoe-og.jpg,
    img/pest-menedzhment-og.jpg (из фото первого экрана этих страниц).

Переадресации, ErrorDocument 404 и lastmod — server/.htaccess и server/sitemap.xml (tools/site/seo_server.py), страница
404 — tools/site/page_404.py. Шаг tools/site/build_site.py после zayavka.py и перед tracking_laws.py; changes() и patch()
применимы и к живым index.php с Timeweb (пакет выкладки tools/deploy/prepare-2026-11-22-seo.py: для каждой из 43 страниц
сайта замены те же, что для страницы репозитория). Повторный запуск ничего не меняет. Счётчики, телефон и почта не
затрагиваются.
"""
import html as H
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
from typo import typo  # noqa: E402  неразрывный пробел после коротких слов, как в остальных текстах сайта

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
NB = '\u00a0'
LAB = 'laboratornye-issledovaniya/'
MARK = 'seo-1811'  # id стилей этого шага

HOME_TITLE = ('Пест-контроль для бизнеса в Москве и области — ПЕСТКОНТРОЛЬ Центр',
              'Пест-контроль предприятий по системе IPM — ПЕСТКОНТРОЛЬ Центр')

# ---------- подвал ----------
FT_LAB = [  # колонка «Услуги», после «Лабораторные исследования»
    (LAB + 'analiz-smyvov/', 'Анализ смывов'),
    (LAB + 'analiz-vody/', 'Анализ воды'),
    (LAB + 'analiz-vozdukha-rabochey-zony/', 'Анализ воздуха рабочей зоны'),
    (LAB + 'analiz-pishchevykh-produktov/', 'Анализ пищевых продуктов'),
    (LAB + 'izmerenie-mikroklimata/', 'Измерение микроклимата'),
    (LAB + 'zamer-osveshchennosti/', 'Замер освещённости'),
    (LAB + 'kontrol-sterilizatorov/', 'Контроль стерилизаторов'),
]
FT_MAT = [  # колонка «Материалы», перед «Все материалы»
    ('materialy/kak-berut-smyvy/', 'Как берут смывы'),
    ('materialy/kontrol-raboty-sterilizatorov/', 'Контроль работы стерилизаторов'),
    ('materialy/zamer-osveshchennosti-i-mikroklimata/', 'Замер освещённости и' + NB + 'микроклимата'),
]


def href(path, target):
    """Относительная ссылка, как на сайте: от страницы к корню и от корня к цели; своя страница — «./»."""
    return './' if target == path else '../' * path.count('/') + target


def ft_a(path, target):
    if target == path:
        return '<a href="./" aria-current="page">'
    return '<a href="%s">' % href(path, target)


def a(path, target, text, cls='ctx-a'):
    return '<a class="%s" href="%s">%s</a>' % (cls, href(path, target), text)


# ---------- текстовые блоки (дословно из seo-agent/drafts/2026-11-17-text-blocks.md) ----------

def tp(text):
    return typo(text)


def section(sid, eyebrow, h2, h2_em, sub, items):
    lis = ''.join('\n      <li>%s</li>' % tp(x) for x in items)
    return ('<section class="s" id="%s">\n  <div class="wrap">\n    <div class="head">\n'
            '      <div class="eyebrow" data-eyebrow>%s</div>\n'
            '      <h2 data-split>%s <em>%s</em></h2>\n'
            '      <p class="sub" data-fade>%s</p>\n'
            '    </div>\n    <ul class="d-ticks" data-group="ctalist">%s\n    </ul>\n  </div>\n</section>\n\n'
            % (sid, tp(eyebrow), tp(h2), tp(h2_em), tp(sub), lis))


NW = '<span class="nw">%s</span>'
LICENSE_URL = ('https://fp.rospotrebnadzor.ru/licen/?oper=search&amp;numb_history=&amp;numb=&amp;firmget_name=&amp;'
               'ogrn_inn_nza=7714462211')

SEC_DERAT = section(
    'unichtozhenie', 'Активный очаг', 'Уничтожение крыс и мышей', 'на предприятии',
    'Если грызуны уже появились, проводим истребительную дератизацию — подавляем активный очаг в производственном или '
    'складском здании, от 3' + NB + '500' + NB + '₽. Одного уничтожения мало: одновременно перекрываем пути захода и '
    'ставим станции по трём контурам, иначе крысы и мыши придут снова. По сигналу выезжаем за 3 часа, круглосуточно.',
    ['В цехах и на складах продукции — ловушки без токсичных приманок. Контейнеры с приманкой ставим только снаружи '
     'здания и крепим к основанию.',
     'Обработку нор в технической зоне или подвале назначаем на ночь, пересменку или санитарное окно — работа объекта '
     'не останавливается.',
     'Каждый визит подтверждаем записью в журнале и актом.'])

SEC_DEZINF = section(
    'kak-vybrat', 'Выбор подрядчика', 'Как выбрать фирму', 'для дезинфекции помещений',
    'Дезинфекция, дезинсекция и дератизация лицензируются с марта 2025 года, поэтому профессиональную дезинфекцию '
    'в Москве заказывают только у организации с лицензией. Проверьте запись в реестре лицензий Роспотребнадзора, '
    'уточните, какие документы останутся после выезда и кто делает лабораторный контроль. Наша лицензия — '
    '№ <a class="ctx-a" href="' + LICENSE_URL + '" target="_blank" rel="noopener noreferrer">'
    + NW % 'Л064-00111-77/01942445' + '</a>.',
    ['После каждого выезда — акт и запись в журнале.',
     'Смывы и пробы воздуха — через аккредитованную лабораторию, с протоколом для программы производственного контроля.',
     'Заказать мастера по дезинфекции можно и на ночь или выходной: такие окна — без наценки, срочный выезд — за 3 часа '
     'по Москве и области.',
     'Работаем только с юридическими лицами.'])

SEC_DEZINS = section(
    'kruglosutochno', 'Срочный выезд', 'Компания для дезинсекции:', 'круглосуточный выезд',
    'Срочные и ночные выезды на дезинсекцию — круглосуточно. Если насекомые появились между плановыми визитами или '
    'нужна обработка перед проверкой, специалист выезжает в течение 3 часов по Москве и области. Плановая дезинсекция '
    'по договору — от 3' + NB + '500' + NB + '₽ в месяц, разовая обработка помещения — от 3' + NB + '500' + NB + '₽ '
    'за выезд, ночной выезд — без наценки.',
    ['До договора — бесплатный осмотр и расчёт.',
     'Чередуем действующие вещества разных групп, чтобы у насекомых не выработалась устойчивость.',
     'Работаем с НДС и без НДС (УСН); договор, акты и УПД — через ЭДО или на бумаге.'])

SEC_DD = section(
    'sanepidemstantsiya', 'Санэпидемстанция', 'Вызвать санэпидемстанцию:', 'кто сейчас делает санобработку',
    'Санэпидемстанцией по привычке называют и надзорный орган, и службу, которая уничтожает насекомых и грызунов. '
    'Проверяет предприятия Роспотребнадзор, а санобработку — дезинсекцию, дератизацию и дезинфекцию — по договору '
    'выполняют организации с лицензией. Мы работаем с юридическими лицами Москвы и Подмосковья по одному договору: '
    'комплекс дератизации и дезинсекции — от 4' + NB + '900' + NB + '₽ в месяц.',
    ['Один договор на грызунов и насекомых: общий график визитов и один комплект документов.',
     'Выезд и расчёт — бесплатно.',
     'После каждого визита — запись в журнале и акт; кратность — по пп. 101 и 110 ' + NW % 'СанПиН 3.3686-21' + '.'])

VODA_SUB = tp('Организации не нужно самой везти пробу в лабораторию. Специалист приезжает на объект в Москве или области '
              'и отбирает воду там, где её используют: из крана на кухне или в цехе, на вводе в здание или у скважины. '
              'Пробы везём в нашу лабораторию в термоконтейнере, микробиологическое исследование начинаем в день отбора.')
VODA_ITEMS = [
    'Химический анализ — от 737' + NB + '₽ за показатель, микробиологический — от 2' + NB + '350' + NB + '₽.',
    'Воду из собственной скважины проверяют 4 раза в год, по сезонам.',
    'В протоколе рядом с каждым результатом стоит норматив СанПиН ' + NW % '1.2.3685-21'
    + ' — документ кладут в папку производственного контроля.',
    'Точную сумму называем до выезда: она зависит от вида воды, набора показателей и числа точек отбора.',
]
VODA_Q = 'Где сдать воду на анализ в Москве?'
VODA_A = ('Пробу не нужно никуда везти. Мы выезжаем на объекты Москвы и Подмосковья, сами отбираем воду по ГОСТ 31942-2012 '
          'и ГОСТ Р 59024-2020 и доставляем её в нашу лабораторию. Работаем с организациями: общепитом, производствами, '
          'гостиницами, бассейнами и объектами со своей скважиной.')
VODA_A_HTML = tp(VODA_A.replace('ГОСТ 31942-2012', 'ГОСТ ' + NW % '31942-2012')
                 .replace('ГОСТ Р 59024-2020', 'ГОСТ Р ' + NW % '59024-2020'))

SMYVY_MR = tp(' Документ часто ищут как «МУК 0220», но это методические рекомендации — МР ' + NW % '4.2.0220-20'
              + ', утверждены Главным государственным санитарным врачом РФ 04.12.2020.')
SMYVY_BGKP = tp(' МР ' + NW % '4.2.0220-20' + ' относит к ним общие и термотолерантные колиформные бактерии (п. 3.1).')

# ---------- стили этого шага (только на страницах, где они нужны) ----------
LINK_CSS = '{color:var(--t1);border-bottom:1px solid rgba(124,134,255,.45);transition:border-color .25s}'
HOVER_CSS = '{border-color:var(--t1)}'
STYLE = {  # адрес страницы: селекторы ссылок
    'razrabotka-ppk/': '.ctx-a',
    'sanitarnyy-audit/': '.ctx-a',
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/': '.ctx-a',
    'dezinfektsiya/': '.ctx-a',
    LAB + 'analiz-vozdukha-rabochey-zony/': '.ctx-a,#voprosy .ans a',
}
VODA_GAP = '.lbs-ticks.ctx-gap{margin:0 0 clamp(32px,3vw,52px)}'


def style_block(path):
    sel = STYLE.get(path)
    extra = VODA_GAP if path == LAB + 'analiz-vody/' else ''
    if not sel and not extra:
        return ''
    css = ''
    if sel:
        hov = ','.join(x + ':hover' for x in sel.split(','))
        css = sel + LINK_CSS + hov + HOVER_CSS
    return ('<style id="%s">/* ссылки в тексте и новые блоки (tools/site/seo_1811.py, 18.11.2026) */%s%s</style>'
            % (MARK, css, extra))


# ---------- og:image ----------
OG = {  # адрес страницы: (картинка, alt)
    '': ('img/home-og.jpg', 'Чистая профессиональная кухня: моечная машина, мойка и стеллажи из нержавеющей стали'),
    'pishchevoe-proizvodstvo/': ('img/pishchevoe-og.jpg',
                                 'Специалист проверяет станцию контроля грызунов в цехе пищевого производства'),
    'materialy/pest-menedzhment-ili-razovaya-obrabotka/': (
        'img/pest-menedzhment-og.jpg', 'Пест-менеджер и инженер предприятия сверяют схему точек контроля на складе'),
}


def og_tags(path):
    img, alt = OG[path]
    tags = []
    if path == '':
        tags.append('<meta property="og:url" content="%s">' % SITE)
    tags += ['<meta property="og:image" content="%s%s">' % (SITE, img),
             '<meta property="og:image:type" content="image/jpeg">',
             '<meta property="og:image:width" content="1200">',
             '<meta property="og:image:height" content="630">',
             '<meta property="og:image:alt" content="%s">' % H.escape(alt),
             '<meta name="twitter:card" content="summary_large_image">']
    return '\n'.join(tags)


# ---------- разметка ----------
FOOD_FAQ_SEC = 'id="voprosy"'


def visible_faq(s):
    """Вопросы и ответы видимого блока «Вопросы» — текстом, как в разметке FAQPage."""
    a_ = s.find('<section class="s" id="voprosy"')
    b_ = s.find('</section>', a_)
    assert a_ > 0 and b_ > a_, 'нет блока вопросов'
    out = []
    for q, ans in re.findall(r'<button[^>]*>(.*?)<span class="pm"></span></button><div class="ans"[^>]*><div>(.*?)</div>'
                             r'</div>', s[a_:b_], re.S):
        out.append(tuple(re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', '', x)).replace(NB, ' ')).strip()
                         for x in (q, ans)))
    return out


def meta_content(s, name):
    m = re.search(r'<meta name="%s" content="([^"]*)">' % name, s)
    assert m, 'нет meta ' + name
    return H.unescape(m.group(1))


def food_graph(s, old_json):
    """@graph пищевого производства: цепочка — прежняя, Service — из description, FAQPage — из видимых вопросов."""
    crumbs = json.loads(old_json)
    assert crumbs.get('@type') == 'BreadcrumbList', 'на странице уже не одна цепочка'
    url = SITE + 'pishchevoe-proizvodstvo/'
    crumbs = {k: v for k, v in crumbs.items() if k != '@context'}
    faq = visible_faq(s)
    assert len(faq) == 7, 'вопросов на странице: %d' % len(faq)
    graph = {'@context': 'https://schema.org', '@graph': [
        crumbs,
        {'@type': 'Service', '@id': url + '#service', 'name': 'Пест-контроль на пищевом производстве',
         'serviceType': 'Дезинсекция и дератизация пищевых производств по договору (СанПиН 3.3686-21, ТР ТС 021/2011, '
                        'ГОСТ Р 54762-2011)',
         'description': meta_content(s, 'description'), 'url': url,
         'provider': {'@type': 'Organization', '@id': SITE + '#org', 'name': 'ПЕСТКОНТРОЛЬ Центр',
                      'legalName': 'ООО «Центр дезинфекционных услуг»', 'url': SITE,
                      'telephone': '+7 495 104-35-70', 'email': 'b2b@pestcontrol-center.ru'},
         'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
         'audience': {'@type': 'BusinessAudience', 'audienceType': 'Пищевые производства'}},
        {'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': t}} for q, t in faq]},
    ]}
    return json.dumps(graph, ensure_ascii=False, separators=(',', ':'))


def jsonld(s):
    return [m.group(1) for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)]


# ---------- поиск точного места ----------

def one(s, pattern, what):
    found = re.findall(pattern, s, re.S)
    assert len(found) == 1, '%s: найдено %d раз' % (what, len(found))
    m = re.search(pattern, s, re.S)
    return m.group(0)


SP = '[ \u00a0]'


# признак правки самой страницы (ссылки, текстовые блоки, разметка); подвал — отдельно, см. page_done()
MARKS = {'razrabotka-ppk/': 'analiz-pishchevykh-produktov/">Сырьё', 'deratizatsiya/': 'id="unichtozhenie"',
         'dezinfektsiya/': 'id="kak-vybrat"', 'dezinsektsiya/': 'id="kruglosutochno"',
         'deratizatsiya-i-dezinsektsiya/': 'id="sanepidemstantsiya"', LAB + 'analiz-vody/': 'class="d-ticks lbs-ticks ctx-gap"',
         'materialy/kak-berut-smyvy/': '«МУК 0220»', 'pishchevoe-proizvodstvo/': '"@graph"',
         'sanitarnyy-audit/': 'kak-berut-smyvy/">отбор смывов', LAB + 'analiz-vozdukha-rabochey-zony/':
         'zamer-osveshchennosti/">освещённость', 'materialy/programma-proizvodstvennogo-kontrolya-haccp/':
         'analiz-vody/">вода', 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/': 'izmerenie-mikroklimata/">Измерение'}


def page_done(path, s):
    """Правки самой страницы (title главной, ссылки и блоки текста, разметка, og:image, стили) уже стоят.
    Подвал проверяется отдельно: tools/menu/apply_menu.py в полной сборке пересобирает его без подпунктов
    лаборатории, и до 23.11.2026 шаг из-за этого пытался заново применить и правки страницы (сборка падала)."""
    checks = []
    if path == '':
        checks.append(HOME_TITLE[1] in s)
    if path in MARKS:
        checks.append(MARKS[path] in s)
    if path == 'restorany-i-kafe/':
        checks.append(all('&nbsp;' not in j for j in jsonld(s)))
    if path in OG:
        checks.append('og:image:alt' in s)
    if style_block(path):
        checks.append(('<style id="%s">' % MARK) in s)
    return all(checks)


def changes(path, s):
    """Замены страницы по порядку: [(было, стало, сколько раз)], посчитаны на тексте после предыдущих замен.
    Если правки уже есть — пустой список."""
    out = []

    def rep(old, new, count=1):
        nonlocal s
        assert old and old != new
        assert s.count(old) == count, '%s: «%s» найдено %d раз (ждали %d)' % (path or '/', old[:70], s.count(old), count)
        s = s.replace(old, new)
        out.append((old, new, count))

    footer_done = 'class="ft-sub"><a href="%s">Анализ смывов</a>' % href(
        path, LAB + 'analiz-smyvov/') in s or '<li class="ft-sub"><a href="./" aria-current="page">Анализ смывов</a>' in s

    # подвал
    if not footer_done:
        lab = '<li>%sЛабораторные исследования</a></li>' % ft_a(path, LAB)
        rep(lab, lab + ''.join('<li class="ft-sub">%s%s</a></li>' % (ft_a(path, t), x) for t, x in FT_LAB))
        allm = '<li>%sВсе материалы</a></li>' % ft_a(path, 'materialy/')
        rep(allm, ''.join('<li>%s%s</a></li>' % (ft_a(path, t), x) for t, x in FT_MAT) + allm)
    if page_done(path, s):
        return out

    # title главной
    if path == '':
        rep(HOME_TITLE[0], HOME_TITLE[1], 2)

    # ссылки в тексте и текстовые блоки
    if path == 'razrabotka-ppk/':
        for word, slug in (('Смывы', 'analiz-smyvov/'), ('Вода', 'analiz-vody/'),
                           ('Сырьё' + SP + 'и' + SP + 'продукция', 'analiz-pishchevykh-produktov/')):
            old = one(s, re.escape('<td data-l="Что исследуют">') + word + re.escape('</td>'), word)
            text = old[len('<td data-l="Что исследуют">'):-len('</td>')]
            rep(old, '<td data-l="Что исследуют">%s</td>' % a(path, LAB + slug, text))
        old = one(s, re.escape('<td data-l="Что определяют">микроклимат, освещённость, шум</td>'), 'Рабочие места')
        rep(old, '<td data-l="Что определяют">%s, %s, шум</td>' % (
            a(path, LAB + 'izmerenie-mikroklimata/', 'микроклимат'),
            a(path, LAB + 'zamer-osveshchennosti/', 'освещённость')))
    if path == 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/':
        cell = '<td data-l="Образец или услуга">'
        hub = cell + '<a href="%s">Лабораторные исследования</a></td></tr>' % href(path, LAB)

        def row(rid, old_cell, new_cell):
            r = one(s, '<tr id="%s">.*?</tr>' % rid, rid)
            assert r.count(old_cell) == 1, rid
            rep(r, r.replace(old_cell, new_cell))

        def lab_a(slug, text):
            return '<a href="%s">%s</a>' % (href(path, LAB + slug), text)
        row('p4-1', cell + '<a href="%s">Санитарный аудит</a></td></tr>' % href(path, 'sanitarnyy-audit/'),
            cell + lab_a('analiz-smyvov/', 'Анализ смывов') + ', <a href="%s">санитарный аудит</a></td></tr>'
            % href(path, 'sanitarnyy-audit/'))
        row('p4-3', hub, cell + lab_a('izmerenie-mikroklimata/', 'Измерение микроклимата') + ', '
            + lab_a('zamer-osveshchennosti/', 'замер освещённости') + '</td></tr>')
        row('p4-4', hub, cell + lab_a('analiz-vody/', 'Анализ воды') + '</td></tr>')
        row('p4-5', hub, cell + lab_a('analiz-pishchevykh-produktov/', 'Анализ пищевых продуктов') + '</td></tr>')
        row('p4-9', hub, cell + lab_a('kontrol-sterilizatorov/', 'Контроль стерилизаторов') + '</td></tr>')
        row('p4-10', hub, cell + lab_a('analiz-vody/', 'Анализ воды') + '</td></tr>')
        row('p4-11', hub, cell + lab_a('analiz-smyvov/', 'Анализ смывов') + '</td></tr>')
    if path == 'materialy/programma-proizvodstvennogo-kontrolya-haccp/':
        old = one(s, re.escape('<span>Лабораторный контроль: сырьё, продукция, смывы, воздух, вода, рабочие места'), 'Стр. 7–9')
        rep(old, '<span>Лабораторный контроль: сырьё, %s, %s, воздух, %s, рабочие места' % (
            a(path, LAB + 'analiz-pishchevykh-produktov/', 'продукция'), a(path, LAB + 'analiz-smyvov/', 'смывы'),
            a(path, LAB + 'analiz-vody/', 'вода')))
    if path == 'sanitarnyy-audit/':
        old = one(s, re.escape('<td data-l="На что смотрим при аудите">микроклимат, освещённость, шум'), 'Условия труда')
        rep(old, '<td data-l="На что смотрим при аудите">%s, %s, шум' % (
            a(path, LAB + 'izmerenie-mikroklimata/', 'микроклимат'), a(path, LAB + 'zamer-osveshchennosti/', 'освещённость')))
        old = one(s, 'отбор смывов' + SP + 'и' + SP + 'проб воздуха', 'Выезд: отбор смывов')
        rep(old, a(path, 'materialy/kak-berut-smyvy/', 'отбор смывов') + old[len('отбор смывов'):])
    if path == 'dezinfektsiya/':
        old = one(s, 'Микробиологические смывы с' + SP + 'поверхностей и' + SP + 'оборудования, пробы воздуха и' + SP
                  + 'исследования', '#kontrol')
        assert s.find(old) > s.find('<div class="d-card" id="kontrol">') > 0, 'ссылка не в карточке #kontrol'
        words = old[len('Микробиологические '):old.index(', пробы')]
        rep(old, 'Микробиологические ' + a(path, LAB + 'analiz-smyvov/', words) + old[old.index(', пробы'):])
        anchor = one(s, r'(?:<!-- =+ [^>]* =+ -->\n)?<section class="s" id="stoimost">', 'stoimost')
        rep(anchor, SEC_DEZINF + anchor)
    if path == LAB + 'analiz-vozdukha-rabochey-zony/':
        old = one(s, 'В' + NB + 'офисах контролируют микроклимат, освещённость и' + NB + 'другие факторы', 'вопрос об офисе')
        rep(old, old.replace('освещённость', a(path, LAB + 'zamer-osveshchennosti/', 'освещённость'), 1))
    if path == 'deratizatsiya/':
        anchor = one(s, r'(?:<!-- =+ [^>]* =+ -->\n)?<section class="s" id="stoimost">', 'stoimost')
        rep(anchor, SEC_DERAT + anchor)
    if path == 'dezinsektsiya/':
        anchor = one(s, r'(?:<!-- =+ [^>]* =+ -->\n)?<section class="s" id="stoimost">', 'stoimost')
        rep(anchor, SEC_DEZINS + anchor)
    if path == 'deratizatsiya-i-dezinsektsiya/':
        anchor = one(s, r'(?:<!-- =+ [^>]* =+ -->\n)?<section class="s" id="chto-vybrat">', 'chto-vybrat')
        rep(anchor, SEC_DD + anchor)
    if path == LAB + 'analiz-vody/':
        old = one(s, '<h2 data-split>Как заказать' + SP + '<em>анализ' + SP + 'воды</em></h2></div>', 'H2 Как заказать')
        rep(old, '<h2 data-split>%s <em>%s</em></h2><p class="sub" data-fade>%s</p></div>\n'
                 '    <ul class="d-ticks lbs-ticks ctx-gap" data-group="ctalist">%s\n    </ul>'
            % (tp('Как сдать воду на анализ,'), tp('в том числе из скважины'), VODA_SUB,
               ''.join('\n      <li>%s</li>' % tp(x) for x in VODA_ITEMS)))
        ids = [int(x) for x in re.findall(r'<button aria-expanded="(?:true|false)" aria-controls="a(\d+)" id="q\d+">', s)]
        n = max(ids) + 1
        assert ('id="q%d"' % n) not in s and ('id="a%d"' % n) not in s
        last = one(s, r'<div class="card qa"><button aria-expanded="(?:true|false)" aria-controls="a%d" id="q%d">.*?'
                      r'</p></div></div></div>' % (n - 1, n - 1), 'последний вопрос')
        rep(last, last + '\n        <div class="card qa"><button aria-expanded="false" aria-controls="a%d" id="q%d">'
                         '<span>%s</span><span class="pm"></span></button><div class="ans" id="a%d" role="region" '
                         'aria-labelledby="q%d"><div><p>%s</p></div></div></div>' % (n, n, tp(VODA_Q), n, n, VODA_A_HTML))
        blocks = [j for j in jsonld(s) if '"FAQPage"' in j]
        assert len(blocks) == 1, 'FAQPage анализа воды'
        data = json.loads(blocks[0])
        assert json.dumps(data, ensure_ascii=False) == blocks[0], 'разметка анализа воды записана иначе'
        faq = [x for x in data['@graph'] if x.get('@type') == 'FAQPage'][0]
        faq['mainEntity'].append({'@type': 'Question', 'name': VODA_Q,
                                  'acceptedAnswer': {'@type': 'Answer', 'text': VODA_A}})
        rep(blocks[0], json.dumps(data, ensure_ascii=False))
    if path == 'materialy/kak-berut-smyvy/':
        old = one(s, '<h2 data-split>Как читать' + SP + '<em>результат смывов</em></h2>', 'H2 Как читать')
        rep(old, '<h2 data-split>%s <em>%s</em></h2>' % (tp('Расшифровка смывов:'), tp('БГКП и стафилококк')))
        old = one(s, '<li><b>БГКП' + SP + re.escape('— бактерии группы кишечной палочки.</b>'), 'БГКП')
        rep(old, old + SMYVY_BGKP)
        old = one(s, 'которые заменили МУ' + SP + re.escape('<span class="nw">2657-82</span>.'), 'вводный абзац')
        rep(old, old + SMYVY_MR)

    # разметка
    if path == 'pishchevoe-proizvodstvo/':
        blocks = jsonld(s)
        assert len(blocks) == 1, 'пищевое производство: блоков разметки %d' % len(blocks)
        rep(blocks[0], food_graph(s, blocks[0]))
    if path == 'restorany-i-kafe/':
        old = one(s, r'"text": "Договор — от 3&nbsp;900&nbsp;₽ в месяц, разовая обработка — от 3&nbsp;500&nbsp;₽ за выезд',
                  '&nbsp; в разметке')
        rep(old, old.replace('&nbsp;', NB))
        assert all('&nbsp;' not in j for j in jsonld(s)), '&nbsp; в разметке ресторанов'

    # og:image
    if path in OG:
        assert 'og:image' not in s, 'og:image уже есть'
        old = one(s, r'<meta property="og:description" content="[^"]*">', 'og:description')
        rep(old, old + '\n' + og_tags(path))

    # стили
    css = style_block(path)
    if css:
        old = one(s, r'footer \.ft-company p\+p\{margin-top:4px\}</style>', 'ft-company-st')
        rep(old, old + '\n' + css)
    return out


def patch(path, s):
    for old, new, count in changes(path, s):
        assert s.count(old) == count
        s = s.replace(old, new)
    return s


def missing(path, s):
    """Чего нет на странице (для --check)."""
    bad = []
    if 'class="ft-sub">' + ft_a(path, LAB + 'kontrol-sterilizatorov/') + 'Контроль стерилизаторов</a></li>' not in s:
        bad.append('подвал: лаборатория')
    if '<li>' + ft_a(path, 'materialy/kak-berut-smyvy/') + 'Как берут смывы</a></li>' not in s:
        bad.append('подвал: материалы')
    if path == '' and HOME_TITLE[1] not in s:
        bad.append('title главной')
    if path in OG and 'og:image:alt' not in s:
        bad.append('og:image')
    if path in MARKS and MARKS[path] not in s:
        bad.append('правка страницы')
    return bad


def repo_pages():
    sys.path.insert(0, str(ROOT / 'tools' / 'site'))
    import build_prod
    return build_prod.PAGES + build_prod.LEGAL


def url_path(rel):
    return '' if rel in ('index.html', 'index.php') else rel.rsplit('/', 1)[0] + '/'


def main():
    check = '--check' in sys.argv[1:]
    changed, bad = [], []
    for rel in repo_pages():
        f = ROOT / rel
        s = f.read_text(encoding='utf-8')
        path = url_path(rel)
        if check:
            what = missing(path, s)
            if what:
                bad.append((path, what))
            continue
        new = patch(path, s)
        if new != s:
            f.write_text(new, encoding='utf-8')
            changed.append(path)
    if check:
        for path, what in bad:
            print('seo_1811:', path or '/', '—', ', '.join(what))
        print('seo_1811: страниц без правок 18.11.2026:', len(bad))
        sys.exit(1 if bad else 0)
    print('seo_1811: подвал, ссылки в тексте, текстовые блоки, разметка и og:image — изменено страниц:', len(changed))


if __name__ == '__main__':
    main()
