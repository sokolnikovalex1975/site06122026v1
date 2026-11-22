#!/usr/bin/env python3
"""Линия сканирования (.panel-scan) проходит весь блок до нижнего края (23.11.2026): точечный пакет для Timeweb.

    python3 tools/deploy/prepare-2026-11-23-scan.py <новая папка>     # снять сайт по HTTPS и собрать пакет
    python3 tools/deploy/prepare-2026-11-23-scan.py <папка> --check   # пересобрать из <папка>/backup и сверить с pkg

Замечание владельца 23.11.2026: фиолетовая линия в блоке самопроверки останавливается раньше нижнего края — исправить
и проверить, где ещё на сайте так же. Правки — tools/site/scan_line.py.

Пакет собирается от сайта после выкладки «Дезинфекция автотранспорта» (23.11.2026, ?v=20261118klient у style.css).
Что меняется на рабочем сайте (остальное — байт в байт):
  * style.css — правило .panel-scan (слой во всю высоту блока, полоса 120 px у его нижнего края) и @keyframes scan
    (от translateY(calc(-100% - 40px)) до translateY(130px));
  * главная — те же два правила во встроенных стилях (ссылки на style.css у неё нет);
  * остальные страницы со ссылкой на style.css (все из sitemap.xml, политика, согласие, 404.html) —
    ?v=20261118klient → ?v=20261123scan у style.css (app.min.js и legal.css — прежние версии), чтобы браузеры
    не брали старый style.css из кэша (на сайте он кэшируется на год).
Счётчики — по закону владельца (tracking_laws) до и после: Метрика, UIS и Radist не меняются, каждый ровно один раз;
закон независимости — до и после. Для каждого файла обратная замена даёт исходник байт в байт.

В папке пакета: backup/ (файлы сайта) и pkg/ (результат), MANIFEST.txt, deploy_payload.json, publish_scan.py,
run_once.sh (разовый запуск в SSH-консоли панели Timeweb).
"""

import concurrent.futures
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
import scan_line  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'scan-2026-11-23'
LEGAL = ('privacy/', 'soglasie/')
STATIC = ['style.css']
EXTRA = ['404.html']


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


def allowed_pairs():
    """Пары замен, разрешённые серверным скриптом (ALLOWED_PAIRS в publish_scan.py)."""
    src = (ROOT / 'tools/deploy/publish_scan.py').read_text(encoding='utf-8')
    block = src[src.index('ALLOWED_PAIRS = {'):src.index('}', src.index('ALLOWED_PAIRS = {'))]
    return set(re.findall(r"'([0-9a-f]{64})'", block))


def edits_for(rel, text):
    if rel == 'style.css':
        return scan_line.style_edits(text)
    return scan_line.page_edits(text, rel)


def check_file(rel, old, new):
    """Законы владельца до и после; обратная замена — исходник байт в байт (проверяется отдельно)."""
    if rel.endswith('.php') or rel == '404.html':
        counters = rel == '404.html' or rel[:-len('index.php')] not in LEGAL
        for label, s in (('исходная страница', old), ('результат', new)):
            bad = tracking_laws.check_page(s, counters=counters)
            assert not bad, '%s, %s: %s' % (rel, label, bad)
        hb, ha = independence_law.violations(old), independence_law.violations(new)
        assert hb == ha == [], '%s: закон независимости: %s' % (rel, ha or hb)
        # счётчики и контакты — тот же текст до и после
        for pat in (r'<!-- Yandex\.Metrika counter -->.*?<!-- /Yandex\.Metrika counter -->', r'<!-- UIS -->.*?</head>',
                    r'<!-- Radist -->.*?<!-- /Radist -->', r'<a [^>]*href="tel:[^"]*"[^>]*>.*?</a>',
                    r'<a [^>]*href="mailto:[^"]*"[^>]*>.*?</a>'):
            a, b = re.findall(pat, old, re.S), re.findall(pat, new, re.S)
            assert a == b, '%s: изменились счётчики или контакты (%s)' % (rel, pat[:30])
    elif rel == 'style.css':
        assert new.count('{') - new.count('}') == old.count('{') - old.count('}') == 0, 'style.css: скобки'
        assert new.count('@keyframes scan{') == 1 and new.count(scan_line.RULE_NEW) == 1 and \
            new.count(scan_line.KF_NEW) == 1, 'style.css: правила линии'


