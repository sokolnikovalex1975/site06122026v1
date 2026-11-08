#!/usr/bin/env python3
"""Выкладка 08.11.2026: поиск по сайту и страница «Документы для Роспотребнадзора» — пакет из файлов, как их отдаёт сайт.

Использование:
  python3 tools/deploy/patch-2026-11-08-dk.py <файлы с сайта> <dist до правки> <dist после правки> <папка пакета> [MANIFEST]

<файлы с сайта> — 23 страницы index.php (список PAGES), sitemap.xml и legal.css, как их отдаёт сайт по HTTPS перед выкладкой
(или как они лежат в копии tools/deploy/backup/before-dk_2026-11-08_ftp.zip); <dist до правки> — сборка
tools/site/build_prod.py (dist/timeweb) из main без этой задачи (d10c458), <dist после правки> — из ветки с задачей.

Что делает:
  * на всех 23 страницах — лупа поиска в шапке и блок поиска в <head> (стили кнопки и раскладки шапки, загрузчик) тем же
    кодом, что в сборке (tools/menu/apply_menu.search_ui), прямо в файле с сайта;
  * остальные отличия «до → после» (пункт «Документы для Роспотребнадзора» в «Материалах» шапки и мобильного меню,
    ссылка в подвале вместо «Документы для проверок», карточки на хабе и в «Материалах», ссылки на перечень на
    отраслевых страницах, «Смотрите также» на проверочных листах, мобильные правки санитарного аудита и листов,
    стили документов политики и согласия) — по строкам: каждый изменённый блок расширяется соседними строками, пока
    фрагмент не станет единственным и в сборке, и в файле с сайта, и заменяется тем же блоком из сборки «после»;
  * sitemap.xml — новый адрес страницы документов (lastmod 2026-11-08), прочие строки не меняются;
  * новые файлы (страница, три PDF, картинки, search.min.js, search-index.json) — из сборки «после».
Проверки:
  * те же замены превращают сборку «до» (с блоком поиска) ровно в сборку «после»;
  * файл с сайта после правки отличается от сборки «после» теми же строками, чем отличался от сборки «до»
    (не выложенные правки других задач в пакет не попадают);
  * блок счётчиков (Метрика 113675622, UIS/CoMagic, Radist) на каждой странице байт в байт прежний; на новой странице —
    тот же блок, что на остальных;
  * шапка, мобильное меню и подвал новой страницы — как на проверочных листах (та же глубина) после правки;
  * индекс поиска, собранный из файлов пакета, совпадает с search-index.json сборки.
"""
import difflib
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'menu'))
import apply_menu  # noqa: E402  тот же блок поиска, что в сборке

SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
PAGES = [
    'index.php', 'dezinfektsiya/index.php', 'deratizatsiya/index.php', 'dezinsektsiya/index.php',
    'dogovor-deratizatsiya-dezinsektsiya/index.php', 'sanitarnyy-audit/index.php',
    'ochistka-dezinfektsiya-ventilyatsii/index.php', 'razrabotka-ppk/index.php', 'pishchevoe-proizvodstvo/index.php',
    'restorany-i-kafe/index.php', 'magaziny-i-torgovye-seti/index.php', 'gostinitsy/index.php',
    'farmatsevticheskie-proizvodstva/index.php', 'sklady-i-logistika/index.php', 'materialy/index.php',
    'materialy/programma-pest-kontrolya/index.php', 'materialy/zhurnal-pest-kontrolya/index.php',
    'materialy/pest-menedzhment-ili-razovaya-obrabotka/index.php',
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/index.php', 'normativnaya-baza/index.php',
    'normativnaya-baza/proverochnye-listy/index.php', 'privacy/index.php', 'soglasie/index.php',
]
LEGAL = {'privacy/index.php', 'soglasie/index.php'}
DK = 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/'
NEW_PAGE = DK + 'index.php'
NEW_FILES = [
    'search.min.js', 'search-index.json',
    DK + 'obrazets-akta-dezinsektsii-i-deratizatsii.pdf', DK + 'blank-akta-dezinsektsii-i-deratizatsii.pdf',
    DK + 'cheklist-dokumentov-dlya-rospotrebnadzora.pdf',
    'img/dk-hero.webp', 'img/dk-hero-1440.webp', 'img/dk-hero-mob.webp', 'img/dk-hero-mob-760.webp', 'img/dk-og.jpg',
    'img/akt-obrazets-p1-360.webp', 'img/akt-obrazets-p1-720.webp',
    'img/akt-obrazets-p1-top-480.webp', 'img/akt-obrazets-p1-top-720.webp',
    'img/cheklist-p1-top-480.webp', 'img/cheklist-p1-top-720.webp',
]
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
MENU = {  # шапка, мобильное меню, колонки подвала
    'nav': re.compile(r'<nav class="nav" aria-label="Основное меню">.*?</nav>', re.S),
    'mm': re.compile(r'<nav class="mmenu" id="mmenu" aria-label="Мобильное меню">.*?</nav>', re.S),
    'ft': re.compile(r'<div><h4>Услуги</h4>.*?(?=\n\s*<div><h4>Контакты</h4>)', re.S),
}


