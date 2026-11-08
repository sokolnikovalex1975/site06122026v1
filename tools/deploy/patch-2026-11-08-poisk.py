#!/usr/bin/env python3
"""Выкладка 08.11.2026: поиск по сайту, образец акта на странице «Документы для Роспотребнадзора», мобильные правки.

Пакет собирается из файлов, как их отдаёт сайт перед выкладкой (на сайте есть правки, которых нет в GitHub, и наоборот —
см. CHANGES.md), поэтому в файлы с сайта переносятся только отличия этой задачи.

    python3 tools/deploy/patch-2026-11-08-poisk.py <файлы с сайта> <dist до правки> <dist после правки> <папка пакета> [MANIFEST]

<файлы с сайта> — 24 страницы index.php (список PAGES), legal.css и sitemap.xml, как их отдаёт сайт по HTTPS;
<dist до правки> — сборка tools/site/build_prod.py (dist/timeweb) из main без этой задачи, <dist после правки> — из ветки
с задачей.

Что делает:
  * на всех 24 страницах — лупа поиска в шапке и блок поиска в <head> (стили кнопки и раскладки шапки, загрузчик) тем же
    кодом, что в сборке (tools/menu/apply_menu.search_ui), прямо в файле с сайта;
  * остальные отличия «до → после» — по строкам: каждый изменённый блок расширяется соседними строками, пока фрагмент не
    станет единственным и в сборке, и в файле с сайта, и заменяется тем же блоком из сборки «после». Это карточка
    «Образец акта» и ссылки «Образец акта» в разделе «Акты», подсветка строки перечня и цели akt_obrazets / akt_shablon
    на странице документов; ссылка «Образец акта» в таблице проверочных листов; штрафы в одну колонку и перенос
    «фармацевтическое» на санитарном аудите до 400 px; версия legal.css на страницах политики и согласия;
  * проверочные листы: перенос строки «№ 18 от 20.01.2022 и № 808 от 24.12.2021» (LIVE_FIXES) — в main это уже
    исправлено, на сайте страница была шире экрана на 320–360 px;
  * legal.css (заголовок документов до 400 px) — из сборки «после», если на сайте он как в сборке «до»;
    sitemap.xml — новые даты изменения по строкам (как страницы);
  * новые файлы (search.min.js, образец и бланк акта PDF, превью акта) — из сборки «после», search-index.json — из
    страниц пакета.
Проверки:
  * те же замены превращают сборку «до» (с блоком поиска) ровно в сборку «после»;
  * файл с сайта после правки отличается от сборки «после» теми же строками, чем отличался от сборки «до»
    (правки других задач на сайте сохраняются, не выложенные правки из GitHub в пакет не попадают);
  * блок счётчиков (Метрика 113675622, UIS/CoMagic, Radist) на каждой странице байт в байт прежний;
  * search-index.json собирается из страниц пакета (тем же tools/search/build_index.py): на сайте ищется то, что на нём
    есть; записи, которые отличаются от индекса сборки (страницы сайта не как в GitHub), печатаются.
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

DK = 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/'
PAGES = [
    'index.php', 'dezinfektsiya/index.php', 'deratizatsiya/index.php', 'dezinsektsiya/index.php',
    'dogovor-deratizatsiya-dezinsektsiya/index.php', 'sanitarnyy-audit/index.php', 'razrabotka-ppk/index.php',
    'ochistka-dezinfektsiya-ventilyatsii/index.php', 'pishchevoe-proizvodstvo/index.php',
    'restorany-i-kafe/index.php', 'magaziny-i-torgovye-seti/index.php', 'gostinitsy/index.php',
    'farmatsevticheskie-proizvodstva/index.php', 'sklady-i-logistika/index.php', 'materialy/index.php',
    'materialy/programma-pest-kontrolya/index.php', 'materialy/zhurnal-pest-kontrolya/index.php',
    'materialy/pest-menedzhment-ili-razovaya-obrabotka/index.php',
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/index.php', 'normativnaya-baza/index.php',
    'normativnaya-baza/proverochnye-listy/index.php', DK + 'index.php', 'privacy/index.php', 'soglasie/index.php',
]
LEGAL = {'privacy/index.php', 'soglasie/index.php'}
NEW_FILES = [
    'search.min.js', 'search-index.json',
    DK + 'obrazets-akta-dezinsektsii-i-deratizatsii.pdf', DK + 'blank-akta-dezinsektsii-i-deratizatsii.pdf',
    'img/akt-obrazets-p1-360.webp', 'img/akt-obrazets-p1-720.webp',
]
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
# Правки, которые уже есть в main (в сборке «до»), но не на сайте, и без которых страница шире экрана телефона:
# на проверочных листах цепочка неразрывных пробелов «№ 18 от 20.01.2022 и № 808 от 24.12.2021» (карточка и FAQ)
# не переносилась — прокрутка вбок 49 px на 320 px, 28 px на 340, 8 px на 360. Переносится в файл с сайта до остальных
# замен, только если на сайте фрагмент прежний, а в сборке «до» — исправленный (столько же раз).
NB = '\u00a0'
LIVE_FIXES = {
    'normativnaya-baza/proverochnye-listy/index.php': [
        (f'№{NB}18{NB}от{NB}20.01.2022{NB}и{NB}№{NB}808{NB}от{NB}24.12.2021',
         f'№{NB}18 от{NB}20.01.2022 и{NB}№{NB}808 от{NB}24.12.2021', 2),
    ],
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
    if rel in LEGAL:
        assert not ca, rel + ': на странице документа появились счётчики'
        return 0
    assert len(ca) == 1, rel + ': блок счётчиков не один'
    c = ca[0]
    for need in ("ym(113675622, 'init'", 'mc.yandex.ru/metrika/tag.js',
                 'app.uiscom.ru/static/cs.min.js?k=ICWycQx6m3NSBe3WlCeDAdAKMTmNhMHC', 'track.radist.me/tracker.min.js'):
        assert need in c, f'{rel}: в блоке счётчиков нет {need}'
    return 1


def live_fix(rel, live, prev):
    for old, fixed, n in LIVE_FIXES.get(rel, []):
        assert live.count(old) == n and live.count(fixed) == 0, rel + ': на сайте фрагмент уже не прежний'
        assert prev.count(fixed) == n and prev.count(old) == 0, rel + ': в сборке «до» нет исправления'
        live = live.replace(old, fixed)
        print(f'{rel}: перенос в строке «{fixed[:22]}…» как в main — {n} раза')
    return live


def patch_page(rel, live, prev, new):
    root = root_of(rel)
    live0 = live
    live = live_fix(rel, live, prev)
    live1, prev1 = apply_menu.search_ui(live, root), apply_menu.search_ui(prev, root)
    reps = pairs(prev1, new, live1)
    assert apply(prev1, reps, rel + ' (сборка)') == new, rel + ': замены не дают сборку «после»'
    out = apply(live1, reps, rel + ' (сайт)')
    assert sig(new, out) == sig(prev1, live1), rel + ': лишние отличия'
    assert out.count('class="srch-btn"') == 1 and out.count('<style id="srch-st">') == 1, rel + ': поиск'
    n = check_counters(rel, live0, out)
    return out, len(reps), n


def pkg_index(pkg, new_dist):
    """search-index.json для сайта — из страниц пакета (то есть из того, что будет на сайте), тем же build_index.py.
    От индекса сборки он может отличаться там, где страницы сайта отличаются от GitHub (не выложенные правки main);
    такие записи печатаются."""
    tmp = pathlib.Path('/tmp/poisk-index-check')
    if tmp.exists():
        shutil.rmtree(tmp)
    for rel in PAGES:
        f = tmp / rel.replace('index.php', 'index.html')
        f.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(pkg / rel, f)
    out = tmp / 'search-index.json'
    r = subprocess.run([sys.executable, str(ROOT / 'tools' / 'search' / 'build_index.py'), '--pages', str(tmp),
                        '--out', str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    a = json.loads(out.read_text(encoding='utf-8'))
    b = json.loads((new_dist / 'search-index.json').read_text(encoding='utf-8'))
    assert a['v'] == b['v'] and a['p'] == b['p'], 'версия или список страниц индекса не как в сборке'
    ai, bi = {json.dumps(x, ensure_ascii=False) for x in a['i']}, {json.dumps(x, ensure_ascii=False) for x in b['i']}
    diff = sorted(ai - bi)
    for x in diff:
        print('  в индексе сайта иначе, чем в сборке:', x[:220])
    assert len(a['i']) == len(b['i']) and len(diff) <= 10, 'индекс из страниц пакета слишком отличается от сборки'
    return out, len(a['i']), len(diff)


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
    # legal.css — на сайте та же, что в сборке «до»
    assert rd(site, 'legal.css') == rd(dprev, 'legal.css'), 'legal.css на сайте не как в сборке «до»'
    out['legal.css'] = rd(dnew, 'legal.css')
    # sitemap.xml — даты изменения по строкам (на сайте адрес страницы документов записан одной строкой — так и остаётся)
    sm_live, sm_prev, sm_new = rd(site, 'sitemap.xml'), rd(dprev, 'sitemap.xml'), rd(dnew, 'sitemap.xml')
    reps = pairs(sm_prev, sm_new, sm_live)
    assert apply(sm_prev, reps, 'sitemap') == sm_new
    sm = apply(sm_live, reps, 'sitemap (сайт)')
    assert sig(sm_new, sm) == sig(sm_prev, sm_live) and sm.count('<loc>') == sm_live.count('<loc>')
    out['sitemap.xml'] = sm
    for rel, text in out.items():
        f = dst / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(text.encode('utf-8'))
    for rel in NEW_FILES:
        f = dst / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(dnew / rel, f)
    idx, n, nd = pkg_index(dst, dnew)
    shutil.copyfile(idx, dst / 'search-index.json')
    print(f'search-index.json — из страниц пакета: {n} записей, отличаются от сборки {nd}')
    # порядок выкладки: новые файлы → legal.css → страницы → главная → sitemap.xml
    rels = NEW_FILES + ['legal.css'] + [r for r in PAGES if r != 'index.php'] + ['index.php', 'sitemap.xml']
    lines = [f'{hashlib.sha256((dst / r).read_bytes()).hexdigest()}  {r}' for r in rels]
    print('\n'.join(lines))
    if manifest:
        want = manifest.read_text(encoding='utf-8').strip().splitlines()
        assert sorted(want) == sorted(lines), 'результат не совпадает с MANIFEST'
        print('== совпадает с', manifest.name)


if __name__ == '__main__':
    main()
