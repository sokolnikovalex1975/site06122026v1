#!/usr/bin/env python3
"""Сборка страницы «Разработка программы производственного контроля по ХАССП» (услуга и образец ППК).

Источники:
  tools/ppk/main.html  — содержимое <main> (первый экран, разделы, FAQ-заглушка, заявка);
  tools/ppk/page.css   — стили собственных блоков страницы (k-*);
  FAQ и микроразметка — ниже в этом файле, чтобы вопросы на странице и в JSON-LD совпадали.

Каркас (шапка, мобильное меню, подвал, служебные скрипты, библиотека стилей d-*/p-*) берётся
со страницы «Программа пест-контроля». Из её встроенных стилей остаются только правила для
классов, которые реально есть на новой странице. После сборки нужно запустить
tools/site/build_site.py — он добавит бегущую строку, «Смотрите также», меню и анимации.

Запуск: python3 tools/ppk/build_ppk.py && python3 tools/site/build_site.py
"""
import html as H
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
from typo import typo  # noqa: E402

SRC = ROOT / 'tools' / 'ppk'
FRAME = ROOT / 'materialy' / 'programma-pest-kontrolya' / 'index.html'
OUT = ROOT / 'materialy' / 'programma-proizvodstvennogo-kontrolya-haccp' / 'index.html'
DOMAIN = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai'
PATH = '/materialy/programma-proizvodstvennogo-kontrolya-haccp/'
URL = DOMAIN + PATH
DATE = '2026-11-06'
MODIFIED = '2026-11-08'  # страница услуги «Разработка ППК по ХАССП» (от 19 900 ₽); простая ППК — отдельная услуга /razrabotka-ppk/

TITLE = 'Разработка программы производственного контроля по ХАССП в Москве и МО — ПЕСТКОНТРОЛЬ Центр'
DESC = ('Разработаем программу производственного контроля по ХАССП для пищевого объекта: анализ опасностей и ККТ, '
        'план лабораторного контроля, формы журналов, ссылки на СанПиН 2026 года. От 19 900 ₽. Образец ППК в PDF.')
OG_TITLE = 'Разработка программы производственного контроля по ХАССП под ваш объект'
HEADLINE = 'Разработка программы производственного контроля по ХАССП'
OG_ALT = ('Специалист ПЕСТКОНТРОЛЬ Центра и инженер по качеству пищевого производства сверяют программу '
          'производственного контроля и план-схему точек контроля')

