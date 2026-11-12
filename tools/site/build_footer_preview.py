#!/usr/bin/env python3
"""Изолированное статическое превью без серверных файлов и браузерного хранилища."""
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(sys.argv[1]).resolve()
assert OUT != ROOT and ROOT not in OUT.parents, 'превью должно быть вне исходников'
shutil.copytree(
    ROOT, OUT, dirs_exist_ok=True,
    ignore=shutil.ignore_patterns(
        '.git', 'tools', 'server', 'dist', 'preview-audit', 'preview-services',
        '*.md', '__pycache__', '*.pyc'
    )
)
old = (
    "    try { if (location.hash || sessionStorage.getItem('pc-intro')) "
    "d.classList.add('no-intro'); else sessionStorage.setItem('pc-intro', '1'); }\n"
    "    catch (e) { if (location.hash) d.classList.add('no-intro'); }"
)
n = 0
for f in OUT.rglob('*.html'):
    s = f.read_text(encoding='utf-8')
    if old in s:
        s = s.replace(old, "    d.classList.add('no-intro');", 1)
        f.write_text(s, encoding='utf-8')
        n += 1
    assert not any(k in s for k in ('sessionStorage', 'localStorage', 'indexedDB')), str(f)
print(f'Превью: {OUT}; заставка без хранилища на {n} страницах. Исходники не изменены.')
