#!/usr/bin/env python3
"""Stranica "Razrabotka PPK" bez frazy "a esli nuzhen vyezd - posle vyezda": vykladka na Timeweb (20.11.2026, paket ppk-bez-vyezda-2026-11-20).

Zapusk ryadom s deploy_payload.json, vne public_html: --check (po umolchaniyu), --publish, --rollback.
Paket gotovit tools/deploy/prepare-2026-11-20-ppk-bez-vyezda.py iz aktualnyh fajlov rabochego sajta.

Dva fajla: razrabotka-ppk/index.php (blok sroka, otvet FAQ i FAQPage) i search-index.json (opisanie voprosa #q2) -
tolko udalenie frazy, drugih izmenenij net.
Schetchiki Metriki, UIS i Radist, telefon i pochta ne zatragivayutsya (proveryaetsya nizhe). Do i posle sveryaetsya SHA-256,
rezervnaya kopiya - vne public_html i ne perezapisyvaetsya, pri lyuboj oshibke fajl vozvrashchaetsya. Povtornyj zapusk posle
uspeshnoj vykladki tolko sveryaet summy. Python 3.6, bez f-strok, soobshcheniya ASCII.
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
assert PAYLOAD['name'] == 'ppk-bez-vyezda-2026-11-20'
ROWS = PAYLOAD['files']
N = len(ROWS)
FILES = ['razrabotka-ppk/index.php', 'search-index.json']
assert N == PAYLOAD['count'] == 2 and [r['file'] for r in ROWS] == FILES, 'unexpected files'
PHRASES = ('\u0430\u00a0\u0435\u0441\u043b\u0438 \u043d\u0443\u0436\u0435\u043d \u0432\u044b\u0435\u0437\u0434\u00a0',
           '\u0430 \u0435\u0441\u043b\u0438 \u043d\u0443\u0436\u0435\u043d \u0432\u044b\u0435\u0437\u0434 ')
TRACK = ('mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<select', '<?', 'fetch(', 'xmlhttp',
         '<link', '@import', 'url(', 'src=', '<script', '<style')
for r in ROWS:
    assert r['before'] != r['after'] and len(r['replace']) == (2 if r['file'].endswith('.php') else 1), r['file']
    for o, n, c in r['replace']:
        assert c in (1, 2) and any(p in o for p in PHRASES) and not any(p in n for p in PHRASES), r['file']
        assert (len(n) < len(o) or r['file'] == 'search-index.json') and o.count('<') == n.count('<'), r['file']
        for bad in TRACK:
            assert bad not in o.lower() and bad not in n.lower(), 'replacement touches ' + bad + ' ' + r['file']


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
    tmp = p.with_name(p.name + '.ppk-bez-vyezda-20261120-stage')
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
