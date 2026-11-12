#!/usr/bin/env python3
"""Блок «Наши клиенты» — стена логотипов клиентов (предложение 12.11.2026, ждёт согласования владельца).

Где стоит (предложение):
  * главная — 4-м блоком, сразу после общего прайса #tseny «Выберите услугу. Узнайте стоимость.», перед «Этапами» (#etapy):
    после цены следующий вопрос посетителя — «а вам можно доверять?»;
  * коммерческие страницы услуг и отраслей (PAGES) — последним блоком перед формой заявки #zayavka, после общего
    прайса или каталога «Один подрядчик»: логотипы — последний довод перед заявкой;
  * на информационных страницах («Материалы», «Нормативная база», политика и согласие) блока нет.

На отраслевых страницах первыми идут логотипы своей отрасли (FIRST), на остальных — общий порядок ORDER.
Последняя клетка — «Станьте нашим клиентом» со ссылкой на форму заявки.
На телефоне видно 7 логотипов и клетка заявки, остальные — по кнопке «Показать всех клиентов» (на планшете — 11).

Логотипы: img/klienty/*.webp (белые одноцветные, tools/klienty/make_logos.py); источник — страница клиентов
cen-dez.ru того же юрлица (ООО «Центр дезинфекционных услуг»). Список для сайта владелец подтверждает отдельно.

Счётчики, телефон и почту не трогает (ЗАКОН ВЛАДЕЛЬЦА, tools/site/tracking_laws.py); стили — сразу после
<style id="pr-st"> (или перед </head>), скрипт — сразу после блока. Повторный вызов patch() ничего не дублирует.
В tools/site/build_site.py шаг пока не включён — только после согласования.
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

# имя файла, alt, подпись под логотипом, отрасль, поправка «визуального веса» (жирные знаки — меньше, узкие — больше)
CLIENTS = {
    'yandex': ('Яндекс', 'IT-компания', 'it', .82),
    'yandex-market': ('Яндекс Маркет', 'Маркетплейс', 'it', .9),
    'yandex-taxi': ('Яндекс Такси', 'Сервис такси', 'it', .9),
    'azimut': ('AZIMUT Hotels', 'Сеть отелей', 'hotel', 1),
    'atelika': ('Ателика — сеть отелей', 'Сеть отелей', 'hotel', 1),
    'avenyu': ('Отель «Авеню»', 'Отель', 'hotel', 1),
    'grand-otel-uyut': ('Гранд Отель «Уют»', 'Отель', 'hotel', 1),
    'fizkult': ('ФизКульт — сеть фитнес-клубов', 'Фитнес-клубы', 'fit', .95),
    'orange-club': ('Фитнес-клуб Orange Club', 'Фитнес-клуб', 'fit', 1),
    'infit': ('Фитнес-клуб InFit', 'Фитнес-клуб', 'fit', 1),
    'spice': ('Фитнес-клуб Spice', 'Фитнес-клуб', 'fit', 1),
    'brusnichka': ('Брусничка — сеть фрешмаркетов', 'Фрешмаркеты', 'retail', 1),
    'shchepka': ('Ресторан «Щепка»', 'Ресторан', 'rest', 1.3),
    'ris': ('РИС — сеть ресторанов', 'Сеть ресторанов', 'rest', 1),
    'veer': ('Ресторан «Веер»', 'Ресторан', 'rest', 1),
    'ukrop': ('Кафе здорового питания «Укроп»', 'Кафе', 'rest', 1),
    'gerkules': ('Геркулес', 'Продукты питания', 'food', 1.05),
    'agrostan': ('Агростан', 'Продукты питания', 'food', 1),
    'sotsagroprodukt': ('СоцАгроПродукт', 'Продукты питания', 'food', 1),
    'stolitsa': ('Медицинский центр «Столица»', 'Медцентр', 'med', 1),
    'siti-med': ('Медицинский центр «Сити-Мед»', 'Медцентр', 'med', 1),
    'status': ('Медицинский центр «Статус»', 'Медцентр', 'med', .92),
    'vita': ('Медицинский центр «Вита»', 'Медцентр', 'med', 1),
}
# общий порядок: в каждой строке по 8 разных отраслей, первые 7 видны и на телефоне
ORDER = ['yandex', 'azimut', 'fizkult', 'brusnichka', 'shchepka', 'gerkules', 'stolitsa', 'ukrop',
         'yandex-market', 'atelika', 'orange-club', 'ris', 'agrostan', 'siti-med', 'veer', 'avenyu',
         'yandex-taxi', 'infit', 'sotsagroprodukt', 'status', 'grand-otel-uyut', 'spice', 'vita']

LAB = ['food', 'rest', 'med']
# коммерческие страницы (без «/» по краям) → отрасли, которые идут первыми; [] — общий порядок
PAGES = {
    'dezinfektsiya': ['med', 'fit', 'rest'], 'deratizatsiya': ['food', 'rest', 'retail'],
    'dezinsektsiya': ['rest', 'food', 'hotel'], 'deratizatsiya-i-dezinsektsiya': ['rest', 'food', 'retail'],
    'zashchita-ot-proniknoveniya-gryzunov': ['food', 'retail', 'rest'], 'sanitarnyy-audit': ['rest', 'food', 'retail'],
    'razrabotka-ppk': ['food', 'rest', 'retail'], 'dogovor-deratizatsiya-dezinsektsiya': [],
    'ochistka-dezinfektsiya-ventilyatsii': ['rest', 'fit', 'hotel'],
    'pishchevoe-proizvodstvo': ['food', 'rest'], 'restorany-i-kafe': ['rest', 'food'],
    'magaziny-i-torgovye-seti': ['retail', 'food'], 'gostinitsy': ['hotel', 'fit'],
    'farmatsevticheskie-proizvodstva': ['med', 'food'], 'sklady-i-logistika': ['it', 'food', 'retail'],
    'biznes-tsentry-torgovye-tsentry-predpriyatiya': ['it', 'fit', 'med'],
    'dezinsektsiya/restorany-i-kafe': ['rest', 'food'], 'deratizatsiya/restorany-i-kafe': ['rest', 'food'],
    'laboratornye-issledovaniya': LAB,
    **{f'laboratornye-issledovaniya/{p}': LAB for p in (
        'analiz-smyvov', 'izmerenie-mikroklimata', 'zamer-osveshchennosti', 'analiz-vozdukha-rabochey-zony',
        'analiz-pishchevykh-produktov', 'analiz-vody', 'kontrol-sterilizatorov')},
}

AREA, HMAX, WMAX = 4300, 56, 128  # «визуальный вес» логотипа на компьютере, px²; предельные высота и ширина, px

ARR = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 11 11 5M6 5h5v5" fill="none" stroke="currentColor" '
       'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')

CSS = ('<style id="kl-st">/* блок «Наши клиенты» (tools/site/clients_block.py) */'
       '.s-kl .head{max-width:860px}'
       '.kl-wall{list-style:none;position:relative;display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:1px;'
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
       '.kl-c.kl-cta{padding:0;background:linear-gradient(180deg,rgba(124,134,255,.13),rgba(124,134,255,.03)),var(--bg)}'
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
       '@media (max-width:1279px){.kl-wall{grid-template-columns:repeat(6,minmax(0,1fr))}}'
       '@media (max-width:899px){.kl-wall{grid-template-columns:repeat(4,minmax(0,1fr))}'
       '.js .kl-wall:not(.kl-open)>.kl-c:not(.kl-cta):nth-child(n+12){display:none}.js .kl-more{display:flex}}'
       '@media (max-width:599px){.kl-wall{grid-template-columns:repeat(2,minmax(0,1fr))}'
       '.js .kl-wall:not(.kl-open)>.kl-c:not(.kl-cta):nth-child(n+8){display:none}'
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


def order_for(cur):
    """Порядок логотипов для страницы cur ('' — главная): сначала отрасли страницы, внутри — общий порядок."""
    first = PAGES.get(cur, [])
    lead = [s for ind in first for s in ORDER if CLIENTS[s][2] == ind]
    return lead + [s for s in ORDER if s not in lead]


def block(root, cur, home=False):
    cells = []
    for slug in order_for('' if home else cur):
        alt, cap, _ind, _k = CLIENTS[slug]
        w, h = _size(slug)
        cells.append(f'<li class="kl-c"><span class="kl-lw"><img class="kl-logo" src="{root}img/klienty/{slug}.webp" '
                     f'alt="{alt}" width="{w}" height="{h}" style="--w:{w}" loading="lazy" decoding="async"></span>'
                     f'<span class="kl-t">{cap}</span></li>')
    start = 'Бесплатный аудит' if home else 'Обследование 0 ₽'
    cells.append(f'<li class="kl-c kl-cta"><a href="#zayavka"><span class="kl-cta-top"><span class="kl-cta-k">{start}</span>'
                 f'<span class="kl-go" aria-hidden="true">{ARR}</span></span><b>Станьте нашим клиентом</b></a></li>')
    html = ('<section class="s s-kl" id="klienty" aria-labelledby="kl-h">\n  <div class="wrap">\n'
            '    <div class="head"><div class="eyebrow" data-eyebrow>Наши клиенты</div>'
            '<h2 id="kl-h" data-split>Нам доверяют <em>свои\u00a0объекты</em></h2>'
            '<p class="sub" data-fade>Рестораны и пищевые производства, магазины, отели, медицинские центры, фитнес-клубы '
            'и офисы. Работаем с объектами любого типа и размера — от одного кафе до сети магазинов.</p></div>\n'
            f'    <ul class="kl-wall" id="kl-wall" data-group="cards">{"".join(cells)}</ul>\n'
            '    <button type="button" class="btn btn-o btn-sm kl-more" id="kl-more" aria-expanded="false" '
            'aria-controls="kl-wall"><span class="btn-t">Показать всех клиентов</span></button>\n'
            '  </div>\n</section>\n')
    return typo(html) + JS + '\n'


def _css(s):
    s = re.sub(r'<style id="kl-st">.*?</style>', '', s, flags=re.S)
    m = re.search(r'<style id="pr-st">.*?</style>', s, re.S)
    if m and m.start() < s.index('</head>'):
        return s[:m.end()] + CSS + s[m.end():]
    return s.replace('</head>', CSS + '</head>', 1)


def patch(s, rel):
    """rel — адрес страницы без «/» по краям ('' — главная). Повторный вызов ничего не меняет."""
    cur = rel.strip('/')
    home = cur == ''
    root = '../' * (cur.count('/') + 1) if cur else ''
    s = SEC_RE.sub('', s)
    s = re.sub(r'<script id="kl-js">.*?</script>\n?', '', s, flags=re.S)
    html = block(root, cur, home)
    if home:
        m = re.search(r'<section class="s s-pr" id="tseny".*?</section>\n?', s, re.S)
        assert m, 'на главной нет прайса #tseny'
        s = s[:m.end()] + '\n' + html + s[m.end():]
    else:
        i = s.index('<section class="cta" id="zayavka"')
        s = s[:i] + html + '\n' + s[i:]
    return _css(s)


if __name__ == '__main__':
    print('Шаг сборки ещё не включён: блок ждёт согласования. Превью — python3 tools/klienty-preview/build.py')
