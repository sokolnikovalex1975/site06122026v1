#!/usr/bin/env python3
"""Блок «Наши клиенты» — стена логотипов клиентов (предложение 12.11.2026, согласовано владельцем 19.11.2026).

Где стоит:
  * главная — 4-м блоком, сразу после общего прайса #tseny «Выберите услугу. Узнайте стоимость.», перед «Этапами» (#etapy):
    после цены следующий вопрос посетителя — «а вам можно доверять?»;
  * коммерческие страницы услуг и отраслей (PAGES) — последним блоком перед формой заявки #zayavka, после общего
    прайса или каталога «Один подрядчик»: логотипы — последний довод перед заявкой;
  * на информационных страницах («Материалы», «Нормативная база», политика и согласие) блока нет.

Клиенты — из amoCRM (только чтение, выгрузка 16.11.2026), самые известные бренды по отраслям (CLIENTS).
На отраслевых страницах (ONLY) — только клиенты своей отрасли (на «Складах» — склады клиентов разных отраслей, EXTRA);
на общих страницах (MIX) — микс из 15 логотипов, первыми отрасли страницы; на главной — 23. Заголовок — по отрасли (HEAD).
Последняя клетка — заявка («Обследование 0 ₽», на главной — «Бесплатный аудит»; между 0 и ₽ неразрывный пробел).
Сетка без пустых клеток в последнем ряду; на телефоне больше 7 логотипов — кнопка «Показать всех клиентов».

Логотипы: img/klienty/*.webp (белые одноцветные; размеры — tools/klienty/logos.json); оригиналы — с сайтов компаний
и Wikimedia Commons (журнал tools/site/klienty-2026-11-19.md).

Счётчики, телефон и почту не трогает (ЗАКОН ВЛАДЕЛЬЦА, tools/site/tracking_laws.py); стили — сразу после
<style id="pr-st"> (или после ссылки на style.css), скрипт — сразу после блока. Повторный вызов patch() ничего не дублирует.
Шаг сборки tools/site/build_site.py — сразу после price_block.py (согласовано 19.11.2026).
"""
import json
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
from typo import typo  # noqa: E402

META = json.loads((ROOT / 'tools' / 'klienty' / 'logos.json').read_text(encoding='utf-8'))

