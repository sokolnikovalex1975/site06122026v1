#!/usr/bin/env python3
"""Переход к блоку по якорю — начало блока сразу под шапкой (13.11.2026): точечный пакет для Timeweb из актуального сайта.

    python3 tools/deploy/prepare-2026-11-13-zagolovok.py <новая папка>            # снять сайт по HTTPS и собрать пакет
    SRC=<папка снимка> python3 tools/deploy/prepare-2026-11-13-zagolovok.py <новая папка>   # то же из готового снимка
    python3 tools/deploy/prepare-2026-11-13-zagolovok.py <папка> --check          # пересобрать из <папка>/backup и сверить

Запрос владельца 13.11.2026: при щелчке по пункту меню блок открывается не с заголовка — сверху остаётся пустое тёмное
поле; заголовок блока должен быть сверху. Было: верх раздела на 176 px от верха окна (щелчок на странице) или 96 px
(переход с другой страницы) плюс собственный отступ раздела 80–130 px — подпись над заголовком на 240–280 px от верха
окна, шапка при прокрутке вниз уезжала. Стало: подпись над заголовком — сразу под шапкой, шапка видна.

Что меняется на рабочем сайте (остальное — байт в байт):
  * app.min.js — три точные замены в сжатом коде рабочего файла (в GitHub есть ещё не опубликованные правки других
    задач, поэтому файл не собирается из app.js заново):
      1) прокрутка к блоку по щелчку (scrollToEl) сначала передаёт работу window.pcAnchor.go;
      2) шапка не прячется, пока у #hdr класс hold (страница едет к блоку);
      3) последний раздел «переход по ссылке с якорем с другой страницы» заменяется разделом «переход к блоку по
         якорю» из app.js репозитория, сжатым esbuild (прежний раздел на сайте совпадает с esbuild байт в байт);
  * style.css — scroll-padding-top 96 px → высота шапки + 20…32 px и scroll-margin-top разделов (.s, .cta) с
    пояснением, ровно как в style.css репозитория; главная (стили встроены) — те же правила, сжатые esbuild;
  * legal.css — scroll-margin-top разделов политики и согласия (заголовок раздела по оглавлению — под шапкой);
  * все страницы — style.css?v= и app.min.js?v= 20261113ekran → 20261113zagolovok, на политике и согласии ещё
    legal.css?v=20261108 → 20261113zagolovok (у файлов кэш на год).
Счётчики — по закону владельца (tracking_laws) до и после: Метрика, UIS и Radist не меняются. После обратной замены
каждый файл совпадает со снимком байт в байт; app.min.js проходит node --check.
"""
import concurrent.futures
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import tracking_laws  # noqa: E402

NAME = 'zagolovok-2026-11-13'
BASE = 'HEAD'  # версия репозитория до правки — задаёт main() через base_rev()
OLD_V, NEW_V = '20261113ekran', '20261113zagolovok'
LEGAL_OLD_V = '20261108'
LEGAL = ('privacy/', 'soglasie/')
JS = 'app.min.js'
ESBUILD = ['npx', '--yes', 'esbuild@0.24.2']
# app.min.js рабочего сайта: d — Lenis, D — «уменьшение движения», S — #hdr, Y — меню открыто, Z — прежняя прокрутка
JS1_OLD = 'var te=function(t,e){d?d.scrollTo(e?0:t,{offset:e?0:-80,duration:1.5,'
JS1_NEW = 'var te=function(t,e){if(window.pcAnchor)return window.pcAnchor.go(t,e,d,D);d?d.scrollTo(e?0:t,{offset:e?0:-80,duration:1.5,'
JS2_OLD = 'S.classList.toggle("scrolled",t>30),Y||(t>Z+4&&t>500?S.classList.add("hide"):(t<Z-4||t<200)&&S.classList.remove("hide")),Z=t;'
JS2_NEW = ('S.classList.toggle("scrolled",t>30),S.classList.contains("hold")?S.classList.remove("hide"):'
           'Y||(t>Z+4&&t>500?S.classList.add("hide"):(t<Z-4||t<200)&&S.classList.remove("hide")),Z=t;')
OLD_MARK = '/* ---------- переход по ссылке с якорем с другой страницы (13.11.2026) ----------'
NEW_MARK = '/* ---------- переход к блоку по якорю: начало блока — сразу под шапкой (13.11.2026) ----------'
CSS_FROM = 'html{scroll-behavior:smooth;scroll-padding-top:96px}\n'
CSS_TO = 'html:has(:target){scroll-behavior:auto}\n'
INLINE_OLD = 'html{scroll-behavior:smooth;scroll-padding-top:96px}html:has(:target){scroll-behavior:auto}'


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


