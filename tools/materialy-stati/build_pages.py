#!/usr/bin/env python3
"""Статьи раздела «Материалы» из согласованных текстов (с 24.11.2026, превью):

    materialy/pest-kontrol-iso-22000-fssc-22000/index.html — «Пест-контроль по ISO 22000 и FSSC 22000: что проверяет аудитор»
    materialy/litsenziya-na-dezinfektsiyu/index.html       — «Лицензия на дезинфекцию и дератизацию: как проверить подрядчика»

Тексты — iso.md и lic.md: раздел «Текст» черновиков проекта SEO (seo-agent/drafts/2026-11-16-pest-kontrol-iso-22000-fssc-22000.md,
seo-agent/drafts/2026-11-24-litsenziya-na-dezinfektsiyu.md), согласованы владельцем 24.11.2026 («Обе статьи»). Правьте текст
в .md, а не в готовой странице. Разметка markdown — только та, что в черновиках: ## раздел, ### подраздел или вопрос FAQ,
абзац, таблица, список «-» и «1.», **жирный**, [ссылка](адрес).

Шаблон и сборка — как у «Акта» и «Схемы точек» (tools/materialy-dokumenty): функции tools/normativnaya-baza/build_pages.py
(шапка, подвал, форма, FAQ, типографика) на шаблоне пищевой отраслевой страницы. Свои: page.css, разметка Article.
Фото первого экрана — make_images.py, картинки для соцсетей — og.mjs.

    python3 tools/materialy-stati/build_pages.py   # build_site.py запускает его сам
"""
import html
import importlib.util
import json
import pathlib
import re
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_spec = importlib.util.spec_from_file_location('nb_build_pages', ROOT / 'tools' / 'normativnaya-baza' / 'build_pages.py')
NB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(NB)
sys.path.insert(0, str(ROOT / 'tools' / 'menu'))
import apply_menu as MENU  # noqa: E402  блок поиска в <head> (search_ui)
SITE = NB.SITE
NB.SEND_TYPES |= {'Бизнес-центр или офисное здание', 'Торговый центр', 'Промышленное предприятие'}

TYPES = [('Пищевое производство', 'Пищевое производство'), ('Ресторан или кафе', 'Ресторан, кафе, столовая'),
         ('Магазин или торговая сеть', 'Магазин или торговая сеть'), ('Склад, логистика', 'Склад, логистика'),
         ('Фармацевтическое производство', 'Фармацевтическое производство'), ('Гостиница', 'Гостиница, отель'),
         ('Бизнес-центр или офисное здание', 'Бизнес-центр, офисное здание'), ('Торговый центр', 'Торговый центр'),
         ('Промышленное предприятие', 'Промышленное предприятие'), ('Другое', 'Медицинская организация'),
         ('Другое', 'Школа, детский сад'), ('Другое', 'Другое')]

