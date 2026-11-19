#!/usr/bin/env python3
"""Страница «Защита от проникновения грызунов» на Timeweb (19.11.2026): пакет от рабочего сайта.

    python3 tools/site/build_prod.py                                   # сначала: dist/timeweb из репозитория
    python3 tools/deploy/prepare-2026-11-19-zashchita.py <новая папка>  # снять сайт по HTTPS и собрать пакет
    python3 tools/deploy/prepare-2026-11-19-zashchita.py <папка> --check

Решение владельца 19.11.2026: «Делаем, выкладывай страницу защиты от проникновения грызунов на Timeweb».

Что меняется на рабочем сайте:
  * новая страница zashchita-ot-proniknoveniya-gryzunov/index.php — сборка для Timeweb (build_prod.py) со счётчиками
    по закону владельца; метки версий style.css и app.min.js — как на остальных страницах сайта сейчас (общие файлы
    сайта не меняются); рядом contours.js и contours.svg (схема трёх контуров);
  * картинки страницы, которых на сайте ещё нет (остальные берутся с сайта как есть);
  * deratizatsiya/index.php — одна вставка: ссылка «защита от проникновения грызунов» в абзаце «Шаг 2 · Инженерный
    барьер» (как в репозитории), остальное байт в байт;
  * sitemap.xml — одна запись <url> страницы после «Дератизации» (lastmod — 2026-11-19);
  * search-index.json — записи новой страницы (из индекса репозитория) в конец списков, остальное без изменений.
Закон владельца (tracking_laws) и закон независимости — для новой страницы и «Дератизации» до и после.
"""
import base64
import hashlib
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
sys.path.insert(0, str(ROOT / 'tools/qa'))
import independence_law  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'zashchita-2026-11-19'
SLUG = 'zashchita-ot-proniknoveniya-gryzunov'
DIST = ROOT / 'dist/timeweb'
PAGE = SLUG + '/index.php'
LASTMOD = '2026-11-19'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def laws(t, name):
    v = tracking_laws.check_page(t, counters=True)
    assert not v, name + ': ' + '; '.join(map(str, v))
    iv = independence_law.violations(t)
    assert not iv, name + ': ' + '; '.join(map(str, iv))


def one_insert(old, new):
    d = len(new) - len(old)
    assert d > 0
    p = 0
    while p < len(old) and old[p] == new[p]:
        p += 1
    assert new[p + d:] == old[p:], 'кроме вставки изменилось что-то ещё'
    return new[p:p + d]


def page_assets(t):
    out = set()
    for m in re.finditer(r'(?:src|href|srcset|imagesrcset|data-src|content)="([^"]+)"', t):
        for part in m.group(1).split(','):
            u = part.strip().split(' ')[0]
            if u.startswith('https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'):
                u = '../' + u[len('https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'):]
            if not u or u.startswith(('#', 'http', 'tel:', 'mailto:', 'data:', '%3C')) or u.endswith('/') or '?' in u:
                continue
            if u.startswith('../'):
                rel = u[3:]
            else:
                rel = SLUG + '/' + u
            if re.search(r'\.(webp|jpg|jpeg|png|svg|js|woff2|pdf)$', rel):
                out.add(rel)
    return sorted(out)


def snapshot():
    import check_live as live
    get = lambda rel: live.get(live.SITE + rel, tries=8)
    files = {}
    for rel, url in (('deratizatsiya/index.php', 'deratizatsiya/'), ('sitemap.xml', 'sitemap.xml'),
                     ('search-index.json', 'search-index.json')):
        code, body = get(url)[:2]
        assert code == 200, url + ' ' + str(code)
        files[rel] = body
    code = get(SLUG + '/')[0]
    assert code != 200, 'страница уже есть на сайте'
    return files, get


