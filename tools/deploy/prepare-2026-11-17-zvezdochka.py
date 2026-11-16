#!/usr/bin/env python3
"""Вид объекта без звёздочки в заявках с отраслевых страниц: пакет для Timeweb из актуального рабочего сайта (17.11.2026).

    python3 tools/deploy/prepare-2026-11-17-zvezdochka.py <новая папка пакета>

Решение владельца 17.11.2026: «Убери звёздочку из значения «Гостиница *» и других отраслевых пунктов формы в заявках».
Продолжение правки страниц ресторанов (tools/site/mushki-2026-11-16.md).

app.js добавляет в комментарий заявки строку «Вид объекта: <подпись пункта>», если подпись выбранного пункта поля
«Тип объекта» отличается от значения. На отраслевых страницах по умолчанию выбран пункт с звёздочкой обязательного поля
(«Гостиница *», «Магазин или торговая сеть *», «Пищевое производство *», «Склад, логистика *», «Фармпроизводство *»),
и звёздочка уходила в заявку. В скрипт формы каждой из 5 страниц сразу после заполнения поля msg добавлен один и тот же
фрагмент: в том же случае, что и app.js, он ставит первой строкой «Вид объекта: <подпись без звёздочки>» — app.js эту
строку уже не добавляет. При другом пункте поля — как раньше. Подпись в форме, type, send.php и app.min.js не меняются.

Страницы снимаются с сайта по HTTPS и правятся точечно (одна вставка на страницу), остальное — байт в байт. Проверки:
закон о счётчиках и контактах и закон независимости до и после, число замен, обратная замена даёт исходник байт в байт.

В папке пакета: backup/ и pkg/, MANIFEST.txt, deploy_payload.json, publish_zvezdochka.py и run_once.sh.
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

NAME = 'zvezdochka-2026-11-17'
VID = 'Вид объекта: '


def S(m):
    """Фрагмент скрипта формы: «Вид объекта: <подпись без звёздочки>» первой строкой msg (m — поле msg)."""
    return ("(function(m){var t=m.form&&m.form.elements.type,o=t&&t.options?t.options[t.selectedIndex]:null;"
            "if(o&&o.value&&o.text!==o.value&&m.value.indexOf('Вид объекта: ')<0)m.value='Вид объекта: '"
            "+o.text.replace(/\\u00a0/g,' ').replace(/\\s*\\*\\s*$/,'')+(m.value?'\\n'+m.value:'')})(" + m + ");")


FILES = [
    # файл на сервере, (старое, новое), подпись пункта по умолчанию
    ('gostinitsy/index.php', ("(/gostinitsy/)';},true);", "(/gostinitsy/)';" + S('e.msg') + "},true);"),
     '<option value="Гостиница" selected>Гостиница *</option>'),
    ('magaziny-i-torgovye-seti/index.php', ("ms.value=parts.join('\\n');", "ms.value=parts.join('\\n');" + S('ms')),
     '<option value="Магазин или торговая сеть" selected>Магазин или торговая сеть *</option>'),
    ('pishchevoe-proizvodstvo/index.php',
     ("(/pishchevoe-proizvodstvo/)';},true);", "(/pishchevoe-proizvodstvo/)';" + S('e.msg') + "},true);"),
     '<option value="Пищевое производство" selected>Пищевое производство *</option>'),
    ('sklady-i-logistika/index.php',
     ("(/sklady-i-logistika/)';});})();", "(/sklady-i-logistika/)';" + S('e.msg') + "});})();"),
     '<option value="Склад, логистика" selected>Склад, логистика *</option>'),
    ('farmatsevticheskie-proizvodstva/index.php', ("ms.value=parts.join('\\n');", "ms.value=parts.join('\\n');" + S('ms')),
     '<option value="Фармацевтическое производство" selected>Фармпроизводство *</option>'),
]
# исходник сборки, экранирование (2 — обратная косая черта удвоена в строке Python), поле msg в скрипте формы
SOURCES = [('tools/gostinitsy/build_page.py', 2, 'e.msg'), ('tools/restorany/template-food.html', 1, 'e.msg'),
           ('tools/site/unify.py', 2, 'e.msg'), ('tools/sklady/page.js', 1, 'e.msg'),
           ('tools/magaziny-i-torgovye-seti/assemble.py', 1, 'ms'), ('tools/farma/assemble.py', 1, 'ms')]

def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


def url_of(rel):
    if rel.endswith('index.php'):
        return rel[:-len('index.php')]
    return rel


# исходники сборки уже исправлены (иначе следующая полная сборка вернёт звёздочку)
for src, esc, m in SOURCES:
    t = (ROOT / src).read_text(encoding='utf-8')
    frag = S(m)
    assert t.count(frag if esc == 1 else frag.replace('\\', '\\\\')) == 1, 'в исходнике нет фрагмента: ' + src

live = module('check_live', 'tools/qa/check_live.py')
OUT = pathlib.Path(sys.argv[1]).resolve()
assert not OUT.exists(), 'используйте новую папку: прежние копии не перезаписываются'

rows = []
for rel, (a, b), opt in FILES:
    status, body = live.get(live.SITE + '/' + url_of(rel), tries=8)  # Timeweb из облака иногда отвечает ложным 502
    assert status == 200, '%s: HTTP %s' % (rel, status)
    old = body.decode('utf-8')
    assert '<?php' not in old and '<?=' not in old, rel + ': PHP в файле'
    bad = tracking_laws.check_page(old, counters=True)
    assert not bad, '%s: исходная страница: %s' % (rel, bad)
    hard_before = independence_law.violations(old)
    assert old.count(a) == 1 and old.count(b) == 0 and old.count(opt) == 1, rel + ': место вставки'
    assert "m.value.indexOf('Вид объекта: ')" not in old, rel + ': фрагмент уже есть'
    new = old.replace(a, b)
    assert new.replace(b, a) == old, rel + ': отличия вне согласованного места'
    bad = tracking_laws.check_page(new, counters=True)
    assert not bad, '%s: результат: %s' % (rel, bad)
    hard_after = independence_law.violations(new)
    assert hard_after == hard_before == [], 'закон независимости: %s' % hard_after
    original, result = body, new.encode('utf-8')
    for folder, content in (('backup', original), ('pkg', result)):
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    rows.append({'file': rel, 'before': sha(original), 'after': sha(result), 'replace': [[a, b, 1]]})

payload = {'name': NAME, 'count': len(rows), 'files': rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows),
                                  encoding='utf-8')
shutil.copy2(str(ROOT / 'tools/deploy/publish_zvezdochka.py'), str(OUT / 'publish_zvezdochka.py'))
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
    %(sp)s publish_zvezdochka.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_zvezdochka.py --check &&
  python3 publish_zvezdochka.py --publish &&
  python3 publish_zvezdochka.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_zvezdochka.py').read_bytes()), 'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
for r in rows:
    print('OK %s: %s… → %s…' % (r['file'], r['before'][:8], r['after'][:8]))
print('Готово: %d страниц, счётчики и контакты — без нарушений, независимость — без нарушений. Пакет: %s' % (len(rows), OUT))
