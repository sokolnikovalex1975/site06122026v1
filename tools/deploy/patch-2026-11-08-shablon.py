#!/usr/bin/env python3
"""Выкладка 08.11.2026: шаблон программы пест-контроля — PDF вместо Word (страница программы и упоминания на сайте).

Владелец: «Тут остался документ Word, шаблон, исправь на PDF» (страница /materialy/programma-pest-kontrolya/).
Правило владельца для всех документов сайта: пустой шаблон и заполненный образец — один макет, шаблон без записей,
только PDF, с шапкой (телефон и сайт) и водяным знаком. Новый файл — shablon-programmy-pest-kontrolya.pdf
(tools/docs_brand/programma_src.py → brand_pdf.py shablon); шаблон Word снимается с сервера.

Использование:
  python3 tools/deploy/patch-2026-11-08-shablon.py repo <корень репозитория>
      — правки в страницах превью (index.html) в репозитории;
  python3 tools/deploy/patch-2026-11-08-shablon.py live <папка с файлами сайта> <папка пакета>
      — те же правки в файлах, как их отдаёт сайт по HTTPS (index.php и sitemap.xml), результат — в папку пакета.

Правки — точные замены фрагментов текста с проверкой числа вхождений; пробел в искомом фрагменте совпадает и с обычным,
и с неразрывным пробелом. Если найденный фрагмент набран с неразрывными пробелами, новый текст проходит ту же типографику
(tools/legal/typo.py), что и тексты страниц. Проверки:
  * каждый фрагмент найден ровно столько раз, сколько ожидается; кроме замен, файл не меняется;
  * блок счётчиков (Метрика 113675622, UIS, Radist) — байт в байт прежний (в файлах сайта);
  * на странице программы не остаётся «Word», «DOCX» и ссылок на .docx; на остальных — «шаблон Word» и «PDF и Word».
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'legal'))
from typo import typo  # noqa: E402

COUNTERS = re.compile(r'<!-- Yandex\.Metrika counter \+ UIS \+ Radist.*?<!-- /Yandex\.Metrika counter -->', re.S)
SP = '(?: |\u00a0)'
PROG = 'materialy/programma-pest-kontrolya/'
URL = 'https://xn----itbbsflddbfpfdodg9d0f.xn--p1ai/materialy/programma-pest-kontrolya/'

# «Смотрите также» — карточка программы (tools/site/unify.py, CARD['prog'])
REL = [('Образец в PDF и шаблон Word:', 'Образец и шаблон в PDF:', 1)]

EDITS = {
    PROG: [
        # description, og:description, описание TechArticle
        ('скачать PDF и шаблон Word, форма из 7 разделов', 'скачать образец и шаблон в PDF, форма из 7 разделов', 3),
        ('Программа пест-контроля: образец PDF, шаблон Word и пример заполнения',
         'Программа пест-контроля: образец и шаблон в PDF, пример заполнения', 1),
        # микроразметка: второй документ — PDF-шаблон, дата изменения статьи
        ('"name":"Шаблон программы пест-контроля в Word (DOCX)","encodingFormat":"application/vnd.openxmlformats-officedocument'
         '.wordprocessingml.document","url":"' + URL + 'shablon-programmy-pest-kontrolya.docx"',
         '"name":"Шаблон программы пест-контроля на предприятии (PDF, 6 страниц, без записей)","encodingFormat":"application/pdf",'
         '"url":"' + URL + 'shablon-programmy-pest-kontrolya.pdf"', 1),
        ('"datePublished":"2026-11-06","dateModified":"2026-11-06"', '"datePublished":"2026-11-06","dateModified":"2026-11-08"', 1),
        # вопросы 3 и 4 — в разметке FAQPage и в блоке вопросов
        ('можно скачать бесплатно — в PDF и как шаблон Word (DOCX). Он обезличен',
         'можно скачать бесплатно в PDF — вместе с пустым шаблоном той же формы. Образец обезличен', 2),
        ('Есть ли шаблон программы пест-контроля в Word, чтобы заполнить самостоятельно?',
         'Есть ли пустой шаблон программы пест-контроля, чтобы заполнить самостоятельно?', 2),
        ('Да, рядом с PDF есть шаблон в формате DOCX с теми же разделами и приложениями; поля для заполнения отмечены подчёркиванием.',
         'Да, рядом с образцом есть шаблон в PDF с теми же разделами и приложениями, но без записей: поля для заполнения '
         'отмечены подчёркиванием, таблицы целевых видов, плана мероприятий и реестра средств пустые, шаблон можно распечатать.', 2),
        # первый экран
        ('Бесплатный образец программы пест-контроля — PDF на 6 страниц и шаблон Word для заполнения',
         'Бесплатный образец программы пест-контроля и пустой шаблон для заполнения — PDF по 6 страниц', 1),
        ('Есть <a href="shablon-programmy-pest-kontrolya.docx" download>шаблон программы в Word (DOCX)</a>',
         'Есть <a href="shablon-programmy-pest-kontrolya.pdf" target="_blank" rel="noopener">пустой шаблон программы, PDF</a>', 1),
        # бегущая строка (два одинаковых ряда)
        ('<b>Шаблон</b> в Word (DOCX)</div>', '<b>Шаблон</b> в PDF для заполнения</div>', 2),
        # содержание страницы и блок «Образец»
        ('<a href="#obrazets">Образец PDF и шаблон Word</a>', '<a href="#obrazets">Образец и шаблон PDF</a>', 1),
        ('<em>скачать PDF и шаблон Word</em></h2>', '<em>скачать PDF и пустой шаблон</em></h2>', 1),
        ('план мероприятий по зонам, реестр средств и подписи сторон.</p>',
         'план мероприятий по зонам, реестр средств и подписи сторон. Рядом — пустой шаблон той же формы без записей.</p>', 1),
        ('<a href="shablon-programmy-pest-kontrolya.docx" class="btn btn-o btn-lg" download><span class="btn-t">Шаблон Word, DOCX</span></a>',
         '<a href="shablon-programmy-pest-kontrolya.pdf" class="btn btn-o btn-lg" target="_blank" rel="noopener">'
         '<span class="btn-t">Скачать шаблон, PDF</span></a>', 1),
        ('PDF — 6 страниц, 145 КБ; DOCX — те же разделы с полями для заполнения.',
         'Образец — PDF, 6 страниц, 191 КБ; шаблон — PDF, 6 страниц, 172 КБ: те же разделы и таблицы без записей.', 1),
        # «Как заполнить шаблон программы»
        ('в том же порядке, что и в шаблоне Word.', 'в том же порядке, что и в шаблоне.', 1),
        ('<a href="shablon-programmy-pest-kontrolya.docx" class="btn btn-w btn-lg" download><span class="btn-t">Скачать шаблон Word</span></a>',
         '<a href="shablon-programmy-pest-kontrolya.pdf" class="btn btn-w btn-lg" target="_blank" rel="noopener">'
         '<span class="btn-t">Скачать шаблон, PDF</span></a>', 1),
    ],
    'materialy/': [
        # карточка 01 и её строка в разметке ItemList (tools/site/unify.py, MAT_LD)
        ('Программа пест-контроля на предприятии: образец PDF, шаблон Word и пример заполнения',
         'Программа пест-контроля на предприятии: образец и шаблон в PDF, пример заполнения', 2),
        ('— образец PDF и шаблон Word</div>', '— образец и шаблон в PDF</div>', 2),
    ],
    'sanitarnyy-audit/': REL,
    'dogovor-deratizatsiya-dezinsektsiya/': REL,
    'dezinsektsiya/': REL,
    'pishchevoe-proizvodstvo/': REL,
    'farmatsevticheskie-proizvodstva/': REL,
    'materialy/zhurnal-pest-kontrolya/': REL,
    'materialy/pest-menedzhment-ili-razovaya-obrabotka/': REL,
    'sklady-i-logistika/': REL + [
        ('<span class="ds">Образец в PDF и шаблон Word</span>', '<span class="ds">Образец и шаблон в PDF</span>', 1)],
    'materialy/programma-proizvodstvennogo-kontrolya-haccp/': REL + [
        ('<a href="../programma-pest-kontrolya/">образец PDF и шаблон Word</a>',
         '<a href="../programma-pest-kontrolya/">образец и шаблон в PDF</a>', 1)],
    'deratizatsiya/': REL + [
        ('Образец программы пест-контроля (PDF и Word) →', 'Образец и шаблон программы пест-контроля (PDF) →', 1)],
}
SITEMAP = [(f'<loc>{URL}</loc>\n    <lastmod>2026-11-06</lastmod>', f'<loc>{URL}</loc>\n    <lastmod>2026-11-08</lastmod>', 1)]
LEFT_PROG = re.compile(r'Word|DOCX|\.docx')
LEFT_ANY = re.compile(r'шаблон' + SP + r'Word|PDF' + SP + r'и' + SP + r'Word|шаблоне' + SP + r'Word|Word' + SP + r'\(DOCX\)'
                      r'|shablon-programmy-pest-kontrolya\.docx')


def pattern(plain):
    return SP.join(re.escape(p) for p in plain.split(' '))


def apply(s, edits, what):
    spots = []
    for old, new, count in edits:
        ms = list(re.finditer(pattern(old), s))
        assert len(ms) == count, f'{what}: «{old[:70]}» — найдено {len(ms)}, ожидалось {count}'
        for m in ms:
            spots.append((m.start(), m.end(), typo(new) if '\u00a0' in m.group(0) else new))
    spots.sort()
    for (a1, b1, _), (a2, b2, _) in zip(spots, spots[1:]):
        assert b1 <= a2, what + ': фрагменты пересекаются'
    for a, b, new in reversed(spots):
        s = s[:a] + new + s[b:]
    return s


def check(rel, before, after, live):
    if live:
        cb, ca = COUNTERS.findall(before), COUNTERS.findall(after)
        assert len(cb) == 1 and cb == ca, rel + ': блок счётчиков изменился'
    left = (LEFT_PROG if rel == PROG else LEFT_ANY).findall(after)
    assert not left, f'{rel}: осталось {left}'


def run(src_root, dst_root, page_name, live):
    for rel, edits in EDITS.items():
        f = pathlib.Path(src_root, rel, page_name)
        before = f.read_bytes().decode('utf-8')
        after = apply(before, edits, rel)
        check(rel, before, after, live)
        out = pathlib.Path(dst_root, rel, page_name)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(after.encode('utf-8'))
        n = sum(c for _, _, c in edits)
        print(f'{rel}{page_name}: замен {n}' + (', счётчики без изменений' if live else ''))
    if live:
        sm = pathlib.Path(src_root, 'sitemap.xml').read_bytes().decode('utf-8')
        out = apply(sm, SITEMAP, 'sitemap.xml')
        pathlib.Path(dst_root, 'sitemap.xml').write_bytes(out.encode('utf-8'))
        print('sitemap.xml: lastmod страницы программы — 2026-11-08')


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'repo':
        run(sys.argv[2], sys.argv[2], 'index.html', live=False)
    elif mode == 'live':
        run(sys.argv[2], sys.argv[3], 'index.php', live=True)
    else:
        sys.exit(__doc__)
