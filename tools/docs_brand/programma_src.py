#!/usr/bin/env python3
"""Пустой шаблон программы пест-контроля в PDF — тот же макет, что у образца, но без записей.

    python3 tools/docs_brand/programma_src.py           → tools/docs_brand/src/shablon-programmy-pest-kontrolya.pdf
    python3 tools/docs_brand/brand_pdf.py shablon       → materialy/programma-pest-kontrolya/shablon-programmy-pest-kontrolya.pdf
                                                          (шапка с телефоном и сайтом, водяной знак — как у образца)
    python3 tools/docs_brand/programma_src.py --check   → печать образца из programma_html.py и сверка
                                                          с src/obrazets-programmy-pest-kontrolya.pdf (текст и картинка страниц)
    python3 tools/docs_brand/programma_src.py --sample  → src/obrazets-programmy-pest-kontrolya.pdf заново из programma_html.py
                                                          (после правки текста образца), затем brand_pdf.py programma и снова
                                                          programma_src.py (шаблон сверяется с новым образцом)

Правило владельца: пустые шаблоны и заполненные образцы на сайте — один макет, шаблон без записей и только в PDF
(08.11.2026 шаблон Word программы на странице заменён этим PDF). Исходник — HTML образца (programma_html.py).

Что пусто в шаблоне — записи по конкретному объекту, их вносит специалист после обследования:
  * п. 2.3 — целевые виды и зоны обнаружения (группы вредителей в первом столбце остаются);
  * Приложение № 1 — матрица мероприятий целиком: 6 строк без кодов зон, подразделений, видов, риска и порогов,
    мероприятий, ответственных и периодичности;
  * Приложение № 2 — реестр средств: назначение и действующие вещества, зоны применения и требования
    (категории средств в первом столбце остаются);
  * даты «2026 г.» → «20__ г.»; в колонтитуле «Шаблон программы…» вместо «Образец программы…».
Общие положения, нормы, методика оценки риска, три контура, регламент сторон, уровни контроля, отчётность и подписи —
как в образце. Записи скрыты (visibility:hidden), поэтому высота строк и вся вёрстка совпадают с образцом; скрытый
текст в PDF не попадает — скрипт это проверяет, как и совпадение линий таблиц с образцом.
"""
import os
import pathlib
import re
import subprocess
import sys
import tempfile

import pymupdf as fitz

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import programma_html  # noqa: E402

SRC_SAMPLE = HERE / 'src' / 'obrazets-programmy-pest-kontrolya.pdf'
SRC_TEMPLATE = HERE / 'src' / 'shablon-programmy-pest-kontrolya.pdf'
TITLE = 'Шаблон программы пест-контроля на предприятии — ПЕСТКОНТРОЛЬ Центр'
SUBJECT = ('Пустой шаблон типовой программы пест-контроля (ПОПМ / PRP) и управления пест-риском по системе IPM и ХАССП: '
           'те же разделы и приложения, что в образце, без записей')
FOOTER_OLD = 'ПЕСТКОНТРОЛЬ Центр · Образец программы пест-контроля на предприятии (система IPM / ХАССП)'
FOOTER_NEW = 'ПЕСТКОНТРОЛЬ Центр · Шаблон программы пест-контроля на предприятии (система IPM / ХАССП)'
YEAR_OLD, YEAR_NEW = '2026 г.', '20__ г.'
# таблицы с записями: (начало абзаца перед таблицей, строк, первый столбец остаётся)
TABLES = [
    ('<p><b>2.3. Перечень целевых биологических видов, контролируемых на объекте:</b></p>', 4, True),
    ('<p><b>4.1. Матрица мероприятий.</b>', 6, False),
    ('<p><b>6.1. Требования к средствам и оборудованию.</b>', 6, True),
]
# записи образца, которых в шаблоне быть не должно, и то, что в шаблоне должно остаться
MUST_GONE = ['Rattus', 'Blattella', 'Plodia', 'Columba', 'A_1', 'F_6', 'Высокий (0,64)', 'Критический (0,85)', 'Ф-ТПК-1',
             'Начальник АХО', 'Прилегающая территория и площадка ТКО', 'Погрызы тары', 'Бромадиолон', 'Имидаклоприд',
             'Ударопрочный пластик', 'Только клеевой тип', 'Строго Контур 1', '2026 г.', 'Образец программы']
