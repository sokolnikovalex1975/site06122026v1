#!/usr/bin/env python3
"""Инфографика в стиле лаборатории на рабочем сайте: пакет для Timeweb (19.11.2026).

    python3 tools/deploy/prepare-2026-11-19-infografika.py <новая папка пакета>

Команда владельца 19.11.2026 (чат согласований): «ПЕСТКОНТРОЛЬ Центр: … 2 делай вариант а» — иконка «Пест-контроль»
вариант A и выкладка всего согласованного набора иконок на рабочий сайт. Страницы снимаются с сайта по HTTPS и правятся
тем же tools/site/infografika.py, что и репозиторий (apply), поэтому неопубликованные правки репозитория в пакет не
попадают. Страницы /zashchita-ot-proniknoveniya-gryzunov/ на рабочем сайте нет (HTTP 404) — она не выкладывается.

В пакет входят новые картинки img/ig-*.webp (только те, на которые ссылаются страницы; на сайте их ещё нет) и страницы
в виде точных замен «было → стало»: каждая замена найдена на странице ровно один раз, последовательное применение даёт
результат apply() байт в байт; откат — из резервной копии страницы. Замены не затрагивают <script>, счётчики Метрики,
UIS и Radist, ссылки tel: и mailto:. Закон о счётчиках и контактах (tracking_laws.check_page) и закон независимости —
до и после; faq_first, tracking_laws, independence_law и infografika --check-prod на результате.

В папке пакета: backup/ (страницы как на сайте), pkg/ (страницы и картинки после выкладки), MANIFEST.txt,
deploy_payload.json, publish_infografika.py и run_once.sh.
"""
import base64
import difflib
import hashlib
import importlib.util
import json
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import independence_law  # noqa: E402
import infografika  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'infografika-2026-11-19'
NOT_LIVE = {'zashchita-ot-proniknoveniya-gryzunov/index.html'}  # на рабочем сайте нет (HTTP 404)
# лабораторные иконки, которые ставит инфографика (они уже на сайте со страницы «Лабораторные исследования»)
LAB = sorted(set(k for t in (infografika.VU, infografika.PR_MINI) for k in t.values() if k.startswith('lab-'))
             | set(k for k in infografika.DK_GROUPS if k.startswith('lab-'))
             | set(k for sid, keys in infografika.STEPS.values() for k in keys if k.startswith('lab-')))
FORBIDDEN = ('<script', 'mc.yandex', 'ym(', 'comagic', 'uiscom', 'radist', 'tel:', 'mailto:', '<?')


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


def tokens(s):
    return re.split(r'(?<=>)', s)


def pairs(old, new):
    """Точные замены «было → стало»: участки разницы по тегам, с контекстом до единственного вхождения."""
    a, b = tokens(old), tokens(new)
    assert ''.join(a) == old and ''.join(b) == new
    ops = [op for op in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes() if op[0] != 'equal']
    out, cur, prev_end = [], old, 0
    for tag, i1, i2, j1, j2 in ops:
        lo, hi = i1, i2
        while True:
            pa = ''.join(a[lo:hi])
            if pa and cur.count(pa) == 1:
                break
            assert lo > prev_end or hi < len(a), 'не удалось сделать замену однозначной'
            if lo > prev_end:  # контекст слева — только до конца предыдущей замены
                lo -= 1
            if hi < len(a):
                hi += 1
        pb = ''.join(a[lo:i1]) + ''.join(b[j1:j2]) + ''.join(a[i2:hi])
        prev_end = hi
        assert pa != pb
        low = (pa + pb).lower()
        for bad in FORBIDDEN:
            assert bad not in low, 'замена затрагивает %s: %s' % (bad, pa[:120])
        cur = cur.replace(pa, pb, 1)
        out.append([pa, pb, 1])
    assert cur == new, 'замены не дают результат apply()'
    return out


def replay(old, reps):
    s = old
    for a, b, c in reps:
        assert s.count(a) == c, 'число вхождений изменилось: ' + a[:80]
        s = s.replace(a, b)
    return s


live = module('check_live', 'tools/qa/check_live.py')
OUT = pathlib.Path(sys.argv[1]).resolve()
assert not OUT.exists(), 'используйте новую папку: прежние копии не перезаписываются'

