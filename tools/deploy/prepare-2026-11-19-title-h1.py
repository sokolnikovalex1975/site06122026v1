#!/usr/bin/env python3
"""Title и H1 с запросом семантического ядра на 12 страницах (PR #1): пакет для Timeweb (19.11.2026).

    python3 tools/deploy/prepare-2026-11-19-title-h1.py <новая папка пакета>

Решение владельца 15.11.2026 (Title и H1), слияние PR #1 и выкладка — по команде владельца 19.11.2026. Страницы
снимаются с сайта по HTTPS и правятся точечно теми же шагами, что и репозиторий: tools/site/meta_titles.py
(TITLE_CORE: <title> и name в разметке WebPage) и tools/site/h1_core.py (H1). В пакет входят только 12 страниц;
search-index.json, style.css, app.min.js и другие файлы не выкладываются.

Проверки: каждая пара замен найдена на живой странице (число вхождений записывается в пакет), результат совпадает
с patch() обоих шагов, построчная разница «до/после» на сайте та же, что в репозитории (8856518 → f6a15c2), обратная
замена даёт исходник байт в байт, закон о счётчиках и контактах (tracking_laws.check_page) и закон независимости —
до и после, faq_first --check-prod на результате.

В папке пакета: backup/ и pkg/, MANIFEST.txt, deploy_payload.json, publish_title_h1.py и run_once.sh.
"""
import difflib
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import h1_core  # noqa: E402
import independence_law  # noqa: E402
import meta_titles  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'title-h1-2026-11-19'
BASE_REV, PR_REV = '8856518', 'f6a15c2'
PAGES = sorted(set(meta_titles.TITLE_CORE) | set(h1_core.H1))
assert len(PAGES) == 12, PAGES


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


def changed_lines(a, b):
    out = []
    for op in difflib.ndiff(a.splitlines(), b.splitlines()):
        if op[:2] in ('- ', '+ '):
            out.append(op[:2])
    return out


live = module('check_live', 'tools/qa/check_live.py')
OUT = pathlib.Path(sys.argv[1]).resolve()
assert not OUT.exists(), 'используйте новую папку: прежние копии не перезаписываются'

rows = []
for path in PAGES:
    rel = path + 'index.php'
    status, body = live.get(live.SITE + path, tries=8)  # Timeweb из облака иногда отвечает ложным 502
    assert status == 200, '%s: HTTP %s' % (rel, status)
    old = body.decode('utf-8')
    assert '<?php' not in old and '<?=' not in old, rel + ': PHP в файле'
    bad = tracking_laws.check_page(old, counters=True)
    assert not bad, '%s: исходная страница: %s' % (rel, bad)
    hard_before = independence_law.violations(old)
    reps = []
    if path in meta_titles.TITLE_CORE:
        reps.append(meta_titles.TITLE_CORE[path])
    if path in h1_core.H1:
        reps.append(h1_core.H1[path])
    new, rep_rows = old, []
    for a, b in reps:
        n = new.count(a)
        assert n >= 1, '%s: на сайте нет «%s»' % (rel, a[:80])
        assert b not in new, '%s: новое уже на сайте' % rel
        pieces = new.split(a)
        new = new.replace(a, b)
        assert a.join(new.split(b)) == a.join(pieces), rel
        rep_rows.append([a, b, n])
    expect = h1_core.patch(path, meta_titles.patch(path, old))
    assert new == expect, rel + ': результат не совпадает с patch() meta_titles + h1_core'
    rev = new
    for a, b, n in reversed(rep_rows):
        rev = rev.replace(b, a)
    assert rev == old, rel + ': обратная замена не даёт исходник'
    repo_a = subprocess.check_output(['git', 'show', '%s:%sindex.html' % (BASE_REV, path)], cwd=str(ROOT)).decode()
    repo_b = subprocess.check_output(['git', 'show', '%s:%sindex.html' % (PR_REV, path)], cwd=str(ROOT)).decode()
    la, lb = changed_lines(old, new), changed_lines(repo_a, repo_b)
    assert la == lb, '%s: разница на сайте %s, в репозитории %s' % (rel, la, lb)
    bad = tracking_laws.check_page(new, counters=True)
    assert not bad, '%s: результат: %s' % (rel, bad)
    hard_after = independence_law.violations(new)
    assert hard_after == hard_before == [], 'закон независимости: %s' % hard_after
    original, result = body, new.encode('utf-8')
    for folder, content in (('backup', original), ('pkg', result)):
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    rows.append({'file': rel, 'before': sha(original), 'after': sha(result), 'replace': rep_rows})

for args in (['independence_law.py', '--check-prod'], ['tracking_laws.py', '--check-prod'], ['faq_first.py', '--check-prod']):
    files = [str(OUT / 'pkg' / r['file']) for r in rows]
    r = subprocess.run([sys.executable, str(ROOT / 'tools/site' / args[0]), args[1]] + files,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    print('%s %s: exit %d — %s' % (args[0], args[1], r.returncode, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ''))
    assert r.returncode == 0, r.stdout

payload = {'name': NAME, 'count': len(rows), 'files': rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows),
                                  encoding='utf-8')
shutil.copy2(str(ROOT / 'tools/deploy/publish_title_h1.py'), str(OUT / 'publish_title_h1.py'))
RUN_ONCE = """#!/bin/sh
# Разовая выкладка пакета %(name)s заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_title_h1.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_title_h1.py --check &&
  python3 publish_title_h1.py --publish &&
  python3 publish_title_h1.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_title_h1.py').read_bytes()), 'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
for r in rows:
    print('OK %s: %s… → %s… (%s)' % (r['file'], r['before'][:8], r['after'][:8],
                                   ', '.join('%d×' % n for _, _, n in r['replace'])))
print('Готово: %d страниц, счётчики и контакты — без нарушений, независимость — без нарушений. Пакет: %s' % (len(rows), OUT))
