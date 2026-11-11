#!/usr/bin/env python3
"""Выкладка 11.11.2026: страница «Дератизация и дезинсекция для организаций» (/deratizatsiya-i-dezinsektsiya/),
пункт меню на всех страницах, карточка комплекса в «Смотрите также» дератизации и дезинсекции, новые цены договора.
Решение владельца 11.11.2026: «Делай новую страницу. И выкладывай её на TimeWeb».

    python3 tools/site/build_prod.py
    python3 tools/deploy/prepare-2026-11-11-dd.py <файлы сайта> <папка pkg> [MANIFEST]

<файлы сайта> — 25 страниц index.php, sitemap.xml и search-index.json, как их отдаёт сайт по HTTPS перед выкладкой
(снимок с Mac mini: tools/deploy/fetch-2026-11-11-dd.sh).

На сайте страницы отличаются от сборки и в местах, которые прежние выкладки оставили как на сайте, — их не трогаем.
В файлы с сайта переносятся только:
  * на всех 25 страницах — пункт «Дератизация и дезинсекция» в «Услугах» шапки, мобильного меню и подвала (блоки
    <header>, <nav class="mmenu">, <footer> из сборки; без ссылок на новую страницу они должны совпадать с сайтом
    байт в байт);
  * «Дератизация» и «Дезинсекция» — блок «Смотрите также» из сборки (первая карточка — комплекс; на сайте блок должен
    совпадать с прежней сборкой — коммит BASE);
  * «Договор» — цены и ссылка «Комплекс» функцией tools/deratizatsiya-i-dezinsektsiya/dogovor_prices.py apply().
Новые файлы: страница deratizatsiya-i-dezinsektsiya/index.php из сборки и её 5 картинок.
sitemap.xml — с сайта + адрес новой страницы (после дезинсекции), lastmod 2026-11-11 у договора;
search-index.json — из страниц пакета (tools/search/build_index.py).
Проверки: блок счётчиков (Метрика 113675622, UIS/CoMagic, Radist) на каждой странице ровно один, байт в байт как на
сайте и как server/counters.html; в остатке «пакет → сборка» нет ни одной из переносимых правок.
"""
import difflib
import hashlib
import importlib.util
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / 'dist' / 'timeweb'
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
DD = 'deratizatsiya-i-dezinsektsiya/'
DOG = 'dogovor-deratizatsiya-dezinsektsiya/index.php'
REL_PAGES = ('deratizatsiya/index.php', 'dezinsektsiya/index.php')
BASE = '0dbd121'  # последний коммит в GitHub до страницы «Дератизация и дезинсекция»
NEW_FILES = ['img/dd-hero.webp', 'img/dd-hero-1440.webp', 'img/dd-hero-mob.webp', 'img/dd-hero-mob-760.webp',
             'img/dd-og.jpg']
BLOCKS = [re.compile(r'<header\b.*?</header>', re.S), re.compile(r'<nav class="mmenu".*?</nav>', re.S),
          re.compile(r'<footer\b.*?</footer>', re.S)]
DD_LINK = re.compile(r'(?:<li>)?<a href="(?:\.\./)*' + re.escape(DD) + r'"[^>]*>Дератизация и(?: |\xa0|&nbsp;)дезинсекция'
                     r'(?:<svg.*?</svg>)?</a>(?:</li>)?', re.S)
REL = re.compile(r'<section class="s s-rel" id="smotrite-takzhe">.*?</section>', re.S)
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
NO_COUNTERS = {'privacy/index.php', 'soglasie/index.php'}
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import build_prod  # noqa: E402

_spec = importlib.util.spec_from_file_location('dogovor_prices', ROOT / 'tools' / 'deratizatsiya-i-dezinsektsiya'
                                               / 'dogovor_prices.py')
dogovor_prices = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dogovor_prices)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def toks(s):
    return re.split(r'(?<=[>};])', s)


