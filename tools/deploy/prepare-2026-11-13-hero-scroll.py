#!/usr/bin/env python3
"""Первый экран главной без затемнения на телефоне (13.11.2026): точечный пакет для Timeweb из актуального сайта.

    python3 tools/deploy/prepare-2026-11-13-hero-scroll.py <новая папка>     # снять сайт по HTTPS и собрать пакет
    python3 tools/deploy/prepare-2026-11-13-hero-scroll.py <папка> --check   # пересобрать из <папка>/backup и сверить

Решение владельца 13.11.2026 (превью по скриншотам 12.11.2026): «Да, вноси правку и выкладывай на сайт, счётчики не трогай».

Что меняется на рабочем сайте (остальное — байт в байт):
  * app.min.js — «уход первого экрана при прокрутке» (затемнение текста и панели до 10 %, сдвиг вверх на 110 px,
    параллакс фото) обёрнут в gsap.matchMedia('(min-width: 1281px)'): до 1280 px первый экран не гаснет и не уезжает.
    Правится рабочий файл одной заменой, а не собирается из app.js репозитория: в GitHub есть ещё не опубликованные
    правки (схема объекта, фото с людьми, защита от проникновения, «Наши клиенты»);
  * style.css — в конец дописывается блок «Первый экран главной на телефоне» из style.css репозитория (байт в байт);
  * главная (стили встроены) — тот же блок, сжатый esbuild, отдельным <style id="hero-scroll-st"> перед <!-- UIS -->;
  * все страницы — версия стилей и скриптов ?v=20261112fon → ?v=20261113hero (у style.css и app.min.js кэш на год,
    иначе вернувшиеся посетители видели бы прежний первый экран).
Счётчики — по закону владельца (tracking_laws) до и после: Метрика, UIS и Radist не меняются.
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

NAME = 'hero-scroll-2026-11-13'
OLD_V, NEW_V = '20261112fon', '20261113hero'
MARK = '/* ===== Первый экран главной на телефоне: отступ до бегущей строки (13.11.2026) ====='
STYLE_ID = 'hero-scroll-st'
JS = 'app.min.js'
JS_OLD = ('gsap.timeline({scrollTrigger:{trigger:P,start:"top top",end:"bottom top",scrub:!0}})'
          '.to(F,{yPercent:14,scale:1.1,ease:"none"},0).to(".hero .wrap",{y:-110,opacity:.1,ease:"none"},0)')
JS_NEW = 'gsap.matchMedia().add("(min-width: 1281px)",function(){' + JS_OLD + '})'
HERO_CSS = '.hero{position:relative;min-height:max(100svh,760px);display:flex;align-items:center;overflow:hidden;padding:clamp(110px,10vw,180px) 0 clamp(80px,7vw,120px)}'
LEGAL = ('privacy/', 'soglasie/')


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
    assert out == '@media (max-width:760px){#hero.hero:not(.f-hero){padding-bottom:32px}}', out
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
        status, body = live.get(site + rel_url, tries=8)  # ложные 502 из облака — больше повторов
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

    def page(path):
        original = fetch(path, path + 'index.php')
        text = original.decode('utf-8')
        assert '<?php' not in text and '<?=' not in text, path + ': PHP в HTML'
        counters = path not in LEGAL
        bad = tracking_laws.check_page(text, counters=counters, parts=parts)
        assert not bad, path + ': живая страница нарушает закон о счётчиках: ' + str(bad[:3])
        assert NEW_V not in text and STYLE_ID not in text, path + ': правка уже на сайте'
        refs = re.findall(r'[^"\' ]*\?v=' + OLD_V, text)
        assert refs and all(r.endswith(('style.css?v=' + OLD_V, 'app.min.js?v=' + OLD_V)) for r in refs), path + ': ' + str(refs)
        replace = [['?v=' + OLD_V, '?v=' + NEW_V, len(refs)]]
        result = text.replace('?v=' + OLD_V, '?v=' + NEW_V)
        if path == '':
            assert 'style.css' not in text and text.count(HERO_CSS) == 1, 'главная: стили встроены, отступ героя прежний'
            assert text.count('id="heroMedia"') == 1 and text.count('id="panel"') == 1 and text.count('class="strip"') == 1
            anchor = '</style>\n<!-- UIS -->'
            assert text.count(anchor) == 1 and text.index(anchor) < text.index('</head>')
            assert text.index('id="pests-map-st"') < text.index(anchor), 'новый стиль — после «Карты очагов», перед UIS'
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
    assert MARK not in css and '#hero.hero:not(.f-hero){padding-bottom' not in css, 'на сайте блок уже есть'
    assert css.endswith('}\n') and HERO_CSS in css
    css_new = (css + blk).encode('utf-8')
    (out_dir / 'pkg').mkdir(parents=True, exist_ok=True)
    (out_dir / 'pkg/style.css').write_bytes(css_new)

    js_old = fetch(JS + '?v=' + OLD_V, JS)
    js = js_old.decode('utf-8')
    assert js.count(JS_OLD) == 1 and 'gsap.matchMedia' not in js, 'app.min.js: ожидаемый участок не найден или правка уже есть'
    js_new = js.replace(JS_OLD, JS_NEW).encode('utf-8')
    assert js_new.decode('utf-8').replace(JS_NEW, JS_OLD) == js
    (out_dir / 'pkg' / JS).write_bytes(js_new)
    node = subprocess.run(['node', '--check', str(out_dir / 'pkg' / JS)], capture_output=True, cwd=ROOT)
    assert node.returncode == 0, 'app.min.js: синтаксис ' + node.stderr.decode()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        pages = sorted(pool.map(page, paths), key=lambda r: r['file'])

    # порядок выкладки: стили, скрипт, затем страницы
    rows = [{'file': 'style.css', 'before': sha(css_old), 'after': sha(css_new), 'append': blk},
            {'file': JS, 'before': sha(js_old), 'after': sha(js_new), 'replace': [[JS_OLD, JS_NEW, 1]]}] + pages
    payload = {'name': NAME, 'old_version': OLD_V, 'new_version': NEW_V, 'pages': len(pages), 'files': rows}
    data = json.dumps(payload, ensure_ascii=False, indent=1).encode('utf-8') + b'\n'
    manifest = ''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows)
    if check:
        assert (out_dir / 'deploy_payload.json').read_bytes() == data, 'пакет не совпадает'
        assert (out_dir / 'MANIFEST.txt').read_text(encoding='utf-8') == manifest
        print('пакет совпадает: %d файлов' % len(rows))
        return
    (out_dir / 'deploy_payload.json').write_bytes(data)
    (out_dir / 'MANIFEST.txt').write_text(manifest, encoding='utf-8')
    print('Готово: %d файлов (style.css, app.min.js и %d страниц). Пакет: %s' % (len(rows), len(pages), out_dir))


if __name__ == '__main__':
    main()
