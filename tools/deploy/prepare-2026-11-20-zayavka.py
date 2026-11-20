#!/usr/bin/env python3
"""«Состав заявки» и длинные блоки на телефоне: пакет для Timeweb (20.11.2026).

    python3 tools/deploy/prepare-2026-11-20-zayavka.py <новая папка пакета>

Команда владельца 20.11.2026: «Делай это на сайте» (решение «Мобильная версия — блоки с выбором и состав заявки»,
16.11.2026). Подробности — CHANGES.md, запись 20.11.2026, и tools/site/zayavka.py.

41 страница снимается с рабочего сайта по HTTPS и правится той же функцией, что и страницы репозитория
(tools/site/zayavka.py → transform): перед <style id="tel-plain"> в <head> — <style id="zv-css">, стили окна
<style id="chk-css"> (где их нет) и скрипты zayavka.min.js и mob-bloki.min.js (на главной — только первый); на 13
страницах с окном самопроверки — новая метка ?v= у samoproverka-forma.min.js. Остальное — байт в байт.
Файлы: zayavka.min.js и mob-bloki.min.js — новые (на сайте 404), samoproverka-forma.min.js — новая версия (сумма
прежней сверяется с сайтом). Проверки: закон о счётчиках и контактах и закон независимости до и после, повторная
правка ничего не меняет, каждая замена ровно одна.
"""
import base64
import hashlib
import importlib.util
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import independence_law  # noqa: E402
import samoproverka_forma  # noqa: E402
import tracking_laws  # noqa: E402
import zayavka  # noqa: E402

NAME = 'zayavka-2026-11-20'


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


live = module('check_live', 'tools/qa/check_live.py')
OUT = pathlib.Path(sys.argv[1]).resolve()
assert not OUT.exists(), 'используйте новую папку: прежние копии не перезаписываются'
(OUT / 'pkg').mkdir(parents=True)
(OUT / 'backup').mkdir()

rows = []
for name in ('zayavka.min.js', 'mob-bloki.min.js'):
    js = (ROOT / name).read_bytes()
    status, _ = live.get(live.SITE + name, tries=8)
    assert status == 404, '%s уже на сайте: HTTP %s' % (name, status)
    rows.append({'file': name, 'before': None, 'after': sha(js), 'content_b64': base64.b64encode(js).decode('ascii')})
    (OUT / 'pkg' / name).write_bytes(js)
name = 'samoproverka-forma.min.js'
js = (ROOT / name).read_bytes()
status, old_js = live.get(live.SITE + name, tries=8)
assert status == 200 and old_js != js, '%s: HTTP %s' % (name, status)
assert b'PCZ' not in old_js, name + ': на сайте уже новая версия'
(OUT / 'backup' / name).write_bytes(old_js)
(OUT / 'pkg' / name).write_bytes(js)
rows.append({'file': name, 'before': sha(old_js), 'after': sha(js), 'content_b64': base64.b64encode(js).decode('ascii')})

OLD_TAG = re.compile(r'<script src="(?:\.\./)*samoproverka-forma\.min\.js\?v=20261119forma" defer></script>')
for page in zayavka.PAGES:
    rel = page.replace('index.html', 'index.php')
    url = live.SITE + page.replace('index.html', '')
    status, body = live.get(url, tries=8)  # Timeweb из облака иногда отвечает ложным 502
    assert status == 200, '%s: HTTP %s' % (rel, status)
    old = body.decode('utf-8')
    assert '<?php' not in old and '<?=' not in old, rel + ': PHP в файле'
    bad = tracking_laws.check_page(old, counters=True)
    assert not bad, '%s: исходная страница: %s' % (rel, bad)
    hard_before = independence_law.violations(old)
    assert 'zv-css' not in old and 'zayavka.min.js' not in old, rel + ': уже опубликовано'
    reps = []
    blk = zayavka.block(old, page)
    reps.append([zayavka.ANCHOR, blk + zayavka.ANCHOR, 1])
    tag = OLD_TAG.search(old)
    if tag:
        p0 = page.replace('/index.html', '').replace('index.html', '')
        reps.append([tag.group(0), samoproverka_forma.script_tag(p0), 1])
    cur = old
    for a, b, c in reps:
        assert cur.count(a) == 1, rel + ': замена найдена не один раз: ' + a[:50]
        pieces = cur.split(a)
        prev, cur = cur, cur.replace(a, b)
        assert b.join(pieces) == cur and len(cur) == len(prev) + len(b) - len(a), rel + ': замена'
    new = cur
    expected = zayavka.transform(old, page)
    if tag:
        expected = expected.replace(tag.group(0), reps[1][1])
    assert new == expected, rel + ': не совпадает с transform()'
    assert zayavka.transform(new, page) == new, rel + ': повторная правка что-то меняет'
    assert not zayavka.problems(new, page), '%s: %s' % (rel, zayavka.problems(new, page))
    if tag:
        assert not samoproverka_forma.problems(new, p0), '%s: %s' % (rel, samoproverka_forma.problems(new, p0))
    bad = tracking_laws.check_page(new, counters=True)
    assert not bad, '%s: результат: %s' % (rel, bad)
    # счётчики: UIS прямо перед </head>, Radist — в конце <body>, новые строки — выше кода UIS
    assert new.index('zayavka.min.js') < new.lower().index('</head>')
    hard_after = independence_law.violations(new)
    assert hard_after == hard_before == [], 'закон независимости: %s' % hard_after
    original, result = body, new.encode('utf-8')
    for folder, content in (('backup', original), ('pkg', result)):
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    rows.append({'file': rel, 'before': sha(original), 'after': sha(result), 'replace': reps})

payload = {'name': NAME, 'count': len(rows), 'version': zayavka.VERSION, 'chk_css': samoproverka_forma.CSS,
           'zv_css': zayavka.css_line(), 'files': rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'] or '-' * 64, r['after'], r['file']) for r in rows),
                                  encoding='utf-8')
shutil.copy2(str(ROOT / 'tools/deploy/publish_zayavka.py'), str(OUT / 'publish_zayavka.py'))
RUN_ONCE = """#!/bin/sh
# Разовая выкладка пакета %(name)s (SSH-консоль или задание Crontab панели Timeweb; задание удалить после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_zayavka.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_zayavka.py --check &&
  python3 publish_zayavka.py --publish &&
  python3 publish_zayavka.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_zayavka.py').read_bytes()), 'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
for r in rows:
    print('OK %s: %s → %s…' % (r['file'], (r['before'] or 'новый')[:8], r['after'][:8]))
print('Готово: %d файлов, счётчики и контакты — без нарушений, независимость — без нарушений. Пакет: %s' % (len(rows), OUT))