PAGES = [
    {
        'key': 'iso', 'md': 'iso.md', 'out': 'materialy/pest-kontrol-iso-22000-fssc-22000/index.html',
        'slug': 'materialy/pest-kontrol-iso-22000-fssc-22000/', 'root': '../../',
        'title': 'Пест-контроль по ISO 22000 и FSSC 22000: что смотрит аудитор',
        'og_title': 'Пест-контроль по ISO 22000 и FSSC 22000: что проверяет аудитор',
        'desc': 'Какие требования к борьбе с вредителями задают ISO 22000, ГОСТ Р 54762 и FSSC 22000 версии 7 и какие записи '
                'аудитор попросит показать на предприятии.',
        'h1': 'Пест-контроль по ISO 22000 и FSSC 22000: что проверяет аудитор',
        'h1_html': '<span class="ln"><span>Пест-контроль по ISO&nbsp;22000</span></span> <span class="ln"><span>и FSSC&nbsp;22000:</span></span> '
                   '<span class="ln"><span><em>что проверяет аудитор</em></span></span>',
        'eyebrow': 'Материалы · Сертификация пищевых производств',
        'crumb': 'Пест-контроль по ISO 22000 и FSSC 22000',
        'og_image': 'iso-og.jpg', 'og_alt': 'Пест-контроль по ISO 22000 и FSSC 22000: что проверяет аудитор',
        'hero': 'iso-hero', 'hero_alt': 'Аудитор в голубом жилете и менеджер по качеству с папкой записей пест-контроля '
                                        'осматривают станцию контроля грызунов в цехе пищевого производства',
        'btns': [('#zayavka', 'Подготовиться к аудиту', 'Санитарный аудит перед сертификацией'),
                 ('#zapisi', 'Какие записи нужны', None)],
        'sections': {
            'Какие документы описывают пест-контроль в системе безопасности пищевой продукции':
                ('dokumenty', 'Документы', 'Какие документы описывают пест-контроль <em>в системе безопасности пищевой продукции</em>', 'Документы'),
            'Обязателен ли пест-контроль, если сертификата нет':
                ('bez-sertifikata', 'Без сертификата', 'Обязателен ли пест-контроль, <em>если сертификата нет</em>', 'Без сертификата'),
            'Что требует раздел 12 ГОСТ Р 54762-2011':
                ('gost-54762', 'ГОСТ Р 54762-2011', 'Что требует раздел 12 <em>ГОСТ Р 54762-2011</em>', 'Раздел 12'),
            'Что меняется с FSSC 22000 версии 7':
                ('fssc-v7', 'FSSC 22000 версии 7', 'Что меняется <em>с FSSC 22000 версии 7</em>', 'Версия 7'),
            'Что аудитор FSSC проверяет по пест-контролю':
                ('audit', 'Аудит', 'Что аудитор FSSC проверяет <em>по пест-контролю</em>', 'Аудит'),
            'Что требуют BRCGS и IFS':
                ('brcgs-ifs', 'BRCGS и IFS', 'Что требуют <em>BRCGS и IFS</em>', 'BRCGS и IFS'),
            'Какие записи подготовить заранее':
                ('zapisi', 'Записи', 'Какие записи <em>подготовить заранее</em>', 'Записи'),
            'Чем поможет ПЕСТКОНТРОЛЬ Центр':
                ('pomoshch', 'Услуги', 'Чем поможет <em>ПЕСТКОНТРОЛЬ Центр</em>', None),
        },
        'faq_h2': 'Вопросы <em>о пест-контроле по ISO 22000 и FSSC 22000</em>',
        'name': 'Пест-контроль по ISO 22000 и FSSC 22000',
        'need': ['Санитарный аудит перед сертификацией', 'Договор на обслуживание пищевого производства',
                 'Сверить программу пест-контроля с ISO 22002-100:2025'],
        'comment_ph': 'Комментарий: схема сертификации, дата аудита, площадь',
        'cta': ('Подготовим пест-контроль <em>к аудиту по ISO 22000 и FSSC 22000</em>',
                'Если аудит скоро, начните с санитарного аудита (от 9 000 ₽): проверим объект и папку пест-контроля и покажем, '
                'что исправить до визита. Если нужен постоянный подрядчик — работаем по договору.',
                ['Санитарный аудит — от 9 000 ₽', 'Программа и схема точек под СанПиН и вашу схему сертификации',
                 'Переход на ISO 22002-100:2025']),
        'about': ['ISO 22000', 'FSSC 22000', 'ГОСТ Р 54762-2011', 'ISO 22002-100:2025', 'Пест-контроль'],
        'checked': 'Нормы сверены — 24.11.2026',
        'author_text': 'Материал подготовила Марианна Семерина, санитарный врач. Требования сверены с официальными текстами '
                       'ISO, FSSC, BRCGS, IFS, Росстандарта и Роспотребнадзора 24.11.2026. Если вы заметили неточность, '
                       'напишите нам — исправим.',
        'date': '2026-11-24',
    },
    {
        'key': 'lic', 'md': 'lic.md', 'out': 'materialy/litsenziya-na-dezinfektsiyu/index.html',
        'slug': 'materialy/litsenziya-na-dezinfektsiyu/', 'root': '../../',
        'title': 'Лицензия на дезинфекцию: нужна ли подрядчику и как её проверить',
        'og_title': 'Лицензия на дезинфекцию и дератизацию: как проверить подрядчика',
        'desc': 'С марта 2025 года дезинфекцию, дезинсекцию и дератизацию для заказчиков оказывают только по лицензии. '
                'Разбираем, что она подтверждает и как найти её в реестре.',
        'h1': 'Лицензия на дезинфекцию и дератизацию: как проверить подрядчика',
        'h1_html': '<span class="ln"><span>Лицензия на дезинфекцию</span></span> <span class="ln"><span>и дератизацию:</span></span> '
                   '<span class="ln"><span><em>как проверить подрядчика</em></span></span>',
        'eyebrow': 'Материалы · Выбор подрядчика',
        'crumb': 'Лицензия на дезинфекцию',
        'og_image': 'lic-og.jpg', 'og_alt': 'Лицензия на дезинфекцию и дератизацию: как проверить подрядчика',
        'hero': 'lic-hero', 'hero_alt': 'Менеджер по закупкам за ноутбуком сверяет договор, рядом стоит специалист '
                                        'по пест-контролю в синей форме с папкой документов',
        'btns': [('#proverka', 'Как проверить лицензию', None),
                 ('#zayavka', 'Договор с подрядчиком', 'Договор на обслуживание')],
        'sections': {
            'С какого момента без лицензии работать нельзя':
                ('sroki', 'Сроки', 'С какого момента <em>без лицензии работать нельзя</em>', 'Сроки'),
            'Какие услуги требуют лицензии':
                ('uslugi', 'Услуги', 'Какие услуги <em>требуют лицензии</em>', 'Услуги'),
            'Кто отвечает за обработку объекта':
                ('otvetstvennost', 'Ответственность', 'Кто отвечает <em>за обработку объекта</em>', None),
            'Что подтверждает лицензия':
                ('trebovaniya', 'Требования', 'Что подтверждает <em>лицензия</em>', 'Требования'),
            'Сколько действует лицензия и где':
                ('srok-deystviya', 'Срок действия', 'Сколько действует лицензия <em>и где</em>', None),
            'Как проверить лицензию подрядчика за пять минут':
                ('proverka', 'Проверка', 'Как проверить лицензию подрядчика <em>за пять минут</em>', 'Проверка'),
            'Наша лицензия':
                ('nasha-litsenziya', 'ПЕСТКОНТРОЛЬ Центр', 'Наша <em>лицензия</em>', 'Наша лицензия'),
        },
        'faq_h2': 'Вопросы <em>о лицензии на дезинфекцию</em>',
        'name': 'Лицензия на дезинфекцию',
        'need': ['Договор на обслуживание', 'Дезинфекция помещений', 'Санитарный аудит: проверить нынешнего подрядчика'],
        'comment_ph': 'Комментарий: объект, площадь, какие работы нужны',
        'cta': ('Подрядчик с лицензией <em>для вашего объекта</em>',
                'Работаем по лицензии Роспотребнадзора № Л064-00111-77/01942445 с организациями Москвы и Подмосковья. '
                'Постоянное обслуживание по договору на дератизацию и дезинсекцию — от 4 900 ₽ в месяц.',
                ['Лицензия на дератизацию, дезинсекцию и дезинфекцию', 'Номер лицензии — в договоре и каждом акте',
                 'Санитарный аудит — от 9 000 ₽']),
        'about': ['Лицензия на дезинфекцию', 'Лицензия на дератизацию', 'Реестр лицензий Роспотребнадзора',
                  'Постановление Правительства РФ № 337'],
        'checked': 'Нормы сверены — 24.11.2026',
        'author_text': 'Материал подготовила Марианна Семерина, санитарный врач. Требования сверены с Федеральным законом '
                       '№ 194-ФЗ, постановлением Правительства № 337 и разъяснениями Роспотребнадзора 24.11.2026. '
                       'Если вы заметили неточность, напишите нам — исправим.',
        'date': '2026-11-24',
    },
]

