#!/usr/bin/env python3
"""Title и description главной (вариант А + описание 1а): пакет для Timeweb из актуального рабочего сайта (13.11.2026).

    python3 tools/deploy/prepare-2026-11-13-home-title.py <новая папка пакета>

Решение владельца 13.11.2026 по документу проекта «SEO/Главная — title и description на согласование 2026-11-13»:
заголовок А и описание 1а — «да!». Главная снимается с сайта по HTTPS и правится точечно, остальное — байт в байт:
  * <title> — «Пест-контроль для бизнеса в Москве и области — ПЕСТКОНТРОЛЬ Центр»;
  * <meta name="description"> — описание 1а, в «3 900 ₽/мес» неразрывные пробелы (цена не разрывается);
  * <meta property="og:title"> — «Пест-контроль для бизнеса в Москве и области» (как H1);
  * разметка WebPage (JSON-LD): те же name и description, dateModified — дата выкладки.
H1, og:description, og:site_name, тексты, счётчики Метрики, UIS и Radist не меняются.

Проверки: закон о счётчиках и контактах (tools/site/tracking_laws.py) и закон независимости
(tools/site/independence_law.py) до и после; обратная замена даёт исходную главную байт в байт; JSON-LD разбирается,
в WebPage новые name и description; других вхождений старых title и description на странице нет.

В папке пакета: backup/index.php и pkg/index.php (до и после), MANIFEST.txt и deploy_payload.json для
publish_home_title.py — серверный скрипт сам применяет те же замены к главной в public_html и сверяет SHA-256.
"""
import hashlib
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import independence_law  # noqa: E402
import tracking_laws  # noqa: E402

NAME = 'home-title-2026-11-13'
DATE_OLD, DATE_NEW = '2026-11-12', '2026-11-13'
NB = '\u00a0'
T_OLD = 'Пест-контроль и пест-менеджмент для бизнеса в Москве и области — ПЕСТКОНТРОЛЬ Центр'
T_NEW = 'Пест-контроль для бизнеса в Москве и области — ПЕСТКОНТРОЛЬ Центр'
D_OLD = ('Пест-контроль и пест-менеджмент по системе IPM для предприятий Москвы и области: бесплатный аудит и оценка '
         'пест-риска, программа пест-контроля, мониторинг вредителей и прогноз численности.')
D_NEW = ('Дератизация, дезинсекция и дезинфекция для организаций. Сначала бесплатный аудит, затем пест-менеджмент '
         'по системе IPM от 3' + NB + '900' + NB + '₽/мес: мониторинг, обработки по показаниям, журнал и акт после визита.')
OG_OLD = 'Пест-контроль и пест-менеджмент для бизнеса в Москве и области'
OG_NEW = 'Пест-контроль для бизнеса в Москве и области'
H1 = 'Пест-контроль для бизнеса в Москве и области'
SITE_ID = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
LD_TAIL = ('","inLanguage":"ru","isPartOf":{"@id":"' + SITE_ID + '#website"},"about":{"@id":"' + SITE_ID
           + '#org"},"dateModified":"')

assert len(T_NEW) == 65 and len(D_NEW) == 198, (len(T_NEW), len(D_NEW))
assert OG_NEW == H1 and T_NEW.startswith(OG_NEW + ' — ')

RULES = [
    ['<title>' + T_OLD + '</title>', '<title>' + T_NEW + '</title>', 1],
    ['<meta name="description" content="' + D_OLD + '">', '<meta name="description" content="' + D_NEW + '">', 1],
    ['<meta property="og:title" content="' + OG_OLD + '">', '<meta property="og:title" content="' + OG_NEW + '">', 1],
    ['"name":"' + T_OLD + '","description":"' + D_OLD + LD_TAIL + DATE_OLD + '"',
     '"name":"' + T_NEW + '","description":"' + D_NEW + LD_TAIL + DATE_NEW + '"', 1],
]


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(b):
    return hashlib.sha256(b).hexdigest()


def webpage(s):
    i = s.index('<script type="application/ld+json">') + len('<script type="application/ld+json">')
    data = json.loads(s[i:s.index('</script>', i)])
    pages = [n for n in data['@graph'] if n.get('@type') == 'WebPage']
    assert len(pages) == 1
    return pages[0]


live = module('check_live', 'tools/qa/check_live.py')
OUT = pathlib.Path(sys.argv[1]).resolve()
assert not OUT.exists(), 'используйте новую папку: прежние копии не перезаписываются'

status, body = live.get(live.SITE)
assert status == 200, 'главная: HTTP %s' % status
old = body.decode('utf-8')
assert '<?php' not in old and '<?=' not in old
h1 = re.findall(r'<h1[^>]*>(.*?)</h1>', old, re.S)
assert len(h1) == 1 and ' '.join(re.sub(r'<[^>]+>', ' ', h1[0]).replace(NB, ' ').split()) == H1, 'H1 главной другой'
bad = tracking_laws.check_page(old, counters=True)
assert not bad, 'исходная главная: %s' % bad
hard_before = independence_law.violations(old)

new = old
for a, b, c in RULES:
    assert new.count(a) == c, 'найдено %d вместо %d: %s' % (new.count(a), c, a[:70])
    new = new.replace(a, b)
assert T_OLD not in new and D_OLD not in new and OG_OLD + '"' not in new
back = new
for a, b, c in reversed(RULES):
    assert back.count(b) == c
    back = back.replace(b, a)
assert back == old, 'отличия вне согласованных мест'
bad = tracking_laws.check_page(new, counters=True)
assert not bad, 'результат: %s' % bad
hard_after = independence_law.violations(new)
assert hard_after == hard_before == [], 'закон независимости: %s' % hard_after
page = webpage(new)
assert page['name'] == T_NEW and page['description'] == D_NEW and page['dateModified'] == DATE_NEW
head = new[:new.index('</head>')]
assert head.count('<title>') == 1 and head.count('name="description"') == 1 and head.count('property="og:title"') == 1

(OUT / 'backup').mkdir(parents=True)
(OUT / 'pkg').mkdir()
(OUT / 'backup' / 'index.php').write_bytes(body)
(OUT / 'pkg' / 'index.php').write_bytes(new.encode('utf-8'))
row = {'file': 'index.php', 'before': sha(body), 'after': sha(new.encode('utf-8')), 'replace': RULES, 'append': ''}
payload = {'name': NAME, 'count': 1, 'files': [row]}
(OUT / 'deploy_payload.json').write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding='utf-8')
(OUT / 'MANIFEST.txt').write_text('%s  %s  index.php\n' % (row['before'], row['after']), encoding='utf-8')
print('OK %s: index.php %s… → %s… (%d замены), счётчики и контакты — без нарушений, независимость — без нарушений'
      % (NAME, row['before'][:8], row['after'][:8], len(RULES)))
print('title (%d): %s' % (len(T_NEW), T_NEW))
print('description (%d): %s' % (len(D_NEW), D_NEW.replace(NB, '[nbsp]')))
print('og:title: %s' % OG_NEW)
