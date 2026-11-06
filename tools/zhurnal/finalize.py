#!/usr/bin/env python3
"""Метаданные PDF и превью листов для страницы /materialy/zhurnal-pest-kontrolya/.

python3 finalize.py <out_dir> <repo_root>

Берёт out_dir/obrazets.pdf и out_dir/shablon.pdf (render_journal.mjs), записывает метаданные,
сжимает и кладёт в materialy/zhurnal-pest-kontrolya/, превью WebP (200 dpi -> q80) — в img/.
"""
import os
import sys
import pathlib
import pymupdf
from PIL import Image

OUT = pathlib.Path(sys.argv[1]).resolve()
ROOT = pathlib.Path(sys.argv[2]).resolve()
DST = ROOT / 'materialy' / 'zhurnal-pest-kontrolya'
IMG = ROOT / 'img'
AUTHOR = 'ПЕСТКОНТРОЛЬ Центр (ООО «Центр дезинфекционных услуг»)'
KEYS = 'журнал пест-контроля, образец заполнения, шаблон, бланк, форма, дератизация, дезинсекция, ХАССП, пестконтроль-центр.рф'
META = {
    'obrazets': ('obrazets-zhurnala-pest-kontrolya.pdf', 'Образец заполнения журнала пест-контроля — ПЕСТКОНТРОЛЬ Центр',
                 'Заполненный образец журнала пест-контроля (форма ЖПК-01, 10 листов)'),
    'shablon': ('shablon-zhurnala-pest-kontrolya.pdf', 'Шаблон журнала пест-контроля (бланк для печати) — ПЕСТКОНТРОЛЬ Центр',
                'Шаблон-бланк журнала пест-контроля (форма ЖПК-01, 10 листов); совпадает с образцом заполнения лист в лист'),
}
for key, (fn, title, subject) in META.items():
    d = pymupdf.open(OUT / f'{key}.pdf')
    d.set_metadata({'title': title, 'author': AUTHOR, 'subject': subject, 'keywords': KEYS,
                    'creator': 'ПЕСТКОНТРОЛЬ Центр · пестконтроль-центр.рф', 'producer': 'ПЕСТКОНТРОЛЬ Центр'})
    d.save(DST / fn, garbage=4, deflate=True)
    print(fn, os.path.getsize(DST / fn))


def preview(fn, page, name, widths):
    pix = pymupdf.open(DST / fn)[page].get_pixmap(dpi=200)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    for w in widths:
        out = IMG / f'{name}-{w}.webp'
        im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(out, 'WEBP', quality=80, method=6)
        print(out.name)


preview(META['obrazets'][0], 0, 'zhurnal-obrazets-p1', [360, 720])   # hero, карточка «Скачать», /dezinsektsiya/
preview(META['obrazets'][0], 7, 'zhurnal-obrazets-p8', [360, 720])   # hero (второй лист)
preview(META['obrazets'][0], 5, 'zhurnal-obrazets-p6', [480, 960])   # блок «Форма журнала»
preview(META['shablon'][0], 0, 'zhurnal-shablon-p1', [360, 720])     # карточка шаблона
