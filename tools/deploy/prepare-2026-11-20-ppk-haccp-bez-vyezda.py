#!/usr/bin/env python3
"""Страница ППК: для ППК по ХАССП выезд не нужен — пакет для Timeweb (20.11.2026).

    python3 tools/deploy/prepare-2026-11-20-ppk-haccp-bez-vyezda.py <новая папка пакета>

Команда владельца 20.11.2026: «ППК по ХАССП выезд не нужен! Внеси исправление на таймвеб сразу».
Замены — tools/site/ppk_haccp_bez_vyezda.py. Файлы снимаются с рабочего сайта по HTTPS:
  razrabotka-ppk/index.php — ответ FAQ, шаг «Сведения об объекте», FAQPage (3 участка);
  search-index.json        — описание вопроса razrabotka-ppk/#q12 (1 участок).
Проверки — как в prepare-2026-11-20-ppk-bez-vyezda.py.
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
import ppk_haccp_bez_vyezda as ppk_bez_vyezda  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'ppk-haccp-bez-vyezda-2026-11-20'
FILES = [('razrabotka-ppk/', 'razrabotka-ppk/index.php', ppk_bez_vyezda.PAGE_REPL, True),
         ('search-index.json', 'search-index.json', ppk_bez_vyezda.INDEX_REPL, False)]
TRACK = ('mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<select', '<?', 'fetch(', 'xmlhttp',
         '<script', '<style', '<link', 'src=')


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
repo_page = (ROOT / 'razrabotka-ppk/index.html').read_text(encoding='utf-8')
rows = []
for url, rel, repl, is_page in FILES:
    status, body = live.get(live.SITE + url, tries=8)  # Timeweb из облака иногда отвечает ложным 502
    assert status == 200, '%s: HTTP %s' % (rel, status)
    old = body.decode('utf-8')
    for a, b, c in repl:
        assert ('выезд' in a or 'приезжает' in a) and 'без\xa0выезда' in b.replace('без выезда', 'без\xa0выезда'), rel
        for t in TRACK:
            assert t not in a.lower() and t not in b.lower(), '%s: замена затрагивает %s' % (rel, t)
    if is_page:
        assert '<?php' not in old and '<?=' not in old, rel + ': PHP в файле'
        bad = tracking_laws.check_page(old, counters=True)
        assert not bad, '%s: исходная страница: %s' % (rel, bad)
        hard_before = independence_law.violations(old)
    new = ppk_bez_vyezda.apply(old, repl)
    assert 'нужен ли выезд' not in new and 'специалист приезжает на\xa0объект' not in new, rel + ': фраза осталась'
    back = new
    for a, b, c in reversed(repl):
        assert back.count(b) >= c
    # обратная замена: каждый новый участок встречается ровно столько раз, сколько заменён
    for a, b, c in repl:
        assert new.count(b) == old.count(b) + c, rel + ': «%s» встречается не там' % b[:40]
    if is_page:
        for a, b, c in repl:
            assert repo_page.count(b) >= c and a not in repo_page, rel + ': не как в репозитории GitHub'
        bad = tracking_laws.check_page(new, counters=True)
        assert not bad, '%s: результат: %s' % (rel, bad)
        hard_after = independence_law.violations(new)
        assert hard_after == hard_before == [], '%s: закон независимости: %s' % (rel, hard_after)
    else:
        json.loads(new)
    original, result = body, new.encode('utf-8')
    for folder, content in (('backup', original), ('pkg', result)):
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    rows.append({'file': rel, 'before': sha(original), 'after': sha(result), 'replace': [[a, b, c] for a, b, c in repl]})
    print('OK %s: %s… → %s… (%+d байт)' % (rel, sha(original)[:8], sha(result)[:8], len(result) - len(original)))

payload = {'name': NAME, 'count': len(rows), 'files': rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows),
                                  encoding='utf-8')
shutil.copy2(str(ROOT / 'tools/deploy/publish_ppk_haccp_bez_vyezda.py'), str(OUT / 'publish_ppk_haccp_bez_vyezda.py'))
RUN_ONCE = """#!/bin/sh
# Разовая выкладка пакета %(name)s на Timeweb (SSH-консоль панели). Повторный запуск ничего не делает.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_ppk_haccp_bez_vyezda.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_ppk_haccp_bez_vyezda.py --check &&
  python3 publish_ppk_haccp_bez_vyezda.py --publish &&
  python3 publish_ppk_haccp_bez_vyezda.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_ppk_haccp_bez_vyezda.py').read_bytes()),
       'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
print('Готово: 2 файла, выезд для ППК по ХАССП убран, счётчики и контакты — без нарушений. Пакет: %s' % OUT)
