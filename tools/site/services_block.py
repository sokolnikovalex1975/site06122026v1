#!/usr/bin/env python3
"""Блок «Все услуги» (согласован владельцем 11.11.2026): краткая витрина всех услуг сайта перед формой заявки.

Ставится на каждой странице перед <section class="cta" id="zayavka">. Текущая услуга в списке отмечена «Вы здесь»
и не ссылается сама на себя. Только HTML/CSS и встроенные SVG-иконки — без фото и без скриптов (около 3,5 КБ в gzip).
Шаг сборки tools/site/build_site.py после tools/menu/apply_menu.py; повторный запуск заменяет прежний блок.
В меню «Услуги» (шапка и телефон) последний пункт «Все услуги» ведёт к этому блоку (#vse-uslugi).
В индекс поиска блок не попадает (SKIP_SECTIONS в tools/search/build_index.py).
Запуск: python3 tools/site/services_block.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'tools' / 'legal'))
from typo import typo  # noqa: E402

P = 'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"'
ICON = {  # 24×24, линии
    'ipm': f'<circle cx="12" cy="12" r="8.5" {P}/><circle cx="12" cy="12" r="4.5" {P}/><path d="M12 2v3M12 19v3M2 12h3M19 12h3" {P}/>',
    'rat': f'<rect x="3.5" y="7" width="17" height="11" rx="2" {P}/><path d="M8.5 18v-3.5a3.5 3.5 0 0 1 7 0V18M7 10.5h2M15 10.5h2" {P}/>',
    'bug': f'<ellipse cx="12" cy="13.5" rx="4.5" ry="6" {P}/><path d="M12 7.5v12M9.5 5 8 3M14.5 5 16 3M7.5 11 4 9.5M7.5 15 4 16.5M16.5 11 20 9.5M16.5 15 20 16.5" {P}/>',
    'both': f'<rect x="3" y="3" width="8" height="8" rx="2" {P}/><rect x="13" y="13" width="8" height="8" rx="2" {P}/><path d="M13 7h4a2 2 0 0 1 2 2v2M11 17H7a2 2 0 0 1-2-2v-2" {P}/>',
    'drop': f'<path d="M12 3.5s6 6.6 6 10.8a6 6 0 0 1-12 0C6 10.1 12 3.5 12 3.5Z" {P}/><path d="M9.5 14.5a2.5 2.5 0 0 0 2.5 2.5" {P}/>',
    'fan': f'<circle cx="12" cy="12" r="9" {P}/><path d="M12 12c0-3 1-5.5 3.5-5.5S18 9 12 12Zm0 0c3 0 5.5 1 5.5 3.5S15 18 12 12Zm0 0c0 3-1 5.5-3.5 5.5S6 15 12 12Zm0 0c-3 0-5.5-1-5.5-3.5S9 6 12 12Z" {P}/>',
    'audit': f'<rect x="5" y="4" width="14" height="17" rx="2" {P}/><path d="M9 4V3h6v1M8.5 12.5l2 2 4-4.5" {P}/>',
    'lab': f'<path d="M9.5 3h5M10.5 3v6L5 18.5A1.7 1.7 0 0 0 6.5 21h11a1.7 1.7 0 0 0 1.5-2.5L13.5 9V3M7.5 15h9" {P}/>',
    'ppk': f'<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8Z" {P}/><path d="M14 3v5h5M9 13h6M9 17h4" {P}/>',
    'folder': f'<path d="M3.5 7a2 2 0 0 1 2-2h4l2 2h7a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2Z" {P}/><path d="M9 13l2 2 4-4" {P}/>',
}
ARR = f'<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" {P}/></svg>'

# адрес ('' — главная), иконка, название, коротко, цена «от»
GROUPS = [
    ('Пест-контроль', [
        ('', 'ipm', 'Пест-контроль для бизнеса', 'Постоянное обслуживание по IPM: мониторинг, программа, отчёты', 'договор от 3 900 ₽/мес'),
        ('deratizatsiya', 'rat', 'Дератизация', 'Крысы и мыши: три контура защиты, точки контроля, акты', 'от 3 500 ₽'),
        ('dezinsektsiya', 'bug', 'Дезинсекция', 'Тараканы, мухи, моль — без остановки работы объекта', 'от 3 500 ₽'),
        ('deratizatsiya-i-dezinsektsiya', 'both', 'Дератизация и дезинсекция', 'Комплекс по одному договору и общему графику', 'от 4 900 ₽/мес'),
    ]),
    ('Санитарная обработка', [
        ('dezinfektsiya', 'drop', 'Дезинфекция', 'Плановая и внеплановая обработка помещений', 'от 3 500 ₽'),
        ('ochistka-dezinfektsiya-ventilyatsii', 'fan', 'Очистка и дезинфекция вентиляции', 'Воздуховоды и кухонные вытяжки, видео до и после', 'от 25 000 ₽'),
    ]),
    ('Контроль и документы', [
        ('sanitarnyy-audit', 'audit', 'Санитарный аудит (СЭС-аудит)', 'По проверочным листам: акт с реестром нарушений', 'от 9 000 ₽'),
        ('laboratornye-issledovaniya', 'lab', 'Лабораторные исследования', 'Смывы, воздух, вода, микроклимат по ППК', 'от 2 600 ₽'),
        ('razrabotka-ppk', 'ppk', 'Разработка ППК', 'Программа производственного контроля, в том числе по ХАССП', 'от 5 900 ₽'),
        ('normativnaya-baza/dokumenty-dlya-rospotrebnadzora', 'folder', 'Документы для Роспотребнадзора', 'Перечень к проверке и чек-лист в PDF', 'бесплатно'),
    ]),
]

CSS = ('<style id="vu-st">/* блок «Все услуги» (tools/site/services_block.py) */'
       # блок ниже первого экрана: браузер не верстает его до подхода (LCP телефона 2,2 → 2,0 с в Lighthouse)
       '.s-vu{content-visibility:auto;contain-intrinsic-size:auto 1000px}'
       '.s-vu .vu-head{display:grid;grid-template-columns:minmax(0,1.7fr) minmax(0,1fr);gap:20px 64px;align-items:end;margin-bottom:clamp(32px,3vw,52px)}'
       '.s-vu .vu-head .head{margin:0}.s-vu .vu-head h2{margin:0}.vu-lead{font-size:17px;line-height:1.6;color:var(--t3);margin:0;max-width:480px}'
       '.vu-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(12px,1.1vw,20px);align-items:start}'
       '.vu-col{display:flex;flex-direction:column;gap:clamp(12px,1.1vw,20px)}'
       '.vu-g{padding:8px;border-radius:20px}'
       '.vu-gt{display:flex;justify-content:space-between;align-items:center;padding:16px 16px 8px;font-size:12px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:var(--acc)}'
       '.vu-gt span{color:var(--t3);letter-spacing:.04em}'
       '.vu-i{position:relative;display:grid;grid-template-columns:40px minmax(0,1fr) auto;gap:14px;align-items:start;padding:16px;border-radius:14px;color:var(--t2);text-decoration:none;transition:background .3s}'
       'a.vu-i:hover,a.vu-i:focus-visible{background:rgba(255,255,255,.05)}'
       '.vu-i+.vu-i::before{content:"";position:absolute;left:70px;right:16px;top:0;height:1px;background:var(--line)}'
       '.vu-ic{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;background:rgba(99,102,241,.12);color:#a5abff}'
       '.vu-ic svg{width:22px;height:22px}'
       '.vu-b{display:flex;flex-direction:column;gap:4px;min-width:0}'
       '.vu-t{font-size:16px;line-height:1.3;color:var(--t1);letter-spacing:-.01em}'
       '.vu-d{font-size:14px;line-height:1.45;color:var(--t3)}'
       '.vu-p{margin-top:4px;font-size:13px;line-height:1.3;color:var(--t2);font-weight:500}'
       '.vu-a{align-self:center;width:32px;height:32px;border-radius:50%;border:1.4px solid var(--line2);display:grid;place-items:center;color:var(--t1);transition:background .3s,border-color .3s,color .3s,transform .4s var(--ease)}'
       '.vu-a svg{width:13px;height:13px}'
       'a.vu-i:hover .vu-a,a.vu-i:focus-visible .vu-a{background:var(--t1);border-color:var(--t1);color:#000;transform:translateX(3px)}'
       '.vu-i.is-cur{background:rgba(99,102,241,.1);box-shadow:inset 0 0 0 1px rgba(124,134,255,.35)}'
       '.vu-i.is-cur+.vu-i::before,.vu-i+.vu-i.is-cur::before{display:none}'
       '.vu-here{align-self:center;font-size:11px;font-weight:500;letter-spacing:.1em;text-transform:uppercase;color:#a5abff;white-space:nowrap}'
       '.vu-cta{padding:clamp(24px,1.8vw,32px);border-radius:20px;display:flex;flex-direction:column;gap:12px;'
       'background:radial-gradient(120% 140% at 100% 0%,rgba(99,102,241,.32),rgba(99,102,241,0) 60%),var(--bg2)}'
       '.vu-cta b{font-size:clamp(19px,1.3vw,24px);font-weight:400;line-height:1.25;letter-spacing:-.02em;color:var(--t1)}'
       '.vu-cta p{margin:0;font-size:15px;line-height:1.55;color:var(--t3)}.vu-cta .btn{align-self:flex-start;margin-top:10px}'
       '@media (max-width:1180px){.vu-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.vu-col:nth-child(3){grid-column:1/-1}'
       '.vu-col:nth-child(3) .vu-g{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}.vu-col:nth-child(3) .vu-gt{grid-column:1/-1}'
       '.vu-col:nth-child(3) .vu-i:nth-child(3)::before{display:none}}'
       '@media (max-width:900px){.s-vu .vu-head{grid-template-columns:1fr}}'
       '@media (max-width:760px){.vu-grid{display:flex;flex-direction:column;gap:12px}.vu-col{display:contents}.vu-g,.vu-cta{width:100%;box-sizing:border-box}.vu-cta{order:9}'
       '.vu-col:nth-child(3) .vu-g{grid-template-columns:1fr}.vu-col:nth-child(3) .vu-i:nth-child(3)::before{display:block}'
       '.vu-g{padding:4px}.vu-gt{padding:14px 12px 6px}.vu-i{grid-template-columns:36px minmax(0,1fr) auto;gap:12px;padding:12px;align-items:center}'
       '.vu-i+.vu-i::before{left:60px;right:12px}.vu-ic{width:36px;height:36px;border-radius:10px}.vu-ic svg{width:20px;height:20px}'
       '.vu-b{gap:2px}.vu-t{font-size:15px}.vu-d{display:none}.vu-p{margin:0;font-weight:400;color:var(--t3)}'
       '.vu-lead{font-size:16px}.vu-cta .btn{align-self:stretch}.s-vu{contain-intrinsic-size:auto 1700px}}'
       '</style>')


def item(root, cur, slug, ic, title, desc, price):
    icon = f'<span class="vu-ic" aria-hidden="true"><svg viewBox="0 0 24 24">{ICON[ic]}</svg></span>'
    body = f'<span class="vu-b"><span class="vu-t">{title}</span><span class="vu-d">{desc}</span><span class="vu-p">{price}</span></span>'
    if slug == cur:
        return f'<div class="vu-i is-cur" aria-current="page">{icon}{body}<span class="vu-here">Вы здесь</span></div>'
    href = (root + slug + '/') if slug else (root or './')
    return f'<a class="vu-i" href="{href}">{icon}{body}<span class="vu-a" aria-hidden="true">{ARR}</span></a>'


def block(root, cur):
    cols = []
    for n, (gt, items) in enumerate(GROUPS):
        rows = ''.join(item(root, cur, *it) for it in items)
        g = f'<div class="card vu-g"><div class="vu-gt">{gt}<span>{len(items)}</span></div>{rows}</div>'
        if n == 1:
            g += ('<div class="card vu-cta"><b>Нужно несколько услуг?</b>'
                  '<p>Осмотрим объект за один выезд и рассчитаем всё вместе — с общим графиком работ и комплектом документов.</p>'
                  '<a class="btn btn-w btn-sm" href="#zayavka"><span class="btn-t">Рассчитать комплекс</span></a></div>')
        cols.append(f'<div class="vu-col">{g}</div>')
    html = ('<section class="s s-vu" id="vse-uslugi" aria-labelledby="vu-h">\n  <div class="wrap">\n'
            '    <div class="vu-head"><div class="head"><div class="eyebrow" data-eyebrow>Все услуги Центра</div>'
            '<h2 id="vu-h" data-split>Один подрядчик — <em>все санитарные задачи</em></h2></div>'
            '<p class="vu-lead">Пест-контроль, санитарная обработка, лабораторный контроль и документы к проверке '
            'Роспотребнадзора для организаций Москвы и области.</p></div>\n'
            f'    <div class="vu-grid" data-group="cards">{"".join(cols)}</div>\n  </div>\n</section>\n')
    return typo(html)


def apply(s, root, cur):
    s = re.sub(r'<section class="s s-vu" id="vse-uslugi".*?</section>\n', '', s, flags=re.S)
    s = re.sub(r'<style id="vu-st">.*?</style>', '', s, flags=re.S)
    # стили — перед <style id="m-crumbs"> (он есть на всех страницах), не вплотную к </head>: на Timeweb прямо перед
    # </head> стоит код UIS (ЗАКОН ВЛАДЕЛЬЦА, tools/site/tracking_laws.py), между ними ничего не вставляем
    head = s[:s.index('</head>')]
    for mark in ('<style id="m-crumbs">', '<!-- UIS -->'):
        if mark in head:
            s = s.replace(mark, CSS + mark, 1)
            break
    else:
        s = s.replace('</head>', CSS + '</head>', 1)
    i = s.index('<section class="cta" id="zayavka">')
    return s[:i] + block(root, cur) + s[i:]


def main():
    sys.path.insert(0, str(ROOT / 'tools' / 'menu'))
    from apply_menu import PAGES
    for rel, root, cur in PAGES:
        f = ROOT / rel
        s = f.read_text(encoding='utf-8')
        if '<section class="cta" id="zayavka">' not in s:
            print('нет формы заявки — пропуск', rel)
            continue
        f.write_text(apply(s, root, cur), encoding='utf-8')
        print('ok', rel)


if __name__ == '__main__':
    main()
