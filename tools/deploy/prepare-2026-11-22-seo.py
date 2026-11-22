#!/usr/bin/env python3
"""SEO-правки по аудиту 17.11.2026 — пакет для Timeweb (собирается 22.11.2026 от рабочего сайта).

    python3 tools/deploy/prepare-2026-11-22-seo.py <новая папка пакета> [--htaccess <файл .htaccess с сервера>]

Решение владельца 18.11.2026 в 13:53 МСК: «правки выложить на сайт» — title главной, внутренние ссылки (10 пунктов
лаборатории в подвале и 21 ссылка в тексте), технические правки (переадресации, index.php, lastmod, разметка, og:image,
404) и шесть текстовых блоков — «вноси на сайт». Title и H1 12 страниц из PR #1 уже на сайте (19.11.2026, 15:20 МСК).
Clean-param в robots.txt в решение не вошёл — robots.txt не трогается.

Файлы снимаются с рабочего сайта по HTTPS (Timeweb из облака иногда отвечает ложным 502 — повторы):
  * 43 страницы (41 адрес sitemap.xml, политика, согласие) — замены tools/site/seo_1811.py: changes() для страницы
    сайта должен совпасть с changes() для той же страницы репозитория (те же пары «было → стало», то же число раз);
    обратная замена даёт исходник байт в байт; tracking_laws.check_page и independence_law.violations — без нарушений
    до и после;
  * search-index.json — индекс поиска, собранный tools/search/build_index.py из получившихся страниц сайта (без
    страницы автотранспорта, которой на сайте нет);
  * sitemap.xml — lastmod (tools/site/seo_server.sitemap);
  * .htaccess — переадресации и ErrorDocument 404 (tools/site/seo_server.htaccess); исходник — server/.htaccess
    из main (не меняется с 06.11.2026) или файл, снятый с сервера (--htaccess); на сервере сумма проверяется;
  * новые файлы: 404.html (tools/site/page_404.build из получившейся страницы политики + счётчики по закону),
    img/home-og.jpg, img/pishchevoe-og.jpg, img/pest-menedzhment-og.jpg (1200×630, из репозитория).
Результат: backup/ (файлы сайта), pkg/ (результат), deploy_payload.json, MANIFEST.txt (до → после), publish_seo.py
(в нём записываются суммы разрешённых пар замен — ALLOWED_PAIRS), run_once.sh. Прежние папки не перезаписываются.
"""
import base64
import hashlib
import importlib.util
import io
import json
import pathlib
import re
import runpy
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import build_prod  # noqa: E402
import independence_law  # noqa: E402
import page_404  # noqa: E402
import seo_1811  # noqa: E402
import seo_server  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'seo-2026-11-22'
SCRIPT = ROOT / 'tools/deploy/publish_seo.py'
LIVE_ONLY_MISSING = 'dezinfektsiya/avtotransport/index.html'  # есть в репозитории, на сайте ещё нет
NEW_IMAGES = ['img/home-og.jpg', 'img/pishchevoe-og.jpg', 'img/pest-menedzhment-og.jpg']


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pair_id(old, new):
    return sha((old + '\x00' + new).encode('utf-8'))


live = module('check_live', 'tools/qa/check_live.py')
args = sys.argv[1:]
OUT = pathlib.Path(args[0]).resolve()
assert not OUT.exists(), 'используйте новую папку: прежние копии не перезаписываются'
ht_file = pathlib.Path(args[args.index('--htaccess') + 1]) if '--htaccess' in args else None


def fetch(rel_url):
    status, body = live.get(live.SITE + rel_url, tries=10)
    assert status == 200 and body, '%s: HTTP %s' % (rel_url, status)
    return body


