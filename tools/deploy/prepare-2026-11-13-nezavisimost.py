#!/usr/bin/env python3
"""Без мессенджеров и адреса склада + новые title и description: пакет для Timeweb из рабочего сайта (13.11.2026).

    python3 tools/deploy/prepare-2026-11-13-nezavisimost.py <новая папка пакета>

Решения владельца 13.11.2026: «Убери строку «Адрес склада» из подвала», «Нужно убрать полностью иконки мессенджеров
с сайта», «Утверждаю новые заголовки и описания» (документ проекта seo-agent/drafts/2026-11-13-title-description.md).
Всё снимается с пестконтроль-центр.рф по HTTPS (в GitHub есть ещё не опубликованные правки других задач) и правится
точечно, остальное остаётся байт в байт:
  * все страницы — tools/site/no_messengers.py: без блоков .msg (шапка, контакты перед формой, подвал) и плавающих
    кнопок .fab, без строки «Адрес склада» в подвале, тексты «напишите в мессенджер» → «напишите на почту»;
  * 20 страниц — tools/site/meta_titles.py: новые title и description (главная не входит);
  * search-index.json (поиск по сайту) — те же title и тексты точными заменами;
  * sitemap.xml — lastmod 2026-11-13 у 20 страниц с новыми title и description.
Счётчики Метрики, UIS и Radist, телефон и почта не меняются: закон tools/site/tracking_laws.py до и после, все
<script> страниц, кроме разметки JSON-LD, — байт в байт; в JSON-LD меняются только строки title и description и тексты
FAQ. Закон независимости (tools/site/independence_law.py): после правки нарушений нет, ссылок Telegram и MAX нет.

В папке пакета: backup/ и pkg/ (копии до и после), MANIFEST.txt, checks.json и deploy_payload.json для
publish_nezavisimost.py — серверный скрипт сам применяет те же замены к файлам public_html и сверяет SHA-256.
"""
import collections
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
import independence_law  # noqa: E402
import meta_titles  # noqa: E402
import no_messengers  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'nezavisimost-2026-11-13'
TODAY = '2026-11-13'
SCRIPT = re.compile(r'<script\b[^>]*>.*?</script>', re.S)
LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


def apply(s, rules):
    for old, new, count in rules:
        assert s.count(old) == count, 'найдено %d вместо %d: %s' % (s.count(old), count, old[:80])
        s = s.replace(old, new)
    return s


def page_rules(path, old):
    """Точные замены, которые дают no_messengers.patch + meta_titles.patch."""
    rules = []
    blocks = collections.Counter(m.group(0) for rx in (no_messengers.MSG, no_messengers.FAB) for m in rx.finditer(old))
    for block, n in sorted(blocks.items(), key=lambda kv: old.index(kv[0])):
        no_messengers._drop_block(re.match(r'.*', block, re.S))  # проверка: внутри только ссылки Telegram и MAX
        rules.append([block, '', n])
    for m in sorted(set(no_messengers.ADDR.findall(old))):
        rules.append([m, '', old.count(m)])
    for a, b in no_messengers.TEXTS:
        if a in old:
            rules.append([a, b, old.count(a)])
    for a, b in meta_titles.META.get(path, {}).values():
        assert a in old, '%s: нет прежней строки %s' % (path, a[:60])
        rules.append([a, b, old.count(a)])
    return rules


def ld_strings(s):
    out = []

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str):
            out.append(x)
    for m in LD.finditer(s):
        walk(json.loads(m.group(1)))
    return out


def build_page(path, original):
    old = original.decode('utf-8')
    assert '<?php' not in old and '<?=' not in old, path + ': PHP в HTML'
    counters = path not in ('privacy/', 'soglasie/')
    bad = tracking_laws.check_page(old, counters=counters)
    assert not bad, '%s: исходная страница: %s' % (path, bad)
    rules = page_rules(path, old)
    new = apply(old, rules)
    assert new == meta_titles.patch(path, no_messengers.patch(old)), path + ': замены не совпадают с правкой модулей'
    if path in meta_titles.META:
        assert meta_titles.left(path, new) == [], '%s: title/description: %s' % (path, meta_titles.left(path, new))
    assert no_messengers.left(new) == [], '%s: осталось %s' % (path, no_messengers.left(new))
    bad = tracking_laws.check_page(new, counters=counters)
    assert not bad, '%s: результат: %s' % (path, bad)
    hard = independence_law.violations(new)
    assert not hard, '%s: закон независимости: %s' % (path, hard)
    # скрипты (счётчики, Radist, приложение) — байт в байт; меняется только разметка JSON-LD
    olds = [m.group(0) for m in SCRIPT.finditer(old) if 'application/ld+json' not in m.group(0)[:60]]
    news = [m.group(0) for m in SCRIPT.finditer(new) if 'application/ld+json' not in m.group(0)[:60]]
    assert olds == news, path + ': изменён <script> вне разметки'
    for k in ('href="tel:', 'href="mailto:', '<form', '</form>', '<h1', '<section'):
        assert old.count(k) == new.count(k), '%s: изменилось число %s' % (path, k)
    # в JSON-LD — только согласованные строки
    repl = {a: b for a, b, _ in rules if b}
    lo, ln = ld_strings(old), ld_strings(new)
    assert len(lo) == len(ln), path + ': изменилась структура JSON-LD'
    for a, b in zip(lo, ln):
        if a != b:
            assert any(x in a for x in repl) and apply_all(a, repl) == b, '%s: JSON-LD: %s' % (path, a[:80])
    return new, rules


