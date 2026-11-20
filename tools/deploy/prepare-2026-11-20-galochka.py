#!/usr/bin/env python3
"""«Заявка отправлена» — крупная зелёная галочка, видна всегда: пакет для Timeweb (20.11.2026).

    python3 tools/deploy/prepare-2026-11-20-galochka.py <новая папка пакета>

Решение владельца 20.11.2026 «выкладывай» по снимку 09-galochka-zayavka-otpravlena.jpg: в шторке заявки, окне
самопроверки и основной форме после отправки — зелёный круг с крупной галочкой; при «Уменьшении движения» на телефоне
галочка тоже видна (раньше она только прорисовывалась анимацией и в этом режиме не появлялась).
41 страница снимается с рабочего сайта по HTTPS; одна точная замена — строка <style id="zv-css"> на новую
(tools/site/zayavka.css → zayavka.transform). Скрипты, тексты, счётчики, телефон и почта не меняются.
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
import tracking_laws  # noqa: E402
import zayavka  # noqa: E402

NAME = 'galochka-2026-11-20'


def sha(b):
    return hashlib.sha256(b).hexdigest()


spec = importlib.util.spec_from_file_location('check_live', ROOT / 'tools/qa/check_live.py')
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)
OUT = pathlib.Path(sys.argv[1]).resolve()
assert not OUT.exists(), 'используйте новую папку'
NEW = zayavka.css_line()
rows = []
for page in zayavka.PAGES:
    rel = page.replace('index.html', 'index.php')
    status, body = live.get(live.SITE + page.replace('index.html', ''), tries=8)
    assert status == 200, '%s: HTTP %s' % (rel, status)
    old = body.decode('utf-8')
    assert not tracking_laws.check_page(old, counters=True), rel
    m = zayavka.ZV_RE.search(old)
    assert m and old.count('<style id="zv-css">') == 1, rel + ': нет zv-css'
    cur = m.group(0).rstrip('\n')
    assert cur != NEW and 'zvOkPop' not in cur, rel + ': уже опубликовано'
    new = old.replace(cur, NEW, 1)
    assert old.count(cur) == 1 and new == zayavka.transform(old, page), rel + ': не совпадает с transform()'
    assert zayavka.transform(new, page) == new and not zayavka.problems(new, page), rel
    assert not tracking_laws.check_page(new, counters=True), rel
    assert independence_law.violations(new) == independence_law.violations(old) == [], rel
    for folder, content in (('backup', body), ('pkg', new.encode('utf-8'))):
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    rows.append({'file': rel, 'before': sha(body), 'after': sha(new.encode('utf-8')), 'replace': [[cur, NEW, 1]]})
payload = {'name': NAME, 'count': len(rows), 'files': rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows), encoding='utf-8')
shutil.copy2(str(ROOT / 'tools/deploy/publish_galochka.py'), str(OUT / 'publish_galochka.py'))
RUN = """#!/bin/sh
# Разовая выкладка пакета %(n)s (SSH-консоль панели Timeweb). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_galochka.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_galochka.py --check &&
  python3 publish_galochka.py --publish &&
  python3 publish_galochka.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'n': NAME, 'sp': sha((OUT / 'publish_galochka.py').read_bytes()), 'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN, encoding='utf-8')
print('Готово: %d страниц. Пакет: %s' % (len(rows), OUT))
