#!/usr/bin/env python3
"""«Мухи и мелкие мушки» и вид объекта без звёздочки в заявках со страниц ресторанов: выкладка на Timeweb (16.11.2026).

Запуск рядом с deploy_payload.json, вне public_html: --check (по умолчанию), --publish, --rollback.
Пакет готовит tools/deploy/prepare-2026-11-16-mushki.py из актуальных файлов рабочего сайта.

Скрипт сам применяет к 7 файлам public_html (6 страниц и search-index.json) точные замены из deploy_payload.json;
разрешены только 6 согласованных пар (суммы SHA-256 пар — в ALLOWED_PAIRS): «Мухи и дрозофилы» → «Мухи и мелкие мушки»
(с прописной и строчной, с обычным и неразрывным пробелом, с &nbsp;) и строка «Вид объекта» без звёздочки в скрипте формы страниц ресторанов.
До и после сверяется SHA-256 каждого файла (при подготовке пакета обратная замена проверена байт в байт, счётчики
Метрики, UIS и Radist не затрагиваются), резервная копия сохраняется вне public_html и не перезаписывается, при любой
ошибке уже заменённые файлы возвращаются. Повторный запуск после успешной выкладки только сверяет суммы.
Без f-строк (на сервере Python 3.6), загрузок, паролей и сторонних пакетов; сообщения — ASCII (LANG=C).
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
assert PAYLOAD['name'] == 'mushki-2026-11-16'
ROWS = PAYLOAD['files']
N = len(ROWS)
FILES = ['index.php', 'restorany-i-kafe/index.php', 'pishchevoe-proizvodstvo/index.php', 'dezinsektsiya/index.php',
         'dezinsektsiya/restorany-i-kafe/index.php', 'deratizatsiya/restorany-i-kafe/index.php', 'search-index.json']
assert N == PAYLOAD['count'] == 7 and [r['file'] for r in ROWS] == FILES, 'unexpected files'
ALLOWED_PAIRS = {
    '0c5b2423df2a5d48ca751bd225788452472dfd5bfd0a3d3e67d146e946b666b0',
    '13be325bf5b425e5061ad6ae9456e403399c28aae7e120ce59c216efe1cc0796',
    '1c1f076f58446cfaf68ef6a2a8f96fa664affd57c320d924fa6ea48bf12f04b7',
    '40c46374d021fcdf4120ede6c850bd14088d220fec8602dc85d706c8f5d560a6',
    '6f33844a9d2d793c5234424c07857eb5dcc975cdc9ad7f2d9319ed539312b412',
    '79367672209b84398dfdef406db28a643a8ce253789068023ad056a8e08c8769',
}
for r in ROWS:
    assert r['before'] != r['after'] and r['replace'], r['file']
    for old, new, count in r['replace']:
        assert 1 <= count <= 4 and old != new, r['file']
        assert hashlib.sha256((old + '\x00' + new).encode('utf-8')).hexdigest() in ALLOWED_PAIRS, \
            'replacement not allowed: ' + r['file']
        for bad in ('<script', 'mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<select'):
            assert bad not in old.lower() and bad not in new.lower(), 'touches tracking or contacts: ' + bad


def sha(b):
    return hashlib.sha256(b).hexdigest()


def target(rel):
    assert rel in FILES and not rel.startswith('/') and '..' not in rel.split('/')
    p = ROOT / rel
    assert p.is_file() and not p.is_symlink(), rel
    assert ROOT in p.resolve().parents
    return p


def apply(s, row):
    out = s
    for old, new, count in row['replace']:
        assert out.count(old) == count, 'COUNT CHANGED: ' + row['file']
        out = out.replace(old, new)
    return out


def replace(p, data, mode):
    tmp = p.with_name(p.name + '.mushki-20261116-stage')
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
    for row in reversed(ROWS):
        if row['file'] not in names:
            continue
        p = target(row['file'])
        b = (BACKUP / row['file']).read_bytes()
        assert sha(b) == row['before']
        # Never overwrite an unrelated version changed by another deployment.
        assert sha(p.read_bytes()) in (row['before'], row['after']), 'CHANGED SINCE PUBLICATION: ' + row['file']
        replace(p, b, (BACKUP / row['file']).stat().st_mode & 0o777)
    STATUS.write_text(json.dumps({'status': 'rolled_back_by_command', 'promoted': []}))
    print('ROLLED BACK: ' + str(len(names)))
    sys.exit(0)

if all(sha(target(r['file']).read_bytes()) == r['after'] for r in ROWS):
    print('ALREADY PUBLISHED: %d/%d checksums match' % (N, N))
    sys.exit(0)

plan = []
for row in ROWS:
    p = target(row['file'])
    old = p.read_bytes()
    assert sha(old) == row['before'], 'CURRENT FILE CHANGED: ' + row['file'] + ' ' + sha(old)[:12]
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
    for row, p, old, new, mode in reversed(plan):
        if row['file'] in promoted:
            replace(p, old, mode)
    STATUS.write_text(json.dumps({'status': 'rolled_back', 'promoted': []}))
    print('AUTOMATIC ROLLBACK: ' + str(len(promoted)))
    raise