def build(files, get, assets_live):
    rows = []
    # 1. новая страница
    page = (DIST / PAGE).read_text(encoding='utf-8')
    derat_live = files['deratizatsiya/index.php'].decode('utf-8')
    vers = dict(re.findall(r'(style\.css|app\.min\.js)\?v=(\w+)', derat_live))
    assert set(vers) == {'style.css', 'app.min.js'}, vers
    page = re.sub(r'(style\.css|app\.min\.js)\?v=\w+', lambda m: m.group(1) + '?v=' + vers[m.group(1)], page)
    assert '<meta name="robots" content="noindex' not in page and '<?php' not in page
    laws(page, PAGE)
    rows.append({'file': PAGE, 'before': None, 'content_b64': base64.b64encode(page.encode()).decode()})
    # 2. файлы страницы и картинки, которых нет на сайте
    for rel in page_assets(page):
        src = DIST / rel
        assert src.is_file(), 'нет в сборке: ' + rel
        code = assets_live.get(rel)
        if code is None:
            code = get(rel)[0]
            assets_live[rel] = code
        if code == 200:
            continue
        assert code == 404, rel + ': ответ ' + str(code)
        rows.append({'file': rel, 'before': None, 'content_b64': base64.b64encode(src.read_bytes()).decode()})
    # 3. «Дератизация»: ссылка на новую услугу
    repo_derat = (DIST / 'deratizatsiya/index.php').read_text(encoding='utf-8')
    span = re.search(r' <span id="proof-service-link">.*?</span>', repo_derat, re.S).group(0)
    anchor = 'щёточные уплотнители ворот.'
    assert derat_live.count(anchor + '</p>') == 1 and 'proof-service-link' not in derat_live, 'абзац не найден'
    i = derat_live.index(anchor + '</p>') + len(anchor)
    derat_new = derat_live[:i] + span + derat_live[i:]
    assert one_insert(derat_live, derat_new) == span
    laws(derat_live, 'deratizatsiya (до)')
    laws(derat_new, 'deratizatsiya (после)')
    rows.append({'file': 'deratizatsiya/index.php', 'before': sha(files['deratizatsiya/index.php']),
                 'content_b64': base64.b64encode(derat_new.encode()).decode()})
    # 4. sitemap.xml
    sm = files['sitemap.xml'].decode('utf-8')
    assert SLUG not in sm
    a = '<loc>https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/deratizatsiya/</loc>'
    j = sm.index('</url>\n', sm.index(a)) + len('</url>\n')
    entry = ('  <url>\n    <loc>https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/' + SLUG + '/</loc>\n    <lastmod>'
             + LASTMOD + '</lastmod>\n    <priority>0.9</priority>\n  </url>\n')
    sm_new = sm[:j] + entry + sm[j:]
    assert sm_new.count(entry) == 1 and sm_new.replace(entry, '', 1) == sm and len(sm_new) == len(sm) + len(entry)
    rows.append({'file': 'sitemap.xml', 'before': sha(files['sitemap.xml']),
                 'content_b64': base64.b64encode(sm_new.encode()).decode()})
    # 5. search-index.json
    L = json.loads(files['search-index.json'])
    R = json.loads((ROOT / 'search-index.json').read_text(encoding='utf-8'))
    assert all(p[1] != SLUG + '/' for p in L['p'])
    k = [n for n, p in enumerate(R['p']) if p[1] == SLUG + '/']
    assert len(k) == 1
    k = k[0]
    n = len(L['p'])
    L2 = {'v': L['v'], 'p': L['p'] + [R['p'][k]], 'i': L['i'] + [it[:5] + [n] for it in R['i'] if it[5] == k]}
    assert len(L2['i']) > len(L['i'])
    raw_old = files['search-index.json']
    # тот же формат, что у build_index.py: компактный JSON без ASCII-экранирования
    assert json.dumps(L, ensure_ascii=False, separators=(',', ':')).encode() == raw_old.rstrip(b'\n'), 'другой формат индекса'
    raw_new = json.dumps(L2, ensure_ascii=False, separators=(',', ':')).encode() + raw_old[len(raw_old.rstrip(b'\n')):]
    rows.append({'file': 'search-index.json', 'before': sha(raw_old), 'content_b64': base64.b64encode(raw_new).decode()})
    for r in rows:
        r['after'] = sha(base64.b64decode(r['content_b64']))
    return rows


def write_package(out, files, rows):
    for r in rows:
        f = out / 'pkg' / r['file']
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(base64.b64decode(r['content_b64']))
        if r['before']:
            b = out / 'backup' / r['file']
            b.parent.mkdir(parents=True, exist_ok=True)
            b.write_bytes(files[r['file']])
    payload = {'name': NAME, 'count': len(rows), 'files': rows}
    (out / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False) + '\n', encoding='utf-8')
    (out / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'] or '-' * 64, r['after'], r['file'])
                                              for r in rows), encoding='utf-8')
    shutil.copy2(str(ROOT / 'tools/deploy/publish_zashchita.py'), str(out / 'publish_zashchita.py'))
    run_once = """#!/bin/sh
# Разовая выкладка пакета %(name)s заданием Crontab панели Timeweb (удалить задание после запуска).
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_zashchita.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_zashchita.py --check &&
  python3 publish_zashchita.py --publish &&
  python3 publish_zashchita.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((out / 'publish_zashchita.py').read_bytes()),
       'sd': sha((out / 'deploy_payload.json').read_bytes())}
    (out / 'run_once.sh').write_text(run_once, encoding='utf-8')
    (out / 'run_once.sh').chmod(0o755)


def main(argv):
    out = pathlib.Path(argv[0]).resolve()
    if argv[1:] == ['--check']:
        files = {p.relative_to(out / 'backup').as_posix(): p.read_bytes()
                 for p in sorted((out / 'backup').rglob('*')) if p.is_file()}
        payload = json.loads((out / 'deploy_payload.json').read_text(encoding='utf-8'))
        page = base64.b64decode(payload['files'][0]['content_b64']).decode()
        codes = {a: 200 for a in page_assets(page)}
        codes.update({r['file']: 404 for r in payload['files'] if not r['before']})
        rows = build(files, lambda rel: (codes[rel], b''), codes)
        assert [(r['file'], r['before'], r['after']) for r in rows] == \
               [(r['file'], r['before'], r['after']) for r in payload['files']], 'payload не совпадает с пересборкой'
        print('Пересборка совпала: %d файлов' % len(rows))
        return
    assert not out.exists(), 'используйте новую папку'
    files, get = snapshot()
    rows = build(files, get, {})
    write_package(out, files, rows)
    print('Готово: %d файлов: %s. Пакет: %s' % (len(rows), ', '.join(r['file'] for r in rows), out))


if __name__ == '__main__':
    main(sys.argv[1:])
