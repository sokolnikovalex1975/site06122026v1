#!/usr/bin/env python3
"""Выкладка 11.11.2026: страница «Пест-контроль бизнес-центров, торговых центров и промышленных предприятий»
(/biznes-tsentry-torgovye-tsentry-predpriyatiya/) и ссылки на неё (решение владельца 11.11.2026: «делай что нужно
и выкладывай на timeweb. Не забудь сделать перелинковку на эту страницу на необходимых страницах и с этой страницы»).

    python3 tools/deploy/prepare-2026-11-11-bctc.py <файлы сайта> <папка pkg> [MANIFEST]   — пакет для Timeweb
    python3 tools/deploy/prepare-2026-11-11-bctc.py --preview                             — те же правки в превью (корень репозитория)

<файлы сайта> — все страницы сайта (index.php по списку tools/menu/apply_menu.PAGES + LEGAL; 11.11.2026 их 36),
sitemap.xml и search-index.json, как их отдаёт сайт по HTTPS перед выкладкой.
Страницы на сайте правятся точечно, остальное остаётся как на сайте:
  * на всех страницах — пункт «Бизнес-центры, ТЦ и предприятия» в шапке (Отрасли), мобильном меню и подвале
    (tools/menu/apply_menu.py; без трёх новых ссылок страница должна совпасть с прежней байт в байт);
  * ссылки на новую страницу в тексте (PATCHES ниже, каждая замена — ровно один раз): главная, дератизация (плитка
    «Промпредприятия, БЦ и ТЦ» — ещё и новое фото вместо пищевого цеха), дезинсекция, дезинфекция, вентиляция,
    магазины, рестораны, склады, разработка ППК, «Пест-менеджмент или разовая обработка»;
  * новая страница собирается из страницы складов, снятой с сайта (tools/bctc/build_page.py), — блок счётчиков
    (Метрика 113675622, UIS/CoMagic, Radist) переходит в неё без изменений;
  * sitemap.xml — с сайта + адрес новой страницы, lastmod 2026-11-11 у страниц с правками в тексте;
  * search-index.json — из страниц пакета (tools/search/build_index.py).
Новые файлы: фото страницы (img/bctc-*.webp, bctc-og.jpg), подвальный комар (img/p-mosquito.webp), фото плитки
(img/ind-bc-tc*.webp) и всё, на что ссылается новая страница и чего нет на страницах сайта.
Проверки: блок счётчиков на каждой странице ровно один, байт в байт как на сайте и как server/counters.html.
"""
import hashlib
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'menu'))
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
sys.path.insert(0, str(ROOT / 'tools' / 'bctc'))
import apply_menu  # noqa: E402
import build_prod  # noqa: E402
import build_page  # noqa: E402

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
SLUG = build_page.SLUG
NEW = SLUG + '/index.php'
LABEL = 'Бизнес-центры, ТЦ и\u00a0предприятия'
TODAY = '2026-11-11'
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
NO_COUNTERS = {'privacy/index.php', 'soglasie/index.php'}
A16 = build_page.A16
P = '../' + SLUG + '/'
# ссылка в тексте карточки .d-obj: поверх кликабельной карточки, с подчёркиванием (как ссылки в карточках вентиляции)
OBJ_CSS = ('<style id="bctc-links">.d-obj p a{position:relative;z-index:2;color:var(--t1);text-decoration:underline;'
           'text-decoration-color:var(--acc);text-underline-offset:3px}.d-obj p a:hover{color:var(--acc)}</style>\n</head>')
XLIST_CSS = ('.ind-xlist{color:var(--t2);margin:24px 0 0;line-height:1.7;font-size:clamp(14px,.9vw,16px)}'
             '.ind-xlist a{color:var(--t1);border-bottom:1px solid var(--line2);transition:color .25s,border-color .25s}'
             '.ind-xlist a:hover,.ind-xlist a:focus-visible{color:var(--acc);border-color:var(--acc)}')
HOME_CSS_END = '.ind .ind-more:focus-visible,.ind .ind-link:focus-visible{outline:none}</style>'

