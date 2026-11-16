#!/usr/bin/env python3
"""«Что видит камера в коробе» на странице вентиляции: выкладка на Timeweb (17.11.2026).

Запуск рядом с deploy_payload.json, вне public_html: --check (по умолчанию), --publish, --rollback.
Пакет готовит tools/deploy/prepare-2026-11-17-kamera.py из актуального файла рабочего сайта.

Скрипт кладёт в public_html/img 9 новых кадров (vent-kadr-*.webp из пакета, суммы SHA-256 сверяются) и применяет
к ochistka-dezinfektsiya-ventilyatsii/index.php точные замены из пакета: подпись над кадром, содержимое кадра (SVG-схема ->
три фото, холст WebGL и кнопка паузы), «Что видно на кадре», стили схемы -> стили блока, скрипт схемы -> скрипт блока.
Счётчики Метрики, UIS и Radist, телефон и почта заменами не затрагиваются (проверяется ниже и при подготовке пакета).
До и после сверяется SHA-256 каждого файла, резервная копия страницы сохраняется вне public_html и не перезаписывается,
при любой ошибке уже заменённое возвращается, добавленные кадры убираются. Повторный запуск после успешной выкладки только
сверяет суммы. Без f-строк (на сервере Python 3.6), загрузок, паролей и сторонних пакетов; сообщения — ASCII (LANG=C).
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
assert PAYLOAD['name'] == 'kamera-2026-11-17'
ROWS = PAYLOAD['files']
N = len(ROWS)
IMAGES = ['img/vent-kadr-%s%s.webp' % (k, w) for k in ('1-do', '2-ochistka', '3-dezinfektsiya')
          for w in ('-720', '-1080', '')]
PAGE = 'ochistka-dezinfektsiya-ventilyatsii/index.php'
assert PAYLOAD['images'] == 9 and N == 10, 'unexpected number of files: %d' % N
assert [r['file'] for r in ROWS] == IMAGES + [PAGE], 'unexpected files'
IMGS, PAGE_ROW = ROWS[:9], ROWS[9]
for r in IMGS:
    assert r['before'] is None and 'replace' not in r, r['file']
    data = base64.b64decode(r['content_b64'].encode('ascii'))
    assert data[:4] == b'RIFF' and data[8:12] == b'WEBP' and hashlib.sha256(data).hexdigest() == r['after'], r['file']
    assert 15000 < len(data) < 110000, r['file']
assert PAGE_ROW['before'] and PAGE_ROW['after'] and 'content_b64' not in PAGE_ROW
REPL = PAGE_ROW['replace']
assert 14 <= len(REPL) <= 16 and all(c == 1 for a, b, c in REPL), 'unexpected replacements'
for a, b, c in REPL:
    assert a and a != b, 'empty or no-op replacement'
    for bad in ('<script', 'mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<?'):
        assert bad not in a.lower() and bad not in b.lower(), 'touches tracking or contacts: ' + bad
assert REPL[0][0].startswith('<span class="v-duct-k">') and 'vent-kadr-1-do' in REPL[1][1]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def target(rel, new=False):
    assert rel in IMAGES + [PAGE] and not rel.startswith('/') and '..' not in rel.split('/') and '\\' not in rel
    p = ROOT / rel
    assert p.parent.is_dir() and ROOT in p.parent.resolve().parents, rel
    assert not p.is_symlink(), rel
    if not new:
        assert p.is_file(), rel
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
    tmp = p.with_name(p.name + '.kamera-20261117-stage')
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
        p = target(row['file'], new=True)
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
        assert sha(old) == row['before'], 'CURRENT FILE CHANGED: ' + row['file'] + ' ' + sha(old)[:12]
        mode = p.stat().st_mode & 0o777
    new = result(row, old)
    assert sha(new) == row['after'], 'PACKAGE MISMATCH: ' + row['file']
    plan.append((row, p, old, new, mode))
print('PRECHECK OK: %d/%d original and resulting checksums verified (9 new images, 1 page, %d replacements)'
      % (N, N, len(REPL)))
if MODE == '--check':
    sys.exit(0)

assert not BACKUP.exists(), 'BACKUP ALREADY EXISTS: do not overwrite'
BACKUP.mkdir()
b = BACKUP / PAGE
b.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(str(target(PAGE)), str(b))
assert sha(b.read_bytes()) == PAGE_ROW['before']
print('BACKUP OK: 1/1 page outside public_html')

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
    print('PUBLISHED: %d/%d checksums verified (9 images, 1 page)' % (N, N))
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
