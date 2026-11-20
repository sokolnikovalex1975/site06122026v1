#!/usr/bin/env python3
"""«Состав заявки» и длинные блоки на телефоне — выкладка на Timeweb (20.11.2026).

Запуск рядом с deploy_payload.json, вне public_html: --check (по умолчанию), --publish, --rollback.
Пакет готовит tools/deploy/prepare-2026-11-20-zayavka.py из актуальных файлов рабочего сайта.

Файлы (содержимое в пакете, сверка SHA-256): zayavka.min.js и mob-bloki.min.js — новые, samoproverka-forma.min.js —
новая версия. Точные замены в 41 странице index.php, других не допускается:
  * <style id="tel-plain"> → [<style id="chk-css">…</style>] <style id="zv-css">…</style> + <script src="…zayavka.min.js?v=…"
    defer> [+ <script src="…mob-bloki.min.js?v=…" defer>] + <style id="tel-plain"> (всё в <head>, выше кода UIS, который
    стоит прямо перед </head>; Radist — в конце <body>, не трогается);
  * на 13 страницах: …samoproverka-forma.min.js?v=20261119forma → ?v=20261120zv.
До и после сверяется SHA-256 каждого файла (при подготовке пакета счётчики Метрики, UIS и Radist, телефон и почта
проверены законом владельца до и после), резервная копия — вне public_html и не перезаписывается, при любой ошибке
уже заменённые файлы возвращаются. Повторный запуск после выкладки только сверяет суммы. Без f-строк (на сервере
Python 3.6), загрузок, паролей и сторонних пакетов; сообщения — ASCII (LANG=C).
"""
import base64
import hashlib
import json
import os
import pathlib
import shutil
import sys

WORK = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.path.expanduser('~/pestcontrol-center/public_html')).resolve()
PAYLOAD = json.loads((WORK / 'deploy_payload.json').read_text(encoding='utf-8'))
BACKUP = WORK / 'backup'
STATUS = WORK / 'publication.json'
MODE = sys.argv[1] if len(sys.argv) == 2 else '--check'
assert MODE in ('--check', '--publish', '--rollback'), MODE
assert ROOT.is_dir() and str(ROOT).endswith('/pestcontrol-center/public_html'), str(ROOT)
assert ROOT not in WORK.parents and ROOT != WORK, 'keep the package outside the public site'
assert PAYLOAD['name'] == 'zayavka-2026-11-20' and PAYLOAD['version'] == '20261120zv'
V = PAYLOAD['version']
ROWS = PAYLOAD['files']
N = len(ROWS)
assert N == PAYLOAD['count'] == 44, N
JS_ROWS, PAGE_ROWS = ROWS[:3], ROWS[3:]
assert [r['file'] for r in JS_ROWS] == ['zayavka.min.js', 'mob-bloki.min.js', 'samoproverka-forma.min.js']
JS = {}
for r in JS_ROWS:
    b = base64.b64decode(r['content_b64'].encode('ascii'))
    assert hashlib.sha256(b).hexdigest() == r['after'] and 'replace' not in r and len(b) < 60000, r['file']
    JS[r['file']] = b
assert JS_ROWS[0]['before'] is None and JS_ROWS[1]['before'] is None and JS_ROWS[2]['before']
assert b'/send.php' in JS['zayavka.min.js'] and b'pc-zayavka-v1' in JS['zayavka.min.js'] and b'PCZ' in JS['samoproverka-forma.min.js']
CHK = PAYLOAD['chk_css']
ZV = PAYLOAD['zv_css']
assert CHK.startswith('<style id="chk-css">') and CHK.endswith('</style>\n')
assert ZV.startswith('<style id="zv-css">') and ZV.endswith('</style>') and '<script' not in ZV.lower() and '\n' not in ZV
ANCHOR = '<style id="tel-plain">'
BAD = ('mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<select', '<?')
assert not any(x in (CHK + ZV).lower() for x in BAD)
pages = 0
for r in PAGE_ROWS:
    f = r['file']
    assert f.endswith('index.php') and r['before'] and r['after'] and r['before'] != r['after'] and 'content_b64' not in r, f
    depth = f.count('/')
    up = '../' * depth
    tags = '<script src="' + up + 'zayavka.min.js?v=' + V + '" defer></script>'
    if f != 'index.php':
        tags += '\n<script src="' + up + 'mob-bloki.min.js?v=' + V + '" defer></script>'
    kinds = []
    for old, new, count in r['replace']:
        assert count == 1 and old != new, f
        if old == ANCHOR:
            assert new in (CHK + ZV + '\n' + tags + '\n' + ANCHOR, ZV + '\n' + tags + '\n' + ANCHOR), 'head: ' + f
            kinds.append('head')
        elif old == '<script src="' + up + 'samoproverka-forma.min.js?v=20261119forma" defer></script>':
            assert new == '<script src="' + up + 'samoproverka-forma.min.js?v=' + V + '" defer></script>', f
            kinds.append('ver')
        else:
            raise AssertionError('replacement not allowed: ' + f)
    assert kinds in (['head'], ['head', 'ver']), f
    pages += 1