parts = tracking_laws.counter_parts()
rows, pairs = [], set()
sitemap_old = fetch('sitemap.xml')
locs = re.findall(r'<loc>%s([^<]*)</loc>' % re.escape(seo_server.SITE), sitemap_old.decode('utf-8'))
assert len(locs) == 41 and set(locs) == set(seo_server.LASTMOD), 'адреса sitemap.xml на сайте изменились'
repo_rel = {seo_1811.url_path(r): r for r in build_prod.PAGES + build_prod.LEGAL}
order = [r for r in build_prod.PAGES + build_prod.LEGAL if r != LIVE_ONLY_MISSING]
assert sorted(seo_1811.url_path(r) for r in order) == sorted(locs + ['privacy/', 'soglasie/'])

pages_after = {}
for rel in order:
    path = seo_1811.url_path(rel)
    prod = rel.replace('index.html', 'index.php')
    body = fetch(path)
    old = body.decode('utf-8')
    legal = rel in build_prod.LEGAL
    assert '<?php' not in old and '<?=' not in old, prod + ': PHP в файле'
    assert not tracking_laws.check_page(old, counters=not legal, parts=parts), prod + ': исходная страница нарушает закон'
    assert not independence_law.violations(old), prod + ': исходная страница нарушает закон независимости'
    repl = seo_1811.changes(path, old)
    assert repl, prod + ': правки уже на странице'
    repo_page = (ROOT / rel).read_text(encoding='utf-8')
    # в репозитории правки уже внесены: changes() для исходника из git должен совпасть
    git_old = subprocess.run(['git', 'show', 'origin/main:' + rel], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    assert seo_1811.changes(path, git_old) == repl, prod + ': замены не те, что в репозитории'
    assert seo_1811.patch(path, git_old) == repo_page, prod + ': страница репозитория не равна patch()'
    new = seo_1811.patch(path, old)
    back = new
    for a, b, c in reversed(repl):
        assert back.count(b) == c, prod + ': обратная замена неоднозначна'
        back = back.replace(b, a)
    assert back == old, prod + ': обратная замена не даёт исходник'
    assert not tracking_laws.check_page(new, counters=not legal, parts=parts), prod + ': результат нарушает закон'
    assert not independence_law.violations(new), prod + ': результат нарушает закон независимости'
    assert seo_1811.changes(path, new) == [] and not seo_1811.missing(path, new), prod + ': повторный запуск'
    for a, b, c in repl:
        pairs.add(pair_id(a, b))
    pages_after[rel] = new
    rows.append({'file': prod, 'kind': 'replace', 'before': sha(body), 'after': sha(new.encode('utf-8')),
                 'replace': [[a, b, c] for a, b, c in repl], '_old': body, '_new': new.encode('utf-8')})
    print('OK %-70s %d замен, %+d байт' % (prod, len(repl), len(new.encode('utf-8')) - len(body)))

# поиск по сайту — из получившихся страниц
tmp = OUT.parent / (OUT.name + '-index-pages')
assert not tmp.exists()
for rel, s in pages_after.items():
    f = tmp / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(s, encoding='utf-8')
index_file = tmp / 'search-index.json'
saved = list(build_prod.PAGES)
build_prod.PAGES[:] = [r for r in saved if r != LIVE_ONLY_MISSING]
argv = sys.argv
sys.argv = ['build_index.py', '--pages', str(tmp), '--out', str(index_file)]
try:
    runpy.run_path(str(ROOT / 'tools/search/build_index.py'), run_name='__main__')
finally:
    sys.argv = argv
    build_prod.PAGES[:] = saved
index_new = index_file.read_bytes()
shutil.rmtree(tmp)
index_old = fetch('search-index.json')
ix_old, ix_new = json.loads(index_old), json.loads(index_new)
assert ix_new['v'] == ix_old['v'] and len(ix_new['p']) == len(ix_old['p']) == 41
assert {u for _, u in ix_new['p']} == {u for _, u in ix_old['p']}, 'поиск: другой список страниц'

sitemap_new = seo_server.sitemap(sitemap_old.decode('utf-8')).encode('utf-8')
ht_old = ht_file.read_bytes() if ht_file else subprocess.run(
    ['git', 'show', 'origin/main:server/.htaccess'], cwd=ROOT, capture_output=True, check=True).stdout
ht_new = seo_server.htaccess(ht_old.decode('utf-8')).encode('utf-8')
for name, old, new in (('search-index.json', index_old, index_new), ('sitemap.xml', sitemap_old, sitemap_new),
                       ('.htaccess', ht_old, ht_new)):
    assert old != new, name + ': без изменений'
    assert not independence_law.violations(new.decode('utf-8')), name + ': закон независимости'
    rows.append({'file': name, 'kind': 'content', 'before': sha(old), 'after': sha(new),
                 'content_b64': base64.b64encode(new).decode('ascii'), '_old': old, '_new': new})
    print('OK %-70s %s… → %s…' % (name, sha(old)[:8], sha(new)[:8]))

# новые файлы
nf = page_404.build(pages_after['privacy/index.html'])
nf = tracking_laws.install_counters(tracking_laws.normalize_contacts(nf), parts)
assert not tracking_laws.check_page(nf, counters=True, parts=parts), '404.html: закон счётчиков'
assert not independence_law.violations(nf), '404.html: закон независимости'
new_rows = [{'file': '404.html', 'kind': 'new', 'before': None, '_new': nf.encode('utf-8')}]
from PIL import Image  # noqa: E402
for rel in NEW_IMAGES:
    b = (ROOT / rel).read_bytes()
    im = Image.open(io.BytesIO(b))
    assert im.format == 'JPEG' and im.size == (1200, 630), rel
    status, _ = live.get(live.SITE + rel, tries=10)
    assert status == 404, rel + ': уже есть на сайте'
    new_rows.append({'file': rel, 'kind': 'new', 'before': None, '_new': b})
status, _ = live.get(live.SITE + '404.html', tries=10)
assert status == 404, '404.html уже есть на сайте'
for r in new_rows:
    r['after'] = sha(r['_new'])
    r['content_b64'] = base64.b64encode(r['_new']).decode('ascii')
    print('OK %-70s новый, %d байт' % (r['file'], len(r['_new'])))

# порядок записи на сервере: новые файлы, страницы, поиск и sitemap, .htaccess последним
rows = new_rows + rows
assert [r['file'] for r in rows][-1] == '.htaccess'
for r in rows:
    for folder, content in (('backup', r.get('_old')), ('pkg', r['_new'])):
        if content is None:
            continue
        f = OUT / folder / r['file']
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
payload = {'name': NAME, 'count': len(rows),
           'files': [{k: v for k, v in r.items() if not k.startswith('_')} for r in rows]}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'] or '-' * 64, r['after'], r['file']) for r in rows),
                                  encoding='utf-8')

