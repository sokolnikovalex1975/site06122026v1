#!/usr/bin/env python3
"""Вход первого экрана без ожидания скриптов анимаций и счётчиков (с 11.11.2026).

    python3 tools/site/hero_in.py           # встроить скрипт на все страницы репозитория
    python3 tools/site/hero_in.py --check   # только проверить: на каждой странице с первым экраном ровно один
                                            # актуальный скрипт сразу после </section> первого экрана

Скрипт tools/site/hero_in.js (сжатый esbuild) ставится сразу после закрывающего </section> первого экрана
(<section … id="hero">) как <script id="hero-in">…</script>. Он запускает тот же вход первого экрана, что раньше
запускал app.js через GSAP, но средствами браузера (Web Animations API) — сразу при разборе страницы. app.js видит
window.pcHero и первый экран не трогает. Стили, которые снимают начальные состояния (класс hero-in), — в конце
style.css. Повторный запуск ничего не меняет: прежний <script id="hero-in"> заменяется.

Счётчики, телефон и почту шаг не трогает (ЗАКОН ВЛАДЕЛЬЦА, tools/site/tracking_laws.py).
apply(html, js) — та же правка для готовых страниц (пакеты выкладки из страниц сайта).
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / 'tools' / 'site' / 'hero_in.js'
ESBUILD = ['npx', '--yes', 'esbuild@0.24.2']
SKIP = ('preview-', 'tools/', 'dist/', 'server/', 'vendor/', 'node_modules/')

HERO_OPEN = re.compile(r'<section\b[^>]*\bid="hero"[^>]*>')
OLD = re.compile(r'\n?<script id="hero-in">.*?</script>', re.S)


def minified():
    res = subprocess.run(ESBUILD + [str(SRC), '--minify', '--target=es2015', '--charset=utf8', '--log-level=warning'],
                         cwd=ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit('esbuild: ' + res.stderr)
    js = res.stdout.strip()
    if '</script' in js.lower():
        sys.exit('hero_in.js: в сжатом коде не должно быть «</script»')
    return js


def hero_end(html):
    """Позиция сразу после </section>, закрывающего первый экран, или None (страница без первого экрана)."""
    m = HERO_OPEN.search(html)
    if not m:
        return None
    depth, pos = 1, m.end()
    for t in re.finditer(r'<(/?)section\b[^>]*>', html[pos:]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return pos + t.end()
    raise ValueError('не найден </section> первого экрана')


def apply(html, js):
    html = OLD.sub('', html)
    end = hero_end(html)
    if end is None:
        return html
    return html[:end] + '\n<script id="hero-in">' + js + '</script>' + html[end:]


def check(html, js):
    """Пустой список — порядок; иначе — что не так."""
    if hero_end(OLD.sub('', html)) is None:
        return ['скрипт входа на странице без первого экрана'] if 'id="hero-in"' in html else []
    found = re.findall(r'<script id="hero-in">(.*?)</script>', html, re.S)
    if len(found) != 1:
        return [f'скриптов входа первого экрана: {len(found)} (нужен один)']
    errs = []
    if found[0] != js:
        errs.append('скрипт входа первого экрана не совпадает с tools/site/hero_in.js')
    if apply(html, js) != html:
        errs.append('скрипт входа первого экрана стоит не сразу после </section> первого экрана')
    return errs


def pages():
    for p in sorted(ROOT.rglob('index.html')):
        rel = p.relative_to(ROOT).as_posix()
        if not rel.startswith(SKIP):
            yield p, rel


def main(argv):
    js = minified()
    bad, changed = 0, 0
    for p, rel in pages():
        s = p.read_text(encoding='utf-8')
        if '--check' in argv:
            errs = check(s, js)
            for e in errs:
                print(f'НАРУШЕНИЕ {rel}: {e}')
            bad += bool(errs)
            continue
        new = apply(s, js)
        if new != s:
            p.write_text(new, encoding='utf-8')
            changed += 1
            print('вход первого экрана:', rel)
    if '--check' in argv:
        print('OK: вход первого экрана на всех страницах' if not bad else f'страниц с ошибками: {bad}')
        return 1 if bad else 0
    print(f'страниц изменено: {changed}; сжатый скрипт — {len(js)} байт')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