# имя файла: alt, подпись под логотипом, отрасль, поправка «визуального веса» (жирные знаки — меньше, узкие — больше).
# Клиенты — из amoCRM (только чтение, выгрузка 16.11.2026): компании с покупками, бренд — из названий сделок.
CLIENTS = {
    # общепит
    'dodo': ('Додо Пицца', 'Сеть пиццерий', 'rest', .78),
    'subway': ('Subway', 'Сеть сэндвич-баров', 'rest', .9),
    'hlebnitsa': ('Пекарня «Хлебница»', 'Сеть пекарен', 'rest', .95),
    'stardogs': ('Stardogs', 'Сеть хот-догов', 'rest', .85),
    'bjorn': ('Ресторан Björn', 'Ресторан', 'rest', 1),
    'uilliams': ("Ресторан Uilliam's", 'Ресторан', 'rest', .9),
    'cevicheria': ('Ресторан Cevicheria', 'Ресторан', 'rest', 1.05),
    'natakhtari': ('Натахтари — грузинская кухня', 'Сеть кафе', 'rest', 1.15),
    'chernyi': ('Кооператив Чёрный', 'Кофейня', 'rest', .9),
    'laolee': ('Lao Lee', 'Сеть кафе', 'rest', 1.05),
    'kv44': ('Кафе-бар «Квартира 44»', 'Кафе-бар', 'rest', 1),
    'kot': ('Бар «Кот Шрёдингера»', 'Бар', 'rest', 1),
    'neon': ('Тайский бар Neon Monkey', 'Бар', 'rest', 1.05),
    'vaffel': ('Vaffel — норвежские вафли', 'Сеть кафе', 'rest', .9),
    'peredelkino': ('Дом творчества Переделкино', 'Ресторан', 'rest', 1.1),
    # пищевое производство
    'konfael': ('Шоколадная фабрика «Конфаэль»', 'Шоколадная фабрика', 'food', 1),
    'chibis': ('Пивоварня Chibis', 'Пивоварня', 'food', 1.1),
    'rrk': ('Русская рыбная компания', 'Рыбная продукция', 'food', .95),
    'multicold': ('Multicold', 'Склады продуктов', 'food', .9),
    # магазины и торговые сети
    'lenta': ('Лента', 'Гипермаркеты', 'retail', .9),
    'selgros': ('Selgros', 'Гипермаркеты', 'retail', .9),
    'labirint': ('Книжный магазин «Лабиринт»', 'Книжные магазины', 'retail', .95),
    'winestyle': ('WineStyle', 'Винные магазины', 'retail', .95),
    'tvoydom': ('Гипермаркет «Твой Дом»', 'Гипермаркет', 'retail', .85),
    'stolichki': ('Аптеки «Столички»', 'Сеть аптек', 'retail', .95),
    '4lapy': ('Четыре Лапы', 'Зоомагазины', 'retail', .95),
    'deichmann': ('Deichmann', 'Обувные магазины', 'retail', .9),
    'fendi': ('Fendi', 'Бутик', 'retail', .95),
    'tommy': ('Tommy Hilfiger', 'Магазины одежды', 'retail', 1),
    'ck': ('Calvin Klein', 'Магазины одежды', 'retail', 1),
    # гостиницы и санатории
    'barvikha': ('Barvikha Hotel & Spa', 'Отель', 'hotel', 1),
    'mriya': ('Mriya Resort', 'Курорт', 'hotel', 1),
    'holiday': ('Holiday Inn', 'Отель', 'hotel', 1.05),
    'mirros': ('Mirros Hotels', 'Отели', 'hotel', .9),
    'victoria': ('Санаторий «Виктория»', 'Санаторий', 'hotel', 1.05),
    'pahra': ('Курорт «Красная Пахра»', 'Курорт', 'hotel', 1.05),
    # фармацевтика и медицина
    'octapharma': ('Octapharma', 'Фармпроизводство', 'pharma', .95),
    'geropharm': ('Герофарм', 'Фармпроизводство', 'pharma', .9),
    'mbpharma': ('МираксБиоФарма', 'Фармпроизводство', 'pharma', .9),
    'pharmoborona': ('Научно-испытательный центр «Фармоборона»', 'Испытания лекарств', 'pharma', .95),
    'ottobock': ('Ottobock', 'Медицинские изделия', 'pharma', .9),
    # склады и логистика
    'essilor': ('Essilor', 'Склад', 'wh', .95),
    'medintorg': ('Мединторг', 'Склад', 'wh', 1),
    'samolet': ('Самолёт', 'Склад', 'wh', .9),
    # офисы, бизнес-центры и предприятия
    'yandex': ('Яндекс', 'IT-компания', 'office', .82),
    'yandex-taxi': ('Яндекс Такси', 'Сервис такси', 'office', .9),
    'dzen': ('Дзен', 'Медиаплатформа', 'office', .9),
    'skillbox': ('Skillbox', 'Онлайн-образование', 'office', .95),
    'vtb': ('ВТБ', 'Банк', 'office', .85),
    'pt': ('Positive Technologies', 'IT-компания', 'office', 1),
    'etalon': ('Группа «Эталон»', 'Девелопер', 'office', .9),
    'alrosa': ('АЛРОСА', 'Офис', 'office', .95),
    'rzd': ('РЖД', 'Офис', 'office', .85),
    'mosgiprotrans': ('Мосгипротранс', 'Проектный институт', 'office', .95),
    'bv': ('Bureau Veritas', 'Офис', 'office', 1.1),
    'sheremetyevo': ('Аэропорт Шереметьево', 'Аэропорт', 'office', 1),
    'uralchem': ('Уралхим', 'Предприятие', 'office', 1),
    'esab': ('ESAB', 'Производство', 'office', .9),
    'dormakaba': ('dormakaba', 'Офис', 'office', 1),
    # фитнес
    'spirit': ('Spirit. Fitness', 'Фитнес-клубы', 'fit', .95),
    'fizkult': ('ФизКульт — сеть фитнес-клубов', 'Фитнес-клубы', 'fit', .95),
}
# на складских страницах — склады клиентов из разных отраслей (Яндекс, Конфаэль, Multicold, РРК — тоже склады)
EXTRA = {'wh': ['yandex', 'essilor', 'medintorg', 'konfael', 'multicold', 'rrk', 'samolet']}
ORDER = list(CLIENTS)

