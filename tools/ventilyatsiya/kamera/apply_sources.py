#!/usr/bin/env python3
"""Блок «Что видит камера в коробе» — в исходники страницы вентиляции (разово, после решения владельца 17.11.2026).

    python3 tools/ventilyatsiya/kamera/apply_sources.py

Переносит в исходники то же, что apply.py делает с готовой страницей:
  main.html — подпись «Иллюстрация · …», содержимое кадра (art.html), «Что видно на кадре» (legend.html, без
              неразрывных пробелов: их ставит typo() при сборке, как во всём main.html);
  extra.css — стили блока (block.css) на месте стилей SVG-схемы, правило reduced-motion схемы убрано;
  page.js   — скрипт блока (block.js) на месте скрипта схемы.
Повторный запуск ничего не меняет (проверяет, что блок уже перенесён).
"""
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent
OLD_LABEL = '<span class="v-duct-k">Схема · что видит камера в коробе</span>'
NEW_LABEL = '<span class="v-duct-k">Иллюстрация · что видит камера в коробе</span>'
OLD_CSS = [
    '.v-duct-art svg{display:block;width:100%;height:100%}\n',
    '.v-duct figcaption [data-cap]{display:block}\n',
    '.v-duct figcaption [data-cap][hidden]{display:none}\n',
    '.v-legend i{width:12px;height:12px;border-radius:50%;flex:0 0 auto}\n',
    '.v-duct .v-dust,.v-duct .v-grease,.v-duct .v-germs,.v-duct .v-ok,.v-duct .v-shine{transition:opacity .7s ease}\n',
    '.v-duct .v-ok,.v-duct .v-shine{opacity:0}\n',
    '.v-duct[data-state="clean"] .v-dust,.v-duct[data-state="clean"] .v-grease,.v-duct[data-state="dez"] .v-dust,'
    '.v-duct[data-state="dez"] .v-grease,.v-duct[data-state="dez"] .v-germs{opacity:0}\n',
    '.v-duct[data-state="clean"] .v-shine{opacity:.6}\n',
    '.v-duct[data-state="dez"] .v-shine,.v-duct[data-state="dez"] .v-ok{opacity:1}\n',
    '@media (prefers-reduced-motion:reduce){\n'
    '.v-duct .v-dust,.v-duct .v-grease,.v-duct .v-germs,.v-duct .v-ok,.v-duct .v-shine{transition:none}\n}\n',
]
OLD_ART_CSS = ('.v-duct-art{grid-area:art;border-radius:calc(var(--r) - 4px);overflow:hidden;background:#0b0d12;'
               'border:1px solid var(--line2);aspect-ratio:720/400}\n')
JS_START = '  /* схема воздуховода: до работ → после очистки → после дезинфекции */\n'
JS_END = "  var lz=document.querySelectorAll('.f-lazy');"


def one(s, old, new):
    assert s.count(old) == 1, 'не найдено или повторяется: ' + old[:70]
    return s.replace(old, new)


def main():
    art = (HERE / 'art.html').read_text(encoding='utf-8')
    legend = (HERE / 'legend.html').read_text(encoding='utf-8').replace('\u00a0', ' ')
    block_css = (HERE / 'block.css').read_text(encoding='utf-8')
    block_js = (HERE / 'block.js').read_text(encoding='utf-8')

    p = SRC / 'main.html'
    s = p.read_text(encoding='utf-8')
    if NEW_LABEL in s:
        assert art in s and legend in s and OLD_LABEL not in s and '<svg viewBox="0 0 720 400"' not in s
        print('main.html: уже перенесено')
    else:
        s = one(s, OLD_LABEL, NEW_LABEL)
        m = re.search(r'      <div class="v-duct-art">\n        <svg viewBox="0 0 720 400".*?</svg>\n      </div>\n', s, re.S)
        assert m, 'нет SVG-схемы в main.html'
        s = s[:m.start()] + art + s[m.end():]
        m = re.search(r'      <ul class="v-legend" aria-label="Обозначения на схеме">.*?</ul>\n', s, re.S)
        assert m, 'нет обозначений схемы в main.html'
        s = s[:m.start()] + legend + s[m.end():]
        p.write_text(s, encoding='utf-8')
        print('main.html: подпись, кадр и «Что видно на кадре»')

    p = SRC / 'extra.css'
    s = p.read_text(encoding='utf-8')
    if '.vk-f{' in s:
        assert OLD_ART_CSS not in s
        print('extra.css: уже перенесено')
    else:
        s = one(s, OLD_ART_CSS, block_css.rstrip('\n') + '\n')
        for rule in OLD_CSS:
            s = one(s, rule, '')
        p.write_text(s, encoding='utf-8')
        print('extra.css: стили блока вместо стилей схемы')

    p = SRC / 'page.js'
    s = p.read_text(encoding='utf-8')
    if block_js in s:
        assert JS_START not in s
        print('page.js: уже перенесено')
    else:
        a = s.index(JS_START)
        b = s.index(JS_END, a)
        assert s.count(JS_START) == 1
        s = s[:a] + block_js + s[b:]
        p.write_text(s, encoding='utf-8')
        print('page.js: скрипт блока вместо скрипта схемы')

    for f in ('main.html', 'extra.css', 'page.js'):
        t = (SRC / f).read_text(encoding='utf-8')
        for left in ('v-shine', 'v-germs', 'vdF', 'Схема · что видит', 'Обозначения на схеме'):
            assert left not in t, f + ': осталось от схемы: ' + left


if __name__ == '__main__':
    main()
