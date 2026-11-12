#!/usr/bin/env python3
"""Схема объекта на главной + зелёная метка «Вы здесь»: точечный пакет для Timeweb из актуального сайта (13.11.2026).

    python3 tools/deploy/prepare-2026-11-13-shema-here.py <новая папка>          # снять сайт по HTTPS и собрать пакет
    python3 tools/deploy/prepare-2026-11-13-shema-here.py <папка> --check        # пересобрать из <папка>/backup и сверить
    python3 tools/deploy/prepare-2026-11-13-shema-here.py <папка> --rebuild      # собрать пакет из <папка>/backup

Команда владельца 13.11.2026: «это делай! … На Timeweb выкладывай» — зелёная «Вы здесь» на всех страницах и
блок «Схема объекта» с меткой на главной.

Что меняется на рабочем сайте (остальное — байт в байт):
  * все страницы — два CSS-правила: .pr-here (общий прайс) и .vu-here (каталог «Все услуги») → зелёная метка
    (tools/site/here_green.RULES), только там, где правило есть;
  * главная index.php:
      - плитка «Пест-контроль по системе IPM»: вместо ссылки на #podhod со стрелкой — текущая страница
        (<div … aria-current="page">) с меткой «Вы здесь», как в GitHub (price_block.py);
      - блок <!-- home-scheme:start --> … <!-- home-scheme:end --> из index.html репозитория — перед «Документами»;
      - <style id="hz-st"> — перед <!-- UIS --> (UIS остаётся последним в <head>);
      - <script id="hz-js"> — перед <!-- Radist --> (Radist остаётся в конце <body>).
Остальные неопубликованные правки GitHub пакет не переносит. Счётчики — по закону владельца (tracking_laws) до и после.
"""
import concurrent.futures
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import tracking_laws  # noqa: E402
import here_green  # noqa: E402

NAME = 'shema-here-2026-11-13'
LEGAL = ('privacy/', 'soglasie/')
DOK = '<section class="s" id="dokumenty">'
UIS = '</style>\n<!-- UIS -->'
RAD = '<!-- Radist -->'
TILE_RE = re.compile(r'<(a|div) class="card pr-card pr-main"[^>]*><div class="pr-num">01 / Постоянная защита.*?<span class="pr-unit">[^<]*</span></div></\1>', re.S)


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


def repo_parts():
    r = (ROOT / 'index.html').read_text(encoding='utf-8')
    sec = re.search(r'<!-- home-scheme:start -->.*?<!-- home-scheme:end -->\n\n', r, re.S).group(0)
    st = re.search(r'<style id="hz-st">.*?</style>', r, re.S).group(0)
    js = re.search(r'<script id="hz-js">.*?</script>', r, re.S).group(0)
    tile = TILE_RE.search(r).group(0)
    assert tile.startswith('<div class="card pr-card pr-main" aria-current="page">') and '<span class="pr-here">Вы здесь</span>' in tile
    assert 'tel:' not in sec + st + js and 'mailto:' not in sec + st + js
    return sec, st, js, tile


