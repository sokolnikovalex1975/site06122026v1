#!/usr/bin/env python3
"""Контент на телефоне — в пределах экрана (замечание владельца 16.11.2026, скриншоты с iPhone).

    python3 tools/site/mob_fit.py            # правит страницы репозитория
    python3 tools/site/mob_fit.py --check    # только проверка, код 1 при нарушениях

Замечание владельца 16.11.2026: «Ошибки на главной странице на телефоне, проверь и на внутренних страницах это.
Контент должен нормально отображаться на устройствах! Исправь». На скриншотах: кнопка «Получить схему для своего
объекта» обрезана справа; «Подробнее о пест-контроле складов / по GMP» разъехались на колонки (правка flex_text.py
от 11.11.2026 была только в GitHub — на рабочий сайт не попала).

Что делает скрипт (повторный запуск ничего не меняет):
  * перед <style id="tel-plain"> ставит одну строку <style id="mob-fit"> (STYLE ниже). До 600 px: текст кнопок
    (.btn, кроме ссылок tel:) переносится на вторую строку вместо обрезки, высота кнопки растёт по тексту; длинные
    ссылки списка норм (.rk-nl), плашка «Непродовольственные» (.pest-b .lvl) и длинные слова в карточках не выходят
    за край; до 400 px слово с дефисом в заголовке карточки (span.nw, «производственно-складские») переносится по дефису
    (19.11.2026). Стиль .fxt для flex_text.py — в этой же строке (не перед </head>: там по закону владельца стоит UIS);
  * «Дератизация», раздел «Документы»: «12 раз/год», «3 контура», «7 документов» — 40 px не помещались в карточку
    на телефоне; число остаётся крупным, единица — подписью под ним (как на «Складах и логистике»).
Ссылки телефона и почты не трогает (ЗАКОН ВЛАДЕЛЬЦА). Проверка в браузере: node tools/qa/mob_fit_test.mjs.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SKIP = {'.git', 'tools', 'dist', 'server', 'node_modules', 'preview-audit', 'preview-services'}
ANCHOR = '<style id="tel-plain">'
CSS = (
    'span.fxt.fxt,span.fxt.fxt span{display:inline}'
    '.kpi .u{display:block;font-style:normal;font-size:12px;letter-spacing:.08em;text-transform:uppercase;'
    'color:var(--acc);margin:0 0 12px}'
    '@media (max-width:600px){'
    ':root .btn:not([href^="tel:"]){white-space:normal;max-width:100%;min-width:0;text-align:center;line-height:1.25}'
    ':root .btn-lg:not([href^="tel:"]){height:auto;min-height:56px;padding-top:10px;padding-bottom:10px}'
    ':root .btn-sm:not([href^="tel:"]){height:auto;min-height:44px;padding-top:8px;padding-bottom:8px}'
    ':root .btn:not([href^="tel:"]) .btn-t{white-space:normal;min-width:0;max-width:100%;flex:0 1 auto;text-align:center}'
    ':root .btn:not([href^="tel:"]) .btn-t>span{white-space:normal}'
    ':root .rk-page .rk-nl a{white-space:normal}'
    ':root .pest-b .lvl{max-width:100%;letter-spacing:.04em;-webkit-hyphens:auto;hyphens:auto;overflow-wrap:anywhere}'
    '.card,.d-card,.panel,.d-obj-b,.d-kind-b,.nb-obj-t,.f-check-l{min-width:0}'
    '.card h3,.card h4,.card p,.card li,.card b,.card span,.d-card h3,.d-card p{overflow-wrap:break-word}'
    '.kpi span,.nb-obj-t,.d-obj-b h3{-webkit-hyphens:auto;hyphens:auto}'
    '}'
    '@media (max-width:400px){.card h3 .nw,.d-card h3 .nw{white-space:normal}}'
)
STYLE = '<style id="mob-fit">' + CSS + '</style>\n'
STYLE_RE = re.compile(r'<style id="mob-fit">.*?</style>\n?', re.S)
# «12 раз/год» → число + подпись единицы (только раздел «Документы» дератизации)
KPI = [
    ('12', ' раз/год', 'раз в год'),
    ('3', ' контура', 'контура'),
    ('7', ' документов', 'документов'),
]


def fix(text):
    if STYLE_RE.search(text):  # уже есть — обновить на месте, не двигая относительно других стилей
        t = STYLE_RE.sub(lambda m: STYLE, text, count=1)
    elif ANCHOR in text:
        t = text.replace(ANCHOR, STYLE + ANCHOR, 1)
    else:
        t = text
    for num, suf, unit in KPI:
        t = re.sub(r'<b data-count="%s" data-suf="%s">%s[ \u00a0]%s</b>' % (num, re.escape(suf), num, re.escape(suf.strip())),
                   '<b data-count="%s">%s</b><i class="u">%s</i>' % (num, num, unit), t)
    return t


def pages():
    for p in sorted(ROOT.rglob('*.html')):
        if not SKIP.intersection(p.relative_to(ROOT).parts):
            yield p


def main():
    check = '--check' in sys.argv[1:]
    bad = 0
    for p in pages():
        s = p.read_text(encoding='utf-8')
        if ANCHOR not in s:
            continue
        t = fix(s)
        if t != s:
            bad += 1
            if not check:
                p.write_text(t, encoding='utf-8')
    print('mob_fit: %s страниц: %d' % ('нужно поправить' if check else 'исправлено', bad))
    return 1 if (check and bad) else 0


if __name__ == '__main__':
    sys.exit(main())