def build(files):
    """files: {rel: bytes с сайта} → строки пакета и результаты."""
    allowed = allowed_pairs()
    rows, results = [], {}
    order = STATIC + sorted(r for r in files if r not in STATIC)
    order = order[:1] + ['index.php'] + [r for r in order[1:] if r != 'index.php']
    for rel in order:
        body = files[rel]
        old = body.decode('utf-8')
        assert '<?php' not in old and '<?=' not in old, rel + ': PHP в файле'
        edits = edits_for(rel, old)
        for a, b, c in edits:
            h = hashlib.sha256((a + '\x00' + b).encode('utf-8')).hexdigest()
            assert h in allowed, '%s: пара замен не разрешена серверным скриптом: %s' % (rel, a[:60])
        new = scan_line.apply(old, edits)
        assert scan_line.revert(new, edits) == old, rel + ': обратная замена не даёт исходник'
        check_file(rel, old, new)
        result = new.encode('utf-8')
        rows.append({'file': rel, 'before': sha(body), 'after': sha(result), 'replace': edits})
        results[rel] = result
    return rows, results


def write_package(out, files, rows, results):
    for rel, body in files.items():
        for folder, content in (('backup', body), ('pkg', results[rel])):
            f = out / folder / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(content)
    payload = {'name': NAME, 'old_version': scan_line.OLD_V, 'new_version': scan_line.NEW_V, 'count': len(rows),
               'pages': len(rows) - 1, 'files': rows}
    (out / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    (out / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows),
                                      encoding='utf-8')
    shutil.copy2(str(ROOT / 'tools/deploy/publish_scan.py'), str(out / 'publish_scan.py'))
    run_once = """#!/bin/sh
# Разовая выкладка пакета %(name)s (SSH-консоль панели Timeweb).
# Повторный запуск ничего не делает: метка run_once.done создаётся до выкладки.
cd "$(dirname "$0")" || exit 1
[ -e run_once.done ] && exit 0
date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z' > run_once.done
{
  echo "start: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
  printf '%%s  %%s\\n%%s  %%s\\n' \\
    %(sp)s publish_scan.py \\
    %(sd)s deploy_payload.json | sha256sum -c - &&
  python3 --version &&
  python3 publish_scan.py --check &&
  python3 publish_scan.py --publish &&
  python3 publish_scan.py --check
  echo "exit: $?"
  echo "end: $(date '+%%Y-%%m-%%d %%H:%%M:%%S %%Z')"
} > run_once.log 2>&1
""" % {'name': NAME, 'sp': sha((out / 'publish_scan.py').read_bytes()), 'sd': sha((out / 'deploy_payload.json').read_bytes())}
    (out / 'run_once.sh').write_text(run_once, encoding='utf-8')
    (out / 'run_once.sh').chmod(0o755)


def snapshot():
    live = module('check_live', 'tools/qa/check_live.py')
    sm = live.get(live.SITE + 'sitemap.xml', tries=8)
    assert sm[0] == 200, 'sitemap.xml: HTTP %s' % sm[0]
    paths = sorted(set(urlpath for urlpath in (u[len(live.SITE):] for u in re.findall(r'<loc>([^<]+)</loc>', sm[1].decode('utf-8')))) | set(LEGAL))
    rels = STATIC + [p + 'index.php' for p in paths] + EXTRA

    def job(rel):
        url = live.SITE + (rel[:-len('index.php')] if rel.endswith('index.php') else rel)
        st, body = live.get(url, tries=8)  # Timeweb из облака иногда отвечает ложным 502
        assert st == 200, '%s: HTTP %s' % (rel, st)
        return rel, body
    with concurrent.futures.ThreadPoolExecutor(4) as ex:
        return dict(ex.map(job, rels))


def main(argv):
    if len(argv) not in (1, 2) or (len(argv) == 2 and argv[1] != '--check'):
        sys.exit(__doc__)
    out = pathlib.Path(argv[0]).resolve()
    if len(argv) == 2:  # пересобрать из backup и сверить с pkg и deploy_payload.json
        files = {p.relative_to(out / 'backup').as_posix(): p.read_bytes() for p in sorted((out / 'backup').rglob('*')) if p.is_file()}
        rows, results = build(files)
        payload = json.loads((out / 'deploy_payload.json').read_text(encoding='utf-8'))
        assert payload['files'] == rows, 'deploy_payload.json не совпадает с пересборкой'
        for rel, b in results.items():
            assert (out / 'pkg' / rel).read_bytes() == b, 'pkg/' + rel + ' не совпадает с пересборкой'
        print('CHECK OK: %d файлов пересобраны из backup байт в байт' % len(rows))
        return
    assert not out.exists(), 'используйте новую папку: прежние копии не перезаписываются'
    files = snapshot()
    rows, results = build(files)
    write_package(out, files, rows, results)
    grow = sum(len(results[r]) - len(files[r]) for r in files)
    print('Готово: %d файлов (style.css, %d страниц, из них главная — встроенные стили); прирост %+d байт; счётчики и'
          ' контакты — без нарушений, независимость — без нарушений. Пакет: %s' % (len(rows), len(rows) - 1, grow, out))


if __name__ == '__main__':
    main(sys.argv[1:])
