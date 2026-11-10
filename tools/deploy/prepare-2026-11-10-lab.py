#!/usr/bin/env python3
"""Выкладка 10.11.2026: страница «Лабораторные исследования», «наша лаборатория» в «Документах для Роспотребнадзора»,
отступы в таблицах на всём сайте (решение владельца 10.11.2026: «Отлично, вноси изменения на хостинг»).

    python3 tools/site/build_prod.py
    python3 tools/deploy/prepare-2026-11-10-lab.py <файлы сайта> <папка pkg> [MANIFEST]

<файлы сайта> — 24 страницы index.php, sitemap.xml и search-index.json, как их отдаёт сайт по HTTPS перед выкладкой.

На сайте страницы отличаются от сборки и в местах, которые прежние выкладки оставили как на сайте (место
<style id="m-crumbs">, role="group" у бегущей строки, стили карточек насекомых, первого экрана вентиляции и т. п.) —
их не трогаем. В файлы с сайта переносятся только:
  * на всех 24 страницах — пункт «Лабораторные исследования» в шапке, мобильном меню и подвале (блоки <header>,
    <nav class="mmenu">, <footer> из сборки; без ссылок на новую страницу они должны совпадать с сайтом байт в байт);
  * на 20 страницах с таблицами — <style id="t-inset"> (поле 16–24 px у первой и последней ячейки) сразу после m-crumbs;
  * «Магазины и торговые сети» — правило «Сводного отчёта по сети» на телефоне (колонка «Визиты» скрыта до 600 px);
  * «Разработка ППК» — фраза «Исследования по плану-графику проводит наша лаборатория — цены и расчёт»;
  * «Документы для Роспотребнадзора» — страница целиком из сборки (на сайте она = сборка 054f332, все отличия — правки
    10.11.2026: «Наша лаборатория» в группе 4 и п. 2.2, карточка, FAQ, JSON-LD, меню, t-inset).
Новые файлы: страница laboratornye-issledovaniya/index.php из сборки, её картинки, чек-лист PDF (пересобран 10.11.2026).
sitemap.xml — с сайта + адрес новой страницы, lastmod 2026-11-10 у документов и разработки ППК;
search-index.json — из страниц пакета (tools/search/build_index.py).
Проверки: блок счётчиков (Метрика 113675622, UIS/CoMagic, Radist) на каждой странице ровно один, байт в байт как на
сайте и как server/counters.html; в остатке «пакет → сборка» нет ни одной из переносимых правок.
"""
import difflib
import hashlib
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / 'dist' / 'timeweb'
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
LAB = 'laboratornye-issledovaniya/'
DOK = 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.php'
PDF = 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/chek-list-dokumentov-dlya-rospotrebnadzora.pdf'
NEW_FILES = (['img/lab-hero.webp', 'img/lab-hero-1440.webp', 'img/lab-hero-mob.webp', 'img/lab-hero-mob-760.webp',
              'img/lab-og.jpg']
             + [f'img/lab-i-{c}.webp' for c in ('ppk', 'smyvy', 'vozduh', 'voda', 'pishcha', 'faktory', 'rabochie-mesta',
                                                'radiaciya', 'sterilnost', 'sterilizatory', 'obluchateli', 'pochva',
                                                'ispytaniya', 'elektro')]
             + [f'img/lab-s{n}.webp' for n in range(1, 6)])
BLOCKS = [re.compile(r'<header\b.*?</header>', re.S), re.compile(r'<nav class="mmenu".*?</nav>', re.S),
          re.compile(r'<footer\b.*?</footer>', re.S)]
LAB_LINK = re.compile(r'(?:<li>)?<a href="(?:\.\./)*' + re.escape(LAB) + r'"[^>]*>Лабораторные исследования'
                      r'(?:<svg.*?</svg>)?</a>(?:</li>)?', re.S)
M_CRUMBS = re.compile(r'<style id="m-crumbs">.*?</style>', re.S)
T_INSET = re.compile(r'\n?<style id="t-inset">.*?</style>', re.S)
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
NO_COUNTERS = {'privacy/index.php', 'soglasie/index.php'}
# правки внутри страницы, которые переносятся из сборки (по фрагменту в отличии «сайт → сборка»)
PICK = {
    'magaziny-i-torgovye-seti/index.php': re.compile(r't-rep-tb|t-kpis span\{hyphens'),
    'razrabotka-ppk/index.php': re.compile(r'наша лаборатория|laboratornye-issledovaniya'),
}
PICK_N = {'magaziny-i-torgovye-seti/index.php': 3, 'razrabotka-ppk/index.php': 1}
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import build_prod  # noqa: E402


def sha(b):
    return hashlib.sha256(b).hexdigest()


def toks(s):
    return re.split(r'(?<=[>};])', s)


def ops(a, b):
    ta, tb = toks(a), toks(b)
    return ta, tb, [o for o in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes() if o[0] != 'equal']


def pick(live, built, rx):
    """перенести из сборки только отличия, в которых есть rx"""
    ta, tb, oo = ops(live, built)
    out, last, n = [], 0, 0
    for t, i1, i2, j1, j2 in oo:
        x, y = ''.join(ta[i1:i2]), ''.join(tb[j1:j2])
        if rx.search(x + y):
            out.append(''.join(ta[last:i1]) + y)
            last, n = i2, n + 1
    out.append(''.join(ta[last:]))
    return ''.join(out), n


