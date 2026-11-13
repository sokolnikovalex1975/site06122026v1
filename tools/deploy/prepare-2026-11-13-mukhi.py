#!/usr/bin/env python3
"""Пункт «Мухи или мелкие мушки» в формах заявки общепита: пакет для Timeweb из актуального рабочего сайта (13.11.2026).

    python3 tools/deploy/prepare-2026-11-13-mukhi.py <новая папка пакета>

Замечание владельца 13.11.2026: в форме заявки пункт «Мухи или дрозофилы» — логическая ошибка (дрозофилы — тоже мухи),
«исправь её и оптимизируй это значение». Решение: один пункт «Мухи или мелкие мушки» — крупные мухи (комнатные, падальные)
и мелкие мушки (дрозофилы в баре и на фруктах, бабочницы в трапах), словами посетителя, без «вида и рода» в одном ряду;
так же названа группа на странице фармпроизводств («Мухи и мелкие мушки»).

Страницы снимаются с сайта по HTTPS и правятся точечно, остальное — байт в байт:
  * restorany-i-kafe/index.php — поле «Задача»: «Мухи или&nbsp;дрозофилы» → «Мухи или&nbsp;мелкие мушки»
    (неразрывный пробел после «или», как ставит типографика tools/legal/typo.py при сборке страницы);
  * dezinsektsiya/restorany-i-kafe/index.php — поле «Что беспокоит»: «Мухи, дрозофилы или мошки» → «Мухи или мелкие мушки».
Значение уходит в заявку строкой «Задача: …» / «Что беспокоит: …» в поле msg; send.php этот пункт не проверяет.
Метрика 113675622, UIS, Radist, телефон и почта не затрагиваются.

Проверки: закон о счётчиках и контактах (tools/site/tracking_laws.py) и закон независимости (tools/site/independence_law.py)
до и после; обратная замена даёт исходную страницу байт в байт; в поле выбора ровно прежние пункты, кроме исправленного.

В папке пакета: backup/ и pkg/ (страницы до и после), MANIFEST.txt и deploy_payload.json для publish_mukhi.py —
серверный скрипт сам применяет те же замены к страницам в public_html и сверяет SHA-256 до и после.
"""
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
import tracking_laws  # noqa: E402

NAME = 'mukhi-2026-11-13'
NB = '\u00a0'
NEW_TEXT = 'Мухи или мелкие мушки'
PAGES = [
    # файл на сервере, старый пункт, новый пункт, подпись поля, пункты поля после правки
    ('restorany-i-kafe/index.php',
     '<option>Мухи или' + NB + 'дрозофилы</option>', '<option>Мухи или' + NB + 'мелкие мушки</option>', 'Задача',
     ['Задача', 'Договор на регулярное обслуживание', 'Срочно: тараканы', 'Срочно: мыши или крысы',
      'Мухи или мелкие мушки', 'Подготовка к проверке', 'Открытие нового заведения']),
    ('dezinsektsiya/restorany-i-kafe/index.php',
     '<option>Мухи, дрозофилы или мошки</option>', '<option>Мухи или мелкие мушки</option>', 'Что беспокоит',
     ['Что беспокоит', 'Тараканы', 'Мухи или мелкие мушки', 'Муравьи', 'Моль или жуки на складе',
      'Нужен договор и журнал к проверке']),
]


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


def options(s):
    m = re.findall(r'<select id="f-task" name="task">(.*?)</select>', s, re.S)
    assert len(m) == 1, 'поле f-task: найдено %d' % len(m)
    return [re.sub(r'<[^>]+>', '', t).replace(NB, ' ') for t in re.findall(r'<option[^>]*>(.*?)</option>', m[0], re.S)]


# пункт в исходниках сборки совпадает с пакетом (иначе следующая полная сборка вернёт старое)
src_rest = (ROOT / 'tools/restorany/main.html').read_text(encoding='utf-8')
assert src_rest.count('<option>' + NEW_TEXT + '</option>') == 1 and 'дрозофилы</option>' not in src_rest
src_usl = (ROOT / 'tools/restorany-uslugi/build_pages.py').read_text(encoding='utf-8')
assert src_usl.count("'" + NEW_TEXT + "'") == 1 and 'дрозофилы или мошки' not in src_usl
for rel, _, new_opt, _, _ in PAGES:
    repo_page = (ROOT / rel.replace('index.php', 'index.html')).read_text(encoding='utf-8')
    assert repo_page.count(new_opt) == 1, 'в репозитории другой пункт: ' + rel

live = module('check_live', 'tools/qa/check_live.py')
OUT = pathlib.Path(sys.argv[1]).resolve()
assert not OUT.exists(), 'используйте новую папку: прежние копии не перезаписываются'

rows = []
for rel, old_opt, new_opt, label, want in PAGES:
    url = live.SITE + rel[:-len('index.php')]
    status, body = live.get(url, tries=8)  # Timeweb из облака иногда отвечает ложным 502 несколько раз подряд
    assert status == 200, '%s: HTTP %s' % (url, status)
    old = body.decode('utf-8')
    assert '<?php' not in old and '<?=' not in old, rel + ': PHP в HTML'
    bad = tracking_laws.check_page(old, counters=True)
    assert not bad, '%s: исходная страница: %s' % (rel, bad)
    hard_before = independence_law.violations(old)
    assert old.count(old_opt) == 1, '%s: старый пункт найден %d раз' % (rel, old.count(old_opt))
    assert ('<label class="sr-only" for="f-task">%s</label>' % label) in old, rel + ': другая подпись поля'
    new = old.replace(old_opt, new_opt)
    assert new.replace(new_opt, old_opt) == old, rel + ': отличия вне согласованного места'
    got = options(new)
    assert got == want, '%s: пункты поля %s' % (rel, got)
    bad = tracking_laws.check_page(new, counters=True)
    assert not bad, '%s: результат: %s' % (rel, bad)
    hard_after = independence_law.violations(new)
    assert hard_after == hard_before == [], 'закон независимости: %s' % hard_after
    assert 'дрозофилы</option>' not in new and 'дрозофилы или мошки</option>' not in new
    original, result = body, new.encode('utf-8')
    for folder, content in (('backup', original), ('pkg', result)):
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    rows.append({'file': rel, 'before': sha(original), 'after': sha(result), 'replace': [[old_opt, new_opt, 1]],
                 'append': ''})

payload = {'name': NAME, 'count': len(rows), 'files': rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows),
                                  encoding='utf-8')
shutil.copy2(str(ROOT / 'tools/deploy/publish_mukhi.py'), str(OUT / 'publish_mukhi.py'))
for r in rows:
    print('OK %s: %s… → %s…' % (r['file'], r['before'][:8], r['after'][:8]))
print('Готово: %d страницы, счётчики и контакты — без нарушений, независимость — без нарушений. Пакет: %s' % (len(rows), OUT))
