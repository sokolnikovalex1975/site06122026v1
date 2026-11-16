#!/usr/bin/env python3
"""«Мухи и мелкие мушки» вместо «Мухи и дрозофилы» и вид объекта без звёздочки в заявках со страниц ресторанов:
пакет для Timeweb из актуального рабочего сайта (16.11.2026).

    python3 tools/deploy/prepare-2026-11-16-mushki.py <новая папка пакета>

Решение владельца 16.11.2026: «Заменить заголовки «Мухи и дрозофилы» на «Мухи и мелкие мушки» на всех страницах»;
«Убрать звёздочку из значения «Ресторан или кафе *» в заявках со страницы ресторанов».

1. «Мухи и дрозофилы» (дрозофилы — тоже мухи, группа и её часть в одном ряду) → «Мухи и мелкие мушки», как на странице
   фармпроизводств: заголовки карточек вредителей (главная, «Рестораны и кафе», «Пищевое производство», «Дезинсекция»),
   та же фраза в подписи зоны «Мойка, трапы, отходы» (главная, «Пищевое производство»), в alt фото на «Дезинсекции»,
   в описании ссылки «Тараканы, мухи и дрозофилы: что делать при находке…» (две страницы ресторанов) и в поиске по сайту
   (search-index.json). Неразрывный пробел после «и» — там же, где был. Остальные упоминания дрозофил в тексте не меняются.
2. Вид объекта в заявке. app.js добавляет в комментарий заявки строку «Вид объекта: <подпись пункта>», если подпись
   отличается от значения; у пункта «Ресторан или кафе *» (значение «Ресторан или кафе») они отличаются только звёздочкой
   обязательного поля, и она уходила в заявку. Скрипт формы трёх страниц ресторанов (/restorany-i-kafe/,
   /dezinsektsiya/restorany-i-kafe/, /deratizatsiya/restorany-i-kafe/) теперь сам ставит первой строкой
   «Вид объекта: <подпись без звёздочки>» в том же случае — app.js эту строку уже не добавляет. Поле «Тип объекта»
   для send.php, подпись в форме и app.min.js (кеш браузеров — год) не меняются.

Страницы снимаются с сайта по HTTPS и правятся точечно, остальное — байт в байт. Проверки: закон о счётчиках и контактах
(tools/site/tracking_laws.py) и закон независимости (tools/site/independence_law.py) до и после; число каждой замены;
обратная замена даёт исходник байт в байт; «Мухи и дрозофилы» на страницах пакета не осталось; JSON поиска читается.
Метрика 113675622, UIS, Radist, телефон и почта не затрагиваются.

В папке пакета: backup/ и pkg/ (файлы до и после), MANIFEST.txt, deploy_payload.json, publish_mushki.py и run_once.sh.
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

NAME = 'mushki-2026-11-16'
NB = '\u00a0'
H_OLD, H_NEW = 'Мухи и дрозофилы', 'Мухи и мелкие мушки'
HN_OLD, HN_NEW = 'Мухи и' + NB + 'дрозофилы', 'Мухи и' + NB + 'мелкие мушки'
L_OLD, L_NEW = 'мухи и дрозофилы', 'мухи и мелкие мушки'
LN_OLD, LN_NEW = 'мухи и' + NB + 'дрозофилы', 'мухи и' + NB + 'мелкие мушки'
E_OLD, E_NEW = 'Мухи и&nbsp;дрозофилы', 'Мухи и&nbsp;мелкие мушки'
JS_OLD = "trim():''},rows=[];if(v('format'))"
JS_NEW = ("trim():''},rows=[],t=f.elements.type,o=t&&t.options?t.options[t.selectedIndex]:null;"
          "if(o&&o.value&&o.text!==o.value)rows.push('Вид объекта: '+o.text.replace(/\\u00a0/g,' ')"
          ".replace(/\\s*\\*\\s*$/,''));if(v('format'))")
PAIRS = {(H_OLD, H_NEW), (HN_OLD, HN_NEW), (L_OLD, L_NEW), (LN_OLD, LN_NEW), (E_OLD, E_NEW), (JS_OLD, JS_NEW)}
FILES = [
    # файл на сервере, замены (старое, новое, сколько раз); пробел после «и» — как был на сайте
    ('index.php', [(H_OLD, H_NEW, 1), (HN_OLD, HN_NEW, 1)]),
    ('restorany-i-kafe/index.php', [(HN_OLD, HN_NEW, 1), (LN_OLD, LN_NEW, 1), (JS_OLD, JS_NEW, 1)]),
    ('pishchevoe-proizvodstvo/index.php', [(H_OLD, H_NEW, 2)]),
    ('dezinsektsiya/index.php', [(H_OLD, H_NEW, 1), (E_OLD, E_NEW, 1)]),
    ('dezinsektsiya/restorany-i-kafe/index.php', [(JS_OLD, JS_NEW, 1)]),
    ('deratizatsiya/restorany-i-kafe/index.php', [(LN_OLD, LN_NEW, 1), (JS_OLD, JS_NEW, 1)]),
    ('search-index.json', [(H_OLD, H_NEW, 4)]),
]
LEFT = (H_OLD, HN_OLD, L_OLD, LN_OLD, E_OLD)
RESTAURANTS = ('restorany-i-kafe/index.php', 'dezinsektsiya/restorany-i-kafe/index.php',
               'deratizatsiya/restorany-i-kafe/index.php')


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


# исходники сборки уже исправлены (иначе следующая полная сборка вернёт старое)
for src in ('tools/food/main.html', 'tools/restorany/main.html', 'tools/restorany/template-food.html',
            'tools/dezinsektsiya/main.html', 'tools/site/unify.py'):
    t = (ROOT / src).read_text(encoding='utf-8')
    assert not any(x in t for x in LEFT), 'в исходнике осталось «Мухи и дрозофилы»: ' + src
for src in ('tools/restorany/assemble.py', 'tools/restorany-uslugi/build_pages.py'):
    t = (ROOT / src).read_text(encoding='utf-8')
    assert "rows.push('Вид объекта: '" in t, 'в исходнике нет строки «Вид объекта»: ' + src

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
    for a, b, n in reps:
        assert (a, b) in PAIRS
        assert new.count(a) == n, '%s: «%s» найдено %d раз, ждали %d' % (rel, a[:40], new.count(a), n)
        had = new.count(b)
        prev, new = new, new.replace(a, b)
        assert new.count(b) == had + n and len(new) == len(prev) + n * (len(b) - len(a)), rel + ': замена ' + a[:40]
    if not any(old.count(b) for a, b, n in reps):
        back = new
        for a, b, n in reversed(reps):
            back = back.replace(b, a)
        assert back == old, rel + ': отличия вне согласованных мест'
    else:  # «Мухи и мелкие мушки» уже было (страница фармпроизводств в поиске): сверка по кускам между заменами
        assert reps == [(H_OLD, H_NEW, 4)], rel
        pieces = old.split(H_OLD)
        assert H_NEW.join(pieces) == new and len(pieces) == 5, rel + ': отличия вне согласованных мест'
    assert not any(x in new for x in LEFT), rel + ': осталось «Мухи и дрозофилы»'
    if is_page:
        bad = tracking_laws.check_page(new, counters=True)
        assert not bad, '%s: результат: %s' % (rel, bad)
        hard_after = independence_law.violations(new)
        assert hard_after == hard_before == [], 'закон независимости: %s' % hard_after
        if rel in RESTAURANTS:
            assert new.count("rows.push('Вид объекта: '") == 1, rel + ': строка «Вид объекта»'
            assert '<option value="Ресторан или кафе" selected>Ресторан или кафе *</option>' in new, rel + ': пункт'
    else:
        json.loads(new)
    original, result = body, new.encode('utf-8')
    for folder, content in (('backup', original), ('pkg', result)):
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    rows.append({'file': rel, 'before': sha(original), 'after': sha(result), 'replace': [list(r) for r in reps]})

payload = {'name': NAME, 'count': len(rows), 'files': rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows),
                                  encoding='utf-8')
shutil.copy2(str(ROOT / 'tools/deploy/publish_mushki.py'), str(OUT / 'publish_mushki.py'))
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
    %(sp)s publish_mushki.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_mushki.py --check &&
  python3 publish_mushki.py --publish &&
  python3 publish_mushki.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_mushki.py').read_bytes()), 'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
for r in rows:
    print('OK %s: %s… → %s…' % (r['file'], r['before'][:8], r['after'][:8]))
print('Готово: %d файлов, счётчики и контакты — без нарушений, независимость — без нарушений. Пакет: %s' % (len(rows), OUT))
