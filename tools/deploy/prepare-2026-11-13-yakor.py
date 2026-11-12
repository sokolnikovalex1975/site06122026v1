#!/usr/bin/env python3
"""Переход по якорю с другой страницы и подсветка пунктов меню: пакет для Timeweb из актуального рабочего сайта (13.11.2026).

    python3 tools/deploy/prepare-2026-11-13-yakor.py <новая папка пакета>

Запрос владельца: «Исправь прокрутку якорей и подсветку «Цена» И выложи сразу на Timeweb».
Всё снимается с пестконтроль-центр.рф по HTTPS (в GitHub есть ещё не опубликованные правки других выкладок: параллакс,
зелёная метка «Вы здесь», клиенты) и правится точечно, остальное остаётся байт в байт:
  * app.min.js — в обработчике подсветки пунктов шапки пункт гаснет, когда его блок уходит из середины экрана
    (одна точная замена в сжатом коде), и в конец дописывается раздел «переход по ссылке с якорем с другой страницы»
    из app.js репозитория, сжатый esbuild (как дополнение курсора 11.11.2026);
  * style.css — после html{scroll-behavior:smooth;…} вставляется правило html:has(:target){scroll-behavior:auto}
    с пояснением, ровно как в style.css репозитория;
  * главная — то же правило во встроенных (сжатых) стилях;
  * все страницы — style.css?v= и app.min.js?v= 20261112fon → 20261113yakor (иначе браузеры возьмут старые файлы из кэша).
Проверки: закон владельца о счётчиках и контактах (tools/site/tracking_laws.py) до и после; после обратной замены каждый
файл совпадает со снимком байт в байт; сжатое правило совпадает с esbuild; app.min.js проходит node --check.

В папке пакета: backup/ и pkg/ (копии до и после), MANIFEST.txt, checks.json и deploy_payload.json для
publish_yakor.py — серверный скрипт сам применяет те же замены к файлам public_html и сверяет SHA-256 до и после.
"""
import concurrent.futures
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import tracking_laws  # noqa: E402

NAME = 'yakor-2026-11-13'
V_OLD, V_NEW = '20261112fon', '20261113yakor'
HTML_RULE = 'html{scroll-behavior:smooth;scroll-padding-top:96px}'
NEXT_RULE = 'html.lenis,html.lenis body{height:auto}'
# подсветка пунктов шапки (app.js: «активный пункт меню»): в сжатом app.min.js сайта — ровно одно место
SPY_OLD = ('function(t){t.forEach(function(e){e.isIntersecting&&_.forEach(function(o){o.classList.toggle("active",'
           'Ct(o)===e.target.id)})})}')
SPY_NEW = ('function(t){t.forEach(function(e){_.forEach(function(o){e.isIntersecting?o.classList.toggle("active",'
           'Ct(o)===e.target.id):Ct(o)===e.target.id&&o.classList.remove("active")})})}')
LANDING_MARK = '/* ---------- переход по ссылке с якорем с другой страницы (13.11.2026) ----------'


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


def esbuild(path, css=False):
    args = ['npx', '--yes', 'esbuild@0.24.2', str(path), '--minify', '--charset=utf8', '--log-level=warning']
    args += ['--loader:.css=css'] if css else ['--target=es2015']
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=True).stdout


live = module('check_live', 'tools/qa/check_live.py')
SITE = live.SITE
OUT = pathlib.Path(sys.argv[1]).resolve()
assert not OUT.exists(), 'используйте новую папку: прежние копии не перезаписываются'
OUT.mkdir(parents=True)
TMP = OUT / 'tmp'
TMP.mkdir()

# --- исходники правок из репозитория ---
app_js = (ROOT / 'app.js').read_text(encoding='utf-8')
assert app_js.count(LANDING_MARK) == 1
(TMP / 'landing.js').write_text(app_js[app_js.index(LANDING_MARK):], encoding='utf-8')
ADDON = esbuild(TMP / 'landing.js')
assert ADDON.startswith('(function(){') and ADDON.endswith('})();\n') and 'scrollPaddingTop' in ADDON
css_repo = (ROOT / 'style.css').read_text(encoding='utf-8')
a = css_repo.index(HTML_RULE + '\n') + len(HTML_RULE) + 1
CSS_INSERT = css_repo[a:css_repo.index(NEXT_RULE, a)]
assert CSS_INSERT.endswith('html:has(:target){scroll-behavior:auto}\n') and CSS_INSERT.startswith('/* ')
(TMP / 'rule.css').write_text(CSS_INSERT, encoding='utf-8')
MIN_RULE = esbuild(TMP / 'rule.css', css=True).strip()
assert MIN_RULE == 'html:has(:target){scroll-behavior:auto}', MIN_RULE


def one(s, old, new, what):
    assert s.count(old) == 1, '%s: найдено %d раз' % (what, s.count(old))
    return s.replace(old, new)