# страница → [(было, стало)]; «~» — неразрывный пробел (на сайте он записан символом U+00A0)
PATCHES = {
    'index.php': [
        (HOME_CSS_END, HOME_CSS_END.replace('</style>', XLIST_CSS + '</style>')),
        ('Подробнее об обслуживании гостиниц' + A16 + '</a></div></article>\n    </div>\n',
         'Подробнее об обслуживании гостиниц' + A16 + '</a></div></article>\n    </div>\n'
         '    <p class="ind-xlist" data-fade>Офисные и&nbsp;торговые здания, непищевые производства: '
         '<a href="' + SLUG + '/"><span class="nw">пест-контроль</span> <span class="nw">бизнес-центров,</span> '
         'торговых центров и&nbsp;промышленных предприятий</a>.</p>\n'),
    ],
    'deratizatsiya/index.php': [
        ('<span class="tag">Паркинги и~подвалы</span></div>',
         '<span class="tag">Паркинги и~подвалы</span></div><a class="ind-more" href="' + P + '">'
         'Пест-контроль бизнес-центров, ТЦ и~предприятий' + A16 + '</a>'),
    ],
    'dezinsektsiya/index.php': [
        ('</head>', OBJ_CSS),
        ('а также обслуживание бизнес-центров и УК: офисные кухни',
         'а также обслуживание <a href="' + P + '">бизнес-центров и&nbsp;УК</a>: офисные кухни'),
    ],
    'dezinfektsiya/index.php': [
        ('кондиционирование и~контроль легионелл.</p>',
         'кондиционирование и~контроль легионелл. <a href="' + P + '"><span class="nw">Пест-контроль</span> '
         '<span class="nw">бизнес-центров</span></a></p>'),
    ],
    'ochistka-dezinfektsiya-ventilyatsii/index.php': [
        ('и~анализ на~легионеллы 2~раза в~год.</p></article>',
         'и~анализ на~легионеллы 2~раза в~год. <a href="' + P + '"><span class="nw">Пест-контроль</span> '
         '<span class="nw">бизнес-центров</span></a></p></article>'),
        ('<a href="../magaziny-i-torgovye-seti/"><span class="nw">Пест-контроль</span> магазинов</a></p></article>',
         '<a href="../magaziny-i-torgovye-seti/"><span class="nw">Пест-контроль</span> магазинов</a> и&nbsp;'
         '<a href="' + P + '">торговых центров</a></p></article>'),
    ],
    'magaziny-i-torgovye-seti/index.php': [
        ('</head>', OBJ_CSS),
        ('<p>Общие зоны ТЦ обычно обслуживает подрядчик управляющей компании, помещение магазина',
         '<p><a href="' + P + '">Общие зоны ТЦ</a> обычно обслуживает подрядчик управляющей компании, помещение магазина'),
        ('Мы стыкуем свои схемы и&nbsp;графики с&nbsp;подрядчиком ТЦ.</p>',
         'Мы стыкуем свои схемы и&nbsp;графики с&nbsp;подрядчиком ТЦ. Для управляющих компаний&nbsp;— '
         '<a href="' + P + '"><span class="nw">пест-контроль</span> торговых центров</a>.</p>'),
    ],
    'restorany-i-kafe/index.php': [
        ('согласуем с~управляющей компанией центра.</p></div></article>',
         'согласуем с~управляющей компанией центра.</p><a class="ind-more" href="' + P + '">'
         'Пест-контроль торговых центров' + A16 + '</a></div></article>'),
    ],
    'sklady-i-logistika/index.php': [
        ('      <li><a href="../pishchevoe-proizvodstvo/">Пест-контроль на~пищевом производстве →</a></li>\n',
         '      <li><a href="../pishchevoe-proizvodstvo/">Пест-контроль на~пищевом производстве →</a></li>\n'
         '      <li><a href="' + P + '">Пест-контроль бизнес-центров, ТЦ и~предприятий →</a></li>\n'),
    ],
    'razrabotka-ppk/index.php': [
        ('<a href="../farmatsevticheskie-proizvodstva/">фармацевтические производства</a>.</p>',
         '<a href="../farmatsevticheskie-proizvodstva/">фармацевтические производства</a>, '
         '<a href="' + P + '">бизнес-центры, ТЦ и&nbsp;предприятия</a>.</p>'),
    ],
    'materialy/pest-menedzhment-ili-razovaya-obrabotka/index.php': [
        ('<a href="../../gostinitsy/">гостиницы</a>.</p>',
         '<a href="../../gostinitsy/">гостиницы</a>, '
         '<a href="../' + P + '">бизнес-центры, ТЦ и&nbsp;предприятия</a>.</p>'),
    ],
}
OLD_ALT = 'alt="Производственное предприятие и инженерные зоны"'
NEW_ALT = 'alt="Технический этаж и паркинг бизнес-центра: кабельные трассы, щитовая и станция контроля грызунов у стены"'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def tile_photo(s):
    """Плитка «Промпредприятия, БЦ и ТЦ» на дератизации: фото паркинга и техэтажа вместо пищевого цеха."""
    if 'ind-bc-tc.webp' in s:
        return s
    assert s.count(OLD_ALT) == 1, 'плитка «Промпредприятия, БЦ и ТЦ» не найдена'
    a = s.find(OLD_ALT)
    i, j = s.rfind('<img', 0, a), s.find('>', a) + 1
    tag = s[i:j]
    assert tag.count('ind-ready') == 3, tag
    return s[:i] + tag.replace('ind-ready', 'ind-bc-tc').replace(OLD_ALT, NEW_ALT) + s[j:]