# отраслевые страницы — только своя отрасль; общие страницы — смесь, первыми отрасли страницы
ONLY = {
    'restorany-i-kafe': 'rest', 'dezinsektsiya/restorany-i-kafe': 'rest', 'deratizatsiya/restorany-i-kafe': 'rest',
    'pishchevoe-proizvodstvo': 'food', 'magaziny-i-torgovye-seti': 'retail', 'gostinitsy': 'hotel',
    'farmatsevticheskie-proizvodstva': 'pharma', 'sklady-i-logistika': 'wh',
    'biznes-tsentry-torgovye-tsentry-predpriyatiya': 'office',
}
LAB = ['food', 'rest', 'pharma']
MIX = {
    'dezinfektsiya': ['pharma', 'fit', 'rest', 'hotel'], 'deratizatsiya': ['food', 'rest', 'retail', 'wh'],
    'dezinsektsiya': ['rest', 'food', 'hotel'], 'deratizatsiya-i-dezinsektsiya': ['rest', 'food', 'retail'],
    'zashchita-ot-proniknoveniya-gryzunov': ['food', 'wh', 'retail'], 'sanitarnyy-audit': ['rest', 'food', 'retail'],
    'razrabotka-ppk': ['food', 'rest', 'pharma'], 'dogovor-deratizatsiya-dezinsektsiya': [],
    'ochistka-dezinfektsiya-ventilyatsii': ['rest', 'fit', 'hotel', 'office'],
    'laboratornye-issledovaniya': LAB,
    **{f'laboratornye-issledovaniya/{p}': LAB for p in (
        'analiz-smyvov', 'izmerenie-mikroklimata', 'zamer-osveshchennosti', 'analiz-vozdukha-rabochey-zony',
        'analiz-pishchevykh-produktov', 'analiz-vody', 'kontrol-sterilizatorov')},
}
PAGES = {**{k: [v] for k, v in ONLY.items()}, **MIX}
CATS = ['office', 'rest', 'retail', 'food', 'pharma', 'hotel', 'fit', 'wh']
MIX_N, HOME_N = 15, 23  # логотипов на общих страницах и на главной (+ клетка заявки)

# заголовок и подзаголовок блока по отрасли страницы
HEAD = {
    'rest': ('свои\u00a0кухни', 'Сети пиццерий и пекарен, рестораны, бары и кофейни Москвы. Работаем с заведениями '
             'любого формата — от одной кофейни до сети.'),
    'food': ('свои\u00a0производства', 'Шоколадная фабрика, пивоварня, производство и склады продуктов. Работаем '
             'по программе пест-контроля с журналами и отчётами для проверок.'),
    'retail': ('свои\u00a0магазины', 'Гипермаркеты, книжные, винные и обувные магазины, бутики и аптечная сеть. '
               'Работаем с одним магазином и с сетью.'),
    'hotel': ('свои\u00a0отели', 'Загородные отели, курорты и санатории Москвы и Подмосковья.'),
    'pharma': ('свои\u00a0производства', 'Фармацевтические производства, испытательный центр и производитель '
               'медицинских изделий.'),
    'wh': ('свои\u00a0склады', 'Склады IT-компании, оптики, фармдистрибьютора, производителей и дистрибьюторов '
           'продуктов.'),
    'office': ('свои\u00a0офисы', 'IT-компании, банк, девелоперы, проектный институт, аэропорт и промышленные '
               'предприятия.'),
    '': ('свои\u00a0объекты', 'Рестораны и пищевые производства, магазины, отели, фармпроизводства, склады и офисы. '
         'Работаем с объектами любого типа и размера — от одного кафе до сети магазинов.'),
}

AREA, HMAX, WMAX = 5000, 60, 140  # «визуальный вес» логотипа на компьютере, px²; предельные высота и ширина, px

ARR = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 11 11 5M6 5h5v5" fill="none" stroke="currentColor" '
       'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')

