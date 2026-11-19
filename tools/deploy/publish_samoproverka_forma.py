#!/usr/bin/env python3
"""Самопроверка → заявка на 13 страницах: кнопка открывает форму, отметки в заявке — выкладка на Timeweb (19.11.2026).

Запуск рядом с deploy_payload.json, вне public_html: --check (по умолчанию), --publish, --rollback.
Пакет готовит tools/deploy/prepare-2026-11-19-samoproverka-forma.py из актуальных файлов рабочего сайта.

Новый файл samoproverka-forma.min.js (содержимое в пакете, сверка SHA-256) и точные замены в 13 страницах index.php:
  * блок <section class="f-checks" id="samoproverka"> — кнопке data-chk-open, под ней строка «Откроется короткая форма…»,
    у секции — настройки окна (data-chk-*); раскладка блока (выложена 17.11.2026) не меняется;
  * сразу после <link … style.css?v=…> — <style id="chk-css">…</style> (стили окна) и
    <script src="…samoproverka-forma.min.js?v=20261119forma" defer></script> (UIS — прямо перед </head>, Radist — в конце <body>).
До и после сверяется SHA-256 каждого файла (при подготовке пакета счётчики Метрики, UIS и Radist, телефон и почта
проверены законом владельца до и после), резервная копия — вне public_html и не перезаписывается, при любой ошибке
уже заменённые файлы возвращаются. Повторный запуск после выкладки только сверяет суммы. Без f-строк (на сервере
Python 3.6), загрузок, паролей и сторонних пакетов; сообщения — ASCII (LANG=C).
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
assert PAYLOAD['name'] == 'samoproverka-forma-2026-11-19'
VERSION = '20261119forma'
ROWS = PAYLOAD['files']
N = len(ROWS)
PAGES = ['materialy/zhurnal-pest-kontrolya', 'materialy/programma-pest-kontrolya',
         'materialy/pest-menedzhment-ili-razovaya-obrabotka', 'deratizatsiya', 'dezinsektsiya',
         'ochistka-dezinfektsiya-ventilyatsii', 'pishchevoe-proizvodstvo', 'restorany-i-kafe', 'magaziny-i-torgovye-seti',
         'sklady-i-logistika', 'farmatsevticheskie-proizvodstva', 'gostinitsy',
         'biznes-tsentry-torgovye-tsentry-predpriyatiya']
assert N == PAYLOAD['count'] == 14 and [r['file'] for r in ROWS] == ['samoproverka-forma.min.js'] + [p + '/index.php' for p in PAGES]
JS_ROW, PAGE_ROWS = ROWS[0], ROWS[1:]
JS = base64.b64decode(JS_ROW['content_b64'].encode('ascii'))
assert JS_ROW['before'] is None and 'replace' not in JS_ROW and hashlib.sha256(JS).hexdigest() == JS_ROW['after']
assert b'data-chk-open' in JS and b'/send.php' in JS and len(JS) < 40000
LINK_RE = re.compile(r'<link rel="stylesheet" href="(?:\.\./)+style\.css\?v=[0-9a-z]+">')
CSS = PAYLOAD['css']
assert CSS.startswith('<style id="chk-css">') and CSS.endswith('</style>\n') and hashlib.sha256(CSS.encode('utf-8')).hexdigest() == PAYLOAD['css_sha256']
BAD = ('mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<select', '<?')
for page, r in zip(PAGES, PAGE_ROWS):
    assert r['before'] and r['after'] and r['before'] != r['after'] and 'content_b64' not in r, r['file']
    kinds = []
    for old, new, count in r['replace']:
        assert count == 1 and old != new, r['file']
        low_old, low_new = old.lower(), new.lower()
        assert not any(b in low_old or b in low_new for b in BAD), 'touches tracking or contacts: ' + r['file']
        if old.startswith('<section class="f-checks" id="samoproverka"'):
            assert old.endswith('</section>') and new.endswith('</section>') and 'data-chk-open' not in old
            assert new.count('data-chk-open') == 1 and 'f-check-tip' in new and '<script' not in low_new and '<script' not in low_old
            assert len(new) - len(old) < 1200, r['file']
            kinds.append('section')
        elif LINK_RE.match(old) and LINK_RE.match(old).group(0) == old:
            depth = page.count('/') + 1
            assert old.startswith('<link rel="stylesheet" href="' + '../' * depth + 'style.css?v=')
            assert new == old + '\n' + CSS + '<script src="' + '../' * depth + 'samoproverka-forma.min.js?v=' + VERSION + '" defer></script>'
            kinds.append('head')
        else:
            raise AssertionError('replacement not allowed: ' + r['file'])
    assert kinds == ['section', 'head'], r['file']


def sha(b):
    return hashlib.sha256(b).hexdigest()


def target(rel, new=False):
    assert not rel.startswith('/') and '..' not in rel.split('/') and '\\' not in rel
    p = ROOT / rel
    assert p.parent.is_dir() and (ROOT in p.parent.resolve().parents or p.parent.resolve() == ROOT), rel
    if not new:
        assert p.is_file() and not p.is_symlink(), rel
    return p


def result(row, old):
    if row['before'] is None:
        return JS
    text = old.decode('utf-8')
    assert '<?php' not in text and '<?=' not in text, row['file']
    out = text
    for a, b, count in row['replace']:
        assert out.count(a) == count, 'COUNT CHANGED: ' + row['file'] + ' ' + a[:40]
        out = out.replace(a, b)
    return out.encode('utf-8')


def write(p, data, mode):
    tmp = p.with_name(p.name + '.samoproverka-forma-20261119-stage')
    assert not tmp.exists(), str(tmp)
    with tmp.open('wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(str(tmp), mode)
    os.replace(str(tmp), str(p))


def current(row):
    p = target(row['file'], new=row['before'] is None)
    return sha(p.read_bytes()) if p.exists() else None


if MODE == '--rollback':
    state = json.loads(STATUS.read_text(encoding='utf-8')) if STATUS.exists() else {}
    names = state.get('promoted', [r['file'] for r in ROWS])
    done = 0
    # pages first, then the new script (pages without the script tag never reference it)
    for row in reversed(ROWS):
        if row['file'] not in names:
            continue
        p = target(row['file'], new=row['before'] is None)
        if row['before'] is None:
            if p.exists():
                assert sha(p.read_bytes()) == row['after'], 'CHANGED BY ANOTHER DEPLOYMENT: ' + row['file']
                p.unlink()
                done += 1
            continue
        b = (BACKUP / row['file']).read_bytes()
        assert sha(b) == row['before']
        # Never overwrite an unrelated version changed by another deployment.
        assert sha(p.read_bytes()) in (row['before'], row['after']), 'CHANGED BY ANOTHER DEPLOYMENT: ' + row['file']
        write(p, b, (BACKUP / row['file']).stat().st_mode & 0o777)
        done += 1
    STATUS.write_text(json.dumps({'status': 'rolled_back_by_command', 'promoted': []}), encoding='utf-8')
    print('ROLLED BACK: %d files' % done)
    sys.exit(0)

if all(current(r) == r['after'] for r in ROWS):
    print('ALREADY PUBLISHED: %d/%d checksums match' % (N, N))
    sys.exit(0)

plan = []
for row in ROWS:
    new_file = row['before'] is None
    p = target(row['file'], new=new_file)
    if new_file:
        assert not p.exists(), 'NEW FILE ALREADY EXISTS: ' + row['file']
        old, mode = None, 0o644
    else:
        old = p.read_bytes()
        assert sha(old) == row['before'], 'CURRENT FILE CHANGED: ' + row['file'] + ' ' + sha(old)[:12]
        mode = p.stat().st_mode & 0o777
    new = result(row, old)
    assert sha(new) == row['after'], 'PACKAGE MISMATCH: ' + row['file']
    plan.append((row, p, old, new, mode))
print('PRECHECK OK: %d/%d original and resulting checksums verified (samoproverka-forma.min.js, 13 pages)' % (N, N))
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
print('BACKUP OK: %d/%d outside public_html' % (N - 1, N - 1))

promoted = []
try:
    # the script first: a published page always finds it
    for row, p, old, new, mode in plan:
        if old is None:
            assert not p.exists(), 'CONCURRENT CHANGE: ' + row['file']
        else:
            assert sha(p.read_bytes()) == row['before'], 'CONCURRENT CHANGE: ' + row['file']
        write(p, new, mode)
        promoted.append(row['file'])
        assert sha(p.read_bytes()) == row['after']
    assert all(current(r) == r['after'] for r in ROWS)
    STATUS.write_text(json.dumps({'status': 'published', 'promoted': promoted}, indent=2), encoding='utf-8')
    print('PUBLISHED: %d/%d checksums verified' % (N, N))
    print('BACKUP: ' + str(BACKUP))
except BaseException:
    for row, p, old, new, mode in reversed(plan):
        if row['file'] in promoted:
            if old is None:
                p.unlink()
            else:
                write(p, old, mode)
    STATUS.write_text(json.dumps({'status': 'rolled_back', 'promoted': []}), encoding='utf-8')
    print('AUTOMATIC ROLLBACK: ' + str(len(promoted)))
    raise