def content(rel, s):
    """Ссылки на новую страницу в тексте; повторный запуск ничего не меняет."""
    key = rel.replace('index.html', 'index.php')
    if key == 'deratizatsiya/index.php':
        s = tile_photo(s)
    n = 0
    for old, new in PATCHES.get(key, []):
        old, new = old.replace('~', '\u00a0'), new.replace('~', '\u00a0')
        if old == '</head>':
            if 'id="bctc-links"' in s:
                continue
        elif new in s:
            continue
        assert s.count(old) == 1, f'{rel}: «{old[:60]}» — вхождений {s.count(old)}'
        s = s.replace(old, new)
        n += 1
    return s, n


def menu(rel, s):
    """Пункт меню в шапке, мобильном меню и подвале; остальное — без изменений."""
    html = rel.replace('index.php', 'index.html')
    root, cur = next((r, c) for f, r, c in apply_menu.PAGES + apply_menu.LEGAL if f == html)
    # только три блока меню; блок поиска в <head> остаётся там, где он стоит на странице
    # (apply_menu.apply_page на главной переставил бы его ниже по <head>)
    cta = re.search(r'<nav class="mmenu"[^>]*>.*?(<a href="(?:\.\./)*#zayavka" class="btn btn-w btn-lg">.*?</a>)\s*</nav>',
                    s, re.S).group(1)
    nav, mm, cols = (apply_menu.typo(x) for x in apply_menu.build(root, cur, cta))
    new = apply_menu.sub1(r'<nav class="nav" aria-label="Основное меню">.*?</nav>', nav, s)
    new = apply_menu.sub1(r'<nav class="mmenu" id="mmenu" aria-label="Мобильное меню">.*?</nav>', mm, new)
    new = apply_menu.sub1(r'<div><h4>(?:Объекты|Отрасли|Услуги)</h4>.*?(?=\n\s*<div><h4>Контакты</h4>)', cols, new)
    link = f'<a href="{root}{SLUG}/">{LABEL}'
    back = new
    for v in (f'<li>{link}</a></li>', f'{link}{apply_menu.ARR}</a>', f'{link}</a>'):
        back = back.replace(v, '')
    added = new.count(root + SLUG + '/"') - s.count(root + SLUG + '/"')
    if back != s:
        # страница уже с пунктом меню (повторный запуск) — тогда она не должна измениться
        assert new == s, f'{rel}: меню изменило страницу не только новым пунктом'
        added = 0
    else:
        assert added == 3, f'{rel}: новых ссылок в меню {added}'
    return new, added


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


def preview():
    """Те же правки в превью: страницы index.html в корне репозитория (счётчиков в них нет)."""
    for html, _, _ in apply_menu.PAGES + apply_menu.LEGAL:
        f = ROOT / html
        if html.startswith(SLUG):
            continue
        s = f.read_text(encoding='utf-8')
        new, n = content(html, s)
        new, m = menu(html, new)
        if new != s:
            f.write_text(new, encoding='utf-8')
        print(f'{html}: ссылок в тексте +{n}, в меню +{m}')
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'bctc' / 'build_page.py')], check=True)


