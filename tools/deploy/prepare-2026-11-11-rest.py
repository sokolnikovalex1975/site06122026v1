#!/usr/bin/env python3
"""Выкладка 11.11.2026: страницы «Дезинсекция кафе, ресторанов и столовых» (/dezinsektsiya/restorany-i-kafe/)
и «Дератизация ресторанов и кафе» (/deratizatsiya/restorany-i-kafe/), подпункты меню и ссылки на них.
Решение владельца 11.11.2026: «Готово. Выкладывай всё на TimeWeb и, соответственно, вноси изменения в верхнее
и нижнее меню, в зависимости от смысла этих страниц».

    python3 tools/site/build_prod.py
    python3 tools/deploy/prepare-2026-11-11-rest.py <файлы сайта> <папка pkg> [MANIFEST]

<файлы сайта> — все страницы сайта (index.php), sitemap.xml и search-index.json, как их отдаёт сайт по HTTPS перед
выкладкой (снимок с Mac mini 11.11.2026 14:55 МСК). Страниц из списка меню, которых нет на сайте (превью другого
чата: «Акт», «Схема точек»), в снимке нет — их не выкладываем и ссылок на них не ставим.

Страницы с сайта правятся точечно, остальное остаётся как на сайте:
  * на всех страницах — подпункты «Дезинсекция кафе и ресторанов» и «Дератизация ресторанов и кафе» под «Рестораны
    и кафе» в «Отраслях» шапки, мобильного меню и подвала (tools/menu/apply_menu.py без пунктов, которых нет на сайте;
    без подпунктов страница должна совпасть с сайтом байт в байт) и их стили в <style id="srch-st">;
  * ссылки на новые страницы в тексте (как в превью, tools/site/unify.py, page_specific):
    «Дезинсекция» — карточка «Рестораны, кафе и столовые»; «Дератизация» — плитка «Кафе и рестораны»;
    «Рестораны и кафе» — «Смотрите также», ссылки «Подробнее» в карточках вредителей, вопрос FAQ
    «Как часто нужен пест-контроль ресторана?», карточка «Разовая обработка» без контрольного осмотра;
    «Дератизация и дезинсекция» — строка «Кафе, ресторан, столовая»;
  * новые страницы — из dist/timeweb (build_prod.py: блок счётчиков server/counters.html), меню — как на сайте;
    ссылки на страницы, которых на сайте нет: акт → «Документы для Роспотребнадзора» (там образец акта),
    карточка схемы точек убрана, под схемой зон — ссылка на программу пест-контроля, строка «Оценка эффективности»
    в нормах убрана;
  * sitemap.xml — с сайта + два адреса (после «Ресторанов и кафе»), lastmod 2026-11-11 у страниц с правками в тексте;
  * search-index.json — из страниц пакета (tools/search/build_index.py).
Проверки: блок счётчиков на каждой странице ровно один, байт в байт как на сайте и как server/counters.html;
все внутренние ссылки и картинки новых страниц есть на сайте (status-urls.txt снимка) или в пакете.
"""
import hashlib
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / 'dist' / 'timeweb'
sys.path.insert(0, str(ROOT / 'tools' / 'menu'))
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import apply_menu  # noqa: E402
import build_prod  # noqa: E402
import unify  # noqa: E402

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
TODAY = '2026-11-11'
NEW = ['dezinsektsiya/restorany-i-kafe/index.php', 'deratizatsiya/restorany-i-kafe/index.php']
SUBS = apply_menu.INDUSTRY_SUB['restorany-i-kafe']
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
NO_COUNTERS = {'privacy/index.php', 'soglasie/index.php'}
SUB_CSS_START = '.nav-dd-panel a.nav-sub{'
SRCH_ST = re.compile(r'<style id="srch-st">.*?</style>', re.S)
NEW_IMG = ['img/dzr-hero.webp', 'img/dzr-hero-1440.webp', 'img/dzr-hero-mob.webp', 'img/dzr-hero-mob-760.webp', 'img/dzr-og.jpg',
           'img/drr-hero.webp', 'img/drr-hero-1440.webp', 'img/drr-hero-mob.webp', 'img/drr-hero-mob-760.webp', 'img/drr-og.jpg',
           'img/drr-prohodka-960.webp', 'img/drr-prohodka-640.webp']


