#!/usr/bin/env python3
"""Статические регрессионные проверки страницы, без сетевых запросов и публикации."""
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/site'))
import unify
import tracking_laws  # закон владельца 11.11.2026: общие страницы меняются им намеренно (телефон, почта, счётчики)
SLUG = 'zashchita-ot-proniknoveniya-gryzunov'
BASELINE = '02a04ee'  # сохраняет утверждённый закон счётчиков, контактов и актуальное меню
SITE = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/'
failures = []


def check(ok, message):
    if not ok:
        failures.append(message)
    print(('PASS ' if ok else 'FAIL ') + message)


def git_file(path):
    return subprocess.check_output(['git', 'show', BASELINE + ':' + path], cwd=ROOT)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def field_signature(form):
    return [(x.name, x.get('name'), x.get('type'), x.has_attr('required'),
             x.get('autocomplete'), x.get('inputmode')) for x in form.select('input,select,textarea')]


for path in ['server/counters.html', 'app.js', 'app.min.js', 'style.css', 'server/send.php', 'index.html']:
    if path == 'server/counters.html':  # изменён законом владельца 11.11.2026: проверяем части, а не базовую версию
        check(set(tracking_laws.counter_parts()) == {'metrika', 'uis', 'noscript', 'radist'},
              path + ': официальные коды счётчиков по закону владельца')
        check(digest((ROOT / path).read_bytes()) == digest(git_file(path)),
              path + ': утверждённые коды не изменены дополнением схемы')
        continue
    base = git_file(path)
    # Актуальная база уже содержит закон владельца: защищённые файлы сравниваем байт в байт.
    check(digest((ROOT / path).read_bytes()) == digest(base), path + ' совпадает с базовой версией')

new = ROOT / SLUG / 'index.html'
s = new.read_text(encoding='utf-8')
soup = BeautifulSoup(s, 'html.parser')
base_soup = BeautifulSoup(git_file('deratizatsiya/index.html'), 'html.parser')
derat_soup = BeautifulSoup((ROOT / 'deratizatsiya/index.html').read_text(), 'html.parser')
derat_without_link = re.sub(
    r' <span id="proof-service-link">.*?</span>', '',
    (ROOT / 'deratizatsiya/index.html').read_text(), count=1)
base_derat_without_link = re.sub(r' <span id="proof-service-link">.*?</span>', '',
                                git_file('deratizatsiya/index.html').decode(), count=1)
check(derat_without_link == base_derat_without_link,
      'на дератизации добавлена только контекстная ссылка, прочая разметка сохранена')
check(str(derat_soup.select_one('#form')) == str(base_soup.select_one('#form')),
      'существующая форма дератизации сохранена без изменений')
check(field_signature(soup.select_one('#form')) == field_signature(base_soup.select_one('#form')),
      'схема полей, обязательность и атрибуты новой формы совпадают с исходными')
for selector in ['input[name=name]', 'input[name=phone]', 'select[name=type]']:
    element = soup.select_one(selector)
    visible = element.get('placeholder', '') if element.name == 'input' else element.find('option').get_text()
    check(element.has_attr('required') and '*' in visible, selector + ': обязательность и звёздочка')

check(len(soup.select('h1')) == 1, 'один H1')
check(' '.join(soup.h1.stripped_strings) == 'Защита от проникновения грызунов', 'H1 соответствует услуге')
check(50 <= len(soup.title.get_text()) <= 60, 'длина title 50–60 символов')
check(140 <= len(soup.select_one('meta[name=description]')['content']) <= 155, 'длина description 140–155 символов')
check(soup.select_one('link[rel=canonical]')['href'] == SITE + SLUG + '/', 'canonical на будущий основной адрес')
check(soup.select_one('meta[name=robots]')['content'] == 'noindex, nofollow', 'GitHub-превью закрыто от индексации')
check('ym(113675622' not in s and 'track.radist.me' not in s and 'app.uiscom.ru/static/' not in s,
      'производственные счётчики не запущены на превью')
check(not tracking_laws.check_page(s, counters=False),
      'телефон и почта превью соответствуют закону владельца')
check('{{' not in s and 'TODO' not in s, 'нет незаменённых плейсхолдеров')
check(soup.select_one('#proof-contours-svg') is not None and
      len(soup.select('#proof-contours [data-contour-button]')) == 4,
      'схема здания и управление всеми тремя контурами присутствуют')