FAQ = [
    ('Кто может разработать программу производственного контроля?',
     'Ответственность за производственный контроль несёт само предприятие, а программу утверждает его руководитель '
     'или уполномоченное лицо (СП 1.1.1058-01, пп. 2.6–2.7). Разработать документ можно своими силами или '
     'с привлечением специалистов — так поступают, когда в штате нет санитарного врача или технолога, знакомого '
     'с ХАССП. ПЕСТКОНТРОЛЬ Центр разрабатывает ППК полностью: от выезда на объект и анализа опасностей '
     'до приложений и форм журналов.'),
    ('Что входит в разработку ППК по ХАССП?',
     'Обследование объекта; перечень действующих санитарных правил и методик; ответственные лица и должности '
     'для медосмотров и гигиенического обучения; план лабораторного контроля с точками отбора проб '
     'и периодичностью; процедуры ХАССП — блок-схемы, анализ опасностей, критические контрольные точки '
     'и программы предварительных мероприятий; уборка, дезинфекция, дезинсекция и дератизация; аварийные '
     'ситуации; формы учёта и план-график на год. Основа — раздел 3 СП 1.1.1058-01 и ст. 10 ТР ТС 021/2011.'),
    ('Сколько стоит разработка ППК по ХАССП?',
     'От 19 900 ₽. Точная цена зависит от вида деятельности, числа цехов и помещений, ассортимента и объёма '
     'лабораторного контроля: её называем после знакомства с объектом и фиксируем в договоре. Для объектов '
     'непищевого профиля — офисов, складов, гостиниц без пищеблока — программа без процедур ХАССП стоит '
     'от 5 900 ₽. Если предприятие заключает договор на пест-контроль, раздел «Дезинсекция и дератизация» '
     'и программа пест-контроля входят в обслуживание: от 3 500 ₽ в месяц для кафе и магазинов и от 4 500 ₽ '
     'для складов до 1 000 м².'),
    ('Нужна ли программа производственного контроля по ХАССП кафе или магазину?',
     'Программа производственного контроля нужна любому юрлицу и ИП: её составляют до начала деятельности '
     '(СП 1.1.1058-01, п. 2.6). Общепит ведёт производственный контроль на принципах ХАССП — это п. 4 '
     'СанПиН 2.3/2.4.4282-26. Для магазина производственный контроль обязателен по п. 3 СП 2.3.6.4281-26, '
     'а процедуры ХАССП ТР ТС 021/2011 требует от изготовителей пищевой продукции: если в магазине есть '
     'кулинария или пекарня, это уже производство.'),
    ('Нужно ли согласовывать ППК с Роспотребнадзором?',
     'Нет. Программу утверждает руководитель (СП 1.1.1058-01, п. 2.6), а Роспотребнадзор оценивает её '
     'и выполнение мероприятий при проверке. Исключение — программа производственного контроля качества '
     'и безопасности систем водоснабжения: её согласовывают с территориальным управлением Роспотребнадзора.'),
    ('Нужно ли менять ППК после 1 сентября 2026 года?',
     'Да, если в ней остались ссылки на СанПиН 2.3/2.4.3590-20, СП 2.3.6.3668-20 или СП 2.1.3678-20: '
     'с 1 сентября 2026 года вместо них действуют СанПиН 2.3/2.4.4282-26, СП 2.3.6.4281-26 и СП 2.1.4284-26. '
     'Для торговых объектов Роспотребнадзор прямо указывает на необходимость внести изменения в программу '
     'производственного контроля. Новую редакцию утверждает руководитель; действующую программу мы обновляем '
     'без разработки с нуля.'),
    ('Где взять образец программы производственного контроля для пищевого производства?',
     'На этой странице — бесплатный образец ППК на 27 страниц в PDF: так выглядит программа, которую мы '
     'разрабатываем для хлебопекарного и кондитерского производства. В нём все пункты раздела 3 СП 1.1.1058-01, '
     'лабораторный контроль сырья, продукции, смывов и воды, 4 критические контрольные точки ХАССП, медосмотры '
     'и гигиеническая подготовка по должностям, раздел о дезинсекции и дератизации, аварийные ситуации и 19 форм '
     'учёта. Реквизиты в образце условные: программу разрабатывают под конкретный объект, утверждает её руководитель.'),
    ('Нужно ли включать дезинсекцию и дератизацию в программу производственного контроля?',
     'Да. ТР ТС 021/2011 требует выбрать способы, установить периодичность и проводить дезинсекцию '
     'и дератизацию (ст. 10 ч. 3 п. 10), а также определить меры против проникновения грызунов, насекомых '
     'и синантропных птиц (ст. 11 ч. 3 пп. 7–8). Для торговли и объектов услуг обязанность проводить '
     'дезинсекцию и дератизацию закреплена в п. 78 СП 2.3.6.4281-26 и п. 14 СП 2.1.4284-26.'),
    ('Как часто проводить дезинсекцию и дератизацию по программе производственного контроля?',
     'На объектах особого эпидемиологического значения — в пищевой промышленности, общепите, на складах '
     'и в магазинах пищевой продукции — обследования на насекомых проводятся не реже 2 раз в месяц, а дератизация — '
     'по результатам ежемесячной оценки (СанПиН 3.3686-21, пп. 98, 101, 110). Конкретный график визитов '
     'и срок внепланового выезда закрепляются в договоре и программе пест-контроля, а в ППК — ссылкой на них.'),
    ('Пест-контроль — это ККТ в плане ХАССП?',
     'Как правило, нет. Борьба с вредителями относится к программам обязательных предварительных '
     'мероприятий (ПОПМ) — ГОСТ Р ИСО 22000-2019 называет её среди них в п. 8.2.4. Критические контрольные '
     'точки устанавливают для параметров технологического процесса, например температуры. Если анализ '
     'опасностей выявил значимую опасность, связанную с вредителями, меры по её управлению оформляют как ППОПМ '
     'с измеримыми или наблюдаемыми критериями действия (п. 8.5.4.2).'),
    ('Чем программа производственного контроля отличается от программы пест-контроля?',
     'ППК — общий документ предприятия по всем санитарным требованиям: нормы, ответственные, лабораторный '
     'контроль, медосмотры, формы учёта. Программа пест-контроля — подробный рабочий документ только '
     'по вредителям: зоны риска, схема точек, пороги численности, средства и график. В ППК достаточно '
     'раздела с обязательствами и ссылкой на программу пест-контроля как приложение.'),
    ('Какие документы по пест-контролю хранить вместе с ППК?',
     'Договор с исполнителем, сведения о его лицензии, акты выполненных работ, журнал учёта, схему точек '
     'контроля, перечень применяемых средств с документами о государственной регистрации и ежемесячные '
     'отчёты. ТР ТС 021/2011 разрешает вести и хранить документацию на бумажных и (или) электронных '
     'носителях (ст. 10 ч. 3 п. 11).'),
]

