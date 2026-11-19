#!/usr/bin/env python3
"""Курсор над чекбоксами — фирменное кольцо вместо «палочки» (вариант А): пакет для Timeweb (20.11.2026).

    python3 tools/deploy/prepare-2026-11-20-chk-cursor.py <новая папка пакета>

Решение владельца 20.11.2026: «Делай вариант А» (превью — коммит 0c689cc, tools/site/chk_cursor.py, CHANGES.md).
Выкладка — только после отдельного разрешения владельца.

15 страниц рабочего сайта (index.php): самопроверка .f-check-list на 14 страницах и опросный лист «Разработка ППК» .rp-chip.
В каждой странице одна точная замена: «</style>⏎<!-- UIS -->» → «</style>⏎», строка <style id="chk-cur">…</style>
(chk_cursor.LINE, та же, что в превью GitHub) и «<!-- UIS -->»: код UIS остаётся прямо перед </head> (закон владельца). Только стили: style.css, app.min.js, версии ?v=, тексты и другие страницы не меняются. Проверки при
сборке: участок ровно один раз, строки chk-cur ещё нет, результат совпадает с chk_cursor.apply(), обратная замена даёт
исходник байт в байт, tracking_laws (Метрика 113675622, UIS, Radist, телефон и почта) и закон независимости — без нарушений
до и после.

В папке пакета: backup/ и pkg/ (копии до и после), MANIFEST.txt, deploy_payload.json, publish_chk_cursor.py и run_once.sh.
"""
import hashlib
import importlib.util
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import chk_cursor as cc  # noqa: E402
import independence_law  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'chk-cursor-2026-11-20'
PAGES = ['biznes-tsentry-torgovye-tsentry-predpriyatiya', 'deratizatsiya', 'dezinsektsiya', 'farmatsevticheskie-proizvodstva',
         'gostinitsy', 'magaziny-i-torgovye-seti', 'materialy/pest-menedzhment-ili-razovaya-obrabotka',
         'materialy/programma-pest-kontrolya', 'materialy/zhurnal-pest-kontrolya', 'ochistka-dezinfektsiya-ventilyatsii',
         'pishchevoe-proizvodstvo', 'razrabotka-ppk', 'restorany-i-kafe', 'sklady-i-logistika',
         'zashchita-ot-proniknoveniya-gryzunov']
TRACK = ('mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<select', '<?')


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
for t in TRACK + ('<script', '<link', '@import'):
    assert t not in cc.LINE.lower(), 'строка стилей затрагивает ' + t
assert cc.LINE.count('<style') == 1 and cc.LINE.endswith('</style>\n')

rows = []
for slug in PAGES:
    rel = slug + '/index.php'
    status, body = live.get(live.SITE + slug + '/', tries=8)  # Timeweb из облака иногда отвечает ложным 502
    assert status == 200, '%s: HTTP %s' % (rel, status)
    old = body.decode('utf-8')
    assert '<?php' not in old and '<?=' not in old, rel + ': PHP в файле'
    assert cc.needs(old), rel + ': нет блока с чекбоксами'
    assert 'id="chk-cur"' not in old, rel + ': уже выложено?'
    bad = tracking_laws.check_page(old, counters=True)
    assert not bad, '%s: исходная страница: %s' % (rel, bad)
    hard_before = independence_law.violations(old)
    assert cc.LINE in (ROOT / slug / 'index.html').read_text(encoding='utf-8'), rel + ': строка стилей не как в превью'
    a, b = '</style>\n<!-- UIS -->', '</style>\n' + cc.LINE + '<!-- UIS -->'  # UIS — прямо перед </head> (закон, п. 1)
    assert old.count(a) == 1, '%s: «</style> + UIS» найдено %d раз' % (rel, old.count(a))
    new = old.replace(a, b)
    assert new == cc.apply(old), rel + ': результат не совпадает с chk_cursor.apply()'
    assert new.count(b) == 1 and new.replace(b, a) == old, rel + ': обратная замена не даёт исходник'
    bad = tracking_laws.check_page(new, counters=True)
    assert not bad, '%s: результат: %s' % (rel, bad)
    hard_after = independence_law.violations(new)
    assert hard_after == hard_before == [], '%s: закон независимости: %s' % (rel, hard_after)
    original, result = body, new.encode('utf-8')
    for folder, content in (('backup', original), ('pkg', result)):
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    rows.append({'file': rel, 'before': sha(original), 'after': sha(result), 'replace': [[a, b, 1]]})
    print('OK %s: %s… → %s… (+%d байт)' % (rel, sha(original)[:8], sha(result)[:8], len(result) - len(original)))

payload = {'name': NAME, 'count': len(rows), 'files': rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows),
                                  encoding='utf-8')
shutil.copy2(str(ROOT / 'tools/deploy/publish_chk_cursor.py'), str(OUT / 'publish_chk_cursor.py'))
RUN_ONCE = """#!/bin/sh
# Разовая выкладка пакета %(name)s на Timeweb (SSH-консоль панели). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_chk_cursor.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_chk_cursor.py --check &&
  python3 publish_chk_cursor.py --publish &&
  python3 publish_chk_cursor.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_chk_cursor.py').read_bytes()),
       'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
print('Готово: %d страниц, по 1 замене, счётчики и контакты — без нарушений, независимость — без нарушений. Пакет: %s'
      % (len(rows), OUT))
