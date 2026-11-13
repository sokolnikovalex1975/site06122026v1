#!/usr/bin/env python3
"""Title и description главной (вариант А + описание 1а): выкладка на Timeweb из SSH-консоли (13.11.2026).

Запуск рядом с deploy_payload.json, вне public_html: --check (по умолчанию), --publish, --rollback.
Пакет готовит tools/deploy/prepare-2026-11-13-home-title.py из актуальной главной рабочего сайта.

Скрипт сам применяет к public_html/index.php четыре точные замены из пакета: <title>, <meta name="description">,
<meta property="og:title"> и name/description/dateModified разметки WebPage. До и после сверяется SHA-256 (при
подготовке пакета обратная замена проверена байт в байт, счётчики Метрики, UIS и Radist не затрагиваются), резервная
копия сохраняется вне public_html и не перезаписывается, при ошибке файл возвращается. Повторный запуск после успешной
выкладки только сверяет сумму. Без f-строк (на сервере Python 3.6), загрузок, паролей и сторонних пакетов.
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
assert PAYLOAD['name'] == 'home-title-2026-11-13' and PAYLOAD['count'] == 1 and len(PAYLOAD['files']) == 1
ROW = PAYLOAD['files'][0]
assert ROW['file'] == 'index.php' and ROW['before'] != ROW['after'] and not ROW['append']
assert len(ROW['replace']) == 4
STARTS = ('<title>', '<meta name="description" content="', '<meta property="og:title" content="', '"name":"')
for (old, new, count), start in zip(ROW['replace'], STARTS):
    assert old != new and count == 1 and old.startswith(start) and new.startswith(start), start
    for bad in ('<script', 'mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:'):
        assert bad not in old.lower() and bad not in new.lower(), 'touches counters or contacts: ' + bad


def sha(b):
    return hashlib.sha256(b).hexdigest()


def replace(p, data, mode):
    tmp = p.with_name(p.name + '.home-title-20261113-stage')
    assert not tmp.exists(), str(tmp)
    with tmp.open('wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(str(tmp), mode)
    os.replace(str(tmp), str(p))


P = ROOT / 'index.php'
assert P.is_file() and not P.is_symlink()

if MODE == '--rollback':
    b = (BACKUP / 'index.php').read_bytes()
    assert sha(b) == ROW['before']
    # Never overwrite a version changed by another deployment.
    assert sha(P.read_bytes()) in (ROW['before'], ROW['after']), 'CHANGED SINCE PUBLICATION: index.php'
    replace(P, b, (BACKUP / 'index.php').stat().st_mode & 0o777)
    STATUS.write_text(json.dumps({'status': 'rolled_back_by_command'}))
    print('ROLLED BACK: index.php')
    sys.exit(0)

cur = P.read_bytes()
if sha(cur) == ROW['after']:
    print('ALREADY PUBLISHED: index.php checksum matches')
    sys.exit(0)
assert sha(cur) == ROW['before'], 'CURRENT FILE CHANGED: index.php ' + sha(cur)[:12]
text = cur.decode('utf-8')
assert '<?php' not in text and '<?=' not in text
out = text
for old, new, count in ROW['replace']:
    assert out.count(old) == count, 'COUNT CHANGED: ' + old[:60]
    out = out.replace(old, new)
new_bytes = out.encode('utf-8')
assert sha(new_bytes) == ROW['after'], 'PACKAGE MISMATCH: index.php'
print('PRECHECK OK: index.php original and resulting checksums verified (4 head replacements)')
if MODE == '--check':
    sys.exit(0)

assert not BACKUP.exists(), 'BACKUP ALREADY EXISTS: do not overwrite'
BACKUP.mkdir()
shutil.copy2(str(P), str(BACKUP / 'index.php'))
assert sha((BACKUP / 'index.php').read_bytes()) == ROW['before']
print('BACKUP OK: ' + str(BACKUP / 'index.php'))
mode = P.stat().st_mode & 0o777
try:
    assert sha(P.read_bytes()) == ROW['before'], 'CONCURRENT CHANGE: index.php'
    replace(P, new_bytes, mode)
    assert sha(P.read_bytes()) == ROW['after']
    STATUS.write_text(json.dumps({'status': 'published'}))
    print('PUBLISHED: index.php checksum verified')
except BaseException:
    replace(P, cur, mode)
    STATUS.write_text(json.dumps({'status': 'rolled_back'}))
    print('AUTOMATIC ROLLBACK: index.php')
    raise
