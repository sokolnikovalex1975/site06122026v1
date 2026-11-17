#!/usr/bin/env python3
"""Compact sticky header (kompaktnaya zakreplyonnaya shapka): publication on Timeweb (17.11.2026).

Run next to deploy_payload.json, outside public_html: --check (default), --publish, --rollback.
The package is built by tools/deploy/prepare-2026-11-17-shapka.py from the current files of the live site.

The script applies exact replacements from the package to public_html: style.css (3: header rules with the compact
header, scroll-padding-top from the compact header height, 0.15 s hover delay of the header dropdowns), app.min.js
(7: header scroll handler, media query and focus, compact header height in window.pcAnchor, 0.8 s anchor scroll),
every page: version ?v=20261117zagolovok -> ?v=20261117shapka of style.css and app.min.js (legal.css keeps its version);
the home page also gets the same 3 CSS replacements in its inline styles. Only the agreed replacement pairs are allowed (SHA-256
of each pair is in ALLOWED_PAIRS); counters (Metrika, UIS, Radist), phone and e-mail are not touched.
style.css and app.min.js are replaced first, then the pages. SHA-256 of every file is verified before and after,
the backup is kept outside public_html and never overwritten, on any error already replaced files are restored.
A repeated run after a successful publication only verifies checksums. Rollback never overwrites a file changed by
another deployment. No f-strings (Python 3.6 on the server), no downloads, passwords or third-party packages;
messages are ASCII (LANG=C).
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
assert PAYLOAD['name'] == 'shapka-2026-11-17'
assert (PAYLOAD['old_version'], PAYLOAD['new_version']) == ('20261117zagolovok', '20261117shapka')
ROWS = PAYLOAD['files']
N = len(ROWS)
PAGES = ROWS[2:]
assert N == PAYLOAD['count'] == len(PAGES) + 2 and 30 <= len(PAGES) <= 60, 'unexpected number of files: %d' % N
assert len(set(r['file'] for r in ROWS)) == N
assert ROWS[0]['file'] == 'style.css' and len(ROWS[0]['replace']) == 3
assert ROWS[1]['file'] == 'app.min.js' and len(ROWS[1]['replace']) == 7
ALLOWED_PAIRS = {
    '033488d646343722989475315a8130a0ef52a2f5b2707dd545a6868cbeffdf90',  # pages: app.min.js ?v=
    '4e22cec54c9c5df723414c196c6d7ac7d1a03a82552b02b8edcf6e9b0b378b94',  # pages: style.css ?v=
    'db705c887b1ccf0fc650fa9e1e84069d98aa25c295d047d6dd16cfe3ecba51e7',  # style.css: scroll-padding-top
    '74ad980699561f4f727643355b44df27d7b3ccc0deccb3710906491291e95f36',  # style.css: header, compact header
    '07df4ac26681b250ce354efed114fb46ed32f26d6a77d431a4bae7e173809eeb',  # style.css: dropdown hover delay
    '9da9bf9cab443665fc9e9bd424e2d32ed98cf8cc12899967400bc5720cb23597',  # app.min.js: header scroll handler
    'c6056b30a0e7df8434ea27daafc01bf169ebb7f0e713325dfe5ad73ecefb8e43',  # app.min.js: focus, media query change
    '04c73a1a2a85c4446305a2d3512907b7158da33b4b2504793f6cd6761fb159c1',  # app.min.js: anchor scroll 0.8 s (no pcAnchor)
    '7d30b82e3a949731acc05e62f5f5ddef8951f3c0679bc94a6f70d6abfd49bbd0',  # app.min.js: pcAnchor compact header height
    '5773aff1ed16392f276c66380bb55c727b045595efe542e3c856287ffed30db0',  # app.min.js: pcAnchor anchorY
    '919e4f14f628907b59c71ac368f30334275cf8f97725f5cf26c01d4767e844b4',  # app.min.js: pcAnchor to top 0.8 s
    '77e774944f8f895ef9e046597526c2bac14b6e997a89c24d5423d562abc59577',  # app.min.js: pcAnchor 0.8 s
    'fc76f895a45ee01079840a7858e089a280a507a7a51ed17049f30a9eb7faf43e',  # home inline CSS: scroll-padding-top
    'd9b9b9ec73f4e00f78434c42fb4e49ee86072c0783aa071032d2afe47b046598',  # home inline CSS: header
    '51478ece6ebd1f74c6ebf1745135a6a815ce7cafdc72675d63dfb2e09622dd4f',  # home inline CSS: dropdown hover delay
}
APP_V = ['app.min.js?v=20261117zagolovok', 'app.min.js?v=20261117shapka']
CSS_V = ['style.css?v=20261117zagolovok', 'style.css?v=20261117shapka']
for r in ROWS:
    assert r['before'] and r['after'] and r['before'] != r['after'] and r['replace'], r['file']
    for old, new, count in r['replace']:
        assert old != new and isinstance(count, int), r['file']
        assert hashlib.sha256((old + '\x00' + new).encode('utf-8')).hexdigest() in ALLOWED_PAIRS, \
            'replacement not allowed: ' + r['file']
        for bad in ('<script', '</script', 'mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', 'metrika'):
            assert bad not in old.lower() and bad not in new.lower(), 'touches tracking or contacts: ' + bad
for r in ROWS[:2]:
    assert all(c == 1 for a, b, c in r['replace']), r['file']
HOME = 0
for r in PAGES:
    assert r['file'] == 'index.php' or r['file'].endswith('/index.php'), r['file']
    a, b, c = r['replace'][0]
    assert [a, b] == APP_V and c in (1, 2), r['file']
    if r['file'] == 'index.php':
        HOME += 1
        assert len(r['replace']) == 4 and all(c == 1 for a, b, c in r['replace'][1:]), r['file']
        assert all(x[0] != CSS_V[0] for x in r['replace']), r['file']
    else:
        assert len(r['replace']) == 2 and r['replace'][1][:2] == CSS_V and r['replace'][1][2] == 1, r['file']
assert HOME == 1, 'home page missing'


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
    tmp = p.with_name(p.name + '.shapka-20261117-stage')
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
print('PRECHECK OK: %d/%d original and resulting checksums verified (style.css, app.min.js, %d pages)' % (N, N, len(PAGES)))
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
