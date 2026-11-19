#!/usr/bin/env python3
"""Главная на телефоне (до 760 px): отрасли, цены и подвал — вариант B, метод IPM — вариант A (решение владельца 19.11.2026).

    python3 tools/home-mobile/build.py            # вставить или обновить блоки в index.html
    python3 tools/home-mobile/build.py --check    # проверить, что блоки на месте и совпадают с исходниками

Ставит в главную (только index.html в корне):
  <style id="hm-st"> — сжатый mobile.css, сразу после <style id="hz-st"> (UIS остаётся последним в <head>);
  <script id="hm-js"> — сжатый mobile.js, сразу после <script id="hz-js"> (Radist остаётся в конце <body>).
Повторный запуск заменяет блоки, а не дублирует. Схема объекта (вариант A) — в tools/home-scheme (scheme.css, scheme.js),
поведение круга IPM на телефоне — в tools/site/ipm_pin.py (круг «прилипает» — значит, без автосмены и с переходом к шагу
по нажатию).
Счётчики, телефон и почту скрипт не трогает (ЗАКОН ВЛАДЕЛЬЦА — tools/site/tracking_laws.py). Превью трёх вариантов —
preview-mobile/, журнал — tools/home-mobile/README.md.
"""
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ESBUILD = ['npx', '--yes', 'esbuild@0.24.2']


def esbuild(path, loader):
    args = ESBUILD + [str(path), '--minify', '--charset=utf8', '--log-level=warning']
    args += ['--loader:.css=css'] if loader == 'css' else ['--target=es2015']
    r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('home-mobile: esbuild: ' + r.stderr)
    return r.stdout.strip()


def blocks():
    st = '<style id="hm-st">' + esbuild(HERE / 'mobile.css', 'css') + '</style>'
    js = '<script id="hm-js">' + esbuild(HERE / 'mobile.js', 'js') + '</script>'
    return st, js


def apply(s, st, js):
    # блок — отдельной строкой сразу после строки hz-st / hz-js: повторный запуск home-scheme и этого скрипта
    # (в любом порядке) даёт тот же файл
    s = re.sub(r'<style id="hm-st">.*?</style>\n?', '', s, flags=re.S)
    s = re.sub(r'<script id="hm-js">.*?</script>\n?', '', s, flags=re.S)

    def after(s, pat, block, what):
        m = re.search(pat, s, re.S)
        if not m:
            sys.exit('home-mobile: в index.html нет ' + what + ' (сначала tools/home-scheme/build.py)')
        e = m.end() + 1 if s[m.end():m.end() + 1] == '\n' else m.end()
        return s[:e] + block + '\n' + s[e:]
    s = after(s, r'<style id="hz-st">.*?</style>', st, '<style id="hz-st">')
    s = after(s, r'<script id="hz-js">.*?</script>', js, '<script id="hz-js">')
    assert s.count('id="hm-st"') == 1 and s.count('id="hm-js"') == 1
    assert s.index('id="hm-st"') < s.index('</head>') < s.index('id="hm-js"') < s.index('</body>')
    return s


def main():
    idx = ROOT / 'index.html'
    s = idx.read_text(encoding='utf-8')
    st, js = blocks()
    new = apply(s, st, js)
    if '--check' in sys.argv:
        if new != s:
            sys.exit('home-mobile: блоки в index.html не совпадают с tools/home-mobile (запустите build.py)')
        print('home-mobile: блоки на месте')
        return
    if new != s:
        idx.write_text(new, encoding='utf-8')
    print(f'home-mobile: index.html — стили {len(st.encode()) // 1024} КБ, скрипт {len(js.encode()) // 1024} КБ')


if __name__ == '__main__':
    main()