def root_of(rel):
    return '../' * rel.count('/')


def pairs(prev, new, live):
    """Замены по строкам: каждый изменённый блок строк сборки «до» (с соседними строками для привязки, пока фрагмент
    не станет единственным и в сборке, и в файле с сайта) → тот же блок из сборки «после». Близкие блоки сливаются."""
    A, B = prev.splitlines(keepends=True), new.splitlines(keepends=True)
    blocks = [(i1, i2, j1, j2) for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes()
              if op != 'equal']
    merged = []
    for blk in blocks:
        if merged and blk[0] - merged[-1][1] <= 3:
            merged[-1] = (merged[-1][0], blk[1], merged[-1][2], blk[3])
        else:
            merged.append(blk)
    out = []
    for i1, i2, j1, j2 in merged:
        for ctx in range(0, 12):
            a, b = max(0, i1 - ctx), min(len(A), i2 + ctx)
            old = ''.join(A[a:b])
            if old and prev.count(old) == 1 and live.count(old) == 1:
                break
        else:
            raise SystemExit(f'нет однозначного фрагмента для строк {i1}–{i2}: {"".join(A[i1:i2])[:200]!r}')
        out.append((old, ''.join(A[a:i1] + B[j1:j2] + A[i2:b])))
    return out


def apply(s, reps, what):
    """Все фрагменты ищутся в исходном тексте (каждый ровно один раз, без пересечений) и заменяются с конца."""
    spots = []
    for old, new in reps:
        assert s.count(old) == 1, (what, old[:100])
        i = s.index(old)
        spots.append((i, i + len(old), new))
    spots.sort()
    for (a1, b1, _), (a2, b2, _) in zip(spots, spots[1:]):
        assert b1 <= a2, (what, 'фрагменты пересекаются')
    for a1, b1, new in reversed(spots):
        s = s[:a1] + new + s[b1:]
    return s


def sig(x, y):
    """Отличия по строкам: (вид, строки x, строки y)."""
    X, Y = x.splitlines(keepends=True), y.splitlines(keepends=True)
    return [(op, tuple(X[i1:i2]), tuple(Y[j1:j2]))
            for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, X, Y, autojunk=False).get_opcodes() if op != 'equal']


def check_counters(rel, before, after):
    cb, ca = COUNTERS.findall(before), COUNTERS.findall(after)
    assert cb == ca, rel + ': блок счётчиков изменился'
    if rel not in LEGAL:
        assert len(ca) == 1, rel + ': блок счётчиков не один'
        c = ca[0]
        for need in ("ym(113675622, 'init'", 'mc.yandex.ru/metrika/tag.js',
                     'app.uiscom.ru/static/cs.min.js?k=ICWycQx6m3NSBe3WlCeDAdAKMTmNhMHC', 'track.radist.me/tracker.min.js'):
            assert need in c, f'{rel}: в блоке счётчиков нет {need}'
    return len(ca)


def patch_page(rel, live, prev, new):
    root = root_of(rel)
    live1, prev1 = apply_menu.search_ui(live, root), apply_menu.search_ui(prev, root)
    reps = pairs(prev1, new, live1)
    assert apply(prev1, reps, rel + ' (сборка)') == new, rel + ': замены не дают сборку «после»'
    out = apply(live1, reps, rel + ' (сайт)')
    assert sig(new, out) == sig(prev1, live1), rel + ': лишние отличия'
    assert out.count('class="srch-btn"') == 1 and out.count('<style id="srch-st">') == 1, rel + ': поиск'
    n = check_counters(rel, live, out)
    return out, len(reps), n


def menus(s):
    return {k: [m.group(0) for m in rx.finditer(s)] for k, rx in MENU.items()}


