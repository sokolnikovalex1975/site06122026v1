#!/usr/bin/env python3
"""Выкладка 11.11.2026: «Пест-контроль для бизнеса» и «Все услуги» в меню «Услуги» + блок «Все услуги» перед заявкой.

    python3 tools/site/build_prod.py
    python3 tools/deploy/prepare-2026-11-11-vu.py <папка с файлами сайта> <папка пакета> [MANIFEST]

<папка с файлами сайта> — страницы, как их отдаёт сайт по HTTPS перед выкладкой (`<путь>/index.php`).
Пакет собирается из текущих файлов сайта: к каждой странице применяются те же функции, что в сборке GitHub —
tools/menu/apply_menu.apply_page (шапка, мобильное меню, колонки подвала) и tools/site/services_block.apply (блок и его
стили перед <style id="m-crumbs"> или перед кодом UIS — не вплотную к </head>). Проверки на каждой странице:
  * меню шапки, мобильное меню, колонки подвала, блок поиска и новый блок со стилями — байт в байт как в сборке для
    Timeweb (dist/timeweb = GitHub main); прочие отличия сайта от main (чужие невыложенные правки) не переносятся;
  * счётчики (Метрика 113675622, UIS, Radist) — те же байты, что на сайте, и проходят закон владельца (tracking_laws.check_page);
  * вне шапки, мобильного меню, подвала и нового блока со стилями страница не изменилась.
Страницы, которых нет на сайте (защита от проникновения грызунов — только GitHub), в пакет не входят.
"""
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / 'dist' / 'timeweb'
sys.path[:0] = [str(ROOT / 'tools' / 'menu'), str(ROOT / 'tools' / 'site')]
import apply_menu  # noqa: E402
import services_block  # noqa: E402
import tracking_laws  # noqa: E402

COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter -->.*?<!-- /Yandex\.Metrika counter -->|<!-- UIS -->.*?<!-- UIS -->|'
                      r'<!-- Radist -->.*?<!-- /Radist -->', re.S)
BLOCKS = [re.compile(r'<nav class="nav" aria-label="Основное меню">.*?</nav>', re.S),
          re.compile(r'<nav class="mmenu".*?</nav>', re.S), re.compile(r'<footer\b.*?</footer>', re.S),
          re.compile(r'<section class="s s-vu" id="vse-uslugi".*?</section>\n', re.S),
          re.compile(r'<style id="vu-st">.*?</style>', re.S), re.compile(r'<style id="srch-st">.*?</style>', re.S)]


def search_in_place(s, root):
    """Блок поиска в <head> обновляется на своём месте (apply_menu.search_ui переставил бы его к </head> — на сайте
    там код UIS, ЗАКОН ВЛАДЕЛЬЦА: между UIS и </head> ничего не ставим)."""
    block = apply_menu.SRCH_CSS + apply_menu.SRCH_JS.replace('"ROOT"', '"' + (root or './') + '"') + '\n'
    s, n = apply_menu.SRCH_HEAD_RE.subn(lambda m: block, s, count=1)
    assert n == 1 and 'class="srch-btn"' in s, 'нет блока поиска'
    return s


apply_menu.search_ui = search_in_place


FT_COLS = re.compile(r'<div><h4>Услуги</h4>.*?(?=\n\s*<div><h4>Контакты</h4>)', re.S)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def outside(s):
    for rx in BLOCKS:
        s = rx.sub('', s)
    return s


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    live_dir, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    legal = {rel for rel, _, _ in apply_menu.LEGAL}
    files = []
    for rel, root, cur in apply_menu.PAGES + apply_menu.LEGAL:
        p = rel.replace('index.html', 'index.php')
        lf = live_dir / p
        if not lf.exists():
            print('нет на сайте — пропуск:', p)
            continue
        old = lf.read_text(encoding='utf-8')
        new = apply_menu.apply_page(old, root, cur)
        if rel not in legal:
            new = services_block.apply(new, root, cur)
        built = (DIST / p).read_text(encoding='utf-8')
        # меняемые части — как в сборке GitHub (остальные отличия сайта от main — чужие невыложенные правки, их не трогаем)
        for rx in BLOCKS:
            a, b = rx.findall(new), rx.findall(built)
            if rx.pattern.startswith('<footer'):  # в подвале меняются только колонки «Услуги/Отрасли/Материалы»
                a, b = [FT_COLS.search(x).group(0) for x in a], [FT_COLS.search(x).group(0) for x in b]
            assert a == b, f'{p}: блок {rx.pattern[:30]} не совпадает со сборкой GitHub'
        assert outside(old) == outside(new), p + ': изменилось что-то вне меню, подвала и блока'
        assert COUNTERS.findall(old) == COUNTERS.findall(new), p + ': счётчики изменились'
        errs = tracking_laws.check_page(new, counters=rel not in legal)
        assert not errs, f'{p}: закон владельца — {errs}'
        if new == old:
            continue
        d = out / p
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_text(new, encoding='utf-8')
        files.append(p)
    lines = ''.join(f'{sha((out / f).read_bytes())}  {f}\n' for f in sorted(files))
    if len(sys.argv) == 4:
        if pathlib.Path(sys.argv[3]).read_text(encoding='utf-8') != lines:
            raise SystemExit('пакет не совпадает с MANIFEST')
        print('MANIFEST совпадает')
    else:
        (out.parent / 'MANIFEST.sha256').write_text(lines, encoding='utf-8')
    exp = ''.join(f'{sha((live_dir / f).read_bytes())}  {f}\n' for f in sorted(files))
    (out.parent / 'EXPECTED_BEFORE.txt').write_text(exp, encoding='utf-8')
    print(f'страниц: {len(files)}; совпадают со сборкой GitHub; счётчики прежние и по закону')


if __name__ == '__main__':
    main()