def apply_all(s, repl):
    for a, b in repl.items():
        s = s.replace(a, b)
    return s


def build_search(original):
    s = original.decode('utf-8')
    json.loads(s)
    pairs = [v for meta in meta_titles.META.values() for v in meta.values()] + list(no_messengers.TEXTS)
    rules = [[a, b, s.count(a)] for a, b in pairs if a in s]
    new = apply(s, rules)
    json.loads(new)
    assert not independence_law.violations(new)
    return new, rules


def build_sitemap(original, site):
    s = original.decode('utf-8')
    rules = []
    for path in sorted(meta_titles.META):
        m = re.search(r'(<loc>' + re.escape(site + path) + r'</loc>\s*<lastmod>)([^<]*)(</lastmod>)', s)
        assert m, 'sitemap.xml: нет ' + path
        if m.group(2) != TODAY:
            rules.append([m.group(0), m.group(1) + TODAY + m.group(3), 1])
    new = apply(s, rules)
    ET.fromstring(new.encode('utf-8'))
    return new, rules


live = module('check_live', 'tools/qa/check_live.py')
SITE = live.SITE
OUT = pathlib.Path(sys.argv[1]).resolve()
assert not OUT.exists(), 'используйте новую папку: прежние копии не перезаписываются'
OUT.mkdir(parents=True)

status, sitemap = live.get(SITE + 'sitemap.xml', tries=8)
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
assert set(meta_titles.META) <= set(paths), 'страниц с новыми title нет на сайте: %s' % (set(meta_titles.META) - set(paths))


def prepare(item):
    rel = item
    if rel.endswith('index.php'):
        url = SITE + rel[:-len('index.php')]
    else:
        url = SITE + rel
    status, original = live.get(url, tries=8)  # Timeweb из облака иногда отвечает ложным 502 несколько раз подряд
    assert status == 200, '%s: HTTP %s' % (url, status)
    if rel == 'search-index.json':
        new, rules = build_search(original)
    elif rel == 'sitemap.xml':
        assert original == sitemap, 'sitemap.xml изменился во время подготовки'
        new, rules = build_sitemap(original, SITE)
    else:
        new, rules = build_page(rel[:-len('index.php')], original)
    result = new.encode('utf-8')
    for folder, content in (('backup', original), ('pkg', result)):
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    return {'file': rel, 'before': sha(original), 'after': sha(result), 'replace': rules, 'append': ''}


items = ['search-index.json', 'sitemap.xml'] + [p + 'index.php' for p in paths]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:  # Timeweb из облака иногда отвечает 502 — бережно
    rows = list(pool.map(prepare, items))
unchanged = [r['file'] for r in rows if r['before'] == r['after']]
assert not unchanged, 'файлы без изменений: %s' % unchanged
payload = {'name': NAME, 'count': len(rows), 'files': rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows),
                                  encoding='utf-8')
(OUT / 'checks.json').write_text(json.dumps([{k: r[k] for k in ('file', 'before', 'after')} for r in rows],
                                            ensure_ascii=False, indent=1), encoding='utf-8')
(OUT / 'sitemap-before.xml').write_bytes(sitemap)
shutil.copy2(str(ROOT / 'tools/deploy/publish_nezavisimost.py'), str(OUT / 'publish_nezavisimost.py'))
pages = [r for r in rows if r['file'].endswith('index.php')]
blocks = sum(c for r in pages for a, b, c in r['replace'] if b == '' and a.lstrip().startswith('<div'))
addr = sum(c for r in pages for a, b, c in r['replace'] if a.startswith('<p>Адрес склада'))
meta = sum(1 for r in pages for a, b, c in r['replace'] if any(a == x for m in meta_titles.META.values()
                                                              for x, _ in m.values()))
print('Готово: файлов %d (search-index.json, sitemap.xml и страниц %d); блоков мессенджеров убрано %d, строк адреса %d, '
      'замен title/description %d. Пакет: %s' % (len(rows), len(pages), blocks, addr, meta, OUT))
