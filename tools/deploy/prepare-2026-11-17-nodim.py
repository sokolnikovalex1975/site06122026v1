#!/usr/bin/env python3
"""Главная без затемнения на телефоне: пакет для Timeweb (17.11.2026).

    python3 tools/deploy/prepare-2026-11-17-nodim.py <новая папка пакета>

Закон владельца 17.11.2026 (README, «на телефоне ничего не затемнять»); команда владельца 17.11.2026: «Выкладывай главную
без затемнения на телефоне на Timeweb». Выкладывается только главная (index.php): её стили встроены в страницу, поэтому
style.css, app.min.js и версии ?v= не меняются. Четыре точные замены в главной с рабочего сайта (до 760 px):
  1. preload фото первого экрана: img/hero-m-dim.webp → img/hero-m.webp (светлое фото уже на сервере, тот же файл);
  2. блок телефона: светлое фото полосой над текстом, без тёмной заливки; у фото этапов нет заливки; [data-scrub] — без
     приглушения (правило !important сильнее приглушения из app.min.js);
  3. фон блока заявки (.cta-bg, затемнённое фото) на телефоне не показывается;
  4. экран ниже 520 px — полосы фото нет (как на страницах отраслей).
Новые участки берутся из главной репозитория (собрана tools/build.py из style.css коммита правки), прежние — из главной
рабочего сайта; в обоих каждый участок ровно один раз. Неопубликованные правки репозитория (переход к блоку под шапку и др.)
в пакет не попадают: меняются только эти 4 участка, остальное — байт в байт.

В папке пакета: backup/ и pkg/, MANIFEST.txt, deploy_payload.json, publish_nodim.py и run_once.sh.
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

NAME = 'nodim-2026-11-17'
REPO = (ROOT / 'index.html').read_text(encoding='utf-8')


def seg(s, start, end):
    """Участок от start (включительно) до end (не включая); оба — ровно один раз."""
    assert s.count(start) == 1 and s.count(end) == 1, (start[:60], s.count(start), s.count(end))
    i = s.find(start)
    j = s.find(end, i)
    assert j > i
    return s[i:j]


PRELOAD = ('<link rel="preload" href="img/hero-m-dim.webp" as="image" media="(max-width:760px)">',
           '<link rel="preload" href="img/hero-m.webp" as="image" media="(max-width:760px)">')
END = '.hero h1{margin:26px 0 20px'
PHONE_OLD = '.hero-bg{background-image:url(img/hero-m-dim.webp)}.hero:before{background:linear-gradient(180deg,#09090b80,#09090bd1 60%,#000)}'
PHONE_NEW = seg(REPO, '.hero-bg{background-image:url(img/hero-m.webp)', END)
CTA = ('.cta-bg{background-image:url(img/cta-m.webp)}', '.cta-bg{display:none}')
LOWH_ANCHOR = '@media (max-width:760px){#hero.hero:not(.f-hero){padding-bottom:32px}}'
LOWH_NEW = seg(REPO, LOWH_ANCHOR, '.lowfx .hero-lens,')
REPS = [PRELOAD, (PHONE_OLD, PHONE_NEW), CTA, (LOWH_ANCHOR, LOWH_NEW)]
# новые участки — в главной репозитория, прежних там уже нет
for a, b in REPS:
    assert REPO.count(b) == 1, 'в главной репозитория нет нового участка: ' + b[:60]
    assert a == LOWH_ANCHOR or REPO.count(a) == 0, 'в главной репозитория остался прежний участок: ' + a[:60]
assert 'hero-m-dim' not in PHONE_NEW and 'brightness' not in PHONE_NEW and '[data-scrub] .sw{opacity:1!important}' in PHONE_NEW
FILES = [('index.php', REPS)]


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

# светлое фото уже на сервере — тот же файл, что в репозитории
status, img = live.get(live.SITE + '/img/hero-m.webp', tries=8)
assert status == 200 and sha(img) == sha((ROOT / 'img/hero-m.webp').read_bytes()), 'img/hero-m.webp на сайте другое'

rows = []
for rel, reps in FILES:
    status, body = live.get(live.SITE + '/', tries=8)  # Timeweb из облака иногда отвечает ложным 502
    assert status == 200, '%s: HTTP %s' % (rel, status)
    old = body.decode('utf-8')
    assert '<?php' not in old and '<?=' not in old, rel + ': PHP в файле'
    bad = tracking_laws.check_page(old, counters=True)
    assert not bad, '%s: исходная страница: %s' % (rel, bad)
    hard_before = independence_law.violations(old)
    new = old
    for a, b in reps:
        assert new.count(a) == 1, '%s: «%s» найдено %d раз' % (rel, a[:60], new.count(a))
        pieces = new.split(a)
        prev, new = new, new.replace(a, b)
        assert b.join(pieces) == new and len(new) == len(prev) + len(b) - len(a), rel + ': замена ' + a[:60]
    # обратная замена даёт исходник байт в байт
    back = new
    for a, b in reversed(reps):
        assert back.count(b) == 1
        back = back.replace(b, a)
    assert back == old, 'обратная замена не даёт исходник'
    assert 'hero-m-dim.webp' not in new and 'img/cta-m.webp' not in new
    bad = tracking_laws.check_page(new, counters=True)
    assert not bad, '%s: результат: %s' % (rel, bad)
    hard_after = independence_law.violations(new)
    assert hard_after == hard_before == [], 'закон независимости: %s' % hard_after
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
shutil.copy2(str(ROOT / 'tools/deploy/publish_nodim.py'), str(OUT / 'publish_nodim.py'))
# Разовый запуск заданием «Crontab» панели Timeweb (SSH-консоль из облака недоступна, как с 15.11.2026).
RUN_ONCE = """#!/bin/sh
# Разовая выкладка пакета %(name)s заданием Crontab панели Timeweb (удалить задание после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_nodim.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_nodim.py --check &&
  python3 publish_nodim.py --publish &&
  python3 publish_nodim.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_nodim.py').read_bytes()), 'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
for r in rows:
    print('OK %s: %s… → %s…' % (r['file'], r['before'][:8], r['after'][:8]))
print('Готово: %d файл, 4 замены, счётчики и контакты — без нарушений, независимость — без нарушений. Пакет: %s' % (len(rows), OUT))
