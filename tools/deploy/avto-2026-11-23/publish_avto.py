#!/usr/bin/env python3
"""Stranica "Dezinfekciya avtotransporta" (/dezinfektsiya/avtotransport/): vykladka na Timeweb (23.11.2026, paket avto-2026-11-23).

Zapusk ryadom s deploy_payload.json, vne public_html: --check (po umolchaniyu), --publish, --rollback.
Paket gotovit tools/deploy/prepare-2026-11-23-avto.py iz aktualnyh fajlov rabochego sajta.

Tri vida fajlov:
  new  - 12 novyh fajlov (stranica, 2 PDF, 9 kartinok): soderzhimoe v pakete, fajla na sajte byt ne dolzhno;
  page - 43 stranicy index.php: tochnye zameny (punkt menyu, "Vse uslugi", "Smotrite takzhe", ssylki), kazhdaya
         zamena vstrechaetsya rovno 1 raz; schetchiki Metriki, UIS i Radist, telefon, pochta, skripty i formy
         zamenami ne zatragivayutsya (proveryaetsya nizhe);
  full - search-index.json i sitemap.xml: novoe soderzhimoe v pakete.
Do i posle sveryaetsya SHA-256 kazhdogo fajla, rezervnaya kopiya - vne public_html i ne perezapisyvaetsya, pri lyuboj
oshibke uzhe zamenennye fajly vozvrashchayutsya, novye - udalyayutsya. Povtornyj zapusk posle vykladki tolko sveryaet summy.
Python 3.6, bez f-strok, zagruzok, parolej i storonnih paketov; soobshcheniya ASCII.
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
assert PAYLOAD['name'] == 'avto-2026-11-23'
ROWS = PAYLOAD['files']
N = len(ROWS)
assert N == PAYLOAD['count'] == 57, N
NEW_DIR = 'dezinfektsiya/avtotransport'
BAD = ('mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<?', '<script', '<style', '<link',
       '<form', '<input', '<select', 'fetch(', 'xmlhttp')
IMG = re.compile(r'(\.\./)*img/ig-avtotransport-(128|240)\.webp( \d+w, (\.\./)*img/ig-avtotransport-240\.webp \d+w)?$')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def changed_part(old, new):
    k = 0
    while k < min(len(old), len(new)) and old[k] == new[k]:
        k += 1
    e = 0
    while e < min(len(old), len(new)) - k and old[-1 - e] == new[-1 - e]:
        e += 1
    return old[k:len(old) - e], new[k:len(new) - e]


CONTENT = {}
kinds = {'new': 0, 'page': 0, 'full': 0}
for r in ROWS:
    f = r['file']
    assert not f.startswith('/') and '..' not in f.split('/') and r['after'], f
    kinds[r['kind']] += 1
    if r['kind'] == 'new':
        assert r['before'] is None and 'replace' not in r, f
        assert f.startswith(NEW_DIR + '/') or re.match(r'img/(avto-[a-z0-9-]+|ig-avtotransport-(128|240))\.(webp|jpg)$', f), f
    elif r['kind'] == 'full':
        assert f in ('search-index.json', 'sitemap.xml') and r['before'] and 'replace' not in r, f
    else:
        assert r['kind'] == 'page' and f.endswith('index.php') and r['before'] != r['after'] and 'content_b64' not in r, f
        assert r['replace'], f
        for old, new, count in r['replace']:
            assert count == 1 and old != new, f
            a, b = changed_part(old, new)
            for x in (a, b):
                for t in BAD:
                    assert t not in x.lower(), 'replacement touches ' + t + ' ' + f
                for src in re.findall(r'src(?:set)?="([^"]*)"', x):
                    assert IMG.match(src), 'image ' + src + ' ' + f
    if 'content_b64' in r:
        b = base64.b64decode(r['content_b64'].encode('ascii'))
        assert sha(b) == r['after'], 'PACKAGE CONTENT MISMATCH: ' + f
        CONTENT[f] = b
assert kinds == {'new': 12, 'page': 43, 'full': 2}, kinds
page = CONTENT[NEW_DIR + '/index.php'].decode('utf-8')
assert '113675622' in page and 'radist' in page.lower() and '<?php' not in page and '<?=' not in page
assert 'href="tel:+74951043570">+7 (495) 104-35-70</a>' in page
assert 'href="mailto:b2b@pestcontrol-center.ru">b2b@pestcontrol-center.ru</a>' in page


def target(rel, must_exist=True):
    p = ROOT / rel
    assert str(p.resolve()).startswith(str(ROOT) + '/'), rel
    if must_exist:
        assert p.is_file() and not p.is_symlink(), 'MISSING: ' + rel
    return p


def apply(s, row):
    out = s
    for old, new, count in row['replace']:
        assert out.count(old) == count, 'COUNT CHANGED: ' + row['file']
        out = out.replace(old, new)
    return out


def write(p, data, mode):
    tmp = p.with_name(p.name + '.avto-20261123-stage')
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
    d = ROOT / NEW_DIR
    if d.is_dir() and not any(d.iterdir()):
        d.rmdir()
    STATUS.write_text(json.dumps({'status': 'rolled_back_by_command'}))
    print('ROLLED BACK: ' + str(n))
    sys.exit(0)

if all(current(r['file']) == r['after'] for r in ROWS):
    print('ALREADY PUBLISHED: %d/%d checksums match' % (N, N))
    sys.exit(0)

plan = []
for row in ROWS:
    rel = row['file']
    if row['kind'] == 'new':
        assert not (ROOT / rel).exists(), 'ALREADY EXISTS: ' + rel
        plan.append((row, ROOT / rel, None, CONTENT[rel], 0o644))
        continue
    p = target(rel)
    old = p.read_bytes()
    assert sha(old) == row['before'], 'CURRENT FILE CHANGED: ' + rel + ' ' + sha(old)[:12]
    if row['kind'] == 'page':
        text = old.decode('utf-8')
        assert '<?php' not in text and '<?=' not in text
        new = apply(text, row).encode('utf-8')
        assert sha(new) == row['after'], 'PACKAGE MISMATCH: ' + rel
    else:
        new = CONTENT[rel]
    plan.append((row, p, old, new, p.stat().st_mode & 0o777))
assert (ROOT / 'dezinfektsiya').is_dir() and (ROOT / 'img').is_dir()
print('PRECHECK OK: %d/%d original and resulting checksums verified' % (N, N))
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
print('BACKUP OK: %d/%d outside public_html' % (nb, N - 12))

promoted = []
made_dir = False
try:
    d = ROOT / NEW_DIR
    if not d.is_dir():
        d.mkdir(mode=0o755)
        os.chmod(str(d), 0o755)
        made_dir = True
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
    if made_dir and not any((ROOT / NEW_DIR).iterdir()):
        (ROOT / NEW_DIR).rmdir()
    STATUS.write_text(json.dumps({'status': 'rolled_back', 'promoted': []}))
    print('AUTOMATIC ROLLBACK: ' + str(len(promoted)))
    raise
