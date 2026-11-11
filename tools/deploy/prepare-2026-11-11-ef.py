#!/usr/bin/env python3
"""Выкладка 11.11.2026: страница «Оценка эффективности дератизации и дезинсекции»
(/normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/), пункт меню и ссылки на неё.
Решение владельца 11.11.2026: «Цена контрольного визита 3000. и выкладывай на timeweb. Найди место для этой страницы
в меню, в верхнем и нижнем — Подумай о ссылке на эту страницу с каких страниц сайта ещё можно сделать и добавь куда нужно».

    python3 tools/deploy/prepare-2026-11-11-ef.py <файлы сайта> <папка pkg> [MANIFEST]

<файлы сайта> — все страницы сайта (index.php по списку tools/menu/apply_menu.PAGES + LEGAL без ещё не выложенных),
sitemap.xml и search-index.json, как их отдаёт сайт по HTTPS перед выкладкой.
Страницы на сайте правятся точечно, остальное остаётся как на сайте:
  * на всех страницах — пункт «Оценка эффективности дератизации и дезинсекции» в «Материалах» шапки, мобильного меню
    и подвала (после «Документов для Роспотребнадзора»; без трёх новых ссылок страница совпадает с прежней байт в байт);
  * ссылки на новую страницу в тексте — те же правки, что в превью (коммиты 22942c1 и 0fca92a): замены вычисляются
    из разницы версий страницы в репозитории (до и после правки) и ложатся на страницу сайта, только если исходный
    фрагмент найден на ней ровно один раз; хаб «Материалы» — отдельно (на сайте нет карточек акта и схемы точек:
    они пока только в превью), новая карточка на сайте — «Материал 12»;
  * новая страница — из сборки для Timeweb (tools/site/build_prod.py): тот же блок счётчиков, что на сайте;
  * sitemap.xml — с сайта + адрес новой страницы, lastmod 2026-11-11 у страниц с правками в тексте;
  * search-index.json — из страниц пакета (tools/search/build_index.py; страницы, которых нет на сайте, пропускаются).
Проверки: блок счётчиков на каждой странице ровно один, байт в байт как на сайте и как server/counters.html;
все внутренние ссылки пакета ведут на страницы сайта или файлы пакета.
"""
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
from contextlib import redirect_stdout

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'menu'))
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
sys.path.insert(0, str(ROOT / 'tools' / 'search'))
import apply_menu  # noqa: E402
import build_prod  # noqa: E402

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
SLUG = 'normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii'
NEW = SLUG + '/index.php'
LABEL = 'Оценка эффективности дератизации и\u00a0дезинсекции'
TODAY = '2026-11-11'
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
NO_COUNTERS = {'privacy/index.php', 'soglasie/index.php'}
# страницы превью, которых ещё нет на сайте (11.11.2026)
NOT_LIVE = {SLUG, 'materialy/akt-deratizatsii-i-dezinsektsii', 'materialy/skhema-tochek-pest-kontrolya',
            'dezinsektsiya/restorany-i-kafe', 'deratizatsiya/restorany-i-kafe'}
# правки текста в превью: (версия до, версия после, страницы)
REVS = [
    ('f7e3960', 'd1f3cd3', ['normativnaya-baza/index.html', 'normativnaya-baza/proverochnye-listy/index.html',
                            'sanitarnyy-audit/index.html', 'dezinsektsiya/index.html', 'deratizatsiya/index.html',
                            'materialy/zhurnal-pest-kontrolya/index.html']),
    ('fd7a780', '0fca92a', ['restorany-i-kafe/index.html', 'gostinitsy/index.html',
                            'deratizatsiya-i-dezinsektsiya/index.html', 'dogovor-deratizatsiya-dezinsektsiya/index.html',
                            'materialy/programma-pest-kontrolya/index.html',
                            'materialy/pest-menedzhment-ili-razovaya-obrabotka/index.html',
                            'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.html',
                            'sklady-i-logistika/index.html']),
]
HUB = 'materialy/index.php'
NB = '\u00a0'
HUB_CARD = '''      <article class="p-sec p-sec-wide">
        <div>
          <div class="p-sec-top"><span class="p-sec-num">Материал 12</span><span class="p-sec-who">СанПиН 3.3686-21 · МР 3.5.3.0374-25</span></div>
          <h3><a href="../normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/" style="color:var(--t1)">Оценка эффективности дератизации и&nbsp;дезинсекции: сроки и&nbsp;критерии</a></h3>
          <p>Когда проверять результат обработки, какие показатели сравнивают до и после, что записать в журнал и акт и кто проводит оценку: своими силами, на контрольном визите или при проверке подрядчика.</p>
          <div class="d-btns" style="margin-top:20px"><a href="../normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/" class="btn btn-o btn-lg" data-magnet><span class="btn-t">Читать материал</span></a></div>
        </div>
      </article>
'''
HUB_LAST = ('<a href="./kontrol-raboty-sterilizatorov/" class="btn btn-o btn-lg" data-magnet><span class="btn-t">Читать материал</span></a></div>\n'
            '        </div>\n      </article>\n')