OWN = ('пестконтроль-центр.рф', 'xn----itbbsflddbfpfdodg9d0f')  # свои страницы в списке источников не показываем


# ---------------------------------------------------------------- markdown черновика → разметка сайта
def inline(s):
    out, pos = [], 0
    for m in re.finditer(r'\[([^\]]+)\]\(([^)\s]+)\)|\*\*([^*]+)\*\*', s):
        out.append(html.escape(s[pos:m.start()], quote=False))
        if m.group(3):
            out.append('<b>' + html.escape(m.group(3), quote=False) + '</b>')
        else:
            t, u = html.escape(m.group(1), quote=False), m.group(2)
            if u.startswith('/'):
                out.append(f'<a href="@{u}">{t}</a>')
            else:
                out.append(f'<a href="{html.escape(u)}" target="_blank" rel="noopener">{t}</a>')
        pos = m.end()
    out.append(html.escape(s[pos:], quote=False))
    return ''.join(out)


def cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def table(rows):
    head, body = cells(rows[0]), [cells(r) for r in rows[2:]]
    th = ''.join(f'<th scope="col">{inline(h) or "<span class=\"sr-only\">Пункт</span>"}</th>' for h in head)
    tr = []
    for r in body:
        tds = []
        for i, c in enumerate(r):
            lab = html.escape(head[i] or 'Пункт')
            v = inline(c)
            tds.append(f'<td data-l="{lab}">' + (f'<b>{v}</b>' if i == 0 else v) + '</td>')
        tr.append('<tr>' + ''.join(tds) + '</tr>')
    return (f'<div class="st-tbl-w"><table class="d-table nb-tbl md-tbl st-tbl st-c{len(head)}"><thead><tr>{th}</tr></thead>'
            '<tbody>' + ''.join(tr) + '</tbody></table></div>')


