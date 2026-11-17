#!/usr/bin/env python3
"""Самопроверка на телефоне: пакет для Timeweb (17.11.2026).

    python3 tools/deploy/prepare-2026-11-17-samoproverka.py <новая папка пакета>

Решение владельца 17.11.2026 (макеты — файлы проекта, папка «Самопроверка — кнопка после пунктов на телефоне»): «Да, делай
в превью. «Заказать обследование», нижнюю панель скрывай»; команда на выкладку 17.11.2026: «Вноси изменения на timeweb».
Правка на GitHub — коммит b3e64bb (tools/site/samoproverka.py, CHANGES.md).

Выкладываются 13 страниц с блоком самопроверки, которые есть на рабочем сайте (страницы «Защита от проникновения грызунов»
на рабочем сайте нет — HTTP 404, она не выкладывается). Стили и скрипт блока встроены в страницы, поэтому style.css,
app.min.js, версии ?v= и другие страницы не меняются. В каждой странице с рабочего сайта две точные замены:
  1. блок <section id="samoproverka"> → новый блок из samoproverka.fix() + сразу после него <script id="f-check-js">;
  2. строка <style id="mob-fit"> → перед ней строка стилей <style id="f-check-m">.
Результат каждой страницы сверяется с samoproverka.fix() байт в байт, новый блок — с блоком той же страницы репозитория
(превью GitHub). Неопубликованные правки репозитория в пакет не попадают: меняются только эти 2 участка, остальное — байт
в байт. Проверки при сборке: каждый участок ровно один раз, обратная замена даёт исходник байт в байт, tracking_laws
(Метрика 113675622, UIS, Radist, телефон и почта) и закон независимости — без нарушений до и после.

В папке пакета: backup/ и pkg/ (копии до и после), MANIFEST.txt, deploy_payload.json, publish_samoproverka.py и run_once.sh.
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
import samoproverka as sp  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'samoproverka-2026-11-17'
PAGES = [
    'restorany-i-kafe', 'gostinitsy', 'pishchevoe-proizvodstvo', 'deratizatsiya', 'sklady-i-logistika',
    'magaziny-i-torgovye-seti', 'biznes-tsentry-torgovye-tsentry-predpriyatiya', 'farmatsevticheskie-proizvodstva',
    'ochistka-dezinfektsiya-ventilyatsii', 'dezinsektsiya', 'materialy/zhurnal-pest-kontrolya',
    'materialy/programma-pest-kontrolya', 'materialy/pest-menedzhment-ili-razovaya-obrabotka',
]
NOT_LIVE = 'zashchita-ot-proniknoveniya-gryzunov'
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

status, _ = live.get(live.SITE + NOT_LIVE + '/', tries=4)
assert status == 404, '%s: на рабочем сайте HTTP %s — страницу нужно добавить в пакет отдельно' % (NOT_LIVE, status)

rows = []
for slug in PAGES:
    rel = slug + '/index.php'
    status, body = live.get(live.SITE + slug + '/', tries=8)  # Timeweb из облака иногда отвечает ложным 502
    assert status == 200, '%s: HTTP %s' % (rel, status)
    old = body.decode('utf-8')
    assert '<?php' not in old and '<?=' not in old, rel + ': PHP в файле'
    bad = tracking_laws.check_page(old, counters=True)
    assert not bad, '%s: исходная страница: %s' % (rel, bad)
    hard_before = independence_law.violations(old)
    assert 'f-check-m' not in old and 'f-check-js' not in old and 'f-check-f' not in old, rel + ': уже выложено?'
    sec_old = sp.SEC_RE.search(old).group(0)
    expected = sp.fix(old)
    sec_new = sp.SEC_RE.search(expected).group(0)
    repo = (ROOT / slug / 'index.html').read_text(encoding='utf-8')
    assert sec_new == sp.SEC_RE.search(repo).group(0), rel + ': новый блок не как в превью GitHub'
    reps = [(sec_old, sec_new + '\n' + sp.SCRIPT), (sp.MOB_FIT, sp.STYLE + sp.MOB_FIT)]
    for a, b in reps:
        for t in TRACK:
            assert t not in a.lower() and t not in b.lower(), '%s: замена затрагивает %s' % (rel, t)
    new = old
    for a, b in reps:
        assert new.count(a) == 1, '%s: «%s» найдено %d раз' % (rel, a[:60], new.count(a))
        prev, new = new, new.replace(a, b)
        assert len(new) == len(prev) + len(b) - len(a), rel + ': замена ' + a[:60]
    assert new == expected, rel + ': результат не совпадает с samoproverka.fix()'
    assert not sp.problems(new), rel
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
shutil.copy2(str(ROOT / 'tools/deploy/publish_samoproverka.py'), str(OUT / 'publish_samoproverka.py'))
RUN_ONCE = """#!/bin/sh
# Разовая выкладка пакета %(name)s на Timeweb (SSH-консоль панели или разовое задание Crontab — удалить после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_samoproverka.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_samoproverka.py --check &&
  python3 publish_samoproverka.py --publish &&
  python3 publish_samoproverka.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_samoproverka.py').read_bytes()),
       'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
print('Готово: %d страниц, по 2 замены, счётчики и контакты — без нарушений, независимость — без нарушений. Пакет: %s'
      % (len(rows), OUT))