CSS = ('<style id="kl-st">/* блок «Наши клиенты» (tools/site/clients_block.py) */'
       '.s-kl .head{max-width:860px}'
       '.kl-wall{list-style:none;position:relative;display:grid;grid-template-columns:repeat(var(--c1,8),minmax(0,1fr));gap:1px;'
       'background:var(--line2);border:1.4px solid var(--line);border-radius:var(--r);overflow:hidden}'
       '.kl-wall::after{content:"";position:absolute;inset:0;z-index:3;pointer-events:none;opacity:0;transition:opacity .45s;'
       'background:radial-gradient(240px circle at var(--mx,-999px) var(--my,-999px),rgba(124,134,255,.13),transparent 70%)}'
       '.kl-wall.kl-lit::after{opacity:1}'
       '.kl-c{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:space-between;gap:12px;'
       'min-height:clamp(132px,9.4vw,170px);padding:clamp(20px,1.6vw,28px) 12px clamp(14px,1.1vw,18px);background:var(--bg);'
       'transition:background .35s}'
       '.kl-lw{flex:1;display:flex;align-items:center;justify-content:center;width:100%;min-height:58px}'
       '.kl-logo{width:calc(var(--w)*1px);max-width:100%;height:auto;opacity:.6;transition:opacity .35s,transform .6s var(--ease)}'
       '.kl-t{font-size:11px;font-weight:500;line-height:1.3;letter-spacing:.07em;text-transform:uppercase;text-align:center;'
       'color:var(--t4);transition:color .35s}'
       '.kl-c:hover{background:#060608}.kl-c:hover .kl-logo{opacity:1;transform:translateY(-2px)}.kl-c:hover .kl-t{color:var(--t2)}'
       '.kl-c.kl-cta{grid-column:span var(--s1,1);padding:0;background:linear-gradient(180deg,rgba(124,134,255,.13),rgba(124,134,255,.03)),var(--bg)}'
       '.kl-cta a{flex:1;display:flex;flex-direction:column;justify-content:space-between;gap:10px;width:100%;'
       'padding:clamp(15px,1.2vw,20px);color:inherit}'
       '.kl-cta:hover{background:linear-gradient(180deg,rgba(124,134,255,.22),rgba(124,134,255,.06)),var(--bg)}'
       '.kl-cta-top{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}'
       '.kl-cta-k{padding-top:3px;font-size:10.5px;font-weight:500;line-height:1.3;letter-spacing:.06em;text-transform:uppercase;color:var(--acc)}'
       '.kl-cta b{display:block;font-size:clamp(15px,1.1vw,18px);font-weight:500;line-height:1.25;letter-spacing:-.02em;color:var(--t1)}'
       '.kl-go{flex:none;width:28px;height:28px;border:1px solid rgba(124,134,255,.45);border-radius:50%;'
       'display:grid;place-items:center;color:var(--acc);transition:background .35s,color .35s,border-color .35s}'
       '.kl-go svg{width:13px;height:13px}.kl-cta:hover .kl-go{background:var(--acc3);color:#fff;border-color:var(--acc3)}'
       '.kl-more{display:none;margin:18px auto 0}'
       '@media (max-width:1279px){.kl-wall{grid-template-columns:repeat(var(--c2,6),minmax(0,1fr))}.kl-c.kl-cta{grid-column:span var(--s2,1)}}'
       '@media (max-width:899px){.kl-wall{grid-template-columns:repeat(var(--c3,4),minmax(0,1fr))}'
       '.kl-c.kl-cta{grid-column:span var(--s3o,1)}.js .kl-wall:not(.kl-open)>.kl-c.kl-cta{grid-column:span var(--s3,1)}'
       '.js .kl-wall:not(.kl-open)>.kl-c:not(.kl-cta):nth-child(n+12){display:none}.js .kl-m3+.kl-more{display:flex}}'
       '@media (max-width:599px){.kl-wall{grid-template-columns:repeat(2,minmax(0,1fr))}'
       '.kl-c.kl-cta{grid-column:span var(--s4o,1)}.js .kl-wall:not(.kl-open)>.kl-c.kl-cta{grid-column:span var(--s4,1)}'
       '.js .kl-wall:not(.kl-open)>.kl-c:not(.kl-cta):nth-child(n+8){display:none}.js .kl-m4+.kl-more{display:flex}.js .kl-wall:not(.kl-m4)+.kl-more{display:none}'
       '.kl-c{min-height:116px;padding:18px 10px 13px;gap:10px}.kl-lw{min-height:50px}'
       '.kl-logo{width:calc(var(--w)*.84px)}.kl-t{font-size:10.5px;letter-spacing:.05em}.kl-more{width:100%}'
       '.kl-cta a{padding:14px;gap:8px}.kl-cta-k{font-size:10px;letter-spacing:.05em}.kl-cta b{font-size:15px}'
       '.kl-go{width:26px;height:26px}}'
       '@media (hover:none){.kl-logo{opacity:.74}.kl-wall::after{display:none}}'
       '</style>')