def blocks(lines):
    """Абзацы, таблицы, списки и ### подзаголовки одного раздела."""
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip() or ln.startswith('<!--'):
            i += 1
            continue
        if ln.startswith('|'):
            j = i
            while j < len(lines) and lines[j].startswith('|'):
                j += 1
            out.append(table(lines[i:j]))
            i = j
            continue
        m = re.match(r'(- |\d+\. )', ln)
        if m:
            tag = 'ul' if ln.startswith('- ') else 'ol'
            items = []
            while i < len(lines) and re.match(r'(- |\d+\. )', lines[i]):
                items.append(re.sub(r'^(- |\d+\. )', '', lines[i]))
                i += 1
            cls = 'md-ul st-ul' if tag == 'ul' else 'md-ol st-ol'
            out.append(f'<{tag} class="{cls}">' + ''.join(f'<li>{inline(x)}</li>' for x in items) + f'</{tag}>')
            continue
        if ln.startswith('### '):
            out.append(f'<h3 class="nb-h3 st-h3">{inline(ln[4:])}</h3>')
            i += 1
            continue
        cls = 'st-p st-note' if ln.startswith(('Источник', 'Источники:', 'Про оба реестра')) else 'st-p'
        out.append(f'<p class="{cls}">{inline(ln)}</p>')
        i += 1
    return '\n    '.join(out)


def parse(md):
    lines = md.split('\n')
    secs, cur = [], None
    for ln in lines:
        if ln.startswith('## '):
            cur = [ln[3:].strip(), []]
            secs.append(cur)
        elif cur is not None:
            cur[1].append(ln)
    lead = re.search(r'\*\*Коротко\.\*\*\s*(.+)', md).group(1).strip()  # «Коротко» из раздела «Текст» — в первый экран
    return lead, [s for s in secs if s[0] != 'Текст']


def faq_items(lines):
    items, q = [], None
    for ln in lines:
        if ln.startswith('### '):
            q = [ln[4:].strip(), []]
            items.append(q)
        elif q is not None and ln.strip():
            q[1].append(ln.strip())
    return [(q, ' '.join(inline(x) for x in a)) for q, a in items]


def sources(lines):
    li = []
    for r in [cells(x) for x in lines if x.startswith('|')][2:]:
        m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', r[0])
        if not m or any(o in m.group(2) for o in OWN):
            continue
        li.append(f'<li>{inline(r[1])} — <a href="{html.escape(m.group(2))}" target="_blank" rel="noopener">'
                  f'{html.escape(m.group(1), quote=False)}</a></li>')
    return li


