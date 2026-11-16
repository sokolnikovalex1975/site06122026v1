#!/usr/bin/env python3
"""«Мухи и мелкие мушки» в заголовках страниц магазинов и бизнес-центров: пакет для Timeweb из рабочего сайта (17.11.2026).

    python3 tools/deploy/prepare-2026-11-17-mushki2.py <новая папка пакета>

Решение владельца 17.11.2026: «Приведи заголовки «Дрозофилы и мухи» и «Мухи, дрозофилы, бабочницы» к «Мухи и мелкие мушки»».
Продолжение tools/site/mushki-2026-11-16.md. Меняются только заголовки карточек вредителей:
  /magaziny-i-torgovye-seti/                      «Дрозофилы и&nbsp;мухи»       → «Мухи и&nbsp;мелкие мушки»
  /biznes-tsentry-torgovye-tsentry-predpriyatiya/ «Мухи, дрозофилы, бабочницы»  → «Мухи и мелкие мушки»
и те же два заголовка в списках разделов search-index.json. Упоминания дрозофил и бабочниц в тексте карточек, в зонах
и в таблице журнала не меняются. Неразрывный пробел после «и» — там же, где был.

Файлы снимаются с сайта по HTTPS и правятся точечно, остальное — байт в байт (сверка по кускам между заменами: в
search-index.json «Мухи и мелкие мушки» уже есть). Проверки: закон о счётчиках и контактах и закон независимости до и после,
число замен, JSON читается.

В папке пакета: backup/ и pkg/, MANIFEST.txt, deploy_payload.json, publish_mushki2.py и run_once.sh.
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

NAME = 'mushki2-2026-11-17'
MAG = ('Дрозофилы и&nbsp;мухи', 'Мухи и&nbsp;мелкие мушки')
BC = ('<h3>Мухи, дрозофилы, бабочницы</h3>', '<h3>Мухи и мелкие мушки</h3>')
SI_MAG = (' · Дрозофилы и мухи · ', ' · Мухи и мелкие мушки · ')
SI_BC = (' · Мухи, дрозофилы, бабочницы · ', ' · Мухи и мелкие мушки · ')
FILES = [
    ('magaziny-i-torgovye-seti/index.php', [MAG]),
    ('biznes-tsentry-torgovye-tsentry-predpriyatiya/index.php', [BC]),
    ('search-index.json', [SI_MAG, SI_BC]),
]
LEFT = ('Дрозофилы и&nbsp;мухи', 'Дрозофилы и мухи', 'Дрозофилы и\u00a0мухи', 'Мухи, дрозофилы, бабочницы')

# исходники сборки уже исправлены (иначе следующая полная сборка вернёт старое)
for src in ('tools/magaziny-i-torgovye-seti/main.html', 'tools/bctc/main.html', 'magaziny-i-torgovye-seti/index.html',
            'biznes-tsentry-torgovye-tsentry-predpriyatiya/index.html', 'search-index.json'):
    t = (ROOT / src).read_text(encoding='utf-8')
    assert not any(x in t for x in LEFT), 'в исходнике остался старый заголовок: ' + src


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
shutil.copy2(str(ROOT / 'tools/deploy/publish_mushki2.py'), str(OUT / 'publish_mushki2.py'))
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
    %(sp)s publish_mushki2.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_mushki2.py --check &&
  python3 publish_mushki2.py --publish &&
  python3 publish_mushki2.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_mushki2.py').read_bytes()), 'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
for r in rows:
    print('OK %s: %s… → %s…' % (r['file'], r['before'][:8], r['after'][:8]))
print('Готово: %d файла, счётчики и контакты — без нарушений, независимость — без нарушений. Пакет: %s' % (len(rows), OUT))