CITATIONS = [
    ('СанПиН 2.3/2.4.4282-26 «Санитарно-эпидемиологические требования к организации общественного питания населения»',
     'http://publication.pravo.gov.ru/document/0001202606020084'),
    ('СП 2.3.6.4281-26 «Санитарно-эпидемиологические требования к условиям деятельности торговых объектов и рынков, реализующих пищевую продукцию»',
     'http://publication.pravo.gov.ru/document/0001202606020079'),
    ('СП 2.1.4284-26 «Санитарно-эпидемиологические требования к эксплуатации помещений, зданий, сооружений, оборудования и транспорта, а также условиям деятельности хозяйствующих субъектов, осуществляющих продажу товаров, выполнение работ или оказание услуг»',
     'http://publication.pravo.gov.ru/document/0001202606020088'),
    ('СанПиН 3.3686-21 «Санитарно-эпидемиологические требования по профилактике инфекционных болезней»',
     'http://pravo.gov.ru/proxy/ips/?docbody=&nd=602107773'),
]

NB = '\u00a0'
NW_PATTERNS = [
    r'СанПиН 2\.3/2\.4\.\d{4}-\d{2}', r'СанПиН 3\.3686-21', r'СП 2\.3\.6\.\d{4}-\d{2}', r'СП 2\.1\.\d{4}-\d{2}',
    r'СП 1\.1\.1058-01', r'ТР ТС 021/2011', r'ГОСТ Р ИСО 22000-2019', r'ГОСТ Р 54762-2011',
    r'Л064-00111-77/01942445', r'Ф\. И\. О\.',
    r'(?<![\w-])[Пп]ест-(?:контрол|менеджер|менеджмент|риск)[а-яё]*',
]
NW_RE = re.compile('(' + '|'.join(NW_PATTERNS) + ')')


def _text_rules(t):
    t = NW_RE.sub(lambda m: '\x00' + m.group(1) + '\x01', t)
    t = re.sub(r'(?<=\d) (?=\d{3}(?!\d))', NB, t)   # 1 000, 3 500
    t = t.replace(' ₽', NB + '₽')
    t = t.replace(' →', NB + '→')   # стрелка не уходит на отдельную строку
    return t


def nw_and_typo(fragment):
    """Неразрывные пробелы и <span class="nw"> для кодов документов и слов через дефис — только в тексте, не в тегах."""
    parts = re.split(r'(<[^>]+>)', fragment)
    out, in_nw = [], 0
    for p in parts:
        if p.startswith('<'):
            if re.match(r'<span class="nw"', p):
                in_nw += 1
            out.append(p)
            continue
        out.append(p if in_nw else _text_rules(p))
    s = ''.join(out)
    s = typo(s)
    s = s.replace('\x00', '<span class="nw">').replace('\x01', '</span>')
    return s


# ---------- CSS: только правила для классов, которые есть на странице ----------
def parse_css(css, media=None):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find('{', i)
        if j < 0:
            break
        head = css[i:j].strip()
        if head.startswith('@'):
            depth, k = 1, j + 1
            while depth and k < n:
                depth += {'{': 1, '}': -1}.get(css[k], 0)
                k += 1
            inner = css[j + 1:k - 1]
            if head.startswith('@media') or head.startswith('@supports'):
                out.extend(parse_css(inner, head))
            else:
                out.append((media, head, inner, True))
            i = k
        else:
            k = css.find('}', j)
            out.append((media, head, css[j + 1:k].strip(), False))
            i = k + 1
    return out


DYNAMIC = {'js', 'anim-ready', 'anim-off', 'anim-fail', 'no-intro', 'scrolled', 'open', 'on', 'show', 'active',
           'in', 'sent', 'err', 'is-loading', 'hidden', 'menu-open', 'has-cursor', 'nohover', 'warn', 'full', 'ok'}