def sha(b):
    return hashlib.sha256(b).hexdigest()


def prod_menu_lists(live_dir):
    """Пункты меню, у которых нет страницы на сайте, убираем (кроме двух новых страниц)."""
    have = {p.parent.relative_to(live_dir).as_posix() for p in live_dir.rglob('index.php')}
    new = {s for s, _ in SUBS}
    gone = []
    for name in ('USLUGI', 'INDUSTRIES', 'MATERIALS'):
        lst = getattr(apply_menu, name)
        keep = [(s, t) for s, t in lst if s.startswith('#') or s in have or s in new]
        gone += [s for s, _ in lst if (s, _) not in keep]
        setattr(apply_menu, name, keep)
    for k in list(apply_menu.FOOTER_MAT_EXTRA):
        if apply_menu.FOOTER_MAT_EXTRA[k][0] not in have:
            gone.append(apply_menu.FOOTER_MAT_EXTRA.pop(k)[0])
    return gone


def menu(rel, s, subs=True):
    """Три блока меню из apply_menu (только пункты, которые есть на сайте); subs=False — без новых подпунктов."""
    html = rel.replace('index.php', 'index.html')
    root, cur = next((r, c) for f, r, c in apply_menu.PAGES + apply_menu.LEGAL if f == html)
    saved = apply_menu.INDUSTRY_SUB
    apply_menu.INDUSTRY_SUB = saved if subs else {}
    try:
        cta = re.search(r'<nav class="mmenu"[^>]*>.*?(<a href="(?:\.\./)*#zayavka" class="btn btn-w btn-lg">.*?</a>)\s*</nav>',
                        s, re.S).group(1)
        nav, mm, cols = (apply_menu.typo(x) for x in apply_menu.build(root, cur, cta))
    finally:
        apply_menu.INDUSTRY_SUB = saved
    new = apply_menu.sub1(r'<nav class="nav" aria-label="Основное меню">.*?</nav>', nav, s)
    new = apply_menu.sub1(r'<nav class="mmenu" id="mmenu" aria-label="Мобильное меню">.*?</nav>', mm, new)
    new = apply_menu.sub1(r'<div><h4>(?:Объекты|Отрасли|Услуги)</h4>.*?(?=\n\s*<div><h4>Контакты</h4>)', cols, new)
    return new


def sub_css(s):
    """Стили подпунктов — в конец <style id="srch-st"> (как SRCH_CSS в apply_menu)."""
    m = SRCH_ST.findall(s)
    assert len(m) == 1, 'нет одного <style id="srch-st">'
    if SUB_CSS_START in m[0]:
        return s
    full = re.search(r'<style id="srch-st">.*?</style>', apply_menu.SRCH_CSS, re.S).group(0)
    rules = full[full.index(SUB_CSS_START):-len('</style>')]
    assert m[0] + '' == full.replace(rules, ''), 'стили поиска на сайте не как в сборке без подпунктов'
    return s.replace(m[0], full, 1)


