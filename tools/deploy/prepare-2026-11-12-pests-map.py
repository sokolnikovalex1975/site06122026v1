#!/usr/bin/env python3
"""Фон блока «Вредители» — «Карта очагов» (вариант A, 12.11.2026): точечный пакет для Timeweb из актуального сайта.

    python3 tools/deploy/prepare-2026-11-12-pests-map.py <новая папка>     # снять сайт по HTTPS и собрать пакет
    python3 tools/deploy/prepare-2026-11-12-pests-map.py <папка> --check   # пересобрать из <папка>/backup и сверить

Решение владельца 12.11.2026: «Делай вариант А. И выкладывай всё сразу на таймвеб».

Что меняется на рабочем сайте (остальное — байт в байт):
  * img/pests-map.svg — новый файл, плитка изолиний 1200×1200 (tools/pests-map/gen_pests_map.py), байт в байт из GitHub;
  * style.css — в конец дописывается блок «Фон блока „Вредители“» из style.css репозитория (байт в байт);
  * главная (стили встроены) — тот же блок, сжатый esbuild, отдельным <style id="pests-map-st"> перед <!-- UIS -->;
  * все страницы — версия стилей и скриптов ?v=20261111btn → ?v=20261112fon (у style.css кэш на год, иначе
    вернувшиеся посетители видели бы старый фон).
В GitHub есть ещё не опубликованные правки (схема объекта, фото с людьми, защита от проникновения, «Наши клиенты») —
их пакет не переносит: правится то, что сейчас отдаёт сайт. Счётчики — по закону владельца (tracking_laws) до и после.
"""
import concurrent.futures
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import tracking_laws  # noqa: E402

NAME = 'pests-map-2026-11-12'
OLD_V, NEW_V = '20261111btn', '20261112fon'
MARK = '/* ===== Фон блока «Вредители»: «Карта очагов» (12.11.2026) ====='
STYLE_ID = 'pests-map-st'
SVG = 'img/pests-map.svg'
LEGAL = ('privacy/', 'soglasie/')
PESTS = {'', 'deratizatsiya/', 'pishchevoe-proizvodstvo/', 'restorany-i-kafe/', 'magaziny-i-torgovye-seti/', 'gostinitsy/',
         'farmatsevticheskie-proizvodstva/', 'sklady-i-logistika/', 'biznes-tsentry-torgovye-tsentry-predpriyatiya/'}


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


def block():
    css = (ROOT / 'style.css').read_text(encoding='utf-8')
    i = css.index(MARK)
    assert css[i - 1] == '\n' and css[i - 2] == '\n', 'блок отделён пустой строкой'
    return '\n' + css[i:]


def minified(b):
    out = subprocess.run(['npx', '--yes', 'esbuild@0.24.2', '--minify', '--loader=css', '--charset=utf8', '--log-level=warning'],
                         input=b, capture_output=True, text=True, cwd=ROOT, check=True).stdout.strip()
    assert out.startswith('.pests-bg{background:url(img/pests-map.svg) 0 0/1200px 1200px repeat,') and '.pests-s:after{' in out
    return out


