#!/usr/bin/env python3
"""Сборка «до» для пакета avto-2026-11-23: сборка репозитория (main) без правок страницы автотранспорта.

    git worktree add /tmp/prev_wt 7a506af && (cd /tmp/prev_wt && python3 tools/site/build_prod.py)
    git worktree add /tmp/avto_wt 17401bc && (cd /tmp/avto_wt && python3 tools/site/build_prod.py)
    python3 tools/site/build_prod.py
    python3 tools/deploy/prepare-2026-11-23-avto-before.py /tmp/prev_wt/dist/timeweb /tmp/avto_wt/dist/timeweb /tmp/A_dist
    python3 tools/deploy/prepare-2026-11-23-avto.py /tmp/A_dist <новая папка пакета>

После 17401bc в main вошли ППК по ХАССП и SEO-правки 17.11 (они уже на сайте), поэтому сборка 7a506af как «до» не
годится: разница с dist/timeweb была бы не только страницей автотранспорта. A = копия dist/timeweb без 12 новых файлов,
на 43 страницах обращены правки «7a506af → 17401bc»: в dist/timeweb ищется «левый край + вставка + правый край»
(однозначно), заменяется на «левый край + было + правый край». Индекс поиска и карта сайта — из сборки 7a506af
(скрипт пакета берёт их с рабочего сайта; здесь нужно лишь, чтобы они отличались от dist/timeweb).
"""
import importlib.util
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('prep', ROOT / 'tools/deploy/prepare-2026-11-23-avto.py')
prep = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(ROOT / 'tools/site'))
spec.loader.exec_module(prep)

B0 = pathlib.Path(sys.argv[1]).resolve()
A0 = pathlib.Path(sys.argv[2]).resolve()
B = ROOT / 'dist/timeweb'
A = pathlib.Path(sys.argv[3]).resolve()
assert not A.exists(), 'используйте новую папку'


def files(d):
    return {str(p.relative_to(d)) for p in d.rglob('*') if p.is_file()}


fb0, fa0, fb = files(B0), files(A0), files(B)
new = sorted(fa0 - fb0)
assert len(new) == 12 and not (fb0 - fa0)
changed = [f for f in sorted(fb0 & fa0) if (B0 / f).read_bytes() != (A0 / f).read_bytes()]
pages = [f for f in changed if f.endswith('index.php')]
assert set(changed) - set(pages) == {'search-index.json', 'sitemap.xml'}
shutil.copytree(str(B), str(A))
for f in new:
    (A / f).unlink()
for d in sorted({(A / f).parent for f in new}, reverse=True):
    if d.exists() and not any(d.iterdir()):
        d.rmdir()
# индекс и карта — как в B0 (скрипт пакета берёт их с рабочего сайта, здесь нужно лишь отличие от B)
for f in ('search-index.json', 'sitemap.xml'):
    shutil.copy2(str(B0 / f), str(A / f))
problems = 0
for f in pages:
    p0 = (B0 / f).read_text(encoding='utf-8')
    a0 = (A0 / f).read_text(encoding='utf-8')
    s = (B / f).read_text(encoding='utf-8')
    for i1, i2, ins in reversed(prep.edits(p0, a0)):
        was = p0[i1:i2]
        done = False
        for c in (40, 80, 160, 30, 20, 12, 6):
            left, right = p0[max(0, i1 - c):i1], p0[i2:i2 + c]
            key = left + ins + right
            if s.count(key) == 1:
                s = s.replace(key, left + was + right)
                done = True
                break
        if not done:
            problems += 1
            print('НЕТ МЕСТА', f, repr(ins[:160]), repr(was[:80]))
    (A / f).write_text(s, encoding='utf-8')
    k = 'dezinfektsiya/avtotransport/'
    if k in s:
        print('ОСТАЛАСЬ ССЫЛКА', f, s.count(k))
        problems += 1
print('страниц', len(pages), 'проблем', problems)
assert problems == 0