def ops(a, b):
    ta, tb = toks(a), toks(b)
    return ta, tb, [o for o in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes() if o[0] != 'equal']


def old_rel(rel):
    """блок «Смотрите также» прежней сборки (BASE — последний коммит до новой страницы) — таким он должен быть на сайте"""
    html = subprocess.run(['git', '-C', str(ROOT), 'show', BASE + ':' + rel[:-len('index.php')] + 'index.html'],
                          capture_output=True, text=True, check=True).stdout
    r = REL.findall(html)
    assert len(r) == 1, rel
    return r[0]


def page(rel, live, built):
    new = live
    for rx in BLOCKS:
        lo, bu = rx.findall(live), rx.findall(built)
        assert len(lo) == 1 and len(bu) == 1, f'{rel}: блок {rx.pattern[:16]} найден {len(lo)}/{len(bu)} раз'
        assert DD_LINK.sub('', lo[0]) == DD_LINK.sub('', bu[0]), f'{rel}: в блоке {rx.pattern[:16]} есть другие отличия'
        new = new.replace(lo[0], bu[0], 1)
    if rel in REL_PAGES:
        lo, bu = REL.findall(new), REL.findall(built)
        assert len(lo) == 1 and len(bu) == 1, rel + ': «Смотрите также»'
        assert lo[0] == old_rel(rel), rel + ': «Смотрите также» на сайте не как в прежней сборке'
        new = new.replace(lo[0], bu[0], 1)
    if rel == DOG:
        new = dogovor_prices.apply(new)
    return new


