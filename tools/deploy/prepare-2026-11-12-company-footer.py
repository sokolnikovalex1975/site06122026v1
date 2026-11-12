#!/usr/bin/env python3
"""Точечный пакет подвала из актуального сайта, без переноса других правок GitHub.

python3 tools/deploy/prepare-2026-11-12-company-footer.py <папка пакета>
"""
import concurrent.futures
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import tracking_laws


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


menu = module('company_menu', 'tools/menu/apply_menu.py')
live = module('check_live', 'tools/qa/check_live.py')
SITE = live.SITE
OUT = pathlib.Path(sys.argv[1]).resolve()
assert not OUT.exists(), 'используйте новую папку: прежние копии не перезаписываются'
OUT.mkdir(parents=True)


def sha(b):
    return hashlib.sha256(b).hexdigest()


status, sitemap = live.get(SITE + 'sitemap.xml')
assert status == 200
paths = []
for node in ET.fromstring(sitemap).iter():
    if node.tag.endswith('}loc') or node.tag == 'loc':
        url = node.text.strip()
        assert url.startswith(SITE), url
        path = urllib.parse.urlsplit(url).path.lstrip('/')
        if path.endswith('/') or path == '':
            paths.append(path)
paths = sorted(set(paths) | {'privacy/', 'soglasie/'})
assert 30 <= len(paths) <= 60, f'неожиданное число страниц: {len(paths)}'


def prepare(path):
    status, original = live.get(SITE + path)
    assert status == 200, f'{path}: HTTP {status}'
    old = original.decode('utf-8')
    assert 'id="requisites"' not in old, path + ': правка уже на сайте'
    assert '<?php' not in old and '<?=' not in old, path + ': PHP в HTML'
    counters = path not in ('privacy/', 'soglasie/')
    before_bad = tracking_laws.check_page(old, counters=counters)
    assert not before_bad, f'{path}: исходная страница: {before_bad}'
    new = menu.company_footer(old)
    assert menu.company_footer(new) == new, path + ': неидемпотентно'
    after_bad = tracking_laws.check_page(new, counters=counters)
    assert not after_bad, f'{path}: результат: {after_bad}'
    back = re.sub(r'<style id="ft-company-st">.*?</style>\n', '', new, flags=re.S)
    back = re.sub(r'  <div class="wrap ft-company" id="requisites">.*?</div>\n', '', back, flags=re.S)
    assert back == old, path + ': изменён посторонний HTML'
    result = new.encode('utf-8')
    rel = path + 'index.php'
    for folder, content in [('backup', original), ('pkg', result)]:
        f = OUT / folder / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    return {'file': rel, 'before': sha(original), 'after': sha(result)}


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    checks = sorted(pool.map(prepare, paths), key=lambda x: x['file'])
(OUT / 'MANIFEST.txt').write_text(
    ''.join(f"{r['before']}  {r['after']}  {r['file']}\n" for r in checks),
    encoding='utf-8'
)
(OUT / 'checks.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / 'sitemap-before.xml').write_bytes(sitemap)
launcher = (ROOT / 'tools/deploy/launch-2026-11-11-btn.sh').read_text(encoding='utf-8')
launcher = launcher.replace('btn-2026-11-11.tmp', 'footer-2026-11-12.tmp')
launcher = launcher.replace('before-btn_2026-11-11_ftp.zip', 'before-footer_2026-11-12_ftp.zip')
(OUT / 'publish.sh').write_text(launcher, encoding='utf-8')
print(f'Готово: {len(checks)} актуальных страниц; только подвал; счётчики и контакты неизменны. Пакет: {OUT}')