JS = ('<script id="kl-js">(function(){var w=document.getElementById("kl-wall"),b=document.getElementById("kl-more");if(!w)return;'
      'if(matchMedia("(hover:hover) and (pointer:fine)").matches){'
      'w.addEventListener("pointermove",function(e){var r=w.getBoundingClientRect();'
      'w.style.setProperty("--mx",e.clientX-r.left+"px");w.style.setProperty("--my",e.clientY-r.top+"px");w.classList.add("kl-lit");},{passive:true});'
      'w.addEventListener("pointerleave",function(){w.classList.remove("kl-lit");});}'
      'if(b)b.addEventListener("click",function(){var o=w.classList.toggle("kl-open");b.setAttribute("aria-expanded",o);'
      'var t=b.querySelector(".btn-t");if(t){t.textContent=o?"Свернуть":"Показать всех клиентов";t.removeAttribute("data-t");}'
      'if(o){[].forEach.call(w.children,function(c){c.style.opacity=1;c.style.transform="none";});'
      'if(window.ScrollTrigger)ScrollTrigger.refresh();}else{w.scrollIntoView({block:"nearest"});}});})();</script>')

SEC_RE = re.compile(r'<section class="s s-kl" id="klienty".*?</section>\n?', re.S)


def _size(slug):
    m = META[slug]
    r = m['w'] / m['h']
    k = CLIENTS[slug][3]
    h = math.sqrt(AREA * k / r)
    w = r * h
    if h > HMAX * min(k, 1.15):
        h = HMAX * min(k, 1.15)
        w = r * h
    if w > WMAX:
        w = WMAX
        h = w / r
    return round(w), round(h)


def _cat(slug):
    return CLIENTS[slug][2]


def order_for(cur):
    """Логотипы страницы cur ('' — главная): отраслевая — только своя отрасль; общая — смесь, первыми отрасли страницы."""
    if cur in ONLY:
        ind = ONLY[cur]
        return list(EXTRA.get(ind) or [s for s in ORDER if _cat(s) == ind])
    lead = MIX.get(cur, [])
    seq = lead + [c for c in CATS if c not in lead]
    pools = {c: [s for s in ORDER if _cat(s) == c] for c in CATS}
    n = HOME_N if cur == '' else MIX_N
    out = []
    for c in lead:  # по два логотипа отраслей страницы
        out += [x for x in pools[c] if x not in out][:2]
    while len(out) < n and any(x not in out for c in seq for x in pools[c]):
        for c in seq:
            nxt = [x for x in pools[c] if x not in out]
            if nxt and len(out) < n:
                out.append(nxt[0])
    return out[:n]


def _cols(cells, maxc):
    rows = math.ceil(cells / maxc)
    return math.ceil(cells / rows)


def _span(cells, c):
    r = cells % c
    return 1 if r == 0 else c - r + 1


def grid(n):
    """Колонки сетки и ширина клетки заявки на компьютере, планшете и телефоне — без пустых клеток в последнем ряду."""
    cells = n + 1
    c1, c2 = _cols(cells, 8), _cols(cells, 6)
    v3, v4 = min(n, 11) + 1, min(n, 7) + 1
    c3 = _cols(v3, 4)
    return {'c1': c1, 's1': _span(cells, c1), 'c2': c2, 's2': _span(cells, c2), 'c3': c3, 's3': _span(v3, c3),
            's3o': _span(cells, c3), 's4': _span(v4, 2), 's4o': _span(cells, 2)}, n > 11, n > 7


