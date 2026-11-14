#!/usr/bin/env python3
"""Блок «Что видит камера в коробе» на странице вентиляции: SVG-схема → три реалистичных кадра с анимацией.

    python3 tools/ventilyatsiya/kamera/apply.py <готовая страница> <куда записать> [--preview]

Правит уже собранную страницу (из репозитория или index.php с сайта): заменяет только
  1) подпись над кадром «Схема · …» → «Иллюстрация · …»;
  2) содержимое кадра (SVG) — три фото, холст WebGL и кнопка паузы (art.html);
  3) обозначения под подписью — «Что видно на кадре» с отметкой убранного (legend.html);
  4) стили схемы в <style> страницы — на block.css;
  5) скрипт схемы в скрипте страницы — на block.js.
Подписи к состояниям, кнопки, остальная страница, счётчики, телефон и почта не меняются.
--preview — копия для GitHub-превью: в title приписка «Превью».
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent

OLD_CSS = [  # правила SVG-схемы из tools/ventilyatsiya/extra.css (в собранной странице — одной строкой)
    '.v-duct-art{grid-area:art;border-radius:calc(var(--r) - 4px);overflow:hidden;background:#0b0d12;border:1px solid var(--line2);aspect-ratio:720/400}',
    '.v-duct-art svg{display:block;width:100%;height:100%}',
    '.v-duct figcaption [data-cap]{display:block}',
    '.v-duct figcaption [data-cap][hidden]{display:none}',
    '.v-legend i{width:12px;height:12px;border-radius:50%;flex:0 0 auto}',
    '.v-duct .v-dust,.v-duct .v-grease,.v-duct .v-germs,.v-duct .v-ok,.v-duct .v-shine{transition:opacity .7s ease}',
    '.v-duct .v-ok,.v-duct .v-shine{opacity:0}',
    '.v-duct[data-state="clean"] .v-dust,.v-duct[data-state="clean"] .v-grease,.v-duct[data-state="dez"] .v-dust,.v-duct[data-state="dez"] .v-grease,.v-duct[data-state="dez"] .v-germs{opacity:0}',
    '.v-duct[data-state="clean"] .v-shine{opacity:.6}',
    '.v-duct[data-state="dez"] .v-shine,.v-duct[data-state="dez"] .v-ok{opacity:1}',
]
OLD_CSS_RM = '@media (prefers-reduced-motion:reduce){.v-duct .v-dust,.v-duct .v-grease,.v-duct .v-germs,.v-duct .v-ok,.v-duct .v-shine{transition:none}}'
JS_START = '  /* схема воздуховода: до работ → после очистки → после дезинфекции */\n'
JS_END = "  var lz=document.querySelectorAll('.f-lazy');"


def mini_css(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    return re.sub(r'\s*\n\s*', '', s).strip()


def one(pat, rep, s, flags=re.S):
    out, n = re.subn(pat, lambda m: rep, s, count=1, flags=flags)
    assert n == 1, 'не найдено: ' + pat[:80]
    return out


def apply(s):
    fig = re.search(r'<figure class="v-duct" id="vduct".*?</figure>', s, re.S)
    assert fig, 'нет блока #vduct'
    f = fig.group(0)
    f, n = re.subn(r'<span class="v-duct-k">Схема · (что видит камера в[ \u00a0]коробе)</span>',
                   r'<span class="v-duct-k">Иллюстрация · \1</span>', f, count=1)
    assert n == 1, 'нет подписи «Схема · что видит камера в коробе»'
    f = one(r'      <div class="v-duct-art">\s*<svg.*?</svg>\s*</div>\n', (HERE / 'art.html').read_text(encoding='utf-8'), f)
    f = one(r'      <ul class="v-legend".*?</ul>\n', (HERE / 'legend.html').read_text(encoding='utf-8'), f)
    s = s[:fig.start()] + f + s[fig.end():]
    # стили
    m = re.search(r'<style>(.*?)</style>', s, re.S)
    css = m.group(1)
    first = css.index(OLD_CSS[0])
    for rule in OLD_CSS:
        assert css.count(rule) == 1, 'стиль не найден или повторяется: ' + rule[:60]
        css = css.replace(rule, '\x00' if rule == OLD_CSS[0] else '')
    assert css.count(OLD_CSS_RM) == 1, 'нет правила reduced-motion схемы'
    css = css.replace(OLD_CSS_RM, '')
    css = css.replace('\x00', mini_css((HERE / 'block.css').read_text(encoding='utf-8')))
    s = s[:m.start(1)] + css + s[m.end(1):]
    assert first > 0
    # скрипт
    a = s.index(JS_START)
    b = s.index(JS_END, a)
    s = s[:a] + (HERE / 'block.js').read_text(encoding='utf-8') + s[b:]
    for left in ('v-shine', 'v-germs', 'vdF', 'Схема · что видит'):
        assert left not in s, 'осталось от схемы: ' + left
    return s


def main():
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    s = apply(src.read_text(encoding='utf-8'))
    if '--preview' in sys.argv:
        s = one(r'<title>', '<title>Превью «Кадры камеры» · ', s)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(s, encoding='utf-8')
    print('ok', dst, len(s), 'байт')


if __name__ == '__main__':
    main()
