#!/usr/bin/env python3
"""Поиск по сайту: индекс search-index.json и движок search.min.js в корне сайта.

    python3 tools/search/build_index.py        (запускается из tools/site/build_site.py после меню и разметки)
    python3 tools/search/build_index.py --pages <папка> --out <файл>   — индекс из других копий страниц (например, файлов
        пакета выкладки: tools/deploy/patch-2026-11-08-poisk.py сверяет его с индексом сборки); search.min.js не трогается

Индекс собирается из готовых страниц сайта (тех же, что уходят на хостинг, — список tools/site/build_prod.PAGES)
и из данных страницы «Документы для Роспотребнадзора» (tools/normativnaya-baza/data/dokumenty.json):
  p — страница: H1, description, <title>;
  h — раздел страницы: <section id> с заголовком H2, первый абзац, подзаголовки H3 и первые ячейки таблиц;
  q — вопрос из блока «Вопросы» (якорь #qN, ответ раскрывается сам — см. загрузчик в tools/menu/apply_menu.py);
  d — документ из перечня для Роспотребнадзора (строка таблицы #p<группа>-<номер>, например #p3-4);
  b — папка к проверке для вида объекта: конструктор «Соберите папку» с выбранным видом (?obekt=<slug>#konstruktor);
  n / o — действующий и отменённый норматив из таблиц хаба «Нормативная база»;
  c — проверочный лист по типу объекта (приказы № 578 и № 580);
  f — образцы в PDF, в том числе нужная страница файла (#page=N; номера сверены по тексту PDF при сборке).

Формат: {"v": версия, "p": [[короткое название страницы, адрес], …], "i": [[вид, адрес, заголовок, описание,
ключевые слова, № страницы], …]}. Адреса — от корня сайта, без ведущего «/».
Движок — tools/search/search.js, сжимается esbuild (нужен Node.js; без него остаётся прежний search.min.js).
Версию (V) меняйте вместе с SEARCH_V в tools/menu/apply_menu.py.
"""
import html as H
import json
import pathlib
import re
import shutil
import subprocess
import sys

from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools' / 'site'))
import build_prod  # noqa: E402

V = '20261108'
DOCS = 'normativnaya-baza/dokumenty-dlya-rospotrebnadzora/'
DK = json.loads((ROOT / 'tools' / 'normativnaya-baza' / 'data' / 'dokumenty.json').read_text(encoding='utf-8'))
AKT_PDF = 'obrazets-akta-dezinsektsii-i-deratizatsii.pdf'  # tools/akt/build_akt.py
AKT_BLANK = 'blank-akta-dezinsektsii-i-deratizatsii.pdf'
CHECKLIST_PDF = 'chek-list-dokumentov-dlya-rospotrebnadzora.pdf'  # чек-лист страницы (собирается в файлах проекта)
SKIP_SECTIONS = {'hero', 'zayavka', 'smotrite-takzhe', 'avtor', 'istochniki', 'main', 'korotko'}
SN = 190   # длина описания в индексе
KWN = 320  # длина ключевых слов раздела

