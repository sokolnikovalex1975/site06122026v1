#!/usr/bin/env python3
"""Самопроверка → заявка на 13 страницах: пакет для Timeweb (19.11.2026).

    python3 tools/deploy/prepare-2026-11-19-samoproverka-forma.py <новая папка пакета>

Решение владельца 19.11.2026: «Принимается, выкладывай на Timeweb» — форма с отметками поверх версии блока, которая
на сайте с 17.11.2026 (tools/site/samoproverka.py). Подробности — tools/site/samoproverka-forma-2026-11-19.md.

13 страниц снимаются с рабочего сайта по HTTPS и правятся той же функцией, что и страницы репозитория
(tools/site/samoproverka_forma.py → transform): кнопка и настройки окна в блоке, стили и скрипт сразу после style.css.
Остальное — байт в байт. Новый файл samoproverka-forma.min.js — из репозитория (на сайте его ещё нет: ответ 404).
Проверки: закон о счётчиках и контактах и закон независимости до и после, повторная правка ничего не меняет, каждая
замена ровно одна.

В папке пакета: backup/ и pkg/, MANIFEST.txt, deploy_payload.json, publish_samoproverka_forma.py и run_once.sh.
"""
import base64
import hashlib
import importlib.util
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import independence_law  # noqa: E402
import samoproverka_forma as samoproverka  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'samoproverka-forma-2026-11-19'


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

js = (ROOT / 'samoproverka-forma.min.js').read_bytes()
status, _ = live.get(live.SITE + 'samoproverka-forma.min.js', tries=8)
assert status == 404, 'samoproverka-forma.min.js уже на сайте: HTTP %s' % status
rows = [{'file': 'samoproverka-forma.min.js', 'before': None, 'after': sha(js), 'content_b64': base64.b64encode(js).decode('ascii')}]
(OUT / 'pkg').mkdir(parents=True)
(OUT / 'pkg' / 'samoproverka-forma.min.js').write_bytes(js)

for page in samoproverka.PAGES:
    rel = page + '/index.php'
    status, body = live.get(live.SITE + page + '/', tries=8)  # Timeweb из облака иногда отвечает ложным 502
    assert status == 200, '%s: HTTP %s' % (rel, status)
    old = body.decode('utf-8')
    assert '<?php' not in old and '<?=' not in old, rel + ': PHP в файле'
    bad = tracking_laws.check_page(old, counters=True)
    assert not bad, '%s: исходная страница: %s' % (rel, bad)
    hard_before = independence_law.violations(old)
    assert 'samoproverka-forma.min.js' not in old and 'data-chk-open' not in old, rel + ': уже опубликовано'
    new, reps = samoproverka.transform(old, page)
    again, more = samoproverka.transform(new, page)
    assert again == new and not more, rel + ': повторная правка что-то меняет'
    assert not samoproverka.problems(new, page), '%s: %s' % (rel, samoproverka.problems(new, page))
    # те же замены по очереди, как на сервере: каждая ровно один раз, остальное — байт в байт (сверка по кускам)
    cur = old
    for a, b, c in reps:
        assert cur.count(a) == 1, rel + ': замена найдена не один раз'
        pieces = cur.split(a)
        prev, cur = cur, cur.replace(a, b)
        assert b.join(pieces) == cur and len(cur) == len(prev) + len(b) - len(a), rel + ': замена'
    assert cur == new, rel + ': замены не дают результат'
    bad = tracking_laws.check_page(new, counters=True)
    assert not bad, '%s: результат: %s' % (rel, bad)
    hard_after = independence_law.violations(new)
    assert hard_after == hard_before == [], 'закон независимости: %s' % hard_after
    original, result = body, new.encode('utf-8')
    for folder, content in (('backup', original), ('pkg', result)):
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    rows.append({'file': rel, 'before': sha(original), 'after': sha(result), 'replace': reps})

payload = {'name': NAME, 'count': len(rows), 'css': samoproverka.CSS,
           'css_sha256': sha(samoproverka.CSS.encode('utf-8')), 'files': rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'] or '-' * 64, r['after'], r['file']) for r in rows),
                                  encoding='utf-8')
shutil.copy2(str(ROOT / 'tools/deploy/publish_samoproverka_forma.py'), str(OUT / 'publish_samoproverka_forma.py'))
RUN_ONCE = """#!/bin/sh
# Разовая выкладка пакета %(name)s (SSH-консоль или задание Crontab панели Timeweb; задание удалить после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_samoproverka_forma.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_samoproverka_forma.py --check &&
  python3 publish_samoproverka_forma.py --publish &&
  python3 publish_samoproverka_forma.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_samoproverka_forma.py').read_bytes()), 'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
for r in rows:
    print('OK %s: %s → %s…' % (r['file'], (r['before'] or 'новый')[:8], r['after'][:8]))
print('Готово: %d файлов, счётчики и контакты — без нарушений, независимость — без нарушений. Пакет: %s' % (len(rows), OUT))