MUST_STAY = ['ПРОГРАММА ПЕСТ-КОНТРОЛЯ', '1. Синантропные и природные грызуны', '4. Случайно проникающие виды и птицы',
             '1. Контрольно-', '6. Инсектицидные гели', 'Подразделение (код на', 'Периодичность и №',
             '4.1. Матрица мероприятий.', '4.2. Правила маркировки', 'Контур 1 (внешний)', '5.1. Перечень мероприятий',
             '7.1. Четыре уровня контроля', '8. Подписи и реквизиты', '20__ г.', 'Шаблон программы пест-контроля',
             'Лицензия ДДД: № Л064-00111-77/01942445', 'ТИПОВОЙ ОБРАЗЕЦ']


def sample_html():
    return programma_html.HTML_CONTENT


def _replace(s, old, new, count):
    n = s.count(old)
    assert n == count, f'{old[:60]!r}: найдено {n}, ожидалось {count}'
    return s.replace(old, new)


def _blank_table(s, anchor, rows, keep_first):
    i = s.index(anchor)
    a = s.index('<tbody>', i)
    b = s.index('</tbody>', a)
    assert s.find('<table', i, a) != -1 and s.find('</table>', i, a) == -1, anchor + ': таблица не сразу после абзаца'
    body = s[a:b]
    trs = re.findall(r'<tr>.*?</tr>', body, flags=re.S)
    assert len(trs) == rows, f'{anchor}: строк {len(trs)}, ожидалось {rows}'

    def tr_sub(m):
        cells = list(re.finditer(r'<td>(.*?)</td>', m.group(0), flags=re.S))
        assert cells, anchor + ': пустая строка'
        out, pos = [], 0
        for k, c in enumerate(cells):
            out.append(m.group(0)[pos:c.start()])
            out.append(c.group(0) if (keep_first and k == 0) else f'<td><div class="blank">{c.group(1)}</div></td>')
            pos = c.end()
        out.append(m.group(0)[pos:])
        return ''.join(out)
    body = re.sub(r'<tr>.*?</tr>', tr_sub, body, flags=re.S)
    return s[:a] + body + s[b:]


def template_html():
    s = sample_html()
    s = _replace(s, '<title>Образец программы пест-контроля на предприятии — ПЕСТКОНТРОЛЬ Центр</title>', f'<title>{TITLE}</title>', 1)
    s = _replace(s, FOOTER_OLD, FOOTER_NEW, 6)
    s = _replace(s, YEAR_OLD, YEAR_NEW, 4)
    s = _replace(s, '</style>', '.blank {\n  visibility: hidden;\n}\n</style>', 1)
    for anchor, rows, keep_first in TABLES:
        s = _blank_table(s, anchor, rows, keep_first)
    return s


def render(html, out_pdf):
    with tempfile.TemporaryDirectory() as t:
        p = pathlib.Path(t) / 'doc.html'
        p.write_text(html, encoding='utf-8')
        subprocess.run(['node', str(HERE / 'render.mjs'), 'doc', str(p), str(out_pdf)], check=True, capture_output=True, text=True,
                       env={**os.environ, 'NODE_PATH': os.environ.get('NODE_PATH', '/home/user/node_modules')})


def boxes(page, skip_pills=False):
    """Линии и заливки страницы (ячейки таблиц, плашки) — для сверки вёрстки шаблона с образцом."""
    out = []
    for g in page.get_drawings():
        r = g['rect']
        if skip_pills and 8 < r.height < 13 and 15 < r.width < 25 and g.get('fill') and g.get('color'):
            continue  # плашки кодов зон A_1…F_6 в Приложении № 1
        out.append((g.get('type'), tuple(round(v, 1) for v in r), tuple(round(c, 3) for c in (g.get('fill') or ())),
                    tuple(round(c, 3) for c in (g.get('color') or ()))))
    return sorted(out)