def split_sel(sel):
    """Список селекторов по запятым верхнего уровня: запятые внутри :where(…), :is(…), :not(…) не делят селектор."""
    out, depth, cur = [], 0, ''
    for ch in sel:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur)
            cur = ''
        else:
            cur += ch
    out.append(cur)
    return out


def shake(css, used):
    keep = []
    for media, sel, body, at in parse_css(css):
        if at:
            keep.append((media, sel, body, at))
            continue
        alive = []
        # :where(…) из tools/site/fx.py с классами чужих страниц выпадет целиком — unify.py добавит эти стили заново
        for one in split_sel(sel):
            cls = set(re.findall(r'\.([a-zA-Z][\w-]*)', re.sub(r'\[[^\]]*\]', '', one)))
            if all(c in used or c in DYNAMIC for c in cls):
                alive.append(one.strip())
        if alive:
            keep.append((media, ','.join(alive), body, at))
    out, cur = [], None
    for media, sel, body, at in keep:
        if media != cur:
            if cur:
                out.append('}')
            if media:
                out.append(media + '{')
            cur = media
        out.append(sel + '{' + body + '}')
    if cur:
        out.append('}')
    return ''.join(out)


def mini(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([{};,>])\s*', r'\1', css)
    return css.replace(';}', '}').strip()


def faq_html():
    half = (len(FAQ) + 1) // 2
    cols = [FAQ[:half], FAQ[half:]]
    html, n = ['<div class="faq">'], 0
    for col in cols:
        html.append('<div class="faq-col" data-group="faq">')
        for q, a in col:
            n += 1
            html.append(f'<div class="card qa"><button aria-expanded="false" aria-controls="a{n}" id="q{n}"><span class="qa-q">{H.escape(q, False)}</span>'
                        f'<span class="pm"></span></button><div class="ans" id="a{n}" role="region" aria-labelledby="q{n}">'
                        f'<div><p>{H.escape(a, False)}</p></div></div></div>')
        html.append('</div>')
    html.append('</div>')
    return ''.join(html)


def ld_json():
    org = {'@type': 'Organization', '@id': DOMAIN + '/#org', 'name': 'ПЕСТКОНТРОЛЬ Центр', 'url': DOMAIN + '/',
           'telephone': '+7-495-104-35-70', 'email': 'b2b@pestcontrol-center.ru'}
    graph = [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': DOMAIN + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Материалы', 'item': DOMAIN + '/materialy/'},
            {'@type': 'ListItem', 'position': 3, 'name': 'Разработка ППК по ХАССП', 'item': URL}]},
        {'@type': 'WebPage', '@id': URL + '#page', 'url': URL, 'name': TITLE, 'headline': HEADLINE, 'description': DESC,
         'inLanguage': 'ru-RU', 'datePublished': DATE, 'dateModified': MODIFIED,
         'primaryImageOfPage': {'@type': 'ImageObject', 'url': DOMAIN + '/img/ppk-og.jpg'},
         'about': ['Программа производственного контроля', 'ХАССП', 'Дезинсекция', 'Дератизация'],
         'mainEntity': {'@id': URL + '#service'}, 'publisher': org,
         'citation': [{'@type': 'Legislation', 'name': n, 'url': u} for n, u in CITATIONS]},
        {'@type': 'Service', '@id': URL + '#service', 'name': 'Разработка программы производственного контроля по ХАССП',
         'alternateName': 'Разработка ППК по ХАССП', 'serviceType': 'Разработка программы производственного контроля',
         'description': ('Программа производственного контроля на принципах ХАССП под объект заказчика: обследование, '
                         'анализ опасностей и критические контрольные точки, план лабораторного контроля, ответственные '
                         'и медосмотры, дезинсекция и дератизация, аварийные ситуации, формы учёта и план-график.'),
         'provider': org,
         'areaServed': [{'@type': 'City', 'name': 'Москва'}, {'@type': 'AdministrativeArea', 'name': 'Московская область'}],
         'audience': {'@type': 'BusinessAudience', 'audienceType': 'Пищевые производства, общественное питание, торговля пищевой продукцией'},
         'offers': {'@type': 'AggregateOffer', 'priceCurrency': 'RUB', 'lowPrice': 19900,
                    'description': 'Стоимость зависит от вида деятельности, числа цехов и помещений, ассортимента и объёма лабораторного контроля'},
         'isRelatedTo': {'@type': 'Service', 'name': 'Разработка программы производственного контроля (ППК)', 'url': DOMAIN + '/razrabotka-ppk/'}},
        {'@type': 'DigitalDocument', 'name': 'Образец программы производственного контроля для пищевого производства (PDF, 27 страниц)',
         'encodingFormat': 'application/pdf', 'url': URL + 'obrazets-programmy-proizvodstvennogo-kontrolya.pdf',
         'inLanguage': 'ru-RU', 'publisher': {'@id': DOMAIN + '/#org'}},
        {'@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]},
    ]
    return json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False)


