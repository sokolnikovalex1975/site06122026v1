#!/usr/bin/env python3
"""Точечная правка страниц, снятых с сайта: одна строка <style id="hero-fold"> перед </head>
(то же правило, что в сборке, — tools/site/hero_fold.py: кнопки первого экрана видны целиком на любом экране).

    python3 tools/deploy/patch-2026-11-10-fold.py <папка со страницами с сайта> <папка pkg> <список страниц>

Список — пути страниц без index.php (. — главная, deratizatsiya, materialy/zhurnal-pest-kontrolya ...), по одному в строке.
Проверяет: добавлена ровно одна строка, без неё файл совпадает с файлом сайта байт в байт, PHP-вставок нет,
счётчики (Метрика 113675622, UIS/CoMagic, Radist) на месте в том же количестве.
"""
import difflib
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('hero_fold', HERE.parent / 'site' / 'hero_fold.py')
mc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc)
COUNTERS = ['113675622', 'mc.yandex.ru/metrika/tag.js',
            'app.uiscom.ru/static/cs.min.js?k=ICWycQx6m3NSBe3WlCeDAdAKMTmNhMHC', 'track.radist.me/tracker.min.js']


def main():
    src, dst, lst = map(pathlib.Path, sys.argv[1:4])
    bad = 0
    for p in lst.read_text(encoding='utf-8').split():
        b = (src / p / 'index.php').read_bytes()
        s = b.decode('utf-8')
        if 'id="hero-fold"' in s:
            print('правило уже есть на сайте:', p); bad += 1; continue
        new, ok = mc.apply(s)
        if not ok:
            print('на странице нет первого экрана #hero:', p); bad += 1; continue
        d = [l for l in difflib.unified_diff(s.splitlines(True), new.splitlines(True), n=0)
             if l[:1] in '+-' and not l.startswith(('+++', '---'))]
        assert d == ['+' + mc.RULE + '\n'], (p, d[:3])
        assert new.replace(mc.RULE + '\n', '', 1) == s
        assert s.count('<?') == 0 and new.count('<?') == 0, p
        for c in COUNTERS:
            assert s.count(c) == new.count(c) >= 1, (p, c)
        o = dst / p / 'index.php'
        o.parent.mkdir(parents=True, exist_ok=True)
        o.write_bytes(new.encode('utf-8'))
        print(f'ok {p}: +{len(new.encode()) - len(b)} байт, счётчики на месте')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
