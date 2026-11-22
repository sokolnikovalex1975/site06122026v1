#!/usr/bin/env python3
"""SEO fixes from the 17.11.2026 audit (owner approval 18.11.2026 13:53 MSK): publication on Timeweb (package seo-2026-11-22).

Run next to deploy_payload.json, outside public_html: --check (default), --publish, --rollback.
The package is built by tools/deploy/prepare-2026-11-22-seo.py from the current files of the live site.

What changes (and nothing else):
  * 43 pages index.php (+ privacy, soglasie): footer links to 7 lab services and 3 lab articles; on 14 pages also the
    home title, 21 in-text links, 6 text blocks, structured data and og:image tags - exact replacements from
    deploy_payload.json ("replace"), every pair is in ALLOWED_PAIRS, the number of occurrences is checked;
  * search-index.json (site search rebuilt from the resulting pages), sitemap.xml (lastmod), .htaccess (redirect of a
    folder address without the trailing slash, 301 for /index.php, ErrorDocument 404) - whole new content;
  * new files: 404.html (own "page not found"), img/home-og.jpg, img/pishchevoe-og.jpg, img/pest-menedzhment-og.jpg -
    they must not exist yet.
Every file is checked by SHA-256 before and after (the package content was checked against the owner's laws when it was
built). Metrika 113675622, UIS, Radist, the phone and e-mail links must stay exactly as they are (counted in every page
before and after). New files are written first, .htaccess last. The backup
is kept outside public_html and never overwritten; on any error already replaced files are restored and new files
removed. A repeated run after a successful publication only verifies checksums. Rollback never overwrites a file changed
by another deployment. No f-strings (Python 3.6 on the server), no downloads, passwords or third-party packages;
messages are ASCII (LANG=C).
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
assert PAYLOAD['name'] == 'seo-2026-11-22'
ROWS = PAYLOAD['files']
N = len(ROWS)
assert N == PAYLOAD['count'] == 50, 'unexpected number of files'

PAGES = [
    'index.php', 'dezinfektsiya/index.php', 'deratizatsiya/index.php', 'zashchita-ot-proniknoveniya-gryzunov/index.php',
    'dezinsektsiya/index.php', 'deratizatsiya-i-dezinsektsiya/index.php', 'dogovor-deratizatsiya-dezinsektsiya/index.php',
    'sanitarnyy-audit/index.php', 'razrabotka-ppk/index.php', 'laboratornye-issledovaniya/index.php',
    'ochistka-dezinfektsiya-ventilyatsii/index.php', 'pishchevoe-proizvodstvo/index.php', 'restorany-i-kafe/index.php',
    'magaziny-i-torgovye-seti/index.php', 'gostinitsy/index.php', 'farmatsevticheskie-proizvodstva/index.php',
    'sklady-i-logistika/index.php', 'biznes-tsentry-torgovye-tsentry-predpriyatiya/index.php', 'materialy/index.php',
    'materialy/programma-pest-kontrolya/index.php', 'materialy/zhurnal-pest-kontrolya/index.php',
    'materialy/pest-menedzhment-ili-razovaya-obrabotka/index.php',
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/index.php', 'normativnaya-baza/index.php',
    'normativnaya-baza/proverochnye-listy/index.php', 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/index.php',
    'normativnaya-baza/effektivnost-deratizatsii-i-dezinsektsii/index.php',
    'materialy/akt-deratizatsii-i-dezinsektsii/index.php', 'materialy/skhema-tochek-pest-kontrolya/index.php',
    'dezinsektsiya/restorany-i-kafe/index.php', 'deratizatsiya/restorany-i-kafe/index.php',
    'laboratornye-issledovaniya/analiz-smyvov/index.php', 'laboratornye-issledovaniya/izmerenie-mikroklimata/index.php',
    'laboratornye-issledovaniya/zamer-osveshchennosti/index.php',
    'laboratornye-issledovaniya/analiz-vozdukha-rabochey-zony/index.php',
    'laboratornye-issledovaniya/analiz-pishchevykh-produktov/index.php', 'laboratornye-issledovaniya/analiz-vody/index.php',
    'laboratornye-issledovaniya/kontrol-sterilizatorov/index.php', 'materialy/kak-berut-smyvy/index.php',
    'materialy/zamer-osveshchennosti-i-mikroklimata/index.php', 'materialy/kontrol-raboty-sterilizatorov/index.php',
    'privacy/index.php', 'soglasie/index.php',
]
CONTENT = ['search-index.json', 'sitemap.xml', '.htaccess']
NEW = ['404.html', 'img/home-og.jpg', 'img/pishchevoe-og.jpg', 'img/pest-menedzhment-og.jpg']
FILES = NEW + PAGES + ['search-index.json', 'sitemap.xml'] + ['.htaccess']  # order of writing: new files first, .htaccess last
assert [r['file'] for r in ROWS] == FILES, 'unexpected files'
LEGAL = ('privacy/index.php', 'soglasie/index.php')
ALLOWED_PAIRS = {  # sha256(old + '\x00' + new) of every allowed replacement, written by prepare-2026-11-22-seo.py
    '01df99de99bd7f77cd237b590e0a64a53623b30aa3406c4b2ef112117cd3bca2',
    '099512d27a7d1b663a770db10572ca6a4e0d8f4bc8ffcea3bab64e1c0d913139',
    '0ba54a12b8b8e7b122e3f46ecc4a873cc300bbe08fda32aa43a420b69fe76dfd',
    '0c0d8f580799771a250ce36b5c94cdbdf612a6ff96482888ccbada938a4fc29c',
    '1b1a25db0163e860a170dec53bfbc5dc1e12b74f72276557aa145160ce946c3d',
    '2214039bca73e7aa5af3fe3586bf164f9e87e2e42c14f0c8c36c21d305c89370',
    '23ca4a90790aee6ec20df937cc06e700e7718385b96b6ac619e8e2e6f781b0ec',
    '2c685b9ee00e4cc96a27c50e0e1caa04e3819c6c5d007b8ec4532852cceee7db',
    '2f3bfd50c47cef3d9da76ba87336934701f23bb7265a64169d75b4c82e79454c',
    '34e3bea09fb48c38572211697be393f4c3fb101d949e2efa6f6f6757292c0ef3',
    '3f0131fd0bd52014fd41f63716cd8d7fefcfa336b785e8c0796f9f1568d5ca3a',
    '46a228f02c1293857ba3953bb3d5f240e281ad048d835ca98852fbebfb916ac6',
    '4855cd13e188c73aa9511799c8a7c586efb49d2c53242ba50f6c18000e6662f3',
    '4bddedc632b7d94832271ef7577582ee14e02c3165964bf44c6a0f0c27e7ae18',
    '4fbd1df107b16f0d31b3e7604ddae8a11d1bdfaa03dad3e7b8ec382d12015d9f',
    '5b53f38269752e703b8ad17a3b33138b42fae9c9b9bf5db0b9cc9a292f3d5bd5',
    '628749f926e05eca8f1775fab47367a677c8b79d47efeaf3e08aa5a66d2ba8b1',
    '67834c5526cad366dc6031a2e9597d338b19df6ca6c0f7e4c655ea389002d9f8',
    '6bc027685f72fb772d4962ae2d0d714f5ce01ba6e859096ba79bc5d833eb8538',
    '814d9f4251ab6e81f760cdec828cdaca987a0fcf59e391d70c388f13f175b8d3',
    '82abafab58fe88a3257fe1248ea2478e4ed5fbb587150c8e7cae139969db2743',
    '82b5558d0b1572ff1f1425e95a2dc3e4e5f43ef5d158bf040eb02a396eedd80f',
    '843228bf43efb36b8bb340f66d558f265777e2cbc9880671bdf57df0e42f1046',
    '86710ebb99cfe55c0106585bc921a3293b4dbe3fae540649c8a07dfdf376b963',
    '9cbf257aed1920499c95bd724b2ca780837b7035faed8242d3a296a30c2c991e',
    'a07a987dce7a5073f91ec60995150b526e1f9043141779036dc4188bd447f3d3',
    'a19ea8658c1d8ff245001fa7569cb8f395a956b11e56acc0c02e15f403062e58',
    'a1f505f8232a60b238d68fde97d29b5f6097e7ae940e108f3686409a6b83c59a',
    'a6f704c76e725791efe3fa15d5592691b2277c7c7059ed128817bcf7004c19d3',
    'a7287addb7b571984b12e67ffae419ccfc46907c39c352ab73fc7f0f77357526',
    'b97a4b8a939cc34cedb94456407462fb589fc8a3f9830fd0340fc2894ee6474b',
    'b9dfaf32d202a0f3f1166864de8ea5e0a0599aebfd1f3e6d3cc3b9ee9a7d4a4f',
    'ba1805c9a974797195996dd0d3dc2bfe8cd1f5740b7a7a3bf4f718ed93f9015c',
    'ba23b27fa6fa04bf3311d710cba92ebe9ee90c08654434d1c8d10022f1744527',
    'bbfdf79c3d876ec16b0531691cf044782b1cc3d1f626e2389c802843e3c4b204',
    'bd4c199db0836d005455eeb52f40b6633638d92e48f5d5bc3914f96e9d02f438',
    'bf41549ee689becf661175f9adf45817dd4bb3259c604037a5008c44d36c5c5e',
    'c182ddda96fa4f83567765f318d299d6771ec4b69b1937ba1508fd331e386238',
    'c88dd116275c03101ef42b854b9796299b2ee3a2767743847fd26abafef9b843',
    'cb23eca1978698ebfb13a37378d6488a298189562542628eff20c7a04c29b6ed',
    'd6a74ab6d80bff8797d5dbc61a5b0c56dbf9a96d6213f2d296d24e757a67e367',
    'd70986e8685848e12c6c5789a067f306275e9b97ad5b455785f3c2b5bf758c44',
    'd96b1c9b822a5a69c89c2ac4d356dc72166e40efca8a0357b68a2e26230a748b',
    'dd6a865636497f550b3446aa9aefb7f01a51e4213c88ee45cb505fcf268e7bc7',
    'e43a7ea98b813f2550078f3f609f4789bc0b14262bc1641761ddb52412d4ef11',
    'e556db9f7e6500db97e1fb2c66c3a8088b6263c8571005f2c3669cf4e6b6afb2',
    'e74d6725a3d0a251e963a99adc341e0e8e3f44321591cc6d4ef5c0ab4ba8d294',
    'e9367a9875964353d7c1bbcc62d50220312d7bdc6a00bc67a87660748fc9f68f',
    'f1bc7975f969b82d4042b50ea58d43ff727c3da7487d89d26eb671e4c680b019',
    'f2407e92911e090d45a6b20d6b8037fb46aaa115a24014f799cbd34607ac0508',
    'f8abf3057d35b8d9a231e57deb962f29607180f1176142654465533b56bf7549',
    'fa1654075e5692f433109ac34613d432973e248a0277d47561739532f0aa3027',
    'fb3e4c709e8be7f11d74919332a74d7511c0ce0eb024d06a8be10ab50fef53f9',
}
# Counters and contacts: the same number of occurrences before and after in every page (owner's law of counters).
KEEP = ('mc.yandex.ru/metrika/tag.js', 'ym(113675622', 'mc.yandex.ru/watch/113675622', 'uiscom', 'comagic', 'radist',
        'href="tel:+74951043570"', 'href="mailto:b2b@pestcontrol-center.ru"', '<script', '<?')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pair_id(old, new):
    return sha((old + '\x00' + new).encode('utf-8'))


def target(rel):
    assert rel in FILES and not rel.startswith('/') and '..' not in rel.split('/'), rel
    p = ROOT / rel
    assert ROOT in p.resolve().parents or p.parent.resolve() == ROOT, rel
    return p


def current(rel):
    p = target(rel)
    return sha(p.read_bytes()) if p.is_file() else None


def check_text(rel, old, new):
    if rel == '404.html':
        assert 'ym(113675622' in new and 'name="robots" content="noindex"' in new, 'BAD 404 PAGE'
    if rel.endswith('.php'):
        assert '<?php' not in new and '<?=' not in new, 'PHP CODE: ' + rel
        if rel not in LEGAL:
            assert 'mc.yandex.ru/metrika/tag.js' in new and 'ym(113675622' in new, 'METRIKA MISSING: ' + rel
        for k in KEEP:
            assert old.count(k) == new.count(k), 'COUNTERS OR CONTACTS CHANGED: ' + rel + ' ' + k


def result(row):
    """Resulting bytes of the file (verified against the package checksum) and current bytes (or None)."""
    rel = row['file']
    p = target(rel)
    cur = p.read_bytes() if p.is_file() else None
    if row['kind'] == 'new':
        assert cur is None, 'FILE ALREADY EXISTS: ' + rel
        new = base64.b64decode(row['content_b64'])
    else:
        assert cur is not None and not p.is_symlink(), 'MISSING: ' + rel
        assert sha(cur) == row['before'], 'CURRENT FILE CHANGED: ' + rel + ' ' + sha(cur)[:12]
        if row['kind'] == 'replace':
            text = cur.decode('utf-8')
            for old, new_, count in row['replace']:
                assert pair_id(old, new_) in ALLOWED_PAIRS, 'REPLACEMENT NOT ALLOWED: ' + rel
                assert text.count(old) == count, 'COUNT CHANGED: ' + rel
                text = text.replace(old, new_)
            new = text.encode('utf-8')
        else:
            new = base64.b64decode(row['content_b64'])
    assert sha(new) == row['after'], 'PACKAGE MISMATCH: ' + rel
    if not rel.endswith('.jpg'):
        check_text(rel, cur.decode('utf-8') if cur is not None else None, new.decode('utf-8'))
    else:
        assert new[:3] == b'\xff\xd8\xff' and len(new) < 400000, 'NOT A JPEG: ' + rel
    return cur, new


def write(p, data, mode):
    tmp = p.with_name(p.name + '.seo-20261122-stage')
    assert not tmp.exists(), str(tmp)
    with tmp.open('wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(str(tmp), mode)
    os.replace(str(tmp), str(p))


if MODE == '--rollback':
    assert BACKUP.is_dir(), 'NO BACKUP'
    state = json.loads(STATUS.read_text()) if STATUS.exists() else {}
    done = state.get('done', FILES)
    for row in ROWS:
        if row['file'] in done and row['kind'] != 'new':
            # Never overwrite an unrelated version changed by another deployment.
            assert current(row['file']) in (row['before'], row['after']), 'CHANGED SINCE PUBLICATION: ' + row['file']
    restored = removed = 0
    for row in reversed(ROWS):
        rel = row['file']
        if rel not in done:
            continue
        p = target(rel)
        if row['kind'] == 'new':
            if p.is_file() and sha(p.read_bytes()) == row['after']:
                p.unlink()
                removed += 1
            continue
        b = BACKUP / rel
        data = b.read_bytes()
        assert sha(data) == row['before'], 'BAD BACKUP: ' + rel
        write(p, data, b.stat().st_mode & 0o777)
        restored += 1
    STATUS.write_text(json.dumps({'status': 'rolled_back_by_command', 'done': []}))
    print('ROLLED BACK: %d files restored, %d new files removed' % (restored, removed))
    sys.exit(0)

if all(current(r['file']) == r['after'] for r in ROWS):
    print('ALREADY PUBLISHED: %d/%d checksums match' % (N, N))
    sys.exit(0)

plan = []
for row in ROWS:
    cur, new = result(row)
    p = target(row['file'])
    plan.append((row, p, cur, new, (p.stat().st_mode & 0o777) if cur is not None else 0o644))
print('PRECHECK OK: %d/%d checksums verified (%d pages, %d whole files, %d new files)'
      % (N, N, len(PAGES), len(CONTENT), len(NEW)))
if MODE == '--check':
    sys.exit(0)

assert not BACKUP.exists(), 'BACKUP ALREADY EXISTS: do not overwrite'
BACKUP.mkdir()
for row, p, cur, new, mode in plan:
    if cur is None:
        continue
    b = BACKUP / row['file']
    b.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(p), str(b))
    assert sha(b.read_bytes()) == row['before']
print('BACKUP OK: %d/%d existing files outside public_html' % (N - len(NEW), N - len(NEW)))

done = []
try:
    for row, p, cur, new, mode in plan:
        if cur is None:
            assert not p.exists(), 'CONCURRENT CHANGE: ' + row['file']
        else:
            assert sha(p.read_bytes()) == row['before'], 'CONCURRENT CHANGE: ' + row['file']
        write(p, new, mode)
        done.append(row['file'])
        assert sha(p.read_bytes()) == row['after']
    assert all(current(r['file']) == r['after'] for r in ROWS)
    STATUS.write_text(json.dumps({'status': 'published', 'done': done}, indent=2))
    print('PUBLISHED: %d/%d checksums verified' % (N, N))
    print('BACKUP: ' + str(BACKUP))
except BaseException:
    for row, p, cur, new, mode in reversed(plan):
        if row['file'] not in done:
            continue
        if cur is None:
            if p.is_file():
                p.unlink()
        else:
            write(p, cur, mode)
    STATUS.write_text(json.dumps({'status': 'rolled_back', 'done': []}))
    print('AUTOMATIC ROLLBACK: %d files' % len(done))
    raise
