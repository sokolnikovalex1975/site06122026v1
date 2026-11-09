#!/usr/bin/env python3
"""Выкладка 09.11.2026: формула пест-риска и номер стандарта на странице «Программа пест-контроля» и в её PDF.

Владелец 08.11.2026 обвёл на странице /materialy/programma-pest-kontrolya/ обозначения «(0…1)» в формуле
«Пест-риск = Пест-опасность (0…1) × Вероятность ущерба (0…1)» и спросил, что это. Это шкала «от 0 до 1»
из методики НЧНОУ «Институт пест-менеджмента», но читателю она непонятна; рядом нашлись ошибки. 09.11.2026:
«Вноси все правки и выкладывай на хостинг».

Правки на странице:
  * номер стандарта «Процедуры управления пест-риском на предприятии» — СТО 55003215.002-2015, а не .001-2015
    (номер .001 — у СТО 55003215.001-2023 «Борьба с вредителями…»): подпись над формулой, абзац раздела «Форма»,
    примечание под планом мероприятий;
  * формула как в PDF-образце: «Пест-риск (R) = Пест-опасность (P) × Вероятность и тяжесть ущерба (D)», под ней —
    пояснение шкалы (каждый показатель от 0 до 1; R: до 0,25 — низкий … выше 0,75 — критический, как в PDF);
  * карточки: «1. Пест-опасность (P): от 0 до 1», «2. Вероятность и тяжесть ущерба (D): от 0 до 1»;
  * шаг 3 «Как заполнить шаблон»: буквы R, P и D расшифрованы;
  * зона E_5 в примере плана: «Высокий (0,55)» вместо «Средний / Высокий (0,55)» — по шкале 0,51–0,75 это высокий риск;
  * размер образца PDF после пересборки (192 КБ), dateModified в JSON-LD — 2026-11-09, стиль .p-formula-note.
PDF (образец и пустой шаблон) пересобираются отдельно: tools/docs_brand/programma_src.py --sample, programma_src.py,
brand_pdf.py programma shablon.

Использование:
  python3 tools/deploy/patch-2026-11-09-pestrisk.py repo <корень репозитория>
      — правки в странице превью (index.html) и server/sitemap.xml; индекс поиска пересоберёт tools/site/build_site.py;
  python3 tools/deploy/patch-2026-11-09-pestrisk.py live <папка с файлами сайта> <папка пакета>
      — те же правки в файлах, как их отдаёт сайт по HTTPS (index.php, search-index.json, sitemap.xml).

Правки — точные замены с проверкой числа вхождений; пробел в искомом фрагменте совпадает и с обычным, и с неразрывным.
Новый текст страницы проходит ту же типографику (tools/legal/typo.py), что и тексты страниц; стили, JSON-LD, индекс
и sitemap — без типографики. Проверки: кроме замен, файл не меняется; блок счётчиков (Метрика 113675622, UIS, Radist)
в файлах сайта — байт в байт прежний; на странице не остаётся «0…1», «55003215.001-2015» и «Средний / Высокий».
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

# две строки: как оценивается показатель и шкала риска; диапазоны шкалы — без переноса после тире (.nw из style.css)
NOTE = ('Каждый показатель оценивается от 0 до 1: 0 — опасности или ущерба нет, 1 — максимум.<br>'
        'Риск R: до 0,25 — низкий, <span class="nw">0,26–0,50</span> — средний, <span class="nw">0,51–0,75</span> — высокий, '
        'выше 0,75 — критический.')

# Переносы: формула и обозначение стандарта не разрываются — «СТО» и номер, «(R) =», «(P) ×», «Пест-опасность (P)»
# и «R = P × D» вместе (неразрывные пробелы и .nw из style.css), диапазоны шкалы — без переноса после тире.
NB = '\u00a0'
STO_NEW = 'СТО' + NB + '55003215.002-2015'
FORMULA = ('Пест-риск (R)' + NB + '= <em><span class="nw">Пест-опасность</span>' + NB + '(P)</em>' + NB + '× '
           '<em>Вероятность и тяжесть ущерба' + NB + '(D)</em>')
CARD1 = '<b>1. Пест-опасность (P): от 0 до 1</b>'
CARD2 = '<b>2. Вероятность и тяжесть ущерба (D): от 0 до 1</b>'
STEP3 = ('<span class="nw">R = P × D</span>, где P — пест-опасность, D — вероятность и тяжесть ущерба '
         '(каждый показатель — от 0 до 1). От него зависят')
E5 = '<span class="p-risk-hi">Высокий (0,55)</span>'
SIZE = 'Образец — PDF, 6 страниц, 192 КБ'
CSS_NOTE = '.p-formula-note{color:var(--t2);font-size:14px;line-height:1.55;margin:-6px 0 20px}'

# (старый фрагмент, новый, сколько раз, типографика нового текста)
PAGE = [
    ('СТО 55003215.001-2015', STO_NEW, 3, False),
    ('СТО 55003215.001-2023', 'СТО' + NB + '55003215.001-2023', 2, False),
    ('<p class="p-formula-eq" data-fade>Пест-риск = <em>Пест-опасность (0…1)</em> × <em>Вероятность ущерба (0…1)</em></p>',
     '<p class="p-formula-eq" data-fade>' + FORMULA + '</p>\n      <p class="p-formula-note" data-fade>' + NOTE + '</p>', 1, True),
    ('<b>1. Пест-опасность (0…1)</b>', CARD1, 1, True),
    ('<b>2. Вероятность ущерба (0…1)</b>', CARD2, 1, True),
    ('R = P × D. От него зависят', STEP3, 1, True),
    ('<span class="p-risk-hi">Средний / Высокий (0,55)</span>', E5, 1, True),
    ('Образец — PDF, 6 страниц, 191 КБ', SIZE, 1, True),
    ('"dateModified":"2026-11-08"', '"dateModified":"2026-11-09"', 1, False),
    ('.p-formula-eq em{font-style:normal;color:var(--yel);font-weight:400}',
     '.p-formula-eq em{font-style:normal;color:var(--yel);font-weight:400}\n' + CSS_NOTE, 1, False),
]
INDEX = [('СТО 55003215.001-2015', 'СТО 55003215.002-2015', 1, False)]  # абзац раздела «Форма» в индексе поиска
SITEMAP = [(f'<loc>{URL}</loc>\n    <lastmod>2026-11-08</lastmod>', f'<loc>{URL}</loc>\n    <lastmod>2026-11-09</lastmod>', 1, False)]
LEFT = re.compile(r'0…1|55003215\.001-2015|Средний' + SP + '/' + SP + 'Высокий|Вероятность' + SP + 'ущерба' + SP + r'\(0')


def pattern(plain):
    return SP.join(re.escape(p) for p in plain.split(' '))


def apply(s, edits, what):
    spots = []
    for old, new, count, ty in edits:
        ms = list(re.finditer(pattern(old), s))
        assert len(ms) == count, f'{what}: «{old[:70]}» — найдено {len(ms)}, ожидалось {count}'
        for m in ms:
            spots.append((m.start(), m.end(), typo(new) if ty else new))
    spots.sort()
    for (a1, b1, _), (a2, b2, _) in zip(spots, spots[1:]):
        assert b1 <= a2, what + ': фрагменты пересекаются'
    for a, b, new in reversed(spots):
        s = s[:a] + new + s[b:]
    return s


def patch_file(src, dst, edits, what, counters=False, left=False):
    before = pathlib.Path(src).read_bytes().decode('utf-8')
    after = apply(before, edits, what)
    if counters:
        cb, ca = COUNTERS.findall(before), COUNTERS.findall(after)
        assert len(cb) == 1 and cb == ca, what + ': блок счётчиков изменился'
    if left:
        rest = LEFT.findall(after)
        assert not rest, f'{what}: осталось {rest}'
    pathlib.Path(dst).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(dst).write_bytes(after.encode('utf-8'))
    print(f'{what}: замен {sum(e[2] for e in edits)}' + (', счётчики без изменений' if counters else ''))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode == 'repo':
        root = pathlib.Path(sys.argv[2])
        patch_file(root / PROG / 'index.html', root / PROG / 'index.html', PAGE, PROG + 'index.html', left=True)
        patch_file(root / 'server' / 'sitemap.xml', root / 'server' / 'sitemap.xml', SITEMAP, 'server/sitemap.xml')
    elif mode == 'live':
        src, dst = pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3])
        patch_file(src / PROG / 'index.php', dst / PROG / 'index.php', PAGE, PROG + 'index.php', counters=True, left=True)
        patch_file(src / 'search-index.json', dst / 'search-index.json', INDEX, 'search-index.json')
        patch_file(src / 'sitemap.xml', dst / 'sitemap.xml', SITEMAP, 'sitemap.xml')
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