def build_static(rel, original):
    s = original.decode('utf-8')
    if rel == 'app.min.js':
        assert 'scrollPaddingTop' not in s and s.endswith('})();\n'), 'app.min.js: дополнение уже есть или другой конец файла'
        new = one(s, SPY_OLD, SPY_NEW, 'app.min.js: подсветка пунктов шапки') + ADDON
        (TMP / 'app.min.js').write_text(new, encoding='utf-8')
        subprocess.run(['node', '--check', str(TMP / 'app.min.js')], check=True)
        back = new[:-len(ADDON)].replace(SPY_NEW, SPY_OLD)
        assert back == s
        return new, [[SPY_OLD, SPY_NEW, 1]], ADDON
    if rel == 'style.css':
        assert 'html:has(:target)' not in s
        new = one(s, HTML_RULE + '\n', HTML_RULE + '\n' + CSS_INSERT, 'style.css: правило html')
        assert new.replace(CSS_INSERT, '', 1) == s
        return new, [[HTML_RULE + '\n', HTML_RULE + '\n' + CSS_INSERT, 1]], ''
    raise AssertionError(rel)


def build_page(path, original):
    old = original.decode('utf-8')
    assert '<?php' not in old and '<?=' not in old, path + ': PHP в HTML'
    counters = path not in ('privacy/', 'soglasie/')
    bad = tracking_laws.check_page(old, counters=counters)
    assert not bad, '%s: исходная страница: %s' % (path, bad)
    rules = []
    for kind in ('style.css', 'app.min.js'):
        a, b = '%s?v=%s' % (kind, V_OLD), '%s?v=%s' % (kind, V_NEW)
        assert kind + '?v=' not in old.replace(a, ''), '%s: версия %s не %s' % (path, kind, V_OLD)
        if a in old:
            rules.append([a, b, old.count(a)])
    if path == '':
        a = HTML_RULE + NEXT_RULE
        rules.append([a, HTML_RULE + MIN_RULE + NEXT_RULE, 1])
    assert 'html:has(:target)' not in old, path + ': правило уже есть'
    new = old
    for a, b, c in rules:
        assert new.count(a) == c, '%s: %s — %d вместо %d' % (path, a, new.count(a), c)
        new = new.replace(a, b)
    assert new.count('app.min.js?v=' + V_OLD) == 0 and new.count('style.css?v=' + V_OLD) == 0
    bad = tracking_laws.check_page(new, counters=counters)
    assert not bad, '%s: результат: %s' % (path, bad)
    back = new
    for a, b, c in reversed(rules):
        assert back.count(b) == c
        back = back.replace(b, a)
    assert back == old, path + ': отличия вне согласованных мест'
    return new, rules, ''


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


def prepare(item):
    rel, is_page = item
    url = SITE + (rel[:-len('index.php')] if is_page else rel)
    status, original = live.get(url, tries=8)  # Timeweb из облака иногда отвечает ложным 502 несколько раз подряд
    assert status == 200, '%s: HTTP %s' % (url, status)
    if is_page:
        new, rules, append = build_page(rel[:-len('index.php')], original)
    else:
        new, rules, append = build_static(rel, original)
    result = new.encode('utf-8')
    for folder, content in (('backup', original), ('pkg', result)):
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    return {'file': rel, 'before': sha(original), 'after': sha(result), 'replace': rules, 'append': append}


items = [('app.min.js', False), ('style.css', False)] + [(p + 'index.php', True) for p in paths]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:  # Timeweb из облака иногда отвечает 502 — бережно
    rows = list(pool.map(prepare, items))
rows.sort(key=lambda r: (r['file'].count('/') > 0 or r['file'] == 'index.php', r['file']))
unchanged = [r['file'] for r in rows if r['before'] == r['after']]
assert not unchanged, 'страницы без версии %s: %s' % (V_OLD, unchanged)
payload = {'name': NAME, 'v_old': V_OLD, 'v_new': V_NEW, 'count': len(rows), 'files': rows}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text(''.join('%s  %s  %s\n' % (r['before'], r['after'], r['file']) for r in rows),
                                  encoding='utf-8')
(OUT / 'checks.json').write_text(json.dumps([{k: r[k] for k in ('file', 'before', 'after')} for r in rows],
                                            ensure_ascii=False, indent=1), encoding='utf-8')
(OUT / 'sitemap-before.xml').write_bytes(sitemap)
shutil.copy2(str(ROOT / 'tools/deploy/publish_yakor.py'), str(OUT / 'publish_yakor.py'))
shutil.rmtree(str(TMP))
pages = [r for r in rows if r['file'].endswith('index.php')]
print('Готово: файлов %d (app.min.js, style.css и страниц %d), замен версий %d. Пакет: %s' % (
    len(rows), len(pages), sum(c for r in pages for a, _, c in r['replace'] if '?v=' in a), OUT))
