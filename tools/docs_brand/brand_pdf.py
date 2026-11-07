#!/usr/bin/env python3
"""Фирменная шапка и водяной знак в готовых PDF: образец программы пест-контроля и образец договора.

python3 tools/docs_brand/brand_pdf.py

Исходники — копии PDF до правки в tools/docs_brand/src/ (повторный запуск не накладывает знак дважды).
1. На первой странице и в начале приложений прежняя шапка (логотип, плашка «Типовой образец», мелкие серые контакты) вырезается
   (redaction: текст и векторная графика в полосе шапки) и на её место ставится шапка как в журнале пест-контроля —
   крупно телефон и сайт (tools/docs_brand/brand.py, печать Chromium, вектор).
2. На остальных страницах в верхнем поле — компактная шапка в одну строку: ПЕСТКОНТРОЛЬ ЦЕНТР, телефон, сайт.
3. На каждую страницу поверх содержимого кладётся водяной знак «пестконтроль-центр.рф» (контуры букв, 12 %).
4. Метаданные: автор ПЕСТКОНТРОЛЬ Центр; превью страниц для сайта — заново (img/*-sample-*.webp).
Текст, таблицы, ссылки и число страниц не меняются.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

import pymupdf as fitz
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import brand  # noqa: E402

AUTHOR = 'ПЕСТКОНТРОЛЬ Центр (ООО «Центр дезинфекционных услуг»)'
DOCS = {
    'programma': dict(
        src=HERE / 'src' / 'obrazets-programmy-pest-kontrolya.pdf',
        dst=ROOT / 'materialy' / 'programma-pest-kontrolya' / 'obrazets-programmy-pest-kontrolya.pdf',
        band=(34, 27, 562, 71), x0=39.8, y0=22.5, width=516.0, runner_y0=14.0,
        tagline='Дератизация, дезинсекция и пест-контроль для организаций · система IPM / ХАССП',
        previews=[(0, 'programma-sample-p1', [240, 360, 720]), (2, 'programma-sample-p3', [240, 360, 720]),
                  (4, 'programma-sample-p5', [240, 360, 720])]),
    'dogovor': dict(
        src=HERE / 'src' / 'obrazets-dogovora-pestkontrol-tsentr.pdf',
        dst=ROOT / 'dogovor-deratizatsiya-dezinsektsiya' / 'obrazets-dogovora-pestkontrol-tsentr.pdf',
        band=(42, 31, 555, 82), x0=48.8, y0=32.0, width=499.4, runner_y0=17.5,
        tagline='Дератизация, дезинсекция и пест-контроль для организаций · IPM / ХАССП',
        previews=[(0, 'dogovor-sample', [680])]),
}


def node(*args):
    out = subprocess.run(['node', str(HERE / 'render.mjs'), *map(str, args)], check=True, capture_output=True, text=True,
                         env={**__import__('os').environ, 'NODE_PATH': __import__('os').environ.get('NODE_PATH', '/home/user/node_modules')})
    return out.stdout.strip()


def header_pdf(tmp, key, width_pt, tagline, s=0.9):
    html = tmp / f'hdr_{key}.html'
    html.write_text(brand.header_doc(round(width_pt / 72 * 25.4, 3), s=s, tagline=tagline), encoding='utf-8')
    node('header', html, tmp / f'hdr_{key}.pdf')
    return fitz.open(tmp / f'hdr_{key}.pdf')


def runner_pdf(tmp, key, width_pt, s=0.92):
    html = tmp / f'rh_{key}.html'
    html.write_text(brand.runner_doc(round(width_pt / 72 * 25.4, 3), s=s), encoding='utf-8')
    node('header', html, tmp / f'rh_{key}.pdf')
    return fitz.open(tmp / f'rh_{key}.pdf')


def watermark_pdf(tmp, w_pt, h_pt):
    html = tmp / 'wm.html'
    w_mm, h_mm = round(w_pt / 72 * 25.4, 3), round(h_pt / 72 * 25.4, 3)
    html.write_text(brand.watermark_doc(w_mm, h_mm), encoding='utf-8')
    node('page', html, tmp / 'wm.pdf', w_mm, h_mm)
    return fitz.open(tmp / 'wm.pdf')


def preview(doc_path, page, name, widths):
    pix = fitz.open(doc_path)[page].get_pixmap(dpi=200)
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    for w in widths:
        fn = f'{name}-p1.webp' if name == 'dogovor-sample' else f'{name}-{w}.webp'
        out = ROOT / 'img' / fn
        im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(out, 'WEBP', quality=80, method=6)
        print('  превью', out.name, w)


def brand_one(key, cfg, tmp):
    d = fitz.open(cfg['src'])
    meta = d.metadata
    hd = header_pdf(tmp, key, cfg['width'], cfg['tagline'])
    hr = hd[0].rect
    rh = runner_pdf(tmp, key, cfg['width'])
    rr = rh[0].rect
    x0, x1 = cfg['x0'], cfg['x0'] + cfg['width']
    band = fitz.Rect(*cfg['band'])
    full = []
    for i, p in enumerate(d):
        if any(r.y1 < band.y1 for r in p.search_for('ТИПОВОЙ ОБРАЗЕЦ')):
            # 1) прежняя шапка (первая страница и начало каждого приложения) → шапка как в журнале
            p.add_redact_annot(band, fill=False)
            p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                               text=fitz.PDF_REDACT_TEXT_REMOVE)
            p.show_pdf_page(fitz.Rect(x0, cfg['y0'], x1, cfg['y0'] + cfg['width'] * hr.height / hr.width), hd, 0)
            full.append(i + 1)
        else:
            # 2) остальные страницы — компактная шапка (телефон и сайт) в свободном верхнем поле
            p.show_pdf_page(fitz.Rect(x0, cfg['runner_y0'], x1, cfg['runner_y0'] + cfg['width'] * rr.height / rr.width), rh, 0)
    print(key, 'полная шапка на стр.', full, '— компактная на остальных')
    # 3) водяной знак на всех страницах
    wm = watermark_pdf(tmp, d[0].rect.width, d[0].rect.height)
    for p in d:
        p.show_pdf_page(p.rect, wm, 0, overlay=True)
    d.set_metadata({**{k: meta.get(k, '') for k in ('title', 'subject', 'keywords')},
                    'author': AUTHOR, 'creator': 'ПЕСТКОНТРОЛЬ Центр · пестконтроль-центр.рф', 'producer': 'ПЕСТКОНТРОЛЬ Центр'})
    d.save(cfg['dst'], garbage=4, deflate=True)
    print(key, cfg['dst'].relative_to(ROOT), cfg['dst'].stat().st_size, 'байт,', len(d), 'стр.')
    for page, name, widths in cfg['previews']:
        preview(cfg['dst'], page, name, widths)


if __name__ == '__main__':
    keys = sys.argv[1:] or list(DOCS)
    with tempfile.TemporaryDirectory() as t:
        for k in keys:
            brand_one(k, DOCS[k], pathlib.Path(t))