# бытовые названия объектов — чтобы «документы для кафе» нашли папку «Ресторан, кафе, столовая» (ключ — slug вида объекта
# в data/dokumenty.json). Бани, прачечные и химчистки по ОКУН — бытовые услуги; аптеки, медицинские, детские и спортивные
# организации, непродовольственные магазины на странице собраны в «Другой объект».
OBJ_KW = {
    'pishchevoe-proizvodstvo': 'пищевое производство цех пекарня хлебозавод мясокомбинат молочный завод кондитерская',
    'restorany': 'ресторан кафе столовая бар общепит общественное питание кофейня пиццерия фудкорт',
    'magaziny': 'магазин продуктов супермаркет торговая сеть рынок продукты торговля',
    'sklady': 'склад логистика распределительный центр хранение',
    'farmproizvodstvo': 'фармацевтическое производство фарма лекарства gmp промышленное предприятие завод',
    'gostinitsy': 'гостиница отель хостел общежитие',
    'uslugi': 'салон красоты парикмахерская маникюр косметология бытовые услуги прачечная химчистка баня сауна',
    'drugoy': ('аптека аптечный пункт медицинская организация медицинский центр клиника поликлиника стоматология '
               'детский сад школа образовательная организация фитнес спортзал спортивный клуб бассейн '
               'непродовольственный магазин одежды обуви электроники техники мебели стройматериалов офис '
               'другой вид деятельности'),
}
# подсказка в заголовке результата: что входит в «Другой объект». Заголовок весит больше синонимов — иначе «аптека»
# (синонимы «фарм», «лекарств» в search.js) поднимала бы папку «Фармацевтическое производство» выше «Другого объекта»
OBJ_HINT = {'drugoy': 'аптека, клиника, школа, детский сад, спорт, офис'}
# образцы в PDF: (файл, страница сайта, [(№ страницы PDF, заголовок, описание, ключевые слова, текст для сверки)])
PPK = 'materialy/programma-proizvodstvennogo-kontrolya-haccp/'
ZH = 'materialy/zhurnal-pest-kontrolya/'
PDFS = [
    (PPK + 'obrazets-programmy-proizvodstvennogo-kontrolya.pdf', PPK, [
        (1, 'Образец программы производственного контроля (ППК) для пищевого производства',
         '27 страниц: ХАССП, лабораторный контроль, журналы, план-график, приложения', 'ппк образец pdf хассп', None),
        (15, 'Раздел ППК «Дезинсекция и дератизация (пест-контроль)»',
         'Раздел 11.3 образца ППК: цель, объекты контроля, периодичность, пороги, меры безопасности (стр. 15–16)',
         'пест-контроль раздел ппк дератизация дезинсекция', '11.3'),
        (20, 'План-схема производства с точками пест-контроля (приложение 1 к ППК)',
         'Точки отбора проб и точки пест-контроля на плане производства', 'план-схема схема точек тпк', 'ПРИЛОЖЕНИЕ 1'),
        (11, 'Критические контрольные точки (план ХАССП) в образце ППК', 'Раздел 6.3 образца ППК', 'ккт хассп', '6.3'),
        (19, 'Сводный план-график производственного контроля на год', 'Раздел 14.1 образца ППК', 'план-график', '14.1'),
    ]),
    (ZH + 'obrazets-zhurnala-pest-kontrolya.pdf', ZH, [
        (1, 'Образец заполнения журнала пест-контроля (PDF, 10 листов)', 'Форма ЖПК-01: 9 разделов, записи за два месяца',
         'журнал пест-контроля образец заполнения', None),
        (3, 'Реестр точек пест-контроля (ТПК) — раздел 2 журнала', 'Номера точек, тип устройства, контур, место, порог',
         'реестр тпк точки', 'Раздел 2'),
        (5, 'Ведомость визитов и расхода средств — раздел 4 журнала', 'Дата, вид визита, работы, расход средств, № акта',
         'ведомость визиты расход акт', 'Раздел 4'),
        (8, 'Замечания, предписания и корректирующие действия — раздел 7 журнала', 'Что выявлено, рекомендация, срок, отметка о выполнении',
         'замечания рекомендации корректирующие', 'Раздел 7'),
        (9, 'Сигнальный лист персонала и инструктажи — раздел 8 журнала', 'Записи сотрудников о вредителях между визитами',
         'сигнальный лист инструктаж', 'Раздел 8'),
    ]),
    (ZH + 'shablon-zhurnala-pest-kontrolya.pdf', ZH, [
        (1, 'Бланк журнала пест-контроля для печати (PDF)', 'Та же форма ЖПК-01 без записей', 'журнал бланк шаблон печать', None),
    ]),
    ('dogovor-deratizatsiya-dezinsektsiya/obrazets-dogovora-pestkontrol-tsentr.pdf', 'dogovor-deratizatsiya-dezinsektsiya/', [
        (1, 'Образец договора на дератизацию и дезинсекцию (PDF)', '6 страниц: предмет, права и обязанности, приёмка работ, приложения',
         'договор образец pdf', None),
        (6, 'Подготовка помещений к обработке — приложение № 2 к договору', 'Что сделать перед дезинсекцией и дератизацией',
         'подготовка помещений памятка', 'Приложение № 2'),
    ]),
    ('materialy/programma-pest-kontrolya/obrazets-programmy-pest-kontrolya.pdf', 'materialy/programma-pest-kontrolya/', [
        (1, 'Образец программы пест-контроля на предприятии (PDF)', '6 страниц: паспорт объекта, целевые виды, план мероприятий, средства, контроль качества',
         'программа пест-контроля образец pdf', None),
    ]),
    (DOCS + AKT_PDF, DOCS, [
        (1, 'Образец акта обследования и выполненных работ по дезинсекции и дератизации (PDF)',
         'Форма АПК-01: обследование по контурам, работы со средствами и расходом, контроль эффективности, рекомендации',
         'акт образец заполнения дератизация дезинсекция выполненных работ', None),
    ]),
    (DOCS + AKT_BLANK, DOCS, [
        (1, 'Бланк акта дезинсекции и дератизации для печати (PDF)', 'Та же форма АПК-01 без записей', 'акт бланк шаблон печать', None),
    ]),
    (DOCS + CHECKLIST_PDF, DOCS, [
        (1, 'Чек-лист документов для проверки Роспотребнадзора (PDF, 10 страниц)',
         '41 общий документ и разделы для восьми видов объектов: кто готовит и основание; отметки «Есть», «Нет», «Не нужно»',
         'чек-лист чеклист документы проверка pdf папка', None),
    ]),
]