check(soup.select_one('script[type=module][src="contours.js"]') is not None,
      'небольшой модуль схемы подключён отдельно, без 3D-библиотек')
check(s.count('id="proof-mobile-performance"') == 1 and unify.proof_performance(s) == s,
      'мобильная оптимизация присутствует и идемпотентна')
text = soup.get_text(' ', strip=True).lower()
check('фумигац' not in text and 'газаци' not in text and 'деорнитизац' not in text, 'нет запрещённых направлений')

ids = [x['id'] for x in soup.select('[id]')]
check(len(ids) == len(set(ids)), 'нет дублирующихся id')
graph = json.loads(soup.select_one('script[type="application/ld+json"]').string)['@graph']
types = {x['@type'] for x in graph}
check({'Organization', 'WebPage', 'Service', 'BreadcrumbList', 'FAQPage'} <= types, 'все согласованные типы JSON-LD')
faq = next(x for x in graph if x['@type'] == 'FAQPage')['mainEntity']
check(len(faq) == len(soup.select('.qa')) == 8, 'восемь FAQ в тексте и разметке')
normalize = lambda v: re.sub(r'\s+', ' ', v).strip()
for question, node in zip(faq, soup.select('.qa')):
    check(normalize(question['name']) == normalize(node.select_one('button').get_text(' ', strip=True))
          and normalize(question['acceptedAnswer']['text']) == normalize(node.select_one('.ans').get_text(' ', strip=True)),
          'FAQ соответствует видимому тексту: ' + question['name'][:38])
check(not any(x.get('price') is not None or x.get('@type') in ('Offer', 'AggregateOffer') for x in graph),
      'нет выдуманных цен и предложений в разметке')

broken = []
for node in soup.select('[href], [src], [srcset], [imagesrcset]'):
    for attribute in ['href', 'src', 'srcset', 'imagesrcset']:
        value = node.get(attribute)
        if not value or value.startswith(('data:', 'tel:', 'mailto:', 'http:', 'https:')):
            continue
        values = [p.strip().split()[0] for p in value.split(',')] if attribute.endswith('srcset') else [value]
        for val in values:
            url = urlsplit(val)
            target = (new.parent / unquote(url.path)).resolve() if url.path else new
            if target.is_dir():
                target = target / 'index.html'
            if not target.exists():
                broken.append(val)
            elif url.fragment and target.suffix == '.html':
                target_soup = soup if target == new else BeautifulSoup(target.read_text(), 'html.parser')
                if not target_soup.find(id=unquote(url.fragment)):
                    broken.append(val + ' (якорь)')
check(not broken, 'все внутренние ссылки, якоря и ресурсы существуют: ' + str(broken))
check(derat_soup.select_one('#proof-service-link a')['href'] == '../' + SLUG + '/',
      'дератизация ссылается на новую услугу')
catalog = BeautifulSoup((ROOT / 'preview-services/index.html').read_text(), 'html.parser')
check(catalog.select_one('[data-service=zashchita-gryzuny]')['href'] == SLUG + '/index.html',
      'каталог тестовой главной ссылается на новую услугу')
index = json.loads((ROOT / 'search-index.json').read_text())
check(any(SLUG + '/' == p[1] for p in index['p']), 'страница присутствует во внутреннем поиске')
check(SITE + SLUG + '/' in (ROOT / 'server/sitemap.xml').read_text(), 'адрес есть в производственном sitemap')

prod = ROOT / 'dist/timeweb' / SLUG / 'index.php'
if prod.exists():
    p = prod.read_text()
    sys.path.insert(0, str(ROOT / 'tools' / 'site'))
    import tracking_laws  # закон владельца 11.11.2026: официальные коды счётчиков на своих местах, телефон и почта без тегов
    laws = tracking_laws.check_page(p)
    check(not laws, 'производственная сборка: счётчики и разметка телефона/почты по закону владельца ' + str(laws))
    check('noindex' not in p, 'производственная сборка: noindex удалён')
    check(digest(re.search(r'<form class="form".*?</form>', p, re.S)[0].encode())
          == digest(re.search(r'<form class="form".*?</form>', s, re.S)[0].encode()),
          'производственная сборка: форма совпадает с проверенной')
else:
    check(False, 'производственная сборка выполнена локально')

print(json.dumps({'failures': failures, 'passed': not failures}, ensure_ascii=False))
raise SystemExit(1 if failures else 0)