def content(rel, s):
    """Ссылки на новые страницы в тексте — те же замены, что в превью (unify.page_specific); каждая ровно один раз."""
    n = 0

    def rep(old, new, regex=False):
        nonlocal s, n
        if regex:
            s2, k = re.subn(old, new, s)
        else:
            k = s.count(old)
            s2 = s.replace(old, new)
        assert k == 1, f'{rel}: «{old[:70]}» — вхождений {k}'
        s, n = s2, n + 1

    if rel == 'dezinsektsiya/index.php':
        rep('<h3><a href="../restorany-i-kafe/">Рестораны, кафе и&nbsp;столовые</a></h3>',
            '<h3><a href="restorany-i-kafe/">Рестораны, кафе и&nbsp;столовые</a></h3>')
    elif rel == 'deratizatsiya/index.php':
        rep('<a class="ind-more" href="../restorany-i-kafe/">Пест-контроль ресторанов и\u00a0кафе',
            '<a class="ind-more" href="restorany-i-kafe/">Дератизация ресторанов и\u00a0кафе')
    elif rel == 'deratizatsiya-i-dezinsektsiya/index.php':
        rep('.dd-obj{display:flex;align-items:center;gap:12px;color:var(--t1)}',
            '.dd-obj{display:flex;align-items:center;gap:12px;color:var(--t1)}\n'
            'td[data-l="Что под контролем"] a{color:var(--t1);border-bottom:1px solid rgba(124,134,255,.45)}')
        rep('<td data-l="Что под контролем">кухня, мойка, склад продуктов, зал</td>',
            '<td data-l="Что под контролем">кухня, мойка, склад продуктов, зал; отдельно — '
            '<a href="../dezinsektsiya/restorany-i-kafe/">дезинсекция</a> и '
            '<a href="../deratizatsiya/restorany-i-kafe/">дератизация ресторана</a></td>')
    elif rel == 'restorany-i-kafe/index.php':
        i = s.index('id="smotrite-takzhe"')
        j = s.index('</section>', i)
        block = s[i:j]
        for old, new in (('dezins', 'dzr'), ('derat', 'drr')):
            block, k = re.subn(r'<a class="card rel-card" href="\.\./' + re.escape(unify.URL[old]) + r'">.*?</a>',
                               lambda m, kk=new: unify.rel_card('../', kk), block, count=1, flags=re.S)
            assert k == 1, rel + ': нет карточки ' + old
            n += 1
        s = s[:i] + block + s[j:]
        # вопрос FAQ: в HTML (неразрывный пробел) и в FAQPage (обычный)
        s2, k = re.subn(r'Как часто нужно проводить дезинсекцию в[ \xa0]ресторане\?', 'Как часто нужен пест-контроль ресторана?', s)
        assert k == 2, f'{rel}: вопрос FAQ — вхождений {k}'
        s, n = s2, n + 1
        rep(r'(Истребительная дезинсекция при[ \xa0]очаге: ночью), с[ \xa0]контрольным осмотром через 10–14[ \xa0]дней',
            lambda m: m.group(1) + ', без гостей и\xa0персонала', regex=True)
        more = ('<a class="pest-more" href="../{0}" style="display:inline-block;margin-top:12px;font-size:14px;color:var(--t1);'
                'border-bottom:1px solid rgba(124,134,255,.45)">{1}&nbsp;→</a>')
        for h3, k_, text in (('Рыжие тараканы', 'dzr', 'Подробнее о дезинсекции'), ('Мыши', 'drr', 'Подробнее о дератизации'),
                             ('Крысы', 'drr', 'Подробнее о дератизации')):
            a = s.find('<h3>' + h3 + '</h3>')
            assert a > 0 and s.count('<h3>' + h3 + '</h3>') == 1, rel + ': нет карточки «' + h3 + '»'
            b = s.index('</div></article>', a)
            assert 'class="pest-more"' not in s[a:b]
            s = s[:b] + more.format(unify.URL[k_], text) + s[b:]
            n += 1
    return s, n


TOUCHED = ['dezinsektsiya/index.php', 'deratizatsiya/index.php', 'deratizatsiya-i-dezinsektsiya/index.php',
           'restorany-i-kafe/index.php']


