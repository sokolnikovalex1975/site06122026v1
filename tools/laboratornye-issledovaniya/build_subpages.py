#!/usr/bin/env python3
"""Страницы направлений раздела «Лабораторные исследования» и статьи о лабораторном контроле (11.11.2026).

Направления (/laboratornye-issledovaniya/<страница>/): анализ смывов, измерение микроклимата, замер освещённости,
анализ воздуха рабочей зоны, анализ пищевых продуктов, анализ воды, контроль стерилизаторов (со стерильностью и
бактерицидными облучателями). Статьи (/materialy/<статья>/): как берут смывы, как проходит замер освещённости
и микроклимата, контроль работы стерилизаторов. Решение — по анализу Кейсо 10.11.2026: страницы-лидеры собирают
кластер запросов направления; тонкие страницы ЭКОСЕТИ в топ-10 не попадают («Лабораторные исследования: анализ
Кейсо и структура страниц» в файлах проекта).

Тексты — pages/*.py (по файлу на страницу), цены — data.py (прайс ЭКОСЕТИ + 100 ₽), расчёт — calc.js, как на главной
странице раздела (общий расчёт между страницами, sessionStorage 'lb-calc'). Аккредитацию, юрлицо лаборатории и срок
выдачи протоколов не указываем (решение владельца 10.11.2026).

Шаблон — pishchevoe-proizvodstvo/index.html (как у главной раздела); страницы лежат на уровень глубже —
относительные пути шаблона '../' становятся '../../' (как в tools/normativnaya-baza/build_pages.py).

    python3 tools/laboratornye-issledovaniya/build_subpages.py   # build_site.py запускает его сам
"""
import html as H
import importlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
sys.path.insert(0, str(HERE))
import data as D  # noqa: E402
from textlib import typeset, plain, cut  # noqa: E402
from build_page import TYPE_SELECT, rub, pr, calc_data, AUTHOR, SITE  # noqa: E402

ORDER = ['smyvy', 'mikroklimat', 'osveshchennost', 'vrz', 'pishcha', 'voda', 'sterilizatory',
         'mat_smyvy', 'mat_zamery', 'mat_sterilizatory']
BYID = {it[0]: (g, it) for g, it in D.items()}
ORG = {'@type': 'Organization', '@id': SITE + '#org', 'name': 'ПЕСТКОНТРОЛЬ Центр',
       'legalName': 'ООО «Центр дезинфекционных услуг»', 'url': SITE,
       'telephone': '+7 495 104-35-70', 'email': 'b2b@pestcontrol-center.ru'}
GOALS = ['Лабораторный контроль по ППК', 'Смывы и пробы воздуха', 'Анализ воздуха рабочей зоны', 'Анализ воды',
         'Анализ пищевых продуктов', 'Замеры на рабочих местах', 'Стерильность и стерилизаторы', 'Анализ почвы',
         'Испытания продукции', 'Не знаю, какие исследования нужны']
ARR = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" '
       'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def deeper(s):
    """Относительные пути шаблона ('../') для страницы на уровень глубже."""
    return re.sub(r'(?<=["\'(,\s])\.\./', '../../', s)


def plural(n, a, b, c):
    m, h = n % 10, n % 100
    return f'{n} ' + (a if m == 1 and h != 11 else b if 2 <= m <= 4 and not 12 <= h <= 14 else c)


