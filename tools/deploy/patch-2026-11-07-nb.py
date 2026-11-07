#!/usr/bin/env python3
"""Пакет выкладки раздела «Нормативная база» (07.11.2026): правка страниц, снятых с сайта.

    python3 tools/site/build_prod.py
    python3 tools/deploy/patch-2026-11-07-nb.py <папка со страницами с сайта> <папка pkg>

В папке с сайта — 20 страниц (<путь>/index.php, главная — index.php) и sitemap.xml, как их отдаёт сайт по HTTPS.
Для каждой страницы сравниваются файл с сайта и сборка dist/timeweb. В файл с сайта переносятся только правки раздела:
  * строки меню «Материалы» в шапке и мобильном меню и колонка «Материалы» в подвале (пункт «Нормативная база»,
    в подвале ещё «Проверочные листы 2026») — только вставки, из строки сайта ничего не удаляется;
  * /materialy/ — материалы 05 и 06, ссылки в CollectionPage;
  * /sanitarnyy-audit/ — ссылки на раздел в блоке «Нормативная база», стиль этих ссылок, фраза
    «Прежние приказы № 18 и № 808 утратили силу»;
  * /restorany-i-kafe/, /magaziny-i-torgovye-seti/, /gostinitsy/ — строка «Что спросит инспектор о вредителях».
Остальные отличия сборки от сайта (не выложенные правки других задач: role="group" у бегущей строки на гостиницах и аудите,
переносы строк в CSS дезинсекции, правки вентиляции) не переносятся — на этих местах остаётся текст сайта.

Проверки: на каждой странице блок счётчиков (от <script> с Метрикой 113675622 до конца файла: Метрика, UIS/CoMagic, Radist)
совпадает с сайтом байт в байт, число вхождений адресов счётчиков то же, PHP-вставок нет (на политике и согласии счётчиков
нет и не появляется, noindex как на сайте); новые страницы — тот же блок счётчиков,
без noindex, canonical на пестконтроль-центр.рф; sitemap.xml отличается от сайта только двумя новыми адресами.
"""
import difflib
import hashlib
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DIST = ROOT / 'dist' / 'timeweb'
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
PAGES = ['index.php', 'deratizatsiya', 'dezinfektsiya', 'dezinsektsiya', 'dogovor-deratizatsiya-dezinsektsiya',
         'farmatsevticheskie-proizvodstva', 'gostinitsy', 'magaziny-i-torgovye-seti', 'materialy',
         'materialy/pest-menedzhment-ili-razovaya-obrabotka', 'materialy/programma-pest-kontrolya',
         'materialy/programma-proizvodstvennogo-kontrolya-haccp', 'materialy/zhurnal-pest-kontrolya',
         'ochistka-dezinfektsiya-ventilyatsii', 'pishchevoe-proizvodstvo', 'privacy', 'restorany-i-kafe',
         'sanitarnyy-audit', 'sklady-i-logistika', 'soglasie']
NEW_PAGES = ['normativnaya-baza', 'normativnaya-baza/proverochnye-listy']
DOCS = {'privacy', 'soglasie'}
NEW_FILES = ['img/nb-og.jpg', 'img/pl-og.jpg']
# сколько отличий сборки от сайта должно остаться без переноса (чужие, ещё не выложенные правки)
FOREIGN = {'gostinitsy': 1, 'sanitarnyy-audit': 1, 'dezinsektsiya': None, 'ochistka-dezinfektsiya-ventilyatsii': None}
# сколько правок раздела ждём на странице (3 строки меню; None — проверяем вручную по выводу)
MINE = {'restorany-i-kafe': 4, 'magaziny-i-torgovye-seti': 4, 'gostinitsy': 4, 'materialy': 5, 'sanitarnyy-audit': None}
COUNTERS = ['113675622', 'mc.yandex.ru/metrika/tag.js',
            'app.uiscom.ru/static/cs.min.js?k=ICWycQx6m3NSBe3WlCeDAdAKMTmNhMHC', 'track.radist.me/tracker.min.js']


def rel(p):
    return p if p.endswith('.php') else p + '/index.php'


def counters_tail(s):
    # блок server/counters.html: от <script> с ym(113675622, 'init' до конца файла
    # (на страницах образцов ym(113675622, 'reachGoal' встречается раньше — в скрипте скачивания)
    i = s.find("ym(113675622, 'init'")
    assert i > 0, 'нет Метрики'
    return s[s.rfind('<script', 0, i):]


def only_inserts(a, b):
    cm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return all(o in ('equal', 'insert') for o, *_ in cm.get_opcodes())