def check_template(tpl_pdf, sample_pdf):
    t, smp = fitz.open(tpl_pdf), fitz.open(sample_pdf)
    assert len(t) == len(smp) == 6, 'страниц не 6'
    text = '\n'.join(p.get_text() for p in t)
    flat = re.sub(r'\s+', ' ', text)
    gone = [w for w in MUST_GONE if w in flat]
    assert not gone, f'в шаблоне остались записи образца: {gone}'
    miss = [w for w in MUST_STAY if w not in flat]
    assert not miss, f'в шаблоне нет: {miss}'
    for i in range(6):
        same = boxes(t[i]) == boxes(smp[i], skip_pills=(i == 2))
        assert same, f'стр. {i + 1}: линии и заливки таблиц не совпадают с образцом'
        if i in (0, 3, 5):  # страницы без таблиц с записями: текст как в образце (кроме дат и колонтитула)
            want = smp[i].get_text().replace('Образец программы', 'Шаблон программы').replace(YEAR_OLD, YEAR_NEW)
            assert t[i].get_text() == want, f'стр. {i + 1}: текст отличается от образца'
        else:  # остальной текст страницы — строки образца
            lines = set(smp[i].get_text().replace('Образец программы', 'Шаблон программы').splitlines())
            extra = [ln for ln in t[i].get_text().splitlines() if ln not in lines]
            assert not extra, f'стр. {i + 1}: строки, которых нет в образце: {extra[:3]}'
    print('проверка шаблона: 6 стр., записей образца нет, линии таблиц и остальной текст — как в образце')


def check_sample():
    with tempfile.TemporaryDirectory() as t:
        out = pathlib.Path(t) / 'sample.pdf'
        render(sample_html(), out)
        a, b = fitz.open(out), fitz.open(SRC_SAMPLE)
        assert len(a) == len(b)
        for i in range(len(a)):
            pa, pb = a[i].get_pixmap(dpi=72), b[i].get_pixmap(dpi=72)
            assert a[i].get_text() == b[i].get_text(), f'стр. {i + 1}: текст образца отличается'
            assert pa.samples == pb.samples, f'стр. {i + 1}: картинка образца отличается'
    print('programma_html.py печатается так же, как src/obrazets-programmy-pest-kontrolya.pdf (6 стр.)')


SAMPLE_TITLE = 'Образец программы пест-контроля на предприятии — ПЕСТКОНТРОЛЬ Центр'
SAMPLE_SUBJECT = 'Типовая программа пест-контроля (ПОПМ / PRP) и управления пест-риском по системе IPM и ХАССП'


def build_sample():
    """src образца из programma_html.py (после правки текста образца, 09.11.2026): затем brand_pdf.py programma."""
    with tempfile.TemporaryDirectory() as t:
        raw = pathlib.Path(t) / 'raw.pdf'
        render(sample_html(), raw)
        d = fitz.open(raw)
        assert len(d) == 6, f'образец: {len(d)} стр., ожидалось 6'
        d.set_metadata({'title': SAMPLE_TITLE, 'subject': SAMPLE_SUBJECT, 'author': 'ПЕСТКОНТРОЛЬ Центр', 'keywords': '',
                        'creator': 'ПЕСТКОНТРОЛЬ Центр · пестконтроль-центр.рф', 'producer': 'ПЕСТКОНТРОЛЬ Центр'})
        d.save(SRC_SAMPLE, garbage=4, deflate=True)
    print(SRC_SAMPLE.relative_to(HERE.parents[1]), SRC_SAMPLE.stat().st_size, 'байт')


def main():
    if '--check' in sys.argv:
        check_sample()
        return
    if '--sample' in sys.argv:
        build_sample()
        check_sample()
        return
    with tempfile.TemporaryDirectory() as t:
        raw = pathlib.Path(t) / 'raw.pdf'
        render(template_html(), raw)
        d = fitz.open(raw)
        d.set_metadata({'title': TITLE, 'subject': SUBJECT, 'author': 'ПЕСТКОНТРОЛЬ Центр', 'keywords': '',
                        'creator': 'ПЕСТКОНТРОЛЬ Центр · пестконтроль-центр.рф', 'producer': 'ПЕСТКОНТРОЛЬ Центр'})
        d.save(SRC_TEMPLATE, garbage=4, deflate=True)
    check_template(SRC_TEMPLATE, SRC_SAMPLE)
    print(SRC_TEMPLATE.relative_to(HERE.parents[1]), SRC_TEMPLATE.stat().st_size, 'байт')


if __name__ == '__main__':
    main()