# ---------------------------------------------------------------- блоки страницы
def hero(p):
    n = p['hero']
    crumbs = ''.join(f'<a href="@/{s}">{t}</a><span aria-hidden="true">→</span>' for t, s in p['crumbs'][:-1])
    crumbs = f'<nav class="f-crumbs" aria-label="Навигационная цепочка">{crumbs}<span aria-current="page">{p["crumbs"][-1][0]}</span></nav>'
    lis = ''.join(f'<li>{b}</li>' for b in p['bullets'])
    ctas = ''.join(f'<a href="{h}" class="btn btn-{k} btn-lg"{" data-goal=" + chr(34) + p["goal"] + chr(34) if h == "#zayavka" else ""}>'
                   f'<span class="btn-t">{t}</span></a>' for h, t, k in p['ctas'])
    return f'''<section class="hero f-hero" id="hero">
  <div class="hero-media"><picture><source media="(max-width:760px)" srcset="@/img/{n}-mob-760.webp 760w, @/img/{n}-mob.webp 1024w" sizes="100vw" width="1024" height="768"><img class="f-hero-img" src="@/img/{n}.webp" srcset="@/img/{n}-1440.webp 1440w, @/img/{n}.webp 1920w" sizes="100vw" width="1920" height="1072" alt="{p['hero_alt']}" fetchpriority="high" decoding="async"></picture></div>
  <div class="wrap">
    <div class="hero-copy">
      {crumbs}
      <span class="badge"><span class="dot"></span>{p['badge']}</span>
      <h1><span class="ln"><span>{p['h1'][0]}</span></span> <span class="ln"><span><em>{p['h1'][1]}</em></span></span></h1>
      <p class="lead">{p['lead']}</p>
      <ul class="lb-hero-list">{lis}</ul>
      <div class="hero-ctas">{ctas}</div>
    </div>
  </div>
</section>
'''


def short(p):
    rows = ''.join(f'<tr><th scope="row">{th}</th><td>{td}</td></tr>' for th, td in p['short'])
    return f'''<section class="s" id="korotko">
  <div class="wrap">
    <div class="head"><div class="eyebrow">Коротко</div><h2>{p['short_h2']}</h2></div>
    <p class="lb-def">{p['definition_html']}</p>
    <table class="d-table lb-short">
      <caption class="sr-only">{plain(p['short_h2'])} — коротко</caption>
      <tbody>{rows}</tbody>
    </table>
    <p class="lb-upd">Обновлено {p['date_ru']} · Автор: <a href="#avtor">Марианна Семерина, санитарный врач</a></p>
  </div>
</section>
'''


def price_table(ids):
    out = ['<table class="d-table lb-tbl"><thead><tr><th scope="col">Услуга</th><th scope="col">Единица</th><th scope="col">Цена</th>'
           '<th scope="col"><span class="sr-only">Расчёт</span></th></tr></thead><tbody>']
    for iid in ids:
        it = BYID[iid][1]
        name = it[1]
        out.append(f'<tr data-id="{iid}"><td data-l="Услуга" class="lb-tn">{name}</td><td data-l="Единица" class="lb-tu">{it[2]}</td>'
                   f'<td data-l="Цена" class="lb-tp">{pr(it)}</td><td class="lb-tc"><button type="button" class="lb-add" data-add="{iid}" '
                   f'aria-label="Добавить в расчёт: {H.escape(name)}"><span aria-hidden="true">+</span></button></td></tr>')
    out.append('</tbody></table>')
    return ''.join(out)


def prices(p, icons):
    groups = []
    for i, (title, ids, opened) in enumerate(p['prices']):
        g = BYID[ids[0]][0]
        cnt = plural(len(ids), 'позиция', 'позиции', 'позиций')
        low = min(D.price(BYID[x][1]) for x in ids)
        groups.append(f'      <details class="lb-grp" id="p-{p["key"]}-{i + 1}"{" open" if opened else ""}><summary><span class="lb-grp-ic">{icons[g[2]]}</span>'
                      f'<span class="lb-grp-n">{title}</span><span class="lb-grp-c">{cnt} · от {rub(low)}</span><span class="pm" aria-hidden="true"></span></summary>\n'
                      f'        {price_table(ids)}\n      </details>')
    note = f'\n    <p class="d-note">{p["price_note"]}</p>' if p.get('price_note') else ''
    return f'''<section class="s" id="ceny">
  <div class="wrap">
    <div class="head"><div class="eyebrow">Цены</div><h2>{p['price_h2']}</h2><p class="sub">{p['price_sub']}</p></div>
    <div class="lb-price">
{chr(10).join(groups)}
    </div>{note}
  </div>
</section>
'''


def section(s):
    sub = f'<p class="sub">{s["sub"]}</p>' if s.get('sub') else ''
    return f'''<section class="s" id="{s['id']}">
  <div class="wrap">
    <div class="head"><div class="eyebrow">{s['eyebrow']}</div><h2>{s['h2']}</h2>{sub}</div>
{s['html'].strip(chr(10))}
  </div>
</section>
'''