assert pages == 41


def sha(b):
    return hashlib.sha256(b).hexdigest()


def target(rel, new=False):
    assert not rel.startswith('/') and '..' not in rel.split('/') and '\\' not in rel
    p = ROOT / rel
    assert p.parent.is_dir() and (ROOT in p.parent.resolve().parents or p.parent.resolve() == ROOT), rel
    if not new:
        assert p.is_file() and not p.is_symlink(), rel
    return p


def result(row, old):
    if row['file'] in JS:
        return JS[row['file']]
    text = old.decode('utf-8')
    assert '<?php' not in text and '<?=' not in text, row['file']
    out = text
    for a, b, count in row['replace']:
        assert out.count(a) == count, 'COUNT CHANGED: ' + row['file'] + ' ' + a[:40]
        out = out.replace(a, b)
    low = out.lower()
    assert out.index('zayavka.min.js') < low.index('</head>'), row['file']
    return out.encode('utf-8')


def write(p, data, mode):
    tmp = p.with_name(p.name + '.zayavka-20261120-stage')
    assert not tmp.exists(), str(tmp)
    with tmp.open('wb') as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.chmod(str(tmp), mode)
    os.replace(str(tmp), str(p))


def current(row):
    p = target(row['file'], new=row['before'] is None)
    return sha(p.read_bytes()) if p.exists() else None


if MODE == '--rollback':
    state = json.loads(STATUS.read_text(encoding='utf-8')) if STATUS.exists() else {}
    names = state.get('promoted', [r['file'] for r in ROWS])
    done = 0
    # pages first, then the scripts (pages without the script tags never reference them)
    for row in reversed(ROWS):
        if row['file'] not in names:
            continue
        p = target(row['file'], new=row['before'] is None)
        if row['before'] is None:
            if p.exists():
                assert sha(p.read_bytes()) == row['after'], 'CHANGED BY ANOTHER DEPLOYMENT: ' + row['file']
                p.unlink()
                done += 1
            continue
        b = (BACKUP / row['file']).read_bytes()
        assert sha(b) == row['before']
        # Never overwrite an unrelated version changed by another deployment.
        assert sha(p.read_bytes()) in (row['before'], row['after']), 'CHANGED BY ANOTHER DEPLOYMENT: ' + row['file']
        write(p, b, (BACKUP / row['file']).stat().st_mode & 0o777)
        done += 1
    STATUS.write_text(json.dumps({'status': 'rolled_back_by_command', 'promoted': []}), encoding='utf-8')
    print('ROLLED BACK: %d files' % done)
    sys.exit(0)

if all(current(r) == r['after'] for r in ROWS):
    print('ALREADY PUBLISHED: %d/%d checksums match' % (N, N))
    sys.exit(0)

plan = []
for row in ROWS:
    new_file = row['before'] is None
    p = target(row['file'], new=new_file)
    if new_file:
        assert not p.exists(), 'NEW FILE ALREADY EXISTS: ' + row['file']
        old, mode = None, 0o644
    else:
        old = p.read_bytes()
        assert sha(old) == row['before'], 'CURRENT FILE CHANGED: ' + row['file'] + ' ' + sha(old)[:12]
        mode = p.stat().st_mode & 0o777
    new = result(row, old)
    assert sha(new) == row['after'], 'PACKAGE MISMATCH: ' + row['file']
    plan.append((row, p, old, new, mode))
print('PRECHECK OK: %d/%d original and resulting checksums verified (3 scripts, 41 pages)' % (N, N))
if MODE == '--check':
    sys.exit(0)

assert not BACKUP.exists(), 'BACKUP ALREADY EXISTS: do not overwrite'
BACKUP.mkdir()
for row, p, old, new, mode in plan:
    if old is None:
        continue
    b = BACKUP / row['file']
    b.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(p), str(b))
    assert sha(b.read_bytes()) == row['before']
print('BACKUP OK: %d/%d outside public_html' % (N - 2, N - 2))

promoted = []
try:
    # the scripts first: a published page always finds them
    for row, p, old, new, mode in plan:
        if old is None:
            assert not p.exists(), 'CONCURRENT CHANGE: ' + row['file']
        else:
            assert sha(p.read_bytes()) == row['before'], 'CONCURRENT CHANGE: ' + row['file']
        write(p, new, mode)
        promoted.append(row['file'])
        assert sha(p.read_bytes()) == row['after']
    assert all(current(r) == r['after'] for r in ROWS)
    STATUS.write_text(json.dumps({'status': 'published', 'promoted': promoted}, indent=2), encoding='utf-8')
    print('PUBLISHED: %d/%d checksums verified' % (N, N))
    print('BACKUP: ' + str(BACKUP))
except BaseException:
    for row, p, old, new, mode in reversed(plan):
        if row['file'] in promoted:
            if old is None:
                p.unlink()
            else:
                write(p, old, mode)
    STATUS.write_text(json.dumps({'status': 'rolled_back', 'promoted': []}), encoding='utf-8')
    print('AUTOMATIC ROLLBACK: ' + str(len(promoted)))
    raise
