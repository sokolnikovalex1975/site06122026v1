#!/usr/bin/env python3
"""Мобильная вёрстка (16.11.2026): пакет для Timeweb из снимка рабочего сайта по HTTPS.

    python3 tools/deploy/prepare-2026-11-16-mobfit.py <папка>   # <папка>/before — 42 index.php, снятые по HTTPS

Собирает <папка>/after (tools/site/mob_fit.py + tools/site/flex_text.py поверх файлов сайта, не из репозитория:
в GitHub есть неопубликованные правки) и tools/deploy/mobfit-2026-11-16/deploy_payload.json — точные замены
с суммами SHA-256 до и после (build_pkg.py). Выкладка: publish_mobfit.py из SSH-консоли Timeweb.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import flex_text  # noqa: E402
import mob_fit  # noqa: E402

W = pathlib.Path(sys.argv[1]).resolve()
B, A = W / 'before', W / 'after'
n = 0
for f in sorted(B.rglob('index.php')):
    rel = f.relative_to(B)
    s = f.read_text(encoding='utf-8')
    assert s.count(mob_fit.ANCHOR) == 1 and 'id="mob-fit"' not in s, rel
    t = flex_text.fix(mob_fit.fix(s))[0]
    out = A / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(t, encoding='utf-8')
    n += 1
print('pages:', n)
