#!/usr/bin/env python3
"""Выкладка 11.11.2026: страницы «Акт дератизации и дезинсекции» (/materialy/akt-deratizatsii-i-dezinsektsii/) и
«Схема точек пест-контроля» (/materialy/skhema-tochek-pest-kontrolya/), пункты меню, ссылки на них, плитки документов
и отрасли в форме на главной. Решение владельца 11.11.2026: «Выноси эти две последние правки и выкладывай всё на
TimeWeb. Не забудь про то, что это нужно разместить где-то в меню, вверху, внизу».

    python3 tools/deploy/prepare-2026-11-11-akt.py <файлы сайта> <папка pkg> [MANIFEST]

<файлы сайта> — все страницы сайта (index.php по tools/menu/apply_menu.PAGES + LEGAL без ещё не выложенных),
sitemap.xml, search-index.json, app.min.js и style.css, как их отдаёт сайт по HTTPS перед выкладкой
(tools/deploy/fetch-2026-11-11-akt.sh). Страницы сайта правятся точечно, остальное остаётся как на сайте:
  * на всех страницах — «Схема точек пест-контроля» и «Акт дератизации и дезинсекции» в «Материалах» шапки, мобильного
    меню и подвала (после «Журнала пест-контроля»). Меню строится так, как оно сейчас на сайте: списки apply_menu из
    коммита c7114e1 (на сайте ещё нет пункта «Пест-контроль для бизнеса» из 3712f71), пункты «Материалов» — текущие.
    Без шести новых ссылок страница совпадает с прежней байт в байт;
  * правки текста — из коммита fd7a780 (главная: ссылки плиток «Документы» и отрасли в форме; программа, журнал,
    документы для Роспотребнадзора — ссылки на новые страницы); замены вычисляются из разницы версий страницы
    в репозитории и ложатся на страницу сайта, только если исходный фрагмент найден на ней ровно один раз;
  * главная: стили плиток во встроенном <style> (правка из fd7a780) сверяются со сборкой build_prod;
    app.min.js?v=20261111akt (новый app.min.js: подпись вида объекта в комментарии заявки);
  * хаб «Материалы»: «Материал 07 · Готовится» → карточка схемы точек, новая карточка акта «Материал 12», оценка
    эффективности — «Материал 13», разметка ItemList — как в репозитории;
  * новые страницы — из сборки для Timeweb (tools/site/build_prod.py) с тем же меню, что у страниц сайта;
  * sitemap.xml — с сайта + два адреса, lastmod 2026-11-11 у страниц с правками в тексте;
  * search-index.json — из страниц пакета (tools/search/build_index.py).
Проверки: счётчики (Метрика 113675622, UIS, Radist — официальные коды по закону владельца) на каждой странице байт
в байт как на сайте и как server/counters.html; все внутренние ссылки пакета ведут на страницы сайта или файлы пакета.
"""
import ast
import difflib
import hashlib
import io
import json
import pathlib
import posixpath
import re
import subprocess
import sys
import tempfile
import types
from contextlib import redirect_stdout

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'menu'))
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
sys.path.insert(0, str(ROOT / 'tools' / 'search'))
import apply_menu  # noqa: E402
import build_prod  # noqa: E402

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
SKH, AKT = 'materialy/skhema-tochek-pest-kontrolya', 'materialy/akt-deratizatsii-i-dezinsektsii'
SLUGS = [SKH, AKT]
NEW = [s + '/index.php' for s in SLUGS]
TODAY = '2026-11-11'
MENU_REV = 'c7114e1'  # меню на сайте = apply_menu этого коммита (+ новые пункты «Материалов»)
APP_V_OLD, APP_V_NEW = 'app.min.js?v=20261106s2', 'app.min.js?v=20261111akt'
CBLOCK = re.compile(r'<!-- Yandex\.Metrika counter.*?<!-- /Yandex\.Metrika counter -->|<!-- UIS -->.*?<!-- UIS -->'
                    r'|<!-- Radist -->.*?<!-- /Radist -->|<!-- Yandex\.Metrika counter: noscript -->.*?</noscript>', re.S)