def fallback(rel, s, live_ok):
    """Новые страницы: ссылки на страницы, которых нет на сайте (превью другого чата), — заменяем или убираем."""
    if 'materialy/akt-deratizatsii-i-dezinsektsii/' in live_ok:
        raise SystemExit('страница акта уже на сайте — обновите fallback()')
    akt = '../../materialy/akt-deratizatsii-i-dezinsektsii/'
    k = s.count(akt)
    assert k >= 3, (rel, 'акт', k)
    s = s.replace(akt, '../../normativnaya-baza/dokumenty-dlya-rospotrebnadzora/')
    # карточка схемы точек
    s, k = re.subn(r'\n\s*<div class="card rk-smp"><a class="rk-smp-im" href="\.\./\.\./materialy/skhema-tochek-pest-kontrolya/".*?'
                   r'Образец PDF</a></span></div></div>', '', s, flags=re.S)
    assert k == 1, (rel, 'схема', k)
    # строка под схемой зон
    s, k = re.subn(r'<p class="rk-zdoc">.*?</p>',
                   '<p class="rk-zdoc">Номера точек на схеме совпадают с номерами в журнале и в акте — '
                   'схема входит в <a href="../../materialy/programma-pest-kontrolya/">программу пест-контроля</a>.</p>', s,
                   count=1, flags=re.S)
    assert k == 1, (rel, 'rk-zdoc', k)
    # строка «Оценка эффективности» в нормах — если страницы на сайте нет
    bads = ['akt-deratizatsii-i-dezinsektsii', 'skhema-tochek-pest-kontrolya', 'zashchita-ot-proniknoveniya-gryzunov']
    if 'normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/' not in live_ok:
        s, k = re.subn(r'\n\s*<li><b>Оценка эффективности</b>.*?</li>', '', s, flags=re.S)
        assert k == 1, (rel, 'эффективность', k)
        bads.append('effektivnost-deratizatsii-i-dezinsektsii')
    for bad in bads:
        assert bad not in s, (rel, bad)
    return s


def links_ok(rel, s, live_ok, pkg, before=''):
    """Все внутренние ссылки, которых не было на странице до правки, ведут на файлы сайта или пакета."""
    old = set(re.findall(r'(?:href|src)="([^"#?]+)', before)) | {x.strip().split(' ')[0] for v in re.findall(r'srcset="([^"]+)"', before) for x in v.split(',')}
    base = pathlib.PurePosixPath('/' + rel).parent
    bad = []
    for u in re.findall(r'(?:href|src)="([^"#?]+)', s) + [x.strip().split(' ')[0] for v in re.findall(r'srcset="([^"]+)"', s)
                                                         for x in v.split(',')]:
        if u in old:
            continue
        if u.startswith(('http', 'mailto:', 'tel:', 'data:', 'javascript:', '//')) or not u:
            continue
        parts = []
        for x in str(base / u).split('/'):
            if x == '..':
                parts.pop()
            elif x and x != '.':
                parts.append(x)
        v = '/'.join(parts) + ('/' if u.endswith('/') else '')
        if v in ('', '/') or v in live_ok or v in pkg or (v.endswith('/') and (v + 'index.php') in pkg):
            continue
        bad.append(v)
    assert not bad, f'{rel}: нет на сайте и в пакете: {sorted(set(bad))}'