CHECK_SVG = ('<svg aria-hidden="true" focusable="false" class="lucide lucide-circle-check" xmlns="http://www.w3.org/2000/svg" '
             'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
             'stroke-linejoin="round" > <circle cx="12" cy="12" r="10" /> <path d="m16 9-5.5 5.5L8 12" /> </svg>')

PAGE_JS = r"""document.addEventListener('click',function(e){var a=e.target.closest('[data-dl]');if(!a)return;try{if(window.ym)ym(113675622,'reachGoal','ppk_'+a.getAttribute('data-dl'))}catch(_){}});
(function(){var f=document.getElementById('form');if(!f)return;f.addEventListener('submit',function(){var e=f.elements,s=e.service.value||'не выбрано',a=e.address.value.trim()||'не указан';e.msg.value='Задача: '+s+'\nАдрес объекта: '+a+'\nСтраница: Разработка ППК по ХАССП (/materialy/programma-proizvodstvennogo-kontrolya-haccp/)';});})();
/* «Скопировать текст» образца раздела */
document.addEventListener('click',function(ev){var b=ev.target.closest('[data-copy]');if(!b)return;var el=document.querySelector(b.getAttribute('data-copy'));if(!el)return;var t=[].map.call(el.querySelectorAll('h3,li'),function(n){return n.tagName==='LI'?n.children[0].textContent+' '+n.children[1].textContent:n.textContent}).join('\n\n').replace(/\u00a0/g,' ').trim(),l=b.querySelector('.btn-t'),o=l.textContent;function ok(){l.textContent='Текст скопирован';setTimeout(function(){l.textContent=o},2400)}function alt(){var a=document.createElement('textarea');a.value=t;a.setAttribute('readonly','');a.style.cssText='position:fixed;top:0;left:0;opacity:0';document.body.appendChild(a);a.select();try{document.execCommand('copy');ok()}catch(x){}document.body.removeChild(a)}if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(t).then(ok,alt);else alt()});"""