def page_html(p):
    lead, secs = parse((HERE / p['md']).read_text(encoding='utf-8'))
    body, toc, faq, src = [], [], [], []
    for title, lines in secs:
        if title == 'Частые вопросы':
            faq = faq_items(lines)
            continue
        if title == 'Источники':
            src = sources(lines)
            continue
        sid, ey, h2, tocname = p['sections'][title]
        if tocname:
            toc.append(f'<a href="#{sid}">{tocname}</a>')
        extra = ''
        if sid in ('pomoshch', 'nasha-litsenziya'):
            extra = ('\n    <div class="d-btns st-btns"><a href="#zayavka" class="btn btn-w btn-lg" data-need="' + p['need'][0]
                     + '"><span class="btn-t">Оставить заявку</span></a></div>')
        body.append(f'<section class="s st-s" id="{sid}">\n  <div class="wrap">\n    <div class="head"><div class="eyebrow">{ey}</div>'
                    f'<h2>{h2}</h2></div>\n    <div class="st-body">\n    {blocks(lines)}{extra}\n    </div>\n  </div>\n</section>')
    toc.append('<a href="#voprosy">Вопросы</a>')
    btns = []
    for i, (href, t, need) in enumerate(p['btns']):
        cls = 'btn btn-w btn-lg' if i == 0 else 'btn btn-o btn-lg'
        dn = f' data-need="{need}"' if need else ''
        btns.append(f'<a href="{href}" class="{cls}"{dn}><span class="btn-t">{t}</span></a>')
    hero = ('<section class="d-hero nb-hero md-hero" id="hero">\n  <div class="wrap">\n    <div class="d-hero-copy">\n'
            '      <nav class="f-crumbs" aria-label="Навигационная цепочка"><a href="@/">Главная</a><span aria-hidden="true">→</span>'
            f'<a href="@/materialy/">Материалы</a><span aria-hidden="true">→</span><span aria-current="page">{p["crumb"]}</span></nav>\n'
            f'      <div class="eyebrow">{p["eyebrow"]}</div>\n      <h1>{p["h1_html"]}</h1>\n      <!--HERO_PHOTO-->\n'
            f'      <p class="lead">{inline(lead)}</p>\n      <div class="d-btns">\n        ' + '\n        '.join(btns)
            + '\n      </div>\n    </div>\n    <nav class="p-toc nb-toc" aria-label="Разделы страницы">' + ''.join(toc)
            + '</nav>\n  </div>\n</section>')
    author = ('<section class="s" id="avtor">\n  <div class="wrap">\n    <div class="head"><div class="eyebrow">Автор и сверка</div>'
              '<h2>Кто подготовил <em>материал</em></h2></div>\n    <div class="nb-author-wrap">\n      <div class="card nb-author">\n'
              '        <img class="nb-avatar" src="@/img/san-author-photo-240.webp" srcset="@/img/san-author-photo-240.webp 240w, '
              '@/img/san-author-photo-480.webp 480w" sizes="(max-width:600px) 80px, 112px" width="240" height="240" loading="lazy" '
              'decoding="async" alt="Иллюстративное фото санитарного врача, изображение сгенерировано">\n'
              '        <div><p class="nb-author-name">Марианна Семерина</p><p class="nb-author-role">Санитарный врач, автор материала</p>'
              f'<p class="nb-author-date">{p["checked"]}</p><p class="nb-author-note">Фото иллюстративное</p></div>\n      </div>\n'
              f'      <p class="nb-author-text">{p["author_text"]}</p>\n    </div>\n  </div>\n</section>')
    srcs = ('<section class="s" id="istochniki">\n  <div class="wrap">\n    <details class="nb-src">\n'
            '      <summary><span class="eyebrow">Источники</span><span class="nb-src-t">Официальные тексты (проверено 24.11.2026)</span></summary>\n'
            '      <ul class="nb-base">\n        ' + '\n        '.join(src) + '\n      </ul>\n    </details>\n  </div>\n</section>')
    h2, sub, li = p['cta']
    cta = ('<section class="cta" id="zayavka"><div class="cta-bg f-lazy" aria-hidden="true"></div>\n  <div class="wrap">\n    <div>\n'
           f'      <div class="eyebrow">Заявка</div>\n      <h2>{h2}</h2>\n      <p class="sub">{sub}</p>\n      <ul class="cta-list">\n'
           + ''.join(f'        <li><!--ICON:lucide-circle-check--><span>{x}</span></li>\n' for x in li)
           + '      </ul>\n<!--CTA_CONTACTS-->\n    </div>\n' + FORM + '  </div>\n</section>')
    main = '<main id="main" tabindex="-1">\n' + hero + '\n\n' + '\n'.join(body) + '\n' + author + '\n' + srcs + '\n<!--FAQ-->\n' + cta + '\n</main>\n'
    return main, faq


