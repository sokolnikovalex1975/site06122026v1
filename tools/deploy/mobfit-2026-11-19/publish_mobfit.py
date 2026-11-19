#!/usr/bin/env python3
"""Мобильная вёрстка, дополнение 19.11.2026: «Бизнес-центры…» — слово с дефисом в заголовке карточки на 320 px
переносится по дефису (до 400 px). Порядок как у mobfit-2026-11-16. Выкладка на Timeweb из SSH-консоли.

Запуск рядом с deploy_payload.json, вне public_html:
  --check    (по умолчанию) сверить SHA-256 всех страниц, ничего не меняя;
  --publish  резервная копия вне public_html, затем точные замены в 42 страницах с проверкой каждого файла;
  --rollback вернуть страницы из резервной копии.

Что меняется: в каждой странице перед <style id="tel-plain"> добавляется строка <style id="mob-fit"> (кнопки
переносят текст на телефоне, длинные слова в карточках не вылезают за край); на главной, «Дезинсекции кафе»
и «Вентиляции» текст во flex-ссылках и подписях обёрнут в один <span class="fxt"> («Подробнее о пест-контроле
складов / по GMP» больше не разъезжается на колонки); на «Дератизации» единицы в цифрах раздела «Документы»
вынесены отдельной подписью. Счётчики (Метрика, UIS, Radist), телефон и почта не меняются.
Без f-строк и сторонних пакетов (Python 3.6 на сервере).
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
MODE = sys.argv[1] if len(sys.argv) == 2 else '--check'
assert MODE in ('--check', '--publish', '--rollback'), MODE
assert ROOT.is_dir() and str(ROOT).endswith('/pestcontrol-center/public_html'), str(ROOT)
assert ROOT not in WORK.parents and ROOT != WORK, 'keep the package outside the public site'
assert PAYLOAD['name'] == 'mobfit-2026-11-19'
ROWS = PAYLOAD['files']
N = len(ROWS)
assert N == PAYLOAD['pages'] == 1, N
COUNTERS = ('mc.yandex.ru/metrika/tag.js', '113675622', 'comagic', 'radist')


def sha(b):
    return hashlib.sha256(b).hexdigest()


def state():
    res = []
    for r in ROWS:
        p = ROOT / r['file']
        h = sha(p.read_bytes()) if p.is_file() else None
        res.append('before' if h == r['before'] else ('after' if h == r['after'] else 'other'))
    return res


def counters_same(old, new):
    for c in COUNTERS:
        if old.count(c) != new.count(c):
            return False
    return True


st = state()
nb, na, no = st.count('before'), st.count('after'), st.count('other')
print('state: before=%d after=%d other=%d of %d' % (nb, na, no, N))
for r, s in zip(ROWS, st):
    if s == 'other':
        print('  changed on server since the snapshot: ' + r['file'])

if MODE == '--check':
    if na == N:
        print('ALREADY PUBLISHED: %d/%d' % (N, N))
    elif nb == N:
        print('PRECHECK OK: %d/%d' % (N, N))
    else:
        print('PRECHECK FAILED')
        sys.exit(2)
    sys.exit(0)

if MODE == '--publish':
    if na == N:
        print('ALREADY PUBLISHED: %d/%d' % (N, N))
        sys.exit(0)
    if nb != N:
        print('PRECHECK FAILED: nothing changed')
        sys.exit(2)
    if BACKUP.exists():
        print('backup already exists, refusing to overwrite: ' + str(BACKUP))
        sys.exit(3)
    for r in ROWS:
        dst = BACKUP / r['file']
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(ROOT / r['file']), str(dst))
        assert sha(dst.read_bytes()) == r['before'], r['file']
    print('BACKUP OK: %d/%d outside public_html (%s)' % (N, N, BACKUP))
    done = []
    try:
        for r in ROWS:
            p = ROOT / r['file']
            text = p.read_bytes().decode('utf-8')
            new = text
            for old, rep, cnt in r['replace']:
                if new.count(old) != cnt:
                    raise RuntimeError('replace count mismatch in ' + r['file'])
                new = new.replace(old, rep)
            data = new.encode('utf-8')
            if sha(data) != r['after'] or not counters_same(text, new):
                raise RuntimeError('result mismatch in ' + r['file'])
            tmp = p.with_name(p.name + '.mobfit.tmp')
            tmp.write_bytes(data)
            shutil.copymode(str(p), str(tmp))
            os.replace(str(tmp), str(p))
            done.append(r)
            if sha(p.read_bytes()) != r['after']:
                raise RuntimeError('verify failed for ' + r['file'])
    except Exception as e:
        print('ERROR: %s; restoring %d file(s)' % (e, len(done)))
        for r in done:
            shutil.copy2(str(BACKUP / r['file']), str(ROOT / r['file']))
        sys.exit(4)
    st = state()
    print('PUBLISHED: %d/%d checksums verified' % (st.count('after'), N))
    sys.exit(0 if st.count('after') == N else 5)

if MODE == '--rollback':
    assert BACKUP.is_dir(), 'no backup'
    for r in ROWS:
        src = BACKUP / r['file']
        assert sha(src.read_bytes()) == r['before'], r['file']
        shutil.copy2(str(src), str(ROOT / r['file']))
    st = state()
    print('ROLLED BACK: %d/%d' % (st.count('before'), N))