# ALLOWED_PAIRS в серверном скрипте
src = SCRIPT.read_text(encoding='utf-8')
m = re.search(r"(ALLOWED_PAIRS = \{[^\n]*\n)(.*?)(^\}\n)", src, re.S | re.M)
assert m, 'publish_seo.py: нет ALLOWED_PAIRS'
src = src[:m.start(2)] + ''.join("    '%s',\n" % p for p in sorted(pairs)) + src[m.end(2):]
SCRIPT.write_text(src, encoding='utf-8')
shutil.copy2(str(SCRIPT), str(OUT / 'publish_seo.py'))
RUN_ONCE = """#!/bin/sh
# Разовая выкладка пакета %(name)s на Timeweb (SSH-консоль панели). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_seo.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_seo.py --check &&
  python3 publish_seo.py --publish &&
  python3 publish_seo.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_seo.py').read_bytes()), 'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
print('Готово: %d файлов (%d страниц, 3 файла целиком, %d новых), %d разрешённых пар замен. Пакет: %s'
      % (len(rows), len(order), len(new_rows), len(pairs), OUT))
for f in ('publish_seo.py', 'deploy_payload.json', 'run_once.sh', 'MANIFEST.txt'):
    print('  %s  %s' % (sha((OUT / f).read_bytes()), f))