HUB_LD = [
    ('как контролируют работу стерилизаторов.", "isPartOf"',
     'как контролируют работу стерилизаторов, как оценивают эффективность дератизации и дезинсекции.", "isPartOf"'),
    ('"name": "Контроль работы стерилизаторов: методы, периодичность, журнал"}]}',
     '"name": "Контроль работы стерилизаторов: методы, периодичность, журнал"}, {"@type": "ListItem", "position": 11, '
     '"url": "' + SITE + SLUG + '/", "name": "Оценка эффективности дератизации и дезинсекции: сроки и критерии"}]}'),
]
MENU_RES = [r'<nav class="nav" aria-label="Основное меню">.*?</nav>',
            r'<nav class="mmenu" id="mmenu" aria-label="Мобильное меню">.*?</nav>',
            r'<div><h4>(?:Объекты|Отрасли|Услуги)</h4>.*?(?=\n\s*<div><h4>Контакты</h4>)']


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git_show(rev, path):
    return subprocess.run(['git', 'show', f'{rev}:{path}'], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout


def menu_blocks(s):
    return [re.search(p, s, re.S).group(0) for p in MENU_RES]


def with_menu(s, blocks):
    for p, b in zip(MENU_RES, blocks):
        s = apply_menu.sub1(p, b, s)
    return s


TOK = re.compile(r'[^\s<>]+|\s+|<|>')


def changes(base, target):
    """Изменения base → target: (начало, конец в base, новый текст); строки, затем слова внутри изменённых строк."""
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
    """Первая правка base → target (без меню) как (было, стало); «было» встречается на странице сайта ровно один раз."""
    target = with_menu(target, menu_blocks(base))
    for bs, be, txt in changes(base, target)[:1]:
        for k in range(8, 4000, 16):
            old = base[max(0, bs - k):be + k]
            new = base[max(0, bs - k):bs] + txt + base[be:be + k]
            if base.count(old) == 1 and live.count(old) == 1:
                return [(old, new)]
        raise SystemExit(f'{rel}: правка не найдена на странице сайта: {base[bs - 60:be + 60]!r} → {txt[:120]!r}')
    return []


def plan():
    """Страница сайта (index.php) → список замен в тексте."""
    edits = {}
    for r1, r2, pages in REVS:
        for html in pages:
            edits[html.replace('index.html', 'index.php')] = (git_show(r1, html), git_show(r2, html))
    return edits


def apply_text(rel, live, pair):
    """Правки по одной: после каждой и страница сайта, и версия «до» получают её, разница считается заново
    (соседние правки с общим контекстом не мешают друг другу)."""
    base, target = pair
    s = live
    for _ in range(100):
        ed = text_edits(base, target, s, rel)
        if not ed:
            return s
        old, new = ed[0]
        assert s.count(old) == 1 and base.count(old) == 1, rel
        s, base = s.replace(old, new), base.replace(old, new)
    raise SystemExit(rel + ': слишком много правок')


def hub(s):
    assert s.count(HUB_LAST) == 1 and 'Материал 12' not in s, 'хаб «Материалы»: последняя карточка не найдена'
    s = s.replace(HUB_LAST, HUB_LAST + HUB_CARD)
    for old, new in HUB_LD:
        assert s.count(old) == 1, 'хаб «Материалы»: разметка ItemList ' + old[:40]
        s = s.replace(old, new)
    j = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S).group(1))
    items = j['@graph'][1]['mainEntity']['itemListElement']
    assert [i['position'] for i in items] == list(range(1, 12)), 'хаб: позиции ItemList'
    return s