def steps(p):
    lis = ''.join(f'<li><img class="lb-step-ic" src="@/img/lab-s{i + 1}.webp" width="120" height="120" alt="" loading="lazy" decoding="async">'
                  f'<b>{t}</b><span>{d}</span></li>' for i, (t, d) in enumerate(p['steps']))
    return f'''<section class="s" id="kak-rabotaem">
  <div class="wrap">
    <div class="head"><div class="eyebrow">Порядок работы</div><h2>{p['steps_h2']}</h2></div>
    <ol class="d-steps lb-steps">{lis}</ol>
  </div>
</section>
'''


def author(p):
    lis = ''.join(f'<li><b>{b}</b> {t}</li>' for b, t in p['principles'])
    return f'''<section class="s" id="avtor">
  <div class="wrap">
    <div class="head"><div class="eyebrow">Автор</div><h2>Кто подготовил <em>материал</em></h2></div>
    <div class="lb-author-wrap">
      <div class="card lb-author">
        <img class="lb-avatar" src="@/img/san-author-photo-240.webp" srcset="@/img/san-author-photo-240.webp 240w, @/img/san-author-photo-480.webp 480w" sizes="(max-width:600px) 80px, 112px" width="240" height="240" loading="lazy" decoding="async" alt="Иллюстративное фото санитарного врача, изображение сгенерировано">
        <div><p class="lb-author-name">Марианна Семерина</p><p class="lb-author-role">Санитарный врач, автор материала</p><p class="lb-author-date">Дата обновления — {p['date_ru']}</p><p class="lb-author-note">Фото иллюстративное</p></div>
      </div>
      <ul class="lb-principles">{lis}</ul>
    </div>
  </div>
</section>
'''


def base(p):
    lis = ''.join(f'<li>{t} (<a href="{H.escape(u)}" target="_blank" rel="noopener">{lbl}</a>)</li>' for t, u, lbl in p['base'])
    return f'''<section class="s" id="normativnaya-baza">
  <div class="wrap">
    <div class="head"><div class="eyebrow">Источники</div><h2>Нормативная база <em>(проверено {p['date_ru']})</em></h2><p class="sub">Документы о производственном контроле, дезинсекции и дератизации — в разделе <a href="@/normativnaya-baza/">«Нормативная база»</a>.</p></div>
    <ul class="lb-base">{lis}</ul>
  </div>
</section>
'''


def faq(p):
    def qa(i, q, a):
        return (f'        <div class="card qa"><button aria-expanded="false" aria-controls="a{i}" id="q{i}"><span>{q}</span><span class="pm"></span></button>'
                f'<div class="ans" id="a{i}" role="region" aria-labelledby="q{i}"><div><p>{a}</p></div></div></div>')
    half = (len(p['faq']) + 1) // 2
    out = ['<section class="s" id="voprosy">', '  <div class="wrap">',
           f'    <div class="head"><div class="eyebrow">Вопросы</div><h2>{p["faq_h2"]}</h2></div>', '    <div class="faq">']
    n = 0
    for col in (p['faq'][:half], p['faq'][half:]):
        out.append('      <div class="faq-col">')
        for q, a in col:
            n += 1
            out.append(qa(n, q, a))
        out.append('      </div>')
    out += ['    </div>', '  </div>', '</section>', '']
    return '\n'.join(out)