NO_COUNTERS = {'privacy/index.php', 'soglasie/index.php'}
NOT_LIVE = set(SLUGS) | {'zashchita-ot-proniknoveniya-gryzunov'}
REVS = [('fd7a780~1', 'fd7a780', ['index.html', 'materialy/programma-pest-kontrolya/index.html',
                                   'materialy/zhurnal-pest-kontrolya/index.html',
                                   'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.html'])]
HUB = 'materialy/index.php'
MAIN = 'index.php'
MENU_RES = [r'<nav class="nav" aria-label="Основное меню">.*?</nav>',
            r'<nav class="mmenu" id="mmenu" aria-label="Мобильное меню">.*?</nav>',
            r'<div><h4>(?:Объекты|Отрасли|Услуги)</h4>.*?(?=\n\s*<div><h4>Контакты</h4>)']
# новые ссылки меню (для сверки «без них страница прежняя»)
NEWLINK = re.compile(r'<li><a href="[^"]*(?:skhema-tochek-pest-kontrolya|akt-deratizatsii-i-dezinsektsii)/"[^>]*>.*?</a></li>'
                     r'|<a href="[^"]*(?:skhema-tochek-pest-kontrolya|akt-deratizatsii-i-dezinsektsii)/"[^>]*>(?:(?!</a>).)*</a>')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git_show(rev, path):
    return subprocess.run(['git', 'show', f'{rev}:{path}'], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout


def live_menu_module():
    """apply_menu в редакции MENU_REV (меню, как на сайте) с текущим списком «Материалов»."""
    src = git_show(MENU_REV, 'tools/menu/apply_menu.py')
    mod = types.ModuleType('apply_menu_live')
    mod.__file__ = str(ROOT / 'tools' / 'menu' / 'apply_menu.py')
    exec(compile(src, mod.__file__, 'exec'), mod.__dict__)
    mod.MATERIALS = list(apply_menu.MATERIALS)
    assert [s for s, _ in mod.MATERIALS if s in SLUGS] == SLUGS
    return mod


M = live_menu_module()


def menu_blocks(s):
    return [re.search(p, s, re.S).group(0) for p in MENU_RES]


def with_menu(s, blocks):
    for p, b in zip(MENU_RES, blocks):
        s = apply_menu.sub1(p, b, s)
    return s


def built_menu(rel, s):
    html = rel.replace('index.php', 'index.html')
    root, cur = next((r, c) for f, r, c in apply_menu.PAGES + apply_menu.LEGAL if f == html)
    cta = re.search(r'<nav class="mmenu"[^>]*>.*?(<a href="(?:\.\./)*#zayavka" class="btn btn-w btn-lg">.*?</a>)\s*</nav>',
                    s, re.S).group(1)
    return [M.typo(x) for x in M.build(root, cur, cta)]


TOK = re.compile(r'[^\s<>]+|\s+|<|>')


def changes(base, target):
    la, lb = base.splitlines(keepends=True), target.splitlines(keepends=True)
    oa = [0]
    for x in la:
        oa.append(oa[-1] + len(x))
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, la, lb, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        ra, rb = ''.join(la[i1:i2]), ''.join(lb[j1:j2])
        a, b = TOK.findall(ra), TOK.findall(rb)
        pa = [0]
        for x in a:
            pa.append(pa[-1] + len(x))
        for op2, x1, x2, y1, y2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if op2 != 'equal':
                out.append((oa[i1] + pa[x1], oa[i1] + pa[x2], ''.join(b[y1:y2])))
    return out


def text_edits(base, target, live, rel):
    target = with_menu(target, menu_blocks(base))
    for bs, be, txt in changes(base, target)[:1]:
        for k in range(8, 4000, 16):
            old = base[max(0, bs - k):be + k]
            new = base[max(0, bs - k):bs] + txt + base[be:be + k]
            if base.count(old) == 1 and live.count(old) == 1:
                return [(old, new)]
        raise SystemExit(f'{rel}: правка не найдена на странице сайта: {base[bs - 60:be + 60]!r} → {txt[:120]!r}')
    return []


def apply_text(rel, live, pair):
    base, target = pair
    s, n = live, 0
    for _ in range(100):
        ed = text_edits(base, target, s, rel)
        if not ed:
            return s, n
        old, new = ed[0]
        assert s.count(old) == 1 and base.count(old) == 1, rel
        s, base, n = s.replace(old, new), base.replace(old, new), n + 1
    raise SystemExit(rel + ': слишком много правок')


def article(s, marker):
    i = s.index(marker)
    a = s.rindex('      <article', 0, i)
    b = s.index('</article>\n', i) + len('</article>\n')
    return a, b


def hub(s):
    repo = (ROOT / 'materialy' / 'index.html').read_text(encoding='utf-8')
    # карточка 07: «Готовится» → схема точек
    assert s.count('Материал 07 · Готовится') == 1 and SKH not in s and AKT not in s
    a, b = article(s, 'Материал 07 · Готовится')
    ra, rb = article(repo, '"p-sec-num">Материал 07<')
    s = s[:a] + repo[ra:rb] + s[b:]
    # карточка акта — «Материал 12» перед оценкой эффективности, она становится «Материалом 13»
    a, b = article(s, '"p-sec-num">Материал 12<')
    ef = s[a:b]
    ra, rb = article(repo, '"p-sec-num">Материал 13<')
    assert ef.replace('Материал 12', 'Материал 13') == repo[ra:rb], 'хаб: карточка оценки эффективности не как в репозитории'
    ka, kb = article(repo, '"p-sec-num">Материал 12<')
    s = s[:a] + repo[ka:kb] + ef.replace('Материал 12', 'Материал 13') + s[b:]
    # разметка: описание и ItemList — как в репозитории
    LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
    lj, rj = json.loads(LD.search(s).group(1)), json.loads(LD.search(repo).group(1))
    lj2 = json.loads(json.dumps(lj))
    for k in ('description',):
        lj2['@graph'][1][k] = rj['@graph'][1][k]
    lj2['@graph'][1]['mainEntity'] = rj['@graph'][1]['mainEntity']
    assert lj2 == rj, 'хаб: разметка JSON-LD отличается не только списком материалов'
    s = s.replace(LD.search(s).group(0), LD.search(repo).group(0), 1)
    items = rj['@graph'][1]['mainEntity']['itemListElement']
    assert [i['position'] for i in items] == list(range(1, len(items) + 1))
    return s


def main_page(s):
    dist = (ROOT / 'dist' / 'timeweb' / 'index.php').read_text(encoding='utf-8')
    a = '.doc:hover:before{opacity:1}'
    css = dist[dist.index(a) + len(a):dist.index('@property --ang', dist.index(a))]
    assert css.startswith('.doc{display:flex') and len(css) < 1200, 'стили плиток в сборке'
    # стили легли правкой текста из fd7a780 (index.html содержит встроенный <style>) — сверка со сборкой
    assert s.count(a + css + '@property --ang') == 1, 'главная: стили плиток не как в сборке'
    assert s.count(APP_V_OLD) == 1
    return s.replace(APP_V_OLD, APP_V_NEW)


def counters_same(rel, live, new):
    c1, c2 = CBLOCK.findall(live), CBLOCK.findall(new)
    if rel in NO_COUNTERS:
        assert c1 == c2 == [], rel + ': на странице документа появились счётчики'
        return
    assert len(c1) == 4 and c1 == c2, rel + ': блок счётчиков изменён или не найден'
    lb, pb = live.encode('utf-8'), new.encode('utf-8')
    for k in (b'113675622', b'uiscom', b'radist'):
        assert lb.count(k) == pb.count(k), f'{rel}: {k!r}: на сайте {lb.count(k)}, в пакете {pb.count(k)}'


def links_ok(files, live_dir, extra_ok):
    have = {str(p.relative_to(live_dir)) for p in live_dir.rglob('*') if p.is_file()} | set(files) | extra_ok
    pages = {p[:-len('index.php')] for p in have if p.endswith('index.php')}
    bad, assets = [], set()
    for rel, data in files.items():
        if not rel.endswith('index.php'):
            continue
        base = rel[:-len('index.php')]
        for h in re.findall(r'href="([^"#?]*)', data.decode('utf-8')):
            if not h or re.match(r'^(https?:|mailto:|tel:|//|data:)', h):
                continue
            p = posixpath.normpath(posixpath.join('/' + base, h)).lstrip('/')
            if h.endswith('/') or h in ('.', '..'):
                p = '' if p in ('', '.') else p + '/'
                if p not in pages:
                    bad.append((rel, h))
            elif p not in have:
                assets.add(p)
    return bad, assets


def search_index(files):
    import build_index  # noqa: E402
    live_pages = [r for r in build_prod.PAGES if (r[:-len('index.html')] + 'index.php') in files]
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        for rel in live_pages:
            d = td / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            d.write_bytes(files[rel[:-len('index.html')] + 'index.php'])
        out = td / 'search-index.json'
        saved = build_prod.PAGES[:]
        build_index.build_prod.PAGES[:] = live_pages
        argv = sys.argv
        try:
            sys.argv = ['build_index.py', '--pages', str(td), '--out', str(out)]
            buf = io.StringIO()
            with redirect_stdout(buf):
                build_index.main()
            print(buf.getvalue().strip())
        finally:
            sys.argv = argv
            build_index.build_prod.PAGES[:] = saved
        data = out.read_bytes()
    j = json.loads(data)
    urls = {p[1] for p in j['p']}
    for u in urls:
        assert u.strip('/') not in NOT_LIVE - set(SLUGS), 'в поиске страница, которой нет на сайте: ' + u
    for s in SLUGS:
        assert any(s in u for u in urls), 'новой страницы нет в поиске: ' + s
    return data, j['v']


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    live_dir, pkg = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    pages = sorted(str(p.relative_to(live_dir)) for p in live_dir.rglob('index.php'))
    want = sorted(f.replace('index.html', 'index.php') for f, _, _ in apply_menu.PAGES + apply_menu.LEGAL
                  if f[:-len('/index.html')] not in NOT_LIVE)
    assert pages == want, f'набор страниц на сайте и в меню разный: {sorted(set(pages) ^ set(want))}'
    edits = {h.replace('index.html', 'index.php'): (git_show(r1, h), git_show(r2, h)) for r1, r2, hs in REVS for h in hs}
    files, touched = {}, []
    for rel in pages:
        live = (live_dir / rel).read_text(encoding='utf-8')
        for sl in SLUGS:
            assert sl + '/' not in live, rel + ': на сайте уже есть ссылка на ' + sl
        # меню: построение как на сайте без новых пунктов должно дать меню сайта
        saved = M.MATERIALS
        M.MATERIALS = [x for x in saved if x[0] not in SLUGS]
        try:
            assert menu_blocks(live) == built_menu(rel, live), rel + ': меню сайта не совпадает с построением ' + MENU_REV
        finally:
            M.MATERIALS = saved
        new, n = live, 0
        if rel in edits:
            new, n = apply_text(rel, live, edits[rel])
        if rel == HUB:
            new, n = hub(new), n + 1
        if rel == MAIN:
            new, n = main_page(new), n + 1
        before_menu = new
        new = with_menu(new, built_menu(rel, new))
        added = len(NEWLINK.findall(new)) - len(NEWLINK.findall(before_menu))
        assert NEWLINK.sub('', new) == NEWLINK.sub('', before_menu), rel + ': меню изменило страницу не только новыми пунктами'
        assert added == 6, f'{rel}: новых ссылок в меню {added}'
        counters_same(rel, live, new)
        files[rel] = new.encode('utf-8')
        if n:
            touched.append(rel)
        print(f'{rel}: правок в тексте {n}, ссылок в меню +6; счётчики прежние')
    assert sorted(touched) == sorted(set(edits) | {HUB, MAIN}), f'правки в тексте легли не на все страницы: {touched}'

    # новые страницы — из сборки для Timeweb; меню — то же построение, что у страниц сайта
    tpl = (live_dir / 'materialy/zhurnal-pest-kontrolya/index.php').read_text(encoding='utf-8')
    for rel in NEW:
        page = (ROOT / 'dist' / 'timeweb' / rel).read_text(encoding='utf-8')
        page = with_menu(page, built_menu(rel, page))
        assert CBLOCK.findall(page) == CBLOCK.findall(tpl), rel + ': счётчики не как на сайте'
        assert 'noindex' not in page and page.count("ym(113675622, 'init'") == 1
        files[rel] = page.encode('utf-8')

    # главная: app.min.js и style.css — на сайте версии до правки fd7a780, заменяются версиями из репозитория
    for f in ('app.min.js', 'style.css'):
        assert sha((live_dir / f).read_bytes()) == sha(git_show('fd7a780~1', f).encode('utf-8')), f + ' на сайте изменён'
        files[f] = (ROOT / f).read_bytes()

    # картинки и файлы, на которые ссылаются страницы пакета и которых нет на сайте
    imgref = lambda s: set(re.findall(r'(?:\.\./)*(img/[A-Za-z0-9_./-]+\.(?:webp|jpg|png|svg))', s))
    have = set()
    for rel in pages:
        have |= imgref((live_dir / rel).read_text(encoding='utf-8'))
    need = set()
    for rel in NEW + touched:
        need |= imgref(files[rel].decode('utf-8'))
    new_files = sorted(need - have) + [SKH + '/obrazets-skhemy-tochek-pest-kontrolya.pdf']
    for f in new_files:
        assert (ROOT / f).exists(), 'нет файла ' + f
        files[f] = (ROOT / f).read_bytes()
    print('новые файлы:', ' '.join(new_files))

    known = set((ROOT / 'tools' / 'deploy' / 'live-assets-2026-11-11-akt.txt').read_text().split()) \
        if (ROOT / 'tools' / 'deploy' / 'live-assets-2026-11-11-akt.txt').exists() else set()
    bad, assets = links_ok(files, live_dir, known)
    assert not bad, f'ссылки на страницы, которых нет на сайте: {bad[:10]}'
    (pkg.parent / 'ASSETS-CHECK.txt').write_text('\n'.join(sorted(assets)) + '\n', encoding='utf-8')
    print('файлы по ссылкам, которые надо проверить на сайте:', len(assets))

    # sitemap: + два адреса после журнала, lastmod правленых страниц
    sm = (live_dir / 'sitemap.xml').read_text(encoding='utf-8')
    after = SITE + 'materialy/zhurnal-pest-kontrolya/'
    m = re.search(r'\n  <url>\s*<loc>' + re.escape(after) + r'</loc>.*?</url>', sm, re.S)
    assert m, 'в sitemap нет журнала'
    add = ''
    for sl in SLUGS:
        assert SITE + sl not in sm
        blk = m.group(0).replace(after, SITE + sl + '/')
        add += re.sub(r'<lastmod>[^<]*</lastmod>', f'<lastmod>{TODAY}</lastmod>', blk)
    sm = sm[:m.end()] + add + sm[m.end():]
    for rel in touched:
        u = SITE + rel[:-len('index.php')]
        pat = re.compile(r'(<loc>' + re.escape(u) + r'</loc>\s*<lastmod>)([0-9-]+)(</lastmod>)')
        assert len(pat.findall(sm)) == 1, rel
        sm = pat.sub(r'\g<1>' + TODAY + r'\g<3>', sm)
    files['sitemap.xml'] = sm.encode('utf-8')

    data, v = search_index(files)
    live_v = json.loads((live_dir / 'search-index.json').read_text(encoding='utf-8'))['v']
    assert v == live_v, f'версия индекса поиска {v}, на сайте {live_v}'
    files['search-index.json'] = data

    # порядок: файлы → app.min.js, style.css → новые страницы → страницы сайта → поиск → sitemap
    order = new_files + ['app.min.js', 'style.css'] + NEW + [p for p in pages if p != MAIN] + [MAIN,
                                                                                               'search-index.json',
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
