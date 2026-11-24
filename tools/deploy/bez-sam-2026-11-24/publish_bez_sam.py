#!/usr/bin/env python3
"""Pravki bez samostoyatelnyh rabot (24.11.2026, paket bez-sam-2026-11-24): 14 stranic, search-index.json, sitemap.xml.

Zapusk ryadom s deploy_payload.json, vne public_html: --check (po umolchaniyu), --publish, --rollback.
Paket gotovit tools/deploy/prepare-2026-11-24-bez-sam.py. Vse fajly - full: summa SHA-256 do vykladki dolzhna
sovpast s paketom. Na kazhdoj stranice index.php do i posle: net PHP-koda; kod Metriki 113675622, UIS i Radist -
rovno odin raz; telefon i pochta v ssylkah. Rezervnaya kopiya - vne public_html i ne perezapisyvaetsya; pri lyuboj
oshibke uzhe zamenennye fajly vozvrashchayutsya. Python 3.6, bez f-strok, zagruzok, parolej; soobshcheniya ASCII.
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
assert PAYLOAD['name'] == 'bez-sam-2026-11-24'
ROWS = PAYLOAD['files']
N = len(ROWS)
assert N == PAYLOAD['count'], N
LEGAL = ('privacy/index.php', 'soglasie/index.php')
NEW_OK = re.compile(r'^$')  # new files are not expected
SKIP = ('.htaccess', 'send.php')
TEL = 'href="tel:+74951043570"'
MAIL = 'href="mailto:b2b@pestcontrol-center.ru"'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def page_ok(rel, b, version=None):
    s = b.decode('utf-8')
    assert '<?php' not in s and '<?=' not in s, 'PHP CODE: ' + rel
    if rel in LEGAL:
        assert 'mc.yandex.ru/metrika' not in s, 'COUNTER ON LEGAL PAGE: ' + rel
        return
    assert s.count("ym(113675622, 'init'") == 1, 'METRIKA: ' + rel
    assert s.count('mc.yandex.ru/watch/113675622') == 1, 'METRIKA NOSCRIPT: ' + rel
    assert s.count('uiscom.ru/static/cs.min.js') == 1, 'UIS: ' + rel
    assert s.count('radist.me/tracker.min.js') == 1, 'RADIST: ' + rel
    assert TEL in s and MAIL in s, 'CONTACTS: ' + rel
    if version:
        assert ('.min.js?v=' + version) in s or ('.css?v=' + version) in s, 'VERSION: ' + rel


CONTENT = {}
kinds = {'new': 0, 'full': 0}
for r in ROWS:
    f = r['file']
    assert not f.startswith('/') and '..' not in f.split('/') and r['after'], f
    assert f.split('/')[-1] not in SKIP, f
    kinds[r['kind']] += 1
    if r['kind'] == 'new':
        assert r['before'] is None and NEW_OK.match(f), f
    else:
        assert r['kind'] == 'full' and r['before'] and r['before'] != r['after'], f
    b = base64.b64decode(r['content_b64'].encode('ascii'))
    assert sha(b) == r['after'], 'PACKAGE CONTENT MISMATCH: ' + f
    if f.endswith('index.php'):
        page_ok(f, b, PAYLOAD['version'])
    CONTENT[f] = b
assert sum(1 for r in ROWS if r['file'].endswith('index.php')) == PAYLOAD['pages']


def target(rel):
    p = ROOT / rel
    assert str(p.resolve()).startswith(str(ROOT) + '/'), rel
    return p


def write(p, data, mode):
    tmp = p.with_name(p.name + '.bezsam-20261124-stage')
    assert not tmp.exists(), str(tmp)
    with tmp.open('wb') as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.chmod(str(tmp), mode)
    os.replace(str(tmp), str(p))


def current(rel):
    p = ROOT / rel
    return sha(p.read_bytes()) if p.is_file() else None


if MODE == '--rollback':
    assert BACKUP.is_dir()
    for row in ROWS:
        # Never overwrite an unrelated version changed by another deployment.
        assert current(row['file']) in (row['before'], row['after']), 'CHANGED SINCE PUBLICATION: ' + row['file']
    n = 0
    for row in reversed(ROWS):
        p = ROOT / row['file']
        if row['kind'] == 'new':
            if p.is_file():
                p.unlink()
                n += 1
        elif current(row['file']) == row['after']:
            b = (BACKUP / row['file']).read_bytes()
            assert sha(b) == row['before']
            write(p, b, (BACKUP / row['file']).stat().st_mode & 0o777)
            n += 1
    STATUS.write_text(json.dumps({'status': 'rolled_back_by_command'}))
    print('ROLLED BACK: ' + str(n))
    sys.exit(0)

if all(current(r['file']) == r['after'] for r in ROWS):
    print('ALREADY PUBLISHED: %d/%d checksums match' % (N, N))
    sys.exit(0)

plan = []
for row in ROWS:
    rel = row['file']
    p = target(rel)
    if row['kind'] == 'new':
        assert not p.exists(), 'ALREADY EXISTS: ' + rel
        assert p.parent.is_dir(), 'NO DIR: ' + rel
        plan.append((row, p, None, CONTENT[rel], 0o644))
        continue
    assert p.is_file() and not p.is_symlink(), 'MISSING: ' + rel
    old = p.read_bytes()
    assert sha(old) == row['before'], 'CURRENT FILE CHANGED: ' + rel + ' ' + sha(old)[:12]
    if rel.endswith('index.php'):
        page_ok(rel, old)
    plan.append((row, p, old, CONTENT[rel], p.stat().st_mode & 0o777))
print('PRECHECK OK: %d/%d original and resulting checksums verified (%d replaced, %d new)'
      % (N, N, kinds['full'], kinds['new']))
if MODE == '--check':
    sys.exit(0)

assert not BACKUP.exists(), 'BACKUP ALREADY EXISTS: do not overwrite'
BACKUP.mkdir()
nb = 0
for row, p, old, new, mode in plan:
    if old is None:
        continue
    b = BACKUP / row['file']
    b.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(p), str(b))
    assert sha(b.read_bytes()) == row['before']
    nb += 1
print('BACKUP OK: %d/%d outside public_html' % (nb, kinds['full']))

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
    assert all(current(r['file']) == r['after'] for r in ROWS)
    STATUS.write_text(json.dumps({'status': 'published', 'promoted': promoted}, indent=2))
    print('PUBLISHED: %d/%d checksums verified' % (N, N))
    print('BACKUP: ' + str(BACKUP))
except BaseException:
    for row, p, old, new, mode in reversed(plan):
        if row['file'] in promoted:
            if old is None:
                p.unlink()
            else:
                write(p, old, mode)
    STATUS.write_text(json.dumps({'status': 'rolled_back', 'promoted': []}))
    print('AUTOMATIC ROLLBACK: ' + str(len(promoted)))
    raise