def menu(rel, s):
    """Пункт меню в шапке, мобильном меню и подвале; остальное — без изменений."""
    html = rel.replace('index.php', 'index.html')
    root, cur = next((r, c) for f, r, c in apply_menu.PAGES + apply_menu.LEGAL if f == html)
    cta = re.search(r'<nav class="mmenu"[^>]*>.*?(<a href="(?:\.\./)*#zayavka" class="btn btn-w btn-lg">.*?</a>)\s*</nav>',
                    s, re.S).group(1)
    nav, mm, cols = (apply_menu.typo(x) for x in apply_menu.build(root, cur, cta))
    new = with_menu(s, [nav, mm, cols])
    link = f'<a href="{root}{SLUG}/">{LABEL}'
    back = new
    for v in (f'<li>{link}</a></li>', f'{link}{apply_menu.ARR}</a>', f'{link}</a>'):
        back = back.replace(v, '')
    added = new.count(root + SLUG + '/"') - s.count(root + SLUG + '/"')
    assert back == s, f'{rel}: меню изменило страницу не только новым пунктом'
    assert added == 3, f'{rel}: новых ссылок в меню {added}'
    return new


def counters_same(rel, live, new, cblock):
    c1, c2 = COUNTERS.findall(live), COUNTERS.findall(new)
    if rel in NO_COUNTERS:
        assert c1 == c2 == [], rel + ': на странице документа появились счётчики'
        return
    assert len(c1) == 1 and c1 == c2, rel + ': блок счётчиков изменён или не найден'
    assert c1[0] in cblock, rel + ': блок счётчиков не как server/counters.html'
    lb, pb = live.encode('utf-8'), new.encode('utf-8')
    for k in (b'113675622', b'comagic', b'uiscom', b'radist'):
        assert lb.count(k) == pb.count(k), f'{rel}: {k!r}: на сайте {lb.count(k)}, в пакете {pb.count(k)}'


def links_ok(files, live_dir):
    """Внутренние ссылки страниц пакета ведут на страницы сайта или файлы пакета."""
    have = {str(p.relative_to(live_dir)) for p in live_dir.rglob('*') if p.is_file()} | set(files)
    pages = {p[:-len('index.php')] for p in have if p.endswith('index.php')}
    bad = []
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
    return bad