def main():
    if sys.argv[1:] == ['--preview']:
        return preview()
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    live_dir, pkg = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    pages = sorted(str(p.relative_to(live_dir)) for p in live_dir.rglob('index.php'))
    want = sorted(f.replace('index.html', 'index.php') for f, _, _ in apply_menu.PAGES + apply_menu.LEGAL
                  if not f.startswith(SLUG))
    assert pages == want, 'набор страниц на сайте и в меню разный'
    cblock = (ROOT / 'server' / 'counters.html').read_text(encoding='utf-8')
    files, touched = {}, []
    for rel in pages:
        live = (live_dir / rel).read_text(encoding='utf-8')
        assert SLUG not in live, rel + ': на сайте уже есть ссылка на новую страницу'
        new, n = content(rel, live)
        new, m = menu(rel, new)
        assert m == 3
        counters_same(rel, live, new, cblock)
        assert new.count(SLUG + '/"') == 3 + sum(x[1].count(SLUG + '/"') for x in PATCHES.get(rel, [])), rel
        files[rel] = new.encode('utf-8')
        if n:
            touched.append(rel)
        print(f'{rel}: ссылок в тексте +{n}, в меню +3; счётчики прежние')
    assert sorted(touched) == sorted(PATCHES), 'правки в тексте легли не на все страницы'

    # новая страница — из страницы складов, снятой с сайта (до правок): счётчики переходят как есть
    tpl = (live_dir / 'sklady-i-logistika/index.php').read_text(encoding='utf-8')
    page = build_page.build(tpl)
    c = COUNTERS.findall(page)
    assert len(c) == 1 and c[0] in cblock and c == COUNTERS.findall(tpl), 'счётчики новой страницы'
    assert 'noindex' not in page and page.count("ym(113675622, 'init'") == 1
    assert page.count('aria-current="page"') >= 3
    files[NEW] = page.encode('utf-8')

    # картинки: всё, на что ссылается новая страница и правленые страницы и чего нет на страницах сайта
    ref = lambda s: set(re.findall(r'(?:\.\./)*(img/[A-Za-z0-9_./-]+\.(?:webp|jpg|png|svg))', s))
    have = set()
    for rel in pages:
        have |= ref((live_dir / rel).read_text(encoding='utf-8'))
    need = ref(page)
    for rel in touched:
        need |= ref(files[rel].decode('utf-8'))
    new_files = sorted(need - have)
    for f in new_files:
        assert (ROOT / f).exists(), 'нет файла ' + f
        files[f] = (ROOT / f).read_bytes()
    print('новые файлы:', ' '.join(new_files))

    # sitemap: с сайта + новая страница (после гостиниц) + lastmod правленых страниц
    sm = (live_dir / 'sitemap.xml').read_text(encoding='utf-8')
    assert SITE + SLUG not in sm
    m = re.search(r'\n  <url>\s*<loc>' + re.escape(SITE + 'gostinitsy/') + r'</loc>.*?</url>', sm, re.S)
    assert m, 'в sitemap нет гостиниц'
    blk = m.group(0).replace(SITE + 'gostinitsy/', SITE + SLUG + '/')
    blk = re.sub(r'<lastmod>[^<]*</lastmod>', f'<lastmod>{TODAY}</lastmod>', blk)
    sm = sm[:m.end()] + blk + sm[m.end():]
    for rel in touched:
        u = SITE + rel[:-len('index.php')]
        pat = re.compile(r'(<loc>' + re.escape(u) + r'</loc>\s*<lastmod>)([0-9-]+)(</lastmod>)')
        assert len(pat.findall(sm)) == 1, rel
        sm = pat.sub(r'\g<1>' + TODAY + r'\g<3>', sm)
    files['sitemap.xml'] = sm.encode('utf-8')

    # поиск по сайту — из страниц пакета
    assert SLUG + '/index.html' in build_prod.PAGES
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        for rel in build_prod.PAGES:
            d = td / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            d.write_bytes(files[rel[:-len('index.html')] + 'index.php'])
        out = td / 'search-index.json'
        r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'search' / 'build_index.py'), '--pages', str(td),
                            '--out', str(out)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        print(r.stdout.strip())
        files['search-index.json'] = out.read_bytes()

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
