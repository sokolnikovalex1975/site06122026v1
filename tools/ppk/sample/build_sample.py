# -*- coding: utf-8 -*-
"""Сборка образца ППК: PDF (2 прохода для номеров страниц в оглавлении), DOCX, превью страниц.

python3 tools/ppk/sample/build_sample.py

Нужно: шрифт Inter 4.x в системе (~/.fonts), Node + playwright (Chromium), PyMuPDF, python-docx, Pillow.
Результат: materialy/programma-proizvodstvennogo-kontrolya-haccp/
  obrazets-programmy-proizvodstvennogo-kontrolya.pdf
  img/ppk-sample-p{1,11,20}-{240,360,720}.webp (превью титула, ККТ и план-схемы для блока «Образец» на странице)
Шаблон Word на сайте не публикуется (снят 07.11.2026): DOCX собирается во временную папку
/tmp/ppk_sample_build/shablon-programmy-proizvodstvennogo-kontrolya.docx — только для файлов проекта.
"""
import json
import pathlib
import shutil
import subprocess
import sys

import pymupdf as fitz
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import content as C  # noqa: E402
import render_html as R  # noqa: E402

OUT = ROOT / 'materialy' / 'programma-proizvodstvennogo-kontrolya-haccp'
PDF_NAME = 'obrazets-programmy-proizvodstvennogo-kontrolya.pdf'
DOCX_NAME = 'shablon-programmy-proizvodstvennogo-kontrolya.docx'
TMP = pathlib.Path('/tmp/ppk_sample_build')
MM = 72 / 25.4


def render(pages, figs=False):
    R.build(TMP, pages)
    cmd = ['node', str(HERE / 'render_pdf.mjs'), str(TMP), str(TMP / 'doc.pdf')] + (['--figs'] if figs else [])
    subprocess.run(cmd, check=True, cwd=str(HERE))
    names = fitz.open(str(TMP / 'doc.pdf')).resolve_names()
    res = {}
    for num, _ in C.TOC:
        key = 's' + (('A' + num[1:]) if num.startswith('П') else num)
        res[num] = names[key]['page'] + 1
    return res


def main():
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True)
    pages = render({}, figs=True)
    for _ in range(3):
        again = render(pages)
        if again == pages:
            break
        pages = again
    else:
        raise SystemExit('номера страниц не сошлись')
    doc = fitz.open(str(TMP / 'doc.pdf'))
    n = doc.page_count
    # обложка без колонтитулов
    p0 = doc[0]
    W, H = p0.rect.width, p0.rect.height
    p0.add_redact_annot(fitz.Rect(0, 0, W, 19.5 * MM))
    p0.add_redact_annot(fitz.Rect(0, H - 14.5 * MM, W, H))
    p0.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED)
    doc.set_metadata({
        'title': 'Образец программы производственного контроля (ППК) для пищевого производства с процедурами ХАССП',
        'author': 'ПЕСТКОНТРОЛЬ Центр (пестконтроль-центр.рф)',
        'subject': 'Программа производственного контроля по СП 1.1.1058-01 и ТР ТС 021/2011 для хлебопекарного и кондитерского производства: лабораторный контроль, ККТ, медосмотры, пест-контроль, аварийные ситуации, формы учёта',
        'keywords': 'программа производственного контроля, ППК, образец, ХАССП, ККТ, СП 1.1.1058-01, ТР ТС 021/2011, пищевое производство, пест-контроль',
        'creator': 'ПЕСТКОНТРОЛЬ Центр',
        'producer': 'ПЕСТКОНТРОЛЬ Центр',
    })
    OUT.mkdir(parents=True, exist_ok=True)
    pdf_path = OUT / PDF_NAME
    doc.save(str(pdf_path), garbage=4, deflate=True)
    doc.close()
    json.dump({'pages': n, 'toc': pages}, open(TMP / 'pages.json', 'w'), ensure_ascii=False)

    # DOCX — только во временную папку (на сайте шаблона Word нет)
    import build_docx
    build_docx.build(TMP / DOCX_NAME, TMP)
    stale = OUT / DOCX_NAME
    if stale.exists():
        stale.unlink()
        print('удалён', stale)

    # превью страниц
    d = fitz.open(str(pdf_path))
    picks = {'cover': 0, 'toc': 1}
    for i, pg in enumerate(d):
        t = pg.get_text().replace('\u00a0', ' ')
        if 'kkt' not in picks and 'Опасный фактор' in t and 'Критический предел' in t:
            picks['kkt'] = i
        if 'lab' not in picks and '5.1. Сырьё' in t:
            picks['lab'] = i
        if 'pest' not in picks and '11.3.1' in t:
            picks['pest'] = i
        if 'plan' not in picks and 'точки отбора проб и точки пест-контроля' in t and 'ПРИЛОЖЕНИЕ 1' in t.upper() and i > 2:
            picks['plan'] = i
    img = ROOT / 'img'
    # превью для блока .p-obr на странице: стр. 1 (титул), ККТ, план-схема — 240/360/720 px
    want = {'cover': 1, 'kkt': 11, 'plan': 20}
    for key, num in want.items():
        got = picks.get(key, -1) + 1
        if got != num:
            print(f'ВНИМАНИЕ: {key} теперь на стр. {got}, а в main.html указана стр. {num} — обновите ссылки и превью')
        pix = d[got - 1].get_pixmap(dpi=200)
        im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        for w in (240, 360, 720):
            h = round(im.height * w / im.width)
            im.resize((w, h), Image.LANCZOS).save(img / f'ppk-sample-p{got}-{w}.webp', 'WEBP', quality=80, method=6)
    print(json.dumps({'pages': n, 'toc': pages, 'thumbs': picks}, ensure_ascii=False))
    print(pdf_path, pdf_path.stat().st_size)


if __name__ == '__main__':
    main()
