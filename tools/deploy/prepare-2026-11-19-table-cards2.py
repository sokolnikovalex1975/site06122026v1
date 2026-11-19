#!/usr/bin/env python3
"""Без прокрутки вбок на остальных страницах: пакет для Timeweb (19.11.2026, второй пакет).

    python3 tools/deploy/prepare-2026-11-19-table-cards2.py <новая папка пакета>

Вторая команда владельца 19.11.2026: «Исправь ошибки прокрутки вбок на остальных страницах. И выложи их сразу на TimeWeb».
Страницы: дезинфекция (таблицы .dzf-kinds и .dzf-freq + заголовок «Документы по дезинфекции» на 441–520 px — 8,4vw вместо
9vw), лаборатория: анализ пищевых продуктов, контроль стерилизаторов, замер освещённости, материалы: контроль работы
стерилизаторов (таблицы .lbs-t на 601–760 px); «Программа пест-контроля», «Нормативная база» и «Документы для
Роспотребнадзора» (таблицы .p-plan-table, .nb-docs, .dk-tbl карточками на 861–980, 901–1000 и 901–1040 px — копия
карточек страницы до 860/900 px; заголовок #dogovory на 441–520 px — 8,4vw). Механика та же, что у первого пакета (описание ниже), строка стилей — table_cards.rule()
с EXTRA для дезинфекции.

Первый пакет (table-cards-2026-11-19, опубликован 19.11.2026 15:48 МСК):

Команда владельца 19.11.2026: «Исправь прокрутку вбок на вентиляции и дезинсекции в превью, потом покажи мне», затем
«Выкладывай эту правку на TimeWeb». Правка на GitHub — коммит d3f6cfb (tools/site/table_cards.py, CHANGES.md).

Выкладываются 2 страницы: вентиляция и дезинсекция. Стили встроены в страницы, поэтому style.css, app.min.js, версии ?v=
и другие страницы не меняются. В каждой странице с рабочего сайта одна точная замена: строка <style id="t-inset">…</style>
→ та же строка и сразу после неё строка <style id="t-cards"> (table_cards.rule(), та же, что в превью GitHub): на 601–760 px
широкие таблицы (вентиляция — .v-freq; дезинсекция — .dz-methods и #sanpin .d-table) показываются карточками, как на
телефоне. Результат сверяется с table_cards.apply() байт в байт. Проверки при сборке: участок ровно один раз, обратная
замена даёт исходник байт в байт, tracking_laws (Метрика 113675622, UIS, Radist, телефон и почта) и закон независимости —
без нарушений до и после.

В папке пакета: backup/ и pkg/ (копии до и после), MANIFEST.txt, deploy_payload.json, publish_table_cards2.py и run_once.sh.
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
import table_cards as tc  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'table-cards2-2026-11-19'
PAGES = ['dezinfektsiya', 'laboratornye-issledovaniya/analiz-pishchevykh-produktov',
         'laboratornye-issledovaniya/kontrol-sterilizatorov', 'laboratornye-issledovaniya/zamer-osveshchennosti',
         'materialy/kontrol-raboty-sterilizatorov', 'materialy/programma-pest-kontrolya', 'normativnaya-baza',
         'normativnaya-baza/dokumenty-dlya-rospotrebnadzora']
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
    assert 't-cards' not in old, rel + ': уже выложено?'
    key = slug + '/index.html'
    expected = tc.apply(key, old)
    m = tc.INSET.search(old)
    line = m.group(0)
    assert line.endswith('\n'), rel + ': после строки t-inset нет перевода строки'
    rule = re.search(r'<style id="t-cards">.*?</style>\n', expected, re.S).group(0)
    assert rule in (ROOT / key).read_text(encoding='utf-8'), rel + ': строка стилей не как в превью GitHub'
    reps = [(line, line + rule)]
    for a, b in reps:
        for t in TRACK:
            assert t not in a.lower() and t not in b.lower(), '%s: замена затрагивает %s' % (rel, t)
    new = old
    for a, b in reps:
        assert new.count(a) == 1, '%s: «%s» найдено %d раз' % (rel, a[:60], new.count(a))
        prev, new = new, new.replace(a, b)
        assert len(new) == len(prev) + len(b) - len(a), rel + ': замена ' + a[:60]
    assert new == expected, rel + ': результат не совпадает с table_cards.apply()'
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
shutil.copy2(str(ROOT / 'tools/deploy/publish_table_cards2.py'), str(OUT / 'publish_table_cards2.py'))
RUN_ONCE = """#!/bin/sh
# Разовая выкладка пакета %(name)s на Timeweb (SSH-консоль панели или разовое задание Crontab — удалить после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_table_cards2.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_table_cards2.py --check &&
  python3 publish_table_cards2.py --publish &&
  python3 publish_table_cards2.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_table_cards2.py').read_bytes()),
       'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
print('Готово: %d страниц, по 1 замене, счётчики и контакты — без нарушений, независимость — без нарушений. Пакет: %s'
      % (len(rows), OUT))