rows, images, lab = [], set(), set()
for rel_html in infografika.pages():
    path = rel_html[:-len('index.html')]
    rel = path + 'index.php'
    status, body = live.get(live.SITE + path, tries=8)  # Timeweb из облака иногда отвечает ложным 502
    if rel_html in NOT_LIVE:
        assert status == 404, '%s: ожидался 404, на сайте %s' % (rel, status)
        print('нет на сайте (404), не выкладывается:', path)
        continue
    assert status == 200, '%s: HTTP %s' % (rel, status)
    old = body.decode('utf-8')
    assert '<?php' not in old and '<?=' not in old, rel + ': PHP в файле'
    bad = tracking_laws.check_page(old, counters=True)
    assert not bad, '%s: исходная страница: %s' % (rel, bad)
    assert independence_law.violations(old) == [], rel + ': закон независимости до выкладки'
    assert 'id="ig"' not in old and 'img/ig-' not in old, rel + ': инфографика уже на сайте'
    report = {}
    new = infografika.apply(rel_html, old, report)
    assert new != old, rel + ': нечего менять'
    assert infografika.apply(rel_html, new) == new, rel + ': повторное применение меняет страницу'
    reps = pairs(old, new)
    assert replay(old, reps) == new
    # откат на сервере — из резервной копии страницы (backup/), а не обратными заменами
    bad = tracking_laws.check_page(new, counters=True)
    assert not bad, '%s: результат: %s' % (rel, bad)
    assert independence_law.violations(new) == [], rel + ': закон независимости после выкладки'
    # счётчики, телефоны и почта — те же вхождения, что до выкладки
    for needle in ('mc.yandex.ru', 'ym(113675622', 'uiscom', 'comagic', 'radist', 'href="tel:', 'href="mailto:', '<script'):
        assert old.count(needle) == new.count(needle), '%s: изменилось число «%s»' % (rel, needle)
    used = infografika.used_images(new, rel_html)
    images.update(used)
    pre = '../' * rel_html.count('/')
    lab.update('img/%s.webp' % k for k in LAB if 'src="%simg/%s.webp"' % (pre, k) in new)
    original, result = body, new.encode('utf-8')
    for folder, content in (('backup', original), ('pkg', result)):
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    rows.append({'file': rel, 'before': sha(original), 'after': sha(result), 'replace': reps,
                 'blocks': report[rel_html][0], 'icons': report[rel_html][1]})
    print('страница %s: блоков %d, иконок %d, замен %d' % (path or '/', len(report[rel_html][0]), report[rel_html][1], len(reps)))

# лабораторные иконки уже на сайте — сверяем, что они те же, что в репозитории
for f in sorted(lab):
    status, body = live.get(live.SITE + f, tries=8)
    assert status == 200 and sha(body) == sha((ROOT / f).read_bytes()), '%s: на сайте %s или другой файл' % (f, status)
img_rows = []
for f in sorted(images):
    data = (ROOT / f).read_bytes()
    assert data[:4] == b'RIFF' and data[8:12] == b'WEBP' and 1000 < len(data) < 40000, f
    status, _ = live.get(live.SITE + f, tries=8)
    assert status == 404, '%s: на сайте уже есть (HTTP %s)' % (f, status)
    (OUT / 'pkg' / f).parent.mkdir(parents=True, exist_ok=True)
    (OUT / 'pkg' / f).write_bytes(data)
    img_rows.append({'file': f, 'before': None, 'after': sha(data), 'content_b64': base64.b64encode(data).decode('ascii')})
print('картинок новых %d (%d КБ), лабораторных уже на сайте %d' % (len(img_rows), sum(len(base64.b64decode(r['content_b64'])) for r in img_rows) // 1024, len(lab)))

pages_pkg = [str(OUT / 'pkg' / r['file']) for r in rows]
for args in (['independence_law.py', '--check-prod'], ['tracking_laws.py', '--check-prod'], ['faq_first.py', '--check-prod'],
             ['infografika.py', '--check-prod']):
    r = subprocess.run([sys.executable, str(ROOT / 'tools/site' / args[0]), args[1]] + pages_pkg,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    print('%s %s: exit %d — %s' % (args[0], args[1], r.returncode, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ''))
    assert r.returncode == 0, r.stdout

payload = {'name': NAME, 'images': len(img_rows), 'pages': len(rows), 'files': img_rows + rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'] or '-' * 64, r['after'], r['file'])
                                          for r in img_rows + rows), encoding='utf-8')
shutil.copy2(str(ROOT / 'tools/deploy/publish_infografika.py'), str(OUT / 'publish_infografika.py'))
RUN_ONCE = """#!/bin/sh
# Разовая выкладка пакета %(name)s заданием Crontab панели Timeweb или из SSH-консоли (задание удалить после запуска).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_infografika.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_infografika.py --check &&
  python3 publish_infografika.py --publish &&
  python3 publish_infografika.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((OUT / 'publish_infografika.py').read_bytes()), 'sd': sha((OUT / 'deploy_payload.json').read_bytes())}
(OUT / 'run_once.sh').write_text(RUN_ONCE, encoding='utf-8')
(OUT / 'run_once.sh').chmod(0o755)
print('Готово: %d страниц (%d замен), %d новых картинок; счётчики и контакты — без нарушений, независимость — без нарушений. '
      'Пакет: %s' % (len(rows), sum(len(r['replace']) for r in rows), len(img_rows), OUT))
