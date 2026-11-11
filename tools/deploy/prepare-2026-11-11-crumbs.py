#!/usr/bin/env python3
"""Выкладка 11.11.2026: хлебные крошки первого экрана на компьютере и планшете — вверху, над заголовком.
Запрос владельца 11.11.2026: «Хлебные крошки прилеплены на главном скрине к кнопкам снизу вплотную. Исправь это вообще,
проверь на всём сайте» → согласован вариант «крошки вверху, над заголовком»; на телефоне — внизу первого экрана или ниже
(на сайте крошки на телефоне скрыты, так и остаётся).

    python3 tools/deploy/prepare-2026-11-11-crumbs.py <файлы сайта> <папка pkg> [MANIFEST]

<файлы сайта> — все страницы сайта (index.php), как их отдаёт сайт по HTTPS перед выкладкой.
Каждая страница правится функцией tools/site/crumbs_top.apply (только стили, тексты и HTML без изменений):
  * блок hero-fold: #hero.d-hero .d-hero-copy>:is(.d-crumbs,.f-crumbs){order:0} — на всех страницах с этим блоком;
  * стили нормативной базы (до 1180 px): крошки без order:7, отступ 18 px снизу — 4 страницы раздела, акт и схема точек;
  * стили акта и схемы точек: без отступа 24 px над крошками.
Страницы, которых правка не касается (политика, согласие), в пакет не входят. sitemap.xml и поиск не меняются.
Проверки: закон владельца (tools/site/tracking_laws.check_page) — Метрика 113675622, UIS и Radist официальными
кодами на своих местах, каждая часть server/counters.html на странице ровно один раз, как на сайте;
без правки страница совпадает с прежней (заменены только строки EDITS).
"""
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import crumbs_top  # noqa: E402
import tracking_laws  # noqa: E402

NB = {'normativnaya-baza/index.php', 'normativnaya-baza/proverochnye-listy/index.php',
      'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.php',
      'normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/index.php',
      'materialy/akt-deratizatsii-i-dezinsektsii/index.php', 'materialy/skhema-tochek-pest-kontrolya/index.php'}
MD = {'materialy/akt-deratizatsii-i-dezinsektsii/index.php', 'materialy/skhema-tochek-pest-kontrolya/index.php'}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    live_dir, pkg = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    parts = tracking_laws.counter_parts()
    pages = sorted(str(p.relative_to(live_dir)) for p in live_dir.rglob('index.php'))
    files = {}
    for rel in pages:
        live = (live_dir / rel).read_text(encoding='utf-8')
        new, n = crumbs_top.apply(live)
        if not n:
            assert rel in ('privacy/index.php', 'soglasie/index.php'), rel + ': правка не легла'
            continue
        want = 1 + (rel in NB) + (rel in MD)
        assert n == want, f'{rel}: правок {n}, ожидалось {want}'
        back = new
        for old, nw in crumbs_top.EDITS:
            back = back.replace(nw, old)
        assert back == live, rel + ': страница изменилась не только правкой крошек'
        # ЗАКОН ВЛАДЕЛЬЦА (tools/site/tracking_laws.py): счётчики официальными кодами на своих местах, телефон и почта
        bad = tracking_laws.check_page(new, counters=True, parts=parts)
        assert not bad, f'{rel}: нарушения закона: {bad[:3]}'
        for k, p in parts.items():
            assert live.count(p) == new.count(p) == 1, f'{rel}: часть счётчиков {k}'
        files[rel] = new.encode('utf-8')
        print(f'{rel}: правок {n}; счётчики прежние')
    assert NB <= set(files), 'нет страниц нормативной базы, акта или схемы'
    order = sorted(files)
    lines = ''
    for rel in order:
        d = pkg / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_bytes(files[rel])
        lines += f'{sha(files[rel])}  {rel}\n'
    if len(sys.argv) == 4:
        if pathlib.Path(sys.argv[3]).read_text(encoding='utf-8') != lines:
            raise SystemExit('пакет не совпадает с MANIFEST')
        print('MANIFEST совпадает')
    else:
        (pkg.parent / 'MANIFEST.sha256').write_text(lines, encoding='utf-8')
    (pkg.parent / 'ORDER.txt').write_text('\n'.join(order), encoding='utf-8')
    (pkg.parent / 'REPLACED.txt').write_text(' '.join(order), encoding='utf-8')
    exp = ''.join(f'{sha((live_dir / rel).read_bytes())}  {rel}\n' for rel in order)
    (pkg.parent / 'EXPECTED_BEFORE.txt').write_text(exp, encoding='utf-8')
    print(f'пакет: {len(order)} страниц (все заменяются) → {pkg}')


if __name__ == '__main__':
    main()
