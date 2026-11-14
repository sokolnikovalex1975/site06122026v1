#!/usr/bin/env python3
"""Переход к блоку по якорю — начало блока сразу под шапкой: выкладка на Timeweb из SSH-консоли (13.11.2026).

Запуск рядом с deploy_payload.json, вне public_html:
  --check    (по умолчанию) сверить суммы SHA-256 всех файлов до и после, ничего не меняя;
  --publish  резервная копия вне public_html, затем style.css, legal.css, app.min.js и страницы с проверкой каждого файла;
  --rollback вернуть файлы из резервной копии.
Пакет готовит tools/deploy/prepare-2026-11-13-zagolovok.py из актуальных файлов рабочего сайта.

Скрипт сам применяет к файлам public_html точные замены из пакета: style.css (scroll-padding-top и scroll-margin-top
разделов), legal.css (scroll-margin-top разделов политики и согласия), app.min.js (две замены в сжатом коде и новый
последний раздел вместо прежнего), главная (те же правила во встроенных стилях) и версии ?v= на страницах. До и после
сверяется SHA-256 каждого файла, резервная копия не перезаписывается, при любой ошибке уже заменённые файлы
возвращаются. Сначала заменяются стили и скрипт, потом страницы: новая версия в адресе не указывает на старый файл.
Повторный запуск после выкладки только сверяет суммы. Без f-строк, загрузок, паролей и сторонних пакетов (Python 3.6).
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
assert PAYLOAD['name'] == 'zagolovok-2026-11-13'
OLD_V, NEW_V, LEGAL_V = PAYLOAD['old_version'], PAYLOAD['new_version'], PAYLOAD['legal_old_version']
assert (OLD_V, NEW_V, LEGAL_V) == ('20261113ekran', '20261113zagolovok', '20261108')
ROWS = PAYLOAD['files']
N = len(ROWS)
assert N == PAYLOAD['pages'] + 3 and 30 <= PAYLOAD['pages'] <= 60, 'unexpected number of files: %d' % N
assert len(set(r['file'] for r in ROWS)) == N
assert [r['file'] for r in ROWS[:3]] == ['style.css', 'legal.css', 'app.min.js'], 'static files must be replaced first'
CSS_ROW, LEGAL_ROW, JS_ROW, PAGES = ROWS[0], ROWS[1], ROWS[2], ROWS[3:]
assert len(CSS_ROW['replace']) == 1 and CSS_ROW['replace'][0][0].startswith('html{scroll-behavior:smooth;scroll-padding-top:96px}\n')
assert 'scroll-padding-top:calc(clamp(68px,6vw,115px) + 1px + clamp(20px,2.2vw,32px))' in CSS_ROW['replace'][0][1]
assert len(LEGAL_ROW['replace']) == 2 and all('.l-sec[id]{scroll-margin-top:' in b for a, b, n in LEGAL_ROW['replace'])
assert len(JS_ROW['replace']) == 3 and 'window.pcAnchor.go(t,e,d,D)' in JS_ROW['replace'][0][1]
assert 'S.classList.contains("hold")' in JS_ROW['replace'][1][1] and 'pcAnchor' in JS_ROW['replace'][2][1]
for r in ROWS[:3]:
    assert all(n == 1 for a, b, n in r['replace']), r['file']
for r in PAGES:
    assert r['file'] == 'index.php' or r['file'].endswith('/index.php'), r['file']
    assert r['replace'][0][:2] == ['?v=' + OLD_V, '?v=' + NEW_V] and r['replace'][0][2] in (1, 2, 3), r['file']
    extra = r['replace'][1:]
    if r['file'] == 'index.php':
        assert len(extra) == 1 and extra[0][0] == 'html{scroll-behavior:smooth;scroll-padding-top:96px}html:has(:target){scroll-behavior:auto}'
    elif r['file'] in ('privacy/index.php', 'soglasie/index.php'):
        assert extra == [['legal.css?v=' + LEGAL_V + '"', 'legal.css?v=' + NEW_V + '"', 1]], r['file']
    else:
        assert not extra, r['file']


def sha(b):
    return hashlib.sha256(b).hexdigest()


def target(rel):
    assert not rel.startswith('/') and '..' not in rel.split('/') and '\\' not in rel
    p = ROOT / rel
    assert p.is_file() and not p.is_symlink(), rel
    assert ROOT in p.parent.resolve().parents or p.parent.resolve() == ROOT, rel
    return p


def result(row, old):
    text = old.decode('utf-8')
    assert '<?php' not in text and '<?=' not in text, row['file']
    out = text
    for a, b, count in row['replace']:
        assert out.count(a) == count, 'COUNT CHANGED: ' + row['file'] + ' ' + a[:60]
        out = out.replace(a, b)
    return out.encode('utf-8')


def replace(p, data, mode):
    tmp = p.with_name(p.name + '.zagolovok-20261113-stage')
    assert not tmp.exists(), str(tmp)
    with tmp.open('wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(str(tmp), mode)
    os.replace(str(tmp), str(p))


if MODE == '--rollback':
    state = json.loads(STATUS.read_text(encoding='utf-8')) if STATUS.exists() else {}
    names = state.get('promoted', [r['file'] for r in ROWS])
    done = 0
    for row in reversed(ROWS):  # сначала страницы, потом стили и скрипт
        if row['file'] not in names:
            continue
        p = target(row['file'])
        b = (BACKUP / row['file']).read_bytes()
        assert sha(b) == row['before']
        # Never overwrite an unrelated version changed by another deployment.
        assert sha(p.read_bytes()) in (row['before'], row['after']), 'CHANGED BY ANOTHER DEPLOYMENT: ' + row['file']
        replace(p, b, (BACKUP / row['file']).stat().st_mode & 0o777)
        done += 1
    STATUS.write_text(json.dumps({'status': 'rolled_back_by_command', 'promoted': []}), encoding='utf-8')
    print('ROLLED BACK: %d files' % done)
    sys.exit(0)

if all(sha(target(r['file']).read_bytes()) == r['after'] for r in ROWS):
    print('ALREADY PUBLISHED: %d/%d checksums match' % (N, N))
    sys.exit(0)

plan = []
for row in ROWS:
    p = target(row['file'])
    old = p.read_bytes()
    assert sha(old) == row['before'], 'CURRENT FILE CHANGED: ' + row['file']
    new = result(row, old)
    assert sha(new) == row['after'], 'PACKAGE MISMATCH: ' + row['file']
    plan.append((row, p, old, new, p.stat().st_mode & 0o777))
links = sum(r['replace'][0][2] for r in PAGES)
print('PRECHECK OK: %d/%d original and resulting checksums verified (style.css, legal.css, app.min.js, %d pages, %d version links)'
      % (N, N, len(PAGES), links))
if MODE == '--check':
    sys.exit(0)

assert not BACKUP.exists(), 'BACKUP ALREADY EXISTS: do not overwrite'
BACKUP.mkdir()
for row, p, old, new, mode in plan:
    b = BACKUP / row['file']
    b.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(p), str(b))
    assert sha(b.read_bytes()) == row['before']
print('BACKUP OK: %d/%d outside public_html' % (len(plan), len(plan)))

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
