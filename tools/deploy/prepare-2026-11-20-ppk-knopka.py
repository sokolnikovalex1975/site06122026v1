#!/usr/bin/env python3
"""Кнопки заявки на странице «Разработка ППК» без обещания выезда: пакет для Timeweb (20.11.2026).

    python3 tools/deploy/prepare-2026-11-20-ppk-knopka.py <новая папка пакета>

Замечание владельца 20.11.2026: ППК разрабатываем дистанционно по опросному листу, «Бесплатный выезд» — только для работ
с участием специалистов на объекте. Решение: «Делай первый вариант, выкладывай сразу на Timeweb». Правка в репозитории —
tools/site/ppk_knopka.py (вызывается из tools/razrabotka-ppk/build_page.py).

Страница снимается с рабочего сайта по HTTPS (razrabotka-ppk/index.php) — другие правки, уже выложенные на сайт,
сохраняются. 3 точные замены текста кнопок, результат сверяется с ppk_knopka.fix() байт в байт; обратная замена даёт
исходник; tracking_laws (Метрика 113675622, UIS, Radist, телефон и почта) и закон независимости — без нарушений до и после.

В папке пакета: backup/ и pkg/ (копии до и после), MANIFEST.txt, deploy_payload.json, publish_ppk_knopka.py, run_once.sh.
"""
import hashlib
import importlib.util
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import independence_law  # noqa: E402
import ppk_knopka  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'ppk-knopka-2026-11-20'
PAGES = [('razrabotka-ppk/', 'razrabotka-ppk/index.php', 'razrabotka-ppk/index.html')]
TRACK = ('mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<select', '<?', 'fetch(', 'xmlhttp')


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

rows = []
for url, rel, key in PAGES:
    status, body = live.get(live.SITE + url, tries=8)  # Timeweb из облака иногда отвечает ложным 502
    assert status == 200, '%s: HTTP %s' % (rel, status)
    old = body.decode('utf-8')
    assert '<?php' not in old and '<?=' not in old, rel + ': PHP в файле'
    bad = tracking_laws.check_page(old, counters=True)
    assert not bad, '%s: исходная страница: %s' % (rel, bad)
    hard_before = independence_law.violations(old)
    expected = ppk_knopka.fix(old)
    assert expected != old, rel + ': уже выложено?'
    reps = list(ppk_knopka.REPL)
    repo = (ROOT / key).read_text(encoding='utf-8')
    assert all(b in repo and a not in repo for a, b in reps), rel + ': не как в репозитории GitHub'
    for a, b in reps:
        for t in TRACK:
            assert t not in a.lower() and t not in b.lower(), '%s: замена затрагивает %s' % (rel, t)
    new = old
    for a, b in reps:
        assert new.count(a) == 1, '%s: «%s» найдено %d раз' % (rel, a[:60], new.count(a))
        prev, new = new, new.replace(a, b)
        assert len(new) == len(prev) + len(b) - len(a), rel + ': замена ' + a[:60]
    assert new == expected, rel + ': результат не совпадает с ppk_knopka.fix()'
    back = new
    for a, b in reversed(reps):
        assert back.count(b) == 1
        back = back.replace(b, a)
    assert back == old, rel + ': обратная замена не даёт исходник'
    bad = tracking_laws.check_page(new, counters=True)
    assert not bad, '%s: результат: %s' % (rel, bad)
    hard_after = independence_law.violations(new)
    assert hard_after == hard_before == [], '%s: закон независимости: %s' % (rel, hard_after)
    original, result = body, new.encode('utf-8')
    for folder, content in (('backup', original), ('pkg', result)):
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    rows.append({'file': rel, 'before': sha(original), 'after': sha(result), 'replace': [[a, b, 1] for a, b in reps]})
    print('OK %s: %s… → %s… (+%d байт)' % (rel, sha(original)[:8], sha(result)[:8], len(result) - len(original)))

payload = {'name': NAME, 'count': len(rows), 'files': rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows),
                                  encoding='utf-8')
shutil.copy2(str(ROOT / 'tools/deploy/publish_ppk_knopka.py'), str(OUT / 'publish_ppk_knopka.py'))
RUN_ONCE = """#!/bin/sh
# Разовая выкладка пакета %(name)s на Timeweb (SSH-консоль панели). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_ppk_knopka.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_ppk_knopka.py --check &&
  python3 publish_ppk_knopka.py --publish &&
  python3 publish_ppk_knopka.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_ppk_knopka.py').read_bytes()),
       'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
print('Готово: %d страница, 3 замены, счётчики и контакты — без нарушений, независимость — без нарушений. Пакет: %s'
      % (len(rows), OUT))
