#!/usr/bin/env python3
"""Выкладка 07.11.2026 23:01 МСК (эффекты под курсором): правки 19 файлов в том виде, как их отдаёт сайт.

Использование:
  python3 tools/deploy/patch-2026-11-07-fx.py <папка с файлами сайта> <папка результата> [MANIFEST]

<папка с файлами сайта> — 19 файлов index.php (список PAGES и VENT), как их отдаёт сайт по HTTPS перед выкладкой
или как они лежат в копии tools/deploy/backup/before-fx_2026-11-07_ftp.zip. В <папку результата> пишутся файлы
пакета pestcontrol-deploy-2026-11-07-fx; если указан MANIFEST (tools/deploy/MANIFEST-2026-11-07-fx.sha256),
суммы результата сверяются с ним.

  * 18 страниц — функция apply() из tools/site/fx.py (та же, что в сборке, коммит aa5d92c): «фонарь» на фото
    первого экрана, подсветка рамки карточек, data-form, data-parallax, data-tilt. Повторный проход ничего не меняет;
  * страница вентиляции — две правки из истории репозитория, перенесённые в файл с сайта по фрагментам:
    самопроверка «0 из 5» по умолчанию (bc57569) и анимации как на главной (d4e9a3a). Из сравнения исходников
    страницы до и после коммита берутся только эти правки; прочие отличия (выложенные раньше) пропускаются;
  * проверки на каждом файле: блок счётчиков (Метрика 113675622, UIS/CoMagic, Radist) байт в байт прежний,
    набор ссылок href не меняется, каждый переносимый фрагмент найден в файле с сайта ровно один раз.
"""
import difflib
import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import fx  # noqa: E402

PAGES = [
    'deratizatsiya/index.php', 'dezinfektsiya/index.php', 'dezinsektsiya/index.php',
    'dogovor-deratizatsiya-dezinsektsiya/index.php', 'farmatsevticheskie-proizvodstva/index.php',
    'gostinitsy/index.php', 'magaziny-i-torgovye-seti/index.php', 'materialy/index.php',
    'materialy/pest-menedzhment-ili-razovaya-obrabotka/index.php', 'materialy/programma-pest-kontrolya/index.php',
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/index.php', 'materialy/zhurnal-pest-kontrolya/index.php',
    'normativnaya-baza/index.php', 'normativnaya-baza/proverochnye-listy/index.php',
    'pishchevoe-proizvodstvo/index.php', 'restorany-i-kafe/index.php', 'sanitarnyy-audit/index.php',
    'sklady-i-logistika/index.php',
]
VENT = 'ochistka-dezinfektsiya-ventilyatsii/index.php'
VENT_SRC = 'ochistka-dezinfektsiya-ventilyatsii/index.html'
# (коммит, отбор правок): из сравнения «коммит^ → коммит» переносятся только правки, подходящие под отбор
VENT_EDITS = [
    ('bc57569', lambda a, b: 'chk-res' in a or (a, b) == ('5</b>', '0</b>') or 'Все пять пунктов' in a
     or a == '<input type="checkbox" checked>'),
    ('d4e9a3a', lambda a, b: any(k in a + b for k in ('v-lit', 'vLit', 'data-tilt', 'data-form', 'Фонарь'))),
]
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
HREFS = re.compile(r'href="([^"]+)"')


def tok(s):
    return re.split(r'(?<=>)|(?<=\n)|(?<=\})|(?<=;)', s)


def git_show(commit, path):
    return subprocess.run(['git', '-C', str(ROOT), 'show', f'{commit}:{path}'],
                          capture_output=True, check=True).stdout.decode('utf-8')


def port(prev, new, target, keep, label, ctx=4, gap=8):
    """Переносит отобранные правки «prev → new» в target: каждый блок правок (близкие блоки сливаются) расширяется
    соседними фрагментами, пока не станет единственным в target, и заменяется тем же блоком из new."""
    A, B = tok(prev), tok(new)
    ops = [o for o in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes()
           if o[0] != 'equal' and keep(''.join(A[o[1]:o[2]]), ''.join(B[o[3]:o[4]]))]
    if not ops:
        raise SystemExit(f'[{label}] нет правок для переноса')
    chunks = []
    for _, i1, i2, j1, j2 in ops:
        # близкие блоки сливаются, только если между ними нет пропущенных правок
        if chunks and i1 - chunks[-1][1] <= gap and A[chunks[-1][1]:i1] == B[chunks[-1][3]:j1]:
            chunks[-1] = (chunks[-1][0], i2, chunks[-1][2], j2)
        else:
            chunks.append((i1, i2, j1, j2))
    out = target
    for i1, i2, j1, j2 in chunks:
        k = ctx
        while True:
            left, right = ''.join(A[max(0, i1 - k):i1]), ''.join(A[i2:i2 + k])
            old = left + ''.join(A[i1:i2]) + right
            n = out.count(old)
            if n == 1:
                break
            if n == 0:
                raise SystemExit(f'[{label}] фрагмент не найден в файле с сайта: {old[:300]!r}')
            k += 2
            if k > 60:
                raise SystemExit(f'[{label}] фрагмент не однозначен: {old[:300]!r}')
        out = out.replace(old, left + ''.join(B[j1:j2]) + right, 1)
    return out, len(chunks)


def same_frame(old, new, rel):
    a, b = COUNTERS.findall(old), COUNTERS.findall(new)
    if len(a) != 1 or a != b:
        raise SystemExit(f'{rel}: блок счётчиков изменён или не найден')
    if sorted(set(HREFS.findall(old))) != sorted(set(HREFS.findall(new))):
        raise SystemExit(f'{rel}: изменился набор ссылок')


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit(__doc__)
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    manifest = {}
    if len(sys.argv) == 4:
        for line in pathlib.Path(sys.argv[3]).read_text(encoding='utf-8').splitlines():
            if line.strip():
                h, f = line.split()
                manifest[f] = h
    done = {}
    for rel in PAGES:
        old = (src / rel).read_text(encoding='utf-8')
        new, info = fx.apply(old)
        if fx.apply(new)[0] != new:
            raise SystemExit(f'{rel}: повторный проход fx.apply меняет файл')
        same_frame(old, new, rel)
        done[rel] = (new, info)
    old = (src / VENT).read_text(encoding='utf-8')
    new, parts = old, []
    for commit, keep in VENT_EDITS:
        new, n = port(git_show(commit + '^', VENT_SRC), git_show(commit, VENT_SRC), new, keep, commit)
        parts.append(f'{commit}: {n} фрагм.')
    same_frame(old, new, VENT)
    done[VENT] = (new, ', '.join(parts))
    bad = 0
    for rel in sorted(done):
        new, info = done[rel]
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(new, encoding='utf-8')
        h = hashlib.sha256(new.encode('utf-8')).hexdigest()
        mark = ''
        if manifest:
            ok = manifest.get(rel) == h
            bad += not ok
            mark = ' MANIFEST ' + ('совпадает' if ok else 'НЕ СОВПАДАЕТ')
        print(f'{rel:66s} {info}{mark}')
    if manifest and (bad or set(manifest) != set(done)):
        raise SystemExit(f'расхождений с MANIFEST: {bad}; файлов в MANIFEST {len(manifest)}, в результате {len(done)}')
    print(f'готово: {len(done)} файлов в {dst}')


if __name__ == '__main__':
    main()
