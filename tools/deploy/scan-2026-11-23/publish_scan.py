#!/usr/bin/env python3
"""Scan line (.panel-scan) runs through the whole block to the bottom edge: publication on Timeweb (23.11.2026).

Run next to deploy_payload.json, outside public_html: --check (default), --publish, --rollback.
The package is built by tools/deploy/prepare-2026-11-23-scan.py from the current files of the live site.

The script applies exact replacements from the package to public_html: style.css (2: the .panel-scan layer takes the
full height of the block, @keyframes scan moves it from above the top edge to below the bottom edge), the home page
(the same 2 rules in its inline styles), every other page with a style.css link, including 404.html: version
?v=20261118klient -> ?v=20261123scan of style.css (app.min.js and legal.css keep their versions). Only the agreed
replacement pairs are allowed (SHA-256 of each pair is in ALLOWED_PAIRS); counters (Metrika, UIS, Radist), phone and
e-mail are not touched. style.css is replaced first, then the pages. SHA-256 of every file is verified before and
after, the backup is kept outside public_html and never overwritten, on any error already replaced files are
restored. A repeated run after a successful publication only verifies checksums. Rollback never overwrites a file
changed by another deployment. No f-strings (Python 3.6 on the server), no downloads, passwords or third-party
packages; messages are ASCII (LANG=C).
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
assert PAYLOAD['name'] == 'scan-2026-11-23'
assert (PAYLOAD['old_version'], PAYLOAD['new_version']) == ('20261118klient', '20261123scan')
ROWS = PAYLOAD['files']
N = len(ROWS)
PAGES = ROWS[1:]
assert N == PAYLOAD['count'] == len(PAGES) + 1 and 30 <= len(PAGES) <= 60, 'unexpected number of files: %d' % N
assert len(set(r['file'] for r in ROWS)) == N
assert ROWS[0]['file'] == 'style.css' and len(ROWS[0]['replace']) == 2
ALLOWED_PAIRS = {
    '4291c056f8d8a0dfd1f0a723c0014cb979ce87e58e85c28b10281038e78e9420',  # style.css: .panel-scan full height of the block
    'fcf7119af6d25997cfcfcd6f777b4b1bacee753286ca16447ef24aac9515c9a1',  # style.css: @keyframes scan to the bottom edge
    'be971384a28aa3579c262a836293a8e56a9d70b1edc5b50a245ea57d709b8fb6',  # home styles: .panel-scan full height of the block
    'ad6f7ea3927ae53a9fb05ccef28861322dee7a91f48aca92761268606951b8a9',  # home styles: @keyframes scan to the bottom edge
    'b3970ec882dfb5c08931c281f681c3e48d002aa3bd3ff95140fae277d754ddf2',  # pages: style.css ?v=
}
CSS_V = ['style.css?v=20261118klient', 'style.css?v=20261123scan']
for r in ROWS:
    assert r['before'] and r['after'] and r['before'] != r['after'] and r['replace'], r['file']
    for old, new, count in r['replace']:
        assert old != new and count == 1, r['file']
        assert hashlib.sha256((old + '\x00' + new).encode('utf-8')).hexdigest() in ALLOWED_PAIRS, \
            'replacement not allowed: ' + r['file']
        for bad in ('<script', '</script', 'mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', 'metrika'):
            assert bad not in old.lower() and bad not in new.lower(), 'touches tracking or contacts: ' + bad
HOME = 0
for r in PAGES:
    assert r['file'] in ('index.php', '404.html') or r['file'].endswith('/index.php'), r['file']
    if r['file'] == 'index.php':
        HOME += 1
        assert len(r['replace']) == 2 and all(x[0] != CSS_V[0] for x in r['replace']), r['file']
    else:
        assert len(r['replace']) == 1 and r['replace'][0][:2] == CSS_V, r['file']
assert HOME == 1, 'home page missing'
assert any(r['file'] == '404.html' for r in PAGES), '404.html missing'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def target(rel):
    assert not rel.startswith('/') and '..' not in rel.split('/') and '\\' not in rel, rel
    p = ROOT / rel
    assert p.is_file() and not p.is_symlink(), rel
    assert ROOT in p.resolve().parents, rel
    return p


def apply(text, row):
    out = text
    for old, new, count in row['replace']:
        assert out.count(old) == count, 'COUNT CHANGED: ' + row['file'] + ' ' + old[:40]
        out = out.replace(old, new)
    return out


def replace(p, data, mode):
    tmp = p.with_name(p.name + '.scan-20261123-stage')
    assert not tmp.exists(), str(tmp)
    with tmp.open('wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(str(tmp), mode)
    os.replace(str(tmp), str(p))


if MODE == '--rollback':
    assert BACKUP.is_dir(), 'NO BACKUP'
    state = json.loads(STATUS.read_text(encoding='utf-8')) if STATUS.exists() else {}
    names = state.get('promoted', [r['file'] for r in ROWS])
    done = 0
    for row in reversed(ROWS):
        if row['file'] not in names:
            continue
        p = target(row['file'])
        b = (BACKUP / row['file']).read_bytes()
        assert sha(b) == row['before'], 'BACKUP DAMAGED: ' + row['file']
        cur = sha(p.read_bytes())
        # Never overwrite an unrelated version changed by another deployment.
        assert cur in (row['before'], row['after']), 'CHANGED SINCE PUBLICATION: ' + row['file']
        if cur != row['before']:
            replace(p, b, (BACKUP / row['file']).stat().st_mode & 0o777)
        done += 1
    STATUS.write_text(json.dumps({'status': 'rolled_back_by_command', 'promoted': []}), encoding='utf-8')
    print('ROLLED BACK: %d/%d files' % (done, len(names)))
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
    assert '<?php' not in text and '<?=' not in text, 'PHP IN FILE: ' + row['file']
    new = apply(text, row).encode('utf-8')
    assert sha(new) == row['after'], 'PACKAGE MISMATCH: ' + row['file']
    plan.append((row, p, old, new, p.stat().st_mode & 0o777))
print('PRECHECK OK: %d/%d original and resulting checksums verified (style.css, %d pages)' % (N, N, len(PAGES)))
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
    STATUS.write_text(json.dumps({'status': 'published', 'promoted': promoted}, indent=1), encoding='utf-8')
    print('PUBLISHED: %d/%d checksums verified' % (N, N))
    print('BACKUP: ' + str(BACKUP))
except BaseException:
    for row, p, old, new, mode in reversed(plan):
        if row['file'] in promoted:
            replace(p, old, mode)
    STATUS.write_text(json.dumps({'status': 'rolled_back', 'promoted': []}), encoding='utf-8')
    print('AUTOMATIC ROLLBACK: %d files' % len(promoted))
    raise