def block(root, cur, home=False):
    key = '' if home else cur
    slugs = order_for(key)
    cells = []
    for slug in slugs:
        alt, cap, _ind, _k = CLIENTS[slug]
        w, h = _size(slug)
        cells.append(f'<li class="kl-c"><span class="kl-lw"><img class="kl-logo" src="{root}img/klienty/{slug}.webp" '
                     f'alt="{alt}" width="{w}" height="{h}" style="--w:{w}" loading="lazy" decoding="async"></span>'
                     f'<span class="kl-t">{cap}</span></li>')
    start = 'Бесплатный аудит' if home else 'Обследование 0\u00a0₽'
    cells.append(f'<li class="kl-c kl-cta"><a href="#zayavka"><span class="kl-cta-top"><span class="kl-cta-k">{start}</span>'
                 f'<span class="kl-go" aria-hidden="true">{ARR}</span></span><b>Станьте нашим клиентом</b></a></li>')
    g, more3, more4 = grid(len(slugs))
    style = ';'.join(f'--{k}:{v}' for k, v in g.items())
    cls = 'kl-wall' + (' kl-m3' if more3 else '') + (' kl-m4' if more4 else '')
    em, sub = HEAD[ONLY.get(key, '')]
    html = ('<section class="s s-kl" id="klienty" aria-labelledby="kl-h">\n  <div class="wrap">\n'
            '    <div class="head"><div class="eyebrow" data-eyebrow>Наши клиенты</div>'
            f'<h2 id="kl-h" data-split>Нам доверяют <em>{em}</em></h2>'
            f'<p class="sub" data-fade>{sub}</p></div>\n'
            f'    <ul class="{cls}" id="kl-wall" data-group="cards" style="{style}">{"".join(cells)}</ul>\n')
    if more4:
        html += ('    <button type="button" class="btn btn-o btn-sm kl-more" id="kl-more" aria-expanded="false" '
                 'aria-controls="kl-wall"><span class="btn-t">Показать всех клиентов</span></button>\n')
    html += '  </div>\n</section>\n'
    return typo(html) + JS + '\n'


def _css(s):
    s = re.sub(r'<style id="kl-st">.*?</style>', '', s, flags=re.S)
    m = re.search(r'<style id="pr-st">.*?</style>', s, re.S)
    if m and m.start() < s.index('</head>'):
        return s[:m.end()] + CSS + s[m.end():]
    # без прайса: сразу после ссылки на style.css (перед </head> нельзя — там по закону владельца стоит UIS)
    m = re.search(r'<link rel="stylesheet" href="[^"]*style\.css[^"]*">', s)
    assert m and m.start() < s.index('</head>'), 'нет ссылки на style.css'
    return s[:m.end()] + CSS + s[m.end():]


def patch(s, rel):
    """rel — адрес страницы без «/» по краям ('' — главная). Повторный вызов ничего не меняет."""
    cur = rel.strip('/')
    home = cur == ''
    root = '../' * (cur.count('/') + 1) if cur else ''
    # прежний блок убрать целиком, вместе с переводами строк, которые добавила вставка (повторный вызов — без изменений)
    s = re.sub(r'\n<section class="s s-kl" id="klienty".*?<script id="kl-js">.*?</script>\n' if home else
               r'<section class="s s-kl" id="klienty".*?<script id="kl-js">.*?</script>\n\n', '', s, count=1, flags=re.S)
    assert 'id="klienty"' not in s and 'id="kl-js"' not in s, 'блок «Наши клиенты» не на своём месте'
    html = block(root, cur, home)
    if home:
        m = re.search(r'<section class="s s-pr" id="tseny".*?</section>\n?', s, re.S)
        assert m, 'на главной нет прайса #tseny'
        s = s[:m.end()] + '\n' + html + s[m.end():]
    else:
        i = s.index('<section class="cta" id="zayavka"')
        s = s[:i] + html + '\n' + s[i:]
    return _css(s)


def main():
    """Шаг сборки (tools/site/build_site.py): блок на главной и коммерческих страницах PAGES."""
    for rel in [''] + list(PAGES):
        f = ROOT / (rel + '/index.html' if rel else 'index.html')
        old = f.read_text(encoding='utf-8')
        new = patch(old, rel)
        if new != old:
            f.write_text(new, encoding='utf-8')
            print('ok', f.relative_to(ROOT))


if __name__ == '__main__':
    main()