def counters_same(rel, live, new, cblock):
    c1, c2 = COUNTERS.findall(live), COUNTERS.findall(new)
    if rel in NO_COUNTERS:
        assert c1 == c2 == [], rel
        return
    assert len(c1) == 1 and c1 == c2, rel + ': блок счётчиков изменён или не найден'
    assert c1[0] in cblock, rel + ': блок счётчиков не как server/counters.html'
    lb, pb = live.encode('utf-8'), new.encode('utf-8')
    for k in (b'113675622', b'comagic', b'uiscom', b'radist'):
        assert lb.count(k) == pb.count(k), f'{rel}: {k!r}'


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    live_dir, pkg = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    st = (live_dir.parent / 'status-urls.txt')
    live_ok = {l.split(' ', 1)[1].split('?')[0] for l in st.read_text().splitlines() if l.startswith('200 ')}
    gone = prod_menu_lists(live_dir)
    print('нет на сайте, в меню не ставим:', ', '.join(gone) or '—')
    pages = sorted(str(p.relative_to(live_dir)) for p in live_dir.rglob('index.php'))
    live_ok |= {p[:-len('index.php')] for p in pages} | {''}
    cblock = (ROOT / 'server' / 'counters.html').read_text(encoding='utf-8')
    files, touched = {}, []
    for rel in pages:
        live = (live_dir / rel).read_text(encoding='utf-8')
        assert 'restorany-i-kafe/" class="nav-sub"' not in live, rel + ': подпункты уже на сайте'
        # меню без подпунктов из сборки должно совпасть с сайтом байт в байт
        assert menu(rel, live, subs=False) == live, rel + ': меню сборки (без подпунктов) не как на сайте'
        new, n = content(rel, live)
        new = sub_css(menu(rel, new))
        counters_same(rel, live, new, cblock)
        files[rel] = new.encode('utf-8')
        if n:
            touched.append(rel)
        print(f'{rel}: ссылок в тексте +{n}, подпункты меню; счётчики прежние')
    assert sorted(touched) == sorted(TOUCHED), touched

    # новые страницы — из dist/timeweb, меню — как на сайте, ссылки — только на то, что есть
    for rel in NEW:
        s = (DIST / rel).read_text(encoding='utf-8')
        s = fallback(rel, menu(rel, s), live_ok)
        c = COUNTERS.findall(s)
        assert len(c) == 1 and c[0] in cblock, rel + ': счётчики'
        assert 'noindex' not in s and s.count("ym(113675622, 'init'") == 1, rel
        assert s.count('aria-current="page"') >= 3, rel
        files[rel] = s.encode('utf-8')
    for f in NEW_IMG:
        files[f] = (ROOT / f).read_bytes()
    pkg_set = set(files)
    for rel in NEW:
        links_ok(rel, files[rel].decode('utf-8'), live_ok, pkg_set)
    for rel in pages:
        links_ok(rel, files[rel].decode('utf-8'), live_ok, pkg_set, (live_dir / rel).read_text(encoding='utf-8'))

    # sitemap: с сайта + 2 адреса после «Ресторанов и кафе» + lastmod у страниц с правками в тексте
    sm = (live_dir / 'sitemap.xml').read_text(encoding='utf-8')
    m = re.search(r'\n  <url>\s*<loc>' + re.escape(SITE + 'restorany-i-kafe/') + r'</loc>.*?</url>', sm, re.S)
    assert m and SITE + 'dezinsektsiya/restorany-i-kafe/' not in sm
    add = ''
    for rel in NEW:
        u = SITE + rel[:-len('index.php')]
        blk = m.group(0).replace(SITE + 'restorany-i-kafe/', u)
        blk = re.sub(r'<lastmod>[^<]*</lastmod>', f'<lastmod>{TODAY}</lastmod>', blk)
        blk = re.sub(r'<priority>[^<]*</priority>', '<priority>0.8</priority>', blk)
        add += blk
    sm = sm[:m.end()] + add + sm[m.end():]
    for rel in touched:
        u = SITE + rel[:-len('index.php')]
        pat = re.compile(r'(<loc>' + re.escape(u) + r'</loc>\s*<lastmod>)([0-9-]+)(</lastmod>)')
        assert len(pat.findall(sm)) == 1, rel
        sm = pat.sub(r'\g<1>' + TODAY + r'\g<3>', sm)
    files['sitemap.xml'] = sm.encode('utf-8')

    # поиск — из страниц пакета (только те, что есть на сайте или в пакете)
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        used = [r for r in build_prod.PAGES if r[:-len('index.html')] + 'index.php' in files]
        for rel in used:
            d = td / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            d.write_bytes(files[rel[:-len('index.html')] + 'index.php'])
        out = td / 'search-index.json'
        # индекс — только из страниц, которые есть на сайте (превью акта и схемы точек в него не попадают)
        sys.path.insert(0, str(ROOT / 'tools' / 'search'))
        import build_index  # noqa: E402
        build_index.build_prod.PAGES[:] = used
        argv, sys.argv = sys.argv, ['build_index.py', '--pages', str(td), '--out', str(out)]
        try:
            build_index.main()
        finally:
            sys.argv = argv
        files['search-index.json'] = out.read_bytes()

    order = NEW_IMG + NEW + pages + ['search-index.json', 'sitemap.xml']
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
