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
store = (
    '<script>window.__pcPreviewStore={values:Object.create(null),'
    'getItem:function(k){return this.values[k]??null},'
    'setItem:function(k,v){this.values[k]=String(v)},'
    'removeItem:function(k){delete this.values[k]},'
    'clear:function(){this.values=Object.create(null)}};</script>'
)
n = 0
for f in OUT.rglob('*.html'):
    s = f.read_text(encoding='utf-8')
    if 'sessionStorage' in s or 'localStorage' in s:
        s = s.replace('sessionStorage', 'window.__pcPreviewStore')
        s = s.replace('localStorage', 'window.__pcPreviewStore')
        s = s.replace('<head>', '<head>\n' + store, 1)
        f.write_text(s, encoding='utf-8')
        n += 1
    assert not any(k in s for k in ('sessionStorage', 'localStorage', 'indexedDB')), str(f)
print(f'Превью: {OUT}; временное состояние в памяти на {n} страницах. Исходники не изменены.')