def patch_page(page, live_s, build_s):
    live = live_s.splitlines(True)
    new = build_s.splitlines(True)
    out, mine, foreign = [], [], []
    sm = difflib.SequenceMatcher(None, live, new, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            out += live[i1:i2]
            continue
        L, N = ''.join(live[i1:i2]), ''.join(new[j1:j2])
        is_mine = ('normativnaya-baza/' in N or (page == 'sanitarnyy-audit' and ('№\u00a018\u00a0и\u00a0' in N
                   or '#normativnaya-baza .sub a' in N)))
        if is_mine:
            # правки раздела — вставки; единственная замена текста — фраза о приказах № 18 и № 808 на аудите
            if not only_inserts(L, N):
                assert page == 'sanitarnyy-audit' and '№\u00a018\u00a0и\u00a0' in N, (page, 'не только вставки', L[:120])
            out += new[j1:j2]
            mine.append((i1, i2, j1, j2, N.strip()[:90]))
        else:
            out += live[i1:i2]
            foreign.append((i1, i2, j1, j2, (N.strip() or L.strip())[:90]))
    return ''.join(out), mine, foreign


def main():
    src, dst = map(pathlib.Path, sys.argv[1:3])
    if dst.exists():
        shutil.rmtree(dst)
    tails = set()
    for page in PAGES:
        r = rel(page)
        live_b = (src / r).read_bytes()
        live_s = live_b.decode('utf-8')
        build_s = (DIST / r).read_text(encoding='utf-8')
        assert 'normativnaya-baza/' not in live_s, ('раздел уже есть на сайте', page)
        new_s, mine, foreign = patch_page(page, live_s, build_s)
        exp_f = FOREIGN.get(page, 0)
        if exp_f is not None:
            assert len(foreign) == exp_f, (page, 'чужих отличий', len(foreign), foreign)
        exp_m = MINE.get(page, 3)
        if exp_m is not None:
            assert len(mine) == exp_m, (page, 'правок раздела', len(mine), mine)
        assert new_s.count('<?') == live_s.count('<?') == 0, page
        assert new_s.count('noindex') == live_s.count('noindex'), page
        if page in DOCS:  # политика и согласие — документы, счётчиков на них нет и не было
            for c in COUNTERS:
                assert new_s.count(c) == live_s.count(c) == 0, (page, c)
        else:
            assert counters_tail(new_s) == counters_tail(live_s), (page, 'блок счётчиков изменился')
            for c in COUNTERS:
                assert new_s.count(c) == live_s.count(c) >= 1, (page, c)
            assert 'noindex' not in new_s, page
            tails.add(counters_tail(live_s))
        o = dst / r
        o.parent.mkdir(parents=True, exist_ok=True)
        o.write_bytes(new_s.encode('utf-8'))
        print(f'ok {r}: правок раздела {len(mine)}, без переноса {len(foreign)}, '
              f'{len(new_s.encode()) - len(live_b):+d} байт, счётчики как на сайте')
        for f in foreign:
            print(f'     оставлено как на сайте: строка {f[0] + 1}: {f[4]}')
    assert len(tails) == 1, 'блок счётчиков на страницах сайта разный'
    tail = tails.pop()
    for page in NEW_PAGES:
        r = page + '/index.php'
        s = (DIST / r).read_text(encoding='utf-8')
        assert counters_tail(s) == tail, (page, 'блок счётчиков не как на сайте')
        assert 'noindex' not in s and s.count('<?') == 0, page
        assert f'<link rel="canonical" href="{SITE}{page}/">' in s, page
        for c in COUNTERS:
            assert s.count(c) == tail.count(c) >= 1, (page, c)
        o = dst / r
        o.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(DIST / r, o)
        print(f'ok {r}: новая страница, блок счётчиков как на сайте')
    for f in NEW_FILES:
        o = dst / f
        o.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / f, o)
        print(f'ok {f}: {o.stat().st_size} байт')
    live_map = (src / 'sitemap.xml').read_text(encoding='utf-8')
    new_map = (ROOT / 'server' / 'sitemap.xml').read_text(encoding='utf-8')
    added = [l for l in difflib.unified_diff(live_map.splitlines(), new_map.splitlines(), lineterm='', n=0)
             if l[:1] in '+-' and not l.startswith(('+++', '---'))]
    assert all(l.startswith('+') for l in added) and len(added) == 10, added
    assert sum('normativnaya-baza' in l for l in added) == 2, added
    (dst / 'sitemap.xml').write_text(new_map, encoding='utf-8')
    print(f'ok sitemap.xml: +2 адреса, всего {new_map.count("<loc>")}')
    with open(dst.parent / ('MANIFEST-' + dst.name[4:] + '.sha256'), 'w') as m:
        for f in sorted(p for p in dst.rglob('*') if p.is_file()):
            m.write(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(dst)}\n')


if __name__ == '__main__':
    main()