def cta(p, icons):
    goal = ''.join(f'<option selected>{g}</option>' if g == p['goal'] else f'<option>{g}</option>' for g in GOALS)
    assert p['goal'] in GOALS, p['goal']
    # текст пункта — одним элементом: пункт списка — flex, иначе вложенный <span class="nw"> отъедет от соседних слов
    lis = ''.join(f'<li>{icons["lucide-circle-check"]}<span>{x}</span></li>' for x in p['cta_list'])
    return f'''<section class="cta" id="zayavka"><div class="cta-bg f-lazy" aria-hidden="true"></div>
  <div class="wrap">
    <div>
      <div class="eyebrow">Заявка</div>
      <h2>{p['cta_h2']}</h2>
      <p class="sub">{p['cta_sub']}</p>
      <ul class="cta-list">{lis}</ul>
<!--CTA_CONTACTS-->
    </div>
    <form class="form" id="form" novalidate data-form>
      <div class="fbody">
        <h3>{p['form_h3']}</h3>
        <p class="fs">Заполнение займёт меньше минуты</p>
        <div class="lb-fcalc" id="lb-fcalc" hidden><p class="lb-fcalc-h">Ваш расчёт</p><ul id="lb-fcalc-list"></ul><p class="lb-fcalc-t" id="lb-fcalc-t"></p></div>
        <div class="fg">
<div class="field"><label class="sr-only" for="f-name">Ваше имя</label><input id="f-name" name="name" placeholder="Ваше имя" required autocomplete="name"><small class="ferr">Укажите имя</small></div>
<div class="field"><label class="sr-only" for="phone">Телефон</label><input name="phone" id="phone" type="tel" inputmode="tel" placeholder="+7 (___) ___-__-__" required autocomplete="tel"><small class="ferr">Укажите телефон полностью</small></div>
<div class="field full"><label class="sr-only" for="f-company">Компания</label><input id="f-company" name="company" placeholder="Компания (необязательно)" autocomplete="organization"></div>
{TYPE_SELECT}
<div class="field full"><label class="sr-only" for="f-goal">Что нужно</label><select id="f-goal" name="goal"><option value="">Что нужно</option>{goal}</select></div>
<div class="field full"><label class="sr-only" for="f-addr">Адрес или район</label><input id="f-addr" name="address" placeholder="Адрес или район" autocomplete="street-address"></div>
<div class="field full"><label class="sr-only" for="f-msg">Комментарий</label><textarea id="f-msg" name="comment" placeholder="{p['comment_ph']}"></textarea></div>
<input type="hidden" name="msg" value="">
<div class="field" hidden><input type="hidden" name="email" value=""></div>
<input type="hidden" name="page" value="{p['name']}">
</div>
        <button type="submit" class="btn btn-w btn-lg" id="submitBtn"><span class="btn-t">{p['submit']}</span><svg class="btn-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg><i class="spin" aria-hidden="true"></i></button>
        <p class="legal">Нажимая кнопку, вы даёте <a href="@/soglasie/" target="_blank" rel="noopener">согласие на обработку персональных данных</a> и подтверждаете, что ознакомились с <a href="@/privacy/" target="_blank" rel="noopener">политикой конфиденциальности</a>.</p>
      </div>
      <div class="ok" role="status" aria-live="polite">
        <svg class="ok-ic" viewBox="0 0 52 52" aria-hidden="true"><circle cx="26" cy="26" r="24" fill="none"/><path fill="none" d="M15 27l7 7 15-16"/></svg>
        <h3>Заявка отправлена</h3><p>Перезвоним в ближайшее рабочее время, уточним задачу и назовём стоимость.</p>
      </div>
    </form>
  </div>
</section>
'''


BAR = ('<div class="lb-bar" id="lb-bar" hidden><div class="lb-bar-in"><p class="lb-bar-t"><span id="lb-bar-n">0 позиций</span><b id="lb-bar-s">от 0 ₽</b></p>'
       '<button type="button" class="lb-bar-clear" id="lb-bar-clear">Очистить</button><a href="#zayavka" class="btn btn-w btn-sm lb-bar-go" id="lb-bar-go">'
       '<span class="btn-t">Отправить расчёт</span></a></div></div>\n')


def main_html(p, icons):
    parts = ['<main id="main" tabindex="-1">\n', hero(p), '\n', short(p), '\n']
    if p.get('prices'):
        parts += [prices(p, icons), '\n']
    for s in p['sections']:
        parts += [section(s), '\n']
    if p.get('steps'):
        parts += [steps(p), '\n']
    parts += [author(p), '\n', base(p), '\n', faq(p), '\n', cta(p, icons), '</main>\n', BAR]
    return ''.join(parts)