def main():
    out_dir = pathlib.Path(sys.argv[1]).resolve()
    check = '--check' in sys.argv[2:]
    live = module('check_live', 'tools/qa/check_live.py')
    site = live.SITE
    if check:
        assert (out_dir / 'backup').is_dir()
    else:
        assert not out_dir.exists(), 'используйте новую папку: прежние копии не перезаписываются'
        (out_dir / 'backup').mkdir(parents=True)

    def fetch(rel_url, rel_file):
        f = out_dir / 'backup' / rel_file
        if check:
            return f.read_bytes()
        status, body = live.get(site + rel_url)
        assert status == 200, rel_url + ': HTTP ' + str(status)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(body)
        return body

    # страницы — как в sitemap.xml рабочего сайта + политика и согласие
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
    assert 'zashchita-ot-proniknoveniya-gryzunov/' not in paths, 'страница защиты от проникновения — только в превью'

    blk = block()
    mini = '<style id="' + STYLE_ID + '">' + minified(blk) + '</style>'
    parts = tracking_laws.counter_parts()
    rows, report = [], []

    def page(path):
        original = fetch(path, path + 'index.php')
        text = original.decode('utf-8')
        assert '<?php' not in text and '<?=' not in text, path + ': PHP в HTML'
        counters = path not in LEGAL
        bad = tracking_laws.check_page(text, counters=counters, parts=parts)
        assert not bad, path + ': живая страница нарушает закон о счётчиках: ' + str(bad[:3])
        assert NEW_V not in text and STYLE_ID not in text and 'pests-map.svg' not in text, path + ': правка уже на сайте'
        assert ('pests-bg' in text) == (path in PESTS), path + ': блок вредителей не там, где ожидался'
        refs = re.findall(r'[^"\' ]*\?v=' + OLD_V, text)
        assert refs and all(r.endswith(('style.css?v=' + OLD_V, 'app.min.js?v=' + OLD_V)) for r in refs), path + ': ' + str(refs)
        replace = [['?v=' + OLD_V, '?v=' + NEW_V, len(refs)]]
        result = text.replace('?v=' + OLD_V, '?v=' + NEW_V)
        if path == '':
            assert 'style.css' not in text and text.count('texture.webp') == 1, 'главная: стили встроены'
            anchor = '</style>\n<!-- UIS -->'
            assert text.count(anchor) == 1 and text.index(anchor) < text.index('</head>')
            replace.append([anchor, '</style>' + mini + '\n<!-- UIS -->', 1])
            result = result.replace(anchor, '</style>' + mini + '\n<!-- UIS -->', 1)
        bad = tracking_laws.check_page(result, counters=counters, parts=parts)
        assert not bad, path + ': правка нарушает закон о счётчиках: ' + str(bad[:3])
        for k, p in parts.items():
            if counters:
                assert text.count(p) == result.count(p) == 1, path + ': часть счётчиков ' + k
            else:
                assert text.count(p) == result.count(p) == 0, path + ': счётчики на юридической странице'
        back = result.replace(mini, '').replace('?v=' + NEW_V, '?v=' + OLD_V)
        assert back == text, path + ': изменения вне согласованных мест'
        res = result.encode('utf-8')
        f = out_dir / 'pkg' / (path + 'index.php')
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(res)
        return {'file': path + 'index.php', 'before': sha(original), 'after': sha(res), 'replace': replace}

    css_old = fetch('style.css', 'style.css')
    css = css_old.decode('utf-8')
    assert MARK not in css and 'pests-map.svg' not in css, 'на сайте блок уже есть'
    assert css.endswith('}\n') and '.pests-bg{position:absolute;inset:-12% 0;background:url(img/texture.webp) center/cover;' in css
    css_new = (css + blk).encode('utf-8')
    (out_dir / 'pkg').mkdir(parents=True, exist_ok=True)
    (out_dir / 'pkg/style.css').write_bytes(css_new)
    svg = (ROOT / SVG).read_bytes()
    assert svg.startswith(b"<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='1200'") and svg.endswith(b'</svg>')
    ET.fromstring(svg)
    (out_dir / 'pkg/img').mkdir(parents=True, exist_ok=True)
    (out_dir / 'pkg' / SVG).write_bytes(svg)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        pages = sorted(pool.map(page, paths), key=lambda r: r['file'])

    # порядок выкладки: рисунок, стили, затем страницы
    rows = [{'file': SVG, 'before': None, 'after': sha(svg), 'create': svg.decode('utf-8')},
            {'file': 'style.css', 'before': sha(css_old), 'after': sha(css_new), 'append': blk}] + pages
    payload = {'name': NAME, 'old_version': OLD_V, 'new_version': NEW_V, 'pages': len(pages), 'files': rows}
    data = json.dumps(payload, ensure_ascii=False, indent=1).encode('utf-8') + b'\n'
    manifest = ''.join('%s  %s  %s\n' % (r['before'] or '-' * 64, r['after'], r['file']) for r in rows)
    if check:
        assert (out_dir / 'deploy_payload.json').read_bytes() == data, 'пакет не совпадает'
        assert (out_dir / 'MANIFEST.txt').read_text(encoding='utf-8') == manifest
        print('пакет совпадает: %d файлов' % len(rows))
        return
    (out_dir / 'deploy_payload.json').write_bytes(data)
    (out_dir / 'MANIFEST.txt').write_text(manifest, encoding='utf-8')
    print('Готово: %d файлов (рисунок, style.css и %d страниц; блок вредителей на %d). Пакет: %s'
          % (len(rows), len(pages), sum(1 for r in pages if r['file'][:-len('index.php')] in PESTS), out_dir))


if __name__ == '__main__':
    main()