def page(rel, live, built):
    if rel == DOK:
        return built
    new = live
    for rx in BLOCKS:
        lo, bu = rx.findall(live), rx.findall(built)
        assert len(lo) == 1 and len(bu) == 1, f'{rel}: блок {rx.pattern[:16]} найден {len(lo)}/{len(bu)} раз'
        assert LAB_LINK.sub('', lo[0]) == LAB_LINK.sub('', bu[0]), f'{rel}: в блоке {rx.pattern[:16]} есть другие отличия'
        new = new.replace(lo[0], bu[0], 1)
    ti = T_INSET.findall(built)
    if ti and 't-inset' not in live:
        mc = M_CRUMBS.findall(new)
        assert len(mc) == 1, f'{rel}: нет <style id="m-crumbs">'
        new = new.replace(mc[0], mc[0] + ti[0], 1)
    if rel in PICK:
        new, n = pick(new, built, PICK[rel])
        assert n == PICK_N[rel], f'{rel}: перенесено {n} правок, ожидалось {PICK_N[rel]}'
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
    if rel != DOK:
        assert new.count(LAB) - live.count(LAB) == 3 + (rel == 'razrabotka-ppk/index.php'), f'{rel}: ссылок на лабораторию {live.count(LAB)} → {new.count(LAB)}'
        assert T_INSET.findall(new) == T_INSET.findall(built), rel + ': t-inset не как в сборке'
        # место m-crumbs на сайте другое, чем в сборке, — остаток сравниваем без этих двух стилей
        strip = lambda s: T_INSET.sub('', M_CRUMBS.sub('', s))
        ta, tb, rest = ops(strip(new), strip(built))
        for t, i1, i2, j1, j2 in rest:
            x, y = ''.join(ta[i1:i2]), ''.join(tb[j1:j2])
            bad = LAB_LINK.search(x + y) or 't-inset' in x + y or (rel in PICK and PICK[rel].search(x + y))
            assert not bad, f'{rel}: в остатке «пакет → сборка» осталась переносимая правка: {(x or y)[:120]!r}'


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    live_dir, pkg = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    pages = sorted(str(p.relative_to(live_dir)) for p in live_dir.rglob('index.php'))
    built = sorted(str(p.relative_to(DIST)) for p in DIST.rglob('index.php'))
    assert pages == [p for p in built if not p.startswith(LAB)], 'набор страниц на сайте и в сборке разный'
    cblock = (ROOT / 'server' / 'counters.html').read_text(encoding='utf-8')
    files = {}
    for rel in pages:
        live = (live_dir / rel).read_text(encoding='utf-8')
        b = (DIST / rel).read_text(encoding='utf-8')
        new = page(rel, live, b)
        check(rel, live, new, b)
        if rel not in NO_COUNTERS:
            assert COUNTERS.findall(new)[0] in cblock, rel + ': блок счётчиков не как server/counters.html'
        files[rel] = new.encode('utf-8')
        print(f'{rel}: ссылок на лабораторию {live.count(LAB)} → {new.count(LAB)}; '
              f'{"t-inset; " if "t-inset" in new else ""}счётчики прежние')
    lab = (DIST / LAB / 'index.php').read_bytes()
    assert len(COUNTERS.findall(lab.decode('utf-8'))) == 1 and COUNTERS.findall(lab.decode('utf-8'))[0] in cblock
    assert b'noindex' not in lab, 'в странице лаборатории остался noindex'
    files[LAB + 'index.php'] = lab
    for f in NEW_FILES + [PDF]:
        files[f] = (DIST / f).read_bytes()
    # sitemap: с сайта + новая страница + lastmod
    sm = (live_dir / 'sitemap.xml').read_text(encoding='utf-8')
    smb = (DIST / 'sitemap.xml').read_text(encoding='utf-8')
    blk = re.search(r'\n  <url>\s*<loc>' + re.escape(SITE + LAB) + r'</loc>.*?</url>', smb, re.S).group(0)
    prev = re.findall(r'<loc>([^<]+)</loc>', smb[:smb.index(blk)])[-1]
    m = re.search(r'<loc>' + re.escape(prev) + r'</loc>.*?</url>', sm, re.S)
    assert m and SITE + LAB not in sm
    sm = sm[:m.end()] + blk + sm[m.end():]
    for rel in ('normativnaya-baza/dokumenty-dlya-rospotrebnadzora/', 'razrabotka-ppk/'):
        pat = re.compile(r'(<loc>' + re.escape(SITE + rel) + r'</loc>\s*<lastmod>)([0-9-]+)(</lastmod>)')
        assert len(pat.findall(sm)) == 1, rel
        sm = pat.sub(r'\g<1>2026-11-10\g<3>', sm)
    files['sitemap.xml'] = sm.encode('utf-8')
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        for rel in build_prod.PAGES:
            php = rel[:-len('index.html')] + 'index.php'
            d = td / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            d.write_bytes(files[php])
        out = td / 'search-index.json'
        r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'search' / 'build_index.py'), '--pages', str(td),
                            '--out', str(out)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        print(r.stdout.strip())
        files['search-index.json'] = out.read_bytes()
    # порядок: картинки и PDF → новая страница → страницы со ссылкой на неё → поиск → sitemap
    order = NEW_FILES + [PDF, LAB + 'index.php'] + [p for p in pages if p != DOK] + [DOK, 'search-index.json',
                                                                                      'sitemap.xml']
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
