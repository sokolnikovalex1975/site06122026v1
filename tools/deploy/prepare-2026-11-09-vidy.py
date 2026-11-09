#!/usr/bin/env python3
"""Выкладка 09.11.2026: «Документы для Роспотребнадзора» — 15 видов объектов вместо 8, чек-лист PDF на 14 страниц.

    git worktree add --detach /tmp/wt-vidy-base 9147cff && (cd /tmp/wt-vidy-base && python3 tools/site/build_prod.py)
    python3 tools/site/build_prod.py
    python3 tools/deploy/prepare-2026-11-09-vidy.py <файлы сайта> /tmp/wt-vidy-base/dist/timeweb <папка pkg> [MANIFEST]

<файлы сайта> — 24 страницы index.php, sitemap.xml и заменяемые файлы (PDF, обложки, OG, search-index.json), как их отдаёт
сайт по HTTPS перед выкладкой (/tmp/fetch_live.sh и докачка файлов).

Что в пакете (8 файлов, все заменяют файлы на сервере):
  * страница документов: в файл с сайта переносятся только изменения сборки 9147cff → эта ветка (`git merge-file`:
    база — сборка 9147cff, «наши» — файл с сайта, «их» — новая сборка); правки других задач на сайте сохраняются;
  * чек-лист PDF, обложки img/dok-cover-240/360/480/720.webp и img/dok-og.jpg — из новой сборки (на сайте — как в 9147cff);
  * search-index.json — из страниц пакета (страницы с сайта + новая страница документов) тем же tools/search/build_index.py.
Хаб нормативной базы и «Материалы» не выкладываются: «15 видов» в них — в карточках, которых на сайте нет (в main лежат
невыложенные ссылки на страницу документов — решения владельца нет, см. CHANGES 08.11.2026). sitemap.xml не меняется:
lastmod страницы документов на сайте уже 2026-11-09.
Проверки: изменения «сайт → пакет» те же, что «сборка 9147cff → новая»; блок счётчиков (Метрика 113675622, UIS/CoMagic,
Radist) на каждой странице — ровно один и байт в байт прежний, как в server/counters.html; поиск по сайту на месте.
"""
import difflib
import hashlib
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / 'dist' / 'timeweb'
DK = 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/'
PAGES = [DK + 'index.php']
BINARY = [DK + 'chek-list-dokumentov-dlya-rospotrebnadzora.pdf', 'img/dok-cover-240.webp', 'img/dok-cover-360.webp',
          'img/dok-cover-480.webp', 'img/dok-cover-720.webp', 'img/dok-og.jpg']
ORDER = BINARY + ['search-index.json'] + PAGES
COUNTERS = re.compile(rb'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import build_prod  # noqa: E402  список страниц сайта (index.html → index.php)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def hunks(x, y):
    sm = difflib.SequenceMatcher(None, x, y, autojunk=False)
    return [('\n'.join(x[i1:i2]), '\n'.join(y[j1:j2])) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != 'equal']


def merge(live, base, new, name):
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        for n, b in (('live', live), ('base', base), ('new', new)):
            (td / n).write_text(b, encoding='utf-8')
        r = subprocess.run(['git', 'merge-file', '-p', '-L', 'live', '-L', 'base', '-L', 'new',
                            str(td / 'live'), str(td / 'base'), str(td / 'new')], capture_output=True)
        assert r.returncode == 0, f'{name}: git merge-file — конфликтов {r.returncode}, разберите вручную'
        out = r.stdout.decode('utf-8')
    h1, h2 = hunks(base.split('\n'), new.split('\n')), hunks(live.split('\n'), out.split('\n'))
    assert h1 and h1 == h2, f'{name}: изменения «сайт → пакет» не совпадают с «сборка 9147cff → новая»'
    return out, len(h1)


def main():
    if len(sys.argv) not in (4, 5):
        raise SystemExit(__doc__)
    live_dir, base_dir, pkg = map(pathlib.Path, sys.argv[1:4])
    if pkg.exists():
        shutil.rmtree(pkg)
    files = {}
    cblock = (ROOT / 'server' / 'counters.html').read_bytes()
    for rel in PAGES:
        live = (live_dir / rel).read_text(encoding='utf-8')
        out, n = merge(live, (base_dir / rel).read_text(encoding='utf-8'), (DIST / rel).read_text(encoding='utf-8'), rel)
        lb, pb = live.encode('utf-8'), out.encode('utf-8')
        c1, c2 = COUNTERS.findall(lb), COUNTERS.findall(pb)
        assert len(c1) == 1 and c1 == c2, f'{rel}: блок счётчиков изменён или не найден'
        assert c1[0] in cblock, f'{rel}: счётчики на сайте не как в server/counters.html'
        for k in (b'113675622', b'srch', b'comagic', b'uiscom', b'radist'):
            assert lb.count(k) == pb.count(k), f'{rel}: {k!r}: на сайте {lb.count(k)}, в пакете {pb.count(k)}'
        files[rel] = pb
        print(f'{rel}: {n} мест (как в сборке); счётчики прежние; поиск на месте')
    sm = (live_dir / 'sitemap.xml').read_text(encoding='utf-8')
    assert re.search(r'dokumenty-dlya-rospotrebnadzora/</loc>\s*<lastmod>2026-11-09</lastmod>', sm), \
        'sitemap.xml: lastmod документов на сайте не 2026-11-09'
    for rel in BINARY:
        lv, bs, nw = (live_dir / rel).read_bytes(), (base_dir / rel).read_bytes(), (DIST / rel).read_bytes()
        assert lv == bs, f'{rel}: на сайте не как в сборке 9147cff'
        assert nw != bs and nw == (ROOT / rel).read_bytes(), rel
        files[rel] = nw
        print(f'{rel}: {len(lv)} → {len(nw)} байт')
    # индекс поиска — из страниц пакета: на сайте ищется то, что на нём есть
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        for rel in build_prod.PAGES:
            php = rel[:-len('index.html')] + 'index.php'
            d = td / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            d.write_bytes(files.get(php) or (live_dir / php).read_bytes())
        out = td / 'search-index.json'
        r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'search' / 'build_index.py'), '--pages', str(td),
                            '--out', str(out)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        print(r.stdout.strip())
        files['search-index.json'] = out.read_bytes()
    import json
    a = json.loads(files['search-index.json'])
    b = json.loads((ROOT / 'search-index.json').read_text(encoding='utf-8'))
    sa, sb = {json.dumps(x, ensure_ascii=False) for x in a['i']}, {json.dumps(x, ensure_ascii=False) for x in b['i']}
    print(f'search-index.json: {len(a["i"])} записей; не как в сборке репозитория: {len(sa - sb)} (страницы сайта не как в main)')
    for x in sorted(sa - sb)[:6]:
        print('   ', x[:160])
    lines = ''
    for rel in ORDER:
        d = pkg / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_bytes(files[rel])
        lines += f'{sha(files[rel])}  {rel}\n'
    if len(sys.argv) == 5:
        if pathlib.Path(sys.argv[4]).read_text(encoding='utf-8') != lines:
            raise SystemExit('пакет не совпадает с MANIFEST')
        print('MANIFEST совпадает')
    else:
        (pkg.parent / 'MANIFEST.sha256').write_text(lines, encoding='utf-8')
    exp = ''.join(f'{sha((live_dir / rel).read_bytes())}  {rel}\n' for rel in ORDER)
    (pkg.parent / 'EXPECTED_BEFORE.txt').write_text(exp, encoding='utf-8')
    print(f'пакет: {len(ORDER)} файлов → {pkg}')


if __name__ == '__main__':
    main()
