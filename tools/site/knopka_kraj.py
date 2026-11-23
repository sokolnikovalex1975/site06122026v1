#!/usr/bin/env python3
"""Кнопки: ровный край без каймы (23.11.2026): точные замены для style.css, встроенных стилей главной и версии
style.css на страницах.

Замечание владельца 23.11.2026 (фото первого экрана главной на компьютере): у левой кнопки «Заказать бесплатный аудит»
рваная окантовка, «как черновик», правая «Как мы работаем» нарисована аккуратно — сделать левую такой же по контуру.

Причины и правка — в комментарии блока в style.css («Кнопки: ровный край без каймы»): кнопка больше не держится
отдельным слоем видеокарты в покое, фиолетовая заливка наведения целиком внутри кнопки и в конце принимает её форму,
фон самой кнопки после заливки тоже фиолетовый — светлой каймы (у правой кнопки — тёмной щели у рамки) нет.
Вид в покое, размеры, цвета и анимация наведения прежние.

На сайте: style.css — блок дописан в конец (после последнего правила); главная — тот же блок (сжатый) в конце
встроенных стилей перед </style><!-- style:end -->; остальные страницы со ссылкой на style.css —
?v=20261123scan → ?v=20261123knopka (app.min.js и legal.css — прежние версии).
"""

OLD_V, NEW_V = '20261123scan', '20261123knopka'

CSS_LAST = '.lowfx .panel{background:#18181bf0}.lowfx .hdr.scrolled{background:#000000eb}.lowfx .form{background:#09090bf0}.lowfx .mbar{background:#121214f7}\n'
CSS_BLOCK = '/* ===== Кнопки: ровный край без каймы (23.11.2026) =====\n   Замечание владельца (фото первого экрана главной на компьютере): у левой кнопки «Заказать бесплатный аудит» рваная\n   окантовка, «как черновик», а правая «Как мы работаем» нарисована аккуратно.\n   Причины: 1) кнопка постоянно держалась отдельным слоем видеокарты (will-change:transform) — Safari и Retina-экраны\n   рисуют скругление такого слоя с зазубринами; 2) под фиолетовой заливкой наведения оставался белый фон кнопки, и на\n   скруглениях он проступал светлой неровной каймой вокруг фиолетовой кнопки (у правой — тёмная щель между рамкой и\n   заливкой); 3) заливка была шире кнопки на 2 px и держалась только обрезкой по краю.\n   Теперь: отдельный слой — только на время движения (магнит); заливка целиком внутри кнопки и в конце наведения\n   принимает её форму; когда заливка дошла до верха, фон самой кнопки тоже становится фиолетовым — каймы нет.\n   Вид, размеры, цвета и анимация наведения прежние. */\n.btn{will-change:auto}\n.btn::before{left:0;right:0;bottom:0;height:100%}\n.btn:hover::before,.btn:focus-visible::before,.btn.is-loading::before,.btn:active::before{border-radius:inherit}\n.btn-w:hover,.btn-w:focus-visible,.btn-o:hover,.btn-o:focus-visible{animation:btn-fill 0s linear .55s forwards}\n.btn-w.is-loading,.btn-o.is-loading{background-color:var(--acc3)}\n@keyframes btn-fill{to{background-color:var(--acc3)}}\n@media (hover:none){ .btn-w:active,.btn-o:active{background-color:var(--acc3)} }\n@media (prefers-reduced-motion:reduce){ .btn-w:hover,.btn-w:focus-visible,.btn-o:hover,.btn-o:focus-visible{background-color:var(--acc3)} }\n'
HOME_END = '</style><!-- style:end -->'
HOME_BLOCK = '.btn{will-change:auto}.btn:before{left:0;right:0;bottom:0;height:100%}.btn:hover:before,.btn:focus-visible:before,.btn.is-loading:before,.btn:active:before{border-radius:inherit}.btn-w:hover,.btn-w:focus-visible,.btn-o:hover,.btn-o:focus-visible{animation:btn-fill 0s linear .55s forwards}.btn-w.is-loading,.btn-o.is-loading{background-color:var(--acc3)}@keyframes btn-fill{to{background-color:var(--acc3)}}@media (hover:none){.btn-w:active,.btn-o:active{background-color:var(--acc3)}}@media (prefers-reduced-motion:reduce){.btn-w:hover,.btn-w:focus-visible,.btn-o:hover,.btn-o:focus-visible{background-color:var(--acc3)}}'

CSS_PAIRS = [(CSS_LAST, CSS_LAST + '\n' + CSS_BLOCK)]
HOME_CSS_PAIRS = [(HOME_END, HOME_BLOCK + HOME_END)]
VERSION_PAIRS = [('style.css?v=' + OLD_V, 'style.css?v=' + NEW_V)]
MARK = '.btn{will-change:auto}'


def _edits(s, pairs, what):
    out = []
    for a, b in pairs:
        n = s.count(a)
        assert n == 1, '%s: «%s» найдено %d раз' % (what, a[:70], n)
        assert MARK not in s, '%s: правка уже есть' % what
        out.append([a, b, 1])
    return out


def style_edits(css):
    return _edits(css, CSS_PAIRS, 'style.css')


def page_edits(html, rel='страница'):
    if 'style.css?v=' not in html:
        assert rel in ('index.php', 'index.html'), rel + ': нет ссылки на style.css'
        return _edits(html, HOME_CSS_PAIRS, rel)
    assert '.btn:before{content' not in html, rel + ': свои стили кнопок'
    return _edits(html, VERSION_PAIRS, rel)


def apply(s, edits):
    for a, b, c in edits:
        assert s.count(a) == c, a[:70]
        s = s.replace(a, b)
    return s


def revert(s, edits):
    for a, b, c in reversed(edits):
        assert s.count(b) == c, b[:70]
        s = s.replace(b, a)
    return s
