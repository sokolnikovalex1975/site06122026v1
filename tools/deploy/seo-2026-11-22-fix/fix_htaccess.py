#!/usr/bin/env python3
"""Package seo-2026-11-22-fix: refines the /index.php rule in .htaccess published on 22.11.2026 at 22:29 MSK.

Run next to htaccess.new, outside public_html: --check (default), --publish, --rollback.

The rule "/folder/index.php -> 301 /folder/" (package seo-2026-11-22) also fired for folders that do not exist, so
/no-such-folder/index.php answered 301 to an address that answers 404. The new .htaccess adds two conditions: the
redirect fires only when the folder exists; otherwise the address answers 404 with the own 404 page. Nothing else
changes: one file, whole new content (htaccess.new), checked by SHA-256 before and after; the backup is kept outside
public_html and never overwritten; file mode is kept. Rollback restores the 22.11.2026 22:29 version only if
.htaccess still has the content of this package. Full rollback of both packages: this script with --rollback first,
then ~/pestcontrol-seo-2026-11-22/publish_seo.py --rollback. No f-strings (Python 3.6), ASCII messages (LANG=C).
"""
import hashlib
import os
import pathlib
import sys

WORK = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.path.expanduser('~/pestcontrol-center/public_html')).resolve()
TARGET = ROOT / '.htaccess'
NEW = WORK / 'htaccess.new'
BACKUP = WORK / 'htaccess.before'
BEFORE = '3a415f7048da34147e966d33b5064295d4cffff0c9e3125966f8bd29134a291e'  # published 22.11.2026 22:29 MSK
AFTER = '60ac35c80f19875fc7fa924f783b9778e2dd51d9123376c7a31127ca0c3c6fc6'
STAGE = '.htaccess.seo-20261122-fix-stage'
MODE = sys.argv[1] if len(sys.argv) == 2 else '--check'
assert MODE in ('--check', '--publish', '--rollback'), MODE
assert ROOT.is_dir() and str(ROOT).endswith('/pestcontrol-center/public_html'), str(ROOT)
assert ROOT not in WORK.parents and ROOT != WORK, 'keep the package outside the public site'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(data, mode):
    tmp = ROOT / STAGE
    assert not tmp.exists(), 'STAGE FILE EXISTS: ' + str(tmp)
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(str(tmp), mode)
    os.replace(str(tmp), str(TARGET))


new = NEW.read_bytes()
assert sha(new) == AFTER, 'BAD PACKAGE: htaccess.new'
cur = TARGET.read_bytes()
mode = TARGET.stat().st_mode & 0o777

if MODE == '--check':
    if sha(cur) == AFTER:
        print('ALREADY PUBLISHED: .htaccess matches ' + AFTER[:8])
        sys.exit(0)
    if sha(cur) == BEFORE:
        print('PRECHECK OK: .htaccess is the 22.11.2026 22:29 version ' + BEFORE[:8])
        sys.exit(0)
    print('STOP: .htaccess was changed by another deployment: ' + sha(cur)[:8])
    sys.exit(1)

if MODE == '--publish':
    if sha(cur) == AFTER:
        print('ALREADY PUBLISHED: .htaccess matches ' + AFTER[:8])
        sys.exit(0)
    if sha(cur) != BEFORE:
        print('STOP: .htaccess was changed by another deployment: ' + sha(cur)[:8])
        sys.exit(1)
    if not BACKUP.exists():
        fd = os.open(str(BACKUP), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(fd, cur)
            os.fsync(fd)
        finally:
            os.close(fd)
    assert sha(BACKUP.read_bytes()) == BEFORE, 'BAD BACKUP'
    print('BACKUP OK: ' + str(BACKUP))
    try:
        write(new, mode)
        assert sha(TARGET.read_bytes()) == AFTER, 'CHECKSUM AFTER WRITE'
    except Exception as e:
        if (ROOT / STAGE).exists():
            (ROOT / STAGE).unlink()
        if sha(TARGET.read_bytes()) != BEFORE:
            write(BACKUP.read_bytes(), mode)
        print('ERROR, .htaccess restored: ' + repr(e))
        sys.exit(1)
    print('PUBLISHED: .htaccess ' + BEFORE[:8] + ' -> ' + AFTER[:8] + ', mode ' + oct(mode))
    sys.exit(0)

if MODE == '--rollback':
    if sha(cur) == BEFORE:
        print('NOTHING TO ROLL BACK: .htaccess is the 22.11.2026 22:29 version')
        sys.exit(0)
    if sha(cur) != AFTER:
        print('STOP: .htaccess was changed by another deployment: ' + sha(cur)[:8])
        sys.exit(1)
    data = BACKUP.read_bytes()
    assert sha(data) == BEFORE, 'BAD BACKUP'
    write(data, mode)
    assert sha(TARGET.read_bytes()) == BEFORE
    print('ROLLED BACK: .htaccess ' + AFTER[:8] + ' -> ' + BEFORE[:8])
    sys.exit(0)