def search_index(files):
    import build_index  # noqa: E402
    live_pages = [r for r in build_prod.PAGES if r[:-len('index.html')].rstrip('/') not in NOT_LIVE or r == SLUG + '/index.html']
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
        assert u.rstrip('/') not in NOT_LIVE - {SLUG}, 'в поиске страница, которой нет на сайте: ' + u
    assert any(SLUG in u for u in urls), 'новой страницы нет в поиске'
    return data, j['v']


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    live_dir, pkg = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    pages = sorted(str(p.relative_to(live_dir)) for p in live_dir.rglob('index.php'))
    want = sorted(f.replace('index.html', 'index.php') for f, _, _ in apply_menu.PAGES + apply_menu.LEGAL
                  if f[:-len('/index.html')] not in NOT_LIVE)
    assert pages == want, f'набор страниц на сайте и в меню разный: {sorted(set(pages) ^ set(want))}'
    cblock = (ROOT / 'server' / 'counters.html').read_text(encoding='utf-8')
    edits = plan()
    files, touched = {}, []
    for rel in pages:
        live = (live_dir / rel).read_text(encoding='utf-8')
        assert SLUG not in live, rel + ': на сайте уже есть ссылка на новую страницу'
        new = live
        if rel in edits:
            new = apply_text(rel, live, edits[rel])
        if rel == HUB:
            new = hub(new)
        n = new.count(SLUG + '/"')
        new = menu(rel, new)
        counters_same(rel, live, new, cblock)
        files[rel] = new.encode('utf-8')
        if n:
            touched.append(rel)
        print(f'{rel}: ссылок в тексте +{n}, в меню +3; счётчики прежние')
    assert sorted(touched) == sorted(set(edits) | {HUB}), f'правки в тексте легли не на все страницы: {touched}'

    # новая страница — из сборки для Timeweb; меню — то же, что получили страницы сайта
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'site' / 'build_prod.py')], cwd=ROOT, check=True,
                   capture_output=True)
    page = (ROOT / 'dist' / 'timeweb' / NEW).read_text(encoding='utf-8')
    tpl = (live_dir / 'normativnaya-baza/proverochnye-listy/index.php').read_text(encoding='utf-8')
    c = COUNTERS.findall(page)
    assert len(c) == 1 and c[0] in cblock and c == COUNTERS.findall(tpl), 'счётчики новой страницы'
    assert 'noindex' not in page and page.count("ym(113675622, 'init'") == 1
    # меню новой страницы — то же построение, что легло на страницы сайта (apply_menu.build), со своим текущим пунктом
    root, cur = next((r, c) for f, r, c in apply_menu.PAGES if f == SLUG + '/index.html')
    cta = re.search(r'<nav class="mmenu"[^>]*>.*?(<a href="(?:\.\./)*#zayavka" class="btn btn-w btn-lg">.*?</a>)\s*</nav>',
                    page, re.S).group(1)
    assert menu_blocks(page) == [apply_menu.typo(x) for x in apply_menu.build(root, cur, cta)], 'меню новой страницы'
    files[NEW] = page.encode('utf-8')

    # картинки: всё, на что ссылаются страницы пакета и чего нет на страницах сайта
    imgref = lambda s: set(re.findall(r'(?:\.\./)*(img/[A-Za-z0-9_./-]+\.(?:webp|jpg|png|svg))', s))
    have = set()
    for rel in pages:
        have |= imgref((live_dir / rel).read_text(encoding='utf-8'))
    need = imgref(page)
    for rel in touched:
        need |= imgref(files[rel].decode('utf-8'))
    new_files = sorted(need - have)
    for f in new_files:
        assert (ROOT / f).exists(), 'нет файла ' + f
        files[f] = (ROOT / f).read_bytes()
    print('новые файлы:', ' '.join(new_files))

    bad = links_ok(files, live_dir)
    assert not bad, f'ссылки на страницы, которых нет на сайте: {bad[:10]}'

    # sitemap: с сайта + новая страница (после «Документов для Роспотребнадзора») + lastmod правленых страниц
    sm = (live_dir / 'sitemap.xml').read_text(encoding='utf-8')
    assert SITE + SLUG not in sm
    after = SITE + 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/'
    m = re.search(r'\n  <url>\s*<loc>' + re.escape(after) + r'</loc>.*?</url>', sm, re.S)
    assert m, 'в sitemap нет «Документов для Роспотребнадзора»'
    blk = m.group(0).replace(after, SITE + SLUG + '/')
    blk = re.sub(r'<lastmod>[^<]*</lastmod>', f'<lastmod>{TODAY}</lastmod>', blk)
    sm = sm[:m.end()] + blk + sm[m.end():]
    for rel in touched:
        u = SITE + rel[:-len('index.php')]
        pat = re.compile(r'(<loc>' + re.escape(u) + r'</loc>\s*<lastmod>)([0-9-]+)(</lastmod>)')
        assert len(pat.findall(sm)) == 1, rel
        sm = pat.sub(r'\g<1>' + TODAY + r'\g<3>', sm)
    files['sitemap.xml'] = sm.encode('utf-8')

    # поиск по сайту — из страниц пакета; формат индекса — как у поиска на сайте
    data, v = search_index(files)
    live_v = json.loads((live_dir / 'search-index.json').read_text(encoding='utf-8'))['v']
    assert v == live_v, f'версия индекса поиска {v}, на сайте {live_v}'
    files['search-index.json'] = data

    # порядок: картинки → новая страница → страницы со ссылками на неё → поиск → sitemap
    order = new_files + [NEW] + pages + ['search-index.json', 'sitemap.xml']
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
