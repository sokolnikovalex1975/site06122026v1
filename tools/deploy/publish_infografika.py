#!/usr/bin/env python3
"""Инфографика в стиле лаборатории на рабочем сайте: выкладка на Timeweb (19.11.2026).

Запуск рядом с deploy_payload.json, вне public_html: --check (по умолчанию), --publish, --rollback.
Пакет готовит tools/deploy/prepare-2026-11-19-infografika.py из актуальных страниц рабочего сайта (HTTPS).

Скрипт кладёт в public_html/img новые картинки img/ig-*.webp (из пакета, суммы SHA-256 сверяются; таких файлов на сайте
ещё нет) и применяет к страницам (index.php) точные замены из пакета: каждая замена найдена ровно один раз, итоговый
SHA-256 сверяется. Замены не затрагивают <script>, счётчики Метрики, UIS и Radist, ссылки tel: и mailto: (проверяется
ниже и при подготовке пакета). До и после сверяется SHA-256 каждого файла, резервные копии страниц сохраняются вне
public_html и не перезаписываются, при любой ошибке уже заменённое возвращается, добавленные картинки убираются.
Повторный запуск после успешной выкладки только сверяет суммы. Без f-строк (на сервере Python 3.6), загрузок, паролей
и сторонних пакетов; сообщения — ASCII (LANG=C).
"""
import base64
import hashlib
import json
import os
import pathlib
import re
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
assert PAYLOAD['name'] == 'infografika-2026-11-19'
ROWS = PAYLOAD['files']
N = len(ROWS)
NI, NP = PAYLOAD['images'], PAYLOAD['pages']
assert N == NI + NP and 40 <= NI <= 90 and 30 <= NP <= 41, 'unexpected number of files: %d' % N
IMGS, PAGES = ROWS[:NI], ROWS[NI:]
IMG_IDS = set(id(r) for r in IMGS)
FORBIDDEN = ('<script', 'mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<?')
for r in IMGS:
    assert re.match(r'^img/ig-[a-z0-9-]+-(128|240)\.webp$', r['file']), r['file']
    assert r['before'] is None and 'replace' not in r, r['file']
    data = base64.b64decode(r['content_b64'].encode('ascii'))
    assert data[:4] == b'RIFF' and data[8:12] == b'WEBP' and hashlib.sha256(data).hexdigest() == r['after'], r['file']
    assert 1000 < len(data) < 40000, r['file']
for r in PAGES:
    assert r['file'].endswith('index.php') and 'content_b64' not in r, r['file']
    assert len(r['before']) == 64 and len(r['after']) == 64 and r['before'] != r['after'], r['file']
    assert r['replace'] and all(c == 1 for a, b, c in r['replace']), 'unexpected replacements: ' + r['file']
    for a, b, c in r['replace']:
        assert a and a != b, 'empty or no-op replacement: ' + r['file']
        for bad in FORBIDDEN:
            assert bad not in a.lower() and bad not in b.lower(), 'touches tracking or contacts: ' + bad + ' ' + r['file']
FILES = [r['file'] for r in ROWS]
assert len(set(FILES)) == N, 'duplicate files'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def target(rel, new=False):
    assert rel in FILES and not rel.startswith('/') and '..' not in rel.split('/') and '\\' not in rel
    p = ROOT / rel
    assert p.parent.is_dir() and (p.parent.resolve() == ROOT or ROOT in p.parent.resolve().parents), rel
    assert not p.is_symlink(), rel
    if not new:
        assert p.is_file(), rel
    return p


def result(row, old):
    if id(row) in IMG_IDS:
        return base64.b64decode(row['content_b64'].encode('ascii'))
    text = old.decode('utf-8')
    assert '<?php' not in text and '<?=' not in text, row['file']
    out = text
    for a, b, count in row['replace']:
        assert out.count(a) == count, 'COUNT CHANGED: ' + row['file'] + ' ' + a[:60].encode('ascii', 'replace').decode()
        out = out.replace(a, b)
    return out.encode('utf-8')


def write(p, data, mode):
    tmp = p.with_name(p.name + '.infografika-20261119-stage')
    assert not tmp.exists(), str(tmp)
    with tmp.open('wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(str(tmp), mode)
    os.replace(str(tmp), str(p))


def current(row):
    p = target(row['file'], new=id(row) in IMG_IDS)
    return sha(p.read_bytes()) if p.exists() else None


def published(row):
    return current(row) == row['after']


if MODE == '--rollback':
    state = json.loads(STATUS.read_text(encoding='utf-8')) if STATUS.exists() else {}
    names = state.get('promoted', FILES)
    done = 0
    for row in reversed(ROWS):
        if row['file'] not in names:
            continue
        p = target(row['file'], new=True)
        if id(row) in IMG_IDS:
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

if all(published(r) for r in ROWS):
    print('ALREADY PUBLISHED: %d/%d checksums match (%d images, %d pages)' % (N, N, NI, NP))
    sys.exit(0)

plan = []
for row in ROWS:
    new_file = id(row) in IMG_IDS
    p = target(row['file'], new=new_file)
    if new_file:
        assert not p.exists(), 'FILE ALREADY EXISTS: ' + row['file']
        old, mode = None, 0o644
    else:
        old = p.read_bytes()
        assert sha(old) == row['before'], 'CURRENT FILE CHANGED: ' + row['file'] + ' ' + sha(old)[:12]
        mode = p.stat().st_mode & 0o777
    new = result(row, old)
    assert sha(new) == row['after'], 'PACKAGE MISMATCH: ' + row['file']
    plan.append((row, p, old, new, mode))
print('PRECHECK OK: %d/%d original and resulting checksums verified (%d new images, %d pages, %d replacements)'
      % (N, N, NI, NP, sum(len(r['replace']) for r in PAGES)))
if MODE == '--check':
    sys.exit(0)

assert not BACKUP.exists(), 'BACKUP ALREADY EXISTS: do not overwrite'
BACKUP.mkdir()
for row in PAGES:
    b = BACKUP / row['file']
    b.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(target(row['file'])), str(b))
    assert sha(b.read_bytes()) == row['before']
print('BACKUP OK: %d/%d pages outside public_html' % (NP, NP))

promoted = []
try:
    for row, p, old, new, mode in plan:
        if old is None:
            assert not p.exists(), 'CONCURRENT CHANGE: ' + row['file']
        else:
            assert sha(p.read_bytes()) == row['before'], 'CONCURRENT CHANGE: ' + row['file']
        write(p, new, mode)
        promoted.append(row['file'])
        assert sha(p.read_bytes()) == sha(new)
    assert all(published(r) for r in ROWS)
    STATUS.write_text(json.dumps({'status': 'published', 'promoted': promoted}, indent=1), encoding='utf-8')
    print('PUBLISHED: %d/%d checksums verified (%d images, %d pages)' % (N, N, NI, NP))
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
