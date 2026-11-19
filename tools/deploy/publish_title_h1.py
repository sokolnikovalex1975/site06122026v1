#!/usr/bin/env python3
"""Title и H1 с запросом семантического ядра на 12 страницах (PR #1): выкладка на Timeweb (19.11.2026).

Запуск рядом с deploy_payload.json, вне public_html: --check (по умолчанию), --publish, --rollback.
Пакет готовит tools/deploy/prepare-2026-11-19-title-h1.py из актуальных файлов рабочего сайта.

Скрипт сам применяет к 12 страницам public_html точные замены: прежний <title> (и name в разметке WebPage) → новый
(TITLE_CORE, tools/site/meta_titles.py) и прежний H1 → новый (tools/site/h1_core.py); разрешена только 21 согласованная
пара замен (суммы SHA-256 пар — в ALLOWED_PAIRS), число вхождений каждой — как при подготовке. До и после сверяется
SHA-256 каждого файла (обратная замена проверена при подготовке байт в байт, счётчики Метрики, UIS и Radist, телефон и
почта не затрагиваются), резервная копия сохраняется вне public_html и не перезаписывается, при любой ошибке уже
заменённые файлы возвращаются. Повторный запуск после успешной выкладки только сверяет суммы. Откат не трогает файл,
изменённый другой выкладкой. Без f-строк (на сервере Python 3.6), загрузок, паролей и сторонних пакетов; сообщения —
ASCII (LANG=C).
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
assert PAYLOAD['name'] == 'title-h1-2026-11-19'
ROWS = PAYLOAD['files']
N = len(ROWS)
FILES = [
    'deratizatsiya-i-dezinsektsiya/index.php',
    'dezinfektsiya/index.php',
    'laboratornye-issledovaniya/index.php',
    'laboratornye-issledovaniya/analiz-pishchevykh-produktov/index.php',
    'laboratornye-issledovaniya/analiz-smyvov/index.php',
    'laboratornye-issledovaniya/kontrol-sterilizatorov/index.php',
    'laboratornye-issledovaniya/zamer-osveshchennosti/index.php',
    'materialy/kak-berut-smyvy/index.php',
    'materialy/programma-pest-kontrolya/index.php',
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/index.php',
    'materialy/skhema-tochek-pest-kontrolya/index.php',
    'materialy/zamer-osveshchennosti-i-mikroklimata/index.php',
]
assert N == PAYLOAD['count'] == 12 and [r['file'] for r in ROWS] == FILES, 'unexpected files'
ALLOWED_PAIRS = {
    '1bf1ea5e7665871cc93d300b00db9aa472fb174e690b671b2c22b99d2b23b76a',
    '1eb1e909dc56eaf7293870703b8636b24cc780ae72a2f14a00844592a51cd8f4',
    '24dbfb0c546ca8b089ff3fdee8021b4eaca288f0789c69b6831e60367e86c927',
    '2ad2bf26e4439fd3a4b6ef7ce97c996d226d2a4298252b1a5af20793729ffd17',
    '387ac5958cde6020782ac123ae915127f7afb527535bcb3d075b26131baf436c',
    '487f2df3b9606c93ecaf29f8dcbdd8c6e68372d206c858f494c81cbb2c80d98c',
    '53b5d79120074ccbcb3a3a92c66f0183857560c2c84ee7b16dcd2ae9ab2ac829',
    '61de63bf824ebc4b7a66eb34b10904838a6adcdeb91d65c3ed19beef6fd8a769',
    '7d81ca53a2e3393577036bc975e4bb2044b77de7f736ceea39488f0d0aa81ea8',
    '8782197fe0538f306c6b9bd38f288c15aaaaea41aa491cb7315cc7ce961fba84',
    '896575d70197eadfbad389ebe9d2d15cbb8597d95c5b58757c9632e8d7a094ba',
    '89c8770a824e5174aec97924e9987dd96f2348c88ea59f6159e92727a70c484f',
    '9f93ac41c1c30ed634020e66c178ecfc6dd7eac18c91700dc7cc175d32299f5d',
    'a06c1a60ac59c8392a384c500defd07bf88f05e9769e070aa2ca9662473dc4d7',
    'b706039d73badf2c778917c406e251cbab45a3ff567be81ad33a264d8ca90a60',
    'ba34a46e8d50267a5ef773b185c901df89de9f82d0932151a891c82670061e81',
    'bf24f0e561224dae7c261f6b42db37484ebf888420027a7f29df40f13793bbc9',
    'd91bc7cfe6b6021260eb2e1c0565270ba82c708b1e937c7db1453193207a7494',
    'ddb017a3098911e5bc75ea28ce57e12d2a54f7c0c58f58eab7f0da7b08f96beb',
    'ea3ad40fa0d66bf12f6dec8afe9de5ac1e5d712ac54a48548718c5fc1b9ce7b6',
    'f13ca7e2a37ce04c37c8dd5ccb583de63d852cc9275af6092bd01a7b87b68d5c',
}
for r in ROWS:
    assert r['before'] != r['after'] and r['replace'], r['file']
    for old, new, count in r['replace']:
        assert 1 <= count <= 3 and old != new, r['file']
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
    tmp = p.with_name(p.name + '.title-h1-20261119-stage')
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