# ---------------------------------------------------------------- разметка для поисковиков и ИИ-ответов
def json_ld(p):
    url = SITE + p['slug']
    crumbs = {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': t, 'item': SITE + s} for i, (t, s) in enumerate(p['crumbs'])]}
    hero_img = {'@type': 'ImageObject', 'url': SITE + 'img/' + p['hero'] + '.webp', 'width': 1920, 'height': 1072, 'caption': p['hero_alt']}
    og_img = {'@type': 'ImageObject', 'url': SITE + 'img/' + p['og'] + '.jpg', 'width': 1200, 'height': 630}
    faqld = {'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in p['faq']]}
    term = {'@type': 'DefinedTerm', '@id': url + '#term', 'name': p['term'], 'description': plain(p['definition_html'])}
    graph = [ORG, crumbs]
    if p['kind'] == 'service':
        items = [x for _, ids, _ in p['prices'] for x in ids]
        catalog = {'@type': 'OfferCatalog', 'name': 'Цены: ' + p['crumbs'][-1][0], 'itemListElement': [
            {'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': BYID[i][1][1]},
             'priceSpecification': {'@type': 'UnitPriceSpecification', ('minPrice' if BYID[i][1][4] else 'price'): D.price(BYID[i][1]),
                                    'priceCurrency': 'RUB', 'unitText': BYID[i][1][2]}} for i in items]}
        graph.append({'@type': 'Service', '@id': url + '#service', 'name': p['service_name'], 'alternateName': p['alt_names'],
                      'serviceType': p['service_type'], 'description': p['desc'], 'url': url, 'provider': {'@id': SITE + '#org'},
                      'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
                      'isRelatedTo': {'@type': 'Service', 'name': 'Лабораторные исследования по программе производственного контроля',
                                      'url': SITE + 'laboratornye-issledovaniya/'},
                      'hasOfferCatalog': catalog})
        graph.append({'@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': p['title'], 'description': p['desc'], 'inLanguage': 'ru',
                      'datePublished': p['date'], 'dateModified': p['date'], 'author': AUTHOR, 'publisher': {'@id': SITE + '#org'},
                      'breadcrumb': {'@id': url + '#crumbs'}, 'about': [{'@id': url + '#service'}, {'@id': url + '#term'}],
                      'primaryImageOfPage': hero_img, 'image': [hero_img, og_img]})
    else:
        graph.append({'@type': 'Article', '@id': url + '#article', 'headline': plain(' '.join(p['h1'])), 'description': p['desc'],
                      'inLanguage': 'ru', 'datePublished': p['date'], 'dateModified': p['date'], 'author': AUTHOR,
                      'publisher': {'@id': SITE + '#org'}, 'mainEntityOfPage': url, 'image': [hero_img, og_img],
                      'about': [{'@id': url + '#term'}] + [{'@type': 'Thing', 'name': a} for a in p['about']],
                      'isPartOf': {'@type': 'CollectionPage', 'name': 'Материалы', 'url': SITE + 'materialy/'}})
    crumbs['@id'] = url + '#crumbs'
    graph += [term, faqld]
    return ('<script type="application/ld+json">'
            + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False) + '</script>')


