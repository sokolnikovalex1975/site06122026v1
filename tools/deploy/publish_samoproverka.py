#!/usr/bin/env python3
"""Самопроверка на телефоне: выкладка на Timeweb (17.11.2026).

Запуск рядом с deploy_payload.json, вне public_html: --check (по умолчанию), --publish, --rollback.
Пакет готовит tools/deploy/prepare-2026-11-17-samoproverka.py из актуальных страниц рабочего сайта.

Скрипт сам применяет к 13 страницам с блоком самопроверки (index.php) по 2 точные замены: блок <section id="samoproverka">
-> новый блок и сразу после него <script id="f-check-js">; строка <style id="mob-fit"> -> перед ней <style id="f-check-m">.
Разрешены только замены такого вида (проверяется ниже): блок самопроверки на блок самопроверки с одним скриптом
f-check-js, строка стилей f-check-m перед mob-fit; счётчики Метрики, UIS и Radist, телефон и почта заменами не
затрагиваются. До и после сверяется SHA-256 каждого файла (при подготовке пакета обратная замена проверена байт в байт),
резервные копии сохраняются вне public_html и не перезаписываются, при любой ошибке уже заменённые файлы возвращаются.
Повторный запуск после успешной выкладки только сверяет суммы. Без f-строк (на сервере Python 3.6), загрузок, паролей
и сторонних пакетов; сообщения — ASCII (LANG=C).
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
assert PAYLOAD['name'] == 'samoproverka-2026-11-17'
ROWS = PAYLOAD['files']
N = len(ROWS)
FILES = [s + '/index.php' for s in (
    'restorany-i-kafe', 'gostinitsy', 'pishchevoe-proizvodstvo', 'deratizatsiya', 'sklady-i-logistika',
    'magaziny-i-torgovye-seti', 'biznes-tsentry-torgovye-tsentry-predpriyatiya', 'farmatsevticheskie-proizvodstva',
    'ochistka-dezinfektsiya-ventilyatsii', 'dezinsektsiya', 'materialy/zhurnal-pest-kontrolya',
    'materialy/programma-pest-kontrolya', 'materialy/pest-menedzhment-ili-razovaya-obrabotka')]
assert N == PAYLOAD['count'] == 13 and [r['file'] for r in ROWS] == FILES, 'unexpected files'
TRACK = ('mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<select', '<?')
MOB_FIT = '<style id="mob-fit">'
for r in ROWS:
    assert r['before'] != r['after'] and len(r['replace']) == 2, r['file']
    (sec_old, sec_new, c1), (st_old, st_new, c2) = r['replace']
    assert c1 == c2 == 1, r['file']
    for s in (sec_old, sec_new, st_old, st_new):
        for bad in TRACK:
            assert bad not in s.lower(), 'touches tracking or contacts: ' + bad + ' ' + r['file']
    assert sec_old.startswith('<section') and 'id="samoproverka"' in sec_old.split('>', 1)[0], r['file']
    assert sec_old.endswith('</section>') and sec_old.count('<section') == 1, r['file']
    assert '<script' not in sec_old.lower() and '<style' not in sec_old.lower(), r['file']
    assert sec_new.split('>', 1)[0] == sec_old.split('>', 1)[0], 'section tag changed: ' + r['file']
    body, script = sec_new.split('</section>\n<script id="f-check-js">')
    assert sec_new.count('<section') == 1 and sec_new.lower().count('<script') == 1, r['file']
    assert script.endswith('</script>') and script.count('</script>') == 1 and '<style' not in sec_new.lower()
    assert st_old == MOB_FIT and st_new.startswith('<style id="f-check-m">/* '), r['file']
    assert '#samoproverka .f-check-list' in st_new and '{' in st_new
    assert st_new.endswith('</style>\n' + MOB_FIT) and st_new.count('<style') == 2 and '<script' not in st_new.lower()


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
    tmp = p.with_name(p.name + '.samoproverka-20261117-stage')
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
        if row['file'] in names:
            # Never overwrite an unrelated version changed by another deployment.
            assert sha(target(row['file']).read_bytes()) in (row['before'], row['after']), \
                'CHANGED SINCE PUBLICATION: ' + row['file']
    for row in reversed(ROWS):
        if row['file'] not in names:
            continue
        p = target(row['file'])
        b = (BACKUP / row['file']).read_bytes()
        assert sha(b) == row['before']
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
