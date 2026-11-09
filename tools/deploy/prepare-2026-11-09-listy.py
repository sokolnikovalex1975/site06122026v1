#!/usr/bin/env python3
"""Выкладка 09.11.2026: «Проверочные листы» — короче вводный абзац (102 → 62 слова) и dateModified 2026-11-09.

    git worktree add --detach /tmp/wt-base2 8216c91 && (cd /tmp/wt-base2 && python3 tools/site/build_prod.py)
    python3 tools/site/build_prod.py
    python3 tools/deploy/prepare-2026-11-09-listy.py <папка с файлами сайта> /tmp/wt-base2/dist/timeweb <папка пакета> [MANIFEST]

<папка с файлами сайта> — normativnaya-baza/proverochnye-listy/index.php, как его отдаёт сайт по HTTPS перед выкладкой.

Страница на сайте отличается от main в своих частях (в main — невыложенная широкая карточка в «Разборах и образцах»
и другой порядок стиля m-crumbs), поэтому в файл с сайта переносятся только изменения сборки 8216c91 → 5b164c7
(абзац и dateModified) — `git merge-file` (база — сборка 8216c91, «наши» — файл с сайта, «их» — текущая сборка).
Единственный конфликт — строка JSON-LD рядом со стилем m-crumbs: строки берутся с сайта, JSON-LD — из новой сборки.
Проверки: изменения «сайт → пакет» те же, что «сборка 8216c91 → текущая»; блок счётчиков (Метрика 113675622, UIS/CoMagic,
Radist) — ровно один и байт в байт прежний, как в server/counters.html; поиск по сайту на месте. sitemap.xml не меняется:
lastmod листов на сайте уже 2026-11-09.
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
PAGE = 'normativnaya-baza/proverochnye-listy/index.php'
COUNTERS = re.compile(rb'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def hunks(x, y):
    sm = difflib.SequenceMatcher(None, x, y, autojunk=False)
    return [('\n'.join(x[i1:i2]), '\n'.join(y[j1:j2])) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != 'equal']


def main():
    if len(sys.argv) not in (4, 5):
        raise SystemExit(__doc__)
    live_dir, base_dir, out = map(pathlib.Path, sys.argv[1:4])
    live = (live_dir / PAGE).read_text(encoding='utf-8')
    base = (base_dir / PAGE).read_text(encoding='utf-8')
    new = (DIST / PAGE).read_text(encoding='utf-8')
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        for n, b in (('live', live), ('base', base), ('new', new)):
            (td / n).write_text(b, encoding='utf-8')
        r = subprocess.run(['git', 'merge-file', '-p', '-L', 'live', '-L', 'base', '-L', 'new',
                            str(td / 'live'), str(td / 'base'), str(td / 'new')], capture_output=True)
        assert r.returncode in (0, 1), 'git merge-file: ' + r.stderr.decode()
        m = r.stdout.decode('utf-8').split('\n')
    # единственный ожидаемый конфликт — строка JSON-LD (dateModified) рядом со стилем m-crumbs, который на сайте стоит
    # сразу после JSON-LD, а в main — в другом месте: берём строки с сайта, а строку JSON-LD — из новой сборки
    marks = [i for i, l in enumerate(m) if l.startswith('<<<<<<< live') or l == '=======' or l.startswith('>>>>>>> new')]
    if marks:
        assert len(marks) == 3, f'ожидался один конфликт, найдено меток: {len(marks)}'
        lv, nw = m[marks[0] + 1:marks[1]], m[marks[1] + 1:marks[2]]
        ld = '<script type="application/ld+json">'
        li = [i for i, l in enumerate(lv) if l.startswith(ld)]
        assert len(li) == 1 and len(nw) == 1 and nw[0].startswith(ld), 'конфликт не у JSON-LD — разберите вручную'
        lv[li[0]] = nw[0]
        m = m[:marks[0]] + lv + m[marks[2] + 1:]
    pkg = '\n'.join(m)
    h1, h2 = hunks(base.split('\n'), new.split('\n')), hunks(live.split('\n'), pkg.split('\n'))
    assert h1 and h1 == h2, 'изменения «сайт → пакет» не совпадают с «сборка 8216c91 → текущая»'
    lb, pb = live.encode('utf-8'), pkg.encode('utf-8')
    c1, c2 = COUNTERS.findall(lb), COUNTERS.findall(pb)
    assert len(c1) == 1 and c1 == c2, 'блок счётчиков изменён или не найден'
    assert c1[0] in (ROOT / 'server' / 'counters.html').read_bytes(), 'счётчики на сайте не как в server/counters.html'
    for k in (b'113675622', b'srch', b'comagic', b'radist'):
        assert lb.count(k) == pb.count(k), f'{k!r}: на сайте {lb.count(k)}, в пакете {pb.count(k)}'
    d = out / PAGE
    d.parent.mkdir(parents=True, exist_ok=True)
    d.write_bytes(pb)
    lines = f'{sha(pb)}  {PAGE}\n'
    if len(sys.argv) == 5:
        if pathlib.Path(sys.argv[4]).read_text(encoding='utf-8') != lines:
            raise SystemExit('пакет не совпадает с MANIFEST')
        print('MANIFEST совпадает')
    else:
        (out.parent / 'MANIFEST.sha256').write_text(lines, encoding='utf-8')
    (out.parent / 'EXPECTED_BEFORE.txt').write_text(f'{sha(lb)}  {PAGE}\n', encoding='utf-8')
    print(f'{PAGE}: {len(h1)} мест (как в сборке); счётчики прежние; поиск на месте')


if __name__ == '__main__':
    main()