def esbuild(text, loader):
    args = ['--minify', '--charset=utf8', '--log-level=warning', '--loader=' + loader]
    if loader == 'js':
        args.append('--target=es2015')
    return subprocess.run(ESBUILD + args, input=text, capture_output=True, text=True, cwd=ROOT, check=True).stdout


def base_rev():
    """Версия репозитория до этой правки: родитель коммита, где в app.js появился раздел NEW_MARK (до коммита — HEAD).
    BASE_REV=<коммит> — указать явно."""
    if os.environ.get('BASE_REV'):
        return os.environ['BASE_REV']
    found = subprocess.run(['git', 'log', '--format=%H', '-S', NEW_MARK, '--', 'app.js'],
                           capture_output=True, text=True, cwd=ROOT, check=True).stdout.split()
    return found[-1] + '~1' if found else 'HEAD'


def git_head(rel):
    """Файл репозитория до этой правки (прежние правила и прежний раздел app.js)."""
    return subprocess.run(['git', 'show', BASE + ':' + rel], capture_output=True, text=True, cwd=ROOT, check=True).stdout


def css_blocks():
    """Прежний и новый участок style.css (от html{scroll-behavior…} до html:has(:target)…) — из GitHub и рабочей копии."""
    head, work = git_head('style.css'), (ROOT / 'style.css').read_text(encoding='utf-8')
    i = head.index(CSS_FROM)
    old = head[i:head.index(CSS_TO, i) + len(CSS_TO)]
    k = work.index('/* переход к блоку по якорю (13.11.2026)')
    new = work[k:work.index(CSS_TO, k) + len(CSS_TO)]
    assert work[:k] == head[:i] and work[k + len(new):] == head[i + len(old):], 'style.css: другие отличия от GitHub'
    assert old.startswith(CSS_FROM) and old.endswith(CSS_TO) and 'scroll-margin-top' not in old, old
    assert 'scroll-padding-top:96px' not in new and new.count('scroll-margin-top') == 2 and new.endswith(CSS_TO), new
    return old, new


def legal_blocks():
    old = git_head('legal.css')
    new = (ROOT / 'legal.css').read_text(encoding='utf-8')
    r = []
    a = '.l-sec{padding-top:8px}\n'
    i = new.index(a) + len(a)
    j = new.index('.l-lead+.l-sec{margin-top:28px}\n', i)
    r.append([a + '.l-lead+.l-sec{margin-top:28px}\n', a + new[i:j] + '.l-lead+.l-sec{margin-top:28px}\n', 1])
    b = '  .l-sec h2{margin-top:48px;scroll-margin-top:90px}\n'
    r.append([b + '}\n', b + '  .l-sec[id]{scroll-margin-top:-56px}\n}\n', 1])
    out = old
    for x, y, n in r:
        assert out.count(x) == n, x
        out = out.replace(x, y)
    assert out == new, 'legal.css: кроме двух правил есть другие отличия от GitHub'
    return r


