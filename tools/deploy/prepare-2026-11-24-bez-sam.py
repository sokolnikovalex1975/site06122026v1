#!/usr/bin/env python3
"""Выкладка правок «без самостоятельных работ» (24.11.2026, пакет bez-sam-2026-11-24).

    python3 tools/site/build_prod.py
    python3 tools/deploy/prepare-2026-11-24-bez-sam.py

Правило владельца 24.11.2026: «не пиши нигде на сайте ничего что клиенты могут делать сами». Согласованные
формулировки на 14 страницах — seo-agent/drafts/2026-11-24-pravki-bez-samostoyatelnyh-rabot.md (проект SEO).
Команда владельца: «делай и выкладывай». В пакете — файлы dist/timeweb, которые на сайте отличаются
(.htaccess и send.php не трогаются), с SHA-256 «до» (по HTTPS) и «после».
"""
import base64
import hashlib
import json
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[2]
DIST = ROOT / 'dist/timeweb'
OUT = ROOT / 'tools/deploy/bez-sam-2026-11-24'
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
SKIP = {'.htaccess', 'send.php'}
NAME = 'bez-sam-2026-11-24'
VERSION = '20261123sborka'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def url(rel):
    if rel == 'index.php':
        return SITE
    if rel.endswith('/index.php'):
        return SITE + urllib.parse.quote(rel[:-len('index.php')])
    return SITE + urllib.parse.quote(rel)


def get(rel):
    last = None
    for i in range(6):
        try:
            req = urllib.request.Request(url(rel), headers={'User-Agent': 'Mozilla/5.0 pestcontrol-check',
                                                            'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(req, timeout=40) as r:
                return rel, r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return rel, None
            last = e
        except Exception as e:  # noqa: BLE001
            last = e
        time.sleep(2 + 2 * i)
    raise SystemExit('не открывается ' + rel + ': ' + str(last))


def main():
    files = sorted(str(p.relative_to(DIST)) for p in DIST.rglob('*') if p.is_file() and p.name not in SKIP)
    with ThreadPoolExecutor(6) as ex:
        live = dict(ex.map(get, files))
    rows = []
    for rel in files:
        b = (DIST / rel).read_bytes()
        old = live[rel]
        if old is not None and sha(old) == sha(b):
            continue
        rows.append({'file': rel, 'kind': 'new' if old is None else 'full',
                     'before': None if old is None else sha(old), 'after': sha(b),
                     'content_b64': base64.b64encode(b).decode('ascii')})
    pages = [r['file'] for r in rows if r['file'].endswith('index.php')]
    payload = {'name': NAME, 'version': VERSION, 'count': len(rows), 'pages': len(pages), 'files': rows}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=True, indent=0), encoding='utf-8')
    lines = ['%-64s  %s  %s' % (r['before'] or '-' * 64, r['after'], r['file']) for r in rows]
    (OUT / 'MANIFEST.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('файлов в пакете: %d (страниц %d, новых %d)' % (len(rows), len(pages),
                                                         sum(r['kind'] == 'new' for r in rows)))
    for cmd in (['tools/site/tracking_laws.py', '--check-prod'] + ['dist/timeweb/' + p for p in pages],
                ['tools/site/independence_law.py', '--check-prod'] + ['dist/timeweb/' + p for p in pages]):
        subprocess.run([sys.executable] + cmd, cwd=str(ROOT), check=True)


if __name__ == '__main__':
    main()
