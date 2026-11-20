#!/usr/bin/env python3
"""«Заявка отправлена» — крупная зелёная галочка: выкладка на Timeweb (20.11.2026).

Запуск рядом с deploy_payload.json, вне public_html: --check (по умолчанию), --publish, --rollback.
Пакет готовит tools/deploy/prepare-2026-11-20-galochka.py из актуальных файлов рабочего сайта. Одна точная замена в
41 странице index.php: строка <style id="zv-css">…</style> → новая (стили состава заявки с новой галочкой). Других
замен нет. Суммы SHA-256 до и после, резервная копия вне public_html, откат при ошибке, Python 3.6, ASCII-сообщения.
"""
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
assert PAYLOAD['name'] == 'galochka-2026-11-20'
ROWS = PAYLOAD['files']
N = len(ROWS)
assert N == PAYLOAD['count'] == 41, N
JS = {}
BAD = ('mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<select', '<?', '<script')
for r in ROWS:
    f = r['file']
    assert f.endswith('index.php') and r['before'] and r['after'] and r['before'] != r['after'], f
    assert len(r['replace']) == 1, f
    old, new, count = r['replace'][0]
    assert count == 1 and old.startswith('<style id="zv-css">') and old.endswith('</style>') and '\n' not in old, f
    assert new.startswith('<style id="zv-css">') and new.endswith('</style>') and '\n' not in new and 'zvOkPop' in new, f
    assert new.count('</style>') == 1 and not any(b in new.lower() for b in BAD), f


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
    return out.encode('utf-8')


def write(p, data, mode):
    tmp = p.with_name(p.name + '.galochka-20261120-stage')
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
print('PRECHECK OK: %d/%d original and resulting checksums verified (41 pages)' % (N, N))
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
print('BACKUP OK: %d/%d outside public_html' % (N, N))

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
