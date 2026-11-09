#!/usr/bin/env python3
"""Выкладка 09.11.2026: «Документы для Роспотребнадзора» — короче вводный абзац и кнопки под фото на телефоне и планшете.

    git worktree add --detach /tmp/wt-base 179aff8 && (cd /tmp/wt-base && python3 tools/site/build_prod.py)
    python3 tools/site/build_prod.py
    python3 tools/deploy/prepare-2026-11-09-dokv1.py [--nb] <папка с файлами сайта> /tmp/wt-base/dist/timeweb <папка пакета> [MANIFEST]

<папка с файлами сайта> — файлы, как их отдаёт сайт по HTTPS перед выкладкой:
    normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.php и sitemap.xml
    (с --nb ещё normativnaya-baza/index.php и normativnaya-baza/proverochnye-listy/index.php — хаб и проверочные листы
    с тем же первым экраном: заголовок → фото → кнопки → абзац).

Почему не файл из сборки целиком: страница на сайте новее main в своих частях — поиск по сайту (лупа в шапке, стили
srch-st, скрипт srch-js), карточка образца акта, подсветка строки перечня из поиска; эти правки выложены из другой задачи
и в main их нет. Поэтому в файл с сайта переносятся только изменения сборки 179aff8 → текущая (5f00de2 «вариант 1» и
следующий коммит): `git merge-file` (база — сборка 179aff8, «наши» — файл с сайта, «их» — текущая сборка).
Единственный конфликт — конец первого блока стилей рядом с JSON-LD: блок стилей берётся с сайта, строка JSON-LD —
из новой сборки (в ней только dateModified 2026-11-09).

Проверки:
  * изменения «сайт → пакет» в точности те же, что «сборка 179aff8 → текущая сборка» (8 мест: стили первого экрана,
    вводный абзац, dateModified);
  * блок счётчиков (Метрика 113675622, UIS/CoMagic, Radist) — ровно один, байт в байт как на сайте и в server/counters.html;
  * поиск и образец акта на месте (столько же вхождений srch и dk-aktcard);
  * sitemap.xml — меняется только lastmod страницы документов: 2026-11-08 → 2026-11-09.
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
DOK = 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.php'
NB = ['normativnaya-baza/index.php', 'normativnaya-baza/proverochnye-listy/index.php']
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
COUNTERS = re.compile(rb'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
LD = '<script type="application/ld+json">'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def hunks(x, y):
    sm = difflib.SequenceMatcher(None, x, y, autojunk=False)
    return [('\n'.join(x[i1:i2]), '\n'.join(y[j1:j2])) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != 'equal']


def merge_page(live, base, new):
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        for n, b in (('live', live), ('base', base), ('new', new)):
            (td / n).write_text(b, encoding='utf-8')
        r = subprocess.run(['git', 'merge-file', '-p', '-L', 'live', '-L', 'base', '-L', 'new',
                            str(td / 'live'), str(td / 'base'), str(td / 'new')], capture_output=True)
        assert r.returncode in (0, 1), 'git merge-file: ' + r.stderr.decode()
        m = r.stdout.decode('utf-8').split('\n')
    marks = [i for i, l in enumerate(m) if l.startswith('<<<<<<< live') or l == '=======' or l.startswith('>>>>>>> new')]
    if marks:
        assert len(marks) == 3, f'ожидался один конфликт, найдено меток: {len(marks)}'
        lv, nw = m[marks[0] + 1:marks[1]], m[marks[1] + 1:marks[2]]
        li = [i for i, l in enumerate(lv) if l.startswith(LD)]
        ni = [i for i, l in enumerate(nw) if l.startswith(LD)]
        assert len(li) == 1 and len(ni) == 1, 'конфликт не у JSON-LD — разберите вручную'
        assert nw[:ni[0]] == ['}</style>'] and nw[ni[0] + 1:] == [], 'в конфликте со стороны сборки что-то кроме JSON-LD'
        lv[li[0]] = nw[ni[0]]
        m = m[:marks[0]] + lv + m[marks[2] + 1:]
    return '\n'.join(m)


def main():
    args = sys.argv[1:]
    with_nb = '--nb' in args
    args = [a for a in args if a != '--nb']
    if len(args) not in (3, 4):
        raise SystemExit(__doc__)
    live_dir, base_dir, out = map(pathlib.Path, args[:3])
    pages = [DOK] + (NB if with_nb else [])
    files, report = {}, []
    for page in pages:
        live = (live_dir / page).read_text(encoding='utf-8')
        base = (base_dir / page).read_text(encoding='utf-8')
        new = (DIST / page).read_text(encoding='utf-8')
        pkg = merge_page(live, base, new)
        h1, h2 = hunks(base.split('\n'), new.split('\n')), hunks(live.split('\n'), pkg.split('\n'))
        assert h1 == h2, page + ': изменения «сайт → пакет» не совпадают с «сборка 179aff8 → текущая»'
        lb, pb = live.encode('utf-8'), pkg.encode('utf-8')
        c1, c2 = COUNTERS.findall(lb), COUNTERS.findall(pb)
        assert len(c1) == 1 and c1 == c2, page + ': блок счётчиков изменён или не найден'
        assert c1[0] in (ROOT / 'server' / 'counters.html').read_bytes(), page + ': счётчики на сайте не как в server/counters.html'
        for k in (b'113675622', b'srch', b'dk-aktcard', b'comagic', b'radist'):
            assert lb.count(k) == pb.count(k), f'{page}: {k!r} на сайте {lb.count(k)}, в пакете {pb.count(k)}'
        files[page] = pb
        report.append(f'{page}: {len(h1)} мест')
    sm = (live_dir / 'sitemap.xml').read_text(encoding='utf-8')
    for page in pages:
        loc = SITE + page[:-len('index.php')]
        rx = re.compile(r'(<loc>' + re.escape(loc) + r'</loc>\s*<lastmod>)2026-11-08(</lastmod>)')
        assert len(rx.findall(sm)) == 1, f'sitemap: запись {loc} не найдена или дата не 2026-11-08'
        sm = rx.sub(r'\g<1>2026-11-09\g<2>', sm, count=1)
    files['sitemap.xml'] = sm.encode('utf-8')
    for f, b in files.items():
        d = out / f
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_bytes(b)
    lines = ''.join(f'{sha(files[f])}  {f}\n' for f in sorted(files))
    if len(args) == 4:
        if pathlib.Path(args[3]).read_text(encoding='utf-8') != lines:
            raise SystemExit('пакет не совпадает с MANIFEST')
        print('MANIFEST совпадает')
    else:
        (out.parent / 'MANIFEST.sha256').write_text(lines, encoding='utf-8')
    exp = ''.join(f'{sha((live_dir / f).read_bytes())}  {f}\n' for f in sorted(files))
    (out.parent / 'EXPECTED_BEFORE.txt').write_text(exp, encoding='utf-8')
    print('; '.join(report) + f' (как в сборке); sitemap: {len(pages)} дат(ы); счётчики прежние; поиск и образец акта на месте')


if __name__ == '__main__':
    main()