def check_new_page(page, listy):
    """Шапка, мобильное меню и подвал новой страницы — как на проверочных листах после правки (та же глубина)."""
    a, b = menus(page), menus(listy)
    for k in MENU:
        assert len(a[k]) == 1 and len(b[k]) == 1, k
        x = a[k][0].replace(' aria-current="page"', '').replace('href="./"', f'href="../../{DK}"')
        y = b[k][0].replace(' aria-current="page"', '').replace('href="./"', 'href="../../normativnaya-baza/proverochnye-listy/"')
        # активный раздел в шапке («Материалы») на обеих страницах один и тот же
        assert x == y, f'новая страница: блок {k} не как на сайте'
    assert page.count('aria-current="page"') >= 3


def check_index(pkg, new_dist):
    """Индекс из файлов пакета (страницы .php) = search-index.json сборки."""
    tmp = pathlib.Path('/tmp/dk-index-check')
    if tmp.exists():
        shutil.rmtree(tmp)
    for rel in PAGES + [NEW_PAGE]:
        f = tmp / rel.replace('index.php', 'index.html')
        f.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(pkg / rel, f)
    r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'search' / 'build_index.py'), '--pages', str(tmp),
                        '--out', str(tmp / 'search-index.json')], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    a = json.loads((tmp / 'search-index.json').read_text(encoding='utf-8'))
    b = json.loads((new_dist / 'search-index.json').read_text(encoding='utf-8'))
    assert a == b, 'индекс из файлов пакета отличается от индекса сборки'
    return len(a['i'])


def main():
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    site, dprev, dnew, dst = (pathlib.Path(x) for x in sys.argv[1:5])
    manifest = pathlib.Path(sys.argv[5]) if len(sys.argv) > 5 else None
    if dst.exists():
        shutil.rmtree(dst)
    rd = lambda d, rel: (d / rel).read_bytes().decode('utf-8')  # noqa: E731  байты как есть
    out = {}
    for rel in PAGES:
        out[rel], k, n = patch_page(rel, rd(site, rel), rd(dprev, rel), rd(dnew, rel))
        print(f'{rel}: замен {k}, блок счётчиков {n} — без изменений')
    # sitemap.xml: новый адрес
    sm_live, sm_prev, sm_new = rd(site, 'sitemap.xml'), rd(dprev, 'sitemap.xml'), rd(dnew, 'sitemap.xml')
    reps = pairs(sm_prev, sm_new, sm_live)
    assert apply(sm_prev, reps, 'sitemap') == sm_new
    sm = apply(sm_live, reps, 'sitemap (сайт)')
    sm, n = re.subn(r'(<loc>' + re.escape(SITE + DK) + r'</loc>\n    <lastmod>)[0-9-]+', r'\g<1>2026-11-08', sm)
    assert n == 1 and sm.count('<url>') == sm_live.count('<url>') + 1
    out['sitemap.xml'] = sm
    # legal.css — на сайте та же, что в сборке «до»
    assert rd(site, 'legal.css') == rd(dprev, 'legal.css'), 'legal.css на сайте не как в сборке «до»'
    out['legal.css'] = rd(dnew, 'legal.css')
    # новая страница — из сборки «после»
    page = rd(dnew, NEW_PAGE)
    check_counters(NEW_PAGE, page, page)
    assert COUNTERS.findall(page) == COUNTERS.findall(out['normativnaya-baza/proverochnye-listy/index.php'])
    assert 'noindex' not in page
    check_new_page(page, out['normativnaya-baza/proverochnye-listy/index.php'])
    out[NEW_PAGE] = page
    for rel, text in out.items():
        f = dst / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(text.encode('utf-8'))
    for rel in NEW_FILES:
        f = dst / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(dnew / rel, f)
    print('индекс поиска из файлов пакета совпадает со сборкой:', check_index(dst, dnew), 'записей')
    rels = NEW_FILES + [NEW_PAGE] + [r for r in PAGES if r != 'index.php'] + ['index.php', 'legal.css', 'sitemap.xml']
    lines = [f'{hashlib.sha256((dst / r).read_bytes()).hexdigest()}  {r}' for r in rels]
    print('\n'.join(lines))
    if manifest:
        want = manifest.read_text(encoding='utf-8').strip().splitlines()
        assert sorted(want) == sorted(lines), 'результат не совпадает с MANIFEST'
        print('== совпадает с', manifest.name)


if __name__ == '__main__':
    main()
