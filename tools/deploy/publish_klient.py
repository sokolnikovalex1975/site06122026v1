#!/usr/bin/env python3
"""Client-side fixes and no dimming on inner pages on phones (pravki dlya klienta): publication on Timeweb (18.11.2026).

Run next to deploy_payload.json, outside public_html: --check (default), --publish, --rollback.
The package is built by tools/deploy/prepare-2026-11-18-klient.py from the current files of the live site.

The script applies exact replacements from the package to public_html: style.css (3: phone rules without dimming -
no CTA background, no photo overlay, no dimmed words, light hero photo band; 44 px tap areas), app.min.js (7: request
confirmation in the middle of the screen, entrance animations finished at the anchor target, no dimmed words on phones),
every page: version ?v=20261117shapka -> ?v=20261118klient of style.css and app.min.js (legal.css keeps its version);
the home page also gets the tap area rule in its hero-scroll-st styles. Only the agreed replacement pairs are allowed
(SHA-256 of each pair is in ALLOWED_PAIRS); counters (Metrika, UIS, Radist), phone and e-mail are not touched.
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
assert PAYLOAD['name'] == 'klient-2026-11-18'
assert (PAYLOAD['old_version'], PAYLOAD['new_version']) == ('20261117shapka', '20261118klient')
ROWS = PAYLOAD['files']
N = len(ROWS)
PAGES = ROWS[2:]
assert N == PAYLOAD['count'] == len(PAGES) + 2 and 30 <= len(PAGES) <= 60, 'unexpected number of files: %d' % N
assert len(set(r['file'] for r in ROWS)) == N
assert ROWS[0]['file'] == 'style.css' and len(ROWS[0]['replace']) == 3
assert ROWS[1]['file'] == 'app.min.js' and len(ROWS[1]['replace']) == 7
ALLOWED_PAIRS = {
    '60cd12c8ebad81bd3de73b6a9f2b38f650a6732257bc7ff41c7ff232fe9c0949',  # pages: app.min.js ?v=
    '7c1be570609bd488822476617ac4d8c7505cb3f245c473e630b8ba136a427cfc',  # pages: style.css ?v=
    '5c1e73d01f90abb7927e55d68d73a4848aca2d3300bcd53d3e3cbe8df1da14f0',  # style.css: phone, no dimming (hero photo band, no overlay, .tl-img, [data-scrub])
    'ba4a94b59e7be85c0bbb2ff4df6776d36f4d10b0b84e34df853b684e72589797',  # style.css: phone, no CTA background
    '142a56411e4fefa880cb343225b55ce66fb12208bf61adfda36f725ea60c4cf2',  # style.css: low phone screen, tap areas 44 px
    'c590dfcf5f6371ba163df26629a07357915a837252a9e96495c1632ef1ee7789',  # app.min.js: __pcok (confirmation on screen)
    '976b9cd7ee0d020f181fc5f968c0c6593d95633aee77cde5bc8bd637de143a77',  # app.min.js: demo submit -> __pcok
    '196872a65c125992b5d6349db72c0757a5b0f244f7b02556077798c39af4a2a3',  # app.min.js: submit success -> __pcok
    'f6b9664a1728f7b6cc0f0e79b3244e2107aafc0320ca76530e4606f4db668e91',  # app.min.js: [data-scrub] not on phone
    'f08811002c5f3af614acebe7de08e558ad2dbba2f76de7a3328b5952007eafe8',  # app.min.js: pcAnchor __pcfin
    '1cfa2947551b40ac975124f7270b7e4246dad1de7dc94be8df3e5ed3ff46a446',  # app.min.js: pcAnchor end -> __pcfin
    'f2fdd1ba14dd20291964a812504f570b1f29a02ca64a9b04fe6dbdacd4c642c4',  # app.min.js: pcAnchor settle -> __pcfin
    '7444fefa9c667c4cc7ff5a3dfa731e467dbc99088ae05f2140e9cac049cf73ae',  # home style hero-scroll-st: tap areas 44 px
}
APP_V = ['app.min.js?v=20261117shapka', 'app.min.js?v=20261118klient']
CSS_V = ['style.css?v=20261117shapka', 'style.css?v=20261118klient']
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
        assert len(r['replace']) == 2 and all(c == 1 for a, b, c in r['replace'][1:]), r['file']
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
    tmp = p.with_name(p.name + '.klient-20261118-stage')
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
