#!/usr/bin/env python3
"""Выкладка 07.11.2026 (образцы документов): правки страницы ППК и раздела «Материалы» в файлах, которые сейчас на сайте.

Использование:
  python3 tools/deploy/patch-2026-11-07-docs.py <папка с файлами сайта> <dist до правки> <dist после правки> <папка пакета>

<папка с файлами сайта> — `materialy/index.php` и `materialy/programma-proizvodstvennogo-kontrolya-haccp/index.php`,
как их отдаёт сайт по HTTPS; <dist до правки> и <dist после правки> — сборки `tools/site/build_prod.py`
(dist/timeweb) из коммита до правки и из текущего. Скрипт берёт все отличия «до → после» (title, description,
og:description, микроразметка, первый экран, блок «Образец», FAQ — снятый шаблон Word; карточка ППК в «Материалах»),
расширяет каждое до однозначного фрагмента и вносит в файлы с сайта. Проверки:
  * те же замены превращают сборку «до» ровно в сборку «после» (других правок в пакете нет);
  * каждый исходный фрагмент встречается в файле с сайта ровно один раз;
  * после правки файл с сайта отличается от сборки «после» только тем, чем отличался от сборки «до»
    (не выложенные правки других задач, например эффекты tools/site/fx.py, в пакет не попадают);
  * блок счётчиков (Метрика 113675622, UIS, Radist) не меняется.
"""
import difflib
import pathlib
import re
import sys

PAGES = ['materialy/programma-proizvodstvennogo-kontrolya-haccp/index.php', 'materialy/index.php']
COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)


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
            if prev.count(old) == 1 and live.count(old) == 1:
                break
        else:
            raise SystemExit(f'нет однозначного фрагмента для строк {i1}–{i2}')
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


def opcodes_signature(x, y):
    sm = difflib.SequenceMatcher(None, x, y, autojunk=False)
    return [(op, x[i1:i2], y[j1:j2]) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != 'equal']


def main(site, dprev, dnew, pkg):
    for rel in PAGES:
        # байты как есть (без перевода строк при чтении)
        live = pathlib.Path(site, rel).read_bytes().decode('utf-8')
        prev = pathlib.Path(dprev, rel).read_bytes().decode('utf-8')
        new = pathlib.Path(dnew, rel).read_bytes().decode('utf-8')
        reps = pairs(prev, new, live)
        assert apply(prev, reps, rel + ' (сборка)') == new, rel + ': замены не дают сборку «после»'
        out = apply(live, reps, rel + ' (сайт)')
        # отличия от сборки «после» — те же, что были между сайтом и сборкой «до»
        assert opcodes_signature(new, out) == opcodes_signature(prev, live), rel + ': лишние отличия'
        cl, co = COUNTERS.findall(live), COUNTERS.findall(out)
        assert len(cl) == 1 and cl == co, rel + ': блок счётчиков'
        p = pathlib.Path(pkg, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(out.encode('utf-8'))
        print(f'{rel}: замен {len(reps)}, счётчики без изменений, отличий от сборки (не выложенные правки других задач): '
              f'{len(opcodes_signature(new, out))}')


if __name__ == '__main__':
    main(*sys.argv[1:5])
