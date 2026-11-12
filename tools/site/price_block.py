#!/usr/bin/env python3
"""Общий прайс на услуги «Выберите услугу. Узнайте стоимость.» (вариант 2, согласован владельцем 11.11.2026).

Где стоит (согласовано по скриншотам 11.11.2026):
  * главная — третьим экраном, перед «Этапами работы» (#etapy), якорь #tseny; пункт меню «Цена» ведёт сюда с главной, политики и согласия
    (на остальных страницах — к своему блоку цен: tools/site/menu_anchors.py, с 12.11.2026);
    прежний блок #usloviya «Стоимость под ваш объект» переименован в «Типовые задачи наших клиентов»;
    плитка «Пест-контроль по системе IPM» на главной — текущая страница: зелёная метка «Вы здесь», без ссылки
    (раньше вела к #podhod через «Этапы работы»; по предложению владельца 12.11.2026), как своя услуга на страницах ниже;
  * страницы услуг и отраслей (PRICE_PAGES) — вместо блока «Один подрядчик — все санитарные задачи» перед формой
    заявки (якорь #vse-uslugi сохраняется, пункт меню «Все услуги» ведёт к прайсу);
  * на остальных страницах остаётся каталог «Один подрядчик» (tools/site/services_block.py) с теми же ценами.

Первые четыре позиции (указание владельца): пест-контроль от 3 900 ₽/мес, дезинсекция от 3 500 ₽, дератизация
от 3 500 ₽, дератизация + дезинсекция от 4 900 ₽/мес. Вентиляция — от 25 000 ₽ (указание владельца).

Только HTML/CSS, без скриптов и картинок. Счётчики, телефон и почту не трогает (ЗАКОН ВЛАДЕЛЬЦА,
tools/site/tracking_laws.py): стили вставляются перед <style id="m-crumbs"> или <!-- UIS -->, не вплотную к </head>.

Шаг сборки tools/site/build_site.py после services_block.py; повторный запуск ничего не дублирует.
patch(s, rel) работает и с готовыми index.php с сайта (выкладка на Timeweb, tools/deploy/prepare-2026-11-11-price.py).
Запуск: python3 tools/site/price_block.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
from typo import typo  # noqa: E402

# (адрес без «/», надзаголовок карточки, название, описание, цена, единица)
CARDS = [
    ('', '01 / Постоянная защита', 'Пест-контроль<br>по системе IPM', 'Мониторинг и защита объекта по графику, журнал и акты.', '3 900', 'в месяц'),
    ('dezinsektsiya', '02 / Насекомые', 'Дезинсекция', 'Тараканы, муравьи, мухи и другие насекомые.', '3 500', 'за выезд'),
    ('deratizatsiya', '03 / Грызуны', 'Дератизация', 'Борьба с крысами и мышами на вашем объекте.', '3 500', 'за обработку'),
    ('deratizatsiya-i-dezinsektsiya', '04 / Комплекс', 'Дератизация<br>+ дезинсекция', 'Грызуны и насекомые по одному договору.', '4 900', 'в месяц'),
]
MINIS = [
    ('dezinfektsiya', 'Дезинфекция помещений', 'Обеззараживание поверхностей и оборудования', '3 500', 'за обработку'),
    ('sanitarnyy-audit', 'Санитарный аудит', 'Обследование и оценка санитарных рисков', '9 000', 'за обследование'),
    ('ochistka-dezinfektsiya-ventilyatsii', 'Очистка и дезинфекция вентиляции', 'Воздуховоды, вытяжки и вентсистемы', '25 000', 'стоимость работ'),
    ('laboratornye-issledovaniya', 'Лабораторный контроль по ППК', 'Исследования и замеры для вашего объекта', '2 600', 'за комплекс исследований'),
]
ALSO = [('razrabotka-ppk', 'разработка ППК'),
        ('normativnaya-baza/dokumenty-dlya-rospotrebnadzora', 'документы для Роспотребнадзора'),
        ('dogovor-deratizatsiya-dezinsektsiya', 'договор на обслуживание')]

# страницы, где прайс стоит вместо каталога «Один подрядчик» (услуги и отрасли)
PRICE_PAGES = [
    'dezinsektsiya', 'deratizatsiya', 'deratizatsiya-i-dezinsektsiya', 'dezinfektsiya',
    'ochistka-dezinfektsiya-ventilyatsii', 'sanitarnyy-audit', 'laboratornye-issledovaniya',
    'zashchita-ot-proniknoveniya-gryzunov', 'dezinsektsiya/restorany-i-kafe', 'deratizatsiya/restorany-i-kafe',
    'pishchevoe-proizvodstvo', 'restorany-i-kafe', 'magaziny-i-torgovye-seti', 'gostinitsy',
    'farmatsevticheskie-proizvodstva', 'sklady-i-logistika', 'biznes-tsentry-torgovye-tsentry-predpriyatiya',
]

# минимальная стоимость заказа под таблицей #stoimost, чтобы цены «от … ₽ за м²/м. п.» не спорили с прайсом
MIN_NOTES = {
    'ochistka-dezinfektsiya-ventilyatsii': 'Минимальная стоимость заказа на очистку и дезинфекцию вентиляции — 25 000 ₽.',
}

# цены каталога «Один подрядчик» на сайте до 11.11.2026 → новые (для готовых страниц с сайта)
VU_PRICES = {
    'договор от 3 500 ₽/мес': 'договор от 3 900 ₽/мес',
    'от 600 ₽ за точку': 'от 3 500 ₽',
    'от 9 ₽ за м²': 'от 3 500 ₽',
    'от 45 ₽ за п. м': 'от 25 000 ₽',
    'смывы от 310 ₽': 'от 2 600 ₽',
}

ARR = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 11 11 5M6 5h5v5" fill="none" stroke="currentColor" '
       'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')

CSS = ('<style id="pr-st">/* общий прайс на услуги (tools/site/price_block.py) */'
       '.s-pr .head{max-width:820px}'
       '.pr-cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}'
       '.pr-card{display:flex;flex-direction:column;min-height:300px;padding:clamp(22px,1.8vw,30px);color:inherit;text-decoration:none;transition:border-color .3s,transform .3s}'
       'a.pr-card:hover,a.pr-card:focus-visible{border-color:rgba(124,134,255,.5)}'
       '.pr-card.pr-main{border-color:rgba(124,134,255,.55);background:linear-gradient(180deg,rgba(124,134,255,.09),rgba(124,134,255,.02)),var(--card)}'
       '.pr-num{display:flex;justify-content:space-between;align-items:center;gap:12px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--t3);margin-bottom:26px}'
       '.pr-go{flex:none;width:28px;height:28px;border:1px solid var(--line2);border-radius:50%;display:grid;place-items:center;color:var(--acc)}'
       '.pr-go svg{width:14px;height:14px}'
       '.pr-here{flex:none;font-size:11px;letter-spacing:.04em;text-transform:none;color:var(--acc);border:1px solid rgba(124,134,255,.4);border-radius:20px;padding:4px 10px}'
       '.pr-card h3{font-size:clamp(20px,1.5vw,24px);font-weight:500;letter-spacing:-.03em;line-height:1.25;margin:0 0 12px}'
       '.pr-card p{margin:0 0 26px;color:var(--t2);font-size:15px;line-height:1.55}'
       '.pr-price{margin-top:auto}'
       '.pr-amt{font-size:clamp(34px,2.6vw,42px);font-weight:400;letter-spacing:-.05em;white-space:nowrap;color:var(--t1)}'
       '.pr-main .pr-amt{color:#b5bcff}'
       '.pr-from{font-size:16px;color:var(--t2);margin-right:6px;letter-spacing:0}'
       '.pr-unit{display:block;margin-top:6px;font-size:13px;color:var(--t3)}'
       '.pr-more-t{font-size:clamp(18px,1.3vw,22px);font-weight:400;letter-spacing:-.02em;margin:clamp(36px,3vw,52px) 0 6px}'
       '.pr-more{display:grid;grid-template-columns:1fr 1fr;column-gap:48px}'
       '.pr-mini{display:flex;justify-content:space-between;align-items:center;gap:18px;padding:20px 0;border-top:1px solid var(--line2);color:inherit;text-decoration:none;transition:color .25s}'
       'a.pr-mini:hover b,a.pr-mini:focus-visible b{color:#b5bcff}'
       '.pr-mini b{display:block;font-weight:500;font-size:16px;letter-spacing:-.01em;margin-bottom:5px;transition:color .25s}'
       '.pr-mini .pr-d{display:block;font-size:14px;color:var(--t3)}'
       '.pr-mini .pr-here{margin-left:8px;vertical-align:2px}'
       '.pr-mini .pr-amt{font-size:26px}.pr-mini .pr-from{font-size:13px}'
       '.pr-mini .pr-price{text-align:right;margin:0}'
       '.pr-fine{display:flex;justify-content:space-between;gap:32px;margin-top:22px;font-size:13.5px;line-height:1.6;color:var(--t3)}'
       '.pr-fine p{margin:0;max-width:760px}.pr-fine b{color:var(--t1);font-weight:500;white-space:nowrap}'
       '.pr-also{margin:12px 0 0;font-size:13.5px;color:var(--t3)}'
       '.pr-also a{color:var(--t2);text-decoration:underline;text-decoration-color:var(--line2);text-underline-offset:3px}'
       '.pr-also a:hover{color:var(--t1)}'
       '.pr-cta{margin-top:28px;padding:clamp(22px,2vw,30px);display:flex;justify-content:space-between;align-items:center;gap:28px;border-color:rgba(124,134,255,.35)}'
       '.pr-cta h3{font-size:clamp(20px,1.5vw,24px);font-weight:400;letter-spacing:-.03em;margin:0 0 6px}'
       '.pr-cta p{margin:0;color:var(--t2);font-size:15px}.pr-cta .btn{flex:none}'
       '.s-pr.pr-low{content-visibility:auto;contain-intrinsic-size:auto 1250px}'
       '@media (max-width:1100px){.pr-cards{grid-template-columns:repeat(2,minmax(0,1fr))}}'
       '@media (max-width:700px){.pr-cards{grid-template-columns:minmax(0,1fr);gap:12px}'
       '.pr-card{min-height:0;padding:22px}.pr-num{margin-bottom:16px}.pr-card p{margin-bottom:16px;font-size:14px}'
       '.pr-amt{font-size:32px}.pr-more{grid-template-columns:minmax(0,1fr)}'
       '.pr-mini{flex-direction:column;align-items:flex-start;gap:10px}.pr-mini .pr-price{text-align:left}'
       '.pr-mini .pr-amt{font-size:24px}.pr-mini .pr-unit{display:inline;margin-left:8px;font-size:12px}'
       '.pr-fine{display:block;font-size:13px}.pr-fine b{display:block;margin-top:8px}'
       '.pr-cta{display:block}.pr-cta .btn{margin-top:18px;width:100%;justify-content:center}'
       '.s-pr.pr-low{contain-intrinsic-size:auto 2500px}}'
       '</style>')

SEC_RE = re.compile(r'<section class="s s-pr[^"]*" id="[^"]*".*?</section>\n?', re.S)
VU_RE = re.compile(r'<section class="s s-vu" id="vse-uslugi".*?</section>\n?', re.S)
NBSP = re.compile(r'[\s\u00a0\u202f]+')


def _amt(a, u):
    a = a.replace(' ', '\u00a0')
    return (f'<div class="pr-price"><span class="pr-amt"><span class="pr-from">от</span>{a}\u00a0₽</span>'
            f'<span class="pr-unit">{u}</span></div>')


def _href(root, slug):
    if slug == '':
        return '#podhod' if root == '' else root
    return f'{root}{slug}/'


def block(root, cur, home=False):
    cards = []
    for n, (slug, num, title, desc, a, u) in enumerate(CARDS):
        cls = 'card pr-card' + (' pr-main' if n == 0 else '')
        # своя услуга — метка «Вы здесь» и без ссылки на себя. Главная и есть «Пест-контроль по системе IPM»: плитка
        # не ведёт к #podhod через «Этапы работы» (предложение владельца 12.11.2026), метка зелёная (стиль — tools/home-scheme/scheme.css)
        here = slug == cur
        mark = '<span class="pr-here">Вы здесь</span>' if here else f'<span class="pr-go" aria-hidden="true">{ARR}</span>'
        if home and here:
            mark = '<span class="pr-here pr-here-g">Вы здесь</span>'
        inner = f'<div class="pr-num">{num}{mark}</div><h3>{title}</h3><p>{desc}</p>{_amt(a, u)}'
        if here:
            cards.append(f'<div class="{cls}" aria-current="page">{inner}</div>')
        else:
            cards.append(f'<a class="{cls}" href="{_href(root, slug)}">{inner}</a>')
    minis = []
    for slug, title, desc, a, u in MINIS:
        here = slug == cur
        pill = '<span class="pr-here">Вы здесь</span>' if here else ''
        txt = (f'<span><b>{title}{pill}</b>'
               f'<span class="pr-d">{desc}</span></span>{_amt(a, u)}')
        minis.append(f'<div class="pr-mini" aria-current="page">{txt}</div>' if here
                     else f'<a class="pr-mini" href="{_href(root, slug)}">{txt}</a>')
    also = ''
    if not home:
        links = [f'<a href="{root}{s}/">{t}</a>' for s, t in ALSO if s != cur]
        also = '<p class="pr-also">Также: ' + ' · '.join(links) + '</p>'
    sid, cls = ('tseny', 's s-pr') if home else ('vse-uslugi', 's s-pr pr-low')
    html = (f'<section class="{cls}" id="{sid}" aria-labelledby="pr-h">\n  <div class="wrap">\n'
            '    <div class="head"><div class="eyebrow" data-eyebrow>Цены на услуги</div>'
            '<h2 id="pr-h" data-split>Выберите услугу. <em>Узнайте стоимость.</em></h2>'
            '<p class="sub" data-fade>Разовый выезд или регулярная защита объекта по договору. Начальные цены '
            'для организаций и ИП в Москве и Московской области.</p></div>\n'
            f'    <div class="pr-cards" data-group="cards">{"".join(cards)}</div>\n'
            '    <h3 class="pr-more-t">Другие услуги</h3>\n'
            f'    <div class="pr-more">{"".join(minis)}</div>\n'
            '    <div class="pr-fine"><p>Начальные цены на работы. Итоговую стоимость согласуем до начала работ после '
            'обследования: учтём площадь, состояние объекта, объём работ и периодичность обслуживания.</p>'
            '<b>Обследование и расчёт — 0 ₽</b></div>\n'
            + (f'    {also}\n' if also else '')
            + '    <div class="card pr-cta"><div><h3>Не знаете, какая услуга нужна?</h3><p>Осмотрим объект и предложим '
            'подходящий состав работ, без лишних услуг.</p></div><a class="btn btn-w btn-lg" href="#zayavka">'
            '<span class="btn-t">Заказать бесплатный осмотр</span></a></div>\n'
            '  </div>\n</section>\n')
    return typo(html)


def _css(s):
    s = re.sub(r'<style id="pr-st">.*?</style>', '', s, flags=re.S)
    head = s[:s.index('</head>')]
    for mark in ('<style id="m-crumbs">', '<!-- UIS -->'):
        if mark in head:
            return s.replace(mark, CSS + mark, 1)
    return s.replace('</head>', CSS + '</head>', 1)


def _vu_prices(s):
    def sub(m):
        t = NBSP.sub(' ', m.group(1))
        new = VU_PRICES.get(t)
        return f'<span class="vu-p">{typo(new)}</span>' if new else m.group(0)
    return re.sub(r'<span class="vu-p">([^<]*)</span>', sub, s)


def patch(s, rel):
    """rel — адрес страницы без «/» по краям ('' — главная). Повторный вызов ничего не меняет."""
    cur = rel.strip('/')
    root = '../' * (cur.count('/') + 1) if cur else ''
    home = cur == ''
    s = _vu_prices(s)
    # пункт «Цена» в шапке, мобильном меню и подвале — к прайсу главной; к своему блоку цен страницы его затем
    # переводит tools/site/menu_anchors.py (решение владельца 12.11.2026)
    s = re.sub(r'href="((?:\.\./)*)#usloviya"', r'href="\1#tseny"', s)
    if home:
        s = SEC_RE.sub('', s)
        s, n = re.subn(r'(<section class="s" id="usloviya">.*?<div class="eyebrow"[^>]*>)Цена(</div>\s*<h2[^>]*>)'
                       r'Стоимость <em>под ваш объект</em>(</h2>\s*<p class="sub"[^>]*>).*?(</p>)',
                       r'\1Примеры работ\2Типовые задачи <em>наших клиентов</em>\3'
                       + typo('Как запускаем обслуживание на объектах разного типа — от первого выезда до регулярного контроля.')
                       + r'\4', s, count=1, flags=re.S)
        assert n == 1 or 'Типовые задачи <em>наших клиентов</em>' in s, 'главная: блок #usloviya не найден'
        i = s.index('<section class="s" id="etapy">')
        s = s[:i] + block('', '', home=True) + s[i:]
    s = re.sub(r'\n    <p class="d-note pr-min"[^>]*>.*?</p>', '', s)  # на дезинфекции строка снята 11.11.2026 (price_laws)
    if cur in MIN_NOTES:
        i = s.index('id="stoimost"')
        j = s.index('</table>', i) + len('</table>')
        s = s[:j] + f'\n    <p class="d-note pr-min" data-fade>{MIN_NOTES[cur]}</p>' + s[j:]
    if cur in PRICE_PAGES:
        if SEC_RE.search(s):  # прайс уже стоит: обновляем на месте, каталог (если его снова добавила сборка) убираем
            s = VU_RE.sub('', s)
            s = SEC_RE.sub(lambda m: block(root, cur), s, count=1)
        elif VU_RE.search(s):
            s = VU_RE.sub(lambda m: block(root, cur), s, count=1)
        else:
            raise ValueError(rel + ': нет блока «Один подрядчик» (#vse-uslugi)')
    elif not home:
        return s
    return _css(s)


def main():
    sys.path.insert(0, str(ROOT / 'tools' / 'menu'))
    from apply_menu import PAGES
    for rel, root, cur in PAGES:
        f = ROOT / rel
        page = rel[:-len('index.html')].strip('/')
        old = f.read_text(encoding='utf-8')
        new = patch(old, page)
        if new != old:
            f.write_text(new, encoding='utf-8')
            print('ok', rel)


if __name__ == '__main__':
    main()
