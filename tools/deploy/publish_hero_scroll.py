#!/usr/bin/env python3
"""Первый экран главной без затемнения на телефоне: выкладка на Timeweb из SSH-консоли (13.11.2026).

Запуск рядом с deploy_payload.json, вне public_html:
  --check    (по умолчанию) сверить суммы SHA-256 всех файлов до и после, ничего не меняя;
  --publish  резервная копия вне public_html, затем style.css, app.min.js и страницы с проверкой каждого файла;
  --rollback вернуть файлы из резервной копии.
Пакет готовит tools/deploy/prepare-2026-11-13-hero-scroll.py из актуальных файлов рабочего сайта.

Скрипт сам применяет к файлам public_html операции из пакета (блок в конец style.css, одна замена в app.min.js,
версия ?v= на страницах и стиль главной), сверяет SHA-256 каждого файла до и после, не перезаписывает резервную копию
и при любой ошибке возвращает уже заменённые файлы. Повторный запуск после выкладки только сверяет суммы.
Без f-строк, загрузок, паролей и сторонних пакетов (Python 3.6 на сервере).
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
assert PAYLOAD['name'] == 'hero-scroll-2026-11-13'
OLD_V, NEW_V = PAYLOAD['old_version'], PAYLOAD['new_version']
assert (OLD_V, NEW_V) == ('20261112fon', '20261113hero')
ROWS = PAYLOAD['files']
N = len(ROWS)
assert N == PAYLOAD['pages'] + 2 and 30 <= PAYLOAD['pages'] <= 60, 'unexpected number of files: %d' % N
assert len(set(r['file'] for r in ROWS)) == N
CSS_ROW, JS_ROW, PAGES = ROWS[0], ROWS[1], ROWS[2:]
assert CSS_ROW['file'] == 'style.css' and 'append' in CSS_ROW and 'replace' not in CSS_ROW
assert CSS_ROW['append'].startswith('\n/* ===== Первый экран главной на телефоне: отступ до бегущей строки (13.11.2026) =====')
assert CSS_ROW['append'].endswith('@media (max-width:760px){#hero.hero:not(.f-hero){padding-bottom:32px}}\n')
assert JS_ROW['file'] == 'app.min.js' and 'append' not in JS_ROW and len(JS_ROW['replace']) == 1
JS_OLD, JS_NEW, JS_COUNT = JS_ROW['replace'][0]
assert JS_COUNT == 1 and JS_NEW == 'gsap.matchMedia().add("(min-width: 1281px)",function(){' + JS_OLD + '})'
assert JS_OLD.endswith('.to(".hero .wrap",{y:-110,opacity:.1,ease:"none"},0)')
for r in PAGES:
    assert r['file'] == 'index.php' or r['file'].endswith('/index.php'), r['file']
    assert r['replace'][0][:2] == ['?v=' + OLD_V, '?v=' + NEW_V] and r['replace'][0][2] in (1, 2), r['file']
    if r['file'] == 'index.php':
        assert len(r['replace']) == 2 and r['replace'][1][0] == '</style>\n<!-- UIS -->' and r['replace'][1][2] == 1
        assert r['replace'][1][1] == ('</style><style id="hero-scroll-st">@media (max-width:760px){#hero.hero:not(.f-hero)'
                                      '{padding-bottom:32px}}</style>\n<!-- UIS -->')
    else:
        assert len(r['replace']) == 1, r['file']


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
    if 'append' in row:
        assert row['append'] not in text, 'ALREADY APPENDED: ' + row['file']
        return (text + row['append']).encode('utf-8')
    out = text
    for a, b, count in row['replace']:
        assert out.count(a) == count, 'COUNT CHANGED: ' + row['file'] + ' ' + a[:60]
        out = out.replace(a, b)
    return out.encode('utf-8')


def replace(p, data, mode):
    tmp = p.with_name(p.name + '.hero-20261113-stage')
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
    for row in ROWS:
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
print('PRECHECK OK: %d/%d original and resulting checksums verified (style.css, app.min.js, %d pages)'
      % (N, N, len(PAGES)))
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
    for row, p, old, new, mode in plan:
        if row['file'] in promoted:
            replace(p, old, mode)
    STATUS.write_text(json.dumps({'status': 'rolled_back', 'promoted': []}), encoding='utf-8')
    print('AUTOMATIC ROLLBACK: %d files' % len(promoted))
    raise