def check(rel, live, new, built):
    lb, pb = live.encode('utf-8'), new.encode('utf-8')
    c1, c2 = COUNTERS.findall(live), COUNTERS.findall(new)
    if rel in NO_COUNTERS:
        assert c1 == c2 == [], rel + ': на странице документа появились счётчики'
    else:
        assert len(c1) == 1 and c1 == c2, rel + ': блок счётчиков изменён или не найден'
        for k in (b'113675622', b'srch', b'comagic', b'uiscom', b'radist'):
            assert lb.count(k) == pb.count(k), f'{rel}: {k!r}: на сайте {lb.count(k)}, в пакете {pb.count(k)}'
    want = 3 + (rel in REL_PAGES) + (rel == DOG)
    got = new.count(DD + '"') - live.count(DD + '"')
    assert got == want, f'{rel}: ссылок на новую страницу добавлено {got}, ожидалось {want}'
    # остаток «пакет → сборка»: только то, что прежние выкладки оставили как на сайте
    ta, tb, rest = ops(new, built)
    for t, i1, i2, j1, j2 in rest:
        x, y = ''.join(ta[i1:i2]), ''.join(tb[j1:j2])
        bad = DD in x + y or 'rel-card' in x + y or '4\xa0900' in x + y
        assert not bad, f'{rel}: в остатке «пакет → сборка» осталась переносимая правка: {(x or y)[:160]!r}'
    return len(rest)


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    live_dir, pkg = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    pages = sorted(str(p.relative_to(live_dir)) for p in live_dir.rglob('index.php'))
    built = sorted(str(p.relative_to(DIST)) for p in DIST.rglob('index.php'))
    # в сборке могут быть страницы, которые пока только в превью (с 11.11.2026 — направления и статьи раздела
    # «Лабораторные исследования»): они не выкладываются, ссылок на них в переносимых блоках быть не должно
    extra = [p for p in built if p not in pages and not p.startswith(DD)]
    assert set(pages) <= set(built) and DD + 'index.php' in built, 'на сайте есть страницы, которых нет в сборке'
    if extra:
        print('только в превью, не выкладываются: ' + ', '.join(extra))
    cblock = (ROOT / 'server' / 'counters.html').read_text(encoding='utf-8')
    files = {}
    for rel in pages:
        live = (live_dir / rel).read_text(encoding='utf-8')
        b = (DIST / rel).read_text(encoding='utf-8')
        new = page(rel, live, b)
        rest = check(rel, live, new, b)
        if rel not in NO_COUNTERS:
            assert COUNTERS.findall(new)[0] in cblock, rel + ': блок счётчиков не как server/counters.html'
        files[rel] = new.encode('utf-8')
        print(f'{rel}: ссылок на новую страницу {live.count(DD)} → {new.count(DD)}; '
              f'прежних отличий от сборки {rest}; счётчики прежние')
    dd = (DIST / DD / 'index.php').read_bytes()
    dds = dd.decode('utf-8')
    assert len(COUNTERS.findall(dds)) == 1 and COUNTERS.findall(dds)[0] in cblock, 'счётчики новой страницы'
    assert b'noindex' not in dd, 'в новой странице остался noindex'
    files[DD + 'index.php'] = dd
    for f in NEW_FILES:
        files[f] = (DIST / f).read_bytes()
    # sitemap: с сайта + новая страница + lastmod договора
    sm = (live_dir / 'sitemap.xml').read_text(encoding='utf-8')
    smb = (DIST / 'sitemap.xml').read_text(encoding='utf-8')
    blk = re.search(r'\n  <url>\s*<loc>' + re.escape(SITE + DD) + r'</loc>.*?</url>', smb, re.S).group(0)
    prev = re.findall(r'<loc>([^<]+)</loc>', smb[:smb.index(blk)])[-1]
    m = re.search(r'<loc>' + re.escape(prev) + r'</loc>.*?</url>', sm, re.S)
    assert m and SITE + DD not in sm and prev == SITE + 'dezinsektsiya/'
    sm = sm[:m.end()] + blk + sm[m.end():]
    pat = re.compile(r'(<loc>' + re.escape(SITE + 'dogovor-deratizatsiya-dezinsektsiya/') + r'</loc>\s*<lastmod>)'
                     r'([0-9-]+)(</lastmod>)')
    assert len(pat.findall(sm)) == 1
    sm = pat.sub(r'\g<1>2026-11-11\g<3>', sm)
    files['sitemap.xml'] = sm.encode('utf-8')
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        for rel in build_prod.PAGES:
            php = rel[:-len('index.html')] + 'index.php'
            if php not in files:
                continue  # страница только в превью — в поиск сайта не попадает
            d = td / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            d.write_bytes(files[php])
        out = td / 'search-index.json'
        # индекс — только из страниц пакета (страницы превью в поиск сайта не попадают): build_index.py с PAGES пакета
        keep = [rel for rel in build_prod.PAGES if rel[:-len('index.html')] + 'index.php' in files]
        code = ('import sys; sys.path.insert(0, %r); import build_prod; build_prod.PAGES = %r; sys.path.insert(0, %r); '
                'sys.argv = ["build_index.py", "--pages", %r, "--out", %r]; import build_index; build_index.main()'
                % (str(ROOT / 'tools' / 'site'), keep, str(ROOT / 'tools' / 'search'), str(td), str(out)))
        r = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        print(r.stdout.strip())
        files['search-index.json'] = out.read_bytes()
    # порядок: картинки → новая страница → страницы со ссылкой на неё → поиск → sitemap
    order = NEW_FILES + [DD + 'index.php'] + pages + ['search-index.json', 'sitemap.xml']
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
    replaced = [rel for rel in order if (live_dir / rel).exists()]
    (pkg.parent / 'ORDER.txt').write_text('\n'.join(order), encoding='utf-8')
    (pkg.parent / 'REPLACED.txt').write_text(' '.join(replaced), encoding='utf-8')
    exp = ''.join(f'{sha((live_dir / rel).read_bytes())}  {rel}\n' for rel in replaced)
    (pkg.parent / 'EXPECTED_BEFORE.txt').write_text(exp, encoding='utf-8')
    print(f'пакет: {len(order)} файлов ({len(replaced)} заменяются, {len(order) - len(replaced)} новых) → {pkg}')


if __name__ == '__main__':
    main()
