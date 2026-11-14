#!/usr/bin/env python3
"""«Лёгкая лупа» и облегчённый режим: выкладка на Timeweb из SSH-консоли (15.11.2026).

Запуск рядом с deploy_payload.json, вне public_html:
  --check    (по умолчанию) сверить суммы SHA-256 всех файлов до и после, ничего не меняя;
  --publish  резервная копия вне public_html, затем новые фото, style.css, app.min.js и страницы с проверкой каждого файла;
  --rollback вернуть файлы из резервной копии и убрать добавленные фото.
Пакет готовит tools/deploy/prepare-2026-11-15-lupa.py из актуальных файлов рабочего сайта.

Скрипт сам применяет к файлам public_html операции из пакета (точные замены с проверкой числа совпадений, три новых
фото из пакета), сверяет SHA-256 каждого файла до и после, не перезаписывает резервную копию и при любой ошибке
возвращает уже заменённые файлы и убирает добавленные. Повторный запуск после выкладки только сверяет суммы.
Без f-строк, загрузок, паролей и сторонних пакетов (Python 3.6 на сервере).
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
assert PAYLOAD['name'] == 'lupa-2026-11-15'
OLD_V, NEW_V = PAYLOAD['old_version'], PAYLOAD['new_version']
assert (OLD_V, NEW_V) == ('20261113ekran', '20261115lupa')
ROWS = PAYLOAD['files']
N = len(ROWS)
assert PAYLOAD['images'] == 3 and N == PAYLOAD['pages'] + 5 and 30 <= PAYLOAD['pages'] <= 60, 'unexpected number of files: %d' % N
assert len(set(r['file'] for r in ROWS)) == N
IMGS, CSS_ROW, JS_ROW, PAGES = ROWS[:3], ROWS[3], ROWS[4], ROWS[5:]
assert [r['file'] for r in IMGS] == ['img/hero-dim.webp', 'img/hero-m-dim.webp', 'img/hero-lit.webp']
for r in IMGS:
    assert r['before'] is None and 'replace' not in r
    data = base64.b64decode(r['content_b64'].encode('ascii'))
    assert data[:4] == b'RIFF' and data[8:12] == b'WEBP' and hashlib.sha256(data).hexdigest() == r['after'], r['file']
assert CSS_ROW['file'] == 'style.css' and len(CSS_ROW['replace']) == 6 and 'content_b64' not in CSS_ROW
assert any('.lowfx .hero-lens' in b for a, b, c in CSS_ROW['replace'])
assert JS_ROW['file'] == 'app.min.js' and len(JS_ROW['replace']) == 13 and 'content_b64' not in JS_ROW
assert JS_ROW['replace'][4][:2] == ['A=a("#heroLit")', 'A=a("#heroLens")']
for r in [CSS_ROW, JS_ROW]:
    assert r['before'] and r['after'] and all(c == 1 for a, b, c in r['replace']), r['file']
for r in PAGES:
    assert r['before'] and r['after'] and 'content_b64' not in r, r['file']
    assert r['file'] == 'index.php' or r['file'].endswith('/index.php'), r['file']
    a, b, c = r['replace'][0]
    assert [a, b] == ['?v=' + OLD_V, '?v=' + NEW_V] and c in (1, 2, 3), r['file']
    assert all(c == 1 for a, b, c in r['replace'][1:]), r['file']
    if r['file'] in ('privacy/index.php', 'soglasie/index.php'):
        assert len(r['replace']) == 1, r['file']
    else:
        assert len(r['replace']) >= 3, r['file']


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
    if row['before'] is None:
        return base64.b64decode(row['content_b64'].encode('ascii'))
    text = old.decode('utf-8')
    assert '<?php' not in text and '<?=' not in text, row['file']
    out = text
    for a, b, count in row['replace']:
        assert out.count(a) == count, 'COUNT CHANGED: ' + row['file'] + ' ' + a[:60]
        out = out.replace(a, b)
    return out.encode('utf-8')


def write(p, data, mode):
    tmp = p.with_name(p.name + '.lupa-20261115-stage')
    assert not tmp.exists(), str(tmp)
    with tmp.open('wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(str(tmp), mode)
    os.replace(str(tmp), str(p))


def current(row):
    p = target(row['file'], new=row['before'] is None)
    return sha(p.read_bytes()) if p.exists() else None


if MODE == '--rollback':
    state = json.loads(STATUS.read_text(encoding='utf-8')) if STATUS.exists() else {}
    names = state.get('promoted', [r['file'] for r in ROWS])
    done = 0
    for row in reversed(ROWS):
        if row['file'] not in names:
            continue
        p = target(row['file'], new=row['before'] is None)
        if row['before'] is None:
            if p.exists():
                # Never delete a file changed by another deployment.
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
        assert not p.exists(), 'FILE ALREADY EXISTS: ' + row['file']
        old, mode = None, 0o644
    else:
        old = p.read_bytes()
        assert sha(old) == row['before'], 'CURRENT FILE CHANGED: ' + row['file']
        mode = p.stat().st_mode & 0o777
    new = result(row, old)
    assert sha(new) == row['after'], 'PACKAGE MISMATCH: ' + row['file']
    plan.append((row, p, old, new, mode))
print('PRECHECK OK: %d/%d original and resulting checksums verified (3 new images, style.css, app.min.js, %d pages)'
      % (N, N, len(PAGES)))
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
print('BACKUP OK: %d/%d outside public_html' % (len(plan) - len(IMGS), len(plan) - len(IMGS)))

promoted = []
try:
    for row, p, old, new, mode in plan:
        if old is None:
            assert not p.exists(), 'CONCURRENT CHANGE: ' + row['file']
        else:
            assert sha(p.read_bytes()) == row['before'], 'CONCURRENT CHANGE: ' + row['file']
        write(p, new, mode)
        promoted.append(row['file'])
        assert sha(p.read_bytes()) == row['after']
    assert all(current(r) == r['after'] for r in ROWS)
    STATUS.write_text(json.dumps({'status': 'published', 'promoted': promoted}, indent=1), encoding='utf-8')
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
    print('AUTOMATIC ROLLBACK: %d files' % len(promoted))
    raise
