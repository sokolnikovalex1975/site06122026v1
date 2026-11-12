#!/usr/bin/env python3
"""Точечный пакет «Цена» и «Вопросы» → блоки этой же страницы, из актуального рабочего сайта (12.11.2026).

    python3 tools/deploy/prepare-2026-11-12-menu-anchors.py <новая папка пакета>

Страницы снимаются с пестконтроль-центр.рф по HTTPS (а не берутся из GitHub: там есть ещё не опубликованные
фотографии и страница инженерной защиты). К каждой применяется tools/site/menu_anchors.patch — меняются только адреса
ссылок «Цена» (шапка, мобильное меню, подвал) и «Вопросы» (подвал). Для каждой страницы проверяется: обратная замена
даёт исходный файл байт в байт, кроме этих ссылок ничего не изменилось, закон о счётчиках и контактах выполнен до и после.

В папке пакета: backup/ и pkg/ (копии до и после), MANIFEST.txt, checks.json и deploy_payload.json для
publish_menu_anchors.py — серверный скрипт сам применяет те же замены к файлам public_html и сверяет SHA-256.
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
import tracking_laws  # noqa: E402
import menu_anchors   # noqa: E402


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


live = module('check_live', 'tools/qa/check_live.py')
SITE = live.SITE
OUT = pathlib.Path(sys.argv[1]).resolve()
assert not OUT.exists(), 'используйте новую папку: прежние копии не перезаписываются'
OUT.mkdir(parents=True)
LINK = re.compile(r'<a href="[^"]*">(Цена|Вопросы)</a>')


def sha(b):
    return hashlib.sha256(b).hexdigest()


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
paths = sorted(set(paths) | {'privacy/', 'soglasie/'})
assert 30 <= len(paths) <= 60, 'неожиданное число страниц: %d' % len(paths)


def prepare(path):
    status, original = live.get(SITE + path)
    assert status == 200, '%s: HTTP %s' % (path, status)
    old = original.decode('utf-8')
    assert '<?php' not in old and '<?=' not in old, path + ': PHP в HTML'
    counters = path not in ('privacy/', 'soglasie/')
    bad = tracking_laws.check_page(old, counters=counters)
    assert not bad, '%s: исходная страница: %s' % (path, bad)
    new, changes = menu_anchors.patch(old, path)
    assert menu_anchors.patch(new, path)[1] == [], path + ': неидемпотентно'
    bad = tracking_laws.check_page(new, counters=counters)
    assert not bad, '%s: результат: %s' % (path, bad)
    for o, n, c in changes:
        assert new.count(o) == 0 and new.count(n) == old.count(n) + c, path + ': неожиданное число ссылок ' + n
    ph = lambda s: LINK.sub(lambda m: '<a href="X">%s</a>' % m.group(1), s)
    assert ph(old) == ph(new), path + ': изменено что-то кроме ссылок «Цена» и «Вопросы»'
    # по порядку: каждая ссылка либо прежняя, либо ровно одна из замен пакета
    rules = {(o, n) for o, n, _ in changes}
    seq = lambda s: [m.group(0) for m in LINK.finditer(s)]
    for a, b in zip(seq(old), seq(new)):
        assert a == b or (a, b) in rules, '%s: %s → %s' % (path, a, b)
    ids = set(re.findall(r'\bid="([^"]+)"', new))
    for href in re.findall(r'<a href="#([^"]+)">(?:Цена|Вопросы)</a>', new):
        assert href in ids, '%s: нет якоря #%s' % (path, href)
    result = new.encode('utf-8')
    rel = path + 'index.php'
    if changes:
        for folder, content in (('backup', original), ('pkg', result)):
            f = OUT / folder / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(content)
    return {'file': rel, 'before': sha(original), 'after': sha(result),
            'replace': [[o, n, c] for o, n, c in changes]}


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    rows = sorted(pool.map(prepare, paths), key=lambda x: x['file'])
same = [r['file'] for r in rows if not r['replace']]
files = [r for r in rows if r['replace']]
payload = {'name': 'menu-anchors-2026-11-12', 'pages_checked': len(rows), 'unchanged': same, 'files': files}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(
    ''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in files), encoding='utf-8')
(OUT / 'checks.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
(OUT / 'sitemap-before.xml').write_bytes(sitemap)
shutil.copy2(str(ROOT / 'tools/deploy/publish_menu_anchors.py'), str(OUT / 'publish_menu_anchors.py'))
links = sum(c for r in files for _, _, c in r['replace'])
print('Готово: проверено %d страниц рабочего сайта, меняются %d (ссылок %d), без изменений: %s. Пакет: %s'
      % (len(rows), len(files), links, ', '.join(same) or '—', OUT))
