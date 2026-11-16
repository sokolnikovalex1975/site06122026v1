#!/usr/bin/env python3
"""«Мелкие мушки» вместо «Дрозофилы» в заголовках примеров ресторанов и пищевого производства: пакет для Timeweb (17.11.2026).

    python3 tools/deploy/prepare-2026-11-17-mushki3.py <новая папка пакета>

Решение владельца 17.11.2026: «Убери слово «Дрозофилы» из примеров заголовков на страницах ресторанов и пищевого
производства». Продолжение tools/site/mushki2-2026-11-17.md. Меняются только заголовки примеров из практики:
  /restorany-i-kafe/        «Дрозофилы в баре не уходят»                 → «Мелкие мушки в баре не уходят»
  /pishchevoe-proizvodstvo/ «Дрозофилы в моечной, обработки не помогают» → «Мелкие мушки в моечной, обработки не помогают»
и те же заголовки в списках разделов search-index.json. Неразрывные пробелы — там же, где были (на странице ресторанов
после «в» и «не»). Тексты примеров и прочие упоминания дрозофил не меняются.

Файлы снимаются с сайта по HTTPS и правятся точечно, остальное — байт в байт (сверка по кускам между заменами). Проверки:
закон о счётчиках и контактах и закон независимости до и после, число замен, JSON читается.

В папке пакета: backup/ и pkg/, MANIFEST.txt, deploy_payload.json, publish_mushki3.py и run_once.sh.
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

NAME = 'mushki3-2026-11-17'
NB = '\u00a0'
RES = ('«Дрозофилы в' + NB + 'баре не' + NB + 'уходят»', '«Мелкие мушки в' + NB + 'баре не' + NB + 'уходят»')
SI_RES = ('«Дрозофилы в баре не уходят»', '«Мелкие мушки в баре не уходят»')
FOOD = ('«Дрозофилы в моечной, обработки не помогают»', '«Мелкие мушки в моечной, обработки не помогают»')
FILES = [
    ('restorany-i-kafe/index.php', [RES]),
    ('pishchevoe-proizvodstvo/index.php', [FOOD]),
    ('search-index.json', [SI_RES, FOOD]),
]
LEFT = ('«Дрозофилы в', '«Дрозофилы' + NB + 'в')

# исходники сборки уже исправлены (иначе следующая полная сборка вернёт старое)
for src in ('tools/restorany/main.html', 'tools/food/main.html', 'tools/restorany/template-food.html',
            'restorany-i-kafe/index.html', 'pishchevoe-proizvodstvo/index.html', 'search-index.json'):
    t = (ROOT / src).read_text(encoding='utf-8')
    assert not any(x in t for x in LEFT), 'в исходнике остался заголовок с «Дрозофилы»: ' + src


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


def url_of(rel):
    return rel[:-len('index.php')] if rel.endswith('index.php') else rel


live = module('check_live', 'tools/qa/check_live.py')
OUT = pathlib.Path(sys.argv[1]).resolve()
assert not OUT.exists(), 'используйте новую папку: прежние копии не перезаписываются'

rows = []
for rel, reps in FILES:
    status, body = live.get(live.SITE + '/' + url_of(rel), tries=8)  # Timeweb из облака иногда отвечает ложным 502
    assert status == 200, '%s: HTTP %s' % (rel, status)
    old = body.decode('utf-8')
    assert '<?php' not in old and '<?=' not in old, rel + ': PHP в файле'
    is_page = rel.endswith('.php')
    if is_page:
        bad = tracking_laws.check_page(old, counters=True)
        assert not bad, '%s: исходная страница: %s' % (rel, bad)
        hard_before = independence_law.violations(old)
    else:
        json.loads(old)
    new = old
    for a, b in reps:
        assert new.count(a) == 1, '%s: «%s» найдено %d раз' % (rel, a, new.count(a))
        pieces = new.split(a)
        prev, new = new, new.replace(a, b)
        assert b.join(pieces) == new and len(new) == len(prev) + len(b) - len(a), rel + ': замена ' + a
    assert not any(x in new for x in LEFT), rel + ': остался старый заголовок'
    if is_page:
        bad = tracking_laws.check_page(new, counters=True)
        assert not bad, '%s: результат: %s' % (rel, bad)
        hard_after = independence_law.violations(new)
        assert hard_after == hard_before == [], 'закон независимости: %s' % hard_after
    else:
        json.loads(new)
    original, result = body, new.encode('utf-8')
    for folder, content in (('backup', original), ('pkg', result)):
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    rows.append({'file': rel, 'before': sha(original), 'after': sha(result), 'replace': [[a, b, 1] for a, b in reps]})

payload = {'name': NAME, 'count': len(rows), 'files': rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows),
                                  encoding='utf-8')
shutil.copy2(str(ROOT / 'tools/deploy/publish_mushki3.py'), str(OUT / 'publish_mushki3.py'))
# Разовый запуск заданием «Crontab» панели Timeweb, если SSH-консоль недоступна из облака (как 15.11.2026).
RUN_ONCE = """#!/bin/sh
# Разовая выкладка пакета %(name)s заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_mushki3.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_mushki3.py --check &&
  python3 publish_mushki3.py --publish &&
  python3 publish_mushki3.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_mushki3.py').read_bytes()), 'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
for r in rows:
    print('OK %s: %s… → %s…' % (r['file'], r['before'][:8], r['after'][:8]))
print('Готово: %d файла, счётчики и контакты — без нарушений, независимость — без нарушений. Пакет: %s' % (len(rows), OUT))