def main():
    frame = FRAME.read_text(encoding='utf-8')
    s = frame

    # ---------- <head> ----------
    def sub1(pat, rep, text, flags=0):
        new, n = re.subn(pat, lambda m: rep, text, count=1, flags=flags)
        if n != 1:
            raise SystemExit('не найдено в каркасе: ' + pat)
        return new
    s = sub1(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, re.S)
    s = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{H.escape(DESC)}">', s)
    s = sub1(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{URL}">', s)
    s = sub1(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{URL}">', s)
    s = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{H.escape(OG_TITLE)}">', s)
    s = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{H.escape(DESC)}">', s)
    s = sub1(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{DOMAIN}/img/ppk-og.jpg">', s)
    s = sub1(r'<meta property="og:image:alt" content="[^"]*">', f'<meta property="og:image:alt" content="{H.escape(OG_ALT)}">', s)
    s = s.replace('programma-hero', 'ppk-hero')  # предзагрузка фото первого экрана (в каркасе — только в <head>)
    # значок вкладки: пробелы в data-URI кодируем, чтобы адрес был валидным для валидатора W3C
    s = re.sub(r'(<link rel="icon" href=")(data:[^"]*)(")', lambda m: m.group(1) + m.group(2).replace(' ', '%20') + m.group(3), s, count=1)

    # ---------- <main> ----------
    main_html = (SRC / 'main.html').read_text(encoding='utf-8')
    contacts = re.search(r'<div class="cta-contacts".*?</div>\s*</div>', frame, re.S).group(0)
    form = re.search(r'<form class="form" id="form".*?</form>', frame, re.S).group(0)
    form = form.replace('<h3>Заявка на разработку программы</h3>', '<h3>Заявка на разработку ППК</h3>')
    form = re.sub(r'(<select id="f-service" name="service">).*?(</select>)',
                  r'\1<option value="" selected>Какая задача стоит</option><option>Разработать ППК по ХАССП с нуля</option>'
                  r'<option>Обновить ППК под санитарные правила 2026 года</option><option>Подготовиться к проверке или аудиту ХАССП</option>'
                  r'<option>Разработать ППК и подключить пест-контроль</option>\2', form, flags=re.S)
    form = form.replace('<span class="btn-t">Получить программу</span>', '<span class="btn-t">Заказать разработку ППК</span>')
    # autocomplete="street-address" допустим только для многострочного поля; для однострочного — address-line1
    form = form.replace('autocomplete="street-address"', 'autocomplete="address-line1"')
    assert 'Заявка на разработку ППК' in form and 'Заказать разработку ППК' in form and 'Разработать ППК по ХАССП с нуля' in form

    main_html = main_html.replace('<!--FAQ-->', faq_html())
    main_html = re.sub(r'(<ul class="cta-list"[^>]*>)(.*?)(</ul>)',
                       lambda m: m.group(1) + m.group(2).replace('<li>', '<li>' + CHECK_SVG) + m.group(3), main_html, flags=re.S)
    main_html = nw_and_typo(main_html)
    main_html = main_html.replace('<!--CONTACTS-->', contacts).replace('<!--FORM-->', form)

    i = s.index('<main id="main" tabindex="-1">') + len('<main id="main" tabindex="-1">')
    j = s.index('</main>')
    s = s[:i] + '\n' + main_html + '\n' + s[j:]

    # кнопка в шапке
    # (разработка ППК — платная услуга, бесплатно у компании только обследование по пест-контролю)
    s = s.replace('<span class="btn-t">Заказать программу</span>', '<span class="btn-t">Заказать ППК</span>', 1)
    # кнопка мобильного меню — то же предложение, что в шапке (в каркасе — «Заказать разработку программы»)
    s = s.replace('<a href="#zayavka" class="btn btn-w btn-lg"><span class="btn-t">Заказать разработку программы</span></a>\n</nav>',
                  '<a href="#zayavka" class="btn btn-w btn-lg"><span class="btn-t">Заказать разработку ППК</span></a>\n</nav>', 1)
    # нижняя панель на телефоне: вместо «Обследование» — заказ ППК (услуга платная)
    s, n = re.subn(r'(<a href="#zayavka" class="c2"><span>)[^<]*', r'\g<1>Заказать ППК', s)
    if n != 1:
        raise SystemExit('не найдена нижняя панель на телефоне')

    # ---------- скрипты страницы: защита предпросмотра остаётся, остальное — своё ----------
    m = re.search(r'(<script>\n\(function\(\)\{if\(/\^\(www\\\.\)\?xn----[^\n]*\n)(.*?)(</script>)', s, re.S)
    if not m:
        raise SystemExit('не найден блок скриптов страницы в каркасе')
    s = s[:m.start()] + m.group(1) + PAGE_JS + '\n' + m.group(3) + s[m.end():]

    # ---------- микроразметка ----------
    s = sub1(r'<script type="application/ld\+json">.*?</script>',
             '<script type="application/ld+json">' + ld_json() + '</script>', s, re.S)

    # ---------- стили ----------
    # классы блоков, которые добавит tools/site/unify.py (бегущая строка, «Смотрите также»)
    used = {'strip', 'strip-track', 'strip-set', 'strip-item', 's-rel', 'rel-grid', 'rel-card', 'rel-k', 'rel-t',
            'rel-d', 'rel-a', 'card', 'head', 'eyebrow', 'wrap', 's'}
    for cl in re.findall(r'class="([^"]*)"', s):
        used.update(cl.split())
    # без <style data-fx> и <style id="m-crumbs"> каркаса — их заново вставляют tools/site/unify.py и mobile_crumbs.py
    frame_css = '\n'.join(re.findall(r'<style(?![^>]*(?:data-fx|id="m-crumbs"))[^>]*>(.*?)</style>', frame, re.S))
    css = shake(frame_css, used) + mini((SRC / 'page.css').read_text(encoding='utf-8'))
    s = re.sub(r'<style[^>]*>.*?</style>\n?', '', s, flags=re.S)
    # стили страницы — сразу после общего style.css, как на других страницах
    link = re.search(r'<link rel="stylesheet" href="\.\./\.\./style\.css[^>]*>', s).group(0)
    s = s.replace(link, link + '\n<style>' + css + '</style>', 1)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(s, encoding='utf-8')
    print(f'{OUT.relative_to(ROOT)}: {len(s.encode("utf-8")) // 1024} КБ, стили страницы {len(css) // 1024} КБ, вопросов FAQ {len(FAQ)}')


if __name__ == '__main__':
    main()
