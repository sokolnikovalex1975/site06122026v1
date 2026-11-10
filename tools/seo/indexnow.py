#!/usr/bin/env python3
"""Сообщить Яндексу о новых и изменённых страницах по протоколу IndexNow (с 11.11.2026).

    python3 tools/seo/indexnow.py                                  → все адреса из server/sitemap.xml
    python3 tools/seo/indexnow.py /dezinsektsiya/ /deratizatsiya/  → только эти страницы (пути или полные адреса,
                                                                     можно с кириллическим доменом)
    python3 tools/seo/indexnow.py --dry-run …                      → показать запрос, ничего не отправлять

Ключ лежит в server/<ключ>.txt и на сайте в корне: https://пестконтроль-центр.рф/<ключ>.txt
(в сборку для Timeweb его кладёт tools/site/build_prod.py, проверку на сайте делает tools/qa/check_live.py).
Запрос: POST https://yandex.com/indexnow — https://yandex.ru/support/webmaster/ru/indexing-options/index-now
Ответы (https://www.indexnow.org/documentation): 200 — принято; 202 — принято, ключ ещё проверяется;
400 — неверный формат; 403 — ключ не найден на сайте или не совпадает; 422 — адрес не с этого сайта
или ключ не по формату; 429 — слишком часто.

Когда запускать: после выкладки — только для выложенных страниц, один раз на изменение. Повторно отправлять
неизменённые страницы не нужно: индексацию это не ускоряет. Песочнице Perplexity yandex.com доступен.
"""
import json
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
HOST = 'xn----itbbsflddbfpfdodg9d0f.xn--p1ai'  # пестконтроль-центр.рф
ENDPOINT = 'https://yandex.com/indexnow'


def key():
    files = [p for p in (ROOT / 'server').glob('*.txt') if re.fullmatch(r'[0-9a-f]{32}\.txt', p.name)]
    if len(files) != 1:
        sys.exit(f'ERROR: в server/ должен быть ровно один файл ключа IndexNow, найдено: {len(files)}')
    k = files[0].read_text(encoding='utf-8')
    if k != files[0].stem:
        sys.exit(f'ERROR: {files[0].name}: содержимое должно совпадать с именем файла (без перевода строки)')
    return k


def sitemap_urls():
    s = (ROOT / 'server' / 'sitemap.xml').read_text(encoding='utf-8')
    return re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', s)


def norm(u):
    if not u.startswith(('http://', 'https://')):
        return f'https://{HOST}/' + u.lstrip('/')
    p = urllib.parse.urlsplit(u)
    host = p.hostname.encode('idna').decode('ascii') if p.hostname else ''
    if host != HOST:
        sys.exit(f'ERROR: {u} — адрес не с сайта {HOST}')
    return urllib.parse.urlunsplit(('https', HOST, p.path or '/', p.query, ''))


def main(argv):
    dry = '--dry-run' in argv
    args = [a for a in argv if a != '--dry-run']
    urls = [norm(u) for u in (args or sitemap_urls())]
    urls = list(dict.fromkeys(urls))
    k = key()
    payload = {'host': HOST, 'key': k, 'keyLocation': f'https://{HOST}/{k}.txt', 'urlList': urls}
    print(f'IndexNow: {len(urls)} адрес(ов) → {ENDPOINT}')
    for u in urls:
        print('  ', u)
    if dry:
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 0
    req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode('utf-8'), method='POST',
                                 headers={'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            code, body = r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        code, body = e.code, e.read().decode('utf-8', 'replace')
    print(f'ответ: HTTP {code} {body.strip()[:500]}')
    return 0 if code in (200, 202) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
