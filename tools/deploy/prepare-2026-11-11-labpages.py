#!/usr/bin/env python3
"""Выкладка 11.11.2026: 7 страниц направлений «Лабораторных исследований» и 3 материала (решение владельца 11.11.2026:
«Исправь все найденные тобой ошибки и выкладывай на timeweb»).

    python3 tools/site/build_prod.py
    python3 tools/deploy/prepare-2026-11-11-labpages.py <файлы сайта> <папка pkg> [MANIFEST]

<файлы сайта> — laboratornye-issledovaniya/index.php, materialy/index.php, sitemap.xml и search-index.json, как их отдаёт
сайт по HTTPS перед выкладкой.

Новые файлы: 10 страниц index.php из сборки (dist/timeweb) и 50 картинок (первый экран и og:image).
Заменяются:
  * laboratornye-issledovaniya/index.php — из сборки: на сайте = сборка 10.11.2026, все отличия — правки 11.11.2026
    (плитки-ссылки, «Подробно о направлениях», «Подробнее» в прайсе, блок «Материалы», window.LBP в расчёте);
  * materialy/index.php — файл с сайта + отличия сборки, кроме перестановки <style id="m-crumbs"> внутри <head>
    (её прежние выкладки оставили как на сайте): описание, ItemList 8–10, карточки «Материал 09–11»;
  * search-index.json — из сборки (на сайте индекс от 10.11.2026; в сборке он же + новые страницы и текущие тексты главной
    и вентиляции, уже выложенные 11.11.2026);
  * sitemap.xml — файл с сайта + 10 новых адресов, lastmod 2026-11-11 у хаба и «Материалов».
Проверки: блок счётчиков (Метрика 113675622, UIS/CoMagic, Radist) на каждой странице ровно один, байт в байт как на
хабе сайта и как в server/counters.html; на заменяемых страницах счётчики и ключи (113675622, comagic, uiscom, radist)
как на сайте; в новых страницах нет noindex.
"""
import difflib
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / 'dist' / 'timeweb'
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
LAB = 'laboratornye-issledovaniya/'
SUBS = ['analiz-smyvov', 'izmerenie-mikroklimata', 'zamer-osveshchennosti', 'analiz-vozdukha-rabochey-zony',
        'analiz-pishchevykh-produktov', 'analiz-vody', 'kontrol-sterilizatorov']
ARTS = ['kak-berut-smyvy', 'zamer-osveshchennosti-i-mikroklimata', 'kontrol-raboty-sterilizatorov']
NEW_PAGES = [f'{LAB}{s}/index.php' for s in SUBS] + [f'materialy/{a}/index.php' for a in ARTS]
IMG = re.compile(r'(lab-(smyvy|mikroklimat|osveshchennost|vrz|pishcha|voda|sterilizatory)|mat-(smyvy|zamery|sterilizatory))'
                 r'-(hero|hero-1440|hero-mob|hero-mob-760)\.webp$|'
                 r'(lab-(smyvy|mikroklimat|osveshchennost|vrz|pishcha|voda|sterilizatory)|mat-(smyvy|zamery|sterilizatory))-og\.jpg$')
HUB, MAT = LAB + 'index.php', 'materialy/index.php'
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
M_CRUMBS = 'm-crumbs'
KEYS = (b'113675622', b'comagic', b'uiscom', b'radist')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def toks(s):
    return re.split(r'(?<=[>};])', s)


