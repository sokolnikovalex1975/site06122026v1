#!/usr/bin/env python3
"""Krug "IPM - cikl vizita" zakreplen pri prokrutke: vykladka na Timeweb (19.11.2026, paket ipm-pin-2026-11-19).

Zapusk ryadom s deploy_payload.json, vne public_html: --check (po umolchaniyu), --publish, --rollback.
Paket gotovit tools/deploy/prepare-2026-11-19-ipm-pin.py iz aktualnyh stranic rabochego sajta.

Glavnaya (index.php) i "Deratizaciya" (deratizatsiya/index.php): po 2 tochnye zameny -
  1) pered <style id="tel-plain"> - stroka <style id="ipm-pin"> (tolko stili kruga);
  2) sekciya #podhod: klass appr-pin, id="cycleNum", tochka kolca cycle-dot, i srazu posle sekcii - <script id="ipm-pin-js"> (bez seti i schetchikov).
Schetchiki Metriki, UIS i Radist, telefon i pochta ne zatragivayutsya (proveryaetsya nizhe). Do i posle sveryaetsya SHA-256
kazhdogo fajla, rezervnye kopii - vne public_html i ne perezapisyvayutsya, pri lyuboj oshibke uzhe zamenennye fajly
vozvrashchayutsya. Povtornyj zapusk posle uspeshnoj vykladki tolko sveryaet summy. Python 3.6, bez f-strok, soobshcheniya ASCII.
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
assert MODE in ('--check', '--publish', '--rollback'), MODE
assert ROOT.is_dir() and str(ROOT).endswith('/pestcontrol-center/public_html'), str(ROOT)
assert ROOT not in WORK.parents and ROOT != WORK, 'keep the package outside the public site'
assert PAYLOAD['name'] == 'ipm-pin-2026-11-19'
ROWS = PAYLOAD['files']
N = len(ROWS)
FILES = ['index.php', 'deratizatsiya/index.php']
assert N == PAYLOAD['count'] == 2 and [r['file'] for r in ROWS] == FILES, 'unexpected files'
TRACK = ('mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<select', '<?', 'fetch(', 'xmlhttp',
         '<link', '@import', 'url(', 'src=')
for r in ROWS:
    assert r['before'] != r['after'] and len(r['replace']) == 2, r['file']
    (o1, n1, c1), (o2, n2, c2) = r['replace'][0], r['replace'][1]
    assert c1 == c2 == 1, r['file']
    for bad in TRACK:
        assert bad not in o1.lower() and bad not in n1.lower(), 'style touches ' + bad + ' ' + r['file']
    assert o1 == '<style id="tel-plain">' and n1.endswith(o1) and n1.startswith('<style id="ipm-pin">'), r['file']
    assert n1[:-len(o1)].count('<style') == 1 and '<script' not in n1, r['file']
    assert o2.startswith('<section class="s" id="podhod">') and o2.endswith('</section>\n') and o2.count('<section') == 1, r['file']
    assert n2.startswith('<section class="s" id="podhod">') and n2.count('<script') == 1, r['file']
    i = n2.index('<script id="ipm-pin-js">')
    sec, js = n2[:i], n2[i:]
    assert sec.endswith('</section>\n') and js.endswith('</script>\n') and js.count('</script>') == 1, r['file']
    for bad in ('mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<?', 'fetch(', 'xmlhttp', 'src=', '<link'):
        assert bad not in js.lower(), 'script touches ' + bad + ' ' + r['file']
    # sekciya: tolko klass, id nomera i tochka kolca
    assert sec.replace('<div class="wrap appr appr-pin">', '<div class="wrap appr">', 1).replace(
        'id="cycleNum"', 'id="cycleStep"', 1).replace('<div class="cycle-dot" id="cycleDot"></div>', '', 1) == o2, r['file']


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
    tmp = p.with_name(p.name + '.ipm-pin-20261119-stage')
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
