#!/usr/bin/env python3
"""Схема объекта на главной + зелёная метка «Вы здесь»: выкладка на Timeweb из SSH-консоли (13.11.2026).

Запуск рядом с deploy_payload.json, вне public_html: --check (по умолчанию), --publish, --rollback.
Пакет готовит tools/deploy/prepare-2026-11-13-shema-here.py из актуальных страниц рабочего сайта.

Скрипт сам применяет к файлам public_html точные замены из пакета (два CSS-правила метки на 40 страницах; на главной
ещё плитка IPM, блок «Схема объекта», его стили перед <!-- UIS --> и скрипт перед <!-- Radist -->), сверяет SHA-256
каждого файла до и после, сохраняет резервную копию вне public_html и при любой ошибке возвращает уже заменённые
файлы. Повторный запуск после успешной выкладки только сверяет суммы. Без f-строк, загрузок, паролей и сторонних
пакетов (Python 3.6 на сервере).
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
assert MODE in ('--check', '--publish', '--rollback')
assert ROOT.is_dir() and str(ROOT).endswith('/pestcontrol-center/public_html')
assert ROOT not in WORK.parents and ROOT != WORK, 'keep the package outside the public site'
assert PAYLOAD['name'] == 'shema-here-2026-11-13'
ROWS = PAYLOAD['files']
N = len(ROWS)
assert N == PAYLOAD['pages'] and 30 <= N <= 60, 'unexpected number of files: %d' % N
assert len(set(r['file'] for r in ROWS)) == N
assert ROWS[0]['file'] == 'index.php' and len(ROWS[0]['replace']) == 6
for r in ROWS:
    assert r['file'] == 'index.php' or r['file'].endswith('/index.php'), r['file']
    for old, new, count in r['replace']:
        assert count == 1, r['file']
    if r['file'] != 'index.php':
        assert 1 <= len(r['replace']) <= 2, r['file']
        for old, new, count in r['replace']:
            assert old.startswith(('.pr-here{', '.vu-here{')) and new.startswith(old[:9]), r['file']


def sha(b):
    return hashlib.sha256(b).hexdigest()


def target(rel):
    assert not rel.startswith('/') and '..' not in rel.split('/')
    assert rel.endswith('index.php')
    p = ROOT / rel
    assert p.is_file() and not p.is_symlink()
    assert ROOT in p.resolve().parents
    return p


def apply(s, row):
    # The exact original (SHA-256 'before') and result (SHA-256 'after') were verified when the package was prepared,
    # so matching both checksums here proves that only these places change.
    out = s
    for old, new, count in row['replace']:
        assert out.count(old) == count, 'COUNT CHANGED: ' + row['file'] + ' ' + old
        out = out.replace(old, new)
    return out


def replace(p, data, mode):
    tmp = p.with_name(p.name + '.shema-20261113-stage')
    assert not tmp.exists(), str(tmp)
    with tmp.open('wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(str(tmp), mode)
    os.replace(str(tmp), str(p))


if MODE == '--rollback':
    assert BACKUP.is_dir()
    state = json.loads(STATUS.read_text()) if STATUS.exists() else {}
    names = state.get('promoted', [r['file'] for r in ROWS])
    for row in ROWS:
        if row['file'] not in names:
            continue
        p = target(row['file'])
        b = (BACKUP / row['file']).read_bytes()
        assert sha(b) == row['before']
        # Never overwrite an unrelated version changed by another deployment.
        assert sha(p.read_bytes()) in (row['before'], row['after'])
        replace(p, b, (BACKUP / row['file']).stat().st_mode & 0o777)
    STATUS.write_text(json.dumps({'status': 'rolled_back_by_command', 'promoted': []}))
    print('ROLLED BACK: ' + str(len(names)))
    sys.exit(0)

already = all(sha(target(r['file']).read_bytes()) == r['after'] for r in ROWS)
if already:
    print('ALREADY PUBLISHED: %d/%d checksums match' % (N, N))
    sys.exit(0)

plan = []
for row in ROWS:
    p = target(row['file'])
    old = p.read_bytes()
    assert sha(old) == row['before'], 'CURRENT FILE CHANGED: ' + row['file']
    text = old.decode('utf-8')
    assert '<?php' not in text and '<?=' not in text
    new = apply(text, row).encode('utf-8')
    assert sha(new) == row['after'], 'PACKAGE MISMATCH: ' + row['file']
    plan.append((row, p, old, new, p.stat().st_mode & 0o777))
print('PRECHECK OK: %d/%d original and resulting checksums verified' % (N, N))
if MODE == '--check':
    sys.exit(0)

assert not BACKUP.exists(), 'BACKUP ALREADY EXISTS: do not overwrite'
BACKUP.mkdir()
for row, p, old, new, mode in plan:
    b = BACKUP / row['file']
    b.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(p), str(b))
    assert sha(b.read_bytes()) == row['before']
print('BACKUP OK: %d/%d outside public_html' % (N, N))

promoted = []
try:
    for row, p, old, new, mode in plan:
        assert sha(p.read_bytes()) == row['before'], 'CONCURRENT CHANGE: ' + row['file']
        replace(p, new, mode)
        promoted.append(row['file'])
        assert sha(p.read_bytes()) == row['after']
    assert all(sha(target(r['file']).read_bytes()) == r['after'] for r in ROWS)
    STATUS.write_text(json.dumps({'status': 'published', 'promoted': promoted}, indent=2))
    print('PUBLISHED: %d/%d checksums verified' % (N, N))
    print('BACKUP: ' + str(BACKUP))
except BaseException:
    for row, p, old, new, mode in plan:
        if row['file'] in promoted:
            replace(p, old, mode)
    STATUS.write_text(json.dumps({'status': 'rolled_back', 'promoted': []}))
    print('AUTOMATIC ROLLBACK: ' + str(len(promoted)))
    raise