def main():
    global BASE
    BASE = base_rev()
    print('исходные файлы репозитория до правки:', BASE)
    out_dir = pathlib.Path(sys.argv[1]).resolve()
    check = '--check' in sys.argv[2:]
    src = os.environ.get('SRC', '')
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
        if src:  # снимок рабочего сайта (страницы — <путь>/index.html)
            s = pathlib.Path(src) / (rel_file[:-len('index.php')] + 'index.html' if rel_file.endswith('index.php') else rel_file)
            body = s.read_bytes()
        else:
            status, body = live.get(site + rel_url, tries=8)  # ложные 502 из облака — больше повторов
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
    assert 'zashchita-ot-proniknoveniya-gryzunov/' not in paths, 'страница защиты от проникновения — только в превью'

    css_old_blk, css_new_blk = css_blocks()
    inline_new = esbuild(css_new_blk, 'css').strip()
    assert inline_new.startswith('html{scroll-behavior:smooth;scroll-padding-top:calc(') and inline_new.endswith(
        'html:has(:target){scroll-behavior:auto}') and 'section.s[id]{' in inline_new and 'section.cta[id]{' in inline_new, inline_new
    assert esbuild(css_old_blk, 'css').strip() == INLINE_OLD
    parts = tracking_laws.counter_parts()

    # app.min.js: прежний последний раздел (как на сайте) и новый — из app.js, сжатые esbuild
    app_head, app_new = git_head('app.js'), (ROOT / 'app.js').read_text(encoding='utf-8')
    sec_old = esbuild(app_head[app_head.index(OLD_MARK):], 'js')
    sec_new = esbuild(app_new[app_new.index(NEW_MARK):], 'js')
    assert sec_old.endswith('})();\n') and sec_new.endswith('})();\n') and 'pcAnchor' in sec_new and 'pcAnchor' not in sec_old

    def page(path):
        original = fetch(path, path + 'index.php')
        text = original.decode('utf-8')
        assert '<?php' not in text and '<?=' not in text, path + ': PHP в HTML'
        counters = path not in LEGAL
        bad = tracking_laws.check_page(text, counters=counters, parts=parts)
        assert not bad, path + ': живая страница нарушает закон о счётчиках: ' + str(bad[:3])
        assert NEW_V not in text, path + ': правка уже на сайте'
        refs = re.findall(r'[^"\' ]*\?v=' + OLD_V, text)
        assert refs and all(r.endswith(('style.css?v=' + OLD_V, 'app.min.js?v=' + OLD_V)) for r in refs), path + ': ' + str(refs)
        replace = [['?v=' + OLD_V, '?v=' + NEW_V, len(refs)]]
        if path in LEGAL:
            a = 'legal.css?v=' + LEGAL_OLD_V + '"'
            assert text.count(a) == 1, path + ': legal.css'
            replace.append([a, 'legal.css?v=' + NEW_V + '"', 1])
        if path == '':
            assert 'style.css' not in text and text.count(INLINE_OLD) == 1, 'главная: стили встроены, правила прежние'
            assert text.index(INLINE_OLD) < text.index('<!-- style:end -->') < text.index('</head>')
            replace.append([INLINE_OLD, inline_new, 1])
        result = text
        for a, b, n in replace:
            assert result.count(a) == n, path + ': ' + a
            result = result.replace(a, b)
        bad = tracking_laws.check_page(result, counters=counters, parts=parts)
        assert not bad, path + ': правка нарушает закон о счётчиках: ' + str(bad[:3])
        for k, p in parts.items():
            if counters:
                assert text.count(p) == result.count(p) == 1, path + ': часть счётчиков ' + k
            else:
                assert text.count(p) == result.count(p) == 0, path + ': счётчики на юридической странице'
        back = result
        for a, b, n in reversed(replace):
            back = back.replace(b, a)
        assert back == text, path + ': изменения вне согласованных мест'
        res = result.encode('utf-8')
        f = out_dir / 'pkg' / (path + 'index.php')
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(res)
        return {'file': path + 'index.php', 'before': sha(original), 'after': sha(res), 'replace': replace}

    def static(rel, ops):
        old_b = fetch(rel + ('?v=' + OLD_V if rel != 'legal.css' else '?v=' + LEGAL_OLD_V), rel)
        old = old_b.decode('utf-8')
        new = old
        for a, b, n in ops:
            assert new.count(a) == n, rel + ': участок не найден или правка уже есть — ' + a[:70]
            new = new.replace(a, b)
        back = new
        for a, b, n in reversed(ops):
            back = back.replace(b, a)
        assert back == old, rel + ': обратная замена не даёт исходник'
        new_b = new.encode('utf-8')
        f = out_dir / 'pkg' / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(new_b)
        return {'file': rel, 'before': sha(old_b), 'after': sha(new_b), 'replace': ops}

    rows = [static('style.css', [[css_old_blk, css_new_blk, 1]]),
            static('legal.css', legal_blocks())]
    js_row = static(JS, [[JS1_OLD, JS1_NEW, 1], [JS2_OLD, JS2_NEW, 1], ['\n' + sec_old, '\n' + sec_new, 1]])
    js_text = (out_dir / 'pkg' / JS).read_text(encoding='utf-8')
    assert js_text.endswith('\n' + sec_new) and js_text.count('pcAnchor') == sec_new.count('pcAnchor') + 2
    node = subprocess.run(['node', '--check', str(out_dir / 'pkg' / JS)], capture_output=True, cwd=ROOT)
    assert node.returncode == 0, 'app.min.js: синтаксис ' + node.stderr.decode()
    rows.append(js_row)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        pages = sorted(pool.map(page, paths), key=lambda r: r['file'])

    # порядок выкладки: стили и скрипт, затем страницы (новая версия в адресе не должна указывать на старый файл)
    rows += pages
    payload = {'name': NAME, 'old_version': OLD_V, 'new_version': NEW_V, 'legal_old_version': LEGAL_OLD_V,
               'pages': len(pages), 'files': rows}
    data = json.dumps(payload, ensure_ascii=False, indent=1).encode('utf-8') + b'\n'
    manifest = ''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows)
    if check:
        assert (out_dir / 'deploy_payload.json').read_bytes() == data, 'пакет не совпадает'
        assert (out_dir / 'MANIFEST.txt').read_text(encoding='utf-8') == manifest
        print('пакет совпадает: %d файлов' % len(rows))
        return
    (out_dir / 'deploy_payload.json').write_bytes(data)
    (out_dir / 'MANIFEST.txt').write_text(manifest, encoding='utf-8')
    print('Готово: %d файлов (style.css, legal.css, app.min.js и %d страниц). Пакет: %s' % (len(rows), len(pages), out_dir))


if __name__ == '__main__':
    main()