FORM = """    <form class="form" id="form" novalidate data-form>
      <div class="fbody">
        <h3>Оставить заявку</h3>
        <p class="fs">Заполнение займёт меньше минуты</p>
        <div class="fg">
<!--FORM_FIELDS-->
</div>
        <button type="submit" class="btn btn-w btn-lg" id="submitBtn"><span class="btn-t">Отправить заявку</span><svg class="btn-ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg><i class="spin" aria-hidden="true"></i></button>
        <p class="legal">Нажимая кнопку, вы даёте <a href="@/soglasie/" target="_blank" rel="noopener">согласие на обработку персональных данных</a> и подтверждаете, что ознакомились с <a href="@/privacy/" target="_blank" rel="noopener">политикой конфиденциальности</a>.</p>
        <p class="legal nb-lic">Работы выполняет ООО «Центр дезинфекционных услуг», лицензия на дезинфекционную деятельность <a href="LICENSE_URL" target="_blank" rel="noopener">№ Л064-00111-77/01942445</a></p>
      </div>
      <div class="ok" role="status" aria-live="polite">
        <svg class="ok-ic" viewBox="0 0 52 52" aria-hidden="true"><circle cx="26" cy="26" r="24" fill="none"/><path fill="none" d="M15 27l7 7 15-16"/></svg>
        <h3>Заявка отправлена</h3><p>Перезвоним в ближайшее рабочее время.</p>
      </div>
    </form>
"""


def json_ld(p):
    url = SITE + p['slug']
    crumbs = {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + s}
        for i, (n, s) in enumerate([('Главная', ''), ('Материалы', 'materialy/'), (p['crumb'], p['slug'])])]}
    faq = {'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': NB.plain(a)}} for q, a in p['faq']]}
    image = {'@type': 'ImageObject', 'url': SITE + 'img/' + p['og_image'], 'width': 1200, 'height': 630}
    hero = {'@type': 'ImageObject', 'url': SITE + 'img/' + p['hero'] + '.webp', 'width': 1920, 'height': 1072,
            'caption': p['hero_alt']}
    page = {'@type': 'Article', '@id': url + '#article', 'headline': p['h1'], 'description': p['desc'],
            'inLanguage': 'ru', 'datePublished': p['date'], 'dateModified': p['date'],
            'author': NB.AUTHOR, 'publisher': {'@id': SITE + '#org'}, 'mainEntityOfPage': url, 'image': [hero, image],
            'about': p['about'], 'isPartOf': {'@type': 'CollectionPage', '@id': SITE + 'materialy/#webpage',
                                              'url': SITE + 'materialy/', 'name': 'Материалы о пест-контроле'}}
    return ('<script type="application/ld+json">'
            + json.dumps({'@context': 'https://schema.org', '@graph': [NB.ORG, crumbs, page, faq]}, ensure_ascii=False) + '</script>')


def main():
    tpl = (ROOT / 'pishchevoe-proizvodstvo' / 'index.html').read_text(encoding='utf-8')
    icons = json.loads((ROOT / 'tools' / 'site' / 'icons.json').read_text(encoding='utf-8'))
    icons.update(json.loads((ROOT / 'tools' / 'normativnaya-baza' / 'icons-nb.json').read_text(encoding='utf-8')))
    NB.json_ld = json_ld
    css = ((ROOT / 'tools' / 'materialy-dokumenty' / 'page.css').read_text(encoding='utf-8').strip() + '\n'
           + (HERE / 'page.css').read_text(encoding='utf-8').strip())
    with tempfile.TemporaryDirectory() as tmp:
        for p in PAGES:
            main_html, faq = page_html(p)
            # цены и числа одним куском: «4 900 ₽», «9 000 ₽» не разрываются по строкам
            nbsp = lambda t: re.sub(r'(\d) (?=\d{3}\b)|(\d) (?=₽)', lambda m: (m.group(1) or m.group(2)) + '\u00a0', t)
            main_html = nbsp(main_html)
            faq = [tuple(nbsp(x) if isinstance(x, str) else x for x in q) for q in faq]
            f = pathlib.Path(tmp) / (p['key'] + '.html')
            f.write_text(main_html, encoding='utf-8')
            q = dict(p, src=str(f), faq=faq, faq_open=True, types=TYPES)
            NB.build(q, tpl, icons)
            out = ROOT / p['out']
            s = out.read_text(encoding='utf-8')
            marker = '</style>\n<script type="application/ld+json">'
            assert s.count(marker) == 1, 'не найден конец стилей'
            s = s.replace(marker, '\n' + css + marker, 1)
            # блок поиска — сразу в том виде, в каком его ставит tools/menu/apply_menu.py: иначе stable_build.carry_head
            # вернул бы его с переводом строки между <style> и <script>, и меню поставило бы второй такой же блок
            s = MENU.search_ui(s, p['root'])
            out.write_text(s, encoding='utf-8')
            print('  + стили страницы', p['key'], '— вопросов в FAQ:', len(faq))


if __name__ == '__main__':
    main()
