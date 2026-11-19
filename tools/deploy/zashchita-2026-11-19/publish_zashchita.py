#!/usr/bin/env python3
"""New page "Zashchita ot proniknoveniya gryzunov" (rodent proofing): publication on Timeweb (19.11.2026).

Run next to deploy_payload.json, outside public_html: --check (default), --publish, --rollback.
The package is built by tools/deploy/prepare-2026-11-19-zashchita.py from the current files of the live site:
new files (the page index.php, contours.js, contours.svg, missing images) must not exist yet; changed files
(deratizatsiya/index.php - one link inserted, sitemap.xml - one <url>, search-index.json - entries of the new page)
must have the "before" SHA-256 and get the "after" SHA-256. Counters Metrika, UIS, Radist, phone and e-mail untouched.
New files are written first, then the changed files. The backup of the pages is kept outside public_html and never overwritten;
on any error already replaced pages are restored and created images removed. A repeated run after a successful
publication only verifies checksums. Rollback never overwrites a file changed by another deployment.
No f-strings (Python 3.6 on the server), no downloads, passwords or third-party packages; messages are ASCII (LANG=C).
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
assert MODE in ('--check', '--publish', '--rollback')
assert ROOT.is_dir() and str(ROOT).endswith('/pestcontrol-center/public_html')
assert ROOT not in WORK.parents and ROOT != WORK, 'keep the package outside the public site'
assert PAYLOAD['name'] == 'zashchita-2026-11-19'
ROWS = PAYLOAD['files']
N = len(ROWS)
PAGES = [r for r in ROWS if r['before']]
IMAGES = [r for r in ROWS if not r['before']]
assert N == PAYLOAD['count']
NEW_RE = re.compile(r'^(zashchita-ot-proniknoveniya-gryzunov/(index\.php|contours\.(js|svg))|img/[a-z0-9-]+\.(webp|jpg|png|svg))$')
CHANGED = ('deratizatsiya/index.php', 'sitemap.xml', 'search-index.json')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def target(row, must_exist):
    rel = row['file']
    assert not rel.startswith('/') and '..' not in rel.split('/')
    assert (NEW_RE.match(rel) if not row['before'] else rel in CHANGED), 'unexpected file: ' + rel
    p = ROOT / rel
    if must_exist:
        assert p.is_file() and not p.is_symlink(), 'MISSING: ' + rel
    assert ROOT in p.resolve().parents
    return p


def content(row):
    b = base64.b64decode(row['content_b64'])
    if row['file'].endswith('.php'):
        t = b.decode('utf-8')
        assert '<?php' not in t and '<?=' not in t and 'mc.yandex.ru/metrika/tag.js' in t, row['file']
    assert sha(b) == row['after'], 'PACKAGE MISMATCH: ' + row['file']
    return b


def write(p, data, mode):
    tmp = p.with_name(p.name + '.zashchita-20261119-stage')
    assert not tmp.exists(), str(tmp)
    with tmp.open('wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(str(tmp), mode)
    os.replace(str(tmp), str(p))


def current(row):
    p = ROOT / row['file']
    return sha(p.read_bytes()) if p.is_file() else None


if MODE == '--rollback':
    assert BACKUP.is_dir()
    state = json.loads(STATUS.read_text()) if STATUS.exists() else {}
    pages = state.get('pages', [r['file'] for r in PAGES])
    images = state.get('images', [r['file'] for r in IMAGES])
    for row in PAGES:
        if row['file'] in pages:
            # Never overwrite an unrelated version changed by another deployment.
            assert current(row) in (row['before'], row['after']), 'CHANGED SINCE PUBLICATION: ' + row['file']
    for row in PAGES:
        if row['file'] not in pages:
            continue
        p = target(row, True)
        b = (BACKUP / row['file']).read_bytes()
        assert sha(b) == row['before']
        write(p, b, (BACKUP / row['file']).stat().st_mode & 0o777)
    removed = 0
    for row in IMAGES:
        p = target(row, False)
        if row['file'] in images and p.is_file() and sha(p.read_bytes()) == row['after']:
            p.unlink()
            removed += 1
    d = ROOT / 'zashchita-ot-proniknoveniya-gryzunov'
    if d.is_dir() and not any(d.iterdir()) and state.get('created_dir'):
        d.rmdir()
    STATUS.write_text(json.dumps({'status': 'rolled_back_by_command', 'pages': [], 'images': []}))
    print('ROLLED BACK: %d changed files, %d new files removed' % (len(pages), removed))
    sys.exit(0)

if all(current(r) == r['after'] for r in ROWS):
    print('ALREADY PUBLISHED: %d/%d checksums match (%d changed, %d new)' % (N, N, len(PAGES), len(IMAGES)))
    sys.exit(0)

plan = []
for row in ROWS:
    p = target(row, bool(row['before']))
    new = content(row)
    cur = current(row)
    if row['before']:
        assert cur == row['before'], 'CURRENT FILE CHANGED: ' + row['file'] + ' ' + str(cur)[:12]
        old = p.read_bytes()
        plan.append((row, p, old, new, p.stat().st_mode & 0o777))
    else:
        assert cur is None, 'FILE ALREADY EXISTS: ' + row['file']
        plan.append((row, p, None, new, 0o644))
print('PRECHECK OK: %d/%d checksums verified (%d changed, %d new)' % (N, N, len(PAGES), len(IMAGES)))
if MODE == '--check':
    sys.exit(0)

assert not BACKUP.exists(), 'BACKUP ALREADY EXISTS: do not overwrite'
BACKUP.mkdir()
for row, p, old, new, mode in plan:
    if old is None:
        continue
    b = BACKUP / row['file']
    b.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(p), str(b))
    assert sha(b.read_bytes()) == row['before']
print('BACKUP OK: %d/%d changed files outside public_html' % (len(PAGES), len(PAGES)))

pages, images = [], []
img_dir = ROOT / 'zashchita-ot-proniknoveniya-gryzunov'
created_dir = not img_dir.exists()
try:
    img_dir.mkdir(mode=0o755, exist_ok=True)
    for row, p, old, new, mode in plan:  # new files first
        if old is None:
            assert not p.exists(), 'CONCURRENT CHANGE: ' + row['file']
            write(p, new, mode)
            images.append(row['file'])
            assert sha(p.read_bytes()) == row['after']
    for row, p, old, new, mode in plan:
        if old is not None:
            assert sha(p.read_bytes()) == row['before'], 'CONCURRENT CHANGE: ' + row['file']
            write(p, new, mode)
            pages.append(row['file'])
            assert sha(p.read_bytes()) == row['after']
    assert all(current(r) == r['after'] for r in ROWS)
    STATUS.write_text(json.dumps({'status': 'published', 'pages': pages, 'images': images,
                                  'created_dir': created_dir}, indent=2))
    print('PUBLISHED: %d/%d checksums verified (%d changed, %d new)' % (N, N, len(pages), len(images)))
    print('BACKUP: ' + str(BACKUP))
except BaseException:
    for row, p, old, new, mode in reversed(plan):
        if old is not None and row['file'] in pages:
            write(p, old, mode)
    for row, p, old, new, mode in plan:
        if old is None and row['file'] in images and p.is_file():
            p.unlink()
    if created_dir and img_dir.is_dir() and not any(img_dir.iterdir()):
        img_dir.rmdir()
    STATUS.write_text(json.dumps({'status': 'rolled_back', 'pages': [], 'images': []}))
    print('AUTOMATIC ROLLBACK: %d changed, %d new' % (len(pages), len(images)))
    raise
