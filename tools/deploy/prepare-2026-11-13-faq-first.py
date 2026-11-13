#!/usr/bin/env python3
"""Вопросы внизу страницы — развёрнут только первый: пакет для Timeweb из актуального рабочего сайта (13.11.2026).

    python3 tools/deploy/prepare-2026-11-13-faq-first.py <новая папка пакета>

Запрос владельца 13.11.2026: «должен быть развёрнут только первый вопрос; все остальные должны быть свёрнуты».
Страницы снимаются с пестконтроль-центр.рф по HTTPS (в GitHub есть ещё не опубликованные правки других задач) и правятся
точечно tools/site/faq_first.py: у вопросов 2…N убираются класс open и aria-expanded="true" → "false". Остальное — байт
в байт. Берутся все страницы из sitemap.xml сайта; в пакет попадают только те, где при загрузке открыт не только первый
вопрос (13.11.2026 — 7 страниц).
Проверки для каждой страницы: замены — только карточки вопросов вида
<div class="card qa open"><button aria-expanded="true" aria-controls="aN" id="qN">, каждая ровно один раз;
обратная замена даёт исходник байт в байт; закон о счётчиках и контактах (tracking_laws.check_page) и закон
независимости (independence_law.violations) — до и после; faq_first.extra_open() результата пуст.

В папке пакета: backup/ и pkg/ (копии до и после), MANIFEST.txt и deploy_payload.json для publish_faq_first.py —
серверный скрипт сам применяет те же замены к файлам public_html и сверяет SHA-256 до и после.
"""
import concurrent.futures
import hashlib
import importlib.util
import json
import pathlib
import re
import shutil
import sys
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import faq_first  # noqa: E402
import independence_law  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'faq-first-2026-11-13'
OLD_RE = re.compile(r'<div class="card qa open"><button aria-expanded="true" aria-controls="a(\d+)" id="q(\d+)">')


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


live = module('check_live', 'tools/qa/check_live.py')
SITE = live.SITE
OUT = pathlib.Path(sys.argv[1]).resolve()
assert not OUT.exists(), 'используйте новую папку: прежние копии не перезаписываются'


def rules_for(old):
    """Точные замены карточек вопросов 2…N: [прежний фрагмент, новый фрагмент, 1]."""
    rules = []
    for n, m in enumerate(faq_first.items(old), 1):
        if n == 1:
            continue
        end = old.index('>', m.end()) + 1
        a = old[m.start():end]
        mm = OLD_RE.fullmatch(a)
        assert mm and mm.group(1) == mm.group(2) == str(n), 'неожиданная карточка вопроса %d: %s' % (n, a[:120])
        b = '<div class="card qa"><button aria-expanded="false" aria-controls="a%d" id="q%d">' % (n, n)
        assert old.count(a) == 1
        rules.append([a, b, 1])
    return rules


def build_page(path, original):
    old = original.decode('utf-8')
    assert '<?php' not in old and '<?=' not in old, path + ': PHP в HTML'
    bad = tracking_laws.check_page(old, counters=True)
    assert not bad, '%s: исходная страница: %s' % (path, bad)
    rules = rules_for(old)
    new = old
    for a, b, c in rules:
        assert new.count(a) == c
        new = new.replace(a, b)
    assert new == faq_first.patch(old), path + ': результат не совпадает с tools/site/faq_first.py'
    assert not faq_first.extra_open(new), path + ': остались открытые вопросы'
    bad = tracking_laws.check_page(new, counters=True)
    assert not bad, '%s: результат: %s' % (path, bad)
    assert not independence_law.violations(new), path + ': закон независимости'
    back = new
    for a, b, c in reversed(rules):
        assert back.count(b) == c
        back = back.replace(b, a)
    assert back == old, path + ': отличия вне карточек вопросов'
    return new, rules


status, sitemap = live.get(SITE + 'sitemap.xml')
assert status == 200, 'sitemap.xml: HTTP %s' % status
paths = []
for node in ET.fromstring(sitemap).iter():
    if node.tag.endswith('}loc') or node.tag == 'loc':
        url = node.text.strip()
        assert url.startswith(SITE), url
        path = urllib.parse.urlsplit(url).path.lstrip('/')
        if path.endswith('/') or path == '':
            paths.append(path)
paths = sorted(set(paths))
assert 30 <= len(paths) <= 60, 'неожиданное число страниц: %d' % len(paths)


def fetch(path):
    status, body = live.get(SITE + path, tries=8)  # Timeweb из облака иногда отвечает ложным 502 несколько раз подряд
    assert status == 200, '%s: HTTP %s' % (path, status)
    return path, body


with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:  # бережно к Timeweb
    pages = list(pool.map(fetch, paths))

OUT.mkdir(parents=True)
rows, clean = [], []
for path, original in pages:
    if not faq_first.extra_open(original.decode('utf-8')):
        clean.append(path)
        continue
    new, rules = build_page(path, original)
    rel = path + 'index.php'
    result = new.encode('utf-8')
    for folder, content in (('backup', original), ('pkg', result)):
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    rows.append({'file': rel, 'before': sha(original), 'after': sha(result), 'replace': rules})
rows.sort(key=lambda r: r['file'])
payload = {'name': NAME, 'count': len(rows), 'files': rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows),
                                  encoding='utf-8')
(OUT / 'sitemap-before.xml').write_bytes(sitemap)
shutil.copy2(str(ROOT / 'tools/deploy/publish_faq_first.py'), str(OUT / 'publish_faq_first.py'))
print('Готово: страниц в пакете %d, свёрнуто вопросов %d; без правки (уже только первый открыт или вопросов нет) %d из %d.'
      % (len(rows), sum(len(r['replace']) for r in rows), len(clean), len(paths)))
for r in rows:
    print('  %-70s вопросов свёрнуто: %d' % (r['file'], len(r['replace'])))
print('Пакет:', OUT)
