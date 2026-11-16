#!/usr/bin/env python3
"""Превью мобильной главной: три варианта — папки preview-mobile/a, b, c (15.11.2026).

    python3 preview-mobile/build_preview.py

Собирает три страницы заново из актуальной главной (index.html в корне репозитория) и правок из preview-mobile/proto/.
Корневые файлы не меняются, в пакет для Timeweb (tools/site/build_prod.py) папка не входит. Счётчиков в превью нет,
как и на всём GitHub Pages: Метрика 113675622, UIS и Radist ставятся только в версию для Timeweb.

Все правки — только для экранов до 760 px (телефон). На компьютере превью выглядит как главная.

  A «Точечные правки»        — common + a: план схемы и круг IPM «прилипают» к верху, нажатие показывает результат;
  B «Компактная мобильная»   — common + b: длинные списки карточек — ленты со свайпом и счётчиком, карточки короче;
  C «Короткая главная»       — common + b + c: как B, плюс пять второстепенных блоков свёрнуты в «Подробнее о работе».

common — общее для всех: отступы 80 → 56 px, 4 типа объекта в схеме сеткой 2×2, в вопросах первые 5, подвал-аккордеон.
Стили вариантов встраиваются в <head> (страница сразу собирается в нужном виде), скрипты подключаются после того,
как главная настроила свои анимации (иначе нечего перенастраивать).
"""
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
PROTO = HERE / 'proto'
VER = '20261115m'

VARIANTS = {
    'a': ('A', 'точечные правки', ['common', 'a']),
    'b': ('B', 'компактная мобильная', ['common', 'b']),
    'c': ('C', 'короткая главная', ['common', 'b', 'c']),
}


def once(s, old, new, what):
    n = s.count(old)
    assert n == 1, f'{what}: ожидалось 1 совпадение, найдено {n}'
    return s.replace(old, new)


def once_re(s, pat, new, what, flags=0):
    out, n = re.subn(pat, new, s, flags=flags)
    assert n == 1, f'{what}: ожидалось 1 совпадение, найдено {n}'
    return out


# ---------------------------------------------------------------- ссылки на общие файлы: через ../../
SKIP_URL = ('#', 'http:', 'https:', '//', '/', 'data:', 'mailto:', 'tel:', 'javascript:', 'about:', 'blob:', '?')
UP = '../../'


def up(u):
    u = u.strip()
    if not u or u.startswith(SKIP_URL):
        return u
    return UP + (u[2:] if u.startswith('./') else u)


def relink(html):
    parts = re.split(r'(<script\b[^>]*>.*?</script>)', html, flags=re.S)
    for i in range(0, len(parts), 2):  # всё, кроме скриптов
        p = parts[i]
        p = re.sub(r'(?<![\w-])(src|href|poster|data-src)="([^"]*)"', lambda m: f'{m[1]}="{up(m[2])}"', p)
        p = re.sub(r'(?<![\w-])(srcset|imagesrcset)="([^"]*)"',
                   lambda m: m[1] + '="' + ', '.join(' '.join([up(x.split()[0])] + x.split()[1:])
                                                    for x in m[2].split(',') if x.strip()) + '"', p)
        p = re.sub(r'url\((["\']?)([^)"\']+)\1\)', lambda m: f'url({m[1]}{up(m[2])}{m[1]})', p)
        parts[i] = p
    return ''.join(parts)


LOADER = """<script id="mc-proto">/* Превью мобильной главной: скрипты варианта подключаются после настройки анимаций главной */
(function (r, l) {
  if (!matchMedia('(max-width:760px)').matches) return;
  var t0 = Date.now();
  var ready = function () { var S = window.ScrollTrigger; return !!S && S.getAll().some(function (s) { return s.trigger && s.trigger.id === 'cycle'; }); };
  var go = function () { l.forEach(function (s) { var e = document.createElement('script'); e.src = r + s; e.async = false; document.body.appendChild(e); }); };
  var wait = function () { if (ready() || Date.now() - t0 > 10000) setTimeout(go, 400); else setTimeout(wait, 150); };
  if (document.readyState === 'complete') wait(); else addEventListener('load', wait);
})('../proto/', [%s]);
</script>
"""


def build(key):
    letter, name, files = VARIANTS[key]
    s = (ROOT / 'index.html').read_text(encoding='utf-8')
    assert 'mc.yandex' not in s and 'uiscom' not in s, 'в версии для GitHub Pages не должно быть счётчиков'
    s = relink(s)
    s = once_re(s, r"\}\)\('', \['vendor/gsap\.min\.js', 'vendor/ScrollTrigger\.min\.js', 'vendor/lenis\.min\.js', "
                   r"'app\.min\.js\?v=([0-9a-z]+)'\]\);",
                r"})('../../', ['vendor/gsap.min.js', 'vendor/ScrollTrigger.min.js', 'vendor/lenis.min.js', 'app.min.js?v=\1']);",
                'загрузчик скриптов')
    s = once_re(s, r'\}\)\("\./","(\d+)"\);</script>', r'})("../../","\1");</script>', 'поиск по сайту')
    s = once_re(s, r'<title>', f'<title>Превью {letter} (телефон) — ', 'заголовок вкладки')
    s = once_re(s, r'<span class="badge" data-h><span class="dot"></span>[^<]*</span>',
                f'<span class="badge" data-h><span class="dot"></span>Превью · вариант {letter}</span>', 'плашка первого экрана')
    css = ''.join(f'<style id="mc-{f}">' + (PROTO / f'{f}.css').read_text(encoding='utf-8').strip() + '</style>' for f in files)
    s = once(s, '</head>', css + '\n</head>', 'стили варианта')
    s = once(s, '</body>', LOADER % ', '.join(f"'{f}.js?v={VER}'" for f in files) + '</body>', 'скрипты варианта')
    # проверка: не осталось ссылок на общие файлы без ../../
    left = [u for u in re.findall(r'(?<![\w-])(?:src|href)="([^"]*)"', re.sub(r'<script\b[^>]*>.*?</script>', '', s, flags=re.S))
            if u and not u.startswith(SKIP_URL + (UP,))]
    assert not left, 'ссылки без ../../: ' + ', '.join(left[:10])
    out = HERE / key
    out.mkdir(exist_ok=True)
    (out / 'index.html').write_text(s, encoding='utf-8')
    print(f'{key}/index.html: вариант {letter} «{name}», {len(s.encode()) // 1024} КБ, правки: {", ".join(files)}')


if __name__ == '__main__':
    for k in VARIANTS:
        build(k)
