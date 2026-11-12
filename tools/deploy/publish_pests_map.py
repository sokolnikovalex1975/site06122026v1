#!/usr/bin/env python3
"""Фон блока «Вредители» — «Карта очагов»: выкладка на Timeweb из SSH-консоли (12.11.2026).

Запуск рядом с deploy_payload.json, вне public_html:
  --check    (по умолчанию) сверить суммы SHA-256 всех файлов до и после, ничего не меняя;
  --svg      только положить новый рисунок img/pests-map.svg (страницы на него ещё не ссылаются);
  --publish  резервная копия вне public_html, затем рисунок, style.css и страницы с проверкой каждого файла;
  --rollback вернуть файлы из резервной копии и убрать рисунок, если его положил этот пакет.
Пакет готовит tools/deploy/prepare-2026-11-12-pests-map.py из актуальных страниц рабочего сайта.

Скрипт сам применяет к файлам public_html операции из пакета (новый рисунок, блок в конец style.css, версия
?v= и стиль главной), сверяет SHA-256 каждого файла до и после, не перезаписывает резервную копию и при любой
ошибке возвращает уже заменённые файлы. Повторный запуск после выкладки только сверяет суммы.
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
SVG_MARK = WORK / 'svg-created-by-this-package'
MODE = sys.argv[1] if len(sys.argv) == 2 else '--check'
assert MODE in ('--check', '--svg', '--publish', '--rollback'), MODE
assert ROOT.is_dir() and str(ROOT).endswith('/pestcontrol-center/public_html'), str(ROOT)
assert ROOT not in WORK.parents and ROOT != WORK, 'keep the package outside the public site'
assert PAYLOAD['name'] == 'pests-map-2026-11-12'
OLD_V, NEW_V = PAYLOAD['old_version'], PAYLOAD['new_version']
assert (OLD_V, NEW_V) == ('20261111btn', '20261112fon')
ROWS = PAYLOAD['files']
N = len(ROWS)
assert N == PAYLOAD['pages'] + 2 and 30 <= PAYLOAD['pages'] <= 60, 'unexpected number of files: %d' % N
assert len(set(r['file'] for r in ROWS)) == N
SVG_ROW, CSS_ROW, PAGES = ROWS[0], ROWS[1], ROWS[2:]
assert SVG_ROW['file'] == 'img/pests-map.svg' and SVG_ROW['before'] is None and 'create' in SVG_ROW
assert CSS_ROW['file'] == 'style.css' and 'append' in CSS_ROW
assert CSS_ROW['append'].startswith('\n/* ===== Фон блока «Вредители»: «Карта очагов» (12.11.2026) =====')
for r in PAGES:
    assert r['file'] == 'index.php' or r['file'].endswith('/index.php'), r['file']
    assert r['replace'][0][:2] == ['?v=' + OLD_V, '?v=' + NEW_V] and r['replace'][0][2] in (1, 2), r['file']
    if r['file'] == 'index.php':
        assert len(r['replace']) == 2 and r['replace'][1][0] == '</style>\n<!-- UIS -->' and r['replace'][1][2] == 1
        assert r['replace'][1][1].startswith('</style><style id="pests-map-st">.pests-bg{background:url(img/pests-map.svg) ')
        assert r['replace'][1][1].endswith('</style>\n<!-- UIS -->')
    else:
        assert len(r['replace']) == 1, r['file']


def sha(b):
    return hashlib.sha256(b).hexdigest()


def target(rel, must_exist=True):
    assert not rel.startswith('/') and '..' not in rel.split('/') and '\\' not in rel
    p = ROOT / rel
    if must_exist:
        assert p.is_file() and not p.is_symlink(), rel
    assert ROOT in p.parent.resolve().parents or p.parent.resolve() == ROOT, rel
    return p


def result(row, old):
    if 'create' in row:
        return row['create'].encode('utf-8')
    text = old.decode('utf-8')
    assert '<?php' not in text and '<?=' not in text, row['file']
    if 'append' in row:
        assert row['append'] not in text, 'ALREADY APPENDED: ' + row['file']
        return (text + row['append']).encode('utf-8')
    out = text
    for a, b, count in row['replace']:
        assert out.count(a) == count, 'COUNT CHANGED: ' + row['file'] + ' ' + a
        out = out.replace(a, b)
    return out.encode('utf-8')


def replace(p, data, mode):
    tmp = p.with_name(p.name + '.pests-20261112-stage')
    assert not tmp.exists(), str(tmp)
    with tmp.open('wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(str(tmp), mode)
    os.replace(str(tmp), str(p))


def svg_state():
    p = target(SVG_ROW['file'], must_exist=False)
    if not p.exists():
        return p, 'missing'
    assert p.is_file() and not p.is_symlink()
    return p, 'ok' if sha(p.read_bytes()) == SVG_ROW['after'] else 'other'


def put_svg():
    p, state = svg_state()
    assert state != 'other', 'SVG EXISTS WITH OTHER CONTENT: ' + str(p)
    if state == 'missing':
        assert p.parent.is_dir(), str(p.parent)
        replace(p, result(SVG_ROW, None), 0o644)
        SVG_MARK.write_text('created ' + SVG_ROW['after'] + '\n')
        assert sha(p.read_bytes()) == SVG_ROW['after']
        return True
    return False


if MODE == '--rollback':
    state = json.loads(STATUS.read_text(encoding='utf-8')) if STATUS.exists() else {}
    names = state.get('promoted', [r['file'] for r in ROWS[1:]])
    done = 0
    for row in ROWS[1:]:
        if row['file'] not in names:
            continue
        p = target(row['file'])
        b = (BACKUP / row['file']).read_bytes()
        assert sha(b) == row['before']
        # Never overwrite an unrelated version changed by another deployment.
        assert sha(p.read_bytes()) in (row['before'], row['after']), 'CHANGED BY ANOTHER DEPLOYMENT: ' + row['file']
        replace(p, b, (BACKUP / row['file']).stat().st_mode & 0o777)
        done += 1
    p, s = svg_state()
    if s == 'ok' and SVG_MARK.exists():
        p.unlink()
        SVG_MARK.unlink()
        print('SVG REMOVED: ' + SVG_ROW['file'])
    STATUS.write_text(json.dumps({'status': 'rolled_back_by_command', 'promoted': []}), encoding='utf-8')
    print('ROLLED BACK: %d files' % done)
    sys.exit(0)

_, s = svg_state()
assert s != 'other', 'SVG EXISTS WITH OTHER CONTENT'
already = s == 'ok' and all(sha(target(r['file']).read_bytes()) == r['after'] for r in ROWS[1:])
if already:
    print('ALREADY PUBLISHED: %d/%d checksums match' % (N, N))
    sys.exit(0)

plan = []
for row in ROWS[1:]:
    p = target(row['file'])
    old = p.read_bytes()
    assert sha(old) == row['before'], 'CURRENT FILE CHANGED: ' + row['file']
    new = result(row, old)
    assert sha(new) == row['after'], 'PACKAGE MISMATCH: ' + row['file']
    plan.append((row, p, old, new, p.stat().st_mode & 0o777))
assert sha(result(SVG_ROW, None)) == SVG_ROW['after']
print('PRECHECK OK: %d/%d original and resulting checksums verified (svg %s, style.css, %d pages)'
      % (N, N, s, len(PAGES)))
if MODE == '--check':
    sys.exit(0)
if MODE == '--svg':
    print('SVG OK: ' + ('created' if put_svg() else 'already in place') + ' ' + SVG_ROW['file'])
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
created = False
try:
    created = put_svg()
    for row, p, old, new, mode in plan:
        assert sha(p.read_bytes()) == row['before'], 'CONCURRENT CHANGE: ' + row['file']
        replace(p, new, mode)
        promoted.append(row['file'])
        assert sha(p.read_bytes()) == row['after']
    assert svg_state()[1] == 'ok'
    assert all(sha(target(r['file']).read_bytes()) == r['after'] for r in ROWS[1:])
    STATUS.write_text(json.dumps({'status': 'published', 'promoted': promoted}, indent=1), encoding='utf-8')
    print('PUBLISHED: %d/%d checksums verified' % (N, N))
    print('BACKUP: ' + str(BACKUP))
except BaseException:
    for row, p, old, new, mode in plan:
        if row['file'] in promoted:
            replace(p, old, mode)
    if created:
        target(SVG_ROW['file']).unlink()
        SVG_MARK.unlink()
    STATUS.write_text(json.dumps({'status': 'rolled_back', 'promoted': []}), encoding='utf-8')
    print('AUTOMATIC ROLLBACK: %d files' % len(promoted))
    raise