# ---------------------------------------------------------------- сборка
def build(p, tpl, icons):
    url = SITE + p['slug']
    n = p['hero']
    head = tpl[:tpl.index('<style>')]
    rep = [
        (r'<title>[^<]*</title>', f'<title>{p["title"]}</title>'),
        (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{p["desc"]}">'),
        (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">'),
        (r'<meta property="og:type" content="[^"]*">', f'<meta property="og:type" content="{"article" if p["kind"] == "article" else "website"}">'),
        (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">'),
        (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{p["og_title"]}">'),
        (r'<meta property="og:description" content="[^"]*">',
         f'<meta property="og:description" content="{p["desc"]}">\n'
         f'<meta property="og:image" content="{SITE}img/{p["og"]}.jpg">\n'
         '<meta property="og:image:type" content="image/jpeg">\n'
         '<meta property="og:image:width" content="1200">\n'
         '<meta property="og:image:height" content="630">\n'
         f'<meta property="og:image:alt" content="{p["hero_alt"]}">\n'
         '<meta name="twitter:card" content="summary_large_image">'),
        (r'<link rel="preload" href="\.\./img/food-hero\.webp"[^>]*>\n<link rel="preload" href="\.\./img/food-hero-mob\.webp"[^>]*>',
         f'<link rel="preload" as="image" media="(min-width:761px)" imagesrcset="../img/{n}-1440.webp 1440w, ../img/{n}.webp 1920w" imagesizes="100vw" fetchpriority="high">\n'
         f'<link rel="preload" as="image" media="(max-width:760px)" imagesrcset="../img/{n}-mob-760.webp 760w, ../img/{n}-mob.webp 1024w" imagesizes="100vw" fetchpriority="high">'),
    ]
    for pat, new in rep:
        head, k = re.subn(pat, lambda m: new, head, count=1)
        assert k == 1, 'шаблон: не найдено ' + pat
    assert 'food-hero' not in head
    css = tpl[tpl.index('<style>') + 7:tpl.index('</style>')]
    css += '\n' + (HERE / 'page.css').read_text(encoding='utf-8').strip()
    css += '\n' + (HERE / 'subpage.css').read_text(encoding='utf-8').strip()

    top = tpl[tpl.index('</head>'):tpl.index('<main id="main"')]
    top = top.replace('<body class="d-page">', f'<body class="d-page lb-page lbs-page lbs-{p["key"]}">', 1)
    assert 'lbs-page' in top
    bottom = tpl[tpl.index('</main>') + len('</main>'):tpl.index('<script>\n/* Предпросмотр')]
    page_js = cut(tpl, '<script>\n/* Предпросмотр', '</script>', after=True)
    pv = re.match(r'<script>\n(/\* Предпросмотр[^\n]*\*/\n\(function\(\)\{.*?\n?\}\)\(\);)', page_js, re.S)
    assert pv, 'шаблон: не найден скрипт предпросмотра'
    page_js = '<script>\n' + pv.group(1) + '\n</script>'
    li = tpl.index('<script>\n  /* скрипты анимаций')
    loader = tpl[li:tpl.index('</script>', li) + len('</script>')] + '\n'
    contacts = cut(tpl, '      <div class="cta-contacts"', '    </div>\n    <form', after=False).replace(' data-fade', '')
    head, top, bottom, page_js, loader, contacts = (deeper(x) for x in (head, top, bottom, page_js, loader, contacts))

    main = main_html(p, icons)
    main = typeset(main)
    main = re.sub(r'<!--ICON:([a-z0-9-]+)-->', lambda m: icons[m.group(1)], main)
    main = main.replace('<!--CTA_CONTACTS-->\n', contacts.rstrip('\n') + '\n')
    main = main.replace('"@/', '"../../').replace(' @/', ' ../../')
    assert '@/' not in main, p['slug'] + ': остались метки @/'
    assert '<!--' not in main.replace('<!-- ', ''), p['slug'] + ': остались метки'

    lbp = {'n': p['name'], 'p': '/' + p['slug']}
    calc_js = ('<script>window.LB=' + json.dumps(calc_data(), ensure_ascii=False, separators=(',', ':'))
               + ';window.LBP=' + json.dumps(lbp, ensure_ascii=False, separators=(',', ':')) + ';\n'
               + (HERE / 'calc.js').read_text(encoding='utf-8').strip() + '</script>\n')
    html = (head + '<style>' + css + '</style>\n' + json_ld(p) + '\n' + top + main + bottom + page_js + '\n'
            + loader + calc_js + '</body>\n</html>\n')
    out = ROOT / p['slug'] / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')
    words = len(re.findall(r'[А-Яа-яЁёA-Za-z0-9]+', plain(main)))
    print('ok', out.relative_to(ROOT), len(html) // 1024, 'КБ,', words, 'слов')


def main():
    tpl = (ROOT / 'pishchevoe-proizvodstvo' / 'index.html').read_text(encoding='utf-8')
    icons = json.loads((ROOT / 'tools' / 'site' / 'icons.json').read_text(encoding='utf-8'))
    icons.update(json.loads((HERE / 'icons-lab.json').read_text(encoding='utf-8')))
    only = sys.argv[1:]  # имена файлов из pages/ (без .py) — собрать только эти страницы
    for n in ORDER:
        if not only or n in only:
            build(importlib.import_module('pages.' + n).PAGE, tpl, icons)


if __name__ == '__main__':
    main()
