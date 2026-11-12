#!/usr/bin/env python3
"""Run beside deploy_payload.json outside public_html, with --check/--publish/--rollback.

Compatible with Python 3.4. No credentials, downloads, or third-party packages.
"""
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
assert MODE in ('--check', '--publish', '--rollback')
assert ROOT.is_dir() and str(ROOT).endswith('/pestcontrol-center/public_html')
assert ROOT not in WORK.parents and ROOT != WORK, 'keep the package outside the public site'
ROWS = PAYLOAD['files']
assert len(ROWS) == 42
assert len(set(r['file'] for r in ROWS)) == len(ROWS)
assert any(r['file'] == 'index.php' for r in ROWS)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def target(rel):
    assert not rel.startswith('/') and '..' not in rel.split('/')
    assert rel == 'index.php' or rel.endswith('/index.php')
    p = ROOT / rel
    assert p.is_file() and not p.is_symlink()
    assert ROOT in p.resolve().parents
    return p


def apply(s):
    assert 'id="requisites"' not in s and 'id="ft-company-st"' not in s
    assert s.count('</head>') == 1 and s.count('</footer>') == 1
    style, block = PAYLOAD['style'], PAYLOAD['block']
    uis = s.find('<!-- UIS -->', 0, s.index('</head>'))
    if uis >= 0:
        s = s[:uis] + style + '\n' + s[uis:]
    else:
        s = s.replace('</head>', style + '\n</head>', 1)
    s = s.replace('</footer>', '  ' + block + '\n</footer>', 1)
    back = s.replace(style + '\n', '', 1).replace('  ' + block + '\n', '', 1)
    return s, back


def replace(p, data, mode):
    tmp = p.with_name(p.name + '.footer-20261112-stage')
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
    print('ROLLED BACK: ' + str(len(names)))
    sys.exit(0)

already = all(sha(target(r['file']).read_bytes()) == r['after'] for r in ROWS)
if already:
    print('ALREADY PUBLISHED: 42/42 checksums match')
    sys.exit(0)

plan = []
for row in ROWS:
    p = target(row['file'])
    old = p.read_bytes()
    assert sha(old) == row['before'], 'CURRENT FILE CHANGED: ' + row['file']
    text = old.decode('utf-8')
    assert '<?php' not in text and '<?=' not in text
    result, back = apply(text)
    assert back == text, 'UNRELATED CHANGE: ' + row['file']
    new = result.encode('utf-8')
    assert sha(new) == row['after'], 'PACKAGE MISMATCH: ' + row['file']
    plan.append((row, p, old, new, p.stat().st_mode & 0o777))
print('PRECHECK OK: 42/42 original and resulting checksums verified')
if MODE == '--check':
    sys.exit(0)

assert not BACKUP.exists(), 'BACKUP ALREADY EXISTS: do not overwrite'
BACKUP.mkdir()
for row, p, old, new, mode in plan:
    b = BACKUP / row['file']
    b.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(p), str(b))
    assert sha(b.read_bytes()) == row['before']
print('BACKUP OK: 42/42 outside public_html')

promoted = []
try:
    for row, p, old, new, mode in plan:
        assert sha(p.read_bytes()) == row['before'], 'CONCURRENT CHANGE: ' + row['file']
        replace(p, new, mode)
        promoted.append(row['file'])
        assert sha(p.read_bytes()) == row['after']
    assert all(sha(target(r['file']).read_bytes()) == r['after'] for r in ROWS)
    STATUS.write_text(json.dumps({'status': 'published', 'promoted': promoted}, indent=2))
    print('PUBLISHED: 42/42 checksums verified')
    print('BACKUP: ' + str(BACKUP))
except BaseException:
    for row, p, old, new, mode in plan:
        if row['file'] in promoted:
            replace(p, old, mode)
    STATUS.write_text(json.dumps({'status': 'rolled_back', 'promoted': []}))
    print('AUTOMATIC ROLLBACK: ' + str(len(promoted)))
    raise