def clean(s):
    s = H.unescape(s or '').replace('\u00a0', ' ').replace('\u00ad', '').replace('\u200b', '')
    return re.sub(r'\s+', ' ', s).strip()


def cut(s, n=SN):
    s = clean(s)
    if len(s) <= n:
        return s
    s = s[:n]
    k = s.rfind(' ')
    return (s[:k] if k > n * 0.6 else s).rstrip(' ,;:—–-') + '…'


def text(el):
    """Текст элемента; пробелы, которые get_text ставит на границах тегов, у скобок и знаков препинания убираются:
    «аудит (<span>СЭС-аудит</span>)» → «аудит (СЭС-аудит)», а не «аудит ( СЭС-аудит )»."""
    if el is None:
        return ''
    s = clean(el.get_text(' ', strip=True))
    s = re.sub(r'\s+([)\].,;:!?»])', r'\1', s)
    return re.sub(r'([(\[«])\s+', r'\1', s)


def page_url(rel):
    return '' if rel == 'index.html' else rel[:-len('index.html')]


def short_name(soup, rel):
    if rel == 'index.html':
        return 'Главная'
    for sc in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(sc.string or '')
        except ValueError:
            continue
        for node in (data.get('@graph', [data]) if isinstance(data, dict) else data):
            if isinstance(node, dict) and node.get('@type') == 'BreadcrumbList':
                items = node.get('itemListElement') or []
                if items:
                    return clean(items[-1].get('name') or (items[-1].get('item') or {}).get('name', ''))
    t = text(soup.find('title'))
    return re.split(r' [—|–] ', t)[0]


class Index:
    def __init__(self):
        self.pages, self.items, self.pidx = [], [], {}

    def page(self, name, url):
        if url not in self.pidx:
            self.pidx[url] = len(self.pages)
            self.pages.append([name, url])
        return self.pidx[url]

    def add(self, k, url, title, snip='', kw='', pi=0):
        title = clean(title)
        if not title:
            return
        self.items.append([k, url, title, cut(snip), cut(kw, KWN), pi])


PAGES_DIR = ROOT  # откуда читать страницы (--pages)


def index_page(ix, rel):
    s = (PAGES_DIR / rel).read_text(encoding='utf-8')
    soup = BeautifulSoup(s, 'lxml')
    url = page_url(rel)
    name = short_name(soup, rel)
    pi = ix.page(name, url)
    h1 = text(soup.find('h1'))
    desc = soup.find('meta', attrs={'name': 'description'})
    ix.add('p', url, h1 or name, desc['content'] if desc else '', text(soup.find('title')) + ' ' + name, pi)
    main = soup.find('main') or soup
    for sec in main.find_all('section', id=True):
        sid = sec['id']
        if sid in SKIP_SECTIONS:
            continue
        h2 = sec.find('h2')
        if not h2:
            continue
        p = h2.find_next('p')
        lead = text(p) if p is not None and sec in p.parents else ''
        kws = [text(h) for h in sec.find_all('h3')]
        for tb in ([] if 'dk-sec' in (sec.get('class') or []) else sec.find_all('table')):
            for tr in tb.find_all('tr')[1:]:
                c = tr.find(['td', 'th'])
                if c is not None:
                    kws.append(text(c))
        ix.add('h', url + '#' + sid, text(h2), lead, ' · '.join(kws), pi)
    for btn in main.select('.qa button[id]'):
        if not re.fullmatch(r'q\d+', btn['id']):
            continue
        ans = soup.find(id=btn.get('aria-controls', ''))
        ix.add('q', url + '#' + btn['id'], text(btn), text(ans), '', pi)
    return soup, pi


def index_hub(ix, soup, pi):
    url = 'normativnaya-baza/'
    for tr in soup.select('#dokumenty table tbody tr'):
        td = tr.find_all('td')
        if len(td) >= 2:
            ix.add('n', url + '#dokumenty', text(td[0]), text(td[1]), text(td[2]) if len(td) > 2 else '', pi)
    for tr in soup.select('#otmenennye table tbody tr'):
        td = tr.find_all('td')
        if len(td) >= 2:
            ix.add('o', url + '#otmenennye', text(td[0]), 'Заменён: ' + text(td[1]) + (' · ' + text(td[2]) if len(td) > 2 else ''),
                   'отменён устаревший утратил силу', pi)


def index_listy(ix, soup, pi):
    url = 'normativnaya-baza/proverochnye-listy/'
    for tr in soup.select('#po-obektam table tbody tr'):
        td = tr.find_all('td')
        if len(td) >= 3:
            ix.add('c', url + '#po-obektam', f'{text(td[0])}: проверочный лист {text(td[1])}',
                   f'Вопросы о вредителях: {text(td[2])}. ' + (text(td[3]) if len(td) > 3 else ''), 'проверочный лист чек-лист форма', pi)