def merge_except(live, built, skip):
    """файл с сайта + все отличия сборки, кроме тех, где встречается skip"""
    ta, tb = toks(live), toks(built)
    out, last, n, skipped = [], 0, 0, 0
    for t, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        if t == 'equal':
            continue
        x, y = ''.join(ta[i1:i2]), ''.join(tb[j1:j2])
        if skip in x + y:
            skipped += 1
            continue
        out.append(''.join(ta[last:i1]) + y)
        last, n = i2, n + 1
    out.append(''.join(ta[last:]))
    return ''.join(out), n, skipped


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    live_dir, pkg = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    cblock = (ROOT / 'server' / 'counters.html').read_text(encoding='utf-8')
    live_hub = (live_dir / HUB).read_text(encoding='utf-8')
    ref = COUNTERS.findall(live_hub)
    assert len(ref) == 1 and ref[0] in cblock, 'на хабе сайта блок счётчиков не как server/counters.html'
    ref = ref[0]
    files = {}
    images = sorted(str(p.relative_to(DIST)) for p in (DIST / 'img').iterdir() if IMG.search(p.name))
    assert len(images) == 50, f'картинок {len(images)}, ожидалось 50'
    for f in images:
        files[f] = (DIST / f).read_bytes()
    for rel in NEW_PAGES:
        s = (DIST / rel).read_text(encoding='utf-8')
        c = COUNTERS.findall(s)
        assert len(c) == 1 and c[0] == ref, rel + ': блок счётчиков не как на сайте'
        assert 'noindex' not in s, rel + ': остался noindex'
        files[rel] = s.encode('utf-8')
        print(f'{rel}: новая, {len(files[rel]) // 1024} КБ, счётчики как на сайте')
    # хаб — из сборки
    hub = (DIST / HUB).read_text(encoding='utf-8')
    # «Материалы» — файл с сайта + правки сборки без перестановки m-crumbs
    live_mat = (live_dir / MAT).read_text(encoding='utf-8')
    mat, n, skipped = merge_except(live_mat, (DIST / MAT).read_text(encoding='utf-8'), M_CRUMBS)
    assert n == 5 and skipped == 2, f'materialy: перенесено {n}, пропущено {skipped}'
    for rel, live, new in ((HUB, live_hub, hub), (MAT, live_mat, mat)):
        assert COUNTERS.findall(new) == COUNTERS.findall(live) == [ref], rel + ': блок счётчиков изменён'
        lb, pb = live.encode('utf-8'), new.encode('utf-8')
        for k in KEYS:
            assert lb.count(k) == pb.count(k), f'{rel}: {k!r}: на сайте {lb.count(k)}, в пакете {pb.count(k)}'
        assert 'noindex' not in new
        files[rel] = pb
        print(f'{rel}: заменяется, счётчики прежние')
    for s in SUBS:
        assert f'href="{s}/"' in hub, f'на хабе нет ссылки на {s}/'
    for a in ARTS:
        assert f'href="./{a}/"' in mat, f'в «Материалах» нет ссылки на {a}/'
    files['search-index.json'] = (DIST / 'search-index.json').read_bytes()
    # sitemap: с сайта + новые адреса + lastmod
    sm = (live_dir / 'sitemap.xml').read_text(encoding='utf-8')
    for u in [f'{LAB}{s}/' for s in SUBS] + [f'materialy/{a}/' for a in ARTS]:
        assert SITE + u not in sm, u
    add = ''.join(f'  <url>\n    <loc>{SITE}{LAB}{s}/</loc>\n    <lastmod>2026-11-11</lastmod>\n    <priority>0.8</priority>\n  </url>\n'
                  for s in SUBS)
    add += ''.join(f'  <url>\n    <loc>{SITE}materialy/{a}/</loc>\n    <lastmod>2026-11-11</lastmod>\n    <priority>0.7</priority>\n  </url>\n'
                   for a in ARTS)
    n_before = sm.count('<url>')
    assert sm.count('</urlset>') == 1
    sm = sm.replace('</urlset>', add + '</urlset>')
    for rel in (LAB, 'materialy/'):
        pat = re.compile(r'(<loc>' + re.escape(SITE + rel) + r'</loc>\s*<lastmod>)([0-9-]+)(</lastmod>)')
        assert len(pat.findall(sm)) == 1, rel
        sm = pat.sub(r'\g<1>2026-11-11\g<3>', sm)
    assert sm.count('<url>') == n_before + 10, sm.count('<url>')
    files['sitemap.xml'] = sm.encode('utf-8')
    # порядок: картинки → новые страницы → хаб и «Материалы» со ссылками на них → поиск → sitemap
    order = images + NEW_PAGES + [HUB, MAT, 'search-index.json', 'sitemap.xml']
    assert sorted(order) == sorted(files)
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
    replaced = [HUB, MAT, 'search-index.json', 'sitemap.xml']
    (pkg.parent / 'ORDER.txt').write_text('\n'.join(order), encoding='utf-8')
    (pkg.parent / 'REPLACED.txt').write_text(' '.join(replaced), encoding='utf-8')
    exp = ''.join(f'{sha((live_dir / rel).read_bytes())}  {rel}\n' for rel in replaced)
    (pkg.parent / 'EXPECTED_BEFORE.txt').write_text(exp, encoding='utf-8')
    print(f'пакет: {len(order)} файлов ({len(replaced)} заменяются, {len(order) - len(replaced)} новых) → {pkg}')


if __name__ == '__main__':
    main()
