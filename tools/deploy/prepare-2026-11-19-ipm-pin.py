#!/usr/bin/env python3
"""Круг «IPM — цикл визита» закреплён при прокрутке: пакет для Timeweb (19.11.2026), главная и «Дератизация».

    python3 tools/deploy/prepare-2026-11-19-ipm-pin.py <новая папка пакета>

Команда владельца 19.11.2026: «Сделай на „Дератизации“ такое же закрепление круга, как на главной. И выложи обе
страницы с закреплённым кругом на Timeweb». Правка в репозитории — tools/site/ipm_pin.py.

Страницы снимаются с рабочего сайта по HTTPS (index.php, deratizatsiya/index.php) — другие правки, уже выложенные
на сайт, сохраняются. В каждой странице 2 точные замены, результат сверяется с ipm_pin.fix() байт в байт:
  1. перед <style id="tel-plain"> — строка <style id="ipm-pin"> (только стили круга);
  2. секция #podhod: класс appr-pin, номер шага id="cycleNum" вместо id="cycleStep" (прежний код круга в app.min.js
     на этих страницах не запускается), точка кольца <div class="cycle-dot">, и сразу после секции — <script id="ipm-pin-js"> (закрепление и переходы; без сети, без счётчиков).
style.css, app.min.js, версии ?v= и другие страницы не меняются. Проверки: каждый участок ровно один раз, обратная
замена даёт исходник байт в байт, tracking_laws (Метрика 113675622, UIS, Radist ровно по разу на своих местах, телефон
и почта) и закон независимости — без нарушений до и после.

В папке пакета: backup/ и pkg/ (копии до и после), MANIFEST.txt, deploy_payload.json, publish_ipm_pin.py, run_once.sh.
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
import ipm_pin  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'ipm-pin-2026-11-19'
PAGES = [('', 'index.php', 'index.html'), ('deratizatsiya/', 'deratizatsiya/index.php', 'deratizatsiya/index.html')]
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
    assert 'ipm-pin' not in old, rel + ': уже выложено?'
    expected = ipm_pin.fix(old)
    m = ipm_pin.SEC_RE.search(old)
    sec = m.group(1)
    sec_new = ipm_pin.SEC_RE.search(expected).group(1)
    reps = [(ipm_pin.ANCHOR, ipm_pin.STYLE + ipm_pin.ANCHOR), (sec, sec_new + ipm_pin.SCRIPT)]
    # стиль и скрипт — те же, что в превью GitHub
    repo = (ROOT / key).read_text(encoding='utf-8')
    assert ipm_pin.STYLE in repo and ipm_pin.SCRIPT in repo and sec_new in repo, rel + ': не как в превью GitHub'
    for a, b in reps:
        for t in TRACK:
            assert t not in a.lower() and t not in b.lower(), '%s: замена затрагивает %s' % (rel, t)
    new = old
    for a, b in reps:
        assert new.count(a) == 1, '%s: «%s» найдено %d раз' % (rel, a[:60], new.count(a))
        prev, new = new, new.replace(a, b)
        assert len(new) == len(prev) + len(b) - len(a), rel + ': замена ' + a[:60]
    assert new == expected, rel + ': результат не совпадает с ipm_pin.fix()'
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
shutil.copy2(str(ROOT / 'tools/deploy/publish_ipm_pin.py'), str(OUT / 'publish_ipm_pin.py'))
RUN_ONCE = """#!/bin/sh
# Разовая выкладка пакета %(name)s на Timeweb (SSH-консоль панели). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_ipm_pin.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_ipm_pin.py --check &&
  python3 publish_ipm_pin.py --publish &&
  python3 publish_ipm_pin.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_ipm_pin.py').read_bytes()),
       'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
print('Готово: %d страницы, по 2 замены, счётчики и контакты — без нарушений, независимость — без нарушений. Пакет: %s'
      % (len(rows), OUT))