def docs_word(n):
    """41 документ, 44 документа, 47 документов."""
    if n % 10 == 1 and n % 100 != 11:
        return 'документ'
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return 'документа'
    return 'документов'


def index_docs(ix, pi):
    """Перечень документов и конструктор страницы «Документы для Роспотребнадзора» — из data/dokumenty.json."""
    for g in DK['groups']:
        for it in g['items']:
            basis = clean(re.sub(r'<[^>]+>', '', it.get('basis_html') or ''))
            snip = (it['note'] + '. ' if it.get('note') else '') + 'Кто готовит: ' + it['who'] + '.' + (' Основание: ' + basis if basis else '')
            kw = ' · '.join(x for x in (it.get('for_whom', ''), g['title']) if x)
            ix.add('d', DOCS + '#p' + it['id'].replace('.', '-'), it['title'], snip, kw, pi)
    for o in DK['objects']:
        ck = o['checklist']
        ck = ck[:1].lower() + ck[1:] if ck[:1].isupper() and ck[1:2].islower() else ck  # «Отдельной формы нет» → «отдельной…»
        hint = OBJ_HINT.get(o['slug'])
        ix.add('b', f"{DOCS}?obekt={o['slug']}#konstruktor",
               f"Документы для проверки: {o['name']}" + (f" ({hint})" if hint else ''),
               f"Конструктор соберёт папку: {o['count']} {docs_word(o['count'])}. Проверочный лист: {ck}. "
               'Отметьте, что уже есть, — конструктор покажет, чего не хватает.',
               OBJ_KW.get(o['slug'], '') + ' папка документы проверка роспотребнадзор конструктор', pi)


def pdf_pages(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    r = PdfReader(str(path))
    return [p.extract_text() or '' for p in r.pages]


def index_pdfs(ix):
    missing = []
    for rel, page, entries in PDFS:
        f = ROOT / rel
        if not f.exists():
            missing.append(rel)
            continue
        texts = pdf_pages(f)
        pi = ix.pidx.get(page, 0)
        for n, title, snip, kw, check in entries:
            if texts is not None:
                assert n <= len(texts), (rel, n, len(texts))
                if check:  # сверка: нужный заголовок действительно на этой странице PDF (буквы «а» в части шрифтов теряются)
                    t = texts[n - 1].replace('\u00a0', ' ')
                    assert check in t or check.replace('а', '') in t, f'{rel}: на странице {n} нет «{check}»'
            ix.add('f', rel + (f'#page={n}' if n > 1 else ''), title, snip, kw, pi)
    return missing


def minify():
    src, out = HERE / 'search.js', ROOT / 'search.min.js'
    npx = shutil.which('npx')
    if not npx:
        print('  внимание: нет Node.js — search.min.js не пересобран')
        return
    res = subprocess.run([npx, '--yes', 'esbuild@0.24.2', str(src), '--minify', '--target=es2015', '--charset=utf8',
                          '--legal-comments=none', f'--outfile={out}'], capture_output=True, text=True, cwd=str(ROOT))
    if res.returncode:
        raise SystemExit('esbuild: ' + res.stderr)
    print(f'  search.min.js: {out.stat().st_size} байт')


def main():
    global PAGES_DIR
    args = sys.argv[1:]
    out_file = ROOT / 'search-index.json'
    if '--pages' in args:
        PAGES_DIR = pathlib.Path(args[args.index('--pages') + 1])
    if '--out' in args:
        out_file = pathlib.Path(args[args.index('--out') + 1])
    ix = Index()
    for rel in build_prod.PAGES:
        if not (PAGES_DIR / rel).exists():
            raise SystemExit(f'нет страницы {rel}')
        soup, pi = index_page(ix, rel)
        if rel == 'normativnaya-baza/index.html':
            index_hub(ix, soup, pi)
        elif rel == 'normativnaya-baza/proverochnye-listy/index.html':
            index_listy(ix, soup, pi)
        elif rel == DOCS + 'index.html':
            index_docs(ix, pi)
    missing = index_pdfs(ix)
    data = {'v': V, 'p': ix.pages, 'i': ix.items}
    raw = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    out_file.write_text(raw, encoding='utf-8')
    kinds = {}
    for it in ix.items:
        kinds[it[0]] = kinds.get(it[0], 0) + 1
    print(f'  search-index.json: {len(ix.items)} записей, {len(raw.encode())} байт ·',
          ', '.join(f'{k} {v}' for k, v in sorted(kinds.items())))
    if missing:
        print('  внимание: нет файлов PDF —', ', '.join(missing))
    if out_file == ROOT / 'search-index.json':
        minify()


if __name__ == '__main__':
    main()
