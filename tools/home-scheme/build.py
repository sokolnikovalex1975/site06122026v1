#!/usr/bin/env python3
"""Главная: интерактивный блок «Схема объекта» (#shema) — заказ владельца 11–12.11.2026.

    python3 tools/home-scheme/build.py

Четыре вкладки — пищевое производство, рестораны и кафе, склады и логистика, БЦ/ТЦ/предприятия.
Планы берутся из готовых отраслевых страниц репозитория (секция с .f-zmap), поэтому схема на главной
всегда совпадает с отраслевой. Стили планов каждой отрасли берутся из её страницы и ограничиваются
классом панели (.hz-food, .hz-rest, .hz-sklad, .hz-bc), id внутри SVG получают префикс — без конфликтов.

Блок ставится после «Пест-менеджмент по системе IPM» (#podhod), перед «Документами» (#dokumenty),
между метками <!-- home-scheme:start --> … <!-- home-scheme:end -->. Стили — <style id="hz-st"> в <head>,
скрипт — <script id="hz-js"> перед </body>. Повторный запуск заменяет блок, а не дублирует.
Счётчики, телефон и почту скрипт не трогает (ЗАКОН ВЛАДЕЛЬЦА — tools/site/tracking_laws.py).
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
HERE = pathlib.Path(__file__).resolve().parent
PAGES = [  # ключ, адрес, вкладка, подпись вкладки, текст ссылки «Подробнее»
    ('food', 'pishchevoe-proizvodstvo', 'Пищевое производство', 'Цеха, склад сырья, упаковка', 'пищевое производство'),
    ('rest', 'restorany-i-kafe', 'Ресторан и кафе', 'Кухня, бар, зал, подвал', 'рестораны и кафе'),
    ('sklad', 'sklady-i-logistika', 'Склад и логистика', 'Доки, стеллажи, периметр', 'склады и логистика'),
    ('bc', 'biznes-tsentry-torgovye-tsentry-predpriyatiya', 'БЦ, ТЦ, предприятие', 'Паркинг, подвал, фуд-корт',
     'бизнес-центры, ТЦ и предприятия'),
]
ARR = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 11 11 5M6 5h5v5" fill="none" stroke="currentColor" '
       'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')
KEY = re.compile(r'\.(f-plan|w-plan|b-plan|lg-[\w-]+|f-legend)(?![\w-])')


def rules(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find('{', i)
        if j < 0:
            break
        sel = css[i:j].strip()
        if sel.startswith('@'):
            d, k = 1, j + 1
            while d and k < n:
                d += {'{': 1, '}': -1}.get(css[k], 0)
                k += 1
            out.append((sel, css[j + 1:k - 1]))
            i = k
        else:
            k = css.find('}', j)
            if k < 0:
                break
            out.append((sel, css[j + 1:k]))
            i = k + 1
    return out


def scope(css, pref):
    res = []
    for sel, body in rules(css):
        if sel.startswith('@media'):
            inner = scope(body, pref)
            if inner:
                res.append(sel + '{' + inner + '}')
        elif not sel.startswith('@') and KEY.search(sel):
            parts = [p.strip() for p in sel.split(',') if KEY.search(p)]
            res.append(','.join(pref + ' ' + p for p in parts) + '{' + body.strip() + '}')
    return ''.join(res)


def panel(n, key, slug, name, hint, more):
    s = (ROOT / slug / 'index.html').read_text(encoding='utf-8')
    i = s.find('class="f-zmap')
    if i < 0:
        sys.exit(f'home-scheme: на странице /{slug}/ нет схемы зон (.f-zmap)')
    sec = s[s.rfind('<section', 0, i):s.find('</section>', i)]
    css = scope(''.join(re.findall(r'<style[^>]*>(.*?)</style>', s, re.S)), '#shema .hz-' + key)
    fig = re.search(r'<figure.*?</figure>', sec, re.S).group(0)
    fig = re.sub(r'<!--.*?-->', '', fig, flags=re.S)
    fig = re.sub(r'\s(data-fade|data-group="[^"]*")', '', fig)
    fig = re.sub(r'(id|aria-labelledby)="([^"]+)"', lambda m: f'{m.group(1)}="hz-{key}-{m.group(2)}"', fig)
    fig = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#hz-{key}-{m.group(1)})', fig)
    fig = re.sub(r'\n\s*\n', '\n', fig)
    ol = re.search(r'<ol class="f-zlist.*?</ol>', sec, re.S).group(0)
    items = []
    for z, body in re.findall(r'<li data-z="(\d+)"[^>]*>(.*?)</li>', ol, re.S):
        b = re.search(r'<b>(.*?)</b>', body, re.S).group(1).strip()
        sp = re.search(r'<span>(.*?)</span>', body, re.S).group(1).strip()
        sm = re.search(r'<small>(.*?)</small>', body, re.S)
        sm = f'<small>{sm.group(1).strip()}</small>' if sm else ''
        items.append(f'<li data-z="{z}" tabindex="0"><b>{b}</b><span class="hz-d">{sp}{sm}</span></li>')
    on = n == 0
    tab = (f'<button class="hz-tab{" is-on" if on else ""}" type="button" role="tab" '
           f'aria-selected="{"true" if on else "false"}" aria-controls="hz-p-{key}" id="hz-t-{key}" data-o="{key}">'
           f'<b>{name}</b><span>{len(items)} зон · {hint}</span></button>')
    pan = (f'<div class="hz-pan hz-{key}{" is-on" if on else ""}" id="hz-p-{key}" role="tabpanel" '
           f'aria-labelledby="hz-t-{key}"{"" if on else " hidden"}>\n      {fig}\n'
           f'      <div class="hz-side"><ol class="hz-zl">{"".join(items)}</ol>'
           f'<a class="hz-more" href="{slug}/">Подробнее: {more}{ARR}</a></div>\n    </div>')
    return tab, pan, css


def main():
    idx = ROOT / 'index.html'
    s = idx.read_text(encoding='utf-8')
    tabs, pans, css = zip(*(panel(n, *p) for n, p in enumerate(PAGES)))
    sec = ('<!-- home-scheme:start -->\n<section class="s" id="shema" aria-labelledby="hz-h">\n  <div class="wrap">\n'
           '    <div class="head"><div class="eyebrow" data-eyebrow>Схема объекта</div>'
           '<h2 id="hz-h" data-split>Где на объекте <em>появляются вредители</em></h2>'
           '<p class="sub" data-fade>Так выглядит схема точек контроля, которую мы составляем после бесплатного аудита. '
           'Выберите тип объекта и нажмите на зону — покажем, откуда приходят вредители и чем каждую зону '
           'контролируем.</p></div>\n'
           f'    <div class="hz-tabs" role="tablist" aria-label="Тип объекта">{"".join(tabs)}</div>\n'
           '    ' + '\n    '.join(pans) + '\n'
           '    <div class="hz-foot"><p>Гостиница, магазин или фармпроизводство? Схему под ваш объект — с зонами, '
           'точками и нормами — составим на бесплатном аудите. Смотрите также: <a href="gostinitsy/">гостиницы</a>, '
           '<a href="magaziny-i-torgovye-seti/">магазины и торговые сети</a>, '
           '<a href="farmatsevticheskie-proizvodstva/">фармацевтические производства</a>.</p>'
           '<a class="btn btn-w btn-lg" href="#zayavka"><span class="btn-t">Получить схему для своего объекта</span></a></div>\n'
           '  </div>\n</section>\n<!-- home-scheme:end -->\n\n')
    s = re.sub(r'<!-- home-scheme:start -->.*?<!-- home-scheme:end -->\n*', '', s, flags=re.S)
    anchor = '<section class="s" id="dokumenty">'
    if anchor not in s:
        sys.exit('home-scheme: на главной нет секции #dokumenty')
    s = s.replace(anchor, sec + anchor, 1)
    style = ('<style id="hz-st">' + (HERE / 'scheme.css').read_text(encoding='utf-8').strip()
             + '\n' + ''.join(css) + '</style>')
    s = re.sub(r'<style id="hz-st">.*?</style>', '', s, flags=re.S)
    s = s.replace('<!-- style:end -->', '<!-- style:end -->' + style, 1) if '<!-- style:end -->' in s \
        else s.replace('</head>', style + '</head>', 1)
    js = '<script id="hz-js">' + (HERE / 'scheme.js').read_text(encoding='utf-8').strip() + '</script>'
    s = re.sub(r'<script id="hz-js">.*?</script>\n?', '', s, flags=re.S)
    s = s.replace('</body>', js + '\n</body>', 1)
    idx.write_text(s, encoding='utf-8')
    print('home-scheme: блок «Схема объекта» на главной —', len(PAGES), 'вкладки')


if __name__ == '__main__':
    main()