def main():
    out_dir = pathlib.Path(sys.argv[1]).resolve()
    check = '--check' in sys.argv[2:]
    rebuild = '--rebuild' in sys.argv[2:]  # собрать пакет заново из уже снятой копии <папка>/backup
    live = module('check_live', 'tools/qa/check_live.py')
    site = live.SITE
    if check or rebuild:
        assert (out_dir / 'backup').is_dir()
    else:
        assert not out_dir.exists(), 'используйте новую папку: прежние копии не перезаписываются'
        (out_dir / 'backup').mkdir(parents=True)

    def fetch(rel_url, rel_file):
        f = out_dir / 'backup' / rel_file
        if check or rebuild:
            return f.read_bytes()
        for i in range(8):  # хостинг иногда отвечает 502 на серию запросов
            status, body = live.get(site + rel_url)
            if status == 200:
                break
            time.sleep(4 + 3 * i)
        assert status == 200, rel_url + ': HTTP ' + str(status)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(body)
        return body

    smap = fetch('sitemap.xml', 'sitemap.xml')
    paths = []
    for node in ET.fromstring(smap).iter():
        if node.tag.endswith('}loc') or node.tag == 'loc':
            url = node.text.strip()
            assert url.startswith(site), url
            p = urllib.parse.urlsplit(url).path.lstrip('/')
            if p.endswith('/') or p == '':
                paths.append(p)
    paths = sorted(set(paths) | set(LEGAL))
    assert 30 <= len(paths) <= 60, 'неожиданное число страниц: %d' % len(paths)

    sec, st, js, tile_new = repo_parts()
    parts = tracking_laws.counter_parts()

    def page(path):
        original = fetch(path, path + 'index.php')
        text = original.decode('utf-8')
        assert '<?php' not in text and '<?=' not in text, path + ': PHP в HTML'
        counters = path not in LEGAL
        bad = tracking_laws.check_page(text, counters=counters, parts=parts)
        assert not bad, path + ': живая страница нарушает закон о счётчиках: ' + str(bad[:3])
        assert 'id="hz-st"' not in text and '.pr-here::before' not in text and '.vu-here::before' not in text, path + ': правка уже на сайте'
        replace = []
        result = text
        for old, new in here_green.RULES:
            n = text.count(old)
            assert n in (0, 1), path + ': правило встречается %d раз' % n
            if n:
                replace.append([old, new, 1])
                result = result.replace(old, new)
        if path == '':
            m = TILE_RE.search(text)
            tile_old = m.group(0)
            assert tile_old.startswith('<a class="card pr-card pr-main" href="#podhod">')
            # содержимое плитки то же, кроме обёртки и стрелки → метки
            norm = lambda t: re.sub(r'<span class="pr-(go|here)".*?</span>(</span>)?', '', re.sub(r'^<(a|div)[^>]*>|</(a|div)>$', '', t), flags=re.S)
            assert norm(tile_old) == norm(tile_new), 'главная: плитка IPM на сайте отличается от GitHub'
            for a, b in [(tile_old, tile_new), (DOK, sec + DOK), (UIS, '</style>' + st + '\n<!-- UIS -->'), (RAD, js + '\n' + RAD)]:
                assert result.count(a) == 1, 'главная: якорь не единственный: ' + a[:60]
                replace.append([a, b, 1])
                result = result.replace(a, b)
            assert result.index('id="hz-st"') < result.index('</head>') < result.index('id="shema"') < result.index('id="hz-js"') < result.index(RAD)
        if not replace:
            return None
        bad = tracking_laws.check_page(result, counters=counters, parts=parts)
        assert not bad, path + ': правка нарушает закон о счётчиках: ' + str(bad[:3])
        for k, p in parts.items():
            assert text.count(p) == result.count(p) == (1 if counters else 0), path + ': часть счётчиков ' + k
        back = result
        for a, b, _ in reversed(replace):
            assert back.count(b) == 1
            back = back.replace(b, a)
        assert back == text, path + ': изменения вне согласованных мест'
        res = result.encode('utf-8')
        f = out_dir / 'pkg' / (path + 'index.php')
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(res)
        return {'file': path + 'index.php', 'before': sha(original), 'after': sha(res), 'replace': replace}

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        rows = sorted((r for r in pool.map(page, paths) if r), key=lambda r: (r['file'] != 'index.php', r['file']))
    assert rows[0]['file'] == 'index.php' and len(rows[0]['replace']) >= 5
    payload = {'name': NAME, 'pages': len(rows), 'files': rows}
    data = json.dumps(payload, ensure_ascii=False, indent=1).encode('utf-8') + b'\n'
    manifest = ''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows)
    if check:
        assert (out_dir / 'deploy_payload.json').read_bytes() == data, 'пакет не совпадает'
        assert (out_dir / 'MANIFEST.txt').read_text(encoding='utf-8') == manifest
        print('пакет совпадает: %d страниц' % len(rows))
        return
    (out_dir / 'deploy_payload.json').write_bytes(data)
    (out_dir / 'MANIFEST.txt').write_text(manifest, encoding='utf-8')
    print('Готово: %d страниц из %d (главная: схема, плитка, стили, скрипт). Пакет: %s' % (len(rows), len(paths), out_dir))


if __name__ == '__main__':
    main()
